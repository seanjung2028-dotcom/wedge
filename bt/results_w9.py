"""Append every settled Week 9 posted line (Thursday JAX @ BAL and Sunday; BUF @ MIN once final) and the certified Week 9 picks that
aren't on the posted board -> rh/results_w6_w9.csv."""
import pandas as pd, csv, json, re
W = '/home/claude/wedger/'
S = pd.read_csv(W + 'bt/w9_settled.csv', low_memory=False, dtype=str, keep_default_na=False)
R = list(csv.DictReader(open(W + 'rh/results_w6_w8.csv'))); cols = list(R[0].keys())
rows = []; seen = set()
for r in S.to_dict('records'):
    key = (r['game'], r['market'], r['contract'])
    if key in seen: continue
    seen.add(key)
    price = int(float(r['yes_price'])); out = r['outcome']
    profit = 0 if out == 'Void' else (100 - price if out == 'Won' else -price)
    rows.append({'id': f'W9S{len(rows) + 1:03d}', 'game': r['game'], 'market': r['market'], 'group': 'Week 9 settled', 'contract': r['contract'], 'yes_price': price,
                 'hit_rate': r.get('hit_rate', '') or r.get('atd_rate', ''), 'hit_bucket': '', 'qualifies': r.get('qualifies', ''), 'flagged': '', 'cat': '',
                 'outcome': out, 'profit_c': profit, 'week6_result': f"W9: {r['detail']}", 'week': 9})
# certified Week 9 picks that aren't on the posted board: price from the every-line board they were picked from
certs = json.load(open(W + 'dbsnap1109/wedger/certs.json'))['picks']
LA = {}
for fn in ('rh/lines_all_w9.csv', 'pull1104/wed_out/lines_all_w9.csv'):
    for r in csv.DictReader(open(W + fn)): LA.setdefault((r['game'], r['market'], r['contract']), r)
st = pd.read_csv(W + 'dl18/stats_player_week_2026.csv', low_memory=False); st = st[(st.week == 9) & (st.season_type == 'REG')]
COL = {'Receiving Yards': ('receiving_yards', 'rec yds'), 'Receptions': ('receptions', 'rec'), 'Rushing Yards': ('rushing_yards', 'rush yds')}
have = {(r['game'], r['market'], r['contract']) for r in rows}
for k in certs:
    wk, g, m, c = k.split('|')
    if wk != 'w9' or (g, m, c) in have: continue
    nm = c.split(':')[0]; p = st[st.player_display_name == nm]
    if not len(p): print('no stats', k); continue
    p = p.iloc[0]
    if m == 'Anytime Touchdown': v = int(p.rushing_tds + p.receiving_tds); won = v >= 1; det = f'{v} TD'
    else:
        line = float(re.search(r'Over ([\d.]+)', c).group(1)); col, unit = COL[m]; v = float(p[col]); won = v > line; det = f'{v:g} {unit}'
    src = LA.get((g, m, c)); price = int(src['yes_price']) if src and src['yes_price'] else ''
    rows.append({'id': f'W9S{len(rows) + 1:03d}', 'game': g, 'market': m, 'group': 'Week 9 settled (pick)', 'contract': c, 'yes_price': price, 'hit_rate': '', 'hit_bucket': '', 'qualifies': '',
                 'flagged': '', 'cat': '', 'outcome': 'Won' if won else 'Lost', 'profit_c': '' if price == '' else (100 - price if won else -price), 'week6_result': f'W9: {det}', 'week': 9})
    print('pick row', k, rows[-1]['outcome'], price, det)
with open(W + 'rh/results_w6_w9.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(R); w.writerows(rows)
print(len(R), '+', len(rows), pd.Series([r['outcome'] for r in rows]).value_counts().to_dict())
keys = {f"w{r['week']}|{r['game']}|{r['market']}|{r['contract']}": r for r in R + rows}
got = [(k, keys[k]['outcome']) for k in certs if k in keys]; miss = [k for k in certs if k not in keys]
won = sum(o == 'Won' for _, o in got); lost = sum(o == 'Lost' for _, o in got)
print('certified record', won, '-', lost, 'missing', miss)
for k in certs:
    if k.startswith('w9'): print('  ', k, keys.get(k, {}).get('outcome'), keys.get(k, {}).get('yes_price'), keys.get(k, {}).get('week6_result'))
