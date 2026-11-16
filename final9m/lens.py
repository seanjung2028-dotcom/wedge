"""Matchup lens for BUF @ MIN (Mon Nov 9): defense allowed by position, target overlap, blitz splits, run direction, comparable defenses, consistency.
Writes final9m/lens.json."""
import json, numpy as np, pandas as pd
W = '/home/claude/wedger/'
FIX = {'LA': 'LAR', 'WAS': 'WSH'}; fx = lambda t: FIX.get(t, t)
p = pd.read_csv(W + 'dl17/play_by_play_2026.csv', low_memory=False)
p = p[(p.season_type == 'REG')].copy()
for c in ('posteam', 'defteam'): p[c] = p[c].map(fx)
ftn = pd.read_csv(W + 'dl17/ftn_charting_2026.csv', low_memory=False)
ftn = ftn.rename(columns={'nflverse_game_id': 'game_id', 'nflverse_play_id': 'play_id'})[['game_id', 'play_id', 'n_blitzers', 'n_pass_rushers', 'n_defense_box', 'n_offense_backfield', 'is_play_action', 'is_screen_pass']]
p = p.merge(ftn, on=['game_id', 'play_id'], how='left')
st = pd.read_csv(W + 'dl17/stats_player_week_2026.csv', low_memory=False)
POS = st.drop_duplicates('player_id').set_index('player_id')['position'].to_dict()
NAME = st.drop_duplicates('player_id').set_index('player_id')['player_display_name'].to_dict()
p['rpos'] = p['receiver_player_id'].map(POS)
live = p[(p.two_point_attempt != 1) & (p.play_type.isin(['pass', 'run'])) & (p.qb_kneel != 1) & (p.qb_spike != 1)]
pas = live[(live.pass_attempt == 1) & (live.sack != 1)]
tgt = pas[pas.receiver_player_id.notna()].copy()
tgt['bucket'] = np.where(tgt.rpos == 'TE', 'TE', np.where(tgt.rpos.isin(['RB', 'FB']), 'RB', np.where(tgt.pass_location == 'middle', 'WR middle', 'WR outside')))
tgt.loc[~tgt.rpos.isin(['TE', 'RB', 'FB', 'WR']), 'bucket'] = 'other'
run = live[(live.rush_attempt == 1)].copy()
run['dir'] = np.where((run.run_location == 'middle') | (run.run_gap == 'guard'), 'inside', np.where(run.run_gap.isin(['tackle', 'end']), 'outside', 'unknown'))
drop = live[live.qb_dropback == 1]
G = live.groupby('defteam').game_id.nunique(); GO = live.groupby('posteam').game_id.nunique()
TEAMS = sorted(G.index)

def ranks(s, high_is_most=True):
    """rank 1 = most (or highest). Returns {team: (value, rank)}."""
    r = s.rank(ascending=not high_is_most, method='min').astype(int)
    return {t: (float(s[t]), int(r[t])) for t in s.index}

D = {}
D['pass_att_faced'] = pas.groupby('defteam').size() / G
D['pass_yds_allowed'] = pas.groupby('defteam').passing_yards.sum() / G
D['rush_att_faced'] = run.groupby('defteam').size() / G
D['rush_yds_allowed'] = run.groupby('defteam').rushing_yards.sum() / G
D['ypc_allowed'] = run.groupby('defteam').rushing_yards.mean()
D['sacks'] = live.groupby('defteam').sack.sum() / G
for b in ('WR', 'TE', 'RB'):
    tb = tgt[tgt.rpos.isin(['RB', 'FB'] if b == 'RB' else [b])]
    D[f'{b}_tgt'] = tb.groupby('defteam').size() / G
    D[f'{b}_rec'] = tb.groupby('defteam').complete_pass.sum() / G
    D[f'{b}_yds'] = tb.groupby('defteam').receiving_yards.sum() / G
