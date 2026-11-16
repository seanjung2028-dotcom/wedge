"""Prices for certified / analyst picks that are not on the 45-55c lines or ATD tables (e.g. picked at 70c),
so the Analysts tab can show the price and later settle them. Price = Robinhood Yes ask at the site's latest refresh."""
import json, csv, re
B = '/home/claude/wedger/rh/'
PRICED = 'Sun Oct 25 ~11:56 AM CT'
picks = set(json.load(open(B + 'certs_live.json'))['picks'])
for v in json.load(open(B + 'analysts_live.json'))['picks'].values(): picks |= set(v)
have = {f"w7|{r['game']}|{r['market']}|{r['contract']}" for r in csv.DictReader(open(B + 'inband_w7.csv'))}
have |= {f"w7|{r['game']}|Anytime Touchdown|{r['player']}" for r in csv.DictReader(open(B + 'atd_w7.csv')) if r['yes_price']}
have |= {f"w{r['week']}|{r['game']}|{r['market']}|{r['contract']}" for r in csv.DictReader(open(B + 'results_w6_w7.csv')) if r['week'] != '7'}
ev = json.load(open(B + 'rh_events_w7.json'))
TEAM = {'PIT': 'Pittsburgh', 'NO': 'New Orleans', 'NYG': 'New York G', 'HOU': 'Houston', 'SF': 'San Francisco', 'ATL': 'Atlanta', 'TB': 'Tampa Bay', 'CAR': 'Carolina',
        'CLE': 'Cleveland', 'TEN': 'Tennessee', 'CIN': 'Cincinnati', 'BAL': 'Baltimore', 'MIA': 'Miami', 'NYJ': 'New York J', 'IND': 'Indianapolis', 'MIN': 'Minnesota',
        'DEN': 'Denver', 'ARI': 'Arizona', 'GB': 'Green Bay', 'DET': 'Detroit', 'LAR': 'Los Angeles R', 'LV': 'Las Vegas', 'KC': 'Kansas City', 'SEA': 'Seattle',
        'DAL': 'Dallas', 'PHI': 'Philadelphia', 'NE': 'New England', 'CHI': 'Chicago'}
out = []
for k in sorted(picks):
    if not k.startswith('w7|') or k in have: continue
    _, game, market, contract = k.split('|', 3)
    a, h = game.split(' @ '); title = f'{TEAM[a]} vs {TEAM[h]}: {market}'
    price = None
    for e in ev:
        if e[1] != title: continue
        for c in e[4]:
            if c[0] == contract and c[1] is not None: price = round(100 * float(c[1]))
    out.append({'key': k, 'week': 7, 'game': game, 'market': market, 'contract': contract, 'yes_price': price if price is not None else '', 'priced_at': PRICED})
    print(k, price)
with open(B + 'pick_prices_w7.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['key', 'week', 'game', 'market', 'contract', 'yes_price', 'priced_at']); w.writeheader(); w.writerows(out)
