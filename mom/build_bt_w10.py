"""Week-by-week backtests, Weeks 1-9 2026, for the Charts tab (Week 9 added Mon Nov 9: Thursday and Sunday games; BUF @ MIN once final).

bt_weeks.csv  real Robinhood prices, 45-55c, by week and segment (strategy, market, side, price band, filter, Wedger picks).
              Weeks 1-5: hist_lines.csv (game lines only; Robinhood didn't keep prop prices). Week 6: results_w6.csv.
              Week 7: results_w6_w7.csv (all 14 games). Every No priced at 100 - Yes + 1c.
bt_props.csv  modeled player props, every week 1-7 of 2026 plus 2023-25 together: the line each player-stat would have had
              (books' own weights on the real Week 6-7 lines: season avg, last 4, multi-season avg; Weeks 1-3 use the
              multi-season avg only), and how often the over cleared it, by factor.
"""
import csv, json, re, numpy as np, pandas as pd
S = '/home/claude/wedger/'
R = S + 'rh/'
FIX = {'LA': 'LAR', 'WAS': 'WSH'}
g = pd.read_csv(S + 'dl18/games.csv'); g = g[(g['season'] == 2026) & (g['game_type'] == 'REG')]
FAV = {}
for r in g.itertuples(index=False):
    a, h = FIX.get(r.away_team, r.away_team), FIX.get(r.home_team, r.home_team)
    FAV[(r.week, f'{a} @ {h}')] = h if r.spread_line > 0 else (a if r.spread_line < 0 else None)
CITY = {'Arizona': 'ARI', 'Atlanta': 'ATL', 'Baltimore': 'BAL', 'Buffalo': 'BUF', 'Carolina': 'CAR', 'Chicago': 'CHI', 'Cincinnati': 'CIN', 'Cleveland': 'CLE',
        'Dallas': 'DAL', 'Denver': 'DEN', 'Detroit': 'DET', 'Green Bay': 'GB', 'Houston': 'HOU', 'Indianapolis': 'IND', 'Jacksonville': 'JAX', 'Kansas City': 'KC',
        'Las Vegas': 'LV', 'Los Angeles C': 'LAC', 'Los Angeles R': 'LAR', 'Miami': 'MIA', 'Minnesota': 'MIN', 'New England': 'NE', 'New Orleans': 'NO',
        'New York G': 'NYG', 'New York J': 'NYJ', 'Philadelphia': 'PHI', 'Pittsburgh': 'PIT', 'San Francisco': 'SF', 'Seattle': 'SEA', 'Tampa Bay': 'TB',
        'Tennessee': 'TEN', 'Washington': 'WSH'}
def team_in(contract):
    c = contract.split(' wins')[0].strip()
    if c in CITY.values(): return c
    for k, v in CITY.items():
        if c.startswith(k): return v
    return None
PROPGRP = {'Receiving Yards': 'Props · receiving', 'Receptions': 'Props · receiving', 'Rushing Yards': 'Props · rushing', 'Rushing + Receiving Yards': 'Props · rushing',
           'Passing Yards': 'Props · passing', 'Passing Touchdowns': 'Props · passing', 'Interceptions': 'Props · passing', 'Anytime Touchdown': 'Props · anytime TD'}
L = []
for r in csv.DictReader(open(R + 'hist_lines.csv')):
    wk = int(r['week'].split()[-1])
    if r['outcome'] not in ('Won', 'Lost'): continue
    L.append({'week': wk, 'group': 'Game lines', 'market': r['market'], 'side': r['side'] if r['side'] in ('Favorite', 'Underdog') else ('Over' if r['market'].startswith('Total') else ''),
              'price': float(r['price_c']), 'won': r['outcome'] == 'Won', 'qual': '', 'pick': ''})
def add67(wk, r, grp):
    mk = r['market']
    if r['outcome'] not in ('Won', 'Lost'): return
    if grp == 'Player props' or mk in PROPGRP: G = PROPGRP.get(mk.replace(' (ATD filter pick)', ''), 'Props · other')
    elif grp == 'Quarters & halves': G = 'Quarters & halves'
    else: G = 'Game lines'
    side = ''
    if G == 'Game lines':
        if mk in ('Moneyline', 'Spreads'):
            t = team_in(r['contract']); f = FAV.get((wk, r['game']))
            side = '' if not t or not f else ('Favorite' if t == f else 'Underdog')
        elif mk == 'Totals': side = 'Over'
    L.append({'week': wk, 'group': G, 'market': mk, 'side': side, 'price': float(r['yes_price']), 'won': r['outcome'] == 'Won', 'qual': r.get('qualifies', ''), 'pick': ''})
for r in csv.DictReader(open(R + 'results_w6.csv')):
    if r['group'] in ('Other Wedger picks', 'ATD filter picks'): continue
    add67(6, r, r['group'])
for r in csv.DictReader(open(R + 'results_w6_w9.csv')):
    if r['week'] == '7' and r['group'] == 'Week 7 settled': add67(7, r, r['group'])
    if r['week'] == '8' and r['group'] == 'Week 8 settled': add67(8, r, r['group'])
    if r['week'] == '9' and r['group'] == 'Week 9 settled': add67(9, r, r['group'])
