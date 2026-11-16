import json, collections, csv
import pandas as pd

B = '/home/claude/wedger/rh/'
D = '/home/claude/wedger/dl8/'
gamelog = {}
espn = json.load(open(B + 'espn_thru8.json'))
week_of = {g['id']: g['w'] for g in espn['games']}
TEAM_FIX = {'LA': 'LAR', 'WAS': 'WSH'}

pbp = pd.read_csv(D + 'play_by_play_2026.csv.gz', low_memory=False)
pbp = pbp[(pbp['season_type'] == 'REG') & (pbp['week'] <= 8)]
pbp['posteam'] = pbp['posteam'].replace({'LA': 'LAR', 'WAS': 'WSH'})
p = pbp[(pbp['play_type'].isin(['run', 'pass'])) & (pbp['play_deleted'] == 0) &
        (pbp['two_point_attempt'] != 1) & (pbp['qb_kneel'] == 0) & (pbp['qb_spike'] == 0)].copy()
p['rz'] = p['yardline_100'] <= 20
car = p[(p['rush_attempt'] == 1) & p['rusher_player_id'].notna()]
tgt = p[(p['pass_attempt'] == 1) & (p['sack'] != 1) & p['receiver_player_id'].notna()]
team_t = tgt.groupby(['posteam', 'week']).size()
team_rzt = tgt[tgt['rz']].groupby(['posteam', 'week']).size()
team_rzc = car[car['rz']].groupby(['posteam', 'week']).size()
g = lambda s, k: int(s.get(k, 0))

def metrics(gid, weeks, roster_team):
    pc = car[car['rusher_player_id'] == gid]; pt = tgt[tgt['receiver_player_id'] == gid]
    team_by_week = {}
    for df in (pc, pt):
        for w, tm in zip(df['week'], df['posteam']):
            team_by_week[w] = tm
    targets = rz_t = rz_c = 0; tt = trzt = trzc = 0; tds = {}
    for w in weeks:
        tm = team_by_week.get(w, roster_team)
        wt = pt[pt['week'] == w]; wc = pc[pc['week'] == w]
        targets += len(wt); rz_t += int(wt['rz'].sum()); rz_c += int(wc['rz'].sum())
        tt += g(team_t, (tm, w)); trzt += g(team_rzt, (tm, w)); trzc += g(team_rzc, (tm, w))
        tds[w] = int(((wc['rush_touchdown'] == 1) & (wc['td_player_id'] == gid)).sum() +
                     ((wt['pass_touchdown'] == 1) & (wt['td_player_id'] == gid)).sum())
    n = len(weeks)
    pct = lambda a, b: round(100 * a / b, 1) if b else 0.0
    return {'games': n, 'atd_hits': sum(1 for v in tds.values() if v >= 1), 'tds': sum(tds.values()),
            'atd_rate': pct(sum(1 for v in tds.values() if v >= 1), n), 'td_pg': round(sum(tds.values()) / n, 2) if n else 0,
            'targets': targets, 'target_share': pct(targets, tt), 'rz_targets': rz_t, 'rz_tgt_share': pct(rz_t, trzt),
            'rz_carries': rz_c, 'rz_opps': rz_t + rz_c, 'rz_opp_share': pct(rz_t + rz_c, trzt + trzc),
            'rz_opps_pg': round((rz_t + rz_c) / n, 1) if n else 0,
            'td_log': ', '.join(f'W{w}:{tds[w]}' for w in weeks)}

# ---- league-wide reference pool: players with 3+ games of involvement and 2+ opportunities per game ----
inv = pd.concat([car[['rusher_player_id', 'week', 'posteam']].rename(columns={'rusher_player_id': 'pid'}),
                 tgt[['receiver_player_id', 'week', 'posteam']].rename(columns={'receiver_player_id': 'pid'})])
opp_ct = inv.groupby('pid').size()
pool = []
for pid, grp in inv.groupby('pid'):
    weeks = sorted(grp['week'].unique())
    if len(weeks) >= 3 and opp_ct[pid] / len(weeks) >= 2:
        pool.append(metrics(pid, weeks, grp['posteam'].iloc[-1]))
