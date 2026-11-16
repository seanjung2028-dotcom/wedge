"""Pool every settled real line with model numbers: Weeks 6-7 (rh/calib_rows.csv) and Week 8 (bt/w8_settled.csv)."""
import pandas as pd, numpy as np
W = '/home/claude/wedger/'
c = pd.read_csv(W + 'rh/calib_rows.csv'); c = c[c['wedger'].notna()].copy()
a = pd.DataFrame({'wk': c.wk, 'stat': c.stat, 'price': c.price, 'y': c.y.astype(float), 'v1': c.wedger, 'ours': c.ours_cal,
                  'mkt': ((c.wedger - 0.15 * c.ours_cal) / 0.85).clip(0.01, 0.99), 'model': c.model, 'n_games': c.n_games, 'player': c.player,
                  'line': c.line, 'proj': c.proj, 'pos': c.pos, 'game': c.game, 'contract': c.contract})
s = pd.read_csv(W + 'bt/w8_settled.csv', low_memory=False)
s = s[s.y.notna() & s.price.notna() & s.stat.isin(['recyd', 'rec', 'rushyd', 'passyd', 'passtd', 'int', 'rryd', 'td'])].copy()
for k in ['sit_v1', 'sit_mkt', 'sit_model', 'sit_hit', 'sit_n', 'sit_proj', 'sit_line', 'no_price']: s[k] = pd.to_numeric(s[k], errors='coerce')
s = s[s.sit_v1.notna()]
b = pd.DataFrame({'wk': 8, 'stat': s.stat, 'price': s.price, 'y': s.y, 'v1': s.sit_v1 / 100, 'mkt': s.sit_mkt / 100,
                  'ours': ((s.sit_v1 / 100 - 0.85 * s.sit_mkt / 100) / 0.15).clip(0.001, 0.999), 'model': s.sit_model / 100, 'n_games': s.sit_n,
                  'player': s.player, 'line': s.sit_line, 'proj': s.sit_proj, 'pos': s.pos if 'pos' in s else '', 'game': s.game, 'contract': s.contract,
                  'posted': s.sit_hit / 100, 'source': s.source, 'role': s.role, 'no_price': s.no_price / 100, 'pick': s.sit_pick})
P = pd.concat([a, b], ignore_index=True)
P['g5'] = P.stat.map({'rec': 'rec', 'recyd': 'recyd', 'rushyd': 'rush', 'rryd': 'rush', 'td': 'td', 'passyd': 'pass', 'passtd': 'pass', 'int': 'pass'})
P.to_pickle(W + 'bt/pool.pkl')
print(P.groupby(['wk']).size().to_dict())
print(P.groupby(['g5', 'wk']).agg(n=('y', 'size'), hit=('y', 'mean'), price=('price', 'mean'), mkt=('mkt', 'mean'), v1=('v1', 'mean'), ours=('ours', 'mean')).round(3).unstack())
