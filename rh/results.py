import json, csv, collections, re, unicodedata

B = '/home/claude/wedger/rh/'
settled = [r for r in json.load(open(B + 'settle_rows.json')) if r['in_band']]
lines = list(csv.DictReader(open(B + 'inband_v3.csv')))
props = {r['id']: r for r in csv.DictReader(open(B + 'props_cat_v3.csv'))}
w6 = json.load(open(B + 'espn_w6.json'))

# players who appeared in Week 6 but have no box-score line (ESPN game log) -> zero stats; others missing were inactive (contract voided)
PLAYED_NO_STATS = {'Cam Skattebo', 'Gunnar Helm'}

FULL = {'Moneyline', 'Spreads', 'Totals', 'Winning Margin', 'Overtime', '1st Half / Fulltime Result'}
def group(m):
    if m in FULL: return 'Full game'
    if re.search(r'Quarter|Half', m): return 'Quarters & halves'
    return 'Player props'

def bucket(hr):
    if hr == '': return ''
    hr = float(hr)
    if hr <= 50: return '50% or less'
    if hr < 60: return 'Over 50–59%'
    if hr < 75: return '60–74%'
    if hr < 100: return '75–99%'
    return '100%'

out = []
for s, l in zip(settled, lines):
    assert s['contract'] == l['contract'] and s['game'] == l['game']
    player = s['contract'].split(':')[0]
    if s.get('n') == 1:
        outcome = 'Won' if s['hits'] == 1 else 'Lost'
    elif player in PLAYED_NO_STATS:
        outcome = 'Lost'
    else:
        outcome = 'Void'
    price = int(l['yes_price'])
    profit = (100 - price) if outcome == 'Won' else (-price if outcome == 'Lost' else 0)
    p = props.get(l['id'])
    out.append({'id': l['id'], 'game': l['game'], 'market': l['market'], 'group': group(l['market']),
                'contract': l['contract'], 'yes_price': price, 'hit_rate': l['hit_rate'], 'hit_bucket': bucket(l['hit_rate']),
                'qualifies': l['qualifies'], 'flagged': 'Yes' if l['flags'] else 'No',
                'cat': p['cat'] if p else '', 'outcome': outcome, 'profit_c': profit,
                'week6_result': (s.get('detail') or '') if outcome != 'Void' else 'Did not play'})

# ---- Anytime TD filter picks (default filter: 3+ games, scored in >50%) ----
def norm(n):
    n = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode().lower().replace('.', '').replace("'", '').replace('-', ' ')
    n = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', n)
    return re.sub(r'\s+', ' ', n).strip()
td6 = collections.Counter(); appeared = set()
for gid, teams in w6['box'].items():
    for t in teams:
        for cat in ('rushing', 'receiving'):
            if cat in t['c']:
                L = t['c'][cat]['l']
                for pid, nm, st in t['c'][cat]['a']:
                    td6[norm(nm)] += float(st[L.index('TD')]); appeared.add(norm(nm))
        for cat, d in t['c'].items():
            for pid, nm, st in d['a']:
                appeared.add(norm(nm))
atd_rows = []
for r in csv.DictReader(open(B + 'atd_v3.csv')):
    if r['games'] and int(r['games']) >= 3 and r['atd_rate'] and float(r['atd_rate']) > 50 and r['yes_price']:
        k = norm(r['player'])
        outcome = 'Won' if td6[k] >= 1 else ('Lost' if k in appeared else 'Void')
        price = round(float(r['yes_price']))
        atd_rows.append({'id': 'ATD|' + r['id'], 'game': r['game'], 'market': 'Anytime Touchdown (ATD filter pick)',
                         'group': 'ATD filter picks', 'contract': r['player'], 'yes_price': price,
                         'hit_rate': r['atd_rate'], 'hit_bucket': bucket(r['atd_rate']), 'qualifies': 'Yes',
                         'flagged': 'Yes' if r['flags'] else 'No', 'cat': '', 'outcome': outcome,
                         'profit_c': (100 - price) if outcome == 'Won' else (-price if outcome == 'Lost' else 0),
                         'week6_result': f"{int(td6[k])} TD" if outcome != 'Void' else 'Did not play'})
out += atd_rows

with open(B + 'results_w6.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

def summ(rows, label):
    s = [r for r in rows if r['outcome'] != 'Void']
    wins = sum(r['outcome'] == 'Won' for r in s); cost = sum(r['yes_price'] for r in s); prof = sum(r['profit_c'] for r in s)
    avgp = cost / len(s) if s else 0
    print(f"{label:46} {wins:3}-{len(s) - wins:<3} win {100 * wins / len(s) if s else 0:5.1f}%  avg price {avgp:4.1f}¢  ROI {100 * prof / cost if cost else 0:+6.1f}%  void {len(rows) - len(s)}")

L = [r for r in out if r['group'] != 'ATD filter picks']
summ([r for r in L if r['qualifies'] == 'Yes'], 'Hit >50% (the screen)')
summ([r for r in L if r['qualifies'] == 'No'], 'Hit 50% or less (rest of 45-55c)')
summ(L, 'All 45-55c lines')
summ([r for r in L if r['qualifies'] == 'Yes' and r['flagged'] == 'No'], 'Hit >50%, unflagged')
for g in ('Full game', 'Quarters & halves', 'Player props'):
    summ([r for r in L if r['qualifies'] == 'Yes' and r['group'] == g], '  >50% · ' + g)
for b in ('Over 50–59%', '60–74%', '75–99%', '100%'):
    summ([r for r in L if r['hit_bucket'] == b], '  hit-rate bucket ' + b)
for c in ('1', '2', '3', '4'):
    summ([r for r in L if r['qualifies'] == 'Yes' and r['cat'] == c], '  >50% · category ' + c)
summ([r for r in L if r['qualifies'] == 'Yes' and r['cat'] in ('1', '2', '3', '4')], '  >50% · categories 1-4 combined')
summ(atd_rows, 'ATD filter picks (default filter)')
for r in atd_rows: print('   ', r['contract'], r['yes_price'], r['outcome'], r['week6_result'])
