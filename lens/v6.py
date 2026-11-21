"""Wedge % v6: the market's own number (mid of bid and ask) moved by the matchup lens, with weights fit on every settled
Robinhood player prop from Weeks 7-9 (10,123 lines) and kept only where they beat the market out of sample.
Receiving and rushing lines move; passing, TD and interception lines stay at the market (the lens didn't beat it there).
Receiving lines also carry one extra term from bt/cal_v6_terms.json (blitz split x pass volume, added Tue Nov 17).
Range = 10th-90th percentile across 40 refits on resampled games."""
import json, sys, math
import numpy as np
sys.path.insert(0, '/home/claude/wedger/lens'); import core
W = '/home/claude/wedger/'
WEEK = 11   # the week being priced; tables use every game before it (was a hard-coded 10 in each default)
CAL = json.load(open(W + 'bt/cal_v6.json'))
COLS = CAL['cols']; GL = CAL['group_levels']; B = np.array(CAL['boot'])
COEF = np.array([CAL['coef'][f'grp.{g}'] for g in GL] + [CAL['coef'][c] for c in COLS])
FAM = CAL['families']; GRP = CAL['groups']
LABEL = {'dvp': 'What the defense allows', 'overlap': 'Where the targets go', 'look': 'Against the blitz', 'volume': 'Volume the defense faces',
         'comp': 'Comparable defenses', 'consist': 'Consistency at this line', 'dir': 'Run direction', 'box': 'Box count'}
# extra terms (Tue Nov 17, bt/next_steps): coef * feature a * feature b on one family, on top of the weights above, which stay fixed.
# Kept only because each beat the market and the formula without it on held-out weeks (bt/next_steps/terms.py, adopt.py).
import os as _os
TERMS = json.load(open(W + 'bt/cal_v6_terms.json'))['terms'] if _os.path.exists(W + 'bt/cal_v6_terms.json') else []
for _t in TERMS: LABEL[_t['name']] = {'look_x_volume': 'Blitz split meets pass volume'}.get(_t['name'], _t['label'])
_T = {}
def tables(week=None, dl=W + 'dl18/'):
    week = WEEK if week is None else week
    if week not in _T:
        live, st, pos = core.load(dl); _T[week] = (core.Tables(live, st, pos, week), st)
    return _T[week]
def pid_of(name, team, week=None):
    week = WEEK if week is None else week
    T, st = tables(week); k = core.nn(name)
    s = st[(st.nn == k) & (st.week < week)].sort_values('week')
    if not len(s): return None
    s2 = s[s.team == team]
    return (s2 if len(s2) else s).iloc[-1].player_id
lg = lambda p: math.log(p / (1 - p)); sg = lambda z: 1 / (1 + math.exp(-z))
def detail(name, team, opp, stat, line, mid_c, week=None, margin=None):
    week = WEEK if week is None else week
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
    z0 = lg(mid); ex, exB, contrib = 0.0, np.zeros(len(B)), {}
    for t in TERMS:
        if t['family'] != fam: continue
        v = float(np.clip(f.get(t['a'], 0.0) * f.get(t['b'], 0.0), -t['clip'], t['clip']))
        ex += t['coef'] * v; exB += np.array(t['boot']) * v; contrib[t['name']] = round(100 * (sg(z0 + t['coef'] * v) - mid), 2)
    p = sg(z0 + x @ COEF + ex); ps = np.array([sg(z0 + x @ b + e) for b, e in zip(B, exB)])
    for i, c in enumerate(COLS):
        if c.startswith(fam + '.'):
            k = c.split('.')[1]; contrib[k] = round(100 * (sg(z0 + COEF[len(GL) + i] * x[len(GL) + i]) - mid), 2)
    lo_, hi_ = float(np.percentile(ps, 10)), float(np.percentile(ps, 90))
    out.update({'p': 100 * p, 'lo': 100 * lo_, 'hi': 100 * hi_,
                'feats': {k: round(v, 3) for k, v in f.items() if f'{fam}.{k}' in cols}, 'contrib': contrib, 'moved': True})
    if BLEND:   # the two-brain join (bt/next_steps/brain_blend.py): p = cos^2(t) * lens + sin^2(t) * research projection, on p, lo and hi
        r = research_p(pid, team, opp, stat, line, mid, week, margin)
        if r is not None:
            w = math.sin(BLEND['params'][0]) ** 2; q = r['p2']
            pb, lb, hb = (1 - w) * p + w * q, (1 - w) * lo_ + w * q, (1 - w) * hi_ + w * q
            contrib['research'] = round(100 * (pb - p), 2)
            out.update({'p': 100 * pb, 'lo': 100 * min(lb, hb), 'hi': 100 * max(lb, hb), 'p_lens': 100 * p, 'research': {**r, 'p2': round(100 * q, 1), 'w': round(w, 4)}})
    return out
