"""Next step 3: curves with a football reason, added to the current formula one at a time.

Each term has a reason it should matter before we look at results, and is zero on the other family's lines:
  rush dir x box        a defense that leaks yards where this team runs AND plays light boxes should be worse than either alone
  rush dvp x volume     a soft run defense that also faces a lot of carries
  rush x favored        favored teams run more late, so a back's volume rises with the spread (expected margin)
  recv overlap x dvp    targets go where this defense is weak AND it allows yards to his position
  recv look x volume    a blitz-beater against a defense that faces many passes
  recv x trailing       teams expected to trail throw more (minus the expected margin)
Pass mark (set before running): held-out log loss below the market AND the current formula leaving one week out, and below
the current formula in the forward test too (each week fit only on the weeks before it). Writes bt/next_steps/terms.json."""
import json
import numpy as np
from common import *

EM = np.array([exp_margin(t, w) for t, w in zip(P.team, P.wk)])
isr, isv = (fam == 'rush').astype(float), (fam == 'recv').astype(float)
raw = lambda c: P[c].fillna(0).values.astype(float)
TERMS = {
    'rush dir x box': isr * raw('dir') * raw('box'),
    'rush dvp x volume': isr * raw('dvp') * raw('volume'),
    'rush x favored': isr * EM,
    'recv overlap x dvp': isv * raw('overlap') * raw('dvp'),
    'recv look x volume': isv * raw('look') * raw('volume'),
    'recv x trailing': isv * -EM,
}
mk = sg(off)
cur = {s: heldout(XBASE, scheme=s) for s in ('lowo', 'forward')}
out = {'market': {s: summ(np.where(np.isnan(cur[s]), np.nan, mk)) for s in cur}, 'current': {s: summ(cur[s]) for s in cur}, 'terms': {}}
print(f"{'':22s} {'LOWO ll':>9s} {'vs current [90%]':>28s} {'vs market':>10s} | {'fwd ll':>8s} {'vs current':>11s}  pass")
print(f"{'market':22s} {out['market']['lowo']['logloss']:9.5f} {'':28s} {'':10s} | {out['market']['forward']['logloss']:8.5f}")
print(f"{'current formula':22s} {out['current']['lowo']['logloss']:9.5f} {'':28s} {'':10s} | {out['current']['forward']['logloss']:8.5f}")
for name, t in TERMS.items():
    sd = t.std(); Z = np.hstack([XBASE, (t / (sd if sd > 0 else 1))[:, None]])
    r = {}
    for s in ('lowo', 'forward'):
        p, fits = heldout(Z, scheme=s, ret_fits=True)
        pm = np.where(np.isnan(p), np.nan, mk)
        r[s] = {**summ(p), 'vs_current': [round(x, 5) for x in compare(p, cur[s])], 'vs_market': [round(x, 5) for x in compare(p, pm)],
                'term_weight_by_week': {w: round(float(f[2][-1]), 4) for w, f in fits.items()}}
    ok = (r['lowo']['vs_market'][0] < 0 and r['lowo']['vs_current'][0] < 0 and r['forward']['vs_current'][0] < 0)
    r['nonzero_lines'] = int((t != 0).sum()); r['pass'] = bool(ok); out['terms'][name] = r
    L, F = r['lowo'], r['forward']
    print(f"{name:22s} {L['logloss']:9.5f} {L['vs_current'][0]:+.5f} [{L['vs_current'][1]:+.5f},{L['vs_current'][2]:+.5f}] {L['vs_market'][0]:+10.5f} | "
          f"{F['logloss']:8.5f} {F['vs_current'][0]:+11.5f}  {'PASS' if ok else 'no'}   weights {L['term_weight_by_week']}")
json.dump(out, open(W + 'bt/next_steps/terms.json', 'w'), indent=1, default=float)
