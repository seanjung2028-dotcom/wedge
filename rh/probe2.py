import csv, json, sys
S = {r['player']: json.loads(r['detail']) for r in csv.DictReader(open('sit_w7.csv'))}
COL = {'rec': [4], 'recyd': [5], 'rushyd': [6], 'rryd': [5, 6], 'passyd': [7], 'passtd': [8], 'int': [9], 'td': [10], 'tgt':[13]}
def vals(d, idx, stat): return [sum(d['log'][i][c] for c in COL[stat]) for i in idx]
def summ(d, idx, stat, line):
    v=vals(d, idx, stat); t=vals(d, idx, 'tgt')
    return f"{sum(1 for x in v if x>line)}/{len(v)} ({100*sum(1 for x in v if x>line)/len(v):.0f}%) avg {sum(v)/len(v):.1f} tgt {sum(t)/len(t):.1f}" if v else '0/0'
def show(name, stat, line):
    d = S[name]; print('=====', name, stat, line, d['seasons'], 'games', len(d['log']), 'base', len(d['base']))
    lab = lambda i: f"'{d['log'][i][0]} W{d['log'][i][1]} {d['log'][i][2]} {sum(d['log'][i][c] for c in COL[stat])}/{d['log'][i][13]}t s{d['log'][i][3]} {d['names'][d['log'][i][11]] if d['log'][i][11] is not None else '-'}{d['log'][i][12]}"
    print('excluded:', [lab(i) for i,r in enumerate(d['log']) if r[12]])
    print('all:', summ(d, d['base'], stat, line))
    for s in d['sets']:
        print(f"[{s['k']}] {s['label']} | pool={s['pool']}: {summ(d, s['idx'], stat, line)}")
        if 'alt' in s: print('    alt', s['alt']['label'], summ(d, s['alt']['idx'], stat, line))
        if s.get('skipped'): print('    skipped', [lab(i) for i in s['skipped']])
        if s['k'] in ('comp',) or (s['k']=='qb' and len(s['alt']['idx'])<6): print('    match', [lab(i) for i in s['idx']][:12], '| alt', [lab(i) for i in s['alt']['idx']][:10])
show(sys.argv[1], sys.argv[2], float(sys.argv[3]))
