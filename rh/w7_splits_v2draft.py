"""Situational splits for every Week 7 player prop, using 2024, 2025 and 2026 (Weeks 1-6) regular-season games
with the player's current team.

Sets of games that look like this week:
  qb  - WR/TE: games with this week's QB situation (expected starter playing, or the injured starter missing),
        shown next to the opposite situation so the projection difference is visible
  tc  - WR/TE: games where the player's top-3 target competitors (2026 targets) had this week's availability,
        plus a with/without line for each of those teammates
  def - all: games vs defenses ranked within +/-8 of this week's opponent vs the position group (that season's ranks)
Games where the player left early (likely in-game injury) are left out of everything; games where the QB left early
are left out of the QB split:
  player: offensive snap share under 60% of his usual that season AND on the next week's injury report or out the next week
  QB:     the team's leading passer played under 80% of offensive snaps
Situational hit % = hits / games pooled across the sets that apply; projection = average stat over the same games.
"""
import csv, json, re, unicodedata, collections, statistics, sys
import pandas as pd

B = '/home/claude/wedger/rh/'
N = '/home/claude/wedger/nflverse_dl3/'
FIX = {'LA': 'LAR', 'WAS': 'WSH', 'OAK': 'LV', 'SD': 'LAC', 'STL': 'LAR'}
fx = lambda t: FIX.get(t, t)
SEASONS = [2024, 2025, 2026]
WINDOW = 8
FORCE_OUT = set(json.load(open(B + 'force_out.json'))) if __import__('os').path.exists(B + 'force_out.json') else set()

def norm(n):
    n = unicodedata.normalize('NFKD', str(n)).encode('ascii', 'ignore').decode().lower().replace('.', '').replace("'", '').replace('-', ' ')
    n = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', n)
    return re.sub(r'\s+', ' ', n).strip()

# ---------------- load ----------------
st = pd.concat([pd.read_csv(N + f'stats_player_week_{y}.csv', low_memory=False) for y in SEASONS], ignore_index=True)
st = st[(st['season_type'] == 'REG') & ~((st['season'] == 2026) & (st['week'] > 6))].copy()
st['team'] = st['team'].map(fx); st['opponent_team'] = st['opponent_team'].map(fx)
rws = pd.concat([pd.read_csv(N + f'roster_weekly_{y}.csv', low_memory=False) for y in SEASONS], ignore_index=True)
rws['team'] = rws['team'].map(fx)
sn = pd.concat([pd.read_csv(N + f'snap_counts_{y}.csv') for y in SEASONS], ignore_index=True)
sn = sn[sn['game_type'] == 'REG'].copy(); sn['team'] = sn['team'].map(fx); sn['opponent'] = sn['opponent'].map(fx)
inj = pd.concat([pd.read_csv(N + f'injuries_{y}.csv') for y in SEASONS], ignore_index=True)
inj['team'] = inj['team'].map(fx)
dc = pd.read_csv(N + 'depth_charts_2026.csv', low_memory=False)
dc = dc[dc['dt'] == dc['dt'].max()].copy(); dc['team'] = dc['team'].map(fx)
DEF26 = {r['team']: r for r in csv.DictReader(open(B + 'defense_w7.csv'))}

pfr2gsis = dict(zip(rws['pfr_id'].dropna(), rws.loc[rws['pfr_id'].notna(), 'gsis_id']))
rw26 = rws[rws['season'] == 2026]
name_team = {}
for r in rw26.sort_values('week').itertuples(index=False):
    name_team[(norm(r.full_name), r.team)] = r.gsis_id
    if isinstance(r.football_name, str):
        name_team.setdefault((norm(f'{r.football_name} {r.last_name}'), r.team), r.gsis_id)
pos_of = dict(zip(rw26['gsis_id'], rw26['position']))
# players reported hurt after the data snapshot (names): treat as out this week
FORCE_OUT = {g for n in FORCE_OUT for (nm, _), g in name_team.items() if nm == norm(n)}
disp = dict(zip(rws['gsis_id'], rws['full_name'])); disp.update(dict(zip(rw26['gsis_id'], rw26['full_name'])))

