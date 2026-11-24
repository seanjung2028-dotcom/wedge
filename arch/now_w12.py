"""Week 8 role profiles, role-matchup shifts and the defense history used by the outlook pop-out.
Writes rh/roles_w12.json  {'Name|TEAM': {pid, pos, arch, tier, metrics, cells: {stat: [...]}, rm: {stat: shift}}}
       rh/defhist_w12.csv every 2026 player-game vs each defense (Weeks 1-7) with stats, his own baseline and the main reason."""
import json, re, numpy as np, pandas as pd
S = '/home/claude/wedger/'
src = open(S + 'arch/build_feat.py').read()
X = pd.read_pickle(S + 'arch/pgx_w12.pkl'); X = X[~((X['season'] == 2026) & (X['week'] == 12))]
base_cols = [c for c in X.columns if not c.startswith(('p_', 'pn', 'psrc', 'arch', 'tier', 'd_', 'o_'))]
X = X[base_cols]
# one synthetic Week 8 row per player active in 2026 (latest team)
cur = X[X['season'] == 2026].sort_values('week').groupby('pid').tail(1)
dummy = cur.copy()
for c in dummy.columns:
    if c not in ('pid', 'name', 'pos', 'season', 'team'): dummy[c] = np.nan if dummy[c].dtype.kind == 'f' else 0
dummy['week'] = 12; dummy['season'] = 2026
X = pd.concat([X, dummy], ignore_index=True).sort_values(['pid', 'season', 'week']).reset_index(drop=True)
for c in ('snap',): X[c] = X[c].astype(float)
ns = {'np': np, 'pd': pd}
exec(src[src.index('def prior_profile'):src.index('PR = pd.concat')], ns)
exec(src[src.index('def archetype'):src.index('A = X.apply')], ns)
W9 = X[(X['season'] == 2026) & (X['week'] == 12)]
PR = pd.concat([ns['prior_profile'](d) for _, d in X[X['pid'].isin(W9['pid'])].groupby('pid', sort=False)])
X = X.join(PR)
W9 = X[(X['season'] == 2026) & (X['week'] == 12)].copy()
A = W9.apply(ns['archetype'], axis=1, result_type='expand'); W9['arch'] = A[0]; W9['tier'] = A[1]
# ---------- game context for Week 8 ----------
con = json.load(open(S + 'rh/rh_w12_consensus.json'))['consensus']
GM = {}
for k, v in con.items():
    a, h = k.split(' @ '); m = v['home_margin']; t = v['total']
    GM[h] = {'opp': a, 'fav_by': m, 'implied': (t + m) / 2, 'home': 1, 'game': k}; GM[a] = {'opp': h, 'fav_by': -m, 'implied': (t - m) / 2, 'home': 0, 'game': k}
dfn = pd.read_pickle(S + 'arch/def_g.pkl'); off = pd.read_pickle(S + 'arch/off_g.pkl')
D26 = dfn[dfn['season'] == 2026].groupby('team')[['man', 'blitz', 'ay_allowed', 'deep_allowed', 'mid_allowed', 'pass_epa', 'rush_epa', 'box8', 'ypc']].mean()
O26 = off[off['season'] == 2026].groupby('team')[['proe', 'pa_rate', 'motion', 'pass_rate', 'epa']].mean()
F = pd.read_pickle(S + 'arch/feat.pkl'); F26 = F[F['season'] == 2026]
TER = {}
for col, labs in (('d_man', ['zone-heavy defense', 'man-heavy defense']), ('d_blitz', ['low-blitz defense', 'blitz-heavy defense']),
                  ('d_deep_allowed', ['defense allows few deep throws', 'defense allows deep throws']), ('d_mid_allowed', ['defense funnels outside', 'defense allows middle of field']),
                  ('d_box8', ['light-box defense', 'stacked-box defense']), ('d_pass_epa', ['tough pass defense', 'soft pass defense']),
                  ('d_rush_epa', ['tough run defense', 'soft run defense']), ('o_proe', ['run-leaning offense', 'pass-leaning offense'])):
    x = F26[col].dropna()
    TER[col] = (float(x.quantile(1 / 3)), float(x.quantile(2 / 3)), labs) if len(x) > 30 else None
def terc(col, v):
    t = TER.get(col)
    if not t or v is None or not np.isfinite(v): return ''
    return t[2][0] if v <= t[0] else (t[2][1] if v >= t[1] else '')
