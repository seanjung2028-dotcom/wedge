"""Records for the Results tab: the backtested card (bt/card_bt/card.pkl, from card_bt.py) next to the live card as it settled
(final10/ onward, every graded play) and the Week 9 card as posted. Fast; rerun after each settle.
Writes rh/card_bt.csv (every backtested pick) and rh/card_bt_sum.csv (records)."""
import json, math, os
import numpy as np, pandas as pd
W = '/home/claude/wedger/'; FEE = 2.0
CARD = pd.read_pickle(W + 'bt/card_bt/card.pkl')
# the owner's call (Tue Nov 17): these four backtested final lines are left out of the record (the page notes it)
EXCLUDE = {(5, 'Drake Maye 35+ rushing yards (Yes)'), (5, 'TreVeyon Henderson 50+ rushing yards (Yes)'),
           (6, 'Najee Harris 35+ rushing yards (Yes)'), (7, 'Aaron Jones Sr. 60+ rush + rec yards (Yes)')}
_x = [(w, l) in EXCLUDE for w, l in zip(CARD.week, CARD.line)]
assert sum(_x) == len(EXCLUDE), f'excluded {sum(_x)} of {len(EXCLUDE)}'
CARD = CARD[[not v for v in _x]].copy()
# ---------------- the live card, settled (Week 10 onward, v6) and the Week 9 card as posted (before v6)
def live(path, wk, label):
    F = json.load(open(W + path)); out = []
    for c in F['cards']:
        for p in c['plays']:
            r = p.get('result') or {}
            if r.get('outcome') not in ('Won', 'Lost'): continue
            out.append({'src': label, 'week': wk, 'game': c['game'], 'line': p['line'], 'side': p.get('side', 'Yes'), 'price': p['price'], 'be': p.get('be', p['price'] + FEE),
                        'mid': p.get('mid'), 'lo': p.get('lo'), 'hi': p.get('hi'), 'decision': p['decision'], 'win': int(r['outcome'] == 'Won'), 'profit': r['profit_c']})
    return pd.DataFrame(out)
import glob, re as _re
LIVE = pd.concat([live(f'final{n}/final_w{n}.json', n, 'live') for n in range(10, 23) if os.path.exists(W + f'final{n}/final_w{n}.json')] +
                 [live('final9/final_w9.json', 9, 'posted9')], ignore_index=True)
LIVE_THRU = int(LIVE[LIVE.src == 'live'].week.max()) if (LIVE.src == 'live').any() else 10
def rec(x, key, label, group, src, week='', tier=''):
    n = len(x); w = int(x.win.sum()) if n else 0; cost = float(x.price.sum()) if n else 0
    return {'key': key, 'label': label, 'group': group, 'src': src, 'week': week, 'tier': tier, 'wins': w, 'losses': n - w,
            'win_pct': round(100 * w / n, 1) if n else None, 'avg_price': round(cost / n, 1) if n else None,
            'needed': round(float(x.be.mean()), 1) if n else None, 'ours': round(float(pd.to_numeric(x.mid, errors='coerce').mean()), 1) if n and pd.to_numeric(x.mid, errors='coerce').notna().any() else None,
            'profit_c': int(round(float(x.profit.sum()))) if n else 0, 'roi_pct': round(100 * float(x.profit.sum()) / cost, 1) if cost else None}
TN = {'Final line': ('final', 'Final lines'), 'Conditional lean': ('lean', 'Conditional leans')}
S = []
for tier, (tk, tl) in TN.items():
    bt = CARD[(CARD.decision == tier) & CARD.src.isin(['real', 'rebuilt'])]
    S.append(rec(bt, f'{tk}_bt', f'{tl} · backtest, Weeks 1–9', 'compare', 'backtest', '', tk))
    S.append(rec(CARD[(CARD.decision == tier) & (CARD.src == 'real')], f'{tk}_real', f'{tl} · Weeks 7–9, real prices', 'compare', 'real', '', tk))
    S.append(rec(CARD[(CARD.decision == tier) & (CARD.src == 'rebuilt')], f'{tk}_rebuilt', f'{tl} · Weeks 1–6, rebuilt lines', 'compare', 'rebuilt', '', tk))
    S.append(rec(LIVE[(LIVE.decision == tier) & (LIVE.src == 'live')], f'{tk}_live', f'{tl} · live card, since Week 10', 'compare', 'live', '', tk))
for tier, (tk, tl) in TN.items():
    for side, sl in (('Yes', 'overs'), ('No', 'unders')):
        S.append(rec(CARD[(CARD.decision == tier) & CARD.src.isin(['real', 'rebuilt']) & (CARD.side == side)], f'{tk}_bt_{side}', f'{tl} · backtest {sl}', 'side', 'backtest', '', tk))
