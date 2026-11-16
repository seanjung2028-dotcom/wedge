"""Week 9 final-card data pack: team offense/defense profiles, script splits, player usage (2026 Weeks 1-8)."""
import pandas as pd, numpy as np, json, sys
S = '/home/claude/wedger/'
pbp = pd.read_csv(S + 'dl8/play_by_play_2026.csv.gz', low_memory=False)
pbp = pbp[pbp.season_type == 'REG'] if 'season_type' in pbp.columns else pbp
ftn = pd.read_csv(S + 'dl8/ftn_charting_2026.csv', low_memory=False)
wk = pd.read_csv(S + 'dl8/stats_player_week_2026.csv', low_memory=False)
snp = pd.read_csv(S + 'dl8/snap_counts_2026.csv', low_memory=False)
G = pd.read_csv(S + 'dl8/games.csv'); G = G[(G.season == 2026) & (G.week <= 8) & G.home_score.notna()]
pbp = pbp.merge(ftn[['nflverse_game_id', 'nflverse_play_id', 'n_blitzers', 'n_pass_rushers', 'is_qb_out_of_pocket', 'is_play_action', 'is_screen_pass', 'n_defense_box']],
                left_on=['game_id', 'play_id'], right_on=['nflverse_game_id', 'nflverse_play_id'], how='left')
real = pbp[(pbp.play_type.isin(['pass', 'run'])) & (pbp.penalty.fillna(0) == 0) | ((pbp.play_type.isin(['pass', 'run'])) & pbp.penalty.fillna(0).eq(1) & pbp.yards_gained.notna())]
real = pbp[pbp.play_type.isin(['pass', 'run'])].copy()
real['qb_run'] = (real.play_type == 'run') & (real.qb_kneel == 0) & real.rusher_player_id.notna()
# team-game results
res = []
for g in G.itertuples():
    res.append({'game_id': g.game_id, 'team': g.home_team, 'opp': g.away_team, 'pf': g.home_score, 'pa': g.away_score, 'week': g.week, 'spread_line': g.spread_line})
    res.append({'game_id': g.game_id, 'team': g.away_team, 'opp': g.home_team, 'pf': g.away_score, 'pa': g.home_score, 'week': g.week, 'spread_line': -g.spread_line})
R = pd.DataFrame(res); R['margin'] = R.pf - R.pa
qbatt = wk[wk.position == 'QB'].groupby(['game_id', 'team']).agg(att=('attempts', 'sum'), cmp=('completions', 'sum'), sk=('sacks_suffered', 'sum'), pyds=('passing_yards', 'sum')).reset_index()
R = R.merge(qbatt, on=['game_id', 'team'], how='left')
ra = real[(real.play_type == 'run') & (real.qb_kneel == 0)].groupby(['game_id', 'posteam']).size().rename('rush').reset_index().rename(columns={'posteam': 'team'})
R = R.merge(ra, on=['game_id', 'team'], how='left')
dr = pbp[pbp.posteam.notna()].groupby(['game_id', 'posteam']).fixed_drive.nunique().rename('drives').reset_index().rename(columns={'posteam': 'team'})
R = R.merge(dr, on=['game_id', 'team'], how='left')
R['plays'] = R.att + R.sk + R.rush
TEAM = {}
for t, d in R.groupby('team'):
    pr = real[real.posteam == t]; neu = pr[(pr.wp.between(.2, .8)) & (pr.qtr <= 3) & (pr.down <= 2)]
    db = pr[pr.qb_dropback == 1]
    third = pr[pr.down == 3]
    split = {k: (round(v.att.mean(), 1), len(v)) for k, v in [('won8+', d[d.margin >= 8]), ('close', d[d.margin.abs() <= 7]), ('lost8+', d[d.margin <= -8])]}
    TEAM[t] = {'g': len(d), 'pf': round(d.pf.mean(), 1), 'pa': round(d.pa.mean(), 1), 'att': round(d.att.mean(), 1), 'cmp': round(d.cmp.mean(), 1), 'sk': round(d.sk.mean(), 1),
               'rush': round(d.rush.mean(), 1), 'drives': round(d.drives.mean(), 1), 'ppd': round(d.plays.sum() / d.drives.sum(), 2), 'neu_pass': round(100 * (neu.play_type == 'pass').mean(), 1),
               'third': round(100 * third.third_down_converted.sum() / max(1, (third.third_down_converted.sum() + third.third_down_failed.sum())), 1),
               'pa_rate': round(100 * db.is_play_action.mean(), 1), 'oop': round(100 * db.is_qb_out_of_pocket.mean(), 1), 'att_by_script': split,
               'logs': [f"W{int(r.week)} {'v' if True else ''}{r.opp} {int(r.pf)}-{int(r.pa)} att {int(r.att) if r.att == r.att else '-'} sk {int(r.sk) if r.sk == r.sk else '-'} ru {int(r.rush)}" for r in d.sort_values('week').itertuples()]}
    # defense
    dpl = real[real.defteam == t]; ddb = dpl[dpl.qb_dropback == 1]
    od = R[R.opp == t]
    qbr = dpl[dpl.qb_run & dpl.rusher_player_id.isin(wk[wk.position == 'QB'].player_id)]
    TEAM[t].update({'d_att': round(od.att.mean(), 1), 'd_sk': round(od.sk.mean(), 1), 'd_rush': round(od.rush.mean(), 1),
                    'd_ypc': round(dpl[(dpl.play_type == 'run') & (dpl.qb_kneel == 0)].yards_gained.mean(), 2),
                    'd_blitz': round(100 * (ddb.n_blitzers > 0).mean(), 1), 'd_rushers': round(ddb.n_pass_rushers.mean(), 2), 'd_oop': round(100 * ddb.is_qb_out_of_pocket.mean(), 1),
                    'd_box': round(dpl[dpl.play_type == 'run'].n_defense_box.mean(), 2), 'd_qbrush': round(qbr.yards_gained.sum() / max(1, len(od)), 1),
                    'd_scr': round(dpl.qb_scramble.sum() / max(1, len(od)), 1), 'd_exp': round(ddb[ddb.yards_gained >= 20].shape[0] / max(1, len(od)), 1)})
