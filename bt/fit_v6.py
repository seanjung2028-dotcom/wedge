"""v6 = v5.1 market shift + matchup-lens features, fit on settled Robinhood prices and tested leave-one-week-out (Weeks 7-9).

Model: logit(P) = logit(market mid) + group shift + sum_k beta[family, k] * feature_k   (ridge; every ladder weighted 1).
Compared with v5.1 (group shift only) and the market mid alone, on the held-out week: log loss, Brier, and the picks each
model would make (better side clears its ask by 3+ points; ROI at the ask, before fees).
Writes bt/cal_v6.json (fit on all three weeks) and bt/v6_report.json."""
import json, numpy as np, pandas as pd
from scipy.optimize import minimize
W = '/home/claude/wedger/'
P = pd.read_pickle(W + 'bt/lens_pool.pkl')
GRP = {'recyd': 'recyd', 'rec': 'rec', 'rushyd': 'rush', 'rryd': 'rush', 'passyd': 'passyd', 'passtd': 'passtd', 'td': 'td'}
FAM = {'recyd': 'recv', 'rec': 'recv', 'rushyd': 'rush', 'rryd': 'rush', 'passyd': 'pass', 'passtd': 'pass', 'td': 'td'}
FEATS = {'recv': ['dvp', 'overlap', 'look', 'volume', 'comp', 'consist'], 'rush': ['dvp', 'dir', 'box', 'volume', 'comp', 'consist'],
         'pass': ['dvp', 'volume', 'pressure', 'comp', 'consist'], 'td': ['dvp', 'overlap', 'consist']}
import os
ONLY = os.environ.get('V6_FAMS'); LAMG = float(os.environ.get('V6_LAMG', '8'))
if ONLY: FEATS = {k: (v if k in ONLY.split(',') else []) for k, v in FEATS.items()}
P['g'] = P.stat.map(GRP); P['fam'] = P.stat.map(FAM)
GL = sorted(P.g.unique()); COLS = [(fm, k) for fm, ks in FEATS.items() for k in ks]
lg = lambda p: np.log(np.clip(p, 1e-4, 1 - 1e-4) / (1 - np.clip(p, 1e-4, 1 - 1e-4))); sg = lambda z: 1 / (1 + np.exp(-z))
def design(d, feats=True):
    Xg = np.column_stack([(d.g == g).astype(float) for g in GL])
    if not feats: return Xg
    Xf = np.column_stack([((d.fam == fm) * d[k]).astype(float) for fm, k in COLS])
    return np.hstack([Xg, Xf])
def fit(d, feats, lam_g=None, lam_f=30.0):
    lam_g = LAMG if lam_g is None else lam_g
    X = design(d, feats); off = lg(d.mid.values); y = d.y.values; w = d.w.values
    pen = np.r_[np.full(len(GL), lam_g), np.full(X.shape[1] - len(GL), lam_f)]
    def f(b):
        z = off + X @ b; p = sg(z)
        nll = -np.sum(w * (y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12)))
        g = X.T @ (w * (p - y)) + 2 * pen * b
        return nll + np.sum(pen * b ** 2), g
    return minimize(f, np.zeros(X.shape[1]), jac=True, method='L-BFGS-B').x
def predict(d, b, feats): return sg(lg(d.mid.values) + design(d, feats) @ b)
def picks(d, p, thr=0.03):
    ey, en = p - d.ya.values, (1 - p) - d.na.values
    side = np.where(ey >= thr, 1, np.where(en >= thr, -1, 0))
    cost = np.where(side == 1, d.ya.values, np.where(side == -1, d.na.values, 0))
    win = np.where(side == 1, d.y.values, np.where(side == -1, 1 - d.y.values, 0))
    pnl = np.where(side != 0, np.where(win == 1, 1 - cost, -cost), 0)
    return side, cost, win, pnl
def lam_search(tr):
    """inner leave-one-week-out on the training weeks to choose the feature penalty"""
    best = None
    for lam in (5, 15, 30, 60, 120, 250):
        ll = 0
        for wk in tr.wk.unique():
            a, t = tr[tr.wk != wk], tr[tr.wk == wk]
            if not len(a) or not len(t): continue
            b = fit(a, True, lam_f=lam); p = predict(t, b, True)
            ll += -np.sum(t.w * (t.y * np.log(p) + (1 - t.y) * np.log(1 - p)))
        if best is None or ll < best[0]: best = (ll, lam)
    return best[1]
out, rep = [], {'folds': {}}
for wk in (7, 8, 9):
    tr, te = P[P.wk != wk], P[P.wk == wk].copy()
    lam = lam_search(tr)
    b5 = fit(tr, False); b6 = fit(tr, True, lam_f=lam)
    te['p_mkt'] = te.mid; te['p5'] = predict(te, b5, False); te['p6'] = predict(te, b6, True); te['lam'] = lam
    out.append(te); rep['folds'][wk] = lam
