"""Settle every Week 7 game that has finished, for the results dataset.

Scores from nflverse games.csv; player stats from nflverse stats_player_week_2026.csv (dl8, pulled Tue Oct 27).
Settles each finished game's player props and Anytime TD lines on the Week 7 tables (at their last pregame prices),
full-game moneylines, spreads and totals, plus analyst / certified picks priced off the 45-55c board (pick_prices).
Quarter and half markets are not settled (no period scores in the feed). Rows go in with week = 7.
"""
import csv, json, re, collections, os
import pandas as pd
B = '/home/claude/wedger/rh/'
D7 = '/home/claude/wedger/dl8/'
norm = lambda s: re.sub(r'[^a-z]', '', re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', str(s).lower()))
TO_SITE = {'LA': 'LAR'}
CITY = {'ARI': 'Arizona', 'ATL': 'Atlanta', 'BAL': 'Baltimore', 'BUF': 'Buffalo', 'CAR': 'Carolina', 'CHI': 'Chicago', 'CIN': 'Cincinnati', 'CLE': 'Cleveland',
        'DAL': 'Dallas', 'DEN': 'Denver', 'DET': 'Detroit', 'GB': 'Green Bay', 'HOU': 'Houston', 'IND': 'Indianapolis', 'JAX': 'Jacksonville', 'KC': 'Kansas City',
        'LAR': 'Los Angeles R', 'LAC': 'Los Angeles C', 'LV': 'Las Vegas', 'MIA': 'Miami', 'MIN': 'Minnesota', 'NE': 'New England', 'NO': 'New Orleans',
        'NYG': 'New York G', 'NYJ': 'New York J', 'PHI': 'Philadelphia', 'PIT': 'Pittsburgh', 'SEA': 'Seattle', 'SF': 'San Francisco', 'TB': 'Tampa Bay',
        'TEN': 'Tennessee', 'WAS': 'Washington'}
G = pd.read_csv(D7 + 'games.csv'); G = G[(G['season'] == 2026) & (G['week'] == 7) & G['home_score'].notna()]
ST = pd.read_csv(D7 + 'stats_player_week_2026.csv', low_memory=False); ST = ST[ST['week'] == 7]
STAT = {'Receiving Yards': ('receiving_yards', 'rec yds'), 'Receptions': ('receptions', 'rec'), 'Rushing Yards': ('rushing_yards', 'rush yds'),
        'Passing Yards': ('passing_yards', 'pass yds'), 'Passing Touchdowns': ('passing_tds', 'pass TDs'), 'Interceptions': ('passing_interceptions', 'INTs'),
        'Rushing + Receiving Yards': ('rr', 'rush + rec yds')}
def val(r, col):
    if col == 'rr': return (r.rushing_yards or 0) + (r.receiving_yards or 0)
    v = getattr(r, col); return 0 if pd.isna(v) else v
def team_is(text, t):
    text = text.replace(' wins', '').strip()
    return text == t or text.startswith(CITY.get(t, '#'))
DONE = {}
for g in G.itertuples(index=False):
    a, h = TO_SITE.get(g.away_team, g.away_team), TO_SITE.get(g.home_team, g.home_team)
    st = ST[ST['team'].isin([g.away_team, g.home_team])]
    DONE[f'{a} @ {h}'] = (a, h, int(g.away_score), int(g.home_score), {norm(r.player_display_name): r for r in st.itertuples(index=False)})
rows, seen = [], set()
def settle(game, m, c, price, extra):
    a, h, SA, SH, P = DONE[game]; FINAL = f'{h} {SH}, {a} {SA}'
    if m in STAT:
        mm = re.match(r'^(.*?): Over ([\d.]+) ', c)
        if not mm: return None
        p = P.get(norm(mm.group(1))); col, unit = STAT[m]
        if p is None: return 'Void', f'no stats recorded ({FINAL})'
        v = val(p, col); return ('Won' if v > float(mm.group(2)) else 'Lost'), f'{int(v)} {unit} ({FINAL})'
    if m == 'Anytime Touchdown':
        p = P.get(norm(c))
        if p is None: return 'Void', f'no stats recorded ({FINAL})'
        td = int((p.rushing_tds or 0) + (p.receiving_tds or 0)); return ('Won' if td >= 1 else 'Lost'), f'{td} TD ({FINAL})'
    if m == 'Moneyline':
        won = (team_is(c, h) and SH > SA) or (team_is(c, a) and SA > SH); return ('Won' if won else 'Lost'), FINAL
    if m == 'Spreads':
        mm = re.match(r'^(.*) wins by over ([\d.]+) points', c)
        if not mm: return None
        marg = SH - SA if team_is(mm.group(1), h) else SA - SH; return ('Won' if marg > float(mm.group(2)) else 'Lost'), FINAL
    if m == 'Totals':
        mm = re.search(r'Over ([\d.]+)', c)
        if not mm: return None
        return ('Won' if SA + SH > float(mm.group(1)) else 'Lost'), FINAL
    return None
def add(game, m, c, price, r, group='Week 7 settled', hit=''):
    res = settle(game, m, c, price, r)
    if not res: return
    outcome, detail = res
    pr = None if price in ('', None) else int(float(price))
    profit = '' if pr is None else (0 if outcome == 'Void' else (100 - pr if outcome == 'Won' else -pr))
    rows.append({'id': f'W7S{len(rows) + 1:03d}', 'game': game, 'market': m, 'group': group, 'contract': c, 'yes_price': '' if pr is None else pr,
                 'hit_rate': hit, 'hit_bucket': '', 'qualifies': r.get('qualifies', '') if r else '', 'flagged': '', 'cat': '',
                 'outcome': outcome, 'profit_c': profit, 'week6_result': f'W7: {detail}', 'week': 7})
for r in list(csv.DictReader(open(B + 'inband_w7.csv'))) + list(csv.DictReader(open(B + 'props_cat_w7.csv'))):
    if r['game'] not in DONE or (r['market'], r['contract']) in seen: continue
    seen.add((r['market'], r['contract'])); add(r['game'], r['market'], r['contract'], r['yes_price'], r, hit=r.get('hit_rate', ''))
for r in csv.DictReader(open(B + 'atd_w7.csv')):
    if r['game'] not in DONE or r['yes_price'] in ('', None) or ('Anytime Touchdown', r['player']) in seen: continue
    seen.add(('Anytime Touchdown', r['player'])); add(r['game'], 'Anytime Touchdown', r['player'], r['yes_price'], r, hit=r.get('atd_rate', ''))
picks = set(json.load(open(B + 'certs_live.json'))['picks'])
for v in json.load(open(B + 'analysts_live.json'))['picks'].values(): picks |= set(v)
have = {f"w7|{r['game']}|{r['market']}|{r['contract']}" for r in rows}
PRICE = {r['key']: r['yes_price'] for r in csv.DictReader(open(B + 'pick_prices_w7.csv'))} if os.path.exists(B + 'pick_prices_w7.csv') else {}
for k in sorted(picks):
    if not k.startswith('w7|') or k in have: continue
    _, game, m, c = k.split('|', 3)
    if game in DONE: add(game, m, c, PRICE.get(k, ''), None, group='Week 7 settled (pick)')
R = list(csv.DictReader(open(B + 'results_w6.csv'))); cols = list(R[0].keys())
with open(B + 'results_w6_w7.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(R); w.writerows(rows)
print('games', sorted(DONE), 'settled', len(rows), collections.Counter(r['outcome'] for r in rows))
allr = {f"w7|{r['game']}|{r['market']}|{r['contract']}": r for r in rows}
for k in sorted(p for p in picks if p.startswith('w7|') and p.split('|')[1] in DONE):
    hit = allr.get(k)
    print('PICK', k, '->', (hit['outcome'], hit['yes_price'], hit['week6_result']) if hit else 'NOT SETTLED')
