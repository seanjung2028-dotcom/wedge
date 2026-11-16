"""Mon Nov 9 ~2:40 PM CT: live Kalshi BUF @ MIN ladders (player props, spread, total, moneyline) pulled through the user's browser.
Reads the compact dump from the session transcript (tool result id passed as argv[1]) and writes pull1109/kalshi_1109.json."""
import json, sys
p = '/root/.claude/projects/-home-claude/7b7587cd-449e-5d94-986d-7a2d5c82d9a5.jsonl'; TID = sys.argv[1]
txt = None
for line in open(p):
    if TID not in line: continue
    o = json.loads(line); c = o.get('message', {}).get('content')
    if isinstance(c, list):
        for b in c:
            if b.get('type') == 'tool_result' and b.get('tool_use_id') == TID:
                txt = ''.join(x.get('text', '') for x in b['content'] if isinstance(x, dict))
s = txt[:txt.index('\n\n(captured')]
d = json.loads(json.loads(s))
names = d['names']; Q = {}
for ser, blob in d['out'].items():
    for row in blob.split(';'):
        f = row.split('|'); t = f'{ser}-26NOV09BUFMIN-{f[0]}'
        code, k = (f[0].rsplit('-', 1) if '-' in f[0] else (f[0], ''))
        sub = names.get(code, code) + (f': {k}+' if k else '')
        Q[t] = [f'{int(f[1]) / 100:.2f}', f'{int(f[2]) / 100:.2f}', f'{int(f[3]) / 100:.2f}', 'active' if f[5] == '1' else 'inactive', sub, int(f[6]), f'{int(f[4]) / 100:.2f}'] + f[7:]
json.dump({'at0': d['at'], 'at1': d['at'], 'names': names, 'q': Q}, open('/home/claude/wedger/pull1109/kalshi_1109.json', 'w'))
print(d['at'], len(Q))
