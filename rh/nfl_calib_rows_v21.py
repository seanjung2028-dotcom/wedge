"""Backtests for the Wedger NFL prop model (nfl_model.py).

A. Week 6 2026 real lines: every player prop the site screened in Week 6 (Robinhood / sportsbook prices, 45-55c), settled.
   Model inputs use only data through Week 5 (histories, defenses, coverage, scoring) plus Week 6 closing spread/total and
   game-day weather from nflverse schedules. Situational splits are not rebuilt, so case odds = his usual mix.
B. 2025 walk-forward: weeks 5-18, WR/TE/RB receiving yards, receptions and RB rushing yards, synthetic line = median of his
   last 8 games (+0.5), at least 8 prior games with the team. Same inputs as of the week before.
Scores: Brier (lower is better), log loss, and for A the record / ROI of buying when the probability beats the price.
"""
import csv, json, math, re, collections, statistics, sys
import numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/wedger/rh')
import nfl_model as M

B = '/home/claude/wedger/rh/'
S = '/home/claude/wedger/'
FIX = {'LA': 'LAR', 'WAS': 'WSH', 'OAK': 'LV', 'SD': 'LAC', 'STL': 'LAR', 'JAC': 'JAX'}
fx = lambda t: FIX.get(t, t)
import unicodedata
def norm(n):
    n = unicodedata.normalize('NFKD', str(n)).encode('ascii', 'ignore').decode().lower().replace('.', '').replace("'", '').replace('-', ' ')
    n = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', n)
    return re.sub(r'\s+', ' ', n).strip()

st = pd.concat([pd.read_csv(S + f'nflverse_dl3/stats_player_week_{y}.csv', low_memory=False) for y in (2023, 2024, 2025, 2026)], ignore_index=True)
st = st[st['season_type'] == 'REG'].copy()
st['team'] = st['team'].map(fx); st['opponent_team'] = st['opponent_team'].map(fx)
sn = pd.concat([pd.read_csv(S + f'nflverse_dl3/snap_counts_{y}.csv') for y in (2023, 2024, 2025, 2026)], ignore_index=True)
rws = pd.concat([pd.read_csv(S + f'nflverse_dl3/roster_weekly_{y}.csv', low_memory=False) for y in (2023, 2024, 2025, 2026)], ignore_index=True)
pfr2g = dict(zip(rws['pfr_id'].dropna(), rws.loc[rws['pfr_id'].notna(), 'gsis_id']))
sn['gsis'] = sn['pfr_player_id'].map(pfr2g)
SNAP = {(r.gsis, int(r.season), int(r.week)): float(r.offense_pct) for r in sn[sn['gsis'].notna()].itertuples(index=False)}
games = pd.read_csv(S + 'dl4/games.csv')
games = games[games['game_type'] == 'REG']
MARG, GINFO = {}, {}
for r in games.itertuples(index=False):
    a, h = fx(r.away_team), fx(r.home_team)
    if not pd.isna(r.home_score):
        MARG[(r.season, r.week, h)] = r.home_score - r.away_score; MARG[(r.season, r.week, a)] = r.away_score - r.home_score
    GINFO[(r.season, r.week, a)] = r; GINFO[(r.season, r.week, h)] = r

ROWS = collections.defaultdict(list)    # gsis -> list of (season, week, team, opp, row)
for r in st.itertuples(index=False):
    row = [int(r.season) % 100, int(r.week), r.opponent_team, (lambda p: round(100 * p) if p is not None else None)(SNAP.get((r.player_id, int(r.season), int(r.week)))),
           int(r.receptions or 0), int(r.receiving_yards or 0), int(r.rushing_yards or 0), int(r.passing_yards or 0), int(r.passing_tds or 0),
           int(r.passing_interceptions or 0), int((r.rushing_tds or 0) + (r.receiving_tds or 0)), None, '', int(r.targets or 0), int(r.carries or 0), int(r.attempts or 0)]
    ROWS[r.player_id].append((int(r.season), int(r.week), r.team, r.opponent_team, row, r.position))
