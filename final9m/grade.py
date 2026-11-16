"""Grade the Week 9 final card's Sunday lines from the box scores and swap in the Monday BUF @ MIN re-run.
Writes final9/final_w9.json and final9/final_w9.csv (Saturday versions kept as *_sat.*)."""
import json, csv, re, shutil, os, unicodedata
import pandas as pd
W = '/home/claude/wedger/'
for f in ('final_w9.json', 'final_w9.csv'):
    sat = W + 'final9/' + f.replace('.', '_sat.')
    if not os.path.exists(sat): shutil.copy(W + 'final9/' + f, sat)
F = json.load(open(W + 'final9/final_w9_sat.json'))
rows = list(csv.DictReader(open(W + 'final9/final_w9_sat.csv')))
M = json.load(open(W + 'final9m/card_BUFMIN.json'))
def nn(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', s); return re.sub(r'[^a-z]', '', s)
FIX = {'LA': 'LAR', 'WAS': 'WSH'}; fx = lambda t: FIX.get(t, t)
st = pd.read_csv(W + 'dl18/stats_player_week_2026.csv', low_memory=False); st = st[(st.week == 9) & (st.season_type == 'REG')]
P = {nn(r.player_display_name): r for r in st.itertuples(index=False)}
sn = pd.read_csv(W + 'dl18/snap_counts_2026.csv'); sn = sn[sn.week == 9]; PLAYED = {nn(x) for x, o in zip(sn.player, sn.offense_snaps) if (o or 0) > 0}
g = pd.read_csv(W + 'dl18/games.csv'); g = g[(g.season == 2026) & (g.week == 9) & g.home_score.notna()]
SC = {f"{fx(r.away_team)} @ {fx(r.home_team)}": f"{fx(r.away_team)} {int(r.away_score)}, {fx(r.home_team)} {int(r.home_score)}" for r in g.itertuples(index=False)}
COL = {'passing yards': ('passing_yards', 'pass yds'), 'rushing yards': ('rushing_yards', 'rush yds'), 'receiving yards': ('receiving_yards', 'rec yds'), 'receptions': ('receptions', 'rec')}
def grade(line, player=None):
    m = re.match(r'^(.*?) (under )?(\d+)\+? (passing yards|rushing yards|receiving yards|receptions) \((Yes|No)\)$', line)
    nm, under, k, stat, side = m.group(1), bool(m.group(2)), int(m.group(3)), m.group(4), m.group(5)
    nm = player or nm; key = nn(nm); r = P.get(key)
    if r is None and key not in PLAYED: return 'Void', None, 'did not play'
    col, unit = COL[stat]; v = 0 if r is None else int(getattr(r, col) or 0)
    hit = v >= k; won = hit if side == 'Yes' else not hit
    return ('Won' if won else 'Lost'), v, f'{v} {unit}'
summ = {'Final line': [0, 0, 0], 'Conditional lean': [0, 0, 0]}
cards = []
for c in F['cards']:
    if c['game'] == 'BUF @ MIN': c = M['card']
    c['status'] = 'Final'; c['score'] = SC.get(c['game'], '')
    for p in c['plays']:
        out, v, det = grade(p['line'], p['player'])
        prof = 0 if out == 'Void' else (100 - p['price'] if out == 'Won' else -p['price'])
        p['result'] = {'outcome': out, 'actual': v, 'text': det, 'profit_c': prof}
        s = summ[p['decision']]; s[0] += out == 'Won'; s[1] += out == 'Lost'; s[2] += prof
    cards.append(c)
F['cards'] = [c for c in cards if c.get('status') != 'Final'] + [c for c in cards if c.get('status') == 'Final']  # Monday first, then the graded games
F['mnf_at'] = M['card']['plays'][0]['checked'] if M['card']['plays'] else F['at']
F['graded'] = {'thru': 'Week 9', 'final': summ['Final line'], 'lean': summ['Conditional lean']}
json.dump(F, open(W + 'final9/final_w9.json', 'w'), ensure_ascii=False)
out_rows = []
for r in rows:
    if r['game'] == 'BUF @ MIN': continue
    o, v, det = grade(r['line'])
    r['result'] = f"{o}: {det}"
    # the read: did the stat land on the side of the market's midpoint our evidence pointed to?
    try:
        mm = re.search(r'(under )?(\d+)\+? ', r['line']); k = int(mm.group(2))
        sh = float(r['shift'] or 0)
        if v is None or sh == 0: r['grade_read'] = 'n/a'
        else:
            # market midpoint at this rung is market_mid; our side is Yes if shift > 0
            r['grade_read'] = 'Right direction' if ((v >= k) == (sh > 0)) else 'Wrong direction'
    except Exception: r['grade_read'] = ''
    r['grade_price'] = 'No closing price logged'
    out_rows.append(r)
for r in M['csv']:
    o, v, det = grade(r['line']); r['result'] = f"{o}: {det}"
    mm = re.search(r'(under )?(\d+)\+? ', r['line']); k = int(mm.group(2)); sh = float(r['shift'] or 0)
    r['grade_read'] = 'n/a' if (v is None or sh == 0) else ('Right direction' if ((v >= k) == (sh > 0)) else 'Wrong direction')
    r['grade_price'] = 'No closing price logged'; out_rows.append(r)
with open(W + 'final9/final_w9.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(out_rows)
print('summary', summ)
for c in cards:
    for p in c['plays']: print(f"{c['game']:10s} {p['decision'][:5]} {p['line'][:52]:52s} {p['price']:3d}¢ {p.get('result', {}).get('outcome', 'open'):5s} {p.get('result', {}).get('text', '')}")
print(len(out_rows), 'csv rows')
