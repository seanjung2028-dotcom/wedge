"""The Week 11 card rules run on Weeks 1-9, graded against how each line settled.

Model (v6): the market mid moved by the matchup lens on receiving and rushing lines; range = 10th-90th percentile of 40 refits.
  Weeks 7-9 (real prices): v6 refit without the week being tested (fit on the other two weeks' settled main lines, same
                           settings as the live fit: receiving and rushing features, no group shift, penalty chosen inside).
  Weeks 2-6 (rebuilt lines): the live v6 weights (fit on Weeks 7-9, so these weeks' results were never used).
  Week 1: no 2026 games before it, so the model has no player to move and posts nothing.
Card rules (final11/brain_layer.decide and final11/build.py):
  Final line = low end of our range beats break-even (price + 2c fee) by 0.5+; conditional lean = the middle does.
  Checks: no backup QB in the game; role steady; side clears in the likely script and in close games; overs not
  leaning on 4th-quarter work. A line that clears but fails a check is a pass.
  Rungs: receptions 2+, yards 10+. One line per player, four per game, about one under per three overs in each tier.
Grading: the settled outcome (real weeks: the record's own settlement; rebuilt weeks: nflverse box scores).
Return = profit on one contract at the price, before fees (same as the rest of Results).
Writes bt/card_bt/card.pkl (the backtested card) and runs summary.py, which writes the site's two datasets."""
import json, math, os, sys
import numpy as np, pandas as pd
from scipy.optimize import minimize
W = '/home/claude/wedger/'
sys.path.insert(0, W + 'brain'); import gates
FEE = 2.0; RATIO = 3
CAL = json.load(open(W + 'bt/cal_v6.json'))
GL = CAL['group_levels']; COLS = CAL['cols']; GRP = CAL['groups']; FAMS = {'recyd': 'recv', 'rec': 'recv', 'rushyd': 'rush', 'rryd': 'rush'}
LIVE_B = np.array([CAL['coef'][f'grp.{g}'] for g in GL] + [CAL['coef'][c] for c in COLS]); LIVE_BOOT = np.array(CAL['boot'])
lg = lambda p: np.log(np.clip(p, 1e-4, 1 - 1e-4) / (1 - np.clip(p, 1e-4, 1 - 1e-4))); sg = lambda z: 1 / (1 + np.exp(-z))
def design(d):
    Xg = np.column_stack([(d.stat.map(GRP) == g).astype(float) for g in GL])
    Xf = np.column_stack([((d.stat.map(FAMS) == c.split('.')[0]) * d[c.split('.')[1]].fillna(0)).astype(float) for c in COLS])
    return np.hstack([Xg, Xf])
def fit(d, lam_f, lam_g=1e6):
    X = design(d); off = lg(d.mid.values); y = d.y.values
    pen = np.r_[np.full(len(GL), lam_g), np.full(len(COLS), lam_f)]
    def f(b):
        p = sg(off + X @ b)
        return -np.sum(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12)) + np.sum(pen * b ** 2), X.T @ (p - y) + 2 * pen * b
    return minimize(f, np.zeros(X.shape[1]), jac=True, method='L-BFGS-B').x
def lam_search(tr):
    best = None
    for lam in (5, 15, 30, 60, 120, 250):
        ll = 0
        for wk in tr.wk.unique():
            a, t = tr[tr.wk != wk], tr[tr.wk == wk]; p = sg(lg(t.mid.values) + design(t) @ fit(a, lam))
            ll += -np.sum(t.y * np.log(p) + (1 - t.y) * np.log(1 - p))
        if best is None or ll < best[0]: best = (ll, lam)
    return best[1]
def boots(d, lam, n=40, seed=7):
    rng = np.random.default_rng(seed); keys = (d.wk.astype(str) + '|' + d.game).values; uk = np.unique(keys); out = []
    for _ in range(n):
        pick = rng.choice(uk, len(uk), replace=True); idx = np.concatenate([np.where(keys == k)[0] for k in pick]); out.append(fit(d.iloc[idx], lam))
    return np.array(out)