# ---------------- per-player games ----------------
STATS = ['receptions', 'receiving_yards', 'rushing_yards', 'passing_yards', 'passing_tds', 'passing_interceptions',
         'rushing_tds', 'receiving_tds', 'targets', 'attempts']
games = collections.defaultdict(dict)  # gsis -> (season, week) -> row
for r in st.itertuples(index=False):
    games[r.player_id][(int(r.season), int(r.week))] = {'team': r.team, 'opp': r.opponent_team, 'pct': None,
                                                       **{k: float(getattr(r, k) or 0) for k in STATS}}
sn['gsis'] = sn['pfr_player_id'].map(pfr2gsis)
for r in sn[sn['gsis'].notna()].itertuples(index=False):
    if r.offense_snaps > 0:
        row = games[r.gsis].setdefault((int(r.season), int(r.week)), {'team': r.team, 'opp': r.opponent, 'pct': None, **{k: 0.0 for k in STATS}})
        row['pct'] = float(r.offense_pct)

on_report = set((r.gsis_id, int(r.season), int(r.week)) for r in inj.itertuples(index=False) if isinstance(r.gsis_id, str))
team_weeks = collections.defaultdict(set)
for r in st.itertuples(index=False):
    team_weeks[(int(r.season), r.team)].add(int(r.week))

def player_partial(g, gk):
    row = games[g].get(gk)
    if not row or row.get('pct') is None: return False
    pcts = [v['pct'] for (yy, _), v in games[g].items() if yy == gk[0] and v.get('pct') is not None]
    if len(pcts) < 3 or row['pct'] >= 0.6 * statistics.median(pcts): return False
    nxt = sorted(w for w in team_weeks[(gk[0], row['team'])] if w > gk[1])
    return (g, gk[0], gk[1] + 1) in on_report or (bool(nxt) and (gk[0], nxt[0]) not in games[g])

team_qb = {}
for (s, tm, wk), grp in st[st['attempts'] > 0].groupby(['season', 'team', 'week']):
    q = grp.sort_values('attempts', ascending=False).iloc[0]['player_id']
    team_qb[(tm, (int(s), int(wk)))] = (q, games[q].get((int(s), int(wk)), {}).get('pct'))
qb_of = lambda tm, gk: team_qb.get((tm, gk), (None, None))[0]
qb_partial = lambda tm, gk: (team_qb.get((tm, gk), (None, None))[1] or 1.0) < 0.8

c26 = collections.defaultdict(collections.Counter); last26 = collections.defaultdict(dict)
for (tm, gk), (q, _) in team_qb.items():
    if gk[0] == 2026: c26[tm][q] += 1; last26[tm][q] = gk[1]
primary = {tm: max(c, key=lambda q: (c[q], last26[tm][q])) for tm, c in c26.items()}
status7 = {r.gsis_id: r.status for r in rw26[rw26['week'] == 7].itertuples(index=False)}
inj7 = {r.gsis_id: r.report_status for r in inj[(inj['season'] == 2026) & (inj['week'] == 7)].itertuples(index=False) if isinstance(r.report_status, str)}
out_this_week = lambda g: g in FORCE_OUT or status7.get(g, 'ACT') != 'ACT' or inj7.get(g) in ('Out', 'Doubtful')

def expected_qb(tm):
    for q in dc[(dc['team'] == tm) & (dc['pos_abb'] == 'QB')].sort_values('pos_rank')['gsis_id']:
        if isinstance(q, str) and not out_this_week(q): return q
    return primary.get(tm)

# ---------------- defense ranks vs position group, per season ----------------
st['ppr'] = st['receptions'] + 0.1 * (st['rushing_yards'] + st['receiving_yards']) + 6 * (st['rushing_tds'] + st['receiving_tds'])
st['grp'] = st['position'].map(lambda p: 'RB' if p in ('RB', 'FB') else ('PC' if p in ('WR', 'TE') else None))
RANK = {}
for y in (2024, 2025):
    sy = st[(st['season'] == y) & st['grp'].notna()]
    gp = sy.groupby('opponent_team')['week'].nunique()
    for grp, key in (('RB', 'rb_rank'), ('PC', 'pc_rank')):
        per = (sy[sy['grp'] == grp].groupby('opponent_team')['ppr'].sum() / gp).sort_values(ascending=False)
        for i, tm in enumerate(per.index):
            RANK.setdefault((y, tm), {})[key] = i + 1
