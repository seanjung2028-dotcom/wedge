"""Real priced player-prop lines from the site (Week 6 and Week 7, 2026), joined to each player's history features.

Sources: rh/results_w6.csv (Week 6 screen, group 'Player props', 45-55c) and rh/results_w6_w7.csv (Week 7, every posted line,
group 'Week 7 settled'); Wedger % and picks from the posted Week 7 tables (inband/props_cat/atd).
Writes mom/real.pkl: one row per settled prop line with price, outcome, and S/L4/C etc. for that player-stat before the game.
"""
import re, csv, unicodedata, numpy as np, pandas as pd
S = '/home/claude/wedger/'
F = pd.read_pickle(S + 'mom/feat.pkl'); pg = pd.read_pickle(S + 'mom/pg.pkl')
STAT = {'Receptions': 'rec', 'Receiving Yards': 'recyd', 'Rushing Yards': 'rushyd', 'Rushing + Receiving Yards': 'rryd', 'Passing Yards': 'passyd',
        'Anytime Touchdown': 'td', 'Passing Touchdowns': 'passtd', 'Interceptions': 'int'}
def norm(n):
    n = unicodedata.normalize('NFKD', str(n)).encode('ascii', 'ignore').decode().lower().replace('.', '').replace("'", '').replace('-', ' ')
    n = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', n); return re.sub(r'\s+', ' ', n).strip()
FIXT = {'LAR': 'LAR', 'LA': 'LAR', 'WAS': 'WSH'}
pg['nn'] = pg['name'].map(norm)
key = {}
for r in pg[pg['season'] == 2026].itertuples(index=False): key[(r.nn, r.week, r.team)] = r.pid
rows = []
def add(wk, game, market, contract, price, outcome, extra):
    if market not in STAT or outcome not in ('Won', 'Lost'): return
    stat = STAT[market]
    if stat == 'td': player, line = contract, 0.5
    else:
        m = re.match(r'^(.*?): Over ([\d.]+) ', contract)
        if not m: return
        player, line = m.group(1), float(m.group(2))
    a, h = [FIXT.get(t, t) for t in game.split(' @ ')]
    pid = key.get((norm(player), wk, a)) or key.get((norm(player), wk, h))
    rows.append({'week': wk, 'game': game, 'market': market, 'stat': stat, 'contract': contract, 'player': player, 'line': line, 'price': float(price),
                 'y_hit': 1 if outcome == 'Won' else 0, 'pid': pid, **extra})
for r in csv.DictReader(open(S + 'rh/results_w6.csv')):
    mk = 'Anytime Touchdown' if r['group'] == 'ATD filter picks' else r['market']
    if r['group'] in ('Player props', 'ATD filter picks'):
        add(6, r['game'], mk, r['contract'], r['yes_price'], r['outcome'], {'qual': r.get('qualifies', ''), 'hit_rate': r.get('hit_rate', '')})
# posted Week 7 Wedger values
post = {}
for f in ('inband_w7.csv', 'props_cat_w7.csv'):
    for r in csv.DictReader(open(S + 'rh/' + f)):
        if r['id'].startswith('C'): continue
        post.setdefault((r['game'], r['market'], r['contract']), r)
for r in csv.DictReader(open(S + 'rh/atd_w7.csv')):
    post.setdefault((r['game'], 'Anytime Touchdown', r['player']), r)
for r in csv.DictReader(open(S + 'rh/results_w6_w7.csv')):
    if r['week'] != '7' or r['group'] != 'Week 7 settled': continue
    p = post.get((r['game'], r['market'], r['contract']), {})
    add(7, r['game'], r['market'], r['contract'], r['yes_price'], r['outcome'],
        {'qual': r.get('qualifies', ''), 'hit_rate': r.get('hit_rate', ''), 'v1': p.get('sit_v1', ''), 'v2': p.get('sit_hit', ''), 'pick': p.get('sit_pick', ''),
         'src': p.get('source', ''), 'yes_bid': p.get('yes_bid', ''), 'no_price': p.get('no_price', '')})
R = pd.DataFrame(rows)
print('lines', len(R), 'matched pid', R['pid'].notna().mean().round(3), R.groupby(['week', 'stat']).size().unstack(fill_value=0))
FF = F[(F['season'] == 2026)][['pid', 'week', 'stat', 'S', 'Smed', 'L4', 'L2', 'E3', 'C', 'P', 'n', 'nC', 'sd', 'vS', 'vL4', 'effS', 'effL4', 'snapS', 'snapL4', 'y', 'pos', 'fav_by', 'implied', 'home']]
R = R.merge(FF, on=['pid', 'week', 'stat'], how='left')
R.to_pickle(S + 'mom/real.pkl')
print('with features', R['S'].notna().sum())
