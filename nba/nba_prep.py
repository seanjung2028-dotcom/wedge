"""NBA player game logs + team/defense context from hoopR (ESPN) box scores.

Seasons: 2025-26 regular season (player_box_2026.csv) and 2026-27 so far (player_box_2027.parquet).
Writes nba_logs.pkl: {'logs': DataFrame (one row per player-game), 'team': DataFrame (one row per team-game)}.
"""
import pandas as pd, numpy as np

D = '/home/claude/wedger/nba/'
FIX = {'GS': 'GSW', 'NY': 'NYK', 'SA': 'SAS', 'NO': 'NOP', 'UTAH': 'UTA', 'WSH': 'WAS', 'BKN': 'BKN', 'PHO': 'PHX'}
fx = lambda t: FIX.get(t, t)
COLS = ['game_id', 'season', 'season_type', 'game_date', 'game_date_time', 'athlete_id', 'athlete_display_name', 'team_abbreviation',
        'opponent_team_abbreviation', 'home_away', 'team_score', 'opponent_team_score', 'minutes', 'points', 'rebounds', 'assists',
        'three_point_field_goals_made', 'three_point_field_goals_attempted', 'field_goals_attempted', 'free_throws_attempted',
        'offensive_rebounds', 'turnovers', 'steals', 'blocks', 'starter', 'did_not_play', 'reason', 'athlete_position_abbreviation', 'active']
a = pd.read_csv(D + 'player_box_2026.csv', usecols=COLS, low_memory=False)
a = a[a['season_type'] == 2]
b = pd.read_parquet(D + 'player_box_2027.parquet')[COLS]
b = b[b['season_type'] == 2] if (b['season_type'] == 2).any() else b
L = pd.concat([a, b], ignore_index=True)
# games hoopR hasn't published yet: ESPN box scores transcribed into nba_box_extra.json (final games only)
import json, os, sys
sys.path.insert(0, D); import nba_model as M
TOT = {}
if os.path.exists(D + 'nba_box_extra.json'):
    have = set(L['game_id'].astype(int))
    L['game_date'] = pd.to_datetime(L['game_date']).dt.strftime('%Y-%m-%d')
    L['nnx'] = L['athlete_display_name'].astype(str).map(M.norm_name)
    last = L.sort_values('game_date').drop_duplicates(['nnx', 'team_abbreviation'], keep='last')
    by_nt = {(r.nnx, fx(r.team_abbreviation)): (r.athlete_id, r.athlete_position_abbreviation) for r in last.itertuples(index=False)}
    by_n = {r.nnx: (r.athlete_id, r.athlete_position_abbreviation) for r in last.itertuples(index=False)}
    rows = []
    for g in json.load(open(D + 'nba_box_extra.json'))['games']:
        if not g['final'] or int(g['event']) in have: continue
        for side, other in (('away', 'home'), ('home', 'away')):
            t, o = g[side], g[other]
            if t.get('totals'): TOT[(int(g['event']), t['abbr'])] = t['totals']
            for p in t['players']:
                n = M.norm_name(p['name']); pid, pos = by_nt.get((n, t['abbr'])) or by_n.get(n) or (-(abs(hash(n)) % 10**9), None)
                rows.append({'game_id': int(g['event']), 'season': 2027, 'season_type': 2, 'game_date': g['date'], 'game_date_time': g['date'] + 'T19:00:00-05:00',
                             'athlete_id': pid, 'athlete_display_name': p['name'], 'team_abbreviation': t['abbr'], 'opponent_team_abbreviation': o['abbr'], 'home_away': side,
                             'team_score': t['score'], 'opponent_team_score': o['score'], 'minutes': np.nan if p['dnp'] else p['min'], 'points': p['pts'], 'rebounds': p['reb'],
                             'assists': p['ast'], 'three_point_field_goals_made': p['3pm'], 'three_point_field_goals_attempted': np.nan, 'field_goals_attempted': np.nan,
                             'free_throws_attempted': np.nan, 'offensive_rebounds': np.nan, 'turnovers': np.nan, 'steals': np.nan, 'blocks': np.nan, 'starter': bool(p.get('starter')),
                             'did_not_play': bool(p['dnp']), 'reason': '', 'athlete_position_abbreviation': pos, 'active': not p['dnp']})
    L = pd.concat([L.drop(columns=['nnx']), pd.DataFrame(rows)], ignore_index=True)
    print('extra player rows', len(rows), 'games', len({r['game_id'] for r in rows}))
