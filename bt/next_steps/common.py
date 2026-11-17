"""Shared harness for the three next-step tests (calibration, football terms, game simulation).

Data: every settled Robinhood receiving and rushing main line from Weeks 7-10 at its real price (1,314 lines:
bt/card_bt/pool_real.pkl + pool_w10.pkl), with point-in-time lens features (games before that week only).
Market price = the Yes price less half a cent (the record's convention). Outcome y = the stat cleared the line.

Two held-out schemes, both used for every decision:
  leave-one-week-out  each of Weeks 7-10 is scored by a model fit only on the other three (penalty chosen inside them)
  forward             Weeks 8-10, each scored by a model fit only on the weeks before it (the live situation)
The card on held-out weeks uses this week's rules (final11/brain_layer + build.py, copied in bt/card_bt/card_bt.py):
needs = ask + 2c, final = low end of the range clears needs by 0.5+, lean = the middle does, checks, card limits."""
import math, sys
import numpy as np, pandas as pd
from scipy.optimize import minimize
W = '/home/claude/wedger/'
sys.path.insert(0, W + 'brain'); import gates
P = pd.concat([pd.read_pickle(W + 'bt/card_bt/pool_real.pkl'), pd.read_pickle(W + 'bt/card_bt/pool_w10.pkl')], ignore_index=True)
FAM = {'recyd': 'recv', 'rec': 'recv', 'rushyd': 'rush', 'rryd': 'rush'}
FE = {'recv': ['dvp', 'overlap', 'look', 'volume', 'comp', 'consist'], 'rush': ['dvp', 'dir', 'box', 'volume', 'comp', 'consist']}
COLS = [f'{f}.{c}' for f in ('recv', 'rush') for c in FE[f]]
WEEKS = (7, 8, 9, 10)
FEE = 2.0; RATIO = 3
sg = lambda z: 1 / (1 + np.exp(-z))
lg = lambda p: np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))
y = P.y.values.astype(float); off = lg(P.mid.values); wk = P.wk.values
games = (P.wk.astype(str) + '|' + P.game).values
fam = P.stat.map(FAM).values


def col(name):
    """one lens column, zero outside its family (recv.dvp is zero on rushing lines)"""
    f, c = name.split('.')
    return ((fam == f) * P[c].fillna(0).values).astype(float)


def scaled(cols):
    Z = np.column_stack(cols); sd = Z.std(0); return Z / np.where(sd > 0, sd, 1)


XBASE = scaled([col(c) for c in COLS])


def fit(Z, idx, lam, o=None):
    o = off if o is None else o
    def f(b):
        p = sg(o[idx] + Z[idx] @ b)
        return (-np.sum(y[idx] * np.log(p + 1e-12) + (1 - y[idx]) * np.log(1 - p + 1e-12)) + lam * b @ b,
                Z[idx].T @ (p - y[idx]) + 2 * lam * b)
    return minimize(f, np.zeros(Z.shape[1]), jac=True, method='L-BFGS-B').x


lli = lambda p, t: -(t * np.log(np.clip(p, 1e-9, 1)) + (1 - t) * np.log(np.clip(1 - p, 1e-9, 1)))
LAMS = (3, 10, 30, 100, 300, 1000)


def pick_lam(Z, tr, o=None):
    o = off if o is None else o; best = None
    for lam in LAMS:
        inner = []
        for w2 in sorted(set(wk[tr])):
            a, t = tr[wk[tr] != w2], tr[wk[tr] == w2]
            if not len(a): continue
            inner.append(lli(sg(o[t] + Z[t] @ fit(Z, a, lam, o)), y[t]).sum())
        if inner and (best is None or np.sum(inner) < best[0]): best = (np.sum(inner), lam)
    return best[1] if best else 30


