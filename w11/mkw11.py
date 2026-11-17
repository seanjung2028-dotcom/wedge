"""Make the Week 11 copies of the Week 10 pipeline scripts: same code, week numbers and file names moved on by one.
Special cases are patched below the generic replacements."""
import re, sys
W = '/home/claude/wedger/'
PAIRS = [('w10/build_inj.py', 'w11/build_inj.py'), ('w10/build_inputs.py', 'w11/build_inputs.py'), ('mom/pg_next_w10.py', 'mom/pg_next_w11.py'),
         ('arch/build_feat_w10.py', 'arch/build_feat_w11.py'), ('arch/now_w10.py', 'arch/now_w11.py'), ('arch/defadj_w10.py', 'arch/defadj_w11.py'),
         ('bt/rff_w10.py', 'bt/rff_w11.py'), ('v2/data_v2_w10.py', 'v2/data_v2_w11.py')] + \
        [(f'rh/w10_{n}.py', f'rh/w11_{n}.py') for n in ('events', 'analyze', 'build_inband', 'categorize', 'atd', 'keep_certs', 'totals', 'splits', 'matchup',
                                                         'reads_cand', 'model', 'proj_exp', 'build_all', 'injflags', 'game_reads')]
def gen(t):
    t = re.sub(r"(week'\]|\.week|\bweek|\bwk)(\s*)(<=|>)(\s*)9\b", r'\1\2\3\g<4>10', t)
    t = re.sub(r"(week'\]|\.week|\bweek|\bwk)(\s*)(==)(\s*)10\b", r'\1\2\3\g<4>11', t)
    t = re.sub(r"(week'\]|\.week|\bweek|\bwk)(\s*)(<)(\s*)10\b", r'\1\2\3\g<4>11', t)
    t = t.replace("'week': 10,", "'week': 11,").replace("'week'] = 10", "'week'] = 11").replace("['week'] = 10", "['week'] = 11")
    t = t.replace('thru9', 'thru10').replace('pull1116', 'pull1117').replace('espn_inj_1116', 'espn_inj_1117')
    t = t.replace('w10', 'w11').replace('W10', 'W11').replace('Week 10', 'Week 11').replace('week-10', 'week-11')
    return t
for a, b in PAIRS:
    t = gen(open(W + a).read())
    open(W + b, 'w').write(t)
print('generated', len(PAIRS))
