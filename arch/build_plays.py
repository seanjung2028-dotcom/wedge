"""Stage 1: play-level data 2023-2026 (nflverse pbp + FTN charting + participation) aggregated to player-game, team-offense-game and defense-game.
Writes arch/plays.pkl, arch/rec_pg.pkl, arch/rush_pg.pkl, arch/qb_pg.pkl, arch/off_g.pkl, arch/def_g.pkl."""
import numpy as np, pandas as pd
S = '/home/claude/wedger/'
FIX = {'LA': 'LAR', 'WAS': 'WSH', 'OAK': 'LV', 'SD': 'LAC', 'STL': 'LAR', 'JAC': 'JAX'}
cols = ['game_id', 'play_id', 'season', 'week', 'season_type', 'posteam', 'defteam', 'play_type', 'pass', 'rush', 'qb_dropback', 'qb_scramble', 'sack',
        'receiver_player_id', 'rusher_player_id', 'passer_player_id', 'air_yards', 'yards_after_catch', 'pass_location', 'run_location', 'run_gap',
        'yardline_100', 'complete_pass', 'yards_gained', 'epa', 'xpass', 'pass_oe', 'shotgun', 'no_huddle', 'touchdown', 'two_point_attempt', 'wp',
        'down', 'ydstogo', 'score_differential', 'qtr']
P = []
for y in (2023, 2024, 2025, 2026):
    d = pd.read_csv(S + f'dl8/play_by_play_{y}.csv.gz', usecols=cols, low_memory=False)
    d = d[(d['season_type'] == 'REG') & d['play_type'].isin(['pass', 'run']) & (d['two_point_attempt'] != 1)]
    ftn = S + (f'dl9/ftn_charting_{y}.csv' if y < 2026 else 'dl8/ftn_charting_2026.csv')
    f = pd.read_csv(ftn, usecols=['nflverse_game_id', 'nflverse_play_id', 'n_defense_box', 'is_motion', 'is_play_action', 'is_screen_pass', 'n_blitzers', 'is_rpo', 'n_offense_backfield'])
    f = f.rename(columns={'nflverse_game_id': 'game_id', 'nflverse_play_id': 'play_id'}).drop_duplicates(['game_id', 'play_id'])
    d = d.merge(f, on=['game_id', 'play_id'], how='left')
    if y < 2026:
        pp = pd.read_csv(S + f'dl9/pbp_participation_{y}.csv', usecols=['nflverse_game_id', 'play_id', 'route', 'defense_man_zone_type', 'defense_coverage_type', 'was_pressure', 'defenders_in_box'])
        pp = pp.rename(columns={'nflverse_game_id': 'game_id'}).drop_duplicates(['game_id', 'play_id'])
        d = d.merge(pp, on=['game_id', 'play_id'], how='left')
    else:
        for c in ('route', 'defense_man_zone_type', 'defense_coverage_type', 'was_pressure', 'defenders_in_box'): d[c] = np.nan
    P.append(d)
P = pd.concat(P, ignore_index=True)
P['posteam'] = P['posteam'].map(lambda t: FIX.get(t, t)); P['defteam'] = P['defteam'].map(lambda t: FIX.get(t, t))
P['box'] = P['n_defense_box'].fillna(P['defenders_in_box'])
P['man'] = np.where(P['defense_man_zone_type'] == 'MAN_COVERAGE', 1.0, np.where(P['defense_man_zone_type'] == 'ZONE_COVERAGE', 0.0, np.nan))
P['blitz'] = np.where(P['n_blitzers'].notna(), (P['n_blitzers'] > 0).astype(float), np.nan)
P['ay'] = P['air_yards']
DEEP = {'GO', 'POST', 'CORNER', 'WHEEL'}
P['deep_route'] = np.where(P['route'].notna(), P['route'].isin(DEEP).astype(float), np.nan)
P['neutral'] = (P['wp'].between(0.2, 0.8)) & (P['qtr'] <= 3)
P.to_pickle(S + 'arch/plays.pkl')

# ---------- receiver games ----------
T = P[(P['pass'] == 1) & P['receiver_player_id'].notna() & (P['sack'] != 1)].copy()
T['tgt'] = 1; T['deep'] = (T['ay'] >= 20).astype(float); T['short'] = (T['ay'] < 5).astype(float); T['mid'] = (T['pass_location'] == 'middle').astype(float)
T['screen'] = T['is_screen_pass'].fillna(0).astype(float); T['ry'] = np.where(T['complete_pass'] == 1, T['yards_gained'], 0.0)
T['yac'] = np.where(T['complete_pass'] == 1, T['yards_after_catch'].fillna(0), 0.0); T['rz'] = (T['yardline_100'] <= 20).astype(float)
T['vs_man'] = (T['man'] == 1).astype(float); T['vs_zone'] = (T['man'] == 0).astype(float)
T['ry_man'] = T['ry'] * T['vs_man']; T['ry_zone'] = T['ry'] * T['vs_zone']
T['deep_rt'] = T['deep_route']
g = T.groupby(['season', 'week', 'posteam', 'defteam', 'receiver_player_id'])
rec = g.agg(tgt=('tgt', 'sum'), ay=('ay', 'sum'), deep=('deep', 'sum'), short=('short', 'sum'), mid=('mid', 'sum'), screen=('screen', 'sum'),
            ry=('ry', 'sum'), yac=('yac', 'sum'), rec=('complete_pass', 'sum'), rz=('rz', 'sum'), t_man=('vs_man', 'sum'), t_zone=('vs_zone', 'sum'),
            ry_man=('ry_man', 'sum'), ry_zone=('ry_zone', 'sum'), deep_rt=('deep_rt', 'sum'), rt_n=('deep_rt', 'count')).reset_index()
