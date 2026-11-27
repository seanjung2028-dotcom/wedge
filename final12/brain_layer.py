"""The research method layered on the v6 card: QB eligibility, research checks per exact line, the evidence chain,
alternatives, objections and card-level interaction. Used by final12/build.py (Week 12).
From Sunday of Week 12 (Fri Nov 27) the checks come from Independent Sports Research v1 (brain/isr.py) on every game through Week 11,
and the hand research below follows that method's workflow. Wednesday-Friday's research entries stay for the record (those games are locked)."""
import json, math, sys
import numpy as np, pandas as pd
W = '/home/claude/wedger/'
sys.path.insert(0, W + 'brain'); import isr as gates   # v3: the new method's checks (brain/isr.py); brain/gates.py stays for the posted cards
INJ_URL = 'https://www.espn.com/nfl/injuries'
# ---- quarterbacks, Week 12 (nflverse starts through Week 11; ESPN injury report Tue Nov 24, 2:42 PM CT). From Week 12 (rules v2) a backup
# starter does not take a game off the board: it is a research factor (BACKUP below; brain/rules.py qb_hold).
QB = {
    'GB @ LAR': (True, 'Jordan Love (GB) and Matthew Stafford (LAR) start; neither is on the injury report (ESPN, Tue Nov 24).'),
    'CHI @ DET': (True, 'Caleb Williams (CHI) and Jared Goff (DET) start; neither is on the injury report (ESPN, Tue Nov 24).'),
    'PHI @ DAL': (True, 'Joe Milton III starts for Philadelphia for the third time in four games (Weeks 9 and 11; Tanner McKee, ribs, is questionable); Dak Prescott (DAL) starts.'),
    'KC @ BUF': (True, 'Patrick Mahomes (KC) and Josh Allen (BUF) start; neither is on the injury report (ESPN, Tue Nov 24).'),
    'DEN @ PIT': (True, 'Bo Nix (DEN) and Aaron Rodgers (PIT) start; neither is on the injury report (ESPN, Tue Nov 24).'),
    'NO @ CIN': (True, 'Tyler Shough (NO) and Joe Burrow (CIN) start; neither is on the injury report (ESPN, Tue Nov 24).'),
    'BAL @ HOU': (True, 'Jacoby Brissett starts for Baltimore again (Lamar Jackson, thumb, is on injured reserve); C.J. Stroud (HOU) starts.'),
    'NYG @ IND': (True, 'J.J. McCarthy (NYG) and Daniel Jones (IND) have started every recent game; neither is on the injury report (ESPN, Tue Nov 24).'),
    'TEN @ JAX': (True, 'Cam Ward (TEN) and Trevor Lawrence (JAX) start; neither is on the injury report (ESPN, Tue Nov 24).'),
    'NYJ @ MIA': (True, 'Geno Smith (NYJ) starts; Kyle McCord starts for Miami again (Malik Willis, abdomen, is on injured reserve).'),
    'ATL @ MIN': (True, 'Michael Penix Jr. (ATL) starts; Kyler Murray (hamstring) is questionable, and Kirk Cousins started the last two games.'),
    'NE @ LAC': (True, 'Drake Maye (fibula) is out; Tommy DeVito started New England’s last game. Justin Herbert is in the concussion protocol (questionable).'),
    'WSH @ ARI': (True, 'Jayden Daniels (WAS) starts; Carson Beck (back) is questionable, and Josh Johnson started for Arizona in Week 11.'),
    'SEA @ SF': (True, 'Sam Darnold (quadriceps) is questionable for Seattle, with Drew Lock behind him; Brock Purdy (SF) starts.'),
    'LV @ CLE': (True, 'Fernando Mendoza (LV) makes his third start; Deshaun Watson (CLE) starts.'),
    'CAR @ TB': (True, 'Bryce Young (CAR) and Baker Mayfield (TB) start; neither is on the injury report (ESPN, Tue Nov 24).'),
}
# rules v2: a team starting a backup, and how many of its last 3 games he started (nflverse, most pass attempts). His team's
# receiving lines stay leans until he has started 2 of the last 3. Sunday entries are re-checked when those ladders open.
BACKUP = {'PHI': {'name': 'Joe Milton III', 'recent': 2}, 'BAL': {'name': 'Jacoby Brissett', 'recent': 2}, 'MIA': {'name': 'Kyle McCord', 'recent': 2},
          'MIN': {'name': 'Kirk Cousins', 'recent': 2}, 'NE': {'name': 'Tommy DeVito', 'recent': 1}, 'ARI': {'name': 'Josh Johnson', 'recent': 1}}
