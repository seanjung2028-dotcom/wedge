"""Pull the last tool result containing a marker out of this session's transcript (browser pulls come back as tool results)."""
import json, sys
p = '/root/.claude/projects/-home-claude/7b7587cd-449e-5d94-986d-7a2d5c82d9a5.jsonl'
def last_result(marker):
    txt = None
    for line in open(p):
        if marker not in line or 'tool_result' not in line: continue
        o = json.loads(line); c = o.get('message', {}).get('content')
        if not isinstance(c, list): continue
        for b in c:
            if b.get('type') == 'tool_result':
                t = b['content'] if isinstance(b['content'], str) else ''.join(x.get('text', '') for x in b['content'] if isinstance(x, dict))
                if marker in t: txt = t
    return txt
