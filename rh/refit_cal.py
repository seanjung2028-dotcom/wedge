"""Refit the Wedger v2 calibration on every settled Week 6-7 line priced 40-60c (calib_rows.csv, v1 base = 'wedger').

logit(P) = logit(P_v1) + icpt + rush*[rush/R+R] + td*[ATD] + pass*[passing/INT] + thin*[<12 games with team]
Fit by maximum likelihood with a light ridge (shrinks each shift toward 0). Compared by 5-fold CV (repeated) and by
leave-one-week-out against: v1, the Sunday (Oct 25) shifts, price alone, and a variant with a slope on logit(P_v1).
"""
import json, math, sys
import numpy as np, pandas as pd
from scipy.optimize import minimize
B = '/home/claude/wedger/rh/'
c = pd.read_csv(B + 'calib_rows.csv')
c = c[c['wedger'].notna()].copy()
lg = lambda p: np.log(np.clip(p, 1e-4, 1 - 1e-4) / (1 - np.clip(p, 1e-4, 1 - 1e-4)))
sg = lambda z: 1 / (1 + np.exp(-z))
GRP = {'rushyd': 'rush', 'rryd': 'rush', 'td': 'td', 'passyd': 'pass', 'passtd': 'pass', 'int': 'pass'}
c['g'] = c['stat'].map(lambda s: GRP.get(s, 'rec'))
X = np.column_stack([np.ones(len(c)), (c['g'] == 'rush'), (c['g'] == 'td'), (c['g'] == 'pass'), (c['n_games'] < 12)]).astype(float)
off = lg(c['wedger'].values); y = c['y'].values.astype(float); price = c['price'].values; wk = c['wk'].values
NAMES = ['icpt', 'rush', 'td', 'pass', 'thin']
OLD = np.array([-0.079, -0.357, -0.328, 0.422, -0.514])

def fit(idx, lam=2.0, slope=False):
    Xi, oi, yi = X[idx], off[idx], y[idx]
    def nll(b):
        s = b[-1] if slope else 1.0; bb = b[:-1] if slope else b
        z = s * oi + Xi @ bb; p = sg(z)
        return -np.sum(yi * np.log(p + 1e-12) + (1 - yi) * np.log(1 - p + 1e-12)) + lam * np.sum(bb[1:] ** 2) + lam * 0.5 * bb[0] ** 2 + (lam * (s - 1) ** 2 if slope else 0)
    b0 = np.zeros(X.shape[1] + (1 if slope else 0)); b0[-1] = 1.0 if slope else 0.0
    return minimize(nll, b0, method='BFGS').x
def pred(b, idx, slope=False):
    s = b[-1] if slope else 1.0; bb = b[:-1] if slope else b
    return sg(s * off[idx] + X[idx] @ bb)
brier = lambda p, yy: float(np.mean((p - yy) ** 2))
ll = lambda p, yy: float(-np.mean(yy * np.log(p) + (1 - yy) * np.log(1 - p)))
allx = np.arange(len(c))
res = {}
for lam in (0.0, 1.0, 2.0, 4.0, 8.0):
    for slope in (False, True):
        cv = []
        for rep in range(20):
            rng = np.random.default_rng(rep); perm = rng.permutation(len(c)); folds = np.array_split(perm, 5)
            P = np.zeros(len(c))
            for f in folds:
                tr = np.setdiff1d(allx, f); b = fit(tr, lam, slope); P[f] = pred(b, f, slope)
            cv.append(brier(P, y))
        lowo = {}
        for w in (6, 7):
            tr, te = allx[wk != w], allx[wk == w]; b = fit(tr, lam, slope); lowo[w] = brier(pred(b, te, slope), y[te])
        res[(lam, slope)] = (float(np.mean(cv)), lowo)
v1 = sg(off); oldp = sg(off + X @ OLD)
print('rows', len(c), 'by week', pd.Series(wk).value_counts().to_dict(), 'yes rate', round(y.mean(), 3), 'avg price', round(price.mean(), 3))
print('baselines  in-sample brier: price %.4f  v1 %.4f  old-v2 %.4f' % (brier(price, y), brier(v1, y), brier(oldp, y)))
for w in (6, 7):
    m = wk == w; print(f'  week {w}: n={m.sum()} price %.4f v1 %.4f old-v2 %.4f' % (brier(price[m], y[m]), brier(v1[m], y[m]), brier(oldp[m], y[m])))
for k, (cvb, lowo) in res.items(): print('lam', k[0], 'slope', k[1], 'CV %.4f' % cvb, 'train W7->test W6 %.4f, train W6->test W7 %.4f' % (lowo[6], lowo[7]))
LAM = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
b = fit(allx, LAM, False); newp = pred(b, allx)
coef = dict(zip(NAMES, [round(float(v), 3) for v in b]))
print('final (lam %.1f):' % LAM, coef, 'in-sample %.4f' % brier(newp, y))
# effect at 50c for each group
for g, j in (('receiving', None), ('rush', 1), ('td', 2), ('pass', 3)):
    z = b[0] + (b[j] if j else 0); print(f'  {g}: 50c -> {100 * sg(z):.1f}; thin -> {100 * sg(z + b[4]):.1f}')
json.dump({'base': 'wedger', 'lam': LAM, 'rows': int(len(c)), **{k: float(v) for k, v in zip(NAMES, b)},
           'cv': {f'{k[0]}|{k[1]}': v for k, v in res.items()}}, open(B + 'wedger_v2_coef_1026.json', 'w'), default=str, indent=1)
