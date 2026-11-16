"""Week 9 update (Tue Nov 3 ~6:20 PM CT): Week 9 board, model v5 (price shifted by each market's over bias), RFF projections,
Weeks 6-8 backtest write-up, cert week key fix, results tab Week 8. Runs after patch_w8f.py."""
B = '/home/claude/wedger/rh/'
s = open(B + 'page_template.html').read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, (old[:100], c); s = s.replace(old, new)
def para_at(marker, new):
    global s
    assert s.count(marker) == 1, (marker[:80], s.count(marker))
    i = s.index(marker); j = s.index('</p>', i) + 4; s = s[:i] + new + s[j:]

SIT_TITLE_OLD = ('title="Wedger’s chance it settles Yes: 85% the books’ no-vig price + 15% our model (usage cases, defense, coverage, game script, team total, weather, '
                 'recent role), re-fit Tue Oct 27 on 706 settled Week 6–7 lines (Yes premium by market). Chip = best side when it clears its price by 3+ pts: Yes +x, or No +x '
                 'when the Yes looks overpriced. Click for the outlook.">')
SIT_TITLE_NEW = ('title="Wedger’s chance it settles Yes (model v5): the price shown (Robinhood’s own, or Robinhood-style from the books), shifted by how often that market’s overs came true at their price on 1,333 settled '
                 'Week 6–8 lines (at 50¢: passing yards 55%, interceptions 53%, passing TDs 50%, receptions 48%, receiving yards 45%, rushing 42%, anytime TD 49%). Chip = best side when it clears its price by 3+ pts: '
                 'Yes +x, or No +x when the Yes looks overpriced. Click for the outlook.">')

# ---------- header, nav ----------
rep('Week 8 · Monday night re-priced Mon Nov 2, 3:15 PM CT', 'Week 9 prices as of Tue Nov 3, 6:20 PM CT')
rep('<div class="wg-dd-label" aria-hidden="true">Week 8</div>', '<div class="wg-dd-label" aria-hidden="true">Week 9</div>')
rep('data-page="lines">Week 8 lines</button>', 'data-page="lines">Week 9 lines</button>')
rep('data-page="proj">Week 8 projections</button>', 'data-page="proj">Week 9 projections</button>')

# ---------- lines tab ----------
para_at('<p class="rs-note">Week 8, Monday update:',
        '<p class="rs-note">Week 9, priced Tue Nov 3 ~6:20 PM CT from Robinhood (moneyline, spread and total ladders, 1st half / full time, overtime, and Kalshi\'s '
        'player-prop ladders) and five sportsbooks (Caesars, DraftKings, FanDuel, BetRivers, BetMGM). Kalshi lists player props for 13 of the 15 games so far '
        '(not yet TB @ CHI or BUF @ MIN), so 169 of the 381 lines priced 45–55¢ are Robinhood\'s own; the rest are Robinhood-style rungs priced from the sportsbooks '
        '(see Source). No official Week 9 practice reports are out yet, so injury notes use ESPN\'s current statuses; players ruled out are taken out of their '
        'teammates\' projections. Hit rate = share of his 2026 games (Weeks 1–8) where the line came true. Wedger % (model v5, new this week) = the price shown, '
        'shifted by how often that kind of line came true at its price in Weeks 6–8: passing-yard and interception overs more often, rushing and receiving-yard overs less. Our matchup read '
        'is still in the outlook, but it no longer moves Wedger % because the backtest found it pointed the wrong way (Methodology). Role = how he is used. '
        'Momentum = his last 4 games vs his season. Click any player prop for the outlook. ★ = projected game total above 49.5.</p>')
rep(SIT_TITLE_OLD, SIT_TITLE_NEW, 2)

# ---------- projections tab ----------
rep('<h2>Week 8 projections · player props before the lines post</h2>', '<h2>Week 9 projections · player props before the lines post</h2>')
para_at("<p class=\"rs-note\">Every starter's main props with the line we expect",
        "<p class=\"rs-note\">Every starter's main props with the line we expect (Tue Nov 3; many are already on the Week 9 lines tab at real prices): the weights "
        "books used on the real Week 6–7 lines (season average, last 4 games and the multi-season average), rounded to a half point. Proj. and Our read % now come from "
        "the random-features model (model v5, Methodology): a ridge regression on thousands of random non-linear transforms of his usage, efficiency, role, the spread, "
        "team total, the opposing defense and weather, trained on 2023–26 games. Walked forward week by week it beat the line estimate and our old projection. Wedger % "
        "is what v5 would show if the line posts at that number for 50¢: passing yards 55%, receptions 48%, receiving yards 45%, rushing 42%, so it reflects the market's "
        "Weeks 6–8 bias, not the player. Anytime TD prices vary by player, so their Wedger % is our read with the TD calibration. Last-4 read = last week's read "
        "with his last 4 games weighted most. Click a row for the outlook.</p>")