COMP = ['rz_opp_share', 'target_share', 'rz_tgt_share', 'td_pg', 'atd_rate']
ref = {c: sorted(m[c] for m in pool) for c in COMP}
def pctl(c, x):
    r = ref[c]; lt = sum(1 for v in r if v < x); eq = sum(1 for v in r if v == x)
    return round(100 * (lt + 0.5 * eq) / len(r))
print('reference pool size', len(pool))

# ---- every Week 7 Anytime TD line: Robinhood (NE @ CHI) + sportsbook averages (other games) ----
import re, unicodedata
from w9_build_inband_ko import KO
def _norm(n):
    n = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode().lower().replace('.', '').replace("'", '').replace('-', ' ')
    n = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', n)
    return re.sub(r'\s+', ' ', n).strip()
ROST = {}
for _r in sorted(csv.DictReader(open(D + 'roster_weekly_2026.csv')), key=lambda r: int(r['week'] or 0)):
    ROST.setdefault(_norm(_r['full_name']), {})[TEAM_FIX.get(_r['team'], _r['team'])] = _r
CITY2 = {'Buffalo': 'BUF', 'Jacksonville': 'JAX', 'Los Angeles C': 'LAC', 'Washington': 'WSH', 'Arizona': 'ARI', 'Los Angeles R': 'LAR', 'Baltimore': 'BAL', 'Cleveland': 'CLE', 'Las Vegas': 'LV', 'Carolina': 'CAR',
         'Philadelphia': 'PHI', 'Chicago': 'CHI', 'Atlanta': 'ATL', 'Dallas': 'DAL', 'Green Bay': 'GB', 'Houston': 'HOU',
         'Kansas City': 'KC', 'New Orleans': 'NO', 'New York G': 'NYG', 'New York J': 'NYJ', 'New England': 'NE',
         'Pittsburgh': 'PIT', 'Tampa Bay': 'TB', 'Tennessee': 'TEN', 'Indianapolis': 'IND', 'San Francisco': 'SF',
         'Minnesota': 'MIN', 'Miami': 'MIA', 'Cincinnati': 'CIN', 'Detroit': 'DET', 'Denver': 'DEN', 'Seattle': 'SEA'}
GAMES = list(KO.keys())
def game_for(evname):
    t = evname.split(':')[0].split(' vs ')
    a, b = CITY2[t[0]], CITY2[t[1]]
    return f'{a} @ {b}' if f'{a} @ {b}' in KO else f'{b} @ {a}'
box_weeks = collections.defaultdict(set)  # espn id -> weeks with a box-score line
for gid, teams in espn['box'].items():
    for t in teams:
        for cat, d in t['c'].items():
            for pid, nm, st in d['a']:
                box_weeks[pid].add(week_of[gid])
BOXPID = {}
for gid, teams in espn['box'].items():
    for t in teams:
        for cat, d in t['c'].items():
            for pid, nm, st in d['a']:
                BOXPID[_norm(nm)] = pid
BYESPN = {}
for nm, byteam in ROST.items():
    for tm, r in byteam.items():
        if r['espn_id']:
            BYESPN.setdefault(r['espn_id'].split('.')[0], {})[tm] = r
players = []
for e in json.load(open(B + 'rh_events_w9.json')):
    if not e[1].endswith(': Anytime Touchdown'):
        continue
    game = game_for(e[1]); teams = game.split(' @ ')
    for c in e[4]:
        name = c[0]; cand = ROST.get(_norm(name), {})
        if not cand and BOXPID.get(_norm(name)) in BYESPN:
            cand = BYESPN[BOXPID[_norm(name)]]
        r = next((cand[t] for t in teams if t in cand), None)
        players.append({'player': name, 'game': game, 'gsis': r['gsis_id'] if r else None, 'espn': (r['espn_id'] or '').split('.')[0] if r else None,
                        'pos': r['position'] if r else '', 'team': TEAM_FIX.get(r['team'], r['team']) if r else '',
                        'ya': c[1], 'yb': c[2], 'na': c[3], 'st': 'active' if c[6] in ('active', 'consensus') else (c[6] or ''),
                        'trad': c[5], 'source': c[8] if len(c) > 8 else 'Robinhood', 'book_lines': c[9] if len(c) > 9 else '', 'book_fair': c[10] if len(c) > 10 else ''})