sh = tgt[tgt.bucket != 'other'].groupby(['defteam', 'bucket']).size().unstack(fill_value=0)
sh = sh.div(sh.sum(1), axis=0)
for b in sh.columns: D[f'share_{b}'] = sh[b]
dr = drop[drop.n_blitzers.notna()]
D['blitz_rate'] = dr.groupby('defteam').n_blitzers.apply(lambda s: (s > 0).mean())
D['box_on_runs'] = run[run.n_defense_box.notna()].groupby('defteam').n_defense_box.mean()
rz = live[live.drive_inside20 == 1].drop_duplicates(['game_id', 'fixed_drive'])
D['rz_td_rate'] = rz.groupby('defteam').fixed_drive_result.apply(lambda s: (s == 'Touchdown').mean())
D['rz_drives'] = rz.groupby('defteam').size()
for d_ in ('inside', 'outside'):
    rr = run[run.dir == d_]
    D[f'ypc_{d_}_allowed'] = rr.groupby('defteam').rushing_yards.mean()
    D[f'sr_{d_}_allowed'] = rr.groupby('defteam').success.mean()
    D[f'share_{d_}_faced'] = rr.groupby('defteam').size() / run.groupby('defteam').size()
D = {k: v.reindex(TEAMS) for k, v in D.items()}

O = {}
O['pass_att'] = pas.groupby('posteam').size() / GO
O['rush_att'] = run.groupby('posteam').size() / GO
O['rush_yds'] = run.groupby('posteam').rushing_yards.sum() / GO
O['ypc'] = run.groupby('posteam').rushing_yards.mean()
neu = live[(live.wp.between(0.2, 0.8)) & (live.down.isin([1, 2])) & (live.half_seconds_remaining > 120)]
O['neutral_pass_rate'] = neu.groupby('posteam').qb_dropback.mean()
O['proe'] = live[live.pass_oe.notna()].groupby('posteam').pass_oe.mean()
for d_ in ('inside', 'outside'):
    rr = run[(run.dir == d_) & (run.qb_scramble != 1)]
    O[f'ypc_{d_}'] = rr.groupby('posteam').rushing_yards.mean()
    O[f'sr_{d_}'] = rr.groupby('posteam').success.mean()
    O[f'share_{d_}'] = rr.groupby('posteam').size() / run[run.qb_scramble != 1].groupby('posteam').size()
O = {k: v.reindex(TEAMS) for k, v in O.items()}

def rk(table, key, team, most=True):
    s = table[key].dropna(); v, r = ranks(s, most)[team]; return {'v': round(v, 3), 'rank': r, 'of': len(s), 'lg': round(float(s.mean()), 3)}

def qb_profile(name_sub, team):
    q = tgt[(tgt.posteam == team) & (tgt.passer_player_name.str.contains(name_sub, na=False)) & (tgt.bucket != 'other')]
    s = q.bucket.value_counts(normalize=True)
    # league QB baseline among passers with 120+ targets
    allq = tgt[tgt.bucket != 'other'].groupby('passer_player_id')
    keep = [k for k, v in allq.size().items() if v >= 120]
    base = tgt[tgt.passer_player_id.isin(keep) & (tgt.bucket != 'other')].groupby('passer_player_id').bucket.value_counts(normalize=True).unstack(fill_value=0)
    out = {}
    for b in ('TE', 'RB', 'WR outside', 'WR middle'):
        v = float(s.get(b, 0)); col = base[b]
        out[b] = {'v': round(v, 3), 'rank': int((col > v).sum() + 1), 'of': int(len(col) + 1), 'lg': round(float(col.mean()), 3)}
    return {'targets': int(len(q)), 'games': int(q.game_id.nunique()), 'split': out}

def catcher_splits(team, opp_blitz):
    q = tgt[(tgt.posteam == team) & (tgt.week >= 1)].merge(pd.DataFrame(), how='left', left_index=True, right_index=True) if False else tgt[tgt.posteam == team]
    q = q[q.n_blitzers.notna()]
    allv = q.receiver_player_id.value_counts(normalize=True)
    bl = q[q.n_blitzers > 0].receiver_player_id.value_counts(normalize=True)
    nb = q[q.n_blitzers == 0].receiver_player_id.value_counts(normalize=True)
    n_bl, n_nb = int((q.n_blitzers > 0).sum()), int((q.n_blitzers == 0).sum())
    rows = []
    for pid, v in allv.items():
        if v < 0.05: continue
        b_, n_ = float(bl.get(pid, 0)), float(nb.get(pid, 0))
        exp = opp_blitz * b_ + (1 - opp_blitz) * n_
        rows.append({'player': NAME.get(pid, pid), 'pos': POS.get(pid, ''), 'all': round(float(v), 3), 'vs_blitz': round(b_, 3), 'vs_no_blitz': round(n_, 3), 'this_opp': round(exp, 3), 'uptick': round(exp - float(v), 3)})
    return {'n_blitz_targets': n_bl, 'n_no_blitz_targets': n_nb, 'rows': sorted(rows, key=lambda r: -r['this_opp'])}