def heldout(Z, o=None, scheme='lowo', ret_fits=False):
    """-> held-out probability for every scored line (nan where not scored), and the fit used for each week"""
    o = off if o is None else o; p = np.full(len(y), np.nan); fits = {}
    for w in WEEKS:
        if scheme == 'lowo': tr = np.where(wk != w)[0]
        else:
            tr = np.where(wk < w)[0]
            if not len(tr): continue
        te = np.where(wk == w)[0]; lam = pick_lam(Z, tr, o); b = fit(Z, tr, lam, o)
        p[te] = sg(o[te] + Z[te] @ b); fits[w] = (tr, lam, b)
    return (p, fits) if ret_fits else p


rng_b = np.random.default_rng(9); UG = np.unique(games)
BOOT = [np.concatenate([np.where(games == k)[0] for k in rng_b.choice(UG, len(UG))]) for _ in range(400)]


def compare(p, base, mask=None):
    """mean log-loss difference p - base on the scored lines, with a 90% game-bootstrap range (negative = p better)"""
    m = ~np.isnan(p) & ~np.isnan(base) if mask is None else mask
    d = np.where(m, lli(np.nan_to_num(p, nan=.5), y) - lli(np.nan_to_num(base, nan=.5), y), np.nan)
    bs = [np.nanmean(d[i]) for i in BOOT]
    return float(np.nanmean(d)), float(np.percentile(bs, 5)), float(np.percentile(bs, 95))


def summ(p, mask=None):
    m = ~np.isnan(p) if mask is None else mask
    return {'n': int(m.sum()), 'logloss': round(float(lli(p[m], y[m]).mean()), 5), 'brier': round(float(np.mean((p[m] - y[m]) ** 2)), 5),
            **{f'w{w}': round(float(lli(p[m & (wk == w)], y[m & (wk == w)]).mean()), 5) for w in WEEKS if (m & (wk == w)).any()}}


def boot_fits(Z, tr, lam, n=40, seed=7, o=None):
    r = np.random.default_rng(seed); keys = games[tr]; uk = np.unique(keys); out = []
    for _ in range(n):
        pick = r.choice(uk, len(uk), replace=True); idx = np.concatenate([tr[keys == k] for k in pick]); out.append(fit(Z, idx, lam, o))
    return np.array(out)


# ---------------- the card on held-out weeks (same rules as bt/card_bt/card_bt.py)
_st = pd.read_csv(W + 'dl19/stats_player_week_2026.csv', low_memory=False); _st = _st[_st.season_type == 'REG']
_pbp = pd.read_csv(W + 'dl19/play_by_play_2026.csv.gz', low_memory=False,
                   usecols=['week', 'qtr', 'rusher_player_id', 'receiver_player_id', 'rushing_yards', 'receiving_yards'])
_games = pd.read_csv(W + 'dl19/games.csv'); G = _games[(_games.season == 2026) & (_games.game_type == 'REG')]
CTX = {w: gates.Ctx(_st, _pbp, _games, w) for w in WEEKS}
_qb = _st[_st.position == 'QB'].sort_values('attempts', ascending=False).groupby(['team', 'week']).head(1)
QBW = {(r.team, r.week): r.player_id for r in _qb.itertuples(index=False)}
UN = {'LAR': 'LA', 'WSH': 'WAS'}; un = lambda t: UN.get(t, t)


def exp_margin(team, w):
    t = un(team); g = G[(G.week == w) & ((G.home_team == t) | (G.away_team == t))]
    if not len(g): return 0.0
    g = g.iloc[0]; return float(g.spread_line) if g.home_team == t else -float(g.spread_line)


def team_total(team, w):
    t = un(team); g = G[(G.week == w) & ((G.home_team == t) | (G.away_team == t))]
    if not len(g): return np.nan
    g = g.iloc[0]; m = exp_margin(team, w); return float(g.total_line) / 2 + m / 2


def qb_ok(team, opp, w):
    for tm in (un(team), un(opp)):
        prim = CTX[w].primary_qb(tm)[0]; now = QBW.get((tm, w))
        if prim is not None and now is not None and now != prim: return False
    return True


_CHK = {}


