"""Round 18 (Wed Nov 18): early lines on The Winning Edge.
Player markets Kalshi hasn't listed yet are priced from the sportsbooks (final11/book_ladders.py), run through the same
final-lines process as the card (final11/build.py writes each card's `early` list and the top-level `early` summary), and
shown below the card as early finals and leans, each with the most it can cost and still hold. The data stays in final.js
(served from lib/protected); only the renderer is in the page."""
V = '/home/claude/wedger/v2/'


def apply(s, js):
    def sr(a, b, n=1):
        nonlocal s
        c = s.count(a); assert c == n, f'r18 html: {a[:70]!r} found {c}'; s = s.replace(a, b)

    def jr(a, b, n=1):
        nonlocal js
        c = js.count(a); assert c == n, f'r18 js: {a[:70]!r} found {c}'; js = js.replace(a, b)
    sr('    <div id="fc-root"><p class="wx-empty">Loading the final card…</p></div>\n',
       '    <div id="fc-root"><p class="wx-empty">Loading the final card…</p></div>\n'
       '    <section class="v2-early" id="fc-early" aria-label="Early lines, priced from the sportsbooks" hidden></section>\n')
    # the Research note: Saturday noon's price checks, the books' role, and no leftover Week 9 lines
    sr("Every Week 11 line at any price (switch to 45–55¢ in the first menu), updated Tue Nov 17 at 6:23 AM CT. Where Robinhood has no line yet, the price comes from the sportsbooks.",
       "Every Week 11 line at any price (switch to 45–55¢ in the first menu). Kalshi prices checked Sat Nov 21 at 10:56 PM CT, with the card’s lines re-checked Sun Nov 22 at 10:10 AM CT; where Robinhood has no line yet, the price comes from eight sportsbooks, checked Sat at 10:57 PM CT.")
    sr("★ marks a high-scoring game. Thursday's JAX @ BAL is final, so its lines are off the board. Out: Sam Darnold, David Montgomery, A.J. Brown, Mike Evans, DeVonta Smith, Garrett Wilson (Sun) and Kyler Murray (Mon).",
       "★ marks a high-scoring game. Thursday's IND @ HOU is final (HOU 26, IND 3), so its lines are off the board. Injury designations: ESPN, Sat Nov 21 at 10:57 PM CT (Friday’s final designations plus Saturday’s moves and downgrades); lines for players ruled out are off the board.")
    k = s.rindex('</style>'); s = s[:k] + open(V + 'src/early.css').read() + s[k:]
    jr('  // ---------------- render ----------------', open(V + 'src/early.js').read() + '\n  // ---------------- render ----------------')
    jr("    if (id === 'final') requestAnimationFrame(() => fcRender());\n",
       "    if (id === 'final') requestAnimationFrame(() => { fcRender(); v2EarlyRender(); });\n")
    return s, js
