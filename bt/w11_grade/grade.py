"""Grade the Week 11 final draft (Sun Nov 22, 10:32 AM CT; bt/w11_sun_board/) plus Thursday's card: finals, leans and every
'considered and passed' line, from nflverse stats and snap counts (dl23, pulled Mon Nov 23). Writes bt/w11_grade/graded.csv."""
import json, re, unicodedata, pandas as pd
W = '/home/claude/wedger/'
def nn(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', s); return re.sub(r'[^a-z]', '', s)
FIX = {'LA': 'LAR', 'WAS': 'WSH', 'JAC': 'JAX'}; fx = lambda t: FIX.get(t, t)
st = pd.read_csv(W + 'dl23/stats_player_week_2026.csv', low_memory=False); st = st[(st.week == 11) & (st.season_type == 'REG')].copy(); st['team'] = st.team.map(fx)
for c in ['receptions', 'receiving_yards', 'rushing_yards', 'passing_yards', 'passing_tds', 'carries', 'targets', 'rushing_tds', 'receiving_tds']:
    st[c] = pd.to_numeric(st[c], errors='coerce').fillna(0)
P = {}
for r in st.itertuples(index=False): P.setdefault(nn(r.player_display_name), []).append(r)
sn = pd.read_csv(W + 'dl23/snap_counts_2026.csv'); sn = sn[sn.week == 11]
PLAYED = {nn(r.player) for r in sn.itertuples(index=False) if (r.offense_snaps or 0) > 0}
DONE = set(fx(t) for t in st.team.unique())
COL = {'receptions': 'receptions', 'receiving yards': 'receiving_yards', 'rushing yards': 'rushing_yards', 'rush + receiving yards': 'rr', 'passing yards': 'passing_yards', 'passing touchdowns': 'passing_tds', 'passing tds': 'passing_tds'}
RX = re.compile(r'^(?P<pl>.+?) (?:(?P<k>\d+)\+|under (?P<u>\d+)) (?P<stat>receptions|receiving yards|rushing yards|rush \+ receiving yards|passing yards|passing touchdowns|passing tds)(?: \((?P<side>Yes|No)\))?')
def parse(text):
    m = RX.match(text.strip())
    if not m: return None
    k = int(m['k'] or m['u']); side = 'Yes' if m['k'] else 'No'
    return m['pl'], k, COL[m['stat']], m['stat'], side
def grade(game, text, price):
    pp = parse(text)
    if not pp: return None
    pl, k, col, stat, side = pp; a, h = [fx(t) for t in game.split(' @ ')]
    if a not in DONE and h not in DONE: return dict(player=pl, k=k, stat=stat, side=side, value=None, result='Pending', pl_c=None)
    rows = [r for r in P.get(nn(pl), []) if r.team in (a, h)]
    if not rows and nn(pl) not in PLAYED: return dict(player=pl, k=k, stat=stat, side=side, value=None, result='Void', pl_c=0)
    r = rows[0] if rows else None
    v = 0.0 if r is None else (float(r.rushing_yards) + float(r.receiving_yards) if col == 'rr' else float(getattr(r, col)))
    hit = v >= k; won = hit if side == 'Yes' else not hit
    return dict(player=pl, k=k, stat=stat, side=side, value=v, result='Won' if won else 'Lost',
                pl_c=None if price is None else ((100 - price) if won else -price), margin=v - k if side == 'Yes' else (k - 1) - v)
SER = {'receptions': 'KXNFLREC', 'receiving_yards': 'KXNFLRECYDS', 'rushing_yards': 'KXNFLRSHYDS', 'rr': 'KXNFLRRYDS', 'passing_yards': 'KXNFLPASSYDS'}
KX = {}
for ser, d in json.load(open(W + 'pull1122b/kalshi_raw_1122b.json')).items():
    for r in (d.get('rows', []) if isinstance(d, dict) else []):
        try: KX[(ser, nn(r[5]), int(r[1].rsplit('-', 1)[1]))] = (r[2], r[4])
        except Exception: pass
RUNG = re.compile(r'Closest rung: (?P<thr>.+?) \((?P<side>Yes|No) (?P<p>\d+)¢, needs (?P<be>\d+)%, ours (?P<lo>\d+)–(?P<hi>\d+)%\)')
out = []
for src, f in (('Thu', 'bt/w11_thu_board/final_w11.json'), ('Sun', 'bt/w11_sun_board/final_w11.json')):
    D = json.load(open(W + f))
    for c in D['cards']:
        g = c['game']
        if (src == 'Thu') != (g == 'IND @ HOU'): continue
        for p in c.get('plays', []):
            r = grade(g, p['line'], p['price'])
            if r: out.append(dict(card=src, game=g, group='Final' if p['decision'] == 'Final line' else 'Lean', line=p['line'], price=p['price'], needs=p['be'], lo=p['lo'], mid=p['mid'], hi=p['hi'], tier=p.get('tier') or p.get('conf'), why_pass='', **r))
        for p in c.get('early', []):
            r = grade(g, p['line'], p['price'])
            if r: out.append(dict(card=src, game=g, group='Early final' if p['decision'] == 'Final line' else 'Early lean', line=p['line'], price=p['price'], needs=p['be'], lo=p.get('lo'), mid=p.get('mid'), hi=p.get('hi'), tier='', why_pass='', **r))
        for p in c.get('passed', []) + c.get('early_passed', []):
            name, why = p.get('name', ''), p.get('why') or ''
            m = RUNG.search(why); price = int(m['p']) if m else None; needs = int(m['be']) if m else None
            lo = int(m['lo']) if m else None; hi = int(m['hi']) if m else None
            if parse(name): text = name
            elif m:
                pl = re.sub(r' (receptions|receiving yards|rushing yards|rush \+ receiving yards|passing yards|passing touchdowns|passing tds)$', '', name)
                text = f"{pl} {m['thr']} ({m['side']})"
            else: text = name
            if price is None:
                mm = re.search(r'\((?:(?:Yes|No) )?(\d+)¢, needs (\d+)%, ours (\d+)–(\d+)%\)', why)
                if mm: price, needs, lo, hi = [int(x) for x in mm.groups()]
            if price is None and parse(text):   # research passes name no price: take it from the 10:32 AM Kalshi pull
                pl_, k_, col_, _, side_ = parse(text); q = KX.get((SER.get(col_), nn(pl_), k_))
                if q: price = q[0] if side_ == 'Yes' else q[1]
            r = grade(g, text, price)
            if r: out.append(dict(card=src, game=g, group='Passed', line=text, price=price, needs=needs, lo=lo, mid=None, hi=hi, tier='', why_pass=(p.get('move') or '') + ' ' + why[:220], **r))
G = pd.DataFrame(out); G.to_csv(W + 'bt/w11_grade/graded.csv', index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 60)
print(G.groupby(['card', 'group', 'result']).size().unstack(fill_value=0))
print(G[G.group != 'Passed'][['card', 'group', 'game', 'line', 'price', 'needs', 'lo', 'hi', 'value', 'result', 'pl_c']].to_string())