T = pd.concat(out)
def ll(p, y, w): return float(-np.sum(w * (y * np.log(np.clip(p, 1e-6, 1)) + (1 - y) * np.log(np.clip(1 - p, 1e-6, 1)))) / np.sum(w))
def br(p, y, w): return float(np.sum(w * (p - y) ** 2) / np.sum(w))
def summary(d, tag):
    r = {'n': int(len(d)), 'ladders': float(d.w.sum())}
    for m in ('p_mkt', 'p5', 'p6'): r[m] = {'logloss': round(ll(d[m], d.y, d.w), 5), 'brier': round(br(d[m], d.y, d.w), 5)}
    for m in ('p5', 'p6'):
        s, c, wn, pnl = picks(d, d[m].values)
        k = s != 0; ww = d.w.values[k]
        r[m]['picks'] = {'n': int(k.sum()), 'ladders': round(float(ww.sum()), 1), 'won': round(float(np.sum(ww * wn[k]) / max(ww.sum(), 1e-9)), 3),
                         'roi': round(float(np.sum(ww * pnl[k]) / max(np.sum(ww * c[k]), 1e-9)), 4)}
    print(f"{tag:28s} n={r['n']:5d}  logloss mkt {r['p_mkt']['logloss']:.4f}  v5.1 {r['p5']['logloss']:.4f}  v6 {r['p6']['logloss']:.4f}  | brier mkt {r['p_mkt']['brier']:.4f} v5.1 {r['p5']['brier']:.4f} v6 {r['p6']['brier']:.4f}"
          f"  | picks v5.1 {r['p5']['picks']['n']:4d} won {r['p5']['picks']['won']:.3f} roi {r['p5']['picks']['roi']:+.3f}   v6 {r['p6']['picks']['n']:4d} won {r['p6']['picks']['won']:.3f} roi {r['p6']['picks']['roi']:+.3f}")
    return r
rep['all'] = summary(T, 'all held-out')
for wk in (7, 8, 9): rep[f'w{wk}'] = summary(T[T.wk == wk], f'week {wk}')
for lo, hi in ((0.25, 0.75), (0.40, 0.60)): rep[f'band{int(lo*100)}_{int(hi*100)}'] = summary(T[T.mid.between(lo, hi)], f'mid {int(lo*100)}-{int(hi*100)}c')
for g in GL: rep['g_' + g] = summary(T[T.g == g], 'stat ' + g)
# how much the model moves prices (spread of v6 - v5.1 shifts) and how sharp it is: calibration by decile of the v6 move
T['move'] = T.p6 - T.p5
T['mb'] = pd.qcut(T.move, 5, labels=False, duplicates='drop')
cal = T.groupby('mb').apply(lambda d: pd.Series({'move': np.average(d.move, weights=d.w), 'p5': np.average(d.p5, weights=d.w), 'p6': np.average(d.p6, weights=d.w), 'hit': np.average(d.y, weights=d.w), 'n': len(d)}))
print(cal.round(3)); rep['move_quintiles'] = cal.round(4).to_dict('records')
# final fit on all weeks
lam = lam_search(P); b = fit(P, True, lam_f=lam)
names = [('grp', g) for g in GL] + COLS
coef = {f'{a}.{c}': round(float(v), 4) for (a, c), v in zip(names, b)}
print('lambda', lam); print({k: v for k, v in coef.items()})
# bootstrap by game for the coefficient spread (used for the range on each line)
rng = np.random.default_rng(7); games = P.game.unique() + '|' + P.wk.astype(str).unique()[0]
keys = (P.wk.astype(str) + '|' + P.game).values; uk = np.unique(keys); boots = []
for i in range(int(os.environ.get('V6_BOOT', '40'))):
    pick = rng.choice(uk, len(uk), replace=True); idx = np.concatenate([np.where(keys == k)[0] for k in pick])
    boots.append(fit(P.iloc[idx], True, lam_f=lam))
B = np.array(boots)
OUT = os.environ.get('V6_OUT', 'cal_v6.json')
json.dump({'groups': GRP, 'families': FAM, 'feats': FEATS, 'group_levels': GL, 'cols': [f'{a}.{c}' for a, c in COLS], 'coef': coef, 'lambda': lam,
           'boot': B.round(5).tolist(), 'n': int(len(P)), 'weeks': [7, 8, 9]}, open(W + 'bt/' + OUT, 'w'))
json.dump(rep, open(W + 'bt/' + OUT.replace('cal_', 'rep_'), 'w'), indent=1, default=float)
