import json, re, csv, itertools, collections, unicodedata

B = '/home/claude/wedger/rh/'
hist = json.load(open(B + 'hist_w1to5.json'))
espn = json.load(open(B + 'espn_thru6.json'))
games = json.load(open(B + 'w1to5_games.json'))  # [week, id, away, home, slugbase, date, kickoff]

CITY = {
    'Arizona': 'ARI', 'Los Angeles R': 'LAR', 'Baltimore': 'BAL', 'Cleveland': 'CLE', 'Buffalo': 'BUF',
    'Las Vegas': 'LV', 'Carolina': 'CAR', 'Philadelphia': 'PHI', 'Chicago': 'CHI', 'Atlanta': 'ATL',
    'Dallas': 'DAL', 'Green Bay': 'GB', 'Houston': 'HOU', 'Jacksonville': 'JAX', 'Los Angeles C': 'LAC',
    'Kansas City': 'KC', 'New Orleans': 'NO', 'New York G': 'NYG', 'New York J': 'NYJ', 'New England': 'NE',
    'Pittsburgh': 'PIT', 'Tampa Bay': 'TB', 'Tennessee': 'TEN', 'Indianapolis': 'IND', 'San Francisco': 'SF',
    'Washington': 'WSH', 'Minnesota': 'MIN', 'Miami': 'MIA', 'Cincinnati': 'CIN', 'Detroit': 'DET',
    'Denver': 'DEN', 'Seattle': 'SEA'}
TFIX = {'WAS': 'WSH', 'LA': 'LAR'}
MARKET = {'moneyline': 'Moneyline', 'spreads': 'Spread', 'totals': 'Total (over)', 'overtime': 'Overtime',
          'winning-margin': 'Winning margin', '1st-half-fulltime-result': '1st half / full time',
          'most-receiving-yards': 'Most receiving yards'}

gmap = {(g[4], g[5]): g for g in games}
gres = {g['id']: g for g in espn['games']}

def norm(n):
    n = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode().lower().replace('.', '').replace("'", '').replace('-', ' ')
    n = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', n)
    return re.sub(r'\s+', ' ', n).strip()

def team(name):
    name = name.strip()
    if name in CITY: return CITY[name]
    return TFIX.get(name, name)

# prices at kickoff for every contract, by game -> favorite
def price(px):
    # last real trade before kickoff (contracts never traded before kickoff have no real price -> excluded)
    return float(px[1]) if px and px[1] is not None else None

fav = {}
for slug, x in hist.items():
    if 'c' not in x: continue
    key = (x['g'], x['d'])
    f = fav.setdefault(key, {'ml': {}, 'wm': collections.Counter()})
    if x['f'] == 'moneyline':
        for cid, nm, px in x['c']:
            if price(px) is not None: f['ml'][team(nm)] = price(px)
    if x['f'] == 'winning-margin':
        for cid, nm, px in x['c']:
            m = re.match(r'^(.*?) (?:wins )?by ', nm)
            if m and price(px) is not None: f['wm'][team(m.group(1))] += price(px)

def favorite(key, away, home):
    f = fav.get(key, {})
    src = f.get('ml') if f.get('ml') and len(f['ml']) == 2 else f.get('wm')
    if not src or away not in src or home not in src or src[away] == src[home]: return None
    return away if src[away] > src[home] else home

