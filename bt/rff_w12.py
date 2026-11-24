"""Fit the random-features ridge projection on every player-game through Week 10 and project Week 12 (rh/rff_w12.json)."""
import numpy as np, pandas as pd, json
from scipy.optimize import minimize
W = '/home/claude/wedger/'
src = open(W + 'bt/rff.py').read(); exec(src[:src.index('results = []')])
F = pd.read_pickle(W + 'arch/feat_w12.pkl'); F['dome'] = F['roof'].isin(['dome', 'closed']).astype(float)
nxt = (F.season == 2026) & (F.week == 12)
dfn = pd.read_pickle(W + 'arch/def_g.pkl'); off = pd.read_pickle(W + 'arch/off_g.pkl')
D26 = dfn[dfn.season == 2026].groupby('team')[['man', 'blitz', 'ay_allowed', 'deep_allowed', 'mid_allowed', 'pass_epa', 'rush_epa', 'box8', 'ypc']].mean()
O26 = off[off.season == 2026].groupby('team')[['proe', 'pa_rate', 'motion', 'pass_rate', 'epa']].mean()
for c in D26.columns: F['d_' + c] = F['d_' + c].astype(float); F.loc[nxt, 'd_' + c] = F.loc[nxt, 'opp'].map(D26[c]).astype(float).values
F.loc[nxt, 'd_n'] = 10
for c in O26.columns: F['o_' + c] = F['o_' + c].astype(float); F.loc[nxt, 'o_' + c] = F.loc[nxt, 'team'].map(O26[c]).astype(float).values
F.loc[nxt, 'o_n'] = 9
PRM = {'rushyd': {'z': 10, 'gamma': 0.5}, 'recyd': {'z': 10, 'gamma': 0.5}, 'rec': {'z': 10, 'gamma': 0.5}, 'passyd': {'z': 10, 'gamma': 1.0}}
sg = lambda z: 1 / (1 + np.exp(-z))
OUT = {}
for st, prm in PRM.items():
    d = F[F.stat == st]; tr = d[~((d.season == 2026) & (d.week == 12))]; te = d[(d.season == 2026) & (d.week == 12)]
    Xtr, cc = matrix(tr); Xte, _ = matrix(te, cc); Gtr, Gte = standardize(Xtr, Xte)
    ytr = (tr.y - tr.base).values.astype(np.float32); mu = ytr.mean()
    p = fit_predict(Gtr, ytr - mu, Gte, 'rff', P=3000, draws=5, **prm) + mu
    # projected margin -> P(over) map, fit on the 2025 out-of-sample fold
    # 2025 out-of-sample fold (train 2023-24), refit here with the same settings
    t5, e5 = d[d.season <= 2024], d[(d.season == 2025) & d.line.notna()]
    X5, c5 = matrix(t5); Xe5, _ = matrix(e5, c5); G5, Ge5 = standardize(X5, Xe5)
    y5 = (t5.y - t5.base).values.astype(np.float32); m5 = y5.mean()
    p5 = e5.base.values + fit_predict(G5, y5 - m5, Ge5, 'rff', P=3000, draws=3, **prm) + m5
    sc = e5.y.std(); x = ((p5 - e5.line.values) / sc); y = (e5.y > e5.line).astype(float).values
    b = minimize(lambda b: -np.sum(y * np.log(sg(b[0] + b[1] * x) + 1e-12) + (1 - y) * np.log(1 - sg(b[0] + b[1] * x) + 1e-12)), [0, 1]).x
    for nm, tm, base, line, pp in zip(te.name, te.team, te.base, te.line, te.base.values + p):
        OUT[f'{nm}|{tm}|{st}'] = {'rff': round(float(pp), 2), 'base': round(float(base), 2), 'line': float(line)}
    OUT[f'_map|{st}'] = {'a': float(b[0]), 'b': float(b[1]), 'sc': float(sc)}
    print(st, len(te), 'mean adj vs book-style base', round(float(np.mean(p)), 2), 'map', np.round(b, 3))
json.dump(OUT, open(W + 'rh/rff_w12.json', 'w'))
print(len(OUT))