def comparable(def_team, feature, n=3):
    s = D[feature].dropna(); v = s[def_team]
    others = (s.drop(def_team) - v).abs().sort_values().index[:n].tolist()
    return others, round(float(v), 3)

def player_vs(team, names, defs):
    s2 = st[(st.team.map(fx) == team) & (st.season_type == 'REG')].copy(); s2['opp'] = s2.opponent_team.map(fx)
    out = {}
    for nm in names:
        g = s2[s2.player_display_name == nm].sort_values('week')
        rows = []
        for r in g.itertuples(index=False):
            rows.append({'week': int(r.week), 'opp': r.opp, 'comp': r.opp in defs, 'tgt': int(r.targets or 0), 'rec': int(r.receptions or 0), 'recyd': int(r.receiving_yards or 0),
                         'car': int(r.carries or 0), 'rushyd': int(r.rushing_yards or 0), 'att': int(r.attempts or 0), 'pyd': int(r.passing_yards or 0), 'td': int((r.rushing_tds or 0) + (r.receiving_tds or 0))})
        out[nm] = rows
    return out

def team_side(off, de):
    L = {'off': off, 'def': de}
    L['def_ranks'] = {k: rk(D, k, de) for k in ['pass_att_faced', 'pass_yds_allowed', 'rush_att_faced', 'rush_yds_allowed', 'ypc_allowed', 'sacks', 'WR_tgt', 'WR_rec', 'WR_yds', 'TE_tgt', 'TE_rec', 'TE_yds',
                                                 'RB_tgt', 'RB_rec', 'RB_yds', 'share_TE', 'share_RB', 'share_WR outside', 'share_WR middle', 'blitz_rate', 'box_on_runs', 'rz_td_rate',
                                                 'ypc_inside_allowed', 'ypc_outside_allowed', 'sr_inside_allowed', 'sr_outside_allowed']}
    L['rz_drives'] = int(D['rz_drives'][de]); L['rz_tds'] = int(round(D['rz_td_rate'][de] * D['rz_drives'][de]))
    L['off_ranks'] = {k: rk(O, k, off) for k in ['pass_att', 'rush_att', 'rush_yds', 'ypc', 'neutral_pass_rate', 'proe', 'ypc_inside', 'ypc_outside', 'sr_inside', 'sr_outside', 'share_inside', 'share_outside']}
    # the defense's most extreme traits (|z| >= 1.2), for the comparable-opponent step
    traits = []
    for k in ['blitz_rate', 'pass_att_faced', 'share_TE', 'share_RB', 'share_WR outside', 'share_WR middle', 'ypc_inside_allowed', 'ypc_outside_allowed', 'box_on_runs', 'sacks']:
        s = D[k].dropna(); z = (s[de] - s.mean()) / s.std()
        if abs(z) >= 1.2: traits.append({'k': k, 'z': round(float(z), 2), 'v': round(float(s[de]), 3)})
    L['traits'] = sorted(traits, key=lambda t: -abs(t['z']))
    return L

BUF_O = team_side('BUF', 'MIN'); MIN_O = team_side('MIN', 'BUF')
BUF_O['qb'] = qb_profile('J.Allen', 'BUF'); MIN_O['qb'] = qb_profile('Wentz', 'MIN')
MIN_O['qb_murray'] = qb_profile('K.Murray', 'MIN') if len(tgt[tgt.passer_player_name.str.contains('K.Murray', na=False) & (tgt.posteam == 'MIN')]) else None
BUF_O['catchers'] = catcher_splits('BUF', float(D['blitz_rate']['MIN'])); MIN_O['catchers'] = catcher_splits('MIN', float(D['blitz_rate']['BUF']))
# Wentz-only catcher shares (Weeks 1-2)
wq = tgt[(tgt.posteam == 'MIN') & tgt.passer_player_name.str.contains('Wentz', na=False)]
MIN_O['wentz_shares'] = [{'player': NAME.get(k, k), 'share': round(float(v), 3), 'tgt': int(c)} for (k, v), c in zip(wq.receiver_player_id.value_counts(normalize=True).items(), wq.receiver_player_id.value_counts().values)][:6]
# comparable opponents on each defense's most extreme trait
for L, team_off in ((BUF_O, 'BUF'), (MIN_O, 'MIN')):
    comp = []
    for t in L['traits'][:2]:
        defs, v = comparable(L['def'], t['k']); played = sorted(set(st[(st.team.map(fx) == team_off)].opponent_team.map(fx)))
        comp.append({'trait': t['k'], 'v': v, 'z': t['z'], 'nearest': [{'team': d, 'v': round(float(D[t['k']][d]), 3), 'played': d in played} for d in defs]})
    L['comparable'] = comp
