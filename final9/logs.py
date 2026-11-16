"""Player-game logs 2025-2026 from play-by-play with game context, for comparable-game tests."""
import pandas as pd, numpy as np
S = '/home/claude/wedger/'
cols = ['game_id', 'season', 'week', 'season_type', 'posteam', 'defteam', 'play_type', 'qb_kneel', 'qb_scramble', 'qb_dropback', 'sack', 'pass_attempt', 'complete_pass', 'yards_gained',
        'receiver_player_id', 'rusher_player_id', 'passer_player_id', 'passing_yards', 'receiving_yards', 'rushing_yards', 'touchdown', 'pass_touchdown', 'interception', 'td_player_id',
        'home_team', 'away_team', 'total_home_score', 'total_away_score', 'qtr', 'score_differential', 'yardline_100', 'two_point_attempt', 'air_yards']
P = pd.concat([pd.read_csv(S + f'dl8/play_by_play_{y}.csv.gz', usecols=lambda c: c in cols, low_memory=False) for y in (2025, 2026)])
P = P[P.season_type == 'REG']
fin = P.groupby('game_id').agg(hs=('total_home_score', 'max'), as_=('total_away_score', 'max'), home=('home_team', 'first'), away=('away_team', 'first'), season=('season', 'first'), week=('week', 'first')).reset_index()
pl = P[P.play_type.isin(['pass', 'run']) & (P.two_point_attempt != 1)]
rows = []
# receiving
r = pl[pl.receiver_player_id.notna() & (pl.play_type == 'pass')].groupby(['game_id', 'posteam', 'receiver_player_id']).agg(tgt=('pass_attempt', 'size'), rec=('complete_pass', 'sum'), recyd=('receiving_yards', 'sum'), rz=('yardline_100', lambda s: (s <= 20).sum())).reset_index().rename(columns={'receiver_player_id': 'pid'})
u = pl[pl.rusher_player_id.notna() & (pl.play_type == 'run') & (pl.qb_kneel != 1)].groupby(['game_id', 'posteam', 'rusher_player_id']).agg(car=('play_type', 'size'), rushyd=('rushing_yards', 'sum'), scr=('qb_scramble', 'sum')).reset_index().rename(columns={'rusher_player_id': 'pid'})
q = pl[pl.passer_player_id.notna() & (pl.play_type == 'pass')]
q = q.groupby(['game_id', 'posteam', 'passer_player_id']).agg(att=('pass_attempt', lambda s: 0), db=('qb_dropback', 'sum'), cmp=('complete_pass', 'sum'), pyd=('passing_yards', 'sum'), sk=('sack', 'sum'), ptd=('pass_touchdown', 'sum'), ints=('interception', 'sum')).reset_index().rename(columns={'passer_player_id': 'pid'})
qa = pl[(pl.play_type == 'pass') & (pl.sack != 1) & pl.passer_player_id.notna() & (pl.qb_scramble != 1)].groupby(['game_id', 'passer_player_id']).size().rename('att').reset_index().rename(columns={'passer_player_id': 'pid'})
q = q.drop(columns='att').merge(qa, on=['game_id', 'pid'], how='left')
td = P[P.td_player_id.notna() & (P.touchdown == 1) & P.play_type.isin(['pass', 'run'])].groupby(['game_id', 'td_player_id']).size().rename('td').reset_index().rename(columns={'td_player_id': 'pid'})
L = r.merge(u, on=['game_id', 'posteam', 'pid'], how='outer').merge(q, on=['game_id', 'posteam', 'pid'], how='outer').merge(td, on=['game_id', 'pid'], how='left').fillna(0)
L = L.merge(fin, on='game_id', how='left')
L['opp'] = np.where(L.posteam == L.home, L.away, L.home)
L['pf'] = np.where(L.posteam == L.home, L.hs, L.as_); L['pa'] = np.where(L.posteam == L.home, L.as_, L.hs); L['margin'] = L.pf - L.pa
# team context: team pass attempts, team rushes, main QB
ta = pl[(pl.play_type == 'pass') & (pl.sack != 1) & (pl.qb_scramble != 1)].groupby(['game_id', 'posteam']).size().rename('team_att')
tr = pl[(pl.play_type == 'run') & (pl.qb_kneel != 1)].groupby(['game_id', 'posteam']).size().rename('team_rush')
tt = pl[(pl.play_type == 'pass') & pl.receiver_player_id.notna()].groupby(['game_id', 'posteam']).size().rename('team_tgt')
mq = q.sort_values('db', ascending=False).drop_duplicates(['game_id', 'posteam']).set_index(['game_id', 'posteam']).pid.rename('qb_pid')
L = L.join(ta, on=['game_id', 'posteam']).join(tr, on=['game_id', 'posteam']).join(tt, on=['game_id', 'posteam']).join(mq, on=['game_id', 'posteam'])
# names
w = pd.read_csv(S + 'dl8/stats_player_week_2026.csv', usecols=['player_id', 'player_display_name', 'position'], low_memory=False).drop_duplicates('player_id')
ros = pd.read_csv(S + 'dl8/roster_weekly_2026.csv', usecols=lambda c: c in ('gsis_id', 'full_name', 'position'), low_memory=False).drop_duplicates('gsis_id').rename(columns={'gsis_id': 'player_id', 'full_name': 'player_display_name'})
nm = pd.concat([w, ros]).drop_duplicates('player_id').set_index('player_id')
L['name'] = L.pid.map(nm.player_display_name); L['pos'] = L.pid.map(nm.position); L['qb'] = L.qb_pid.map(nm.player_display_name)
L.to_csv(S + 'final9/logs.csv', index=False)
print(L.shape, L.season.value_counts().to_dict())
