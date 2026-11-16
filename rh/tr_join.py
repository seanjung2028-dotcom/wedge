import json, sys
D = '/root/.claude/projects/-home-claude/7b7587cd-449e-5d94-986d-7a2d5c82d9a5/tool-results/mcp-remote-devices-Claude_Browser__javascript_tool-'
out, ids = sys.argv[1], sys.argv[2:]
parts = []
for f in ids:
    t = json.load(open(D + f + '.txt'))[0]['text']
    s, _ = json.JSONDecoder().raw_decode(t)
    parts.append(s.rstrip(' '))
full = ''.join(parts)
d = json.loads(full)
json.dump(d, open(out, 'w'))
print(out, len(full))
