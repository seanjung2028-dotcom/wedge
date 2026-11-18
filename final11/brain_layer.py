"""The research method layered on the v6 card: QB eligibility, research checks per exact line, the evidence chain,
alternatives, objections and card-level interaction. Used by final11/build.py (Week 11)."""
import json, math, sys
import numpy as np, pandas as pd
W = '/home/claude/wedger/'
sys.path.insert(0, W + 'brain'); import gates
INJ_URL = 'https://www.espn.com/nfl/injuries'
# ---- this slate's rule: no game where either team starts a backup quarterback (checked Tue Nov 17 ~6:30 AM CT, ESPN injury report blurbs)
QB = {
    'IND @ HOU': (True, 'Daniel Jones (IND) and C.J. Stroud (HOU) start; neither is on the injury report (ESPN, Tue Nov 17).'),
    # Wed Nov 18 (ESPN injury report, 1:52 PM CT), same rule as Week 10: a replacement starter for an injured starter leaves the game off
    'TEN @ DAL': (True, 'Cam Ward (TEN) and Dak Prescott (DAL) start; neither is on the injury report (ESPN, Wed Nov 18).'),
    'CIN @ WSH': (True, 'Joe Burrow (CIN) and Jayden Daniels (WSH) start; neither is on the injury report (ESPN, Wed Nov 18).'),
    'TB @ DET': (True, 'Jared Goff (DET) starts. Baker Mayfield (TB, foot) is questionable after missing Wednesday’s practice (Todd Bowles, via ESPN): the game stays on only if he starts.'),
    'NYJ @ LAC': (True, 'Justin Herbert (LAC) starts. Geno Smith (NYJ, ankle) is questionable and was limited Wednesday (Aaron Glenn, via ESPN): the game stays on only if he starts.'),
    'MIA @ BUF': (False, 'Miami starts a backup: Malik Willis (abdomen) is on injured reserve (ESPN, Wed Nov 18); Kyle McCord started in his place in Week 10.'),
    'MIN @ SF': (False, 'Minnesota starts Kirk Cousins again: Kyler Murray (hamstring) is out and missed Wednesday’s practice (Kevin Seifert, ESPN).'),
    'LV @ DEN': (True, 'Fernando Mendoza, named the Raiders’ starter last week, makes his second start; Denver’s starter is not on the injury report (ESPN, Wed Nov 18).'),
    'ARI @ KC': (False, 'Arizona starts Carson Beck: Gardner Minshew (elbow) had season-ending surgery and is on injured reserve (ESPN, Wed Nov 18).'),
    'BAL @ CAR': (False, 'Baltimore starts a backup: Lamar Jackson (thumb) is on injured reserve (ESPN, Wed Nov 18), with a Week 16 return the hope.'),
}
OVERS_NOTE = 'In testing, the model’s overs that passed these same checks broke even (36 picks, Weeks 7–9), while its unders won in each week.'
RATIO = 3   # preferred mix on the card: about one under for every three overs, for finals and for leans
CTX = None
def ctx():
    global CTX
    if CTX is None:
        st = pd.read_csv(W + 'dl19/stats_player_week_2026.csv', low_memory=False)
        pbp = pd.read_csv(W + 'dl19/play_by_play_2026.csv.gz', low_memory=False, usecols=['week', 'qtr', 'rusher_player_id', 'receiver_player_id', 'rushing_yards', 'receiving_yards'])
        games = pd.read_csv(W + 'dl19/games.csv')
        CTX = gates.Ctx(st, pbp, games, 11)
    return CTX
UN = {'LAR': 'LA', 'WSH': 'WAS'}
def un(t): return UN.get(t, t)
def run_checks(game, pid, team, stat, k, side, exp_margin):
    ok, note = QB.get(game, (True, ''))
    return gates.check(ctx(), pid, un(team), stat, k, side, exp_margin, ok, note)
def decide(x):
    """value + checks -> call and the reason a line stops short."""
    c = x['chk']; vf = x['edge_lo'] >= 0.5; vl = x['edge_mid'] >= 0.5
    fails = [n for n in ('ROLE', 'SCRIPT', 'LATE') if not c[n]['pass']]
    if not c['QB']['pass']: return 'Pass', 'Game left off: a backup quarterback starts.'
    if fails and vl: return 'Pass', 'Clears on price but fails ' + ', '.join(LBL[f].lower() for f in fails) + '.'
    if vf: return 'Final line', ''
    if vl: return 'Conditional lean', ''
    return 'Pass', ''
LBL = {'QB': 'Quarterbacks', 'ROLE': 'Role check', 'SCRIPT': 'Game-script check', 'LOG': 'Full game log', 'LATE': 'Late-work check'}
ordn = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
def tier(mid):
    return 'High' if mid >= 65 else ('Solid' if mid >= 57 else ('Lean' if mid >= 50 else 'Long shot'))
