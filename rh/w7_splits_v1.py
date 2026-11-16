"""Situational splits for every Week 7 player prop.

For each prop, three sets of 2026 games (Weeks 1-6) that look like this week:
  qb  - WR/TE only: games with the same QB situation (team's primary starter playing, or not)
  tc  - WR/TE only: games where the player's top target competitors had the same availability as this week
  def - all players: games against defenses ranked within +/-8 of this week's opponent vs the position group
Situational hit % = total hits / total games across the sets that apply (a game can count in more than one set);
projection = average stat across the same games.
"""
import csv, json, re, unicodedata, collections
import pandas as pd

B = '/home/claude/wedger/rh/'
N = '/home/claude/wedger/nflverse_dl3/'
FIX = {'LA': 'LAR', 'WAS': 'WSH'}
WINDOW = 8

def norm(n):
    n = unicodedata.normalize('NFKD', str(n)).encode('ascii', 'ignore').decode().lower().replace('.', '').replace("'", '').replace('-', ' ')
    n = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', n)
    return re.sub(r'\s+', ' ', n).strip()

st = pd.read_csv(N + 'stats_player_week_2026.csv', low_memory=False)
st = st[(st['season_type'] == 'REG') & (st['week'] <= 6)].copy()
st['team'] = st['team'].map(lambda t: FIX.get(t, t)); st['opponent_team'] = st['opponent_team'].map(lambda t: FIX.get(t, t))
rw = pd.read_csv(N + 'roster_weekly_2026.csv', low_memory=False)
rw['team'] = rw['team'].map(lambda t: FIX.get(t, t))
sn = pd.read_csv(N + 'snap_counts_2026.csv')
sn['team'] = sn['team'].map(lambda t: FIX.get(t, t)); sn['opponent'] = sn['opponent'].map(lambda t: FIX.get(t, t))
inj = pd.read_csv(N + 'injuries_2026.csv')
dc = pd.read_csv(N + 'depth_charts_2026.csv', low_memory=False)
dc = dc[dc['dt'] == dc['dt'].max()].copy(); dc['team'] = dc['team'].map(lambda t: FIX.get(t, t))
DEF = {r['team']: r for r in csv.DictReader(open(B + 'defense_w7.csv'))}

# ---------- who is who ----------
pfr2gsis = dict(zip(rw['pfr_id'].dropna(), rw.loc[rw['pfr_id'].notna(), 'gsis_id']))
name_team = {}
for _, r in rw.sort_values('week').iterrows():
    name_team[(norm(r['full_name']), r['team'])] = r['gsis_id']
    if isinstance(r.get('football_name'), str):
        name_team.setdefault((norm(r['football_name'] + ' ' + r['last_name']), r['team']), r['gsis_id'])
pos_of = dict(zip(rw['gsis_id'], rw['position']))
disp = dict(zip(rw['gsis_id'], rw['full_name']))

# ---------- per-player games (stats rows + offensive snaps so 0-stat games count) ----------
STATS = ['receptions', 'receiving_yards', 'rushing_yards', 'passing_yards', 'passing_tds', 'passing_interceptions', 'rushing_tds', 'receiving_tds', 'targets', 'attempts']
games = collections.defaultdict(dict)  # gsis -> week -> {team, opp, stats}
for _, r in st.iterrows():
    games[r['player_id']][int(r['week'])] = {'team': r['team'], 'opp': r['opponent_team'], **{k: float(r[k] or 0) for k in STATS}}
sn['gsis'] = sn['pfr_player_id'].map(pfr2gsis)
for _, r in sn[(sn['offense_snaps'] > 0) & sn['gsis'].notna()].iterrows():
    games[r['gsis']].setdefault(int(r['week']), {'team': r['team'], 'opp': r['opponent'], **{k: 0.0 for k in STATS}})

# team-game: who quarterbacked (most pass attempts)
team_week_qb = {}
for (tm, wk), grp in st[st['attempts'] > 0].groupby(['team', 'week']):
    team_week_qb[(tm, int(wk))] = grp.sort_values('attempts', ascending=False).iloc[0]['player_id']