rep('title="Yards and catches: Wedger % if the line posts at this number for 50¢ (85% price + 15% our read, then the Week 6–7 calibration). Anytime TDs: our read with '
    'the TD calibration. Click for the outlook.">',
    'title="Yards and catches: Wedger % if the line posts at this number for 50¢ (model v5: 50¢ shifted by how often that market’s overs came true at their price in '
    'Weeks 6–8). Anytime TDs: our read with the TD calibration. Click for the outlook.">')
rep('title="Our model alone: usage cases, defense, coverage, game script, team total, weather and recent role. On real prices it hasn\'t beaten the market by itself.">',
    'title="The random-features model’s chance of the over at the expected line (anytime TDs: our usage-case read). On real Weeks 6–8 lines it beat the line only on '
    'passing yards, so treat it as a lean, not an edge.">')

# ---------- defense, ATD ----------
rep('Teams playing in Week 8 are in bold. Through Week 7.</p>', 'Teams playing in Week 9 are in bold. Through Week 8.</p>')
para_at("<p class=\"rs-note\">Robinhood's Yes price (Tue Oct 27 ~10:11 AM CT;",
        "<p class=\"rs-note\">Robinhood's Yes price (Tue Nov 3 ~6:20 PM CT) where Robinhood lists the player; otherwise the sportsbook average (average implied chance "
        "of Yes at DraftKings, FanDuel, BetMGM and Caesars). Wedger % = our chance he scores (model v5): the price, shifted slightly down because anytime TDs "
        "came true a little less often than their price in Weeks 6–8; click a player for the outlook. ★ = projected game total above 49.5. Usage comes from 2026 "
        "play-by-play, Weeks 1–8. Values in green are in the top quarter of the league-wide pool. Every box is a minimum; set it to 0 to switch it off.</p>")

# ---------- charts ----------
rep('<h2>Week 8 board · season hit rate vs price</h2>', '<h2>Week 9 board · season hit rate vs price</h2>')
rep('Each dot is a Week 8 line priced 45–55¢, placed by its price and by how often its condition came true in Weeks 1–7.',
    'Each dot is a Week 9 line priced 45–55¢, placed by its price and by how often its condition came true in Weeks 1–8.')
rep("tip: [`${r.segment} · Weeks 1–7`", "tip: [`${r.segment} · Weeks 1–8`")
rep("const PERIODS = ['Wk 1', 'Wk 2', 'Wk 3', 'Wk 4', 'Wk 5', 'Wk 6', 'Wk 7', '2023–25'];",
    "const PERIODS = ['Wk 1', 'Wk 2', 'Wk 3', 'Wk 4', 'Wk 5', 'Wk 6', 'Wk 7', 'Wk 8', '2023–25'];")

# ---------- methodology ----------
rep("The favorite is the side with the higher Robinhood moneyline (Tue Oct 27 ~10:11 AM CT). Player props Robinhood doesn't list use the Robinhood-style rungs "
    "priced from the sportsbooks described on the Week 8 lines tab.",
    "The favorite is the side with the higher Robinhood moneyline (Tue Nov 3 ~6:20 PM CT). Player props Robinhood doesn't list use the Robinhood-style rungs "
    "priced from the sportsbooks described on the Week 9 lines tab.")
