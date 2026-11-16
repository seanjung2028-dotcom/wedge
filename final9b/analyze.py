"""Turn engine.json (every two-sided rung, any price) into per-thesis decisions under the doc's rules.
Final line: our low end clears break-even (ask + 2c fees) by at least half a point.
Conditional lean: our middle clears break-even by at least half a point, but the low end doesn't (smaller margins are inside rounding).
Pass: nothing clears at our middle, or the evidence is too thin (no view, <=2 evidence points, or fewer than 3 two-sided rungs)."""
import json, sys, math
import pandas as pd
sys.path.insert(0, '/home/claude/wedger/final9b')
E = json.load(open('/home/claude/wedger/final9b/engine.json'))
CC = json.load(open('/home/claude/wedger/final9b/cands2.json'))
from calib import PTS  # noqa  (re-runs calib printing; harmless)
L = pd.read_csv('/home/claude/wedger/final9/logs.csv'); L = L[L.season == 2026]
COL = {'pass': 'pyd', 'rush': 'rushyd', 'rec': 'rec', 'recyd': 'recyd'}
ALIAS = {'Kyle Pitts Sr.': 'Kyle Pitts', 'James Cook III': 'James Cook'}
def call_of(r):
    if r['edge_lo'] >= 0.5: return 'Final line'
    if r['edge_mid'] >= 0.5: return 'Conditional lean'
    return 'Pass'
OUT = []
for R, (g, nm, st, d, w, cond) in zip(E['res'], CC):
    pts = PTS[nm]
    lg = L[L.name == ALIAS.get(R['player'], R['player'])].sort_values('week')
    vals = [(int(w_), float(v_), o_) for w_, v_, o_ in zip(lg.week, lg[COL[st]], lg.opp)]
    rows = []
    for r in R['rows']:
        r = dict(r); r['call'] = call_of(r)
        k = r['k']; hit = [v for v in vals if (v[1] >= k if r['side'] == 'Yes' else v[1] < k)]
        r['n_hit'], r['n'] = len(hit), len(vals); rows.append(r)
    thin = R['thin'] or pts <= 2 or d == 0
    why_thin = ('no edge either way (our evidence nets to zero)' if d == 0 else
                'only one rung has a two-sided quote, so the ladder can\'t be read' if R['thin'] else
                'evidence too thin (2 points or less)' if pts <= 2 else '')
    elig = [r for r in rows if r['call'] != 'Pass'] if not thin else []
    KF = lambda r: (-round(r['edge_lo'], 1), -round(r['edge_mid'], 1), -r['mid'])   # final lines: low-end margin, then middle, then likelier
    KL = lambda r: (-round(r['edge_mid'], 1), -round(r['edge_lo'], 1), -r['mid'])   # leans: middle margin, then low end, then likelier
    fin = sorted([r for r in elig if r['call'] == 'Final line'], key=KF)
    lea = sorted([r for r in elig if r['call'] == 'Conditional lean'], key=KL)
    pick = (fin or lea or [None])[0]
    # closest alternative: the best other rung by the same yardstick the pick won on
    others = [r for r in rows if pick is None or (r['k'], r['side']) != (pick['k'], pick['side'])]
    alt = sorted(others, key=KF if (pick and pick['call'] == 'Final line') else KL)[0] if others else None
    # price at which it becomes / stays a final line: lo - (ask + 2) >= 0.1
    if pick:
        pick['final_at'] = int(math.floor(pick['lo'] - 2 - 0.5 + 1e-9))
        pick['lean_at'] = int(math.floor(pick['mid'] - 2 - 0.5 + 1e-9))
    best_any = sorted(rows, key=lambda r: (-r['edge_mid'], -r['edge_lo']))[0] if rows else None
    if best_any is not None:
        best_any = dict(best_any); best_any['lean_at'] = int(math.floor(best_any['mid'] - 2 - 0.5 + 1e-9)); best_any['final_at'] = int(math.floor(best_any['lo'] - 2 - 0.5 + 1e-9))
    likely = sorted(rows, key=lambda r: -r['mid'])[0] if rows and d != 0 else None
    OUT.append({'game': g, 'name': nm, 'player': R['player'], 'stat': st, 'delta': d, 'pts': pts, 'cond': cond, 'thin': thin, 'why_thin': why_thin,
                'prefix': R['prefix'], 'vals': vals, 'rows': rows, 'pick': pick, 'alt': alt, 'closest': best_any, 'likely': likely,
                'call': pick['call'] if pick else 'Pass'})
json.dump({'at': E['at'], 'res': OUT}, open('/home/claude/wedger/final9b/analysis.json', 'w'))
U = {'rec': ' rec', 'recyd': ' rec yds', 'rush': ' rush yds', 'pass': ' pass yds'}
def lab(r, st): return (f"{int(r['k'])}+" if r['side'] == 'Yes' else f"under {int(r['k'])}") + U[st]
if __name__ == '__main__':
    for o in OUT:
        p, a = o['pick'], o['alt']
        s = f"{o['game']:8s} {o['player'][:19]:19s} {o['call'][:5]:5s} "
        if p: s += f"{lab(p,o['stat'])} {p['side']} {p['ask']}c BE{p['be']} mkt{p['mkt']} us{p['lo']}-{p['hi']} lo{p['edge_lo']:+} mid{p['edge_mid']:+} hits {p['n_hit']}/{p['n']} finalAt{p['final_at']}"
        else: s += f"[{o['why_thin'] or 'nothing clears'}]"
        if a: s += f" || alt {lab(a,o['stat'])} {a['ask']}c us{a['lo']}-{a['hi']} lo{a['edge_lo']:+} mid{a['edge_mid']:+} {a['n_hit']}/{a['n']}"
        print(s)