def check(r, k, side):
    key = (r.wk, r.pid, r.stat, k, side)
    if key not in _CHK:
        _CHK[key] = gates.check(CTX[r.wk], r.pid, un(r.team), r.stat, k, side, exp_margin(r.team, r.wk), qb_ok(r.team, r.opp, r.wk))
    return _CHK[key]


def cleared(D):
    """D: pool rows with p, lo, hi in percent. -> every side that clears the lean bar, with its call (Final line / lean / Pass)"""
    rows = []
    for r in D.itertuples():
        k = int(round(r.line + 0.5))
        if k < (2 if r.stat == 'rec' else 10): continue
        for side in ('Yes', 'No'):
            ask = r.ya if side == 'Yes' else r.na
            if not (3 < ask < 97): continue
            p, lo, hi = (r.p, r.lo, r.hi) if side == 'Yes' else (100 - r.p, 100 - r.hi, 100 - r.lo)
            be = ask + FEE; e_lo, e_mid = lo - be, p - be
            if e_mid < 0.5: continue
            c = check(r, k, side)
            fails = [n for n in ('ROLE', 'SCRIPT', 'LATE') if not c[n]['pass']]
            if not c['QB']['pass']: call = 'Pass'
            elif fails: call = 'Pass'
            elif e_lo >= 0.5: call = 'Final line'
            else: call = 'Conditional lean'
            win = int(r.y == 1) if side == 'Yes' else int(r.y == 0)
            rows.append({'i': r.Index, 'week': r.wk, 'game': r.game, 'player': r.player, 'stat': r.stat, 'k': k, 'side': side, 'price': ask,
                         'mkt': 100 * r.mid if side == 'Yes' else 100 - 100 * r.mid, 'stated': p, 'lo': lo, 'edge_lo': e_lo, 'edge_mid': e_mid,
                         'call': call, 'win': win, 'profit': (100 - ask) if win else -ask})
    return pd.DataFrame(rows)


def card(C):
    """best rung per player-stat, one line per player and four per game, then about one under per three overs per tier"""
    out = []
    for w in sorted(C.week.unique()):
        d = C[(C.week == w) & (C.call != 'Pass')].copy()
        if not len(d): continue
        d['t'] = (d.call != 'Final line').astype(int); d['u'] = (d.side != 'Yes').astype(int); d['e'] = np.where(d.call == 'Final line', d.edge_lo, d.edge_mid)
        d = d.sort_values(['t', 'u', 'e'], ascending=[True, True, False]).groupby(['player', 'stat']).head(1)
        keep = []
        for g, x in d.groupby('game'):
            seen = set()
            for r in x.sort_values(['t', 'u', 'e'], ascending=[True, True, False]).itertuples():
                if r.player in seen or len([1 for q in keep if q[0] == g]) >= 4: continue
                seen.add(r.player); keep.append((g, r.Index))
        d = d.loc[[i for _, i in keep]]
        for tier in ('Final line', 'Conditional lean'):
            x = d[d.call == tier]; O = x[x.side == 'Yes']; U = x[x.side == 'No'].sort_values('e', ascending=False)
            allow = max(1, math.ceil(len(O) / RATIO)) if len(U) else 0
            out += [O, U.head(allow)]
    return pd.concat(out).drop(columns=['t', 'u', 'e']) if out else C.iloc[:0]


def tier_stats(K):
    """stated chance vs win rate per tier, with the calibration z-score (won - stated) / sd"""
    res = {}
    for tier in ('Final line', 'Conditional lean'):
        x = K[K.call == tier]
        if not len(x): res[tier] = {'n': 0}; continue
        ps = x.stated.values / 100; z = (x.win.sum() - ps.sum()) / max(math.sqrt(np.sum(ps * (1 - ps))), 1e-9)
        res[tier] = {'n': int(len(x)), 'stated': round(100 * ps.mean(), 1), 'won': round(100 * x.win.mean(), 1), 'gap': round(100 * (x.win.mean() - ps.mean()), 1),
                     'z': round(float(z), 2), 'mkt': round(float(x.mkt.mean()), 1), 'roi': round(100 * x.profit.sum() / x.price.sum(), 1)}
    return res
