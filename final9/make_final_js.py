import json
B = '/home/claude/wedger/'
F = json.load(open(B + 'final9/final_w9.json'))
js = 'window.WZ_FINAL=' + json.dumps(F, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ';\n'
open(B + 'rh/final.js', 'w').write(js)
json.dump({'text': js}, open(B + 'dbw/final_js_doc.json', 'w'), ensure_ascii=False)
print('final.js bytes', len(js.encode()), 'doc', len(json.dumps({'text': js}, ensure_ascii=False).encode()))