for tm, r in DEF26.items():
    RANK[(2026, tm)] = {'rb_rank': int(r['rb_rank']), 'pc_rank': int(r['pc_rank'])}

# ---------------- splits ----------------
def stat_of(market, s):
    return {'Receptions': s['receptions'], 'Receiving Yards': s['receiving_yards'], 'Rushing Yards': s['rushing_yards'],
            'Rushing + Receiving Yards': s['rushing_yards'] + s['receiving_yards'], 'Passing Yards': s['passing_yards'],
            'Passing Touchdowns': s['passing_tds'], 'Interceptions': s['passing_interceptions'],
            'Anytime Touchdown': s['rushing_tds'] + s['receiving_tds']}.get(market)
UNIT = {'Receptions': 'rec', 'Receiving Yards': 'rec yds', 'Rushing Yards': 'rush yds', 'Rushing + Receiving Yards': 'rush+rec yds',
        'Passing Yards': 'pass yds', 'Passing Touchdowns': 'pass TDs', 'Interceptions': 'INTs', 'Anytime Touchdown': 'TDs'}
gl = lambda gk: f"'{str(gk[0])[2:]} W{gk[1]}"

def seasons_label(gks):
    ys = sorted({g[0] for g in gks})
    return '' if not ys else (str(ys[0]) if len(ys) == 1 else f'{ys[0]}–{str(ys[-1])[2:]}')

def splits(g, team, opp, market, line):
    pos = pos_of.get(g, '')
    hist = {gk: v for gk, v in games.get(g, {}).items() if v['team'] == team}
    left_early = sorted(gk for gk in hist if player_partial(g, gk))
    base = {gk: v for gk, v in hist.items() if gk not in left_early}
    if not base: return None
    hit = (lambda v: v >= 1) if market == 'Anytime Touchdown' else (lambda v: v > line)
    def summ(gks):
        vals = [stat_of(market, base[k]) for k in gks]
        return {'hits': sum(1 for v in vals if hit(v)), 'n': len(vals), 'avg': round(sum(vals) / len(vals), 1) if vals else None,
                'games': [gl(k) for k in sorted(gks)]}
    def diff(a, b):
        return round(a['avg'] - b['avg'], 1) if (a['avg'] is not None and b['avg'] is not None) else None
    out = []
    if pos in ('WR', 'TE'):
        exp = expected_qb(team); prim = primary.get(team)
        key_qb = prim if (prim and exp != prim and out_this_week(prim)) else exp
        clean = [k for k in base if qb_of(team, k) and not qb_partial(team, k)]
        with_g = [k for k in clean if qb_of(team, k) == key_qb]; wo_g = [k for k in clean if qb_of(team, k) != key_qb]
        nm = disp.get(key_qb, 'the starter'); match_with = key_qb == exp
        sm, sa = (summ(with_g), summ(wo_g)) if match_with else (summ(wo_g), summ(with_g))
        out.append({'k': 'qb', 'label': f'With {nm} at QB' if match_with else f'Without {nm} at QB',
                    'now': f'This week: {disp.get(exp, "unknown")} expected to start', **sm,
                    'alt': {'label': f'Without {nm}' if match_with else f'With {nm}', **sa}, 'diff': diff(sm, sa),
                    'skipped': len(base) - len(clean)})
        mates = st[(st['season'] == 2026) & (st['team'] == team) & (st['player_id'] != g) & st['position'].isin(['WR', 'TE', 'RB'])]
        top = [p for p, t in mates.groupby('player_id')['targets'].sum().sort_values(ascending=False).items() if t >= 10][:3]
        if top:
            played = lambda p, k: k in games.get(p, {}) and games[p][k]['team'] == team
            now = {p: not out_this_week(p) for p in top}
            act = [disp.get(p, p) for p in top if now[p]]; gone = [disp.get(p, p) for p in top if not now[p]]
            per = []
            for p in top:
                w = summ([k for k in base if played(p, k)]); wo = summ([k for k in base if not played(p, k)])
                per.append({'name': disp.get(p, p), 'now': 'active' if now[p] else 'out', 'with': w, 'without': wo, 'diff': diff(w, wo)})
            gks = [k for k in base if all(played(p, k) == now[p] for p in top)]
            lab = 'Same target competition: ' + '; '.join(filter(None, [', '.join(act) + ' active' if act else '', ', '.join(gone) + ' out' if gone else '']))
            out.append({'k': 'tc', 'label': lab, 'now': 'Games where those teammates were in the same lineup situation as this week',
                        **summ(gks), 'mates': per})
    grp, key = ('RB', 'rb_rank') if pos in ('RB', 'FB') else ('WR/TE', 'pc_rank')
    if (2026, opp) in RANK:
        r0 = RANK[(2026, opp)][key]; lo, hi = max(1, r0 - WINDOW), min(32, r0 + WINDOW)
        gks = [k for k, v in base.items() if (k[0], v['opp']) in RANK and lo <= RANK[(k[0], v['opp'])].get(key, 99) <= hi]
        out.append({'k': 'def', 'label': f'Vs defenses ranked {lo}–{hi} vs {grp} (that season)',
                    'now': f'This week: {opp} ranks #{r0} (1 = most PPR allowed)', **summ(gks)})
    used = [s for s in out if s['n']]
    res = {'splits': out, 'unit': UNIT.get(market, ''), 'seasons': seasons_label(list(base)), 'left_early': [gl(k) for k in left_early],
           'all': summ(list(base)), 'sit_hit': '', 'sit_n': 0, 'sit_proj': '', 'hits': 0}
    if used:
        H = sum(s['hits'] for s in used); Nn = sum(s['n'] for s in used)
        res.update({'sit_hit': round(100 * H / Nn, 1), 'sit_n': Nn, 'hits': H,
                    'sit_proj': round(sum(s['avg'] * s['n'] for s in used) / Nn, 1) if market != 'Anytime Touchdown' else ''})
    return res

