"""Week 8 page update: Week 8 lines + projections, momentum filter, week-by-week backtests, momentum study, v3 text."""
B = '/home/claude/wedger/rh/'
s = open(B + 'page_template_w7final.html').read()
def rep(old, new, count=1, first=False):
    global s
    c = s.count(old); assert c == count, (old[:90], c); s = s.replace(old, new, 1) if first else s.replace(old, new)

# ---------- header, nav ----------
rep('<span class="wg-sub">Prices as of Sun Oct 25, 11:56 AM CT (DAL @ PHI: Mon 1:31 PM) · Robinhood first',
    '<span class="wg-sub">Week 8 prices as of Tue Oct 27, 10:11 AM CT · Robinhood first')
rep('<div class="wg-dd-label" aria-hidden="true">Week 7</div>', '<div class="wg-dd-label" aria-hidden="true">Week 8</div>')
rep('data-page="lines">Week 7 lines</button>', 'data-page="lines">Week 8 lines</button>\n        <button type="button" class="wg-dd-item" role="menuitem" data-page="proj">Week 8 projections</button>')
rep("const NFL_PAGES = new Set(['lines', 'cat-1',", "const NFL_PAGES = new Set(['lines', 'proj', 'cat-1',")

# ---------- lines tab ----------
i = s.index('<p class="rs-note">Prices as of Sun Oct 25 ~11:56 AM CT, just before the early kickoffs;'); j = s.index('</p>', i) + 4
s = s[:i] + ('<p class="rs-note">Week 8, priced Tue Oct 27 ~10:11 AM CT. Robinhood already lists every game\'s moneyline, spread and total ladders (and Thursday\'s '
             'CAR @ GB player props through Kalshi\'s ladders); for those, Robinhood\'s price is shown and the sportsbooks\' consensus is the books\' price inside Wedger % '
             '(spreads from 8 books and Kalshi, moneylines from DraftKings and Kalshi, totals from DraftKings, each turned into a fair chance for every rung). '
             'Sunday\'s player props are mostly not posted yet: only MIN @ DET and a few anytime TDs have sportsbook lines (Robinhood-style rungs priced from '
             'DraftKings, FanDuel, BetMGM, Caesars and BetRivers); the rest are on Week 8 projections until they post. Injuries: ESPN\'s status as of Tue morning '
             'plus Monday news (Jalen Hurts and Terry McLaurin out for the season; Lamar Jackson, Saquon Barkley, Aaron Jones and Jaylen Waddle questionable); '
             'official practice reports start Wednesday. Weather: NFLWeather and RotoWire forecasts, Tue morning. Hit rate = share of his 2026 games (Weeks 1–7) '
             'where the line came true. Wedger % = 85% the books\' price, 15% our read, re-fit Tue Oct 27 (see Charts). Momentum = his last 4 games vs his season: '
             'role (snap share ±10 pts), volume (targets / carries ±15%) or efficiency alone; role moves have carried into the next game, efficiency spikes haven\'t. '
             'Click any player prop for the outlook. ★ = projected game total above 49.5. Rows for games that have kicked off are dimmed.</p>') + s[j:]
MOMSEL = ('<select class="{cls}" aria-label="Momentum">\n          <option value="">Any momentum</option>\n          <option value="Role up">Role up (snaps +10)</option>\n'
          '          <option value="Volume up">Volume up</option>\n          <option value="Stable">Stable</option>\n          <option value="Hot efficiency">Hot efficiency only</option>\n'
          '          <option value="Cold efficiency">Cold efficiency only</option>\n          <option value="Volume down">Volume down</option>\n          <option value="Role down">Role down (snaps −10)</option>\n'
          '          <option value="view">Last-4 view beats price by 3+</option>\n        </select>')
rep('''          <option>Player props</option>
        </select>
        <label><input type="checkbox" class="rs-clean"> Hide flagged</label>''', '''          <option>Player props</option>
        </select>
        ''' + MOMSEL.format(cls='rs-mom') + '''
        <label><input type="checkbox" class="rs-clean"> Hide flagged</label>''')
MOMTH = '<th data-field="mom_type" class="rs-hide-narrow"><button data-k="mom_type" title="His last 4 games vs his 2026 season. Role = snap share moved 10+ pts; Volume = targets / carries moved 15%+; Efficiency = yards per target / carry moved 15%+ with volume flat. Hover a chip for the numbers and the last-4 view (the model with his last 4 games weighted most).">Momentum</button></th>'
rep('''            <th data-field="hits" class="num"><button data-k="hits">Hits</button></th>
            <th data-field="games" class="num"><button data-k="games">Games</button></th>
            <th data-field="sample" class="rs-hide-narrow">''', '''            ''' + MOMTH + '''
            <th data-field="hits" class="num"><button data-k="hits">Hits</button></th>
            <th data-field="games" class="num"><button data-k="games">Games</button></th>
            <th data-field="sample" class="rs-hide-narrow">''', count=2, first=True)
