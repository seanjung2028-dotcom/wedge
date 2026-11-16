import json, csv

B = '/home/claude/wedger/rh/'
rows = json.load(open(B + 'rows.json'))

KO = {  # label, UTC
    'HOU @ JAX': ('8:30 AM CT', '2026-10-18T13:30:00Z'),
    'CHI @ ATL': ('12:00 PM CT', '2026-10-18T17:00:00Z'), 'BAL @ CLE': ('12:00 PM CT', '2026-10-18T17:00:00Z'),
    'TEN @ IND': ('12:00 PM CT', '2026-10-18T17:00:00Z'), 'NYJ @ NE': ('12:00 PM CT', '2026-10-18T17:00:00Z'),
    'NO @ NYG': ('12:00 PM CT', '2026-10-18T17:00:00Z'), 'CAR @ PHI': ('12:00 PM CT', '2026-10-18T17:00:00Z'),
    'PIT @ TB': ('12:00 PM CT', '2026-10-18T17:00:00Z'), 'ARI @ LAR': ('3:05 PM CT', '2026-10-18T20:05:00Z'),
    'LAC @ KC': ('3:25 PM CT', '2026-10-18T20:25:00Z'), 'BUF @ LV': ('3:25 PM CT', '2026-10-18T20:25:00Z'),
    'DAL @ GB': ('7:20 PM CT', '2026-10-19T00:20:00Z'), 'WSH @ SF': ('7:15 PM CT Mon', '2026-10-20T00:15:00Z'),
}

out = []
for r in [r for r in rows if r['in_band']]:
    ya = float(r['yes_ask']); yb = float(r['yes_bid']) if r['yes_bid'] else None
    na = float(r['no_ask']) if r['no_ask'] else None
    flags = []
    if yb is None: flags.append('No bid')
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
                'season_results': r.get('detail', ''), 'flags': '; '.join(flags), 'kickoff_utc': KO[r['game']][1]})

with open(B + 'inband_v3.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

# the Sunday rows must be unchanged from the version already on the dashboard
old = {r['id']: r for r in csv.DictReader(open(B + 'inband_v2.csv'))}
diff = [o['id'] for o in out if o['id'] in old and any(str(o[k]) != old[o['id']][k] for k in ('game', 'contract', 'yes_price', 'hits', 'games', 'hit_rate', 'qualifies'))]
print('rows', len(out), 'old', len(old), 'changed Sunday rows', diff[:10], 'MNF', sum(1 for o in out if o['game'] == 'WSH @ SF'),
      'MNF qualifying', sum(1 for o in out if o['game'] == 'WSH @ SF' and o['qualifies'] == 'Yes'))