i = s.index('<p><b>Monday update (Mon Nov 2).</b>'); j = s.index('</p>', i) + 4
s = s[:j] + (
    '\n    <p><b>Model v5 and the Weeks 6–8 backtest (Tue Nov 3).</b> We settled every Week 8 line we posted (894 lines across all 15 games, from nflverse box '
    'scores and snap counts) and re-tested the model on all 1,333 settled Week 6–8 player lines at real prices, holding out one week at a time. Seven problems '
    'turned up. (1) Our matchup read pointed the wrong way: how far it leaned from the price was negatively correlated with how lines settled in every week '
    '(−0.03, −0.04, −0.08; −0.29 on rushing). (2) We calibrated the blend of market and read when the price itself was the better thing to calibrate: shifting the '
    'Robinhood price by its market\'s over bias scored a Brier of 0.2460 held out, vs 0.2471 for last week\'s model and 0.2493 for the raw price (Week 8 alone: '
    '0.2459 vs 0.2510). (3) Receptions were lumped in with receiving yards, and passing TDs and interceptions with passing yards; at about 50¢ receptions came true 48% of '
    'the time, receiving yards 45%, rushing 39–42%, passing yards 62%, interceptions 56% and passing TDs 50%. (4) Our projections missed by more than the line itself (average miss on real lines: rushing 25.4 yards vs 21.7 for the line, receiving 24.4 vs '
    '23.2, passing 58.2 vs 56.3). (5) Thursday prices for Sunday games scored worse than Sunday-morning prices (0.2164 vs 0.2098), and late moves kept going rather '
    'than reversing; the Sunday re-price was built but never went live. (6) Picks per pull ballooned (59, 167, 275) as Kalshi\'s ladders grew, and bigger edges '
    'didn\'t win more often than small ones. (7) The certification key still said Week 7, so four Week 8 certified picks never settled; fixed, and they now show '
    'under Week 8 on the Results tab.</p>\n'
    '    <p><b>What changed.</b> Wedger % = the price shown (Robinhood\'s own, or Robinhood-style from the books) shifted in log-odds by its market\'s over bias (passing yards +0.22, interceptions +0.13, passing TDs +0.01, '
    'receptions −0.08, receiving yards −0.19, rushing −0.31, anytime TD −0.02), fit on Weeks 6–8 with shrinkage; our read is still shown in the outlook. Held out a week at a time, its picks (3+ pts vs '
    'the price) went 283–208 (57.6%), +12.9% before fees; the Wedger picks actually posted in Weeks 6–8 went 248–190 (56.6%), +4.0%. Projections: we took the '
    'random-features ridge regression from Kelly, Malamud and Zhou\'s “The Virtue of Complexity in Return Prediction” (AQR; Journal of Finance 2024) and AQR\'s '
    '“Understanding the Virtue of Complexity” (2025): 3,000 random sine/cosine transforms of the inputs, fit with heavy ridge shrinkage and averaged over five '
    'draws, which picks up non-linear effects without hand-picking them. It is trained on 2023–26 player games to predict how far he lands from a book-style line, '
    'using recent volume and efficiency, his usage profile (target and carry share, depth of target), role, the spread and team total, the opposing defense\'s '
    'coverage, blitz and run-defense numbers, his offense\'s pass rate, and weather. Walked forward, it beat our old projection on passing, receiving and rushing '
    'yards and added 2–6% of explained variance over the book-style line. On real lines it improved only passing (average miss 54.7 vs 56.3 for the line), so the '
    'best estimate is the line moved toward it by a weight fit on Weeks 6–8: passing all the way, receptions half, receiving yards a quarter, rushing not at all. We '
    'also checked Moskowitz\'s “Asset Pricing and Sports Betting” (AQR), which finds sportsbook line moves overreact and partly reverse; on Kalshi\'s Week 8 props the '
    'moves continued, so v5 doesn\'t fade them. Three weeks is a small sample: the shifts are estimates and will move as more weeks settle.</p>') + s[j:]
rep("Wedger % is 85% market and 15% our read (70/30 before Week 8), then the Week 6–7 calibration by market.",
    "Since Week 9 (model v5), Wedger % is the market price shifted by its market's over bias on Weeks 6–8 and our read is shown for reference (Week 8: 85% market "
    "and 15% our read; before that 70/30).")
rep('(2026 through Week 7)', '(2026 through Week 8)')
rep('NFLWeather and RotoWire forecasts (Week 8)', 'NFLWeather and RotoWire forecasts (Week 9)')

# ---------- outlook ----------
rep("the Wedger chance is 85% market + 15% our read, re-fit Tue Oct 27 on 706 settled Week 6–7 lines (Yes premium by market);",
    "since Week 9 the Wedger chance is the market price shifted by its market’s over bias on 1,333 settled Week 6–8 lines (model v5), and our read is shown, not used;")
rep("No price yet. Our read alone: ${pctR(100 * O.P)}",
    "No price yet. Our read alone${O.rff != null && !isTd ? ` (random-features model, projection ${fmtStat(stat, O.rff)})` : ''}: ${pctR(100 * O.P)}")
rep("Wedger would be about ${pctR(P)}: 85% the price + 15% our read, then the Week 6–7 calibration (passing overs have come true more often than their price, rushing overs less)${rmPts(O, P) ? ` and ${rmPts(O, P)} for his role and spot` : ''}.",
    "Wedger would be about ${pctR(P)}: model v5 shifts the price by how often these overs came true at their price in Weeks 6–8 (passing yards more often, rushing and receiving yards less).")
