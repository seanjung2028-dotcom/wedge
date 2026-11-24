import json
B = '/home/claude/wedger/'
F = json.load(open(B + 'final12/final_w12.json'))
js = 'window.WZ_FINAL=' + json.dumps(F, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ';\n'
open(B + 'rh/final.js', 'w').write(js)
print('final.js bytes', len(js.encode()), 'doc', len(json.dumps({'text': js}, ensure_ascii=False).encode()))
BR = json.load(open(B + 'final12/brain_w12.json'))
bj = 'window.WZ_BRAIN=' + json.dumps(BR, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + ';\n'
open(B + 'rh/brain.js', 'w').write(bj)
print('brain.js bytes', len(bj.encode()), 'doc', len(json.dumps({'text': bj}, ensure_ascii=False).encode()))
