"""Split the minified page for the Dashboard store: files/index.html = markup + CSS + <script src="wg.js">, files/wg.js = the script (+ NBA backtest data)."""
import re, json, sys
B = '/home/claude/wedger/'
t = open(B + 'rh/index_min.html').read()
m = re.search(r'<script type="application/json" id="nbt-data">([\s\S]*?)</script>', t); nbt = m.group(1) if m else 'null'
if m: t = t.replace(m.group(0), '')
scripts = re.findall(r'<script>([\s\S]*?)</script>', t); assert len(scripts) == 1
js = 'window.WG_NBT=' + nbt + ';\n' + scripts[0]
page = t.replace('<script>' + scripts[0] + '</script>', '<script src="final.js"></script><script src="wg.js"></script>')
# styles go to their own file (files/wg.css) so the page stays under the store's 256 KB per document
styles = re.findall(r'<style>([\s\S]*?)</style>', page)
css = '\n'.join(styles)
first = True
for st in styles:
    page = page.replace('<style>' + st + '</style>', '<link rel="stylesheet" href="wg.css">' if first else '', 1); first = False
open(B + 'rh/wg.css', 'w').write(css)
json.dump({'text': css}, open(B + 'dbw/wg_css_doc.json', 'w'), ensure_ascii=False)
open(B + 'rh/wg.js', 'w').write(js); open(B + 'rh/index_page.html', 'w').write(page)
json.dump({'text': page}, open(B + 'dbw/index_doc_w9.json', 'w'), ensure_ascii=False)
json.dump({'text': js}, open(B + 'dbw/wg_doc.json', 'w'), ensure_ascii=False)
for n, x in (('index.html', page), ('wg.js', js), ('wg.css', css)):
    print(n, 'bytes', len(x.encode()), 'doc', len(json.dumps({'text': x}, ensure_ascii=False).encode()))
# runtime emulation for the harness: scripts removed from markup, wg.js run after
open(B + 'rh/index_split_test.html', 'w').write(page.replace('<link rel="stylesheet" href="wg.css">', '<style>' + css + '</style>').replace('<script src="final.js"></script><script src="wg.js"></script>', '') + '<script>' + open(B + 'rh/final.js').read() + '</script><script>' + js + '</script>')