WT = "Wedger’s chance it settles Yes: 85% the books’ no-vig price + 15% our model (usage cases, defense, coverage, game script, team total, weather, recent role), re-fit Tue Oct 27 on 706 settled Week 6–7 lines (Yes premium by market)."
rep("Wedger’s chance it settles Yes: 70% the books’ no-vig price + 30% our model (usage cases, defense, coverage, game script, team total, weather), recalibrated on settled Week 6–7 lines (Yes premium by market).", WT, 2)
rep('Teams playing in Week 7 are in bold.', 'Teams playing in Week 8 are in bold. Through Week 7.')
i = s.index("<p class=\"rs-note\">Robinhood's Yes price (Sun Oct 25 ~11:56 AM CT; DAL @ PHI Mon ~1:31 PM) where Robinhood lists the player;")
rep("Robinhood's Yes price (Sun Oct 25 ~11:56 AM CT; DAL @ PHI Mon ~1:31 PM) where Robinhood lists the player", "Robinhood's Yes price (Tue Oct 27 ~10:11 AM CT; Thursday's CAR @ GB only so far) where Robinhood lists the player")
rep("Wedger % = our chance he scores: 70% the books' no-vig price, 30% our read", "Wedger % = our chance he scores: 85% the books' no-vig price, 15% our read")
rep('Usage comes from 2026 play-by-play, Weeks 1–6.', 'Usage comes from 2026 play-by-play, Weeks 1–7. Most Sunday anytime-TD prices post later this week.')
rep('<h2>Week 7 board · season hit rate vs price</h2>', '<h2>Week 8 board · season hit rate vs price</h2>')
rep('<p class="rs-note">Each dot is a Week 7 line priced 45–55¢, placed by its price and by how often its condition came true in Weeks 1–6.',
    '<p class="rs-note">Each dot is a Week 8 line priced 45–55¢, placed by its price and by how often its condition came true in Weeks 1–7.')
rep('<p class="rs-note">Week 7: every line posted through Sunday night, settled from the final box scores (DAL @ PHI settles after Monday night);',
    '<p class="rs-note">Week 7: every line posted, all 14 games settled from the final box scores (nflverse, Tue Oct 27);')

# ---------- projections page ----------
PROJ = '''
  <!-- ============ WEEK 8 PROJECTIONS ============ -->
  <div class="rs-page" id="proj" hidden>
    <section class="rs-card" id="proj-card">
      <h2>Week 8 projections · player props before the lines post</h2>
      <p class="rs-note">Books hadn't posted most Sunday player props on Tuesday morning, so this is every starter's main props with the line we expect: the weights books used on the real Week 6–7 lines (season average, last 4 games and the multi-season average), rounded to a half point. Projection and Our read % are the model alone (usage cases, defense, coverage, game script, team total, weather, recent role). Wedger % is what it would show if the line posts at that number for 50¢ (85% price + 15% our read, then the Week 6–7 calibration), so it mostly reflects the market: passing overs about 56%, receiving about 45%, rushing about 40%. Anytime TD prices vary by player, so their Wedger % is our read with the TD calibration. On real prices our read alone hasn't beaten the market, so treat this as a watch list until the lines post. Last-4 read = our read with his last 4 games weighted most. Click a row for the outlook.</p>
      <div class="rs-controls">
        <select class="pj-game" aria-label="Game"></select>
        <select class="pj-mkt" aria-label="Market"><option value="">All markets</option><option>Passing Yards</option><option>Rushing Yards</option><option>Receiving Yards</option><option>Receptions</option><option>Anytime Touchdown</option></select>
        <select class="pj-pos" aria-label="Position"><option value="">All positions</option><option>QB</option><option>RB</option><option>WR</option><option>TE</option></select>
        ''' + MOMSEL.format(cls='pj-mom').replace('<option value="view">Last-4 view beats price by 3+</option>', '<option value="view">Last-4 read 5+ pts above our read</option>') + '''
        <input type="search" class="pj-search" placeholder="Search player, team…" aria-label="Search projections">
        <span class="rs-count pj-count"></span>
      </div>
      <div class="rs-tablebox">
        <table class="rs-table" id="proj-table" data-source="proj" data-row-key="id">
          <thead><tr>
            <th data-field="game"><button data-k="game">Game</button></th>
            <th data-field="kickoff" class="rs-hide-narrow"><button data-k="kickoff_utc">Kickoff</button></th>
            <th data-field="contract"><button data-k="contract">Line (expected)</button></th>
            <th data-field="pos" class="rs-hide-narrow"><button data-k="pos">Pos</button></th>
            <th data-field="team"><button data-k="team">Team</button></th>
            <th data-field="proj" class="num"><button data-k="proj">Proj.</button></th>
            <th data-field="p_wedger" class="rs-barcell"><button data-k="p_wedger" title="Yards and catches: Wedger % if the line posts at this number for 50¢ (85% price + 15% our read, then the Week 6–7 calibration). Anytime TDs: our read with the TD calibration. Click for the outlook.">Wedger %</button></th>
            <th data-field="p_over" class="num"><button data-k="p_over" title="Our model alone: usage cases, defense, coverage, game script, team total, weather and recent role. On real prices it hasn't beaten the market by itself.">Our read %</button></th>
            <th data-field="mom_p" class="num rs-hide-narrow"><button data-k="mom_p" title="Our read with his last 4 games weighted most">Last-4 read %</button></th>
            ''' + MOMTH + '''
            <th data-field="season_avg" class="num rs-hide-narrow"><button data-k="season_avg">2026 avg</button></th>
            <th data-field="games" class="num rs-hide-narrow"><button data-k="games">Games</button></th>
            <th data-field="flags"><button data-k="flags">Flags</button></th>
          </tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </section>
  </div>
'''
rep('  <!-- ============ CATEGORY TABS ============ -->', PROJ + '\n  <!-- ============ CATEGORY TABS ============ -->')

