"""Wed Nov 4 evening: simpler descriptions + per-game reads tabs in the lobby's "The reads." section.
Runs on the final index.html (after gen_page.py and the Wedger -> Wedge step), before esmin/split_page.
Per-game reads mirror w9_game_reads.py: Robinhood's own player props, the better side priced 25-75c, Wedge % beating that
price by 3+ pts, Questionable/Doubtful players left out, ranked by Kelly growth, one line per player per stat family, two
per player, six per game."""
B = '/home/claude/wedger/rh/'
s = open(B + 'index.html').read()

def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, (old[:90], c); s = s.replace(old, new)

def para(anchor, new, count=1):
    """Replace a paragraph's text, from its first words (anchor) up to its closing </p>."""
    global s
    c = s.count(anchor); assert c == count, (anchor, c)
    for _ in range(count):
        i = s.index(anchor); j = s.index('</p>', i); assert '<p' not in s[i:j], anchor
        s = s[:i] + new + s[j:]
    assert s.count(new) >= count

# ---------------------------------------------------------------- simpler descriptions
para("Week 9, re-priced Wed Nov 4 ~3:37 PM CT from Robinhood",
     "Every Week 9 line priced 45–55¢, updated Wed Nov 4 at 3:37 PM CT. Where Robinhood has no line yet, the price comes from the sportsbooks. "
     "Hit rate is how often the line came true in his 2026 games; Wedge % is our chance it comes true this week. Select a player prop for the full read. "
     "★ marks a high-scoring game. Out: Lamar Jackson and Tyler Huntley (Thu), Sam Darnold and David Montgomery (Sun).")
para("Every starter's main props with the line we expect",
     "Every starter's main props before the books post them. Line is where we expect books to open; Proj. is our projection. "
     "Wedge % is our chance he clears that line if it opens at 50¢, so it mostly reflects how that market has priced overs. Select a row for the full read.")
para("Same filter as before: Yes price 45–55¢",
     "Props priced 45–55¢ that came true in more than half of his 2026 games. Wedge % is our chance it hits; the thin mark is the price. "
     "Switch to “All 45–55¢ props” to drop the hit-rate filter. Select a prop for the full read.", count=4)
para("PPR fantasy points allowed per game to running backs",
     "Fantasy points (PPR) allowed per game to running backs and to receivers and tight ends, Weeks 1–8. Rank 1 allows the most; the top 10 count as soft. Week 9 teams are in bold.")
para("Robinhood's Yes price (Wed Nov 4 ~3:37 PM CT) where Robinhood lists",
     "Anytime TD prices from Robinhood, or the sportsbook average where Robinhood has no line. Wedge % is our chance he scores; select a player for the full read. "
     "Green marks the league's top quarter. Each box is a minimum; set it to 0 to turn it off.")
para("Every Week 6 line from the 45–55¢ screen, settled against",
     "Week 6 lines from the 45–55¢ screen, settled. Return is the profit from buying one Yes of each at its listed price, before fees. One week is a small, noisy sample.")
para("Weeks 7 and 8: every line posted",
     "Every Week 7 and 8 line we posted, settled from the final box scores. “Wedge certified only” shows certified picks at any price. Charts has every week.")
para("Tick the factors to split by; every combination",
     "Tick factors to split the lines. Edge is hit rate minus average price: above zero, the lines hit more often than they cost. Small groups swing a lot.")
para("How well each way of reading a player prop called Yes vs No",
     "How well each method called Yes or No (Brier score, lower is better). Bars right of center beat a coin flip.")
para("What it means: the matchup model clearly beats",
     "In short: the model beats past hit rates, but against real prices it adds little. Buying every Week 6 line where a method beat the price by 3+ points lost money.")
para("Robinhood Yes prices (the Kalshi order book",
     "NBA lines from Robinhood for Oct 24–27 games, priced Fri Oct 23 at 11:40 PM CT. Hit rate is his last 20 games; Books % is the sportsbooks' fair chance; "
     "Wedge % is our chance it hits. Select a player prop for the full read.")
para("NBA lines priced 45–55¢ per game, and how many pass",
     "Lines priced 45–55¢ per game, and how many pass the &gt;50% test.")
para("Every NBA line this page listed at 45–55¢, frozen at",
     "Every NBA line we listed at 45–55¢, settled from the final box score. Return is the profit from buying one Yes at the posted price, before fees. "
     "Two nights is a small sample; the season backtest below is the bigger test. <span id=\"nr-sum\"></span>")
para("Closing player-prop lines from DraftKings",
     "37,519 closing player props from the 2025-26 season, with sportsbook prices standing in for Robinhood's, settled from box scores. Every input uses only games played before that night.")
