import json, collections, csv
import pandas as pd

B = '/home/claude/wedger/rh/'
D = '/home/claude/wedger/nflverse_dl/'

players = json.load(open(B + 'atd_players.json'))
prices = json.load(open(B + 'atd_prices.json'))
t = json.load(open('/root/.claude/projects/-home-claude/7b7587cd-449e-5d94-986d-7a2d5c82d9a5/tool-results/mcp-remote-devices-Claude_Browser__javascript_tool-1792353621605.txt'))[0]['text']
i = t.find('\n\n(captured'); t = t[:i] if i >= 0 else t
gamelog = json.loads(t)['gl']
espn = json.load(open(B + 'espn.json'))
week_of = {g['id']: g['w'] for g in espn['games']}

# Joshua Palmer (BUF WR) was missing from the nflverse roster under that name
ro = pd.read_csv(D + 'roster2026.csv', low_memory=False)
pal = ro[(ro['last_name'] == 'Palmer') & (ro['team'] == 'BUF')]
for e in prices['events']:
    if e['name'].startswith('Las Vegas vs Buffalo'):
        for c in e['c']:
            if c['player'] == 'Joshua Palmer':
                players.append({'player': 'Joshua Palmer', 'event': 'Las Vegas vs Buffalo',
                                'gsis': pal['gsis_id'].iloc[0] if len(pal) else None, 'espn': '4242433',
                                'pos': 'WR', 'team': 'BUF', 'ya': c['ya'], 'yb': c['yb'], 'na': c['na'],
                                'st': c['st'], 'trad': c['trad'], 'ncand': 1})

GAME = {'Los Angeles R vs Arizona': ('ARI @ LAR', '3:05 PM CT Sun'),
        'Kansas City vs Los Angeles C': ('LAC @ KC', '3:25 PM CT Sun'),
        'Las Vegas vs Buffalo': ('BUF @ LV', '3:25 PM CT Sun'),
        'Green Bay vs Dallas': ('DAL @ GB', '7:20 PM CT Sun'),
        'San Francisco vs Washington': ('WSH @ SF', '7:15 PM CT Mon')}
TEAM_FIX = {'LA': 'LAR', 'WAS': 'WSH'}

pbp = pd.read_csv(D + 'pbp2026.csv.gz', low_memory=False)
p = pbp[(pbp['play_type'].isin(['run', 'pass'])) & (pbp['play_deleted'] == 0) &
        (pbp['two_point_attempt'] != 1) & (pbp['qb_kneel'] == 0) & (pbp['qb_spike'] == 0)].copy()
p['rz'] = p['yardline_100'] <= 20
p['i10'] = p['yardline_100'] <= 10
car = p[(p['rush_attempt'] == 1) & p['rusher_player_id'].notna()]
tgt = p[(p['pass_attempt'] == 1) & (p['sack'] != 1) & p['receiver_player_id'].notna()]

# team totals per (team, week)
team_t = tgt.groupby(['posteam', 'week']).size()
team_rzt = tgt[tgt['rz']].groupby(['posteam', 'week']).size()
team_rzc = car[car['rz']].groupby(['posteam', 'week']).size()

def g(series, key):
    return int(series.get(key, 0))

