"""Build rh_events_w12.json for the Thu Oct 22 morning refresh (also used Wed Oct 21).

1. Robinhood game lines: every Week 7 game-line event page (moneyline, spreads, totals, quarters, halves, overtime...).
2. Robinhood player props: Robinhood lists the Kalshi player-prop ladders (same contracts, same order book - e.g. Brock
   Bowers 70+ rec yds: 47c bid / 53c ask on both). Pulled from the exchange's market list: receiving, rushing and
   passing yards, passing TDs, receptions (NE @ CHI only so far), rush + rec yards, and 1+/2+/3+ touchdowns.
3. Where Robinhood has nothing for a player in a market, a Robinhood-style ladder priced from the sportsbooks
   (DraftKings, FanDuel, BetMGM, Caesars, BetRivers via Action Network): fit the player's distribution so each book's
   line clears at that book's no-vig Over chance (yards: gamma with a CV from his own 2025-26 games shrunk toward a
   position prior; receptions / pass TDs / INTs: Poisson), then price rungs on Robinhood's grid - yards in X+ steps of
   5 (pass yards 25), counts in steps of 1. Anytime TD = average implied Yes chance, as before.
Contract row: [name, yes_ask, yes_bid, no_ask, last, tradable, quote_state, description, source, book_lines]
"""
import json, re, math, statistics, collections, unicodedata
import pandas as pd
from scipy import stats, optimize

B = '/home/claude/wedger/rh/'
N = '/home/claude/wedger/dl18/'
rh = json.load(open(B + 'rh_w12_gamelines.json'))
kx = json.load(open(B + 'kalshi_props_w12.json'))
an = json.load(open(B + 'an_w12.json'))

CITY = {'ARI': 'Arizona', 'LAR': 'Los Angeles R', 'BAL': 'Baltimore', 'CLE': 'Cleveland', 'BUF': 'Buffalo', 'LV': 'Las Vegas',
        'CAR': 'Carolina', 'PHI': 'Philadelphia', 'CHI': 'Chicago', 'ATL': 'Atlanta', 'DAL': 'Dallas', 'GB': 'Green Bay',
        'HOU': 'Houston', 'JAX': 'Jacksonville', 'LAC': 'Los Angeles C', 'KC': 'Kansas City', 'NO': 'New Orleans',
        'NYG': 'New York G', 'NYJ': 'New York J', 'NE': 'New England', 'PIT': 'Pittsburgh', 'TB': 'Tampa Bay',
        'TEN': 'Tennessee', 'IND': 'Indianapolis', 'SF': 'San Francisco', 'WSH': 'Washington', 'MIN': 'Minnesota',
        'MIA': 'Miami', 'CIN': 'Cincinnati', 'DET': 'Detroit', 'DEN': 'Denver', 'SEA': 'Seattle'}
FIX = {'LA': 'LAR', 'WAS': 'WSH', 'JAC': 'JAX'}
BOOK = {49: 'Caesars', 68: 'DraftKings', 69: 'FanDuel', 71: 'BetRivers', 75: 'BetMGM', 15: 'Books consensus',
        # Action Network's Illinois book ids (Wed Nov 18 pull)
        1538: 'DraftKings', 270: 'FanDuel', 282: 'BetMGM', 279: 'Caesars', 262: 'BetRivers', 3646: 'Hard Rock', 3915: 'bet365', 2990: 'Fanatics'}

def norm(n):
    n = unicodedata.normalize('NFKD', str(n)).encode('ascii', 'ignore').decode().lower().replace('.', '').replace("'", '').replace('-', ' ')
    n = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', n)
    return re.sub(r'\s+', ' ', n).strip()

price = lambda x: None if x in (None, '') or float(x) <= 0 or float(x) >= 1 else f'{float(x):.2f}'

# ---------------- 1. Robinhood game lines ----------------
events = []
for key, name, eid, state, parent, etype, cs in rh['events']:
    out = [[short or nm, price(ya), price(yb), price(na), price(last),
            'TRADABLE' if trad == 'EVENT_CONTRACT_TRADABILITY_TRADABLE' else trad, qst, desc,
            ('Sportsbook consensus (game lines)' if qst == 'consensus' else 'Robinhood'), vol if qst == 'consensus' else '', f'{float(ya):.4f}' if qst == 'consensus' else '']
           for cid, nm, short, trad, ya, yb, na, last, qst, desc, vol in cs]
    events.append([key, name, eid, state, out])

