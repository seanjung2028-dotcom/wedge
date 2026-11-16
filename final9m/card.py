"""Assemble the Monday BUF @ MIN card (final9m/card_BUFMIN.json) from final9m/analysis.json, the matchup lens and the written record."""
import json, math, re
W = '/home/claude/wedger/'
A = json.load(open(W + 'final9m/analysis.json')); AT = A['at']
LN = json.load(open(W + 'final9m/lens.json'))
WORD = {'pass': 'passing yards', 'rush': 'rushing yards', 'rec': 'receptions', 'recyd': 'receiving yards'}
SHORT = {'pass': 'pass yds', 'rush': 'rush yds', 'rec': 'rec', 'recyd': 'rec yds'}
def thr(r, st, short=False):
    w = SHORT[st] if short else WORD[st]
    return f"{int(r['k'])}+ {w}" if r['side'] == 'Yes' else f"under {int(r['k'])} {w}"
pct = lambda x: f"{x:.0f}%"; rng = lambda r: f"{r['lo']:.0f}–{r['hi']:.0f}%"; sgn = lambda x: ('+' if x >= 0 else '−') + f"{abs(x):.1f}"
def ladder_rows(o):
    p, a = o['pick'], o['alt']; out = []
    for r in sorted(o['rows'], key=lambda r: (r['side'], r['k'])):
        tag = 'card' if p and (r['k'], r['side']) == (p['k'], p['side']) else ('alt' if a and p and (r['k'], r['side']) == (a['k'], a['side']) else '')
        out.append({'t': thr(r, o['stat'], True), 'side': r['side'], 'ask': r['ask'], 'pays': r['pays'], 'be': r['be'], 'mkt': r['mkt'], 'lo': r['lo'], 'mid': r['mid'], 'hi': r['hi'],
                    'hits': f"{r['n_hit']}/{r['n']}", 'call': r['call'], 'tag': tag})
    return out
def vs_text(o):
    p, a = o['pick'], o['alt']
    if not a: return ''
    fin = p['call'] == 'Final line'; ep, ea = (p['edge_lo'], a['edge_lo']) if fin else (p['edge_mid'], a['edge_mid'])
    yard = 'at the low end of our number' if fin else 'at the middle of our number'
    head = f"Beat {thr(a, o['stat'])} ({a['side']} {a['ask']}¢, needs {a['be']}%, ours {rng(a)}). "
    if abs(ep - ea) < 0.05:
        body = (f"Both clear break-even by {sgn(ep)} points {yard}; this one hits more often ({pct(p['mid'])} vs {pct(a['mid'])} by our number)." if p['mid'] >= a['mid'] else
                f"Both clear break-even by {sgn(ep)} points {yard}; this one pays more ({p['pays']:.2f}× vs {a['pays']:.2f}×).")
    elif a['mid'] > p['mid']: body = f"That rung hits more often ({pct(a['mid'])} vs {pct(p['mid'])}), but its price leaves {sgn(ea)} points over break-even {yard}, against {sgn(ep)} here."
    else: body = f"That rung pays more ({a['pays']:.2f}× vs {p['pays']:.2f}×) but hits less often ({pct(a['mid'])} vs {pct(p['mid'])}), leaving {sgn(ea)} points over break-even {yard}, against {sgn(ep)} here."
    return head + body
def sample_text(o, r):
    lab = f"{int(r['k'])}+" if r['side'] == 'Yes' else f"Under {int(r['k'])}"
    return f"{lab} in {r['n_hit']} of {r['n']} games this season ({', '.join(str(int(v)) for _, v, _ in o['vals'])}, in order)."