# ---------- charts: week-by-week + momentum ----------
CH = '''
    <section class="rs-card" id="ch-weeks">
      <h2>Week by week · every 45–55¢ line at Robinhood's price</h2>
      <p class="rs-note">Weeks 1–5 are game lines only (Robinhood didn't keep prop prices); Weeks 6–7 add quarters, halves and player props. Win % of the Yes side each week, with the 50% line dashed; hover a point for the record and return. "Every No" buys the other side at 100 − Yes + 1¢.</p>
      <div class="rs-controls"><label>Group <select class="chw-grp" aria-label="Group"><option>Strategy</option><option>Market</option><option value="Side (game lines)">Side (game lines)</option><option>Price band</option></select></label></div>
      <div class="wg-key chw-key"></div>
      <div class="wg-chart" id="ch-weeks-chart" data-source="bt_weeks"></div>
      <h3 class="wg-h3">All seven weeks together</h3>
      <div class="wg-chart" id="ch-weeks-all" data-source="bt_weeks"></div>
    </section>

    <section class="rs-card" id="ch-props">
      <h2>Week by week · player props against the line books would set</h2>
      <p class="rs-note">Every starter's receiving, receptions, rushing and passing line in each week of 2026 (and 2023–25 together), with the line set the way books set the real Week 6–7 lines (season average, last 4 and multi-season average, to a half point). Cells show how often the over cleared it; green = above that week's average for all props, red = below. Rows that stay green week after week are the steady edges.</p>
      <div class="rs-controls"><label>Split by <select class="chp-fac" aria-label="Factor"><option>Stat</option><option>Position</option><option>Favorite / underdog</option><option>Home / away</option><option>Team total</option><option>Momentum</option><option>Season hit rate</option></select></label></div>
      <div class="wg-chart" id="ch-props-chart" data-source="bt_props"></div>
    </section>

    <section class="rs-card" id="ch-mom">
      <h2>Momentum · do the last four games beat the season?</h2>
      <p class="rs-note">23,000 player-games, 2023–2026. On its own the last-4 average is a worse guide than the season average, and books already weigh it; what carries forward is a change in role (snap share) or volume, not a hot or cold run of yards per catch.</p>
      <div class="wg-grid2">
        <div class="wg-mini"><h3>How much of a last-4 run shows up next game</h3><div class="wg-chart" id="ch-mom-persist" data-source="mom_summary"></div></div>
        <div class="wg-mini"><h3>Error of each guide vs the season average (100)</h3><div class="wg-chart" id="ch-mom-acc" data-source="mom_summary"></div></div>
        <div class="wg-mini"><h3>Overs vs a book-style line, by momentum (2023–26)</h3><div class="rs-controls"><select class="chm-stat" aria-label="Stat"><option value="recyd">Receiving yards</option><option value="rec">Receptions</option><option value="rushyd">Rushing yards</option></select></div><div class="wg-chart" id="ch-mom-cat" data-source="mom_summary"></div></div>
        <div class="wg-mini"><h3>Real Week 6–7 prices, by momentum</h3><div class="wg-chart" id="ch-mom-real" data-source="mom_summary"></div></div>
      </div>
      <p class="rs-note" id="ch-mom-var" data-source="mom_summary"></p>
    </section>

    <section class="rs-card" id="ch-teams">
      <h2>Teams · first four games vs the last four</h2>
      <p class="rs-note">Offensive EPA per play (win probability 5–95%), adjusted for the defenses faced, in each team's first four 2026 games (hollow) and its last four (filled). Team momentum has carried little into the next game since 2023 (7% of the gap), and books have over-reacted to recent scoring: teams scoring 4+ points under their season average over the last four beat their implied total by 1.5 points.</p>
      <div class="wg-chart" id="ch-teams-chart" data-source="team_mom"></div>
    </section>
'''
rep('''  <div class="rs-page" id="charts" hidden>
''', '''  <div class="rs-page" id="charts" hidden>
''' + CH)

