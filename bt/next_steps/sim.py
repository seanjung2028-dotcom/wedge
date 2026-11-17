"""Next step 1: simulate the game. Every rung of a player's ladder is priced from one simulated distribution.

  rushing yards   carries ~ negative binomial around his recent carries; each carry's yards drawn from his own carries
                  (2025 and 2026, before the week), blended with his position's carries as his sample is small
  receptions      targets ~ negative binomial around his recent targets; each target caught at his catch rate
                  (shrunk toward his position's rate)
  receiving yards each catch's yards drawn the same way as carries
  rush + rec      the two added
4,000 simulated games per player-week. All settings come from the 2025 season, which the test never touches:
the recency half-life and the volume spread (negative binomial size) are the ones that best predicted 2025's next game;
the blending strengths (50 carries, 30 catches, 30 targets) are fixed in advance. So no 2026 week is used to fit the
simulation itself, and Weeks 7-10 are all weeks it wasn't fit on.

Judged three ways on the 1,314 Weeks 7-10 lines at real prices:
  alone             the simulation's own chance vs the market price (the stated test)
  with the market   logit p = logit(mid) + b * (logit(sim) - logit(mid)), b fit on held-out weeks
  with the formula  the same disagreement added to the current formula as one more term
Pass mark (set before running): held-out log loss below the market's (and, to replace the formula, below it too).
Writes bt/next_steps/sim.json and bt/next_steps/sim_p.pkl."""
import json
import numpy as np, pandas as pd
from scipy.special import gammaln
from common import *

N = 4000; K_PLAY = {'rush': 50, 'rec': 30}; K_CATCH = 30
rng = np.random.default_rng(11)
cols = ['season', 'season_type', 'week', 'rush_attempt', 'complete_pass', 'two_point_attempt', 'rusher_player_id', 'receiver_player_id', 'rushing_yards', 'receiving_yards']
pb = pd.concat([pd.read_csv(W + 'dl18/play_by_play_2025.csv.gz', usecols=cols, low_memory=False),
                pd.read_csv(W + 'dl19/play_by_play_2026.csv.gz', usecols=cols, low_memory=False)], ignore_index=True)
pb = pb[(pb.season_type == 'REG') & (pb.two_point_attempt.fillna(0) != 1)]
RUSH = pb[(pb.rush_attempt == 1) & pb.rusher_player_id.notna() & pb.rushing_yards.notna()][['season', 'week', 'rusher_player_id', 'rushing_yards']]
RUSH.columns = ['season', 'week', 'pid', 'yd']
CATCH = pb[(pb.complete_pass == 1) & pb.receiver_player_id.notna() & pb.receiving_yards.notna()][['season', 'week', 'receiver_player_id', 'receiving_yards']]
CATCH.columns = ['season', 'week', 'pid', 'yd']
st = pd.concat([pd.read_csv(W + 'dl18/stats_player_week_2025.csv', low_memory=False), pd.read_csv(W + 'dl19/stats_player_week_2026.csv', low_memory=False)])
st = st[st.season_type == 'REG'][['player_id', 'season', 'week', 'team', 'position_group', 'carries', 'targets', 'receptions']].fillna({'carries': 0, 'targets': 0, 'receptions': 0})
POSG = st.sort_values(['season', 'week']).drop_duplicates('player_id', keep='last').set_index('player_id').position_group.to_dict()
grp = lambda pid: {'RB': 'RB', 'WR': 'WR', 'TE': 'TE', 'QB': 'QB'}.get(POSG.get(pid, ''), 'WR')
RUSH['g'] = RUSH.pid.map(grp); CATCH['g'] = CATCH.pid.map(grp)


def ewma(v, h):
    a = 0.5 ** (np.arange(len(v))[::-1] / h); return float(np.sum(a * v) / np.sum(a))


def nb_ll(c, mu, r):
    mu = np.maximum(mu, 1e-3); return gammaln(c + r) - gammaln(r) - gammaln(c + 1) + r * np.log(r / (r + mu)) + c * np.log(mu / (r + mu))