SCR = {'control': 'his team won by 8+', 'close': 'one-score games', 'trail': 'his team lost by 8+'}
def check_rows(x, o, word):
    c = x['chk']; out = []
    out.append({'k': LBL['QB'], 'ok': c['QB']['pass'], 't': c['QB']['note']})
    r = c['ROLE'].get('data')
    if r:
        unit = 'carries' if r['col'] == 'carries' else 'targets'
        t = (f"{100 * r['last3_share']:.0f}% of {o['team']}’s {unit} over the last 3 games ({100 * r['season_share']:.0f}% on the season), "
             f"{r['last3_median']:g} a game; played {r['played_last3']} of the last 3.")
        t += (' The role is holding.' if c['ROLE']['pass'] else ' The role is shrinking or he missed time.') if x['side'] == 'Yes' else \
             (' The role is not growing.' if c['ROLE']['pass'] else ' His role is growing, which works against an under.')
    else: t = 'No 2026 role with this team to measure.'
    out.append({'k': LBL['ROLE'], 'ok': c['ROLE']['pass'], 't': t})
    s = c['SCRIPT']; bk = s['buckets']
    parts = [f"{SCR[b]}: {bk[b][0]}/{bk[b][1]}" for b in ('control', 'close', 'trail') if b in bk]
    t = f"The spread points to {('a game ' + o['team'] + ' controls') if s['likely'] == 'control' else ('a game ' + o['team'] + ' chases' if s['likely'] == 'trail' else 'a one-score game')}. " + \
        (f"Cleared by game result: {'; '.join(parts)}." if parts else 'No games to split.') + (f" Thin sample in {', '.join(SCR[b] for b in s['thin'])}." if s['thin'] else '')
    out.append({'k': LBL['SCRIPT'], 'ok': s['pass'], 't': t})
    L = c['LOG']; out.append({'k': LBL['LOG'], 'ok': L['pass'], 't': f"Cleared in {L['hits']} of {L['n']} games with {o['team']} at this exact number (misses included).", 'info': True})
    q = c['LATE']['q4_share']
    out.append({'k': LBL['LATE'], 'ok': c['LATE']['pass'], 't': ('Not a factor for an under.' if x['side'] == 'No' else
               (f"{100 * q:.0f}% of his {word} came in fourth quarters." if q is not None else 'No fourth-quarter split available.'))})
    return out
def chain(x, o, T, rank):
    """defense concession -> offense ability -> deployment -> what the exact number needs"""
    D = T.D.loc[o['opp']]; r = x['chk']['ROLE'].get('data') or {}; st = o['stat']; k = x['k']; under = x['side'] == 'No'
    logs = [v for _, v, *_ in ctx().logs(o['pid'], un(o['team']), st) if True]
    S = ctx().s; me = S[(S.player_id == o['pid']) & (S.team == un(o['team']))]
    if st in ('rushyd', 'rryd'):
        inn = float(T.O.in_share.get(o['team'], 0.6)) if hasattr(T.O, 'in_share') else 0.6
        con = f"{o['opp']} allows {D.ypc:.2f} yards a carry ({rank('ypc', o['opp'])}) and {D.rush_yds:.0f} rushing yards a game: {D.ypc_in:.2f} inside, {D.ypc_out:.2f} outside."
        ex = f"{o['team']} runs inside {100 * inn:.0f}% of the time and has run {r.get('team_last3_per_game', 0):g} times a game over its last 3."
        car = r.get('last3_median', 0) or 0
        ypc = float(me.rushing_yards.sum() / me.carries.sum()) if me.carries.sum() else 0
        dep = f"{o['name']} takes {100 * r.get('last3_share', 0):.0f}% of those carries lately ({car:g} a game)."
        need = (f"{k} yards on {car:g} carries needs {k / car:.1f} a carry; he averages {ypc:.1f} this season." if car else f"He has no recent carries to project {k} yards from.")
        if under: need = f"Staying under {k} means {k - 1} or fewer: at {ypc:.1f} a carry that is about {max(0, (k - 1) / ypc if ypc else 0):.0f} carries or fewer; he has had {car:g} a game lately."
    else:
        pos = T.pos.get(o['pid'], ''); b = 'TE' if pos == 'TE' else ('RB' if pos in ('RB', 'FB') else 'WR')
        con = f"{o['opp']} allows {D[b + '_rec']:.1f} catches and {D[b + '_yds']:.0f} yards a game to {b}s ({rank(b + '_yds', o['opp'])}), and faces {D.pass_att:.0f} passes a game."
        ex = f"{o['team']} has thrown {r.get('team_last3_per_game', 0):g} targets a game over its last 3; {o['opp']} sends {100 * D['sh_' + ('WRm' if b == 'WR' else b)]:.0f}% of the targets it allows to {'middle WRs' if b == 'WR' else b + 's'}."
        tg = r.get('last3_median', 0) or 0
        dep = f"{o['name']} draws {100 * r.get('last3_share', 0):.0f}% of the targets lately ({tg:g} a game)."
        cr = float(me.receptions.sum() / me.targets.sum()) if me.targets.sum() else 0; ypt = float(me.receiving_yards.sum() / me.targets.sum()) if me.targets.sum() else 0
        if st == 'rec': need = (f"{k} catches on {tg:g} targets needs a {100 * k / tg:.0f}% catch rate; he catches {100 * cr:.0f}%." if tg else 'No recent targets to project from.')
        else: need = (f"{k} yards on {tg:g} targets needs {k / tg:.1f} a target; he averages {ypt:.1f}." if tg else 'No recent targets to project from.')
        if under: need = 'For the under: ' + need[0].lower() + need[1:]
    return [{'k': 'What the defense allows', 't': con}, {'k': 'Can this offense get there', 't': ex}, {'k': 'Is he the one who gets it', 't': dep}, {'k': 'What the exact number needs', 't': need}]
