import json, sys, base64, re
src, out = sys.argv[1], sys.argv[2]
t = json.load(open(src)); t = t[0]['text'] if isinstance(t, list) else t
m = re.search(r'data:(image/[a-z+]+);base64,([A-Za-z0-9+/=]+)', t)
open(out, 'wb').write(base64.b64decode(m.group(2))); print(out, m.group(1), len(m.group(2)))
