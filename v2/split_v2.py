"""Minified V2 page -> files for the Dashboard store (index.html, wg.css, wg.js, final.js) + an emulator page for the harness."""
import re, json, subprocess
B = '/home/claude/wedger/'; V = B + 'v2/'
subprocess.run(['node', B + 'rh/esmin.js', V + 'index_full.html', V + 'index_min.html'], check=True, capture_output=True)
t = open(V + 'index_min.html').read()
m = re.search(r'<script type="application/json" id="nbt-data">([\s\S]*?)</script>', t); nbt = m.group(1) if m else 'null'
if m: t = t.replace(m.group(0), '')
scripts = re.findall(r'<script>([\s\S]*?)</script>', t); assert len(scripts) == 1, len(scripts)
js = 'window.WG_NBT=' + nbt + ';\n' + scripts[0]
page = t.replace('<script>' + scripts[0] + '</script>', '<script src="final.js"></script><script src="brain.js"></script><script src="wg.js"></script>')
styles = re.findall(r'<style>([\s\S]*?)</style>', page)
css = '\n'.join(styles); first = True
for st in styles:
    page = page.replace('<style>' + st + '</style>', '<link rel="stylesheet" href="wg.css">' if first else '', 1); first = False
final = open(B + 'rh/final.js').read()
import os; os.makedirs(V + 'out', exist_ok=True); os.makedirs(V + 'db', exist_ok=True)
files = {'index.html': page, 'wg.js': js, 'wg.css': css, 'final.js': final, 'brain.js': open(B + 'rh/brain.js').read()}
for n, x in files.items():
    open(V + 'out/' + n, 'w').write(x)
    json.dump({'text': x}, open(V + 'db/' + n.replace('.', '_') + '.json', 'w'), ensure_ascii=False)
    print(n, 'bytes', len(x.encode()), 'doc', len(json.dumps({'text': x}, ensure_ascii=False).encode()))
if not os.path.exists(B + 'rh/index_emu.html'): print('no emulator template; skipped index_emu.html'); raise SystemExit
tpl = open(B + 'rh/index_emu.html').read()
i = tpl.index('new Map(Object.entries(') + len('new Map(Object.entries('); j = tpl.index('));\nconst S95')
open(V + 'index_emu.html', 'w').write(tpl[:i] + json.dumps(files).replace('</', '<\\/') + tpl[j:])
