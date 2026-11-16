"""Week 7 matchup, game-script and conditions context (nfl_ctx.json + nflctx_w7.csv).

Per defense (2026 Weeks 1-6 unless noted):
  pass D: EPA per dropback allowed, explosive-pass rate (20+ yd) allowed, sack rate, pressure rate (PFR pressures / dropbacks),
          blitz rate and average box (FTN charting), and 2025 coverage shells (man rate, top shells) from NGS/FTN participation
  vs position: targets, receptions and yards allowed per game to WRs, TEs and RBs, with league ranks
  run D: yards per carry and rush yards per game allowed
  coverage defenders: top players by targets in coverage (PFR): targets, yards/target, passer rating allowed, and this week's
          practice / game status
Per game: head coaches, venue, roof, surface, forecast (Open-Meteo), Robinhood/books spread and total, implied team totals,
  and game-script odds (lead by 8+, within a score, trail by 8+) from a normal margin with a 13.5-point spread.
"""
import json, math, collections, statistics
import pandas as pd
from scipy import stats

B = '/home/claude/wedger/rh/'
S = '/home/claude/wedger/'
FIX = {'LA': 'LAR', 'WAS': 'WSH', 'OAK': 'LV', 'SD': 'LAC', 'STL': 'LAR', 'JAC': 'JAX'}
fx = lambda t: FIX.get(t, t)

pbp = pd.read_csv(S + 'nflverse_dl/pbp2026_w6full.csv.gz', low_memory=False,
                  usecols=['play_id', 'game_id', 'week', 'posteam', 'defteam', 'play_type', 'yards_gained', 'qb_dropback', 'epa',
                           'success', 'sack', 'pass', 'rush', 'pass_attempt', 'rush_attempt', 'receiver_player_id', 'complete_pass', 'air_yards'])
pbp = pbp[pbp['week'] <= 6].copy()
pbp['posteam'] = pbp['posteam'].map(fx); pbp['defteam'] = pbp['defteam'].map(fx)
ftn = pd.read_csv(S + 'dl4/ftn_charting_2026.csv', low_memory=False)
ftn = ftn[ftn['week'] <= 6]
pbp = pbp.merge(ftn[['nflverse_game_id', 'nflverse_play_id', 'n_blitzers', 'n_pass_rushers', 'n_defense_box', 'is_play_action']],
                left_on=['game_id', 'play_id'], right_on=['nflverse_game_id', 'nflverse_play_id'], how='left')
adv = pd.read_csv(S + 'dl4/advstats_week_def_2026.csv')
adv = adv[(adv['game_type'] == 'REG') & (adv['week'] <= 6)].copy(); adv['team'] = adv['team'].map(fx)
rw = pd.read_csv(S + 'dl4/roster_weekly_2026.csv', low_memory=False); rw['team'] = rw['team'].map(fx)
inj = pd.read_csv(S + 'dl4/injuries_2026.csv'); inj['team'] = inj['team'].map(fx)
st = pd.read_csv(S + 'nflverse_dl3/stats_player_week_2026.csv', low_memory=False)
st = st[(st['season_type'] == 'REG') & (st['week'] <= 6)].copy()
st['team'] = st['team'].map(fx); st['opponent_team'] = st['opponent_team'].map(fx)
part = pd.read_csv(S + 'dl4/pbp_participation_2025.csv', low_memory=False,
                   usecols=['nflverse_game_id', 'possession_team', 'defense_man_zone_type', 'defense_coverage_type', 'was_pressure'])
games = pd.read_csv(S + 'dl4/games.csv')
an = json.load(open(B + 'an_w7.json'))
weather = json.load(open(B + 'weather_w7.json'))

# ---------------- pass / run defense ----------------
db = pbp[pbp['qb_dropback'] == 1]
ru = pbp[(pbp['rush'] == 1) & (pbp['qb_dropback'] != 1)]
team_games = pbp.groupby('defteam')['game_id'].nunique()
D = {}
lg = {}
for t, g in db.groupby('defteam'):
    pa = g[g['pass_attempt'] == 1]
    D[t] = {'games': int(team_games[t]), 'dropbacks': int(len(g)),
            'epa_db': round(float(g['epa'].mean()), 3), 'success_db': round(100 * float(g['success'].mean()), 1),
            'explosive': round(100 * float((pa['yards_gained'] >= 20).mean()), 1),
            'sack_rate': round(100 * float(g['sack'].mean()), 1),
            'blitz': round(100 * float((g['n_blitzers'].fillna(0) > 0).mean()), 1) if g['n_blitzers'].notna().any() else None,
            'rushers': round(float(g['n_pass_rushers'].mean()), 2) if g['n_pass_rushers'].notna().any() else None}
