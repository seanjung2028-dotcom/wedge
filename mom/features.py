"""Per player-game predictors built only from games before it (same player, same team).

For each stat: S = season-to-date mean, L4 = last-4 mean (this season), L2, E2/E3/E4 = exponentially weighted means of this
season's games (half-life 2/3/4 games), P = last season's mean with the same team (NaN if none), C = all games since 2023
with the team (season-weighted like the live model: this season 1, last 0.75, two back 0.5, three back 0.35),
and volume/efficiency splits. Writes mom/feat.pkl (one row per player-game-stat with n_prior >= 3 this season).
"""
import pandas as pd, numpy as np
S = '/home/claude/wedger/'
pg = pd.read_pickle(S + 'mom/pg.pkl')
STATS = {'recyd': ('WR', 'TE', 'RB'), 'rec': ('WR', 'TE', 'RB'), 'rushyd': ('RB', 'QB'), 'rryd': ('RB',), 'passyd': ('QB',), 'td': ('WR', 'TE', 'RB')}
VOLC = {'recyd': 'tgt', 'rec': 'tgt', 'rushyd': 'car', 'rryd': None, 'passyd': 'att', 'td': None}
SW = {0: 1.0, 1: 0.75, 2: 0.5, 3: 0.35}

def ew(x, hl):
    n = len(x)
    if n == 0: return np.nan
    w = 0.5 ** (np.arange(n)[::-1] / hl)
    return float(np.sum(w * x) / np.sum(w))

out = []
for (pid, team), d in pg.groupby(['pid', 'team'], sort=False):
    d = d.sort_values(['season', 'week'])
    seasons = d['season'].values; weeks = d['week'].values
    for stat, poss in STATS.items():
        if d['pos'].iloc[-1] not in poss: continue
        y = d[stat].values.astype(float)
        vc = VOLC[stat]; v = d[vc].values.astype(float) if vc else None
        snap = d['snap'].values
        for i in range(len(d)):
            s = seasons[i]
            cur = np.where((seasons == s) & (np.arange(len(d)) < i))[0]
            if len(cur) < 3: continue
            yc = y[cur]
            prev = np.where(seasons == s - 1)[0]
            allp = np.where(np.arange(len(d)) < i)[0]
            wts = np.array([SW.get(s - seasons[j], 0.3) for j in allp])
            row = {'pid': pid, 'team': team, 'stat': stat, 'season': s, 'week': int(weeks[i]), 'idx': int(d.index[i]), 'y': y[i],
                   'n': len(cur), 'S': yc.mean(), 'Smed': float(np.median(yc)), 'L4': yc[-4:].mean(), 'L2': yc[-2:].mean(),
                   'E2': ew(yc, 2), 'E3': ew(yc, 3), 'E4': ew(yc, 4), 'sd': yc.std(ddof=1) if len(yc) > 2 else np.nan,
                   'P': y[prev].mean() if len(prev) else np.nan, 'nP': len(prev),
                   'C': float(np.sum(wts * y[allp]) / np.sum(wts)), 'nC': len(allp),
                   'first4': yc[:4].mean(), 'snapS': np.nanmean(snap[cur]) if np.isfinite(snap[cur]).any() else np.nan,
                   'snapL4': np.nanmean(snap[cur][-4:]) if np.isfinite(snap[cur][-4:]).any() else np.nan}
            if v is not None:
                vcur = v[cur]
                row.update({'vS': vcur.mean(), 'vL4': vcur[-4:].mean(), 'vy': v[i],
                            'effS': yc.sum() / max(vcur.sum(), 1), 'effL4': yc[-4:].sum() / max(vcur[-4:].sum(), 1)})
            out.append(row)
F = pd.DataFrame(out)
F = F.merge(pg[['pos', 'name', 'opp', 'home', 'fav_by', 'total_line', 'implied', 'pts', 'qb_id']], left_on='idx', right_index=True, how='left')
F.to_pickle(S + 'mom/feat.pkl')
print(F.shape); print(F.groupby(['stat', 'season']).size().unstack())
