import json, re, collections, unicodedata, csv, sys

BASE = '/home/claude/wedger/rh/'
ev = json.load(open(BASE + 'rh_events_w10.json'))  # Week 7, priced Tue Oct 20 ~8:20 PM CT (Robinhood + sportsbook averages)
TFIX = {'WAS': 'WSH', 'LA': 'LAR'}
espn = json.load(open(BASE + 'espn_thru9.json'))  # 2026 Weeks 1-6

CITY = {
    'Arizona': 'ARI', 'Los Angeles R': 'LAR', 'Baltimore': 'BAL', 'Cleveland': 'CLE', 'Buffalo': 'BUF',
    'Las Vegas': 'LV', 'Carolina': 'CAR', 'Philadelphia': 'PHI', 'Chicago': 'CHI', 'Atlanta': 'ATL',
    'Dallas': 'DAL', 'Green Bay': 'GB', 'Houston': 'HOU', 'Jacksonville': 'JAX', 'Los Angeles C': 'LAC',
    'Kansas City': 'KC', 'New Orleans': 'NO', 'New York G': 'NYG', 'New York J': 'NYJ', 'New England': 'NE',
    'Pittsburgh': 'PIT', 'Tampa Bay': 'TB', 'Tennessee': 'TEN', 'Indianapolis': 'IND',
    'San Francisco': 'SF', 'Washington': 'WSH', 'Minnesota': 'MIN', 'Miami': 'MIA', 'Cincinnati': 'CIN',
    'Detroit': 'DET', 'Denver': 'DEN', 'Seattle': 'SEA',
}
NICK = {
    'Cardinals': 'ARI', 'Rams': 'LAR', 'Ravens': 'BAL', 'Browns': 'CLE', 'Bills': 'BUF', 'Raiders': 'LV',
    'Panthers': 'CAR', 'Eagles': 'PHI', 'Bears': 'CHI', 'Falcons': 'ATL', 'Cowboys': 'DAL', 'Packers': 'GB',
    'Texans': 'HOU', 'Jaguars': 'JAX', 'Chargers': 'LAC', 'Chiefs': 'KC', 'Saints': 'NO', 'Giants': 'NYG',
    'Jets': 'NYJ', 'Patriots': 'NE', 'Steelers': 'PIT', 'Buccaneers': 'TB', 'Titans': 'TEN', 'Colts': 'IND',
    '49ers': 'SF', 'Commanders': 'WSH', 'Vikings': 'MIN', 'Dolphins': 'MIA', 'Bengals': 'CIN', 'Lions': 'DET',
    'Broncos': 'DEN', 'Seahawks': 'SEA',
}
ABBRS = set(CITY.values())

# ---------- ESPN: team game records ----------
finals = [g for g in espn['games'] if g['st'] == 'STATUS_FINAL']
team_games = collections.defaultdict(list)
for g in finals:
    for me, op in (('h', 'a'), ('a', 'h')):
        m, o = g[me], g[op]
        ls_m = m['ls'] + [0] * (4 - len(m['ls']))
        ls_o = o['ls'] + [0] * (4 - len(o['ls']))
        team_games[m['t']].append({
            'gid': g['id'], 'w': g['w'], 'opp': o['t'], 'home': me == 'h',
            'pts': m['s'], 'opp_pts': o['s'], 'ls': ls_m, 'ols': ls_o,
            'ot': len(m['ls']) > 4,
        })
game_by_id = {g['id']: g for g in finals}


def games_union(*teams):
    seen = {}
    for t in teams:
        for r in team_games[t]:
            seen.setdefault(r['gid'], r)
    return list(seen.values())


def period_pts(r, period, opp=False):
    ls = r['ols'] if opp else r['ls']
    if period == 'Q1': return ls[0]
    if period == 'Q2': return ls[1]
    if period == 'Q3': return ls[2]
    if period == 'Q4': return ls[3]
    if period == 'H1': return ls[0] + ls[1]
    if period == 'H2': return sum(ls[2:])  # includes OT
    if period == 'FG': return sum(ls)
    raise ValueError(period)


# ---------- ESPN: player game logs ----------
def norm(n):
    n = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode()
    n = n.lower().replace('.', '').replace("'", '').replace('-', ' ')
    n = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', n)
    return re.sub(r'\s+', ' ', n).strip()


