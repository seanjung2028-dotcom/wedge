"""Two brains, one number (Sat Nov 21, the owner's spec): join the model's projection and the research method's projection
through a nonlinear formula, fit it 1,000 times, and use the average.

Projection 1 (p1): Wedge % v6, the market mid moved by the matchup lens. In every test it is itself held out: a line's p1
  comes from a lens fit that never saw that line's week (nested inside the training weeks too).
Projection 2 (p2): the research method's own number for the exact line (brain/gates.py evidence), written before any fitting:
  his hit rate at this threshold pooled over four blocks of his 2026 games before the week (all games, games in the script the
  spread points to, one-score games, his last 3 games), shrunk to the market price with 6 games of weight:
      p2 = (h_all + h_script + h_close + h_last3 + 6*mid) / (n_all + n_script + n_close + n_last3 + 6)
  A game can sit in more than one block, so script-matching, close and recent games count more, as the method weighs them.
Nonlinear joins (each with its own fitted parameters):
  trig blend    p = cos^2(t)*p1 + sin^2(t)*p2                 t in [0, pi/2]; the weights always sum to 1
  sine pull     logit p = logit p1 + a*sin(logit p2 - logit p1)  the pull saturates, so a thin log can't drag a line far
  scaled sine   logit p = logit p1 + a*sin(b*(logit p2 - logit p1))
1,000 runs: each fit is repeated on 1,000 game-bootstrap resamples of its training lines and the parameters averaged.
Held-out scoring: leave one week out (Weeks 7-10) and forward (Weeks 9-10, fit only on earlier weeks), against v6 alone and the
market. The final parameters are the average over 1,000 resamples of all four weeks. Writes bt/brain_blend.json (read by lens/v6.py)
and bt/next_steps/brain_blend_report.json."""
import json, math, time
import numpy as np, pandas as pd
from scipy.optimize import minimize
from common import *

N_RUNS = 1000; A_PRIOR = 6; rng = np.random.default_rng(20261121)
# ---------------- projection 2 on every settled line
H = np.zeros(len(y)); N = np.zeros(len(y)); blocks = []
for i, r in enumerate(P.itertuples()):
    k = int(round(r.line + 0.5)); c = check(r, k, 'Yes')
    g = c['LOG']['games']; h_a, n_a = sum(1 for _, v, _ in g if v >= k), len(g)
    bk = c['SCRIPT']['buckets']; ls = c['SCRIPT']['likely']
    h_s, n_s = bk.get(ls, [0, 0]); h_c, n_c = bk.get('close', [0, 0])
    g3 = g[-3:]; h_3, n_3 = sum(1 for _, v, _ in g3 if v >= k), len(g3)
    H[i] = h_a + h_s + h_c + h_3; N[i] = n_a + n_s + n_c + n_3; blocks.append((h_a, n_a, h_s, n_s, h_c, n_c, h_3, n_3))
mid = P.mid.values
p2 = np.clip((H + A_PRIOR * mid) / (N + A_PRIOR), 0.01, 0.99); L2 = lg(p2)


# ---------------- held-out v6 (p1): outer folds, and nested inner predictions for the training lines
def v6_pred(tr, te):
    lam = pick_lam(XBASE, tr); b = fit(XBASE, tr, lam); return sg(off[te] + XBASE[te] @ b)


def inner_p1(tr):
    """for training lines, a v6 number from a fit that left that line's week out (within the training weeks)"""
    p = np.full(len(y), np.nan); ws = sorted(set(wk[tr]))
    if len(ws) < 2: p[tr] = v6_pred(tr, tr); return p
    for w2 in ws:
        a, t = tr[wk[tr] != w2], tr[wk[tr] == w2]; p[t] = v6_pred(a, t)
    return p