for t, g in ru.groupby('defteam'):
    D[t].update({'ypc': round(float(g['yards_gained'].mean()), 2), 'rush_ypg': round(float(g['yards_gained'].sum()) / D[t]['games'], 1),
                 'box': round(float(g['n_defense_box'].mean()), 2) if g['n_defense_box'].notna().any() else None})
press = adv.groupby('team')['def_pressures'].sum()
for t in D:
    D[t]['pressure'] = round(100 * float(press.get(t, 0)) / max(1, D[t]['dropbacks']), 1)
# 2025 coverage shells (charting for 2026 is not public yet)
part['defteam'] = part.apply(lambda r: [x for x in r['nflverse_game_id'].split('_')[2:4] if x != r['possession_team']][0]
                             if r['possession_team'] in r['nflverse_game_id'] else None, axis=1).map(lambda x: fx(x) if x else x)
cov = part[part['defense_coverage_type'].notna() & part['defteam'].notna()]
for t, g in cov.groupby('defteam'):
    if t not in D: continue
    mz = g['defense_man_zone_type'].value_counts(normalize=True)
    shells = g['defense_coverage_type'].value_counts(normalize=True).head(3)
    D[t]['man_2025'] = round(100 * float(mz.get('MAN_COVERAGE', 0)), 1)
    D[t]['shells_2025'] = [[k.replace('_', ' ').title().replace('Cover ', 'Cover '), round(100 * float(v), 1)] for k, v in shells.items()]

# vs position (targets / receptions / yards allowed per game)
_dp = rw.sort_values('week').drop_duplicates('gsis_id', keep='last')
def _pos(r):
    d = r['depth_chart_position'] if isinstance(r['depth_chart_position'], str) else ''
    if d in ('CB', 'LCB', 'RCB', 'NB'): return 'CB'
    if d in ('FS', 'SS', 'S'): return 'S'
    if d in ('LB', 'ILB', 'OLB', 'MLB', 'WLB', 'SLB', 'LILB', 'RILB', 'LOLB', 'ROLB'): return 'LB'
    if d in ('DE', 'DT', 'NT', 'LDE', 'RDE', 'LDT', 'RDT', 'EDGE'): return 'DL'
    return d or r['position']
pos_of = {r['gsis_id']: _pos(r) for _, r in _dp.iterrows()}
st['grp'] = st['position'].map(lambda p: p if p in ('WR', 'TE', 'RB') else ('RB' if p == 'FB' else None))
for grp in ('WR', 'TE', 'RB'):
    sg = st[st['grp'] == grp].groupby('opponent_team').agg(tgt=('targets', 'sum'), rec=('receptions', 'sum'), yds=('receiving_yards', 'sum'),
                                                           ryds=('rushing_yards', 'sum'), car=('carries', 'sum'),
                                                           tds=('receiving_tds', 'sum'), rtds=('rushing_tds', 'sum'))
    for t, r in sg.iterrows():
        if t not in D: continue
        n = D[t]['games']
        D[t][f'{grp}_tgt_pg'] = round(r['tgt'] / n, 1); D[t][f'{grp}_rec_pg'] = round(r['rec'] / n, 1)
        D[t][f'{grp}_yds_pg'] = round(r['yds'] / n, 1); D[t][f'{grp}_ypt'] = round(r['yds'] / max(1, r['tgt']), 2)
        if grp == 'RB': D[t]['RB_rush_pg'] = round(r['ryds'] / n, 1)
        D[t][f'{grp}_td_pg'] = round((r['tds'] + (r['rtds'] if grp == 'RB' else 0)) / n, 2)
    # ranks (1 = most allowed)
    for key in (f'{grp}_yds_pg', f'{grp}_rec_pg', f'{grp}_ypt'):
        order = sorted([t for t in D if key in D[t]], key=lambda t: -D[t][key])
        for i, t in enumerate(order): D[t][key + '_rk'] = i + 1
for key in ('epa_db', 'explosive', 'ypc', 'RB_rush_pg', 'pressure', 'blitz', 'sack_rate', 'box', 'WR_td_pg', 'TE_td_pg', 'RB_td_pg', 'success_db'):
    order = sorted([t for t in D if D[t].get(key) is not None], key=lambda t: -D[t][key])
    for i, t in enumerate(order): D[t][key + '_rk'] = i + 1
