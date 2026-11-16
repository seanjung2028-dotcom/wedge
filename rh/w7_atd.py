import json, collections, csv
import pandas as pd

B = '/home/claude/wedger/rh/'
D = '/home/claude/wedger/nflverse_dl/'
players = json.load(open(B + 'atd_players_w7.json'))
gamelog = json.load(open(B + 'gamelog_w7.json'))
espn = json.load(open(B + 'espn_thru6.json'))
week_of = {g['id']: g['w'] for g in espn['games']}
TEAM_FIX = {'LA': 'LAR', 'WAS': 'WSH'}

pbp = pd.read_csv(D + 'pbp2026_w6.csv.gz', low_memory=False)
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

rows = []
for pl in players:
    weeks = sorted({week_of[e] for e in gamelog.get(pl['espn'], []) if e in week_of})
    m = metrics(pl['gsis'], weeks, pl['team']) if weeks else None
    ya = float(pl['ya']) if pl['ya'] else None
    flags = []
    if not weeks: flags.append('No 2026 games')
    elif len(weeks) < 3: flags.append('Small sample')
    if pl['st'] != 'active' or pl['trad'] != 'TRADABLE': flags.append('Inactive')
    elif ya is None: flags.append('No price')
    elif not pl['yb']: flags.append('No bid')
    elif ya - float(pl['yb']) > 0.05 + 1e-9: flags.append('Wide spread')
    row = {'id': f"NE @ CHI|{pl['player']}", 'game': 'NE @ CHI', 'kickoff': '7:15 PM CT Thu', 'player': pl['player'],
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
    row['kickoff_utc'] = '2026-10-23T00:15:00Z'
    row['priced_at'] = 'Mon 10:33 PM CT'
    rows.append(row)

old_cols = list(csv.DictReader(open(B + 'atd_v3.csv')).fieldnames)
rows.sort(key=lambda r: -(r['score'] if r['score'] != '' else -1))
with open(B + 'atd_w7.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=old_cols); w.writeheader(); w.writerows(rows)
df = pd.DataFrame(rows)
print(df[['player', 'pos', 'yes_price', 'games', 'atd_hits', 'atd_rate', 'td_pg', 'rz_opp_share', 'target_share', 'rz_tgt_share', 'score', 'flags']].to_string(index=False))