player_games = collections.defaultdict(dict)  # norm name -> gid -> stats
max_rec = {}
for gid, teams in espn['box'].items():
    best = 0
    for t in teams:
        for cat, d in t['c'].items():
            L = d['l']
            for pid, nm, st in d['a']:
                k = norm(nm)
                s = player_games[k].setdefault(gid, {'team': t['t'], 'name': nm, 'rec': 0, 'recyds': 0, 'rushyds': 0,
                                                    'passyds': 0, 'passtd': 0, 'int': 0, 'rushtd': 0, 'rectd': 0})
                def v(lbl):
                    try:
                        return float(st[L.index(lbl)])
                    except Exception:
                        return 0.0
                if cat == 'passing':
                    s['passyds'] = v('YDS'); s['passtd'] = v('TD'); s['int'] = v('INT')
                elif cat == 'rushing':
                    s['rushyds'] = v('YDS'); s['rushtd'] = v('TD')
                elif cat == 'receiving':
                    s['rec'] = v('REC'); s['recyds'] = v('YDS'); s['rectd'] = v('TD')
                    best = max(best, v('YDS'))
    max_rec[gid] = best

# Games the player appeared in (per ESPN game log) but recorded no box-score line -> zeros
ZERO_GAMES = {}  # Week 8 build: nflverse box scores (no ESPN game-log zero lines)
for nm, gids in ZERO_GAMES.items():
    k = norm(nm)
    team = next(iter(player_games[k].values()))['team'] if player_games.get(k) else None
    for gid in gids:
        player_games[k].setdefault(gid, {'team': team, 'name': nm, 'rec': 0, 'recyds': 0, 'rushyds': 0,
                                         'passyds': 0, 'passtd': 0, 'int': 0, 'rushtd': 0, 'rectd': 0})

# ---------- Robinhood: map events to Sunday games ----------
SUNDAY = {}
for e in ev:
    slug, name = e[0], e[1]
    if re.fullmatch(r'[a-z-]+-vs-[a-z-]+-(?:nov-1[2-6])-2026(-[0-9a-f]{8})?', slug) and not re.search(
            r'(spreads|totals|overtime|winning-margin|most-receiving-yards|1st-half-fulltime-result)', slug):
        a, h = name.split(' vs ')
        SUNDAY[(CITY[a], CITY[h])] = name


def game_of(evname):
    head = evname.split(':')[0]
    head = re.sub(r' (Spreads|Totals)$', '', head)
    parts = head.split(' vs ')
    if len(parts) != 2:
        return None
    x, y = CITY.get(parts[0].strip()), CITY.get(parts[1].strip())
    if (x, y) in SUNDAY: return (x, y)
    if (y, x) in SUNDAY: return (y, x)
    return None


def ev_type(e):
    slug, name = e[0], e[1]
    if ':' in name:
        return name.split(': ', 1)[1]
    if re.search(r'-spreads-(?:nov-1[2-6])-2026$', slug): return 'Spreads'
    if re.search(r'-totals-(?:nov-1[2-6])-2026$', slug): return 'Totals'
    return 'Moneyline'


def rate(hits, n):
    return (hits / n) if n else None


PROP_STAT = {
    'Rec Yards': lambda s: s['recyds'], 'Receiving Yards': lambda s: s['recyds'], 'Receptions': lambda s: s['rec'], 'Rush Yards': lambda s: s['rushyds'],
    'Rush+Receiving Yards': lambda s: s['rushyds'] + s['recyds'], 'Pass Yards': lambda s: s['passyds'],
    'Pass TDs': lambda s: s['passtd'], 'Interceptions': lambda s: s['int'],
}