# ---------- methodology ----------
i = s.index('<p><b>Live check and re-fit (Mon Oct 26).</b>'); j = s.index('</p>', i) + 4
s = s[:j] + ('\n    <p><b>Model v3 and the momentum study (Tue Oct 27).</b> With all 14 Week 7 games settled (Monday night\'s DAL @ PHI went 5–9 for the picks; '
             'the week finished 153–110, +3.8%), our own matchup read showed no correlation with result minus price on 706 real Week 6–7 lines, so Wedger % now leans '
             'harder on the market: 85% books, 15% our read (trained on one week, tested on the other: Brier 0.2474 vs 0.2480 at 70/30; price alone 0.2512). Calibration re-fit '
             'on all 706 lines: a Yes priced 50¢ comes true about 45% for receiving and anytime TDs, 40% for rushing and 56% for passing. New "Recent role" factor: when '
             'a player\'s snap share over his last 4 games moved 10+ points from his season share, his volume moves with it (2023–25: 34–55% of the gap carried into the '
             'next game after a role change vs 6–21% otherwise). Weighting the last 4 games heavily (the last-4 view) tested worse on real prices (0.2487), so it is shown '
             'as a filter, not used in Wedger %. Week by week at real prices (Charts): every Yes 45–55¢ lost 6.6% over Weeks 1–7 and every No made 4.4%; passing props '
             'hit 60% (54–36), rushing props 39%, game-total overs 56%, favorites on team lines 40%.</p>') + s[j:]

# ---------- CSS ----------
rep('  .rs-tabs { display: flex;', '''  .wg-mom-chip { display: inline-block; font-size: 11px; line-height: 1.5; padding: 0 7px; border-radius: 9px; white-space: nowrap; background: var(--cds-chart-grid); color: var(--color-fg); }
  .wg-mom-chip.up { background: color-mix(in srgb, var(--wg-green) 26%, var(--color-bg)); }
  .wg-mom-chip.up2 { background: color-mix(in srgb, var(--wg-green) 12%, var(--color-bg)); }
  .wg-mom-chip.hot { background: color-mix(in srgb, var(--color-warn) 22%, var(--color-bg)); }
  .wg-mom-chip.down { background: color-mix(in srgb, var(--cds-chart-status-critical) 22%, var(--color-bg)); }
  .wg-mom-chip.down2 { background: color-mix(in srgb, var(--cds-chart-status-critical) 10%, var(--color-bg)); }
  .wg-h3 { font-size: var(--cds-font-size-body); font-weight: 600; margin: 18px 0 6px; }
  .rs-tabs { display: flex;''')
open(B + 'page_template.html', 'w').write(s)
print('markup ok', len(s))

# ---------- methodology tail fixes (run before patch_w8_js.py) ----------
s = open(B + 'page_template.html').read()
def rep2(old, new):
    global s
    c = s.count(old); assert c == 1, (old[:90], c); s = s.replace(old, new)
rep2("The favorite is the side with the higher Robinhood moneyline (Sun Oct 25 ~11:56 AM CT). Player props Robinhood doesn't list use the Robinhood-style rungs priced from the sportsbooks described on the Week 7 lines tab.",
     "The favorite is the side with the higher Robinhood moneyline (Tue Oct 27 ~10:11 AM CT). Player props Robinhood doesn't list use the Robinhood-style rungs priced from the sportsbooks described on the Week 8 lines tab.")
rep2("since 2023 (2026 through Week 6). Usage cases:", "since 2023 (2026 through Week 7). Usage cases:")
rep2("(calibrated on 2025); Wedger % is 70% market and 30% our read.", "(calibrated on 2025); Wedger % is 85% market and 15% our read (70/30 before Week 8), then the Week 6–7 calibration by market. Recent role: when his snap share over the last 4 games is 10+ points off his season share, the projection scales with the square root of his change in volume (targets, attempts) or moves 75% of the way to his last-4 rushing average, capped at −20% / +25%.")
rep2("Open-Meteo forecasts; Action Network book lines.", "NFLWeather and RotoWire forecasts (Week 8); ESPN injury statuses; Action Network, VegasInsider and Covers book lines; Kalshi prices.")
open(B + 'page_template.html', 'w').write(s)
print('method ok')