rec = rec.rename(columns={'receiver_player_id': 'pid', 'posteam': 'team', 'defteam': 'opp'})
rec.to_pickle(S + 'arch/rec_pg.pkl')

# ---------- rusher games ----------
R = P[(P['rush'] == 1) & P['rusher_player_id'].notna()].copy()
R['car'] = 1; R['i10'] = (R['yardline_100'] <= 10).astype(float); R['outside'] = R['run_location'].isin(['left', 'right']).astype(float)
R['heavy'] = (R['box'] >= 8).astype(float); R['light'] = (R['box'] <= 6).astype(float); R['scr'] = R['qb_scramble'].fillna(0)
R['expl'] = (R['yards_gained'] >= 15).astype(float); R['stuff'] = (R['yards_gained'] <= 0).astype(float)
R['gun'] = R['shotgun'].fillna(0)
g = R.groupby(['season', 'week', 'posteam', 'defteam', 'rusher_player_id'])
rush = g.agg(car=('car', 'sum'), yds=('yards_gained', 'sum'), i10=('i10', 'sum'), outside=('outside', 'sum'), heavy=('heavy', 'sum'), light=('light', 'sum'),
             expl=('expl', 'sum'), stuff=('stuff', 'sum'), scr=('scr', 'sum'), gun=('gun', 'sum'), boxn=('box', 'count'), box=('box', 'mean')).reset_index()
rush = rush.rename(columns={'rusher_player_id': 'pid', 'posteam': 'team', 'defteam': 'opp'})
rush.to_pickle(S + 'arch/rush_pg.pkl')

# ---------- QB games ----------
Q = P[(P['qb_dropback'] == 1) & P['passer_player_id'].notna()].copy()
Q['db'] = 1; Q['pa'] = Q['is_play_action'].fillna(0).astype(float); Q['att'] = ((Q['pass'] == 1) & (Q['sack'] != 1) & (Q['qb_scramble'] != 1)).astype(float)
Q['ay_att'] = np.where(Q['att'] == 1, Q['ay'], np.nan); Q['prs'] = Q['was_pressure'].astype(float) if Q['was_pressure'].notna().any() else np.nan
Q['blz'] = Q['blitz']
g = Q.groupby(['season', 'week', 'posteam', 'defteam', 'passer_player_id'])
qb = g.agg(db=('db', 'sum'), att=('att', 'sum'), ay=('ay_att', 'sum'), pa=('pa', 'sum'), scr=('qb_scramble', 'sum'), sk=('sack', 'sum'),
           blz=('blz', 'mean'), prs=('prs', 'mean'), epa=('epa', 'mean')).reset_index()
qb = qb.rename(columns={'passer_player_id': 'pid', 'posteam': 'team', 'defteam': 'opp'})
qb.to_pickle(S + 'arch/qb_pg.pkl')

# ---------- team offense and defense games ----------
O = P.groupby(['season', 'week', 'posteam', 'defteam']).agg(plays=('play_id', 'size'), pass_rate=('pass', 'mean'), proe=('pass_oe', 'mean'),
       pa_rate=('is_play_action', 'mean'), motion=('is_motion', 'mean'), gun=('shotgun', 'mean'), nohud=('no_huddle', 'mean'),
       screen=('is_screen_pass', 'mean'), rpo=('is_rpo', 'mean'), epa=('epa', 'mean')).reset_index().rename(columns={'posteam': 'team', 'defteam': 'opp'})
O.to_pickle(S + 'arch/off_g.pkl')
pas = P[(P['pass'] == 1) & (P['sack'] != 1)]
runs = P[P['rush'] == 1]
Dd = P.groupby(['season', 'week', 'defteam', 'posteam']).agg(man=('man', 'mean'), blitz=('blitz', 'mean'), plays=('play_id', 'size')).reset_index()
Dp = pas.groupby(['season', 'week', 'defteam']).agg(ay_allowed=('ay', 'mean'), deep_allowed=('ay', lambda s: float((s >= 20).mean())),
       mid_allowed=('pass_location', lambda s: float((s == 'middle').mean())), pass_epa=('epa', 'mean'), cmp=('complete_pass', 'mean')).reset_index()
Dr = runs.groupby(['season', 'week', 'defteam']).agg(box8=('box', lambda s: float((s >= 8).mean()) if s.notna().any() else np.nan), rush_epa=('epa', 'mean'),
       ypc=('yards_gained', 'mean')).reset_index()
D = Dd.merge(Dp, on=['season', 'week', 'defteam'], how='left').merge(Dr, on=['season', 'week', 'defteam'], how='left').rename(columns={'defteam': 'team', 'posteam': 'opp'})
D.to_pickle(S + 'arch/def_g.pkl')
print('plays', len(P), 'rec', len(rec), 'rush', len(rush), 'qb', len(qb), 'off', len(O), 'def', len(D))
print('man coverage known', P['man'].notna().mean().round(3), 'box known', P['box'].notna().mean().round(3), 'route known', P['route'].notna().mean().round(3))
