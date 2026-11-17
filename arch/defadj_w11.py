"""Opponent-adjusted defense signal: what each defense allowed to each position/stat EARLIER that season, measured against
each opponent's OWN baseline (book-style expectation), with the rushing part split into volume, blocking/front (yards before
contact) and the runner (after contact). build(season, week) -> {defense: {'RB|rushyd': {...}, ...}}.
Run directly: writes rh/def_adj_w11.json for the Week 11 model."""
import json, numpy as np, pandas as pd
S = '/home/claude/wedger/'
_F = None
def _load():
    global _F
    if _F is not None: return _F
    F = pd.read_pickle(S + 'arch/feat.pkl')
    F = F[F['pos'].isin(['WR', 'TE', 'RB', 'QB'])].copy()
    F['ypu'] = np.where(F['vol'] > 0, F['y'] / F['vol'], np.nan)
    F['c_vol'] = (F['vol'] - F['vol_base']) * F['eff_base']
    R = F['stat'] == 'rushyd'
    F['c_ybc'] = np.where(R & F['p_ybc'].notna() & F['ybc'].notna() & (F['car'] > 0), F['ybc'] - F['car'] * F['p_ybc'], np.nan)
    F['c_yac'] = np.where(R & F['p_yacr'].notna() & F['yac_r'].notna() & (F['car'] > 0), F['yac_r'] - F['car'] * F['p_yacr'], np.nan)
    _F = F
    return F
def build(season, week):
    F = _load()
    d = F[(F['season'] == season) & (F['week'] < week)]
    out = {}
    for (opp, pos, st), x in d.groupby(['opp', 'pos', 'stat']):
        g = x['week'].nunique()
        if g < 2: continue
        out.setdefault(opp, {})[f'{pos}|{st}'] = {'resid': float(x['resid'].mean()), 'vol': float(x['c_vol'].mean()),
                                                   'front': float(x['c_ybc'].mean()) if x['c_ybc'].notna().any() else None,
                                                   'runner': float(x['c_yac'].mean()) if x['c_yac'].notna().any() else None,
                                                   'n': int(len(x)), 'g': int(g)}
    return out
if __name__ == '__main__':
    D = build(2026, 11)
    json.dump(D, open(S + 'rh/def_adj_w11.json', 'w'), indent=0)
    print(len(D), 'defenses;', D.get('GB', {}).get('RB|rushyd'))
