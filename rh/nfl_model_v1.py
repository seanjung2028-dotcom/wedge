"""Wedger NFL prop model (shared by the live Week 7 build and the backtests).

1. Cases: a player's games (recent seasons weighted more) split into thirds by volume (targets / carries / touches / attempts).
   P(Yes | case) = weighted hit rate in that third, nudged toward his overall rate. Case odds this week = how the situational
   splits (QB, lineup, No. 1 competitor, defense) fall across the thirds. -> P_cases and a base projection.
2. Adjustments to the base projection (each bounded and shrunk):
   defense   opponent's 2026 production allowed to the position vs league average
   coverage  yards per target allowed by the opponent's active coverage players (PFR) vs league
   script    the player's averages when his team led by 8+, stayed within a score or trailed by 8+, weighted by this
             game's odds of each (normal margin around the spread, SD 13.5)
   total     the team's implied points (books' team totals) vs its 2026 scoring
   weather   wind, gusts, rain and cold at outdoor venues
3. P_model = chance the adjusted projection clears the line: gamma for yards (CV from his games, shrunk to a position prior),
   Poisson for receptions / pass TDs / INTs, 1 - e^-m for touchdowns.
4. Calibration (from the backtests in nfl_model_bt.py): our raw chances were overconfident, so
   P_ours = 0.5 + 0.65 x ((P_cases + P_model) / 2 - 0.5)            (best shrink on 3,400 2025 player-games)
   Wedger = 0.7 x market + 0.3 x P_ours                               (best weights on Week 6's 334 real lines)
   market = the books' fair (no-vig) chance for that rung when the books price it, otherwise Robinhood's mid price.
"""
import math
import numpy as np
from scipy import stats

COL = {'rec': [4], 'recyd': [5], 'rushyd': [6], 'rryd': [5, 6], 'passyd': [7], 'passtd': [8], 'int': [9], 'td': [10]}
VOL = {'rec': [13], 'recyd': [13], 'rushyd': [14], 'rryd': [13, 14], 'td': [13, 14], 'passyd': [15], 'passtd': [15], 'int': [15]}
VUNIT = {'rec': 'targets', 'recyd': 'targets', 'rushyd': 'carries', 'rryd': 'touches', 'td': 'touches', 'passyd': 'attempts',
         'passtd': 'attempts', 'int': 'attempts'}
SEASON_W = {0: 1.0, 1: 0.75, 2: 0.5, 3: 0.35}
CV_PRIOR = {('recyd', 'WR'): 0.70, ('recyd', 'TE'): 0.75, ('recyd', 'RB'): 0.95, ('rushyd', 'RB'): 0.55, ('rushyd', 'QB'): 0.85,
            ('rushyd', 'WR'): 1.2, ('passyd', 'QB'): 0.28, ('rryd', 'RB'): 0.5, ('rryd', 'WR'): 0.65}
SHRINK = 0.65
W_MKT = 0.70


def val(L, i, stat): return sum(L[i][c] or 0 for c in COL[stat])
def vol(L, i, stat): return sum(L[i][c] or 0 for c in VOL[stat]) if len(L[i]) > max(VOL[stat]) else 0


def season_weights(L, idx, target_yy):
    w = {i: SEASON_W.get(target_yy - L[i][0], 0.3) for i in idx}
    # role change: if his current-season snap share is far from his earlier share, lean harder on this season
    cur = [L[i][3] for i in idx if L[i][0] == target_yy and L[i][3] is not None]
    old = [L[i][3] for i in idx if L[i][0] != target_yy and L[i][3] is not None]
    if len(cur) >= 3 and len(old) >= 4 and abs(np.mean(cur) - np.mean(old)) >= 15:
        for i in idx:
            if L[i][0] != target_yy: w[i] *= 0.5
    return w


def cases(L, base, stat, line, pools, w):
    if len(base) < 4: return None
    v = sorted(vol(L, i, stat) for i in base)
    q1, q2 = float(np.quantile(v, 1 / 3)), float(np.quantile(v, 2 / 3))
    a, b = math.ceil(q1 - 1e-9), math.floor(q2 + 1e-9)
    if a > b: a = b = math.floor((q1 + q2) / 2 + 0.5)
    tier = lambda i: 0 if vol(L, i, stat) < a else (2 if vol(L, i, stat) > b else 1)
    hit = lambda i: val(L, i, stat) > line
    tw = sum(w[i] for i in base); P_all = sum(w[i] for i in base if hit(i)) / tw
    T = []
    for t in range(3):
        ids = [i for i in base if tier(i) == t]
        wn = sum(w[i] for i in ids); wh = sum(w[i] for i in ids if hit(i))
        T.append({'n': len(ids), 'h': sum(1 for i in ids if hit(i)), 'p': (wh + 2 * P_all) / (wn + 2),
                  'm': (sum(w[i] * val(L, i, stat) for i in ids) / wn) if wn else None, 'share': wn / tw})
    if sum(1 for t in T if t['n']) < 2: return None
    W = [0.0, 0.0, 0.0]
    pools = [p for p in pools if p]
    if pools:
        for ids in pools:
            pw = sum(w.get(i, 0) for i in ids)
            for t in range(3):
                W[t] += (sum(w.get(i, 0) for i in ids if tier(i) == t) + 3 * T[t]['share']) / (pw + 3) / len(pools)
    else:
        W = [t['share'] for t in T]
    live = [t for t in range(3) if T[t]['m'] is not None]
    p = sum(W[t] * T[t]['p'] for t in range(3))
    m0 = sum(W[t] * T[t]['m'] for t in live) / sum(W[t] for t in live)
    unit = VUNIT[stat]
    labels = [f'≤ {a - 1} {unit}', f'{a} {unit}' if a == b else f'{a}–{b} {unit}', f'{b + 1}+ {unit}']
    return {'a': a, 'b': b, 'T': T, 'W': W, 'p': p, 'm0': m0, 'labels': labels, 'P_all': P_all, 'tier': tier}