COMP_BUF = {d['team'] for c in BUF_O['comparable'] for d in c['nearest'] if d['played']}
COMP_MIN = {d['team'] for c in MIN_O['comparable'] for d in c['nearest'] if d['played']}
BUF_O['logs'] = player_vs('BUF', ['Josh Allen', 'James Cook', 'DJ Moore', 'Dalton Kincaid', 'Khalil Shakir', 'Keon Coleman', 'Ty Johnson', 'Dawson Knox'], COMP_BUF)
MIN_O['logs'] = player_vs('MIN', ['Carson Wentz', 'Justin Jefferson', 'T.J. Hockenson', 'Jordan Addison', 'Aaron Jones', 'Jordan Mason'], COMP_MIN)
# opponent run-defense rank for each BUF game (matchup-proof check for Cook)
ypc_rank = ranks(D['ypc_allowed'].dropna(), high_is_most=False)  # rank 1 = stingiest
for r in BUF_O['logs']['James Cook']: r['opp_ypc_rank'] = ypc_rank[r['opp']][1]
for r in MIN_O['logs']['Aaron Jones'] + MIN_O['logs']['Jordan Mason']: r['opp_ypc_rank'] = ypc_rank[r['opp']][1]
# environment: Wentz's two starts
wx = p[(p.posteam == 'MIN') & p.passer_player_name.str.contains('Wentz', na=False)].groupby('week').agg(opp=('defteam', 'first'), roof=('roof', 'first'), weather=('weather', 'first')).reset_index()
MIN_O['wentz_env'] = wx.to_dict('records')
# QB scrambles and designed runs against the blitz (MIN blitzes most)
qa = live[(live.posteam == 'BUF') & (live.qb_dropback == 1) & live.n_blitzers.notna()]
BUF_O['allen_scramble'] = {'vs_blitz': round(float(qa[qa.n_blitzers > 0].qb_scramble.mean()), 3), 'vs_no_blitz': round(float(qa[qa.n_blitzers == 0].qb_scramble.mean()), 3),
    'lg_vs_blitz': round(float(live[(live.qb_dropback == 1) & (live.n_blitzers > 0)].qb_scramble.mean()), 3)}
qd = live[(live.defteam == 'MIN') & (live.qb_scramble == 1)]
BUF_O['min_scrambles_allowed'] = {'per_game': round(len(qd) / float(G['MIN']), 2), 'yds_per_game': round(float(qd.rushing_yards.sum()) / float(G['MIN']), 1),
    'rank': ranks((live[live.qb_scramble == 1].groupby('defteam').size() / G).dropna())['MIN'][1]}
LENS = {'game': 'BUF @ MIN', 'thru': 'Week 9 Sunday (BUF and MIN: 7 games each); FTN charting through Week 8', 'BUF_off': BUF_O, 'MIN_off': MIN_O,
        'league_blitz': round(float(D['blitz_rate'].mean()), 3)}
json.dump(LENS, open(W + 'final9m/lens.json', 'w'), indent=1, default=float)
def show(L):
    print(f"\n===== {L['off']} offense vs {L['def']} defense")
    for k, v in L['def_ranks'].items(): print(f"  D {k:22s} {v['v']:8.3f}  rank {v['rank']:2d}/{v['of']} (lg {v['lg']})")
    print('  RZ', L['rz_tds'], '/', L['rz_drives'])
    for k, v in L['off_ranks'].items(): print(f"  O {k:22s} {v['v']:8.3f}  rank {v['rank']:2d}/{v['of']} (lg {v['lg']})")
    print('  traits', L['traits']); print('  comparable', L['comparable'])
    print('  QB', L['qb'])
    for r in L['catchers']['rows']: print('   ', r)
show(BUF_O); show(MIN_O)
print(MIN_O['wentz_shares']); print(MIN_O['wentz_env'])
for nm, rows in {**BUF_O['logs'], **MIN_O['logs']}.items(): print(nm, [(r['week'], r['opp'], r['tgt'], r['rec'], r['recyd'], r['car'], r['rushyd'], r.get('opp_ypc_rank'), 'C' if r['comp'] else '') for r in rows])
