import json, glob
B = '/home/claude/wedger/final9/'
PL = json.load(open(B + 'plays.json')); FR = json.load(open(B + 'fresh.json')); Q = {m[0]: m for m in FR['m']}
ORDER = ['CIN@ATL', 'NYG@PHI', 'DEN@CAR', 'DET@MIA', 'NYJ@KC', 'CLE@NO', 'LA@WAS', 'DAL@IND', 'HOU@LAC', 'LV@SF', 'ARI@SEA', 'GB@NE', 'TB@CHI', 'BUF@MIN']
cards = []; rows = []
for g in ORDER:
    c = json.load(open(B + f'cards/{g}.json'))
    for p in c['plays']:
        m = [x for x in PL if x['game'] == g and x['player'].split(' ')[-1].lower() in p['line'].lower()]
        if len(m) != 1: print('MATCH?', g, p['line'], len(m)); continue
        x = m[0]; q = Q[x['ticker']]
        price = round(100 * float(q[1] if x['side'] == 'Y' else q[3]))
        old = p['price']; p['price'] = price; p['ticker'] = x['ticker']; p['side'] = 'Yes' if x['side'] == 'Y' else 'No'
        p['be'] = price + 2; p['payout'] = round(100 / price, 2)
        lo, hi = p['est']; mid = (lo + hi) / 2
        want = 'Final' if lo >= p['be'] else ('Lean' if mid >= p['be'] else 'Pass')
        flag = '' if want == p['decision'] else f'  <-- rule says {want}'
        if old != price: flag += f'  (price {old}->{price})'
        print(f"{g:8s} {p['decision']:5s} {p['line'][:48]:48s} {p['side']:3s} {price}¢ BE{p['be']} est {lo}-{hi} edge {mid - p['be']:+.1f}{flag}")
        rows.append({'game': c['game'], 'decision': p['decision'], 'line': p['line'], 'side': p['side'], 'price': price, 'payout': p['payout'], 'be': p['be'], 'est_lo': lo, 'est_hi': hi, 'edge_mid': round(mid - p['be'], 1), 'cond': p.get('cond', ''), 'ticker': x['ticker'], 'checked': FR['at']})
    cards.append(c)
json.dump({'at': FR['at'], 'books_at': '2026-11-07T23:47:21Z', 'cards': cards}, open(B + 'final_w9.json', 'w'), ensure_ascii=False)
import csv
with open(B + 'final_w9.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows), sum(r['decision'] == 'Final' for r in rows), 'final', sum(r['decision'] == 'Lean' for r in rows), 'lean')