def script_split(L, base, stat, line, w, margin_of, probs, team_label):
    """Player averages / hit rates by final margin bucket, shrunk toward his overall; weighted by this game's script odds."""
    if not probs: return None
    tw = sum(w[i] for i in base)
    m_all = sum(w[i] * val(L, i, stat) for i in base) / tw
    p_all = sum(w[i] for i in base if val(L, i, stat) > line) / tw
    out, wsum, msum, psum = [], 0, 0, 0
    for k, lab, test in (('lead8', f'{team_label} win by 8+', lambda m: m >= 8), ('close', 'Within 7 either way', lambda m: -8 < m < 8),
                         ('trail8', f'{team_label} lose by 8+', lambda m: m <= -8)):
        ids = [i for i in base if margin_of(i) is not None and test(margin_of(i))]
        wn = sum(w[i] for i in ids)
        m = (sum(w[i] * val(L, i, stat) for i in ids) + 4 * m_all) / (wn + 4)
        p = (sum(w[i] for i in ids if val(L, i, stat) > line) + 4 * p_all) / (wn + 4)
        pr = probs[k]
        out.append({'k': k, 'label': lab, 'prob': round(pr, 3), 'n': len(ids), 'avg': round(m, 2), 'hit': round(p, 3)})
        msum += pr * m; psum += pr * p; wsum += pr
    return {'rows': out, 'mean': msum / wsum, 'p': psum / wsum, 'm_all': m_all}


def clip(x, lo, hi): return max(lo, min(hi, x))


