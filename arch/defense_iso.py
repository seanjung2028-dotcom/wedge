"""(B) How much do other players' results against a defense tell us about the next player?
For every player-game-stat row (2023-2026) we take what the defense allowed, earlier that season, to the same position:
  raw      = their yards minus the league average for that position/stat (classic defense-vs-position)
  adjusted = their yards minus their OWN pre-game baseline (book-style line before rounding) -> removes who they were
  same     = adjusted, only opponents of the same role archetype (slot vs deep threat, workhorse vs pass-catching...)
  pieces   = adjusted split into volume (more carries/targets than usual) and efficiency (more yards per touch);
             for rushing, efficiency split again into yards before contact (blocking / front) and after contact (the runner),
             and NGS expected rush yards (blocking + box + defenders' positions) vs rush yards over expected (the runner)
  last1    = the single most recent opponent at that position (e.g. one huge Gibbs game)
and test which predicts the next player's result vs HIS baseline. Writes arch/defense_iso.json and rh/def_iso.csv (page)."""
import json, numpy as np, pandas as pd
S = '/home/claude/wedger/'
F = pd.read_pickle(S + 'arch/feat.pkl')
F = F[F['pos'].isin(['WR', 'TE', 'RB', 'QB'])].copy()
F['ypu'] = np.where(F['vol'] > 0, F['y'] / F['vol'], np.nan)
F['c_vol'] = (F['vol'] - F['vol_base']) * F['eff_base']
F['c_eff'] = F['vol'] * (F['ypu'].fillna(F['eff_base']) - F['eff_base'])
R = F['stat'] == 'rushyd'
F['c_ybc'] = np.where(R & F['p_ybc'].notna() & F['ybc'].notna() & (F['car'] > 0), F['ybc'] - F['car'] * F['p_ybc'], np.nan)
F['c_yac'] = np.where(R & F['p_yacr'].notna() & F['yac_r'].notna() & (F['car'] > 0), F['yac_r'] - F['car'] * F['p_yacr'], np.nan)
F['c_xry'] = np.where(R & F['p_xry'].notna() & F['expected_rush_yards'].notna(), F['expected_rush_yards'] - F['ngs_att'] * F['p_xry'], np.nan)
F['c_ryoe'] = np.where(R & F['p_ryoe'].notna() & F['rush_yards_over_expected'].notna(), F['rush_yards_over_expected'] - F['ngs_att'] * F['p_ryoe'], np.nan)
lg = F.groupby(['season', 'stat', 'pos'])['y'].mean().rename('lg_y'); F = F.join(lg, on=['season', 'stat', 'pos']); F['raw'] = F['y'] - F['lg_y']
SIG = ['raw', 'resid', 'c_vol', 'c_eff', 'c_ybc', 'c_yac', 'c_xry', 'c_ryoe']
rows = []
for (s, st, pos, opp), d in F.groupby(['season', 'stat', 'pos', 'opp']):
    d = d.sort_values('week'); wk = d['week'].values
    for i in range(len(d)):
        prior = d[wk < wk[i]]
        if prior['week'].nunique() < 2: continue
        r = d.iloc[i]
        rec = {'season': s, 'stat': st, 'pos': pos, 'week': int(wk[i]), 'arch': r['arch'], 'y_resid': r['resid'], 'y_raw': r['raw'],
               'y_vol': r['c_vol'], 'y_eff': r['c_eff'], 'n_prior': len(prior), 'g_prior': prior['week'].nunique()}
        for c in SIG: rec['d_' + c] = prior[c].mean()
        same = prior[prior['arch'] == r['arch']]
        rec['d_same'] = same['resid'].mean() if len(same) else np.nan; rec['n_same'] = len(same)
        last = prior[prior['week'] == prior['week'].max()].sort_values('vol', ascending=False).iloc[0]
        rec['d_last1'] = last['resid']; rec['last1_ybc'] = last['c_ybc']; rec['last1_yac'] = last['c_yac']
        rows.append(rec)
