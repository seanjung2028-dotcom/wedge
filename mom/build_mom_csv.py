"""Flatten the momentum study into rh/mom_summary.csv (charts) and rh/team_mom.csv (team first-4 vs last-4)."""
import json, csv, pandas as pd
S = '/home/claude/wedger/'
st = json.load(open(S + 'mom/study.json')); hs = json.load(open(S + 'mom/hist_sim.json')); ra = json.load(open(S + 'mom/real_analysis.json'))
cv = json.load(open(S + 'rh/compare_variants.json')); tm = json.load(open(S + 'mom/team.json'))
SL = {'recyd': 'Receiving yards', 'rec': 'Receptions', 'rushyd': 'Rushing yards', 'rryd': 'Rush + rec yards', 'passyd': 'Passing yards', 'td': 'Touchdowns'}
rows = []
def add(section, key, label, value, n='', value2='', note=''):
    rows.append({'section': section, 'key': key, 'label': label, 'value': value, 'value2': value2, 'n': n, 'note': note})
# 1. persistence: share of the last-4 vs season gap that shows up next game
for s in ('recyd', 'rec', 'rushyd', 'passyd', 'td'):
    p = st['persistence'][s]; r = st['role'][s]
    add('persist', f'{s}|all', SL[s], round(100 * p['all']), p['n'], note='all player-games')
    add('persist_role', f'{s}|role', SL[s], round(100 * r['role_change']), r['n_change'], round(100 * r['stable_role']), 'role change vs stable role')
for s, v in st['vol_vs_eff'].items():
    add('persist_ve', s, SL[s], round(100 * v['volume_persist']), v['n'], round(100 * v['efficiency_persist']), 'volume vs efficiency')
# 2. accuracy of each predictor (error vs the season average = 100)
LAB = {'L2': 'Last 2 games', 'L4': 'Last 4 games', 'E2': 'Recent-weighted (half-life 2)', 'E4': 'Recent-weighted (half-life 4)', 'S': 'Season average',
       'Smed': 'Season median', 'P': 'Last season', 'C': 'Multi-season, weighted'}
for k in ('L2', 'L4', 'E2', 'E4', 'S', 'Smed', 'P', 'C'):
    add('accuracy', k, LAB[k], round(100 * st['mae_rel_to_S'][k], 1), st['n'])
# blend: average test-error ratio of the least-squares blend vs season average across stats (2025-26 test)
bl = st['blend']; ratio = sum(bl[s]['test_mae_lsq'] / bl[s]['test_mae_S'] for s in bl) / len(bl)
add('accuracy', 'blend', 'Season + last 4 + multi-season blend', round(100 * ratio, 1), note='fit 2023-24, tested 2025-26')
# 3. books' weights vs best weights
for s in ('recyd', 'rec', 'rushyd'):
    f = ra['line_fit'][s]; b = bl[s]['lsq_w']
    add('weights', f'{s}|books', SL[s], f'{f["w_S"]:.2f}|{f["w_L4"]:.2f}|{f["w_C"]:.2f}', f['n'], round(f['r2'], 2), 'books: season | last 4 | multi-season (R²)')
    add('weights', f'{s}|best', SL[s], f'{b[0]:.2f}|{b[1]:.2f}|{b[2]:.2f}', '', '', 'best predictor weights 2023-24')
# 4. momentum types vs a book-style line, 2023-26
CAT = ['Role up (snaps +10)', 'Volume up', 'Efficiency-only up', 'Stable', 'Efficiency-only down', 'Volume down', 'Role down (snaps -10)']
for s in ('recyd', 'rec', 'rushyd'):
    for c in CAT:
        x = hs[s].get(c)
        if x: add('hist_cat', f'{s}|{c}', c, x['vs_base'], x['n'], x['over'], SL[s])
# 5. real Week 6-7 prices by momentum
for k, v in ra['momentum_real'].items():
    if v.get('n'): add('real_cat', k, k, v['hit'], v['n'], v['price'], f"edge {v['edge']:+.1f}")
# 6. model variants on real lines (trained on one week, tested on the other)
for k, lab in (('price', 'Price alone'), ('standard (v1 blend)', 'Standard read (70/30)'), ('last-4 view', 'Last-4 momentum view'), ('v3 (recent role)', 'v3: recent-role factor')):
    v = cv[k]
    add('variants', k, lab, v.get('cal_test_W7', v['raw_W7']), cv['by_week_n']['7'], v.get('cal_test_W6', v['raw_W6']), 'Brier, Week 7 | Week 6 (lower is better)')
# 7. team momentum
add('team', 'persist_epa', 'Team offense EPA/play', round(100 * tm['persist_epa']), note='share of last-4 gap carried into next game, 2023-25')
for k, v in tm['pts_vs_implied_by_momentum'].items():
    add('team_pts', k, k, v['avg_beat_implied'], v['n'], note='points vs books implied team total')
with open(S + 'rh/mom_summary.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['section', 'key', 'label', 'value', 'value2', 'n', 'note']); w.writeheader(); w.writerows(rows)
# team first-4 vs last-4, with Week 8 opponent
g = pd.read_csv(S + 'dl8/games.csv'); g = g[(g['season'] == 2026) & (g['week'] == 8)]
FX = {'LA': 'LAR', 'WAS': 'WSH'}
opp = {}
for r in g.itertuples(index=False):
    a, h = FX.get(r.away_team, r.away_team), FX.get(r.home_team, r.home_team); opp[a] = '@' + h; opp[h] = 'vs ' + a
T = []
for r in tm['teams_2026']:
    T.append({**r, 'week8': opp.get(r['team'], 'Bye')})
with open(S + 'rh/team_mom.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(T[0].keys())); w.writeheader(); w.writerows(T)
print(len(rows), 'summary rows;', len(T), 'teams')
