"""Adopt the one football term that passed (bt/next_steps/terms.py): receiving blitz split x pass volume the defense faces.

Reason: a receiver whose target share rises against the blitz, facing a blitz-heavy defense that also faces a lot of
pass attempts, gets more of those blitz snaps. Added on top of the live v6 lens with the live weights held fixed, so every
other weight and the range stay as they are.
  weight     fit on every settled Weeks 7-10 main line at its real price (1,314), penalty chosen by leaving one week out
  range      40 refits on resampled games, paired with the live v6 refits, so the range carries this term's spread too
  clip       the product is held to +/-1.5 (about its 1st-99th percentile here) so the term never extrapolates
  check      the same fit on Weeks 7-9 only, scored on Week 10 (which neither it nor the live weights ever saw)
Writes bt/cal_v6_terms.json, which lens/v6.py reads."""
import json
import numpy as np
from common import *

CAL = json.load(open(W + 'bt/cal_v6.json')); GL = CAL['group_levels']
COEF = np.array([CAL['coef'][f'grp.{g}'] for g in GL] + [CAL['coef'][c] for c in CAL['cols']]); BOOT = np.array(CAL['boot'])
Xg = np.column_stack([(P.stat.map(CAL['groups']) == g).astype(float).values for g in GL])
Xf = np.column_stack([col(c) for c in CAL['cols']]); X = np.hstack([Xg, Xf])
ol = off + X @ COEF                                         # the live v6 number on every line, in log-odds
CLIP = 1.5                                                  # about the 1st-99th percentile of the product on these lines: no extrapolating past it
isv = (fam == 'recv').astype(float); t = isv * np.clip(P.look.fillna(0).values * P.volume.fillna(0).values, -CLIP, CLIP); Z = t[:, None]
alli = np.arange(len(y)); lam = pick_lam(Z, alli, ol); c = float(fit(Z, alli, lam, ol)[0])
r = np.random.default_rng(17); uk = np.unique(games); boot = []
for i in range(len(BOOT)):
    pick = r.choice(uk, len(uk), replace=True); idx = np.concatenate([np.where(games == k)[0] for k in pick])
    boot.append(float(fit(Z, idx, lam, off + X @ BOOT[i])[0]))
tr, te = np.where(wk < 10)[0], np.where(wk == 10)[0]; lam9 = pick_lam(Z, tr, ol); c9 = float(fit(Z, tr, lam9, ol)[0])
chk = {'fit_weeks': [7, 8, 9], 'lambda': lam9, 'weight': round(c9, 4), 'week10_lines': int(len(te)),
       'week10_logloss': {'market': round(float(lli(sg(off[te]), y[te]).mean()), 5), 'live_v6': round(float(lli(sg(ol[te]), y[te]).mean()), 5),
                          'live_v6_plus_term': round(float(lli(sg(ol[te] + Z[te, 0] * c9), y[te]).mean()), 5)}}
T = json.load(open(W + 'bt/next_steps/terms.json'))['terms']['recv look x volume']
out = {'note': 'Extra lens terms on top of bt/cal_v6.json (live weights held fixed). Each term = coef * feature a * feature b on its family.',
       'terms': [{'name': 'look_x_volume', 'family': 'recv', 'a': 'look', 'b': 'volume', 'label': 'Blitz split x pass volume', 'clip': CLIP,
                  'coef': round(c, 4), 'boot': [round(b, 4) for b in boot], 'lambda': lam, 'n': int(len(y)), 'weeks': [7, 8, 9, 10],
                  'evidence': {'leave_one_week_out': {k: T['lowo'][k] for k in ('logloss', 'vs_current', 'vs_market', 'term_weight_by_week')},
                               'forward': {k: T['forward'][k] for k in ('logloss', 'vs_current', 'vs_market')}, 'week10_live_check': chk}}]}
json.dump(out, open(W + 'bt/cal_v6_terms.json', 'w'), indent=1)
print('lambda', lam, 'coef', round(c, 4), 'boot 10-90%', np.percentile(boot, [10, 90]).round(4)); print(chk)