def committee(o):
    """the teammate taking the most of the same work (carries or targets), last 3 games"""
    S = ctx().s; col = 'carries' if o['stat'] in ('rushyd', 'rryd') else 'targets'; t = un(o['team'])
    wks = sorted(S[S.team == t].week.unique())[-3:]
    d = S[(S.team == t) & S.week.isin(wks)].groupby(['player_id', 'player_display_name'])[col].sum().sort_values(ascending=False)
    tot = d.sum() or 1
    for (pid, nm), v in d.items():
        if pid != o['pid'] and (col == 'targets' or True): return nm, v / tot
    return None, 0
def objection(x, o, word):
    c = x['chk']; nm, sh = committee(o)
    if o['status'] == 'Questionable': return f"{o['name']} is questionable; if he is limited, the work goes elsewhere."
    bk = c['SCRIPT']['buckets']; worst = sorted([(v[0] / v[1], b) for b, v in bk.items() if v[1] >= 2])
    if x['side'] == 'Yes' and nm and sh >= 0.25: return f"{nm} takes {100 * sh:.0f}% of the same work; a hot hand there caps his share."
    if worst and worst[0][0] < 0.5: return f"In games where {SCR[worst[0][1]]}, this side cleared only {bk[worst[0][1]][0]} of {bk[worst[0][1]][1]}."
    neg = [l for l in x.get('_lens', []) if l['pts'] < 0]
    if neg: return neg[0]['text']
    if x['side'] == 'Yes': return OVERS_NOTE
    return 'No single factor stands out against it; the risk is ordinary game-to-game spread.'
def miss_path(x, o):
    nm, sh = committee(o); k = x['k']
    if o['stat'] in ('rushyd', 'rryd'):
        if x['side'] == 'Yes': return f"{o['team']} runs well, but the carries split{(' with ' + nm) if nm else ''} or an early lead hands the fourth quarter to the backups."
        if (ctx().role(o['pid'], un(o['team']), o['stat']) or {}).get('season_share', 0) < 0.2: return f"Pressure flushes him and the scrambles add up to {k}+ even if designed runs stay quiet."
        return f"{o['team']} gets ahead and leans on him to close it out; clock-killing carries push him to {k}+."
    if x['side'] == 'Yes': return f"The matchup opens, but the targets go to {nm or 'a teammate'}{(' (' + str(round(100 * sh)) + '% share lately)') if nm else ''}."
    return f"The defense takes away the deep ball and he piles up short catches past {k}."
def change(x, o, cond):
    out = [cond]
    nm, sh = committee(o)
    qb = (ctx().role(o['pid'], un(o['team']), o['stat']) or {}).get('season_share', 1) < 0.2 and o['stat'] in ('rushyd', 'rryd')
    if nm and sh >= 0.2 and not qb: out.append(f"If {nm} is ruled out, his share grows: re-check {'the under' if x['side'] == 'No' else 'the price'}.")
    out.append('A change at quarterback or a late scratch at his position voids the read.')
    return ' '.join(s for s in out if s)
