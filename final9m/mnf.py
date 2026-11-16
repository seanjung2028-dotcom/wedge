"""BUF @ MIN final card, Monday re-run (Kalshi ladders checked Mon Nov 9 2:39 PM CT), with the matchup lens.

Each thesis carries a ledger: every lens step that moved our number, in probability points at the market's median
(+ means more than the market expects). The net is converted into stat units at the ladder's slope, exactly as on
Saturday's card, then every two-sided rung is re-read under the same rules (final line / conditional lean / pass).
Writes final9m/analysis.json."""
import json, math, sys
import numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/wedger/final9b')
import engine
from engine import market_curve, S
W = '/home/claude/wedger/'
K = json.load(open(W + 'pull1109/kalshi_1109.json'))
engine.Q = {'at0': K['at0'], 'at1': K['at1'], 'q': {t: tuple(v[:5]) for t, v in K['q'].items()}}
FEE = 0.02
SER = {'pass': 'KXNFLPASSYDS', 'recyd': 'KXNFLRECYDS', 'rec': 'KXNFLREC', 'rush': 'KXNFLRSHYDS'}
def prefix_for(nm, st):
    norm = lambda x: x.lower().replace("'", '').replace('.', '')
    for t, v in engine.Q['q'].items():
        if t.split('-')[0] == SER[st] and norm(nm) in norm(v[4]): return t.rsplit('-', 1)[0], v[4].split(':')[0]
    raise KeyError((nm, st))

