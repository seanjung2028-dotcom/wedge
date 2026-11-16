B = '/home/claude/wedger/rh/'

CATS = {
    '1': ('RBs on the favored team',
          'Running backs (incl. fullbacks) on the team with the higher pregame Robinhood moneyline. Props whose opponent is one of the 10 softest run defenses are in tab 3 instead.'),
    '2': ('WRs + TEs on the underdog',
          'Wide receivers and tight ends on the team with the lower pregame moneyline. Props whose opponent is one of the 10 softest pass-catcher defenses are in tab 4 instead.'),
    '3': ('RBs on the favored team vs a soft run defense',
          'Tab 1 props where the opponent is one of the 10 defenses allowing the most PPR points per game to running backs in 2026.'),
    '4': ('WRs + TEs on the underdog vs a soft pass defense',
          'Tab 2 props where the opponent is one of the 10 defenses allowing the most PPR points per game to WRs + TEs in 2026.'),
}
TAB_LABEL = {'1': '1 · RB, favorite', '2': '2 · WR/TE, underdog', '3': '3 · RB vs soft D', '4': '4 · WR/TE vs soft D'}

cat_tabs = ''.join(f'<button class="rs-tab" role="tab" id="tab-cat-{k}" data-page="cat-{k}" aria-selected="false">{TAB_LABEL[k]}</button>' for k in CATS)

def cat_page(k):
    title, rule = CATS[k]
    return f'''
  <div class="rs-page rc-page" id="cat-{k}" data-cat="{k}" role="tabpanel" hidden>
    <section class="rs-tiles" id="cat-{k}-tiles">
      <div class="rs-card">
        <div class="rs-tile-label">Props whose condition hit &gt;50% in 2026</div>
        <div class="rs-tile-num dash-skeleton" data-source="cat_counts" data-where="cat={k}" data-field="qualifying">—</div>
        <div class="rs-tile-note">Priced 45–55¢ (Yes side)</div>
      </div>
      <div class="rs-card">
        <div class="rs-tile-label">All props in this group priced 45–55¢</div>
        <div class="rs-tile-num dash-skeleton" data-source="cat_counts" data-where="cat={k}" data-field="all">—</div>
        <div class="rs-tile-note">Before the &gt;50% filter</div>
      </div>
      <div class="rs-card rs-rule">
        <div class="rs-tile-label">Rule</div>
        <p class="rs-rule-text">{rule}</p>
      </div>
    </section>
    <section class="rs-card" id="cat-{k}-props">
      <h2>{k} · {title}</h2>
      <p class="rs-note">Same filter as before: Yes price 45–55¢ (Saturday ~10:30 PM CT for Sunday games, Sunday ~11 PM CT for Monday night), condition fulfilled in more than half of the relevant 2026 games. Switch to “All 45–55¢ props” to drop the hit-rate filter. Rows for games that have kicked off are dimmed.</p>
      <div class="rs-controls">
        <select class="rc-show" aria-label="Which props">
          <option value="q">Hit &gt;50% only</option>
          <option value="all">All 45–55¢ props</option>
        </select>
        <select class="rc-game" aria-label="Game"></select>
        <label><input type="checkbox" class="rc-clean"> Hide flagged</label>
        <label><input type="checkbox" class="rc-upcoming"> Hide games that have kicked off</label>
        <input type="search" class="rc-search" placeholder="Search player, team, line…" aria-label="Search props">
        <span class="rs-count rc-count"></span>
      </div>
      <div class="rs-tablebox">
        <table class="rs-table rc-table" id="cat-{k}-table" data-source="props" data-row-key="id">
          <thead><tr>
            <th data-field="game"><button data-k="game">Game</button></th>
            <th data-field="kickoff" class="rs-hide-narrow"><button data-k="kickoff_utc">Kickoff</button></th>
            <th data-field="contract"><button data-k="contract">Line</button></th>
            <th data-field="market" class="rs-hide-narrow"><button data-k="market">Market</button></th>
            <th data-field="pos"><button data-k="pos">Pos</button></th>
            <th data-field="team"><button data-k="team">Team</button></th>
            <th data-field="team_ml" class="num"><button data-k="team_ml">ML ¢</button></th>
            <th data-field="opp_rank_vs_pos" class="num"><button data-k="opp_rank_vs_pos">Opp D rank</button></th>
            <th data-field="yes_price" class="num"><button data-k="yes_price">Price ¢</button></th>
            <th data-field="hit_rate" class="rs-barcell"><button data-k="hit_rate">Hit rate</button></th>
            <th data-field="hits" class="num"><button data-k="hits">Hits</button></th>
            <th data-field="games" class="num"><button data-k="games">Games</button></th>
            <th data-field="season_results" class="rs-hide-narrow"><button data-k="season_results">2026 results</button></th>
            <th data-field="flags"><button data-k="flags">Flags</button></th>
          </tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </section>
  </div>'''

cat_pages = ''.join(cat_page(k) for k in CATS)

html = open(B + 'page_template.html').read()
html = html.replace('<!--CAT_TABS-->', cat_tabs).replace('<!--CAT_PAGES-->', cat_pages)
open(B + 'index.html', 'w').write(html)
print('written', len(html))