# books' consensus fair chance for each Robinhood game-line contract (spreads from 8 books + Kalshi, DraftKings and Kalshi
# moneylines, DraftKings total): normal margin SD 12.6, total SD 13.1 (2021-25 results vs closing lines)
CONS = json.load(open(B + 'rh_w12_consensus.json'))['consensus']
CITY_R = {v: k for k, v in CITY.items()}
for ev_ in events:
    name = ev_[1]
    head = re.sub(r' (Spreads|Totals)$', '', name.split(':')[0])
    parts = head.split(' vs ')
    if len(parts) != 2 or parts[0] not in CITY_R or parts[1] not in CITY_R: continue
    a_, h_ = CITY_R[parts[0]], CITY_R[parts[1]]
    c_ = CONS.get(f'{a_} @ {h_}')
    if not c_: continue
    for ct_ in ev_[4]:
        nm_ = ct_[0]; p_ = None; det_ = ''
        m_ = re.match(r'^(.*) wins by over ([\d.]+) points$', nm_)
        if name.endswith('Spreads') and m_ and m_.group(1) in CITY_R:
            t_ = CITY_R[m_.group(1)]; mu_ = c_['home_margin'] if t_ == h_ else -c_['home_margin']
            p_ = 1 - stats.norm.cdf(float(m_.group(2)), mu_, 12.6); det_ = f"Books: {h_} by {c_['home_margin']:+.1f} — " + '; '.join(c_['spread_books'])
        elif name.endswith('Totals') and re.match(r'^Over ([\d.]+) points$', nm_):
            p_ = 1 - stats.norm.cdf(float(re.match(r'^Over ([\d.]+) points$', nm_).group(1)), c_['total'], 13.1); det_ = f"Books: total {c_['total']:.1f} — " + c_['total_note']
        elif ':' not in name and not name.endswith(('Spreads', 'Totals')) and nm_ in (a_, h_, {'LAR': 'LA', 'WSH': 'WAS', 'JAX': 'JAC'}.get(a_), {'LAR': 'LA', 'WSH': 'WAS', 'JAX': 'JAC'}.get(h_)):
            t_ = {'LA': 'LAR', 'WAS': 'WSH', 'JAC': 'JAX'}.get(nm_, nm_)
            p_ = c_['p_home'] if t_ == h_ else 1 - c_['p_home']
            det_ = f"Books: {h_} {100 * c_['p_home']:.0f}% (DraftKings {100 * c_['p_dk']:.0f}%" + (f", Kalshi {100 * c_['p_kalshi']:.0f}%" if c_.get('p_kalshi') else '') + f", spread {100 * c_['p_spread']:.0f}%)"
        if p_ is not None:
            while len(ct_) < 11: ct_.append('')
            ct_[9] = det_; ct_[10] = f'{p_:.4f}'

# ---------------- 2. Robinhood player props (exchange ladders) ----------------
CODES = set(CITY) | {'LA', 'JAC', 'WAS'}
def split_game(code):
    for i in range(2, len(code) - 1):
        a, h = code[:i], code[i:]
        if a in CODES and h in CODES: return FIX.get(a, a), FIX.get(h, h)
    return None
SER = {'KXNFLRECYDS': ('Receiving Yards', 'Receiving Yards'), 'KXNFLRSHYDS': ('Rushing Yards', 'Rush Yards'),
       'KXNFLPASSYDS': ('Passing Yards', 'Pass Yards'), 'KXNFLPASSTDS': ('Passing Touchdowns', 'Pass TDs'),
       'KXNFLREC': ('Receptions', 'Receptions'), 'KXNFLRRYDS': ('Rushing + Receiving Yards', 'Rush+Receiving Yards')}
TDM = {0.5: 'Anytime Touchdown', 1.5: '2+ Touchdowns', 2.5: '3+ Touchdowns'}
props = collections.defaultdict(list)          # (away, home, market) -> contracts
have = set()                                    # (away, home, market, norm(player))
for ser, rows in kx['series'].items():
    for ev_t, tick, sub, strike, ya, yb, na, last, vol, status in rows:
        g = split_game(ev_t.split('-')[1][7:])
        if not g: continue
        player = sub.split(':')[0].strip()
        if 'D/ST' in player: continue
        if ser == 'KXNFLTD':
            market = TDM.get(strike)
            if not market: continue
            cname = player
            desc = f'{player} scores {int(strike + 0.5)}+ rushing/receiving TDs ({g[0]} @ {g[1]})'
        elif ser in SER:
            market, suffix = SER[ser]
            cname = f'{player}: Over {strike} {suffix}'
            desc = f'{player} {int(strike + 0.5)}+ {suffix.lower()} ({g[0]} @ {g[1]})'
        else:
            continue
        props[(g[0], g[1], market)].append([cname, price(ya), price(yb), price(na), price(last),
                                            'TRADABLE' if status == 'active' else status, 'active' if status == 'active' else status,
                                            desc, 'Robinhood', '', '', (g[0], g[1], market, norm(player), strike)])
        have.add((g[0], g[1], market, norm(player)))