print('ATD lines', len(players), 'unmatched', [p['player'] for p in players if not p['gsis']])

rows = []
for pl in players:
    wk = {week_of[e] for e in gamelog.get(pl['espn'] or '', []) if e in week_of} if pl['espn'] in gamelog else set(box_weeks.get(pl['espn'] or '', set()))
    if pl['gsis']:
        wk |= set(car[car['rusher_player_id'] == pl['gsis']]['week']) | set(tgt[tgt['receiver_player_id'] == pl['gsis']]['week'])
    weeks = sorted(int(w) for w in wk)
    m = metrics(pl['gsis'], weeks, pl['team']) if (weeks and pl['gsis']) else None
    ya = float(pl['ya']) if pl['ya'] else None
    flags = []
    if not weeks: flags.append('No 2026 games')
    elif len(weeks) < 3: flags.append('Small sample')
    book = pl['source'] != 'Robinhood'
    if pl['st'] != 'active' or pl['trad'] != 'TRADABLE': flags.append('Inactive')
    elif ya is None: flags.append('No price')
    elif book: pass
    elif not pl['yb']: flags.append('No bid')
    elif ya - float(pl['yb']) > 0.05 + 1e-9: flags.append('Wide spread')
    row = {'id': f"{pl['game']}|{pl['player']}", 'game': pl['game'], 'kickoff': KO[pl['game']][0], 'player': pl['player'],
           'pos': pl['pos'], 'team': TEAM_FIX.get(pl['team'], pl['team']),
           'yes_price': round(ya * 100) if ya is not None else '', 'yes_bid': round(float(pl['yb']) * 100) if pl['yb'] else ''}
    keys = ['games', 'atd_hits', 'atd_rate', 'tds', 'td_pg', 'targets', 'target_share', 'rz_targets', 'rz_tgt_share',
            'rz_carries', 'rz_opps', 'rz_opp_share', 'rz_opps_pg', 'td_log']
    for k in keys:
        row[k] = m[k] if m else ('' if k != 'games' else 0)
    row['i10_opps_pg'] = ''
    row['flags'] = '; '.join(flags)
    for c in COMP:
        row[c + '_pctl'] = pctl(c, m[c]) if m else ''
    row['score'] = round(sum(row[c + '_pctl'] for c in COMP) / len(COMP)) if m else ''
    row['rate_minus_price'] = round(m['atd_rate'] - row['yes_price'], 1) if (m and row['yes_price'] != '') else ''
    row['kickoff_utc'] = KO[pl['game']][1]
    row['priced_at'] = 'Mon Nov 2 ~3:15 PM CT'
    row['source'] = 'Robinhood' if not book else 'Sportsbook avg'
    row['source_detail'] = pl['source'] if book else ''
    row['book_lines'] = pl['book_lines']
    row['book_fair'] = round(100 * float(pl['book_fair']), 1) if pl.get('book_fair') else ''
    rows.append(row)

old_cols = list(csv.DictReader(open(B + 'atd_v3.csv')).fieldnames) + ['source', 'source_detail', 'book_lines', 'book_fair']
rows.sort(key=lambda r: -(r['score'] if r['score'] != '' else -1))
with open(B + 'atd_w9.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=old_cols); w.writeheader(); w.writerows(rows)
df = pd.DataFrame(rows)
print(df[['game', 'player', 'pos', 'yes_price', 'games', 'atd_rate', 'score', 'source', 'flags']].head(30).to_string(index=False)); print(len(df), 'rows; qualified', int(((df['games'].astype(int) >= 3) & (pd.to_numeric(df['atd_rate'], errors='coerce') > 50)).sum()))
