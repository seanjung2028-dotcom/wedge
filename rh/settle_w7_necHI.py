"""Settle Week 7 games that have finished (NE @ CHI, Thu Oct 22: CHI 30, NE 24) for the results dataset.

Every NE @ CHI player prop and Anytime TD line on the Week 7 tables (Thursday prices), plus the full-game moneyline,
spread and total lines, settled from nflverse player stats. Rows go in with week = 7 and group 'Week 7 settled' so the
Wedger record and analyst standings pick them up; the Week 6 results views filter them out.
"""
import csv, json, re, collections
import pandas as pd
B = '/home/claude/wedger/rh/'
S = '/home/claude/wedger/dl5/stats_player_week_2026.csv'
GAME, AWAY, HOME, SA, SH = 'NE @ CHI', 'NE', 'CHI', 24, 30
FINAL = f'CHI {SH}, NE {SA}'
st = pd.read_csv(S, low_memory=False); st = st[(st['week'] == 7) & st['team'].isin([AWAY, HOME])]
norm = lambda s: re.sub(r'[^a-z]', '', str(s).lower().replace(' jr', '').replace(' iii', '').replace(' ii', ''))
P = {norm(r.player_display_name): r for r in st.itertuples(index=False)}
STAT = {'Receiving Yards': ('receiving_yards', 'rec yds'), 'Receptions': ('receptions', 'rec'), 'Rushing Yards': ('rushing_yards', 'rush yds'),
        'Passing Yards': ('passing_yards', 'pass yds'), 'Passing Touchdowns': ('passing_tds', 'pass TDs'), 'Interceptions': ('passing_interceptions', 'INTs'),
        'Rushing + Receiving Yards': ('rr', 'rush + rec yds')}
def val(r, col):
    if col == 'rr': return (r.rushing_yards or 0) + (r.receiving_yards or 0)
    v = getattr(r, col); return 0 if pd.isna(v) else v
rows = []
lines = list(csv.DictReader(open(B + 'inband_w7.csv'))) + list(csv.DictReader(open(B + 'props_cat_w7.csv')))
seen = set()
for r in lines:
    if r['game'] != GAME: continue
    key = (r['market'], r['contract'])
    if key in seen: continue
    seen.add(key)
    m, c, price = r['market'], r['contract'], int(float(r['yes_price']))
    outcome, detail = None, ''
    if m in STAT:
        mm = re.match(r'^(.*?): Over ([\d.]+) ', c)
        if not mm: continue
        p = P.get(norm(mm.group(1)))
        col, unit = STAT[m]
        if p is None: outcome, detail = 'Void', 'no stats recorded'
        else:
            v = val(p, col); outcome = 'Won' if v > float(mm.group(2)) else 'Lost'; detail = f'{int(v)} {unit}'
    elif m == 'Anytime Touchdown':
        p = P.get(norm(c))
        if p is None: outcome, detail = 'Void', 'no stats recorded'
        else:
            td = int((p.rushing_tds or 0) + (p.receiving_tds or 0)); outcome = 'Won' if td >= 1 else 'Lost'; detail = f'{td} TD'
    elif m in ('Moneyline', 'Spreads', 'Totals'):
        if m == 'Moneyline':
            team = c.replace(' wins', ''); won = (team.startswith('Chicago') and SH > SA) or (team.startswith('New England') and SA > SH)
        elif m == 'Spreads':
            mm = re.match(r'^(.*) wins by over ([\d.]+) points', c)
            if not mm: continue
            marg = SH - SA if mm.group(1).startswith('Chicago') else SA - SH
            won = marg > float(mm.group(2))
        else:
            mm = re.search(r'Over ([\d.]+)', c)
            if not mm: continue
            won = SA + SH > float(mm.group(1))
        outcome, detail = ('Won' if won else 'Lost'), FINAL
    else:
        continue
    profit = 0 if outcome == 'Void' else (100 - price if outcome == 'Won' else -price)
    rows.append({'id': f'W7S{len(rows) + 1:03d}', 'game': GAME, 'market': m, 'group': 'Week 7 settled', 'contract': c, 'yes_price': price,
                 'hit_rate': r.get('hit_rate', ''), 'hit_bucket': '', 'qualifies': r.get('qualifies', ''), 'flagged': '', 'cat': '',
                 'outcome': outcome, 'profit_c': profit, 'week6_result': f'W7: {detail}' + ('' if m in ('Moneyline', 'Spreads', 'Totals') else f' ({FINAL})'), 'week': 7})
# Anytime TD lines from the ATD table (keyed by player)
for r in csv.DictReader(open(B + 'atd_w7.csv')):
    if r['game'] != GAME or r['yes_price'] in ('', None) or ('Anytime Touchdown', r['player']) in seen: continue
    seen.add(('Anytime Touchdown', r['player']))
    p = P.get(norm(r['player'])); price = int(float(r['yes_price']))
    if p is None: outcome, detail = 'Void', 'no stats recorded'
    else:
        td = int((p.rushing_tds or 0) + (p.receiving_tds or 0)); outcome = 'Won' if td >= 1 else 'Lost'; detail = f'{td} TD'
    profit = 0 if outcome == 'Void' else (100 - price if outcome == 'Won' else -price)
    rows.append({'id': f'W7S{len(rows) + 1:03d}', 'game': GAME, 'market': 'Anytime Touchdown', 'group': 'Week 7 settled', 'contract': r['player'],
                 'yes_price': price, 'hit_rate': r.get('atd_rate', ''), 'hit_bucket': '', 'qualifies': '', 'flagged': '', 'cat': '',
                 'outcome': outcome, 'profit_c': profit, 'week6_result': f'W7: {detail} ({FINAL})', 'week': 7})
R = list(csv.DictReader(open(B + 'results_w6.csv'))); cols = list(R[0].keys())
with open(B + 'results_w6_w7.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(R); w.writerows(rows)
print('settled', len(rows), collections.Counter(r['outcome'] for r in rows))
# every NE @ CHI pick on the board should now be settled
picks = set(json.load(open(B + 'certs_live.json'))['picks'])
for v in json.load(open(B + 'analysts_live.json'))['picks'].values(): picks |= set(v)
have = {f"w7|{r['game']}|{r['market']}|{r['contract']}" for r in rows}
for k in sorted(p for p in picks if p.startswith('w7|NE @ CHI')):
    hit = next((r for r in rows if f"w7|{r['game']}|{r['market']}|{r['contract']}" == k), None)
    print('PICK', k, '->', (hit['outcome'], hit['yes_price'], hit['week6_result']) if hit else 'NOT SETTLED')
