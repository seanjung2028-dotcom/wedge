"""Backtest the Wedger NBA screen and model on real 2025-26 sportsbook prices.

Prices: closing player-prop lines from DraftKings, FanDuel, BetRivers, BetMGM and others (via Action Network), every other
date of the 2025-26 regular season. Price = the books' average no-vig chance of the Over at their consensus line.
Settled against ESPN box scores. Everything about a line uses only games played before that date.
"""
import json, collections, math, sys
import numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/wedger/nba')
import nba_model as M

D = '/home/claude/wedger/nba/'
X = pd.read_pickle(D + 'nba_logs.pkl'); L, T = X['logs'], X['team']
L = L[L['yy'] == 26].copy()          # backtest season only (2025-26)
T = T[T['yy'] == 26].copy()
BT = json.load(open(D + 'an_bt.json'))
NAMES = BT['names']; MK = ['pts', 'reb', 'ast', '3pm', 'pra']
FIX = {'GS': 'GSW', 'NY': 'NYK', 'SA': 'SAS', 'NO': 'NOP', 'UTAH': 'UTA', 'WSH': 'WAS', 'PHO': 'PHX'}
fx = lambda t: FIX.get(t, t)
L['nn'] = L['name'].map(M.norm_name)
by_key = {(r.nn, r.date): r for r in L.itertuples(index=False)}
by_pid = {pid: g.reset_index(drop=True) for pid, g in L.groupby('pid')}
TEAM_NAME = {}

import os
rows = []
miss = collections.Counter()
REBUILD = '--rebuild' in sys.argv or not os.path.exists(D + 'nba_bt_rows.pkl')
for ds in (sorted(BT['d']) if REBUILD else []):
    day = BT['d'][ds]
    date = f'{ds[:4]}-{ds[4:6]}-{ds[6:]}'
    if not day['r']: continue
    DEF, LGD, RK = M.defense_table(L, date, 26)
    TT, LGT = M.team_table(T, date, 26)
    G = day['G']
    # who sat out each team-game that night (for teammates-out)
    today = L[L['date'] == date]
    for eid, ni, mk, line, p1000, nb, lo, hi in day['r']:
        name, team_an, pos_an = NAMES[ni]
        g = G.get(str(eid))
        if not g: continue
        stat = MK[mk]
        r = by_key.get((M.norm_name(name), date))
        if r is None:
            # ESPN dates can differ by a day for late tips listed by UTC
            miss['no box'] += 1; continue
        if r.dnp: miss['dnp'] += 1; continue
        H = by_pid[r.pid]; H = H[(H['date'] < date) & (~H['dnp'])]
        if len(H) < 8: miss['few games'] += 1; continue
        a, h, sp_home, tot = fx(g[0]), fx(g[1]), g[2], g[3]
        team = r.team
        if team not in (a, h): miss['team mismatch'] += 1; continue
        sp_team = None if sp_home is None else (sp_home if team == h else -sp_home)
        implied = None if (sp_team is None or tot is None) else tot / 2 - sp_team / 2
        # teammates out tonight: top-3 minutes players on his team over their last 15 games who did not play
        mates = today[(today['team'] == team) & (today['pid'] != r.pid)]
        recent = L[(L['team'] == team) & (L['date'] < date) & (~L['dnp'])]
        top = recent.groupby('name')['min'].apply(lambda s: s.tail(15).mean()).sort_values(ascending=False)
        top = [n for n in top.index[:3] if top[n] >= 26]
        out_names = [n for n in top if (mates[mates['name'] == n]['dnp'].all() if (mates['name'] == n).any() else True)]
        mo = M.mates_out(L, r.pid, team, date, 26, out_names, stat) if out_names else []
        ctx = {'yy': 26, 'team': team, 'opp': r.opp, 'grp': r.grp, 'def': DEF, 'lg': LGD, 'rank': RK, 'teams': TT, 'lgt': LGT,
               'spread': sp_team, 'implied': implied, 'rest': None if pd.isna(r.rest) else int(r.rest), 'mates_out': mo}
        p = p1000 / 1000
        E = M.evaluate(H, stat, line, ctx, p_mkt=p)
        if not E: continue
        actual = getattr(r, {'3pm': '_23'}.get(stat, stat)) if stat != '3pm' else r[L.columns.get_loc('3pm')]
        y = 1 if actual > line else 0
        last20 = H[stat].to_numpy()[-20:]
        hit20 = float((last20 > line).mean())
        rows.append({'date': date, 'stat': stat, 'player': name, 'team': team, 'line': line, 'p': p, 'nb': nb, 'y': y, 'actual': float(actual),
                     'hit20': hit20, 'n20': len(last20), 'cases': E['P_cases'], 'model': E['P_model'], 'raw': E['P_raw'],
                     'm': E['m'], 'm0': E['C']['m0'], 'avg_all': E['avg_all'], 'mates': len(mo)})