def score(d, b, B):
    X = design(d); z0 = lg(d.mid.values)
    d['p'] = 100 * sg(z0 + X @ b); ps = np.array([sg(z0 + X @ bb) for bb in B])
    d['lo'] = 100 * np.percentile(ps, 10, axis=0); d['hi'] = 100 * np.percentile(ps, 90, axis=0)
    return d
# ---------------- pools
R = pd.read_pickle(W + 'bt/card_bt/pool_real.pkl'); RB = pd.read_pickle(W + 'bt/card_bt/pool_rebuilt.pkl')
st = pd.read_csv(W + 'dl19/stats_player_week_2026.csv', low_memory=False); st = st[st.season_type == 'REG']
PRIOR = {(w, pid) for w in range(1, 11) for pid in st[st.week < w].player_id.unique()}
FOLD = {}
for wk in (7, 8, 9):
    tr = R[R.wk != wk]; lam = lam_search(tr); FOLD[wk] = (fit(tr, lam), boots(tr, lam), lam)
    print('fold', wk, 'lambda', lam, 'train', len(tr))
parts = []
for wk in (7, 8, 9):
    parts.append(score(R[R.wk == wk].copy(), FOLD[wk][0], FOLD[wk][1]).assign(src='real'))
    parts.append(score(RB[RB.wk == wk].copy(), FOLD[wk][0], FOLD[wk][1]).assign(src='check'))
parts.append(score(RB[RB.wk <= 6].copy(), LIVE_B, LIVE_BOOT).assign(src='rebuilt'))
D = pd.concat(parts, ignore_index=True)
D['moved'] = [(w, p) in PRIOR for w, p in zip(D.wk, D.pid)]
# ---------------- research checks (games before the week only)
pbp = pd.read_csv(W + 'dl19/play_by_play_2026.csv.gz', low_memory=False, usecols=['week', 'qtr', 'rusher_player_id', 'receiver_player_id', 'rushing_yards', 'receiving_yards'])
games = pd.read_csv(W + 'dl19/games.csv'); G = games[(games.season == 2026) & (games.game_type == 'REG')]
CTX = {w: gates.Ctx(st, pbp, games, w) for w in range(2, 10)}
qbw = st[st.position == 'QB'].sort_values('attempts', ascending=False).groupby(['team', 'week']).head(1)
QBW = {(r.team, r.week): r.player_id for r in qbw.itertuples(index=False)}
UN = {'LAR': 'LA', 'WSH': 'WAS'}; un = lambda t: UN.get(t, t)
def exp_margin(team, wk):
    t = un(team); g = G[(G.week == wk) & ((G.home_team == t) | (G.away_team == t))]
    if not len(g): return 0.0
    g = g.iloc[0]; return float(g.spread_line) if g.home_team == t else -float(g.spread_line)
def qb_ok(team, opp, wk):
    for tm in (un(team), un(opp)):
        prim = CTX[wk].primary_qb(tm)[0]; now = QBW.get((tm, wk))
        if prim is not None and now is not None and now != prim: return False
    return True
WORD = {'rushyd': 'rushing yards', 'rec': 'receptions', 'recyd': 'receiving yards', 'rryd': 'rush + rec yards'}
def decide(c, vf, vl):
    fails = [n for n in ('ROLE', 'SCRIPT', 'LATE') if not c[n]['pass']]
    if not c['QB']['pass']: return 'Pass', 'Backup quarterback'
    if fails and vl: return 'Pass', 'Fails ' + ', '.join(fails)
    if vf: return 'Final line', ''
    if vl: return 'Conditional lean', ''
    return 'Pass', ''