# ---------------- projection 2, the research method's number for the exact line (same definition as the 1,000-run test)
BLEND = json.load(open(W + 'bt/brain_blend.json')) if _os.path.exists(W + 'bt/brain_blend.json') else None
if BLEND and BLEND.get('form') != 'trig blend': BLEND = None
LABEL['research'] = 'Research projection'
_CTX, _RP, _GM = {}, {}, None
def _ctx(week):
    if week not in _CTX:
        import pandas as pd; sys.path.insert(0, W + 'brain'); import gates
        dl = W + 'dl19/'
        st = pd.read_csv(dl + 'stats_player_week_2026.csv', low_memory=False)
        pbp = pd.read_csv(dl + 'play_by_play_2026.csv.gz', low_memory=False, usecols=['week', 'qtr', 'rusher_player_id', 'receiver_player_id', 'rushing_yards', 'receiving_yards'])
        _CTX[week] = (gates, gates.Ctx(st, pbp, pd.read_csv(dl + 'games.csv'), week))
    return _CTX[week]
_UN = {'LAR': 'LA', 'WSH': 'WAS', 'JAC': 'JAX'}
def _margin(team, week):
    """his team's expected margin from nflverse's line for the week (the test's source), when the caller doesn't pass the card's"""
    global _GM
    if _GM is None:
        import pandas as pd; g = pd.read_csv(W + 'dl22/games.csv'); _GM = g[(g.season == 2026) & (g.game_type == 'REG')]
    t = _UN.get(team, team); g = _GM[(_GM.week == week) & ((_GM.home_team == t) | (_GM.away_team == t))]
    if not len(g): return 0.0
    g = g.iloc[0]; return float(g.spread_line) if g.home_team == t else -float(g.spread_line)
def research_p(pid, team, opp, stat, line, mid, week, margin=None):
    """hit rate at this threshold pooled over his 2026 games before the week, games in the script the spread points to, one-score
    games and his last 3 games, shrunk to the market mid with 6 games of weight (bt/brain_blend.json)."""
    week = WEEK if week is None else week; k = int(round(line + 0.5)); em = _margin(team, week) if margin is None else float(margin)
    key = (pid, team, stat, k, week, round(em, 1))
    if key not in _RP:
        gates, C = _ctx(week); c = gates.check(C, pid, _UN.get(team, team), stat, k, 'Yes', em)
        g = c['LOG']['games']; h_a, n_a = sum(1 for _, v, _ in g if v >= k), len(g)
        bk = c['SCRIPT']['buckets']; ls = c['SCRIPT']['likely']
        h_s, n_s = bk.get(ls, [0, 0]); h_c, n_c = bk.get('close', [0, 0]); g3 = g[-3:]; h_3, n_3 = sum(1 for _, v, _ in g3 if v >= k), len(g3)
        _RP[key] = {'h': h_a + h_s + h_c + h_3, 'n': n_a + n_s + n_c + n_3, 'all': [h_a, n_a], 'script': [h_s, n_s, ls], 'close': [h_c, n_c], 'last3': [h_3, n_3]}
    r = dict(_RP[key]); a = BLEND.get('prior_games', 6)
    r['p2'] = min(max((r['h'] + a * mid) / (r['n'] + a), 0.01), 0.99)
    return r
def prob(name, team, opp, stat, line, mid_c, week=None): return detail(name, team, opp, stat, line, mid_c, week)['p']
import re as _re
FIXG = {'LA': 'LAR', 'WAS': 'WSH', 'JAC': 'JAX'}
def detail_game(name, game, stat, line, mid_c, week=None):
    week = WEEK if week is None else week
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
