"""Week 10 final lines -> Wedge's certified record. The card's finals (as posted before each kickoff), settled from the box score.
Brock Purdy is certified at 20+ (the line taken), not the 25+ the card moved to Sunday. A final that matches a settled board line
reuses that row (its board price); the rest become 'Other Wedge picks' rows at the card price."""
import csv, json, pandas as pd
W = '/home/claude/wedger/'
F = json.load(open(W + 'pull1115/sun_out/final_w10.json'))
st = pd.read_csv(W + 'dl20/stats_player_week_2026.csv', low_memory=False); st = st[(st.week == 10) & (st.season_type == 'REG')]
S = list(csv.DictReader(open(W + 'bt/w10_settled_sun.csv')))
have = {f"w10|{r['game']}|{r['market']}|{r['contract']}": r for r in S}
UNIT = {'rushing yards': ('Rushing Yards', 'Rush Yards', 'rushing_yards'), 'receiving yards': ('Receiving Yards', 'Receiving Yards', 'receiving_yards'), 'receptions': ('Receptions', 'Receptions', 'receptions')}
import re
fin = [(c['game'], p) for c in F['cards'] if c.get('status') != 'Final' for p in c['plays'] if p['decision'] == 'Final line']
OVR = {'Brock Purdy 25+ rushing yards (Yes)': ('Brock Purdy 20+ rushing yards (Yes)', 52)}   # taken at 20+ (Saturday's card line, 52¢)
rows, keys, log = [], [], []
for g, p in fin:
    line, price = p['line'], p['price']
    if line in OVR: line, price = OVR[line]
    m = re.match(r"(.+?) (under )?(\d+)\+? (rushing yards|receiving yards|receptions) \((Yes|No)\)", line)
    name, k, unit, side = m.group(1), int(m.group(3)), m.group(4), m.group(5)
    mkt, short, col = UNIT[unit]
    v = st[st.player_display_name == name]; actual = float(v.iloc[0][col]) if len(v) else None
    won = (actual >= k) if side == 'Yes' else (actual < k)
    contract = f"{name}: {'Over' if side == 'Yes' else 'Under'} {k - 0.5:g} {short}"
    key = f"w10|{g}|{mkt}|{contract}"
    if key in have:
        r0 = have[key]; keys.append(key); log.append((key, actual, r0['outcome'], 'board row', r0['yes_price'])); continue
    rows.append({'id': f'C10{len(rows) + 1:02d}', 'game': g, 'market': mkt, 'group': 'Other Wedge picks', 'contract': contract, 'yes_price': price, 'hit_rate': '', 'hit_bucket': '',
                 'qualifies': '', 'flagged': 'No', 'cat': 'Week 10 final line', 'outcome': 'Won' if won else 'Lost', 'profit_c': (100 - price) if won else -price,
                 'week6_result': f"W10:{actual:g}", 'week': 10})
    keys.append(key); log.append((key, actual, 'Won' if won else 'Lost', 'new row', price))
for x in log: print(x)
print(sum(x[2] == 'Won' for x in log), '-', sum(x[2] == 'Lost' for x in log))
cols = list(csv.DictReader(open(W + 'rh/results_w6_w9.csv')).fieldnames)
with open(W + 'certs10/rows_w10_finals.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
json.dump(keys, open(W + 'certs10/keys_w10_finals.json', 'w'), indent=1)
