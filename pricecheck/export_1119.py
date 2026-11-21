"""Flatten pricecheck_1119.json into the two files the Week 11 Price Check page reads.
props_1119.json: one row per player market on Sunday's slate. gamelines_1119.json: one row per side of each game line.
All prices are the cost of a $1 payout in cents: a sportsbook's implied chance from its American odds (vig included), Kalshi's ask
plus its taker fee (7% x p x (1 - p)), Robinhood's ask plus its 1-cent commission (any exchange fee not included)."""
import json, collections
W = '/home/claude/wedger/pricecheck/'
P = json.load(open(W + 'pricecheck_1119.json'))
BK = [('dk', 'DraftKings'), ('fd', 'FanDuel'), ('mgm', 'BetMGM'), ('fan', 'Fanatics'), ('czr', 'Caesars')]
MK = {'recyd': 'Receiving yards', 'rec': 'Receptions', 'rushyd': 'Rushing yards', 'rryd': 'Rush + rec yards', 'passyd': 'Passing yards', 'ptd': 'Passing TDs', 'atd': 'Anytime TD'}
CODE = {'MIA @ BUF': 'MIABUF', 'BAL @ CAR': 'BALCAR', 'NO @ CHI': 'NOCHI', 'TEN @ DAL': 'TENDAL', 'TB @ DET': 'TBDET', 'ARI @ KC': 'ARIKC',
        'JAX @ NYG': 'JAXNYG', 'NYJ @ LAC': 'NYJLAC', 'LV @ DEN': 'LVDEN', 'PIT @ PHI': 'PITPHI', 'MIN @ SF': 'MINSF'}
kfee = lambda p: 7 * (p / 100) * (1 - p / 100)
r1 = lambda x: None if x is None else round(x, 1)
props = []
for x in P['props']:
    L = x['L']; b = x['b']
    row = {'key': f"{CODE[x['g']]}-{x['p'].lower().replace(' ', '').replace('.', '').replace(chr(39), '')}-{x['st']}", 'game': x['g'], 'kick': x['ko'],
           'player': x['p'], 'team': x['team'], 'pos': x['pos'], 'market': MK[x['st']], 'line': L,
           'fair': x['fair'], 'fair_under': r1(100 - x['fair']) if x['fair'] is not None else None}
    cnt = collections.Counter(v[0] for v in b.values())
    row['books_at_line'] = sum(1 for v in b.values() if v[0] == L)
    row['other_lines'] = ', '.join(f"{n} at {v[0]:g}" for n, v in b.items() if v[0] != L) if x['st'] != 'atd' else ''
    for k, n in BK:
        v = b.get(n)
        row[k + '_line'] = v[0] if v else None
        row[k + '_over'] = v[1] if v and v[0] == L else None
        row[k + '_under'] = v[2] if v and v[0] == L else None
    kx, rx = x['k']['x'], x['r']['x']
    row['k_over'] = r1(kx[0] + kfee(kx[0])) if kx else None
    row['k_under'] = r1(kx[2] + kfee(kx[2])) if kx and kx[1] and kx[2] is not None else None   # no bid on Yes means no No offer
    row['r_over'] = r1(rx[0] + 1) if rx and rx[0] is not None else None
    row['r_under'] = r1(rx[2] + 1) if rx and rx[1] is not None and rx[2] is not None else None
    row['k_mid'] = x['k']['mid']; row['r_mid'] = x['r']['mid']
    row['k_rungs'] = x['k']['n']; row['r_rungs'] = x['r']['n']
    row['k_vs_fair'] = x['kg']; row['r_vs_fair'] = x['rg']
    row['k_vs_fair_u'] = r1(-x['kg']) if x['kg'] is not None else None
    row['r_vs_fair_u'] = r1(-x['rg']) if x['rg'] is not None else None
    ov = [(n, row[k + '_over']) for k, n in BK if row[k + '_over'] is not None] + [('Kalshi', row['k_over']), ('Robinhood', row['r_over'])]
    un = [(n, row[k + '_under']) for k, n in BK if row[k + '_under'] is not None] + [('Kalshi', row['k_under']), ('Robinhood', row['r_under'])]
    ov = [t for t in ov if t[1] is not None]; un = [t for t in un if t[1] is not None]
    bo = min(ov, key=lambda t: t[1]) if ov else None; bu = min(un, key=lambda t: t[1]) if un else None
    row['best_over'] = bo[0] if bo else None; row['best_over_cost'] = bo[1] if bo else None
    row['best_under'] = bu[0] if bu else None; row['best_under_cost'] = bu[1] if bu else None
    row['card'] = x['card']
    props.append(row)
