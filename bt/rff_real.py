"""Does the random-features projection add information on REAL lines (Weeks 6-8)?"""
import pandas as pd, numpy as np, re, unicodedata, glob
from scipy.optimize import minimize
W = '/home/claude/wedger/'
def nn(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', s); return re.sub(r'[^a-z]', '', s)
pr = pd.concat([pd.read_pickle(f) for f in [W + 'bt/rff_preds_rushyd.pkl', W + 'bt/rff_preds_recyd_rec_passyd.pkl']])
sg = lambda z: 1 / (1 + np.exp(-z)); lg = lambda p: np.log(np.clip(p, 1e-4, 1 - 1e-4) / (1 - np.clip(p, 1e-4, 1 - 1e-4)))
# map projected margin -> P(over) with a logistic fit on the 2025 out-of-sample fold (book-style lines)
MAP = {}
for st, d in pr[pr.fold == '2025'].groupby('stat'):
    sc = d.y.std()
    for col in ('p_rff', 'p_lin', 'base'):
        x = ((d[col] - d.line) / sc).values; y = (d.y > d.line).astype(float).values
        f = lambda b: -np.sum(y * np.log(sg(b[0] + b[1] * x) + 1e-12) + (1 - y) * np.log(1 - sg(b[0] + b[1] * x) + 1e-12))
        MAP[(st, col)] = (minimize(f, [0, 1]).x, sc)
P = pd.read_pickle(W + 'bt/pool.pkl')
P = P[P.stat.isin(['rec', 'recyd', 'rushyd', 'passyd']) & P.price.between(0.4, 0.6)].copy()
P['k'] = P.player.map(nn)
q = pr[pr.season == 2026].copy(); q['k'] = q.name.map(nn)
M = P.merge(q[['k', 'week', 'stat', 'p_rff', 'p_lin', 'base']], left_on=['k', 'wk', 'stat'], right_on=['k', 'week', 'stat'], how='left')
print('matched', M.p_rff.notna().sum(), 'of', len(M))
M = M[M.p_rff.notna()].copy()
for col in ('p_rff', 'p_lin', 'base'):
    M['P_' + col] = [sg(MAP[(s, col)][0][0] + MAP[(s, col)][0][1] * (v - l) / MAP[(s, col)][1]) for s, v, l in zip(M.stat, M[col], M.line)]
print('\ncorr(P_x - price, y - price) by week   [our read for comparison: ours - mkt]')
for wk in (6, 7, 8):
    d = M[M.wk == wk]
    print(wk, len(d), ' rff', round(np.corrcoef(d.P_p_rff - d.price, d.y - d.price)[0, 1], 3), ' linear', round(np.corrcoef(d.P_p_lin - d.price, d.y - d.price)[0, 1], 3),
          ' book-style base', round(np.corrcoef(d.P_base - d.price, d.y - d.price)[0, 1], 3), ' our read', round(np.corrcoef(d.ours - d.mkt, d.y - d.mkt)[0, 1], 3),
          ' our proj-line', round(np.corrcoef((d.proj - d.line) / d.line.clip(lower=1), d.y - d.price)[0, 1], 3), ' rff proj-line', round(np.corrcoef((d.p_rff - d.line) / d.line.clip(lower=1), d.y - d.price)[0, 1], 3))
d = M
print('all', len(d), ' rff', round(np.corrcoef(d.P_p_rff - d.price, d.y - d.price)[0, 1], 3), ' our read', round(np.corrcoef(d.ours - d.mkt, d.y - d.mkt)[0, 1], 3))
print('\nprojection MAE on real lines (actual from feat y):')
y_act = q.set_index(['k', 'week', 'stat'])['y']
M['actual'] = [y_act.get((k, w, s), np.nan) for k, w, s in zip(M.k, M.wk, M.stat)]
for st, d in M.dropna(subset=['actual']).groupby('stat'):
    print(f"{st:7s} n={len(d):4d}  line {np.mean(abs(d.actual - d.line)):6.1f}  our proj {np.mean(abs(d.actual - d.proj)):6.1f}  book-style base {np.mean(abs(d.actual - d.base)):6.1f}  rff {np.mean(abs(d.actual - d.p_rff)):6.1f}   RMSE line {np.sqrt(np.mean((d.actual - d.line) ** 2)):6.1f} ours {np.sqrt(np.mean((d.actual - d.proj) ** 2)):6.1f} rff {np.sqrt(np.mean((d.actual - d.p_rff) ** 2)):6.1f}")
M.to_pickle(W + 'bt/real_rff.pkl')
