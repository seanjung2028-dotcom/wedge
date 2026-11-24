"""Round 22 (Tue Nov 24): the site moves to Week 12. Labels, the cert week and the price-check times move on by one.
"Since Week 10 (v6)" stays (v6 started then), and the pick-rules copy that names Weeks 7-11 stays as history.
Kalshi lists player ladders for Wednesday-Friday's five games so far; Sunday and Monday games show their game lines and
"Props soon" until their ladders open."""
import re
CHK = 'Tue Nov 24 at 2:39 PM CT'
INJ = 'Tue Nov 24 at 2:42 PM CT'


def apply(s, js):
    def jr(a, b, n=None):
        nonlocal js
        c = js.count(a); assert c >= 1 and (n is None or c == n), f'r22 js: {a[:70]!r} found {c}'; js = js.replace(a, b)

    def sr(a, b, n=1):
        nonlocal s
        c = s.count(a); assert c == n, f'r22 html: {a[:70]!r} found {c}'; s = s.replace(a, b)
    jr("const CERT_WEEK = 'w11';", "const CERT_WEEK = 'w12';", 1)
    jr("{ week: 11, game:", "{ week: 12, game:", 2)
    # no sportsbook pull yet this week: the early-lines block stays hidden rather than showing empty counts
    jr("if (!box || v2EarlyDone || !F || !F.early) return;", "if (!box || v2EarlyDone || !F || !F.early || !F.early.assessed) return;", 1)
    # the Research note: this pull's times, no Thursday game final yet, no book-priced lines this early in the week
    sr("Every Week 11 line at any price (switch to 45–55¢ in the first menu). Kalshi prices checked Sun Nov 22 at 10:32 AM CT; where Robinhood has no line yet, the price comes from eight sportsbooks, checked at 10:32 AM CT.",
       f"Every Week 11 line at any price (switch to 45–55¢ in the first menu). Kalshi prices checked {CHK}: player ladders are open for Wednesday’s, Thursday’s and Friday’s five games; Sunday and Monday ladders post later in the week.")
    sr("★ marks a high-scoring game. Thursday's IND @ HOU is final (HOU 26, IND 3), so its lines are off the board. Injury designations: ESPN, Sun Nov 22 at 10:31 AM CT (Friday’s final designations plus weekend moves and Sunday-morning reports); lines for players ruled out are off the board.",
       f"★ marks a high-scoring game. Injury designations: ESPN, {INJ} (Monday’s and Tuesday’s estimated practice reports; Wednesday’s game has its final designations); lines for players ruled out are off the board.")
    out = []
    for v in (s, js):
        v = v.replace('Since Week 10 (v6)', '@@SINCE@@').replace('Weeks 7–11', '@@HIST@@').replace('Weeks 7-11', '@@HIST2@@')
        v = re.sub(r'\bWeek 11\b', 'Week 12', v)
        v = v.replace('@@SINCE@@', 'Since Week 10 (v6)').replace('@@HIST@@', 'Weeks 7–11').replace('@@HIST2@@', 'Weeks 7-11')
        v = v.replace('Sun Nov 22 at 10:32 AM CT', CHK).replace('Sun Nov 22, 10:32 AM CT', 'Tue Nov 24, 2:39 PM CT')
        out.append(v)
    return out[0], out[1]
