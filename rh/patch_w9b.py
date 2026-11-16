"""Week 9 Wednesday refresh (Wed Nov 4 ~3:37 PM CT): new prices, Wednesday injury news, every-line view text.
Runs after patch_w9.py."""
B = '/home/claude/wedger/rh/'
s = open(B + 'page_template.html').read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, (old[:100], c); s = s.replace(old, new)

rep('Week 9 prices as of Tue Nov 3, 6:20 PM CT', 'Week 9 · priced Wed Nov 4, 3:37 PM CT')
rep("Week 9, priced Tue Nov 3 ~6:20 PM CT from Robinhood", "Week 9, re-priced Wed Nov 4 ~3:37 PM CT from Robinhood")
i = s.index('Kalshi lists player props for 13 of the 15 games so far'); j = s.index("are Robinhood's own;", i) + len("are Robinhood's own;")
s = s[:i] + "Kalshi lists player props for 14 of the 15 games (not yet BUF @ MIN), so 259 of the 430 lines priced 45–55¢ are Robinhood's own;" + s[j:]
i = s.index("No official Week 9 practice reports are out yet, so injury notes use ESPN"); j = s.index("projections.", i) + len("projections.")
s = s[:i] + ("Injury notes use ESPN's current statuses and Wednesday's practice news (Lamar Jackson and Tyler Huntley are out Thursday, "
             "Sam Darnold and David Montgomery are out Sunday); players ruled out are taken out of their teammates' projections.") + s[j:]
rep("(Tue Nov 3; many are already on the Week 9 lines tab at real prices)", "(re-run Wed Nov 4; many are already on the Week 9 lines tab at real prices)")
rep("Robinhood's Yes price (Tue Nov 3 ~6:20 PM CT)", "Robinhood's Yes price (Wed Nov 4 ~3:37 PM CT)")
rep("higher Robinhood moneyline (Tue Nov 3 ~6:20 PM CT)", "higher Robinhood moneyline (Wed Nov 4 ~3:37 PM CT)")
i = s.index('<p><b>Model v5 and the Weeks 6–8 backtest (Tue Nov 3).</b>')
s = s[:i] + ('<p><b>Wednesday update (Wed Nov 4).</b> Every Week 9 game re-priced at ~3:37 PM CT from Robinhood (73 game-line events), '
             "Kalshi's player-prop ladders (now 14 games; TB @ CHI added) and five sportsbooks, with ESPN's current injury statuses and "
             "Wednesday's practice news; weather re-pulled. The Lines tab now has an every-line view: all 5,722 Week 9 lines at any price, "
             "each with its 2026 hit rate. Inside 45–55¢ nothing changed about how Wedger % or picks work. Outside it, Wedger % applies the "
             "same market shifts, which were fit on lines priced 40–60¢, so it is a rough guide there and no picks are made. One fix: the "
             "situational splits had been reading last week's injury file, so this week's outs (for example a team's starting QB) were "
             "missed in the QB and lineup splits; they now read Week 9's.</p>\n    ") + s[i:]
open(B + 'page_template.html', 'w').write(s)
print('w9b ok')