def evaluate(etype, cname, game):
    """Return (hits, n, sample_desc, condition_text, detail) or None if not evaluable."""
    away, home = game
    # --- player props with a line ---
    m = re.match(r'^(.*?): Over ([\d.]+) (Rec Yards|Receiving Yards|Receptions|Rush Yards|Rush\+Receiving Yards|Pass Yards|Pass TDs|Interceptions)$', cname)
    if m:
        pl, line, stat = m.group(1), float(m.group(2)), m.group(3)
        logs = player_games.get(norm(pl))
        if not logs:
            return (None, 0, 'player not found in 2026 box scores', f'{pl} over {line} {stat}', '')
        vals = [(game_by_id[g]['w'], PROP_STAT[stat](s)) for g, s in logs.items()]
        vals.sort()
        hits = sum(1 for _, x in vals if x > line)
        return (hits, len(vals), f"{pl}'s 2026 games", f'{pl} over {line} {stat}',
                ', '.join(f'W{w}:{int(x) if x == int(x) else x}' for w, x in vals))
    if etype in ('Anytime Touchdown', '2+ Touchdowns', '3+ Touchdowns'):
        need = {'Anytime Touchdown': 1, '2+ Touchdowns': 2, '3+ Touchdowns': 3}[etype]
        logs = player_games.get(norm(cname))
        if not logs:
            return (None, 0, 'player not found', f'{cname} {need}+ rush/rec TD', '')
        vals = sorted((game_by_id[g]['w'], s['rushtd'] + s['rectd']) for g, s in logs.items())
        hits = sum(1 for _, x in vals if x >= need)
        return (hits, len(vals), f"{cname}'s 2026 games", f'{cname} scores {need}+ rush/rec TD',
                ', '.join(f'W{w}:{int(x)}' for w, x in vals))
    if etype == 'Most Receiving Yards':
        logs = player_games.get(norm(cname))
        if not logs:
            return (None, 0, 'player not found', f'{cname} leads game in rec yds', '')
        vals = sorted((game_by_id[g]['w'], s['recyds'], max_rec[g]) for g, s in logs.items())
        hits = sum(1 for _, x, mx in vals if x >= mx and x > 0)
        return (hits, len(vals), f"{cname}'s 2026 games", f'{cname} has most rec yds in game',
                ', '.join(f'W{w}:{int(x)}/{int(mx)}' for w, x, mx in vals))
    # --- full-game team markets ---
    if etype == 'Moneyline':
        t = TFIX.get(cname, cname)
        rs = team_games[t]
        hits = sum(1 for r in rs if r['pts'] > r['opp_pts'])
        return (hits, len(rs), f'{t} games', f'{t} wins', rec_str(rs))
    if etype == 'Spreads':
        m = re.match(r'^(.*) wins by over ([\d.]+) points$', cname)
        t, line = CITY[m.group(1)], float(m.group(2))
        rs = team_games[t]
        hits = sum(1 for r in rs if r['pts'] - r['opp_pts'] > line)
        return (hits, len(rs), f'{t} games', f'{t} wins by {line}+', margins(rs))
    if etype == 'Totals':
        line = float(re.match(r'^Over ([\d.]+) points$', cname).group(1))
        rs = games_union(away, home)
        hits = sum(1 for r in rs if r['pts'] + r['opp_pts'] > line)
        return (hits, len(rs), f'all {away} + {home} games', f'game total over {line}',
                ', '.join(str(r['pts'] + r['opp_pts']) for r in rs))
    if etype == 'Winning Margin':
        if cname == 'Tie':
            rs = games_union(away, home)
            hits = sum(1 for r in rs if r['pts'] == r['opp_pts'])
            return (hits, len(rs), f'all {away} + {home} games', 'game ends tied', '')
        m = re.match(r'^(.*) by (\d+) (?:to (\d+)|or more)$', cname)
        t = CITY[m.group(1)]; lo = int(m.group(2)); hi = int(m.group(3)) if m.group(3) else 999
        rs = team_games[t]
        hits = sum(1 for r in rs if lo <= r['pts'] - r['opp_pts'] <= hi)
        return (hits, len(rs), f'{t} games', f'{t} wins by {lo}-{hi if hi < 999 else "+"}', margins(rs))
    if etype == 'Overtime':
        rs = games_union(away, home)
        hits = sum(1 for r in rs if r['ot'])
        return (hits, len(rs), f'all {away} + {home} games', 'game goes to OT', '')
    if etype == '1st Half / Fulltime Result':
        m = re.match(r'^(.*) 1H / (.*) game$', cname)
        a, b = m.group(1), m.group(2)
        anchor = CITY.get(a) or CITY.get(b)
        rs = team_games[anchor]
        def res(r, who, per):
            me, op = period_pts(r, per), period_pts(r, per, True)
            if who == 'Tie': return me == op
            t = CITY[who]
            return (me > op) if t == anchor else (op > me)
        hits = sum(1 for r in rs if res(r, a, 'H1') and res(r, b, 'FG'))
        return (hits, len(rs), f'{anchor} games', f'{a} leads at half & {b} result', '')
    # --- period markets ---
    PER = {'First Quarter': 'Q1', 'Second Quarter': 'Q2', 'Third Quarter': 'Q3', 'Fourth Quarter': 'Q4',
           'First Half': 'H1', 'Second Half': 'H2'}
    base = etype.replace(' Spread', '').replace(' Total Points', '')
    if base in PER:
        per = PER[base]
        if etype.endswith('Total Points'):
            line = float(re.search(r'Over ([\d.]+) points', cname).group(1))
            rs = games_union(away, home)
            hits = sum(1 for r in rs if period_pts(r, per) + period_pts(r, per, True) > line)
            return (hits, len(rs), f'all {away} + {home} games', f'{per} total over {line}',
                    ', '.join(str(period_pts(r, per) + period_pts(r, per, True)) for r in rs))
        if etype.endswith('Spread'):
            m = re.match(r'^\S+ (?:Quarter|Half) (\w+) ([+-][\d.]+) points$', cname)
            t, sp = NICK[m.group(1)], float(m.group(2))
            rs = team_games[t]
            # Yes if margin + spread > 0  (e.g. -2.5 -> margin > 2.5 ; +1.5 -> margin > -1.5)
            hits = sum(1 for r in rs if period_pts(r, per) - period_pts(r, per, True) + sp > 0)
            return (hits, len(rs), f'{t} games', f'{t} {per} {sp:+}',
                    ', '.join(f'{period_pts(r, per) - period_pts(r, per, True):+d}' for r in rs))
        # winner
        if cname == 'Tie':
            rs = games_union(away, home)
            hits = sum(1 for r in rs if period_pts(r, per) == period_pts(r, per, True))
            return (hits, len(rs), f'all {away} + {home} games', f'{per} tied', '')
        t = TFIX.get(cname, cname)
        rs = team_games[t]
        hits = sum(1 for r in rs if period_pts(r, per) > period_pts(r, per, True))
        return (hits, len(rs), f'{t} games', f'{t} wins {per}',
                ', '.join(f'{period_pts(r, per)}-{period_pts(r, per, True)}' for r in rs))
    return None