para("The filter (hit &gt;50% of his last 20) won 48.9%",
     "Over the 2025-26 season the &gt;50% filter won 48.9% of lines and the model 48.4%; both lost money before fees (−2.5% and −1.3%). "
     "In the NBA the price is the signal: use the screen and the read to understand a line, not as an edge.")
para("Every starter's receiving yards, receptions, rushing yards and passing yards against the line books would set",
     "Which roles and game spots cleared the line books would set. “Held” means the spot also beat its 2023–25 average, so it is less likely to be luck. Overs at these lines hit about 45% overall.")
para("Public projection systems build a prop as volume times efficiency",
     "A projection is volume times efficiency. Volume follows recent games; efficiency is mostly noise, so it needs a long window. We tested both on every 2023–26 player-game.")
para("Weeks 1–5 are game lines only",
     "Win % of the Yes side each week (game lines only in Weeks 1–5; props from Week 6). Hover a point for the record and return.")
para("Every starter's receiving, receptions, rushing and passing line in each week of 2026",
     "How often overs cleared a book-style line, week by week. Green beats that week's average; rows that stay green are the steady edges.")
para("23,000 player-games, 2023–2026. On its own the last-4",
     "Across 23,000 player-games, a hot or cold last four games barely carries forward. A change in role or volume does.")
para("Offensive EPA per play (win probability 5–95%)",
     "Each offense in its first four games (hollow) and its last four (filled), adjusted for opponents. Team momentum has carried little into the next game, and books have overreacted to recent scoring.")
para("Each cell is the hit rate of the lines in that row and column",
     "Hit rate for each pair of factors. Green is above 50%, red below; the deeper the color, the further from 50%.")
para("Every Week 6 line from the 45–55¢ screen, settled. The groups match",
     "Week 6 lines from the 45–55¢ screen, settled, by group.")
para("Each dot is a Week 9 line priced 45–55¢",
     "Each dot is a Week 9 line: its price against how often it came true. Dots above the diagonal hit more often than they cost.")
para("Each pick counts as one Yes contract at its listed price",
     "Each pick counts as one contract at its listed price. Win % and profit count settled picks only; standings go by win %, then profit.")
para("This tab gets the same treatment as the NFL and NBA",
     "Soccer gets the same treatment as the NFL and NBA: every Robinhood line priced 45–55¢ across the top leagues and MLS, with the full read and a backtest.")

# methodology: a short "How it works", the full notes and model history folded underneath
i = s.index('<section class="rs-card rs-method" id="method" hidden>'); j = s.index('</section>', i)
sec = s[i:j]
h = '<h2>How the test works</h2>'; assert sec.count(h) == 1
k = sec.index(h) + len(h)
SHORT = '''<h2>How it works</h2>
    <dl class="wx-how">
      <div><dt>The lines</dt><dd>Every Robinhood NFL line, updated Wed Nov 4 at 3:37 PM CT. Where Robinhood has no line yet, we price a matching one from five sportsbooks (Source: Books · RH-style).</dd></div>
      <div><dt>Hit rate</dt><dd>How often the line came true in 2026: in his games for player props, in the team's games for team lines, in either team's games for totals.</dd></div>
      <div><dt>Wedge %</dt><dd>Our chance the line comes true: the price, adjusted for how often that kind of line beat its price in Weeks 6–8. Passing overs have come true more often than priced; rushing and receiving-yard overs less often.</dd></div>
      <div><dt>Picks</dt><dd>The side where Wedge % beats the price by 3 points or more, on Robinhood's own lines priced 45–55¢. Posted picks went 248–190 (56.6%) over Weeks 6–8, +4.0% before fees.</dd></div>
      <div><dt>Reads by game</dt><dd>Each game's reads rank Robinhood's own player props, the better side priced 25–75¢, by the best balance of chance and price (Kelly growth): how far Wedge % clears the price, weighed by how likely it is to hit. Wedge % was fit on lines priced 40–60¢, so reads outside that range are marked as a rough guide.</dd></div>
      <div><dt>The read</dt><dd>Select a player prop for his games since 2023, the matchup, the game script, the weather and our projection.</dd></div>
      <div><dt>Flags</dt><dd>“No bid”: only an ask is posted. “Wide spread”: more than 5¢ between bid and ask. “Small sample”: fewer than 3 games.</dd></div>
    </dl>
    <details class="wx-fold"><summary>Full method notes and model history</summary>'''
sec = sec[:sec.index(h)] + SHORT + sec[k:].rstrip() + '\n    </details>\n  '
s = s[:i] + sec + s[j:]

