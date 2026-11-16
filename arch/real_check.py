"""Real Robinhood / book prices, Weeks 6-7 (calib_rows): hit rate vs price by role archetype and side."""
import json, re, unicodedata, numpy as np, pandas as pd
S = '/home/claude/wedger/'
def nn(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower(); s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', s); return re.sub(r'[^a-z]', '', s)
c = pd.read_csv(S + 'rh/calib_rows.csv')
X = pd.read_pickle(S + 'arch/pgx.pkl'); X = X[X['season'] == 2026]
X['nk'] = X['name'].map(nn)
c['nk'] = c['player'].map(nn)
c = c.merge(X[['nk', 'team', 'week', 'arch', 'pos', 'fav_by', 'opp', 'd_box8', 'd_blitz', 'implied']].rename(columns={'week': 'wk', 'pos': 'pos_x'}), on=['nk', 'team', 'wk'], how='left')
print('matched', c['arch'].notna().mean().round(3), len(c))
c['fav'] = np.where(c['fav_by'] >= 0.5, 'favorite', np.where(c['fav_by'] <= -0.5, 'underdog', 'pick'))
c['edge'] = c['y'] - c['price']
def tab(cols, d=c, min_n=12):
    g = d.groupby(cols).agg(n=('y', 'size'), hit=('y', 'mean'), price=('price', 'mean')).reset_index()
    g = g[g['n'] >= min_n]; g['hit'] = (100 * g['hit']).round(1); g['price'] = (100 * g['price']).round(1); g['edge'] = (g['hit'] - g['price']).round(1)
    return g
pd.set_option('display.width', 250)
print(tab(['stat', 'fav']).to_string(index=False))
print(tab(['stat', 'arch']).to_string(index=False))
print(tab(['stat', 'arch', 'fav'], min_n=8).to_string(index=False))
c.to_pickle(S + 'arch/real_rows.pkl')
