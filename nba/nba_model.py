"""Wedger NBA prop model: same philosophy as the NFL model (nfl_model.py).

Bear / base / bull usage cases by minutes, a projection = case average x this game's adjustments
(defense vs position, pace, game script from the spread, team total, rest, teammates out), a distribution
priced at the projection, and a market-anchored blend.
"""
import math, re, unicodedata, collections
import numpy as np
import pandas as pd
from scipy import stats

STATS = ('pts', 'reb', 'ast', '3pm', 'pra')
UNIT = {'pts': 'pts', 'reb': 'reb', 'ast': 'ast', '3pm': '3PM', 'pra': 'PRA'}
WORD = {'pts': 'points', 'reb': 'rebounds', 'ast': 'assists', '3pm': 'threes made', 'pra': 'points + rebounds + assists'}
SEASON_W = {27: 1.0, 26: 0.6}
CV_PRIOR = {'pts': 0.42, 'reb': 0.45, 'ast': 0.55, '3pm': 0.75, 'pra': 0.33}
EXP_TT = {'pts': 0.5, 'reb': 0.0, 'ast': 0.3, '3pm': 0.5, 'pra': 0.35}
SD_MARGIN = 12.5
K_CAL = 0.3          # shrink of our raw probability toward 50% (fit on the first half of 2025-26 in nba_bt.py)
W_MKT = 0.7

def norm_name(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r"[.'’\-]", ' ', s)
    s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', ' ', s)
    return ' '.join(s.split())

clip = lambda x, a, b: max(a, min(b, x))

def defense_table(L, before, yy_now):
    """Per opponent team: stat allowed per team-game to each position group, vs league. Weighted current season 1, last 0.5."""
    P = L[(L['date'] < before) & (~L['dnp'])]
    w = P['yy'].map(lambda y: 1.0 if y == yy_now else 0.5)
    P = P.assign(w=w)
    g = P.groupby(['opp', 'grp', 'game_id']).agg(**{s: (s, 'sum') for s in STATS}, w=('w', 'first')).reset_index()
    out = {}
    lg = {}
    for grp, gg in g.groupby('grp'):
        lg[grp] = {s: float(np.average(gg[s], weights=gg['w'])) for s in STATS}
    for (opp, grp), gg in g.groupby(['opp', 'grp']):
        out[(opp, grp)] = {s: float(np.average(gg[s], weights=gg['w'])) for s in STATS}
        out[(opp, grp)]['n'] = float(gg['w'].sum())
    # ranks (1 = most allowed)
    ranks = {}
    for grp in lg:
        for s in STATS:
            teams = sorted([t for (t, g2) in out if g2 == grp], key=lambda t: -out[(t, grp)][s])
            for i, t in enumerate(teams): ranks[(t, grp, s)] = i + 1
    return out, lg, ranks

def team_table(T, before, yy_now):
    P = T[T['date'] < before]
    w = P['yy'].map(lambda y: 1.0 if y == yy_now else 0.5)
    P = P.assign(w=w)
    res = {}
    for t, g in P.groupby('team'):
        res[t] = {'pace': float(np.average(g['pace'].fillna(g['pace'].mean()), weights=g['w'])), 'ppg': float(np.average(g['score'], weights=g['w'])),
                  'opp_ppg': float(np.average(g['opp_score'], weights=g['w'])), 'n': float(g['w'].sum())}
        res[t]['drtg'] = 100 * res[t]['opp_ppg'] / res[t]['pace'] if res[t]['pace'] else None
        res[t]['ortg'] = 100 * res[t]['ppg'] / res[t]['pace'] if res[t]['pace'] else None
    lg = {k: float(np.mean([v[k] for v in res.values()])) for k in ('pace', 'ppg', 'drtg')}
    return res, lg

def p_over(stat, m, cv, line):
    """P(X > line) for a distribution with mean m. Points/PRA: gamma; counts: negative binomial."""
    if m <= 0: return 0.0
    if stat in ('pts', 'pra'):
        k = 1 / max(cv, 0.12) ** 2
        return float(stats.gamma.sf(line, a=k, scale=m / k))
    var = max(m * 1.05, (cv * m) ** 2)
    if var <= m * 1.0001:
        return float(stats.poisson.sf(math.floor(line), m))
    p = m / var; n = m * p / (1 - p)
    return float(stats.nbinom.sf(math.floor(line), n, p))

