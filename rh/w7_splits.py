"""Situational splits for every Week 7 player prop, from 2023-2026 (2026: Weeks 1-6) regular-season games
with the player's current team.

Game sets that resemble this week (each kept as indices into the player's game log so the page can chart them):
  qb    WR/TE: games with this week's QB situation (expected starter, or without the injured starter), plus the opposite
  tc    same lineup: games where the player's top 2026 teammates for targets (RBs: touches) had this week's availability
  comp  comparable No. 1 competitor: each season's top other target-getter on the team (RBs: top other back by touches;
        QBs: top target-getter). Games with him vs without him, so a missing star (Adams now, Kupp in 2023-24) has history.
  def   vs defenses ranked within +/-8 of this week's opponent vs the position group, using that season's ranks
  mates per-teammate with / missed / not on the team
Exclusions: games the player left early (snap share under 60% of his season median AND on the next week's injury
report or out the next game) are dropped from every set; games where the leading passer played under 80% of snaps
are dropped from the QB split; games a teammate left early are dropped from that teammate's and the lineup split.
Situational hit % = hits / games pooled over qb, tc, def and (when the No. 1 competitor is out this week) comp.
Outputs: sit_* columns on the line tables and sit_w7.csv (one row per player: game log + sets as JSON).
"""
import csv, json, re, os, math, unicodedata, collections, statistics, sys
import pandas as pd

B = '/home/claude/wedger/rh/'
N = '/home/claude/wedger/nflverse_dl3/'
FIX = {'LA': 'LAR', 'WAS': 'WSH', 'OAK': 'LV', 'SD': 'LAC', 'STL': 'LAR'}
fx = lambda t: FIX.get(t, t)
SEASONS = [2023, 2024, 2025, 2026]
WINDOW = 8
FORCE_OUT_NAMES = json.load(open(B + 'force_out.json')) if os.path.exists(B + 'force_out.json') else []

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
sn = sn[(sn['game_type'] == 'REG') & ~((sn['season'] == 2026) & (sn['week'] > 6))].copy()
sn['team'] = sn['team'].map(fx); sn['opponent'] = sn['opponent'].map(fx)
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
disp = dict(zip(rws['gsis_id'], rws['full_name'])); disp.update(dict(zip(rw26['gsis_id'], rw26['full_name'])))
FORCE_OUT = {g for n in FORCE_OUT_NAMES for (nm, _), g in name_team.items() if nm == norm(n)}

def short(g):
    n = disp.get(g, '?').split(' ')
    return (n[0][0] + '. ' + ' '.join(n[1:])) if len(n) > 1 else n[0]

# ---------------- per-player games ----------------
STATS = ['receptions', 'receiving_yards', 'rushing_yards', 'passing_yards', 'passing_tds', 'passing_interceptions',
         'rushing_tds', 'receiving_tds', 'targets', 'attempts', 'carries']
games = collections.defaultdict(dict)  # gsis -> (season, week) -> row
for r in st.itertuples(index=False):
    games[r.player_id][(int(r.season), int(r.week))] = {'team': r.team, 'opp': r.opponent_team, 'pct': None, 'pos': r.position,
                                                       **{k: float(getattr(r, k) or 0) for k in STATS}}
sn['gsis'] = sn['pfr_player_id'].map(pfr2gsis)
for r in sn[sn['gsis'].notna()].itertuples(index=False):
    if r.offense_snaps > 0:
        row = games[r.gsis].setdefault((int(r.season), int(r.week)), {'team': r.team, 'opp': r.opponent, 'pct': None, 'pos': r.position,
                                                                      **{k: 0.0 for k in STATS}})
        row['pct'] = float(r.offense_pct)

on_report = set((r.gsis_id, int(r.season), int(r.week)) for r in inj.itertuples(index=False) if isinstance(r.gsis_id, str))
team_weeks = collections.defaultdict(set)
for r in st.itertuples(index=False):
    team_weeks[(int(r.season), r.team)].add(int(r.week))

