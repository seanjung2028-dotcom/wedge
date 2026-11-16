"""Live read of Wedger v2 on Week 7 (posted Sun Oct 25 ~11:56 AM CT, before the early kickoffs).

Every Week 7 line the site posted with a Wedger % (Week 7 lines, Prop categories, ATD tabs), joined to its settled outcome.
NE @ CHI and PIT @ NO were already final when v2 was fitted (they are in its training set) and DAL @ PHI hasn't played,
so the out-of-sample set is the 12 Sunday games. Writes live_eval_w7.json for the page and the growth-plan doc.
"""
import csv, json, math, collections
import pandas as pd, numpy as np
B = '/home/claude/wedger/rh/'
num = lambda x: None if x in ('', None) else float(x)
res = {}
for r in csv.DictReader(open(B + 'results_w6_w7.csv')):
    if r['week'] != '7' or r['group'] != 'Week 7 settled': continue
    res[(r['game'], r['market'], r['contract'])] = r['outcome']
rows = {}
for f in ('inband_w7.csv', 'props_cat_w7.csv'):
    for r in csv.DictReader(open(B + f)):
        if r.get('id', '').startswith('C'): continue            # re-added picked lines carry old prices
        k = (r['game'], r['market'], r['contract'])
        if k in rows or r.get('sit_hit') in ('', None): continue
        rows[k] = {'game': r['game'], 'market': r['market'], 'contract': r['contract'], 'price': num(r['yes_price']), 'bid': num(r.get('yes_bid')),
                   'no': num(r.get('no_price')), 'src': r['source'], 'v2': num(r['sit_hit']), 'v1': num(r.get('sit_v1')), 'pick': r.get('sit_pick', ''),
                   'pedge': num(r.get('sit_pedge')), 'qual': r.get('qualifies', ''), 'tab': f}
for r in csv.DictReader(open(B + 'atd_w7.csv')):
    k = (r['game'], 'Anytime Touchdown', r['player'])
    if k in rows or r.get('sit_hit') in ('', None): continue
    rows[k] = {'game': r['game'], 'market': 'Anytime Touchdown', 'contract': r['player'], 'price': num(r['yes_price']), 'bid': num(r.get('yes_bid')),
               'no': None, 'src': r['source'], 'v2': num(r['sit_hit']), 'v1': num(r.get('sit_v1')), 'pick': r.get('sit_pick', ''),
               'pedge': num(r.get('sit_pedge')), 'qual': '', 'tab': 'atd_w7.csv'}
SKIP = {'NE @ CHI', 'PIT @ NO', 'DAL @ PHI'}
D = []
for k, r in rows.items():
    o = res.get(k)
    if r['game'] in SKIP or o not in ('Won', 'Lost') or r['price'] is None or r['v1'] is None: continue
    r['y'] = 1 if o == 'Won' else 0
    r['no_ask'] = r['no'] if r['no'] is not None else (100 - r['bid'] if r['bid'] is not None else None)
    D.append(r)
D = pd.DataFrame(D)
GROUP = lambda m: 'Rushing / R+R' if m in ('Rushing Yards', 'Rushing + Receiving Yards') else ('Anytime TD' if m == 'Anytime Touchdown' else
        ('Passing' if m in ('Passing Yards', 'Passing Touchdowns', 'Interceptions') else 'Receiving'))
D['grp'] = D['market'].map(GROUP)
def brier(p, y): return round(float(np.mean((p - y) ** 2)), 4)
def scores(d):
    return {'n': int(len(d)), 'yes_rate': round(100 * d['y'].mean(), 1), 'avg_price': round(d['price'].mean(), 1),
            'brier_price': brier(d['price'] / 100, d['y']), 'brier_v1': brier(d['v1'] / 100, d['y']), 'brier_v2': brier(d['v2'] / 100, d['y']),
            'v2_mean': round(d['v2'].mean(), 1), 'v1_mean': round(d['v1'].mean(), 1)}
