"""Week 8 Sunday update (Sun Nov 1 ~10:50 AM CT): times, sources and injury notes. Runs after patch_w8d.py."""
B = '/home/claude/wedger/rh/'
s = open(B + 'page_template.html').read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, (old[:100], c); s = s.replace(old, new)
rep('Week 8 prices as of Thu Oct 29, 5:15 PM CT', 'Week 8 prices as of Sun Nov 1, 10:50 AM CT')
i = s.index('<p class="rs-note">Week 8, re-priced Thu Oct 29 ~5:15 PM CT.'); j = s.index('</p>', i) + 4
s = s[:i] + ('<p class="rs-note">Week 8, re-priced Sun Nov 1 ~10:50 AM CT (CAR @ GB was played Thursday and is off the board). Robinhood lists every remaining '
             'game\'s moneyline, spread and total ladders (plus 1st half / full time and overtime) and, through Kalshi\'s ladders, player props for all 13 games; '
             'Robinhood\'s price is shown and the sportsbooks\' consensus is the books\' price inside Wedger % (spreads, totals and moneylines from Caesars, '
             'DraftKings, FanDuel, BetRivers and BetMGM). Where Robinhood has no rung for a player, Robinhood-style rungs are priced from those five books, or their '
             'consensus line. Injuries: the official Friday game designations, with players ruled Out taken out of their teammates\' projections, plus Sunday-morning '
             'news (A.J. Brown and TreVeyon Henderson ruled out; Lamar Jackson active; Saquon Barkley expected to play; Breece Hall questionable). Weather: '
             'NFLWeather and RotoWire, Thursday. Hit rate = share of his 2026 games (Weeks 1–7) where the line came true. Wedger % = 85% the books\' price, 15% our '
             'read, then the Week 6–7 calibration and a small role-and-matchup adjustment (model v4). Role = how he is used. Momentum = his last 4 games vs his '
             'season. Click any player prop for the outlook. ★ = projected game total above 49.5.</p>') + s[j:]
rep("Every starter's main props with the line we expect (most are now on the Week 8 lines tab at real prices; Thu Oct 29):",
    "Every starter's main props with the line we expect (most are now on the Week 8 lines tab at real prices; Sun Nov 1):")
i = s.index('<p><b>Thursday update (Thu Oct 29).</b>'); j = s.index('</p>', i) + 4
s = s[:j] + ('\n    <p><b>Sunday update (Sun Nov 1).</b> Prices re-pulled from Robinhood, Kalshi and five sportsbooks at ~10:50 AM CT: 441 of the 487 lines priced '
             '45–55¢ are Robinhood\'s own. Injury statuses now use the official Friday designations (Out and Doubtful players removed from their teammates\' '
             'projections) and Sunday-morning news. CAR @ GB is off the board. Model, roles and the defense history are unchanged from Tuesday evening.</p>') + s[j:]
open(B + 'page_template.html', 'w').write(s)
print('w8e ok')
