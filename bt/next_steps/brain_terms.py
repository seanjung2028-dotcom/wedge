"""Combine the two brains (Sat Nov 21): can the research method's evidence move Wedge % itself, instead of only vetoing lines?

The method's checks (brain/gates.py) are pass/fail today. Each one also measures something the lens may not, and each has a
football reason, written down before looking at results:
  role trend    his share of the team's carries (rushing) or targets (receiving) over the last 3 games vs his season share,
                as a log ratio held to +/-1: a growing role should clear more often than a season-long average says
  script        his hit rate at this exact line in games that matched the expected script (won by 8+, one-score, lost by 8+),
                shrunk to the price with 6 games of weight (the lens's `consist` uses the same shrink over all games)
  close games   the same, in one-score games only (the method requires the side to hold up in close games)
  recent form   his hit rate at this line over his last 3 games, shrunk to the price with 3 games of weight
  late work     the share of his yards in this stat that came in the 4th quarter, less 25%: an over that leans on late work
                should clear less often (receptions have no yardage split and get 0)
Already in the lens and not tested again: the full-log hit rate at the line (`consist`). The backup-QB rule stays a rule.
Books' consensus can't be tested: book prices were pulled for Week 9 only before this week, too few settled lines to judge.

Data and held-out schemes: the shared harness (common.py): 1,314 settled Weeks 7-10 main lines at real prices, every input from
games before the week. Pass mark (set before running, same as the football-terms test): held-out log loss below the market AND
the current formula leaving one week out, and below the current formula in the forward test. Terms that pass alone are then
tested together, and the card each version would have built is graded on the held-out weeks.
Writes bt/next_steps/brain_terms.json."""
import json, math
import numpy as np, pandas as pd
from common import *

A_SCRIPT, A_RECENT = 6, 3
feat = {k: np.zeros(len(y)) for k in ('role trend', 'script', 'close games', 'recent form', 'late work')}
for i, r in enumerate(P.itertuples()):
    k = int(round(r.line + 0.5)); price = r.mid
    c = check(r, k, 'Yes')
    rd = c['ROLE'].get('data')
    if rd and rd['season_share'] > 0:
        feat['role trend'][i] = float(np.clip(math.log((rd['last3_share'] + 0.01) / (rd['season_share'] + 0.01)), -1, 1))
    bk = c['SCRIPT']['buckets']; ls = c['SCRIPT']['likely']
    if ls in bk: h, n = bk[ls]; feat['script'][i] = (h + A_SCRIPT * price) / (n + A_SCRIPT) - price
    if 'close' in bk: h, n = bk['close']; feat['close games'][i] = (h + A_SCRIPT * price) / (n + A_SCRIPT) - price
    g = c['LOG']['games'][-3:]
    if g:
        h = sum(1 for _, v, _ in g if v >= k); feat['recent form'][i] = (h + A_RECENT * price) / (len(g) + A_RECENT) - price
    q = c['LATE']['q4_share']
    if q is not None: feat['late work'][i] = q - 0.25

mk = sg(off)
cur = {s: heldout(XBASE, scheme=s) for s in ('lowo', 'forward')}
out = {'n': int(len(y)), 'weeks': list(WEEKS), 'market': {s: summ(np.where(np.isnan(cur[s]), np.nan, mk)) for s in cur},
       'current': {s: summ(cur[s]) for s in cur}, 'terms': {}, 'feature_coverage': {k: int((v != 0).sum()) for k, v in feat.items()}}
print(f"{'':16s} {'LOWO ll':>9s} {'vs current [90%]':>28s} {'vs market':>10s} | {'fwd ll':>8s} {'vs current':>11s}  pass   nonzero")
print(f"{'market':16s} {out['market']['lowo']['logloss']:9.5f} {'':28s} {'':10s} | {out['market']['forward']['logloss']:8.5f}")
print(f"{'current':16s} {out['current']['lowo']['logloss']:9.5f} {'':28s} {'':10s} | {out['current']['forward']['logloss']:8.5f}")


def test(Zx):
    Z = np.hstack([XBASE, Zx]); r = {}
    for s in ('lowo', 'forward'):
        p, fits = heldout(Z, scheme=s, ret_fits=True); pm = np.where(np.isnan(p), np.nan, mk)
        r[s] = {**summ(p), 'vs_current': [round(x, 5) for x in compare(p, cur[s])], 'vs_market': [round(x, 5) for x in compare(p, pm)],
                'weights_by_week': {w: [round(float(v), 4) for v in f[2][XBASE.shape[1]:]] for w, f in fits.items()}}
    r['pass'] = bool(r['lowo']['vs_market'][0] < 0 and r['lowo']['vs_current'][0] < 0 and r['forward']['vs_current'][0] < 0)
    return r


sd1 = lambda v: (v / (v.std() if v.std() > 0 else 1))[:, None]
for name, v in feat.items():
    r = test(sd1(v)); r['nonzero_lines'] = int((v != 0).sum()); out['terms'][name] = r
    L, F = r['lowo'], r['forward']
    print(f"{name:16s} {L['logloss']:9.5f} {L['vs_current'][0]:+.5f} [{L['vs_current'][1]:+.5f},{L['vs_current'][2]:+.5f}] {L['vs_market'][0]:+10.5f} | "
          f"{F['logloss']:8.5f} {F['vs_current'][0]:+11.5f}  {'PASS' if r['pass'] else 'no':5s} {r['nonzero_lines']}   weights {L['weights_by_week']}")
passed = [n for n, r in out['terms'].items() if r['pass']]
out['passed_alone'] = passed
if len(passed) > 1:
    r = test(np.hstack([sd1(feat[n]) for n in passed])); out['together'] = r
    print('together', passed, r['lowo']['logloss'], r['lowo']['vs_current'], r['forward']['vs_current'], 'PASS' if r['pass'] else 'no')


# ---------------- the card each version would have built on held-out weeks (leave one week out), with 10th-90th ranges
def card_for(Z, label):
    p = np.full(len(y), np.nan); lo = p.copy(); hi = p.copy()
    for w in WEEKS:
        tr, te = np.where(wk != w)[0], np.where(wk == w)[0]; lam = pick_lam(Z, tr); b = fit(Z, tr, lam); B = boot_fits(Z, tr, lam)
        p[te] = sg(off[te] + Z[te] @ b); pb = sg(off[te][:, None] + Z[te] @ B.T); lo[te] = np.percentile(pb, 10, axis=1); hi[te] = np.percentile(pb, 90, axis=1)
    D = P.copy(); D['p'] = 100 * p; D['lo'] = 100 * lo; D['hi'] = 100 * hi
    C = cleared(D); K = card(C); res = {'card': tier_stats(K), 'all_cleared': tier_stats(C)}
    f, l = res['card']['Final line'], res['card']['Conditional lean']
    print(f"{label:28s} finals n={f.get('n')} stated {f.get('stated')} won {f.get('won')} roi {f.get('roi')} | leans n={l.get('n')} stated {l.get('stated')} won {l.get('won')} roi {l.get('roi')}")
    return res


out['cards'] = {'current': card_for(XBASE, 'current formula')}
use = passed if passed else []
if use:
    out['cards']['combined'] = card_for(np.hstack([XBASE] + [sd1(feat[n]) for n in use]), 'combined (' + ', '.join(use) + ')')
json.dump(out, open(W + 'bt/next_steps/brain_terms.json', 'w'), indent=1, default=float)
np.save(W + 'bt/next_steps/brain_terms_feat.npy', np.column_stack([feat[k] for k in feat]))