def evaluate(H, stat, line, ctx, p_mkt=None, k_cal=K_CAL, w_mkt=W_MKT):
    """H: DataFrame of the player's past played games (sorted by date), with columns stat, min, margin, yy, rest, pace.
    ctx: {'yy': current season, 'team': team, 'opp': opp, 'grp': grp, 'def': table, 'lg': league by grp, 'rank': ranks,
          'teams': team table, 'lgt': league team avgs, 'spread': team spread (negative = favored), 'implied': implied team pts,
          'rest': rest days tonight, 'mates_out': [(name, ratio, n_without)], 'team_changed': bool, 'starter': bool or None}"""
    H = H[H['min'].notna() & (H['min'] > 0)]
    if len(H) < 8: return None
    yy = ctx['yy']
    w = H['yy'].map(lambda y: SEASON_W.get(y, 0.3) if y == yy else SEASON_W.get(y, 0.3) * (0.6 if ctx.get('team_changed') else 1.0)).to_numpy(dtype=float).copy()
    # recency boost for the last 15 games
    w[-15:] *= 1.5
    x = H[stat].to_numpy(dtype=float); mins = H['min'].to_numpy(dtype=float)
    # ---- cases by minutes (weighted tertiles)
    order = np.argsort(mins); cw = np.cumsum(w[order]) / w.sum()
    t1 = mins[order][np.searchsorted(cw, 1 / 3)]; t2 = mins[order][min(len(cw) - 1, np.searchsorted(cw, 2 / 3))]
    if t2 <= t1: t2 = t1 + 1
    tier = np.where(mins <= t1, 0, np.where(mins <= t2, 1, 2))
    lo, hi = int(round(t1)), int(round(t2))
    labels = [f'≤ {lo} min', f'{lo + 1}–{hi} min', f'{hi + 1}+ min']
    hit_all = float(np.average(x > line, weights=w))
    T = []
    for t in range(3):
        s = tier == t; ws = w[s]
        n = int(s.sum()); h = int((x[s] > line).sum())
        p = (float((ws * (x[s] > line)).sum()) + 2 * hit_all) / (float(ws.sum()) + 2) if n else hit_all
        m = float(np.average(x[s], weights=ws)) if n else None
        T.append({'n': n, 'h': h, 'p': p, 'm': m})
    overall = np.array([w[tier == t].sum() for t in range(3)]) / w.sum()
    rec = tier[-10:]; rec_share = np.array([(rec == t).sum() for t in range(3)], dtype=float)
    recent = (rec_share + 3 * overall) / (len(rec) + 3)
    W = 0.6 * recent + 0.4 * overall
    # blowout risk: more bear weight when this game is likelier to be lopsided than his usual
    sp = ctx.get('spread')
    p_blow = None
    if sp is not None:
        mu = -sp
        p_blow = float(stats.norm.sf(14.5, mu, SD_MARGIN) + stats.norm.cdf(-14.5, mu, SD_MARGIN))
        hist_blow = float(np.average(np.abs(H['margin'].to_numpy(dtype=float)) >= 15, weights=w))
        shift = clip(0.5 * (p_blow - hist_blow), -0.08, 0.12)
        if shift > 0:
            take = min(shift, W[2] * 0.5); W = W + np.array([take, 0, -take])
        else:
            take = min(-shift, W[0] * 0.5); W = W + np.array([-take, 0, take])
    W = W / W.sum()
    P_cases = float(sum(W[t] * T[t]['p'] for t in range(3)))
    m0 = float(sum(W[t] * (T[t]['m'] if T[t]['m'] is not None else np.average(x, weights=w)) for t in range(3)))
    avg_all = float(np.average(x, weights=w))
    # ---- adjustments
    F = []
    grp, opp = ctx['grp'], ctx['opp']
    D = ctx['def'].get((opp, grp)); LG = ctx['lg'].get(grp)
    if D and LG and LG[stat] > 0:
        r = D[stat] / LG[stat]; sh = D['n'] / (D['n'] + 10)
        rk = ctx['rank'].get((opp, grp, stat))
        F.append({'k': 'def', 'label': 'Defense vs position', 'f': clip(1 + sh * 0.6 * (r - 1), 0.88, 1.12),
                  'why': f"{opp} allow {D[stat]:.1f} {UNIT[stat]}/g to {'guards' if grp == 'G' else 'forwards' if grp == 'F' else 'centers'} — #{rk} of 30, 1 = most (league {LG[stat]:.1f})"})
    TT = ctx['teams']; tm = TT.get(ctx['team']); op = TT.get(opp)
    pace_f = 1.0
    if tm and op:
        exp_pace = (tm['pace'] + op['pace']) / 2
        hp = H['pace'].to_numpy(dtype=float); ok = ~np.isnan(hp)
        hist_pace = float(np.average(hp[ok], weights=w[ok])) if ok.any() else ctx['lgt']['pace']
        pace_f = clip(exp_pace / hist_pace, 0.93, 1.07) if stat != '3pm' else clip(1 + 0.6 * (exp_pace / hist_pace - 1), 0.95, 1.05)
        F.append({'k': 'pace', 'label': 'Pace', 'f': pace_f, 'why': f"{ctx['team']} {tm['pace']:.1f} + {opp} {op['pace']:.1f} possessions → {exp_pace:.1f} vs {hist_pace:.1f} in his games"})
    if sp is not None:
        mu = -sp
        pb = [float(stats.norm.sf(14.5, mu, SD_MARGIN)), 0.0, float(stats.norm.cdf(-14.5, mu, SD_MARGIN))]
        pb[1] = 1 - pb[0] - pb[2]
        marg = H['margin'].to_numpy(dtype=float)
        B = [marg >= 15, np.abs(marg) < 15, marg <= -15]
        rows = []; f = 0
        for k, (key, mask) in enumerate(zip(('lead8', 'close', 'trail8'), B)):
            n = int(mask.sum()); wsum = float(w[mask].sum())
            avg_b = (float((w[mask] * x[mask]).sum()) + 5 * avg_all) / (wsum + 5)
            hit_b = (float((w[mask] * (x[mask] > line)).sum()) + 2 * hit_all) / (wsum + 2)
            f += pb[k] * avg_b / avg_all if avg_all > 0 else pb[k]
            nm = ctx.get('team_name', ctx['team'])
            rows.append({'k': key, 'label': [f'{nm} win by 15+', 'Within 14 either way', f'{nm} lose by 15+'][k], 'short': ['Win 15+', 'Close', 'Lose 15+'][k], 'prob': round(pb[k], 3), 'n': n,
                         'avg': round(float(np.average(x[mask], weights=w[mask])), 2) if n else None, 'hit': round(hit_b, 3)})
        fav = f"favored by {abs(sp):.1f}" if sp < -0.05 else (f"underdog by {abs(sp):.1f}" if sp > 0.05 else "pick'em")
        F.append({'k': 'script', 'label': 'Game script', 'f': clip(f, 0.9, 1.08),
                  'why': f"{ctx.get('team_name', ctx['team'])} {fav}: win by 15+ {round(100 * pb[0])}%, within 14 {round(100 * pb[1])}%, lose by 15+ {round(100 * pb[2])}%"})
        S = rows
    else:
        S = None
    if ctx.get('implied') and tm and EXP_TT[stat]:
        base = tm['ppg'] * pace_f
        F.append({'k': 'total', 'label': 'Team total', 'f': clip((ctx['implied'] / base) ** EXP_TT[stat], 0.92, 1.08),
                  'why': f"implied {ctx['implied']:.1f} pts vs {base:.1f} expected from his team’s scoring at this pace"})
    rest = ctx.get('rest')
    if rest is not None:
        if rest == 0:
            F.append({'k': 'rest', 'label': 'Rest', 'f': 0.97 if stat in ('pts', 'pra', '3pm') else 0.98, 'why': 'Second night of a back-to-back'})
        else:
            F.append({'k': 'rest', 'label': 'Rest', 'f': 1.0, 'why': f'{rest} day{"s" if rest != 1 else ""} of rest — no effect' if rest < 5 else 'Well rested — no effect'})
    for nm, ratio, nw in ctx.get('mates_out', [])[:2]:
        F.append({'k': 'mate', 'label': f'{nm} out', 'f': clip(ratio, 0.9, 1.18), 'why': f'his {UNIT[stat]} per game without {nm.split(" ")[-1]}: {nw} game{"s" if nw != 1 else ""}, shrunk toward his usual'})
    prod = clip(float(np.prod([f['f'] for f in F])) if F else 1.0, 0.75, 1.3)
    m = m0 * prod
    # spread of outcomes: player CV shrunk toward a stat prior
    sd = float(np.sqrt(np.average((x - avg_all) ** 2, weights=w)))
    cv_p = sd / avg_all if avg_all > 0 else CV_PRIOR[stat]
    n_eff = len(x)
    cv = (n_eff * cv_p + 15 * CV_PRIOR[stat]) / (n_eff + 15)
    P_model = p_over(stat, m, cv, line)
    P_raw = (P_cases + P_model) / 2
    P_ours = 0.5 + k_cal * (P_raw - 0.5)
    P = w_mkt * p_mkt + (1 - w_mkt) * P_ours if p_mkt is not None else P_ours
    return {'C': {'labels': labels, 'T': T, 'W': [float(v) for v in W], 'p': P_cases, 'm0': m0, 'by': 'minutes'}, 'F': F, 'S': S, 'prod': prod, 'm': m, 'cv': cv,
            'P_cases': P_cases, 'P_model': P_model, 'P_raw': P_raw, 'P_ours': P_ours, 'P': P, 'hit_all': hit_all, 'avg_all': avg_all, 'p_blow': p_blow}

def mates_out(L, pid, team, before, yy, out_names, stat):
    """Ratio of his per-game stat without each listed teammate (who is out) vs with, shrunk (5 games' worth)."""
    P = L[(L['team'] == team) & (L['date'] < before) & (L['yy'] >= yy - 1)]
    me = P[(P['pid'] == pid) & (~P['dnp'])][['game_id', stat]]
    if len(me) < 8: return []
    base = me[stat].mean()
    res = []
    for nm in out_names:
        mate = P[P['name'] == nm]
        if mate.empty: continue
        played = set(mate[~mate['dnp']]['game_id'])
        wo = me[~me['game_id'].isin(played)]; wi = me[me['game_id'].isin(played)]
        if len(wi) < 5 or base <= 0 or wi[stat].mean() <= 0: continue
        n = len(wo); r = ((wo[stat].sum() + 5 * wi[stat].mean()) / (n + 5)) / wi[stat].mean() if n else 1.0
        res.append((nm, r, n))
    return res
