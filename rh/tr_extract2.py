"""Safe tagged-chunk extractor (no regex scan of padding)."""
import json, sys
F, tag, n, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
arr = json.load(open(F)); txt = ''.join(x.get('text', '') for x in arr)
raw = ''
for i in range(n):
    a = txt.index(f'{tag}{i}<<') + len(f'{tag}{i}<<'); b = txt.index(f'>>{tag}{i}', a); raw += txt[a:b]
try: d = json.loads(raw)
except Exception: d = json.loads(raw.encode('utf-8').decode('unicode_escape').encode('latin-1').decode('utf-8'))
json.dump(d, open(out, 'w')); print('ok', out)
