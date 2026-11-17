"""Next step 2: correct the confidence.

Question: when the card calls a line a final, is the chance it states the chance it wins? Each correction is fit only on
predictions the model made for weeks it hadn't seen (inner held-out weeks inside the training weeks), then applied to the
week being tested, so neither the model nor the correction ever saw the week it's graded on.
  none        the current formula as it is
  shrink      keep k of the lens's move:            logit p = logit(mid) + k * move
  recalibrate refit the whole map:                  logit p = a + c * logit(mid) + k * move
  pick-aware  shrink fit only on the sides the card would pick (the winner's-curse correction: our biggest moves
              are the ones most inflated by noise, and they're the ones that become finals)
Pass mark (set before running): finals' stated chance lands closer to their win rate on held-out weeks, with all-line
log loss no worse than the current formula. Writes bt/next_steps/calib.json."""
import json
import numpy as np, pandas as pd
from scipy.optimize import minimize
from common import *

KS = np.round(np.arange(0, 1.51, 0.05), 2)


def side_rows(idx, p):
    """the better side of each line, if it clears the lean bar: (index, sign, ask) -- sign +1 Yes, -1 No"""
    out = []
    for i, pi in zip(idx, p):
        r = P.iloc[i]; k = int(round(r.line + 0.5))
        if k < (2 if r.stat == 'rec' else 10): continue
        for s, ask in ((1, r.ya), (-1, r.na)):
            ps = pi if s == 1 else 1 - pi
            if 3 < ask < 97 and 100 * ps - (ask + FEE) >= 0.5: out.append((i, s))
    return out


def fit_cal(idx, mv):
    """-> dict of correction functions fit on the inner held-out lines idx with lens moves mv"""
    o, t = off[idx], y[idx]
    k1 = min(KS, key=lambda k: lli(sg(o + k * mv), t).mean())
    def f(v):
        p = sg(v[0] + v[1] * o + v[2] * mv); return lli(p, t).sum() + 1.0 * (v[0] ** 2 + (v[1] - 1) ** 2 + (v[2] - 1) ** 2)
    a, c, k2 = minimize(f, [0, 1, 1], method='Nelder-Mead').x
    S = side_rows(idx, sg(o + mv)); pos = {i: j for j, i in enumerate(idx)}
    if S:
        ii = np.array([pos[i] for i, _ in S]); ss = np.array([s for _, s in S])
        ys = np.where(ss == 1, t[ii], 1 - t[ii])
        k3 = min(KS, key=lambda k: lli(sg(ss * (o[ii] + k * mv[ii])), ys).mean())
    else: k3 = 1.0
    return {'none': (lambda oo, m: sg(oo + m)), 'shrink': (lambda oo, m, k=k1: sg(oo + k * m)),
            'recalibrate': (lambda oo, m, a=a, c=c, k=k2: sg(a + c * oo + k * m)), 'pick-aware': (lambda oo, m, k=k3: sg(oo + k * m))}, \
           {'shrink': float(k1), 'recalibrate': [round(float(a), 3), round(float(c), 3), round(float(k2), 3)], 'pick-aware': float(k3), 'pick_sides': len(S)}


def run(scheme):
    names = ('none', 'shrink', 'recalibrate', 'pick-aware')
    p = {n: np.full(len(y), np.nan) for n in names}; lo = {n: np.full(len(y), np.nan) for n in names}; hi = {n: np.full(len(y), np.nan) for n in names}
    params = {}
    for w in WEEKS:
        tr = np.where(wk != w)[0] if scheme == 'lowo' else np.where(wk < w)[0]
        te = np.where(wk == w)[0]
        if len(set(wk[tr])) < 2: continue           # the correction needs a week the model didn't see inside the training weeks
        lam = pick_lam(XBASE, tr); b = fit(XBASE, tr, lam); B = boot_fits(XBASE, tr, lam)
        inner_i, inner_m = [], []
        for t in sorted(set(wk[tr])):
            a_ = tr[wk[tr] != t]; tt = tr[wk[tr] == t]
            if scheme == 'forward': a_ = tr[wk[tr] < t]
            if not len(a_): continue
            inner_i.append(tt); inner_m.append(XBASE[tt] @ fit(XBASE, a_, lam))
        ii, mm = np.concatenate(inner_i), np.concatenate(inner_m)
        F, prm = fit_cal(ii, mm); params[w] = prm
        mv = XBASE[te] @ b; mvB = XBASE[te] @ B.T
        for n in names:
            p[n][te] = F[n](off[te], mv)
            pb = F[n](off[te][:, None], mvB)
            lo[n][te] = np.percentile(pb, 10, axis=1); hi[n][te] = np.percentile(pb, 90, axis=1)
    out = {'params': params, 'models': {}}
    base = p['none']; m = ~np.isnan(base)
    mk = sg(off).copy(); mk[~m] = np.nan
    out['market'] = summ(mk, m)
    for n in names:
        D = P.loc[m].copy(); D['p'] = 100 * p[n][m]; D['lo'] = 100 * lo[n][m]; D['hi'] = 100 * hi[n][m]
        C = cleared(D); K = card(C)
        d = compare(p[n], base) if n != 'none' else (0.0, 0.0, 0.0)
        dm = compare(p[n], mk)
        allc = C[C.call != 'Pass']
        out['models'][n] = {**summ(p[n], m), 'vs_current': [round(x, 5) for x in d], 'vs_market': [round(x, 5) for x in dm],
                            'card': tier_stats(K), 'all_cleared': tier_stats(allc),
                            'finals': K[K.call == 'Final line'][['week', 'game', 'player', 'stat', 'k', 'side', 'price', 'mkt', 'stated', 'win']].round(1).to_dict('records')}
    # reliability of every scored line (deciles of our number), current formula
    q = pd.qcut(base[m], 10, labels=False, duplicates='drop')
    out['reliability'] = [{'stated': round(100 * float(base[m][q == j].mean()), 1), 'won': round(100 * float(y[m][q == j].mean()), 1), 'n': int((q == j).sum())} for j in range(q.max() + 1)]
    return out


R = {s: run(s) for s in ('lowo', 'forward')}
json.dump(R, open(W + 'bt/next_steps/calib.json', 'w'), indent=1, default=float)
for s, r in R.items():
    print(f'\n=== {s}   params by week: {r["params"]}')
    print(f"market  logloss {r['market']['logloss']}")
    for n, v in r['models'].items():
        c = v['card']; f, l = c['Final line'], c['Conditional lean']; a = v['all_cleared']['Final line']
        print(f"{n:12s} ll {v['logloss']:.5f} vs cur {v['vs_current'][0]:+.5f} [{v['vs_current'][1]:+.5f},{v['vs_current'][2]:+.5f}]  "
              f"| card finals n={f.get('n')} stated {f.get('stated')} won {f.get('won')} z {f.get('z')} roi {f.get('roi')}"
              f"  leans n={l.get('n')} stated {l.get('stated')} won {l.get('won')}  | all cleared finals n={a.get('n')} stated {a.get('stated')} won {a.get('won')} z {a.get('z')}")
print('\nreliability (lowo, current):', R['lowo']['reliability'])
