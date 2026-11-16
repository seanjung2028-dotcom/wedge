"""What the market's own lines say about recency (Week 6-7 2026 real prices).

1. How books set the line: least squares of the line (priced 45-55c, so near the market's median) on season average S,
   last-4 L4 and the multi-season weighted average C, by stat group.
2. Does recency beat the price? For every settled prop with history: hit rate when the last 4 run above vs below the season,
   split by volume-led vs efficiency-led momentum, against the average price.
Writes mom/real_analysis.json.
"""
import json, numpy as np, pandas as pd
S = '/home/claude/wedger/'
R = pd.read_pickle(S + 'mom/real.pkl')
R = R[R['S'].notna()].copy()
out = {'n': int(len(R))}
G = {'recyd': 'yards', 'rushyd': 'yards', 'rryd': 'yards', 'passyd': 'yards', 'rec': 'rec'}
fit = {}
for st in ('recyd', 'rec', 'rushyd', 'passyd'):
    d = R[(R['stat'] == st) & R['price'].between(45, 55) & R['C'].notna()]
    if len(d) < 15: continue
    X = np.column_stack([d['S'], d['L4'], d['C']]); b = np.linalg.lstsq(X, d['line'], rcond=None)[0]
    r2 = 1 - np.sum((d['line'] - X @ b) ** 2) / np.sum((d['line'] - d['line'].mean()) ** 2)
    fit[st] = {'n': int(len(d)), 'w_S': round(float(b[0]), 3), 'w_L4': round(float(b[1]), 3), 'w_C': round(float(b[2]), 3), 'r2': round(float(r2), 3),
               'line_minus_S': round(float((d['line'] - d['S']).mean()), 2), 'line_minus_L4': round(float((d['line'] - d['L4']).mean()), 2),
               'line_minus_C': round(float((d['line'] - d['C']).mean()), 2)}
out['line_fit'] = fit
# momentum vs outcome on all non-TD props priced 30-70c
d = R[(R['stat'] != 'td') & R['price'].between(30, 70) & R['vS'].notna()].copy()
d['scale'] = d.groupby('stat')['S'].transform('mean')
d['mom'] = (d['L4'] - d['S']) / d['S'].clip(lower=1)
d['volmom'] = (d['vL4'] - d['vS']) / d['vS'].clip(lower=0.5)
d['effmom'] = (d['effL4'] - d['effS']) / d['effS'].abs().clip(lower=0.1)
def rec(x):
    if not len(x): return {'n': 0}
    return {'n': int(len(x)), 'hit': round(100 * x['y_hit'].mean(), 1), 'price': round(x['price'].mean(), 1),
            'edge': round(100 * x['y_hit'].mean() - x['price'].mean(), 1)}
out['momentum_real'] = {
    'all': rec(d),
    'L4 above season by 15%+': rec(d[d['mom'] >= 0.15]), 'L4 within 15%': rec(d[d['mom'].abs() < 0.15]), 'L4 below season by 15%+': rec(d[d['mom'] <= -0.15]),
    'volume up 15%+': rec(d[d['volmom'] >= 0.15]), 'volume down 15%+': rec(d[d['volmom'] <= -0.15]),
    'efficiency up, volume flat': rec(d[(d['effmom'] >= 0.15) & (d['volmom'].abs() < 0.15)]),
    'efficiency down, volume flat': rec(d[(d['effmom'] <= -0.15) & (d['volmom'].abs() < 0.15)]),
    'snap share up 10+': rec(d[(d['snapL4'] - d['snapS']) >= 10]), 'snap share down 10+': rec(d[(d['snapL4'] - d['snapS']) <= -10]),
    'line above C (multi-season avg)': rec(d[d['line'] > d['C']]), 'line below C': rec(d[d['line'] < d['C']]),
    'line above season avg': rec(d[d['line'] > d['S']]), 'line below season avg': rec(d[d['line'] < d['S']]),
}
out['by_week'] = {int(w): rec(x) for w, x in d.groupby('week')}
json.dump(out, open(S + 'mom/real_analysis.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
