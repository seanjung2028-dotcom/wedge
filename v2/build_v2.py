"""Build V2 (the Wedge) from V1's built page (rh/index_full.html), leaving V1 untouched.
Structure: Home | NFL (Research, The Winning Edge, Thesis, Database: Charts & Trends, Analysts, Results) | NBA (same) | Soccer."""
import re, json, subprocess, sys
B = '/home/claude/wedger/'
V = B + 'v2/'
s = open(B + 'rh/index_full.html').read()

def rep(a, b, n=1, src=None):
    global s
    t = s if src is None else src
    c = t.count(a)
    assert c == n, f'expected {n} of {a[:90]!r}, found {c}'
    t = t.replace(a, b)
    if src is None: s = t
    return t

def div_span(t, start):
    """[start, end) of the <div ...> beginning at start, matching nested divs."""
    depth = 0
    for m in re.finditer(r'<(/?)div\b[^>]*>', t[start:]):
        depth += -1 if m.group(1) else 1
        if depth == 0: return start, start + m.end()
    raise ValueError('unbalanced')

def page_span(pid):
    m = re.search(r'<div class="rs-page[^"]*" id="%s"[^>]*>' % re.escape(pid), s)
    assert m, pid
    return div_span(s, m.start())

def cut_page(pid):
    global s
    a, b = page_span(pid); s = s[:a] + s[b:]

def sec_span(t, sid, tag='section'):
    m = re.search(r'<%s\b[^>]*\bid="%s"[^>]*>' % (tag, re.escape(sid)), t)
    assert m, sid
    a = m.start(); depth = 0
    for mm in re.finditer(r'<(/?)%s\b[^>]*>' % tag, t[a:]):
        depth += -1 if mm.group(1) else 1
        if depth == 0: return a, a + mm.end()
    raise ValueError(sid)

# split markup / css / js
i = s.index('<script>'); j = s.rindex('</script>')
js = s[i + 8:j]; s = s[:i] + '@@JS@@' + s[j + 9:]

# ======================= markup =======================
# --- nav
a = s.index('<nav class="rs-tabs wg-nav"'); b = s.index('</nav>', a) + 6
CARET = '<svg class="wg-caret" viewBox="0 0 10 6" aria-hidden="true"><path d="M1 1l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
def dd(sport, label, items):
    out = [f'<div class="wg-dd" id="{sport}-dd">',
           f'  <button type="button" class="rs-tab wg-dd-btn" id="{sport}-btn" aria-haspopup="true" aria-expanded="false" aria-controls="{sport}-menu">{label}<span class="wg-dd-cur"></span>{CARET}</button>',
           f'  <div class="wg-dd-menu" id="{sport}-menu" role="menu" aria-labelledby="{sport}-btn" hidden>']
    for it in items:
        if it[0] == 'label': out.append(f'    <div class="wg-dd-label" aria-hidden="true">{it[1]}</div>')
        elif it[0] == 'sep': out.append('    <div class="wg-dd-sep" role="separator"></div>')
        else: out.append(f'    <button type="button" class="wg-dd-item{" wg-dd-sub" if len(it) > 2 else ""}" role="menuitem" data-page="{it[0]}">{it[1]}</button>')
    out += ['  </div>', '</div>']
    return '\n    '.join(out)
NAV = f'''<nav class="rs-tabs wg-nav" aria-label="Sections">
    <button type="button" class="rs-tab" data-page="lobby" aria-current="page">Home</button>
    {dd('nfl', 'NFL', [('label', 'Week 9'), ('research', 'Research'), ('final', 'The Winning Edge'), ('thesis', 'Thesis', 1), ('sep',), ('label', 'Database'), ('charts', 'Charts &amp; Trends'), ('analysts', 'Analysts'), ('results', 'Results')])}
    {dd('nba', 'NBA', [('label', 'Tonight'), ('nba', 'Research'), ('nba-edge', 'The Winning Edge'), ('nba-thesis', 'Thesis', 1), ('sep',), ('label', 'Database'), ('nba-charts', 'Charts &amp; Trends'), ('nba-analysts', 'Analysts'), ('nba-results', 'Results')])}
    <button type="button" class="rs-tab" data-page="soccer">Soccer</button>
  </nav>'''
s = s[:a] + NAV + s[b:]

# --- logo: an ink version for the light top of the page
rep('<img src="/_blob/ee61fb3a382bb851df8754438f5fc0d6" alt="Wedge" width="112" height="40">',
    '<img class="v2-logo-l" src="/_blob/ee61fb3a382bb851df8754438f5fc0d6" alt="Wedge" width="112" height="40"><img class="v2-logo-i" src="/_blob/574a1535b4f45851e0d51298efe3d357" alt="" width="112" height="40" aria-hidden="true">')

# --- drop pages: prop categories, defense ranks, anytime TD, backtest, subscribe, the old paywall page
for pid in ['subscribe', 'cat-1', 'cat-2', 'cat-3', 'cat-4', 'defense', 'atd', 'backtest', 'unlock']:
    cut_page(pid)

