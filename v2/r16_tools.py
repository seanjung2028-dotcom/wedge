"""Round 16 (Tue Nov 17): two live tools under NFL.
  Line Shopping (#shop)  every Kalshi receiving and rushing rung in a game, priced after Kalshi's and Robinhood's fees,
                         Wedge's number on the live price (plans that include the card), the ladder, 72 hours of prices.
  Analyst (#ask)         questions answered by Claude on the site's server, from Wedge's tools only, every number checked.
Server side: functions/api/v1/shop/*.js, functions/api/v1/ask.js, lib/live.js, lib/analyst.js, lib/gen/ (v2/build_live.py).
Both pages are open to everyone; the server decides what each plan sees."""
V = '/home/claude/wedger/v2/'
SUB_ADD = '<span class="v2-sn-g">Live</span><button type="button" class="v2-sn" data-page="shop"><i>07</i>Line Shopping</button><button type="button" class="v2-sn" data-page="ask"><i>08</i>Analyst</button>'
FINE_SHOP = ('Prices: Kalshi’s public market data, read live. Robinhood’s NFL props trade on Kalshi’s book, so they’re priced here with Robinhood’s fees. '
             'DraftKings, FanDuel, BetMGM, Fanatics and Caesars need a licensed odds feed, which isn’t connected yet. Estimated value is an estimate, not a promise, '
             'and assumes holding to settlement. 21+. Gambling problem? Call 1-800-GAMBLER.')
FINE_ASK = ('Answers come only from Wedge’s data and live Kalshi prices, and every number is checked against them before it’s shown. '
            'Wedge doesn’t price in-game situations or two outcomes together. Estimates, not promises. 21+. Gambling problem? Call 1-800-GAMBLER.')


def pages(sub):
    return f'''<div class="rs-page v2-open v2-tool" id="shop" hidden>
  <header class="wx-band"><span class="wx-label"><i class="wx-dot" aria-hidden="true"></i>NFL / Live</span><h2>Line Shopping.</h2><p class="v2-cta">Every receiving and rushing line, priced after fees</p></header>
  {sub}
  <section class="v2-sh" aria-label="Line Shopping">
    <div class="v2-sh-watch" id="shop-watch" hidden></div>
    <div class="v2-sh-games" id="shop-games" role="group" aria-label="Game"></div>
    <div class="v2-sh-ctl">
      <label class="v2-sh-search"><span class="wg-visually-hidden">Search players or lines</span><input type="search" id="shop-q" placeholder="Search a player or line" autocomplete="off"></label>
      <label><span class="wg-visually-hidden">Stat</span><select id="shop-stat"><option value="">All stats</option><option value="rec">Receptions</option><option value="recyd">Receiving yards</option><option value="rushyd">Rushing yards</option><option value="rryd">Rush + rec yards</option></select></label>
      <label><span class="wg-visually-hidden">Side</span><select id="shop-side"><option value="yes">Yes · over</option><option value="no">No · under</option></select></label>
      <label class="v2-sh-size">Contracts <input type="number" id="shop-size" value="10" min="1" max="500" inputmode="numeric"></label>
    </div>
    <p class="v2-sh-status" id="shop-status" role="status">Reading Kalshi’s prices…</p>
    <div class="v2-sh-grid">
      <div class="v2-sh-list" id="shop-list" aria-label="Lines"></div>
      <div class="v2-sh-side" id="shop-detail" aria-live="polite"><p class="v2-sh-empty">Pick a line to compare every platform.</p></div>
    </div>
    <p class="v2-tool-fine">{FINE_SHOP}</p>
  </section>
</div>
<div class="rs-page v2-open v2-tool" id="ask" hidden>
  <header class="wx-band"><span class="wx-label"><i class="wx-dot" aria-hidden="true"></i>NFL / Live</span><h2>Analyst.</h2><p class="v2-cta">Ask about a player, a line or a price</p></header>
  {sub}
  <section class="v2-ak" aria-label="Analyst">
    <p class="v2-ak-note" id="ask-note" role="status" hidden></p>
    <div class="v2-ak-log" id="ask-log" aria-live="polite"></div>
    <div class="v2-ak-start" id="ask-start"></div>
    <form class="v2-ak-form" id="ask-form">
      <label for="ask-q" class="wg-visually-hidden">Your question</label>
      <textarea id="ask-q" rows="2" maxlength="2000" placeholder="Ask about a player, a line or a price"></textarea>
      <div class="v2-ak-actions"><button type="button" class="wz-link" id="ask-clear" hidden>New conversation</button><button type="submit" class="wz-btn wz-btn-g" id="ask-go">Ask ↗</button></div>
    </form>
    <p class="v2-tool-fine">{FINE_ASK}</p>
  </section>
</div>
'''


def apply(s, js):
    def sr(a, b, n=1):
        nonlocal s
        c = s.count(a); assert c == n, f'r16 html: {a[:70]!r} found {c}'; s = s.replace(a, b)
    def jr(a, b, n=1):
        nonlocal js
        c = js.count(a); assert c == n, f'r16 js: {a[:70]!r} found {c}'; js = js.replace(a, b)
    # every NFL page strip gains the two tools
    import re
    end = '<i>06</i>Results</button></nav>'
    pat = re.compile(r'<nav class="v2-subnav" aria-label="NFL pages">.*?</nav>', re.S)
    navs = pat.findall(s); assert len(navs) == 6 and all(x.endswith(end) for x in navs), f'r16: NFL strips {len(navs)}'
    s = pat.sub(lambda m: m.group(0)[:-len('</nav>')] + SUB_ADD + '</nav>', s)
    sub = pat.search(s).group(0)
    # the NFL menu
    sr('role="menuitem" data-page="results">Results</button>',
       'role="menuitem" data-page="results">Results</button>\n        <div class="wg-dd-sep" role="separator"></div>\n        <div class="wg-dd-label" aria-hidden="true">Live</div>\n'
       '        <button type="button" class="wg-dd-item" role="menuitem" data-page="shop">Line Shopping</button>\n        <button type="button" class="wg-dd-item" role="menuitem" data-page="ask">Analyst</button>')
    # the pages
    sr('<div class="rs-page v2-open" id="charts" hidden>', pages(sub) + '<div class="rs-page v2-open" id="charts" hidden>')
    k = s.rindex('</style>'); s = s[:k] + open(V + 'src/tools.css').read() + s[k:]
    # the scripts, and opening each page draws it
    jr('  // ---------------- render ----------------', open(V + 'src/shop.js').read() + '\n' + open(V + 'src/ask.js').read() + '\n  // ---------------- render ----------------')
    jr("const NFL_PAGES = new Set(['research', 'final', 'thesis', 'charts', 'analysts', 'results']);", "const NFL_PAGES = new Set(['research', 'final', 'thesis', 'charts', 'analysts', 'results', 'shop', 'ask']);")
    jr("    if (id === 'final') requestAnimationFrame(() => fcRender());",
       "    if (id === 'final') requestAnimationFrame(() => fcRender());\n    if (id === 'shop') requestAnimationFrame(() => v2ShopOpen());\n    if (id === 'ask') requestAnimationFrame(() => v2AskOpen());")
    return s, js