OVERS_NOTE ='In testing, the model’s overs that passed these same checks broke even (36 picks, Weeks 7–9), while its unders won in each week.'
RATIO = 3   # preferred mix on the card: about one under for every three overs, for finals and for leans
CTX = None
def ctx():
    global CTX
    if CTX is None:
        st = pd.read_csv(W + 'dl19/stats_player_week_2026.csv', low_memory=False)
        pbp = pd.read_csv(W + 'dl19/play_by_play_2026.csv.gz', low_memory=False, usecols=['week', 'qtr', 'rusher_player_id', 'receiver_player_id', 'rushing_yards', 'receiving_yards'])
        games = pd.read_csv(W + 'dl19/games.csv')
        CTX = gates.Ctx(st, pbp, games, 12)   # every game before Week 12 (Tuesday's build used 11 and left Week 11 out)
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
LBL = {'QB': 'Quarterbacks', 'ROLE': 'Role check', 'SCRIPT': 'Game-script check', 'LOG': 'Full game log', 'LATE': 'Late-work check', 'MOMENTUM': 'Form against his baseline'}
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
    m = c.get('MOMENTUM')
    if m and m.get('state') in ('hot', 'cold', 'steady'):
        t = {'hot': f"Running hot: {m['last3']:g} over his last 3 against a {m['season']:g} season median. The research checks whether it holds and whether the defense will key on him.",
             'cold': f"Running cold: {m['last3']:g} over his last 3 against a {m['season']:g} season median. The research looks for the cause before assuming a bounce-back.",
             'steady': f"In line with his baseline: {m['last3']:g} over his last 3, {m['season']:g} season median."}[m['state']]
        out.append({'k': LBL['MOMENTUM'], 'ok': True, 't': t, 'info': True})
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
# ---- research pass on the card lines (Tue Nov 24, ~3:30 PM CT): each line's strongest objection, its full 2026 log at the exact
# threshold, current news and the kickoff forecast. Calls change only on evidence; the master prompt (Nov 23) asks for the role and
# script that the numbers can't see yet.
ESPN = {'t': 'ESPN NFL injuries, Tue Nov 24 2:42 PM CT', 'u': INJ_URL}
NFLV = {'t': 'nflverse player stats, 2026 Weeks 1–11', 'u': 'https://github.com/nflverse/nflverse-data/releases/tag/stats_player'}
WX = {'t': 'Open-Meteo kickoff forecast, Tue Nov 24', 'u': 'https://open-meteo.com/'}
RAMS = {'t': 'Rams.com, Stafford confident in next receivers up with Nacua and Adams sidelined (Nov 11, 2026)', 'u': 'https://www.therams.com/news/i-trust-those-guys-to-be-in-the-right-spots-matthew-stafford-confident-in-next-receivers-up-with-puka-nacua-and-davante-adams-sidelined'}
PITT = {'t': 'TSN (AP), Steelers get a boost as WRs Pittman Jr. and Wilson return to practice (Nov 18, 2026)', 'u': 'https://www.tsn.ca/nfl/article/steelers-get-a-boost-as-wrs-pittman-wilson-return-to-practice/'}
BUFWX = 'Kickoff forecast at Highmark Stadium: 36°F, 96% chance of precipitation, 18 mph wind with gusts to 41 mph (Open-Meteo, Tue Nov 24).'
PITWX = 'Kickoff forecast in Pittsburgh: 38°F, drizzle likely (58%), 14 mph wind with gusts to 33 mph (Open-Meteo, Tue Nov 24).'
RESEARCH = {
    ('GB @ LAR', 'Jordan Love under 10 rushing yards (No)'): {
        'notes': ['Under 10 in 8 of his 10 games; he has 4 or fewer carries in every game and 0–1 in his last four.',
                  'Against it: two of his last five games reached 12 and 13 yards on scrambles, and one more scramble beats the line.'], 'src': [NFLV, ESPN]},
    ('GB @ LAR', 'Savion Williams under 10 rushing yards (No)'): {
        'notes': ['His carries are gadget runs (0–3 a game), so most games stay small.',
                  'Against it: he reached 18 and 13 in two of his five games, and Josh Jacobs (finger) is questionable, which can add designed touches.'],
        'src': [NFLV, ESPN], 'decision': 'Conditional lean',
        'why': 'Lean: a single long sweep beats this line (18 and 13 yards in two of his five games), so his log is thinner than our number. Stronger if Josh Jacobs plays.'},
    ('CHI @ DET', 'Kalif Raymond under 40 receiving yards (No)'): {
        'notes': ['Under 40 in 7 of 10 games and in every one of his last six (0–32).', 'Against it: Sam LaPorta (ankle) is questionable; targets he leaves spread over several players.'], 'src': [NFLV, ESPN]},
    ('CHI @ DET', 'Amon-Ra St. Brown 60+ receiving yards (Yes)'): {
        'notes': ['60+ in 7 of 10 games. Sam LaPorta (ankle) was limited Monday and is questionable, which would push more targets his way.',
                  'Against it: he was held to 46 and 37 in two of his last four, and a 55-point total game can still run through Gibbs.'], 'src': [NFLV, ESPN]},
    ('CHI @ DET', 'Jameson Williams 3+ receptions (Yes)'): {
        'notes': ['3+ catches in 7 of 10 games and in four of his last five; LaPorta’s questionable tag leaves more short targets.', 'Against it: he caught 1 and 2 in his two misses, on low-volume days.'], 'src': [NFLV, ESPN]},
    ('CHI @ DET', 'Kyle Monangai under 50 rushing yards (No)'): {
        'notes': ['D’Andre Swift is the lead back (13–27 carries a game); Monangai had 8 carries for 18 yards in Week 11.',
                  'Against it: his two big games (100 and 146) came when he carried 10 and 30 times; a Swift injury would flip this.'], 'src': [NFLV, ESPN]},
    ('PHI @ DAL', 'KaVontae Turpin under 2 receptions (No)'): {
        'notes': ['0 or 1 catch in 7 of his 8 games; he is a return man with a handful of snaps on offense.'], 'src': [NFLV]},
    ('PHI @ DAL', 'CeeDee Lamb 6+ receptions (Yes)'): {
        'notes': ['11+ targets in each of his last five games and 6+ catches in 8 of 11; Jake Ferguson (knee/ankle) did not practice Monday.',
                  'Against it: a big Dallas lead (Dallas is favored by about 9) can shorten the passing game late.'], 'src': [NFLV, ESPN]},
    ('PHI @ DAL', 'Darius Cooper 15+ receiving yards (Yes)'): {
        'notes': ['15+ in 7 of 10 games, 4 of his last 5; Dallas Goedert (shin) is limited and questionable.'], 'src': [NFLV, ESPN]},
    ('KC @ BUF', 'Josh Downs under 60 receiving yards (No)'): {
        'notes': ['Under 60 in 9 of 11 games, including both games with Kansas City (53 and 59).', BUFWX], 'src': [NFLV, WX]},
    ('KC @ BUF', 'Travis Kelce under 6 receptions (No)'): {
        'notes': ['Under 6 catches in 8 of 10 games.', BUFWX], 'src': [NFLV, WX]},
    ('KC @ BUF', 'Rashee Rice under 70 receiving yards (No)'): {
        'notes': ['Under 70 in 4 of his 7 games; he reached 82–88 in three of them.', BUFWX],
        'src': [NFLV, WX], 'decision': 'Conditional lean',
        'why': 'Lean while the wind forecast holds (18 mph, gusts to 41 at kickoff): his log alone, 4 of 7 under 70, is thinner than our number.'},
    ('DEN @ PIT', 'Marvin Mims Jr. under 20 receiving yards (No)'): {
        'notes': ['Under 20 in 6 of 8 games on 0–4 targets; Waddle and Sutton draw the volume.', PITWX], 'src': [NFLV, WX]},
    ('DEN @ PIT', 'Bo Nix under 20 rushing yards (No)'): {
        'notes': ['Under 20 in 9 of 10 games; he has run 7 or fewer times in every game.', 'Against it: his 73-yard game (Week 7) came on 7 carries; one long scramble does it.'], 'src': [NFLV]},
    ('DEN @ PIT', 'Germie Bernard under 40 receiving yards (No)'): {
        'notes': ['Under 40 in 6 of 9 games. Michael Pittman Jr. returned to practice from injured reserve on Nov 18, which would take snaps from him.', PITWX,
                  'Against it: he drew 10 targets in Week 11 (40 yards, a loss at this line by one yard).'], 'src': [NFLV, PITT, WX]},
    ('GB @ LAR', 'Christian Watson 4+ receptions (Yes)'): {
        'notes': ['4+ catches in 7 of 10 games on 8+ targets in most of them; with the Rams thin at receiver, Green Bay should be able to pass.', 'Against it: 3 catches in Week 10 on 5 targets.'], 'src': [NFLV]},
    ('PHI @ DAL', 'Javonte Williams 60+ rushing yards (Yes)'): {
        'notes': ['60+ in 4 of his last 5 games (16–25 carries); Dallas is favored by about 9, the script that keeps him running.', 'Against it: 6 of 11 for the season; his early-season games ran 30–45 yards.'], 'src': [NFLV]},
    ('KC @ BUF', 'Keon Coleman under 40 receiving yards (No)'): {
        'notes': ['Under 40 in 7 of 10 games and in four of his last five (4–17 yards).', BUFWX], 'src': [NFLV, WX]},
    ('KC @ BUF', 'Josh Allen under 50 rushing yards (No)'): {
        'notes': ['Under 50 in 8 of 10 games; he ran 0–7 times in each of his last five.', BUFWX,
                  'Against it: he reached 69 and 121 in two games, and a quarterback can keep the ball more in snow.'], 'src': [NFLV, WX]},
    ('DEN @ PIT', 'Jaylen Waddle under 60 receiving yards (No)'): {
        'notes': ['Under 60 in 8 of 10 games.', PITWX, 'Against it: he had 61 in Week 11 on 6 targets.'], 'src': [NFLV, WX]},
}
# research that holds for every rung of a player's side (keyed by game, player, side)
RESEARCH_PLAYER = {
    ('GB @ LAR', 'Konata Mumpfield', 'No'): {
        'notes': ['Puka Nacua (knee) had surgery and is out for the season (ESPN, Nov 22); Davante Adams is on injured reserve. Mumpfield is now a starter: 81 yards in Week 10, the first game without Nacua.',
                  'His 7-of-9 log at this line comes from games when he was the fourth or fifth option.'],
        'src': [ESPN, RAMS, NFLV], 'decision': 'Pass', 'why': 'Research pass: his role changed with Nacua and Adams out (81 yards in the first game without Nacua), so his old log overstates the under.'},
    ('GB @ LAR', 'Xavier Smith', 'No'): {
        'notes': ['With Nacua and Adams out, the Rams named him among the next receivers up; he had 40 yards on 2 targets in Week 10, his first real role.',
                  'Three of his four games at this line were 0-target games before the injuries.'],
        'src': [ESPN, RAMS, NFLV], 'decision': 'Pass', 'why': 'Research pass: his log is from before he had a role; with Nacua and Adams out he is a regular now.'},
    ('PHI @ DAL', 'George Pickens', 'No'): {
        'notes': ['He has 145 and 102 yards in his last two games on 18 and 10 targets, and Jake Ferguson (knee/ankle) did not practice Monday.'],
        'src': [NFLV, ESPN], 'decision': 'Pass', 'why': 'Research pass: his last two games went 145 and 102 on 18 and 10 targets, and Ferguson’s absence would push more targets his way.'},
    ('KC @ BUF', 'James Cook III', 'No'): {
        'notes': ['He carried 21–31 times in six of his last seven games and went 107+ in four of them.', BUFWX + ' Snow and wind push teams to the run.'],
        'src': [NFLV, WX], 'decision': 'Pass', 'why': 'Research pass: the snow-and-wind forecast pushes Buffalo to the run, and he has gone 107+ in four of his last seven.'},
    ('DEN @ PIT', 'Jonah Coleman', 'No'): {
        'notes': ['His carries went 10, 9, 11, 17, 24 over his last five games, with 111 yards in Week 11; J.K. Dobbins had 1 carry.'],
        'src': [NFLV], 'decision': 'Pass', 'why': 'Research pass: he took over as the lead back (24 carries, 111 yards in Week 11), so his earlier log understates his workload.'},
    ('GB @ LAR', 'Tucker Kraft', 'Yes'): {
        'notes': ['25+ in 7 of 10 games, but 1 and 19 yards in his last two on 3–4 targets, with Matthew Golden and Christian Watson drawing 8–13 targets.'],
        'src': [NFLV], 'decision': 'Pass', 'why': 'Research pass: his last two games went 1 and 19 yards on 3–4 targets, so the 7-of-10 log is behind his current role.'},
    ('KC @ BUF', 'Cyrus Allen', 'No'): {
        'notes': ['Under 20 in only 4 of 8 games, and his role is growing: 4 targets and 41–44 yards in each of his last two.'],
        'src': [NFLV], 'decision': 'Pass', 'why': 'Research pass: his last two games went 44 and 41 yards on 4 targets each; the weather alone doesn’t make up for a 4-of-8 log.'},
    ('DEN @ PIT', 'Evan Engram', 'No'): {
        'notes': ['Under 4 catches in 6 of 10 games, and he caught 6 of 8 targets in Week 11.'],
        'src': [NFLV], 'decision': 'Pass', 'why': 'Research pass: under 4 catches in only 6 of 10 games, with 6 catches on 8 targets last week.'},
    ('GB @ LAR', 'Matthew Golden', 'No'): {
        'notes': ['He draws 9–13 targets in most games and reached 100+ in 4 of 10.'],
        'src': [NFLV], 'decision': 'Pass', 'why': 'Research pass: he reached 100 yards in 4 of 10 games on 9–13 targets, too often for an under at this line.'},
}

