"""Append every settled Week 10 posted line (Thursday WSH @ NYG so far) -> rh/results_w6_w10.csv. Certified Week 10 picks are graded when settled."""
import pandas as pd, csv, json, re, sys
W = '/home/claude/wedger/'
S = pd.concat([pd.read_csv(W + 'bt/w10_settled.csv', low_memory=False, dtype=str, keep_default_na=False),   # Thursday WSH @ NYG
               pd.read_csv(W + 'bt/w10_settled_sun.csv', low_memory=False, dtype=str, keep_default_na=False)], ignore_index=True)   # Sunday
R = list(csv.DictReader(open(W + 'rh/results_w6_w9.csv'))); cols = list(R[0].keys())
rows = []; seen = set()
for r in S.to_dict('records'):
    key = (r['game'], r['market'], r['contract'])
    if key in seen: continue
    seen.add(key)
    price = int(float(r['yes_price'])); out = r['outcome']
    profit = 0 if out == 'Void' else (100 - price if out == 'Won' else -price)
    rows.append({'id': f'W10S{len(rows) + 1:03d}', 'game': r['game'], 'market': r['market'], 'group': 'Week 10 settled', 'contract': r['contract'], 'yes_price': price,
                 'hit_rate': r.get('hit_rate', '') or r.get('atd_rate', ''), 'hit_bucket': '', 'qualifies': r.get('qualifies', ''), 'flagged': '', 'cat': '',
                 'outcome': out, 'profit_c': profit, 'week6_result': f"W10: {r['detail']}", 'week': 10})
certs = json.load(open(sys.argv[1] if len(sys.argv) > 1 else W + 'rh/certs_seed.json'))['picks']
have = {(r['game'], r['market'], r['contract']) for r in rows}
for k in certs:
    wk, g, m, c = k.split('|')
    if wk == 'w10' and (g, m, c) not in have: print('cert not on board (own row):', k)
with open(W + 'rh/results_w6_w10.csv', 'w', newline='') as f:
    PL = list(csv.DictReader(open(W + 'picklog/rows_nov8_12.csv')))  # user's Nov 8-12 pick log, verified against box scores
    PL += list(csv.DictReader(open(W + 'certs10/rows_w10_finals.csv')))  # Week 10 final lines not on the settled board
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(R); w.writerows(rows); w.writerows(PL)
print(len(R), '+', len(rows), pd.Series([r['outcome'] for r in rows]).value_counts().to_dict(), 'net', sum(int(r['profit_c']) for r in rows))
keys = {f"w{r['week']}|{r['game']}|{r['market']}|{r['contract']}": r for r in R + rows}
got = [(k, keys[k]['outcome']) for k in certs if k in keys]
print('certified record', sum(o == 'Won' for _, o in got), '-', sum(o == 'Lost' for _, o in got), 'w10 certs:', [k for k in certs if k.startswith('w10')])
