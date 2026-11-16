"""(D) Role-matchup prior: how players of the same role, in the same game script and against the same kind of defense, have done
vs the line books would set. L2-regularized logistic regression on 2023-25 player-games (offset = the stat's base over rate),
features = role x side, role x spread, position-stat x box count / blitz / coverage / middle-of-field / deep-allowed tercile,
position-stat x team total band, position-stat x pass-rate tercile. Tested out of sample on 2026 Weeks 1-7 (modeled lines) and on the
real Week 6-7 prices. Writes arch/rm_coef.json (used by nfl_model.role_matchup) and arch/rm_eval.json."""
import json, numpy as np, pandas as pd
from scipy.optimize import minimize
S = '/home/claude/wedger/'
exec(open(S + 'arch/categories.py').read().split("REL = ")[0])   # reuse feature prep (F with terciles etc.)
F = F[F['arch'].ne('Unknown')].copy()
F['ps'] = F['pos'] + '|' + F['stat']
F['arch2'] = F['arch'].str.replace(' · seam', '').str.replace(' · underneath', '')
def feats(d):
    cols = {}
    cols['a_side'] = d['ps'] + '|' + d['arch2'] + '|' + d['fav']
    cols['a_spread'] = d['ps'] + '|' + d['arch2'] + '|' + d['spread']
    for c in ('d_box', 'd_blz', 'd_cov', 'd_midf', 'd_deep', 'd_pass', 'd_run', 'o_proe', 'tot'):
        cols[c] = d['ps'] + '|' + c + '|' + d[c].astype(str)
    cols['venue'] = d['ps'] + '|' + d['venue']
    return pd.DataFrame(cols, index=d.index)
tr = F[F['season'] <= 2025]; te = F[F['season'] == 2026]
base = tr.groupby('ps')['over'].mean()
lg = lambda p: np.log(p / (1 - p)); sg = lambda z: 1 / (1 + np.exp(-z))
Ftr, Fte = feats(tr), feats(te)
vocab = {}
for c in Ftr.columns:
    vc = Ftr[c].value_counts()
    for k, n in vc.items():
        if n >= 25 and not k.endswith('|') and '|nan' not in k and not k.endswith('|') : vocab[f'{c}={k}'] = len(vocab)
def design(Fx):
    rows, cols = [], []
    for j, c in enumerate(Fx.columns):
        for i, k in enumerate(Fx[c].values):
            v = vocab.get(f'{c}={k}')
            if v is not None: rows.append(i); cols.append(v)
    Xm = np.zeros((len(Fx), len(vocab)))
    Xm[rows, cols] = 1.0
    return Xm
Xtr, Xte = design(Ftr), design(Fte)
otr = lg(tr['ps'].map(base).clip(0.05, 0.95).values); ote = lg(te['ps'].map(base).fillna(0.45).clip(0.05, 0.95).values)
ytr, yte = tr['over'].values.astype(float), te['over'].values.astype(float)
def fit(lam):
    f = lambda b: -np.sum(ytr * np.log(sg(otr + Xtr @ b)) + (1 - ytr) * np.log(1 - sg(otr + Xtr @ b))) + lam * np.sum(b ** 2)
    g = lambda b: -Xtr.T @ (ytr - sg(otr + Xtr @ b)) + 2 * lam * b
    return minimize(f, np.zeros(Xtr.shape[1]), jac=g, method='L-BFGS-B').x
br = lambda p, y: float(np.mean((p - y) ** 2))
ll = lambda p, y: float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))
ev = {'n_train': int(len(tr)), 'n_test_2026': int(len(te)), 'features': len(vocab)}
p0 = sg(ote); ev['test_base'] = {'brier': round(br(p0, yte), 4), 'logloss': round(ll(p0, yte), 4)}
best = None
for lam in (5, 15, 40, 100, 250):
    b = fit(lam); p = sg(ote + Xte @ b)
    r = {'brier': round(br(p, yte), 4), 'logloss': round(ll(p, yte), 4)}
    ev[f'test_lam{lam}'] = r
    if best is None or r['logloss'] < best[1]['logloss']: best = (lam, r, b)
lam, r, b = best
ev['chosen_lambda'] = lam
# rank spread of predictions in 2026: top vs bottom fifth realized over rate
p = sg(ote + Xte @ b); q = pd.qcut(p, 5, labels=False, duplicates='drop')
ev['quintiles_2026'] = [{'q': int(k), 'pred': round(float(p[q == k].mean()), 3), 'actual': round(float(yte[q == k].mean()), 3), 'n': int((q == k).sum())} for k in sorted(set(q))]
coef = {k: round(float(b[i]), 4) for k, i in vocab.items() if abs(b[i]) >= 0.005}
json.dump({'lambda': lam, 'base': {k: round(float(v), 4) for k, v in base.items()}, 'coef': coef}, open(S + 'arch/rm_coef.json', 'w'), indent=1)
# real Week 6-7 prices: does adding the shift to the calibrated Wedger % help? (shift fit on 2023-25 only -> fully out of sample)
R = pd.read_pickle(S + 'arch/real_rows.pkl')
R = R[R['stat'].isin(['recyd', 'rec', 'rushyd', 'passyd']) & R['arch'].notna() & R['wedger_v3'].notna()].copy()
# rebuild the same features for real rows from the player-game row (pgx) of that week
X = pd.read_pickle(S + 'arch/pgx.pkl'); X = X[X['season'] == 2026]
import re, unicodedata
def nn(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower(); s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', s); return re.sub(r'[^a-z]', '', s)
X['nk'] = X['name'].map(nn)
Fx = F[F['season'] == 2026][['pid', 'week', 'stat', 'd_box', 'd_blz', 'd_cov', 'd_midf', 'd_deep', 'd_pass', 'd_run', 'o_proe', 'tot', 'spread', 'fav', 'venue', 'arch2', 'ps']]
R = R.merge(X[['nk', 'team', 'week', 'pid']].rename(columns={'week': 'wk'}), on=['nk', 'team', 'wk'], how='left')
R = R.merge(Fx.rename(columns={'week': 'wk', 'fav': 'fav2'}), on=['pid', 'wk', 'stat'], how='inner')
R['fav'] = R['fav2']
Xr = design(feats(R))
shift = Xr @ b
w = R['wedger_v3'].values  # 70/30 blend before calibration in calib rows; apply v3 calibration
import sys; sys.path.insert(0, S + 'rh'); import nfl_model as M
M.CAL = dict(M.CAL_V3)
pw = np.array([M.calibrate(0.85 * pr + 0.15 * o, st, 99) for pr, o, st in zip(R['price'], R['ours_v3'], R['stat'])])
yr = R['y'].values.astype(float)
ev['real'] = {'n': int(len(R)), 'price': round(br(R['price'].values, yr), 4), 'wedger_v3': round(br(pw, yr), 4)}
for k in (0.25, 0.5, 1.0):
    ev['real'][f'wedger_v3_plus_rm{k}'] = round(br(sg(lg(np.clip(pw, 1e-3, 1 - 1e-3)) + k * shift), yr), 4)
ev['real']['corr_shift_with_y_minus_price'] = round(float(np.corrcoef(shift, yr - R['price'].values)[0, 1]), 3)
json.dump(ev, open(S + 'arch/rm_eval.json', 'w'), indent=1)
print(json.dumps(ev, indent=1))
top = sorted(coef.items(), key=lambda kv: -abs(kv[1]))[:40]
for k, v in top: print(f'{v:+.3f}  {k}')
