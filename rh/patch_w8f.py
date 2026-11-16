"""Week 8 Monday update (Mon Nov 2 ~3:15 PM CT): CHI @ SEA re-priced; finished games keep Thursday's posted numbers. Runs after patch_w8d.py (replaces the unpublished Sunday patch_w8e)."""
B = '/home/claude/wedger/rh/'
s = open(B + 'page_template.html').read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, (old[:100], c); s = s.replace(old, new)
rep('Week 8 prices as of Thu Oct 29, 5:15 PM CT', 'Week 8 · Monday night re-priced Mon Nov 2, 3:15 PM CT')
i = s.index('<p class="rs-note">Week 8, re-priced Thu Oct 29 ~5:15 PM CT.'); j = s.index('</p>', i) + 4
s = s[:i] + ('<p class="rs-note">Week 8, Monday update: CHI @ SEA re-priced Mon Nov 2 ~3:15 PM CT from Robinhood (moneyline, spread and total ladders, 1st half / full '
             'time, overtime, and Kalshi\'s player-prop ladders) and five sportsbooks (Caesars, DraftKings, FanDuel, BetRivers, BetMGM), with the final injury report: '
             'Bears RB Kyle Monangai out and TE Cole Kmet on injured reserve; Seahawks WR Rashid Shaheed, RB Velus Jones Jr. and LT Charles Cross out; Zach Charbonnet off the report '
             'for his season debut. Players ruled out are taken out of their teammates\' projections. Games already played (CAR @ GB Thursday and every Sunday game) '
             'keep the numbers they were posted with on Thu Oct 29 ~5:15 PM CT; tick “Hide games that have kicked off” to see Monday night alone. Robinhood\'s price is '
             'shown and the sportsbooks\' consensus is the books\' price inside Wedger %. Hit rate = share of his 2026 games (Weeks 1–7) where the line came true. '
             'Wedger % = 85% the books\' price, 15% our read, then the Week 6–7 calibration and a small role-and-matchup adjustment (model v4). Role = how he is used. '
             'Momentum = his last 4 games vs his season. Click any player prop for the outlook. ★ = projected game total above 49.5.</p>') + s[j:]
rep("Every starter's main props with the line we expect (most are now on the Week 8 lines tab at real prices; Thu Oct 29):",
    "Every starter's main props with the line we expect (most are now on the Week 8 lines tab at real prices; Thu Oct 29, CHI @ SEA re-run Mon Nov 2):")
i = s.index('<p><b>Thursday update (Thu Oct 29).</b>'); j = s.index('</p>', i) + 4
s = s[:j] + ('\n    <p><b>Monday update (Mon Nov 2).</b> CHI @ SEA re-priced at ~3:15 PM CT from Robinhood, Kalshi and five sportsbooks, with the Bears\' and Seahawks\' '
             'final injury report and the current rosters. Every game already played keeps its Thursday Oct 29 numbers, so the board shows what was posted before '
             'kickoff. Model, roles and the defense history are unchanged from Tuesday evening.</p>') + s[j:]
open(B + 'page_template.html', 'w').write(s)
print('w8f ok')