D = pd.DataFrame(L)
D = D[D['price'].between(45, 55)]
# Wedger picks (Week 7 live: Sunday v2 + Monday v2.1)
live = pd.concat([pd.read_csv(R + 'live_eval_w7_rows.csv'), pd.read_csv(R + 'live_eval_w7_mnf_rows.csv')], ignore_index=True)
live = live[(live['src'] == 'Robinhood') & live['no_ask'].notna() & live['pick'].isin(['Yes', 'No'])]
s8 = pd.read_csv(S + 'bt/w8_settled.csv', low_memory=False)
s8 = s8[(s8['source'] == 'Robinhood') & s8['no_price'].notna() & s8['sit_pick'].isin(['Yes', 'No']) & s8['y'].notna()]
live8 = pd.DataFrame({'pick': s8['sit_pick'], 'y': s8['y'], 'price': s8['yes_price'].astype(float), 'no_ask': s8['no_price'].astype(float)})
s9 = pd.read_csv(S + 'bt/w9_settled.csv', low_memory=False)
s9 = s9[(s9['source'] == 'Robinhood') & s9['no_price'].notna() & s9['sit_pick'].isin(['Yes', 'No']) & s9['y'].notna()]
live9 = pd.DataFrame({'pick': s9['sit_pick'], 'y': s9['y'], 'price': s9['yes_price'].astype(float), 'no_ask': s9['no_price'].astype(float)})
def rec(wins, n, cost, profit):
    return {'n': int(n), 'wins': int(wins), 'losses': int(n - wins), 'win_pct': round(100 * wins / n, 1) if n else None,
            'avg_price': round(cost / n, 1) if n else None, 'roi_pct': round(100 * profit / cost, 1) if cost else None}
rows = []
def seg(wk, grp, name, d, side='Yes'):
    if not len(d): return
    if side == 'Yes':
        wins = d['won'].sum(); cost = d['price'].sum(); profit = np.where(d['won'], 100 - d['price'], -d['price']).sum()
    else:
        nc = 100 - d['price'] + 1; wins = (~d['won']).sum(); cost = nc.sum(); profit = np.where(~d['won'], 100 - nc, -nc).sum()
    rows.append({'week': wk, 'seg_group': grp, 'segment': name, **rec(wins, len(d), cost, profit)})
for wk in list(range(1, 10)) + ['all']:
    d = D if wk == 'all' else D[D['week'] == wk]
    seg(wk, 'Strategy', 'Every Yes', d); seg(wk, 'Strategy', 'Every No', d, 'No')
    q = d[d['qual'] == 'Yes']
    if len(q): seg(wk, 'Strategy', 'Hit >50% filter (Yes)', q)
    for G in ['Game lines', 'Quarters & halves', 'Props · receiving', 'Props · rushing', 'Props · passing', 'Props · anytime TD']:
        seg(wk, 'Market', G, d[d['group'] == G])
    for sd in ['Favorite', 'Underdog', 'Over']:
        seg(wk, 'Side (game lines)', {'Over': 'Game total over'}.get(sd, sd), d[(d['group'] == 'Game lines') & (d['side'] == sd)])
    for lo, hi, lab in ((45, 48, '45–48¢'), (49, 51, '49–51¢'), (52, 55, '52–55¢')):
        seg(wk, 'Price band', lab, d[d['price'].between(lo, hi)])
    if wk in (7, 8, 9, 'all'):
        lv = live if wk == 7 else (live8 if wk == 8 else (live9 if wk == 9 else pd.concat([live, live8, live9], ignore_index=True)))
        y = np.where(lv['pick'] == 'Yes', lv['y'] == 1, lv['y'] == 0); cost = np.where(lv['pick'] == 'Yes', lv['price'], lv['no_ask'])
        rows.append({'week': wk, 'seg_group': 'Strategy', 'segment': 'Wedger picks (3+ pts)', **rec(y.sum(), len(lv), cost.sum(), np.where(y, 100 - cost, -cost).sum())})
B = pd.DataFrame(rows); B['week'] = B['week'].astype(str)
B.to_csv(R + 'bt_weeks.csv', index=False)
print(B[B['seg_group'] == 'Strategy'].to_string())