# --- Home: drop the ticker belt, membership plans and the "good result" quote with its ledger
a = s.index('<div class="wz-ticker" id="wz-ticker"'); a, b = div_span(s, a); s = s[:a] + s[b:]
a, b = sec_span(s, 'wz-plans'); s = s[:a] + s[b:]
m = re.search(r'<section class="pf-quote[^"]*"[^>]*>', s); a = m.start(); b = s.index('</section>', a) + 10; s = s[:a] + s[b:]
rep('data-wz-jump="wz-reads">This week\'s reads</button>', 'data-wz-jump="v2-matchups">This week\'s matchups</button>')
rep('<button type="button" class="wz-btn wz-btn-line" data-go="analysts">Picks by team</button>', '<button type="button" class="wz-btn wz-btn-line" data-go="analysts">Every analyst pick</button>')
# Home no longer carries "The analysts." (the standings live on NFL > Analysts); the hero's record button goes there
a, b = sec_span(s, 'wz-analysts'); s = s[:a] + s[b:]
rep('<button type="button" class="wz-btn wz-btn-w" data-wz-jump="wz-analysts">See the record ↗</button>', '<button type="button" class="wz-btn wz-btn-w" data-go="analysts">See the record ↗</button>')
# Picks by matchup (relocated "Picks by team", one tile per game), then the reads it opens
MATCH = '''<section class="pf-sec wz-reveal" id="v2-matchups" aria-labelledby="pm-h">
      <div class="pf-head">
        <div><span class="pf-label">01 / This week</span><h2 class="pf-h2" id="pm-h">Picks by matchup.</h2></div>
        <p class="pf-sub">Every Week 9 game. Select a matchup for its final lines and leans from The Winning Edge.</p>
      </div>
      <div class="pf-tgrid v2-mgrid" id="v2-mgrid" role="group" aria-label="Week 9 matchups"><p class="wx-empty">Loading this week's matchups…</p></div>
    </section>

    '''
a, b = sec_span(s, 'wz-reads')
READS = '''<section class="pf-sec v2-reads" id="wz-reads" aria-labelledby="reads-h" hidden>
      <div class="pf-head">
        <div><span class="pf-label">01 / The Winning Edge</span><h2 class="pf-h2" id="reads-h">The reads.</h2></div>
        <p class="pf-sub" id="wx-reads-sub">Select a matchup above.</p>
      </div>
      <div class="wz-matchup" id="wz-matchup" hidden></div>
      <div class="wx-reads" id="wg-hot-cards" aria-live="polite"></div>
      <div class="pf-row" id="v2-reads-row"><button type="button" class="wz-btn wz-btn-line" id="v2-reads-edge">Open in The Winning Edge ↗</button><button type="button" class="wz-btn wz-btn-line" id="v2-reads-thesis">Read the thesis ↗</button><button type="button" class="wz-link" id="v2-reads-close">Back to the matchups</button></div>
    </section>'''
s = s[:a] + MATCH + READS + s[b:]
rep('<span class="pf-label">04 / Schedule</span>', '<span class="pf-label">02 / Schedule</span>')
rep('<span class="pf-label">05 / Method</span>', '<span class="pf-label">03 / Method</span>')
rep('<p class="pf-sub">Reads open as Robinhood lists each game. Select a game for its reads.</p>', '<p class="pf-sub">Every game this week. Select one for its final lines and leans.</p>')

# --- Analysts: "Picks by team" moved to Home as "Picks by matchup"
a, b = sec_span(s, 'pf-teams'); s = s[:a] + s[b:]
rep('<div class="rs-page" id="analysts" hidden>', '<div class="rs-page" id="analysts" hidden>\n  <header class="wx-band"><span class="wx-label"><i class="wx-dot" aria-hidden="true"></i>NFL / Database</span><h2>Analysts.</h2><p>Every pick tracked and settled against the box score<br>Picks by matchup now live on Home</p></header>')
# the analyst application was linked from Home's analysts section; it now sits under the standings
rep('<section class="wg-board" id="an-board" data-source="results lines" aria-label="Analyst standings"></section>',
    '<section class="wg-board" id="an-board" data-source="results lines" aria-label="Analyst standings"></section>\n    <div class="pf-row v2-an-row"><button type="button" class="wz-link" data-go="apply">Apply to be an analyst</button></div>')

# --- Research: lines and projections in one page
la, lb = page_span('lines'); lines_page = s[la:lb]
pa, pb = page_span('proj'); proj_page = s[pa:pb]
def inner(pg):
    body = pg[pg.index('>') + 1: pg.rindex('</div>')]
    body = re.sub(r'<header class="wx-band">[\s\S]*?</header>', '', body, count=1)
    return body
