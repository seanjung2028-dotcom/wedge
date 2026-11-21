"""The record file for Week 11: rh/results_w6_w10.csv (Weeks 6-10 through Sunday) plus Monday's LAC @ BAL board,
graded from the box score (bt/w10_settled_mon.csv), then Week 11 as games finish: Thursday's IND @ HOU board (bt/w11_settled.csv).
Writes rh/results_w6_w11.csv."""
import pandas as pd, csv, json
W = '/home/claude/wedger/'
R = list(csv.DictReader(open(W + 'rh/results_w6_w10.csv'))); cols = list(R[0].keys())
have = {(r['game'], r['market'], r['contract']) for r in R if r['week'] == '10'}
S = pd.read_csv(W + 'bt/w10_settled_mon.csv', low_memory=False, dtype=str, keep_default_na=False)
rows = []
for r in S.to_dict('records'):
    key = (r['game'], r['market'], r['contract'])
    if key in have: continue
    have.add(key)
    price = int(float(r['yes_price'])); out = r['outcome']
    profit = 0 if out == 'Void' else (100 - price if out == 'Won' else -price)
    rows.append({'id': f'W10M{len(rows) + 1:03d}', 'game': r['game'], 'market': r['market'], 'group': 'Week 10 settled', 'contract': r['contract'], 'yes_price': price,
                 'hit_rate': r.get('hit_rate', '') or r.get('atd_rate', ''), 'hit_bucket': '', 'qualifies': r.get('qualifies', ''), 'flagged': '', 'cat': '',
                 'outcome': out, 'profit_c': profit, 'week6_result': f"W10: {r['detail']}", 'week': 10})
have11 = set()
for src, tag in (('bt/w11_settled.csv', 'W11T'),):
    S = pd.read_csv(W + src, low_memory=False, dtype=str, keep_default_na=False); n0 = len(rows)
    for r in S.to_dict('records'):
        key = (r['game'], r['market'], r['contract'])
        if key in have11 or r['yes_price'] == '': continue
        have11.add(key)
        price = int(float(r['yes_price'])); out = r['outcome']
        profit = 0 if out == 'Void' else (100 - price if out == 'Won' else -price)
        rows.append({'id': f'{tag}{len(rows) - n0 + 1:03d}', 'game': r['game'], 'market': r['market'], 'group': 'Week 11 settled', 'contract': r['contract'], 'yes_price': price,
                     'hit_rate': r.get('hit_rate', '') or r.get('atd_rate', ''), 'hit_bucket': '', 'qualifies': r.get('qualifies', ''), 'flagged': '', 'cat': '',
                     'outcome': out, 'profit_c': profit, 'week6_result': f"W11: {r['detail']}", 'week': 11})
with open(W + 'rh/results_w6_w11.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(R); w.writerows(rows)
print(len(R), '+', len(rows), pd.Series([r['outcome'] for r in rows]).value_counts().to_dict(), 'net', sum(int(r['profit_c']) for r in rows))
certs = json.load(open(W + 'rh/certs_seed.json'))['picks']
keys = {f"w{r['week']}|{r['game']}|{r['market']}|{r['contract']}": r for r in R + rows}
got = [keys[k]['outcome'] for k in certs if k in keys]
print('certified record', got.count('Won'), '-', got.count('Lost'))
