"""Leave-one-week-out tests of calibration / blending designs on every settled real line (Weeks 6-8, player props + ATD)."""
import numpy as np, pandas as pd
from scipy.optimize import minimize
P = pd.read_pickle('/home/claude/wedger/bt/pool.pkl')
P = P[(P.price.between(0.40, 0.60)) | (P.g5 == 'td')].copy()
lg = lambda p: np.log(np.clip(p, 1e-4, 1 - 1e-4) / (1 - np.clip(p, 1e-4, 1 - 1e-4))); sg = lambda z: 1 / (1 + np.exp(-z))
GROUPS = {'g4': lambda d: d.g5.replace({'rec': 'recv', 'recyd': 'recv'}), 'g5': lambda d: d.g5}
def design(d, grp):
    G = GROUPS[grp](d); levels = sorted(G.unique())
    return np.column_stack([(G == l).astype(float) for l in levels]), levels
def fit(off, X, y, lam, slope=False, prior=None):
    k = X.shape[1]; pr = np.zeros(k) if prior is None else prior
    def nll(b):
        s = b[-1] if slope else 1.0; bb = b[:k]
        p = sg(s * off + X @ bb)
        return -np.sum(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12)) + lam * np.sum((bb - pr) ** 2) + (lam * 4 * (s - 1) ** 2 if slope else 0)
    b0 = np.r_[np.zeros(k), [1.0]] if slope else np.zeros(k)
    return minimize(nll, b0, method='BFGS').x
def pred(b, off, X, slope=False):
    k = X.shape[1]; s = b[-1] if slope else 1.0
    return sg(s * off + X @ b[:k])
CALV3 = {'recv': -0.199, 'rec': -0.199, 'recyd': -0.199, 'rush': -0.393, 'td': -0.208, 'pass': 0.254}
br = lambda p, y: float(np.mean((p - y) ** 2)); ll = lambda p, y: float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
def evaluate(name, fn, sub=None):
    out = []
    d0 = P if sub is None else P[sub(P)]
    for wk in (6, 7, 8):
        tr, te = d0[d0.wk != wk], d0[d0.wk == wk]
        p = fn(tr, te); out.append((wk, len(te), br(p, te.y.values), ll(p, te.y.values)))
    n = sum(o[1] for o in out); B = sum(o[1] * o[2] for o in out) / n; L = sum(o[1] * o[3] for o in out) / n
    print(f'{name:46s} Brier {B:.4f}  LL {L:.4f}   ' + '  '.join(f'W{o[0]} {o[2]:.4f}' for o in out))
    return B
for label, sub in (('PLAYER PROPS 40-60c (no TD)', lambda d: d.g5 != 'td'), ('ALL incl. ATD', None)):
    print('====', label)
    evaluate('price (Yes ask)', lambda tr, te: te.price.values, sub)
    evaluate('market (books fair / RH mid)', lambda tr, te: te.mkt.values, sub)
    evaluate('v1 blend (85% mkt + 15% read)', lambda tr, te: te.v1.values, sub)
    evaluate('CAL_V3 as posted (fit W6-7)', lambda tr, te: sg(lg(te.v1.values) + te.g5.map(CALV3).values), sub)
    for grp in ('g4', 'g5'):
        for base in ('v1', 'mkt', 'price'):
            for lam in (2.0, 8.0, 20.0):
                def f(tr, te, grp=grp, base=base, lam=lam):
                    Xtr, lv = design(tr, grp); Xte, lv2 = design(te, grp)
                    # align columns
                    Xte = np.column_stack([(GROUPS[grp](te) == l).astype(float) for l in lv])
                    b = fit(lg(tr[base].values), Xtr, tr.y.values, lam)
                    return pred(b, lg(te[base].values), Xte)
                evaluate(f'shift by {grp} on {base}, ridge {lam:g}', f, sub)
    # blend weight sweep with refit g5 shifts
    for w in (0.85, 0.9, 0.95, 1.0):
        def f(tr, te, w=w):
            btr = lg(w * tr.mkt.values + (1 - w) * tr.ours.values); bte = lg(w * te.mkt.values + (1 - w) * te.ours.values)
            Xtr, lv = design(tr, 'g5'); Xte = np.column_stack([(te.g5 == l).astype(float) for l in lv])
            b = fit(btr, Xtr, tr.y.values, 8.0); return pred(b, bte, Xte)
        evaluate(f'market weight {w:.2f} + g5 shifts ridge 8', f, sub)
print('\nread value: corr(ours - mkt, y - mkt) by week')
for wk in (6, 7, 8):
    d = P[(P.wk == wk) & (P.g5 != 'td')]
    print(wk, len(d), round(np.corrcoef(d.ours - d.mkt, d.y - d.mkt)[0, 1], 3), '| model-only', round(np.corrcoef(d.model.fillna(d.mkt) - d.mkt, d.y - d.mkt)[0, 1], 3))
