"""v4 variants on every settled Week 6-7 line priced 40-60c: 85% price + 15% our read, calibration (icpt + rush/td/pass) fit on one week,
tested on the other; plus the role-matchup shift (fit on 2023-25 only). Writes rh/compare_v4.json."""
import json, re, unicodedata, numpy as np, pandas as pd
from scipy.optimize import minimize
S = '/home/claude/wedger/'
c = pd.read_csv(S + 'rh/calib_rows.csv'); c = c[c['wedger'].notna()].copy()
lg = lambda p: np.log(np.clip(p, 1e-4, 1 - 1e-4) / (1 - np.clip(p, 1e-4, 1 - 1e-4))); sg = lambda z: 1 / (1 + np.exp(-z))
G = {'rushyd': 'rush', 'rryd': 'rush', 'td': 'td', 'passyd': 'pass', 'passtd': 'pass', 'int': 'pass'}
c['g'] = c['stat'].map(lambda s: G.get(s, 'rec'))
X = np.column_stack([np.ones(len(c)), c['g'] == 'rush', c['g'] == 'td', c['g'] == 'pass']).astype(float)
y = c['y'].values.astype(float); wk = c['wk'].values; A = np.arange(len(c))
def fit(o, idx, lam=4.):
    f = lambda b: -np.sum(y[idx] * np.log(sg(o[idx] + X[idx] @ b)) + (1 - y[idx]) * np.log(1 - sg(o[idx] + X[idx] @ b))) + lam * np.sum(b[1:] ** 2) + 0.5 * lam * b[0] ** 2
    return minimize(f, np.zeros(4), method='BFGS').x
br = lambda p, m: float(np.mean((p[m] - y[m]) ** 2))
# role-matchup shift for these rows
rm = pd.read_pickle(S + 'arch/real_rows.pkl')
out = {'n': int(len(c)), 'price': round(br(c['price'].values, wk > 0), 4)}
def score(p_ours, wm=0.85, shift=None):
    o = lg(wm * c['price'].values + (1 - wm) * p_ours)
    r = {}
    for w in (6, 7):
        b = fit(o, A[wk != w]); z = o + X @ b
        if shift is not None: z = z + shift
        r[w] = br(sg(z), wk == w)
    return round((r[6] + r[7]) / 2, 4), round(r[6], 4), round(r[7], 4)
for tag, col in (('v1 standard', 'ours_cal'), ('l4', 'ours_l4'), ('v3', 'ours_v3'), ('ve 50%', 'ours_ve5'), ('ve 100%', 'ours_ve10'), ('adj defense', 'ours_dadj'), ('v4 (ve 50% + adj defense)', 'ours_v4')):
    p = c[col].fillna(c['ours_cal']).values
    out[tag] = {'avg': score(p)[0], 'W6': score(p)[1], 'W7': score(p)[2], 'corr_ours_minus_price_vs_y_minus_price': round(float(np.corrcoef(p - c['price'], y - c['price'])[0, 1]), 3)}
    for wm in (0.7, 1.0):
        out[tag][f'avg_w{int(wm*100)}'] = score(p, wm)[0]
# projections vs line: MAE of projection vs actual for yardage stats
json.dump(out, open(S + 'rh/compare_v4.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
