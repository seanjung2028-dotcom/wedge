"""(C) Which position / role / team / game-script / scheme categories clear the line books would set more than 50% of the time?
Every starter's receiving yards, receptions, rushing yards and passing yards vs the book-style line (season avg, last 4 and multi-season
avg weighted as books set the real Week 6-7 lines, at the x.5 just below). Each category: over % for all of 2026 (Weeks 1-7),
Weeks 4-7, and 2023-25 (same definitions, as a check that it isn't noise). Writes arch/categories.json and rh/cats.csv."""
import json, numpy as np, pandas as pd
S = '/home/claude/wedger/'
F = pd.read_pickle(S + 'arch/feat.pkl')
F = F[F['pos'].isin(['WR', 'TE', 'RB', 'QB'])].copy()
STL = {'recyd': 'receiving yds', 'rec': 'receptions', 'rushyd': 'rushing yds', 'passyd': 'passing yds'}
F['statl'] = F['stat'].map(STL)
F['grp'] = F['pos'] + ' ' + F['statl']
F['fav'] = np.where(F['fav_by'] >= 0.5, 'favorite', np.where(F['fav_by'] <= -0.5, 'underdog', "pick'em"))
F['spread'] = pd.cut(F['fav_by'], [-60, -6.75, -0.25, 0.25, 6.75, 60], labels=['underdog by 7+', 'underdog by 1–6.5', "pick'em", 'favored by 1–6.5', 'favored by 7+']).astype(str)
F['tot'] = pd.cut(F['implied'], [0, 20.4, 24.4, 60], labels=['team total under 20.5', 'team total 20.5–24', 'team total 24.5+']).astype(str)
F['venue'] = np.where(F['home'] == 1, 'home', 'away')
F['indoor'] = np.where(F['roof'].isin(['dome', 'closed']), 'indoors', 'outdoors')
# season-to-date scheme profiles, split into thirds within each season (defense and offense)
def terc(col, labs):
    out = pd.Series('', index=F.index, dtype=object)
    for s, d in F.groupby('season'):
        x = d[col]; ok = x.notna() & (d[col.split('_')[0] + '_n'] >= 2)
        if ok.sum() < 30: continue
        q1, q2 = x[ok].quantile([1 / 3, 2 / 3])
        out.loc[d.index[ok & (x <= q1)]] = labs[0]; out.loc[d.index[ok & (x >= q2)]] = labs[1]
    return out
F['d_cov'] = terc('d_man', ['zone-heavy defense', 'man-heavy defense'])
F['d_blz'] = terc('d_blitz', ['low-blitz defense', 'blitz-heavy defense'])
F['d_deep'] = terc('d_deep_allowed', ['defense allows few deep throws', 'defense allows deep throws'])
F['d_midf'] = terc('d_mid_allowed', ['defense funnels outside', 'defense allows middle of field'])
F['d_box'] = terc('d_box8', ['light-box defense', 'stacked-box defense'])
F['d_pass'] = terc('d_pass_epa', ['tough pass defense', 'soft pass defense'])
F['d_run'] = terc('d_rush_epa', ['tough run defense', 'soft run defense'])
F['o_proe'] = terc('o_proe', ['run-leaning offense', 'pass-leaning offense'])
F['o_pa'] = terc('o_pa_rate', ['low play-action offense', 'play-action-heavy offense'])
F['o_mot'] = terc('o_motion', ['low-motion offense', 'motion-heavy offense'])
F['per'] = np.where(F['season'] == 2026, '2026', 'hist')
REL = {'recyd': ['WR', 'TE', 'RB'], 'rec': ['WR', 'TE', 'RB'], 'rushyd': ['RB', 'QB'], 'passyd': ['QB']}
DIMS = {'Position & side': ['fav'], 'Position & venue': ['venue'], 'Role': ['arch'], 'Role & side': ['arch', 'fav'], 'Role & spread': ['arch', 'spread'],
        'Position & spread': ['spread'], 'Position & team total': ['tot'], 'Role & team total': ['arch', 'tot'],
        'Scheme: coverage': ['d_cov'], 'Scheme: blitz': ['d_blz'], 'Scheme: deep throws allowed': ['d_deep'], 'Scheme: middle of field': ['d_midf'],
        'Scheme: box count': ['d_box'], 'Defense quality: pass': ['d_pass'], 'Defense quality: run': ['d_run'],
        'Offense: pass rate over expected': ['o_proe'], 'Offense: play action': ['o_pa'], 'Offense: motion': ['o_mot'],
        'Role & coverage': ['arch', 'd_cov'], 'Role & deep throws allowed': ['arch', 'd_deep'], 'Role & middle of field': ['arch', 'd_midf'],
        'Role & box count': ['arch', 'd_box'], 'Role & blitz': ['arch', 'd_blz'], 'Role & pass rate': ['arch', 'o_proe'],
        'Momentum': ['mom'], 'Role & momentum': ['arch', 'mom'], 'Position & roof': ['indoor']}