# ---------------- settings from 2025: recency half-life and volume spread, by position group and volume type
s25 = st[st.season == 2025].sort_values('week'); TUNE = {}
for vol in ('carries', 'targets'):
    for g in ('RB', 'WR', 'TE', 'QB'):
        if vol == 'targets' and g == 'QB': continue
        best = None
        for h in (2, 3, 4, 6, 10):
            C, M = [], []
            for pid, d in s25[s25.position_group == g].groupby('player_id'):
                v = d[vol].values
                for j in range(2, len(v)): C.append(v[j]); M.append(ewma(v[:j], h))
            C, M = np.array(C), np.array(M); keep = M >= 0.5
            for r in (1, 2, 3, 5, 8, 12, 20, 40):
                ll = nb_ll(C[keep], M[keep], r).sum()
                if best is None or ll > best[0]: best = (ll, h, r, int(keep.sum()))
        TUNE[(vol, g)] = {'half_life': best[1], 'nb_size': best[2], 'n': best[3]}
CR_POS = (s25.groupby('position_group').receptions.sum() / s25.groupby('position_group').targets.sum()).to_dict()
print('settings from 2025:', {f'{a}/{b}': v for (a, b), v in TUNE.items()}, {k: round(v, 3) for k, v in CR_POS.items() if k in ('RB', 'WR', 'TE')})


def before(df, w):
    return df[(df.season == 2025) | ((df.season == 2026) & (df.week < w))]


def draws(own, league, n, k):
    """n per-play yardages: his own plays with weight m/(m+k), his position's otherwise"""
    if n == 0: return np.zeros(0)
    wo = len(own) / (len(own) + k)
    pick_own = rng.random(n) < wo
    out = np.empty(n)
    if len(own): out[pick_own] = own[rng.integers(0, len(own), pick_own.sum())]
    else: pick_own[:] = False
    out[~pick_own] = league[rng.integers(0, len(league), (~pick_own).sum())]
    return out


def simulate(pid, w):
    g = grp(pid); s = st[(st.player_id == pid) & (st.season == 2026) & (st.week < w)].sort_values('week')
    if len(s) < 2: return None
    out = {}
    R = before(RUSH, w); Cc = before(CATCH, w)
    for vol, kind in (('carries', 'rush'), ('targets', 'rec')):
        tg = TUNE.get((vol, g)) or TUNE[(vol, 'RB' if vol == 'carries' else 'WR')]
        mu = ewma(s[vol].values, tg['half_life']); r = tg['nb_size']
        cnt = rng.negative_binomial(r, r / (r + mu), N) if mu > 0.05 else np.zeros(N, int)
        if vol == 'targets':
            cr = (s.receptions.sum() + K_CATCH * CR_POS.get(g, 0.65)) / (s.targets.sum() + K_CATCH)
            cnt_r = rng.binomial(cnt, cr); out['rec'] = cnt_r.astype(float); cnt = cnt_r
        D = R if kind == 'rush' else Cc
        own = D[D.pid == pid].yd.values.astype(float); lg_ = D[D.g == g].yd.values.astype(float)
        if not len(lg_): lg_ = D.yd.values.astype(float)
        tot = int(cnt.sum()); d = draws(own, lg_, tot, K_PLAY[kind])
        idx = np.repeat(np.arange(N), cnt); yd = np.bincount(idx, weights=d, minlength=N) if tot else np.zeros(N)
        out['rushyd' if kind == 'rush' else 'recyd'] = yd
    out['rryd'] = out['rushyd'] + out['recyd']
    return out


SIM = {}
for (pid, w) in P[['pid', 'wk']].drop_duplicates().itertuples(index=False):
    SIM[(pid, w)] = simulate(pid, w)
ps = np.full(len(P), np.nan); smean = np.full(len(P), np.nan)
for i, r in enumerate(P.itertuples(index=False)):
    s = SIM.get((r.pid, r.wk))
    if s is None: continue
    ps[i] = (np.sum(s[r.stat] > r.line) + 0.5) / (N + 1); smean[i] = float(np.median(s[r.stat]))
