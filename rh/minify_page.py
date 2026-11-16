"""Shrink index.html for the 256 KB page document: drop indentation, blank lines and whole-line comments."""
import re, json
B = '/home/claude/wedger/rh/'
t = open(B + 'index.html').read()
out, mode = [], 'html'
for line in t.split('\n'):
    s = line.strip()
    if s.startswith('<style'): mode = 'css'
    if s.startswith('<script'): mode = 'js'
    if not s: continue
    if mode == 'css' and re.fullmatch(r'/\*.*\*/', s): continue
    if mode == 'js' and s.startswith('//'): continue
    if mode == 'html' and re.fullmatch(r'<!--(?!CAT).*-->', s): continue
    out.append(s)
    if s.startswith('</style'): mode = 'html'
    if s.startswith('</script'): mode = 'html'
m = '\n'.join(out)
open(B + 'index.html', 'w').write(m)
doc = json.dumps({'text': m}, ensure_ascii=False)
print('chars', len(m), 'utf8', len(m.encode()), 'doc bytes', len(doc.encode()))
json.dump({'text': m}, open(B + 'index_doc.json', 'w'), ensure_ascii=False)