def alts(x, o, all_res, thr, word):
    """nearest same-player rungs, opposite side, other markets for him, and the strongest teammate in the same family"""
    out = []
    same = sorted([y for y in o['rows'] if y['side'] == x['side'] and y['k'] != x['k']], key=lambda y: abs(y['k'] - x['k']))[:2]
    opp = [y for y in o['rows'] if y['side'] != x['side'] and y['k'] == x['k']][:1]
    for y in same + opp:
        why = (f"Fails {', '.join(LBL[n].lower() for n in ('ROLE', 'SCRIPT', 'LATE') if not y['chk'][n]['pass'])}." if not all(y['chk'][n]['pass'] for n in ('ROLE', 'SCRIPT', 'LATE')) else
               ('Ours sits below the price there.' if y['edge_mid'] < 0.5 else ('Clears by less at the low end.' if y['edge_lo'] < x['edge_lo'] else 'Likelier to hit but clears by less after price.')))
        out.append({'line': f"{o['name']} {thr(y, o['stat'])} ({y['side']})", 'ask': y['ask'], 'be': y['be'], 'ours': f"{y['lo']:.0f}–{y['hi']:.0f}%", 'why': why})
    for o2 in all_res:
        if o2 is o: continue
        if o2['name'] == o['name'] or (o2['team'] == o['team'] and ((o2['stat'] in ('rushyd', 'rryd')) == (o['stat'] in ('rushyd', 'rryd')))):
            y = sorted(o2['rows'], key=lambda y: -y['edge_mid'])[0]
            why = ('Same player, other market: ' if o2['name'] == o['name'] else 'Same team, same kind of work: ') + \
                  ('ours sits below the price.' if y['edge_mid'] < 0.5 else (f"fails {', '.join(LBL[n].lower() for n in ('ROLE', 'SCRIPT', 'LATE') if not y['chk'][n]['pass'])}." if not all(y['chk'][n]['pass'] for n in ('ROLE', 'SCRIPT', 'LATE')) else 'clears, but by less.'))
            out.append({'line': f"{o2['name']} {thr(y, o2['stat'])} ({y['side']})", 'ask': y['ask'], 'be': y['be'], 'ours': f"{y['lo']:.0f}–{y['hi']:.0f}%", 'why': why})
            if len(out) >= 5: break
    return out[:5]
def need_state(p):
    """the game state a play needs, and the one that sinks it"""
    rush = p['_stat'] in ('rushyd', 'rryd'); qb = p.get('_qb')
    if rush and not qb: return ('ahead', 'behind') if p['side'] == 'Yes' else ('behind', 'ahead')
    if qb: return ('any', 'pressure')
    return ('behind', 'ahead') if p['side'] == 'Yes' else ('ahead', 'behind')
def interaction(plays):
    out = []
    by = {}
    for p in plays:
        good, bad = need_state(p)
        if bad in ('ahead', 'behind'): by.setdefault((p['_team'], bad), []).append(p['line'])
    for (team, bad), ls in by.items():
        if len(ls) >= 2: out.append(f"{' and '.join(ls)} {'both' if len(ls) == 2 else 'all'} lose if {team} is {'ahead' if bad == 'ahead' else 'behind'} early: treat them as one position, not {len(ls)}.")
    rush_unders = [p['line'] for p in plays if p['_stat'] in ('rushyd', 'rryd') and p['side'] == 'No']
    if len(rush_unders) >= 3: out.append(f"{len(rush_unders)} rushing unders here share one risk: a run-heavy game.")
    return out or ['The lines here don’t share a single failure path.']
# ---- research pass on the finalists (Sat Nov 14, ~8:30 PM CT): news that supports or defeats each line's key assumption
ESPN = {'t': 'ESPN NFL injury report (team and beat-reporter notes), Sat Nov 14', 'u': INJ_URL}
RESEARCH = {   # Week 11 news checks (Tue Nov 17 ~6:40 AM CT). Searches turned up only 2025 coverage of both quarterbacks, which doesn't count.
    ('IND @ HOU', 'C.J. Stroud 10+ rushing yards (Yes)'): {
        'notes': ['ESPN’s injury report (Tue Nov 17) lists Stroud as active with no designation. He ran 3 times for 20 yards in Sunday’s 27–24 loss at Cleveland.',
                  'Thursday game: the first practice reports post Monday through Wednesday. Re-check before kickoff.'],
        'src': [{'t': 'ESPN NFL injuries, Tue Nov 17', 'u': INJ_URL}]},
    ('IND @ HOU', 'Daniel Jones under 15 rushing yards (No)'): {
        'notes': ['ESPN’s injury report (Tue Nov 17) lists Jones as active with no designation. He ran 5 times for 9 yards in Sunday’s 24–22 win over Miami.',
                  'Thursday game: the first practice reports post Monday through Wednesday. Re-check before kickoff.'],
        'src': [{'t': 'ESPN NFL injuries, Tue Nov 17', 'u': INJ_URL}]},
}