# ---------------------------------------------------------------- per-game reads: markup
rep('<p class="wx-sec-sub">The widest gaps between Wedge % and the price on Robinhood\'s own Week 9 lines: three Yes, three No, two per game at most. Select one for the full read.</p>',
    '<p class="wx-sec-sub" id="wx-reads-sub">The biggest gaps between Wedge % and the price this week. Pick a game for its own reads.</p>')
rep('      <div class="wx-reads" id="wg-hot-cards">',
    '      <div class="wx-tabs" role="tablist" id="wx-read-tabs" aria-label="Reads by game"><button type="button" class="wx-tab" role="tab" aria-selected="true" data-game="">All games</button></div>\n'
    '      <div class="wx-reads" id="wg-hot-cards" role="tabpanel" aria-labelledby="reads-h">')
rep('<button type="button" class="wg-go" data-go="lines" data-wg-show="pick">All <span data-wg-count="picks">40</span> reads ↗</button>',
    '<button type="button" class="wg-go" id="wx-reads-more" data-go="lines" data-wg-show="pick" data-wg-game="">All <span data-wg-count="picks">40</span> reads ↗</button>')

CSS = '''
  /* reads by game */
  .wx-tabs { display: flex; gap: 2px; overflow-x: auto; scrollbar-width: thin; margin: 0 0 18px; border-bottom: 1px solid var(--wx-rule); -webkit-overflow-scrolling: touch; }
  .wx-tab { all: unset; box-sizing: border-box; cursor: pointer; flex: none; padding: 10px 14px 11px; font-family: var(--wx-mono); font-size: 11px; letter-spacing: .08em; text-transform: uppercase; white-space: nowrap; color: var(--wx-muted); border-bottom: 2px solid transparent; margin-bottom: -1px; transition: color .15s ease, border-color .15s ease; }
  .wx-tab small { font-size: 10px; margin-left: 6px; opacity: .7; letter-spacing: .06em; }
  .wx-tab:hover { color: var(--wx-ink); }
  .wx-tab[aria-selected="true"] { color: var(--wx-ink); border-bottom-color: var(--wx-green); }
  .wx-tab:focus-visible { outline: 2px solid var(--wx-green); outline-offset: -2px; }
  .wx-read-foot .wx-rough { color: var(--wx-muted); }
  .wx-reads .wx-empty { grid-column: 1 / -1; padding: 28px 20px; margin: 0; background: var(--color-panel); color: var(--wx-muted); }
  /* how it works */
  .wx-how { display: grid; gap: 0; margin: 4px 0 18px; border-top: 1px solid var(--color-border-line); }
  .wx-how > div { display: grid; grid-template-columns: 150px minmax(0, 1fr); gap: 16px; padding: 12px 0; border-bottom: 1px solid var(--color-border-line); }
  .wx-how dt { font-family: var(--wx-mono); font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: var(--wx-muted); padding-top: 2px; }
  .wx-how dd { margin: 0; line-height: 1.55; }
  @media (max-width: 640px) { .wx-how > div { grid-template-columns: 1fr; gap: 4px; } }
  .wx-fold { margin-top: 6px; }
  .wx-fold > summary { display: list-item; text-align: left; cursor: pointer; font-family: var(--wx-mono); font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: var(--wx-green-ink); padding: 8px 0; }
  .wx-fold[open] > summary { margin-bottom: 8px; }
'''
assert s.count('</style>') == 1
s = s.replace('</style>', CSS + '</style>')

# ---------------------------------------------------------------- per-game reads: script
rep("""  document.querySelectorAll('[data-wg-show]').forEach((b) => b.addEventListener('click', () => {
    const sel = $('.rs-show'); if (sel && [...sel.options].some((o) => o.value === b.dataset.wgShow)) { sel.value = b.dataset.wgShow; sel.dispatchEvent(new Event('change')); }
  }));""",
"""  // jump to the Lines tab with a view (and optionally a game and a search) set
  const wxToLines = (show, game, q) => {
    if (game != null) ls.game = game;
    if (q != null) { ls.q = q.toLowerCase(); const f = $('.rs-search'); if (f) f.value = q; }
    const px = $('.rs-px'); if (px && show !== 'every') { px.value = ''; ls.px = ''; }
    const sel = $('.rs-show'); if (sel && [...sel.options].some((o) => o.value === show)) { sel.value = show; sel.dispatchEvent(new Event('change')); }
  };
  document.querySelectorAll('[data-wg-show]').forEach((b) => b.addEventListener('click', () => {
    wxToLines(b.dataset.wgShow, 'wgGame' in b.dataset ? b.dataset.wgGame : null, 'wgGame' in b.dataset ? '' : null);
  }));""")

