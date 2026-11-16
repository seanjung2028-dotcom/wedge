"""Player-game table 2023-2026 (regular season) for the momentum study and the weekly backtests.

One row per player-game for offensive skill players (QB/RB/FB/WR/TE) with box-score stats, volume, snap share,
team context (closing spread/total from nflverse schedules, team points, starting QB) and team volume that game.
Writes mom/pg.pkl.
"""
import pandas as pd, numpy as np
S = '/home/claude/wedger/'
FIX = {'LA': 'LAR', 'WAS': 'WSH', 'OAK': 'LV', 'SD': 'LAC', 'STL': 'LAR', 'JAC': 'JAX'}
fx = lambda t: FIX.get(t, t)
st = pd.concat([pd.read_csv(S + f'nflverse_dl3/stats_player_week_{y}.csv', low_memory=False) for y in (2023, 2024, 2025)] +
               [pd.read_csv(S + 'dl18/stats_player_week_2026.csv', low_memory=False)], ignore_index=True)
st = st[(st['season_type'] == 'REG') & st['position'].isin(['QB', 'RB', 'FB', 'WR', 'TE'])].copy()
st['team'] = st['team'].map(fx); st['opp'] = st['opponent_team'].map(fx)
for c in ['receptions', 'targets', 'receiving_yards', 'carries', 'rushing_yards', 'passing_yards', 'passing_tds', 'passing_interceptions',
          'attempts', 'completions', 'rushing_tds', 'receiving_tds', 'target_share', 'air_yards_share', 'receiving_air_yards', 'receiving_epa', 'rushing_epa', 'passing_epa']:
    st[c] = pd.to_numeric(st[c], errors='coerce').fillna(0)
pg = pd.DataFrame({'pid': st['player_id'], 'name': st['player_display_name'], 'pos': st['position'], 'season': st['season'].astype(int),
                   'week': st['week'].astype(int), 'team': st['team'], 'opp': st['opp'],
                   'rec': st['receptions'], 'tgt': st['targets'], 'recyd': st['receiving_yards'], 'car': st['carries'], 'rushyd': st['rushing_yards'],
                   'passyd': st['passing_yards'], 'passtd': st['passing_tds'], 'int': st['passing_interceptions'], 'att': st['attempts'],
                   'td': st['rushing_tds'] + st['receiving_tds'], 'tshare': st['target_share'], 'ayshare': st['air_yards_share'],
                   'airyd': st['receiving_air_yards'], 'rec_epa': st['receiving_epa'], 'rush_epa': st['rushing_epa'], 'pass_epa': st['passing_epa']})
pg['rryd'] = pg['recyd'] + pg['rushyd']
# snap share via pfr id
sn = pd.concat([pd.read_csv(S + f'nflverse_dl3/snap_counts_{y}.csv') for y in (2023, 2024, 2025)] + [pd.read_csv(S + 'dl18/snap_counts_2026.csv')], ignore_index=True)
sn = sn[sn['game_type'] == 'REG']
rws = pd.concat([pd.read_csv(S + f'nflverse_dl3/roster_weekly_{y}.csv', low_memory=False) for y in (2023, 2024, 2025)] +
                [pd.read_csv(S + 'dl18/roster_weekly_2026.csv', low_memory=False)], ignore_index=True)
pfr2g = dict(zip(rws['pfr_id'].dropna(), rws.loc[rws['pfr_id'].notna(), 'gsis_id']))
sn['pid'] = sn['pfr_player_id'].map(pfr2g)
snap = sn[sn['pid'].notna()].groupby(['pid', 'season', 'week'])['offense_pct'].max()
pg = pg.merge(snap.rename('snap').reset_index(), on=['pid', 'season', 'week'], how='left')
pg['snap'] = pg['snap'] * 100
# schedule context
g = pd.read_csv(S + 'dl18/games.csv'); g = g[(g['game_type'] == 'REG') & (g['season'] >= 2023)].copy()
g['away_team'] = g['away_team'].map(fx); g['home_team'] = g['home_team'].map(fx)
rows = []
for r in g.itertuples(index=False):
    for t, o, home in ((r.home_team, r.away_team, 1), (r.away_team, r.home_team, 0)):
        sp = r.spread_line if home else -r.spread_line          # nflverse: positive = home favored; here: positive = this team favored
        pts = r.home_score if home else r.away_score; opts = r.away_score if home else r.home_score
        rows.append({'season': r.season, 'week': r.week, 'team': t, 'gopp': o, 'home': home, 'fav_by': sp, 'total_line': r.total_line,
                     'implied': (r.total_line + sp) / 2 if not pd.isna(r.total_line) and not pd.isna(sp) else np.nan,
                     'pts': pts, 'opts': opts, 'qb_id': r.home_qb_id if home else r.away_qb_id, 'qb_name': r.home_qb_name if home else r.away_qb_name,
                     'roof': r.roof, 'wind': r.wind, 'temp': r.temp, 'game_id': r.game_id, 'gameday': r.gameday})
G = pd.DataFrame(rows)
pg = pg.merge(G, on=['season', 'week', 'team'], how='left')
# team volume that game (all players of the team in the table)
tv = pg.groupby(['season', 'week', 'team']).agg(team_tgt=('tgt', 'sum'), team_car=('car', 'sum'), team_att=('att', 'sum')).reset_index()
pg = pg.merge(tv, on=['season', 'week', 'team'], how='left')
pg['car_share'] = pg['car'] / pg['team_car'].replace(0, np.nan)
pg = pg.sort_values(['pid', 'season', 'week']).reset_index(drop=True)
pg.to_pickle(S + 'mom/pg.pkl')
print(pg.shape, pg.groupby('season').size().to_dict(), pg['snap'].notna().mean().round(3), pg['fav_by'].notna().mean().round(3))
print(pg[(pg.season == 2026) & (pg.week == 7)].groupby('team').size().shape)