LG = {k: round(statistics.mean(D[t][k] for t in D if D[t].get(k) is not None), 3)
      for k in ('epa_db', 'success_db', 'box', 'explosive', 'sack_rate', 'pressure', 'blitz', 'ypc', 'RB_rush_pg', 'WR_yds_pg', 'TE_yds_pg', 'RB_yds_pg',
                'WR_rec_pg', 'TE_rec_pg', 'RB_rec_pg', 'WR_ypt', 'TE_ypt', 'RB_ypt', 'WR_td_pg', 'TE_td_pg', 'RB_td_pg', 'man_2025')}

# ---------------- coverage defenders ----------------
pfr2gsis = dict(zip(rw['pfr_id'].dropna(), rw.loc[rw['pfr_id'].notna(), 'gsis_id']))
name_of = dict(zip(rw['gsis_id'], rw['full_name']))
w7 = inj[(inj['season'] == 2026) & (inj['week'] == 7)]
status = {}
for r in w7.itertuples(index=False):
    s = r.report_status if isinstance(r.report_status, str) else ''
    pr = r.practice_status if isinstance(r.practice_status, str) else ''
    inj_txt = r.report_primary_injury if isinstance(r.report_primary_injury, str) else (r.practice_primary_injury if isinstance(r.practice_primary_injury, str) else '')
    status[r.gsis_id] = {'game': s, 'practice': pr.replace(' Participation in Practice', '').replace('Did Not Participate In Practice', 'Did not practice'), 'injury': inj_txt}
rw7 = rw[rw['week'] == rw['week'].max()]
rstat = dict(zip(rw7['gsis_id'], rw7['status']))
cov_players = adv.groupby(['team', 'pfr_player_id']).agg(name=('pfr_player_name', 'first'), g=('week', 'nunique'), tgt=('def_targets', 'sum'),
                                                         cmp=('def_completions_allowed', 'sum'), yds=('def_yards_allowed', 'sum'),
                                                         td=('def_receiving_td_allowed', 'sum'), ints=('def_ints', 'sum'),
                                                         mt=('def_missed_tackles', 'sum'), tk=('def_tackles_combined', 'sum'),
                                                         prs=('def_pressures', 'sum'), sk=('def_sacks', 'sum')).reset_index()
lg_ypt = float(cov_players['yds'].sum() / cov_players['tgt'].sum())
DEF = collections.defaultdict(list)
TACK = collections.defaultdict(list); RUSHERS = collections.defaultdict(list)
for r in cov_players.itertuples(index=False):
    gs = pfr2gsis.get(r.pfr_player_id)
    stt = status.get(gs, {})
    out = (rstat.get(gs, 'ACT') not in ('ACT', None)) or stt.get('game') in ('Out', 'Doubtful')
    base = {'name': name_of.get(gs, r.name), 'pos': pos_of.get(gs, ''), 'g': int(r.g), 'status': ('Out' if out and not stt.get('game') else stt.get('game') or ''),
            'practice': stt.get('practice', ''), 'out': bool(out)}
    if r.tk >= 8: TACK[r.team].append({**base, 'tk': int(r.tk), 'mt': int(r.mt), 'mt_pct': round(100 * r.mt / max(1, r.tk + r.mt), 1)})
    if r.prs >= 3: RUSHERS[r.team].append({**base, 'prs': int(r.prs), 'sk': float(r.sk)})
for r in cov_players.itertuples(index=False):
    if r.tgt < 5: continue
    gs = pfr2gsis.get(r.pfr_player_id)
    pos = pos_of.get(gs, '')
    grp = pos if pos in ('CB', 'S', 'LB', 'DL') else ('CB' if pos == 'DB' else (pos or '?'))
    stt = status.get(gs, {})
    out = (rstat.get(gs, 'ACT') not in ('ACT', None)) or stt.get('game') in ('Out', 'Doubtful')
    DEF[r.team].append({'name': name_of.get(gs, r.name), 'pos': grp, 'g': int(r.g), 'tgt': int(r.tgt), 'cmp': int(r.cmp), 'yds': int(r.yds),
                        'ypt': round(r.yds / r.tgt, 1), 'td': int(r.td), 'int': int(r.ints), 'mt': int(r.mt),
                        'status': ('Out' if out and not stt.get('game') else stt.get('game') or ''), 'practice': stt.get('practice', ''),
                        'injury': stt.get('injury', ''), 'out': bool(out)})