props.sort(key=lambda r: (list(CODE).index(r['game']), list(MK.values()).index(r['market']), r['player']))
assert len({r['key'] for r in props}) == len(props)
games = []
kq = lambda q: r1(q + kfee(q)) if q is not None else None
for g in P['games']:
    c = CODE[g['g']]
    def add(market, side, line, role, fair, books, k, r, near=''):
        row = {'key': f"{c}-{market[:2].lower()}-{role}", 'game': g['g'], 'kick': g['ko'], 'market': market, 'side': side, 'line': line, 'role': role, 'fair': fair}
        for kk, n in BK: row[kk] = books.get(n)
        row['kalshi'] = k; row['robinhood'] = r; row['near'] = near
        opts = [(n, books.get(n)) for _, n in BK] + [('Kalshi', k), ('Robinhood', r)]
        opts = [t for t in opts if t[1] is not None]
        bt = min(opts, key=lambda t: t[1]) if opts else None
        row['best'] = bt[0] if bt else None; row['best_cost'] = bt[1] if bt else None
        games.append(row)
    for m in g['ml']:
        role = 'fav' if m['t'] == g['fav'] else 'dog'
        add('Moneyline', f"{m['t']} wins", None, 'ml-' + role, m['fair'], m['b'], kq(m['k'][0]) if m['k'] else None, (m['r'][0] + 1) if m['r'] and m['r'][0] is not None else None)
    for m in g['sp']:
        S = g['spread']; exact = [q for q in m['k'] if q[0] == S]; rexact = [q for q in m['r'] if q[0] == S]
        if m['side'] == 'fav':
            k = kq(exact[0][1]) if exact and exact[0][1] is not None else None; r = (rexact[0][1] + 1) if rexact and rexact[0][1] is not None else None
            side = f"{m['t']} −{S:g}"
        else:
            k = kq(exact[0][3]) if exact and exact[0][3] is not None else None; r = (rexact[0][3] + 1) if rexact and rexact[0][3] is not None else None
            side = f"{m['t']} +{S:g}"
        near = ''
        if not exact:
            pick = (lambda q: q[1]) if m['side'] == 'fav' else (lambda q: q[3])
            near = 'Kalshi ' + ', '.join(f"{pick(q)}¢ at {q[0]:g}" for q in m['k'] if pick(q) is not None) + '; Robinhood ' + ', '.join(f"{pick(q)}¢ at {q[0]:g}" for q in m['r'] if pick(q) is not None)
            near = near.replace('Kalshi ;', 'Kalshi none;')
        add('Spread', side, S, 'sp-' + m['side'], m['fair'], m['b'], k, r, near)
    for m in g['tot']:
        T = g['total']; exact = [q for q in m['k'] if q[0] == T]; rexact = [q for q in m['r'] if q[0] == T]
        pick = (lambda q: q[1]) if m['side'] == 'over' else (lambda q: q[3])
        k = kq(pick(exact[0])) if exact and pick(exact[0]) is not None else None; r = (pick(rexact[0]) + 1) if rexact and pick(rexact[0]) is not None else None
        near = '' if exact else 'Kalshi ' + ', '.join(f"{pick(q)}¢ at {q[0]:g}" for q in m['k'] if pick(q) is not None) + '; Robinhood ' + ', '.join(f"{pick(q)}¢ at {q[0]:g}" for q in m['r'] if pick(q) is not None)
        add('Total', f"{m['side'].title()} {T:g}", T, 'to-' + m['side'], m['fair'], m['b'], k, r, near)
assert len({r['key'] for r in games}) == len(games)
AT = P['summary']['at']
META = [{'label': 'Prices checked', 'value': 'Thu Nov 19, 2026: Kalshi 6:04 AM CT, sportsbooks 6:06 AM CT, Robinhood 6:34 AM CT'},
        {'label': 'Sources', 'value': "Kalshi's public market data; Robinhood's public prediction-market quotes; DraftKings, FanDuel, BetMGM, Fanatics and Caesars Illinois odds as published by Action Network"},
        {'label': 'Prices', 'value': "Cost of a $1 payout in cents. Sportsbooks: the implied chance of the American odds, vig included. Kalshi: the ask plus its taker fee, 7% x p x (1 - p). Robinhood: the ask plus its 1-cent commission; any exchange fee is not included."},
        {'label': 'Books\' line and fair', 'value': "The line most books post; fair is the average across books at that line of the Over's chance with the vig removed. Anytime TD has no fair, since the books only offer Yes."},
        {'label': 'Kalshi and Robinhood rungs', 'value': "Kalshi's 'k+' rung counts as Over k - 0.5; Robinhood's 'Over x' as Over x. A price is shown only where a rung sits exactly on the books' line; the midpoint is interpolated between the two rungs around it."}]
def dump(path, rows, extra):
    body = '{"meta": ' + json.dumps(META + extra, ensure_ascii=False) + ',\n"rows": [\n' + ',\n'.join(json.dumps(r, ensure_ascii=False) for r in rows) + '\n]}\n'
    open(path, 'w').write(body)
dump(W + 'props_1119.json', props, [])
dump(W + 'gamelines_1119.json', games, [{'label': 'Spreads and totals', 'value': "At the books' number. Where it is a whole number, Kalshi and Robinhood have no rung there, and their prices half a point either side are listed under Nearby numbers."}])
import os
print(len(props), len(games), os.path.getsize(W + 'props_1119.json'), os.path.getsize(W + 'gamelines_1119.json'))
print(games[0]); print(games[2]); print([g for g in games if g['near']][:2]); print(props[0])