L['team'] = L['team_abbreviation'].map(fx); L['opp'] = L['opponent_team_abbreviation'].map(fx)
T30 = {'ATL','BOS','BKN','CHA','CHI','CLE','DAL','DEN','DET','GSW','HOU','IND','LAC','LAL','MEM','MIA','MIL','MIN','NOP','NYK','OKC','ORL','PHI','PHX','POR','SAC','SAS','TOR','UTA','WAS'}
L = L[L['team'].isin(T30) & L['opp'].isin(T30)].copy()   # drops All-Star exhibition teams
L['date'] = pd.to_datetime(L['game_date']).dt.strftime('%Y-%m-%d')
L['yy'] = L['season'] % 100          # 26 = 2025-26, 27 = 2026-27
L['min'] = pd.to_numeric(L['minutes'], errors='coerce')
for c, s in [('pts', 'points'), ('reb', 'rebounds'), ('ast', 'assists'), ('3pm', 'three_point_field_goals_made'), ('3pa', 'three_point_field_goals_attempted'),
             ('fga', 'field_goals_attempted'), ('fta', 'free_throws_attempted'), ('oreb', 'offensive_rebounds'), ('tov', 'turnovers'), ('stl', 'steals'), ('blk', 'blocks')]:
    L[c] = pd.to_numeric(L[s], errors='coerce')
L['pra'] = L['pts'] + L['reb'] + L['ast']
L['margin'] = L['team_score'] - L['opponent_team_score']
L['home'] = (L['home_away'] == 'home').astype(int)
L['dnp'] = L['did_not_play'].fillna(False).astype(bool) | L['min'].isna() | (L['min'] <= 0)
L['pos'] = L['athlete_position_abbreviation'].fillna('')
L['grp'] = L['pos'].map(lambda p: 'C' if p in ('C',) else ('F' if p in ('F', 'PF', 'SF', 'FC') else 'G'))
L = L.rename(columns={'athlete_id': 'pid', 'athlete_display_name': 'name'})

# team-game table: totals, possessions
played = L[~L['dnp']]
T = played.groupby(['game_id', 'date', 'yy', 'team', 'opp', 'home']).agg(
    pts=('pts', 'sum'), reb=('reb', 'sum'), ast=('ast', 'sum'), tpm=('3pm', 'sum'), fga=('fga', 'sum'), fta=('fta', 'sum'),
    oreb=('oreb', 'sum'), tov=('tov', 'sum'), score=('team_score', 'first'), opp_score=('opponent_team_score', 'first')).reset_index()
for (gid, tm), tt in TOT.items():
    m = (T['game_id'] == gid) & (T['team'] == tm)
    for c in ('fga', 'fta', 'oreb', 'tov'): T.loc[m, c] = tt[c]
T['poss'] = T['fga'] + 0.44 * T['fta'] - T['oreb'] + T['tov']
# opponent's possessions and pace (average of both sides)
o = T[['game_id', 'team', 'poss']].rename(columns={'team': 'opp', 'poss': 'opp_poss'})
T = T.merge(o, on=['game_id', 'opp'], how='left')
T['pace'] = (T['poss'] + T['opp_poss']) / 2
# rest days for each team-game
T = T.sort_values(['team', 'date'])
T['prev'] = T.groupby('team')['date'].shift(1)
T['rest'] = (pd.to_datetime(T['date']) - pd.to_datetime(T['prev'])).dt.days - 1
L = L.merge(T[['game_id', 'team', 'rest', 'pace']], on=['game_id', 'team'], how='left')
L = L.sort_values(['pid', 'date']).reset_index(drop=True)
pd.to_pickle({'logs': L, 'team': T}, D + 'nba_logs.pkl')
print('player-games', len(L), 'played', int((~L['dnp']).sum()), 'team-games', len(T), 'dates', L['date'].min(), L['date'].max())
print(L[L['yy'] == 27].groupby('date').game_id.nunique())