# (player, stat, ledger[(lens step, points, finding)], personnel condition)
C = [
 ('Justin Jefferson', 'recyd', [
   ('QB tendency', +2, 'With Wentz he drew 34% of the targets (13 of 38), against 22% for the season.'),
   ('Comparable game', +1, "The closest coverage match is Week 1 vs GB, Wentz's other dome start: 9 targets, 8 catches, 92 yards."),
   ('Alignment allowed', -1, 'BUF sends only 40.3% of its targets allowed to WRs outside the numbers (29th), and 88% of his targets come outside.'),
   ('Environment', +1, 'Dome. His 55 at CHI came in the rain.'),
   ('Consistency', -1, '80+ in 2 of 6 games (92, 79 the closest miss).')], ''),
 ('T.J. Hockenson', 'recyd', [
   ('QB tendency', +2, "Wentz threw 34% of his targets to TEs, third most of any QB (league 24%)."),
   ('Position allowed', +2, 'BUF allows 9.1 TE targets and 70.6 TE yards a game, both 4th most.'),
   ('Comparable game', +1, 'Against the defenses most like BUF: 119 vs MIA (RB/TE-funnel), 58 vs DET (pass-heavy faced). With Wentz vs GB: 36.'),
   ('Look split', -1, 'BUF blitzes 38.6% (7th). His share drops against the blitz (13% vs 24% without).'),
   ('Consistency', -1, '40+ in 2 of 7 games.')], ''),
 ('Jordan Addison', 'recyd', [
   ('QB tendency', -2, "Wentz threw only 39.5% of his targets to WRs outside (29th); Addison's come 79% outside, and he had 0 and 21 yards with Wentz."),
   ('Alignment allowed', -1, 'BUF allows the 4th-lowest share of targets to outside WRs (40.3%).'),
   ('Volume', +1, 'Jennings is out, so the WR targets concentrate on Jefferson and Addison.')], ''),
 ('Carson Wentz', 'pass', [
   ('Volume', -2, 'He threw 23 times in both starts; MIN is 29th in pass attempts and 20th in neutral pass rate.'),
   ('Defense allowed', +2, 'BUF faces 38.3 attempts and 269 passing yards a game, 2nd and 3rd most.'),
   ('Script', +1, 'BUF is a 3.5-point favorite (64% on Kalshi), so the trailing script adds throws.'),
   ('Comparable game', -1, "The closest coverage match, GB in Week 1: 133 yards on 23 attempts.")], ''),
 ('James Cook', 'rush', [
   ('Run scheme', +1, "BUF has the league's best inside-run success rate (52.8%) and runs inside 66.5% of the time. MIN allows 3.96 inside (13th most)."),
   ('Defense allowed', +1, 'MIN allows 4.60 yards a carry (11th most), with light boxes (6.5, 24th) and a blitz on 72.8% of dropbacks.'),
   ('Script', +1, 'BUF is favored and 3rd in rush attempts (29.6 a game).'),
   ('Matchup-proof', 0, 'Against the three top-10 run defenses he has faced: 75 (12 carries), 111, 80.'),
   ('Consistency', 0, '90+ in 4 of 7. 110+ scrimmage yards in 4 of 7.')], ''),
 ('Josh Allen', 'rush', [
   ('Look split', -2, 'Against the blitz he scrambles on 4.8% of dropbacks, half his 9.7% without it, and MIN blitzes 72.8%, by far the most.'),
   ('Defense allowed', -1, 'MIN allows 1.1 QB scrambles and 8 scramble yards a game (5th fewest).'),
   ('Comparable game', +1, 'Against the other high-sack defenses (HOU, DET): 23 and 69.')], 'Only if Dawkins plays.'),
 ('Khalil Shakir', 'recyd', [
   ('Alignment overlap', +2, "MIN allows 15.6% of targets to WRs in the middle (4th most) and Allen throws there 15.6% (5th most). Shakir is BUF's middle WR (39% of his targets)."),
   ('Look split', +1, 'He gets 22.9% of the targets against the blitz, 17.9% without; MIN blitzes 72.8%.'),
   ('Position allowed', -1, 'MIN allows the 6th-fewest WR yards (122.7 a game).'),
   ('Volume', +1, 'Josh Palmer is out.'),
   ('Consistency', 0, '40+ in 4 of 7.')], ''),
 ('Keon Coleman', 'recyd', [
   ('Look split', +2, 'His share jumps against the blitz: 18.6% vs 11.4% without.'),
   ('Position allowed', -1, 'MIN allows the 6th-fewest WR yards.'),
   ('Volume', +1, 'Josh Palmer is out.'),
   ('Consistency', -1, '25+ in 4 of 7, but 1, 4 and 7 in the misses.')], ''),
 ('DJ Moore', 'recyd', [
   ('Volume', +1, "He led BUF in targets in each of his three full games (8, 10, 7)."),
   ('Alignment allowed', 0, "By location MIN is 20th in outside-WR targets allowed (44.8%). No edge either way."),
   ('Look split', -1, 'His share falls against the blitz (11.4% vs 15.4%).'),
   ('Position allowed', -1, 'MIN allows the 6th-fewest WR yards.')], ''),
 ('Dalton Kincaid', 'recyd', [
   ('Position allowed', -2, 'MIN allows the fewest TE catches (3.1 a game) and 2nd-fewest TE yards (39).'),
   ('Look split', 0, "No blitz split (18.6% vs 17.9%)."),
   ('Comparable game', +1, 'Against the other high-sack defenses (HOU, DET): 130 and 95.')], ''),
 ('Jordan Mason', 'rush', [
   ('Run scheme', -2, "MIN's inside runs average 3.02 yards (30th) with a 30.2% success rate (31st); BUF allows 3.90 inside."),
   ('Defense allowed', -1, 'BUF allows 3.94 yards a carry (9th fewest) and stacks 6.8 in the box (4th most).'),
   ('Volume', +1, 'Claiborne is out, so the carries split between Mason, Jones and DeeJay Dallas.'),
   ('Script', -1, 'No schematic edge for MIN on the ground, and the trailing script cuts carries.')], ''),
 ('Aaron Jones', 'rush', [
   ('Run scheme', -1, 'BUF is 24th in yards allowed on outside runs (4.18), where MIN averages 4.94 (9th).'),
   ('Defense allowed', -1, 'BUF allows 3.94 yards a carry (9th fewest).'),
   ('Volume', +1, 'Claiborne is out.')], ''),
]
ALIAS = {'James Cook III': 'James Cook', 'Aaron Jones Sr.': 'Aaron Jones'}
L = pd.read_csv(W + 'final9/logs.csv'); L = L[L.season == 2026]
COL = {'pass': 'pyd', 'rush': 'rushyd', 'rec': 'rec', 'recyd': 'recyd'}
def call_of(r):
    if r['edge_lo'] >= 0.5: return 'Final line'
    if r['edge_mid'] >= 0.5: return 'Conditional lean'
    return 'Pass'
