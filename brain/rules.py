"""Wedge pick rules v2, from Week 12 (set Mon Nov 23, 2026), under the master prompt of Nov 23 (brain/Master_Prompt_2026-11-23.txt).

What changed from v1 (Weeks 7-11, which stay as posted and graded):
  v1 ranked lines by edge: Final = the low end of our number beats the price after fees, Lean = the middle does.
  v2 ranks lines by the chance the exact line settles a winner; price and value are separate and secondary.

Settings the owner chose Mon Nov 23 (session settings in the prompt's terms, so they can change week to week):
  CAP     a line priced above 75c is passed on price, however likely it is.
  QB      games with a backup quarterback are no longer left off; the change is a research factor (see qb_hold).
  MIX     no under/over quota: unders and overs compete on chance alone.
Wedge's own bars (the prompt has no fixed numbers, so these are Wedge's conversions, disclosed on the site):
  BAR     70%: Final = the low end of our range is 70%+, Lean = our middle is 70%+.
  Card    one line per player, up to four per game, best chance first (unchanged from v1).
The research checks (role, game script, late work) and the hand research still veto a line, as in v1."""
VERSION = 'v2'
SINCE = 'Week 12'
CAP = 75          # cents, the ask
BAR = 70          # percent chance
PER_GAME = 4
FEE = 2           # cents a contract, used only for the value read
VETO = ('ROLE', 'SCRIPT', 'LATE')
LBL = {'ROLE': 'role check', 'SCRIPT': 'game-script check', 'LATE': 'late-work check'}


def qb_hold(stat, backup):
    """A team starting a backup: its receiving lines can be at most a lean unless the backup started 2 of the team's last 3 games,
    so the role check's last-3 window already reflects him (the prompt: don't use a previous quarterback's behavior for the starter's).
    backup = None, or {'name': ..., 'recent': starts in the last 3, 'note': ...}. Returns the condition text, or ''."""
    if not backup or stat not in ('rec', 'recyd'): return ''
    if backup.get('recent', 0) >= 2: return ''
    return f"Only a lean while {backup['name']} starts: his team's catch logs mostly come from another quarterback."


def decide(x, stat, backup=None, status=''):
    """x: one rung and side, with ask (cents), lo/mid/hi (percent chance) and chk (research checks).
    status: the player's injury designation. -> (call, note); for a lean the note is its open condition."""
    c = x['chk']
    if x['mid'] < BAR: return 'Pass', ''
    fails = [n for n in VETO if not c[n]['pass']]
    if fails: return 'Pass', f"Likely enough (ours {x['lo']:.0f}–{x['hi']:.0f}%) but fails the " + ', '.join(LBL[f] for f in fails) + '.'
    if x['ask'] > CAP: return 'Pass', f"Likely enough (ours {x['lo']:.0f}–{x['hi']:.0f}%) but priced {x['ask']}¢, above the {CAP}¢ cap."
    hold = qb_hold(stat, backup)
    if status == 'Questionable': hold = (f"Only if he plays (questionable). " + hold).strip()
    if x['lo'] >= BAR and not hold: return 'Final line', ''
    if x['lo'] < BAR: hold = (hold + f" Our low end is {int(x['lo'])}%; a final needs {BAR}%.").strip()
    return 'Conditional lean', hold


def cond(x, call, note):
    """the condition line on a play"""
    if call == 'Final line': return f"Holds as a final line up to {CAP}¢ while the news holds."
    return note or f"Becomes a final line if the low end of our number reaches {BAR}%."


def vs(x, alt, thr_x, thr_alt):
    """one line against the player's strongest other rung"""
    if not alt: return ''
    if key(alt) <= key(x): d = 'this one is likelier'
    elif alt['ask'] > CAP: d = f"that one is likelier but priced above the {CAP}¢ cap"
    else: d = 'that one is likelier but fails a check'
    return f"Picked over {thr_alt} ({alt['side']} {alt['ask']}¢, ours {alt['lo']:.0f}–{alt['hi']:.0f}%): {d}."


def why_not(y, cap=CAP):
    """why a rung isn't the card line, for the alternatives table: chance first, then the checks, then the cap"""
    if y['mid'] < BAR: return f"Less likely: ours {y['lo']:.0f}–{y['hi']:.0f}%, under the {BAR}% bar."
    bad = [LBL[n] for n in VETO if not y['chk'][n]['pass']]
    if bad: return 'Likely enough but fails the ' + ', '.join(bad) + '.'
    if y['ask'] > cap: return f"Likelier (ours {y['mid']:.0f}%) but priced {y['ask']}¢, above the {cap}¢ cap."
    return f"Close: ours {y['lo']:.0f}–{y['hi']:.0f}%, a little less likely at the low end."


def passed_move(y):
    """what would put a passed player's closest rung on the card"""
    if y['ask'] > CAP: return f"Back in play if the price drops to {CAP}¢ or less."
    if y['mid'] < BAR: return f"Our number tops out at {y['mid']:.0f}% inside the {CAP}¢ cap; the card needs {BAR}%."
    return 'Re-check if the news changes.'


def key(x):
    """ranking key: the low end of our chance first, then the middle"""
    return (x['lo'], x['mid'])


