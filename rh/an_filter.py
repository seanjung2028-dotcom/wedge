"""Keep the five main books (Caesars 49, DraftKings 68, FanDuel 69, BetRivers 71, BetMGM 75); fall back to consensus 15."""
import json, sys
src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src)); KEEP = {49, 68, 69, 71, 75}
rows = []
for r in d['rows']:
    ok = (lambda b: True) if r[0] == 'Anytime Touchdown' else (lambda b: b[2] is not None and b[3] is not None)
    bk = [b for b in r[5] if b[0] in KEEP and ok(b)] or [b for b in r[5] if b[0] == 15 and ok(b)]
    if not bk: continue
    if r[0] == 'Anytime Touchdown': bk = [[b[0], None, b[2], b[3], b[4]] for b in bk]
    rows.append([r[0], r[1], r[2], r[3], r[4], bk])
out = {k: v for k, v in d.items() if k not in ('rows', 'dbg')}; out['rows'] = rows
json.dump(out, open(dst, 'w'))
print(len(d['rows']), '->', len(rows))
