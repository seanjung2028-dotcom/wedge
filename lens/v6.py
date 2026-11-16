"""Wedge % v6: the market's own number (mid of bid and ask) moved by the matchup lens, with weights fit on every settled
Robinhood player prop from Weeks 7-9 (10,123 lines) and kept only where they beat the market out of sample.
Receiving and rushing lines move; passing, TD and interception lines stay at the market (the lens didn't beat it there).
Range = 10th-90th percentile across 40 refits on resampled games."""
import json, sys, math
import numpy as np
sys.path.insert(0, '/home/claude/wedger/lens'); import core
W = '/home/claude/wedger/'
CAL = json.load(open(W + 'bt/cal_v6.json'))
COLS = CAL['cols']; GL = CAL['group_levels']; B = np.array(CAL['boot'])
COEF = np.array([CAL['coef'][f'grp.{g}'] for g in GL] + [CAL['coef'][c] for c in COLS])
FAM = CAL['families']; GRP = CAL['groups']
LABEL = {'dvp': 'What the defense allows', 'overlap': 'Where the targets go', 'look': 'Against the blitz', 'volume': 'Volume the defense faces',
         'comp': 'Comparable defenses', 'consist': 'Consistency at this line', 'dir': 'Run direction', 'box': 'Box count'}
_T = {}
def tables(week=10, dl=W + 'dl18/'):
    if week not in _T:
        live, st, pos = core.load(dl); _T[week] = (core.Tables(live, st, pos, week), st)
    return _T[week]
def pid_of(name, team, week=10):
    T, st = tables(week); k = core.nn(name)
    s = st[(st.nn == k) & (st.week < week)].sort_values('week')
    if not len(s): return None
    s2 = s[s.team == team]
    return (s2 if len(s2) else s).iloc[-1].player_id
lg = lambda p: math.log(p / (1 - p)); sg = lambda z: 1 / (1 + math.exp(-z))
def detail(name, team, opp, stat, line, mid_c, week=10):
    """-> dict(p, lo, hi, feats, contrib) in percent; p = market mid if the stat isn't moved or the player isn't found."""
    mid = min(max(mid_c / 100, 0.01), 0.99)
    out = {'p': 100 * mid, 'lo': 100 * mid, 'hi': 100 * mid, 'feats': {}, 'contrib': {}, 'moved': False}
    fam = FAM.get(stat); g = GRP.get(stat)
    if fam is None: return out
    cols = [c for c in COLS if c.startswith(fam + '.')]
    if not cols: return out
    T, _ = tables(week); pid = pid_of(name, team, week)
    if pid is None: return out
    f = core.features(T, pid, team, opp, stat, line, mid)
    x = np.zeros(len(GL) + len(COLS)); x[GL.index(g)] = 1.0
    for i, c in enumerate(COLS):
        if c.startswith(fam + '.'): x[len(GL) + i] = f.get(c.split('.')[1], 0.0)
    z0 = lg(mid); p = sg(z0 + x @ COEF); ps = np.array([sg(z0 + x @ b) for b in B])
    contrib = {}
    for i, c in enumerate(COLS):
        if c.startswith(fam + '.'):
            k = c.split('.')[1]; contrib[k] = round(100 * (sg(z0 + COEF[len(GL) + i] * x[len(GL) + i]) - mid), 2)
    out.update({'p': 100 * p, 'lo': float(100 * np.percentile(ps, 10)), 'hi': float(100 * np.percentile(ps, 90)),
                'feats': {k: round(v, 3) for k, v in f.items() if f'{fam}.{k}' in cols}, 'contrib': contrib, 'moved': True})
    return out
def prob(name, team, opp, stat, line, mid_c, week=10): return detail(name, team, opp, stat, line, mid_c, week)['p']
import re as _re
FIXG = {'LA': 'LAR', 'WAS': 'WSH', 'JAC': 'JAX'}
def detail_game(name, game, stat, line, mid_c, week=10):
    """Same as detail(), finding the player's team from the game ('AWY @ HOM')."""
    a, h = [FIXG.get(t, t) for t in game.split(' @ ')]
    T, st = tables(week); k = core.nn(name)
    s = st[(st.nn == k) & (st.week < week)].sort_values('week')
    team = s.team.iloc[-1] if len(s) else a
    if team not in (a, h):
        s2 = s[s.team.isin([a, h])]; team = s2.team.iloc[-1] if len(s2) else a
    return detail(name, team, h if team == a else a, stat, line, mid_c, week)
def line_of(contract):
    m = _re.search(r'Over ([\d.]+)', contract); return float(m.group(1)) if m else 0.5