for t in DEF:
    DEF[t].sort(key=lambda d: -d['tgt'])
    # coverage factor by group: yards/target allowed by the defenders playing this week vs league, weighted by targets, shrunk
    for grp, poss in (('WR', ('CB',)), ('TE', ('S', 'LB')), ('RB', ('LB', 'S'))):
        act = [d for d in DEF[t] if d['pos'] in poss and not d['out']]
        allp = [d for d in DEF[t] if d['pos'] in poss]
        if not act: continue
        ypt_act = sum(d['yds'] for d in act) / max(1, sum(d['tgt'] for d in act))
        ypt_all = sum(d['yds'] for d in allp) / max(1, sum(d['tgt'] for d in allp))
        n = sum(d['tgt'] for d in act)
        w = n / (n + 60)
        D[t][f'cov_{grp}'] = round(w * ypt_act / lg_ypt + (1 - w), 3)
        D[t][f'cov_{grp}_missing'] = round(ypt_act / ypt_all, 3) if ypt_all else 1.0
LG['ypt_cov'] = round(lg_ypt, 2)

# ---------------- games: coaches, venue, conditions, market script ----------------
def imp(o): return 100 / (o + 100) if o > 0 else -o / (-o + 100)
G = {}
# nflverse coach fields lag 2026 hires (checked against Wikipedia's current head coach list, Oct 22)
COACH_FIX = {'ATL': 'Kevin Stefanski', 'ARI': 'Mike LaFleur', 'LV': 'Klint Kubiak'}
w26 = games[(games['season'] == 2026) & (games['week'] == 7)]
for r in w26.itertuples(index=False):
    a, h = fx(r.away_team), fx(r.home_team)
    key = f'{a} @ {h}'
    gl = next((x for x in an['glines'] if x['game'].replace('LA@', 'LAR@').replace('@LA', '@LAR') == f'{a}@{h}'
               or [fx(t) for t in x['game'].split('@')] == [a, h]), None)
    spreads, totals, tt = [], [], collections.defaultdict(list)
    if gl:
        for bk, o in gl['books'].items():
            if bk in ('15', '30'): continue
            for side, team, val, odds in o.get('spread', []):
                if team and fx(team) == h and val is not None: spreads.append(val)
            for side, team, val, odds in o.get('total', []):
                if side == 'over' and val is not None: totals.append(val)
            for side, team, val, odds in o.get('core_bet_type_6_team_score', []):
                if side == 'over' and team and val is not None: tt[fx(team)].append(val)
    hs = statistics.mean(spreads) if spreads else -float(r.spread_line)   # home spread (negative = home favored)
    tot = statistics.mean(totals) if totals else float(r.total_line)
    margin_h = -hs                                                        # expected home margin
    sd = 13.5
    def script(m):  # for a team with expected margin m
        return {'lead8': round(float(1 - stats.norm.cdf(7.5, m, sd)), 3), 'close': round(float(stats.norm.cdf(7.5, m, sd) - stats.norm.cdf(-7.5, m, sd)), 3),
                'trail8': round(float(stats.norm.cdf(-7.5, m, sd)), 3), 'win': round(float(1 - stats.norm.cdf(0, m, sd)), 3)}
    imp_h = statistics.mean(tt[h]) if tt.get(h) else round((tot + margin_h) / 2, 1)
    imp_a = statistics.mean(tt[a]) if tt.get(a) else round((tot - margin_h) / 2, 1)
    wx = weather.get(f'{a}@{h}')
    roof = r.roof if isinstance(r.roof, str) else 'retractable'
    if 'Stade de France' in str(r.stadium): roof = 'outdoors'
    stadium = {'Reliant Stadium': 'NRG Stadium'}.get(r.stadium, r.stadium)
    G[key] = {'away': a, 'home': h, 'stadium': stadium, 'roof': roof, 'surface': r.surface, 'kick': f'{r.gameday} {r.gametime} ET',
              'coach': {a: COACH_FIX.get(a, r.away_coach), h: COACH_FIX.get(h, r.home_coach)}, 'spread_home': round(hs, 1), 'total': round(tot, 1),
              'implied': {a: round(imp_a, 1), h: round(imp_h, 1)}, 'script': {h: script(margin_h), a: script(-margin_h)},
              'weather': wx if roof in ('outdoors', 'open') else None, 'rest': {a: int(r.away_rest), h: int(r.home_rest)}}