rows = []
for slug, x in hist.items():
    if 'c' not in x: continue
    g = gmap[(x['g'], x['d'])]
    week, gid, away, home = g[0], g[1], g[2], g[3]
    r = gres[gid]
    pts = {r['h']['t']: r['h']['s'], r['a']['t']: r['a']['s']}
    ls = {r['h']['t']: r['h']['ls'], r['a']['t']: r['a']['ls']}
    ot = len(r['h']['ls']) > 4
    fv = favorite((x['g'], x['d']), away, home)
    box = espn['box'].get(gid, [])
    rec = {}
    for t in box:
        if 'receiving' in t['c']:
            L = t['c']['receiving']['l']
            for pid, nm, st in t['c']['receiving']['a']:
                rec[norm(nm)] = (t['t'], float(st[L.index('YDS')]))
    played = {norm(nm) for t in box for cat, dd in t['c'].items() for pid, nm, st in dd['a']}
    maxrec = max([v[1] for v in rec.values()] or [0])
    for cid, nm, px in x['c']:
        p = price(px)
        if p is None or not (0.45 <= p <= 0.55):
            continue
        fam = x['f']; tm = None; outcome = None
        if fam == 'moneyline':
            tm = team(nm); opp = home if tm == away else away
            outcome = pts[tm] > pts[opp]
        elif fam == 'spreads':
            m = re.match(r'^(.*) wins by over ([\d.]+) points$', nm); tm = team(m.group(1)); opp = home if tm == away else away
            outcome = pts[tm] - pts[opp] > float(m.group(2))
        elif fam == 'totals':
            outcome = pts[away] + pts[home] > float(re.match(r'^Over ([\d.]+) points$', nm).group(1))
        elif fam == 'overtime':
            outcome = ot
        elif fam == 'winning-margin':
            m = re.match(r'^(.*?) (?:wins )?by (\d+) (?:to (\d+)|or more)(?: points)?$', nm)
            if m:
                tm = team(m.group(1)); opp = home if tm == away else away
                lo = int(m.group(2)); hi = int(m.group(3)) if m.group(3) else 999
                outcome = lo <= pts[tm] - pts[opp] <= hi
            else:
                outcome = pts[away] == pts[home]
        elif fam == '1st-half-fulltime-result':
            if nm.endswith('Game ends in a tie'):
                a = re.match(r'^(.*?)(?: wins)? 1H / ', nm).group(1); b = 'Tie'
            else:
                m = re.match(r'^(.*?)(?: wins)? 1H / (.*?)(?: wins)? game$', nm); a, b = m.group(1), m.group(2)
            h1 = {t: sum(ls[t][:2]) for t in ls}
            def res(who, per):
                if per == 'H1':
                    if who == 'Tie': return h1[away] == h1[home]
                    t = team(who); o = home if t == away else away
                    return h1[t] > h1[o]
                if who == 'Tie': return pts[away] == pts[home]
                t = team(who); o = home if t == away else away
                return pts[t] > pts[o]
            outcome = res(a, 'H1') and res(b, 'FG')
            tm = team(b) if b != 'Tie' else None
        elif fam == 'most-receiving-yards':
            k = norm(nm)
            if k in rec:
                tm = rec[k][0]; outcome = rec[k][1] >= maxrec and maxrec > 0
            elif k in played:
                outcome = False
            else:
                outcome = None  # did not play -> void
        side = 'n/a' if tm is None else ('Pick\'em' if fv is None else ('Favorite' if tm == fv else 'Underdog'))
        venue = 'n/a' if tm is None else ('Home' if tm == home else 'Away')
        c = round(p * 100)
        band = '45–48¢' if c <= 48 else ('49–51¢' if c <= 51 else '52–55¢')
        v = px[3] or 0
        fresh = 'Under 1k contracts' if v < 1000 else ('1k–50k contracts' if v < 50000 else '50k+ contracts')
        res_ = 'Void' if outcome is None else ('Won' if outcome else 'Lost')
        rows.append({'id': cid, 'week': f'Week {week}', 'game': f'{away} @ {home}', 'market': MARKET[fam], 'contract': nm,
                     'price_c': c, 'side': side, 'venue': venue, 'price_band': band, 'liquidity': fresh,
                     'team': tm or '', 'outcome': res_, 'profit_c': (100 - c) if res_ == 'Won' else (-c if res_ == 'Lost' else 0),
                     'final': f"{away} {pts[away]} – {home} {pts[home]}{' (OT)' if ot else ''}",
                     'last_trade_utc': px[2] or '', 'volume_3d': px[3]})

with open(B + 'hist_lines.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

# ---- every combination of factors ----
DIMS = ['market', 'side', 'venue', 'price_band', 'week', 'liquidity']
LABEL = {'market': 'Market', 'side': 'Fav/Dog', 'venue': 'Home/Away', 'price_band': 'Price band', 'week': 'Week', 'liquidity': 'Liquidity'}
settled = [r for r in rows if r['outcome'] != 'Void']
perms = []
for k in range(0, len(DIMS) + 1):
    for combo in itertools.combinations(DIMS, k):
        groups = collections.defaultdict(list)
        for r in settled:
            groups[tuple(r[d] for d in combo)].append(r)
        for key, rs in groups.items():
            n = len(rs); wins = sum(r['outcome'] == 'Won' for r in rs)
            cost = sum(r['price_c'] for r in rs); prof = sum(r['profit_c'] for r in rs)
            row = {'grouping': '+'.join(combo) if combo else 'all'}
            for d in DIMS:
                row[d] = key[combo.index(d)] if d in combo else ''
            hit = 100 * wins / n
            row.update({'n': n, 'wins': wins, 'losses': n - wins, 'hit_pct': round(hit, 1),
                        'avg_price': round(cost / n, 1), 'edge_pts': round(hit - cost / n, 1),
                        'roi_pct': round(100 * prof / cost, 1)})
            row['id'] = row['grouping'] + '|' + '|'.join(row[d] for d in DIMS)
            perms.append(row)
cols = ['id', 'grouping'] + DIMS + ['n', 'wins', 'losses', 'hit_pct', 'avg_price', 'edge_pts', 'roi_pct']
with open(B + 'hist_perms.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(perms)

print('lines', len(rows), 'void', sum(r['outcome'] == 'Void' for r in rows), 'perm rows', len(perms), 'groupings', len({p['grouping'] for p in perms}))
show = lambda grp: [print(f"  {' / '.join(p[d] for d in DIMS if p[d]) or 'ALL':60} {p['wins']:3}-{p['losses']:<3} {p['hit_pct']:5}%  avg {p['avg_price']}¢  ROI {p['roi_pct']:+}%") for p in sorted([p for p in perms if p['grouping'] == grp], key=lambda p: -p['n'])]
for grp in ['all', 'market', 'side', 'venue', 'price_band', 'week', 'liquidity', 'market+side', 'market+price_band']:
    print(grp); show(grp)