def played(p, team, gk):
    v = games.get(p, {}).get(gk)
    return bool(v) and v['team'] == team

_pp = {}
def hurt_after(g, gk, team):
    nxt = sorted(w for w in team_weeks[(gk[0], team)] if w > gk[1])
    return (g, gk[0], gk[1] + 1) in on_report or (bool(nxt) and (gk[0], nxt[0]) not in games[g])

def partial(g, gk):
    """'e' = left early hurt: snap share < 70% of his season median AND on the next week's injury report or out
    the next game. 'r' = rested: under 60% of his median in the season's final regular-season week."""
    if (g, gk) in _pp: return _pp[(g, gk)]
    row = games[g].get(gk); res = ''
    if row and row.get('pct') is not None:
        pcts = [v['pct'] for (yy, _), v in games[g].items() if yy == gk[0] and v.get('pct') is not None]
        if len(pcts) >= 3:
            med = statistics.median(pcts)
            if row['pct'] < 0.7 * med and hurt_after(g, gk, row['team']): res = 'e'
            elif gk[0] < 2026 and gk[1] == max(team_weeks[(gk[0], row['team'])]) and row['pct'] < 0.6 * med: res = 'r'
    _pp[(g, gk)] = res
    return res

team_qb = {}
for (s, tm, wk), grp in st[st['attempts'] > 0].groupby(['season', 'team', 'week']):
    q = grp.sort_values('attempts', ascending=False).iloc[0]['player_id']
    team_qb[(tm, (int(s), int(wk)))] = (q, games[q].get((int(s), int(wk)), {}).get('pct'))
qb_of = lambda tm, gk: team_qb.get((tm, gk), (None, None))[0]
def qb_partial(tm, gk):
    """Leading passer under 80% of snaps, or under 95% and hurt afterwards (left with an injury)."""
    q, pct = team_qb.get((tm, gk), (None, None))
    if q is None or pct is None: return False
    return pct < 0.8 or (pct < 0.95 and hurt_after(q, gk, tm))

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

# team totals per game for target share
team_tgt = collections.Counter()
for r in st.itertuples(index=False):
    team_tgt[(int(r.season), r.team, int(r.week))] += float(r.targets or 0)

# ---------------- defense ranks vs position group, per season ----------------
st['ppr'] = st['receptions'] + 0.1 * (st['rushing_yards'] + st['receiving_yards']) + 6 * (st['rushing_tds'] + st['receiving_tds'])
st['grp'] = st['position'].map(lambda p: 'RB' if p in ('RB', 'FB') else ('PC' if p in ('WR', 'TE') else None))
RANK = {}
for y in (2023, 2024, 2025):
    sy = st[(st['season'] == y) & st['grp'].notna()]
    gp = sy.groupby('opponent_team')['week'].nunique()
    for grp, key in (('RB', 'rb_rank'), ('PC', 'pc_rank')):
        per = (sy[sy['grp'] == grp].groupby('opponent_team')['ppr'].sum() / gp).sort_values(ascending=False)
        for i, tm in enumerate(per.index):
            RANK.setdefault((y, tm), {})[key] = i + 1
for tm, r in DEF26.items():
    RANK[(2026, tm)] = {'rb_rank': int(r['rb_rank']), 'pc_rank': int(r['pc_rank'])}

# ---------------- teammates ----------------
season_team = collections.defaultdict(lambda: collections.defaultdict(list))  # (season, team) -> pid -> [weeks]
for p, gs in games.items():
    for (s, w), v in gs.items():
        season_team[(s, v['team'])][p].append(w)

