"""Round 21 (Mon Nov 23): the page copy for pick rules v2 (brain/rules.py), shown only when the card's data says rules 'v2'.
From Week 12, Finals and Leans are ranked by the chance the exact line hits (price cap 75c, 70% bar), price second.
Weeks 7-11 were picked by edge over the price (v1), so every switch keeps the v1 text for a v1 card."""
import sys
sys.path.insert(0, '/home/claude/wedger/brain'); import rules as R
T = R.TEXT
q = lambda t: t.replace("\\", "\\\\").replace("'", "\\'")
HELPER = "function v2Rules() { return ((typeof window !== 'undefined' && window.WZ_FINAL) || {}).rules === 'v2'; }\n"
LEDE_V2 = ("Every Sunday and Monday game, run through the final-lines process. For every player we had a read on, every threshold on the ladder was priced "
           f"and ranked by how likely it is to hit. A final line has a {R.BAR}%+ chance even at the low end of our number, passes every research check and costs "
           f"{R.CAP}¢ or less. A lean reaches {R.BAR}% at our middle, or has one named condition open. Price comes second: each line shows what the price needs "
           "against our number, but that never moves a line up or down. Everything else is passed, with the reason.")


def apply(s, js):
    def jr(a, b, n=1):
        nonlocal js
        c = js.count(a); assert c == n, f'r21 js: {a[:70]!r} found {c}'; js = js.replace(a, b)
    js = HELPER + js
    jr("['Final line', 'Our low end beats Needs by 0.5+ points.'],",
       f"['Final line', v2Rules() ? '{q(T['final'])}' : 'Our low end beats Needs by 0.5+ points.'],")
    jr("['Conditional lean', 'Our middle beats Needs by 0.5+. Final at the price or condition shown.'],",
       f"['Conditional lean', v2Rules() ? '{q(T['lean'])}' : 'Our middle beats Needs by 0.5+. Final at the price or condition shown.'],")
    jr("['Pass', 'Nothing beats Needs at our middle.'],",
       f"['Pass', v2Rules() ? '{q(T['passed'])}' : 'Nothing beats Needs at our middle.'], ...(v2Rules() ? [['Price', '{q(T['value'])}'], ['Backup QBs', '{q(T['qb'])}']] : []),")
    jr("const lede = el('p', 'fc-lede', \"Every Sunday and Monday game",
       f"const lede = el('p', 'fc-lede', v2Rules() ? '{q(LEDE_V2)}' : \"Every Sunday and Monday game")
    jr("else s7.append(el('p', 'fc-none', 'Nothing clears break-even. Pass.'));",
       f"else s7.append(el('p', 'fc-none', v2Rules() ? 'Nothing reaches a {R.BAR}% chance at {R.CAP}¢ or less. Pass.' : 'Nothing clears break-even. Pass.'));")
    jr("lst('Best at the quoted price', 'Clears break-even at our low end', c.value)",
       "lst(v2Rules() ? 'Price check' : 'Best at the quoted price', v2Rules() ? 'What the price needs against our number; it never moves a line' : 'Clears break-even at our low end', c.value)")
    jr("`Nothing in ${g} clears break-even. Pass.`",
       f"(v2Rules() ? `Nothing in ${{g}} reaches a {R.BAR}% chance at {R.CAP}¢ or less. Pass.` : `Nothing in ${{g}} clears break-even. Pass.`)")
    jr("c.plays.length ? null : 'No line cleared break-even. Closest calls:');",
       "c.plays.length ? null : (v2Rules() ? 'No line reached the card. Closest calls:' : 'No line cleared break-even. Closest calls:'));")
    jr("el('p', 'wx-empty', 'Nothing clears break-even at the expected prices yet.')",
       f"el('p', 'wx-empty', v2Rules() ? 'Nothing reaches a {R.BAR}% chance at {R.CAP}¢ or less at the expected prices yet.' : 'Nothing clears break-even at the expected prices yet.')")
    # ranking: chance first under v2 (the low end for finals, the middle for leans)
    jr("const fcE = (p) => (p.decision === 'Final line' ? p.edge_lo : p.edge_mid);",
       "const fcE = (p) => (v2Rules() ? (p.decision === 'Final line' ? p.lo : p.mid) : (p.decision === 'Final line' ? p.edge_lo : p.edge_mid));")
    jr("|| b[1].edge_mid - a[1].edge_mid);",
       "|| (v2Rules() ? b[1].mid - a[1].mid : b[1].edge_mid - a[1].edge_mid));")
    # the Winning Edge heading: under v2, one line on how the card is ranked
    jr("(v2F() || {}).draft ? `${v2F().draft}: finals and leans as of ${fcTime(v2F().at)}. Leans below; each one names what it needs.` : null));",
       "([(v2F() || {}).draft ? `${v2F().draft}: finals and leans as of ${fcTime(v2F().at)}. Leans below; each one names what it needs.` : '', "
       f"v2Rules() ? 'Ranked by the chance each line hits. A final line has a {R.BAR}%+ chance even at the low end of our number, passes every research check and costs {R.CAP}¢ or less; price comes second.' : ''].filter(Boolean).join(' ') || null)));")
    jr("'Only markets with three or more books are priced. Quarterback rule, research checks and the one-under-per-three-overs mix apply as on the card. ",
       f"'Only markets with three or more books are priced. ' + (v2Rules() ? 'Research checks, the {R.BAR}% bar and the {R.CAP}¢ cap apply as on the card. ' : 'Quarterback rule, research checks and the one-under-per-three-overs mix apply as on the card. ') + '")
    return s, js
