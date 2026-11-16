"""Week 9 Saturday refresh (Sat Nov 7 ~2:25 PM CT): JAX @ BAL is final and off the board; the 14 Sunday/Monday games are
re-priced from Robinhood, Kalshi and five sportsbooks with every team's final injury report and fresh forecasts."""
import re
P = '/home/claude/wedger/rh/index.html'
s = open(P).read()

def rep(a, b, n=None):
    global s
    c = s.count(a)
    assert c and (n is None or c == n), (a[:80], c)
    s = s.replace(a, b)

rep('<span data-wg-count="lines">430</span> at 45–55¢ · <span data-wg-count="every">5,722</span> at any price<br>Priced Wed Nov 4, 3:37 PM CT',
    '<span data-wg-count="lines">496</span> at 45–55¢ · <span data-wg-count="every">6,393</span> at any price<br>Priced Sat Nov 7, 2:25 PM CT', 1)
rep('updated Wed Nov 4 at 3:37 PM CT', 'updated Sat Nov 7 at 2:25 PM CT', 2)
rep('Out: Lamar Jackson and Tyler Huntley (Thu), Sam Darnold and David Montgomery (Sun).',
    "Thursday's JAX @ BAL is final, so its lines are off the board. Out: Sam Darnold, David Montgomery, A.J. Brown, Mike Evans, "
    'DeVonta Smith, Garrett Wilson (Sun) and Kyler Murray (Mon).', 1)
rep('Every starter, before the books post<br>Re-run Wed Nov 4', 'Every starter, before the books post<br>Re-run Sat Nov 7', 1)
rep('Red-zone usage, target share, TD rate<br>Priced Wed Nov 4', 'Red-zone usage, target share, TD rate<br>Priced Sat Nov 7', 1)
rep('higher Robinhood moneyline (Wed Nov 4 ~3:37 PM CT)', 'higher Robinhood moneyline (Sat Nov 7 ~2:25 PM CT)', 1)

# methodology: the Saturday paragraph goes right after Wednesday's
i = s.index('<p><b>Wednesday update (Wed Nov 4).</b>'); j = s.index('</p>', i) + 4
s = s[:j] + ('\n    <p><b>Saturday update (Sat Nov 7).</b> Thursday\'s JAX @ BAL is final (Jaguars 33–10), so its lines are off the board. '
             'The 14 Sunday and Monday games were re-priced at ~2:25 PM CT from Robinhood (70 game-line events), Kalshi\'s player-prop '
             'ladders (now all 14 games, BUF @ MIN included) and five sportsbooks, so 448 of the 496 lines priced 45–55¢ are Robinhood\'s own. '
             'Injury notes use every team\'s final report (Friday; the Bills and Vikings through Saturday: Kyler Murray and Jauan '
             'Jennings are out for Monday) and ESPN\'s latest news; weather re-pulled from game-day forecasts. Model, roles and the '
             'defense history are unchanged.</p>') + s[j:]

for bad in ('Wed Nov 4, 3:37', 'Wed Nov 4 at 3:37', 'Lamar Jackson and Tyler Huntley (Thu)'):
    assert bad not in s, bad
open(P, 'w').write(s)
print('patched Saturday refresh')