# ==== Sunday and Monday, Week 12 (Fri Nov 27): Independent Sports Research v1, game first ==========================================
# Each game was read before its lines: the AP game preview (records, stakes, injuries, coach and player quotes, the matchup to watch),
# ESPN's injury report (Fri Nov 27, 3:01 AM CT: Thursday's practice reports), team analysts where they covered the game, the kickoff
# forecast, and nflverse logs and usage through Week 11. Then each card line was held against that read; a line stays only when the
# football case holds, and each keeps its strongest counterargument. Final injury designations post Friday afternoon.
ESPN = {'t': 'ESPN NFL injuries, Fri Nov 27 3:01 AM CT', 'u': INJ_URL}
WX2 = {'t': 'Open-Meteo kickoff forecast, Fri Nov 27', 'u': 'https://open-meteo.com/'}
def AP(gid, title): return {'t': f'AP game preview via ESPN: {title} (Nov 25–26, 2026)', 'u': f'https://www.espn.com/nfl/game/_/gameId/{gid}'}
AP_NOCIN = AP(401873087, 'Bengals look to get back on track when they host the Saints on a short week')
AP_BALHOU = AP(401873085, 'Ravens limp in on 6-game skid without Jackson')
AP_NYGIND = AP(401873088, 'QB Anthony Richardson hopes to follow J.J. McCarthy’s lead')
AP_TENJAX = AP(401873090, 'Jaguars are simplifying the operation against the Titans')
AP_NYJMIA = AP(401873089, 'Dolphins playing host to Jets')
AP_ATLMIN = AP(401873084, 'Kirk Cousins makes his home debut in his second act with the Vikings')
AP_NELAC = AP(401873093, 'Patriots-Chargers shaping up to be battle of backup QBs')
AP_WSHARI = AP(401873092, 'Commanders try to continue momentum')
AP_SEASF = AP(401873091, 'Purdy and the 49ers prepare for another tough test')
AP_LVCLE = AP(401873086, 'Deshaun Watson and Fernando Mendoza face primetime pressure')
AP_CARTB = AP(401873094, 'Buccaneers will need more from Baker Mayfield')
NINERS = {'t': '49ers Webzone, 49ers vs. Seahawks injury report: Brock Purdy misses second straight practice (Nov 26, 2026)', 'u': 'https://www.49erswebzone.com/articles/205551-seahawks-injury-report-straight-practice/'}
HENRY = {'t': 'NBC Sports, Derrick Henry (concussion) gets full practice (Nov 26, 2026)', 'u': 'https://www.nbcsports.com/fantasy/football/player-news/2026-11-26/derrick-henry-concussion-gets-full-practice'}
JAXSCOUT = {'t': 'Jaguars.com, Scout’s Take: Bucky Brooks looks ahead to Week 12 vs. Titans (Nov 25, 2026)', 'u': 'https://jaguars.com/news/scout-s-take-bucky-brooks-looks-ahead-to-week-12-vs-titans'}
TITANSWIRE = {'t': 'Titans Wire, Titans vs. Jaguars: 3 key matchups for Week 12 (Nov 26, 2026)', 'u': 'https://sports.yahoo.com/nfl/articles/tennessee-titans-vs-jacksonville-jaguars-100803504.html'}
CINWX = 'Kickoff forecast in Cincinnati: 50°F, rain likely (91–97%), gusts near 30 mph (Open-Meteo, Fri Nov 27).'
CLEWX = 'Kickoff forecast in Cleveland: 47°F, light rain (99%), little wind (Open-Meteo, Fri Nov 27).'
SFWX = 'Kickoff forecast in Santa Clara: 66°F, showers possible (69%), 10 mph wind (Open-Meteo, Fri Nov 27).'
QB.update({
    'NO @ CIN': (True, 'Tyler Shough (NO) and Joe Burrow (CIN) start; neither is on the injury report (ESPN, Fri Nov 27).'),
    'BAL @ HOU': (True, 'Jacoby Brissett makes his third Baltimore start (Lamar Jackson and Tyler Huntley are on injured reserve); C.J. Stroud (HOU) starts.'),
    'NYG @ IND': (True, 'J.J. McCarthy (NYG) starts. Anthony Richardson starts for Indianapolis, his first start in nearly two years (Daniel Jones is gone).'),
    'TEN @ JAX': (True, 'Cam Ward (TEN) and Trevor Lawrence (JAX) start; neither is on the injury report (ESPN, Fri Nov 27).'),
    'NYJ @ MIA': (True, 'Geno Smith (NYJ) starts; Kyle McCord starts for Miami again (Malik Willis is on injured reserve).'),
    'ATL @ MIN': (True, 'Michael Penix Jr. (ATL) starts; Kirk Cousins makes his third straight start for Minnesota (Kyler Murray, hamstring, is questionable).'),
    'NE @ LAC': (True, 'Tommy DeVito starts for New England (Drake Maye, fibula, is out). Justin Herbert is in the concussion protocol, and DJ Uiagalelei is in line for his first start.'),
    'WSH @ ARI': (True, 'Jayden Daniels (WAS) starts. Josh Johnson is likely to start for Arizona again (Carson Beck, back spasms, is questionable).'),
    'SEA @ SF': (True, 'Sam Darnold (SEA) practiced fully. Brock Purdy (ankle, not a high-ankle sprain) missed Wednesday and Thursday and is day-to-day.'),
    'LV @ CLE': (True, 'Fernando Mendoza (LV) makes his third start; Deshaun Watson (CLE) starts.'),
    'CAR @ TB': (True, 'Bryce Young (CAR) and Baker Mayfield (TB) start; neither is on the injury report (ESPN, Fri Nov 27).'),
})
BACKUP.update({'IND': {'name': 'Anthony Richardson', 'recent': 0}, 'LAC': {'name': 'DJ Uiagalelei', 'recent': 0}})

