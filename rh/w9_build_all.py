"""Every Week 9 line at any price (the Lines tab's "Every line, any price" view), Wed Nov 4.
In-band (45-55c) rows carry the full model columns from inband_w9.csv (Wedge %, pick, outlook key). Every other player
prop gets Wedge % from the v5.1 market shift alone (fit on lines priced 40-60c, so it is a rough guide far from 50c) and no
pick; game lines show the books' fair price. Writes lines_all_w9.csv; run after w9_model.py, before w9_injflags.py."""
import json, csv, math, re
B = '/home/claude/wedger/rh/'
from w9_build_inband_ko import KO
rows = json.load(open(B + 'rows_w9.json'))
inb = {(r['game'], r['market'], r['contract']): r for r in csv.DictReader(open(B + 'inband_w9.csv'))}
cand = {(r['game'], r['market'], r['contract']): r for r in csv.DictReader(open(B + 'reads_cand_w9.csv'))}   # per-game read candidates: full model columns, no pick
cols = list(next(iter(inb.values())).keys())
CAL = json.load(open('/home/claude/wedger/bt/cal_v51.json'))['cal_v5']
STAT = {'Receiving Yards': 'recyd', 'Receptions': 'rec', 'Rushing Yards': 'rushyd', 'Rushing + Receiving Yards': 'rryd',
        'Passing Yards': 'passyd', 'Passing Touchdowns': 'passtd', 'Interceptions': 'int', 'Anytime Touchdown': 'td'}
G = {'recyd': 'recyd', 'rec': 'rec', 'rushyd': 'rush', 'rryd': 'rush', 'passyd': 'passyd', 'passtd': 'passtd', 'int': 'int', 'td': 'td'}
role = {}
for fn in ('inband_w9.csv', 'props_cat_w9.csv', 'proj_w9.csv'):
    for r in csv.DictReader(open(B + fn)):
        nm = r.get('player') or (r['contract'].split(':')[0] if ':' in r['contract'] else r['contract'])
        if r.get('role'): role.setdefault((r['game'], nm), r['role'])
out = []
for r in rows:
    if r['yes_ask'] is None: continue
    if r['contract'].startswith('#'): continue
    key = (r['game'], r['market'], r['contract'])
    if key in inb:
        o = dict(inb[key]); o['id'] = 'A' + o['id']; out.append(o); continue
    ya = float(r['yes_ask']); yb = float(r['yes_bid']) if r['yes_bid'] else None
    na = float(r['no_ask']) if r['no_ask'] else None
    book = r.get('source', 'Robinhood') != 'Robinhood'
    if book: na = 1 - ya
    flags = []
    if not book:
        if yb is None: flags.append('No bid')
        elif ya - yb > 0.05 + 1e-9: flags.append('Wide spread')
    n = r.get('n') or 0
    if 0 < n < 3: flags.append('Small sample')
    hr = r.get('hit_rate')
    o = {c: '' for c in cols}
    o.update({'id': f'A{len(out) + 1:04d}', 'game': r['game'], 'kickoff': KO[r['game']][0], 'market': r['market'], 'contract': r['contract'],
              'yes_price': round(ya * 100), 'yes_bid': round(yb * 100) if yb is not None else '', 'no_price': round(na * 100) if na is not None else '',
              'hits': r.get('hits') if r.get('hits') is not None else '', 'games': n, 'hit_rate': round(hr * 100, 1) if hr is not None else '',
              'qualifies': 'Yes' if (hr is not None and hr > 0.5) else 'No', 'sample': r.get('sample', '') or '',
              'season_results': r.get('detail', '') or '', 'flags': '; '.join(flags), 'kickoff_utc': KO[r['game']][1],
              'source': 'Robinhood' if not book else 'Sportsbook avg', 'source_detail': '',
              'book_fair': round(100 * float(r['book_fair']), 1) if r.get('book_fair') else ''})
    st = STAT.get(r['market'])
    if st and 0.01 <= ya <= 0.99:
        z = math.log(ya / (1 - ya)) + CAL[G[st]]
        p = 100 / (1 + math.exp(-z)); o['sit_hit'] = round(p, 1); o['sit_stat'] = st; o['sit_edge'] = round(p - 100 * ya, 1)
    nm = r['contract'].split(':')[0] if ':' in r['contract'] else r['contract']
    o['role'] = role.get((r['game'], nm), '')
    c = cand.get(key)
    if c and c.get('sit_key'):
        for k in cols:
            if (k.startswith('sit_') or k.startswith('mom_') or k == 'role') and c.get(k) not in (None, ''): o[k] = c[k]
        o['sit_pick'] = ''; o['sit_pedge'] = ''
    out.append(o)
with open(B + 'lines_all_w9.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)
import collections
print('every line', len(out), 'in band', sum(1 for o in out if o['id'].startswith('AL')), collections.Counter(o['source'] for o in out))
