"""Round 10 (wedgepicks.com): Subscribe page, email sign-in, members-only pages, filter-pill and badge spacing.
Applied by build_v2.py after round 9. Pages and code are inert on the dashboard artifact (no window.WEDGE_ACCESS there)."""
V = '/home/claude/wedger/v2/'

SUBSCRIBE = '''
  <div class="rs-page v2-open v2-plans-page" id="subscribe" hidden>
    <header class="wx-band"><span class="wx-label"><i class="wx-dot" aria-hidden="true"></i>Wedge / Membership</span><h2>Pick your edge.</h2></header>
    <div class="v2-plans">
      <article class="v2-plan" data-plan="research" aria-labelledby="plan-r-h">
        <span class="pf-label">Tier 1</span>
        <h3 class="v2-plan-name" id="plan-r-h">Research</h3>
        <div class="v2-plan-price"><b>$19.99</b><span>a month</span></div>
        <p class="v2-plan-sub">Renews monthly. Cancel anytime.</p>
        <ul class="v2-plan-list">
          <li><b>Research</b>: every NFL and NBA line at every price, with our projection beside each</li>
          <li>The <b>research file</b> behind any line: bull, bear and base, the injury report and the game script</li>
          <li><b>Charts &amp; Trends</b>: which spots clear the line, by role, script and scheme</li>
          <li><b>Results</b> and <b>Analysts</b>: every posted line and analyst pick, graded from the box score</li>
        </ul>
        <button type="button" class="wz-btn wz-btn-w wz-btn-lg v2-plan-go">Start Research ↗</button>
        <p class="v2-plan-note"></p>
      </article>
      <article class="v2-plan is-top" data-plan="inner" aria-labelledby="plan-i-h">
        <span class="pf-label">Tier 2</span>
        <h3 class="v2-plan-name" id="plan-i-h">Inner Circle</h3>
        <div class="v2-plan-price"><b>$119.99</b><span>for the season</span></div>
        <p class="v2-plan-sub">One payment. No renewal.</p>
        <ul class="v2-plan-list">
          <li>Everything in <b>Research</b></li>
          <li><b>The Winning Edge</b>: our final lines and conditional leans for every game, every week</li>
          <li>The <b>Thesis</b> behind every game on the card</li>
          <li>Every sport we publish a card for, all season</li>
        </ul>
        <button type="button" class="wz-btn wz-btn-g wz-btn-lg v2-plan-go">Join the Inner Circle ↗</button>
        <p class="v2-plan-note"></p>
      </article>
    </div>
    <div class="v2-plans-foot">
      <p>Already a member? <button type="button" class="wz-link" data-go="signin">Sign in with your email</button></p>
      <p class="v2-fine">Research renews each month until you cancel. Inner Circle is a one-time payment that covers the 2026–27 season, through the Super Bowl. Wedge publishes research and opinions on prediction-market prices for information and entertainment. It isn’t financial or betting advice, and past results don’t guarantee future ones.</p>
    </div>
  </div>

  <div class="rs-page v2-open" id="signin" hidden>
    <header class="wx-band"><span class="wx-label"><i class="wx-dot" aria-hidden="true"></i>Wedge / Account</span><h2 id="v2-si-h">Sign in.</h2></header>
    <section class="v2-si" aria-labelledby="v2-si-h">
      <div class="v2-si-card">
        <form id="v2-si-email" novalidate>
          <label for="v2-si-e">Your email</label>
          <input id="v2-si-e" type="email" autocomplete="email" inputmode="email" placeholder="you@example.com" required>
          <button type="submit" class="wz-btn wz-btn-g wz-btn-lg">Email me a code</button>
        </form>
        <form id="v2-si-code" novalidate hidden>
          <p>Enter the 6-digit code we sent to <b id="v2-si-to"></b>.</p>
          <label for="v2-si-c" class="wg-visually-hidden">Sign-in code</label>
          <input id="v2-si-c" type="text" inputmode="numeric" autocomplete="one-time-code" maxlength="6" pattern="[0-9]{6}" placeholder="000000" required>
          <button type="submit" class="wz-btn wz-btn-g wz-btn-lg">Sign in</button>
          <button type="button" class="wz-link" id="v2-si-back">Use a different email</button>
        </form>
        <div id="v2-si-acct" hidden>
          <dl id="v2-si-dl"></dl>
          <button type="button" class="wz-btn wz-btn-g wz-btn-lg" id="v2-si-up">See Inner Circle ↗</button>
          <a class="wz-btn wz-btn-line wz-btn-lg" id="v2-si-bill" href="#" target="_blank" rel="noopener" hidden>Manage billing ↗</a>
          <button type="button" class="wz-link" id="v2-si-out">Sign out</button>
        </div>
        <p class="v2-si-msg" id="v2-si-msg" role="status" aria-live="polite"></p>
      </div>
      <p class="v2-si-help">No password. We email you a one-time code whenever you sign in on a new device. Not a member yet? <button type="button" class="wz-link" data-go="subscribe">See plans</button></p>
    </section>
  </div>
'''


