"""Which number predicts hits best? Week 11 test for the Week 12 card (Tue Nov 24). Every Kalshi rung on the Week 11
final-draft board (Sun Nov 22 10:32 AM CT, bt/w11_likely/rows.csv; Sunday and Monday games), graded from nflverse (nfl12/).
Models compared, all as the chance the exact side settles a winner:
  kalshi      Kalshi's own mid
  v6b         Wedge % as used (matchup lens + 5% research projection), the v1/v2 card number
  book        the sportsbooks' consensus: each book's main line de-vigged, the player's distribution fit to all of them
              (rh/book_fits_w11.json, same Sunday 10:34 AM pull), priced at the exact rung
  book+lens   the book chance moved by the lens's own shift (logit book + logit v6b - logit kalshi)
  avg         the logit average of book and v6b
Scored on log loss and Brier (all rungs, and the 60-90% band the card picks from), calibration, and the v2 card each would
have picked (best chance per player, 75c cap, 70% bar on the low end ~ middle here, checks, four per game).
Writes bt/w12_model/report.json."""
import json, math, re, collections, unicodedata
import numpy as np, pandas as pd
from scipy import stats
W = '/home/claude/wedger/'
D = pd.read_csv(W + 'bt/w11_likely/rows.csv')
def nn(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', s); return re.sub(r'[^a-z]', '', s)
FX = {'LA': 'LAR', 'WAS': 'WSH', 'JAC': 'JAX'}
st = pd.read_csv(W + 'nfl12/stats_player_week_2026.csv', low_memory=False); st = st[(st.week == 11) & (st.season_type == 'REG')].copy()
st['team'] = st.team.map(lambda t: FX.get(t, t)); st['k'] = st.player_display_name.map(nn)
for c in ('receptions', 'receiving_yards', 'rushing_yards'): st[c] = pd.to_numeric(st[c], errors='coerce').fillna(0)
sn = pd.read_csv(W + 'nfl12/snap_counts_2026.csv'); sn = sn[sn.week == 11]
PLAYED = {nn(p) for p, o in zip(sn.player, sn.offense_snaps) if (o or 0) > 0}
VAL = {}
for r in st.itertuples(index=False):
    VAL[r.k] = {'rec': r.receptions, 'recyd': r.receiving_yards, 'rushyd': r.rushing_yards, 'rryd': r.receiving_yards + r.rushing_yards}
def res(r):
    k = nn(r.player)
    if k not in PLAYED: return 'Void'
    v = VAL.get(k, {}).get(r.stat, 0)
    hit = v >= r.k
    return 'Won' if (hit if r.side == 'Yes' else not hit) else 'Lost'
D['result'] = [res(r) for r in D.itertuples(index=False)]
D['pl_c'] = np.where(D.result == 'Won', 100 - D.ask, np.where(D.result == 'Lost', -D.ask, 0))
# book chance per rung
BF = json.load(open(W + 'rh/book_fits_w11.json'))
MK = {'recyd': 'Receiving Yards', 'rec': 'Receptions', 'rushyd': 'Rushing Yards', 'rryd': 'Rushing + Receiving Yards'}
FITS = {}
for key, f in BF.items():
    g, m, p = key.split('|')
    if 'mean' in f: FITS[(g, m, nn(p))] = f
def sf(f, x):
    if f.get('dist') == 'gamma': k = f['k']; return float(stats.gamma.sf(x, k, scale=f['mean'] / k))
    return float(1 - stats.poisson.cdf(math.floor(x), f['mean']))
pb = []
for r in D.itertuples(index=False):
    f = FITS.get((r.game, MK[r.stat], nn(r.player)))
    if not f: pb.append(np.nan); continue
    py = sf(f, r.k - 0.5); pb.append(100 * (py if r.side == 'Yes' else 1 - py))
D['book'] = pb
lg = lambda p: np.log(np.clip(p, 1e-4, 1 - 1e-4) / (1 - np.clip(p, 1e-4, 1 - 1e-4))); sg = lambda z: 1 / (1 + np.exp(-z))
D['kalshi'] = D.mkt; D['v6b'] = D.mid
D['book_lens'] = 100 * sg(lg(D.book / 100) + lg(D.v6b / 100) - lg(D.kalshi / 100))
D['avg'] = 100 * sg((lg(D.book / 100) + lg(D.v6b / 100)) / 2)
S = D[D.result.isin(['Won', 'Lost']) & D.book.notna()].copy(); y = (S.result == 'Won').astype(float).values
M = ['kalshi', 'v6b', 'book', 'book_lens', 'avg']
def scores(df, yy):
    out = {}
    for m in M:
        p = np.clip(df[m].values / 100, 1e-4, 1 - 1e-4)
        out[m] = {'logloss': round(float(-np.mean(yy * np.log(p) + (1 - yy) * np.log(1 - p))), 5), 'brier': round(float(np.mean((p - yy) ** 2)), 5)}
    return out
R = {'n_rungs': int(len(S)), 'games': sorted(S.game.unique().tolist()), 'all': scores(S, y)}
band = S.kalshi.between(60, 90); R['band_60_90'] = dict(n=int(band.sum()), **scores(S[band], y[band.values]))
cal = {}
for m in M:
    b = pd.cut(S[m], [0, 50, 60, 70, 75, 80, 85, 90, 95, 100])
    g = S.assign(y=y).groupby(b, observed=True).agg(n=('y', 'size'), hit=('y', 'mean'), said=(m, 'mean'))
    cal[m] = {str(k): [int(v.n), round(100 * v.hit, 1), round(v.said, 1)] for k, v in g.iterrows()}
R['calibration'] = cal
# the v2 card each model would pick (checks and research as on the posted board, no QB veto, no mix)
el = D[D.result.isin(['Won', 'Lost']) & D.book.notna() & D.role & D.script & D.late & ~D.research_pass & (D.ask <= 75)].copy()
cards = {}
for m in M:
    e = el[el[m] >= 70].sort_values(m, ascending=False)
    seen, pg, keep = set(), collections.Counter(), []
    for r in e.itertuples(index=False):
        if r.player in seen or pg[r.game] >= 4: continue
        seen.add(r.player); pg[r.game] += 1; keep.append(r)
    k = pd.DataFrame(keep)
    w = int((k.result == 'Won').sum()) if len(k) else 0
    cards[m] = {'n': len(k), 'won': w, 'lost': len(k) - w, 'hit': round(100 * w / max(len(k), 1), 1), 'said': round(float(k[m].mean()), 1) if len(k) else None,
                'profit_c': int(k.pl_c.sum()) if len(k) else 0, 'avg_price': round(float(k.ask.mean()), 1) if len(k) else None}
    # strict: top 20 by the model
    t = k.sort_values(m, ascending=False).head(20) if len(k) else k
    cards[m]['top20'] = [int((t.result == 'Won').sum()), int((t.result == 'Lost').sum()), int(t.pl_c.sum())] if len(t) else None
R['v2_card'] = cards
# does book minus Kalshi predict the result? (the gap the early-lines note describes)
S['gap'] = S.book - S.kalshi
gb = S.assign(y=y).groupby(pd.cut(S.gap, [-50, -6, -3, -1, 1, 3, 6, 50]), observed=True).agg(n=('y', 'size'), hit=('y', 'mean'), kalshi=('kalshi', 'mean'), book=('book', 'mean'))
R['book_minus_kalshi'] = {str(k): [int(v.n), round(100 * v.hit, 1), round(v.kalshi, 1), round(v.book, 1)] for k, v in gb.iterrows()}
# game-bootstrap interval for the log-loss gap book vs kalshi and v6b vs kalshi
rng = np.random.default_rng(7); games = S.game.unique(); idx = {g: np.where(S.game.values == g)[0] for g in games}
def ll(m, ii): p = np.clip(S[m].values[ii] / 100, 1e-4, 1 - 1e-4); yy = y[ii]; return -np.mean(yy * np.log(p) + (1 - yy) * np.log(1 - p))
boot = collections.defaultdict(list)
for _ in range(2000):
    ii = np.concatenate([idx[g] for g in rng.choice(games, len(games))])
    for m in ('v6b', 'book', 'book_lens', 'avg'): boot[m].append(ll(m, ii) - ll('kalshi', ii))
R['logloss_vs_kalshi_90pct'] = {m: [round(float(np.percentile(v, 5)), 5), round(float(np.mean(v)), 5), round(float(np.percentile(v, 95)), 5)] for m, v in boot.items()}
json.dump(R, open(W + 'bt/w12_model/report.json', 'w'), indent=1)
D.to_csv(W + 'bt/w12_model/rows_w11_graded.csv', index=False)
print(json.dumps({k: R[k] for k in ('n_rungs', 'all', 'band_60_90', 'v2_card', 'logloss_vs_kalshi_90pct', 'book_minus_kalshi')}, indent=1))
for m in M: print(m, R['calibration'][m])