# team scoring baseline (2026 points per game) for implied-total adjustments
pts = collections.defaultdict(list)
for r in games[(games['season'] == 2026) & (games['week'] <= 6) & games['home_score'].notna()].itertuples(index=False):
    pts[fx(r.home_team)].append(r.home_score); pts[fx(r.away_team)].append(r.away_score)
PPG = {t: round(statistics.mean(v), 1) for t, v in pts.items()}
LG['ppg'] = round(statistics.mean(PPG.values()), 1)

# ---------------- display blocks for the outlook view (built here so the page only renders) ----------------
TEAMNAME = {'LAR': 'Rams', 'LV': 'Raiders', 'NE': 'Patriots', 'CHI': 'Bears', 'PIT': 'Steelers', 'NO': 'Saints', 'SF': '49ers', 'ATL': 'Falcons',
            'CIN': 'Bengals', 'BAL': 'Ravens', 'TB': 'Buccaneers', 'CAR': 'Panthers', 'NYG': 'Giants', 'HOU': 'Texans', 'IND': 'Colts',
            'MIN': 'Vikings', 'MIA': 'Dolphins', 'NYJ': 'Jets', 'CLE': 'Browns', 'TEN': 'Titans', 'DEN': 'Broncos', 'ARI': 'Cardinals',
            'GB': 'Packers', 'DET': 'Lions', 'KC': 'Chiefs', 'SEA': 'Seahawks', 'DAL': 'Cowboys', 'PHI': 'Eagles', 'BUF': 'Bills',
            'JAX': 'Jaguars', 'LAC': 'Chargers', 'WSH': 'Commanders'}
COACH = {}
for g in G.values():
    COACH.update(g['coach'])
def metric(t, label, key, fmt, more_is='good', lgkey=None):
    d = D[t]; v = d.get(key)
    if v is None: return None
    rk = d.get(key + '_rk'); n = sum(1 for x in D.values() if x.get(key) is not None)
    tone = ''
    if rk:
        top, bot = rk <= 10, rk > n - 10
        if more_is == 'good': tone = 'good' if top else ('bad' if bot else '')
        elif more_is == 'bad': tone = 'bad' if top else ('good' if bot else '')
    lv = LG.get(lgkey or key)
    return {'label': label, 'v': fmt.format(v), 'lg': fmt.format(lv) if lv is not None else '', 'rk': rk, 'n': n, 'tone': tone}
def status_txt(d):
    if d.get('status'): return d['status']
    if d.get('practice') and d['practice'] not in ('Full',): return d['practice']
    return ''