rows = []
for pl in players:
    gid = pl['gsis']; eid = pl['espn']
    weeks = sorted({week_of[e] for e in gamelog.get(eid, []) if e in week_of}) if isinstance(gamelog.get(eid), list) else []
    pc = car[car['rusher_player_id'] == gid]; pt = tgt[tgt['receiver_player_id'] == gid]
    # player's team each week = team on his plays that week, else roster team
    team_by_week = {}
    for df in (pc, pt):
        for w, tm in zip(df['week'], df['posteam']):
            team_by_week[w] = tm
    roster_team = {'LAR': 'LA', 'WSH': 'WAS'}.get(pl['team'], pl['team'])
    n = len(weeks)
    targets = rz_t = rz_c = i10 = 0; team_targets = team_rz_t = team_rz_c = 0
    tds_by_week = {}
    for w in weeks:
        tm = team_by_week.get(w, roster_team)
        wt = pt[pt['week'] == w]; wc = pc[pc['week'] == w]
        targets += len(wt); rz_t += int(wt['rz'].sum()); rz_c += int(wc['rz'].sum())
        i10 += int(wt['i10'].sum()) + int(wc['i10'].sum())
        team_targets += g(team_t, (tm, w)); team_rz_t += g(team_rzt, (tm, w)); team_rz_c += g(team_rzc, (tm, w))
        # credited only when he is the one who scored (a lateral after his catch goes to the other player)
        tds_by_week[w] = int(((wc['rush_touchdown'] == 1) & (wc['td_player_id'] == gid)).sum() +
                             ((wt['pass_touchdown'] == 1) & (wt['td_player_id'] == gid)).sum())
    tds = sum(tds_by_week.values())
    hits = sum(1 for v in tds_by_week.values() if v >= 1)
    pct = lambda a, b: round(100 * a / b, 1) if b else None
    game, kick = GAME[pl['event']]
    ya = float(pl['ya']) if pl['ya'] else None
    rate = pct(hits, n)
    flags = []
    if n == 0: flags.append('No 2026 games')
    elif n < 3: flags.append('Small sample')
    if pl['st'] != 'active' or pl['trad'] != 'TRADABLE': flags.append('Inactive')
    elif ya is None: flags.append('No price')
    elif not pl['yb']: flags.append('No bid')
    elif ya - float(pl['yb']) > 0.05 + 1e-9: flags.append('Wide spread')
    if game == 'ARI @ LAR': flags.append('Live — kicked off 3:05 PM')
    rows.append({
        'id': f"{game}|{pl['player']}", 'game': game, 'kickoff': kick, 'player': pl['player'], 'pos': pl['pos'],
        'team': TEAM_FIX.get(pl['team'], pl['team']),
        'yes_price': round(ya * 100) if ya is not None else '',
        'yes_bid': round(float(pl['yb']) * 100) if pl['yb'] else '',
        'games': n, 'atd_hits': hits if n else '', 'atd_rate': rate if rate is not None else '',
        'tds': tds if n else '', 'td_pg': round(tds / n, 2) if n else '',
        'targets': targets if n else '', 'target_share': pct(targets, team_targets) if n else '',
        'rz_targets': rz_t if n else '', 'rz_tgt_share': pct(rz_t, team_rz_t) if n else '',
        'rz_carries': rz_c if n else '', 'rz_opps': (rz_t + rz_c) if n else '',
        'rz_opp_share': pct(rz_t + rz_c, team_rz_t + team_rz_c) if n else '',
        'rz_opps_pg': round((rz_t + rz_c) / n, 1) if n else '',
        'i10_opps_pg': round(i10 / n, 1) if n else '',
        'td_log': ', '.join(f'W{w}:{tds_by_week[w]}' for w in weeks),
        'flags': '; '.join(flags),
    })

df = pd.DataFrame(rows)
played = df['games'] > 0
pool = df['games'] >= 3  # percentiles are measured against players with 3+ games
COMP = ['rz_opp_share', 'target_share', 'rz_tgt_share', 'td_pg', 'atd_rate']
for c in COMP:
    ref = sorted(pd.to_numeric(df.loc[pool, c]))
    def pctl(x):
        if x == '' or pd.isna(x): return None
        x = float(x); lt = sum(1 for v in ref if v < x); eq = sum(1 for v in ref if v == x)
        return round(100 * (lt + 0.5 * eq) / len(ref))
    df[c + '_pctl'] = [pctl(x) if g > 0 else None for x, g in zip(df[c], df['games'])]
df['score'] = df[[c + '_pctl' for c in COMP]].mean(axis=1).round(0)
for c in [c + '_pctl' for c in COMP] + ['score']:
    df[c] = df[c].apply(lambda x: '' if x is None or pd.isna(x) else int(x))
df['rate_minus_price'] = [round(r - pr, 1) if (r != '' and pr != '') else '' for r, pr in zip(df['atd_rate'], df['yes_price'])]
df = df.sort_values(['score'], key=lambda s: pd.to_numeric(s, errors='coerce'), ascending=False)
df.to_csv(B + 'atd.csv', index=False)

# validation vs ESPN box score rush+rec TDs
box_td = collections.Counter()
for gid_, teams in espn['box'].items():
    for tm in teams:
        for cat in ('rushing', 'receiving'):
            if cat in tm['c']:
                L = tm['c'][cat]['l']
                for pid, nm, st in tm['c'][cat]['a']:
                    box_td[pid] += float(st[L.index('TD')])
mism = []
for pl, r in zip(players, rows):
    if r['games'] and int(box_td.get(pl['espn'], 0)) != r['tds']:
        mism.append((pl['player'], r['tds'], box_td.get(pl['espn'], 0)))
print('rows', len(df), 'played', int(played.sum()), 'TD mismatches vs ESPN:', mism)
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 200)
print(df[['game', 'player', 'pos', 'yes_price', 'games', 'atd_rate', 'td_pg', 'rz_opp_share', 'rz_opps_pg', 'target_share', 'rz_tgt_share', 'score', 'rate_minus_price', 'flags']].head(45).to_string(index=False))