def value(x):
    """the separate price read: ours (middle) against what the price needs after the fee. Never reorders the card."""
    be = x['ask'] + FEE; d = x['mid'] - be
    if d >= 0.5: return {'v': 'under', 't': f"Priced under our number: needs {be}%, ours {x['mid']:.0f}%."}
    if d > -0.5: return {'v': 'fair', 't': f"Priced at our number: needs {be}%, ours {x['mid']:.0f}%."}
    return {'v': 'over', 't': f"Priced above our number: needs {be}%, ours {x['mid']:.0f}%. Likely, but the price takes the edge."}


def closest(rows):
    """for a player with nothing on the card: his likeliest rung inside the cap that reaches the bar, else the cheapest one that
    does, else his likeliest rung inside the cap"""
    good = [y for y in rows if y['mid'] >= BAR]
    inside = [y for y in good if y['ask'] <= CAP]
    if inside: return max(inside, key=key)
    if good: return min(good, key=lambda y: y['ask'])
    return max([y for y in rows if y['ask'] <= CAP] or rows, key=key)


def alts(x, o, all_res, thr):
    """the alternatives table, by chance: nearest same-player rungs, the opposite side, his other markets and the strongest teammate
    doing the same kind of work (v1's version in finalN/brain_layer.py compared edges)"""
    out = []
    same = sorted([y for y in o['rows'] if y['side'] == x['side'] and y['k'] != x['k']], key=lambda y: abs(y['k'] - x['k']))[:2]
    opp = [y for y in o['rows'] if y['side'] != x['side'] and y['k'] == x['k']][:1]
    for y in same + opp:
        out.append({'line': f"{o['name']} {thr(y, o['stat'])} ({y['side']})", 'ask': y['ask'], 'be': y['be'], 'ours': f"{y['lo']:.0f}–{y['hi']:.0f}%", 'why': why_not(y)})
    for o2 in all_res:
        if o2 is o: continue
        if o2['name'] == o['name'] or (o2['team'] == o['team'] and ((o2['stat'] in ('rushyd', 'rryd')) == (o['stat'] in ('rushyd', 'rryd')))):
            y = closest(o2['rows'])
            w = (f"also makes the bar (ours {y['lo']:.0f}–{y['hi']:.0f}%), so it can sit on the card too." if y.get('call', 'Pass') != 'Pass' else why_not(y))
            pre = 'Same player, other market: ' if o2['name'] == o['name'] else 'Same team, same kind of work: '
            out.append({'line': f"{o2['name']} {thr(y, o2['stat'])} ({y['side']})", 'ask': y['ask'], 'be': y['be'], 'ours': f"{y['lo']:.0f}–{y['hi']:.0f}%", 'why': pre + w[0].lower() + w[1:]})
            if len(out) >= 5: break
    return out[:5]


def card(plays, keyf=lambda p: (p['lo'], p['mid'])):
    """one line per player, up to PER_GAME, finals first, best chance first. -> (keep, cut)"""
    plays = sorted(plays, key=lambda p: (p['decision'] != 'Final line', -keyf(p)[0], -keyf(p)[1]))
    seen, keep, cut = set(), [], []
    for p in plays:
        if p['player'] in seen or len(keep) >= PER_GAME: cut.append(p); continue
        seen.add(p['player']); keep.append(p)
    return keep, cut


ORDER = ('research', 'check', 'cap', 'limit', 'bar')


def reason(entry):
    """the passed-list reason group of a passed entry: its 'kind' tag, else read from its text"""
    if entry.get('kind') in ORDER: return entry['kind']
    t = (entry.get('why', '') + ' ' + entry.get('move', '')).lower()
    if 'research pass' in t: return 'research'
    if 'card limit' in t: return 'limit'
    if 'tops out' in t: return 'bar'
    if 'fails the' in t: return 'check'
    if 'cap' in t: return 'cap'
    return 'bar'


def kind(y):
    """the reason group for a passed player's closest rung"""
    if y['mid'] < BAR: return 'bar'
    if any(not y['chk'][n]['pass'] for n in VETO): return 'check'
    if y['ask'] > CAP: return 'cap'
    return 'research'


def order_passed(passed, n=8):
    """round-robin over the reason groups so the list shows each kind of pass, earliest-listed first within a group"""
    groups = {g: [x for x in passed if reason(x) == g] for g in ORDER}
    out = []
    while len(out) < n and any(groups.values()):
        for g in ORDER:
            if groups[g] and len(out) < n: out.append(groups[g].pop(0))
    return out


TEXT = {   # page copy for the method, one source for the site, the docs and the README
    'final': f"Final line: even the low end of our range gives it a {BAR}%+ chance, it passes every research check, and it costs {CAP}¢ or less.",
    'lean': f"Lean: our middle number gives it a {BAR}%+ chance and it passes every check, but the low end dips under {BAR}% or one named condition is open.",
    'passed': f"Considered and passed: likely enough by our number but failed a check or the research, priced above {CAP}¢, or a fifth line in one game.",
    'value': "Price comes second: each line shows what the price needs against our number, but that read never moves a line up or down the card.",
    'qb': "Games with a backup quarterback stay on the board; his team's receiving lines stay leans until he has started two of its last three games.",
}