def rec_str(rs):
    return ', '.join(f"W{r['w']} {'vs' if r['home'] else '@'}{r['opp']} {r['pts']}-{r['opp_pts']}" for r in rs)


def margins(rs):
    return ', '.join(f"{r['pts'] - r['opp_pts']:+d}" for r in rs)


rows = []
unhandled = collections.Counter()
for e in ev:
    game = game_of(e[1])
    if not game:
        continue
    et = ev_type(e)
    for c in e[4]:
        cname, ya, yb, na, last, trad, qst, desc = c[:8]
        row = {'game': f'{game[0]} @ {game[1]}', 'market': et, 'contract': cname, 'yes_ask': ya, 'yes_bid': yb,
               'no_ask': na, 'last': last, 'tradable': trad, 'quote_state': qst, 'description': desc,
               'source': c[8] if len(c) > 8 else 'Robinhood', 'book_lines': c[9] if len(c) > 9 else '', 'book_fair': c[10] if len(c) > 10 else ''}
        inband = ya is not None and 0.45 <= float(ya) <= 0.55
        row['in_band'] = inband
        if ya is not None:   # Wed Nov 4: hit rates for every priced line (the any-price view), not just 45-55c
            try:
                r = evaluate(et, cname, game)
            except Exception as ex:
                r = None
                unhandled[(et, 'ERR ' + str(ex)[:60])] += 1
            if r is None:
                unhandled[et] += 1
            else:
                hits, n, sample, cond, detail = r
                row.update({'hits': hits, 'n': n, 'hit_rate': rate(hits, n) if hits is not None else None,
                            'sample': sample, 'condition': cond, 'detail': detail})
        rows.append(row)

json.dump(rows, open(BASE + 'rows_w10.json', 'w'))
print('rows', len(rows), 'in band', sum(r['in_band'] for r in rows))
print('unhandled', unhandled)
ib = [r for r in rows if r['in_band']]
print('evaluated', sum(1 for r in ib if r.get('n')), 'not found', sum(1 for r in ib if 'n' in r and not r['n']))
print('pass >50%', sum(1 for r in ib if r.get('hit_rate') is not None and r['hit_rate'] > 0.5))