def record(d, side):
    if not len(d): return {'n': 0}
    if side == 'Yes':
        won = d['y'] == 1; cost = d['price']; prof = np.where(won, 100 - d['price'], -d['price'])
    else:
        won = d['y'] == 0; cost = d['no_ask']; prof = np.where(won, 100 - d['no_ask'], -d['no_ask'])
    return {'n': int(len(d)), 'won': int(won.sum()), 'win_pct': round(100 * won.mean(), 1), 'avg_cost': round(float(cost.mean()), 1),
            'profit_c': int(round(float(prof.sum()))), 'roi': round(100 * float(prof.sum()) / float(cost.sum()), 1)}
band = D[(D['price'] >= 40) & (D['price'] <= 60)]
rh = D[(D['src'] == 'Robinhood') & D['no_ask'].notna()]
out = {'games': sorted(D['game'].unique().tolist()), 'all': scores(D), 'band40_60': scores(band),
       'by_group': {g: scores(x) for g, x in D.groupby('grp')},
       'v2_yes': record(rh[rh['pick'] == 'Yes'], 'Yes'), 'v2_no': record(rh[rh['pick'] == 'No'], 'No'),
       'v2_any': None,
       'v1_yes': record(rh[(rh['v1'] - rh['price']) >= 3], 'Yes'),
       'all_yes': record(rh, 'Yes'), 'all_no': record(rh, 'No'),
       'filter_yes': record(rh[rh['qual'] == 'Yes'], 'Yes'),
       'v2_no_by_group': {g: record(x[x['pick'] == 'No'], 'No') for g, x in rh.groupby('grp')},
       'v2_yes_by_group': {g: record(x[x['pick'] == 'Yes'], 'Yes') for g, x in rh.groupby('grp')},
       'all_no_by_group': {g: record(x, 'No') for g, x in rh.groupby('grp')}}
p = rh[rh['pick'].isin(['Yes', 'No'])]
prof = np.where(p['pick'] == 'Yes', np.where(p['y'] == 1, 100 - p['price'], -p['price']), np.where(p['y'] == 0, 100 - p['no_ask'], -p['no_ask']))
cost = np.where(p['pick'] == 'Yes', p['price'], p['no_ask'])
won = np.where(p['pick'] == 'Yes', p['y'] == 1, p['y'] == 0)
out['v2_any'] = {'n': int(len(p)), 'won': int(won.sum()), 'win_pct': round(100 * won.mean(), 1), 'profit_c': int(round(prof.sum())), 'roi': round(100 * prof.sum() / cost.sum(), 1)}
# bigger edges
for lo in (3, 5, 8):
    q = p[p['pedge'] >= lo]
    pr = np.where(q['pick'] == 'Yes', np.where(q['y'] == 1, 100 - q['price'], -q['price']), np.where(q['y'] == 0, 100 - q['no_ask'], -q['no_ask']))
    co = np.where(q['pick'] == 'Yes', q['price'], q['no_ask']); wn = np.where(q['pick'] == 'Yes', q['y'] == 1, q['y'] == 0)
    out[f'v2_edge{lo}'] = {'n': int(len(q)), 'won': int(wn.sum()), 'win_pct': round(100 * wn.mean(), 1) if len(q) else None, 'profit_c': int(round(pr.sum())),
                           'roi': round(100 * pr.sum() / co.sum(), 1) if len(q) else None}
# calibration buckets of v2
cal = []
for lo in range(10, 90, 10):
    b = D[(D['v2'] >= lo) & (D['v2'] < lo + 10)]
    if len(b) >= 5: cal.append({'lo': lo, 'hi': lo + 10, 'n': int(len(b)), 'pred': round(b['v2'].mean(), 1), 'hit': round(100 * b['y'].mean(), 1), 'price': round(b['price'].mean(), 1)})
out['calibration_v2'] = cal
json.dump(out, open(B + 'live_eval_w7.json', 'w'), indent=1)
D.to_csv(B + 'live_eval_w7_rows.csv', index=False)
print(json.dumps({k: v for k, v in out.items() if k not in ('games',)}, indent=0)[:6000])
