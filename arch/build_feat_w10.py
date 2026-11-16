"""Stage 2: one row per player-game-stat, 2023-2026, with everything known BEFORE the game:
book-style line (weights fit on real Week 6-7 lines, rounded to the nearest x.5 below), the player's role archetype (season to date,
falling back to last season), the defense's and offense's season-to-date profile, game script, and the result.
Also the 'residual' pieces used to test how much opponents' results vs a defense tell us about the next player.
Writes arch/feat_w10.pkl and arch/arch_now.pkl (archetypes for Week 8)."""
import json, numpy as np, pandas as pd
S = '/home/claude/wedger/'
pg = pd.read_pickle(S + 'mom/pg_w10.pkl')
rec = pd.read_pickle(S + 'arch/rec_pg.pkl'); rush = pd.read_pickle(S + 'arch/rush_pg.pkl'); qb = pd.read_pickle(S + 'arch/qb_pg.pkl')
off = pd.read_pickle(S + 'arch/off_g.pkl'); dfn = pd.read_pickle(S + 'arch/def_g.pkl')
RA = json.load(open(S + 'mom/real_analysis.json'))['line_fit']
# PFR advanced rushing (yards before / after contact, broken tackles) mapped to gsis ids
ros = pd.concat([pd.read_csv(S + f'nflverse_dl3/roster_weekly_{y}.csv', usecols=['gsis_id', 'pfr_id']) for y in (2023, 2024, 2025, 2026)]).dropna().drop_duplicates('pfr_id')
p2g = dict(zip(ros['pfr_id'], ros['gsis_id']))
adv = pd.concat([pd.read_csv(S + f'dl9/advstats_week_rush_{y}.csv') for y in (2023, 2024, 2025, 2026)])
adv = adv[adv['game_type'] == 'REG']; adv['pid'] = adv['pfr_player_id'].map(p2g)
adv = adv.groupby(['season', 'week', 'pid'], as_index=False).agg(ybc=('rushing_yards_before_contact', 'sum'), yac_r=('rushing_yards_after_contact', 'sum'), btk=('rushing_broken_tackles', 'sum'))
ngs = pd.read_csv(S + 'dl9/ngs_rushing.csv.gz'); ngs = ngs[(ngs['season_type'] == 'REG') & (ngs['week'] > 0)]
ngs = ngs.rename(columns={'player_gsis_id': 'pid'})[['season', 'week', 'pid', 'expected_rush_yards', 'rush_yards_over_expected', 'rush_attempts']].rename(columns={'rush_attempts': 'ngs_att'})
X = pg.merge(rec.drop(columns=['team', 'opp', 'tgt', 'rec']).rename(columns={'ay': 'r_ay', 'deep': 'r_deep', 'short': 'r_short', 'mid': 'r_mid', 'screen': 'r_screen', 'ry': 'r_ry', 'yac': 'r_yac', 'rz': 'r_rz'}),
             on=['season', 'week', 'pid'], how='left')
X = X.merge(rush.drop(columns=['team', 'opp', 'car', 'yds']).rename(columns={'scr': 'scr_r', 'gun': 'gun_r', 'box': 'box_r'}), on=['season', 'week', 'pid'], how='left')
X = X.merge(qb.drop(columns=['team', 'opp', 'att', 'epa']).rename(columns={'ay': 'q_ay', 'scr': 'q_scr', 'sk': 'q_sk'}), on=['season', 'week', 'pid'], how='left')
X = X.merge(adv, on=['season', 'week', 'pid'], how='left').merge(ngs, on=['season', 'week', 'pid'], how='left')
for c in X.columns:
    if c.startswith(('r_', 'i10', 'outside', 'heavy', 'light', 'expl', 'stuff', 'scr_r', 'gun_r', 't_man', 't_zone', 'ry_man', 'ry_zone', 'deep_rt', 'rt_n', 'db', 'pa', 'q_')):
        X[c] = X[c].fillna(0)
X = X.sort_values(['pid', 'season', 'week']).reset_index(drop=True)
# team totals per game for shares
tm = X.groupby(['season', 'week', 'team']).agg(T_tgt=('tgt', 'sum'), T_car=('car', 'sum'), T_i10=('i10', 'sum'), T_ay=('r_ay', 'sum')).reset_index()
X = X.merge(tm, on=['season', 'week', 'team'], how='left')

