"""Round 7 copy pass: every description on the site, short and to the point.
MARK rewrites apply to the page markup, JS rewrites to the page script. Each must match."""

MARK = [
    # Home: the method steps and the fine print
    ('How often the line came true in his games this season, and how he is used.', 'His hit rate this season and his role.'),
    ('The defense, the game script, the weather and the injury report, all in the full read.', 'Defense, game script, weather and injuries.'),
    ("Wedge % against Robinhood's price. A read needs a 3-point edge.", 'Wedge % vs the price. A read needs a 3-point edge.'),
    ('Wedge is football research, not financial advice. Prices move and reads lose; every figure is before fees.', 'Research, not financial advice. Figures are before fees.'),
    # Research: the projections view
    ("Every starter's main props before the books post them. Line is where we expect books to open; Proj. is our projection. Wedge % is our chance he clears that line if it opens at 50¢, so it mostly reflects how that market has priced overs. Select any row to open its file.",
     'Main props before books post them. Line: our expected opener. Proj.: our projection. Wedge %: our chance he clears it.'),
    # Charts
    ('Which roles and game spots cleared the line books would set. “Held” means the spot also beat its 2023–25 average, so it is less likely to be luck. Overs at these lines hit about 45% overall.',
     'Roles and spots that cleared the book line. “Held” = also beat its 2023–25 average. Overs hit about 45% overall.'),
    ('A projection is volume times efficiency. Volume follows recent games; efficiency is mostly noise, so it needs a long window. We tested both on every 2023–26 player-game.',
     'Projection = volume × efficiency. Volume follows recent games; efficiency needs a long window.'),
    ('Win % of the Yes side each week (game lines only in Weeks 1–5; props from Week 6). Hover a point for the record and return.', 'Yes win % by week. Hover for record and return.'),
    ("How often overs cleared a book-style line, week by week. Green beats that week's average; rows that stay green are the steady edges.", "Overs vs a book-style line, by week. Green beats the week's average."),
    ('Across 23,000 player-games, a hot or cold last four games barely carries forward. A change in role or volume does.', 'Hot or cold streaks barely carry forward. Role changes do.'),
    ('Each offense in its first four games (hollow) and its last four (filled), adjusted for opponents. Team momentum has carried little into the next game, and books have overreacted to recent scoring.',
     'First four games (hollow) vs last four (filled), opponent-adjusted. Team momentum carries little.'),
    ('Every Robinhood line that cost 45–55¢ at its last trade before kickoff, Weeks 1–5. A bar past the dark tick hit more often than its average price implied.', '45–55¢ lines, Weeks 1–5. Past the tick = hit more than its price implied.'),
    ('Tick factors to split the same lines into every combination of them. Groups below the minimum size are hidden.', 'Tick factors to combine them. Small groups are hidden.'),
    ('Hit rate for each pair of factors. Green is above 50%, red below; the deeper the color, the further from 50%.', 'Hit rate by pair of factors. Green above 50%, red below.'),
    ('Week 6 lines from the 45–55¢ screen, settled, by group.', 'Week 6, 45–55¢ lines, by group.'),
    ('Each dot is a Week 9 line: its price against how often it came true. Dots above the diagonal hit more often than they cost.', 'Price vs hit rate for each Week 9 line. Above the diagonal = hit more than it cost.'),
    # Analysts, Apply
    ('Each pick counts as one contract at its listed price. Win % and profit count settled picks only; standings go by win %, then profit.', 'One contract per pick at its listed price. Settled picks only; ranked by win %, then profit.'),
    ("Applying opens your email app with your application filled in, so you just hit send. We'll reply by email.", 'Opens your email app with the application filled in.'),
    # Results
    ('Week 6 win rate · lines that hit &gt;50%', 'Week 6 win rate · hit &gt;50%'),
    ('Return buying every one at its price', 'Return at the price'),
    ('Rest of the 45–55¢ lines (hit 50% or less)', 'Rest of 45–55¢ lines'),
    ('Lines that hit 75–99% this season', 'Hit 75–99% this season'),
    ('Week 6 lines from the 45–55¢ screen, settled. Return is the profit from buying one Yes of each at its listed price, before fees. One week is a small, noisy sample.', 'Week 6, 45–55¢ lines. Return: one Yes each, before fees.'),
    ('Every Week 7 and 8 line we posted, settled from the final box scores. “Wedge certified only” shows certified picks at any price. Charts has every week.', 'Every Week 7–8 line, settled from box scores.'),
    # NBA
    ('…that hit in more than half of the last 20 games', 'Hit &gt;50% of last 20 games'),
    ('Filter 4,738–4,945 (−2.5%); model 48.4% (−1.3%) on 37,519 2025-26 lines', 'Backtest: filter −2.5%, model −1.3%'),
    ("NBA lines from Robinhood for Oct 24–27 games, priced Fri Oct 23 at 11:40 PM CT. Hit rate is his last 20 games; Books % is the sportsbooks' fair chance; Wedge % is our chance it hits. Select a player prop for the full read.",
     "Robinhood NBA lines, Oct 24–27. Hit rate: last 20 games. Books %: sportsbooks' chance. Wedge %: ours."),
    ('No NBA slate has been run through the final-lines process yet.', 'No NBA final card yet.'),
    ('When one is, its final lines, conditional leans and passes appear here with the same record as the NFL card: line and price, why it’s on the card, evidence, where it loses and the decision.', 'It will appear here in the NFL card’s format.'),
    ('The NBA thesis opens with the first NBA final card.', 'Opens with the first NBA final card.'),
    ('Each game will get its keys, its three scripts and the thesis behind every line on the card.', 'Keys, scripts and the thesis behind every line.'),
    ("37,519 closing player props from the 2025-26 season, with sportsbook prices standing in for Robinhood's, settled from box scores. Every input uses only games played before that night.", '37,519 closing 2025-26 player props at sportsbook prices, settled from box scores.'),
    ('Over the 2025-26 season the &gt;50% filter won 48.9% of lines and the model 48.4%; both lost money before fees (−2.5% and −1.3%). In the NBA the price is the signal: use the screen and the read to understand a line, not as an edge.',
     'Filter 48.9%, model 48.4%; both lost money (−2.5%, −1.3%). In the NBA, the price is the signal.'),
    ('Dot = how often the Yes came true; tick = average price paid. Green = hit more often than it cost (made money), red = less often.', 'Dot: hit rate. Tick: average price. Green made money.'),
    ('The same two strategies, split by stat. Return on the right.', 'By stat. Return on the right.'),
    ('Every backtest line, bucketed by Wedge % (and by price alone). On the dashed line = the chance was right.', 'By Wedge % and by price. On the dashed line = right.'),
    ('Gain over a coin flip in Brier score (lower Brier is better), every line in the sample.', 'Brier gain over a coin flip.'),
    ('Projection error (average miss): book line 3.1, his average 3.28, minutes cases 3.26, adjusted projection 3.26.', 'Average miss: book line 3.1, his average 3.28, our projection 3.26.'),
    ('Analyst picks are tracked for the NFL so far.', 'NFL only, for now.'),
    ('NBA picks will be filed and settled the same way once analysts start posting them.', 'NBA picks will be tracked the same way.'),
    ('Every NBA line we listed at 45–55¢, settled from the final box score. Return is the profit from buying one Yes at the posted price, before fees. Two nights is a small sample; the season backtest below is the bigger test.',
     'Every 45–55¢ NBA line, settled from box scores. Return: one Yes each, before fees.'),
    ('Filter, model and every line for each market. Return on the right.', 'By market. Return on the right.'),
    ('Settled props bucketed by Wedge % (and by price), 5-point buckets with 5+ props. On the dashed line = the chance was right.', 'By Wedge % and by price. On the dashed line = right.'),
    # Soccer
    ('Soccer gets the same treatment as the NFL and NBA: every Robinhood line priced 45–55¢ across the top leagues and MLS, with the full read and a backtest.', 'Every 45–55¢ Robinhood line in the top leagues and MLS, with the full read.'),
]