# ---------- modeled props, Weeks 1-7 2026 and 2023-25 ----------
pg = pd.read_pickle(S + 'mom/pg.pkl')
RA = json.load(open(S + 'mom/real_analysis.json'))['line_fit']
STATS = {'recyd': ('WR', 'TE', 'RB'), 'rec': ('WR', 'TE', 'RB'), 'rushyd': ('RB',), 'passyd': ('QB',)}
SW = {0: 1.0, 1: 0.75, 2: 0.5, 3: 0.35}
VOLC = {'recyd': 'tgt', 'rec': 'tgt', 'rushyd': 'car', 'passyd': 'att'}
MIN = {'recyd': 20, 'rec': 2, 'rushyd': 25, 'passyd': 150}
# defense allowed per game to each position group, season to date (for opponent rank)
allow = pg.groupby(['season', 'week', 'opp', 'pos'])[['recyd', 'rushyd', 'passyd', 'rec']].sum().reset_index()
out = []
for (pid, team), d in pg.groupby(['pid', 'team'], sort=False):
    d = d.sort_values(['season', 'week'])
    pos = d['pos'].iloc[-1]
    for st, poss in STATS.items():
        if pos not in poss: continue
        y = d[st].values.astype(float); v = d[VOLC[st]].values.astype(float); sn = d['snap'].values; seas = d['season'].values
        for i in range(len(d)):
            s = seas[i]; cur = np.where((seas == s) & (np.arange(len(d)) < i))[0]; allp = np.arange(i)
            if len(allp) < 4: continue
            w = np.array([SW.get(s - seas[j], 0.3) for j in allp]); C = float(np.sum(w * y[allp]) / np.sum(w))
            f = RA.get(st); wS, w4, wC = (f['w_S'], f['w_L4'], f['w_C']) if f and f['n'] >= 40 else (0.3, 0.2, 0.5)
            if len(cur) >= 3:
                Sv, L4 = y[cur].mean(), y[cur][-4:].mean(); line = wS * Sv + w4 * L4 + wC * C
                vm = (v[cur][-4:].mean() - v[cur].mean()) / max(v[cur].mean(), 0.5)
                eS = y[cur].sum() / max(v[cur].sum(), 1); e4 = y[cur][-4:].sum() / max(v[cur][-4:].sum(), 1); em = (e4 - eS) / max(abs(eS), 0.1)
                sm = np.nanmean(sn[cur][-4:]) - np.nanmean(sn[cur]) if np.isfinite(sn[cur]).sum() >= 3 else 0
                mom = 'Role up' if sm >= 10 else 'Role down' if sm <= -10 else 'Volume up' if vm >= .15 else 'Volume down' if vm <= -.15 else 'Hot efficiency' if em >= .15 else 'Cold efficiency' if em <= -.15 else 'Stable'
                hr = float(np.mean(y[cur] > line))
            else:
                Sv, line, mom, hr = np.nan, C, 'Early season', np.nan
            if (Sv if np.isfinite(Sv) else C) < MIN[st]: continue
            step = 0.5 if st == 'rec' else 5.0
            line = np.floor(line / step) * step + (0.5 if st == 'rec' else 4.5)
            row = d.iloc[i]
            out.append({'season': s, 'week': int(row['week']), 'stat': st, 'pos': pos, 'over': int(y[i] > line), 'mom': mom, 'hr': hr,
                        'fav': 'Favorite' if row['fav_by'] > 0 else 'Underdog' if row['fav_by'] < 0 else "Pick'em", 'home': 'Home' if row['home'] == 1 else 'Away',
                        'implied': row['implied'], 'opp': row['opp']})
P = pd.DataFrame(out)
P['period'] = np.where(P['season'] == 2026, 'Wk ' + P['week'].astype(str), '2023–25')
P = P[(P['season'] < 2026) | (P['week'] <= 9)]
P['tot'] = pd.cut(P['implied'], [0, 20.4, 24.4, 60], labels=['Implied under 20.5', 'Implied 20.5–24', 'Implied 24.5+'])
P['hrb'] = np.where(P['hr'].isna(), 'n/a', np.where(P['hr'] > 0.5, 'Hit >50% vs line', 'Hit 50% or less'))
STL = {'recyd': 'Receiving yards', 'rec': 'Receptions', 'rushyd': 'Rushing yards', 'passyd': 'Passing yards'}
P['stat_l'] = P['stat'].map(STL)
rows = []
for per, d in P.groupby('period'):
    base = d['over'].mean()
    rows.append({'period': per, 'factor': 'All', 'level': 'All props', 'n': len(d), 'over_pct': round(100 * base, 1), 'diff': 0.0})
    for fac, col in (('Stat', 'stat_l'), ('Position', 'pos'), ('Favorite / underdog', 'fav'), ('Home / away', 'home'), ('Team total', 'tot'), ('Momentum', 'mom'), ('Season hit rate', 'hrb')):
        for lev, x in d.groupby(col, observed=True):
            if lev == 'n/a' or len(x) < 8: continue
            rows.append({'period': per, 'factor': fac, 'level': str(lev), 'n': len(x), 'over_pct': round(100 * x['over'].mean(), 1),
                         'diff': round(100 * (x['over'].mean() - base), 1)})
BP = pd.DataFrame(rows)
order = {f'Wk {i}': i for i in range(1, 10)}; order['2023–25'] = 0
BP['ord'] = BP['period'].map(order)
BP = BP.sort_values(['ord', 'factor', 'level']).drop(columns='ord')
BP.to_csv(R + 'bt_props.csv', index=False)
print(BP[BP['factor'].isin(['All', 'Stat'])].to_string())
# consistency: levels whose over% beat the period base in most 2026 weeks
cons = BP[BP['period'] != '2023–25'].groupby(['factor', 'level']).agg(weeks=('diff', 'size'), beat=('diff', lambda s: int((s > 0).sum())), avg=('diff', 'mean')).reset_index()
print(cons.sort_values('avg').to_string())