PLAY = {
 'T.J. Hockenson': dict(
  why="Where Wentz throws and where BUF gives up volume meet at tight end. Wentz sent 34% of his targets to TEs (3rd among QBs), and BUF allows 9.1 TE targets and 70.6 TE yards a game, both 4th most.",
  support="The closest coverage match, Week 1 vs GB with Wentz: 5 targets, 4 catches, 36 yards and a TD. Against the defenses most like BUF: 119 (MIA) and 58 (DET).",
  note="With Wentz: 36 and 29.",
  counter="His share falls against the blitz (13% vs 24% without), and BUF blitzes 38.6% of dropbacks (7th).",
  loses="MIN leads and runs, or Wentz's 23-attempt pattern holds."),
 'James Cook': dict(
  why="The deciding factor: BUF's run game against MIN's one soft spot. BUF has the league's best inside-run success rate (52.8%). MIN allows 4.60 yards a carry (11th most) and plays light boxes (6.5) while blitzing on 72.8% of dropbacks.",
  support="50+ in all 7 games, including 75, 111 and 80 against the three top-10 run defenses he has faced. BUF is 3rd in rush attempts and a 3.5-point favorite.",
  note="Our direction stand-in for scheme only partly confirms the MIN side (3.96 yards allowed inside, 13th most).",
  counter="MIN's success rate allowed on inside runs is good (38.0%), so the yards come in chunks, not every down.",
  loses="Ray Davis or Ty Johnson take the late work in a blowout, or MIN leads and BUF throws."),
 'Khalil Shakir': dict(
  why="The alignment overlap. MIN allows 15.6% of targets to WRs in the middle (4th most), Allen throws there 15.6% of the time (5th), and Shakir is BUF's middle receiver (39% of his targets).",
  support="Against the blitz his share rises to 22.9% (17.9% without), and MIN blitzes on 72.8% of dropbacks, by far the most. Josh Palmer is out.",
  note="His 5.5-yard average target depth means 40 takes catches: he had 4+ in 4 of 7.",
  counter="MIN allows the 6th-fewest WR yards (122.7 a game).",
  loses="The quick throws go to Kincaid and the backs, or a 1-catch day like Week 3 (6 yards)."),
 'Jordan Mason': dict(
  why="MIN's inside run game is 30th in yards a carry (3.02) and 31st in success rate, and BUF allows 3.94 a carry with 6.8 in the box (4th most).",
  support="No schematic edge for MIN on the ground. With Claiborne out, the carries split three ways (Mason, Jones, DeeJay Dallas).",
  note="20 on 8 carries against DET, the closest comp to BUF's defense.",
  counter="He had 15 carries in two of his three games, and one long run clears 30.",
  loses="MIN leads and leans on Mason late."),
}
PASS = {
 'Justin Jefferson': dict(why="The lens leans his way: 34% of Wentz's targets, 9 catches for 92 and 2 TDs in the Week 1 coverage match (GB), and a dome. But BUF rarely allows targets outside the numbers (29th), and he has 80+ in 2 of 6. Net +2, too thin to rank.", move=None),
 'Jordan Addison': dict(why="Wentz rarely throws outside (29th), BUF allows the 4th-lowest outside share, and Addison had 0 and 21 yards with Wentz. Jennings being out offsets part of it. Net −2, too thin to rank.", move=None),
 'Carson Wentz': dict(why="Saturday's lean (under 200) is off. The lens nets to zero: 23 attempts in both starts and a run-first MIN (29th in pass attempts), against a BUF defense that faces 38.3 attempts a game (2nd) and a trailing script.", move="None pregame."),
 'Josh Allen': dict(why="MIN's blitz halves his scrambles (4.8% of dropbacks vs 9.7%), and MIN allows the 5th-fewest scramble yards. But he ran for 69 against DET, a similar pass rush. Net −2, too thin to rank.", move="None pregame.", pers='Only if Dawkins plays.'),
 'Keon Coleman': dict(why="His share jumps against the blitz (18.6% vs 11.4%), but MIN allows the 6th-fewest WR yards. Net +1.", move=None),
 'DJ Moore': dict(why="No outside-target edge by location (MIN is 20th), and his share falls against the blitz. He has led BUF in targets in each full game. Net −1.", move=None),
 'Dalton Kincaid': dict(why="MIN allows the fewest TE catches (3.1 a game). No blitz split either. Net −1.", move=None),
 'Aaron Jones': dict(why="Outside runs are MIN's better side (4.94, 9th), and BUF allows 4.18 there. Net −1.", move=None),
}
c = json.load(open(W + 'final9/cards/BUF@MIN.json'))
c['kick'] = 'Mon 7:15 PM CT (MNF)'
c['market'] = "BUF −3.5 (Kalshi: BUF 64%, BUF by 4+ at 49¢), total 45.5 (50¢). Ladders re-checked Monday 2:39 PM CT: Wentz's passing median is about 213, Allen's 232, Cook's rushing 87, Jefferson's receiving 79."
c['lineup'] = ("MIN: Carson Wentz starts (Kyler Murray out, hamstring). WR Jauan Jennings (calf) and RB Demond Claiborne (knee) are out. Odell Beckham Jr. was signed to the active roster Sunday; S Jay Ward is questionable. "
               "BUF: WRs Joshua Palmer (hamstring) and Tyrell Shavers are out; CB Jordan Hancock is on IR (designated to return). OTs Dion Dawkins (ribs) and Alec Anderson (ankle) and DT Greg Gaines are questionable. "
               "Final actives post about 5:45 PM CT.")