def top_other(season, team, exclude, kind):
    """Season's No. 1 other target-getter (kind 'tgt': WR/TE by targets/game) or back (kind 'touch': RB by carries+targets/game)."""
    best = None
    for p, wks in season_team[(season, team)].items():
        if p == exclude or len(wks) < 3: continue
        rows = [games[p][(season, w)] for w in wks]
        pos = collections.Counter(v['pos'] for v in rows).most_common(1)[0][0]
        if kind == 'tgt' and pos not in ('WR', 'TE'): continue
        if kind == 'touch' and pos not in ('RB', 'FB'): continue
        vol = sum(v['targets'] + (v['carries'] if kind == 'touch' else 0) for v in rows) / len(rows)
        share = 100 * sum(v['targets'] for v in rows) / max(1, sum(team_tgt[(season, team, w)] for w in wks))
        if best is None or vol > best[1]: best = (p, vol, share, len(rows))
    if best and best[1] >= (5 if kind == 'tgt' else 8): return best
    return None

def mates_2026(g, team, pos):
    m = st[(st['season'] == 2026) & (st['team'] == team) & (st['player_id'] != g)].copy()
    if pos in ('RB', 'FB'):
        m = m[m['position'].isin(['RB', 'FB'])]; m['vol'] = m['carries'] + m['targets']; k, mn = 2, 10
    else:
        m = m[m['position'].isin(['WR', 'TE', 'RB'])]; m['vol'] = m['targets']; k, mn = 3, 10
    return [p for p, t in m.groupby('player_id')['vol'].sum().sort_values(ascending=False).items() if t >= mn][:k]

# ---------------- splits ----------------
STAT = {'Receptions': 'rec', 'Receiving Yards': 'recyd', 'Rushing Yards': 'rushyd', 'Rushing + Receiving Yards': 'rryd',
        'Passing Yards': 'passyd', 'Passing Touchdowns': 'passtd', 'Interceptions': 'int', 'Anytime Touchdown': 'td'}
COL = {'rec': [4], 'recyd': [5], 'rushyd': [6], 'rryd': [5, 6], 'passyd': [7], 'passtd': [8], 'int': [9], 'td': [10]}
val = lambda row, stat: sum(row[i] for i in COL[stat])
yl = lambda ys: '' if not ys else (f"'{str(ys[0])[2:]}" if len(ys) == 1 else f"'{str(ys[0])[2:]}–{str(ys[-1])[2:]}")

PLAYERS = {}  # gsis -> detail (market independent)