rows = []
for r in D[D.moved].itertuples(index=False):
    k = int(round(r.line + 0.5))
    if k < (2 if r.stat == 'rec' else 10): continue
    for side in ('Yes', 'No'):
        ask = r.ya if side == 'Yes' else r.na
        if not (3 < ask < 97): continue
        p, lo, hi = (r.p, r.lo, r.hi) if side == 'Yes' else (100 - r.p, 100 - r.hi, 100 - r.lo)
        be = ask + FEE; e_lo, e_mid = lo - be, p - be
        if e_mid < 0.5: continue            # can't be a final or a lean
        c = gates.check(CTX[r.wk], r.pid, un(r.team), r.stat, k, side, exp_margin(r.team, r.wk), qb_ok(r.team, r.opp, r.wk))
        call, why = decide(c, e_lo >= 0.5, e_mid >= 0.5)
        win = int(r.y == 1) if side == 'Yes' else int(r.y == 0)
        rows.append({'src': r.src, 'week': r.wk, 'game': r.game, 'player': r.player, 'pid': r.pid, 'team': r.team, 'stat': r.stat, 'k': k, 'side': side,
                     'line': f"{r.player} {(str(k) + '+ ') if side == 'Yes' else ('under ' + str(k) + ' ')}{WORD[r.stat]} ({side})",
                     'price': int(ask), 'be': be, 'mkt': round(100 * r.mid if side == 'Yes' else 100 - 100 * r.mid, 1), 'lo': round(lo, 1), 'mid': round(p, 1), 'hi': round(hi, 1),
                     'edge_lo': round(e_lo, 1), 'edge_mid': round(e_mid, 1), 'call': call, 'why': why, 'win': win, 'profit': (100 - ask) if win else -ask,
                     'actual': r.actual, **{f'chk_{n}': bool(c[n]['pass']) for n in ('QB', 'ROLE', 'SCRIPT', 'LATE')}})
C = pd.DataFrame(rows)
# ---------------- the card: best rung per player-stat, one line per player and four per game, then the card mix per tier
def card(d):
    d = d[d.call != 'Pass'].copy()
    d['t'] = (d.call != 'Final line').astype(int); d['u'] = (d.side != 'Yes').astype(int); d['e'] = np.where(d.call == 'Final line', d.edge_lo, d.edge_mid)
    d = d.sort_values(['t', 'u', 'e'], ascending=[True, True, False]).groupby(['player', 'stat']).head(1)
    keep = []
    for g, x in d.groupby('game'):
        seen = set()
        for r in x.sort_values(['t', 'u', 'e'], ascending=[True, True, False]).itertuples():
            if r.player in seen or len([1 for q in keep if q[0] == g]) >= 4: continue
            seen.add(r.player); keep.append((g, r.Index))
    d = d.loc[[i for _, i in keep]]
    out, cut = [], []
    for tier in ('Final line', 'Conditional lean'):
        x = d[d.call == tier]; O = x[x.side == 'Yes']; U = x[x.side == 'No'].sort_values('e', ascending=False)
        allow = max(1, math.ceil(len(O) / RATIO)) if len(U) else 0
        out += [O, U.head(allow)]; cut.append(U.iloc[allow:])
    return pd.concat(out).drop(columns=['t', 'u', 'e']), pd.concat(cut).drop(columns=['t', 'u', 'e'])
_k = [card(C[(C.src == s) & (C.week == w)]) for s in C.src.unique() for w in sorted(C[C.src == s].week.unique())]
CARD = pd.concat([k for k, _ in _k], ignore_index=True); MIXCUT = pd.concat([c for _, c in _k], ignore_index=True); MIXCUT['decision'] = MIXCUT.call
MIXCUT.to_pickle(W + 'bt/card_bt/mixcut.pkl')
CARD['decision'] = CARD.call
CARD.to_pickle(W + 'bt/card_bt/card.pkl'); C.to_pickle(W + 'bt/card_bt/cleared.pkl')
json.dump({'folds': {w: FOLD[w][2] for w in FOLD}, 'cleared_lines': int(len(C[C.call != 'Pass'])), 'by_src_week': C.groupby(['src', 'week', 'call']).size().unstack(fill_value=0).reset_index().to_dict('records')},
          open(W + 'bt/card_bt/card_bt.json', 'w'), indent=1, default=str)
import subprocess; subprocess.run([sys.executable, W + 'bt/card_bt/summary.py'], check=True)