def _r(notes, src, decision=None, why=None):
    d = {'notes': notes, 'src': src}
    if decision: d['decision'] = decision; d['why'] = why
    return d
RESEARCH.update({
    # NO @ CIN: Cincinnati by 10 on a short week after Monday's loss; two top-10 pass rushes; rain and gusts at kickoff
    ('NO @ CIN', 'Chase Brown 15+ receiving yards (Yes)'): _r([
        '15+ in 8 of 10 games. The Saints’ edge pair (Granderson 8.5 sacks, Young 8) is the reason to expect quick throws, and backs are Burrow’s outlet under pressure.',
        CINWX + ' Rain favors short throws over deep ones.', 'Against it: a Bengals lead of 10+ shifts the second half to the run.'], [AP_NOCIN, NFLV, WX2]),
    ('NO @ CIN', 'Tyler Shough 10+ rushing yards (Yes)'): _r([
        'Cincinnati gives up 10.7 yards per scramble, the second most in the league, and Shough has 204 yards on 25 scrambles.',
        'He has 25+ in four of his last five games. Trailing by 10 means more dropbacks against a pass rush (Mafe 9.5 sacks) that flushes quarterbacks.',
        'Against it: wet footing and a quick-game plan can cut scrambles.'], [AP_NOCIN, NFLV]),
    ('NO @ CIN', 'Devaughn Vele under 50 receiving yards (No)'): _r([
        'Under 50 in only 5 of 10 games. Both things most likely to change his usage push it up: New Orleans trailing by 10, and Juwan Johnson (hamstring) questionable.',
        CINWX], [AP_NOCIN, ESPN, NFLV, WX2], 'Pass',
        'Research pass: a coin-flip log at this line (5 of 10), with the script and Juwan Johnson’s hamstring both pushing his targets up. The rain helps the under, but not enough.'),
    ('NO @ CIN', 'Travis Etienne Jr. under 25 receiving yards (No)'): _r([
        'Trailing by 10 against a top-10 pass rush (29 sacks) is the game state that sends a quarterback to his back on checkdowns, and rain favors the short throw.'],
        [AP_NOCIN, NFLV], 'Pass', 'Research pass: the likely game (Saints trailing, under pressure, in rain) is the one that feeds a running back’s catches; the matchup points against the under.'),
    ('NO @ CIN', 'Ja\'Marr Chase under 120 receiving yards (No)'): _r([
        'Under 120 in 7 of 10. He went 141, 155 and 231 before Washington held him to 31 on Monday, a sign defenses are keying on him.',
        CINWX + ' Gusts near 30 mph cut into the deep shots that produce 120-yard games, and a big Bengals lead shortens the passing game.',
        'Against it: he has 120+ in three of his last four games.'], [AP_NOCIN, NFLV, WX2]),
    # BAL @ HOU: Houston by 6.5; Henry practiced fully (out of protocol); Brissett has thrown 49 and 37 times in two Baltimore starts
    ('BAL @ HOU', 'Jacoby Brissett under 10 rushing yards (No)'): _r([
        'A pocket passer: 2 and 7 rushing yards in his two Baltimore starts, under 20 in every 2026 start.',
        'Against it: Will Anderson Jr. (11.5 sacks) will chase him from the pocket.'], [AP_BALHOU, NFLV]),
    ('BAL @ HOU', 'Tank Dell 20+ receiving yards (Yes)'): _r([
        '20+ in all four games since his return. Dalton Schultz (illness) and Kayshon Boutte (hip) are questionable, which would push more targets his way.'], [AP_BALHOU, ESPN, NFLV]),
    ('BAL @ HOU', 'Zay Flowers under 8 receptions (No)'): _r([
        'With Brissett he caught 6 and 8: Brissett throws 37–49 times a game, and Baltimore is a 6.5-point underdog.'],
        [AP_BALHOU, NFLV], 'Pass', 'Research pass: the quarterback change raised his volume (6 and 8 catches with Brissett), and trailing adds throws; the under needs 7 or fewer.'),
    ('BAL @ HOU', 'Nico Collins 40+ receiving yards (Yes)'): _r([
        '40+ in 7 of his 8 games, 58 last week. Houston is favored at home against a team that has lost six straight.',
        'Against it: a Texans lead and Woody Marks back would tilt the game to the run.'], [AP_BALHOU, NFLV]),
    # NYG @ IND: Richardson's first start in nearly two years; Alec Pierce on IR; the Giants' run game against one of the worst run defenses
    ('NYG @ IND', 'Tyler Warren 3+ receptions (Yes)'): _r([
        'Running cold: 2 and 1 catches in his last two games. Anthony Richardson makes his first start in nearly two years; his accuracy is the question, and a tight end’s short catches depend on it.'],
        [AP_NYGIND, NFLV], 'Pass', 'Research pass: cold (2 and 1 catches in his last two), and the new quarterback’s accuracy is the open question for short targets.'),
    ('NYG @ IND', 'Malachi Fields 15+ receiving yards (Yes)'): _r([
        '15+ in all 10 games. The Giants should lean on the run against one of the worst run defenses, which limits the passing game, so this stays a small number.'], [AP_NYGIND, NFLV]),
    # TEN @ JAX: Jacksonville by 14.5 two weeks after a 40-23 win; the Titans allow the most passing yards; the Jaguars are simplifying
    ('TEN @ JAX', 'Tony Pollard under 95 rush + rec yards (No)'): _r([
        'Over 95 in each of his last four games. In the first meeting he was held to 33 rushing yards on 9 carries but caught 8 passes for 66: 99 in all.',
        'The script that slows his carries (Tennessee trailing) is the one that adds his catches.'], [AP_TENJAX, TITANSWIRE, NFLV], 'Pass',
        'Research pass: over 95 in four straight, and in the first meeting the trailing script moved his yards to catches (33 rushing + 66 receiving = 99).'),
    ('TEN @ JAX', 'Brenton Strange under 50 receiving yards (No)'): _r([
        'His role has shrunk: 2–3 targets in each of the last four games (22, 9 and 16 yards in the last three, 9 against Tennessee in Week 10).',
        'Against it: Tennessee allows the most passing yards in the league (272.7 a game), and the Jaguars’ scout expects him to find room between the numbers.'], [AP_TENJAX, JAXSCOUT, TITANSWIRE, NFLV]),
    ('TEN @ JAX', 'Travis Hunter under 20 receiving yards (No)'): _r([
        'Under 20 in 9 of 10 games: his offensive role is small, and the Jaguars’ scout lists Washington, Meyers, Strange and Thomas as the receivers who should get open.'], [JAXSCOUT, NFLV]),
    ('TEN @ JAX', 'Cam Ward under 15 rushing yards (No)'): _r([
        'He ran for 39 yards on 3 carries against Jacksonville in Week 10 and 41 the game before; trailing by two scores means dropbacks and scrambles.'],
        [TITANSWIRE, NFLV], 'Pass', 'Research pass: 39 rushing yards against this defense two weeks ago, and the trailing script adds dropbacks.'),
    # NYJ @ MIA
    ('NYJ @ MIA', 'Adonai Mitchell 20+ receiving yards (Yes)'): _r([
        'His role swings: 3 to 12 targets a game, 3 last week, and 0 catches on 3 targets in the October game against Miami. The preview’s matchup to watch is Mason Taylor against the Miami secondary.'],
        [AP_NYJMIA, NFLV], 'Pass', 'Research pass: his targets swing from 3 to 12, and he was shut out by Miami in October; the role isn’t steady enough for a final.'),
    ('NYJ @ MIA', 'Breece Hall 10+ receiving yards (Yes)'): _r([
        '10+ in all six games he played, on 2–5 targets each.', 'Against it: Braelon Allen leads the Jets in rushing and a lead turns the backfield to him.'], [NFLV]),
    ('NYJ @ MIA', 'Greg Dulcich 15+ receiving yards (Yes)'): _r([
        'Three straight misses (14, 0, 12), the last two in Kyle McCord’s two starts on 2 and 7 targets.'],
        [AP_NYJMIA, NFLV], 'Pass', 'Research pass: three straight misses, two of them since the quarterback change to McCord.'),
    # ATL @ MIN: Minnesota by 7; Cousins at home against his former team; Addison doubtful; the 49ers beat this defense with quick throws to the middle
    ('ATL @ MIN', 'Drake London under 7 receptions (No)'): _r([
        'Under 7 in 7 of 10 games (5 a game). In the AP’s account of last week, San Francisco beat Minnesota with quick throws to the middle of the field, not the outside routes London mostly runs.'], [AP_ATLMIN, NFLV]),
    ('ATL @ MIN', 'Kyle Pitts Sr. under 40 receiving yards (No)'): _r([
        'San Francisco beat this defense by throwing quickly to spaces in the middle of the field created by its aggressive rush, and Atlanta comes off a bye with its coach saying there was plenty to learn from that game.',
        'Pitts is Atlanta’s middle-of-the-field target and has 40+ in four of his last seven.'], [AP_ATLMIN, NFLV], 'Pass',
        'Research pass: Minnesota’s known weakness (quick throws to the middle) is where Pitts lives, and Atlanta had a bye to plan for it.'),
    ('ATL @ MIN', 'Justin Jefferson under 110 receiving yards (No)'): _r([
        'Under 110 in all 9 of his games, including 74 and 86 in Cousins’ two starts.',
        'Against it: Jordan Addison (thumb) is doubtful, and Cousins fed Jefferson some of the biggest seasons of his career.'], [AP_ATLMIN, ESPN, NFLV]),
    ('ATL @ MIN', 'Bijan Robinson under 100 rushing yards (No)'): _r([
        'Under 100 in 7 of 10. Atlanta is a 7-point underdog, the script that cuts carries late.', 'Against it: he is rested after the bye and went 145 and 194 in two games.'], [AP_ATLMIN, NFLV]),
    ('ATL @ MIN', 'T.J. Hockenson under 60 receiving yards (No)'): _r([
        'Running hot (55 over his last 3), Addison is doubtful, and Cousins and Hockenson were a high-volume pair before.'],
        [AP_ATLMIN, ESPN, NFLV], 'Pass', 'Research pass: every catalyst points up: Cousins back, Addison doubtful, and his recent form.'),
    # NE @ LAC: two backups, total 35.5
    ('NE @ LAC', 'Kimani Vidal 10+ rushing yards (Yes)'): _r([
        'A first-time starter at quarterback (DJ Uiagalelei, if Herbert stays in the protocol) usually means a heavier run plan; Vidal has 20+ in 6 of his last 7.',
        'Against it: Omarion Hampton leads the backfield, and Vidal had 0 rushing yards in two games.'], [AP_NELAC, NFLV]),
    ('NE @ LAC', 'Mack Hollins under 4 receptions (No)'): _r([
        'A.J. Brown (hamstring) is doubtful and Romeo Doubs is on injured reserve, which leaves Hollins among New England’s top two receivers.'],
        [AP_NELAC, ESPN, NFLV], 'Pass', 'Research pass: with Brown doubtful and Doubs out, his targets go up; the under needs 3 or fewer.'),
    # WSH @ ARI: Washington by 7; Arizona fired its defensive coordinator; Josh Johnson likely again
    ('WSH @ ARI', 'Josh Johnson under 25 rushing yards (No)'): _r([
        'He ran for 5 yards in his Week 11 start, at 40. But Carson Beck (back spasms) is questionable, and the line only matters if Johnson starts.'],
        [AP_WSHARI, ESPN, NFLV], 'Conditional lean', 'Only if Josh Johnson starts (Carson Beck is questionable with back spasms).'),
    ('WSH @ ARI', 'Antonio Williams 3+ receptions (Yes)'): _r([
        '3+ in 8 of 10. Dyami Brown is on injured reserve and Treylon Burks (foot) is questionable, so the targets concentrate on him. Arizona has allowed 30+ points in 8 of 11 games.'], [AP_WSHARI, ESPN, NFLV]),
    ('WSH @ ARI', 'Bam Knight under 40 rushing yards (No)'): _r([
        'Under 40 in 5 of 7. Tyler Allgeier leads Arizona’s backfield with Jeremiyah Love on injured reserve, and a 7-point deficit cuts the carries.'], [AP_WSHARI, ESPN, NFLV]),
    ('WSH @ ARI', 'Chig Okonkwo 25+ receiving yards (Yes)'): _r([
        '25+ in 5 of 8, 66 last week. Arizona has allowed a league-high 25 passing touchdowns and has a new defensive coordinator this week.'], [AP_WSHARI, NFLV]),
    # SEA @ SF: Purdy day-to-day; Evans and Smith-Njigba limited; Seattle's defense has held San Francisco in check
    ('SEA @ SF', 'Tory Horton under 15 receiving yards (No)'): _r([
        'Under 15 in only 3 of 6 and over in his last two (26, 22). Jaxon Smith-Njigba (ankle) is limited, which can only add to Horton’s role.'],
        [NINERS, NFLV], 'Pass', 'Research pass: a 3-of-6 log with two straight misses, and Smith-Njigba’s ankle could push him up.'),
    ('SEA @ SF', 'Rashid Shaheed under 30 receiving yards (No)'): _r([
        'Under 30 in 6 of 8; 1 and 8 yards in his last two. ' + SFWX, 'Against it: if Smith-Njigba is limited, Shaheed is next in line for targets.'], [NINERS, NFLV, WX2]),
    ('SEA @ SF', 'George Kittle 30+ receiving yards (Yes)'): _r([
        '30+ in 8 of 10. Brock Purdy (ankle) missed Wednesday and Thursday; Kyle Shanahan called him day-to-day. A backup throwing to him changes the read.'],
        [NINERS, NFLV], 'Conditional lean', 'Only if Brock Purdy starts (ankle; missed Wednesday and Thursday practice).'),
    ('SEA @ SF', 'Kaelon Black under 30 rushing yards (No)'): _r([
        'Over 30 in four of his last five (34, 63, 70, 53): his role has grown. If Purdy sits, San Francisco leans on the run.'],
        [NINERS, NFLV], 'Pass', 'Research pass: his workload has grown (30+ in four of his last five), and a Purdy absence would add carries.'),
    # LV @ CLE: Cleveland by 4.5 in light rain; Raheim Sanders on injured reserve
    ('LV @ CLE', 'Quinshon Judkins 40+ rushing yards (Yes)'): _r([
        'Raheim Sanders is on injured reserve, so the carries are his. Cleveland is favored, and ' + CLEWX[0].lower() + CLEWX[1:],
        'Against it: 40+ in only 5 of 9, and Watson has thrown for 300+ in three straight.'], [AP_LVCLE, ESPN, NFLV, WX2]),
    ('LV @ CLE', 'Mike Washington Jr. 20+ rushing yards (Yes)'): _r([
        '20+ in 7 of 11, 23 and 42 in his last two.', 'Against it: a Raiders deficit cuts the run game, and Ashton Jeanty leads the backfield.'], [AP_LVCLE, NFLV]),
    # CAR @ TB (Monday): Irving ran 24 times for 106 in the 43-13 win in October; Carolina has since fired its defensive coordinator
    ('CAR @ TB', 'Bucky Irving 60+ rushing yards (Yes)'): _r([
        'He ran 24 times for 106 yards and two touchdowns in the October meeting, when Tampa Bay ran for 258. Carolina fired its defensive coordinator less than two weeks later.',
        'Against it: Kenneth Gainwell took 14 carries in that game, and a Panthers lead would cut the run game.'], [AP_CARTB, NFLV]),
    ('CAR @ TB', 'Ted Hurst III under 40 receiving yards (No)'): _r([
        'His role jumped last week: 7 targets for 56 yards after three straight one-target games. The cause isn’t clear yet, and until it is, his old log can’t carry an under.'],
        [NFLV], 'Pass', 'Research pass: 7 targets and 56 yards last week after three one-target games; a role change the log doesn’t reflect yet.'),
    ('CAR @ TB', 'Chuba Hubbard under 30 receiving yards (No)'): _r([
        'Under 30 in 7 of 10.', 'Against it: Carolina is the underdog, and he had 80 receiving two games ago.'], [AP_CARTB, NFLV]),
    ('CAR @ TB', 'John Metchie III under 20 receiving yards (No)'): _r([
        'He cleared 20 in 4 of 9, and the AP preview’s theme is that Tampa Bay needs more from its passing game.'],
        [AP_CARTB, NFLV], 'Pass', 'Research pass: a near coin-flip log (under in 5 of 9), with Tampa Bay looking to throw more.'),
})
# lines the model doesn't price (the method's other markets), at the market's own number, kept only on a research case
RESEARCH_MARKET = {
    ('BAL @ HOU', 'KXNFLPASSATT', 'Jacoby Brissett', 31, 'Yes'): _r([
        '31+ attempts in 5 of his last 6 starts (47, 35, 48, 49, 37; the miss was 23). Baltimore is a 6.5-point underdog, and Houston held Indianapolis to 38 rushing yards last week.',
        'Against it: Derrick Henry is back from the protocol (full practice Thursday), which can pull the plan toward the run.'], [AP_BALHOU, HENRY, NFLV], 'Final line',
        'A research pick: our model doesn’t price passing attempts, so the chance shown is the market’s.'),
    ('ATL @ MIN', 'KXNFLRSHATT', 'Jordan Mason', 17, 'No'): _r([
        'Under 17 carries in all six games he has played (15, 15, 8, 6, 16, 11); Aaron Jones leads Minnesota’s backfield.',
        'Against it: a Vikings lead of 7+ hands the fourth quarter to the backs.'], [AP_ATLMIN, NFLV], 'Final line',
        'A research pick: our model doesn’t price rushing attempts, so the chance shown is the market’s.'),
}
RESEARCH.update({
    ('NO @ CIN', 'Tee Higgins under 7 receptions (No)'): _r([
        'Under 7 in 8 of 10 games (5 a game). ' + CINWX, 'Against it: he caught 10 and 11 in two games, and Chase draws the coverage.'], [AP_NOCIN, NFLV, WX2]),
    ('TEN @ JAX', 'Parker Washington under 100 receiving yards (No)'): _r([
        'Over 100 in two of his last three (152, 103), and the Jaguars’ scout names him first among the receivers who should find room. He is questionable (shoulder).'],
        [JAXSCOUT, ESPN, NFLV], 'Pass', 'Research pass: over 100 in two of his last three, and Jacksonville’s own scout expects him to be featured.'),
    ('SEA @ SF', 'Sam Darnold under 10 rushing yards (No)'): _r([
        'Over 10 in each of his last three games (19, 17, 20) after five straight under it.'],
        [NFLV], 'Pass', 'Research pass: 17–20 rushing yards in each of his last three games; the log at this line has turned.'),
})
RESEARCH_PLAYER.update({
    ('ATL @ MIN', 'Kyle Pitts Sr.', 'No'): _r([
        'San Francisco beat Minnesota with quick throws to the middle of the field, and Atlanta comes off a bye with its coach saying there was plenty to learn from that game. Pitts has 4+ catches in four of his last six.'],
        [AP_ATLMIN, NFLV], 'Pass', 'Research pass: Minnesota’s known weakness (quick throws to the middle) is where Pitts lives, and Atlanta had a bye to plan for it.'),
})