RMC = json.load(open(S + 'arch/rm_coef.json')); COEF = RMC['coef']
CATS = pd.read_csv(S + 'arch/categories_all.csv').set_index('label')
STL = {'recyd': 'receiving yds', 'rec': 'receptions', 'rushyd': 'rushing yds', 'passyd': 'passing yds'}
REL = {'WR': ['recyd', 'rec'], 'TE': ['recyd', 'rec'], 'RB': ['rushyd', 'recyd', 'rec'], 'QB': ['passyd', 'rushyd']}
def spread_lab(f):
    return 'underdog by 7+' if f <= -6.75 else ('underdog by 1–6.5' if f < -0.25 else ("pick'em" if f <= 0.25 else ('favored by 1–6.5' if f < 6.75 else 'favored by 7+')))
def tot_lab(i): return 'team total under 20.5' if i < 20.5 else ('team total 20.5–24' if i < 24.5 else 'team total 24.5+')
roles = {}
for r in W9.itertuples(index=False):
    g = GM.get(r.team)
    if not g or r.pos not in REL: continue
    opp = g['opp']; Dp = D26.loc[opp] if opp in D26.index else None; Op = O26.loc[r.team] if r.team in O26.index else None
    arch = r.arch; arch2 = arch.replace(' · seam', '').replace(' · underneath', '')
    fav = 'favorite' if g['fav_by'] >= 0.5 else ('underdog' if g['fav_by'] <= -0.5 else "pick'em")
    ctx = {'fav': fav, 'spread': spread_lab(g['fav_by']), 'tot': tot_lab(g['implied']), 'venue': 'home' if g['home'] else 'away',
           'd_cov': terc('d_man', Dp['man'] if Dp is not None else None), 'd_blz': terc('d_blitz', Dp['blitz'] if Dp is not None else None),
           'd_deep': terc('d_deep_allowed', Dp['deep_allowed'] if Dp is not None else None), 'd_midf': terc('d_mid_allowed', Dp['mid_allowed'] if Dp is not None else None),
           'd_box': terc('d_box8', Dp['box8'] if Dp is not None else None), 'd_pass': terc('d_pass_epa', Dp['pass_epa'] if Dp is not None else None),
           'd_run': terc('d_rush_epa', Dp['rush_epa'] if Dp is not None else None), 'o_proe': terc('o_proe', Op['proe'] if Op is not None else None)}
    met = {k: (None if not np.isfinite(getattr(r, k)) else round(float(getattr(r, k)), 3)) for k in
           ('p_tshare', 'p_cshare', 'p_tpg', 'p_cpg', 'p_adot', 'p_deep', 'p_mid', 'p_screen', 'p_yacsh', 'p_i10sh', 'p_outside', 'p_ypt', 'p_ypc', 'p_qadot', 'p_pa', 'p_scr', 'p_ybc', 'p_yacr', 'p_ryoe', 'p_snap')
           if hasattr(r, k)}
    met['games'] = int(r.pn) if np.isfinite(r.pn) else 0; met['src'] = r.psrc if isinstance(r.psrc, str) else ''
    cells, rm = {}, {}
    for st in REL[r.pos]:
        ps = f'{r.pos}|{st}'
        feats = {'a_side': f'{ps}|{arch2}|{fav}', 'a_spread': f"{ps}|{arch2}|{ctx['spread']}", 'venue': f"{ps}|{ctx['venue']}", 'tot': f"{ps}|tot|{ctx['tot']}"}
        for c in ('d_box', 'd_blz', 'd_cov', 'd_midf', 'd_deep', 'd_pass', 'd_run', 'o_proe'):
            if ctx[c]: feats[c] = f'{ps}|{c}|{ctx[c]}'
        sh = 0.0; used = []
        for c, k in feats.items():
            v = COEF.get(f'{c}={k}')
            if v: sh += v; used.append([c, k.split('|', 2)[-1], v])
        rm[st] = round(sh, 4)
        # category hit rates for his spots (season, Weeks 4-7, 2023-25)
        pre = f"{r.pos} {STL[st]} · "
        labs = [pre + arch, pre + f'{arch} · {fav}', pre + f"{arch} · {ctx['spread']}", pre + f"{arch} · {ctx['tot']}", pre + fav, pre + ctx['spread'], pre + ctx['tot'], pre + ctx['venue']]
        for c in ('d_box', 'd_blz', 'd_cov', 'd_midf', 'd_deep', 'd_pass', 'd_run', 'o_proe'):
            if ctx[c]: labs += [pre + ctx[c], pre + f'{arch} · {ctx[c]}']
        rows = []
        for lb in labs:
            if lb in CATS.index:
                c = CATS.loc[lb]
                rows.append([lb.replace(pre, ''), int(c['n_season']), float(c['over_season']), int(c['n_w47']) if np.isfinite(c['n_w47']) else 0,
                             float(c['over_w47']) if np.isfinite(c['over_w47']) else None, int(c['n_hist']),
                             float(c['over_hist']) if np.isfinite(c['over_hist']) else None, float(c['base_season']), float(c['base_hist'])])
        cells[st] = {'rows': rows, 'used': used}
    roles[f'{r.name}|{r.team}'] = {'pid': r.pid, 'pos': r.pos, 'arch': arch, 'tier': r.tier, 'm': met, 'ctx': ctx, 'opp': opp, 'cells': cells, 'rm': rm}
