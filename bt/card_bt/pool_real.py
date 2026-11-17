"""Backtest pool, Weeks 7-9 (real prices): every settled Robinhood receiving and rushing main line from the record
(rh/results_w6_w11.csv), with point-in-time lens features (games before that week only).
Prices: the Yes price on the board; No = 100 - Yes + 1 (the same convention as the site's other backtests).
Writes bt/card_bt/pool_real.pkl."""
import re, sys
import numpy as np, pandas as pd
W = '/home/claude/wedger/'
sys.path.insert(0, W + 'lens'); import core
live, st, pos = core.load(W + 'dl18/')
MK = {'Receiving Yards': 'recyd', 'Receptions': 'rec', 'Rushing Yards': 'rushyd', 'Rushing + Receiving Yards': 'rryd'}
r = pd.read_csv(W + 'rh/results_w6_w11.csv', low_memory=False)
r = r[r.group.str.match(r'Week [789] settled$') & r.market.isin(MK)].copy()
rows, miss = [], 0
for wk in (7, 8, 9):
    T = core.Tables(live, st, pos, wk)
    sw = st[st.week == wk]
    for x in r[r.week == wk].itertuples(index=False):
        m = MK[x.market]; nm = x.contract.split(':')[0].strip(); k = core.nn(nm)
        mm = re.search(r'Over ([\d.]+)', x.contract)
        if not mm or x.outcome not in ('Won', 'Lost'): continue
        line = float(mm.group(1)); a, h = [core.fx(t) for t in x.game.split(' @ ')]
        s = sw[(sw.nn == k) & sw.team.isin([a, h])]
        if not len(s): miss += 1; continue
        s = s.iloc[0]; team = s.team; opp = h if team == a else a
        v = (s.rushing_yards or 0) + (s.receiving_yards or 0) if m == 'rryd' else (s[core.STATCOL[m]] or 0)
        ya = float(x.yes_price); na = 101.0 - ya; mid = (ya - 0.5) / 100
        f = core.features(T, s.player_id, team, opp, m, line, mid)
        y = 1.0 if x.outcome == 'Won' else 0.0
        if y != float(v > line): print('settle mismatch', wk, x.contract, v, x.outcome)
        rows.append(dict(wk=wk, src='real', game=x.game, player=nm, pid=s.player_id, pos=pos.get(s.player_id, ''), team=team, opp=opp, stat=m, line=line,
                         ya=ya, na=na, mid=mid, y=y, actual=float(v), rid=x.id, **f))
P = pd.DataFrame(rows)
P.to_pickle(W + 'bt/card_bt/pool_real.pkl')
print(P.shape, 'unmatched', miss); print(P.groupby(['stat', 'wk']).size().unstack()); print(P.groupby('pos').size())
print(P.groupby('wk').y.mean().round(3), P.ya.describe().round(1))
