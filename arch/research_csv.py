"""Flatten the Oct 27 evening research for the Charts tab: rh/research.csv (recency curves, defense signal, big single games,
model variants) and rh/cats.csv (role / script / scheme categories vs the book-style line)."""
import json, numpy as np, pandas as pd
S = '/home/claude/wedger/'
rows = []
def add(section, key, label, value, value2='', n='', note=''): rows.append({'section': section, 'key': key, 'label': label, 'value': value, 'value2': value2, 'n': n, 'note': note})
rc = json.load(open(S + 'arch/recency.json'))
NM = {'WR rec': 'WR targets → yds/target', 'TE rec': 'TE targets → yds/target', 'RB rush': 'RB carries → yds/carry', 'RB rec': 'RB targets → yds/target', 'QB pass': 'QB attempts → yds/attempt'}
for k, v in rc.items():
    vb, eb = v['volume_best'], v['efficiency_best']
    add('recency_best', k, NM[k], vb['half_life_games'], eb['half_life_games'], v['n'], f"volume prior-season factor {vb['season_factor']}; efficiency shrink {eb['shrink_units']} units toward the position average, prior-season factor {eb['season_factor']}")
    mv = min(x[2] for x in v['volume_grid']); me = min(x[2] for x in v['efficiency_grid_hl'])
    for sf, hl, e in v['volume_grid']: add('recency_vol', f'{k}|{hl}', k, hl, round(100 * (e / mv - 1), 2), v['n'])
    for hl, kk, e in v['efficiency_grid_hl']: add('recency_eff', f'{k}|{hl}', k, hl, round(100 * (e / me - 1), 2), v['n'])
    me2 = min(x[2] for x in v['efficiency_grid_k'])
    for hl, kk, e in v['efficiency_grid_k']: add('recency_shrink', f'{k}|{kk}', k, kk, round(100 * (e / me2 - 1), 2), v['n'])
di = json.load(open(S + 'arch/defense_iso.json'))
SIGL = {'d_raw': 'Raw yards allowed (defense vs position)', 'd_resid': 'Allowed vs each opponent’s own average', 'd_same': 'Same, only opponents with his role',
        'd_c_vol': 'Extra volume allowed (carries / targets)', 'd_c_eff': 'Extra yards per touch allowed', 'd_c_ybc': 'Blocking: yards before contact allowed',
        'd_c_yac': 'The runners: yards after contact', 'd_c_xry': 'NGS expected rush yards (blocking, box, defenders)', 'd_c_ryoe': 'NGS rush yards over expected (the runner)',
        'd_last1': 'Only the most recent opponent'}
for grp, v in di.items():
    if grp.startswith('_'): continue
    for c, lab in SIGL.items():
        x = v.get(c)
        if x: add('def_signal', f'{grp}|{c}', lab, x['slope'], x['r'], x['n'], grp)
    for c in ('oos_d_raw', 'oos_d_resid'):
        x = v.get(c)
        if x: add('def_oos', f'{grp}|{c}', grp, x['gain_pct'], x['k'], '', c)
for grp, v in di['_big_single_game'].items():
    for k2, x in v.items():
        if isinstance(x, dict) and x.get('n'): add('big_game', f'{grp}|{k2}', k2.replace('_', ' '), x['next_resid'], '', x['n'], grp)
cv = json.load(open(S + 'rh/compare_v4.json'))
for k, v in cv.items():
    if isinstance(v, dict): add('variants', k, k, v['avg'], v.get('corr_ours_minus_price_vs_y_minus_price', ''), cv['n'], 'Brier, fit on one week tested on the other (85% price)')
add('variants', 'price', 'Price alone', cv['price'], '', cv['n'], '')
rm = json.load(open(S + 'arch/rm_eval.json'))
add('rm', 'real_base', 'Wedger % (v3)', rm['real']['wedger_v3'], '', rm['real']['n'], 'real Week 6-7 prices')
add('rm', 'real_rm', 'Wedger % + role & matchup history', rm['real']['wedger_v3_plus_rm0.5'], '', rm['real']['n'], 'shift fit on 2023-25 only, weight 0.5')
add('rm', 'real_price', 'Price alone', rm['real']['price'], '', rm['real']['n'], '')
for q in rm['quintiles_2026']: add('rm_q', str(q['q']), f"Fifth {q['q'] + 1}", round(100 * q['pred'], 1), round(100 * q['actual'], 1), q['n'], '2026 Weeks 1-7, modeled lines')
pd.DataFrame(rows).to_csv(S + 'rh/research.csv', index=False)
C = pd.read_csv(S + 'arch/categories_all.csv')
C = C[C['n_season'] >= 20].copy()
C['kind'] = np.where(C['above50'], 'over', np.where(C['under60'], 'under', ''))
C['held'] = np.where(C['kind'] == 'over', C['held'], np.where(C['kind'] == 'under', C['held_under'], False))
C['label'] = C['label'].str.replace(' yds', ' yards')
C[['dim', 'pos', 'stat', 'label', 'n_season', 'over_season', 'n_w47', 'over_w47', 'n_hist', 'over_hist', 'base_season', 'base_hist', 'kind', 'held']].to_csv(S + 'rh/cats.csv', index=False)
print(len(rows), 'research rows;', len(C), 'categories;', C['kind'].value_counts().to_dict(), 'held', int(C['held'].sum()))
