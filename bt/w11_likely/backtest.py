"""Week 11 test of the revised master prompt (Mon Nov 23): rank every executable Kalshi rung by its chance of settling Yes/No
(Wedge %, low end of the range first), price second, against the card as posted (ranked by edge over the price).
Board: Sun Nov 22 10:32 AM CT (the final draft). Results: nflverse stats + snap counts (dl23). Sunday games only
(Thursday was graded from its own card; Monday night is still to play). Writes bt/w11_likely/rows.csv and summary.json."""
import json, re, sys, collections, math
import pandas as pd
W = '/home/claude/wedger/'
src = open(W + 'final11/build.py').read(); src = src[:src.index('# --- write-ups')]
G = {'__name__': 'bt'}; exec(compile(src, 'build_head', 'exec'), G)
res, BR, WORD = G['res'], G['BR'], G['WORD']
gr = open(W + 'bt/w11_grade/grade.py').read(); gr = gr[:gr.index('SER = {')]
GG = {}; exec(compile(gr, 'grade_head', 'exec'), GG)
def thr(x, stat): return (f"{x['k']}+ " if x['side'] == 'Yes' else f"under {x['k']} ") + WORD[stat]
STW = {'rushyd': 'rushing yards', 'rec': 'receptions', 'recyd': 'receiving yards', 'rryd': 'rush + receiving yards'}
rows = []
for game, L in res.items():
    if game in ('IND @ HOU',): continue
    for o in L:
        if o['early']: continue
        for x in o['rows']:
            line = f"{o['name']} {thr(x, o['stat'])} ({x['side']})"
            rs = BR.RESEARCH.get((game, line)) or BR.RESEARCH_PLAYER.get((game, o['name'], x['side']))
            c = x['chk']
            gtxt = f"{o['name']} " + (f"{x['k']}+ " if x['side'] == 'Yes' else f"under {x['k']} ") + STW[o['stat']] + f" ({x['side']})"
            g_ = GG['grade'](game, gtxt, x['ask'])
            rows.append(dict(game=game, player=o['name'], stat=o['stat'], k=x['k'], side=x['side'], line=line, ask=x['ask'], be=x['be'], lo=x['lo'], mid=x['mid'], hi=x['hi'],
                             mkt=x['mkt'], edge_lo=x['edge_lo'], edge_mid=x['edge_mid'], call=x['call'],
                             qb=c['QB']['pass'], role=c['ROLE']['pass'], script=c['SCRIPT']['pass'], log=c['LOG']['pass'], late=c['LATE']['pass'],
                             log_hits=c['LOG']['hits'], log_n=c['LOG']['n'], research_pass=bool(rs and rs.get('decision') == 'Pass'),
                             result=g_['result'] if g_ else None, pl_c=g_['pl_c'] if g_ else None))
D = pd.DataFrame(rows); D.to_csv(W + 'bt/w11_likely/rows.csv', index=False)
D['checks'] = D.qb & D.role & D.script & D.late & ~D.research_pass
S = D[D.result.isin(['Won', 'Lost'])].copy()
def card(df, key, n=None, per_game=4):
    """one line per player, up to per_game a game, best key first; n = slate size (None = all that qualify)"""
    df = df.sort_values(key, ascending=False)
    seen, pg, out = set(), collections.Counter(), []
    for r in df.itertuples(index=False):
        if r.player in seen or pg[r.game] >= per_game: continue
        seen.add(r.player); pg[r.game] += 1; out.append(r)
        if n and len(out) >= n: break
    return pd.DataFrame(out)
def summ(c):
    if not len(c): return {'n': 0}
    w = int((c.result == 'Won').sum()); n = len(c)
    return {'n': n, 'won': w, 'lost': n - w, 'hit': round(100 * w / n, 1), 'profit_c': int(c.pl_c.sum()), 'avg_price': round(c.ask.mean(), 1), 'avg_ours_lo': round(c.lo.mean(), 1), 'avg_ours_mid': round(c.mid.mean(), 1)}
OUT = {}
el = S[S.checks]
OUT['as posted: edge first (finals + leans, Sunday games)'] = summ(S[S.call.isin(['Final line', 'Conditional lean'])])
for cap in (96, 90, 85, 80, 75, 70):
    e = el[el.ask <= cap].copy(); e['key'] = e.lo + e.mid / 1000
    OUT[f'chance first, price cap {cap}c, top 18'] = summ(card(e, 'key', 18))
e = el[el.mid >= el.be].copy(); e['key'] = e.lo + e.mid / 1000
OUT['chance first, only where ours >= needs, top 18'] = summ(card(e, 'key', 18))
OUT['chance first, only where ours >= needs, all that qualify'] = summ(card(e, 'key'))
# calibration of the number at the high end: does a 90% rung hit 90%?
S['band'] = pd.cut(S.mid, [0, 50, 60, 70, 80, 90, 100])
cal = S[S.checks].groupby('band', observed=True).agg(n=('result', 'size'), won=('result', lambda s: (s == 'Won').sum()), ours=('mid', 'mean'), price=('ask', 'mean'), pl=('pl_c', 'sum'))
cal['hit'] = (100 * cal.won / cal.n).round(1)
OUT['calibration (lines passing the checks, by our number)'] = {str(k): {kk: (round(float(v), 1) if isinstance(v, float) else int(v)) for kk, v in r.items()} for k, r in cal.iterrows()}
json.dump(OUT, open(W + 'bt/w11_likely/summary.json', 'w'), indent=1)
print(json.dumps(OUT, indent=1))
print('rows', len(D), 'graded', len(S), 'passing checks', int(S.checks.sum()))
for cap in (96, 85, 75):
    e = el[el.ask <= cap].copy(); e['key'] = e.lo + e.mid / 1000
    print(f'--- top 18, cap {cap}'); print(card(e, 'key', 18)[['game', 'line', 'ask', 'lo', 'mid', 'result', 'pl_c']].to_string(index=False))
