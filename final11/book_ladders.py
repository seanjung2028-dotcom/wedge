"""Expected Kalshi ladders from the sportsbooks, for player markets Kalshi hasn't listed yet (Week 11, Wed Nov 18 pull).

Each book's main line is de-vigged (Over / (Over + Under)); the player's distribution is fit to clear every book's line at
its no-vig chance (gamma for yards with a CV from his own games shrunk toward a position prior, Poisson for catches; see
rh/w11_events.py), giving rh/book_fits_w11.json. Here that curve is priced on Kalshi's rung grid and moved onto Kalshi's
scale with a calibration fit on the rungs where both exist today: Kalshi's mid minus the books' chance by price band and market
family, and the Kalshi bid-ask spread seen at that price. The result is where a rung is likely to open, not a tradable price."""
import json, math, re, collections, unicodedata
import numpy as np
from scipy import stats
W = '/home/claude/wedger/'
BF = json.load(open(W + 'rh/book_fits_w11.json'))
KP = json.load(open(W + 'rh/kalshi_props_w11.json'))
AN = json.load(open(W + 'rh/an_w11.json'))
SER = {'KXNFLRECYDS': ('recyd', 'Receiving Yards'), 'KXNFLREC': ('rec', 'Receptions'), 'KXNFLRSHYDS': ('rushyd', 'Rushing Yards'),
       'KXNFLRRYDS': ('rryd', 'Rushing + Receiving Yards'), 'KXNFLPASSYDS': ('passyd', 'Passing Yards')}
MK = {v[1]: (s, v[0]) for s, v in SER.items()}
GRID = {'recyd': [10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150], 'rushyd': [10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150],
        'rryd': [20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150], 'rec': list(range(2, 12)), 'passyd': list(range(100, 425, 25))}
