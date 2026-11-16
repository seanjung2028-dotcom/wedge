set -e
cd /home/claude/wedger/rh
python3 patch_w8_page.py >/dev/null && python3 patch_w8_js.py >/dev/null && python3 patch_w8b.py >/dev/null && python3 patch_w8c.py >/dev/null && python3 patch_w8d.py >/dev/null && python3 patch_w8f.py >/dev/null && python3 patch_w9.py && python3 patch_w9b.py && python3 patch_wedge.py && python3 gen_page.py >/dev/null && python3 -c "p='index.html';s=open(p).read();open(p,'w').write(s.replace('Wedger','Wedge'))" && python3 patch_w9c.py && python3 patch_w9d.py && python3 patch_w9e.py && python3 patch_w9f.py && python3 patch_w9g.py && python3 patch_w9h.py
cp index.html index_full.html && node esmin.js index_full.html index_min.html >/dev/null && python3 split_page.py
python3 - <<'PY'
import json
S='/home/claude/wedger/'
files={'index.html':json.load(open(S+'dbw/index_doc_w9.json'))['text'],'wg.js':json.load(open(S+'dbw/wg_doc.json'))['text'],'wg.css':json.load(open(S+'dbw/wg_css_doc.json'))['text'],'final.js':json.load(open(S+'dbw/final_js_doc.json'))['text']}
t=open(S+'rh/index_emu.html').read()
i=t.index('new Map(Object.entries(')+len('new Map(Object.entries('); j=t.index('));\nconst S95')
open(S+'rh/index_emu.html','w').write(t[:i]+json.dumps(files).replace('</','<\\/')+t[j:])
PY
cd .. && python3 harness/build.py $PWD/rh/ harness/w8/emu.html light owner index_emu.html && python3 harness/build.py $PWD/rh/ harness/w8/emu_dark.html dark none index_emu.html
