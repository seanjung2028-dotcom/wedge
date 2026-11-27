"""Add Week 12's card finals to the final-line record (owner, Fri Nov 27 evening: "add the finals lines thus far in this week").
The owner chose Week 12 only: Week 11's card finals (0-4) are not counted, and the page says so (label "Weeks 1-10, 12", Week 11
shown as not counted). Idempotent: drops any Week 12 card rows, then appends every graded Week 12 final from Tuesday's posted card
(bt/w12_tue_board), and later the Sunday/Monday card's finals once graded.
Grading: nflverse player stats (Wed/Thu games, pulled Fri Nov 27 evening) and, for DEN @ PIT (Fri, PIT 27-5) before nflverse
posts it, news box scores: Bo Nix 1 carry for 7 yards (Bleacher Report box score), Germie Bernard 1 catch for 58 yards (Steelers
Now, Post-Gazette, ESPN game leaders). Marvin Mims Jr.'s line wasn't in any final box score found, so it stays pending.
Re-run after nflverse posts Friday's game: MANUAL entries are then checked against it."""
import json, re, sys, pandas as pd
W = '/home/claude/wedger/'
sys.path.insert(0, W + 'lens'); import core
STATS = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/-home-claude/7b7587cd-449e-5d94-986d-7a2d5c82d9a5/scratchpad/nfl1128/stats.csv'
MANUAL = {'Bo Nix under 20 rushing yards (No)': (7, 'DEN'), 'Germie Bernard under 40 receiving yards (No)': (58, 'PIT')}
SKIP = [11]
COL = {'rushing yards': ('rushing_yards', 'rush yds'), 'receiving yards': ('receiving_yards', 'rec yds'), 'receptions': ('receptions', 'rec')}
s = pd.read_csv(STATS, low_memory=False); s = s[(s.week == 12) & (s.season_type == 'REG')]
card = json.load(open(W + 'bt/w12_tue_board/final_w12.json'))
REC = pd.read_csv(W + 'rh/final_record.csv'); REC = REC[~((REC.week == 12) & (REC.source == 'Week 12 card'))]
rows, pending = [], []
for c in card['cards']:
    for p in c.get('plays', []):
        if p['decision'] != 'Final line': continue
        m = re.search(r'(under )?(\d+)\+? (rushing yards|receiving yards|receptions)', p['thr']); k = int(m.group(2)); col, unit = COL[m.group(3)]
        r = s[s.player_display_name == p['player']]
        if len(r): v, team = float(r.iloc[0][col] or 0), core.fx(r.iloc[0].team)
        elif p['line'] in MANUAL: v, team = MANUAL[p['line']]
        else: pending.append(p['line']); continue
        if p['line'] in MANUAL and len(r): assert v == MANUAL[p['line']][0], ('box score differs from nflverse', p['line'], v)
        won = v >= k if p['side'] == 'Yes' else v < k
        rows.append({'week': 12, 'source': 'Week 12 card', 'game': c['game'], 'team': team, 'line': p['line'], 'price': int(p['price']), 'mid': p['mid'],
                     'outcome': 'Won' if won else 'Lost', 'result': f"W12: {int(v)} {unit}", 'profit_c': (100 - int(p['price'])) if won else -int(p['price'])})
REC = pd.concat([REC.drop(columns='id'), pd.DataFrame(rows)], ignore_index=True).sort_values(['week', 'source', 'game', 'line']).reset_index(drop=True)
REC.insert(0, 'id', [f'FR{i + 1:03d}' for i in range(len(REC))])
REC.to_csv(W + 'rh/final_record.csv', index=False)
weeks = sorted(int(x) for x in REC.week.unique()); thru = max(weeks)
lab = f"1–{thru}" if not SKIP else '1–' + ', '.join(str(w) for w in range(1, thru + 1) if w not in SKIP).replace('1, 2, 3, 4, 5, 6, 7, 8, 9, 10', '10')
lab = '1–10, 12' if SKIP == [11] and thru == 12 else lab
n = len(REC); w_ = int((REC.outcome == 'Won').sum()); cost = float(REC.price.sum()); prof = float(REC.profit_c.sum())
note = 'Backtested, brainstormed, and settled. Week 11 is not counted.' + (f" {len(pending)} Week 12 line{'s' if len(pending) > 1 else ''} still to be graded." if pending else '')
SUM = pd.read_csv(W + 'rh/card_bt_sum.csv')
for c_ in ('weeks', 'skip', 'note'):
    if c_ not in SUM.columns: SUM[c_] = ''
i = SUM.index[SUM.key == 'final_record'][0]
SUM.loc[i, ['label', 'wins', 'losses', 'win_pct', 'avg_price', 'needed', 'profit_c', 'roi_pct', 'thru', 'weeks', 'skip', 'note']] = [
    f'Final lines · Weeks {lab}', w_, n - w_, round(100 * w_ / n, 1), round(cost / n, 1), round(cost / n + 2, 1), int(prof), round(100 * prof / cost, 1), thru, lab, ','.join(map(str, SKIP)), note]
SUM.to_csv(W + 'rh/card_bt_sum.csv', index=False)
pd.DataFrame([{'wins': w_, 'losses': n - w_, 'win_pct': round(100 * w_ / n, 1), 'roi_pct': round(100 * prof / cost, 1), 'profit_c': int(prof), 'thru': thru, 'weeks': lab}]).to_csv(W + 'rh/frec.csv', index=False)
print(f'final record {w_}-{n - w_} ({round(100 * w_ / n, 1)}%), {int(prof):+}c, ROI {round(100 * prof / cost, 1)}%, weeks {lab}; Week 12 added {len(rows)}: '
      f"{sum(r['outcome'] == 'Won' for r in rows)}-{sum(r['outcome'] == 'Lost' for r in rows)} {sum(r['profit_c'] for r in rows):+}c; pending {pending}")