c['branches'] = "If both BUF tackles sit, MIN's blitz gets home faster: that hurts Allen's passing more than the run game, which works inside behind the guards."
c['keys'] = [
 {'team': 'MIN', 'take': "BUF's inside run game.", 'how': "Win early downs with the blitz (72.8% of dropbacks, most by far) and keep the red zone shut: 4 TDs on 16 trips allowed.",
  'gives': "Light boxes (6.5 defenders on runs, 24th) against the league's best inside-run offense (52.8% success).", 'counter': "Cook between the guards, then Shakir in the middle against the pressure."},
 {'team': 'BUF', 'take': "Jefferson and the tight end, where Wentz throws.", 'how': "Wentz sent 34% of his targets to Jefferson and 34% to TEs. BUF allows the 4th-lowest share of targets to outside WRs.",
  'gives': "TE and RB volume: 9.1 TE targets (4th most) and 8.7 RB targets (most) a game.", 'counter': "Hockenson underneath. Wentz rarely throws to backs (10.5%, last), so the RB funnel goes unused."}]
c['scripts'] = {
 'control': "BUF leads behind Cook's inside runs. Wentz throws 30+ for the first time this season, into the defense that faces the 2nd-most attempts. Hockenson and Jefferson get volume.",
 'competitive': "A grinding game with MIN's red-zone defense (4 TDs on 16 trips) turning drives into field goals. Shakir's quick throws beat the blitz.",
 'reversal': "MIN leads, as in Wentz's two wins, and runs the clock. Allen chases against the blitz, which halves his scrambles."}
