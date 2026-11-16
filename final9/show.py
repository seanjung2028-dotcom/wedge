import json, sys, pandas as pd, statistics as st
S = '/home/claude/wedger/'
T = json.load(open(S + 'final9/team.json')); U = json.load(open(S + 'final9/usage.json'))
X = json.load(open(S + 'final9/an_extra.json')); AN = json.load(open(S + 'rh/an_w9_raw.json'))
W = json.load(open(S + 'w9/weather_w9.json'))
LA = pd.read_csv(S + 'rh/lines_all_w9.csv', low_memory=False)
INJ = pd.read_csv(S + 'dl8/injuries_w9.csv', low_memory=False)
MAP = {'LA': 'LAR', 'WAS': 'WSH'}
g = sys.argv[1]; a, h = g.split('@'); gl = f"{MAP.get(a, a)} @ {MAP.get(h, h)}"
def team(t, o):
    x = T[t]; y = T[o]
    print(f"{t} O: g{x['g']} pf {x['pf']} att {x['att']} cmp {x['cmp']} sk {x['sk']} rush {x['rush']} drv {x['drives']} ppd {x['ppd']} neuPass {x['neu_pass']}% 3rd {x['third']}% PA {x['pa_rate']}% oop {x['oop']}% | att by script {x['att_by_script']}")
    print(f"   logs: {' | '.join(x['logs'])}")
    print(f"{o} D vs: pa {y['pa']} oppAtt {y['d_att']} sk {y['d_sk']} oppRush {y['d_rush']} ypc {y['d_ypc']} blitz {y['d_blitz']}% rushers {y['d_rushers']} oopForced {y['d_oop']}% box {y['d_box']} QBrushYds/g {y['d_qbrush']} scr/g {y['d_scr']} 20+pass/g {y['d_exp']} tgtAllowed {y['d_tg']}")
    for p in U[t][:9]:
        print(f"   {p['pos']} {p['name']}: g{p['g']} tgt {p['tgt']} ({p['ts']}%) rec {p['rec']} ryd {p['recyd']} | car {p['car']} ({p['cs']}%) rush {p['rushyd']}" + (f" | att {p['att']} pyd {p['pyd']}" if p['pos'] == 'QB' else '') + f" || {p['l3']}")
print('=====', g, '| weather', W.get(f'{a}@{h}') or W.get(gl.replace(' ', '')))
for r in X['gl']:
    if r[0] == g: print('consensus spread', r[1], 'total', r[2], 'ML', r[3], '@', X['at'])
for r in X['rows']:
    if r[1] == g and r[0] in ('Pass Attempts', 'Completions', 'Rush Attempts'):
        ls = [b[1] for b in r[5] if b[1] is not None]; print('  ', r[0], r[2], r[3], st.median(ls) if ls else None, [b for b in r[5] if b[0] == 15])
team(a, h); team(h, a)
inj = INJ[INJ.team.isin([a, h, MAP.get(a, a), MAP.get(h, h)]) & INJ.report_status.isin(['Out', 'Doubtful', 'Questionable']) & (INJ.week == 9)]
print('INJ:', '; '.join(f"{r.team} {r.full_name} {r.position} {r.report_status}" for r in inj.itertuples()))
L = LA[(LA.game == gl) & (LA.source == 'Robinhood')]
gm = L[L.market.isin(['Spreads', 'Totals', 'Moneyline'])]
print('RH game lines 35-65c:', '; '.join(f"{r.contract} {int(r.yes_price)}/{'' if pd.isna(r.no_price) else int(r.no_price)}" for r in gm.itertuples() if 35 <= r.yes_price <= 65))
