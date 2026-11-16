"""(A) Which time window predicts each component of a prop: volume (targets / carries / attempts per game) vs efficiency (yards per target /
carry / attempt). Exponentially weighted averages over all prior games (prior seasons discounted by a season factor), efficiency shrunk toward the
position mean with k pseudo-games. Grid search on 2024-2026 next-game error. Writes arch/recency.json."""
import json, numpy as np, pandas as pd
S = '/home/claude/wedger/'
X = pd.read_pickle(S + 'arch/pgx.pkl')
CMP = {'WR rec': ('WR', 'tgt', 'recyd'), 'TE rec': ('TE', 'tgt', 'recyd'), 'RB rush': ('RB', 'car', 'rushyd'), 'RB rec': ('RB', 'tgt', 'recyd'), 'QB pass': ('QB', 'att', 'passyd')}
HL = [1, 2, 3, 4, 6, 8, 12, 16, 24, 1000]
SEAS = [1.0, 0.7, 0.5, 0.3]
K = [0, 10, 25, 50, 100, 200]
out = {}
for name, (pos, vc, yc) in CMP.items():
    d = X[(X['pos'] == pos)].sort_values(['pid', 'season', 'week'])
    rows = []
    for pid, g in d.groupby('pid', sort=False):
        v = g[vc].values.astype(float); y = g[yc].values.astype(float); s = g['season'].values; t = g['team'].values
        for i in range(4, len(g)):
            if s[i] < 2024: continue
            idx = np.arange(i)
            rows.append((v[idx], y[idx], s[i] - s[idx], np.arange(i, 0, -1), v[i], y[i], t[idx] == t[i]))
    if not rows: continue
    mu_eff = np.nansum(d[yc]) / max(np.nansum(d[vc]), 1)
    # restrict to players with real volume
    rows = [r for r in rows if r[0][-8:].mean() >= (3 if vc != 'att' else 15)]
    res = {'n': len(rows)}
    best = None; grid_v = []
    for sf in SEAS:
        for h in HL:
            err = []
            for vv, yy, ds, age, v1, y1, same in rows:
                w = (0.5 ** (age / h)) * (sf ** ds)
                err.append(abs(v1 - np.sum(w * vv) / np.sum(w)))
            e = float(np.mean(err)); grid_v.append((sf, h, e))
            if best is None or e < best[2]: best = (sf, h, e)
    res['volume_best'] = {'season_factor': best[0], 'half_life_games': best[1], 'mae': round(best[2], 3)}
    res['volume_grid'] = [[a, b, round(c, 3)] for a, b, c in grid_v if a == best[0]]
    best = None; grid_e = []
    for sf in SEAS:
        for h in HL:
            for k in K:
                err = []; wt = []
                for vv, yy, ds, age, v1, y1, same in rows:
                    if v1 <= 0: continue
                    w = (0.5 ** (age / h)) * (sf ** ds)
                    e_hat = (np.sum(w * yy) + k * mu_eff) / (np.sum(w * vv) + k)
                    err.append(abs(y1 / v1 - e_hat) * v1); wt.append(v1)
                e = float(np.sum(err) / np.sum(wt)); grid_e.append((sf, h, k, e))
                if best is None or e < best[3]: best = (sf, h, k, e)
    res['efficiency_best'] = {'season_factor': best[0], 'half_life_games': best[1], 'shrink_units': best[2], 'mae_per_unit': round(best[3], 3)}
    res['efficiency_grid_hl'] = [[b, c, round(e, 4)] for a, b, c, e in grid_e if a == best[0] and c == best[2]]
    res['efficiency_grid_k'] = [[b, c, round(e, 4)] for a, b, c, e in grid_e if a == best[0] and b == best[1]]
    out[name] = res
    print(name, res['n'], res['volume_best'], res['efficiency_best'])
json.dump(out, open(S + 'arch/recency.json', 'w'), indent=1)