def adjustments(stat, pos, ctx, script):
    """ctx: def (opponent dict), lg (league dict), cov, implied, ppg, ppg_n, wx (dict or None). Returns list of factors."""
    D, LG = ctx.get('def') or {}, ctx.get('lg') or {}
    grp = 'RB' if pos in ('RB', 'FB') else ('TE' if pos == 'TE' else ('WR' if pos == 'WR' else 'QB'))
    n = D.get('games', 0); shrink = n / (n + 4)
    F = []
    # defense vs position
    r = None; why = ''
    if stat in ('rec', 'recyd') and grp in ('WR', 'TE', 'RB'):
        k = f'{grp}_rec_pg' if stat == 'rec' else f'{grp}_yds_pg'
        if D.get(k) and LG.get(k): r = D[k] / LG[k]; why = f"allows {D[k]:.1f} {'catches' if stat == 'rec' else 'yds'}/g to {grp}s — #{D.get(k + '_rk', '?')} of 32, 1 = most"
    elif stat == 'rushyd' and grp == 'RB' and D.get('RB_rush_pg'):
        r = D['RB_rush_pg'] / LG['RB_rush_pg']; why = f"allows {D['RB_rush_pg']:.0f} rush yds/g to RBs — #{D.get('RB_rush_pg_rk', '?')} of 32"
    elif stat == 'rushyd' and D.get('ypc'):
        r = D['ypc'] / LG['ypc']; why = f"allows {D['ypc']:.2f} yds/carry — #{D.get('ypc_rk', '?')} of 32"
    elif stat == 'rryd' and D.get('RB_rush_pg') and grp == 'RB':
        r = (D['RB_rush_pg'] + D.get('RB_yds_pg', 0)) / (LG['RB_rush_pg'] + LG['RB_yds_pg']); why = f"allows {D['RB_rush_pg'] + D.get('RB_yds_pg', 0):.0f} scrimmage yds/g to RBs"
    elif stat in ('passyd', 'passtd') and D.get('WR_yds_pg'):
        tot = D['WR_yds_pg'] + D.get('TE_yds_pg', 0) + D.get('RB_yds_pg', 0); lt = LG['WR_yds_pg'] + LG['TE_yds_pg'] + LG['RB_yds_pg']
        r = tot / lt; why = f"allows {tot:.0f} receiving yds/g, EPA/dropback {D.get('epa_db', 0):+.2f} — #{D.get('epa_db_rk', '?')} of 32"
    elif stat == 'td':
        k = f'{grp}_td_pg' if grp in ('WR', 'TE', 'RB') else None
        if k and D.get(k) is not None and LG.get(k): r = (D[k] + 0.3) / (LG[k] + 0.3); why = f"allows {D[k]:.2f} TDs/g to {grp}s"
    if r is not None:
        F.append({'k': 'def', 'label': 'Defense vs position', 'f': clip(1 + shrink * 0.6 * (r - 1), 0.85, 1.15), 'why': why})
    # coverage players
    if stat in ('rec', 'recyd', 'rryd', 'passyd') and ctx.get('cov') is not None:
        c = ctx['cov']
        F.append({'k': 'cov', 'label': 'Coverage players', 'f': clip(1 + 0.5 * (c - 1), 0.93, 1.07), 'why': ctx.get('cov_why', '')})
    # game script
    if script and script.get('m_all'):
        F.append({'k': 'script', 'label': 'Game script', 'f': clip(script['mean'] / script['m_all'], 0.85, 1.15),
                  'why': ctx.get('script_why', '')})
    # implied team total
    if ctx.get('implied') and ctx.get('ppg'):
        lgp = LG.get('ppg', 23.0); pn = ctx.get('ppg_n', 6)
        ppg = (pn * ctx['ppg'] + 3 * lgp) / (pn + 3)
        e = 0.8 if stat in ('td', 'passtd') else 0.35
        F.append({'k': 'total', 'label': 'Team total', 'f': clip((ctx['implied'] / ppg) ** e, 0.85, 1.18),
                  'why': f"implied {ctx['implied']:.1f} pts vs {ctx['ppg']:.1f} per game so far"})
    # weather
    wx = ctx.get('wx')
    if wx:
        pen = 0.0; bits = []
        if wx['wind'] >= 20: pen += 0.08; bits.append(f"wind {wx['wind']:.0f} mph")
        elif wx['wind'] >= 15: pen += 0.04; bits.append(f"wind {wx['wind']:.0f} mph")
        if wx.get('gust', 0) >= 30: pen += 0.02; bits.append(f"gusts {wx['gust']:.0f} mph")
        if wx.get('precip_prob', 0) >= 50: pen += 0.03; bits.append(f"{wx['precip_prob']}% rain chance")
        if wx.get('temp', 60) <= 25: pen += 0.03; bits.append(f"{wx['temp']}°F")
        f = 1.0
        if stat in ('recyd', 'passyd', 'passtd'): f = 1 - pen
        elif stat == 'rec': f = 1 - pen / 2
        elif stat == 'rushyd': f = 1 + pen / 3
        elif stat == 'int': f = 1 + pen
        elif stat in ('td', 'rryd'): f = 1 - pen / 3
        F.append({'k': 'wx', 'label': 'Weather', 'f': f,
                  'why': (', '.join(bits) if bits else f"{wx['temp']}°F, wind {wx['wind']:.0f} mph — no effect")})
    elif ctx.get('roof'):
        F.append({'k': 'wx', 'label': 'Weather', 'f': 1.0, 'why': 'Indoors' if ctx['roof'] in ('dome', 'closed') else 'Retractable roof, likely closed'})
    return F


def player_cv(L, base, stat, pos, w):
    prior = CV_PRIOR.get((stat, pos), 0.8)
    xs = [(w[i], val(L, i, stat)) for i in base]
    tw = sum(a for a, _ in xs)
    if tw <= 0: return prior
    mu = sum(a * x for a, x in xs) / tw
    if mu <= 0 or len(xs) < 4: return prior
    var = sum(a * (x - mu) ** 2 for a, x in xs) / tw
    cv = clip(math.sqrt(var) / mu, 0.2, 1.6)
    k = len(xs) / (len(xs) + 8)
    return k * cv + (1 - k) * prior


def p_over(stat, m, line, cv):
    if m <= 0: return 0.0
    if stat in ('recyd', 'rushyd', 'rryd', 'passyd'):
        k = 1 / cv ** 2
        return float(stats.gamma.sf(line, k, scale=m / k))
    if stat == 'td':
        return float(1 - math.exp(-m))
    return float(1 - stats.poisson.cdf(math.floor(line), m))


def evaluate(L, base, stat, line, pos, pools, ctx, margin_of, script_probs, team_label, target_yy, p_books=None, w_mkt=None, shrink=None):
    w = season_weights(L, base, target_yy)
    C = cases(L, base, stat, line, pools, w)
    if not C: return None
    S = script_split(L, base, stat, line, w, margin_of, script_probs, team_label) if script_probs else None
    F = adjustments(stat, pos, ctx, S)
    prod = 1.0
    for f in F: prod *= f['f']
    prod = clip(prod, 0.7, 1.35)
    m = C['m0'] * prod
    cv = player_cv(L, base, stat, pos, w)
    P_model = p_over(stat, m, line, cv)
    raw = 0.5 * C['p'] + 0.5 * P_model
    sh = SHRINK if shrink is None else shrink
    P_ours = 0.5 + sh * (raw - 0.5)
    wm = W_MKT if w_mkt is None else w_mkt
    P = wm * p_books + (1 - wm) * P_ours if p_books is not None else P_ours
    return {'C': C, 'S': S, 'F': F, 'prod': prod, 'm': m, 'cv': cv, 'P_cases': C['p'], 'P_model': P_model, 'P_raw': raw,
            'P_ours': P_ours, 'P_books': p_books, 'P': P, 'w': w}