primary = {}
for tm in {t for t, _ in team_week_qb}:
    seq = [(w, q) for (t, w), q in team_week_qb.items() if t == tm]
    cnt = collections.Counter(q for _, q in seq)
    last = {q: w for w, q in seq}
    primary[tm] = max(cnt, key=lambda q: (cnt[q], last[q]))

# availability by week (weeks 1-6 from game-day rosters; week 7 from current roster status + Week 7 report)
status = {(r['gsis_id'], int(r['week'])): r['status'] for _, r in rw.iterrows()}
inj7 = {r['gsis_id']: r['report_status'] for _, r in inj[inj['week'] == 7].iterrows() if isinstance(r['report_status'], str)}
def played(g, wk):
    return wk in games.get(g, {})
def out_this_week(g):
    return status.get((g, 7), 'ACT') != 'ACT' or inj7.get(g) in ('Out', 'Doubtful')

def depth_qb1(tm):
    qbs = dc[(dc['team'] == tm) & (dc['pos_abb'] == 'QB')].sort_values('pos_rank')
    return qbs.iloc[0]['gsis_id'] if len(qbs) else primary.get(tm)

def expected_qb(tm):
    qbs = dc[(dc['team'] == tm) & (dc['pos_abb'] == 'QB')].sort_values('pos_rank')
    for _, q in qbs.iterrows():
        if isinstance(q['gsis_id'], str) and not out_this_week(q['gsis_id']):
            return q['gsis_id']
    return primary.get(tm)

def short(g):
    n = disp.get(g, g); parts = n.split(' ')
    return n if len(parts) < 2 else n

# ---------- prop stat ----------
def stat_of(market, s):
    return {'Receptions': s['receptions'], 'Receiving Yards': s['receiving_yards'], 'Rushing Yards': s['rushing_yards'],
            'Rushing + Receiving Yards': s['rushing_yards'] + s['receiving_yards'], 'Passing Yards': s['passing_yards'],
            'Passing Touchdowns': s['passing_tds'], 'Interceptions': s['passing_interceptions'],
            'Anytime Touchdown': s['rushing_tds'] + s['receiving_tds']}.get(market)

UNIT = {'Receptions': 'rec', 'Receiving Yards': 'rec yds', 'Rushing Yards': 'rush yds', 'Rushing + Receiving Yards': 'rush+rec yds',
        'Passing Yards': 'pass yds', 'Passing Touchdowns': 'pass TDs', 'Interceptions': 'INTs', 'Anytime Touchdown': 'TDs'}

def splits(player, team, opp, market, line):
    g = name_team.get((norm(player), team))
    if not g:
        return None
    pos = pos_of.get(g, '')
    hist = {wk: v for wk, v in games.get(g, {}).items() if v['team'] == team}
    if not hist:
        return None
    hit = (lambda v: v >= 1) if market == 'Anytime Touchdown' else (lambda v: v > line)
    out = []
    def add(k, label, now, wks):
        vals = [stat_of(market, hist[w]) for w in wks]
        out.append({'k': k, 'label': label, 'now': now, 'hits': sum(1 for v in vals if hit(v)), 'n': len(vals),
                    'avg': round(sum(vals) / len(vals), 1) if vals else None, 'weeks': sorted(wks)})
    pc = pos in ('WR', 'TE')
    if pc:
        exp = expected_qb(team); prim = primary.get(team)
        if exp != prim and prim and out_this_week(prim):
            wks = [w for w in hist if team_week_qb.get((team, w)) != prim]
            label = f'Without {disp.get(prim, "the starter")} at QB'
        else:
            wks = [w for w in hist if team_week_qb.get((team, w)) == exp]
            label = f'With {disp.get(exp, "this QB")} at QB'
        add('qb', label, f'This week: {disp.get(exp, "unknown")} expected to start', wks)
        # target competition: top-3 teammates by 2026 targets (WR/TE/RB)
        mates = st[(st['team'] == team) & (st['player_id'] != g) & (st['position'].isin(['WR', 'TE', 'RB']))]
        top = mates.groupby('player_id')['targets'].sum().sort_values(ascending=False)
        top = [p for p, t in top.items() if t >= 10][:3]
        if top:
            now = {p: not out_this_week(p) for p in top}
            wks = [w for w in hist if all(played(p, w) == now[p] for p in top)]
            act = [disp.get(p, p) for p in top if now[p]]; gone = [disp.get(p, p) for p in top if not now[p]]
            lab = 'Same target competition: ' + (', '.join(act) + ' active' if act else '') + ('; ' if act and gone else '') + (', '.join(gone) + ' out' if gone else '')
            add('tc', lab, 'Games where those teammates had the same availability as this week', wks)
    grp, key = ('RB', 'rb_rank') if pos in ('RB', 'FB') else ('WR/TE', 'pc_rank')
    if opp in DEF:
        r0 = int(DEF[opp][key]); lo, hi = max(1, r0 - WINDOW), min(32, r0 + WINDOW)
        wks = [w for w, v in hist.items() if v['opp'] in DEF and lo <= int(DEF[v['opp']][key]) <= hi]
        add('def', f'Vs defenses ranked {lo}–{hi} vs {grp}', f'This week: {opp} ranks #{r0} (1 = most PPR allowed)', wks)
    used = [s for s in out if s['n']]
    if not used:
        return {'sit_hit': '', 'sit_n': 0, 'sit_proj': '', 'splits': out}
    H = sum(s['hits'] for s in used); Nn = sum(s['n'] for s in used)
    proj = round(sum(s['avg'] * s['n'] for s in used) / Nn, 1)
    return {'sit_hit': round(100 * H / Nn, 1), 'sit_n': Nn, 'sit_hits': H, 'sit_proj': proj if market != 'Anytime Touchdown' else '',
            'unit': UNIT.get(market, ''), 'splits': out}