def block(t, kind):
    nm = TEAMNAME.get(t, t); d = D[t]
    if kind.startswith('rec-') or kind.startswith('td-'):
        grp = kind.split('-')[1]
    else:
        grp = None
    M = []
    if kind.startswith('rec-'):
        M = [metric(t, f'Receiving yds allowed to {grp}s / game', f'{grp}_yds_pg', '{:.1f}'),
             metric(t, f'Catches allowed to {grp}s / game', f'{grp}_rec_pg', '{:.1f}'),
             metric(t, f'Yards per target allowed to {grp}s', f'{grp}_ypt', '{:.2f}'),
             metric(t, 'EPA per dropback allowed', 'epa_db', '{:+.2f}'),
             metric(t, 'Explosive pass rate allowed (20+ yds)', 'explosive', '{:.1f}%'),
             metric(t, 'Pressure rate', 'pressure', '{:.1f}%', 'bad'),
             metric(t, 'Blitz rate', 'blitz', '{:.1f}%', 'neutral')]
        poss = {'WR': ('CB',), 'TE': ('S', 'LB'), 'RB': ('LB', 'S')}[grp]
        pl = [x for x in DEF.get(t, []) if x['pos'] in poss][:6]
        players = {'title': f"{nm} {'/'.join(poss)}s in coverage (2026)", 'cols': ['Player', 'Pos', 'Tgt', 'Yds/tgt', 'TD', 'INT', 'Status'],
                   'bar': 3, 'lg': LG['ypt_cov'], 'rows': [[x['name'], x['pos'], x['tgt'], x['ypt'], x['td'], x['int'], status_txt(x)] for x in pl]}
    elif kind == 'pass':
        M = [metric(t, 'EPA per dropback allowed', 'epa_db', '{:+.2f}'), metric(t, 'Success rate allowed on dropbacks', 'success_db', '{:.1f}%'),
             metric(t, 'Explosive pass rate allowed (20+ yds)', 'explosive', '{:.1f}%'),
             metric(t, 'Pressure rate', 'pressure', '{:.1f}%', 'bad'), metric(t, 'Sack rate', 'sack_rate', '{:.1f}%', 'bad'),
             metric(t, 'Blitz rate', 'blitz', '{:.1f}%', 'neutral'), metric(t, 'Receiving yds allowed to WRs / game', 'WR_yds_pg', '{:.1f}')]
        pl = [x for x in DEF.get(t, []) if x['pos'] in ('CB', 'S')][:6]
        players = {'title': f'{nm} defensive backs in coverage (2026)', 'cols': ['Player', 'Pos', 'Tgt', 'Yds/tgt', 'TD', 'INT', 'Status'],
                   'bar': 3, 'lg': LG['ypt_cov'], 'rows': [[x['name'], x['pos'], x['tgt'], x['ypt'], x['td'], x['int'], status_txt(x)] for x in pl]}
        pr = sorted(RUSHERS.get(t, []), key=lambda x: -x['prs'])[:4]
        if pr: players['extra'] = {'title': 'Top pass rushers', 'cols': ['Player', 'Pressures', 'Sacks', 'Status'],
                                   'rows': [[x['name'], x['prs'], x['sk'], status_txt(x)] for x in pr]}
    elif kind == 'rush':
        M = [metric(t, 'RB rushing yds allowed / game', 'RB_rush_pg', '{:.1f}'), metric(t, 'Yards per carry allowed', 'ypc', '{:.2f}'),
             metric(t, 'Average men in the box', 'box', '{:.2f}', 'bad'), metric(t, 'RB touchdowns allowed / game', 'RB_td_pg', '{:.2f}')]
        pl = sorted(TACK.get(t, []), key=lambda x: -x['tk'])[:6]
        players = {'title': f'{nm} leading tacklers (2026)', 'cols': ['Player', 'Pos', 'Tackles', 'Missed', 'Missed %', 'Status'],
                   'bar': 4, 'lg': None, 'rows': [[x['name'], x['pos'], x['tk'], x['mt'], x['mt_pct'], status_txt(x)] for x in pl]}
    else:
        key = f'{grp}_td_pg' if grp in ('WR', 'TE', 'RB') else None
        M = [metric(t, f'TDs allowed to {grp}s / game', key, '{:.2f}') if key else None,
             metric(t, 'EPA per dropback allowed', 'epa_db', '{:+.2f}'), metric(t, 'Yards per carry allowed', 'ypc', '{:.2f}')]
        players = None
    M = [m for m in M if m]
    shells = d.get('shells_2025')
    out = {'title': f'{nm} defense', 'coach': COACH.get(t, ''), 'games': d['games'], 'metrics': M, 'players': players}
    if shells and kind != 'rush' and not kind.startswith('td-'):
        out['shells'] = {'title': f"Coverage shells in 2025 (man {d.get('man_2025', 0):.0f}% · league {LG.get('man_2025', 0):.0f}%)", 'rows': shells}
    return out
MB = {}
for t in D:
    for kind in ('rec-WR', 'rec-TE', 'rec-RB', 'pass', 'rush', 'td-WR', 'td-TE', 'td-RB', 'td-QB'):
        MB[f'{t}|{kind}'] = block(t, kind)

out = {'def': D, 'defenders': {t: v[:8] for t, v in DEF.items()}, 'games': G, 'ppg': PPG, 'lg': LG}
json.dump(out, open(B + 'nfl_ctx.json', 'w'))
import csv
with open(B + 'nflctx_w7.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['kind', 'key', 'detail'])
    for k in sorted(MB):
        w.writerow(['mb', k, json.dumps(MB[k], separators=(',', ':'), ensure_ascii=False)])
    for k in sorted(G):
        w.writerow(['game', k, json.dumps(G[k], separators=(',', ':'), ensure_ascii=False)])
    w.writerow(['lg', 'lg', json.dumps(LG, separators=(',', ':'))])
print('defenses', len(D), 'games', len(G), 'lg', LG)
print(json.dumps(G['LAR @ LV'], indent=0)[:900])
print(json.dumps({k: D['LV'][k] for k in D['LV'] if not k.endswith('_rk')})[:900])
print(DEF['LV'][:4])