def build(g, team, opp):
    if g in PLAYERS: return PLAYERS[g]
    pos = pos_of.get(g, '')
    hist = sorted(gk for gk, v in games.get(g, {}).items() if v['team'] == team)
    if not hist: PLAYERS[g] = None; return None
    names = []; ni = {}
    def nidx(p):
        if p not in ni: ni[p] = len(names); names.append(short(p))
        return ni[p]
    log, I = [], {}
    for gk in hist:
        v = games[g][gk]; q = qb_of(team, gk)
        I[gk] = len(log)
        log.append([gk[0] % 100, gk[1], v['opp'], round(100 * v['pct']) if v['pct'] is not None else None,
                    int(v['receptions']), int(v['receiving_yards']), int(v['rushing_yards']), int(v['passing_yards']),
                    int(v['passing_tds']), int(v['passing_interceptions']), int(v['rushing_tds'] + v['receiving_tds']),
                    nidx(q) if q else None, partial(g, gk), int(v['targets']), int(v['carries']), int(v['attempts'])])
    base = [gk for gk in hist if not partial(g, gk)]
    ix = lambda gks: [I[k] for k in sorted(gks)]
    sets = []
    # --- QB (pass catchers) ---
    if pos in ('WR', 'TE'):
        exp = expected_qb(team); prim = primary.get(team)
        key_qb = prim if (prim and exp != prim and out_this_week(prim)) else exp
        clean = [k for k in base if qb_of(team, k) and not qb_partial(team, k)]
        with_g = [k for k in clean if qb_of(team, k) == key_qb]; wo_g = [k for k in clean if qb_of(team, k) != key_qb]
        nm = disp.get(key_qb, 'the starter'); match_with = key_qb == exp
        a, b = (with_g, wo_g) if match_with else (wo_g, with_g)
        sets.append({'k': 'qb', 'label': f'With {nm} at QB' if match_with else f'Without {nm} at QB',
                     'now': f'This week: {disp.get(exp, "unknown")} expected to start' + ('' if match_with else f' ({nm} out)'),
                     'idx': ix(a), 'alt': {'label': f'Without {nm}' if match_with else f'With {nm}', 'idx': ix(b)},
                     'skipped': ix([k for k in base if k not in clean]), 'pool': True})
    # --- teammates / same lineup ---
    top = mates_2026(g, team, pos)
    mates = []
    if top:
        now = {p: not out_this_week(p) for p in top}
        ok = lambda p, k: played(p, team, k) and not partial(p, k)
        for p in top:
            on_team = {s for s in SEASONS if season_team[(s, team)].get(p)}
            mates.append({'name': disp.get(p, p), 'now': 'active' if now[p] else 'out',
                          'with': ix([k for k in base if ok(p, k)]),
                          'missed': ix([k for k in base if k[0] in on_team and not played(p, team, k)]),
                          'off': ix([k for k in base if k[0] not in on_team]),
                          'partial': ix([k for k in base if played(p, team, k) and partial(p, k)])})
        act = [disp.get(p, p) for p in top if now[p]]; gone = [disp.get(p, p) for p in top if not now[p]]
        gks = [k for k in base if all((ok(p, k) if now[p] else not played(p, team, k)) for p in top)]
        lab = '; '.join(filter(None, [', '.join(act) + (' active' if act else ''), ', '.join(gone) + (' out' if gone else '')]))
        sets.append({'k': 'tc', 'label': 'Same lineup: ' + lab,
                     'now': 'Games where those teammates were playing (or missing, or not yet on the team) just like this week', 'idx': ix(gks), 'pool': True})
    # --- comparable No. 1 competitor ---
    kind = 'touch' if pos in ('RB', 'FB') else 'tgt'
    cur = top_other(2026, team, g, kind)
    if cur:
        cur_out = out_this_week(cur[0])
        who, w_g, wo_g, amb = [], [], [], []
        for s in sorted({k[0] for k in base}):
            c = top_other(s, team, g, kind)
            if not c: continue
            who.append({'season': s, 'name': disp.get(c[0], c[0]), 'vol': round(c[1], 1), 'share': round(c[2], 1), 'g': c[3]})
            for k in [k for k in base if k[0] == s]:
                if played(c[0], team, k):
                    (amb if partial(c[0], k) else w_g).append(k)
                else:
                    wo_g.append(k)
        if who:
            byname = collections.OrderedDict()
            for w in who: byname.setdefault(w['name'].split(' ')[-1], []).append(w['season'])
            tag = ' · '.join(f"{n} {yl(ys)}" for n, ys in byname.items())
            role = 'No. 1 other back' if kind == 'touch' else ('No. 1 target' if pos == 'QB' else 'No. 1 other target')
            a, b = (wo_g, w_g) if cur_out else (w_g, wo_g)
            sets.append({'k': 'comp', 'label': f"{'Without' if cur_out else 'With'} the {role} ({tag})",
                         'now': f"This week: {disp.get(cur[0])} {'out' if cur_out else 'active'} ({cur[1]:.1f} {'touches' if kind == 'touch' else 'targets'}/g, {cur[2]:.0f}% of targets in 2026)",
                         'idx': ix(a), 'alt': {'label': f"{'With' if cur_out else 'Without'} him", 'idx': ix(b)},
                         'skipped': ix(amb), 'who': who, 'pool': cur_out})
    # --- defense ---
    grp, key = ('RB', 'rb_rank') if pos in ('RB', 'FB') else ('WR/TE', 'pc_rank')
    if (2026, opp) in RANK:
        r0 = RANK[(2026, opp)][key]; lo, hi = max(1, r0 - WINDOW), min(32, r0 + WINDOW)
        gks = [k for k in base if (k[0], games[g][k]['opp']) in RANK and lo <= RANK[(k[0], games[g][k]['opp'])].get(key, 99) <= hi]
        sets.append({'k': 'def', 'label': f"Vs defenses ranked {lo}–{hi} vs {grp}{' (pass D proxy)' if pos == 'QB' else ''}",
                     'now': f'This week: {opp} ranks #{r0} (1 = most PPR allowed; each game uses that season’s rank)', 'idx': ix(gks), 'pool': True})
    det = {'p': disp.get(g), 'team': team, 'pos': pos, 'opp': opp, 'seasons': yl(sorted({k[0] for k in hist})),
           'cols': ['yy', 'wk', 'opp', 'snap', 'rec', 'recyd', 'rushyd', 'passyd', 'passtd', 'int', 'td', 'qb', 'flag', 'tgt', 'car', 'att'],
           'log': log, 'names': names, 'base': ix(base), 'sets': sets, 'mates': mates}
    PLAYERS[g] = det
    return det

