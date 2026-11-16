import json, sys, base64, re
src, out = sys.argv[1], sys.argv[2]
d = json.load(open(src)); t = d[0]['text'] if isinstance(d, list) else d
i = t.find('data:image/jpeg;base64,'); j = t.find('"', i) if t.find('"', i) > 0 else len(t)
b = t[i + len('data:image/jpeg;base64,'):]
b = re.match(r'[A-Za-z0-9+/=]+', b).group(0)
open(out, 'wb').write(base64.b64decode(b)); print(out, len(b))