rep("""  const wxRead = (r) => {
    const yes = num(r.yes_price);
    const no = num(r.no_price) != null ? num(r.no_price) : (num(r.yes_bid) != null ? 100 - num(r.yes_bid) : null);
    const side = r.sit_pick, pYes = num(r.sit_hit), pSide = side === 'Yes' ? pYes : 100 - pYes;""",
"""  const wxRead = (r, o = {}) => {
    const yes = num(r.yes_price);
    const no = num(r.no_price) != null ? num(r.no_price) : (num(r.yes_bid) != null ? 100 - num(r.yes_bid) : null);
    const side = o.side || r.sit_pick, pYes = num(r.sit_hit), pSide = side === 'Yes' ? pYes : 100 - pYes;
    const edge = o.edge != null ? o.edge : num(r.sit_pedge);""")
rep("const top = el('span', 'wx-read-top'); top.append(el('span', null, `${r.game} · ${r.kickoff}`), el('span', null, WX_MKT[r.sit_stat] || r.market));",
    "const top = el('span', 'wx-read-top'); top.append(el('span', null, o.rank ? `${String(o.rank).padStart(2, '0')} · ${r.kickoff}` : `${r.game} · ${r.kickoff}`), el('span', null, WX_MKT[r.sit_stat] || r.market));")
rep("    foot.append(dot, `${side}, +${Math.round(num(r.sit_pedge))} pts vs price`, el('em', null, 'Read ↗'));",
    "    foot.append(dot, `${side}, +${Math.round(edge)} pts vs price`); if (o.rough) foot.append(el('span', 'wx-rough', '· rough guide'));\n    foot.append(el('em', null, 'Read ↗'));")