JS = [
    # Home: the live example in the method
    ("'His last four games against his season. The defense, game script and weather are in the full read'", "'Last four games vs his season'"),
    # The Winning Edge
    ("'Nothing on any ladder in this game clears break-even at the middle of our number, at any price. Pass on this game.'", "'Nothing clears break-even. Pass.'"),
    ("'Highest chance by our number, any threshold, any price'", "'By our number'"),
    ("'Clears break-even after fees at the low end of our number'", "'Clears break-even at our low end'"),
    ("'Postgame grading: every line, passes included, is logged at its pre-kickoff price, then graded on the read and on the price.'", "'Every line is logged before kickoff and graded after the game.'"),
    # Charts: the research and momentum notes
    ("`${b.label}: volume is predicted best with a half-life of ${+b.value} games; efficiency with ${+b.value2 >= 1000 ? 'every game weighted equally' : `a half-life of ${+b.value2} games`} (${b.note}). Lower is better; the dip shows where recent games stop helping. ${fmt(+b.n)} player-games, 2024–26.`",
     "`${b.label}: volume works best over ${+b.value} games, efficiency over ${+b.value2 >= 1000 ? 'every game' : `${+b.value2} games`}. Lower is better. ${fmt(+b.n)} player-games.`"),
    ("`After an opponent beat his own usual by 40+ yards against that defense, the next player beat his usual by ${(+g1.value).toFixed(1)} (n ${g1.n}) vs ${(+g0.value).toFixed(1)} otherwise.`",
     "`After a 40+ yard game against a defense, the next player beat his usual by ${(+g1.value).toFixed(1)} (vs ${(+g0.value).toFixed(1)}).`"),
    ("` When that big game came mostly before contact (blocking), the next back gained ${(+gb.value).toFixed(1)}; when it came after contact (the runner), ${(+gr.value).toFixed(1)}.`",
     "` Before-contact games carry over (${(+gb.value).toFixed(1)}); after-contact ones less (${(+gr.value).toFixed(1)}).`"),
    ("' Bars: how much of what a defense allowed per game (vs each opponent’s own usual) showed up for the next player, 2023–26.'", "''"),
    ("`Tested on the 706 real Week 6–7 lines (Brier, lower is better; fit on one week, tested on the other): ${vtxt}. Adding the role-and-matchup history (fit on 2023–25 only): ${rb ? (+rb.value).toFixed(4) : ''} → ${rr ? (+rr.value).toFixed(4) : ''}. The books' price is still the hardest number to beat; what helps most is knowing which roles and spots the books misprice.`",
     "`Brier on 706 real Week 6–7 lines (lower is better): ${vtxt}. With role and matchup: ${rb ? (+rb.value).toFixed(4) : ''} → ${rr ? (+rr.value).toFixed(4) : ''}. The price is still hardest to beat.`"),
    ("`Model variants on real prices, fit on one week and tested on the other (Brier score, lower is better; Week 7, then Week 6): ${V.map((r) => `${r.label} ${(+r.value).toFixed(4)} / ${(+r.value2).toFixed(4)}`).join(' · ')}. Books’ Week 6–7 lines weighed receiving yards ${wtxt(bk('recyd'))} (season / last 4 / multi-season, R² ${bk('recyd').value2}); the weights that best predicted 2023–24 games were ${wtxt(best('recyd'))}. For receptions books used ${wtxt(bk('rec'))} vs best ${wtxt(best('rec'))}; rushing yards ${wtxt(bk('rushyd'))} vs ${wtxt(best('rushyd'))}.`",
     "`Brier, Week 7 / Week 6 (lower is better): ${V.map((r) => `${r.label} ${(+r.value).toFixed(4)} / ${(+r.value2).toFixed(4)}`).join(' · ')}.`"),
    ("    const vtxt = V.map((r) => `${r.label} ${(+r.value).toFixed(4)}`).join(' · ');",
     "    const vtxt = (() => { const ok = V.filter((r) => isFinite(+r.value)), bst = ok.slice().sort((a, b) => a.value - b.value)[0], pr = ok.find((r) => /price/i.test(r.label)); return bst ? `best ${bst.label} ${(+bst.value).toFixed(4)}` + (pr && pr !== bst ? `, price alone ${(+pr.value).toFixed(4)}` : '') : ''; })();"),
    # The research file (full outlooks)
    ("'Dots: bear, base and bull averages after the adjustments below. Diamond: the projection. Dashed: the line.' + (O.cal === 'v5' && !isTd && O.proj_best != null ? ` Best estimate (v5): ${fmtStat(stat, O.proj_best)}. In Weeks 6–8 the line was closer to the result than this projection, so the best estimate starts at the line and moves toward the random-features projection (${fmtStat(stat, O.rff)}) only as far as tested best.` : '')",
     "'Dots: bear, base, bull. Diamond: projection. Dashed: the line.' + (O.cal === 'v5' && !isTd && O.proj_best != null ? ` Best estimate: ${fmtStat(stat, O.proj_best)}.` : '')"),
    ("`How often the over cleared the line books would set for players in these spots. All ${SIT_WORD[stat] || ''} props: ${bs != null ? pct1(bs) : '—'} in 2026, ${bh != null ? pct1(bh) : '—'} in 2023–25 (green = 3+ pts better, red = 3+ worse).${rmPts(O, P) ? ` Together these move Wedge % by ${rmPts(O, P)}.` : ''}`",
     "`Overs vs the book line in these spots. All ${SIT_WORD[stat] || ''} props: ${bs != null ? pct1(bs) : '—'} in 2026, ${bh != null ? pct1(bh) : '—'} in 2023–25.${rmPts(O, P) ? ` Moves Wedge % by ${rmPts(O, P)}.` : ''}`"),
    ("`Every ${grp} who faced ${tname(opp)} in 2026, against his own usual (the line books would have set for him). Green bar = same role as ${O.team ? 'this player' : 'him'}. ` +",
     "`Every ${grp} vs ${tname(opp)} in 2026, against his usual. Green = same role. ` +"),
    ("'Extra carries a defense allows and yards before contact (its front and the blocking it faces) have carried into the next game; yards after contact and one long run belong to the runner and mostly have not. '", "'Carries and yards before contact carry over; after contact mostly doesn’t. '"),
    ("'Pass defense is mostly a team-level effect; it carries over a little. '", "'Carries over a little. '"),
    ("'For receivers, what one player did against a defense has told us almost nothing about the next one (2023–26), so this weighs very little. '", "'For receivers this barely carries over. '"),
    ("`Tick = league average (${P0.lg}). Green = allows more than average.`", "`Tick: league average (${P0.lg}).`"),
]
FOOT = [
    ("foot: 'How it works: usage cases are his games since 2023 split into thirds by volume", "foot: 'Usage cases: his games since 2023, split by volume. Projection: case average × this week’s adjustments. Wedge %: the price shifted by its market’s over bias. Treat edges under 5 points as noise.' },"),
    ('foot: "How it works: minutes cases are his games since 2025-26', "foot: 'Minutes cases: his games since 2025-26, split by minutes. Wedge %: 70% books’ price + 30% our read. Treat gaps under 5 points as noise.' },"),
]
FC_HOW = """    how.append(fcDl([
      ['Needs', 'Price plus up to 2¢ in fees. A 40¢ Yes needs 42%.'],
      ['Market', 'Bid–ask midpoint on each live Kalshi rung (spread 8¢ or less).'],
      ['Our number', 'The market’s curve, shifted by role, matchup, script and personnel.'],
      ['Final line', 'Our low end beats Needs by 0.5+ points.'],
      ['Conditional lean', 'Our middle beats Needs by 0.5+. Final at the price or condition shown.'],
      ['Pass', 'Nothing beats Needs at our middle, or the evidence is thin.'],
      ['Games hit', 'His 2026 games that reached the threshold.'],
      ['Times', `Prices ${fcTime(F.at)}. Books ${fcTime(F.books_at)}. Inactives post 90 minutes before kickoff.`],
    ]));
"""

def apply(s, js):
    for a, b in MARK:
        n = s.count(a); assert n >= 1, ('markup', a[:70]); s = s.replace(a, b)
    for a, b in JS:
        n = js.count(a); assert n >= 1, ('js', a[:70]); js = js.replace(a, b)
    for a, b in FOOT:  # these entries run to the end of their line
        i = js.index(a); j = js.index('\n', i); js = js[:i] + b + js[j:]
    i = js.index('    how.append(fcDl(['); j = js.index(']));\n', i) + len(']));\n'); js = js[:i] + FC_HOW + js[j:]
    return s, js