MIXCUT = pd.read_pickle(W + 'bt/card_bt/mixcut.pkl')
for tier, (tk, tl) in TN.items():
    S.append(rec(MIXCUT[(MIXCUT.decision == tier) & MIXCUT.src.isin(['real', 'rebuilt'])], f'{tk}_mixcut', f'{tl} · unders left off for the card mix', 'side', 'backtest', '', tk))
for wk in range(1, 10):
    src = 'real' if wk >= 7 else 'rebuilt'
    for tier, (tk, tl) in TN.items():
        S.append(rec(CARD[(CARD.decision == tier) & (CARD.src == src) & (CARD.week == wk)], f'w{wk}_{tk}', f'Week {wk} · {tl.lower()}', 'week', src, wk, tk))
for wk in sorted(LIVE[LIVE.src == 'live'].week.unique()):
    for tier, (tk, tl) in TN.items():
        S.append(rec(LIVE[(LIVE.decision == tier) & (LIVE.src == 'live') & (LIVE.week == wk)], f'w{wk}_{tk}', f'Week {wk} · {tl.lower()} (live card)', 'week', 'live', int(wk), tk))
for tier, (tk, tl) in TN.items():
    S.append(rec(LIVE[(LIVE.decision == tier) & (LIVE.src == 'posted9')], f'p9_{tk}', f'Week 9 · {tl.lower()}, card as posted (before v6)', 'check', 'posted9', 9, tk))
    S.append(rec(CARD[(CARD.decision == tier) & (CARD.src == 'real') & (CARD.week == 9)], f'b9_{tk}', f'Week 9 · {tl.lower()}, backtest', 'check', 'real', 9, tk))
    S.append(rec(CARD[(CARD.decision == tier) & (CARD.src == 'check')], f'c79_{tk}', f'Weeks 7–9 · {tl.lower()} on rebuilt lines (check)', 'check', 'check', '', tk))
SUM = pd.DataFrame(S)
PK = CARD[CARD.src.isin(['real', 'rebuilt'])].copy()
PK['outcome'] = np.where(PK.win == 1, 'Won', 'Lost')
UNIT = {'rec': 'rec', 'recyd': 'rec yds', 'rushyd': 'rush yds', 'rryd': 'rush + rec yds'}
PK['result'] = [f"W{w}: {int(a)} {UNIT[s]}" for w, a, s in zip(PK.week, PK.actual, PK.stat)]
PK['prices'] = np.where(PK.src == 'real', 'Real price', 'Rebuilt line')
PK = PK.sort_values(['week', 'decision', 'game', 'line'], ascending=[True, False, True, True]).reset_index(drop=True)
PK['id'] = [f'BT{i + 1:03d}' for i in range(len(PK))]
PK['est'] = [f"{lo:.0f}–{hi:.0f}%" for lo, hi in zip(PK.lo, PK.hi)]
PK[['id', 'week', 'prices', 'game', 'team', 'decision', 'line', 'side', 'price', 'be', 'mkt', 'lo', 'mid', 'hi', 'est', 'outcome', 'result', 'profit']].rename(columns={'profit': 'profit_c', 'be': 'needed'}).to_csv(W + 'rh/card_bt.csv', index=False)
SUM.to_csv(W + 'rh/card_bt_sum.csv', index=False)
pd.set_option('display.width', 220)
print(SUM[['key', 'wins', 'losses', 'win_pct', 'avg_price', 'needed', 'ours', 'profit_c', 'roi_pct']].to_string())

# ---------------- the final-line record on Results (Tue Nov 17, the owner's call) ----------------
# backtested finals (above, four left out) + Wedge picks added by hand as final lines + the Week 10 card's final lines as
# certified (certs10/keys_w10_finals.json). Prices, outcomes and profit come from the record (rh/results_w6_w11.csv).
import re, sys
sys.path.insert(0, W + 'lens'); import core
ADDED = [(6, 'HOU @ JAX', 'Xavier Hutchinson: Over 1.5 Receptions'), (6, 'WSH @ SF', 'Brock Purdy: Over 19.5 Rush Yards'),
         (6, 'WSH @ SF', 'Christian McCaffrey: Over 5.5 Receptions'), (6, 'LAC @ KC', 'Kenneth Walker: Over 89.5 Rush Yards'),
         (6, 'BUF @ LV', 'Ashton Jeanty: Over 3.5 Receptions'), (7, 'NE @ CHI', "D'Andre Swift: Over 2.5 Receptions"),
         (7, 'PIT @ NO', 'Jaylen Warren: Over 14.5 Receiving Yards'), (7, 'NE @ CHI', 'Rhamondre Stevenson: Over 2.5 Receptions'),
         (7, 'CIN @ BAL', 'Chase Brown: Over 39.5 Rush Yards'), (9, 'CIN @ ATL', 'Tee Higgins: Over 4.5 Receptions'),
         (9, 'CLE @ NO', 'Chris Olave: Over 5.5 Receptions'), (10, 'WSH @ NYG', 'Malik Nabers: Over 4.5 Receptions')]
