"""mom/pg_w11.pkl = mom/pg.pkl (through Week 9) + one Week 11 row per 2026 player on a team that plays in Week 11 (latest team),
with the game context: opponent, home, favored-by and total from Kalshi's ladders (Tue Nov 10), team implied points, the team's
most recent starting QB, roof. The projection fits read these rows as 'next game'."""
import json, numpy as np, pandas as pd
W = '/home/claude/wedger/'; FIX = {'LA': 'LAR', 'WAS': 'WSH', 'JAC': 'JAX'}; fx = lambda t: FIX.get(t, t)
pg = pd.read_pickle(W + 'mom/pg.pkl')
g = pd.read_csv(W + 'dl18/games.csv'); g = g[(g.season == 2026) & (g.week == 11)]
con = json.load(open(W + 'rh/rh_w11_consensus.json'))['consensus']
cur = pg[(pg.season == 2026) & (pg.week >= 6)].sort_values('week').groupby('pid').tail(1)
qbs = pg[(pg.season == 2026) & (pg.pos == 'QB') & (pg.att.fillna(0) >= 10)].sort_values('week').groupby('team').tail(1).set_index('team')
rows = []
for r in g.itertuples(index=False):
    a, h = fx(r.away_team), fx(r.home_team); c = con[f'{a} @ {h}']; hm, tot = c['home_margin'], c['total']
    for team, opp, home in ((a, h, 0), (h, a, 1)):
        fav = hm if home else -hm
        for p in cur[cur.team.map(fx) == team].itertuples(index=False):
            d = {k: np.nan for k in pg.columns}
            d.update({'pid': p.pid, 'name': p.name, 'pos': p.pos, 'season': 2026, 'week': 11, 'team': p.team, 'opp': opp, 'gopp': opp, 'home': home,
                      'fav_by': fav, 'total_line': tot, 'implied': tot / 2 + fav / 2, 'qb_id': qbs.qb_id.get(team, '') if 'qb_id' in qbs else '',
                      'qb_name': qbs.qb_name.get(team, '') if 'qb_name' in qbs else '', 'roof': r.roof if isinstance(r.roof, str) else 'outdoors',
                      'game_id': r.game_id, 'gameday': r.gameday})
            rows.append(d)
nx = pd.DataFrame(rows)[pg.columns]
for c in pg.columns:
    if pg[c].dtype.kind in 'iub' and nx[c].isna().any(): nx[c] = nx[c].fillna(0).astype(pg[c].dtype)
out = pd.concat([pg, nx], ignore_index=True); out.to_pickle(W + 'mom/pg_w11.pkl')
print(len(nx), 'week-11 rows;', nx.team.nunique(), 'teams')