# ---------------- 3. Robinhood-style ladders from the books ----------------
st = pd.concat([pd.read_csv(B + '../nflverse_dl3/stats_player_week_2025.csv', low_memory=False), pd.read_csv(N + 'stats_player_week_2026.csv', low_memory=False)], ignore_index=True)
st = st[(st['season_type'] == 'REG') & ~((st['season'] == 2026) & (st['week'] > 11))]
st['nm'] = st['player_display_name'].map(norm)
st['rr_yards'] = st['rushing_yards'].fillna(0) + st['receiving_yards'].fillna(0)
HCOL = {'Receiving Yards': 'receiving_yards', 'Rush Yards': 'rushing_yards', 'Pass Yards': 'passing_yards', 'Rush + Rec Yards': 'rr_yards'}
CV_PRIOR = {('Receiving Yards', 'WR'): 0.70, ('Receiving Yards', 'TE'): 0.75, ('Receiving Yards', 'RB'): 0.95,
            ('Rush Yards', 'RB'): 0.55, ('Rush Yards', 'QB'): 0.85, ('Rush Yards', 'WR'): 1.2, ('Pass Yards', 'QB'): 0.28,
            ('Rush + Rec Yards', 'RB'): 0.50, ('Rush + Rec Yards', 'WR'): 0.65, ('Rush + Rec Yards', 'TE'): 0.70, ('Rush + Rec Yards', 'QB'): 0.80}

def player_cv(player, label, pos):
    prior = CV_PRIOR.get((label, pos), 0.8)
    s = st[st['nm'] == norm(player)][HCOL[label]].astype(float)
    s = s[s > 0] if label != 'Pass Yards' else s[s > 40]
    if len(s) < 4 or s.mean() <= 0: return prior, 0
    cv = min(1.6, max(0.2, s.std(ddof=1) / s.mean()))
    w = len(s) / (len(s) + 8)
    return w * cv + (1 - w) * prior, len(s)

def imp(o):
    if o is None: return None
    return 100 / (o + 100) if o > 0 else -o / (-o + 100)

MARKET = {'Receiving Yards': ('Receiving Yards', 'Receiving Yards', 'gamma', 5),
          'Receptions': ('Receptions', 'Receptions', 'poisson', 1),
          'Rush Yards': ('Rushing Yards', 'Rush Yards', 'gamma', 5),
          'Pass Yards': ('Passing Yards', 'Pass Yards', 'gamma', 25),
          'Rush + Rec Yards': ('Rushing + Receiving Yards', 'Rush+Receiving Yards', 'gamma', 5),
          'Pass TDs': ('Passing Touchdowns', 'Pass TDs', 'poisson', 1),
          'Interceptions': ('Interceptions', 'Interceptions', 'poisson', 1),
          'Anytime Touchdown': ('Anytime Touchdown', None, None, None)}