OUT = []
for nm, stt, ledger, cond in C:
    pre, full = prefix_for(nm, stt); r = engine.ladder(pre); xs, ys = market_curve(r)
    grid = np.linspace(xs[0], xs[-1], 2000); sv = np.array([S(xs, ys, x) for x in grid]); med = float(grid[np.argmin(abs(sv - 0.5))])
    h = max(1e-6, (xs[-1] - xs[0]) / 40); slope = abs(S(xs, ys, med - h) - S(xs, ys, med + h)) / (2 * h)
    net = sum(x[1] for x in ledger); pts = abs(net)
    d = 0.0 if net == 0 else float(np.sign(net) * (pts / 100) / slope); unit = 0.1 if stt == 'rec' else 1; d = round(round(d / unit) * unit, 1)
    side = 'Yes' if d > 0 else ('No' if d < 0 else 'Both'); rows = []
    for k, ya, yb, na in r:
        if not (yb > 0 and ya > 0 and ya - yb <= 0.08): continue
        m = S(xs, ys, k)
        for sd in (['Yes', 'No'] if side == 'Both' else [side]):
            ask = ya if sd == 'Yes' else na
            if not (0.03 < ask < 0.97): continue
            def pf(delta):
                s_ = S(xs, ys, k - delta); return s_ if sd == 'Yes' else 1 - s_
            mid, lo, hi = pf(d), pf(d / 2), pf(1.5 * d)
            if sd == 'No': lo, hi = min(lo, hi), max(lo, hi)
            be = ask + FEE
            rows.append({'k': k, 'side': sd, 'ask': round(ask * 100), 'pays': round(1 / ask, 2), 'be': round(be * 100), 'mkt': round(100 * (m if sd == 'Yes' else 1 - m), 1),
                         'mid': round(100 * mid, 1), 'lo': round(100 * lo, 1), 'hi': round(100 * hi, 1), 'edge_lo': round(100 * (lo - be), 1), 'edge_mid': round(100 * (mid - be), 1)})
    n2 = sum(1 for k, ya, yb, na in r if yb > 0 and ya > 0 and ya - yb <= 0.08)
    lg = L[L.name == ALIAS.get(full, full)].sort_values('week')
    vals = [(int(w_), float(v_), o_) for w_, v_, o_ in zip(lg.week, lg[COL[stt]], lg.opp)]
    for x in rows:
        x['call'] = call_of(x); hit = [v for v in vals if (v[1] >= x['k'] if x['side'] == 'Yes' else v[1] < x['k'])]; x['n_hit'], x['n'] = len(hit), len(vals)
    thin = n2 < 3 or pts <= 2 or d == 0
    why_thin = ('no edge either way (the lens nets to zero)' if d == 0 else "only one rung has a two-sided quote, so the ladder can't be read" if n2 < 3 else
                'evidence too thin (2 points or less)' if pts <= 2 else '')
    elig = [x for x in rows if x['call'] != 'Pass'] if not thin else []
    KF = lambda x: (-round(x['edge_lo'], 1), -round(x['edge_mid'], 1), -x['mid']); KL = lambda x: (-round(x['edge_mid'], 1), -round(x['edge_lo'], 1), -x['mid'])
    fin = sorted([x for x in elig if x['call'] == 'Final line'], key=KF); lea = sorted([x for x in elig if x['call'] == 'Conditional lean'], key=KL)
    pick = (fin or lea or [None])[0]
    others = [x for x in rows if pick is None or (x['k'], x['side']) != (pick['k'], pick['side'])]
    alt = sorted(others, key=KF if (pick and pick['call'] == 'Final line') else KL)[0] if others else None
    if pick: pick['final_at'] = int(math.floor(pick['lo'] - 2 - 0.5 + 1e-9)); pick['lean_at'] = int(math.floor(pick['mid'] - 2 - 0.5 + 1e-9))
    best_any = dict(sorted(rows, key=lambda x: (-x['edge_mid'], -x['edge_lo']))[0]) if rows else None
    if best_any: best_any['lean_at'] = int(math.floor(best_any['mid'] - 2 - 0.5 + 1e-9)); best_any['final_at'] = int(math.floor(best_any['lo'] - 2 - 0.5 + 1e-9))
    OUT.append({'game': 'BUF@MIN', 'name': nm, 'player': full, 'stat': stt, 'delta': d, 'pts': pts, 'net': net, 'ledger': [{'step': a, 'pts': b, 'text': c} for a, b, c in ledger],
                'cond': cond, 'thin': thin, 'why_thin': why_thin, 'prefix': pre, 'vals': vals, 'rows': rows, 'pick': pick, 'alt': alt, 'closest': best_any,
                'call': pick['call'] if pick else 'Pass', 'med': round(med, 1), 'slope': slope})
json.dump({'at': K['at1'], 'res': OUT}, open(W + 'final9m/analysis.json', 'w'))
U = {'rec': ' rec', 'recyd': ' rec yds', 'rush': ' rush yds', 'pass': ' pass yds'}
lab = lambda x, st: (f"{int(x['k'])}+" if x['side'] == 'Yes' else f"under {int(x['k'])}") + U[st]
for o in OUT:
    p, a, cl = o['pick'], o['alt'], o['closest']
    s = f"{o['player'][:18]:18s} {o['stat']:5s} net{o['net']:+d} med{o['med']:6.1f} Δ{o['delta']:+5.1f} {o['call'][:5]:5s} "
    if p: s += f"{lab(p, o['stat'])} {p['side']} {p['ask']}c BE{p['be']} mkt{p['mkt']} us{p['lo']}-{p['hi']} lo{p['edge_lo']:+} mid{p['edge_mid']:+} hits {p['n_hit']}/{p['n']} finalAt{p['final_at']}"
    else: s += f"[{o['why_thin'] or 'nothing clears'}]" + (f" closest {lab(cl, o['stat'])} {cl['side']} {cl['ask']}c BE{cl['be']} us{cl['lo']}-{cl['hi']} mid{cl['edge_mid']:+}" if cl else '')
    print(s)
