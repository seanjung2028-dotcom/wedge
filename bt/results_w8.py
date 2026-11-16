"""Append every settled Week 8 posted line (and certified Week 8 picks) to the results dataset -> rh/results_w6_w8.csv."""
import pandas as pd, csv, json, re
W = '/home/claude/wedger/'
S = pd.read_csv(W + 'bt/w8_settled.csv', low_memory=False, dtype=str, keep_default_na=False)
R = list(csv.DictReader(open(W + 'rh/results_w6_w7.csv'))); cols = list(R[0].keys())
FULL = {'Moneyline', 'Spreads', 'Totals', '1st Half / Fulltime Result'}
CITY = {'ARI': 'Arizona', 'DAL': 'Dallas'}
rows = []; seen = set()
for r in S.to_dict('records'):
    key = (r['game'], r['market'], r['contract'])
    if key in seen: continue
    seen.add(key)
    price = int(float(r['yes_price'])); out = r['outcome']
    profit = 0 if out == 'Void' else (100 - price if out == 'Won' else -price)
    contract = r['contract']
    if r['market'] == 'Moneyline': contract = contract  # team code as posted
    rows.append({'id': f'W8S{len(rows) + 1:03d}', 'game': r['game'], 'market': r['market'], 'group': 'Week 8 settled', 'contract': contract, 'yes_price': price,
                 'hit_rate': r.get('hit_rate', '') or r.get('atd_rate', ''), 'hit_bucket': '', 'qualifies': r.get('qualifies', ''), 'flagged': '', 'cat': '',
                 'outcome': out, 'profit_c': profit, 'week6_result': f"W8: {r['detail']}", 'week': 8})
# certified Week 8 picks that are not on the posted board (line moved after the pick)
st = pd.read_csv(W + 'dl8/stats_player_week_2026.csv', low_memory=False); st = st[st.week == 8]
j = st[st.player_display_name == 'Josh Jacobs'].iloc[0]
rows.append({'id': f'W8S{len(rows) + 1:03d}', 'game': 'CAR @ GB', 'market': 'Receiving Yards', 'group': 'Week 8 settled (pick)', 'contract': 'Josh Jacobs: Over 14.5 Receiving Yards',
             'yes_price': '', 'hit_rate': '', 'hit_bucket': '', 'qualifies': '', 'flagged': '', 'cat': '',
             'outcome': 'Won' if float(j.receiving_yards) > 14.5 else 'Lost', 'profit_c': '', 'week6_result': f"W8: {int(j.receiving_yards)} rec yds", 'week': 8})
with open(W + 'rh/results_w6_w8.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(R); w.writerows(rows)
print(len(R), '+', len(rows), pd.Series([r['outcome'] for r in rows]).value_counts().to_dict(), rows[-1])