RESEARCH = f'''<div class="rs-page v2-research" id="research" hidden>
  <header class="wx-band"><span class="wx-label"><i class="wx-dot" aria-hidden="true"></i>NFL / Week 9</span><h2>Research.</h2><p><span data-wg-count="every">6,393</span> lines at any price, with our projection beside each<br>Select any line to open its file</p></header>
  <div class="v2-seg" role="tablist" aria-label="Research view">
    <button type="button" role="tab" class="v2-seg-b" id="v2-rv-lines" aria-selected="true" data-view="lines">Every line</button>
    <button type="button" role="tab" class="v2-seg-b" id="v2-rv-proj" aria-selected="false" data-view="proj" tabindex="-1">Projections before the lines post</button>
  </div>
  <div class="v2-rv" id="v2-rv-lines-p">{inner(lines_page)}</div>
  <div class="v2-rv" id="v2-rv-proj-p" hidden>{inner(proj_page)}</div>
</div>'''
# remove both, insert research where lines was
first, second = sorted([(la, lb), (pa, pb)])
s = s[:second[0]] + s[second[1]:]
s = s[:first[0]] + RESEARCH + s[first[1]:]
rep('<option value="every">Every line, any price</option>', '<option value="every" selected>Every line, any price</option>')
# projection column beside Wedge %
_i = s.index('id="lines-table"'); _a = '<th data-field="role" class="rs-hide-narrow"><button data-k="role"'; _j = s.index(_a, _i)
s = s[:_j] + '<th class="v2-pjth"><span title="Our projection for this player and stat: bear, base and bull">Bear · Base · Bull</span></th> ' + s[_j:]

rep('''<p class="rs-note">Every Week 9 line priced 45–55¢, updated Sat Nov 7 at 2:25 PM CT. Where Robinhood has no line yet, the price comes from the sportsbooks. Hit rate is how often the line came true in his 2026 games; Wedge % is our chance it comes true this week. Select a player prop for the full read.''',
    '''<p class="rs-note">Every Week 9 line at any price (switch to 45–55¢ in the first menu), updated Sat Nov 7 at 2:25 PM CT. Where Robinhood has no line yet, the price comes from the sportsbooks. Hit rate is how often the line came true in his 2026 games; Wedge % is our chance it comes true this week; Bear · Base · Bull is our projection for that player and stat. Select any line to open its file: the bull, the bear and the base, the injury report, and the game script.''')
rep('''Select a row for the full read.</p>''', '''Select any row to open its file.</p>''')

# --- The Winning Edge (the final card page) and the Thesis page
rep('<h2>Final card.</h2><p>Every remaining game, every threshold, any price<br>', '<h2>The Winning Edge.</h2><p>Final lines and leans for every remaining game · every threshold, any price<br>')
fa, fb = page_span('final')
THESIS = '''
<div class="rs-page v2-thesis" id="thesis" hidden>
  <header class="wx-band"><span class="wx-label"><i class="wx-dot" aria-hidden="true"></i>NFL / Week 9 · The Winning Edge</span><h2>Thesis.</h2><p>The game, the line and the player, before the price<br><span id="v2-th-when">Prices checked Sat Nov 7</span></p></header>
  <div class="wx-tabs v2-th-tabs" role="tablist" id="v2-th-tabs" aria-label="Games"></div>
  <div id="v2-th-root"><p class="wx-empty">Loading the thesis…</p></div>
</div>'''
s = s[:fb] + THESIS + s[fb:]

# --- Charts & Trends heading
rep('<h2>The record.</h2><p>Every 45–55¢ line at Robinhood\'s price</p>', '<h2>Charts &amp; trends.</h2><p>Weeks 1–8 · every 45–55¢ line at Robinhood\'s price</p>')

# --- NBA in the NFL's layout: Research | The Winning Edge | Thesis | Charts & Trends | Analysts | Results
na, nb = page_span('nba'); nba = s[na:nb]
def take(t, sid):
    a2, b2 = sec_span(t, sid); return t[a2:b2], t[:a2] + t[b2:]
rec, nba = take(nba, 'nba-rec')
bt, nba = take(nba, 'nba-bt')
nba = nba.replace('<h2>NBA lines.</h2><p>The 45–55¢ screen</p>', '<h2>Research.</h2><p>NBA · the 45–55¢ screen with the read behind each line<br>Select any line for its file</p>', 1)
def nba_page(pid, label, h2, p, body):
    return f'''
<div class="rs-page" id="{pid}" hidden>
  <header class="wx-band"><span class="wx-label"><i class="wx-dot" aria-hidden="true"></i>NBA / {label}</span><h2>{h2}</h2><p>{p}</p></header>
  {body}
</div>'''
def soon(t, p):
    return f'<section class="wg-soon v2-soon"><span class="wg-kick">Not yet</span><h3>{t}</h3><p>{p}</p></section>'
NBA_MORE = (nba_page('nba-edge', 'The Winning Edge', 'The Winning Edge.', 'Final lines and leans, built the same way as the NFL card',
                     soon('No NBA slate has been run through the final-lines process yet.', 'When one is, its final lines, conditional leans and passes appear here with the same record as the NFL card: line and price, why it’s on the card, evidence, where it loses and the decision.'))
            + nba_page('nba-thesis', 'Thesis', 'Thesis.', 'The game, the line and the player',
                       soon('The NBA thesis opens with the first NBA final card.', 'Each game will get its keys, its three scripts and the thesis behind every line on the card.'))
            + nba_page('nba-charts', 'Database', 'Charts &amp; trends.', 'The 2025-26 backtest on real prices', bt)
            + nba_page('nba-analysts', 'Database', 'Analysts.', 'Analyst picks',
                       soon('Analyst picks are tracked for the NFL so far.', 'NBA picks will be filed and settled the same way once analysts start posting them.'))
            + nba_page('nba-results', 'Database', 'Results.', 'The live record, settled from the box score', rec))
s = s[:na] + nba + NBA_MORE + s[nb:]

