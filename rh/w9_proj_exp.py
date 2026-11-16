"""Projections (v5): 'Wedger % if priced 50¢' = 50¢ shifted by the market's over bias (Weeks 6-8). Anytime TDs keep our read
with the TD calibration. Run after w9_model.py."""
import csv, json, sys, math
B = '/home/claude/wedger/rh/'
sys.path.insert(0, B); import nfl_model as M
M.CAL = dict(M.CAL_V3)
CAL5 = json.load(open('/home/claude/wedger/bt/cal_v51.json'))['cal_v5']
G5 = {'rec': 'rec', 'recyd': 'recyd', 'rushyd': 'rush', 'td': 'td', 'passyd': 'passyd'}
STAT = {'Passing Yards': 'passyd', 'Rushing Yards': 'rushyd', 'Receiving Yards': 'recyd', 'Receptions': 'rec', 'Anytime Touchdown': 'td'}
P = list(csv.DictReader(open(B + 'proj_w9.csv')))
O = list(csv.DictReader(open(B + 'outlook_w9.csv'))); OI = {r['key']: i for i, r in enumerate(O)}
for p in P:
    st = STAT[p['market']]; ours = float(p['p_over']) / 100
    pw = M.calibrate(ours, st, 99) if st == 'td' else 1 / (1 + math.exp(-CAL5[G5[st]]))
    k = f"{p['game']}|{p['market']}|{p['contract']}"; i = OI[k]; d = json.loads(O[i]['detail'])
    p.pop('p_wedger', None); p['p_wedger'] = round(100 * pw, 1)
    if d.get('cal') == 'proj': d['P_exp'] = round(pw, 4); d['P'] = round(ours, 4); O[i]['detail'] = json.dumps(d, separators=(',', ':'), ensure_ascii=False)
cols = list(P[0].keys()); cols.insert(cols.index('p_over') + 1, cols.pop(cols.index('p_wedger')))
with open(B + 'proj_w9.csv', 'w', newline='') as f: w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(P)
with open(B + 'outlook_w9.csv', 'w', newline='') as f: w = csv.DictWriter(f, fieldnames=['key', 'detail']); w.writeheader(); w.writerows(O)
import collections
by = collections.defaultdict(list)
for p in P: by[p['market']].append(float(p['p_wedger']))
print({k: (round(min(v), 1), round(sum(v) / len(v), 1), round(max(v), 1)) for k, v in by.items()})