# targets allowed by position
pos = wk[['player_id', 'position']].drop_duplicates('player_id').set_index('player_id').position
tg = real[(real.play_type == 'pass') & real.receiver_player_id.notna()].copy(); tg['pos'] = tg.receiver_player_id.map(pos)
for t in TEAM:
    x = tg[tg.defteam == t]; n = TEAM[t]['g']
    TEAM[t]['d_tg'] = {p: (round((x.pos == p).sum() / n, 1), round(x[(x.pos == p)].yards_gained.sum() / n, 1)) for p in ['WR', 'TE', 'RB']}
json.dump(TEAM, open(S + 'final9/team.json', 'w'))
# players: usage
wk['g'] = 1
snap = snp.copy()
def pl_usage(team):
    w = wk[wk.team == team]; tt = w.groupby('game_id').targets.sum(); tc = w.groupby('game_id').carries.sum()
    rows = []
    for (pid, nm, ps), d in w.groupby(['player_id', 'player_display_name', 'position']):
        if ps not in ('QB', 'RB', 'WR', 'TE'): continue
        if d.targets.sum() + d.carries.sum() + d.attempts.sum() < 8: continue
        ts = d.targets.sum() / tt.loc[d.game_id].sum(); cs = d.carries.sum() / max(1, tc.loc[d.game_id].sum())
        l3 = d.sort_values('week').tail(3)
        rows.append({'name': nm, 'pos': ps, 'g': len(d), 'tgt': round(d.targets.mean(), 1), 'ts': round(100 * ts, 1), 'rec': round(d.receptions.mean(), 1), 'recyd': round(d.receiving_yards.mean(), 1),
                     'car': round(d.carries.mean(), 1), 'cs': round(100 * cs, 1), 'rushyd': round(d.rushing_yards.mean(), 1), 'att': round(d.attempts.mean(), 1), 'pyd': round(d.passing_yards.mean(), 1),
                     'l3': ' '.join(f"W{int(r.week)}:{int(r.receptions)}/{int(r.targets)}-{int(r.receiving_yards)} c{int(r.carries)}-{int(r.rushing_yards)}" + (f" a{int(r.attempts)}-{int(r.passing_yards)}" if ps == 'QB' else '') for r in l3.itertuples())})
    return sorted(rows, key=lambda r: -(r['tgt'] + r['car'] + r['att']))
U = {t: pl_usage(t) for t in TEAM}
json.dump(U, open(S + 'final9/usage.json', 'w'))
print('ok', len(TEAM))