# --- the file (outlook) dialog becomes a manila folder with three tabs
rep('<dialog class="wg-sitdlg" id="sit-dlg" aria-labelledby="sit-title">', '<dialog class="wg-sitdlg v2-folder" id="sit-dlg" aria-labelledby="sit-title">')
rep('''<div class="wg-sd-kicker" id="sit-kicker">Outlook</div>''', '''<div class="wg-sd-kicker" id="sit-kicker">Research file</div>''')
rep('''<button type="button" class="wg-sd-tab" role="tab" id="sit-t-ov" aria-controls="sit-p-ov" aria-selected="true">Overview</button>
          <button type="button" class="wg-sd-tab" role="tab" id="sit-t-mu" aria-controls="sit-p-mu" aria-selected="false" tabindex="-1">Matchup &amp; script</button>
          <button type="button" class="wg-sd-tab" role="tab" id="sit-t-hi" aria-controls="sit-p-hi" aria-selected="false" tabindex="-1">History</button>''',
    '''<button type="button" class="wg-sd-tab" role="tab" id="sit-t-ov" aria-controls="sit-p-ov" aria-selected="true"><span class="v2-tl">The Bull, the Bear, and the Base</span><span class="v2-ts" aria-hidden="true">Bull · Bear · Base</span></button>
          <button type="button" class="wg-sd-tab" role="tab" id="sit-t-inj" aria-controls="sit-p-inj" aria-selected="false" tabindex="-1"><span>Injury Report</span></button>
          <button type="button" class="wg-sd-tab" role="tab" id="sit-t-mu" aria-controls="sit-p-mu sit-p-hi" aria-selected="false" tabindex="-1"><span>Game Script</span></button>''')
rep('''<div class="wg-sd-panel" id="sit-p-mu" role="tabpanel" aria-labelledby="sit-t-mu" hidden></div>''',
    '''<div class="wg-sd-panel" id="sit-p-inj" role="tabpanel" aria-labelledby="sit-t-inj" hidden></div>
        <div class="wg-sd-panel" id="sit-p-mu" role="tabpanel" aria-labelledby="sit-t-mu" hidden></div>''')
rep('''<div class="wg-sd-panel" id="sit-p-hi" role="tabpanel" aria-labelledby="sit-t-hi" hidden>''', '''<div class="wg-sd-panel" id="sit-p-hi" role="tabpanel" aria-labelledby="sit-t-mu" hidden>''')
rep('''<div class="wg-sd-sech"><h3 id="sit-log-h">Game log</h3>''', '''<div class="wg-sd-sech"><h3 id="sit-log-h">Every game against the line</h3>''')
rep('''<div class="wg-sd-in">
      <div class="wg-sd-head">''', '''<div class="wg-sd-in"><span class="v2-cover" aria-hidden="true"></span><span class="v2-clip" aria-hidden="true"></span>
      <div class="wg-sd-head">''')

# ======================= script =======================
def jrep(a, b, n=1):
    global js
    c = js.count(a); assert c == n, f'js: expected {n} of {a[:90]!r}, found {c}'; js = js.replace(a, b)
def jcut(a, b, repl):
    global js
    i2 = js.index(a); j2 = js.index(b, i2); js = js[:i2] + repl + js[j2:]

# dropped pages' code
jcut('  // ---------------- category pages ----------------', '  // ---------------- Week 8 projections ----------------', '  const catPages = [];\n\n')
jcut('  // ---------------- defense table ----------------', '  // ---------------- anytime TD page ----------------', '  function drawDefense() {}\n\n')
jcut('  // ---------------- anytime TD page ----------------', '  // ---------------- week 6 results ----------------', '  function drawAtd() {}\n\n')
jcut('  // ---------------- weeks 1-5 backtest ----------------', '  // ---------------- charts tab ----------------', '  function drawBtPerms() {}\n  function drawBtLines() {}\n\n')

# Home's analyst board is gone; the hero chip (analyst win %) still computes from the standings
jrep("    const box = $('#wz-board'); if (!box) return;", "    const box = $('#wz-board');")
jrep("    box.replaceChildren(...(cards.length ? cards : [el('p', 'wx-empty', 'No analysts yet.')]));", "    if (box) box.replaceChildren(...(cards.length ? cards : [el('p', 'wx-empty', 'No analysts yet.')]));")
# every line row and line card gets the read card's sheen on hover
_n = js.index('  function drawNba() {'); _m = js.index('  function drawProj() {')
_seg = js[_n:_m]; assert _seg.count('wzTint(tr, r);') == 1
js = js[:_n] + _seg.replace('wzTint(tr, r);', 'wzTint(tr, r); v2Sheen(tr, r, true);') + js[_m:]
jrep('wzTint(tr, r);\n', 'wzTint(tr, r); v2Sheen(tr, r);\n', js.count('wzTint(tr, r);\n'))
jrep("      const tr = el('tr', 'fc-row'); tr.tabIndex = 0;", "      const tr = el('tr', 'fc-row'); tr.tabIndex = 0; v2Sheen(tr, { game: c.game, contract: p.player });")
jrep("""      const tr = document.createElement('tr'); tr.dataset.key = r.id;
      const td = mkTd(tr);
      td(r.analyst, 'rs-contract');""", """      const tr = document.createElement('tr'); tr.dataset.key = r.id; v2Sheen(tr, r);
      const td = mkTd(tr);
      td(r.analyst, 'rs-contract');""")
