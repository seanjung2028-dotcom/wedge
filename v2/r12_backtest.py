"""Round 12 (Tue Nov 17): Results shows the card rules backtested on Weeks 1-9 (final lines and conditional leans), next to
the live card as it settled. Data: card_bt_sum and card_bt (bt/card_bt/). The Week 6 tiles give way to the four card
records; the new sections come first and the Week 6 table and the settled lines follow, renumbered."""
import re
V = '/home/claude/wedger/v2/'
TILE = '''      <div class="rs-card" data-bt="{k}">
        <div class="rs-tile-label">{label}</div>
        <div class="rs-tile-num dash-skeleton">—</div>
        <div class="rs-tile-note">&nbsp;</div>
      </div>'''
TILES = '''    <section class="rs-tiles" id="results-tiles">
''' + '\n'.join(TILE.format(k=k, label=l) for k, l in (('final_bt', 'Final lines · backtest'), ('lean_bt', 'Conditional leans · backtest'),
                                                      ('final_live', 'Final lines · live card'), ('lean_live', 'Conditional leans · live card'))) + '''
    </section>'''
HEAD = '''<thead><tr>
            <th><button data-k="label">Group</button></th>
            <th class="num"><button data-k="wins">Won</button></th>
            <th class="num"><button data-k="losses">Lost</button></th>
            <th class="rs-barcell"><button data-k="win_pct">Win %</button></th>
            <th class="num"><button data-k="ours" title="Our number for the side we took, averaged">Ours</button></th>
            <th class="num"><button data-k="needed" title="Price plus the 2¢ fee: the win rate a line needs to break even">Needed</button></th>
            <th class="num"><button data-k="avg_price">Avg price ¢</button></th>
            <th class="num"><button data-k="roi_pct">Return</button></th>
          </tr></thead>'''