# ---------- season-to-date (prior games) profiles with last-season fallback ----------
def prior_profile(d):
    """d: one player's games sorted. For each game, sums over this season's prior games with the same team (fallback: last season's games)."""
    out = []
    keys = ['tgt', 'T_tgt', 'car', 'T_car', 'r_ay', 'r_deep', 'r_mid', 'r_screen', 'r_ry', 'r_yac', 'i10', 'T_i10', 'outside', 'rec', 'recyd', 'rushyd', 'passyd',
            'att', 'db', 'q_ay', 'pa', 'q_scr', 'scr_r', 'snap', 'ybc', 'yac_r', 'expected_rush_yards', 'rush_yards_over_expected', 'ngs_att']
    vals = {k: d[k].values.astype(float) for k in keys}
    seas = d['season'].values; team = d['team'].values
    for i in range(len(d)):
        idx = np.where((seas == seas[i]) & (team == team[i]) & (np.arange(len(d)) < i))[0]
        src = 'cur'
        if len(idx) < 3:
            prev = np.where((seas == seas[i] - 1) & (np.arange(len(d)) < i))[0]
            if len(prev) >= 4: idx = np.concatenate([prev[-8:], idx]); src = 'prev'
        n = len(idx)
        if n == 0: out.append({'pn': 0}); continue
        s = {k: np.nansum(vals[k][idx]) for k in keys}
        sn = vals['snap'][idx]
        out.append({'pn': n, 'psrc': src,
                    'p_tshare': s['tgt'] / max(s['T_tgt'], 1), 'p_cshare': s['car'] / max(s['T_car'], 1), 'p_tpg': s['tgt'] / n, 'p_cpg': s['car'] / n,
                    'p_adot': s['r_ay'] / s['tgt'] if s['tgt'] >= 5 else np.nan, 'p_deep': s['r_deep'] / s['tgt'] if s['tgt'] >= 5 else np.nan,
                    'p_mid': s['r_mid'] / s['tgt'] if s['tgt'] >= 5 else np.nan, 'p_screen': s['r_screen'] / s['tgt'] if s['tgt'] >= 5 else np.nan,
                    'p_yacsh': s['r_yac'] / s['r_ry'] if s['r_ry'] >= 40 else np.nan, 'p_i10sh': s['i10'] / s['T_i10'] if s['T_i10'] >= 3 else np.nan,
                    'p_outside': s['outside'] / s['car'] if s['car'] >= 10 else np.nan, 'p_ypt': s['recyd'] / s['tgt'] if s['tgt'] >= 5 else np.nan,
                    'p_ypc': s['rushyd'] / s['car'] if s['car'] >= 10 else np.nan, 'p_qadot': s['q_ay'] / s['att'] if s['att'] >= 20 else np.nan,
                    'p_pa': s['pa'] / s['db'] if s['db'] >= 20 else np.nan, 'p_qrush': (s['car']) / n, 'p_scr': s['q_scr'] / n,
                    'p_ybc': s['ybc'] / s['car'] if s['car'] >= 10 else np.nan, 'p_yacr': s['yac_r'] / s['car'] if s['car'] >= 10 else np.nan,
                    'p_xry': s['expected_rush_yards'] / s['ngs_att'] if s['ngs_att'] >= 10 else np.nan, 'p_ryoe': s['rush_yards_over_expected'] / s['ngs_att'] if s['ngs_att'] >= 10 else np.nan,
                    'p_snap': float(np.nanmean(sn)) if np.isfinite(sn).any() else np.nan})
    return pd.DataFrame(out, index=d.index)
PR = pd.concat([prior_profile(d) for _, d in X.groupby('pid', sort=False)])
X = X.join(PR)

def archetype(r):
    pos = r['pos']
    if r.get('pn', 0) < 3 or not np.isfinite(r.get('p_tshare', np.nan)): return ('Unknown', '')
    if pos == 'WR':
        tier = 'Alpha' if r['p_tshare'] >= 0.24 else ('No. 2' if r['p_tshare'] >= 0.16 else 'Depth')
        a, dp, md, sc = r['p_adot'], r['p_deep'], r['p_mid'], r['p_screen']
        if not np.isfinite(a): return ('WR · ' + tier, tier)
        style = 'Deep threat' if (a >= 13 or (np.isfinite(dp) and dp >= 0.28)) else ('Slot / underneath' if (a < 8.5 and ((np.isfinite(md) and md >= 0.30) or (np.isfinite(sc) and sc >= 0.12))) else 'Intermediate')
        return (style, tier)
    if pos == 'TE':
        tier = 'Receiving TE' if r['p_tshare'] >= 0.15 else 'Secondary TE'
        a = r['p_adot']
        return (tier if not np.isfinite(a) else (tier + (' · seam' if a >= 8.5 else ' · underneath')), tier)
    if pos in ('RB', 'FB'):
        cs, ts, i10 = r['p_cshare'], r['p_tshare'], r['p_i10sh']
        catch = ts >= 0.10
        if cs >= 0.55: return ('Workhorse · three-down' if catch else 'Workhorse · early-down', 'Workhorse')
        if catch: return ('Pass-catching back', 'Pass-catching')
        if cs >= 0.30 and np.isfinite(i10) and i10 >= 0.45: return ('Early-down / goal-line', 'Committee')
        return ('Committee / change-of-pace', 'Committee')
    if pos == 'QB':
        rushq = (r['p_qrush'] + r['p_scr']) >= 6
        a = r['p_qadot']
        style = 'Dual-threat' if rushq else ('Vertical pocket' if np.isfinite(a) and a >= 8.5 else ('Quick-game pocket' if np.isfinite(a) and a < 7 else 'Pocket'))
        return (style, style)
    return ('Unknown', '')
