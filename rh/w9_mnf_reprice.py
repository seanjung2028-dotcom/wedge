"""Mon Nov 9 ~2:40-3:00 PM CT: re-price every BUF @ MIN row on the Week 9 board at Monday's prices.
Player props: Kalshi ladders (traded on Robinhood), pulled 2:39 PM CT. Game lines: Robinhood's own events, pulled 2:58 PM CT.
Finished games keep the rows they were posted with. Hit rates, samples and projections are unchanged (BUF and MIN haven't
played since); Wedge % on every repriced player prop is re-read from the v5.1 market shift at the new price, and the read
pick (Yes/No by 3+ points) is re-checked at the new price.
Writes rh/mnf9/{inband,lines_all,props_cat,atd}_w9.csv."""
import csv, json, math, os, re, unicodedata
B = '/home/claude/wedger/'; R = B + 'rh/'; O = R + 'mnf9/'; os.makedirs(O, exist_ok=True)
K = json.load(open(B + 'pull1109/kalshi_1109.json')); Q = K['q']
RH = json.load(open(B + 'pull1109/rh_1109.json'))
CAL5 = json.load(open(B + 'bt/cal_v51.json'))['cal_v5']
G5 = {'rec': 'rec', 'recyd': 'recyd', 'rushyd': 'rush', 'rryd': 'rush', 'td': 'td', 'passyd': 'passyd', 'passtd': 'passtd', 'int': 'int'}
def v5(price_c, stat):
    pp = min(max(price_c / 100, 0.01), 0.99); z = math.log(pp / (1 - pp)) + CAL5[G5[stat]]; return 100 / (1 + math.exp(-z))
def nn(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', s); return re.sub(r'[^a-z]', '', s)
CODE = {nn(v): k for k, v in K['names'].items() if not k[0].isdigit()}
SER = {'Receiving Yards': 'KXNFLRECYDS', 'Receptions': 'KXNFLREC', 'Rushing Yards': 'KXNFLRSHYDS', 'Passing Yards': 'KXNFLPASSYDS', 'Passing Touchdowns': 'KXNFLPASSTDS',
       'Rushing + Receiving Yards': 'KXNFLRRYDS', 'Anytime Touchdown': 'KXNFLTD', '2+ Touchdowns': 'KXNFLTD', '3+ Touchdowns': 'KXNFLTD'}
STAT = {'Receiving Yards': 'recyd', 'Receptions': 'rec', 'Rushing Yards': 'rushyd', 'Passing Yards': 'passyd', 'Passing Touchdowns': 'passtd', 'Rushing + Receiving Yards': 'rryd',
        'Anytime Touchdown': 'td', 'Interceptions': 'int'}
RHG = {}
for ev, rows in RH['events'].items():
    for nm, ya, yb, na, st in rows: RHG[nm] = (ya, yb, na)
ML = {'BUF': 'Buffalo wins', 'MIN': 'Minnesota wins'}
def quote(r):
    m, c = r['market'], r['contract']
    if m in ('Totals', 'Spreads', 'Overtime', '1st Half / Fulltime Result', 'Moneyline'):
        q = RHG.get(ML.get(c, c)) if m == 'Moneyline' else RHG.get(c)
        if not q: return None
        f = lambda x: round(100 * float(x)) if x not in ('', None) else ''
        return f(q[0]), f(q[1]), f(q[2]), 'Robinhood 2:58 PM CT'
    if m not in SER: return None
    nm = c.split(':')[0].strip(); code = CODE.get(nn(nm))
    if not code: return None
    if m in ('Anytime Touchdown', '2+ Touchdowns', '3+ Touchdowns'): k = {'Anytime Touchdown': 1, '2+ Touchdowns': 2, '3+ Touchdowns': 3}[m]
    else:
        mm = re.search(r'Over ([\d.]+)', c)
        if not mm: return None
        k = int(float(mm.group(1)) + 0.5)
    v = Q.get(f'{SER[m]}-26NOV09BUFMIN-{code}-{k}')
    if not v or v[3] != 'active': return None
    return round(100 * float(v[0])), round(100 * float(v[1])), round(100 * float(v[2])), 'Kalshi 2:39 PM CT'
stats = {}
for fn in ('inband_w9.csv', 'lines_all_w9.csv', 'props_cat_w9.csv', 'atd_w9.csv'):
    rows = list(csv.DictReader(open(R + fn))); cols = list(rows[0].keys()); n = hit = 0
    for r in rows:
        if r['game'] != 'BUF @ MIN': continue
        n += 1
        rr = dict(r)
        if fn == 'atd_w9.csv': rr['market'], rr['contract'] = 'Anytime Touchdown', r['player']
        q = quote(rr)
        if not q: continue
        hit += 1
        ya, yb, na, src = q
        r['yes_price'], r['yes_bid'] = ya, yb
        if 'no_price' in r: r['no_price'] = na
        if 'priced_at' in r: r['priced_at'] = '2026-11-09T20:39:49Z'
        st = r.get('sit_stat') or STAT.get(rr['market'])
        if st and st in G5 and ya not in ('', None) and 1 <= ya <= 99 and r.get('sit_hit', '') != '':
            P = v5(ya, st); r['sit_hit'] = round(P, 1); r['sit_edge'] = round(P - ya, 1)
            if fn != 'lines_all_w9.csv' or r['id'].startswith('AL'):
                r['sit_pick'], r['sit_pedge'] = '', ''
                nob = na if na not in ('', None) else (100 - yb if yb not in ('', None) else None)
                ey, en = P - ya, ((100 - P) - nob) if nob is not None else None
                if r.get('source', 'Robinhood') == 'Robinhood':
                    if ey >= 3: r['sit_pick'], r['sit_pedge'] = 'Yes', round(ey, 1)
                    elif en is not None and en >= 3: r['sit_pick'], r['sit_pedge'] = 'No', round(en, 1)
    with open(O + fn, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    stats[fn] = (n, hit)
print(stats)
for r in csv.DictReader(open(O + 'inband_w9.csv')):
    if r['game'] == 'BUF @ MIN' and r['sit_pick']: print('  pick', r['contract'], r['yes_price'], r['no_price'], r['sit_pick'], r['sit_pedge'])