ALIAS = {'Kenneth Gainwell': 'Kenny Gainwell'}
ladders, skipped, fits = collections.defaultdict(list), collections.Counter(), []
FAIR = {}          # (away, home, market, norm(player)) -> (sf, mean, detail) from the books, for every listed player
BOOKFITS = {}      # 'AWAY @ HOME|market|player' -> book-implied mean and dispersion (model prior)
for label, g, player, team, pos, books in an['rows']:
    if not player.strip() or player.strip().endswith('Defense'):
        skipped['team defense'] += 1; continue
    player = ALIAS.get(player, player)
    away, home = (FIX.get(x, x) for x in g.split('@'))
    market, suffix, dist, step = MARKET[label]
    listed = (away, home, market, norm(player)) in have
    if label == 'Anytime Touchdown':
        ps = [imp(b[4]) for b in books if b[4] is not None]
        if not ps: skipped['no price'] += 1; continue
        p = statistics.mean(ps)
        names = [BOOK[b[0]] for b in books if b[4] is not None]
        detail = '; '.join(f"{BOOK[b[0]]} {'+' if b[4] > 0 else ''}{b[4]}" for b in books if b[4] is not None)
        FAIR[(away, home, market, norm(player))] = (lambda x, p=p: p, None, f"Avg of {len(ps)} books: {detail}")
        BOOKFITS[f'{away} @ {home}|{market}|{player}'] = {'p_yes': round(p, 4), 'n_books': len(ps)}
        if listed: skipped['Robinhood lists him'] += 1; continue
        ladders[(away, home, market)].append([player, f'{p:.4f}', None, None, None, 'TRADABLE', 'consensus',
                                              f'{player} scores a rushing or receiving TD ({away} @ {home}); sportsbook average',
                                              f"Avg of {len(ps)} books ({', '.join(names)})", detail])
        continue
    usable = [(b[0], b[1], imp(b[2]), imp(b[3])) for b in books if b[1] is not None and b[2] is not None and b[3] is not None]
    if not usable: skipped['one-sided'] += 1; continue
    pts = [(L, io / (io + iu)) for _, L, io, iu in usable]
    if dist == 'gamma':
        cv, n_hist = player_cv(player, label, pos)
        k = 1 / cv ** 2
        theta = statistics.mean(L / stats.gamma.isf(p, k) for L, p in pts)
        sf = lambda x, k=k, theta=theta: float(stats.gamma.sf(x, k, scale=theta))
        mean = k * theta
        model = f'gamma, mean {mean:.1f}, CV {cv:.2f}'
    else:
        def lam_for(L, p):
            f = lambda lam: (1 - stats.poisson.cdf(math.floor(L), lam)) - p
            return optimize.brentq(f, 1e-4, 60)
        lam = statistics.mean(lam_for(L, p) for L, p in pts)
        sf = lambda x, lam=lam: float(1 - stats.poisson.cdf(math.floor(x), lam))
        mean = lam; k = None
        model = f'Poisson, mean {lam:.2f}'
    detail = '; '.join(f"{BOOK[b[0]]} {b[1]} o{'+' if b[2] > 0 else ''}{b[2]}/u{'+' if b[3] > 0 else ''}{b[3]}"
                       for b in books if b[1] is not None and b[2] is not None and b[3] is not None)
    src = (f"Robinhood-style rung priced from {len(usable)} books ({', '.join(BOOK[u[0]] for u in usable)}): "
           f"avg line {statistics.mean(L for L, _ in pts):.1f}, Over {100 * statistics.mean(p for _, p in pts):.0f}% no-vig; {model}")
    FAIR[(away, home, market, norm(player))] = (sf, mean, detail)
    BOOKFITS[f'{away} @ {home}|{market}|{player}'] = {'mean': round(mean, 2), 'dist': dist, 'k': round(k, 3) if k else None,
                                                      'line': round(statistics.mean(L for L, _ in pts), 2),
                                                      'p_over': round(statistics.mean(p for _, p in pts), 4), 'n_books': len(usable)}
    if listed:
        skipped['Robinhood lists him'] += 1; continue
    rung = step if dist == 'gamma' else 1
    x = rung
    while x <= (500 if step == 25 else (400 if dist == 'gamma' else 20)):
        pr = sf(x - 0.5)
        if 0.05 <= pr <= 0.95:
            ladders[(away, home, market)].append([f'{player}: Over {x - 0.5} {suffix}', f'{pr:.4f}', None, None, None, 'TRADABLE',
                                                  'consensus', f'{player} {x}+ {suffix.lower()} ({away} @ {home}); Robinhood-style rung from sportsbook lines',
                                                  src, detail, f'{pr:.4f}'])
        x += rung
    fits.append((label, player, g, pts, round(mean, 2)))

# books' fair chance for each Robinhood rung (same player, same threshold), so the page can show cheap vs rich prices
attached = 0
for cs in props.values():
    for c in cs:
        a, h, mk, nm, strike = c[11]
        f = FAIR.get((a, h, mk, nm))
        if f and mk not in ('2+ Touchdowns', '3+ Touchdowns'):
            c[10] = f'{f[0](strike):.4f}'; c[9] = f[2]; attached += 1
        del c[11]
print('book fair values attached to Robinhood rungs', attached)
json.dump(BOOKFITS, open(B + 'book_fits_w12.json', 'w'))
for (away, home, mk), cs in sorted(props.items()):
    events.append([f'rh-props-{away}-{home}-{mk}'.lower().replace(' ', '-'), f'{CITY[away]} vs {CITY[home]}: {mk}', None, 'ACTIVE', cs])
for (away, home, mk), cs in sorted(ladders.items()):
    events.append([f'books-{away}-{home}-{mk}'.lower().replace(' ', '-'), f'{CITY[away]} vs {CITY[home]}: {mk}', None, 'CONSENSUS', cs])

json.dump(events, open(B + 'rh_events_w12.json', 'w'))
json.dump(fits, open(B + 'ladder_fits_w12.json', 'w'))
print('events', len(events))
print('robinhood game-line contracts', sum(len(e[4]) for e in events[:len(rh['events'])]))
print('robinhood prop contracts', sum(len(v) for v in props.values()), collections.Counter(k[2] for k, v in props.items() for _ in v))
print('book ladder contracts', sum(len(v) for v in ladders.values()), collections.Counter(k[2] for k, v in ladders.items() for _ in v))
print('book ladders by game', collections.Counter(f'{k[0]}@{k[1]}' for k, v in ladders.items() for _ in v))
print('skipped', skipped)