jrep("""      const tr = document.createElement('tr'); tr.dataset.key = r.id;
      const ck = keyOfResult(r);""", """      const tr = document.createElement('tr'); tr.dataset.key = r.id; v2Sheen(tr, r);
      const ck = keyOfResult(r);""")
jrep("    const a = el('article', 'fc-play fc-p-' + (FC_CLS[p.decision] || 'pass'));", "    const a = el('article', 'fc-play fc-p-' + (FC_CLS[p.decision] || 'pass')); v2Sheen(a, { game: c.game, contract: p.player });")
jrep('    root.replaceChildren(top, games, post);', '    root.replaceChildren(...v2EdgeLayout(all, top, games), post);')
jrep("        const mid = el('span'); mid.append(el('b', null, `${wzTeam(a)[0]} at ${wzTeam(h)[0]}`), el('small', null, `${g} · ${String(v.ko).replace(/\s*(Thu|Fri|Sat|Sun|Mon)$/, '')}`));",
     "        const mid = el('span'); mid.append(el('b', null, g), el('small', null, String(v.ko).replace(/\s*(Thu|Fri|Sat|Sun|Mon)$/, '')));")
# The Winning Edge: no lede paragraph above the card; a short note on grading at the end
jrep('    top.append(stats, lede, how, tbl);', '    top.append(stats, how, tbl); void lede;')
_pa = js.index("    const post = el('p', 'fc-post', 'Postgame grading:"); _pb = js.index('\n', _pa)
js = js[:_pa] + "    const post = el('p', 'fc-post', 'Postgame grading: every line, passes included, is logged at its pre-kickoff price, then graded on the read and on the price.');" + js[_pb:]
# speed: Research starts with 100 rows (Show more adds 300) instead of 500
jrep("px: '', lim: 500, clean: false", "px: '', lim: 100, clean: false")
jrep('ls.lim = 500;', 'ls.lim = 100;', js.count('ls.lim = 500;'))
jrep('ls.lim += 500;', 'ls.lim += 300;')
# navigation: several dropdowns, page aliases, scroll to top
nav_a = js.index('  // ---------------- navigation ----------------')
nav_b = js.index("  navBtns.forEach((b) => b.addEventListener('click', () => showPage(b.dataset.page)));")
NAVJS = open(V + 'src/nav.js').read()
js = js[:nav_a] + NAVJS + js[nav_b:]
jrep("  navBtns.forEach((b) => b.addEventListener('click', () => showPage(b.dataset.page)));",
     "  navBtns.forEach((b) => b.addEventListener('click', () => { showPage(b.dataset.page); v2Top(); }));")
jrep('''  const hash = location.hash.slice(1);
  if (PAGES.includes(hash)) showPage(hash);''', '''  const hash = location.hash.slice(1);
  if (PAGES.includes(hash) || V2_ALIAS[hash]) showPage(hash);''')

# the file dialog: three tabs (Bull/Bear/Base, Injury Report, Game Script = matchup + history), page flips
jrep("  const TABS = [['ov', 'sit-t-ov', 'sit-p-ov'], ['mu', 'sit-t-mu', 'sit-p-mu'], ['hi', 'sit-t-hi', 'sit-p-hi']];",
     "  const TABS = [['ov', 'sit-t-ov', ['sit-p-ov']], ['inj', 'sit-t-inj', ['sit-p-inj']], ['mu', 'sit-t-mu', ['sit-p-mu', 'sit-p-hi']]];")
jrep('''  const showTab = (k, focus) => {
    sit.tab = k;
    TABS.forEach(([id, tb, pn]) => { const on = id === k; const b = $('#' + tb); b.setAttribute('aria-selected', String(on)); b.tabIndex = on ? 0 : -1; $('#' + pn).hidden = !on; if (on && focus) b.focus(); });
    moveInk();
    const panel = $('#' + TABS.find((x) => x[0] === k)[2]);
    animIn(panel);
    if (k === 'hi') drawSitLog(true);
  };''', '''  const showTab = (k, focus) => {
    const prev = sit.tab; sit.tab = k; sitDlg.dataset.v2tab = k;
    const leaf = v2LeafStart(prev, k);
    TABS.forEach(([id, tb, pns]) => { const on = id === k; const b = $('#' + tb); b.setAttribute('aria-selected', String(on)); b.tabIndex = on ? 0 : -1; pns.forEach((pn) => { $('#' + pn).hidden = !on; }); if (on && focus) b.focus(); });
    moveInk();
    v2Flip(prev, k, leaf);
    TABS.find((x) => x[0] === k)[2].forEach((pn) => animIn($('#' + pn)));
    if (k === 'mu') drawSitLog(true);
  };''')
jrep("    Object.assign(sit, { r, ctx, O, sp, det: sp.sit(r.sit_key), sel: null, tab: 'ov' });",
     "    Object.assign(sit, { r, ctx, O, sp, det: sp.sit(r.sit_key), sel: null, tab: 'ov', lite: false });")
jrep('''    renderSit();
    showTab('ov');
  }''', '''    renderSit();
    v2AfterFile();
    showTab('ov');
  }''')
