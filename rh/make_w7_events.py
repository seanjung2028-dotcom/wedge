"""Build rh_events_w7.json for the Week 7 refresh.

Robinhood contracts come first. Where Robinhood has no market for a game (player props for the
Sunday/Monday games right now), add a sportsbook-average contract built from DraftKings, FanDuel,
BetMGM, Caesars and BetRivers main lines (via Action Network): the average of the books' lines,
priced at the average no-vig probability of the Over (Anytime TD: average implied Yes probability).
Each contract row: [name, yes_ask, yes_bid, no_ask, last, tradable, quote_state, description, source]
"""
import json, collections, statistics

B = '/home/claude/wedger/rh/'
raw = json.load(open(B + 'rh_w7_raw_1021.json'))
an = json.load(open(B + 'an_w7.json'))

CITY = {'ARI': 'Arizona', 'LAR': 'Los Angeles R', 'BAL': 'Baltimore', 'CLE': 'Cleveland', 'BUF': 'Buffalo', 'LV': 'Las Vegas',
        'CAR': 'Carolina', 'PHI': 'Philadelphia', 'CHI': 'Chicago', 'ATL': 'Atlanta', 'DAL': 'Dallas', 'GB': 'Green Bay',
        'HOU': 'Houston', 'JAX': 'Jacksonville', 'LAC': 'Los Angeles C', 'KC': 'Kansas City', 'NO': 'New Orleans',
        'NYG': 'New York G', 'NYJ': 'New York J', 'NE': 'New England', 'PIT': 'Pittsburgh', 'TB': 'Tampa Bay',
        'TEN': 'Tennessee', 'IND': 'Indianapolis', 'SF': 'San Francisco', 'WSH': 'Washington', 'MIN': 'Minnesota',
        'MIA': 'Miami', 'CIN': 'Cincinnati', 'DET': 'Detroit', 'DEN': 'Denver', 'SEA': 'Seattle'}
FIX = {'LA': 'LAR', 'WAS': 'WSH'}
BOOK = {49: 'Caesars', 68: 'DraftKings', 69: 'FanDuel', 71: 'BetRivers', 75: 'BetMGM'}

# ---------------- Robinhood ----------------
events = []
rh_markets = collections.defaultdict(set)  # (away, home) -> set of Robinhood event types present
for key, name, eid, state, parent, etype, cs in raw['events']:
    out = []
    for cid, nm, short, trad, ya, yb, na, last, qst, desc, vol in cs:
        out.append([short or nm, ya, yb, na, last, 'TRADABLE' if trad == 'EVENT_CONTRACT_TRADABILITY_TRADABLE' else trad,
                    qst, desc, 'Robinhood'])
    events.append([key, name, eid, state, out])

# which Robinhood market types exist per game (by event display name)
for e in events:
    nm = e[1]
    head = nm.split(':')[0]
    for suffix in (' Spreads', ' Totals'):
        head = head.replace(suffix, '')
    teams = head.split(' vs ')
    if len(teams) == 2:
        mk = nm.split(': ', 1)[1] if ': ' in nm else ('Spreads' if nm.endswith('Spreads') else ('Totals' if nm.endswith('Totals') else 'Moneyline'))
        rh_markets[frozenset(teams)].add(mk)

# ---------------- sportsbook averages ----------------
def imp(o):
    if o is None: return None
    return 100 / (o + 100) if o > 0 else -o / (-o + 100)

MARKET = {  # Action Network label -> (Robinhood event market, contract stat suffix)
    'Receiving Yards': ('Receiving Yards', 'Receiving Yards'), 'Receptions': ('Receptions', 'Receptions'),
    'Rush Yards': ('Rushing Yards', 'Rush Yards'), 'Pass Yards': ('Passing Yards', 'Pass Yards'),
    'Pass TDs': ('Passing Touchdowns', 'Pass TDs'), 'Interceptions': ('Interceptions', 'Interceptions'),
    'Anytime Touchdown': ('Anytime Touchdown', None),
}

def snap_half(mean, lines):
    # nearest X.5 to the mean of the books' lines; ties go to the most common book line
    lo = int(mean // 1) - 0.5 if mean % 1 < 0.5 else int(mean // 1) + 0.5
    cands = sorted({lo, lo + 1, lo - 1}, key=lambda v: (abs(v - mean), -lines.count(v)))
    return cands[0]

cons = collections.defaultdict(list)  # (away, home, market) -> contracts
skipped = collections.Counter()
ALIAS = {'Kenneth Gainwell': 'Kenny Gainwell'}  # sportsbook name -> ESPN box-score name
for label, g, player, team, pos, books in an['rows']:
    if not player.strip() or player.strip().endswith('Defense'):
        skipped['team defense'] += 1; continue
    player = ALIAS.get(player, player)
    away, home = (FIX.get(x, x) for x in g.split('@'))
    rh_mk, stat = MARKET[label]
    if rh_mk in rh_markets.get(frozenset((CITY[away], CITY[home])), set()):
        skipped['Robinhood has this market'] += 1
        continue
    if label == 'Anytime Touchdown':
        ps = [imp(b[4]) for b in books if b[4] is not None]
        if not ps:
            skipped['no price'] += 1; continue
        p = statistics.mean(ps)
        src = f"Avg of {len(ps)} books ({', '.join(BOOK[b[0]] for b in books if b[4] is not None)})"
        detail = '; '.join(f"{BOOK[b[0]]} {'+' if b[4] > 0 else ''}{b[4]}" for b in books if b[4] is not None)
        cname = player
        desc = f'{player} scores a rushing or receiving touchdown ({away} @ {home}); sportsbook average'
    else:
        usable = [(b[0], b[1], imp(b[2]), imp(b[3])) for b in books if b[1] is not None and b[2] is not None and b[3] is not None]
        if not usable:
            skipped['one-sided'] += 1; continue
        lines = [u[1] for u in usable]
        line = snap_half(statistics.mean(lines), lines)
        p = statistics.mean(io / (io + iu) for _, _, io, iu in usable)
        src = f"Avg of {len(usable)} books ({', '.join(BOOK[u[0]] for u in usable)})"
        detail = '; '.join(f"{BOOK[b[0]]} {b[1]} o{'+' if b[2] > 0 else ''}{b[2]}/u{'+' if b[3] > 0 else ''}{b[3]}"
                           for b in books if b[1] is not None and b[2] is not None and b[3] is not None)
        cname = f'{player}: Over {line} {stat}'
        desc = f'{player} over {line} {stat.lower()} ({away} @ {home}); sportsbook average of lines {", ".join(str(l) for l in lines)}'
    ya = f'{p:.4f}'
    cons[(away, home, rh_mk)].append([cname, ya, None, None, None, 'TRADABLE', 'consensus', desc, src, detail])

for (away, home, mk), cs in sorted(cons.items()):
    events.append([f'consensus-{away}-{home}-{mk}'.lower().replace(' ', '-'), f'{CITY[away]} vs {CITY[home]}: {mk}', None, 'CONSENSUS', cs])

json.dump(events, open(B + 'rh_events_w7.json', 'w'))
print('events', len(events), 'robinhood contracts', sum(len(e[4]) for e in events if e[3] != 'CONSENSUS'),
      'consensus contracts', sum(len(e[4]) for e in events if e[3] == 'CONSENSUS'))
print('skipped', skipped)
print(collections.Counter((k[0] + '@' + k[1]) for k, v in cons.items() for _ in v))
print(collections.Counter(k[2] for k, v in cons.items() for _ in v))