plays, passed, rows_csv = [], [], []
for o in A['res']:
    p, nm = o['pick'], o['name']; T = (PLAY if p else PASS)[nm]; pers = T.get('pers', '') or o['cond']
    if p:
        price_cond = f"Holds as a final line up to {p['final_at']}¢." if p['call'] == 'Final line' else f"Becomes a final line at {p['final_at']}¢ or less."
        plays.append({'decision': p['call'], 'player': o['player'], 'line': f"{o['player']} {thr(p, o['stat'])} ({p['side']})", 'thr': thr(p, o['stat']), 'side': p['side'], 'price': p['ask'],
                      'payout': p['pays'], 'be': p['be'], 'mkt': p['mkt'], 'est': [round(p['lo']), round(p['hi'])], 'lo': p['lo'], 'mid': p['mid'], 'hi': p['hi'], 'edge_lo': p['edge_lo'],
                      'edge_mid': p['edge_mid'], 'platform': 'Robinhood (Kalshi contract)', 'checked': AT, 'ticker': o['prefix'] + '-' + str(int(p['k'])), 'why': T['why'], 'support': T['support'],
                      'sample': sample_text(o, p) + ' ' + T['note'], 'counter': T['counter'], 'loses': T['loses'], 'cond': (pers + ' ' if pers else '') + price_cond, 'vs': vs_text(o),
                      'pts': o['pts'], 'shift': o['delta'], 'lens': o['ledger'], 'ladder': ladder_rows(o)})
    else:
        cl = o['closest']; why = T['why']
        if cl and o['delta'] != 0: why += f" Closest rung: {thr(cl, o['stat'])} ({cl['side']} {cl['ask']}¢, needs {cl['be']}%, ours {rng(cl)})."
        mv = T['move'] or (f"A price of {cl['lean_at']}¢ or less on {thr(cl, o['stat'])} makes it a lean." if cl else 'None pregame.')
        if pers: mv = pers + ' ' + mv
        passed.append({'name': f"{o['player']} {WORD[o['stat']]}", 'why': why, 'move': mv, 'thesis': True, 'lens': o['ledger']})
        if cl: rows_csv.append({'game': c['game'], 'decision': 'Pass', 'line': f"{o['player']} {thr(cl, o['stat'])} ({cl['side']})", 'side': cl['side'], 'price': cl['ask'], 'payout': cl['pays'],
                                'breakeven': cl['be'], 'market_mid': cl['mkt'], 'our_lo': cl['lo'], 'our_mid': cl['mid'], 'our_hi': cl['hi'], 'edge_lo': cl['edge_lo'], 'edge_mid': cl['edge_mid'],
                                'evidence_pts': o['pts'], 'shift': o['delta'], 'condition': mv, 'ticker': o['prefix'] + '-' + str(int(cl['k'])), 'checked': AT, 'result': '', 'grade_read': '', 'grade_price': ''})
plays.sort(key=lambda p: (p['decision'] != 'Final line', -(p['edge_lo'] if p['decision'] == 'Final line' else p['edge_mid'])))
for p in plays:
    rows_csv.append({'game': c['game'], 'decision': p['decision'], 'line': p['line'], 'side': p['side'], 'price': p['price'], 'payout': p['payout'], 'breakeven': p['be'], 'market_mid': p['mkt'],
                     'our_lo': p['lo'], 'our_mid': p['mid'], 'our_hi': p['hi'], 'edge_lo': p['edge_lo'], 'edge_mid': p['edge_mid'], 'evidence_pts': p['pts'], 'shift': p['shift'], 'condition': p['cond'],
                     'ticker': p['ticker'], 'checked': AT, 'result': '', 'grade_read': '', 'grade_price': ''})
cand = [o for o in A['res'] if o['delta'] != 0]
lk = []
for o in cand:
    r = sorted(o['rows'], key=lambda r: -r['mid'])[0]
    lk.append((r['mid'], f"{o['player']} {thr(r, o['stat'], True)} ({r['side']} {r['ask']}¢): ours {pct(r['mid'])}, needs {r['be']}%" + (' · clears' if r['edge_lo'] >= 0.5 else ' · priced at or past our number' if r['edge_mid'] < 0.5 else ' · clears only at our middle')))
c['likely'] = [f"{p['player']} {p['thr']} ({p['side']} {p['price']}¢): ours {pct(p['mid'])}, needs {p['be']}% · clears only at our middle" for p in sorted(plays, key=lambda p: -p['mid'])[:3]]
c['value'] = ['Nothing clears break-even at the low end of our number after fees.'] + [f"Closest: {p['line']} at {p['price']}¢ (needs {p['be']}%, ours {p['est'][0]}–{p['est'][1]}%), a conditional lean." for p in plays[:2]]
# keep Saturday's non-thesis passes that the lens didn't re-read
keep = [x for x in c['passed'] if not re.search(r'Cook|Wentz|Jefferson|Hockenson|Allen|Shakir|Mason|Jones|Addison|Moore|Kincaid|Coleman', x['name'])]
c['plays'], c['passed'] = plays, passed + [dict(x, thesis=False) for x in keep]