if REBUILD:
    print('rows', len(rows), dict(miss))
    R = pd.DataFrame(rows)
    R.to_pickle(D + 'nba_bt_rows.pkl')
else:
    R = pd.read_pickle(D + 'nba_bt_rows.pkl')

def brier(p, y): return float(np.mean((np.asarray(p) - np.asarray(y)) ** 2))
def logloss(p, y):
    p = np.clip(np.asarray(p, dtype=float), 0.01, 0.99); y = np.asarray(y)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))

# calibrate on the first half of the season, test on the second half
R = R.sort_values('date').reset_index(drop=True)
dates = sorted(R['date'].unique()); cut = dates[len(dates) // 2]
A = R[R['date'] < cut]
ks = [round(float(k), 2) for k in np.arange(0.1, 1.01, 0.05)]
k_best = min(ks, key=lambda kk: brier(0.5 + kk * (A['raw'] - 0.5), A['y']))
wms = [round(float(w), 2) for w in np.arange(0.0, 1.01, 0.05)]
wm_best = min(wms, key=lambda wm: brier(wm * A['p'] + (1 - wm) * (0.5 + k_best * (A['raw'] - 0.5)), A['y']))
print('calibration (first half): k', k_best, 'w_mkt', wm_best)
K, WM = k_best, wm_best
R['ours_cal'] = 0.5 + K * (R['raw'] - 0.5)
R['wedger'] = WM * R['p'] + (1 - WM) * R['ours_cal']
B = R[R['date'] >= cut]

def summ(df):
    out = {'n': int(len(df)), 'hit_rate': round(100 * df['y'].mean(), 1), 'avg_price': round(100 * df['p'].mean(), 1)}
    for k in ('p', 'hit20', 'cases', 'model', 'raw', 'ours_cal', 'wedger'):
        out[k] = {'brier': round(brier(df[k], df['y']), 4), 'logloss': round(logloss(df[k], df['y']), 4)}
    return out

def strat(df, mask):
    s = df[mask]
    if not len(s): return {'n': 0}
    prof = (s['y'] - s['p']).sum(); stake = s['p'].sum()
    return {'n': int(len(s)), 'won': int(s['y'].sum()), 'win_pct': round(100 * s['y'].mean(), 1), 'avg_price': round(100 * s['p'].mean(), 1),
            'roi': round(100 * prof / stake, 1)}

out = {'all': summ(R), 'second_half': summ(B), 'cut': cut, 'calibration': {'k': K, 'w_mkt': WM}}
band = (R['p'] >= 0.45) & (R['p'] <= 0.55)
out['screen'] = {
    'band_all': strat(R, band),
    'band_hit20_gt50': strat(R, band & (R['hit20'] > 0.5)),
    'band_hit20_ge60': strat(R, band & (R['hit20'] >= 0.6)),
    'band_hit20_ge70': strat(R, band & (R['hit20'] >= 0.7)),
    'band_hit20_lt50': strat(R, band & (R['hit20'] < 0.5)),
    'band_wedger_plus3': strat(R, band & (R['wedger'] - R['p'] >= 0.03)),
    'band_ours_plus5': strat(R, band & (R['ours_cal'] - R['p'] >= 0.05)),
    'band_ours_plus10': strat(R, band & (R['raw'] - R['p'] >= 0.10)),
}
out['by_stat'] = {}
for s, g in R.groupby('stat'):
    b = (g['p'] >= 0.45) & (g['p'] <= 0.55)
    out['by_stat'][s] = {'n': int(len(g)), 'hit_rate': round(100 * g['y'].mean(), 1),
                         'brier': {k: round(brier(g[k], g['y']), 4) for k in ('p', 'hit20', 'raw', 'ours_cal', 'wedger')},
                         'screen': strat(g, b & (g['hit20'] > 0.5)), 'band': strat(g, b)}
out['by_month'] = {}
R['month'] = R['date'].str[:7]
for mth, g in R.groupby('month'):
    b = (g['p'] >= 0.45) & (g['p'] <= 0.55)
    out['by_month'][mth] = {'screen': strat(g, b & (g['hit20'] > 0.5)), 'band': strat(g, b)}
# hit-rate bands (like the NFL factor table)
out['hit20_bands'] = {}
for lo_, hi_, lab in ((0, 0.3, '<30%'), (0.3, 0.5, '30–49%'), (0.5, 0.6, '50–59%'), (0.6, 0.7, '60–69%'), (0.7, 1.01, '70%+')):
    out['hit20_bands'][lab] = strat(R, band & (R['hit20'] >= lo_) & (R['hit20'] < hi_))
# calibration of wedger
cal = collections.defaultdict(list)
for pv, yv in zip(R['wedger'], R['y']): cal[min(9, int(pv * 10))].append(yv)
out['wedger_calibration'] = {f'{10 * k}-{10 * k + 10}%': [len(v), round(100 * float(np.mean(v)), 1)] for k, v in sorted(cal.items())}
cal = collections.defaultdict(list)
for pv, yv in zip(R['raw'], R['y']): cal[min(9, int(pv * 10))].append(yv)
out['raw_calibration'] = {f'{10 * k}-{10 * k + 10}%': [len(v), round(100 * float(np.mean(v)), 1)] for k, v in sorted(cal.items())}
out['projection_mae'] = {'history_avg': round(float(np.mean(np.abs(R['avg_all'] - R['actual']))), 2), 'cases': round(float(np.mean(np.abs(R['m0'] - R['actual']))), 2),
                         'adjusted': round(float(np.mean(np.abs(R['m'] - R['actual']))), 2), 'book_line': round(float(np.mean(np.abs(R['line'] - R['actual']))), 2)}
out['dates'] = [R['date'].min(), R['date'].max(), int(R['date'].nunique())]
hb = out['hit20_bands']; Aall = out['all']; W3 = out['screen']['band_wedger_plus3']
out['takeaway'] = (f"A hot recent record barely moved the needle: lines that hit in 70%+ of his last 20 won {hb['70%+']['win_pct']}%, lines under 30% won {hb['<30%']['win_pct']}%, "
                   f"and every band lost money because Overs at these prices came true {Aall['hit_rate']}% of the time against an average price of {Aall['avg_price']}¢. "
                   f"The books' line was the best single read (Brier {Aall['p']['brier']}); our matchup model on its own ({Aall['raw']['brier']}) was worse than a coin flip until shrunk, "
                   f"and blending it in as Wedger % ({Aall['wedger']['brier']}) did not beat the price. Lines where Wedger % beat the price by 3+ points went {W3['won']} of {W3['n']}. "
                   "In the NBA the price is the signal; use the screen and the outlook to understand a line, not as an edge on their own.")
json.dump(out, open(D + 'nba_bt.json', 'w'), indent=1)
print(json.dumps({k: out[k] for k in ('all', 'second_half', 'calibration', 'screen', 'projection_mae', 'dates')}, indent=1))
