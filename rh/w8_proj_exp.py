"""Projections: add 'Wedger % if priced 50¢' = calibrate(0.85 x 50% + 0.15 x our read) with the v3 calibration (run after w8_model.py)."""
import csv, json, sys, math
B = '/home/claude/wedger/rh/'
sys.path.insert(0, B); import nfl_model as M
M.CAL = dict(M.CAL_V3)
STAT = {'Passing Yards': 'passyd', 'Rushing Yards': 'rushyd', 'Receiving Yards': 'recyd', 'Receptions': 'rec', 'Anytime Touchdown': 'td'}
P = list(csv.DictReader(open(B + 'proj_w8.csv')))
O = list(csv.DictReader(open(B + 'outlook_w8.csv'))); OI = {r['key']: i for i, r in enumerate(O)}
for p in P:
    st = STAT[p['market']]; ours = float(p['p_over']) / 100
    # yards / catches: the expected line should post near 50¢; anytime TDs vary by player, so use our read with the TD calibration
    pw = M.calibrate(ours, st, 99) if st == 'td' else M.calibrate(M.W_MKT_V3 * 0.5 + (1 - M.W_MKT_V3) * ours, st, 99)
    k = f"{p['game']}|{p['market']}|{p['contract']}"; i = OI[k]; d = json.loads(O[i]['detail'])
    rm = d.get('rm') or 0.0      # role-matchup shift (already x RM_K), logit scale
    if rm: pw = 1 / (1 + math.exp(-(math.log(pw / (1 - pw)) + rm)))
    p.pop('p_wedger', None); p['p_wedger'] = round(100 * pw, 1)
    if d.get('cal') == 'proj': d['P_exp'] = round(pw, 4); O[i]['detail'] = json.dumps(d, separators=(',', ':'), ensure_ascii=False)
cols = list(P[0].keys()); cols.insert(cols.index('p_over') + 1, cols.pop(cols.index('p_wedger')))
with open(B + 'proj_w8.csv', 'w', newline='') as f: w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(P)
with open(B + 'outlook_w8.csv', 'w', newline='') as f: w = csv.DictWriter(f, fieldnames=['key', 'detail']); w.writeheader(); w.writerows(O)
import collections
by = collections.defaultdict(list)
for p in P: by[p['market']].append(p['p_wedger'])
print({k: (round(min(v), 1), round(sum(v) / len(v), 1), round(max(v), 1)) for k, v in by.items()})