T = pd.DataFrame(rows)
def slope(x, y):
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 60: return None
    x, y = x[m], y[m]; b = np.polyfit(x, y, 1)[0]; r = np.corrcoef(x, y)[0, 1]
    return {'n': int(m.sum()), 'slope': round(float(b), 3), 'r': round(float(r), 3)}
GROUPS = {'RB rushing yards': (T['stat'] == 'rushyd') & (T['pos'] == 'RB'), 'WR receiving yards': (T['stat'] == 'recyd') & (T['pos'] == 'WR'),
          'TE receiving yards': (T['stat'] == 'recyd') & (T['pos'] == 'TE'), 'RB receiving yards': (T['stat'] == 'recyd') & (T['pos'] == 'RB'),
          'WR receptions': (T['stat'] == 'rec') & (T['pos'] == 'WR'), 'QB passing yards': (T['stat'] == 'passyd') & (T['pos'] == 'QB')}
out = {}
for gname, m in GROUPS.items():
    d = T[m]
    res = {'n': int(len(d))}
    for c in ['d_raw', 'd_resid', 'd_same', 'd_c_vol', 'd_c_eff', 'd_c_ybc', 'd_c_yac', 'd_c_xry', 'd_c_ryoe', 'd_last1']:
        res[c] = slope(d[c].values, d['y_resid'].values)
    # what the next player's volume vs efficiency gets from the defense's volume vs efficiency
    res['vol_on_vol'] = slope(d['d_c_vol'].values, d['y_vol'].values); res['eff_on_eff'] = slope(d['d_c_eff'].values, d['y_eff'].values)
    # out-of-sample check: fit on 2023-24, test 2025-26, error with vs without the adjusted signal (shrunk by games)
    tr, te = d[d['season'] <= 2024], d[d['season'] >= 2025]
    for c in ['d_raw', 'd_resid', 'd_same']:
        a, b = tr[c].values, tr['y_resid'].values; mk = np.isfinite(a) & np.isfinite(b)
        if mk.sum() < 60: continue
        k = np.polyfit(a[mk], b[mk], 1)[0]
        x = te[c].values; y = te['y_resid'].values; mk2 = np.isfinite(x) & np.isfinite(y)
        base_mae = float(np.mean(np.abs(y[mk2] - np.mean(b[mk])))); mae = float(np.mean(np.abs(y[mk2] - (np.mean(b[mk]) + k * (x[mk2] - np.nanmean(a[mk]))))))
        res['oos_' + c] = {'k': round(float(k), 3), 'mae_without': round(base_mae, 2), 'mae_with': round(mae, 2), 'gain_pct': round(100 * (base_mae - mae) / base_mae, 2)}
    out[gname] = res
# one huge game: a prior opponent's single best game vs that defense (+40 rushing / +40 receiving yards over his own baseline)
big = {}
for gname, m in GROUPS.items():
    d = T[m]; thr = 40 if 'yards' in gname else 3
    hi = d[d['d_last1'] >= thr]; lo = d[d['d_last1'] < thr]
    big[gname] = {'after_big_game': {'n': int(len(hi)), 'next_resid': round(float(hi['y_resid'].mean()), 2) if len(hi) else None},
                  'otherwise': {'n': int(len(lo)), 'next_resid': round(float(lo['y_resid'].mean()), 2)}}
    if gname == 'RB rushing yards':
        hb = hi[hi['last1_ybc'].notna()]
        ybc_led = hb[hb['last1_ybc'] >= hb['last1_yac']]; yac_led = hb[hb['last1_ybc'] < hb['last1_yac']]
        big[gname]['big_game_led_by_blocking'] = {'n': int(len(ybc_led)), 'next_resid': round(float(ybc_led['y_resid'].mean()), 2) if len(ybc_led) else None}
        big[gname]['big_game_led_by_runner'] = {'n': int(len(yac_led)), 'next_resid': round(float(yac_led['y_resid'].mean()), 2) if len(yac_led) else None}
out['_big_single_game'] = big
json.dump(out, open(S + 'arch/defense_iso.json', 'w'), indent=1)
for k, v in out.items(): print(k, json.dumps(v)[:900]); print()
T.to_pickle(S + 'arch/def_iso_rows.pkl')