FORMS = {
    'trig blend': {'n': 1, 'x0': [0.3], 'bounds': [(0.0, math.pi / 2)],
                   'f': lambda th, q1, l2: np.cos(th[0]) ** 2 * q1 + np.sin(th[0]) ** 2 * sg(l2)},
    'sine pull': {'n': 1, 'x0': [0.1], 'bounds': [(-1.5, 1.5)],
                  'f': lambda th, q1, l2: sg(lg(q1) + th[0] * np.sin(l2 - lg(q1)))},
    'scaled sine': {'n': 2, 'x0': [0.1, 1.0], 'bounds': [(-1.5, 1.5), (0.05, 3.0)],
                    'f': lambda th, q1, l2: sg(lg(q1) + th[0] * np.sin(th[1] * (l2 - lg(q1))))},
}


def fit_form(F, idx, q1):
    t = y[idx]; a, b2 = q1[idx], L2[idx]
    obj = lambda th: float(np.sum(lli(np.clip(F['f'](th, a, b2), 1e-6, 1 - 1e-6), t)))
    return minimize(obj, F['x0'], method='L-BFGS-B', bounds=F['bounds']).x


def bag(F, idx, q1, n=N_RUNS):
    """1,000 game-bootstrap fits on the training lines -> every fit's parameters"""
    keys = games[idx]; uk = np.unique(keys); pos = {k: idx[keys == k] for k in uk}; out = []
    for _ in range(n):
        pick = rng.choice(uk, len(uk), replace=True); out.append(fit_form(F, np.concatenate([pos[k] for k in pick]), q1))
    return np.array(out)


t0 = time.time()
cur_lowo = heldout(XBASE, scheme='lowo')
res = {'n': int(len(y)), 'runs': N_RUNS, 'p2_mean_n_games': round(float(N.mean()), 1),
       'p2_vs_market_alone': {'logloss_p2': round(float(lli(p2, y).mean()), 5), 'logloss_market': round(float(lli(sg(off), y).mean()), 5)}, 'forms': {}}
print('p2 alone', res['p2_vs_market_alone'], 'v6 alone (LOWO)', round(float(lli(cur_lowo, y).mean()), 5))
OUTER = {}
for w in WEEKS:   # leave one week out
    tr, te = np.where(wk != w)[0], np.where(wk == w)[0]; OUTER[('lowo', w)] = (tr, te, inner_p1(tr), v6_pred(tr, te))
for w in (9, 10):   # forward: only earlier weeks
    tr, te = np.where(wk < w)[0], np.where(wk == w)[0]; OUTER[('fwd', w)] = (tr, te, inner_p1(tr), v6_pred(tr, te))
for name, F in FORMS.items():
    r = {}
    for scheme in ('lowo', 'fwd'):
        pb = np.full(len(y), np.nan); p6 = np.full(len(y), np.nan); avg = {}
        for (s, w), (tr, te, q_in, q_te) in OUTER.items():
            if s != scheme: continue
            th = bag(F, tr, q_in).mean(0); avg[w] = [round(float(v), 4) for v in th]
            pb[te] = F['f'](th, q_te, L2[te]); p6[te] = q_te
        m = ~np.isnan(pb); mk = np.where(m, sg(off), np.nan)
        r[scheme] = {'lines': int(m.sum()), 'logloss': round(float(lli(pb[m], y[m]).mean()), 5), 'v6_logloss': round(float(lli(p6[m], y[m]).mean()), 5),
                     'market_logloss': round(float(lli(mk[m], y[m]).mean()), 5), 'vs_v6': [round(x, 5) for x in compare(pb, p6)],
                     'vs_market': [round(x, 5) for x in compare(pb, mk)], 'avg_params_by_week': avg}
    r['beats_v6_both'] = bool(r['lowo']['vs_v6'][0] < 0 and r['fwd']['vs_v6'][0] < 0)
    res['forms'][name] = r
    print(f"{name:12s} LOWO {r['lowo']['logloss']:.5f} (v6 {r['lowo']['v6_logloss']:.5f}, mkt {r['lowo']['market_logloss']:.5f}) vs v6 {r['lowo']['vs_v6']} | "
          f"fwd {r['fwd']['logloss']:.5f} (v6 {r['fwd']['v6_logloss']:.5f}) vs v6 {r['fwd']['vs_v6']} | params {r['lowo']['avg_params_by_week']}  {time.time() - t0:.0f}s")
