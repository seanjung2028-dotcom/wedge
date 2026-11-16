"""Momentum study: does a player's last 4 games say more about his next game than his whole season?

Sample: player-games 2023-2026 (regular season) with 3+ earlier games this season with the same team, prop-relevant
roles only (season averages: rec yds >= 20, catches >= 2, rush yds >= 25 for RBs / >= 10 for QBs, pass yds >= 150).
A. Accuracy: mean absolute error of each predictor for the next game.
B. Persistence: how much of the gap between the last 4 and the season average carries into the next game
   (slope of next-game minus season average on last-4 minus season average), overall, by stat, by week and for
   volume (targets, carries) vs efficiency (yards per target or carry).
C. Best blend: weight on the last 4 vs the season average that minimizes error, fit on 2023-2024, tested on 2025-2026.
Writes mom/study.json.
"""
import json, numpy as np, pandas as pd
S = '/home/claude/wedger/'
F = pd.read_pickle(S + 'mom/feat.pkl')
MIN = {'recyd': 20, 'rec': 2, 'rryd': 40, 'passyd': 150, 'td': 0.25}
def keep(d):
    m = pd.Series(True, index=d.index)
    for st, lo in MIN.items(): m &= ~((d['stat'] == st) & (d['S'] < lo))
    m &= ~((d['stat'] == 'rushyd') & (d['pos'] == 'RB') & (d['S'] < 25)) & ~((d['stat'] == 'rushyd') & (d['pos'] == 'QB') & (d['S'] < 10))
    return d[m]
F = keep(F).copy()
F['wkb'] = pd.cut(F['week'], [0, 7, 11, 18], labels=['Wk 4-7', 'Wk 8-11', 'Wk 12-18'])
out = {'n': int(len(F)), 'by_stat_n': F['stat'].value_counts().to_dict()}
# A. accuracy
PRED = ['S', 'Smed', 'L4', 'L2', 'E2', 'E3', 'E4', 'C', 'P']
acc = {}
for st, d in F.groupby('stat'):
    r = {}
    for p in PRED:
        dd = d[d[p].notna()]
        r[p] = round(float((dd['y'] - dd[p]).abs().mean()), 3)
    # same-sample comparison (rows with P available)
    dd = d[d['P'].notna()]
    r['n'] = int(len(d)); r['n_withP'] = int(len(dd))
    acc[st] = r
out['mae'] = acc
# relative MAE vs season average (lower = better), all stats pooled with each stat scaled by its MAE(S)
rel = {}
for p in PRED:
    vals = []
    for st, d in F.groupby('stat'):
        dd = d[d[p].notna()]
        vals.append(float((dd['y'] - dd[p]).abs().mean() / (dd['y'] - dd['S']).abs().mean()))
    rel[p] = round(float(np.mean(vals)), 4)
out['mae_rel_to_S'] = rel
# B. persistence
def slope(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float); m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if len(x) < 30: return None
    b = np.polyfit(x, y, 1)[0]
    return round(float(b), 3)
per = {}
for st, d in F.groupby('stat'):
    per[st] = {'all': slope(d['L4'] - d['S'], d['y'] - d['S']), 'n': int(len(d))}
    for wb, dw in d.groupby('wkb', observed=True): per[st][str(wb)] = slope(dw['L4'] - dw['S'], dw['y'] - dw['S'])
    # among games where his season is already 6+ games deep (L4 genuinely differs from the season)
    dd = d[d['n'] >= 6]; per[st]['n6plus'] = slope(dd['L4'] - dd['S'], dd['y'] - dd['S'])
out['persistence'] = per
# volume vs efficiency: for yards stats
ve = {}
for st, vcol in (('recyd', 'tgt'), ('rushyd', 'car'), ('passyd', 'att')):
    d = F[(F['stat'] == st) & F['vS'].notna()].copy()
    d = d[d['vS'] > 0]
    gap_vol = (d['vL4'] - d['vS']) * d['effS']           # yards the volume change alone would add
    gap_eff = d['vS'] * (d['effL4'] - d['effS'])          # yards the efficiency change alone would add
    X = np.column_stack([np.ones(len(d)), gap_vol, gap_eff]); yv = (d['y'] - d['S']).values
    b = np.linalg.lstsq(X, yv, rcond=None)[0]
    # volume itself: does the next game's volume follow the last-4 volume?
    vb = slope(d['vL4'] - d['vS'], d['vy'] - d['vS'])
    ve[st] = {'volume_persist': round(float(b[1]), 3), 'efficiency_persist': round(float(b[2]), 3), 'volume_count_persist': vb, 'n': int(len(d))}
out['vol_vs_eff'] = ve
# snap-share change (role change) as a filter: persistence when snap share moved 10+ points
role = {}
for st, d in F.groupby('stat'):
    d = d[d['snapS'].notna() & d['snapL4'].notna()]
    ch = (d['snapL4'] - d['snapS']).abs() >= 10
    role[st] = {'role_change': slope(d[ch]['L4'] - d[ch]['S'], d[ch]['y'] - d[ch]['S']), 'n_change': int(ch.sum()),
                'stable_role': slope(d[~ch]['L4'] - d[~ch]['S'], d[~ch]['y'] - d[~ch]['S'])}
out['role'] = role
# C. best blend weight on L4 (fit 2023-24, test 2025-26)
bl = {}
for st, d in F.groupby('stat'):
    tr, te = d[d['season'] <= 2024], d[d['season'] >= 2025]
    ws = np.linspace(0, 1, 21)
    err = [float((tr['y'] - ((1 - w) * tr['S'] + w * tr['L4'])).abs().mean()) for w in ws]
    wb = float(ws[int(np.argmin(err))])
    # add last season / career as a third input: fit weights by least squares on train
    dd = tr[tr['C'].notna()]
    X = np.column_stack([dd['S'], dd['L4'], dd['C']]); bb = np.linalg.lstsq(X, dd['y'], rcond=None)[0]
    tt = te[te['C'].notna()]
    mae = lambda p: round(float((tt['y'] - p).abs().mean()), 3)
    bl[st] = {'w_L4': wb, 'test_mae_S': mae(tt['S']), 'test_mae_L4': mae(tt['L4']), 'test_mae_blend': mae((1 - wb) * tt['S'] + wb * tt['L4']),
              'test_mae_C': mae(tt['C']), 'lsq_w': [round(float(x), 3) for x in bb], 'test_mae_lsq': mae(np.column_stack([tt['S'], tt['L4'], tt['C']]) @ bb)}
out['blend'] = bl
json.dump(out, open(S + 'mom/study.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
