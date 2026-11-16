import sys, json
sys.argv.append('probe')
exec(open('/home/claude/wedger/rh/w7_splits.py').read())
import csv
S = {r['key']: json.loads(r['detail']) for r in csv.DictReader(open(B + 'sit_w7.csv'))}
byname = {d['p']: d for d in S.values()}
for name, stat, line in [('Puka Nacua', 'recyd', 99.5), ('Puka Nacua', 'recyd', 94.5), ('Puka Nacua', 'rec', 7.5), ('Luther Burden III', 'recyd', 59.5), ('Matthew Stafford', 'passyd', 249.5), ('Jahmyr Gibbs', 'td', 0.5)]:
    d = byname[name]; sc = scenarios(d, stat, line)
    print(name, stat, line, 'P=%.3f proj=%.1f n=%d cuts %s-%s %s' % (sc['p'], sc['proj'], sc['n'], sc['a'], sc['b'], sc['unit']))
    for k, t, w in zip(('bear', 'base', 'bull'), sc['tiers'], sc['w']):
        print('   %s n=%d h=%d p=%.3f m=%s share=%.2f w=%.3f' % (k, t['n'], t['h'], t['p'], None if t['m'] is None else round(t['m'], 1), t['share'], w))
