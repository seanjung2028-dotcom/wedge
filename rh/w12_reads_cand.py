"""Per-game reads (Wed Nov 4): Robinhood player props outside the 45-55c table whose better side, priced 25-75c, beats its
price by 3+ pts on Wedge % (v6: market mid + backtested matchup lens). w12_model.py gives these the full outlook, so every per-game read card opens
its read. Writes reads_cand_w12.csv (inband_w12.csv columns). Run after w12_build_inband / before w12_model."""
import json, csv, math
B = '/home/claude/wedger/rh/'
from w12_build_inband_ko import KO
rows = json.load(open(B + 'rows_w12.json'))
inb = list(csv.DictReader(open(B + 'inband_w12.csv')))
cols = list(inb[0].keys()); inkeys = {(r['game'], r['market'], r['contract']) for r in inb}
CAL = json.load(open('/home/claude/wedger/bt/cal_v51.json'))['cal_v5']
import sys as _s; _s.path.insert(0, '/home/claude/wedger/lens'); import v6 as V6
STAT = {'Receiving Yards': 'recyd', 'Receptions': 'rec', 'Rushing Yards': 'rushyd', 'Rushing + Receiving Yards': 'rryd',
        'Passing Yards': 'passyd', 'Passing Touchdowns': 'passtd', 'Interceptions': 'int', 'Anytime Touchdown': 'td'}
G = {'recyd': 'recyd', 'rec': 'rec', 'rushyd': 'rush', 'rryd': 'rush', 'passyd': 'passyd', 'passtd': 'passtd', 'int': 'int', 'td': 'td'}
out = []
for r in rows:
    if r.get('source', 'Robinhood') != 'Robinhood' or r['yes_ask'] in (None, '') or r['contract'].startswith('#'): continue
    st = STAT.get(r['market'])
    if not st or st == 'td' or (r['game'], r['market'], r['contract']) in inkeys: continue
    ya = round(float(r['yes_ask']) * 100); yb = round(float(r['yes_bid']) * 100) if r['yes_bid'] not in (None, '') else None
    na = round(float(r['no_ask']) * 100) if r['no_ask'] not in (None, '') else (100 - yb if yb is not None else None)
    if not 1 <= ya <= 99: continue
    p = V6.detail_game(r['contract'].split(':')[0].strip(), r['game'], st, V6.line_of(r['contract']), (ya + yb) / 2 if yb else ya - 1)['p']
    ok = (25 <= ya <= 75 and p - ya >= 3) or (na is not None and 25 <= na <= 75 and (100 - p) - na >= 3)
    if not ok: continue
    o = {c: '' for c in cols}
    o.update({'id': f'R{len(out) + 1:03d}', 'game': r['game'], 'kickoff': KO[r['game']][0], 'kickoff_utc': KO[r['game']][1], 'market': r['market'],
              'contract': r['contract'], 'yes_price': ya, 'yes_bid': yb if yb is not None else '', 'no_price': na if na is not None else '',
              'source': 'Robinhood', 'book_fair': round(100 * float(r['book_fair']), 1) if r.get('book_fair') else ''})
    out.append(o)
with open(B + 'reads_cand_w12.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)
print('read candidates', len(out))
