"""Market-implied game total from Robinhood's game-total ladder: the point where the Over's mid price crosses 50%.
Adds game_total to the line tables (and writes game_totals_w8.json)."""
import json, re, csv, collections
B = '/home/claude/wedger/rh/'
rows = json.load(open(B + 'rows_w8.json'))
lad = collections.defaultdict(list)
for r in rows:
    if r['market'] != 'Totals': continue
    m = re.match(r'^Over ([\d.]+) points$', r['contract'])
    if not m: continue
    ya = float(r['yes_ask']) if r['yes_ask'] else None; yb = float(r['yes_bid']) if r['yes_bid'] else None
    mid = (ya + yb) / 2 if (ya is not None and yb is not None) else (ya if ya is not None else yb)
    if mid is None: continue
    lad[r['game']].append((float(m.group(1)), mid))
tot = {}
for g, pts in lad.items():
    pts.sort()
    est = None
    for (l0, p0), (l1, p1) in zip(pts, pts[1:]):
        if p0 >= 0.5 >= p1 and p0 != p1:
            est = l0 + (p0 - 0.5) / (p0 - p1) * (l1 - l0); break
    if est is None: continue
    tot[g] = round(est + 0.0, 1)
json.dump(tot, open(B + 'game_totals_w8.json', 'w'), indent=1)
print(sorted(tot.items(), key=lambda x: -x[1]))
for f in ('inband_w8.csv', 'props_cat_w8.csv', 'atd_w8.csv'):
    rs = list(csv.DictReader(open(B + f))); cols = [c for c in rs[0].keys() if c != 'game_total'] + ['game_total']
    for r in rs: r['game_total'] = tot.get(r['game'], '')
    w = csv.DictWriter(open(B + f, 'w', newline=''), fieldnames=cols); w.writeheader(); w.writerows(rs)
