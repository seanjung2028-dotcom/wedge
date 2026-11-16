import pandas as pd, numpy as np
S = pd.read_csv('/home/claude/wedger/bt/w8_settled.csv', low_memory=False)
S = S[S.y.notna() & S.price.notna()].copy()
for c in ['sit_hit', 'sit_model', 'sit_v1', 'mom_p', 'book_fair', 'sit_proj', 'sit_pedge', 'no_price', 'yes_bid', 'sit_line', 'actual', 'sit_mkt']:
    if c in S: S[c] = pd.to_numeric(S[c], errors='coerce')
props = S[S.stat.isin(['recyd', 'rec', 'rushyd', 'passyd', 'passtd', 'int', 'rryd', 'td'])].copy()
br = lambda p, y: np.mean((p - y) ** 2)
print('=== Week 8 player props + ATD, settled', len(props))
m = props.dropna(subset=['sit_hit'])
for nm, col, sc in [('Yes ask price', 'price', 1), ('books fair', 'book_fair', 100), ('Wedger v4', 'sit_hit', 100), ('model only', 'sit_model', 100), ('blend pre-cal v1', 'sit_v1', 100), ('last-4 view', 'mom_p', 100), ('market used', 'sit_mkt', 100)]:
    mm = m.dropna(subset=[col]) if col in m else None
    if mm is None or not len(mm): continue
    print(f'{nm:18s} n={len(mm):4d} brier={br(mm[col] / sc, mm.y):.4f}  (price on same rows {br(mm.price, mm.y):.4f})')
print('\n=== by stat: n, hit rate, avg price, avg Wedger, avg model')
print(m.groupby('stat').agg(n=('y', 'size'), hit=('y', 'mean'), price=('price', 'mean'), wedger=('sit_hit', lambda x: x.mean() / 100), model=('sit_model', lambda x: x.mean() / 100), fair=('book_fair', lambda x: x.mean() / 100)).round(3))
print('\n=== by source')
print(m.groupby('source').agg(n=('y', 'size'), hit=('y', 'mean'), price=('price', 'mean'), wedger=('sit_hit', lambda x: x.mean() / 100)).round(3))
p = S[S.sit_pick.isin(['Yes', 'No'])].copy()
p['win'] = np.where(p.sit_pick == 'Yes', p.y, 1 - p.y)
p['cost'] = np.where(p.sit_pick == 'Yes', p.price * 100, p.no_price)
p['pnl'] = np.where(p.win == 1, 100 - p.cost, -p.cost)
print('\n=== picks', len(p), 'record', int(p.win.sum()), '-', int((1 - p.win).sum()), 'ROI', round(p.pnl.sum() / p.cost.sum() * 100, 1), '%')
print(p.groupby(['sit_pick', 'stat']).agg(n=('win', 'size'), won=('win', 'mean'), avg_cost=('cost', 'mean'), pnl=('pnl', 'sum')).round(2))
p['edge_b'] = pd.cut(p.sit_pedge, [0, 5, 8, 11, 50])
print(p.groupby('edge_b', observed=True).agg(n=('win', 'size'), won=('win', 'mean'), pnl=('pnl', 'sum')).round(2))
q = m.dropna(subset=['sit_proj', 'actual'])
q = q[q.stat.isin(['recyd', 'rec', 'rushyd', 'passyd', 'rryd'])]
q['err'] = q.actual - q.sit_proj
print('\n=== projection error (actual - projection) by stat (unique player-stat)')
qq = q.drop_duplicates(['player', 'stat'])
print(qq.groupby('stat').agg(n=('err', 'size'), bias=('err', 'mean'), mae=('err', lambda x: x.abs().mean()), line_bias=('actual', 'mean'), proj=('sit_proj', 'mean'), line=('sit_line', 'mean')).round(1))
print(qq.groupby(['role']).agg(n=('err', 'size'), bias=('err', 'mean'), mae=('err', lambda x: x.abs().mean())).round(1).sort_values('n', ascending=False).head(14))
