"""Price check, NFL Week 11 Sunday slate (Thu Nov 19 morning pulls).

Venues: Kalshi (exchange order book, 6:04 AM CT), Robinhood (its public prediction-market quotes, 6:34 AM CT; game lines trade on
Robinhood's Rothera exchange, player props on a third venue), and five sportsbooks from Action Network's Illinois odds feed
(DraftKings, FanDuel, BetMGM, Fanatics, Caesars; 6:06 AM CT).

Every price is the cost of a $1 payout in cents. A sportsbook's American odds become their implied chance (vig included); Kalshi
and Robinhood are their asks (No = 100 minus the Yes bid). Fees: Kalshi's taker fee is 7% x p x (1 - p) per contract; Robinhood's
1 cent commission per contract; exchange fees on Robinhood's venues, if any, are not included.

Lines are compared at the books' main line L (the most common line across the five books). The fair chance at L is the five books'
average with the vig removed (Over / (Over + Under)). Kalshi and Robinhood are compared at exactly L when they list it, and
otherwise their midpoints are interpolated at L between the two rungs around it.
Writes pricecheck/pricecheck_1119.json for the page."""
import json, re, math, statistics as S, unicodedata, collections, csv
W = '/home/claude/wedger/'
GAMES = {'MIABUF': 'MIA @ BUF', 'BALCAR': 'BAL @ CAR', 'NOCHI': 'NO @ CHI', 'TENDAL': 'TEN @ DAL', 'TBDET': 'TB @ DET', 'ARIKC': 'ARI @ KC',
         'JACNYG': 'JAX @ NYG', 'NYJLAC': 'NYJ @ LAC', 'LVDEN': 'LV @ DEN', 'PITPHI': 'PIT @ PHI', 'MINSF': 'MIN @ SF'}
KICK = {'MIA @ BUF': 'Sun 12:00', 'BAL @ CAR': 'Sun 12:00', 'NO @ CHI': 'Sun 12:00', 'TEN @ DAL': 'Sun 12:00', 'TB @ DET': 'Sun 12:00', 'ARI @ KC': 'Sun 12:00',
        'JAX @ NYG': 'Sun 12:00', 'NYJ @ LAC': 'Sun 3:05', 'LV @ DEN': 'Sun 3:25', 'PIT @ PHI': 'Sun 3:25', 'MIN @ SF': 'Sun 7:20'}
FIX = {'JAC': 'JAX', 'WAS': 'WSH', 'LA': 'LAR'}
CITY = {'Buffalo': 'BUF', 'Miami': 'MIA', 'Carolina': 'CAR', 'Baltimore': 'BAL', 'Chicago': 'CHI', 'New Orleans': 'NO', 'Dallas': 'DAL', 'Tennessee': 'TEN',
        'Detroit': 'DET', 'Tampa': 'TB', 'Tampa Bay': 'TB', 'Kansas': 'KC', 'Kansas City': 'KC', 'Arizona': 'ARI', 'New York G': 'NYG', 'Jacksonville': 'JAX',
        'New York J': 'NYJ', 'Los Angeles C': 'LAC', 'Las Vegas': 'LV', 'Denver': 'DEN', 'Pittsburgh': 'PIT', 'Philadelphia': 'PHI', 'San Francisco': 'SF', 'Minnesota': 'MIN'}