V5_WORD = "({ passyd: 'passing-yard', passtd: 'passing-TD', int: 'interception', rushyd: 'rushing-yard', rryd: 'rushing', recyd: 'receiving-yard', rec: 'reception', td: 'anytime-TD' })[stat] || 'these'"
rep("      : O.cal === 'v4'\n        ? `Wedger = 85% market + 15% our read",
    "      : O.cal === 'v5'\n        ? `Wedger (model v5) = the price shown${O.P_price != null ? ` (${pctR(100 * O.P_price)})` : ''}, shifted by how often ${" + V5_WORD + "} overs came true at their "
    "price on 1,333 settled Week 6–8 lines (${O.shift5 >= 0 ? '+' : '−'}${Math.abs(O.shift5 || 0).toFixed(2)} in log-odds: at 50¢ that is ${pctR(100 / (1 + Math.exp(-(O.shift5 || 0))))}). "
    "Our matchup read${O.P_v4 != null ? ` (${pctR(100 * O.P_v4)} under last week’s model)` : ''} no longer moves the number: in the backtest it pointed the wrong way."
    "${O.rff != null && !isTd ? ` Random-features projection ${fmtStat(stat, O.rff)}${O.proj_best != null ? `; best estimate ${fmtStat(stat, O.proj_best)}` : ''}.` : ''}"
    "${O.P_l4 != null ? ` Last-4 view: ${pctR(100 * O.P_l4)}.` : ''} ${pickTxt}Yes = ${cond}.`\n"
    "      : O.cal === 'v4'\n        ? `Wedger = 85% market + 15% our read")
rep("c2.append(rng, lab, el('p', 'wg-note', 'Dots: bear, base and bull averages after the adjustments below. Diamond: the projection. Dashed: the line.'));",
    "c2.append(rng, lab, el('p', 'wg-note', 'Dots: bear, base and bull averages after the adjustments below. Diamond: the projection. Dashed: the line.' + "
    "(O.cal === 'v5' && !isTd && O.proj_best != null ? ` Best estimate (v5): ${fmtStat(stat, O.proj_best)}. In Weeks 6–8 the line was closer to the result than this "
    "projection, so the best estimate starts at the line and moves toward the random-features projection (${fmtStat(stat, O.rff)}) only as far as tested best.` : '')));")

# ---------- certification + results ----------
rep("const CERT_WEEK = 'w7';", "const CERT_WEEK = 'w9';")
rep('<select class="rr-week" aria-label="Week"><option value="7">Week 7</option><option value="6">Week 6</option></select>',
    '<select class="rr-week" aria-label="Week"><option value="8">Week 8</option><option value="7">Week 7</option><option value="6">Week 6</option></select>')
rep("const rs = { wk: 7, show: 'q',", "const rs = { wk: 8, show: 'q',")
rep("(rs.wk === 7 && r.market === 'Anytime Touchdown')", "(rs.wk >= 7 && r.market === 'Anytime Touchdown')")
para_at('<p class="rs-note">Week 7: every line posted, all 14 games settled',
        '<p class="rs-note">Weeks 7 and 8: every line posted, every game settled from the final box scores and snap counts (nflverse; Week 8 on Tue Nov 3); '
        'anytime TDs at any price under “Anytime TD filter picks”. The group records above are Week 6; the Charts tab has every week. “Wedger certified only” lists '
        'every pick you certified that week, including picks priced outside 45–55¢.</p>')

rep("put(keyOfLine(r), { week: 7, game: r.game,", "put(keyOfLine(r), { week: 9, game: r.game,")
rep("put(keyOfAtd(r), { week: 7, game: r.game,", "put(keyOfAtd(r), { week: 9, game: r.game,")
rep("const weeks = ['1', '2', '3', '4', '5', '6', '7'];", "const weeks = [...new Set(rows.map((r) => String(r.week)))].sort((a, b) => a - b);")
rep('<h3 class="wg-h3">All seven weeks together</h3>', '<h3 class="wg-h3">All eight weeks together</h3>')
rep("Weeks 1–5 are game lines only (Robinhood didn't keep prop prices); Weeks 6–7 add quarters, halves and player props.", "Weeks 1–5 are game lines only (Robinhood didn't keep prop prices); Weeks 6–8 add quarters, halves and player props.")

open(B + 'page_template.html', 'w').write(s)
print('w9 ok')
