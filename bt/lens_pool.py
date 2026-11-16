"""Backtest pool for the matchup lens: every Robinhood player prop on the Week 7, 8 and 9 boards (all prices, both quotes
live), settled from the box scores, with point-in-time lens features (games before that week only).
Writes bt/lens_pool.pkl."""
import json, re, sys
import numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/wedger/lens'); import core
W = '/home/claude/wedger/'; DL = W + 'dl18/'
live, st, pos = core.load(DL)
sn = pd.read_csv(DL + 'snap_counts_2026.csv'); PLAYED = {(int(w), core.nn(p)) for w, p, o in zip(sn.week, sn.player, sn.offense_snaps) if (o or 0) > 0}
MK = {'Receiving Yards': 'recyd', 'Receptions': 'rec', 'Rushing Yards': 'rushyd', 'Passing Yards': 'passyd', 'Passing Touchdowns': 'passtd',
      'Rushing + Receiving Yards': 'rryd', 'Anytime Touchdown': 'td'}
rows = []
for wk in (7, 8, 9):
    T = core.Tables(live, st, pos, wk)
    sw = st[st.week == wk].set_index('nn')
    prior = st[st.week < wk].sort_values('week').drop_duplicates('nn', keep='last').set_index('nn')
    R = json.load(open(W + f'rh/rows_w{wk}.json'))
    for r in R:
        m = MK.get(r['market'])
        if not m or r['source'] != 'Robinhood' or r['yes_ask'] in (None, '') or r['yes_bid'] in (None, ''): continue
        ya, yb = float(r['yes_ask']), float(r['yes_bid'])
        na = float(r['no_ask']) if r['no_ask'] not in (None, '') else 1 - yb
        if ya - yb > 0.08 or not (0.03 <= (ya + yb) / 2 <= 0.97): continue
        nm = r['contract'].split(':')[0].strip(); k = core.nn(nm)
        if m == 'td': line = 0.5
        else:
            mm = re.search(r'Over ([\d.]+)', r['contract'])
            if not mm: continue
            line = float(mm.group(1))
        a, h = [core.fx(t) for t in r['game'].split(' @ ')]
        if (wk, k) not in PLAYED or k not in sw.index: continue
        s = sw.loc[k]
        if isinstance(s, pd.DataFrame): s = s[s.team.isin([a, h])].iloc[0] if len(s[s.team.isin([a, h])]) else s.iloc[0]
        team = s.team
        if team not in (a, h): continue
        opp = h if team == a else a
        if m == 'rryd': v = (s.rushing_yards or 0) + (s.receiving_yards or 0)
        elif m == 'td': v = (s.rushing_tds or 0) + (s.receiving_tds or 0)
        else: v = s[core.STATCOL[m]] or 0
        mid = (ya + yb) / 2
        f = core.features(T, s.player_id, team, opp, m, line, mid)
        rows.append(dict(wk=wk, game=r['game'], player=nm, pid=s.player_id, pos=pos.get(s.player_id, ''), team=team, opp=opp, stat=m, line=line,
                         ya=ya, yb=yb, na=na, mid=mid, y=float(v > line), actual=float(v), **f))
    print(wk, len(rows))
P = pd.DataFrame(rows)
# one weight per player-stat ladder so a 12-rung ladder counts the same as a 1-rung one
P['n_rungs'] = P.groupby(['wk', 'pid', 'stat']).y.transform('size'); P['w'] = 1 / P.n_rungs
P.to_pickle(W + 'bt/lens_pool.pkl')
print(P.shape); print(P.groupby(['stat', 'wk']).size().unstack())
print(P[['dvp', 'overlap', 'look', 'volume', 'dir', 'box', 'pressure', 'comp', 'consist']].describe().round(3))
