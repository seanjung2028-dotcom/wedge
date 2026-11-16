"""Week 8 Thursday update (Thu Oct 29 ~5:15 PM CT): times, sources and injury notes. Runs after patch_w8c.py."""
B = '/home/claude/wedger/rh/'
s = open(B + 'page_template.html').read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, (old[:100], c); s = s.replace(old, new)
rep('Week 8 prices as of Wed Oct 28, 2:31 PM CT', 'Week 8 prices as of Thu Oct 29, 5:15 PM CT')
i = s.index('<p class="rs-note">Week 8, re-priced Wed Oct 28 ~2:31 PM CT.'); j = s.index('</p>', i) + 4
s = s[:i] + ('<p class="rs-note">Week 8, re-priced Thu Oct 29 ~5:15 PM CT. Robinhood lists every game\'s moneyline, spread and total ladders (plus 1st half / '
             'full time and overtime) and, through Kalshi\'s ladders, player props for all 14 games; Robinhood\'s price is shown and the sportsbooks\' consensus is '
             'the books\' price inside Wedger % (spreads, totals and moneylines from Caesars, DraftKings, FanDuel, BetRivers and BetMGM). Where Robinhood has no rung '
             'for a player yet, Robinhood-style rungs are priced from those five books, or their consensus line. Injuries: CAR @ GB uses the final report (Matthew '
             'Golden questionable after a limited Wednesday; Jalen Coker and Bryce Young full; Panthers CB Akayleb Evans, OLB Jaelan Phillips and two guards out; '
             'Packers C Sean Rhyan, G Travis Glover and LB Zaire Franklin out){INACT}. Sunday and Monday teams: the official Wednesday practice report plus Thursday news '
             '(Jahmyr Gibbs and Amon-Ra St. Brown back to full practice; Jaylen Waddle limited; Rashee Rice and Emeka Egbuka limited again; Stefon Diggs full; '
             'Ja\'Marr Chase back after a rest day; Saquon Barkley and DeVonta Smith missed both days). Game designations come Friday. Weather: NFLWeather and '
             'RotoWire, Thursday afternoon. Hit rate = share of his 2026 games (Weeks 1–7) where the line came true. Wedger % = 85% the books\' price, 15% our read, '
             'then the Week 6–7 calibration and a small role-and-matchup adjustment (model v4). Role = how he is used. Momentum = his last 4 games vs his season. '
             'Click any player prop for the outlook. ★ = projected game total above 49.5.</p>') + s[j:]
rep("Every starter's main props with the line we expect (most are now on the Week 8 lines tab at real prices; Wed Oct 28):",
    "Every starter's main props with the line we expect (most are now on the Week 8 lines tab at real prices; Thu Oct 29):")
i = s.index('<p><b>Wednesday update (Wed Oct 28).</b>'); j = s.index('</p>', i) + 4
s = s[:j] + ('\n    <p><b>Thursday update (Thu Oct 29).</b> Prices re-pulled from Robinhood, Kalshi and five sportsbooks at ~5:15 PM CT: Kalshi now lists player props '
             'for every Week 8 game (LV @ NYJ, CLE @ PIT, ARI @ DAL, PHI @ WSH and CHI @ SEA were added), so 380 of the 459 lines priced 45–55¢ are Robinhood\'s own. '
             'Injury notes now use the official Wednesday practice report for every Sunday team (defenders too, on the Matchup tab), with Thursday news on top; '
             'weather re-pulled. Model, roles and the defense history are unchanged from Tuesday evening.</p>') + s[j:]
import json, os
INF = B + 'inactives_cargb.json'
inact = json.load(open(INF))['text'] if os.path.exists(INF) else ''
s = s.replace('{INACT}', inact)
open(B + 'page_template.html', 'w').write(s)
print('w8d ok', bool(inact))
