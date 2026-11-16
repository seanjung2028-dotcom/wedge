import json, csv

B = '/home/claude/wedger/rh/'
rows = json.load(open(B + 'rows_w8.json'))
from w8_build_inband_ko import KO as KO8

KO = {  # label, UTC
    'NE @ CHI': ('7:15 PM CT Thu', '2026-10-23T00:15:00Z'),
    'PIT @ NO': ('8:30 AM CT Sun', '2026-10-25T13:30:00Z'),
    'SF @ ATL': ('12:00 PM CT Sun', '2026-10-25T17:00:00Z'), 'CLE @ TEN': ('12:00 PM CT Sun', '2026-10-25T17:00:00Z'),
    'IND @ MIN': ('12:00 PM CT Sun', '2026-10-25T17:00:00Z'), 'MIA @ NYJ': ('12:00 PM CT Sun', '2026-10-25T17:00:00Z'),
    'TB @ CAR': ('12:00 PM CT Sun', '2026-10-25T17:00:00Z'), 'CIN @ BAL': ('12:00 PM CT Sun', '2026-10-25T17:00:00Z'),
    'NYG @ HOU': ('12:00 PM CT Sun', '2026-10-25T17:00:00Z'), 'DEN @ ARI': ('3:05 PM CT Sun', '2026-10-25T20:05:00Z'),
    'GB @ DET': ('3:25 PM CT Sun', '2026-10-25T20:25:00Z'), 'LAR @ LV': ('3:25 PM CT Sun', '2026-10-25T20:25:00Z'),
    'KC @ SEA': ('7:20 PM CT Sun', '2026-10-26T00:20:00Z'), 'DAL @ PHI': ('7:15 PM CT Mon', '2026-10-27T00:15:00Z'),
}

KO = KO8
out = []
for r in [r for r in rows if r['in_band']]:
    ya = float(r['yes_ask']); yb = float(r['yes_bid']) if r['yes_bid'] else None
    na = float(r['no_ask']) if r['no_ask'] else None
    book = r.get('source', 'Robinhood') != 'Robinhood'
    if book:
        na = 1 - ya
    flags = []
    if book: pass
    elif yb is None: flags.append('No bid')
    elif ya - yb > 0.05 + 1e-9: flags.append('Wide spread')
    n = r.get('n') or 0
    if 0 < n < 3: flags.append('Small sample')
    if n == 0: flags.append('No 2026 data')
    hr = r.get('hit_rate')
    out.append({'id': f'L{len(out) + 1:03d}', 'game': r['game'], 'kickoff': KO[r['game']][0], 'market': r['market'],
                'contract': r['contract'], 'yes_price': round(ya * 100), 'yes_bid': round(yb * 100) if yb is not None else '',
                'no_price': round(na * 100) if na is not None else '',
                'hits': r.get('hits') if r.get('hits') is not None else '', 'games': n,
                'hit_rate': round(hr * 100, 1) if hr is not None else '',
                'qualifies': 'Yes' if (hr is not None and hr > 0.5) else 'No', 'sample': r.get('sample', ''),
                'season_results': r.get('detail', ''), 'flags': '; '.join(flags), 'kickoff_utc': KO[r['game']][1],
                'source': 'Robinhood' if not book else 'Sportsbook avg', 'source_detail': r.get('source', '') if book else '',
                'book_lines': r.get('book_lines', ''),
                'book_fair': round(100 * float(r['book_fair']), 1) if r.get('book_fair') else ''})

with open(B + 'inband_w8.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

import collections
print('rows', len(out), 'qualifying', sum(o['qualifies'] == 'Yes' for o in out), collections.Counter(o['game'] for o in out if o['qualifies'] == 'Yes'))