SECTIONS = f'''
    <section class="rs-card" id="results-bt">
      <div class="pf-head v2-head"><div><span class="pf-label">01 / Backtest</span><h2 class="pf-h2 v2-h2">The card, backtested.</h2></div></div>
      <p class="rs-note">This week’s card rules, run on Weeks 1–9 and graded on how each line settled. Weeks 7–9 use the real Robinhood prices, with the model refit without the week being tested. Robinhood didn’t keep prop prices before Week 7, so Weeks 2–6 use lines rebuilt from box scores the way the books set them. Week 1 had no earlier games to read. “Ours” is our number for the side we took; “Needed” is the price plus the 2¢ fee. Return: one contract each, before fees.</p>
      <div class="rs-tablebox" style="max-height: none;">
        <table class="rs-table v2-bt-table" id="results-bt-compare">
          {HEAD}
          <tbody></tbody>
        </table>
      </div>
    </section>

    <section class="rs-card" id="results-bt-week">
      <div class="pf-head v2-head"><div><span class="pf-label">02 / By week</span><h2 class="pf-h2 v2-h2">Week by week.</h2></div></div>
      <div class="rs-controls">
        <select class="bt-w-tier" aria-label="Which calls"><option value="final">Final lines</option><option value="lean">Conditional leans</option></select>
      </div>
      <div class="rs-tablebox" style="max-height: none;">
        <table class="rs-table v2-bt-table" id="results-bt-weeks">
          <thead><tr>
            <th><button data-k="week">Week</button></th>
            <th><button data-k="src">Prices</button></th>
            <th class="num"><button data-k="wins">Won</button></th>
            <th class="num"><button data-k="losses">Lost</button></th>
            <th class="rs-barcell"><button data-k="win_pct">Win %</button></th>
            <th class="num"><button data-k="ours">Ours</button></th>
            <th class="num"><button data-k="needed">Needed</button></th>
            <th class="num"><button data-k="roi_pct">Return</button></th>
          </tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </section>

    <section class="rs-card" id="results-bt-checks">
      <div class="pf-head v2-head"><div><span class="pf-label">03 / Checks</span><h2 class="pf-h2 v2-h2">Overs, unders and checks.</h2></div></div>
      <p class="rs-note">The card keeps about one under for every three overs; the unders it leaves off are graded here too. Week 9 sets the backtest beside the card we posted that week, before v6. The rebuilt lines are checked on Weeks 7–9, where the real prices exist.</p>
      <div class="rs-tablebox" style="max-height: none;">
        <table class="rs-table v2-bt-table" id="results-bt-sides">
          {HEAD}
          <tbody></tbody>
        </table>
      </div>
    </section>

    <section class="rs-card" id="results-bt-list">
      <div class="pf-head v2-head"><div><span class="pf-label">04 / Every pick</span><h2 class="pf-h2 v2-h2">Every backtested pick.</h2></div></div>
      <div class="rs-controls">
        <select class="bt-p-week" aria-label="Week"><option value="">All weeks</option></select>
        <select class="bt-p-tier" aria-label="Which calls"><option value="">Final lines and leans</option><option value="Final line">Final lines</option><option value="Conditional lean">Conditional leans</option></select>
        <select class="bt-p-outcome" aria-label="Outcome"><option value="">Won and lost</option><option>Won</option><option>Lost</option></select>
        <input type="search" class="bt-p-search" placeholder="Search player, team, line…" aria-label="Search backtested picks">
        <span class="rs-count bt-p-count"></span>
      </div>
      <div class="rs-tablebox">
        <table class="rs-table" id="results-bt-picks">
          <thead><tr>
            <th><button data-k="week">Week</button></th>
            <th><button data-k="game">Game</button></th>
            <th><button data-k="line">Line</button></th>
            <th class="num"><button data-k="price">Price ¢</button></th>
            <th class="rs-barcell"><button data-k="mid">Ours</button></th>
            <th class="num rs-hide-narrow"><button data-k="needed">Needed</button></th>
            <th><button data-k="outcome">Outcome</button></th>
            <th class="rs-hide-narrow"><button data-k="result">Result</button></th>
            <th class="num"><button data-k="profit_c">Profit ¢</button></th>
          </tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </section>
'''
CSS = '''
/* round 12: the backtest tables on Results */
.wg-paper .v2-open .v2-bt-table tr.v2-bt-break td { border-top: 1px solid var(--v2-hair-strong, rgba(255,255,255,.22)); }
.wg-paper .v2-open .v2-bt-tag { display: inline-block; margin-right: 8px; padding: 1px 7px; border: 1px solid var(--v2-hair, rgba(255,255,255,.14)); border-radius: 999px;
  font: 600 10.5px/1.5 var(--wz-mono, ui-monospace, monospace); letter-spacing: .06em; text-transform: uppercase; color: var(--pf-muted, #9aa0a6); vertical-align: 1px; }
.wg-paper .v2-open .v2-bt-tag.is-final { border-color: var(--wg-green); color: var(--wg-green); }
'''
def apply(s, js):
    def sr(a, b, n=1):
        nonlocal s
        c = s.count(a); assert c == n, f'r12 html: {a[:70]!r} found {c}'; s = s.replace(a, b)
    def jr(a, b, n=1):
        nonlocal js
        c = js.count(a); assert c == n, f'r12 js: {a[:70]!r} found {c}'; js = js.replace(a, b)
    i = s.index('<section class="rs-tiles" id="results-tiles">'); j = s.index('</section>', i) + len('</section>')
    s = s[:i] + TILES.lstrip() + s[j:]
    sr('    <section class="rs-card" id="results-summary">', SECTIONS.lstrip('\n') + '\n    <section class="rs-card" id="results-summary">')
    sr('<span class="pf-label">01 / Week 6</span>', '<span class="pf-label">05 / Week 6</span>')
    i = s.index('id="results-lines"'); k = s.index('<span class="pf-label">02 / The record</span>', i)
    s = s[:k] + '<span class="pf-label">06 / The record</span>' + s[k + len('<span class="pf-label">02 / The record</span>'):]
    k = s.rindex('</style>'); s = s[:k] + CSS + s[k:]
    jr('  // ---------------- render ----------------', open(V + 'src/bt.js').read() + '\n  // ---------------- render ----------------')
    jr("results: () => { drawResultsSummary(); drawResults(); }", "results: () => { v2DrawBt(); drawResultsSummary(); drawResults(); }")
    return s, js