# the history block becomes a function so files without a full outlook can show it too
h_a = js.index('    // ---------- History ----------')
h_b = js.index("    $('#sit-foot').textContent = sp.foot || '';\n  }", h_a)
hist = js[h_a:h_b]
js = js[:h_a] + "    sitHistory(det, stat, line, price, sp);\n" + js[h_b:]
jrep('  function selectSit(sel) {', '  function sitHistory(det, stat, line, price, sp) {\n' + hist + '  }\n\n  function selectSit(sel) {')

# NBA pages: the record and backtest charts moved to their own pages
jrep("    const d = dash.data('nba_results'), page = $('#nba');", "    const d = dash.data('nba_results'), page = $('#nba-results');")
jrep("    if (page && !page.hidden) drawNbaBt();", "    { const pc = $('#nba-charts'); if (pc && !pc.hidden) drawNbaBt(); }")
jrep("window.addEventListener('resize', () => { const p = $('#nba'); if (!p || p.hidden) return;", "window.addEventListener('resize', () => { const p = [$('#nba-results'), $('#nba-charts')].find((x) => x && !x.hidden); if (!p) return;")

jrep("    $('#sit-kicker').textContent = `Outlook · ${team} ${O.pos || ''} vs ${opp}`;", "    $('#sit-kicker').textContent = `Research file · ${team} ${O.pos || ''} vs ${opp}`;")
jrep("  const ls = { show: 'q', game: '',", "  const ls = { show: 'every', game: '',")

# Research table: projection column, every row opens a file
jrep('''      sitCell(tr, r, { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source });
      roleCell(tr, r);''', '''      sitCell(tr, r, { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source });
      v2ProjCell(tr, r);
      roleCell(tr, r);''')
jrep('''      td(r.flags, 'rs-flag');
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
  }

  // ---------------- NBA lines ----------------''', '''      td(r.flags, 'rs-flag');
      if (!tr.classList.contains('wg-click')) v2Clickable(tr, r);
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
  }

  // ---------------- NBA lines ----------------''')
jrep('''      td(r.flags, 'rs-flag');
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
  }

  function drawDefense() {}''', '''      td(r.flags, 'rs-flag');
      if (!tr.classList.contains('wg-click')) v2Clickable(tr, { ...r, yes_price: '', yes_bid: '' });
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
  }

  function drawDefense() {}''')

# Home: matchups replace the game tabs; the schedule opens the same reads
jrep('''    if (la.status === 'ok') wxTabs(la.data);
    if (ld.status === 'ok' || la.status === 'ok') wxDraw();
    wzLobby();''', '''    wzLobby();
    v2Home();''')
jrep("        b.addEventListener('click', () => { wxGame = g; try { localStorage.setItem('wx-read-game', g); } catch (e) { /* storage unavailable */ } wxDraw(); const t = $('#wz-reads'); if (t) t.scrollIntoView({ behavior: WZ_REDUCE ? 'auto' : 'smooth', block: 'start' }); });",
     "        b.addEventListener('click', () => v2SelectGame(g, true));")
jrep("const st = el('span', 'wz-st' + (!off && n ? ' live' : ''), off ? 'Kicked off' : (n ? `${n} read${n === 1 ? '' : 's'}` : 'Lines open'));",
     "const st = el('span', 'wz-st' + (!off && v2PlayN(g) ? ' live' : ''), off ? 'Kicked off' : v2PlayTag(g));")

# The Winning Edge: the game's thesis moves to the Thesis page
jrep('    body.append(s1, s3, s4, s7, sp);', '    body.append(v2ThesisLink(c), s7, sp);')

# render: V2 pieces redraw with the data
jrep('''    drawLobby();
    drawAnalysts();''', '''    drawLobby();
    drawAnalysts();
    v2OnData();''')

# V2 modules go in before the render block
V2JS = open(V + 'src/v2.js').read()
jrep('  // ---------------- render ----------------', V2JS + '\n  // ---------------- render ----------------')

# ======================= styles =======================
css_blocks = re.findall(r'<style>([\s\S]*?)</style>', s)
last = [c for c in css_blocks if '/* ===================== Wedge round 3' in c][0]
print('style blocks', len(css_blocks), [len(c) for c in css_blocks])
# tokens for the light top of the page: the last brand layer's hard-coded whites and near-blacks become variables
r3 = last.index('/* ===================== Wedge round 3')
pre, post = last[:r3], last[r3:]
# V1's styles stay exactly as V1 has them (V2 uses V1's look)
new_last = pre + post + '\n' + open(V + 'src/v2.css').read()
s = s.replace('<style>' + last + '</style>', '<style>' + new_last + '</style>', 1)

# sport pages get the open layout (no boxed cards; hairlines and space between sections)
for pid in ['research', 'final', 'thesis', 'charts', 'analysts', 'results', 'nba', 'nba-edge', 'nba-thesis', 'nba-charts', 'nba-analysts', 'nba-results']:
    m = re.search(r'<div class="rs-page([^"]*)" id="%s"' % re.escape(pid), s); assert m, pid
    s = s[:m.start()] + '<div class="rs-page%s v2-open" id="%s"' % (m.group(1), pid) + s[m.end():]
