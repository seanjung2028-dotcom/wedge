"""The significance test for rules v3's second path (set by the owner Fri Nov 27): a line priced 50-75c that misses the 70% bar can
still be a final line IF AND ONLY IF our number is statistically significantly above its break-even (price + fee).

Why not just the model's own range: Wedge % is the market's mid moved by the matchup lens, and the range (10th-90th percentile over
40 refits) only measures how much the lens's fit wobbles. The question for money is whether the lens's move holds up on games it
was not fit on. So the test uses that track record:

  logit P(win) = logit(market mid) + beta * (logit(Wedge %) - logit(market mid))

fit on every graded rung the model priced before kickoff (held-out weeks only), with standard errors clustered by player and game
(a player's rungs move together). beta = 1 means the lens's move is fully real, 0 means it adds nothing. A line passes when the
one-sided 95% lower bound of its chance, using beta's lower bound and the fit wobble, still clears the break-even:

  lower = sigmoid( logit(mkt) + beta*d - 1.645 * sqrt( (se*d)^2 + (beta*s_fit)^2 ) ),   d = logit(ours) - logit(mkt)
  pass  <=>  50 <= ask <= 75  and  lower > (ask + fee) / 100

When the lens's edge is not yet established (beta's lower bound at or below 0), no line can pass: the market mid sits below every
break-even. The fit updates as each week is graded (bt/w12_model/rows_w11_graded.csv now; add later weeks to SOURCES).
Writes brain/sig.json."""
import json, math, os
import numpy as np, pandas as pd
W = '/home/claude/wedger/'
SOURCES = [W + 'bt/w12_model/rows_w11_graded.csv']   # graded held-out rungs: columns kalshi (market mid), v6b (Wedge %), result
Z = 1.645
FLOOR, CAP, FEE = 50, 75, 2
L = lambda p: math.log(p / (1 - p))
S = lambda x: 1 / (1 + math.exp(-x))


def fit():
    import statsmodels.api as sm
    D = pd.concat([pd.read_csv(f) for f in SOURCES], ignore_index=True)
    D = D[D.result.isin(['Won', 'Lost'])].copy()
    cl = lambda p: np.clip(p, 0.5, 99.5) / 100
    D['lm'] = np.log(cl(D.kalshi) / (1 - cl(D.kalshi))); D['d'] = np.log(cl(D.v6b) / (1 - cl(D.v6b))) - D.lm
    y = (D.result == 'Won').astype(int); g = pd.factorize(D.game + '|' + D.player)[0]
    m = sm.GLM(y, D[['d']], family=sm.families.Binomial(), offset=D.lm).fit(cov_type='cluster', cov_kwds={'groups': g})
    out = {'beta': float(m.params.d), 'se': float(m.bse.d), 'p_beta_gt_0': float(m.pvalues.d / 2 if m.params.d > 0 else 1 - m.pvalues.d / 2),
           'n_rungs': int(len(D)), 'n_players': int(g.max() + 1), 'sources': [os.path.relpath(f, W) for f in SOURCES], 'z': Z,
           'beta_low': float(m.params.d - Z * m.bse.d)}
    json.dump(out, open(W + 'brain/sig.json', 'w'), indent=1)
    return out


P = json.load(open(W + 'brain/sig.json')) if os.path.exists(W + 'brain/sig.json') else None


def lower(mkt, ours, lo=None, hi=None):
    """one-sided 95% lower bound (percent) for the chance of a side, given the market mid and our number (both percent, same side)"""
    if P is None: return None
    m, o = min(max(mkt, 0.5), 99.5) / 100, min(max(ours, 0.5), 99.5) / 100
    d = L(o) - L(m); b, se = P['beta'], P['se']
    s_fit = 0.0
    if lo is not None and hi is not None and hi > lo: s_fit = (L(min(hi, 99.5) / 100) - L(max(lo, 0.5) / 100)) / (2 * 1.2816)
    return 100 * S(L(m) + b * d - Z * math.sqrt((se * d) ** 2 + (b * s_fit) ** 2))


def passes(ask, mkt, ours, lo=None, hi=None):
    if not (FLOOR <= ask <= CAP): return False, None
    lb = lower(mkt, ours, lo, hi)
    return (lb is not None and lb > ask + FEE), lb


if __name__ == '__main__':
    r = fit(); print(json.dumps(r, indent=1))
    P = r
    for mkt, ours in [(60, 66), (55, 62), (68, 74), (65, 75)]:
        print(mkt, ours, round(lower(mkt, ours, ours - 1.5, ours + 1.5), 1))