NAME = {}
for r in st.itertuples(index=False): NAME.setdefault((norm(r.player_display_name), fx(r.team), int(r.season)), r.player_id)


def defense_ctx(season, week):
    """Opponent defense allowed through week-1 of season (falls back to last season's full numbers before week 4)."""
    s = st[(st['season'] == season) & (st['week'] < week)]
    if week < 4: s = st[(st['season'] == season - 1)]
    s = s.copy(); s['grp'] = s['position'].map(lambda p: p if p in ('WR', 'TE', 'RB') else ('RB' if p == 'FB' else None))
    gp = s.groupby('opponent_team')['week'].nunique()
    D = collections.defaultdict(dict)
    for grp in ('WR', 'TE', 'RB'):
        sg = s[s['grp'] == grp].groupby('opponent_team').agg(rec=('receptions', 'sum'), yds=('receiving_yards', 'sum'), ryds=('rushing_yards', 'sum'),
                                                             td=('receiving_tds', 'sum'), rtd=('rushing_tds', 'sum'))
        for t, r in sg.iterrows():
            n = gp[t]; D[t]['games'] = int(n)
            D[t][f'{grp}_rec_pg'] = r['rec'] / n; D[t][f'{grp}_yds_pg'] = r['yds'] / n
            D[t][f'{grp}_td_pg'] = (r['td'] + (r['rtd'] if grp == 'RB' else 0)) / n
            if grp == 'RB': D[t]['RB_rush_pg'] = r['ryds'] / n
    LG = {k: statistics.mean(D[t][k] for t in D if k in D[t]) for k in ('WR_rec_pg', 'TE_rec_pg', 'RB_rec_pg', 'WR_yds_pg', 'TE_yds_pg', 'RB_yds_pg',
                                                                        'RB_rush_pg', 'WR_td_pg', 'TE_td_pg', 'RB_td_pg')}
    pts = collections.defaultdict(list)
    for (se, wk, t), mg in MARG.items():
        if se == season and wk < week:
            g = GINFO[(se, wk, t)]
            pts[t].append(g.home_score if fx(g.home_team) == t else g.away_score)
    LG['ppg'] = statistics.mean(v for l in pts.values() for v in l) if pts else 23.0
    for k in ('epa_db', 'ypc'): LG[k] = 1.0
    return D, LG, pts


def script_probs(m):
    from scipy import stats as ss
    return {'lead8': float(1 - ss.norm.cdf(7.5, m, 13.5)), 'close': float(ss.norm.cdf(7.5, m, 13.5) - ss.norm.cdf(-7.5, m, 13.5)),
            'trail8': float(ss.norm.cdf(-7.5, m, 13.5))}


def game_ctx(season, week, team, opp, D, LG, pts):
    g = GINFO.get((season, week, team))
    if g is None: return None
    home = fx(g.home_team) == team
    m_home = float(g.spread_line) if not pd.isna(g.spread_line) else 0.0       # nflverse: positive = home favored
    m = m_home if home else -m_home
    tot = float(g.total_line) if not pd.isna(g.total_line) else 44.0
    implied = (tot + m) / 2
    roof = g.roof if isinstance(g.roof, str) else 'retractable'
    wx = None
    if roof in ('outdoors', 'open') and not pd.isna(g.temp):
        wx = {'temp': float(g.temp), 'wind': float(g.wind) if not pd.isna(g.wind) else 0.0, 'gust': 0, 'precip_prob': 0}
    p = pts.get(team, [])
    return {'def': D.get(opp, {}), 'lg': LG, 'implied': implied, 'ppg': statistics.mean(p) if p else LG['ppg'], 'ppg_n': len(p),
            'wx': wx, 'roof': roof}, script_probs(m)


