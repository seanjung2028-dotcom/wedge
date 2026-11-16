import json, sys, numpy as np
sys.path.insert(0, '/home/claude/wedger/final9b')
from engine import ladder, market_curve, S, prefix_for
from cands import C
# evidence size in probability points at the market's median (same judgments as the first card, without the backtest)
PTS = {'Joe Burrow': 5, 'Tee Higgins': 4, 'Bijan Robinson': 4, 'Kyle Pitts': 3, 'Chase Brown': 0, 'Dallas Goedert': 4, 'Malik Nabers': 5, 'Bryce Young': 6, 'Chuba Hubbard': 4,
       'Ollie Gordon': 5, 'Greg Dulcich': 5, 'Jahmyr Gibbs': 0, 'Braelon Allen': 4, 'Kenneth Walker': 4, 'Harold Fannin': 3, 'Tyler Shough': 3, 'Chris Olave': 2, 'Jayden Daniels': 4,
       'Puka Nacua': 5, 'CeeDee Lamb': 3, 'Jonathan Taylor': 3, 'Javonte Williams': 2, 'Justin Herbert': 5, 'Woody Marks': 3, 'George Kittle': 5, 'Ashton Jeanty': 4,
       'Christian McCaffrey': 3, 'Smith-Njigba': 6, 'Trey McBride': 5, 'Tyler Allgeier': 3, 'Matthew Golden': 5, 'Rhamondre Stevenson': 3, 'Bucky Irving': 4, 'Caleb Williams': 5,
       'Colston Loveland': 6, "D'Andre Swift": 2, 'Josh Allen': 2, 'James Cook': 0, 'Hockenson': 3, 'Carson Wentz': 4}
out = []
for g, nm, st, d, w, cond in C:
    pre, full = prefix_for(g, nm, st); r = ladder(pre); xs, ys = market_curve(r)
    # market median: where S crosses 0.5
    grid = np.linspace(xs[0], xs[-1], 2000); sv = np.array([S(xs, ys, x) for x in grid])
    med = float(grid[np.argmin(abs(sv - 0.5))])
    h = max(1e-6, (xs[-1] - xs[0]) / 40); slope = abs(S(xs, ys, med - h) - S(xs, ys, med + h)) / (2 * h)  # prob per unit
    pts = PTS[nm]; delta = 0 if pts == 0 else np.sign(d) * (pts / 100) / slope
    unit = 0.1 if st == 'rec' else 1
    delta = round(delta / unit) * unit
    out.append((g, nm, st, float(round(delta, 1)), w, cond))
    print(f"{g:8s} {nm:20s} {st:5s} med {med:6.1f} slope {100*slope:5.2f}pts/unit  pts {pts} -> delta {delta:+.1f} (was {d:+})")
open('/home/claude/wedger/final9b/cands2.json', 'w').write(json.dumps(out))
