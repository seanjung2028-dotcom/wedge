"""Re-read every rung of each candidate's Kalshi/Robinhood ladder (any price) after shifting the market's distribution by our evidence."""
import json, sys, numpy as np
sys.path.insert(0, '/home/claude/wedger/final9b'); from cands import C
Q = json.load(open('/home/claude/wedger/final9b/quotes.json'))
FEE = 0.02
SD_DEFAULT = [30]
def ladder(prefix):
    rungs = []
    for t, (ya, yb, na, st, sub) in Q['q'].items():
        if t.rsplit('-', 1)[0] != prefix or st != 'active': continue
        k = float(t.rsplit('-', 1)[1]); ya, yb, na = float(ya), float(yb), float(na)
        rungs.append((k, ya, yb, na))
    return sorted(rungs)
def market_curve(rungs):
    xs, ys = [], []
    for k, ya, yb, na in rungs:
        if yb > 0 and ya > 0 and ya - yb <= 0.08: xs.append(k); ys.append((ya + yb) / 2)
    ys = np.array(ys, float); xs = np.array(xs, float)
    if len(xs) == 1:  # single rung: assume a normal spread around it (sd by stat) so a shift can be read
        from statistics import NormalDist
        sd = SD_DEFAULT[0]; mu = xs[0] + sd * NormalDist().inv_cdf(min(.99, max(.01, ys[0])))
        xs = np.arange(xs[0] - 3 * sd, xs[0] + 3 * sd + 1, sd / 4); ys = np.array([1 - NormalDist(mu, sd).cdf(x) for x in xs]); return xs, ys
    # isotonic non-increasing (pool adjacent violators)
    v = list(ys); w = [1] * len(v); i = 0
    blocks = [[y, 1] for y in v]; out = []
    for b in blocks:
        out.append(b)
        while len(out) > 1 and out[-2][0] < out[-1][0]:
            y2, n2 = out.pop(); y1, n1 = out.pop(); out.append([(y1 * n1 + y2 * n2) / (n1 + n2), n1 + n2])
    fit = []
    for y, n in out: fit += [y] * n
    return xs, np.array(fit)
def S(xs, ys, x):
    if len(xs) == 0: return None
    if x <= xs[0]: # extrapolate up toward 0.99 with the first slope
        return float(min(0.99, ys[0] + (xs[0] - x) * (ys[0] - ys[min(1, len(ys) - 1)]) / max(1e-9, (xs[min(1, len(xs) - 1)] - xs[0]) or 1)))
    if x >= xs[-1]:
        return float(max(0.01, ys[-1] - (x - xs[-1]) * (ys[-2] - ys[-1]) / max(1e-9, xs[-1] - xs[-2]) if len(xs) > 1 else ys[-1]))
    return float(np.interp(x, xs, ys))
def prefix_for(g, nm, st):
    SER = {'pass': 'KXNFLPASSYDS', 'recyd': 'KXNFLRECYDS', 'rec': 'KXNFLREC', 'rush': 'KXNFLRSHYDS'}
    norm = lambda x: x.lower().replace("'", '')
    for t, v in Q['q'].items():
        if t.startswith(SER[st]) and norm(nm) in norm(v[4]) and (g.replace('@', '') in t or (g == 'LA@WAS' and 'LARWAS' in t)): return t.rsplit('-', 1)[0], v[4].split(':')[0]
def run(CC):
    RES = []
    for g, nm, st, d, _w, cond in CC:
        pre, full = prefix_for(g, nm, st); r = ladder(pre); xs, ys = market_curve(r)
        side = 'Yes' if d > 0 else ('No' if d < 0 else 'Both')
        rows = []
        for k, ya, yb, na in r:
            m = S(xs, ys, k)
            for sd in (['Yes', 'No'] if side == 'Both' else [side]):
                ask = ya if sd == 'Yes' else na
                if not (0.03 < ask < 0.97): continue
                if not (yb > 0 and ya > 0 and ya - yb <= 0.08): continue  # only rungs with a real two-sided quote (no extrapolated ends)
                def p(delta):
                    s_ = S(xs, ys, k - delta); return s_ if sd == 'Yes' else 1 - s_
                mid, lo, hi = p(d), p(d / 2), p(1.5 * d)
                if sd == 'No': lo, hi = min(lo, hi), max(lo, hi)
                be = ask + FEE
                call = 'Final' if lo >= be else ('Lean' if mid >= be else 'Pass')
                rows.append({'k': k, 'side': sd, 'ask': round(ask * 100), 'pays': round(1 / ask, 2), 'be': round(be * 100), 'mkt': round(100 * (m if sd == 'Yes' else 1 - m), 1),
                             'mid': round(100 * mid, 1), 'lo': round(100 * lo, 1), 'hi': round(100 * hi, 1), 'call': call, 'edge_lo': round(100 * (lo - be), 1), 'edge_mid': round(100 * (mid - be), 1)})
        n2 = sum(1 for k, ya, yb, na in r if yb > 0 and ya > 0 and ya - yb <= 0.08)
        RES.append({'game': g, 'player': full, 'stat': st, 'delta': d, 'cond': cond, 'prefix': pre, 'rows': rows, 'n_two_sided': n2, 'thin': n2 < 3})
    json.dump({'at': Q['at1'], 'res': RES}, open('/home/claude/wedger/final9b/engine.json', 'w'))
    UNIT = {'rec': '', 'recyd': ' yds', 'rush': ' yds', 'pass': ' yds'}
    for R in RES:
        clear = [x for x in R['rows'] if x['call'] != 'Pass']
        best = sorted(clear, key=lambda x: (x['call'] != 'Final', -(x['edge_lo'] if x['call'] == 'Final' else x['edge_mid'])))
        tag = best[0] if best else None
        print(f"{R['game']:8s} {R['player'][:20]:20s} {R['stat']:5s} Δ{R['delta']:+} | " + (f"{tag['call']} {int(tag['k'])}+ {tag['side']} {tag['ask']}¢ BE{tag['be']} mkt{tag['mkt']} us {tag['lo']}-{tag['hi']} (mid {tag['mid']})" if tag else 'pass') + f" | clears {len(clear)}/{len(R['rows'])}" + (' THIN' if R['thin'] else ''))
    

if __name__ == '__main__':
    import os
    CC = json.load(open('/home/claude/wedger/final9b/cands2.json')) if os.path.exists('/home/claude/wedger/final9b/cands2.json') else C
    run(CC)