rows = []
base = {}
for per, d in (('season', F[F['per'] == '2026']), ('w47', F[(F['per'] == '2026') & (F['week'] >= 4)]), ('hist', F[F['per'] == 'hist'])):
    base[per] = {g: round(100 * x['over'].mean(), 1) for g, x in d.groupby('grp')}
    base[per]['all'] = round(100 * d['over'].mean(), 1)
for dimname, cols in DIMS.items():
    for st, poss in REL.items():
        for pos in poss:
            d = F[(F['stat'] == st) & (F['pos'] == pos)]
            for c in cols: d = d[(d[c].astype(str) != '') & (d[c].astype(str) != 'Unknown') & (d[c].astype(str) != 'nan')]
            if 'arch' in cols: d = d[~d['arch'].str.startswith(('WR · ', 'Secondary TE'))] if pos in ('WR',) else d
            for key, x in d.groupby(cols):
                key = key if isinstance(key, tuple) else (key,)
                s = x[x['per'] == '2026']; w = s[s['week'] >= 4]; h = x[x['per'] == 'hist']
                if len(s) < 20: continue
                lab = f"{pos} {STL[st]} · " + ' · '.join(str(k) for k in key)
                rows.append({'dim': dimname, 'stat': st, 'pos': pos, 'label': lab,
                             'n_season': len(s), 'over_season': round(100 * s['over'].mean(), 1),
                             'n_w47': len(w), 'over_w47': round(100 * w['over'].mean(), 1) if len(w) else None,
                             'n_hist': len(h), 'over_hist': round(100 * h['over'].mean(), 1) if len(h) >= 20 else None,
                             'base_season': base['season'].get(f'{pos} {STL[st]}'), 'base_hist': base['hist'].get(f'{pos} {STL[st]}')})
C = pd.DataFrame(rows).drop_duplicates('label')
C['above50'] = (C['over_season'] > 50) & (C['over_w47'].fillna(0) > 50)
C['held'] = C['over_hist'].notna() & (C['over_hist'] >= C['base_hist'] + 2)
C['under60'] = (C['over_season'] < 40) & (C['over_w47'].fillna(100) < 40)
C['held_under'] = C['over_hist'].notna() & (C['over_hist'] <= C['base_hist'] - 2)
# simple z-score of the season over% vs 50 to rank (n-aware)
C['z'] = (C['over_season'] / 100 - 0.5) / np.sqrt(0.25 / C['n_season'])
C.to_csv(S + 'arch/categories_all.csv', index=False)
top = C[C['above50']].sort_values(['held', 'z'], ascending=[False, False])
und = C[C['under60']].sort_values(['held_under', 'z'], ascending=[False, True])
print('base', base)
print('ABOVE 50% (season & weeks 4-7):', len(top))
print(top[['label', 'n_season', 'over_season', 'n_w47', 'over_w47', 'n_hist', 'over_hist', 'base_hist', 'held']].head(60).to_string(index=False))
print('UNDERS (over <40% season & wks 4-7):', len(und))
print(und[['label', 'n_season', 'over_season', 'n_w47', 'over_w47', 'n_hist', 'over_hist', 'base_hist', 'held_under']].head(40).to_string(index=False))
json.dump({'base': base}, open(S + 'arch/categories.json', 'w'), indent=1)
