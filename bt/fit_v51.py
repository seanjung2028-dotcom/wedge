"""v5.1: split the passing group (passing yards / passing TDs / interceptions were lumped, like receptions with receiving yards in v4).
Same price-anchored ridge fit as final_fit.py; compares held-out Brier and picks for the v5 vs v5.1 groupings."""
import numpy as np, pandas as pd, json
from scipy.optimize import minimize
P = pd.read_pickle('/home/claude/wedger/bt/pool.pkl')
P = P[(P.price.between(0.40, 0.60)) | (P.g5 == 'td')].copy()
G51 = {'passyd': 'passyd', 'passtd': 'passtd', 'int': 'int', 'rec': 'rec', 'recyd': 'recyd', 'rushyd': 'rush', 'rryd': 'rush', 'td': 'td'}
P['g51'] = P.stat.map(G51)
lg = lambda p: np.log(np.clip(p, 1e-4, 1 - 1e-4) / (1 - np.clip(p, 1e-4, 1 - 1e-4))); sg = lambda z: 1 / (1 + np.exp(-z))
def fit(d, col, LV, lam=8.0):
    X = np.column_stack([(d[col] == l).astype(float) for l in LV]); off = lg(d.price.values); y = d.y.values
    f = lambda b: -np.sum(y * np.log(sg(off + X @ b) + 1e-12) + (1 - y) * np.log(1 - sg(off + X @ b) + 1e-12)) + lam * np.sum(b ** 2)
    return dict(zip(LV, minimize(f, np.zeros(len(LV))).x))
SPEC = {'v5': ('g5', ['pass', 'rec', 'recyd', 'rush', 'td']), 'v5.1': ('g51', ['passyd', 'passtd', 'int', 'rec', 'recyd', 'rush', 'td'])}
res = []
for nm, (col, LV) in SPEC.items():
    for wk in (6, 7, 8):
        tr, te = P[P.wk != wk], P[P.wk == wk].copy()
        b = fit(tr, col, LV); p = sg(lg(te.price.values) + te[col].map(b).values)
        te['p'] = p; te['noask'] = te.no_price.where(te.no_price.notna(), 1 - te.price + 0.01)
        ey = te.p - te.price; en = (1 - te.p) - te.noask
        side = np.where(ey >= 0.03, 'Yes', np.where(en >= 0.03, 'No', ''))
        for s, y, pr, na, pp, st in zip(side, te.y, te.price, te.noask, te.p, te.stat):
            cost = pr if s == 'Yes' else na; win = (y if s == 'Yes' else 1 - y) if s else np.nan
            res.append((nm, wk, st, (pp - y) ** 2, (pr - y) ** 2, s, cost, win, ((1 - cost) if win else -cost) if s else 0.0))
R = pd.DataFrame(res, columns=['m', 'wk', 'stat', 'brier', 'brier_px', 'side', 'cost', 'win', 'pnl'])
print(R.groupby('m')[['brier', 'brier_px']].mean().round(4))
print(R[R.stat.isin(['passyd', 'passtd', 'int'])].groupby(['m', 'stat'])[['brier', 'brier_px']].mean().round(4))
pk = R[R.side != '']
t = pk.groupby('m').agg(n=('win', 'size'), won=('win', 'mean'), pnl=('pnl', 'sum'), cost=('cost', 'sum')); t['roi%'] = 100 * t.pnl / t.cost; print(t.round(3))
print(pk[pk.stat.isin(['passtd', 'int', 'passyd'])].groupby(['m', 'stat']).agg(n=('win', 'size'), won=('win', 'mean'), pnl=('pnl', 'sum')).round(3))
b = fit(P, 'g51', SPEC['v5.1'][1]); CAL = {k: round(float(v), 3) for k, v in b.items()}
print('v5.1 all weeks:', CAL, {k: round(100 * float(sg(v)), 1) for k, v in CAL.items()})
json.dump({'cal_v5': CAL, 'n': int(len(P)), 'groups': G51}, open('/home/claude/wedger/bt/cal_v51.json', 'w'))