FIX = {'LA': 'LAR', 'WAS': 'WSH', 'JAC': 'JAX'}; KXC = {'JAX': 'JAC', 'WSH': 'WAS'}
CODES = {'ARI', 'LAR', 'LA', 'BAL', 'CLE', 'BUF', 'LV', 'CAR', 'PHI', 'CHI', 'ATL', 'DAL', 'GB', 'HOU', 'JAX', 'JAC', 'LAC', 'KC', 'NO', 'NYG', 'NYJ', 'NE', 'PIT', 'TB', 'TEN', 'IND', 'SF', 'WSH', 'WAS', 'MIN', 'MIA', 'CIN', 'DET', 'DEN', 'SEA'}
def norm(n):
    n = unicodedata.normalize('NFKD', str(n)).encode('ascii', 'ignore').decode().lower().replace('.', '').replace("'", '').replace('-', ' ')
    return re.sub(r'\s+', ' ', re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', n)).strip()
def split_game(code):
    for i in range(2, len(code) - 1):
        a, h = code[:i], code[i:]
        if a in CODES and h in CODES: return FIX.get(a, a), FIX.get(h, h)
def sf_of(f):
    if f.get('dist') == 'gamma': k = f['k']; th = f['mean'] / k; return lambda x: float(stats.gamma.sf(x, k, scale=th))
    lam = f['mean']; return lambda x: float(1 - stats.poisson.cdf(math.floor(x), lam))
FITS = {}   # (game, market, norm(player)) -> (fit, display name)
for key, f in BF.items():
    game, market, player = key.split('|')
    if market in MK and 'mean' in f: FITS[(game, market, norm(player))] = (f, player)
# book detail per player-market, for the write-up
DET = {}
LBL = {'Receiving Yards': 'Receiving Yards', 'Receptions': 'Receptions', 'Rush Yards': 'Rushing Yards', 'Rush + Rec Yards': 'Rushing + Receiving Yards', 'Pass Yards': 'Passing Yards'}
BOOKN = AN.get('books', {})
for label, g, player, team, pos, books in AN['rows']:
    if label not in LBL: continue
    a, h = (FIX.get(x, x) for x in g.split('@'))
    imp = lambda o: 100 / (o + 100) if o > 0 else -o / (-o + 100)
    bl = [(BOOKN.get(str(b), str(b)), L, o, u, imp(o) / (imp(o) + imp(u))) for b, L, o, u, _ in books]
    DET[(f'{a} @ {h}', LBL[label], norm(player))] = {'n': len(bl), 'line': round(float(np.mean([x[1] for x in bl])), 1), 'lines': sorted({x[1] for x in bl}),
                                                    'p_over': round(float(np.mean([x[4] for x in bl])), 3),
                                                    'text': '; '.join(f"{n} {L:g} o{'+' if o > 0 else ''}{o}/u{'+' if u > 0 else ''}{u}" for n, L, o, u, _ in bl), 'team': team, 'pos': pos}
# ---- calibration on rungs both list today
pairs, kal_have = [], set()
for ser, rows in KP['series'].items():
    if ser not in SER: continue
    stat, market = SER[ser]
    for ev, tick, sub, strike, ya, yb, na, last, vol, st_ in rows:
        g = split_game(ev.split('-')[1][7:])
        if not g: continue
        game = f'{g[0]} @ {g[1]}'; nm = norm(sub.split(':')[0]); kal_have.add((game, market, nm))
        ya, yb = round(100 * float(ya)), round(100 * float(yb))
        if not (yb > 0 and ya > 0 and ya - yb <= 8): continue
        f = FITS.get((game, market, nm))
        if not f: continue
        k = int(strike + 0.5); bp = 100 * sf_of(f[0])(k - 0.5)
        pairs.append({'stat': stat, 'game': game, 'player': f[1], 'k': k, 'book': bp, 'mid': (ya + yb) / 2, 'spread': ya - yb, 'ask': ya})
P = [x for x in pairs if 3 <= x['book'] <= 97 and 3 <= x['mid'] <= 97]
# Kalshi's mid minus the books' chance, by price band and market family (catches, passing, all other yards). Kalshi prices the
# likely rungs (low thresholds) below the books' curve: the gamma's lower tail is thinner than real games, where a player can
# be held to nothing. A band needs 8+ pairs; otherwise no adjustment. Out of sample (leave one game out) this cuts the miss
# from 3.44 to 3.09 points.
BANDS = [(3, 12), (12, 20), (20, 35), (35, 50), (50, 65), (65, 80), (80, 90), (90, 97.01)]
grp = lambda s: 'rec' if s == 'rec' else ('pass' if s == 'passyd' else 'yds')
band = lambda m: next((i for i, (lo, hi) in enumerate(BANDS) if lo <= m < hi), len(BANDS) - 1)
def fit_gaps(rows):
    g = collections.defaultdict(list)
    for x in rows: g[(grp(x['stat']), band(x['book']))].append(x['mid'] - x['book'])
    return {k: float(np.mean(v)) for k, v in g.items() if len(v) >= 8}
GAP = fit_gaps(P)
pred = lambda bp, stat: bp + GAP.get((grp(stat), band(bp)), 0.0)
e_raw, e_cal = [], []
for gm in sorted({x['game'] for x in P}):
    G_ = fit_gaps([x for x in P if x['game'] != gm])
    for x in (x for x in P if x['game'] == gm):
        e_raw.append(abs(x['mid'] - x['book'])); e_cal.append(abs(x['mid'] - (x['book'] + G_.get((grp(x['stat']), band(x['book'])), 0.0))))
SPREAD = {}
for i, (lo, hi) in enumerate(BANDS):
    s_ = [x['spread'] for x in P if lo <= x['mid'] < hi]
    SPREAD[i] = float(np.median(s_)) if len(s_) >= 8 else 5.0
by_stat = {}
for st_ in sorted({x['stat'] for x in P}):
    q = [x for x in P if x['stat'] == st_]
    by_stat[st_] = {'n': len(q), 'gap': round(float(np.mean([x['mid'] - x['book'] for x in q])), 2), 'mae': round(float(np.mean([abs(x['mid'] - x['book']) for x in q])), 2)}
CAL = {'n': len(P), 'players': len({(x['game'], x['player'], x['stat']) for x in P}), 'games': len({x['game'] for x in P}),
       'gap_mean': round(float(np.mean([x['mid'] - x['book'] for x in P])), 2), 'mae_raw': round(float(np.mean(e_raw)), 2), 'mae_cal': round(float(np.mean(e_cal)), 2),
       'within3': round(100 * float(np.mean([e <= 3 for e in e_cal])), 1), 'spread_med': float(np.median([x['spread'] for x in P])), 'by_stat': by_stat,
       'bands': [{'band': f'{lo}-{int(hi)}', **{g_: (round(GAP[(g_, i)], 1) if (g_, i) in GAP else None) for g_ in ('yds', 'rec', 'pass')},
                  'n': int(sum(lo <= x['book'] < hi for x in P)), 'spread': SPREAD[i]} for i, (lo, hi) in enumerate(BANDS)]}
# ---- expected ladders where Kalshi has nothing for the player in that market
LAD = collections.defaultdict(list); META = {}
for (game, market, nm), (f, player) in FITS.items():
    if (game, market, nm) in kal_have: continue
    ser, stat = MK[market]; a, h = game.split(' @ '); code = KXC.get(a, a) + KXC.get(h, h)
    sf = sf_of(f)
    for k in GRID[stat]:
        bp = 100 * sf(k - 0.5)
        if not (5 <= bp <= 95): continue
        m = min(97.0, max(3.0, pred(bp, stat))); s = SPREAD[band(m)]
        ya = int(math.ceil(m + s / 2 - 1e-9)); yb = int(math.floor(m - s / 2 + 1e-9)); yb = min(yb, ya - 1)
        LAD[(code, player, stat)].append((k, ya, yb, 100 - yb, f'BOOKS-{ser}-{code}-{nm.replace(" ", "")}-{k}', round(bp, 1), round(m, 1)))
    META[(code, player, stat)] = {'fit': f, 'det': DET.get((game, market, nm)), 'game': game}
if __name__ == '__main__':
    print('calibration', {k: v for k, v in CAL.items() if k != 'bands'})
    for b_ in CAL['bands']: print('  ', b_)
    print('book-only ladders', len(LAD), collections.Counter(k[2] for k in LAD), 'rungs', sum(len(v) for v in LAD.values()))
    print('by game', collections.Counter(META[k]['game'] for k in LAD))