def apply(s, js):
    def rep(a, b, n=1):
        nonlocal s
        c = s.count(a); assert c == n, f'r10 markup: expected {n} of {a[:80]!r}, found {c}'; s = s.replace(a, b)

    def jrep(a, b, n=1):
        nonlocal js
        c = js.count(a); assert c == n, f'r10 js: expected {n} of {a[:80]!r}, found {c}'; js = js.replace(a, b)

    # Join buttons open the Subscribe page; a Sign in / Account button sits beside Join
    rep('<button type="button" class="wz-btn wz-btn-w wz-btn-sm pf-join" data-wz-join="monthly">Join ↗</button>',
        '<button type="button" class="wz-btn wz-btn-ghost wz-btn-sm" id="v2-acct" hidden>Sign in</button>\n        '
        '<button type="button" class="wz-btn wz-btn-w wz-btn-sm pf-join" data-go="subscribe">Join ↗</button>')
    rep('data-wz-join="monthly">Join Wedge Pro ↗</button>', 'data-go="subscribe">Join Wedge Pro ↗</button>')
    rep('id="wz-gopro" data-wz-join="monthly" hidden>', 'id="wz-gopro" data-go="subscribe" hidden>')
    rep('<p class="pf-fine">$19.99 a month or $119.99 a season · cancel anytime</p>',
        '<p class="pf-fine">Research $19.99 a month · Inner Circle $119.99 for the season</p>')
    # the two new pages
    rep('  <div class="rs-page" id="soccer" hidden>', SUBSCRIBE + '\n  <div class="rs-page" id="soccer" hidden>')
    # styles last, so they win
    i = s.rindex('</style>')
    s = s[:i] + open(V + 'src/site.css').read() + s[i:]

    # navigation: every page change runs the lock check
    jrep("    document.querySelectorAll('.rs-page').forEach((p) => { p.hidden = p.id !== id; });",
         "    document.querySelectorAll('.rs-page').forEach((p) => { p.hidden = p.id !== id; });\n    v2GateHook(id);")
    # Home and the schedule: locked visitors see an Inner Circle tag and go to The Winning Edge's sign-up
    jrep('  function v2Home() {', '  function v2Home() { v2Home0(); if (v2SiteOn) v2HomeLocks(); }\n  function v2Home0() {')
    jrep('  function v2PlayTag(g) {', "  function v2PlayTag(g) { if (v2SiteOn && !v2Can('final')) return 'Inner Circle'; return v2PlayTag0(g); }\n  function v2PlayTag0(g) {")
    jrep('  function v2SelectGame(g, scroll) {',
         "  function v2SelectGame(g, scroll) { if (v2SiteOn && !v2Can('final')) { v2Remember('final'); v2Go('final'); return; } return v2SelectGame0(g, scroll); }\n  function v2SelectGame0(g, scroll) {")
    # The Winning Edge game rows: the final score sits under the game on the left as plain text; the card record stays at the far right
    jrep("    if (c.status === 'Final') { const rc = v2Rec(c); tags.prepend(el('span', 'fc-badge v2-fin', 'Final' + (c.score ? ' · ' + c.score : ''))); if (rc) tags.append(el('span', 'fc-badge fc-lean', 'Card ' + rc)); }",
         "    if (c.status === 'Final') { const rc = v2Rec(c); const sc = el('span', 'v2-sum-score'); sc.append(el('i', null, 'Final'), c.score ? ' · ' + c.score : ''); nm.append(sc); if (rc) tags.append(el('span', 'fc-badge fc-lean v2-card-rec', 'Card ' + rc)); }")
    # the module, then start it (after every page module has loaded, before the data render)
    jrep('  // ---------------- render ----------------', open(V + 'src/site.js').read() + '\n  v2SiteInit();\n\n  // ---------------- render ----------------')
    return s, js