# Home's section language on the sport pages: "01 / Label" over a big uppercase headline
HEADS = {
    'research': {'Lines': ('Week 9 board', 'Every line.'), 'By game': ('By game', 'Game by game.'),
                 'Week 9 projections · player props before the lines post': ('Week 9 projections', 'Before the lines post.')},
    'charts': {'Role, game script and scheme · which spots clear the line': ('Role, script and scheme', 'Which spots clear the line.'),
               'Research · what other prop models weigh, tested on 2023–26': ('Research · 2023–26', 'What other prop models weigh.'),
               "Week by week · every 45–55¢ line at Robinhood's price": ('Week by week', "Every 45–55¢ line at Robinhood's price."),
               'Week by week · player props against the line books would set': ('Week by week · props', 'Against the line books would set.'),
               'Momentum · do the last four games beat the season?': ('Momentum', 'Do the last four games beat the season?'),
               'Teams · first four games vs the last four': ('Teams', 'First four games vs the last four.'),
               'Weeks 1–5 · hit rate by factor': ('Weeks 1–5', 'Hit rate by factor.'), 'Weeks 1–5 · any combination of factors': ('Weeks 1–5', 'Any combination of factors.'),
               'Weeks 1–5 · two factors at once': ('Weeks 1–5', 'Two factors at once.'), 'Week 6 · win rate by group': ('Week 6', 'Win rate by group.'),
               'Week 9 board · season hit rate vs price': ('Week 9 board', 'Season hit rate vs price.')},
    'analysts': {'Analyst picks': ('Every pick', 'Analyst picks.')},
    'results': {'Week 6 record by group': ('Week 6', 'Record by group.'), 'Every line, settled': ('The record', 'Every line, settled.')},
    'nba': {'NBA lines': ('The NBA board', 'Every line.'), 'By game': ('By game', 'Game by game.'), 'How the NBA screen and outlook work': ('Method', 'How the screen and outlook work.')},
    'nba-charts': {'NBA backtest · the filter and the model on 2025-26 prices': ('NBA backtest', 'The filter and the model on 2025-26 prices.')},
    'nba-results': {'NBA live record · how the posted lines did': ('NBA live record', 'How the posted lines did.')},
}
def page_span(pid):
    m = re.search(r'<div class="rs-page[^"]*" id="%s"' % re.escape(pid), s); assert m, pid
    n = re.search(r'<div class="rs-page[^"]*" id=', s[m.end():])
    return m.start(), (m.end() + n.start()) if n else s.index('<dialog', m.end())
for pid, H in HEADS.items():
    a0, b0 = page_span(pid); seg = s[a0:b0]; k = 0
    def one(mm):
        global k
        txt = re.sub(r'<[^>]+>', '', mm.group(2)).replace('&amp;', '&')
        if txt not in H: raise KeyError((pid, txt))
        k += 1; lab, hd = H[txt]
        return (f'{mm.group(1)}<div class="pf-head v2-head"><div><span class="pf-label">{k:02d} / {lab.replace("&", "&amp;")}</span>'
                f'<h2 class="pf-h2 v2-h2">{hd.replace("&", "&amp;")}</h2></div></div>')
    seg2 = re.sub(r'(<section class="rs-card[^"]*"[^>]*>\s*)<h2>(.*?)</h2>', one, seg)
    assert k == len(H), (pid, k, len(H))
    s = s[:a0] + seg2 + s[b0:]
# a strip of the sport's pages under each page title, styled like Home's nav
def subnav(sport, items):
    out = [f'<nav class="v2-subnav" aria-label="{sport} pages">']; n = 0
    for it in items:
        if it[0] == 'label': out.append(f'<span class="v2-sn-g">{it[1]}</span>')
        else: n += 1; out.append(f'<button type="button" class="v2-sn" data-page="{it[0]}"><i>{n:02d}</i>{it[1]}</button>')
    return ''.join(out) + '</nav>'
SN = {'NFL': subnav('NFL', [('label', 'Week 9'), ('research', 'Research'), ('final', 'The Winning Edge'), ('thesis', 'Thesis'), ('label', 'Database'), ('charts', 'Charts &amp; Trends'), ('analysts', 'Analysts'), ('results', 'Results')]),
      'NBA': subnav('NBA', [('label', 'Tonight'), ('nba', 'Research'), ('nba-edge', 'The Winning Edge'), ('nba-thesis', 'Thesis'), ('label', 'Database'), ('nba-charts', 'Charts &amp; Trends'), ('nba-analysts', 'Analysts'), ('nba-results', 'Results')])}
for pid in ['research', 'final', 'thesis', 'charts', 'analysts', 'results', 'nba', 'nba-edge', 'nba-thesis', 'nba-charts', 'nba-analysts', 'nba-results']:
    a0, b0 = page_span(pid); seg = s[a0:b0]
    e = seg.index('</header>') + len('</header>')
    seg = seg[:e] + '\n  ' + SN['NBA' if pid.startswith('nba') else 'NFL'] + seg[e:]
    s = s[:a0] + seg + s[b0:]