PROP = {'Receptions', 'Receiving Yards', 'Rushing Yards', 'Rushing + Receiving Yards', 'Passing Yards', 'Passing Touchdowns',
        'Interceptions', 'Anytime Touchdown'}
ROLE_TEAM = {}
for r in csv.DictReader(open(B + 'props_cat_w7.csv')):
    ROLE_TEAM[(r['game'], r['contract'])] = r['team']

def team_for(player, game):
    a, h = game.split(' @ ')
    for t in (a, h):
        if (norm(player), t) in name_team:
            return t, (h if t == a else a)
    return None, None

def enrich(path, kind):
    rows = list(csv.DictReader(open(path)))
    cols = list(rows[0].keys())
    for c in ('sit_hit', 'sit_n', 'sit_proj', 'sit_edge', 'sit_detail'):
        if c not in cols: cols.append(c)
    done = 0
    for r in rows:
        r.update({'sit_hit': '', 'sit_n': '', 'sit_proj': '', 'sit_edge': '', 'sit_detail': ''})
        if kind == 'atd':
            market, player, line = 'Anytime Touchdown', r['player'], 0.5
        else:
            market = r['market']
            if market not in PROP: continue
            m = re.match(r'^(.*?): Over ([\d.]+) ', r['contract'])
            player, line = (m.group(1), float(m.group(2))) if m else (r['contract'], 0.5)
        team, opp = team_for(player, r['game'])
        if not team: continue
        s = splits(player, team, opp, market, line)
        if not s: continue
        price = float(r['yes_price']) if r.get('yes_price') not in ('', None) else None
        r['sit_hit'] = s['sit_hit']; r['sit_n'] = s['sit_n']; r['sit_proj'] = s['sit_proj']
        r['sit_edge'] = round(s['sit_hit'] - price, 1) if (s['sit_hit'] != '' and price is not None) else ''
        r['sit_detail'] = json.dumps({'line': line if market != 'Anytime Touchdown' else None, 'unit': s.get('unit', ''),
                                      'hits': s.get('sit_hits'), 'splits': s['splits']}, separators=(',', ':'))
        done += 1
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    return done, len(rows)

print('primary QBs', {t: disp.get(q) for t, q in sorted(primary.items())})
print('QB1 vs expected vs most starts', {t: (disp.get(depth_qb1(t)), disp.get(expected_qb(t)), disp.get(primary.get(t)), [disp.get(team_week_qb.get((t, w))) for w in range(1, 7)]) for t in primary if expected_qb(t) != depth_qb1(t) or depth_qb1(t) != primary.get(t)})
print('lines', enrich(B + 'inband_w7.csv', 'lines'))
print('props', enrich(B + 'props_cat_w7.csv', 'lines'))
print('atd', enrich(B + 'atd_w7.csv', 'atd'))
