"""Per-game reads, Week 9 (mirror of the page's lobby game tabs; kept for settling). For each game: Robinhood's own player
props, the better side priced 25-75c, Wedge % beating that price by 3+ pts, players listed Questionable/Doubtful left out.
Ranked by Kelly growth (expected log growth at the Kelly stake: how far Wedge % clears the price, weighed by the chance it
hits), one line per player per stat family (rushing, receiving, passing), two per player, six per game. Writes game_reads_w12.csv."""
import csv, math, re
B = '/home/claude/wedger/rh/'
rows = list(csv.DictReader(open(B + 'lines_all_w12.csv')))
FAM = {'rushyd': 'rush', 'rryd': 'rush', 'recyd': 'recv', 'rec': 'recv', 'passyd': 'pass', 'passtd': 'pass'}   # one line per player per stat family
INJ = re.compile(r'Questionable|Doubtful|Out\b|Inactive|No bid', re.I)
def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None
def best(r):
    p = num(r['sit_hit']); y = num(r['yes_price'])
    if p is None or y is None: return None
    n = num(r['no_price'])
    if n is None and num(r['yes_bid']) is not None: n = 100 - num(r['yes_bid'])
    out = None
    for side, q, ps in (('Yes', y, p), ('No', n, 100 - p)):
        if q is None or not 25 <= q <= 75 or ps - q < 3: continue
        P, Q = ps / 100, q / 100
        g = P * math.log(P / Q) + (1 - P) * math.log((1 - P) / (1 - Q))
        if not out or g > out['g']: out = {'side': side, 'q': q, 'p': ps, 'edge': ps - q, 'g': g}
    return out
by = {}
for r in rows:
    if r['source'] != 'Robinhood' or INJ.search(r['flags'] or ''): continue
    b = best(r)
    if b: by.setdefault(r['game'], []).append((b, r))
res = []
for game, L in by.items():
    L.sort(key=lambda t: (-t[0]['g'], -t[0]['edge'], t[1]['contract']))
    seen, per, top = set(), {}, []
    for b, r in L:
        pl = r['contract'].split(':')[0]
        k = (pl, FAM.get(r['sit_stat'], r['sit_stat']))
        if k in seen or per.get(pl, 0) >= 2: continue
        seen.add(k); per[pl] = per.get(pl, 0) + 1; top.append((b, r))
        if len(top) == 6: break
    for i, (b, r) in enumerate(top, 1):
        res.append({'game': game, 'rank': i, 'id': r['id'], 'contract': r['contract'], 'market': r['market'], 'side': b['side'], 'price': round(b['q']),
                    'wedge_pct': round(b['p'], 1), 'edge': round(b['edge'], 1), 'kelly_growth': round(b['g'], 5), 'in_tested_range': 40 <= b['q'] <= 60,
                    'has_outlook': bool(r['sit_key'])})
with open(B + 'game_reads_w12.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(res[0].keys())); w.writeheader(); w.writerows(res)
if __name__ == '__main__':
    import collections
    print('games', len(by), 'reads', len(res), collections.Counter(x['game'] for x in res))
    print('no outlook', [x['contract'] for x in res if not x['has_outlook']])
    print('outside 40-60', sum(1 for x in res if not x['in_tested_range']))
    for x in res:
        if x['game'] in ('JAX @ BAL', 'ARI @ SEA', 'CLE @ NO'): print(x['game'], x['rank'], x['contract'], x['side'], x['price'], x['wedge_pct'], x['edge'], x['kelly_growth'])