# ---------- the lens, for display ----------
B, M = LN['BUF_off'], LN['MIN_off']
def r_(d, k, most_word='most', few_word='fewest'):
    v = d[k]; n = v['of']; rk = v['rank']
    return f"{rk}{'st' if rk % 10 == 1 and rk != 11 else 'nd' if rk % 10 == 2 and rk != 12 else 'rd' if rk % 10 == 3 and rk != 13 else 'th'} {most_word}" if rk <= n / 2 else \
           f"{n + 1 - rk}{'st' if (n + 1 - rk) % 10 == 1 and (n + 1 - rk) != 11 else 'nd' if (n + 1 - rk) % 10 == 2 and (n + 1 - rk) != 12 else 'rd' if (n + 1 - rk) % 10 == 3 and (n + 1 - rk) != 13 else 'th'} {few_word}"
f1 = lambda x: f"{x:.1f}"; pc = lambda x: f"{100 * x:.1f}%"
def where(S):
    q, d = S['qb']['split'], S['def_ranks']
    out = []
    for b, key in (('Tight ends', 'TE'), ('Running backs', 'RB'), ('WRs outside', 'WR outside'), ('WRs in the middle', 'WR middle')):
        qv, dv = q[key], d['share_' + key]
        qhi, dhi = qv['v'] > qv['lg'], dv['v'] > dv['lg']
        verdict = 'Overlap' if (qhi and dhi) else ('QB only' if qhi else ('Defense only' if dhi else 'Neither'))
        out.append([b, f"{pc(qv['v'])} ({qv['rank']} of {qv['of']})", f"{pc(dv['v'])} ({dv['rank']} of {dv['of']})", verdict])
    return out
def facts(S):
    d = S['def_ranks']
    return [['Pass attempts faced', f1(d['pass_att_faced']['v']), r_(d, 'pass_att_faced')], ['Pass yards allowed', f1(d['pass_yds_allowed']['v']), r_(d, 'pass_yds_allowed')],
            ['Yards per carry allowed', f"{d['ypc_allowed']['v']:.2f}", r_(d, 'ypc_allowed')], ['WR yards allowed', f1(d['WR_yds']['v']), r_(d, 'WR_yds')],
            ['TE catches / yards allowed', f"{f1(d['TE_rec']['v'])} / {f1(d['TE_yds']['v'])}", r_(d, 'TE_yds')], ['RB catches / yards allowed', f"{f1(d['RB_rec']['v'])} / {f1(d['RB_yds']['v'])}", r_(d, 'RB_yds')],
            ['Sacks', f1(d['sacks']['v']), r_(d, 'sacks')], ['Blitz rate', pc(d['blitz_rate']['v']), r_(d, 'blitz_rate', 'highest', 'lowest')],
            ['Red-zone TDs allowed', f"{S['rz_tds']} of {S['rz_drives']} trips", r_(d, 'rz_td_rate', 'highest', 'lowest')]]
def runs(S):
    o, d = S['off_ranks'], S['def_ranks']
    return [[nm, f"{o['ypc_' + k]['v']:.2f} · {pc(o['sr_' + k]['v'])} ({r_(o, 'sr_' + k, 'best', 'worst')})", f"{d['ypc_' + k + '_allowed']['v']:.2f} · {pc(d['sr_' + k + '_allowed']['v'])} ({r_(d, 'sr_' + k + '_allowed', 'most', 'fewest')})", pc(o['share_' + k]['v'])]
            for nm, k in (('Inside (middle, guards)', 'inside'), ('Outside (tackles, ends)', 'outside'))]
def looks(S, opp_rate):
    return [[r['player'], pc(r['all']), pc(r['vs_blitz']), pc(r['vs_no_blitz']), ('+' if r['uptick'] >= 0 else '−') + f"{abs(100 * r['uptick']):.1f}"] for r in S['catchers']['rows'][:6]]
