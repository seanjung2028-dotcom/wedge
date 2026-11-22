"""Saturday-night Kalshi pull (Sat Nov 21, 10:5x PM CT), stored by the browser as one JSON (kalshi_raw_1121d.json: series -> rows of
[game code, ticker tail, yes ask, yes bid, no ask, title head, tradable]) -> raw/<SERIES>.txt in the compact format convert.py reads."""
import json, os, re, collections
D = os.path.dirname(os.path.abspath(__file__)) + '/'
K = json.load(open(D + 'kalshi_raw_1121d.json'))
for ser, S in K.items():
    rows = S['rows']; hdr = f"{S['at']} {ser} n={len(rows)} all={S['all']} cursor= pages={S['pages']}"
    if ser in ('KXNFLGAME',):
        body = ';'.join(f'{c}|{t}|{ya}/{yb}/{na}|{tr}' for c, t, ya, yb, na, _, tr in rows)
        open(D + f'raw/{ser}.txt', 'w').write(hdr + '\n' + body + '\n'); continue
    if ser in ('KXNFLSPREAD', 'KXNFLTOTAL'):
        g = collections.OrderedDict()
        for c, t, ya, yb, na, _, tr in rows:
            m = re.match(r'^([A-Z]*)(\d+)$', t); team, k = (m.group(1) or 'T'), m.group(2)
            g.setdefault((c, team), []).append(f'{k}:{ya}/{yb}/{na}:{tr}')
        body = ';'.join(f'{c}|{team}|{",".join(v)}' for (c, team), v in g.items())
        open(D + f'raw/{ser}.txt', 'w').write(hdr + ' grouped\n' + body + '\n'); continue
    g = collections.OrderedDict(); names = {}
    for c, t, ya, yb, na, nm, tr in rows:
        if ser == 'KXNFLTD' and ('D/ST' in nm or 'Defense' in nm): continue
        pc, k = t.rsplit('-', 1)
        g.setdefault((c, pc), []).append(f'{k}:{ya}/{yb}/{na}'); names[pc] = nm
    body = ';'.join(f'{c}|{pc}|{",".join(v)}' for (c, pc), v in g.items())
    open(D + f'raw/{ser}.txt', 'w').write(hdr + (' noDST' if ser == 'KXNFLTD' else '') + '\n' + body + '\n#\n' + ';'.join(f'{a}={b}' for a, b in names.items()) + '\n')
    print(ser, len(rows), 'players', len(g), 'games', sorted({c for c, _ in g}))