# the form used: best held-out log loss leaving one week out (the scheme with all four weeks)
best = min(res['forms'], key=lambda n: res['forms'][n]['lowo']['logloss']); res['chosen'] = best
alli = np.arange(len(y)); TH = bag(FORMS[best], alli, cur_lowo)
res['final'] = {'form': best, 'params_mean': [round(float(v), 5) for v in TH.mean(0)], 'params_p10_p90': [[round(float(a), 5), round(float(b), 5)] for a, b in zip(np.percentile(TH, 10, 0), np.percentile(TH, 90, 0))],
                'runs': N_RUNS, 'fit_on': 'all 1,314 settled Weeks 7-10 lines, v6 held out by week'}
pf = FORMS[best]['f'](TH.mean(0), cur_lowo, L2)
res['final']['move_vs_v6_pts'] = {'median_abs': round(float(np.median(np.abs(100 * (pf - cur_lowo)))), 2), 'p90_abs': round(float(np.percentile(np.abs(100 * (pf - cur_lowo)), 90)), 2)}


# ---------------- the card on held-out weeks, current vs combined (v6 ranges from 40 refits, the blend applied to p, lo and hi)
def card_eval(th, F):
    p = np.full(len(y), np.nan); lo = p.copy(); hi = p.copy(); pc = p.copy(); loc = p.copy(); hic = p.copy()
    for w in WEEKS:
        tr, te = np.where(wk != w)[0], np.where(wk == w)[0]; lam = pick_lam(XBASE, tr); b = fit(XBASE, tr, lam); B = boot_fits(XBASE, tr, lam)
        q = sg(off[te] + XBASE[te] @ b); qb = sg(off[te][:, None] + XBASE[te] @ B.T); ql, qh = np.percentile(qb, 10, 1), np.percentile(qb, 90, 1)
        p[te], lo[te], hi[te] = q, ql, qh
        t_ = th[w] if isinstance(th, dict) else th
        pc[te], loc[te], hic[te] = F['f'](t_, q, L2[te]), F['f'](t_, ql, L2[te]), F['f'](t_, qh, L2[te])
    out = {}
    for lab, (a, b_, c_) in (('v6', (p, lo, hi)), ('combined', (pc, np.minimum(loc, hic), np.maximum(loc, hic)))):
        D = P.copy(); D['p'] = 100 * a; D['lo'] = 100 * b_; D['hi'] = 100 * c_; C = cleared(D); K = card(C); out[lab] = tier_stats(K)
        f_, l_ = out[lab]['Final line'], out[lab]['Conditional lean']
        print(f"card {lab:9s} finals n={f_.get('n')} stated {f_.get('stated')} won {f_.get('won')} roi {f_.get('roi')} | leans n={l_.get('n')} stated {l_.get('stated')} won {l_.get('won')} roi {l_.get('roi')}")
    return out


wk_th = {w: np.array(res['forms'][best]['lowo']['avg_params_by_week'][w]) for w in WEEKS}
res['card_heldout'] = card_eval(wk_th, FORMS[best])
print('chosen', best, res['final'])
json.dump(res, open(W + 'bt/next_steps/brain_blend_report.json', 'w'), indent=1, default=float)
json.dump({'note': 'Two-brain join on top of Wedge % v6 (lens/v6.py applies it to p, lo and hi of receiving and rushing lines).',
           'form': best, 'params': res['final']['params_mean'], 'prior_games': A_PRIOR, 'runs': N_RUNS,
           'p2': 'hit rate at the exact line pooled over all 2026 games, expected-script games, one-score games and the last 3 games, shrunk to the mid with 6 games',
           'heldout': {k: res['forms'][best][k] for k in ('lowo', 'fwd')}, 'beats_v6_both': res['forms'][best]['beats_v6_both'],
           'made': 'Sat Nov 21, 2026'}, open(W + 'bt/brain_blend.json', 'w'), indent=1)
