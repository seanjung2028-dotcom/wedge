import json, sys
src, tag, out = sys.argv[1], sys.argv[2], sys.argv[3]
t = json.load(open(src)); t = t[0]['text'] if isinstance(t, list) else t
if t.lstrip().startswith('"'): t, _ = json.JSONDecoder().raw_decode(t.lstrip())
i = t.index(tag + '<<') + len(tag) + 2; j = t.index('>>END', i)
s = t[i:j]
if '…[truncated' in s: sys.exit('TRUNCATED')
d = json.loads(s); json.dump(d, open(out, 'w')); print(out, len(s))
