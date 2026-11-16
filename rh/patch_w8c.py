"""Week 8 Wednesday update (Wed Oct 28 ~2:31 PM CT): times, sources and injury notes. Runs after patch_w8b.py."""
B = '/home/claude/wedger/rh/'
s = open(B + 'page_template.html').read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, (old[:100], c); s = s.replace(old, new)
rep('Week 8 prices as of Tue Oct 27, 4:23 PM CT', 'Week 8 prices as of Wed Oct 28, 2:31 PM CT')
i = s.index('<p class="rs-note">Week 8, re-priced Tue Oct 27 ~4:23 PM CT.'); j = s.index('</p>', i) + 4
s = s[:i] + ('<p class="rs-note">Week 8, re-priced Wed Oct 28 ~2:31 PM CT. Robinhood lists every game\'s moneyline, spread and total ladders (plus 1st half / '
             'full time and overtime for 13 games) and, through Kalshi\'s ladders, player props for Thursday\'s CAR @ GB and most Sunday games (BAL @ BUF, MIN @ DET, '
             'NE @ MIA, IND @ JAX, TEN @ CIN, KC @ DEN, ATL @ TB, with a few more for LAC @ LAR and anytime TDs everywhere); Robinhood\'s price is shown and the '
             'sportsbooks\' consensus is the books\' price inside Wedger % (spreads, totals and moneylines from Caesars, DraftKings, FanDuel, BetRivers and BetMGM). '
             'Where Robinhood has no line yet (CHI @ SEA, CLE @ PIT, ARI @ DAL, LV @ NYJ, most of PHI @ WSH), Robinhood-style rungs are priced from those five books, '
             'or their consensus line. Injuries: the Packers\' and Panthers\' final Thursday report (Matthew Golden questionable after a limited Wednesday practice, '
             'back in his teammates\' projections; Jalen Coker and Bryce Young full; Panthers CB Akayleb Evans, OLB Jaelan Phillips and two guards out; Packers C Sean '
             'Rhyan, G Travis Glover and LB Zaire Franklin out). Sunday teams\' official reports were not out yet; statuses are from ESPN and Wednesday news (Lamar '
             'Jackson practicing and expected to play; Rashee Rice back at practice; Breece Hall limited; Amon-Ra St. Brown expected to play). Weather: NFLWeather and '
             'RotoWire, Wednesday afternoon. Hit rate = share of his 2026 games (Weeks 1–7) where the line came true. Wedger % = 85% the books\' price, 15% our read, '
             'then the Week 6–7 calibration and a small role-and-matchup adjustment (model v4). Role = how he is used. Momentum = his last 4 games vs his season. '
             'Click any player prop for the outlook. ★ = projected game total above 49.5.</p>') + s[j:]
rep("Every starter's main props with the line we expect (most Sunday props are now on the Week 8 lines tab too, at real prices):",
    "Every starter's main props with the line we expect (most are now on the Week 8 lines tab at real prices; Wed Oct 28):")
i = s.index('<p><b>Model v4, roles and the defense study (Tue Oct 27, evening).</b>'); j = s.index('</p>', i) + 4
s = s[:j] + ('\n    <p><b>Wednesday update (Wed Oct 28).</b> Prices re-pulled from Robinhood, Kalshi and five sportsbooks at ~2:31 PM CT: Robinhood now lists player '
             'props for most Sunday games, so 220 of the 408 lines priced 45–55¢ are Robinhood\'s own. Injury statuses updated from the Packers\' and Panthers\' final '
             'report and Wednesday news; weather re-pulled. Model, roles and the defense history are unchanged from Tuesday evening.</p>') + s[j:]
open(B + 'page_template.html', 'w').write(s)
print('w8c ok')