rep("""    b.addEventListener('click', () => openSit(r, ctx, b));
    return b;
  };""",
"""    if (r.sit_key) b.addEventListener('click', () => openSit(r, ctx, b));
    else b.addEventListener('click', () => { showPage('lines'); wxToLines('every', r.game, label.split(':')[0]); ($('#top') || document.body).scrollIntoView({ block: 'start' }); });
    return b;
  };
  // reads by game: the better side priced 25-75c, Wedge % 3+ pts over it, ranked by Kelly growth (chance and price in balance)
  const WX_FAM = { rushyd: 'rush', rryd: 'rush', recyd: 'recv', rec: 'recv', passyd: 'pass', passtd: 'pass' };
  const WX_SKIP = /Questionable|Doubtful|Out\\b|Inactive|No bid/i;
  const wxBest = (r) => {
    const p = num(r.sit_hit), y = num(r.yes_price); if (p == null || y == null) return null;
    let n = num(r.no_price); if (n == null && num(r.yes_bid) != null) n = 100 - num(r.yes_bid);
    let out = null;
    for (const [side, q, ps] of [['Yes', y, p], ['No', n, 100 - p]]) {
      if (q == null || q < 25 || q > 75 || ps - q < 3) continue;
      const P = ps / 100, Q = q / 100, g = P * Math.log(P / Q) + (1 - P) * Math.log((1 - P) / (1 - Q));
      if (!out || g > out.g) out = { side, q, p: ps, edge: ps - q, g };
    }
    return out;
  };
  function wxGameReads(rows, game) {
    const L = [];
    for (const r of rows) {
      if (r.game !== game || r.source !== 'Robinhood' || WX_SKIP.test(r.flags || '')) continue;
      const b = wxBest(r); if (b) L.push([b, r]);
    }
    L.sort((a, b) => b[0].g - a[0].g || b[0].edge - a[0].edge || (a[1].contract < b[1].contract ? -1 : 1));
    const seen = new Set(), per = new Map(), top = [];
    for (const [b, r] of L) {
      const pl = String(r.contract).split(':')[0], k = pl + '|' + (WX_FAM[r.sit_stat] || r.sit_stat);
      if (seen.has(k) || (per.get(pl) || 0) >= 2) continue;
      seen.add(k); per.set(pl, (per.get(pl) || 0) + 1); top.push([b, r]);
      if (top.length === 6) break;
    }
    return { top, props: rows.some((r) => r.game === game && r.source === 'Robinhood' && num(r.sit_hit) != null) };
  }
  let wxGame = ''; try { wxGame = localStorage.getItem('wx-read-game') || ''; } catch (e) { /* storage unavailable */ }
  let wxAllTop = null, wxPicksN = null;
  function wxTabs(rows) {
    const bar = $('#wx-read-tabs'); if (!bar || bar.dataset.built) return;
    const ko = new Map(); for (const r of rows) if (!ko.has(r.game)) ko.set(r.game, [r.kickoff_utc || '', r.kickoff || '']);
    const games = [...ko.keys()].sort((a, b) => (ko.get(a)[0] < ko.get(b)[0] ? -1 : ko.get(a)[0] > ko.get(b)[0] ? 1 : a < b ? -1 : 1));
    if (wxGame && !ko.has(wxGame)) wxGame = '';
    const mk = (g) => {
      const t = el('button', 'wx-tab'); t.type = 'button'; t.setAttribute('role', 'tab'); t.dataset.game = g;
      if (g) { t.append(g); const d = (ko.get(g)[1].match(/(Thu|Fri|Sat|Sun|Mon)\\b/) || [])[1]; if (d) t.append(el('small', null, d)); } else t.append('All games');
      t.addEventListener('click', () => { wxGame = g; try { localStorage.setItem('wx-read-game', g); } catch (e) { /* storage unavailable */ } wxDraw(); });
      return t;
    };
    bar.replaceChildren(mk(''), ...games.map(mk)); bar.dataset.built = '1';
    bar.addEventListener('keydown', (e) => {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      const tabs = [...bar.querySelectorAll('.wx-tab')], i = tabs.indexOf(document.activeElement); if (i < 0) return;
      const n = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length]; n.focus(); n.click(); e.preventDefault();
    });
  }
  function wxDraw() {
    const box = $('#wg-hot-cards'), sub = $('#wx-reads-sub'), more = $('#wx-reads-more'), bar = $('#wx-read-tabs');
    if (bar) bar.querySelectorAll('.wx-tab').forEach((t) => { const on = t.dataset.game === wxGame; t.setAttribute('aria-selected', on ? 'true' : 'false'); t.tabIndex = on ? 0 : -1; });
    if (!box) return;
    if (!wxGame) {
      if (sub) sub.textContent = 'The biggest gaps between Wedge % and the price this week. Pick a game for its own reads.';
      if (more) { more.dataset.wgShow = 'pick'; more.dataset.wgGame = ''; if (wxPicksN != null) { const c = el('span', null, wgFmt(wxPicksN)); c.dataset.wgCount = 'picks'; more.replaceChildren('All ', c, ' reads ↗'); } }
      if (wxAllTop) box.replaceChildren(...(wxAllTop.length ? wxAllTop.map((r) => wxRead(r)) : [el('p', 'wx-empty', 'No line clears its price by 3+ points right now.')]));
      return;
    }
    const la = dash.data('lines_all');
    if (more) { more.dataset.wgShow = 'every'; more.dataset.wgGame = wxGame; more.replaceChildren(`Every ${wxGame} line ↗`); }
    if (la.status !== 'ok') { box.replaceChildren(el('p', 'wx-empty', la.status === 'error' ? 'This game’s lines failed to load. Reload the page to try again.' : 'Loading this game’s reads…')); return; }
    const { top, props } = wxGameReads(la.data, wxGame);
    if (sub) sub.textContent = top.length
      ? `${wxGame}: the best balance of chance and price. Wedge % well above the price, on a side with a real chance to hit; long shots and near-locks rank lower.`
      : `${wxGame}: nothing clears its price right now.`;
    box.replaceChildren(...(top.length
      ? top.map(([b, r], i) => wxRead(r, { side: b.side, edge: b.edge, rank: i + 1, rough: b.q < 40 || b.q > 60 }))
      : [el('p', 'wx-empty', props ? 'No Robinhood line in this game clears its price by 3+ points right now.' : 'Robinhood hasn’t listed player props for this game yet. Its reads appear here when it does.')]));
  }""")

rep("""      const box = $('#wg-hot-cards');
      if (box) box.replaceChildren(...(top.length ? top.map(wxRead) : [el('p', 'wx-empty', 'No line clears its price by 3+ points right now.')]));
    } else if (ld.status === 'error') { const box = $('#wg-hot-cards'); if (box) box.replaceChildren(el('p', 'wx-empty', 'This week’s lines failed to load. Reload the page to try again.')); }""",
"""      wxAllTop = top; wxPicksN = picks.length;
    } else if (ld.status === 'error' && !wxGame) { const box = $('#wg-hot-cards'); if (box) box.replaceChildren(el('p', 'wx-empty', 'This week’s lines failed to load. Reload the page to try again.')); }
    if (la.status === 'ok') wxTabs(la.data);
    if (ld.status === 'ok' || la.status === 'ok') wxDraw();""")

open(B + 'index.html', 'w').write(s)
print('w9c ok', len(s))
