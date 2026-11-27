"""Round 23 (Fri Nov 27): the Sunday and Monday card under pick rules v3 with the research method Independent Sports Research v1.
- The v2 copy (round 21) now shows for a v3 card too (v2Rules() is true for 'v2' and 'v3'); v3Rules() adds the research and markets rows.
- The lede and the heading line add v3's second path: a line priced 50-75c under the 70% bar qualifies only when our number is
  significantly above what the price needs (brain/sig.py).
- A research pick in a market the model doesn't price (p.market_only) shows the market's number, labeled as the market's.
- The Research note's times: Sunday and Monday prices checked Fri Nov 27, 2:58 AM CT; Wednesday-Friday games keep Tuesday's card."""
import sys
sys.path.insert(0, '/home/claude/wedger/brain'); import rules as R
T = R.TEXT
q = lambda t: t.replace("\\", "\\\\").replace("'", "\\'")
CHK = 'Fri Nov 27 at 2:58 AM CT'
INJ = 'Fri Nov 27 at 3:01 AM CT'
OLD_HELPER = "function v2Rules() { return ((typeof window !== 'undefined' && window.WZ_FINAL) || {}).rules === 'v2'; }\n"
NEW_HELPER = ("function v2Rules() { const r = ((typeof window !== 'undefined' && window.WZ_FINAL) || {}).rules; return r === 'v2' || r === 'v3'; }\n"
              "function v3Rules() { return ((typeof window !== 'undefined' && window.WZ_FINAL) || {}).rules === 'v3'; }\n")
PATHB = (f"A line priced {R.FLOOR}–{R.CAP}¢ under the bar qualifies only when our number is significantly above what the price needs "
         "(95% confidence, judged on how much of our model’s edge has held up in graded weeks).")


def apply(s, js):
    def jr(a, b, n=1):
        nonlocal js
        c = js.count(a); assert c == n, f'r23 js: {a[:70]!r} found {c}'; js = js.replace(a, b)

    def sr(a, b, n=1):
        nonlocal s
        c = s.count(a); assert c == n, f'r23 html: {a[:70]!r} found {c}'; s = s.replace(a, b)
    jr(OLD_HELPER, NEW_HELPER)
    # the legend: the research method and its markets under v3
    jr(f"['Backup QBs', '{q(T['qb'])}']] : []),",
       f"['Backup QBs', '{q(T['qb'])}'], ...(v3Rules() ? [['Research', '{q(T['research'])}'], ['Markets', '{q(T['markets'])}']] : [])] : []),")
    # the lede and the heading line: v3's second path
    jr("and costs {CAP}¢ or less. A lean reaches".replace('{CAP}', str(R.CAP)),
       f"and costs {R.CAP}¢ or less. ' + (v3Rules() ? '{q(PATHB)} ' : '') + 'A lean reaches")
    jr(f"passes every research check and costs {R.CAP}¢ or less; price comes second.' : ''].filter(Boolean)",
       f"passes every research check and costs {R.CAP}¢ or less; price comes second.' + (v3Rules() ? ' {q(PATHB)}' : '') : ''].filter(Boolean)")
    # a research pick shows the market's number, labeled as such
    jr("lab.append('Our', document.createElement('br'), 'number');", "lab.append(p.market_only ? 'Market’s' : 'Our', document.createElement('br'), 'number');")
    jr("'our range' + (p.tier ?", "(p.market_only ? 'market range' : 'our range') + (p.tier ?")
    jr("`Our number ${Math.round(p.mid)}% (range", "`${p.market_only ? 'Market’s number' : 'Our number'} ${Math.round(p.mid)}% (range")
    jr("cell('Our number', fcNum(p), 'fc-us')", "cell(p.market_only ? 'Market’s number' : 'Our number', fcNum(p), 'fc-us')")
    # the Research note: this week's two price checks and the injury report
    sr("Kalshi prices checked Tue Nov 24 at 2:39 PM CT: player ladders are open for Wednesday’s, Thursday’s and Friday’s five games; Sunday and Monday ladders post later in the week.",
       f"Kalshi prices checked {CHK} for Sunday’s and Monday’s games; Wednesday’s through Friday’s five games keep Tuesday’s card (prices checked Tue Nov 24 at 2:39 PM CT).")
    sr("Injury designations: ESPN, Tue Nov 24 at 2:42 PM CT (Monday’s and Tuesday’s estimated practice reports; Wednesday’s game has its final designations); lines for players ruled out are off the board.",
       f"Injury designations: ESPN, {INJ} (Thursday’s practice reports; final designations post Friday afternoon); lines for players ruled out are off the board.")
    return s, js