json.dump(roles, open(S + 'rh/roles_w12.json', 'w'), separators=(',', ':'))
print('roles', len(roles), pd.Series([v['arch'] for v in roles.values()]).value_counts().to_dict())

# ---------- defense history: every 2026 opponent at each position, with the main reason ----------
P = pd.read_pickle(S + 'arch/plays.pkl'); P = P[P['season'] == 2026]
lr = P[P['rush'] == 1].groupby(['week', 'rusher_player_id'])['yards_gained'].max().rename('long_rush')
lc = P[(P['pass'] == 1) & (P['complete_pass'] == 1)].groupby(['week', 'receiver_player_id'])['yards_gained'].max().rename('long_rec')
g = pd.read_csv(S + 'dl18/games.csv'); g = g[(g['season'] == 2026) & (g['week'] <= 11)]
FX = {'LA': 'LAR', 'WAS': 'WSH', 'JAC': 'JAX'}
MG = {}
for x in g.itertuples(index=False):
    a, h = FX.get(x.away_team, x.away_team), FX.get(x.home_team, x.home_team)
    MG[(x.week, h)] = (x.home_score - x.away_score, x.home_score, x.away_score); MG[(x.week, a)] = (x.away_score - x.home_score, x.away_score, x.home_score)
X7 = pd.read_pickle(S + 'arch/pgx_w12.pkl'); X7 = X7[(X7['season'] == 2026) & (X7['week'] <= 11)]
Fb = F26.pivot_table(index=['pid', 'week'], columns='stat', values='base', aggfunc='first')
X7 = X7.join(Fb, on=['pid', 'week'], rsuffix='_b').join(lr, on=['week', 'pid']).join(lc, on=['week', 'pid'])
out = []
for r in X7.itertuples(index=False):
    if r.pos not in ('WR', 'TE', 'RB', 'QB'): continue
    if r.pos == 'QB' and (r.att or 0) < 10: continue
    if r.pos in ('WR', 'TE') and (r.tgt or 0) < 2: continue
    if r.pos == 'RB' and (r.car or 0) + (r.tgt or 0) < 5: continue
    mg = MG.get((r.week, r.team), (None, None, None))
    b_rush = getattr(r, 'rushyd_b', np.nan); b_rec = getattr(r, 'recyd_b', np.nan); b_recs = getattr(r, 'rec_b', np.nan); b_pass = getattr(r, 'passyd_b', np.nan)
    resid = {'rushyd': r.rushyd - b_rush if np.isfinite(b_rush) else None, 'recyd': r.recyd - b_rec if np.isfinite(b_rec) else None,
             'rec': r.rec - b_recs if np.isfinite(b_recs) else None, 'passyd': r.passyd - b_pass if np.isfinite(b_pass) else None}
    if r.pos == 'RB': main = 'rushyd' if resid['rushyd'] is not None else ('recyd' if resid['recyd'] is not None else 'rushyd')
    else: main = {'WR': 'recyd', 'TE': 'recyd', 'QB': 'passyd'}[r.pos]
    rv = resid[main] if resid[main] is not None else 0.0
    R = []
    def add(v, txt):
        if v is not None and np.isfinite(v): R.append((float(v), txt))
    if main == 'rushyd' and r.car:
        if np.isfinite(r.p_cpg): add((r.car - r.p_cpg) * (r.p_ypc if np.isfinite(r.p_ypc) else 4.2), f"{'more' if r.car > r.p_cpg else 'fewer'} carries: {int(r.car)} vs {r.p_cpg:.0f} usual")
        if np.isfinite(r.ybc) and np.isfinite(r.p_ybc): add(r.ybc - r.car * r.p_ybc, f"blocking: {r.ybc / r.car:.1f} yds before contact per carry vs {r.p_ybc:.1f} usual")
        if np.isfinite(r.yac_r) and np.isfinite(r.p_yacr): add(r.yac_r - r.car * r.p_yacr, f"the runner: {r.yac_r / r.car:.1f} yds after contact per carry vs {r.p_yacr:.1f} usual")
        if np.isfinite(r.long_rush) and r.long_rush >= 20 and r.rushyd > 0: R.append((0.6 * r.long_rush, f"one {int(r.long_rush)}-yd run ({100 * r.long_rush / max(r.rushyd, 1):.0f}% of his yards)"))
    if main == 'recyd' and r.tgt:
        if np.isfinite(r.p_tpg): add((r.tgt - r.p_tpg) * (r.p_ypt if np.isfinite(r.p_ypt) else 7.5), f"{'more' if r.tgt > r.p_tpg else 'fewer'} targets: {int(r.tgt)} vs {r.p_tpg:.1f} usual")
        if np.isfinite(r.p_ypt) and r.tgt >= 3: add(r.recyd - r.tgt * r.p_ypt, f"{'better' if r.recyd / r.tgt > r.p_ypt else 'worse'} efficiency: {r.recyd / r.tgt:.1f} yds per target vs {r.p_ypt:.1f} usual")
        if np.isfinite(r.long_rec) and r.long_rec >= 30 and r.recyd > 0: R.append((0.6 * r.long_rec, f"one {int(r.long_rec)}-yd catch ({100 * r.long_rec / max(r.recyd, 1):.0f}% of his yards)"))
        if r.r_yac and r.recyd and r.r_yac / max(r.recyd, 1) >= 0.6 and r.recyd >= 40: R.append((0.4 * r.r_yac, f"after the catch: {int(r.r_yac)} of his {int(r.recyd)} yds"))
        if r.tgt and np.isfinite(r.r_ay) and r.r_ay / r.tgt >= 15 and rv > 0: R.append((0.3 * rv, f"downfield: {r.r_ay / r.tgt:.0f} air yds per target"))
    if main == 'passyd' and r.att:
        R.append(((r.att - 33) * 6.5, f"{'more' if r.att > 33 else 'fewer'} attempts: {int(r.att)}"))
        if r.passyd and r.att: R.append(((r.passyd / r.att - 6.8) * r.att, f"{r.passyd / r.att:.1f} yds per attempt"))
    thr = {'rushyd': 10, 'recyd': 10, 'passyd': 25}[main]
    if abs(rv) < thr: why = [(0, 'about his usual')]
    else:
        why = sorted([x for x in R if (x[0] > 0) == (rv > 0) and x[0] != 0], key=lambda x: -abs(x[0]))[:2]
        if not why: why = [(0, 'no single cause')]
    rec_note = ''
    if r.pos == 'RB' and main == 'rushyd' and resid['recyd'] is not None and abs(resid['recyd']) >= 25:
        rec_note = f"receiving {'+' if resid['recyd'] > 0 else ''}{resid['recyd']:.0f} vs his usual ({int(r.tgt)} targets)"
    out.append({'def': r.opp, 'week': int(r.week), 'player': r.name, 'team': r.team, 'pos': r.pos, 'arch': r.arch,
                'car': int(r.car or 0), 'rushyd': int(r.rushyd or 0), 'ybc_pc': round(r.ybc / r.car, 1) if r.car and np.isfinite(r.ybc) else '',
                'yac_pc': round(r.yac_r / r.car, 1) if r.car and np.isfinite(r.yac_r) else '', 'long_rush': int(r.long_rush) if np.isfinite(r.long_rush) else '',
                'tgt': int(r.tgt or 0), 'rec': int(r.rec or 0), 'recyd': int(r.recyd or 0), 'adot': round(r.r_ay / r.tgt, 1) if r.tgt else '',
                'yac': int(r.r_yac or 0), 'long_rec': int(r.long_rec) if np.isfinite(r.long_rec) else '', 'att': int(r.att or 0), 'passyd': int(r.passyd or 0),
                'td': int(r.td or 0), 'snap': round(float(r.snap)) if np.isfinite(r.snap) else '',
                'base_rushyd': round(b_rush, 1) if np.isfinite(b_rush) else '', 'base_recyd': round(b_rec, 1) if np.isfinite(b_rec) else '',
                'base_rec': round(b_recs, 1) if np.isfinite(b_recs) else '', 'base_passyd': round(b_pass, 1) if np.isfinite(b_pass) else '',
                'resid_main': round(rv, 1), 'main': main, 'why': '; '.join(t for _, t in why), 'why_rec': rec_note,
                'margin': int(mg[0]) if mg[0] is not None else '', 'score': f'{int(mg[1])}–{int(mg[2])}' if mg[1] is not None else ''})
DH = pd.DataFrame(out).sort_values(['def', 'week', 'pos', 'resid_main'], ascending=[True, True, True, False])
DH.to_csv(S + 'rh/defhist_w12.csv', index=False)
print('defhist rows', len(DH)); print(DH[(DH['def'] == 'GB') & (DH['pos'] == 'RB')].head(8).to_string())
