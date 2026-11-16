"""Mon Nov 2: finished Week 8 games keep the rows they were posted with (Thu Oct 29 ~5:15 PM CT upload);
CHI @ SEA rows come from the Monday re-price. Writes merged CSVs to mnf_out/."""
import pandas as pd, os
W = '/home/claude/wedger/'; R = W + 'rh/'; T = W + 'thu_posted/'; O = W + 'mnf_out/'
G = 'CHI @ SEA'
rd = lambda p: pd.read_csv(p, dtype=str, keep_default_na=False)
thu = {'inband': rd(W + 'dbsnap1029b/blobs/20063d8cbc21629541f480f673e9a2f4.csv'), 'props': rd(T + 'b2831372c5e0ff74c63ecaadfdeff144.csv'),
       'atd': rd(T + '37dbf03e807e6b55071d1d8755397eb0.csv'), 'sit': rd(T + '5af8d6a74ba6e763146fb5308011a9d1.csv'),
       'outlook': rd(T + '36a6289a9770d3f27ffa6428587b14fc.csv'), 'nflctx': rd(T + '775d70259c0d918f710b6f92055c3e4d.csv'), 'proj': rd(T + 'd92a5680090a7a6be48b3459ce869bb1.csv')}
new = {'inband': rd(R + 'inband_w8.csv'), 'props': rd(R + 'props_cat_w8.csv'), 'atd': rd(R + 'atd_w8.csv'), 'sit': rd(R + 'sit_w8.csv'),
       'outlook': rd(R + 'outlook_w8.csv'), 'nflctx': rd(R + 'nflctx_w8.csv'), 'proj': rd(R + 'proj_w8.csv')}
def cat(a, b):
    for c in a.columns:
        if c not in b.columns: b[c] = ''
    extra = [c for c in b.columns if c not in a.columns]
    if extra: print('  new-only columns dropped:', extra)
    return pd.concat([a, b[a.columns]], ignore_index=True)
out = {}
# lines + props share ids
ni = new['inband'][new['inband']['game'] == G].copy()
nmax = max(int(x[1:]) for x in thu['inband']['id'] if x[1:].isdigit())
idmap = {old: f'L{nmax + 41 + k:03d}' for k, old in enumerate(ni['id'])}
ni['id'] = ni['id'].map(idmap)
out['inband'] = cat(thu['inband'][thu['inband']['game'] != G], ni)
npp = new['props'][new['props']['game'] == G].copy()
assert set(npp['id']) <= set(idmap), set(npp['id']) - set(idmap)
npp['id'] = npp['id'].map(idmap)
out['props'] = cat(thu['props'][thu['props']['game'] != G], npp)
out['atd'] = cat(thu['atd'][thu['atd']['game'] != G], new['atd'][new['atd']['game'] == G].copy())
nj = new['proj'][new['proj']['game'] == G].copy(); nj['id'] = [f'P{900 + k}' for k in range(len(nj))]
out['proj'] = cat(thu['proj'][thu['proj']['game'] != G], nj)
gk = lambda df: df['key'].str.split('|').str[0]
assert (gk(new['outlook']).str.contains(' @ ')).all()
out['outlook'] = cat(thu['outlook'][gk(thu['outlook']) != G], new['outlook'][gk(new['outlook']) == G].copy())
ns = new['sit'][new['sit']['team'].isin(['CHI', 'SEA'])]
out['sit'] = cat(thu['sit'][~thu['sit']['key'].isin(ns['key'])], ns.copy())
mine = lambda df: ((df['kind'] == 'game') & (df['key'] == G)) | ((df['kind'] == 'mb') & df['key'].str.split('|').str[0].isin(['CHI', 'SEA']))
out['nflctx'] = cat(thu['nflctx'][~mine(thu['nflctx'])], new['nflctx'][mine(new['nflctx'])].copy())
names = {'inband': 'inband_w8.csv', 'props': 'props_cat_w8.csv', 'atd': 'atd_w8.csv', 'sit': 'sit_w8.csv', 'outlook': 'outlook_w8.csv', 'nflctx': 'nflctx_w8.csv', 'proj': 'proj_w8.csv'}
for k, df in out.items():
    df.to_csv(O + names[k], index=False)
    print(k, 'thu', len(thu[k]), '-> merged', len(df), '| CHI@SEA rows thu/new:',
          (thu[k]['game'] == G).sum() if 'game' in thu[k] else '-', (df['game'] == G).sum() if 'game' in df else '-')