def summ(det, idx, stat, line):
    vals = [val(det['log'][i], stat) for i in idx]
    hit = (lambda v: v >= 1) if stat == 'td' else (lambda v: v > line)
    return sum(1 for v in vals if hit(v)), len(vals), (sum(vals) / len(vals) if vals else None)

def situational(det, stat, line):
    H = Nn = S = 0
    for s in det['sets']:
        if not s['pool']: continue
        h, n, a = summ(det, s['idx'], stat, line)
        H += h; Nn += n; S += (a or 0) * n
    return (round(100 * H / Nn, 1), Nn, round(S / Nn, 1)) if Nn else ('', 0, '')

# ---------------- bear / base / bull scenarios ----------------
# Volume tiers come from every clean game since 2023 (targets for receiving lines, carries for rushing, touches for
# rush+rec and TDs, pass attempts for QB lines): bear = bottom third, base = middle, bull = top third.
# P(Yes | tier) = his hit rate in that tier, nudged toward his overall rate (2 games' worth).
# Tier odds this week = how this week's situational splits (QB, lineup, No. 1 competitor when out, defense) distribute
# across the tiers, each split weighted equally and nudged toward his overall mix (3 games' worth).
# Blended probability = sum of tier odds x P(Yes | tier); projection = sum of tier odds x tier average.
import numpy as np
VOL = {'rec': [13], 'recyd': [13], 'rushyd': [14], 'rryd': [13, 14], 'td': [13, 14], 'passyd': [15], 'passtd': [15], 'int': [15]}
VUNIT = {'rec': 'targets', 'recyd': 'targets', 'rushyd': 'carries', 'rryd': 'touches', 'td': 'touches', 'passyd': 'attempts', 'passtd': 'attempts', 'int': 'attempts'}
def scenarios(det, stat, line, keep=lambda i: True):
    L = det['log']
    base = [i for i in det['base'] if keep(i)]
    if len(base) < 4: return None
    vol = lambda i: sum(L[i][c] for c in VOL[stat])
    v = sorted(vol(i) for i in base)
    q1, q2 = float(np.quantile(v, 1 / 3)), float(np.quantile(v, 2 / 3))
    a, b = math.ceil(q1 - 1e-9), math.floor(q2 + 1e-9)
    if a > b: a = b = math.floor((q1 + q2) / 2 + 0.5)
    tier = lambda i: 0 if vol(i) < a else (2 if vol(i) > b else 1)
    hit = lambda i: val(L[i], stat) > line
    n = len(base); H = sum(1 for i in base if hit(i)); P_all = H / n
    T = []
    for t in range(3):
        ids = [i for i in base if tier(i) == t]
        h = sum(1 for i in ids if hit(i))
        T.append({'n': len(ids), 'h': h, 'p': (h + 2 * P_all) / (len(ids) + 2),
                  'm': (sum(val(L[i], stat) for i in ids) / len(ids)) if ids else None, 'share': len(ids) / n})
    if sum(1 for t in T if t['n']) < 2: return None
    pools = [[i for i in s['idx'] if keep(i)] for s in det['sets'] if s['pool']]
    W = [0.0, 0.0, 0.0]
    if pools:
        for ids in pools:
            for t in range(3):
                c = sum(1 for i in ids if tier(i) == t)
                W[t] += (c + 3 * T[t]['share']) / (len(ids) + 3) / len(pools)
    else:
        W = [t['share'] for t in T]
    p = sum(W[t] * T[t]['p'] for t in range(3))
    mw = sum(W[t] for t in range(3) if T[t]['m'] is not None)
    proj = sum(W[t] * T[t]['m'] for t in range(3) if T[t]['m'] is not None) / mw
    return {'a': a, 'b': b, 'unit': VUNIT[stat], 'tiers': T, 'w': W, 'p': p, 'proj': proj, 'n': n}

