"""Fri Nov 27 pull (Sunday and Monday games, 2:56 AM CT). Turn the compact pull (raw/<SERIES>.txt, one file per Kalshi series, read from the exchange's market list with a
browser) into the pull files w12/build_inputs.py reads: kalshi_props_w12.json {at, n, q} and kalshi_games_w12.json {at, q}.
Raw format: first line '<ISO time> <SERIES> n=<rows> ...' (optional), then 'CODE|PLAYER|k:ya/yb/na,...;...' for props or
'CODE|SUFFIX|ya/yb/na|tradable;...' for game series, then '#' and 'PLAYER=Name;...' for props."""
import json, os, re, sys, glob
D = os.path.dirname(os.path.abspath(__file__)) + '/'
PROPS = ['KXNFLREC', 'KXNFLRECYDS', 'KXNFLRSHYDS', 'KXNFLPASSYDS', 'KXNFLPASSTDS', 'KXNFLRRYDS', 'KXNFLTD']
GAMES = ['KXNFLGAME', 'KXNFLSPREAD', 'KXNFLTOTAL']
KCITY = {'ARI': 'Arizona', 'LA': 'Los Angeles R', 'BAL': 'Baltimore', 'CLE': 'Cleveland', 'BUF': 'Buffalo', 'LV': 'Las Vegas', 'CAR': 'Carolina',
         'PHI': 'Philadelphia', 'CHI': 'Chicago', 'ATL': 'Atlanta', 'DAL': 'Dallas', 'GB': 'Green Bay', 'HOU': 'Houston', 'JAC': 'Jacksonville',
         'LAC': 'Los Angeles C', 'KC': 'Kansas City', 'NO': 'New Orleans', 'NYG': 'New York G', 'NYJ': 'New York J', 'NE': 'New England',
         'PIT': 'Pittsburgh', 'TB': 'Tampa Bay', 'TEN': 'Tennessee', 'IND': 'Indianapolis', 'SF': 'San Francisco', 'WAS': 'Washington',
         'MIN': 'Minnesota', 'MIA': 'Miami', 'CIN': 'Cincinnati', 'DET': 'Detroit', 'DEN': 'Denver', 'SEA': 'Seattle'}
def read(ser):
    p = D + f'raw/{ser}.txt'
    if not os.path.exists(p): return None, '', ''
    t = open(p).read().strip('\n'); at = None
    first, _, rest = t.partition('\n')
    if re.match(r'^\d{4}-\d\d-\d\dT', first): at, t = first.split()[0], rest
    body, _, names = t.partition('\n#\n')
    return at, body.strip(), names.strip()
ats, q, n, missing = [], {}, {}, []
for ser in PROPS:
    at, body, names = read(ser)
    if at: ats.append(at)
    if body is None or (not body and at is None and not os.path.exists(D + f'raw/{ser}.txt')): missing.append(ser); q[ser] = ''; continue
    rows = []
    for grp in filter(None, body.split(';')):
        code, pc, rungs = grp.split('|')
        for r in rungs.split(','):
            k, quote = r.split(':'); ya, yb, na = quote.split('/')
            rows.append(f'{code}|{pc}-{k}|{ya}|{yb}|{na}')
    q[ser] = ';'.join(rows)
    for kv in filter(None, names.split(';')):
        a, _, b = kv.partition('='); n[a] = b
gq = {}
for ser in GAMES:
    at, body, _ = read(ser)
    if at: ats.append(at)
    if not os.path.exists(D + f'raw/{ser}.txt'): missing.append(ser); continue
    rows, flat = [], []
    for r in filter(None, body.split(';')):                    # grouped form: CODE|TEAM (or T for totals)|k:ya/yb/na:t,...
        f = r.split('|')
        if len(f) == 3 and ':' in f[2]:
            for x in f[2].split(','):
                k, q_, t_ = x.split(':'); flat.append(f'{f[0]}|{"" if f[1] == "T" else f[1]}{k}|{q_}|{t_}')
        else: flat.append(r)
    for r in flat:
        code, suf, quote, tr = r.split('|'); ya, yb, na = quote.split('/')
        if ser == 'KXNFLGAME': title = KCITY.get(suf, suf)
        elif ser == 'KXNFLSPREAD':
            m = re.match(r'^([A-Z]+?)(\d+)$', suf); title = f'{KCITY.get(m.group(1), m.group(1))} wins by over {int(m.group(2)) - 0.5} points'
        else: title = f'Over {int(suf) - 0.5} points'
        rows.append(f'{code}|{suf}|{ya}|{yb}|{na}|{tr}|{title}')
    gq[ser] = ';'.join(rows)
at = max(ats) if ats else None
if False:
    M = {}
    for ser in missing:
        if ser in M['q']: q[ser] = M['q'][ser]
    for k, v in M['n'].items(): n.setdefault(k, v)
json.dump({'at': at, 'n': n, 'q': q}, open(D + 'kalshi_props_w12.json', 'w'))
if len(gq) == len(GAMES): json.dump({'at': at, 'q': gq}, open(D + 'kalshi_games_w12.json', 'w'))
print('props', {k: (v.count(';') + 1 if v else 0) for k, v in q.items()}, 'names', len(n), 'games', {k: v.count(';') + 1 for k, v in gq.items()}, 'missing', missing, 'at', at)

# markets the research method adds (Fri Nov 27): rushing and passing attempts (player ladders), team totals and team sacks (game ladders).
# The model doesn't price these: the card reads them at the market's own number, and only the research can put one on the card.
EXTRA_P = ['KXNFLRSHATT', 'KXNFLPASSATT']; EXTRA_G = ['KXNFLTEAMTOTAL', 'KXNFLTEAMSACK']
ex = {'at': at, 'props': {}, 'games': {}, 'n': {}}
for ser in EXTRA_P:
    at_, body, names = read(ser); rows = []
    for grp in filter(None, (body or '').split(';')):
        code, pc, rungs = grp.split('|')
        for r in rungs.split(','):
            k, quote = r.split(':'); ya, yb, na = quote.split('/'); rows.append([code, pc, int(k), int(ya or 0), int(yb or 0), int(na or 0)])
    ex['props'][ser] = rows
    for kv in filter(None, names.split(';')):
        a, _, b = kv.partition('='); ex['n'][a] = b
for ser in EXTRA_G:
    at_, body, _ = read(ser); rows = []
    for grp in filter(None, (body or '').split(';')):
        code, team, rungs = grp.split('|')
        for x in rungs.split(','):
            k, quote, tr = x.split(':'); ya, yb, na = quote.split('/'); rows.append([code, team, int(k), int(ya or 0), int(yb or 0), int(na or 0), int(tr)])
    ex['games'][ser] = rows
json.dump(ex, open(D + 'kalshi_extra_w12.json', 'w'))
print('extra', {k: len(v) for k, v in {**ex['props'], **ex['games']}.items()})
