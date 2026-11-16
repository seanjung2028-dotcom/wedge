"""AQR-style complexity test (Kelly, Malamud & Zhou, 'The Virtue of Complexity in Return Prediction'):
random Fourier features + ridge, ensembled over draws, to predict each player-stat's deviation from the book-style
projection, using only what is known before the game (feat.pkl). Rolling out-of-sample: 2025 (train 2023-24) and
every 2026 week 2-8 (train on everything before it). Compared with: book-style base, linear ridge on the same features."""
import numpy as np, pandas as pd, json, sys, time
W = '/home/claude/wedger/'
F = pd.read_pickle(W + 'arch/feat.pkl')
LEAK = {'y', 'over', 'resid', 'idx', 'vol', 'rec', 'tgt', 'recyd', 'car', 'rushyd', 'passyd', 'passtd', 'int', 'att', 'td', 'tshare', 'ayshare', 'airyd', 'rec_epa', 'rush_epa',
        'pass_epa', 'rryd', 'snap', 'pts', 'opts', 'team_tgt', 'team_car', 'team_att', 'car_share', 'i10', 'outside', 'heavy', 'light', 'expl', 'stuff', 'scr_r', 'gun_r',
        'boxn', 'box_r', 'db', 'pa', 'blz', 'prs', 'ybc', 'yac_r', 'btk', 'expected_rush_yards', 'rush_yards_over_expected', 'ngs_att', 'deep_rt', 'rt_n',
        'season', 'week', 'gopp'}
num = [c for c in F.columns if F[c].dtype.kind in 'fi' and c not in LEAK and not c.startswith(('r_', 't_', 'ry_', 'q_', 'T_'))]
F['dome'] = F['roof'].isin(['dome', 'closed']).astype(float)
cat = ['mom', 'arch']
def matrix(d, cols_cat=None):
    X = d[num + ['dome']].astype(float).copy()
    for c in num:
        X[c + '_na'] = X[c].isna().astype(float)
    D = pd.get_dummies(d[cat].astype(str), dtype=float)
    if cols_cat is not None: D = D.reindex(columns=cols_cat, fill_value=0.0)
    return pd.concat([X, D], axis=1), list(D.columns)
def standardize(Xtr, Xte):
    med = Xtr.median().fillna(0); Xtr = Xtr.fillna(med); Xte = Xte.fillna(med)
    mu, sd = Xtr.mean(), Xtr.std().fillna(1).replace(0, 1)
    return ((Xtr - mu) / sd).values.astype(np.float32), ((Xte - mu) / sd).values.astype(np.float32)
def ridge(S, y, z):
    T, P = S.shape
    if P <= T:
        A = S.T @ S / T + z * np.eye(P, dtype=S.dtype); return np.linalg.solve(A, S.T @ y / T)
    A = S @ S.T / T + z * np.eye(T, dtype=S.dtype); return S.T @ np.linalg.solve(A, y / T)
def rff(G, Wm, gamma):
    Z = gamma * (G @ Wm); P2 = Wm.shape[1]
    return np.hstack([np.sin(Z), np.cos(Z)]) / np.sqrt(P2)
def fit_predict(Gtr, ytr, Gte, kind, z, gamma=1.0, P=3000, draws=5, seed=0):
    if kind == 'linear':
        b = ridge(np.hstack([Gtr, np.ones((len(Gtr), 1), np.float32)]), ytr, z)
        return np.hstack([Gte, np.ones((len(Gte), 1), np.float32)]) @ b
    out = np.zeros(len(Gte))
    for d in range(draws):
        rng = np.random.default_rng(seed + d); Wm = rng.standard_normal((Gtr.shape[1], P // 2)).astype(np.float32) / np.sqrt(Gtr.shape[1])
        Str, Ste = rff(Gtr, Wm, gamma), rff(Gte, Wm, gamma)
        sd = Str.std(0) + 1e-6; Str /= sd; Ste /= sd
        b = ridge(Str, ytr, z); out += Ste @ b
    return out / draws
def tune(dtr, stat, kind, grid):
    """time-ordered validation: last 25% of the training rows by date."""
    dtr = dtr.sort_values(['season', 'week']); cut = int(len(dtr) * 0.75)
    a, b = dtr.iloc[:cut], dtr.iloc[cut:]
    Xa, cc = matrix(a); Xb, _ = matrix(b, cc); Ga, Gb = standardize(Xa, Xb)
    ya = (a.y - a.base).values.astype(np.float32); yb = (b.y - b.base).values
    best = None
    for prm in grid:
        p = fit_predict(Ga, ya - ya.mean(), Gb, kind, **prm) + ya.mean()
        mse = np.mean((yb - p) ** 2)
        if best is None or mse < best[0]: best = (mse, prm)
    return best[1]
results = []; preds = []
STATS = sys.argv[1:] or ['rec', 'recyd', 'rushyd', 'passyd']
for stat in STATS:
    d = F[F.stat == stat].copy()
    folds = [('2025', (d.season <= 2024), (d.season == 2025))] + [(f'2026 W{w}', (d.season < 2026) | ((d.season == 2026) & (d.week < w)), (d.season == 2026) & (d.week == w)) for w in range(2, 9)]
    LG = [{'z': z} for z in (1e-2, 1e-1, 1, 10, 100)]
    RG = [{'z': z, 'gamma': g, 'P': 3000, 'draws': 3} for z in (1e-2, 1e-1, 1, 10) for g in (0.5, 1.0)]
    t0 = time.time()
    lin_prm = tune(d[d.season <= 2024], stat, 'linear', LG); rff_prm = tune(d[d.season <= 2024], stat, 'rff', RG)
    rff_prm['draws'] = 5
    for name, trm, tem in folds:
        tr, te = d[trm], d[tem]
        if not len(te): continue
        Xtr, cc = matrix(tr); Xte, _ = matrix(te, cc); Gtr, Gte = standardize(Xtr, Xte)
        ytr = (tr.y - tr.base).values.astype(np.float32); mu = ytr.mean()
        pl = fit_predict(Gtr, ytr - mu, Gte, 'linear', **lin_prm) + mu
        pr = fit_predict(Gtr, ytr - mu, Gte, 'rff', **rff_prm) + mu
        yt = (te.y - te.base).values
        res = {'stat': stat, 'fold': name, 'n': len(te), 'mse_base': np.mean(yt ** 2), 'mse_base_bias': np.mean((yt - mu) ** 2),
               'mse_lin': np.mean((yt - pl) ** 2), 'mse_rff': np.mean((yt - pr) ** 2)}
        results.append(res)
        preds.append(pd.DataFrame({'stat': stat, 'fold': name, 'pid': te.pid.values, 'name': te.name.values, 'season': te.season.values, 'week': te.week.values,
                                   'team': te.team.values, 'base': te.base.values, 'line': te.line.values, 'y': te.y.values, 'p_lin': te.base.values + pl,
                                   'p_rff': te.base.values + pr, 'mu': mu}))
    print(stat, 'lin', lin_prm, 'rff', rff_prm, f'{time.time() - t0:.0f}s', flush=True)
R = pd.DataFrame(results)
for c in ['base_bias', 'lin', 'rff']: R['r2_' + c] = 1 - R['mse_' + c] / R['mse_base']
print(R[['stat', 'fold', 'n', 'mse_base', 'r2_base_bias', 'r2_lin', 'r2_rff']].round(4).to_string())
pd.concat(preds).to_pickle(W + f"bt/rff_preds_{'_'.join(STATS)}.pkl"); R.to_csv(W + f"bt/rff_res_{'_'.join(STATS)}.csv", index=False)
