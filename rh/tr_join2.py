import json, sys
out, paths = sys.argv[1], sys.argv[2:]
parts = []
for f in paths:
    t = json.load(open(f))[0]['text']
    s, _ = json.JSONDecoder().raw_decode(t)
    parts.append(s.rstrip(' '))
full = ''.join(parts)
d = json.loads(full)
json.dump(d, open(out, 'w'))
print(out, len(full))
