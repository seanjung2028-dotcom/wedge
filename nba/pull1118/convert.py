"""Rebuild the Kalshi NBA pull (kalshi_nba_1118.json, {'at', 'out': {SERIES: [[tail, event, title, floor, ya, yb, last, vol], ...]}})
and the ESPN injury report (espn_inj_nba.json, {'at', 'inj': {TEAM: {name: 'Out'|'GTD'}}}) from the compact browser pulls in this folder.
Props other than points were pulled only where the ask was 44-56c (nba_lines.py keeps the 45-55c band)."""
import json, os, re
H = os.path.dirname(os.path.abspath(__file__)) + '/'
out, at = {}, {}
def p4(s): return [int(x) for x in s.split('/')]
# points: one line, EVT|PLAYERCODE|Name|k:ya/yb/last/vol,...;...
hdr, body = open(H + 'KXNBAPTS.txt').read().split('\n', 1)
at['KXNBAPTS'] = hdr.split()[0]; rows = []
for grp in body.strip().split(';'):
    evt, pc, nm, rungs = grp.split('|')
    for rg in rungs.split(','):
        k, px = rg.split(':'); ya, yb, last, vol = p4(px)
        rows.append([f'{pc}-{k}', f'KXNBAPTS-{evt}', f'{nm}: {k}+ points', int(k) - 0.5, ya, yb, last, vol])
out['KXNBAPTS'] = rows
# rebounds / assists / threes: EVT|TAIL|ya/yb/last/vol|title ; PRA: EVT|TAIL|ya/yb/last/vol|Name
for ser in ('KXNBAREB', 'KXNBAAST', 'KXNBA3PT', 'KXNBAPRA'):
    lines = open(H + ser + '.txt').read().strip().split('\n'); at[ser] = lines[0].split()[0]; rows = []
    for ln in lines[1:]:
        evt, tail, px, t = ln.split('|'); ya, yb, last, vol = p4(px); k = int(tail.rsplit('-', 1)[1])
        title = f'{t}: {k}+ combined points, rebounds, and assists' if ser == 'KXNBAPRA' else t
        rows.append([tail, f'{ser}-{evt}', title, k - 0.5, ya, yb, last, vol])
    out[ser] = rows
# moneyline: EVT|TEAM|ya/yb/last/vol|title
lines = open(H + 'KXNBAGAME.txt').read().strip().split('\n'); at['KXNBAGAME'] = lines[0].split()[0]
out['KXNBAGAME'] = [[t, f'KXNBAGAME-{e}', ti, None] + p4(px) for e, t, px, ti in (ln.split('|') for ln in lines[1:])]
# ladders: EVT|TEAM(or T)|title{}#suffix~strike|strike:ya/yb/last/vol,...
for ser in ('KXNBASPREAD', 'KXNBATOTAL', 'KXNBATEAMTOTAL'):
    lines = open(H + ser + '.txt').read().strip().split('\n'); at[ser] = lines[0].split()[0]; rows = []
    for ln in lines[1:]:
        evt, team, tpl, rungs = ln.split('|'); tpl = tpl.split('#')[0]
        for rg in rungs.split(','):
            st, px = rg.split(':'); x = float(st); suf = str(int(x + 0.5))
            tail = suf if team == 'T' else team + suf
            rows.append([tail, f'{ser}-{evt}', tpl.replace('{}', st), x] + p4(px))
    out[ser] = rows
json.dump({'at': at, 'out': out}, open(H + '../kalshi_nba_1118.json', 'w'), ensure_ascii=False)
print({k: len(v) for k, v in out.items()})
# injuries
FIX = {'GS': 'GSW', 'NO': 'NOP', 'UTAH': 'UTA', 'WSH': 'WAS', 'NY': 'NYK', 'SA': 'SAS'}
lines = open(H + 'espn_inj_raw.txt').read().strip().split('\n'); inj = {}
for ln in lines[1:]:
    t, rest = ln.split(':', 1); t = FIX.get(t, t)
    for it in rest.split(';'):
        nm, st = it.split('=', 1); st = st.split('@')[0]
        inj.setdefault(t, {})[nm] = 'Out' if st == 'Out' else 'GTD'
json.dump({'at': lines[0].split()[0], 'src': 'ESPN injury report', 'inj': inj}, open(H + 'espn_inj_nba.json', 'w'), ensure_ascii=False, indent=0)
print(sum(len(v) for v in inj.values()), 'injuries on', len(inj), 'teams')
