"""Compare the standard read, the last-4 (momentum) view and the role-adjusted v3 on every settled Week 6-7 line priced 40-60c.
Raw Brier, and Brier after the v2.1-style calibration (icpt + rush/td/pass shifts, ridge 4) fit on one week and tested on the other."""
import json, numpy as np, pandas as pd
from scipy.optimize import minimize
B = '/home/claude/wedger/rh/'
c = pd.read_csv(B + 'calib_rows.csv'); c = c[c['wedger'].notna()].copy()
lg = lambda p: np.log(np.clip(p, 1e-4, 1 - 1e-4) / (1 - np.clip(p, 1e-4, 1 - 1e-4))); sg = lambda z: 1 / (1 + np.exp(-z))
G = {'rushyd': 'rush', 'rryd': 'rush', 'td': 'td', 'passyd': 'pass', 'passtd': 'pass', 'int': 'pass'}
c['g'] = c['stat'].map(lambda s: G.get(s, 'rec'))
X = np.column_stack([np.ones(len(c)), c['g'] == 'rush', c['g'] == 'td', c['g'] == 'pass']).astype(float)
y = c['y'].values.astype(float); wk = c['wk'].values
def fit(o, idx, lam=4.):
    f = lambda b: -np.sum(y[idx] * np.log(sg(o[idx] + X[idx] @ b)) + (1 - y[idx]) * np.log(1 - sg(o[idx] + X[idx] @ b))) + lam * np.sum(b[1:] ** 2) + 0.5 * lam * b[0] ** 2
    return minimize(f, np.zeros(4), method='BFGS').x
br = lambda p, m: round(float(np.mean((p[m] - y[m]) ** 2)), 4)
out = {'n': int(len(c)), 'by_week_n': {int(w): int((wk == w).sum()) for w in (6, 7)}}
A = np.arange(len(c))
for name, col in (('price', 'price'), ('standard (v1 blend)', 'wedger'), ('last-4 view', 'wedger_l4'), ('v3 (recent role)', 'wedger_v3')):
    p = c[col].values
    r = {'raw_W6': br(p, wk == 6), 'raw_W7': br(p, wk == 7), 'raw_all': br(p, wk > 0)}
    if col != 'price':
        o = lg(p)
        for w in (6, 7):
            b = fit(o, A[wk != w]); r[f'cal_test_W{w}'] = br(sg(o + X @ b), wk == w)
        r['cal_test_avg'] = round((r['cal_test_W6'] + r['cal_test_W7']) / 2, 4)
        b = fit(o, A); r['coef_all'] = [round(float(v), 3) for v in b]
    out[name] = r
# the ours-only reads (no market blend): does the last-4 view carry signal of its own?
for name, col in (('ours standard', 'ours_cal'), ('ours last-4', 'ours_l4'), ('ours v3', 'ours_v3')):
    p = c[col].values; out[name] = {'raw_all': br(p, wk > 0), 'corr_with_y_minus_price': round(float(np.corrcoef(p - c['price'], y - c['price'])[0, 1]), 3)}
# role-changed lines only
m = c['role_v3'] != 1
out['role_lines'] = {'n': int(m.sum()), 'yes_rate': round(float(y[m].mean()), 3), 'price': round(float(c.loc[m, 'price'].mean()), 3),
                     'brier_v1': br(c['wedger'].values, m.values), 'brier_v3': br(c['wedger_v3'].values, m.values), 'brier_price': br(c['price'].values, m.values)}
json.dump(out, open(B + 'compare_variants.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
