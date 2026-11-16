"""Momentum categories against a market-style line, 2023-2026.

The line each player-game would have had is estimated with the weights books used on the real Week 6-7 lines
(mom/real_analysis.json: line = a*S + b*L4 + c*C per stat, scaled so the average line matches the real ones).
Then: how often the over cleared that line, by momentum type, relative to all lines of that stat.
Momentum types: role up (snap share last 4 >= season + 10), volume up (targets/carries last 4 >= season +15%, snaps flat),
efficiency-only up (yards per target/carry up 15%+, volume flat), and the same downward; stable otherwise.
Writes mom/hist_sim.json.
"""
import json, numpy as np, pandas as pd
S = '/home/claude/wedger/'
F = pd.read_pickle(S + 'mom/feat.pkl')
RA = json.load(open(S + 'mom/real_analysis.json'))['line_fit']
MIN = {'recyd': 20, 'rec': 2, 'rushyd': 25, 'passyd': 150}
out = {}
for st in ('recyd', 'rec', 'rushyd', 'passyd'):
    d = F[(F['stat'] == st) & (F['S'] >= MIN[st]) & F['C'].notna() & F['vS'].notna() & (F['vS'] > 0)].copy()
    if st == 'rushyd': d = d[d['pos'] == 'RB']
    f = RA.get(st)
    w = (f['w_S'], f['w_L4'], f['w_C']) if f and f['n'] >= 40 else (0.3, 0.2, 0.5)
    line = w[0] * d['S'] + w[1] * d['L4'] + w[2] * d['C']
    step = 0.5 if st == 'rec' else 5.0
    d['line'] = np.floor(line / step) * step + (0.5 if st == 'rec' else 4.5)   # books' style: x.5 rungs
    d['over'] = (d['y'] > d['line']).astype(int)
    vm = (d['vL4'] - d['vS']) / d['vS']; em = (d['effL4'] - d['effS']) / d['effS'].abs().clip(lower=0.1)
    sm = (d['snapL4'] - d['snapS'])
    cat = np.select([sm >= 10, sm <= -10, (vm >= 0.15), (vm <= -0.15), (em >= 0.15), (em <= -0.15)],
                    ['Role up (snaps +10)', 'Role down (snaps -10)', 'Volume up', 'Volume down', 'Efficiency-only up', 'Efficiency-only down'], 'Stable')
    d['cat'] = cat
    base = d['over'].mean()
    res = {'n': int(len(d)), 'base_over': round(100 * base, 1), 'line_w': w}
    for c, x in d.groupby('cat'):
        res[c] = {'n': int(len(x)), 'over': round(100 * x['over'].mean(), 1), 'vs_base': round(100 * (x['over'].mean() - base), 1),
                  'by_season': {int(s): round(100 * (xx['over'].mean() - d[d['season'] == s]['over'].mean()), 1) for s, xx in x.groupby('season') if len(xx) >= 30}}
    out[st] = res
    d[['pid', 'season', 'week', 'stat', 'line', 'over', 'cat', 'y', 'S', 'L4', 'C']].to_pickle(S + f'mom/hist_lines_{st}.pkl')
json.dump(out, open(S + 'mom/hist_sim.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