ALIAS = {'Hollywood Brown': 'Marquise Brown', 'Drew Ogletree': 'Andrew Ogletree'}
def who(player, game):
    player = ALIAS.get(player, player)
    a, h = game.split(' @ ')
    for t in (a, h):
        g = name_team.get((norm(player), t))
        if g: return g, t, (h if t == a else a)
    return None, None, None

SITCOLS = ['sit_key', 'sit_stat', 'sit_line', 'sit_hit', 'sit_n', 'sit_proj', 'sit_lo', 'sit_hi', 'sit_pool', 'sit_edge']
miss = collections.Counter()
def enrich(path, kind):
    rows = list(csv.DictReader(open(path)))
    cols = [c for c in rows[0].keys() if not c.startswith('sit_')] + SITCOLS
    done = 0
    for r in rows:
        for c in SITCOLS: r[c] = ''
        if kind == 'atd':
            market, player, line = 'Anytime Touchdown', r['player'], 0.5
        else:
            market = r['market']
            if market not in STAT: continue
            m = re.match(r'^(.*?): Over ([\d.]+) ', r['contract'])
            player, line = (m.group(1), float(m.group(2))) if m else (r['contract'], 0.5)
        g, team, opp = who(player, r['game'])
        if not g: miss[player] += 1; continue
        det = build(g, team, opp)
        if not det: continue
        stat = STAT[market]
        pooled, n, proj = situational(det, stat, line)
        sc = scenarios(det, stat, line)
        price = float(r['yes_price']) if r.get('yes_price') not in ('', None) else None
        if sc:
            h = round(100 * sc['p'], 1)
            r.update({'sit_n': sc['n'], 'sit_proj': round(sc['proj'], 2 if stat in ('td', 'passtd', 'int') else 1),
                      'sit_lo': round(sc['tiers'][0]['m'], 1) if sc['tiers'][0]['m'] is not None else '',
                      'sit_hi': round(sc['tiers'][2]['m'], 1) if sc['tiers'][2]['m'] is not None else ''})
        else:
            h = pooled
            r.update({'sit_n': n, 'sit_proj': proj})
        r.update({'sit_key': g, 'sit_stat': stat, 'sit_line': line, 'sit_hit': h, 'sit_pool': pooled,
                  'sit_edge': round(h - price, 1) if (h != '' and price is not None) else ''})
        done += 1
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    return done, len(rows)

if __name__ == '__main__' and 'probe' not in sys.argv:
    print('lines', enrich(B + 'inband_w7.csv', 'lines'))
    print('props', enrich(B + 'props_cat_w7.csv', 'lines'))
    print('atd', enrich(B + 'atd_w7.csv', 'atd'))
    print('unmatched', miss.most_common(20))
    with open(B + 'sit_w7.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['key', 'player', 'team', 'pos', 'detail'])
        for g, det in sorted(PLAYERS.items(), key=lambda x: (x[1] or {}).get('p') or ''):
            if det: w.writerow([g, det['p'], det['team'], det['pos'], json.dumps(det, separators=(',', ':'), ensure_ascii=False)])
    print('players', sum(1 for d in PLAYERS.values() if d), 'bytes', os.path.getsize(B + 'sit_w7.csv'))
