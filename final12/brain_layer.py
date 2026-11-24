"""The research method layered on the v6 card: QB eligibility, research checks per exact line, the evidence chain,
alternatives, objections and card-level interaction. Used by final12/build.py (Week 12)."""
import json, math, sys
import numpy as np, pandas as pd
W = '/home/claude/wedger/'
sys.path.insert(0, W + 'brain'); import gates
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
