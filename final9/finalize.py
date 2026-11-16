import json, re, csv
B = '/home/claude/wedger/final9/'
PL = json.load(open(B + 'plays.json')); EST = json.load(open(B + 'est.json')); FR = json.load(open(B + 'fresh.json'))
COND = {'Dallas Goedert': 'Only if Milton starts as announced.', 'Braelon Allen': 'Only if Breece Hall is active.', 'Harold Fannin': 'Only if Watson is active and starting.',
        'Josh Allen': 'Only if Dawkins plays.', 'CeeDee Lamb': 'Only in the Pickens-out branch.', 'Bryce Young': 'Stronger if C Corey Bullock is inactive.'}
ORDER = ['CIN@ATL', 'NYG@PHI', 'DEN@CAR', 'DET@MIA', 'NYJ@KC', 'CLE@NO', 'LA@WAS', 'DAL@IND', 'HOU@LAC', 'LV@SF', 'ARI@SEA', 'GB@NE', 'TB@CHI', 'BUF@MIN']
cards, rows = [], []
for g in ORDER:
    c = json.load(open(B + f'cards/{g}.json'))
    keep = []
    for p in c['plays']:
        i = [k for k, x in enumerate(PL) if x['game'] == g and x['player'].split(' ')[-1].lower() in p['line'].lower()][0]
        x = PL[i]; e = EST[i]
        _, sub, side, price, be, books, wedge, base, adj, lo, hi, edge, dec = e
        mid = base + adj
        p.update({'price': price, 'side': 'Yes' if side == 'Y' else 'No', 'be': be, 'payout': round(100 / price, 2), 'est': [lo, hi], 'books': books, 'wedge': wedge,
                  'base': base, 'adj': adj, 'decision': dec, 'ticker': x['ticker']})
        pers = next((v for k, v in COND.items() if k in p['line']), '')
        if dec == 'Final': p['cond'] = (pers + ' ' if pers else '') + f'Holds as a final line up to {lo - 2}¢.'
        elif dec == 'Lean': p['cond'] = (pers + ' ' if pers else '') + f'Becomes a final line at {lo - 2}¢ or less.'
        rows.append({'game': c['game'], 'decision': dec, 'line': p['line'], 'side': p['side'], 'price': price, 'payout': p['payout'], 'breakeven': be, 'books_fair': books,
                     'backtest': wedge, 'base': base, 'evidence_adj': adj, 'est_lo': lo, 'est_hi': hi, 'edge_mid': round(mid - be, 1), 'condition': p.get('cond', ''), 'ticker': x['ticker'],
                     'checked': FR['at'], 'result': '', 'grade_read': '', 'grade_price': ''})
        if dec == 'Pass':
            p['cond'] = f"A price of {round(mid) - 2}¢ or less makes it a lean." + (' ' + pers if pers else '')
            rows[-1]['condition'] = p['cond']
            c['passed'].insert(0, {'name': f"{p['line']} ({price}¢)", 'why': f"Our number ({lo}–{hi}%) doesn't clear the {be}% break-even after fees. " + p['why'],
                                   'move': f"A price of {round(mid) - 2}¢ or less makes it a lean." + (' ' + pers if pers else '')})
        else: keep.append(p)
    c['plays'] = sorted(keep, key=lambda p: (p['decision'] != 'Final', -((p['est'][0] + p['est'][1]) / 2 - p['be'])))
    c['likely'] = [re.sub(r'\s*\(~?\d+%[^)]*\)', '', s) for s in c['likely']]
    c['value'] = [f"{p['line']} at {p['price']}¢ (needs {p['be']}%, our number {p['est'][0]}–{p['est'][1]}%)" for p in c['plays']] or ['Nothing clears the hurdle at current prices.']
    json.dump(c, open(B + f'cards/{g}.json', 'w'), ensure_ascii=False, indent=1)
    cards.append(c)
json.dump({'at': FR['at'], 'books_at': '2026-11-07T23:47:21Z', 'rh_at': '2026-11-07T20:23:00Z', 'cards': cards}, open(B + 'final_w9.json', 'w'), ensure_ascii=False)
with open(B + 'final_w9.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows: print(f"{r['game']:10s} {r['decision']:5s} {r['line'][:50]:50s} {r['price']}¢ BE{r['breakeven']} est {r['est_lo']}-{r['est_hi']} | {r['condition']}")
print(sum(r['decision'] == 'Final' for r in rows), 'final', sum(r['decision'] == 'Lean' for r in rows), 'lean', sum(r['decision'] == 'Pass' for r in rows), 'pass')
