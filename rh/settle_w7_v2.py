"""Settle Week 7 games that have finished (NE @ CHI Thu: CHI 30, NE 24; PIT @ NO Sun in Dublin: PIT 16, NO 10) for the results dataset.

Every NE @ CHI player prop and Anytime TD line on the Week 7 tables (Thursday prices), plus the full-game moneyline,
spread and total lines, settled from nflverse player stats. Rows go in with week = 7 and group 'Week 7 settled' so the
Wedger record and analyst standings pick them up; the Week 6 results views filter them out.
"""
import csv, json, re, collections
import pandas as pd
B = '/home/claude/wedger/rh/'
S = '/home/claude/wedger/dl5/stats_player_week_2026.csv'
norm = lambda s: re.sub(r'[^a-z]', '', str(s).lower().replace(' jr', '').replace(' iii', '').replace(' ii', ''))
NAMES = {'NE': 'New England', 'CHI': 'Chicago', 'PIT': 'Pittsburgh', 'NO': 'New Orleans'}
def espn_box(path):
    """ESPN box score transcribed as PASS/RUSH/REC lines -> nflverse-style rows."""
    acc = collections.defaultdict(lambda: collections.defaultdict(float)); team = {}
    for ln in open(path):
        p = ln.strip().split('|'); kind, tm, nm = p[0], p[1], p[2]; kv = dict(x.split('=') for x in p[3:]); team[nm] = tm; a = acc[nm]
        if kind == 'PASS': a['passing_yards'] += float(kv['YDS']); a['passing_tds'] += float(kv['TD']); a['passing_interceptions'] += float(kv['INT'])
        elif kind == 'RUSH': a['rushing_yards'] += float(kv['YDS']); a['rushing_tds'] += float(kv['TD'])
        elif kind == 'REC': a['receptions'] += float(kv['REC']); a['receiving_yards'] += float(kv['YDS']); a['receiving_tds'] += float(kv['TD'])
    cols = ['passing_yards', 'passing_tds', 'passing_interceptions', 'rushing_yards', 'rushing_tds', 'receptions', 'receiving_yards', 'receiving_tds']
    return pd.DataFrame([{'player_display_name': n, 'team': team[n], **{c: a.get(c, 0.0) for c in cols}} for n, a in acc.items()])
GAMES_DONE = [('NE @ CHI', 'NE', 'CHI', 24, 30, 'nflverse'), ('PIT @ NO', 'PIT', 'NO', 16, 10, '/home/claude/wedger/dl6/pitno_box.txt')]
ST_ALL = pd.read_csv(S, low_memory=False)
STAT = {'Receiving Yards': ('receiving_yards', 'rec yds'), 'Receptions': ('receptions', 'rec'), 'Rushing Yards': ('rushing_yards', 'rush yds'),
        'Passing Yards': ('passing_yards', 'pass yds'), 'Passing Touchdowns': ('passing_tds', 'pass TDs'), 'Interceptions': ('passing_interceptions', 'INTs'),
        'Rushing + Receiving Yards': ('rr', 'rush + rec yds')}
def val(r, col):
    if col == 'rr': return (r.rushing_yards or 0) + (r.receiving_yards or 0)
    v = getattr(r, col); return 0 if pd.isna(v) else v
rows = []
PP = {}
for GAME, AWAY, HOME, SA, SH, SRC in GAMES_DONE:
    FINAL = f'{HOME} {SH}, {AWAY} {SA}'
    st = ST_ALL[(ST_ALL['week'] == 7) & ST_ALL['team'].isin([AWAY, HOME])] if SRC == 'nflverse' else espn_box(SRC)
    P = {norm(r.player_display_name): r for r in st.itertuples(index=False)}; PP[GAME] = (P, FINAL)
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
                team = c.replace(' wins', ''); won = (team.startswith(NAMES[HOME]) and SH > SA) or (team.startswith(NAMES[AWAY]) and SA > SH)
            elif m == 'Spreads':
                mm = re.match(r'^(.*) wins by over ([\d.]+) points', c)
                if not mm: continue
                marg = SH - SA if mm.group(1).startswith(NAMES[HOME]) else SA - SH
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
picks = set(json.load(open(B + 'certs_live.json'))['picks'])
for v in json.load(open(B + 'analysts_live.json'))['picks'].values(): picks |= set(v)
have = {f"w7|{r['game']}|{r['market']}|{r['contract']}" for r in rows}
PRICE = {r['key']: r['yes_price'] for r in csv.DictReader(open(B + 'pick_prices_w7.csv'))} if __import__('os').path.exists(B + 'pick_prices_w7.csv') else {}
for k in sorted(picks):
    if not k.startswith('w7|') or k in have: continue
    _, game, m, c = k.split('|', 3)
    if game not in PP: continue
    P, FINAL = PP[game]
    price = PRICE.get(k, '')
    if m in STAT:
        mm = re.match(r'^(.*?): Over ([\d.]+) ', c); p = P.get(norm(mm.group(1))) if mm else None; col, unit = STAT[m]
        if p is None: outcome, detail = 'Void', 'no stats recorded'
        else: v = val(p, col); outcome = 'Won' if v > float(mm.group(2)) else 'Lost'; detail = f'{int(v)} {unit}'
    elif m == 'Anytime Touchdown':
        p = P.get(norm(c))
        if p is None: outcome, detail = 'Void', 'no stats recorded'
        else: td = int((p.rushing_tds or 0) + (p.receiving_tds or 0)); outcome = 'Won' if td >= 1 else 'Lost'; detail = f'{td} TD'
    else: continue
    pr = int(float(price)) if price not in ('', None) else None
    profit = '' if pr is None else (0 if outcome == 'Void' else (100 - pr if outcome == 'Won' else -pr))
    rows.append({'id': f'W7S{len(rows) + 1:03d}', 'game': game, 'market': m, 'group': 'Week 7 settled (pick)', 'contract': c, 'yes_price': '' if pr is None else pr,
                 'hit_rate': '', 'hit_bucket': '', 'qualifies': '', 'flagged': '', 'cat': '', 'outcome': outcome, 'profit_c': profit,
                 'week6_result': f'W7: {detail} ({FINAL})', 'week': 7})
R = list(csv.DictReader(open(B + 'results_w6.csv'))); cols = list(R[0].keys())
with open(B + 'results_w6_w7.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(R); w.writerows(rows)
print('settled', len(rows), collections.Counter(r['outcome'] for r in rows))
# every NE @ CHI pick on the board should now be settled
picks = set(json.load(open(B + 'certs_live.json'))['picks'])
for v in json.load(open(B + 'analysts_live.json'))['picks'].values(): picks |= set(v)
have = {f"w7|{r['game']}|{r['market']}|{r['contract']}" for r in rows}
for k in sorted(p for p in picks if p.startswith(('w7|NE @ CHI', 'w7|PIT @ NO'))):
    hit = next((r for r in rows if f"w7|{r['game']}|{r['market']}|{r['contract']}" == k), None)
    print('PICK', k, '->', (hit['outcome'], hit['yes_price'], hit['week6_result']) if hit else 'NOT SETTLED')
