"""Extract tagged chunks (TAG0<<...>>TAG0 ...) from a saved browser_batch tool result and join them into JSON."""
import json, re, sys
F, tag, n, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
arr = json.load(open(F)); txt = ''.join(x.get('text', '') for x in arr)
raw = ''
for i in range(n):
    m = re.search(r'%s%d<<(.*?)>>%s%d' % (tag, i, tag, i), txt, re.S)
    if m: raw += m.group(1)
try: d = json.loads(raw)
except Exception:
    d = json.loads(raw.encode('utf-8').decode('unicode_escape').encode('latin-1').decode('utf-8'))
json.dump(d, open(out, 'w'))
for t in re.findall(r'(\w+)<<(\{[^<]{0,400}\})>>\1', txt):
    if not re.match(r'%s\d' % tag, t[0]): print(t[0], t[1])
print('ok', out)