c['lens'] = {
 'title': 'The matchup lens',
 'how': ("The matchup lens reads a game in six steps: what each defense allows by position, where it lets the ball go against where the QB likes to throw, "
         "how each pass catcher's share changes against the look this defense shows, the run-scheme matchup, the closest comparable games, and how consistent each player is. "
         "Coverage and scheme charting isn't public for 2026, so two stand-ins are used: FTN's blitz charting for the coverage split, and run direction (inside vs outside) for run scheme. "
         "Each step that moves a line is scored in points at the market's median, and only the net goes into our number."),
 'thru': LN['thru'],
 'sides': [
  {'off': 'BUF', 'def': 'MIN', 'facts': facts(B), 'where': where(B), 'qb': 'Allen', 'looks': looks(B, 0), 'look_note': f"MIN blitzes on {pc(B['def_ranks']['blitz_rate']['v'])} of dropbacks (league {pc(LN['league_blitz'])}). Share = share of BUF targets; change = expected share against MIN's blitz rate minus his overall share.",
   'runs': runs(B), 'run_note': "BUF's inside run game is the best in the league by success rate. By direction, MIN is average inside (3.96) and soft outside (4.99, 9th most).",
   'comps': [f"MIN's most extreme trait is its blitz rate (z = {B['traits'][0]['z']}). BUF hasn't faced a top-3 blitz defense. On sacks, the closest defenses it has faced are HOU (Week 1) and DET (Week 2): Allen ran for 23 and 69, Kincaid had 130 and 95, DJ Moore 100 and 0."]},
  {'off': 'MIN', 'def': 'BUF', 'facts': facts(M), 'where': where(M), 'qb': 'Wentz', 'looks': looks(M, 0), 'look_note': f"BUF blitzes on {pc(M['def_ranks']['blitz_rate']['v'])} of dropbacks (7th). Splits are from all MIN games; with Wentz (2 starts): Jefferson 34% of targets, Hockenson 21%, Addison 18%.",
   'runs': runs(M), 'run_note': "MIN's inside run game is 30th in yards a carry and 31st in success rate; BUF holds inside runs to 3.90. No schematic edge for MIN.",
   'comps': ["Closest coverage match: Week 1 vs GB, with Wentz in a dome: Jefferson 9 targets, 8 catches, 92 yards, 2 TDs; Hockenson 5-4-36 and a TD.",
             "BUF's most extreme traits are the pass attempts it faces (38.3, z = 1.87) and its share of targets to RBs. The closest defenses MIN has faced: DET (Week 8, Jefferson 33, Hockenson 58) and MIA (Week 4, Hockenson 13 catches for 119), both with Murray."]}],
 'verdict': ("The deciding factor: BUF's run game against MIN's light, blitzing front, and Wentz's volume going to Jefferson and the tight end. "
             "The lens moved four lines to conditional leans (Hockenson, Cook, Shakir, Mason under) and took Saturday's Wentz-under lean off. Nothing clears at the low end of our number, so there's no final line."),
}
c['sources'] = [

 {'t': 'ESPN injury report, BUF and MIN, checked Mon Nov 9 2:42 PM CT', 'u': 'https://www.espn.com/nfl/injuries', 'k': 'Official'},
 {'t': 'AP via WAFB: Vikings sit Murray, will start Wentz (Nov 5)', 'u': 'https://www.wafb.com/2026/11/05/vikings-sit-murray-with-hamstring-strain-will-start-wentz-qb-against-bills-monday-night/', 'k': 'Reporting'},
 {'t': 'nflverse play-by-play 2026 through Week 9 Sunday, FTN charting through Week 8 (blitz, box)', 'u': 'https://github.com/nflverse/nflverse-data/releases', 'k': 'Logs'},
 {'t': 'Kalshi ladders (traded on Robinhood), every rung checked Mon 2:39 PM CT', 'u': 'https://kalshi.com', 'k': 'Market'}]
c['rerun'] = 'Re-run Monday 2:39 PM CT with live prices and the matchup lens.'
json.dump({'card': c, 'csv': rows_csv}, open(W + 'final9m/card_BUFMIN.json', 'w'), ensure_ascii=False)
print(len(plays), 'plays', len(passed), 'thesis passes', len(keep), 'kept')
for p in plays: print(' ', p['decision'], p['line'], p['price'], p['be'], p['est'], p['cond'])
for x in c['lens']['sides']: print(x['where']); print(x['runs']); print(x['facts'][:3])
print(c['likely'])