A = X.apply(archetype, axis=1, result_type='expand'); X['arch'] = A[0]; X['tier'] = A[1]

# ---------- defense / offense season-to-date profiles ----------
def prior_team(df, key, cols):
    df = df.sort_values(['team', 'season', 'week']).copy()
    res = []
    for (t, s), d in df.groupby(['team', 'season']):
        cs = d[cols].expanding().mean().shift(1)
        cs['n'] = np.arange(len(d))
        res.append(pd.concat([d[['season', 'week', 'team']], cs], axis=1))
    out = pd.concat(res); out.columns = ['season', 'week', 'team'] + [f'{key}_{c}' for c in cols] + [f'{key}_n']
    return out
DP = prior_team(dfn, 'd', ['man', 'blitz', 'ay_allowed', 'deep_allowed', 'mid_allowed', 'pass_epa', 'rush_epa', 'box8', 'ypc'])
OP = prior_team(off, 'o', ['proe', 'pa_rate', 'motion', 'pass_rate', 'epa'])
X = X.merge(DP.rename(columns={'team': 'opp'}), on=['season', 'week', 'opp'], how='left').merge(OP, on=['season', 'week', 'team'], how='left')
X.to_pickle(S + 'arch/pgx_w10.pkl')

# ---------- book-style lines per player-game-stat ----------
STATS = {'recyd': ('WR', 'TE', 'RB'), 'rec': ('WR', 'TE', 'RB'), 'rushyd': ('RB', 'QB'), 'passyd': ('QB',)}
VOLC = {'recyd': 'tgt', 'rec': 'tgt', 'rushyd': 'car', 'passyd': 'att'}
MIN = {'recyd': 20, 'rec': 2, 'rushyd': 25, 'passyd': 150}
SW = {0: 1.0, 1: 0.75, 2: 0.5, 3: 0.35}
rows = []
for (pid, team), d in X.groupby(['pid', 'team'], sort=False):
    pos = d['pos'].iloc[-1]
    for st, poss in STATS.items():
        if pos not in poss: continue
        y = d[st].values.astype(float); v = d[VOLC[st]].values.astype(float); seas = d['season'].values; sn = d['snap'].values
        for i in range(len(d)):
            s = seas[i]; cur = np.where((seas == s) & (np.arange(len(d)) < i))[0]; allp = np.arange(i)
            if len(allp) < 4: continue
            w = np.array([SW.get(s - seas[j], 0.3) for j in allp]); C = float(np.sum(w * y[allp]) / np.sum(w))
            f = RA.get(st); wS, w4, wC = (f['w_S'], f['w_L4'], f['w_C']) if f and f['n'] >= 40 else (0.3, 0.2, 0.5)
            if len(cur) >= 3:
                Sv, L4 = y[cur].mean(), y[cur][-4:].mean(); base = wS * Sv + w4 * L4 + wC * C
                vS = v[cur].mean(); v4 = v[cur][-4:].mean(); vm = (v4 - vS) / max(vS, 0.5)
                eS = y[cur].sum() / max(v[cur].sum(), 1); e4 = y[cur][-4:].sum() / max(v[cur][-4:].sum(), 1); em = (e4 - eS) / max(abs(eS), 0.1)
                sm = np.nanmean(sn[cur][-4:]) - np.nanmean(sn[cur]) if np.isfinite(sn[cur]).sum() >= 3 else 0
                mom = 'Role up' if sm >= 10 else 'Role down' if sm <= -10 else 'Volume up' if vm >= .15 else 'Volume down' if vm <= -.15 else 'Hot efficiency' if em >= .15 else 'Cold efficiency' if em <= -.15 else 'Stable'
            else:
                Sv = (y[cur].sum() + 2 * C) / (len(cur) + 2); base = Sv  # weeks 1-3: prior seasons, blended with the games so far vS = v[allp][-8:].mean(); eS = y[allp][-8:].sum() / max(v[allp][-8:].sum(), 1); mom = 'Early season'
            if Sv < MIN[st] and C < MIN[st]: continue
            line = np.floor(base) + 0.5
            r = d.iloc[i]
            rows.append({'idx': d.index[i], 'stat': st, 'base': base, 'line': line, 'y': y[i], 'over': int(y[i] > line), 'resid': y[i] - base,
                         'vol': v[i], 'vol_base': vS, 'eff_base': eS, 'hr': float(np.mean(y[cur] > line)) if len(cur) else np.nan, 'mom': mom})
L = pd.DataFrame(rows)
F = L.join(X, on='idx')
F['fav'] = np.where(F['fav_by'] > 0, 'Favorite', np.where(F['fav_by'] < 0, 'Underdog', "Pick'em"))
F.to_pickle(S + 'arch/feat_w10.pkl')
print(len(F), F.groupby('season').size().to_dict())
print(F.groupby(['stat'])['over'].mean().round(3).to_dict())
print(F[F['season'] == 2026].groupby(['pos', 'arch']).size().to_string())