BOOKS = [(1538, 'DraftKings'), (270, 'FanDuel'), (282, 'BetMGM'), (2990, 'Fanatics'), (279, 'Caesars')]
BID = {b: n for b, n in BOOKS}
ST = {'recyd': 'Receiving yards', 'rec': 'Receptions', 'rushyd': 'Rushing yards', 'rryd': 'Rush + rec yards', 'passyd': 'Passing yards', 'ptd': 'Passing TDs', 'atd': 'Anytime TD'}
def norm(n):
    n = unicodedata.normalize('NFKD', str(n)).encode('ascii', 'ignore').decode().lower().replace('.', '').replace("'", '').replace('-', ' ')
    return re.sub(r'\s+', ' ', re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', n)).strip()
imp = lambda o: 100 / (o + 100) if o > 0 else -o / (-o + 100)
kfee = lambda p: 7 * (p / 100) * (1 - p / 100)          # cents per contract
TEAMGAME = {}
for code, g in GAMES.items():
    for t in g.split(' @ '): TEAMGAME[t] = g
def game_of_teams(ts):
    gs = {TEAMGAME.get(t) for t in ts}
    gs.discard(None)
    return gs.pop() if len(gs) == 1 else None
D = collections.defaultdict(lambda: {'books': {}, 'k': {}, 'r': {}, 'name': None, 'team': '', 'pos': ''})   # (game, norm player, stat)
# ---- sportsbooks
A = json.load(open(W + 'pull1119/an_props_raw.json'))
AL = {'Receiving Yards': 'recyd', 'Receptions': 'rec', 'Rush Yards': 'rushyd', 'Rush + Rec Yards': 'rryd', 'Pass Yards': 'passyd', 'Pass TDs': 'ptd', 'Anytime Touchdown': 'atd'}
for label, g, player, team, pos, bk in A['rows']:
    if label not in AL: continue
    a, h = (FIX.get(x, x) for x in g.split('@')); game = f'{a} @ {h}'
    if game not in KICK: continue
    d = D[(game, norm(player), AL[label])]; d['name'] = d['name'] or player; d['team'] = FIX.get(team, team); d['pos'] = pos
    for b, L, o, u, y in bk:
        if b not in BID: continue
        if AL[label] == 'atd':
            if y: d['books'][BID[b]] = [0.5, round(100 * imp(y), 1), None]
        elif L is not None and o and u: d['books'][BID[b]] = [L, round(100 * imp(o), 1), round(100 * imp(u), 1)]
# ---- Kalshi (rung k+ is Over k - 0.5)
K = json.load(open(W + 'pull1119/kalshi_props_w11.json'))
KS = {'KXNFLRECYDS': 'recyd', 'KXNFLREC': 'rec', 'KXNFLRSHYDS': 'rushyd', 'KXNFLRRYDS': 'rryd', 'KXNFLPASSYDS': 'passyd', 'KXNFLPASSTDS': 'ptd', 'KXNFLTD': 'atd'}
for ser, st in KS.items():
    for row in filter(None, K['q'].get(ser, '').split(';')):
        code, tail, ya, yb, na = row.split('|')
        if code not in GAMES: continue
        pc, k = tail.rsplit('-', 1); k = int(k)
        if st == 'atd' and k != 1: continue
        nm = K['n'].get(pc, pc); d = D[(GAMES[code], norm(nm), st)]; d['name'] = d['name'] or nm
        d['k'][k - 0.5] = [int(ya), int(yb), int(na)]
# ---- Robinhood
R = json.load(open(W + 'pricecheck/rh_raw_1119.json'))
RT = {'REC_YDS': 'recyd', 'RECEPTIONS': 'rec', 'RUSH_YDS': 'rushyd', 'RUSH_REC_YDS': 'rryd', 'PASS_YDS': 'passyd', 'PASS_TD': 'ptd', 'ANY_TD': 'atd'}
RG = collections.defaultdict(dict)     # game lines
rh_ven = collections.Counter()
for ev, typ, sym, name, floor, exch, tr, *q in R['rows']:
    if not q or q[0] is None: continue
    ya, yb, na, nb = q[0], q[1], q[2], q[3]
    teams = [CITY[c] for c in sorted(CITY, key=len, reverse=True) if re.search(r'\b' + re.escape(c) + r'\b', ev.split(':')[0])]
    game = game_of_teams(teams)
    if not game: continue
    rh_ven[(typ, exch)] += 1
    if typ in RT:
        if typ == 'ANY_TD': nm, x = name, 0.5
        else:
            m = re.match(r'^(.*?): Over ([\d.]+) ', name)
            if not m: continue
            nm, x = m.group(1), float(m.group(2))
        d = D[(game, norm(nm), RT[typ])]; d['name'] = d['name'] or nm
        d['r'][x] = [ya, yb, na if na is not None else (100 - yb if yb is not None else None)]
    elif typ in ('WINNER', 'SPREAD', 'TOTALS'):
        RG[game][(typ, name)] = [ya, yb, na, floor]
# ---- the card, for flags
CARD = {}
for r in csv.DictReader(open(W + 'final11/final_w11.csv')):
    if r['decision'] in ('Final line', 'Conditional lean'): CARD[(r['game'], r['line'])] = 'Final' if r['decision'] == 'Final line' else 'Lean'
CARDN = {(g, norm(re.split(r' (?:under )?\d+\+? | under \d', l)[0])): v for (g, l), v in CARD.items()}
def at_line(lad, L):
    """(exact quote or None, interpolated mid at L or None, the two rungs used)"""
    if not lad: return None, None, []
    pts = sorted((x, (q[0] + q[1]) / 2 if q[1] is not None and q[0] is not None else None) for x, q in lad.items())
    pts = [(x, m) for x, m in pts if m is not None]
    ex = lad.get(L)
    for (x0, m0), (x1, m1) in zip(pts, pts[1:]):
        if x0 <= L <= x1:
            return ex, (m0 + (m1 - m0) * (L - x0) / (x1 - x0)) if x1 > x0 else m0, [x0, x1]
    if pts and pts[0][0] == L: return ex, pts[0][1], [L]
    return ex, None, []
rows, cost2 = [], collections.defaultdict(list)
for (game, pn, st), d in D.items():
    if not d['books'] and not d['k'] and not d['r']: continue
    lines = [v[0] for v in d['books'].values()]
    L = S.mode(lines) if lines else None
    if L is None:   # no book line: report the venues' own midpoint line
        lad = d['k'] or d['r']; L = min(lad, key=lambda x: abs((lad[x][0] + (lad[x][1] or 0)) / 2 - 50)) if lad else None
    atL = {b: v for b, v in d['books'].items() if v[0] == L}
    if st == 'atd': fair = None
    else:
        nv = [v[1] / (v[1] + v[2]) for v in atL.values() if v[2]]
        fair = round(100 * S.mean(nv), 1) if nv else None
    kx, km, kr = at_line(d['k'], L); rx, rm, rr = at_line(d['r'], L)
    over, under = [], []
    for b, v in atL.items():
        over.append((b, v[1])); cost2[b].append(v[1] + v[2] - 100) if v[2] else None
        if v[2]: under.append((b, v[2]))
    if kx:
        over.append(('Kalshi', kx[0] + kfee(kx[0]))); under.append(('Kalshi', kx[2] + kfee(kx[2])))
        if kx[1]: cost2['Kalshi'].append(kx[0] - kx[1] + kfee(kx[0]) + kfee(kx[2]))
    if rx and rx[0] is not None:
        over.append(('Robinhood', rx[0] + 1))
        if rx[2] is not None: under.append(('Robinhood', rx[2] + 1))
        if rx[1] is not None: cost2['Robinhood'].append(rx[0] - rx[1] + 2)
    bo = min(over, key=lambda x: x[1]) if over else None; bu = min(under, key=lambda x: x[1]) if under else None
    name = d['name']
    rows.append({'g': game, 'ko': KICK[game], 'p': name, 'st': st, 'L': L, 'team': d['team'], 'pos': d['pos'],
                 'b': {b: v for b, v in d['books'].items()}, 'fair': fair,
                 'k': {'x': kx, 'mid': round(km, 1) if km is not None else None, 'br': kr, 'n': len(d['k'])},
                 'r': {'x': rx, 'mid': round(rm, 1) if rm is not None else None, 'br': rr, 'n': len(d['r'])},
                 'kg': round(km - fair, 1) if km is not None and fair is not None else None, 'rg': round(rm - fair, 1) if rm is not None and fair is not None else None,
                 'bo': [bo[0], round(bo[1], 1)] if bo else None, 'bu': [bu[0], round(bu[1], 1)] if bu else None,
                 'card': CARDN.get((game, norm(name)), '') if st in ('recyd', 'rec', 'rushyd', 'rryd') else ''})
# ---- value spots: a prediction-market price at exactly the books' line that beats the books' fair after fees
spots = []
for x in rows:
    if x['fair'] is None: continue
    for v, q, fee in (('Kalshi', x['k']['x'], kfee), ('Robinhood', x['r']['x'], lambda p: 1)):
        if not q or q[0] is None: continue
        if q[0] + fee(q[0]) < x['fair']: spots.append({**{k: x[k] for k in ('g', 'ko', 'p', 'st', 'L', 'card')}, 'v': v, 'side': 'Over', 'cost': round(q[0] + fee(q[0]), 1), 'fair': x['fair'], 'edge': round(x['fair'] - q[0] - fee(q[0]), 1), 'ask': q[0]})
        if q[2] is not None and q[2] + fee(q[2]) < 100 - x['fair']: spots.append({**{k: x[k] for k in ('g', 'ko', 'p', 'st', 'L', 'card')}, 'v': v, 'side': 'Under', 'cost': round(q[2] + fee(q[2]), 1), 'fair': round(100 - x['fair'], 1), 'edge': round(100 - x['fair'] - q[2] - fee(q[2]), 1), 'ask': q[2]})
spots.sort(key=lambda s: -s['edge'])
# ---- game lines
GL = json.load(open(W + 'pull1119/an_glines_raw.json'))
KG = json.load(open(W + 'pull1119/kalshi_games_w11.json'))
KGQ = collections.defaultdict(dict)
for ser, body in KG['q'].items():
    for row in filter(None, body.split(';')):
        code, suf, ya, yb, na, tr, title = row.split('|')
        if code in GAMES: KGQ[GAMES[code]][(ser, suf)] = [int(ya), int(yb), int(na), title]
games = []
for g, ko, bk in GL['g']:
    a, h = (FIX.get(x, x) for x in g.split('@')); game = f'{a} @ {h}'
    if game not in KICK: continue
    B5 = {BID[b[0]]: b for b in bk if b[0] in BID}
    sp = S.mode([b[1] for b in B5.values()]); tot = S.mode([b[4] for b in B5.values()])
    fav, dog, fs = (h, a, -sp) if sp < 0 else (a, h, sp)          # fav wins by over fs
    ka, kh = a.replace('JAX', 'JAC').replace('WSH', 'WAS'), h.replace('JAX', 'JAC').replace('WSH', 'WAS')
    kfav = fav.replace('JAX', 'JAC').replace('WSH', 'WAS')
    def kq(ser, suf): return KGQ[game].get((ser, suf))
    def rq(typ, name): return RG[game].get((typ, name))
    rnames = {t: [c for c, v in CITY.items() if v == t] for t in (a, h)}
    def rwin(t):
        for c in rnames[t]:
            q = rq('WINNER', f'{c} wins')
            if q: return q
    def rspread(t, x):
        for c in rnames[t]:
            q = rq('SPREAD', f'{c} wins by over {x:g} points')
            if q: return q
    out = {'g': game, 'ko': KICK[game], 'fav': fav, 'dog': dog, 'spread': fs, 'total': tot, 'ml': [], 'sp': [], 'tot': []}
    for t, ko_ in ((a, 8), (h, 7)):
        row = {'t': t, 'b': {}, 'k': None, 'r': None}
        nv = []
        for n, b in B5.items():
            hm, am = imp(b[7]), imp(b[8]); row['b'][n] = round(100 * (hm if t == h else am), 1); nv.append((hm if t == h else am) / (hm + am))
        row['fair'] = round(100 * S.mean(nv), 1)
        q = kq('KXNFLGAME', ka if t == a else kh); row['k'] = q[:3] if q else None
        q = rwin(t); row['r'] = q[:3] if q else None
        out['ml'].append(row)
    # spread at the books' number: favorite covers / underdog covers
    rows_sp = []
    for side in ('fav', 'dog'):
        row = {'side': side, 't': fav if side == 'fav' else dog, 'b': {}}
        nv = []
        for n, b in B5.items():
            if b[1] != sp: continue
            ho, ao = imp(b[2]), imp(b[3]); pf = ho if fav == h else ao; pd = ao if fav == h else ho
            row['b'][n] = round(100 * (pf if side == 'fav' else pd), 1); nv.append((pf if side == 'fav' else pd) / (pf + pd))
        row['fair'] = round(100 * S.mean(nv), 1) if nv else None
        rungs = [fs] if fs % 1 else [fs - 0.5, fs + 0.5]
        kk, rr = [], []
        for x in rungs:
            q = kq('KXNFLSPREAD', f'{kfav}{int(x + 0.5)}'); kk.append([x, q[0], q[1], q[2]] if q else [x, None, None, None])
            q = rspread(fav, x); rr.append([x, q[0], q[1], q[2]] if q else [x, None, None, None])
        row['k'], row['r'] = kk, rr
        rows_sp.append(row)
    out['sp'] = rows_sp
    rows_t = []
    for side in ('over', 'under'):
        row = {'side': side, 'b': {}}
        nv = []
        for n, b in B5.items():
            if b[4] != tot: continue
            po, pu = imp(b[5]), imp(b[6]); row['b'][n] = round(100 * (po if side == 'over' else pu), 1); nv.append((po if side == 'over' else pu) / (po + pu))
        row['fair'] = round(100 * S.mean(nv), 1) if nv else None
        rungs = [tot] if tot % 1 else [tot - 0.5, tot + 0.5]
        kk, rr = [], []
        for x in rungs:
            q = kq('KXNFLTOTAL', f'{int(x + 0.5)}'); kk.append([x, q[0], q[1], q[2]] if q else [x, None, None, None])
            q = rq('TOTALS', f'Over {x:g} points'); rr.append([x, q[0], q[1], q[2]] if q else [x, None, None, None])
        row['k'], row['r'] = kk, rr
        rows_t.append(row)
    out['tot'] = rows_t
    games.append(out)
games.sort(key=lambda x: list(KICK).index(x['g']))
# ---- summary
cov = {v: sum(1 for x in rows if (x['b'].get(v) if v in BID.values() else x[{'Kalshi': 'k', 'Robinhood': 'r'}[v]]['n'])) for v in ['Kalshi', 'Robinhood'] + [n for _, n in BOOKS]}
best = collections.Counter(); bestu = collections.Counter()
for x in rows:
    if x['bo'] and x['st'] != 'atd': best[x['bo'][0]] += 1
    if x['bu'] and x['st'] != 'atd': bestu[x['bu'][0]] += 1
both = [(x['k']['mid'], x['r']['mid']) for x in rows if x['k']['mid'] is not None and x['r']['mid'] is not None]
gaps = {'Kalshi': [x['kg'] for x in rows if x['kg'] is not None], 'Robinhood': [x['rg'] for x in rows if x['rg'] is not None]}
summ = {'at': {'kalshi': K['at'], 'books': A['at'], 'robinhood': R['at']}, 'n_props': len(rows), 'coverage': cov,
        'cost2': {v: round(S.median(c), 1) for v, c in cost2.items() if c}, 'cost2_n': {v: len(c) for v, c in cost2.items()},
        'best_over': dict(best), 'best_under': dict(bestu), 'spots': len(spots),
        'gap_med': {v: round(S.median(g), 1) for v, g in gaps.items() if g}, 'gap_mae': {v: round(S.mean(abs(x) for x in g), 1) for v, g in gaps.items() if g},
        'gap_n': {v: len(g) for v, g in gaps.items()},
        'k_vs_r': {'n': len(both), 'med': round(S.median([r - k for k, r in both]), 1) if both else None, 'mae': round(S.mean(abs(r - k) for k, r in both), 1) if both else None},
        'rh_venues': {f'{t}|{e}': n for (t, e), n in rh_ven.items()}}
json.dump({'summary': summ, 'games': games, 'props': rows, 'spots': spots, 'stats': ST, 'books': [n for _, n in BOOKS]}, open(W + 'pricecheck/pricecheck_1119.json', 'w'))
print(json.dumps(summ, indent=1)[:2500])
print('spots', len(spots)); [print(' ', s) for s in spots[:15]]