ps = np.clip(ps, 0.01, 0.99)
have = ~np.isnan(ps)
print(f'simulated {have.sum()} of {len(P)} lines ({(~have).sum()} players had fewer than 2 games before the week -> left at the market)')
psim = np.where(have, ps, sg(off))
mk = sg(off)
res = {'settings_2025': {f'{a}/{b}': v for (a, b), v in TUNE.items()}, 'simulated_lines': int(have.sum()), 'lines': int(len(P))}
res['alone'] = {**summ(psim), 'vs_market': [round(x, 5) for x in compare(psim, mk)]}
res['alone_simulated_only'] = {**summ(psim, have), 'market': summ(mk, have)}
# as a projection: how close the simulated median and the line each come to what happened (simulated lines only)
act = P.actual.values
res['projection'] = {s_: {'n': int((have & (P.stat.values == s_)).sum()),
                          'sim_median_abs_err': round(float(np.mean(np.abs(smean - act)[have & (P.stat.values == s_)])), 2),
                          'line_abs_err': round(float(np.mean(np.abs(P.line.values - act)[have & (P.stat.values == s_)])), 2),
                          'corr_sim_actual': round(float(np.corrcoef(smean[have & (P.stat.values == s_)], act[have & (P.stat.values == s_)])[0, 1]), 3),
                          'corr_line_actual': round(float(np.corrcoef(P.line.values[have & (P.stat.values == s_)], act[have & (P.stat.values == s_)])[0, 1]), 3)}
                     for s_ in ('rec', 'recyd', 'rushyd', 'rryd')}
# reliability of the simulation alone, and its average bias by stat
q = pd.qcut(psim[have], 10, labels=False, duplicates='drop')
res['alone_reliability'] = [{'sim': round(100 * float(psim[have][q == j].mean()), 1), 'won': round(100 * float(y[have][q == j].mean()), 1)} for j in range(q.max() + 1)]
res['by_stat'] = {s: {'sim': round(100 * float(psim[have & (P.stat.values == s)].mean()), 1), 'market': round(100 * float(mk[have & (P.stat.values == s)].mean()), 1),
                      'won': round(100 * float(y[have & (P.stat.values == s)].mean()), 1), 'sim_ll': round(float(lli(psim, y)[have & (P.stat.values == s)].mean()), 5),
                      'mkt_ll': round(float(lli(mk, y)[have & (P.stat.values == s)].mean()), 5)} for s in ('rec', 'recyd', 'rushyd', 'rryd')}
dis = lg(psim) - off; dz = (dis / dis.std())[:, None]
cur = {}
for s in ('lowo', 'forward'):
    cur[s] = heldout(XBASE, scheme=s)
    pmk = np.where(np.isnan(cur[s]), np.nan, mk)
    pa, fa = heldout(dz, scheme=s, ret_fits=True)
    pf, ff = heldout(np.hstack([XBASE, dz]), scheme=s, ret_fits=True)
    res[f'with_market_{s}'] = {**summ(pa), 'vs_market': [round(x, 5) for x in compare(pa, pmk)], 'b_by_week': {w: round(float(f[2][0] / dis.std()), 4) for w, f in fa.items()}}
    res[f'with_formula_{s}'] = {**summ(pf), 'vs_market': [round(x, 5) for x in compare(pf, pmk)], 'vs_current': [round(x, 5) for x in compare(pf, cur[s])],
                                'b_by_week': {w: round(float(f[2][-1] / dis.std()), 4) for w, f in ff.items()}}
    res[f'current_{s}'] = summ(cur[s]); res[f'market_{s}'] = summ(pmk)
json.dump(res, open(W + 'bt/next_steps/sim.json', 'w'), indent=1, default=float)
pd.DataFrame({'rid': P.rid, 'wk': P.wk, 'stat': P.stat, 'line': P.line, 'mid': P.mid, 'y': y, 'p_sim': psim, 'sim_median': smean, 'simulated': have}).to_pickle(W + 'bt/next_steps/sim_p.pkl')
print(json.dumps({k: v for k, v in res.items() if k != 'settings_2025'}, indent=1, default=float))