PROP = {'Receptions', 'Receiving Yards', 'Rushing Yards', 'Rushing + Receiving Yards', 'Passing Yards', 'Passing Touchdowns',
        'Interceptions', 'Anytime Touchdown'}

def who(player, game):
    a, h = game.split(' @ ')
    for t in (a, h):
        g = name_team.get((norm(player), t))
        if g: return g, t, (h if t == a else a)
    return None, None, None

def enrich(path, kind):
    rows = list(csv.DictReader(open(path)))
    cols = [c for c in rows[0].keys() if not c.startswith('sit_')] + ['sit_hit', 'sit_n', 'sit_proj', 'sit_edge', 'sit_detail']
    done = 0
    for r in rows:
        for c in ('sit_hit', 'sit_n', 'sit_proj', 'sit_edge', 'sit_detail'): r[c] = ''
        if kind == 'atd':
            market, player, line = 'Anytime Touchdown', r['player'], 0.5
        else:
            market = r['market']
            if market not in PROP: continue
            m = re.match(r'^(.*?): Over ([\d.]+) ', r['contract'])
            player, line = (m.group(1), float(m.group(2))) if m else (r['contract'], 0.5)
        g, team, opp = who(player, r['game'])
        if not g: continue
        s = splits(g, team, opp, market, line)
        if not s: continue
        price = float(r['yes_price']) if r.get('yes_price') not in ('', None) else None
        r['sit_hit'], r['sit_n'], r['sit_proj'] = s['sit_hit'], s['sit_n'], s['sit_proj']
        r['sit_edge'] = round(s['sit_hit'] - price, 1) if (s['sit_hit'] != '' and price is not None) else ''
        r['sit_detail'] = json.dumps({'line': line if market != 'Anytime Touchdown' else None, 'unit': s['unit'], 'hits': s['hits'],
                                      'seasons': s['seasons'], 'left_early': s['left_early'], 'all': s['all'], 'splits': s['splits']},
                                     separators=(',', ':'))
        done += 1
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    return done, len(rows)

if __name__ == '__main__' and 'probe' not in sys.argv:
    print('lines', enrich(B + 'inband_w7.csv', 'lines'))
    print('props', enrich(B + 'props_cat_w7.csv', 'lines'))
    print('atd', enrich(B + 'atd_w7.csv', 'atd'))
