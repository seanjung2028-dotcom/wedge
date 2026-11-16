"""Team momentum: offense by game 2023-2026 from nflverse play-by-play.

Per team-game: offensive EPA/play and success rate (pass + run plays, win prob 5-95%), points, starting QB.
Opponent-adjusted EPA = raw minus (what that defense allowed in its other games this season - league average).
A. Persistence: next game's adjusted EPA vs season-to-date and last-4 (2023-2025 + 2026), slope and best blend.
B. 2026: Weeks 1-4 vs the last 4 games, risers and fallers, with QB changes and schedule strength.
Writes mom/team.json and mom/team_games.pkl.
"""
import json, numpy as np, pandas as pd
S = '/home/claude/wedger/'
FIX = {'LA': 'LAR', 'WAS': 'WSH', 'OAK': 'LV', 'SD': 'LAC', 'STL': 'LAR', 'JAC': 'JAX'}
cols = ['game_id', 'season', 'week', 'season_type', 'posteam', 'defteam', 'play_type', 'epa', 'success', 'wp', 'passer_player_id', 'passer_player_name', 'pass', 'rush', 'qb_dropback']
P = []
for y in (2023, 2024, 2025, 2026):
    d = pd.read_csv(S + f'dl8/play_by_play_{y}.csv.gz', usecols=cols, low_memory=False)
    P.append(d[(d['season_type'] == 'REG') & d['play_type'].isin(['pass', 'run']) & d['epa'].notna()])
P = pd.concat(P, ignore_index=True)
P['posteam'] = P['posteam'].map(lambda t: FIX.get(t, t)); P['defteam'] = P['defteam'].map(lambda t: FIX.get(t, t))
P = P[P['wp'].between(0.05, 0.95)]
tg = P.groupby(['season', 'week', 'posteam', 'defteam']).agg(epa=('epa', 'mean'), sr=('success', 'mean'), plays=('epa', 'size'),
                                                              pass_rate=('qb_dropback', 'mean')).reset_index()
qb = P[P['passer_player_id'].notna()].groupby(['season', 'week', 'posteam'])['passer_player_name'].agg(lambda s: s.value_counts().index[0]).rename('qb')
tg = tg.merge(qb.reset_index(), on=['season', 'week', 'posteam'], how='left')
g = pd.read_pickle(S + 'mom/pg.pkl')[['season', 'week', 'team', 'pts', 'fav_by', 'implied']].drop_duplicates(['season', 'week', 'team'])
tg = tg.merge(g, left_on=['season', 'week', 'posteam'], right_on=['season', 'week', 'team'], how='left')
# opponent adjustment: defense's EPA allowed in its OTHER games this season
tg['adj'] = np.nan
for s, d in tg.groupby('season'):
    lg = d['epa'].mean()
    for i, r in d.iterrows():
        other = d[(d['defteam'] == r['defteam']) & (d['week'] != r['week'])]
        tg.loc[i, 'adj'] = r['epa'] - (other['epa'].mean() - lg) if len(other) else r['epa']
tg = tg.sort_values(['posteam', 'season', 'week']).reset_index(drop=True)
rows = []
for (t, s), d in tg.groupby(['posteam', 'season']):
    a = d['adj'].values; p = d['pts'].values
    for i in range(3, len(d)):
        rows.append({'team': t, 'season': s, 'week': int(d['week'].iloc[i]), 'y': a[i], 'S': a[:i].mean(), 'L4': a[max(0, i - 4):i].mean(),
                     'ypts': p[i], 'Spts': np.nanmean(p[:i]), 'L4pts': np.nanmean(p[max(0, i - 4):i]), 'implied': d['implied'].iloc[i],
                     'qb_change': d['qb'].iloc[i] != d['qb'].iloc[i - 1]})
T = pd.DataFrame(rows)
out = {}
def slope(x, y):
    m = np.isfinite(x) & np.isfinite(y); return round(float(np.polyfit(x[m], y[m], 1)[0]), 3)
H = T[T['season'] <= 2025]
out['persist_epa'] = slope((H['L4'] - H['S']).values, (H['y'] - H['S']).values)
out['persist_pts'] = slope((H['L4pts'] - H['Spts']).values, (H['ypts'] - H['Spts']).values)
out['mae_epa'] = {k: round(float((H['y'] - H[k]).abs().mean()), 4) for k in ('S', 'L4')}
ws = np.linspace(0, 1, 21)
out['best_w_L4_epa'] = float(ws[int(np.argmin([((H['y'] - ((1 - w) * H['S'] + w * H['L4'])).abs().mean()) for w in ws]))])
# do points beat the books' implied total? (is recent scoring momentum priced?)
I = T[T['implied'].notna()]
I = I.assign(res=I['ypts'] - I['implied'], mom=I['L4pts'] - I['Spts'])
out['pts_vs_implied_by_momentum'] = {
    'hot (L4 pts >= season +4)': {'n': int((I['mom'] >= 4).sum()), 'avg_beat_implied': round(float(I[I['mom'] >= 4]['res'].mean()), 2)},
    'cold (L4 pts <= season -4)': {'n': int((I['mom'] <= -4).sum()), 'avg_beat_implied': round(float(I[I['mom'] <= -4]['res'].mean()), 2)},
    'flat': {'n': int((I['mom'].abs() < 4).sum()), 'avg_beat_implied': round(float(I[I['mom'].abs() < 4]['res'].mean()), 2)}}
# 2026 risers / fallers: first four games vs last four games
cur = tg[tg['season'] == 2026]
team26 = []
for t, d in cur.groupby('posteam'):
    d = d.sort_values('week')
    f4, l4 = d.head(4), d.tail(4)
    sched_f = f4['epa'].mean() - f4['adj'].mean(); sched_l = l4['epa'].mean() - l4['adj'].mean()
    team26.append({'team': t, 'games': int(len(d)), 'epa_first4': round(float(f4['adj'].mean()), 3), 'epa_last4': round(float(l4['adj'].mean()), 3),
                   'change': round(float(l4['adj'].mean() - f4['adj'].mean()), 3), 'pts_first4': round(float(f4['pts'].mean()), 1),
                   'pts_last4': round(float(l4['pts'].mean()), 1), 'sr_first4': round(float(100 * f4['sr'].mean()), 1), 'sr_last4': round(float(100 * l4['sr'].mean()), 1),
                   'qbs_first4': '/'.join(pd.unique(f4['qb'].dropna())), 'qbs_last4': '/'.join(pd.unique(l4['qb'].dropna())),
                   'opp_easier_last4': round(float(sched_l - sched_f), 3), 'weeks': ','.join(str(w) for w in d['week'])})
team26 = sorted(team26, key=lambda r: -r['change'])
out['teams_2026'] = team26
json.dump(out, open(S + 'mom/team.json', 'w'), indent=1)
tg.to_pickle(S + 'mom/team_games.pkl')
print(json.dumps({k: v for k, v in out.items() if k != 'teams_2026'}, indent=1))
for r in team26: print(r)
