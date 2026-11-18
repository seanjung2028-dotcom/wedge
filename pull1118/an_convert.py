"""Sportsbook props and game lines for Week 11 (Action Network, Illinois books, Wed Nov 18 2:46 PM CT) -> pull1118/an_w11.json,
in the an_w11 format the line pipeline reads: rows = [label, 'AWAY@HOME', player, team, pos, [[book, line, over, under, yes], ...]].
Books kept: DraftKings, FanDuel, BetMGM, Caesars, BetRivers, Hard Rock, bet365, Fanatics. Left out: Action's own consensus and
opening lines, PrizePicks (no odds) and Polymarket (a different contract)."""
import json, os, collections
H = os.path.dirname(os.path.abspath(__file__)) + '/'
BOOKS = {1538: 'DraftKings', 270: 'FanDuel', 282: 'BetMGM', 279: 'Caesars', 262: 'BetRivers', 3646: 'Hard Rock', 3915: 'bet365', 2990: 'Fanatics'}
KEEP = {'Receiving Yards', 'Receptions', 'Rush Yards', 'Pass Yards', 'Pass TDs', 'Anytime Touchdown', 'Rush + Rec Yards'}
raw = json.load(open(H + 'an_props_raw.json'))
nz = lambda o: None if o in (None, 0) else o
rows, drop = [], collections.Counter()
for label, g, player, team, pos, books in raw['rows']:
    if label not in KEEP: drop[label] += 1; continue
    bk = [[b, line, nz(o), nz(u), nz(y)] for b, line, o, u, y in books if b in BOOKS]
    if label == 'Anytime Touchdown': bk = [x for x in bk if x[4] is not None]
    else: bk = [x for x in bk if x[1] is not None and x[2] is not None and x[3] is not None]
    if not bk: drop['no two-sided book'] += 1; continue
    rows.append([label, g, player, team, pos, bk])
gl = json.load(open(H + 'an_glines_raw.json')); glines = []
for g, ko, bk in gl['g']:
    a, h = g.split('@'); books = {}
    for b, hs, ho, ao, tot, oo, uo, hml, aml in bk:
        if b not in BOOKS: continue
        books[str(b)] = {'spread': [['home', h, hs, ho], ['away', a, -hs, ao]], 'total': [['over', None, tot, oo], ['under', None, tot, uo]],
                         'moneyline': [['home', h, 0, hml], ['away', a, 0, aml]]}
    glines.append({'game': g, 'start': ko, 'status': 'scheduled', 'books': books})
json.dump({'rows': rows, 'picks': {}, 'glines': glines, 'at': raw['at'], 'books': {str(k): v for k, v in BOOKS.items()}, 'src': raw['src']}, open(H + 'an_w11.json', 'w'))
print('rows', len(rows), collections.Counter(r[0] for r in rows), 'dropped', dict(drop), 'glines', len(glines))
print('books per row', round(sum(len(r[5]) for r in rows) / len(rows), 1), collections.Counter(BOOKS[b[0]] for r in rows for b in r[5]))
