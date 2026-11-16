"""Do the method's research checks improve the v6 picks? Weeks 7-9, every settled Robinhood/Kalshi prop line.
v6 probabilities are held out by week (fit on the other two weeks, same settings as the live model). Picks mimic the card:
receiving and rushing lines, tradable rungs, one line per player per week (the best edge), side = Yes or No.
Checks use only games before the week. Writes bt/brain_bt.json."""
import json, os, sys, numpy as np, pandas as pd
os.environ['V6_FAMS'] = 'recv,rush'; os.environ['V6_LAMG'] = '1000000'
W = '/home/claude/wedger/'
sys.path.insert(0, W + 'brain'); import gates
src = open(W + 'bt/fit_v6.py').read().split('T = pd.concat(out)')[0]
src = src.replace("out, rep = [], {'folds': {}}", "out, rep = [], {'folds': {}}")
ns = {}; exec(compile(src, 'fit_v6_head', 'exec'), ns)
T = pd.concat(ns['out'])
FEE = 0.02
st = pd.read_csv(W + 'dl19/stats_player_week_2026.csv', low_memory=False)
pbp = pd.read_csv(W + 'dl19/play_by_play_2026.csv.gz', low_memory=False, usecols=['week', 'qtr', 'rusher_player_id', 'receiver_player_id', 'rushing_yards', 'receiving_yards'])
games = pd.read_csv(W + 'dl19/games.csv')
FX = {'LA': 'LAR', 'WAS': 'WSH'}; UNFX = {'LAR': 'LA', 'WSH': 'WAS', 'JAX': 'JAX'}
T = T[T.stat.isin(['rec', 'recyd', 'rushyd', 'rryd'])].copy()
T['k'] = (T.line + 0.5).round().astype(int)
T = T[(T.yb > 0) & ((T.ya - T.yb) <= 0.08) & (T.k >= np.where(T.stat == 'rec', 2, 10))]
rows = []
for r in T.itertuples(index=False):
    for side in ('Yes', 'No'):
        ask = r.ya if side == 'Yes' else r.na
        if not (0.03 < ask < 0.97): continue
        p = r.p6 if side == 'Yes' else 1 - r.p6
        mk = r.mid if side == 'Yes' else 1 - r.mid
        rows.append({'wk': r.wk, 'player': r.player, 'pid': r.pid, 'team': r.team, 'opp': r.opp, 'stat': r.stat, 'k': r.k, 'side': side, 'ask': ask, 'p': p, 'mkt': mk,
                     'edge': p - (ask + FEE), 'win': int(r.y == 1) if side == 'Yes' else int(r.y == 0), 'game': r.game})
C = pd.DataFrame(rows)
C = C[C.edge >= 0.005].sort_values('edge', ascending=False).groupby(['wk', 'pid']).head(1).copy()
ctxs = {w: gates.Ctx(st, pbp, games, w) for w in (7, 8, 9)}
qbw = st[(st.position == 'QB') & (st.season_type == 'REG')].sort_values('attempts', ascending=False).groupby(['team', 'week']).head(1)
QBW = {(r.team, r.week): r.player_id for r in qbw.itertuples(index=False)}
G = games[(games.season == 2026)]
def exp_margin(team, wk):
    t = UNFX.get(team, team)
    g = G[(G.week == wk) & ((G.home_team == t) | (G.away_team == t))]
    if not len(g): return 0.0
    g = g.iloc[0]; return float(g.spread_line) if g.home_team == t else -float(g.spread_line)
out = []
for r in C.itertuples(index=False):
    cx = ctxs[r.wk]; t, o = UNFX.get(r.team, r.team), UNFX.get(r.opp, r.opp)
    qb_ok = True
    for tm in (t, o):
        prim = cx.primary_qb(tm)[0]; now = QBW.get((tm, r.wk))
        if prim is not None and now is not None and now != prim: qb_ok = False
    c = gates.check(cx, r.pid, t, r.stat, r.k, r.side, exp_margin(r.team, r.wk), qb_ok)
    out.append({**r._asdict(), **{g_: c[g_]['pass'] for g_ in ('QB', 'ROLE', 'SCRIPT', 'LOG', 'LATE')}, 'ALL': c['all']})
D = pd.DataFrame(out)
def summ(d, label):
    if not len(d): return {'label': label, 'n': 0}
    cost = d.ask.sum(); pnl = np.where(d.win == 1, 1 - d.ask, -d.ask).sum() - FEE * len(d)
    return {'label': label, 'n': int(len(d)), 'won': round(float(d.win.mean()), 3), 'avg_price': round(float(d.ask.mean()), 3), 'avg_p': round(float(d.p.mean()), 3),
            'roi': round(float(pnl / cost), 3)}
rep = {'tiers': {}}
for tier, thr in (('lean+', 0.005), ('final-like (3+ pts)', 0.03)):
    d = D[D.edge >= thr]; R = [summ(d, 'all v6 picks')]
    for g_ in ('QB', 'ROLE', 'SCRIPT', 'LOG', 'LATE', 'ALL'):
        R.append(summ(d[d[g_]], f'passes {g_}')); R.append(summ(d[~d[g_]], f'fails {g_}'))
    for wk in (7, 8, 9):
        R.append(summ(d[(d.wk == wk)], f'week {wk} all')); R.append(summ(d[(d.wk == wk) & d.ALL], f'week {wk} pass ALL'))
    rep['tiers'][tier] = R
    print('\n==', tier)
    for x in R: print(f"{x['label']:22s} n={x.get('n', 0):4d} won={x.get('won', '')} price={x.get('avg_price', '')} ours={x.get('avg_p', '')} roi={x.get('roi', '')}")
D.to_csv(W + 'bt/brain_bt_rows.csv', index=False)
json.dump(rep, open(W + 'bt/brain_bt.json', 'w'), indent=1)