CARD10 = [(10,) + tuple(k.split('|')[1:2]) + (k.split('|')[3],) for k in json.load(open(W + 'certs10/keys_w10_finals.json'))]
RR = pd.read_csv(W + 'rh/results_w6_w11.csv', low_memory=False)
ST = pd.read_csv(W + 'dl19/stats_player_week_2026.csv', low_memory=False); ST = ST[ST.season_type == 'REG'].copy()
ST['nn'] = ST.player_display_name.map(core.nn); ST['team'] = ST.team.map(core.fx)
MW = {'Receptions': ('receptions', 'receptions', 'rec'), 'Rush Yards': ('rushing yards', 'rushing_yards', 'rush yds'), 'Receiving Yards': ('receiving yards', 'receiving_yards', 'rec yds')}
F10 = {p['line']: p for c in json.load(open(W + 'final10/final_w10.json'))['cards'] for p in c['plays']}
def rec_row(wk, game, contract, source):
    x = RR[(RR.week == wk) & (RR.game == game) & (RR.contract == contract)]
    assert len(x) >= 1, (wk, game, contract); x = x.iloc[0]
    m = re.match(r"(.+?): (Over|Under) ([\d.]+) (Receptions|Rush Yards|Receiving Yards)$", contract)
    name, ou, ln, mk = m.group(1), m.group(2), float(m.group(3)), m.group(4); k = int(ln + 0.5); word, col, unit = MW[mk]
    a, h = game.split(' @ '); s = ST[(ST.week == wk) & (ST.nn == core.nn(name)) & ST.team.isin([a, h])]
    actual = float(s.iloc[0][col]) if len(s) else 0.0
    won = actual > ln if ou == 'Over' else actual < ln
    assert won == (x.outcome == 'Won'), (contract, actual, x.outcome)
    line = f"{name} {k}+ {word} (Yes)" if ou == 'Over' else f"{name} under {k} {word} (No)"
    f = F10.get(line) if source == 'Week 10 card' else None
    return {'week': wk, 'source': source, 'game': game, 'team': s.iloc[0].team if len(s) else '', 'line': line, 'price': int(x.yes_price),
            'mid': f['mid'] if f and f.get('price') == int(x.yes_price) else None, 'outcome': x.outcome, 'result': f"W{wk}: {int(actual)} {unit}", 'profit_c': int(x.profit_c)}
REC = [{'week': r.week, 'source': 'Backtest', 'game': r.game, 'team': r.team, 'line': r.line, 'price': int(r.price), 'mid': r.mid, 'outcome': r.outcome,
        'result': r.result, 'profit_c': int(r.profit)} for r in PK[PK.decision == 'Final line'].itertuples()]
REC += [rec_row(w, g, c, 'Added') for w, g, c in ADDED] + [rec_row(w, g, c, 'Week 10 card') for w, g, c in CARD10]
REC = pd.DataFrame(REC); REC['k'] = REC.groupby(['week', 'line']).line.transform('size'); assert (REC.k == 1).all(), 'duplicate line'
REC = REC.drop(columns='k').sort_values(['week', 'source', 'game', 'line']).reset_index(drop=True); REC.insert(0, 'id', [f'FR{i + 1:03d}' for i in range(len(REC))])
REC.to_csv(W + 'rh/final_record.csv', index=False)
n = len(REC); w_ = int((REC.outcome == 'Won').sum()); cost = float(REC.price.sum()); prof = float(REC.profit_c.sum())
row = {'key': 'final_record', 'label': 'Final lines · Weeks 1–10', 'group': 'record', 'src': 'record', 'week': '', 'tier': 'final', 'wins': w_, 'losses': n - w_,
       'win_pct': round(100 * w_ / n, 1), 'avg_price': round(cost / n, 1), 'needed': round(cost / n + FEE, 1), 'ours': None, 'profit_c': int(prof), 'roi_pct': round(100 * prof / cost, 1),
       'added': int((REC.source == 'Added').sum()), 'thru': int(REC.week.max())}
SUM = pd.concat([SUM, pd.DataFrame([row])], ignore_index=True); SUM.to_csv(W + 'rh/card_bt_sum.csv', index=False)
pd.DataFrame([{k: row[k] for k in ('wins', 'losses', 'win_pct', 'roi_pct', 'profit_c', 'thru')}]).to_csv(W + 'rh/frec.csv', index=False)   # Home's headline numbers (public)
print('final record', f"{w_}-{n - w_}", row['win_pct'], f"{row['roi_pct']:+}%", REC.groupby('source').outcome.value_counts().unstack(fill_value=0).to_dict('index'))
