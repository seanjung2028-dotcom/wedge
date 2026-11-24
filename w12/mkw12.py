"""Make the Week 12 copies of the Week 11 pipeline scripts (Tue Nov 24): same code, week numbers and file names moved on by
one. Data now come from nfl12/ (nflverse through Week 11, Monday night included; dl18 and dl19 point there). Special cases are
patched by hand after this runs."""
import re, shutil, os
W = '/home/claude/wedger/'
PAIRS = [('w11/build_inj.py', 'w12/build_inj.py'), ('w11/build_inputs.py', 'w12/build_inputs.py'), ('w11/run_chain.sh', 'w12/run_chain.sh'),
         ('mom/pg_next_w11.py', 'mom/pg_next_w12.py'), ('arch/build_feat_w11.py', 'arch/build_feat_w12.py'), ('arch/now_w11.py', 'arch/now_w12.py'),
         ('arch/defadj_w11.py', 'arch/defadj_w12.py'), ('bt/rff_w11.py', 'bt/rff_w12.py'), ('v2/data_v2_w11.py', 'v2/data_v2_w12.py'),
         ('final11/build.py', 'final12/build.py'), ('final11/brain_layer.py', 'final12/brain_layer.py'), ('final11/book_ladders.py', 'final12/book_ladders.py'),
         ('final11/make_final_js.py', 'final12/make_final_js.py')] + \
        [(f'rh/w11_{n}.py', f'rh/w12_{n}.py') for n in ('events', 'analyze', 'build_inband', 'categorize', 'atd', 'keep_certs', 'totals', 'splits', 'matchup',
                                                         'reads_cand', 'model', 'proj_exp', 'build_all', 'injflags', 'game_reads')]
def gen(t):
    t = re.sub(r"(week'\]|\.week|\bweek|\bwk)(\s*)(<=|>)(\s*)10\b", r'\1\2\3\g<4>11', t)
    t = re.sub(r"(week'\]|\.week|\bweek|\bwk)(\s*)(==)(\s*)11\b", r'\1\2\3\g<4>12', t)
    t = re.sub(r"(week'\]|\.week|\bweek|\bwk)(\s*)(<)(\s*)11\b", r'\1\2\3\g<4>12', t)
    t = t.replace("'week': 11,", "'week': 12,").replace("'week'] = 11", "'week'] = 12").replace("['week'] = 11", "['week'] = 12")
    t = t.replace('v6.tables(11)', 'v6.tables(12)').replace('lens_block(a, h, 11,', 'lens_block(a, h, 12,')
    t = t.replace('thru10', 'thru11').replace('pull1117pm', 'pull1124').replace('pull1117', 'pull1124').replace('espn_inj_1117', 'espn_inj_1124')
    t = t.replace('final11', 'final12').replace('w11', 'w12').replace('W11', 'W12').replace('Week 11', 'Week 12').replace('week-11', 'week-12')
    return t
for a, b in PAIRS:
    open(W + b, 'w').write(gen(open(W + a).read()))
print('generated', len(PAIRS))
