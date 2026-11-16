import numpy as np, pandas as pd, json
from scipy.optimize import minimize
P = pd.read_pickle('/home/claude/wedger/bt/pool.pkl')
P = P[(P.price.between(0.40, 0.60)) | (P.g5 == 'td')].copy()
lg = lambda p: np.log(np.clip(p, 1e-4, 1 - 1e-4) / (1 - np.clip(p, 1e-4, 1 - 1e-4))); sg = lambda z: 1 / (1 + np.exp(-z))
LV = ['pass', 'rec', 'recyd', 'rush', 'td']
def fit(d, lam=8.0):
    X = np.column_stack([(d.g5 == l).astype(float) for l in LV]); off = lg(d.price.values); y = d.y.values
    f = lambda b: -np.sum(y * np.log(sg(off + X @ b) + 1e-12) + (1 - y) * np.log(1 - sg(off + X @ b) + 1e-12)) + lam * np.sum(b ** 2)
    return minimize(f, np.zeros(len(LV))).x
b = fit(P); CAL = dict(zip(LV, np.round(b, 3)))
print('price-anchored shifts (all Weeks 6-8, ridge 8):', CAL, {k: round(float(sg(v)), 3) for k, v in CAL.items()})
json.dump({'cal_v5': CAL, 'n': int(len(P))}, open('/home/claude/wedger/bt/cal_v5.json', 'w'))
# LOWO pick test: posted-style rule (edge >= 3 pts vs the ask) under old (posted) vs new probabilities
rows = []
for wk in (6, 7, 8):
    tr, te = P[P.wk != wk], P[P.wk == wk].copy()
    bb = dict(zip(LV, fit(tr)))
    te['p_new'] = sg(lg(te.price.values) + te.g5.map(bb).values)
    te['noask'] = te.no_price.where(te.no_price.notna(), 1 - te.price + 0.01)
    for nm, col in (('new (price + over-bias shift, no read)', 'p_new'),):
        ey = te[col] - te.price; en = (1 - te[col]) - te.noask
        side = np.where(ey >= 0.03, 'Yes', np.where(en >= 0.03, 'No', ''))
        for s, y, pr, na in zip(side, te.y, te.price, te.noask):
            if not s: continue
            cost = pr if s == 'Yes' else na; win = y if s == 'Yes' else 1 - y
            rows.append((wk, nm, s, cost, win, (1 - cost) if win else -cost))
R = pd.DataFrame(rows, columns=['wk', 'rule', 'side', 'cost', 'win', 'pnl'])
print(R.groupby(['rule', 'wk']).agg(n=('win', 'size'), won=('win', 'mean'), roi=('pnl', lambda x: x.sum())).round(3))
print(R.groupby(['rule', 'side']).agg(n=('win', 'size'), won=('win', 'mean'), pnl=('pnl', 'sum'), cost=('cost', 'sum')).round(2))
tot = R.groupby('rule').agg(n=('win', 'size'), won=('win', 'mean'), pnl=('pnl', 'sum'), cost=('cost', 'sum')); tot['roi%'] = 100 * tot.pnl / tot.cost; print(tot.round(3))
# posted picks for reference (Week 8 only has posted picks in pool)
w8 = P[(P.wk == 8) & P.pick.isin(['Yes', 'No'])].copy()
w8['win'] = np.where(w8.pick == 'Yes', w8.y, 1 - w8.y); w8['cost'] = np.where(w8.pick == 'Yes', w8.price, w8.no_price)
print('posted Week 8 picks (props+ATD in pool):', len(w8), round(w8.win.mean(), 3), 'roi%', round(100 * (np.where(w8.win == 1, 1 - w8.cost, -w8.cost).sum() / w8.cost.sum()), 1))