# ---- round 7: fewer words. Home's hero, matchups and schedule, and every sport page's title, lose their descriptions
rep('        <div class="pf-chips"><span class="pf-chip"><i class="wx-dot" aria-hidden="true"></i><span id="wz-kick">NFL · Week 9</span></span></div>\n', '')
rep("        <p class=\"pf-lede\">Analyst picks and certified reads on Robinhood's football markets. Every result stays on the record.</p>\n", '')
rep("""        <div class="pf-chips">
          <span class="pf-chip"><b data-wz="cert-wl">—</b> certified</span>
          <span class="pf-chip"><b data-wz="cert-profit">—</b> net</span>
          <span class="pf-chip g"><b data-wz="an-pct">—</b> analysts</span>
        </div>
        <span class="pf-cap"><span data-wz="cert-rec">Settled picks, before fees</span> · positions, not returns · misses stay posted</span>""",
    """        <div class="v2-proof-row">
          <span class="v2-ps"><b data-wz="cert-wl">—</b>certified</span>
          <span class="v2-ps v2-ps-net"><b data-wz="cert-profit">—</b>net</span>
        </div>""")
rep('        <p class="pf-sub">Every Week 9 game. Select a matchup for its final lines and leans from The Winning Edge.</p>\n', '')
rep('<p class="pf-sub" id="wx-reads-sub">Select a matchup above.</p>', '<p class="pf-sub" id="wx-reads-sub" hidden>Select a matchup above.</p>')
rep('        <p class="pf-sub">Every game this week. Select one for its final lines and leans.</p>\n', '')
rep('        <p class="pf-sub">Three steps, in order. The price comes last.</p>\n', '')
_a = s.index('        <aside class="wz-cover" aria-label="Coverage">'); _b = s.index('</aside>', _a) + len('</aside>\n')
s = s[:_a] + s[_b:]
# page titles: no description; Research keeps one line, bigger: what to do
BAND_P = {'research': '<p class="v2-cta">Select any line to open its file</p>', 'nba': '<p class="v2-cta">Select any line to open its file</p>',
          'thesis': '<p hidden><span id="v2-th-when"></span></p>'}
for pid in ['research', 'final', 'thesis', 'charts', 'analysts', 'results', 'nba', 'nba-edge', 'nba-thesis', 'nba-charts', 'nba-analysts', 'nba-results']:
    a0, b0 = page_span(pid); seg = s[a0:b0]
    m = re.search(r'(<header class="wx-band">.*?</h2>)<p>.*?</p>(</header>)', seg, re.S); assert m, pid
    seg = seg[:m.start()] + m.group(1) + BAND_P.get(pid, '') + m.group(2) + seg[m.end():]
    s = s[:a0] + seg + s[b0:]
# speed: when data arrives, redraw only the page on screen (one redraw per frame); other pages draw when opened
jrep("""    drawLines();
    drawNba();
    drawNbaRec();
    catPages.forEach((draw) => draw());
    drawProj();
    drawDefense();
    drawAtd();
    drawResultsSummary();
    drawResults();
    drawRecord();
    drawProfit();
    drawLobby();
    drawAnalysts();
    v2OnData();
    drawBtPerms();
    drawBtLines();
    drawCharts();
  });""", """    v2RedrawSoon();
  });""")
# speed: helmets below the fold load as they come into view
jrep("im.decoding = 'async';", "im.decoding = 'async'; im.loading = 'lazy';")
# ---- round 7: every description, short and to the point
import importlib.util as _ilu
_sp = _ilu.spec_from_file_location('copy_r7', V + 'copy_r7.py'); _cm = _ilu.module_from_spec(_sp); _sp.loader.exec_module(_cm)
s, js = _cm.apply(s, js)
# ---- round 8: graded Sunday results and the matchup lens
_sp8 = _ilu.spec_from_file_location('r8_week', V + 'r8_week.py'); _r8 = _ilu.module_from_spec(_sp8); _sp8.loader.exec_module(_r8)
s, js = _r8.apply(s, js)
# ---- round 9: Week 10 and Wedge % v6
_sp9 = _ilu.spec_from_file_location('r9_week10', V + 'r9_week10.py'); _r9 = _ilu.module_from_spec(_sp9); _sp9.loader.exec_module(_r9)
s, js = _r9.apply(s, js)
# ---- round 10: wedgepicks.com membership (Subscribe, sign-in, members-only pages) and spacing fixes
_sp10 = _ilu.spec_from_file_location('r10_site', V + 'r10_site.py'); _r10 = _ilu.module_from_spec(_sp10); _sp10.loader.exec_module(_r10)
s, js = _r10.apply(s, js)
# ---- round 11: Week 11
_sp11 = _ilu.spec_from_file_location('r11_week11', V + 'r11_week11.py'); _r11 = _ilu.module_from_spec(_sp11); _sp11.loader.exec_module(_r11)
s, js = _r11.apply(s, js)
# ---- round 12: Results shows the card rules backtested on Weeks 1-9 beside the live card
_sp12 = _ilu.spec_from_file_location('r12_backtest', V + 'r12_backtest.py'); _r12 = _ilu.module_from_spec(_sp12); _sp12.loader.exec_module(_r12)
s, js = _r12.apply(s, js)
s = s.replace('@@JS@@', '<script>' + js + '</script>')
s = s.replace('<title>Wedge', '<title>Wedge')
open(V + 'index_full.html', 'w').write(s)
print('v2 page', len(s), 'js', len(js))