def history(gsis, season, week, team):
    rows = [x for x in ROWS.get(gsis, []) if (x[0], x[1]) < (season, week) and x[2] == team and x[0] >= season - 3]
    rows.sort(key=lambda x: (x[0], x[1]))
    L = [x[4] for x in rows]
    pos = collections.Counter(x[5] for x in rows).most_common(1)[0][0] if rows else ''
    margin = {i: MARG.get((rows[i][0], rows[i][1], team)) for i in range(len(rows))}
    return L, pos, margin


def brier(ps, ys): return float(np.mean([(p - y) ** 2 for p, y in zip(ps, ys)]))
def logloss(ps, ys): return float(np.mean([-(y * math.log(min(max(p, 1e-3), 1 - 1e-3)) + (1 - y) * math.log(min(max(1 - p, 1e-3), 1 - 1e-3))) for p, y in zip(ps, ys)]))

STAT = {'Receptions': 'rec', 'Receiving Yards': 'recyd', 'Rushing Yards': 'rushyd', 'Rushing + Receiving Yards': 'rryd',
        'Passing Yards': 'passyd', 'Passing Touchdowns': 'passtd', 'Interceptions': 'int', 'Anytime Touchdown': 'td'}

# ---------------- real Robinhood/book lines, Weeks 6-7 2026, settled ----------------
res = [dict(r, wk=6) for r in csv.DictReader(open(B + 'results_w6.csv'))]
res += [dict(r, wk=7) for r in csv.DictReader(open(B + 'results_w6_w7.csv')) if str(r.get('week')) == '7' and r['group'] == 'Week 7 settled']
CTX = {wk: defense_ctx(2026, wk) for wk in (6, 7)}
A = []
for r in res:
    mk = 'Anytime Touchdown' if r['group'] == 'ATD filter picks' else r['market']
    if mk not in STAT or r['outcome'] not in ('Won', 'Lost'): continue
    price = float(r['yes_price']) / 100
    if not (0.40 <= price <= 0.60): continue
    stat = STAT[mk]; wk = r['wk']
    if stat == 'td': player, line = r['contract'], 0.5
    else:
        m = re.match(r'^(.*?): Over ([\d.]+) ', r['contract'])
        if not m: continue
        player, line = m.group(1), float(m.group(2))
    a, h = r['game'].split(' @ ')
    gsis = team = opp = None
    for t, o in ((a, h), (h, a)):
        g = NAME.get((norm(player), t, 2026))
        if g: gsis, team, opp = g, t, o; break
    row = {'wk': wk, 'stat': stat, 'market': mk, 'price': price, 'y': 1 if r['outcome'] == 'Won' else 0, 'contract': r['contract'], 'game': r['game'],
           'hr26': float(r['hit_rate']) / 100 if r['hit_rate'] not in ('', None) else None, 'qual': r.get('qualifies', ''), 'flag': r.get('flagged', ''),
           'line': line, 'player': player, 'team': team}
    if gsis:
        L, pos, margin = history(gsis, 2026, wk, team)
        gc = game_ctx(2026, wk, team, opp, *CTX[wk]) if len(L) >= 4 else None
        if gc:
            ctx, sp = gc
            E = M.evaluate(L, list(range(len(L))), stat, line, pos, [], ctx, lambda i: margin.get(i), sp, team, 26, p_books=price)
            if E:
                row.update({'cases': E['P_cases'], 'model': E['P_model'], 'ours': E['P_raw'], 'ours_cal': E['P_ours'], 'wedger': E['P_v1'], 'wedger_v2': E['P'], 'pos': pos,
                            'n_games': len(L), 'proj': E['m'], 'avg': float(np.mean([M.val(L, i, stat) for i in range(len(L))])),
                            'med': float(np.median([M.val(L, i, stat) for i in range(len(L))])),
                            'last4': float(np.mean([M.val(L, i, stat) for i in range(max(0, len(L) - 4), len(L))]))})
    A.append(row)
pd.DataFrame(A).to_csv(B + 'calib_rows.csv', index=False)
print('rows', len(A), 'with model', sum(1 for x in A if 'wedger' in x))
