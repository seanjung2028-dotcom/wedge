
(() => {
  const num = (x) => (x === '' || x == null) ? null : Number(x);
  const fmt = d3.format(',');
  const $ = (s, root) => (root || document).querySelector(s);
  const started = (r) => r.kickoff_utc && Date.parse(r.kickoff_utc) <= Date.now();

  // ---------------- calcs ----------------
  dash.calc('summary', {
    title: 'Screen totals',
    description: 'Counts of 45–55¢ lines, those whose condition hit in more than half of 2026 games, the unflagged subset, and 100% hits over 4+ games.',
    inputs: ['lines'],
    fn: (lines) => {
      const q = lines.filter((r) => r.qualifies === 'Yes');
      return [{
        inband: lines.length,
        qualifying: q.length,
        clean: q.filter((r) => !r.flags).length,
        perfect: q.filter((r) => Number(r.hit_rate) === 100 && Number(r.games) >= 4).length,
      }];
    },
  });

  dash.calc('by_game', {
    title: 'Lines per game',
    description: 'Per game: lines priced 45–55¢ and how many hit more than 50% in 2026.',
    inputs: ['lines'],
    fn: (lines) => {
      const m = new Map();
      for (const r of lines) {
        const g = m.get(r.game) || { game: r.game, kickoff_utc: r.kickoff_utc, inband: 0, qualifying: 0 };
        g.inband += 1; if (r.qualifies === 'Yes') g.qualifying += 1;
        m.set(r.game, g);
      }
      return [...m.values()];
    },
  });

  dash.calc('cat_counts', {
    title: 'Props per category',
    description: 'Per category: player props priced 45–55¢, and how many of them hit more than 50% in 2026.',
    inputs: ['props'],
    fn: (props) => ['1', '2', '3', '4', '-'].map((cat) => {
      const rows = props.filter((r) => r.cat === cat);
      return { cat, all: rows.length, qualifying: rows.filter((r) => r.qualifies === 'Yes').length };
    }),
  });

  dash.calc('atd_summary', {
    title: 'Anytime TD totals',
    description: 'Anytime TD lines with a price, players with 3+ games who scored in more than half of them, and how many of those have an ATD score of 80 or more.',
    inputs: ['atd'],
    fn: (atd) => {
      const q = atd.filter((r) => Number(r.games) >= 3 && Number(r.atd_rate) > 50);
      return [{
        lines: atd.filter((r) => r.yes_price !== '').length,
        qualified: q.length,
        strong: q.filter((r) => Number(r.score) >= 80).length,
      }];
    },
  });


  // ---------------- Week 9 final card ----------------
  let fcDone = false;
  const fcTime = (iso) => { try { return new Date(iso).toLocaleString('en-US', { weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZone: 'America/Chicago' }) + ' CT'; } catch (e) { return iso; } };
  const fcId = (g) => 'fc-' + String(g).replace(/[^A-Za-z]+/g, '-');
  const FC_CLS = { 'Final line': 'final', 'Conditional lean': 'lean', 'Pass': 'pass' };
  function fcBadge(d) { return el('span', 'fc-badge fc-' + (FC_CLS[d] || 'pass'), d); }
  function fcNum(p) { return `${p.est[0]}–${p.est[1]}%`; }
  const fcF1 = (x) => (Math.round(x * 10) / 10).toFixed(1);
  const fcSg = (x) => (x >= 0 ? '+' : '−') + Math.abs(Math.round(x * 10) / 10).toFixed(1);
  function fcDl(pairs) {
    const dl = el('dl', 'fc-dl');
    for (const [k, v] of pairs) { if (!v) continue; const dd = el('dd'); if (v instanceof Node) dd.append(v); else dd.textContent = v; dl.append(el('dt', null, k), dd); }
    return dl;
  }
  function fcLadder(p) {
    const d = el('details', 'fc-lad'); d.open = true;
    d.append(el('summary', null, `Every threshold on this ladder, side by side (${p.ladder.length})`));
    const box = el('div', 'rs-tablebox fc-ladbox');
    const t = el('table', 'rs-table'); const th = el('thead'); const hr = el('tr');
    ['Threshold', 'Price', 'Pays', 'Needs', 'Market', 'Ours', 'Games hit', 'Call'].forEach((h) => hr.append(el('th', null, h))); th.append(hr);
    const tb = el('tbody');
    for (const r of p.ladder) {
      const tr = el('tr', 'fc-lr' + (r.tag ? ' fc-lr-' + r.tag : ''));
      const t0 = el('td', 'fc-lt'); t0.append(el('b', null, r.t), el('span', 'fc-lside', ' ' + r.side));
      if (r.tag) t0.append(el('span', 'fc-ltag', r.tag === 'card' ? 'On the card' : 'Closest alternative'));
      const tc = el('td'); tc.append(fcBadge(r.call));
      tr.append(t0, el('td', 'fc-n', r.ask + '¢'), el('td', 'fc-n', r.pays.toFixed(2) + '×'), el('td', 'fc-n', r.be + '%'), el('td', 'fc-n', fcF1(r.mkt) + '%'),
        el('td', 'fc-n fc-us', `${Math.round(r.lo)}–${Math.round(r.hi)}%`), el('td', 'fc-n', r.hits), tc);
      tb.append(tr);
    }
    t.append(th, tb); box.append(t); d.append(box); return d;
  }
  function fcPlay(c, p, F) {
    const a = el('article', 'fc-play fc-p-' + (FC_CLS[p.decision] || 'pass'));
    const top = el('div', 'fc-play-top');
    top.append(fcBadge(p.decision), el('h4', null, p.line));
    const px = el('div', 'fc-px');
    const cell = (k, v, cls) => { const d = el('div', 'fc-pxc' + (cls ? ' ' + cls : '')); d.append(el('span', null, k), el('b', null, v)); return d; };
    px.append(cell('Price', p.price + '¢'), cell('Pays', p.payout.toFixed(2) + '×'), cell('Needs', p.be + '%'), cell('Our number', fcNum(p), 'fc-us'));
    const ev = el('div', 'fc-ev');
    const evp = (k, v) => { const q = el('p'); q.append(el('b', null, k + ' '), document.createTextNode(v)); return q; };
    ev.append(evp('Strongest supporting source.', p.support), evp('Relevant game sample.', p.sample), evp('Strongest counterevidence.', p.counter));
    const dec = el('div', 'fc-dec');
    const d1 = el('p'); d1.append(el('b', null, p.decision + '. '), document.createTextNode(p.cond)); dec.append(d1);
    if (p.vs) dec.append(el('p', null, p.vs));
    const unit = /receptions/.test(p.thr) ? (Math.abs(p.shift) === 1 ? 'catch' : 'catches') : 'yards';
    a.append(top, px, fcDl([
      ['Line and price', `${p.thr}, ${p.side} at ${p.price}¢ on ${p.platform}. Pays ${p.payout.toFixed(2)}× the stake. Checked ${fcTime(p.checked)}.`],
      ['Why it’s on the card', p.why],
      ['Evidence', ev],
      ['Where it loses', p.loses],
      ['Decision', dec]]),
      fcLadder(p),
      el('p', 'fc-brk', `Market ${fcF1(p.mkt)}% (midpoint of bid and ask) · our shift ${p.shift > 0 ? '+' : '−'}${Math.abs(p.shift)} ${unit} from ${p.pts} evidence points · ours ${fcF1(p.lo)}–${fcF1(p.hi)}% (middle ${fcF1(p.mid)}%) · needs ${p.be}% after Robinhood's 2¢ fees · margin ${fcSg(p.edge_lo)} at the low end, ${fcSg(p.edge_mid)} at the middle`));
    return a;
  }
  function fcGame(c, F) {
    const [aw, hm] = wzSides(c.game);
    const d = el('details', 'fc-game'); d.id = fcId(c.game);
    d.style.setProperty('--ga', wzTeam(aw)[1]); d.style.setProperty('--gh', wzTeam(hm)[1]);
    const sm = el('summary', 'fc-sum');
    const nm = el('div', 'fc-sum-name'); nm.append(el('b', null, c.game), el('span', null, `${c.kick} · ${c.venue}`));
    const tags = el('div', 'fc-sum-tags');
    const nF = c.plays.filter((p) => p.decision === 'Final line').length, nL = c.plays.filter((p) => p.decision === 'Conditional lean').length;
    if (nF) tags.append(el('span', 'fc-badge fc-final', nF + ' final'));
    if (nL) tags.append(el('span', 'fc-badge fc-lean', nL + (nL > 1 ? ' conditional leans' : ' conditional lean')));
    if (!nF && !nL) tags.append(el('span', 'fc-badge fc-pass', 'Pass'));
    sm.append(wzHelmPair(c.game), nm, tags);
    const body = el('div', 'fc-body');
    const sec = (t) => { const s2 = el('section', 'fc-sec'); s2.append(el('h3', null, t)); return s2; };
    const s1 = sec('Market and lineup');
    s1.append(el('p', null, c.market), el('p', null, c.lineup));
    if (c.branches) s1.append(el('p', 'fc-branch', 'Personnel branches: ' + c.branches));
    const s3 = sec('Keys to win, both teams');
    const kg = el('div', 'fc-keys');
    for (const k of c.keys) {
      const kc = el('div', 'fc-key'); kc.style.setProperty('--tc', wzTeam(k.team)[1]);
      kc.append(el('h4', null, k.team + ' must'), fcDl([['Take away', k.take], ['How', k.how], ['What it gives up', k.gives], ['Best counter', k.counter]]));
      kg.append(kc);
    }
    s3.append(kg);
    const s4 = sec('Three scripts');
    s4.append(fcDl([['Control', c.scripts.control], ['Competitive', c.scripts.competitive], ['Reversal', c.scripts.reversal]]));
    const s7 = sec('Tested against comparables, ranked, called');
    if (c.plays.length) c.plays.forEach((p) => s7.append(fcPlay(c, p, F)));
    else s7.append(el('p', 'fc-none', 'Nothing on any ladder in this game clears break-even at the middle of our number, at any price. Pass on this game.'));
    const rk = el('div', 'fc-rank');
    const lst = (t, sub, arr) => { const b = el('div'); b.append(el('h4', null, t), el('p', 'fc-rsub', sub)); const ol = el('ol'); arr.forEach((x) => ol.append(el('li', null, x))); b.append(ol); return b; };
    rk.append(lst('Most likely to hit', 'Highest chance by our number, any threshold, any price', c.likely), lst('Best at the quoted price', 'Clears break-even after fees at the low end of our number', c.value));
    s7.append(rk);
    const sp = sec('Considered and passed');
    const ul = el('ul', 'fc-passed');
    for (const x of c.passed) { const li = el('li'); li.append(el('b', null, x.name), el('span', null, x.why), el('em', null, 'What would change it: ' + x.move)); ul.append(li); }
    sp.append(ul);
    body.append(s1, s3, s4, s7, sp);
    if (c.sources && c.sources.length) {
      const so = sec('Sources, by what they can prove'); const u2 = el('ul', 'fc-src');
      c.sources.forEach((x) => { const li = el('li'); const a = el('a', null, x.t); a.href = x.u; a.target = '_blank'; a.rel = 'noopener noreferrer'; if (x.k) li.append(el('span', 'fc-sk', x.k)); li.append(a); u2.append(li); });
      so.append(u2); body.append(so);
    }
    d.append(sm, body);
    return d;
  }
  function fcRender() {
    if (fcDone) return; const root = $('#fc-root'); if (!root) return;
    const F = window.WZ_FINAL;
    if (!F || !F.cards) { root.replaceChildren(el('p', 'wx-empty', 'The final card failed to load.')); return; }
    fcDone = true;
    const when = $('#fc-when'); if (when) when.textContent = 'Prices checked ' + fcTime(F.at);
    const all = []; F.cards.forEach((c) => c.plays.forEach((p) => all.push([c, p])));
    const nF = all.filter(([, p]) => p.decision === 'Final line').length, nL = all.length - nF;
    const nP = F.cards.reduce((a, c) => a + c.passed.length, 0);
    // summary
    const top = el('section', 'rs-card fc-top');
    const stats = el('div', 'fc-stats');
    const st = (n, t, cls) => { const d = el('div', 'fc-stat' + (cls ? ' ' + cls : '')); d.append(el('b', null, String(n)), el('span', null, t)); return d; };
    stats.append(st(nF, 'final lines', 'g'), st(nL, 'conditional leans'), st(nP, 'considered and passed'), st(F.cards.length, 'games'));
    const lede = el('p', 'fc-lede', "Every Sunday and Monday game, run through the final-lines process. For every player we had a read on, every threshold on the ladder was priced, at any price, from long shots to near-certainties, and ranked two ways: how likely it is to hit, and whether it beats its break-even after fees. A final line clears break-even even at the low end of our number. A conditional lean clears it only at the middle, and comes with the price or personnel condition that would make it final. Everything else is passed, with the reason.");
    const how = el('details', 'fc-how'); how.append(el('summary', null, 'How to read the numbers'));
    how.append(fcDl([
      ['Needs', "Robinhood price plus up to 2¢ in fees per contract (commission up to 1¢, exchange fee up to 1¢), so a 40¢ Yes needs 42% to break even."],
      ['Market', 'The midpoint of the bid and ask on each rung of the Kalshi ladder that Robinhood trades. Only rungs with both a bid and an ask no more than 8¢ apart are used, so every number comes from a live two-sided market. Rungs without a bid are left out at any price.'],
      ['Our number', "The market's own curve across the whole ladder, shifted by what the process found (role, matchup, script, personnel). The evidence is scored in points at the ladder's median and converted into yards or catches at the ladder's slope. The middle applies the full shift, the low end half of it and the high end one and a half times it. There is no backtest adjustment."],
      ['Final line', 'The low end of our number clears Needs by at least half a point. Holds up to the price shown.'],
      ['Conditional lean', "The middle clears Needs by at least half a point, but the low end doesn't. It becomes final at the price shown, or once the stated personnel condition is confirmed."],
      ['Pass', 'Nothing on the ladder clears Needs at our middle, or the evidence is too thin to rank: no net view, 2 evidence points or fewer, or fewer than three rungs with a two-sided quote.'],
      ['Games hit', "How many of the player's 2026 games reached that threshold. With eight games or fewer, it's context for the read, not the estimate."],
      ['Times', `Every rung checked ${fcTime(F.at)}. Sportsbook lines ${fcTime(F.books_at)}. Injury reports through Saturday afternoon. Official inactives post 90 minutes before each kickoff (Monday's at about 5:45 PM CT), and any listed condition should be re-checked then.`]]));
    const tbl = el('div', 'rs-tablebox fc-board');
    const t = el('table', 'rs-table'); const th = el('thead'); const hr = el('tr');
    ['Call', 'Game', 'Line', 'Price', 'Needs', 'Our number', 'Condition'].forEach((h) => hr.append(el('th', null, h))); th.append(hr);
    const tb = el('tbody');
    const fcE = (p) => (p.decision === 'Final line' ? p.edge_lo : p.edge_mid);
    all.sort((x, y) => (x[1].decision !== 'Final line') - (y[1].decision !== 'Final line') || (fcE(y[1]) - fcE(x[1])));
    for (const [c, p] of all) {
      const tr = el('tr', 'fc-row'); tr.tabIndex = 0;
      const tdC = el('td'); tdC.append(fcBadge(p.decision));
      const tdG = el('td'); wzGameCell(tdG, c.game);
      tr.append(tdC, tdG, el('td', 'fc-line', p.line), el('td', 'fc-n', p.price + '¢'), el('td', 'fc-n', p.be + '%'), el('td', 'fc-n fc-us', fcNum(p)), el('td', 'fc-cond', p.cond || ''));
      const go = () => { const g = document.getElementById(fcId(c.game)); if (g) { g.open = true; g.scrollIntoView({ block: 'start', behavior: 'smooth' }); } };
      tr.addEventListener('click', go); tr.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); } });
      tb.append(tr);
    }
    t.append(th, tb); tbl.append(t);
    top.append(stats, lede, how, tbl);
    const games = el('div', 'fc-games');
    F.cards.forEach((c, i) => { const g = fcGame(c, F); if (i === 0) g.open = false; games.append(g); });
    const post = el('p', 'fc-post', 'Postgame grading: every line here, passes included, is logged at the price shown before kickoff. After the games we grade the read and the price separately: did we name the right defensive priority, did the player get the expected opportunities, did late personnel news or a different script explain the miss, and did the price we took beat the closing price.');
    root.replaceChildren(top, games, post);
  }

  // ---------------- navigation ----------------
  const NFL_PAGES = new Set(['final', 'lines', 'proj', 'cat-1', 'cat-2', 'cat-3', 'cat-4', 'defense', 'atd', 'results', 'backtest']);
  const METHOD_PAGES = new Set([...NFL_PAGES, 'charts']); METHOD_PAGES.delete('final');
  const PAGES = [...document.querySelectorAll('.rs-page')].map((p) => p.id);
  const navBtns = [...document.querySelectorAll('.wg-nav [data-page]')];
  const ddBtn = $('#nfl-btn'), ddMenu = $('#nfl-menu'), ddCur = $('.wg-dd-cur', ddBtn);
  const ddItems = [...ddMenu.querySelectorAll('.wg-dd-item')];
  const closeMenu = (focusBtn) => { ddMenu.hidden = true; ddBtn.setAttribute('aria-expanded', 'false'); if (focusBtn) ddBtn.focus(); };
  const openMenu = (focusItem) => {
    ddMenu.hidden = false; ddBtn.setAttribute('aria-expanded', 'true');
    if (focusItem) (ddItems.find((i) => i.getAttribute('aria-current') === 'page') || ddItems[0]).focus();
  };
  ddBtn.addEventListener('click', (e) => { if (ddMenu.hidden) openMenu(e.detail === 0); else closeMenu(false); });
  ddBtn.addEventListener('keydown', (e) => { if (e.key === 'ArrowDown') { e.preventDefault(); openMenu(true); } else if (e.key === 'Escape') closeMenu(false); });
  ddMenu.addEventListener('keydown', (e) => {
    const i = ddItems.indexOf(document.activeElement);
    if (e.key === 'ArrowDown') { e.preventDefault(); ddItems[(i + 1) % ddItems.length].focus(); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); ddItems[(i - 1 + ddItems.length) % ddItems.length].focus(); }
    else if (e.key === 'Home') { e.preventDefault(); ddItems[0].focus(); }
    else if (e.key === 'End') { e.preventDefault(); ddItems[ddItems.length - 1].focus(); }
    else if (e.key === 'Escape') { e.preventDefault(); closeMenu(true); }
    else if (e.key === 'Tab') closeMenu(false);
  });
  document.addEventListener('click', (e) => { if (!ddMenu.hidden && !e.target.closest('#nfl-dd')) closeMenu(false); });
  const showPage = (id) => {
    if (!PAGES.includes(id)) return;
    navBtns.forEach((b) => { if (b.dataset.page === id) b.setAttribute('aria-current', 'page'); else b.removeAttribute('aria-current'); });
    if (NFL_PAGES.has(id)) ddBtn.setAttribute('aria-current', 'page'); else ddBtn.removeAttribute('aria-current');
    const cur = ddItems.find((b) => b.dataset.page === id);
    ddCur.textContent = cur ? cur.textContent : '';
    closeMenu(false);
    document.querySelectorAll('.rs-page').forEach((p) => { p.hidden = p.id !== id; });
    $('#method').hidden = !METHOD_PAGES.has(id);
    dash.setLink(id);
    if (id === 'charts') requestAnimationFrame(() => drawCharts());
    if (id === 'final') requestAnimationFrame(() => fcRender());
    if (id === 'nba') requestAnimationFrame(() => drawNbaRec());
    if (id === 'lobby') { const l = $('#lobby'); l.classList.remove('wg-play'); void l.offsetWidth; l.classList.add('wg-play'); }
  };
  navBtns.forEach((b) => b.addEventListener('click', () => showPage(b.dataset.page)));
  document.querySelectorAll('[data-go]').forEach((b) => b.addEventListener('click', () => {
    showPage(b.dataset.go);
    const after = b.dataset.scrollAfter && document.getElementById(b.dataset.scrollAfter);
    (after || $('#top')).scrollIntoView({ block: 'start', behavior: after ? 'smooth' : 'auto' });
  }));
  document.querySelectorAll('[data-scroll]').forEach((b) => b.addEventListener('click', () => {
    const t = document.getElementById(b.dataset.scroll);
    if (t) { t.scrollIntoView({ block: 'start', behavior: 'smooth' }); const f = t.querySelector('input'); if (f) setTimeout(() => f.focus({ preventScroll: true }), 400); }
  }));
  (() => {
    if (!$('.wg-hero-shine')) return;
    const shine = $('.wg-hero-shine'), mask = 'url("' + $('.wg-hero-letters').src + '"), url("' + $('.wg-hero-tri').src + '")';
    shine.style.webkitMaskImage = mask; shine.style.maskImage = mask;
  })();

  // ---------------- waitlist and analyst application (sent by email) ----------------
  const WEDGER_EMAIL = 'seanjung2028@u.northwestern.edu';
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const wireMailForm = (root, subject, body) => {
    const btn = $('.wg-submit', root), msg = $('.wg-form-msg', root), done = $('.wg-form-done', root), link = $('.wg-mailto', root);
    $('.wg-addr', root).textContent = WEDGER_EMAIL;
    btn.addEventListener('click', () => {
      msg.textContent = '';
      const fields = [...root.querySelectorAll('[data-f]')];
      const groups = [...root.querySelectorAll('[data-group]')];
      [...fields, ...groups].forEach((f) => f.removeAttribute('aria-invalid'));
      const v = {};
      for (const f of fields) v[f.dataset.f] = f.value.trim();
      for (const g of groups) v[g.dataset.group] = [...g.querySelectorAll('input:checked')].map((c) => c.value);
      const missing = fields.find((f) => f.required && !v[f.dataset.f]);
      if (missing) { missing.setAttribute('aria-invalid', 'true'); missing.focus(); msg.textContent = 'Please fill in the required fields.'; return; }
      const em = fields.find((f) => f.dataset.f === 'email');
      if (em && !EMAIL_RE.test(v.email)) { em.setAttribute('aria-invalid', 'true'); em.focus(); msg.textContent = 'Please enter a valid email address.'; return; }
      const emptyGroup = groups.find((g) => !v[g.dataset.group].length);
      if (emptyGroup) { emptyGroup.setAttribute('aria-invalid', 'true'); msg.textContent = 'Please pick at least one sport.'; return; }
      link.href = 'mailto:' + WEDGER_EMAIL + '?subject=' + encodeURIComponent(subject(v)) + '&body=' + encodeURIComponent(body(v));
      done.hidden = false;
      try { link.click(); } catch (e) { /* the link stays for the visitor to use */ }
    });
  };
  wireMailForm($('#waitlist-form'), (v) => `Wedge Pro waitlist: ${v.first} ${v.last}`,
    (v) => `Name: ${v.first} ${v.last}\nEmail: ${v.email}\n\nMessage:\n${v.message || '(none)'}\n\nSent from the Wedge waitlist form.`);
  wireMailForm($('#apply-form'), (v) => `Wedge analyst application: ${v.first} ${v.last}`,
    (v) => `Name: ${v.first} ${v.last}\nEmail: ${v.email}\nSports: ${v.sports.join(', ')}\nExperience: ${v.experience}\nTrack record or socials: ${v.links || '(none)'}\n\nHow I find an edge:\n${v.edge}\n\nAnything else:\n${v.message || '(none)'}\n\nSent from the Wedge analyst application.`);

  const hash = location.hash.slice(1);
  if (PAGES.includes(hash)) showPage(hash);

  // ---------------- shared helpers ----------------
  const pctCell = (tr, value) => {
    const c = document.createElement('td'); c.className = 'rs-barcell';
    const hr = num(value);
    c.textContent = hr == null ? '—' : (hr % 1 ? hr.toFixed(1) : hr) + '%';
    if (hr != null) {
      const bar = document.createElement('div'); bar.className = 'rs-bar';
      const fill = document.createElement('span'); fill.style.width = Math.max(0, Math.min(100, hr)) + '%';
      fill.style.background = hr > 50 ? 'var(--wg-green)' : 'var(--cds-chart-muted)';
      bar.append(fill, document.createElement('i')); c.appendChild(bar);
    }
    tr.appendChild(c);
  };
  const makeSorter = (state, numKeys) => (a, b) => {
    const k = state.sortK; let x = a[k], y = b[k];
    if (numKeys.has(k)) { x = num(x) ?? -1e9; y = num(y) ?? -1e9; }
    else { x = String(x || ''); y = String(y || ''); }
    if (x < y) return -1 * state.sortDir; if (x > y) return 1 * state.sortDir;
    return (num(b.hit_rate ?? b.score) ?? 0) - (num(a.hit_rate ?? a.score) ?? 0) || (num(b.games) ?? 0) - (num(a.games) ?? 0);
  };
  const wireSort = (table, state, numKeys, redraw) => {
    table.querySelectorAll('th button').forEach((b) => b.addEventListener('click', () => {
      const k = b.dataset.k;
      if (state.sortK === k) state.sortDir *= -1; else { state.sortK = k; state.sortDir = numKeys.has(k) && !/rank/.test(k) ? -1 : 1; }
      redraw();
    }));
  };
  const markSort = (table, state) => table.querySelectorAll('th').forEach((th) => {
    const btn = th.querySelector('button'); if (!btn) return;
    const k = btn.dataset.k;
    th.setAttribute('aria-sort', k === state.sortK ? (state.sortDir > 0 ? 'ascending' : 'descending') : 'none');
  });
  const fillGames = (sel, rows, current) => {
    if (!sel.options.length) {
      const games = [...new Map(rows.map((r) => [r.game, r.kickoff_utc])).entries()]
        .sort((a, b) => String(a[1]).localeCompare(String(b[1])) || a[0].localeCompare(b[0])).map((e) => e[0]);
      sel.replaceChildren(new Option('All games', ''), ...games.map((g) => new Option(g, g)));
    }
    sel.value = current;
  };
  const srcCell = (tr, r) => {
    const c = document.createElement('td'); c.className = 'rs-hide-narrow';
    const book = r.source && r.source !== 'Robinhood';
    const s = document.createElement('span'); s.className = 'wg-src' + (book ? ' wg-src-book' : '');
    s.textContent = !book ? 'Robinhood' : (/Robinhood-style/.test(r.source_detail || '') ? 'Books · RH-style' : 'Sportsbook avg');
    if (book) s.title = (r.source_detail || '') + (r.book_lines ? ' · ' + r.book_lines : '');
    c.appendChild(s); tr.appendChild(c); return c;
  };
  const mkTd = (tr) => (text, cls) => { const c = document.createElement('td'); if (cls) c.className = cls; c.textContent = text; tr.appendChild(c); return c; };

  // ---------------- outlook view (shared by NFL and NBA lines) ----------------
  const SIT_COL = { rec: [4], recyd: [5], rushyd: [6], rryd: [5, 6], passyd: [7], passtd: [8], int: [9], td: [10] };
  const SIT_UNIT = { rec: 'rec', recyd: 'rec yds', rushyd: 'rush yds', rryd: 'rush + rec yds', passyd: 'pass yds', passtd: 'pass TDs', int: 'INTs', td: 'TDs' };
  const SIT_WORD = { rec: 'receptions', recyd: 'receiving yards', rushyd: 'rushing yards', rryd: 'rushing + receiving yards', passyd: 'passing yards', passtd: 'passing TDs', int: 'interceptions', td: 'touchdowns' };
  const RH_SHORT = { 'Receiving Yards': 'rec yds', 'Rec Yards': 'rec yds', 'Rush Yards': 'rush yds', 'Pass Yards': 'pass yds', 'Pass TDs': 'pass TDs', 'Receptions': 'receptions', 'Rush+Receiving Yards': 'rush + rec yds', 'Interceptions': 'INTs', 'Points': 'pts', 'Rebounds': 'reb', 'Assists': 'ast', 'Threes': '3PM' };
  const rhLabel = (c) => { const m = /^(.*?): Over (\d+)\.5 (.+)$/.exec(c || ''); return m && RH_SHORT[m[3]] ? `${m[1]}: ${+m[2] + 1}+ ${RH_SHORT[m[3]]}` : c; };
  const reduced = () => window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const pctR = (v) => (v == null ? '—' : Math.round(v) + '%');
  const avg1 = (v) => (v == null ? '—' : (Math.round(v * 10) / 10).toFixed(1));
  const BIG = new Set(['recyd', 'rushyd', 'rryd', 'passyd', 'pts', 'pra']);
  const SMALL = new Set(['td', 'passtd', 'int']);
  const fmtStat = (stat, v) => (v == null ? '—' : (BIG.has(stat) ? String(Math.round(v)) : SMALL.has(stat) ? (Math.round(v * 100) / 100).toFixed(2) : avg1(v)));
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const grow = (node, prop, value) => { if (reduced()) { node.style[prop] = value; return; } requestAnimationFrame(() => requestAnimationFrame(() => { node.style[prop] = value; })); };
  const countUp = (node, to, fmtFn) => {
    if (to == null) { node.textContent = '—'; return; }
    if (reduced()) { node.textContent = fmtFn(to); return; }
    const t0 = performance.now(), dur = 650;
    const step = (t) => { const k = Math.min(1, (t - t0) / dur); node.textContent = fmtFn(to * (1 - Math.pow(1 - k, 3))); if (k < 1 && node.isConnected) requestAnimationFrame(step); };
    node.textContent = fmtFn(0); requestAnimationFrame(step);
  };
  const totalStar = (cell, r) => {
    wzGameCell(cell, r.game);
    const t = num(r.game_total);
    if (t == null || t <= (r.star_at || 49.5)) return;
    const s = el('span', 'wg-star', '★'); s.title = `Projected total ${t} points, above ${r.star_at || 49.5}`;
    s.setAttribute('aria-label', `Projected total ${t} points`); cell.appendChild(s);
  };
  const lazyMap = (id, keyFn) => {
    let src = null, m = new Map();
    return (k) => {
      const d = dash.data(id);
      if (d.status !== 'ok' || k == null) return null;
      if (src !== d.data) { src = d.data; m = new Map(d.data.map((r) => [keyFn(r), r])); }
      const r = m.get(String(k)); if (!r) return null;
      if (!('__p' in r)) { try { r.__p = typeof r.detail === 'string' ? JSON.parse(r.detail) : r.detail; } catch (e) { r.__p = null; } }
      return r.__p;
    };
  };
  const SPORTS = {
    nfl: { sit: lazyMap('sit', (r) => String(r.key)), out: lazyMap('outlook', (r) => r.key), ctx: lazyMap('nflctx', (r) => r.kind + '|' + r.key),
      since: 2023, foot: 'How it works: usage cases are his games since 2023 split into thirds by volume (targets, carries or dropbacks), weighted toward this season. The projection is the case average times this week’s adjustments (defense vs position, coverage, game script from the spread, team total, weather), capped at −30% / +35%. Our read averages the cases and the projection, calibrated on 2025 results; since Week 9 the Wedge chance is the market price shifted by its market’s over bias on 1,333 settled Week 6–8 lines (model v5), and our read is shown, not used; a recent-role factor moves the projection when his snap share over the last 4 games moved 10+ points. Backtest, 3,436 player lines from 2025: Brier 0.238 vs 0.250 for a coin flip. On 706 real Week 6–7 prices (fit on one week, tested on the other): Wedge 0.2474 vs 0.2512 for the price alone, so the market is hard to beat. Treat edges under 5 points as noise.' },
    nba: { sit: lazyMap('nba_sit', (r) => String(r.key)), out: lazyMap('nba_outlook', (r) => r.key), ctx: lazyMap('nba_ctx', (r) => r.kind + '|' + r.key),
      since: 2025, sinceLab: '2025-26', when: 'tonight', cap: '−25% / +30%', like: 'Games like tonight', foot: "How it works: minutes cases are his games since 2025-26 split into thirds by minutes, weighted toward this season and his last 15 games. The projection is the case average times tonight’s adjustments (defense vs his position, pace, game script from the spread, team total, rest, teammates out), capped at −25% / +30%. Our read averages the cases and the projection, shrunk hard toward 50% (fit on 2025-26); Wedge % is 70% the books’ price for this rung + 30% our read. Backtest on 37,519 real 2025-26 prop prices: books’ price Brier 0.2464, Wedge % 0.2465, his last-20 hit rate 0.2667 (0.250 = coin flip). The price already holds nearly everything here, so treat any gap under 5 points as noise." },
  };

  const sitCell = (tr, r, ctx) => {
    const c = document.createElement('td'); c.className = 'rs-barcell wg-sitcell';
    const hr = num(r.sit_hit), price = num(r.yes_price);
    if (hr != null && !r.sit_key) {
      const st = el('div', 'wg-sitstatic'), row1 = el('span', 'wg-sit-row1'); row1.append(el('b', null, pctR(hr)));
      const ed = price == null ? null : Math.round(hr - price); if (ed != null) row1.append(el('span', 'wg-sit-edge flat', (ed > 0 ? '+' : '') + ed));
      const bar = el('div', 'rs-bar'), fill = el('span'); fill.style.width = Math.max(0, Math.min(100, hr)) + '%'; fill.style.background = 'var(--cds-chart-muted)';
      const tick = el('i'); if (price != null) tick.style.left = Math.max(0, Math.min(100, price)) + '%'; bar.append(fill, tick);
      st.append(row1, bar); st.title = 'Market shift only (no outlook outside 45–55¢)'; c.appendChild(st); tr.appendChild(c); return c;
    }
    if (hr == null || !r.sit_key) { c.textContent = '—'; c.classList.add('rs-sub'); tr.appendChild(c); return c; }
    const b = el('button', 'wg-sitbtn'); b.type = 'button';
    b.setAttribute('aria-haspopup', 'dialog');
    const edge = price == null ? null : Math.round(hr - price);
    b.setAttribute('aria-label', `Wedge chance ${pctR(hr)}${edge == null ? '' : `, ${edge >= 0 ? '+' : ''}${edge} points vs price`}. Open the outlook for ${ctx.title}`);
    const row1 = el('span', 'wg-sit-row1');
    row1.append(el('b', null, pctR(hr)));
    if (r.sit_pick) { const pe = Math.round(num(r.sit_pedge)); const ch = el('span', 'wg-sit-edge ' + (r.sit_pick === 'Yes' ? 'up' : 'no'), `${r.sit_pick} +${pe}`); ch.title = r.sit_pick === 'Yes' ? `Wedge % beats the ${price}¢ Yes price by ${pe} pts` : `Yes looks overpriced: buying No (${100 - num(r.yes_bid ?? price)}¢) has a ${pe}-pt edge`; row1.append(ch); }
    else if (edge != null) row1.append(el('span', 'wg-sit-edge flat', (edge > 0 ? '+' : '') + edge));
    const go = el('span', 'wg-sit-go', 'Outlook ›'); go.setAttribute('aria-hidden', 'true'); row1.append(go);
    const bar = el('div', 'rs-bar'); const fill = el('span');
    fill.style.width = Math.max(0, Math.min(100, hr)) + '%';
    fill.style.background = price != null && hr > price ? 'var(--wg-green)' : 'var(--cds-chart-muted)';
    const tick = el('i'); if (price != null) tick.style.left = Math.max(0, Math.min(100, price)) + '%';
    bar.append(fill, tick);
    b.append(row1, bar);
    if (!ctx.key) ctx.key = ctx.market === 'Anytime Touchdown' ? `${ctx.game}|Anytime Touchdown|${r.player || r.contract}` : `${ctx.game}|${ctx.market}|${r.contract}`;
    const open = () => openSit(r, ctx, b);
    b.addEventListener('click', (e) => { e.stopPropagation(); open(); });
    tr.classList.add('wg-click');
    tr.addEventListener('click', (e) => {
      if (e.target.closest('input, button, a, select, label, textarea')) return;
      if (window.getSelection && String(window.getSelection())) return;
      open();
    });
    c.appendChild(b); tr.appendChild(c); return c;
  };

  // ---------------- momentum (last 4 games vs season) ----------------
  const MOM_CLS = { 'Role up': 'up', 'Volume up': 'up2', Stable: '', 'Hot efficiency': 'hot', 'Cold efficiency': 'down2', 'Volume down': 'down2', 'Role down': 'down' };
  const MOM_SHORT = { 'Role up': 'Role ↑', 'Volume up': 'Volume ↑', Stable: 'Stable', 'Hot efficiency': 'Hot eff.', 'Cold efficiency': 'Cold eff.', 'Volume down': 'Volume ↓', 'Role down': 'Role ↓' };
  const MOM_WHY = {
    'Role up': 'His snap share over the last 4 games is 10+ points above his season. Role changes have carried into the next game (34–55% of the gap since 2023) and books have under-priced them: overs vs a book-style line hit 3–7 pts more often.',
    'Role down': 'His snap share over the last 4 games is 10+ points below his season. Role drops have carried over and books have been slow: overs vs a book-style line hit 5–14 pts less often.',
    'Volume up': 'More targets, carries or attempts lately with no big snap change. About a quarter to a third of that carries over, and books already weigh it, so it has added little on its own.',
    'Volume down': 'Fewer targets, carries or attempts lately with no big snap change. Partly carries over; books already weigh it.',
    'Hot efficiency': 'More yards per touch on the same volume. That hasn’t carried over (receiving −4%, passing −16% of the gap), so don’t chase it.',
    'Cold efficiency': 'Fewer yards per touch on the same volume. That tends to bounce back toward his season.',
    Stable: 'His last 4 games look like his season.',
  };
  const momOk = (r, f, base, thr = 3) => !f || (f === 'view' ? (num(r.mom_p) != null && base != null && num(r.mom_p) - base >= thr) : r.mom_type === f);
  const roleOk = (r, f) => !f || (f === 'pocket' ? /pocket/i.test(r.role || '') : String(r.role || '').startsWith(f));
  const roleCell = (tr, r) => {
    const c = document.createElement('td'); c.className = 'rs-hide-narrow';
    if (!r.role) { c.textContent = '—'; c.classList.add('rs-sub'); tr.appendChild(c); return c; }
    c.appendChild(el('span', 'wg-role-chip', r.role)); tr.appendChild(c); return c;
  };
  const momCell = (tr, r) => {
    const c = document.createElement('td'); c.className = 'rs-hide-narrow';
    if (!r.mom_type) { c.textContent = '—'; c.classList.add('rs-sub'); tr.appendChild(c); return c; }
    const ch = el('span', 'wg-mom-chip ' + (MOM_CLS[r.mom_type] || ''), MOM_SHORT[r.mom_type] || r.mom_type);
    ch.title = `${r.mom_type}: last 4 ${r.mom_l4} vs season ${r.mom_s}${r.mom_snap ? ` · snaps ${r.mom_snap}` : ''}${r.mom_vol ? ` · ${r.mom_vol}` : ''}${num(r.mom_p) != null ? ` · last-4 view ${pctR(num(r.mom_p))}` : ''}`;
    c.appendChild(ch); tr.appendChild(c); return c;
  };

  const sitDlg = $('#sit-dlg');
  const sit = { r: null, ctx: null, O: null, det: null, sel: null, tab: 'ov', sp: null };
  let sitOpener = null;
  const closeSit = () => {
    if (!sitDlg.open || sitDlg.classList.contains('closing')) return;
    if (reduced()) { sitDlg.close(); return; }
    sitDlg.classList.add('closing');
    setTimeout(() => { sitDlg.classList.remove('closing'); sitDlg.close(); }, 160);
  };
  sitDlg.querySelector('.wg-sd-close').addEventListener('click', closeSit);
  sitDlg.addEventListener('click', (e) => { if (e.target === sitDlg) closeSit(); });
  sitDlg.addEventListener('cancel', (e) => { e.preventDefault(); closeSit(); });
  sitDlg.addEventListener('close', () => { hideTip($('#sit-log')); if (sitOpener && sitOpener.isConnected) sitOpener.focus(); });
  const TABS = [['ov', 'sit-t-ov', 'sit-p-ov'], ['mu', 'sit-t-mu', 'sit-p-mu'], ['hi', 'sit-t-hi', 'sit-p-hi']];
  const moveInk = () => { const t = $('#' + TABS.find((x) => x[0] === sit.tab)[1]); const ink = $('.wg-sd-ink', sitDlg); ink.style.left = t.offsetLeft + 'px'; ink.style.width = t.offsetWidth + 'px'; };
  const showTab = (k, focus) => {
    sit.tab = k;
    TABS.forEach(([id, tb, pn]) => { const on = id === k; const b = $('#' + tb); b.setAttribute('aria-selected', String(on)); b.tabIndex = on ? 0 : -1; $('#' + pn).hidden = !on; if (on && focus) b.focus(); });
    moveInk();
    const panel = $('#' + TABS.find((x) => x[0] === k)[2]);
    animIn(panel);
    if (k === 'hi') drawSitLog(true);
  };
  const animIn = (panel) => { panel.classList.remove('wg-anim'); [...panel.children].forEach((c, i) => c.style.setProperty('--i', i)); void panel.offsetWidth; panel.classList.add('wg-anim'); setTimeout(() => panel.classList.remove('wg-anim'), 1000); };
  TABS.forEach(([id, tb]) => {
    const b = $('#' + tb);
    b.addEventListener('click', () => showTab(id));
    b.addEventListener('keydown', (e) => {
      const i = TABS.findIndex((x) => x[0] === id);
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); showTab(TABS[(i + (e.key === 'ArrowRight' ? 1 : 2)) % 3][0], true); }
    });
  });

  function openSit(r, ctx, opener) {
    const sp = SPORTS[ctx.sport || 'nfl'];
    const O = sp.out(ctx.key);
    if (!O) { if ((opener.__tries = (opener.__tries || 0) + 1) < 20) setTimeout(() => openSit(r, ctx, opener), 250); return; }
    opener.__tries = 0;
    Object.assign(sit, { r, ctx, O, sp, det: sp.sit(r.sit_key), sel: null, tab: 'ov' });
    sitOpener = opener;
    if (!sitDlg.open) { try { sitDlg.showModal(); } catch (e) { sitDlg.setAttribute('open', ''); } }
    $('.wg-sd-body', sitDlg).scrollTop = 0;
    renderSit();
    showTab('ov');
  }

  const VUNIT_S = { rec: 'targets', recyd: 'targets', rushyd: 'carries', passyd: 'attempts' };
  const statOf = (det, stat) => (det && det.statcols && det.statcols[stat]) || SIT_COL[stat] || [4];
  const sitSum = (det, stat, line, idx) => {
    const cols = statOf(det, stat); let h = 0, s = 0;
    for (const i of idx) { const v = cols.reduce((a, c) => a + (det.log[i][c] || 0), 0); s += v; if (v > line) h += 1; }
    return { h, n: idx.length, avg: idx.length ? s / idx.length : null, p: idx.length ? 100 * h / idx.length : null };
  };
  const sec = (title, hint, ...kids) => {
    const s = el('section', 'wg-sd-sec'); const h = el('div', 'wg-sd-sech'); h.append(el('h3', null, title)); if (hint) h.append(el('span', 'wg-sd-hint', hint));
    s.append(h, ...kids); return s;
  };
  const meter = (pct, price, color) => {
    const m = el('span', 'wg-meter'); if (color) m.style.setProperty('--c', color);
    const f = el('span'); const t = el('i'); if (price != null) t.style.left = price + '%'; else t.hidden = true;
    m.append(f, t); grow(f, 'width', Math.max(0, Math.min(100, pct ?? 0)) + '%'); return m;
  };
  const oddsBar = (parts) => {
    const o = el('div', 'wg-odds'); o.setAttribute('role', 'img');
    o.setAttribute('aria-label', parts.map((p) => `${p.label} ${pctR(100 * p.w)}`).join(', '));
    parts.forEach((p) => { const s = el('span', p.k, p.w >= 0.12 ? `${p.short || p.label} ${pctR(100 * p.w)}` : ''); o.append(s); grow(s, 'flexBasis', (100 * p.w) + '%'); });
    return o;
  };
  const caseCard = (k, tag, vol, p, pLabel, price, kv) => {
    const c = el('div', 'wg-card wg-sc ' + k);
    const top = el('div', 'wg-sc-top'); top.append(el('span', 'wg-sc-tag', tag), el('span', 'wg-sc-vol', vol)); if (vol) top.lastChild.title = vol;
    const pr = el('div', 'wg-sc-p'); const pb = el('b'); pr.append(pb, el('span', null, pLabel));
    const dl = el('dl', 'wg-kv'); kv.forEach(([a, b]) => { const d = el('div'); d.append(el('dt', null, a), el('dd', null, b)); dl.append(d); });
    c.append(top, pr, meter(p, price, 'var(--c)'), dl);
    countUp(pb, p, (x) => Math.round(x) + '%');
    return c;
  };

  function renderSit() {
    const { r, ctx, O, det, sp } = sit;
    const stat = O.stat, line = O.line, price = num(r.yes_price);
    const unit = O.unit || SIT_UNIT[stat] || '', word = O.word || SIT_WORD[stat] || 'value', isTd = stat === 'td';
    const G = sp.ctx('game|' + (O.game || r.game)) || {};
    const MB0 = O.mkey ? sp.ctx('mb|' + O.mkey) : null;
    const MBf = MB0 && !MB0.players && O.mkey ? sp.ctx('mb|' + O.mkey.replace(/\|td-(WR|TE|RB)$/, '|rec-$1').replace(/\|td-QB$/, '|pass')) : null;
    const MB = MB0 && MBf ? Object.assign({}, MB0, { players: MBf.players, shells: MB0.shells || MBf.shells }) : MB0;
    const team = O.team, opp = O.opp;
    const tname = (t) => (G.names && G.names[t]) || t;

    // header
    $('#sit-kicker').textContent = `Outlook · ${team} ${O.pos || ''} vs ${opp}`;
    $('#sit-title').textContent = ctx.title;
    const sub = $('#sit-sub'); sub.replaceChildren();
    const gs = el('span', null, ctx.game); totalStar(gs, r); sub.append(gs);
    if (r.kickoff) sub.append(el('span', null, r.kickoff));
    if (price != null) {
      const book = r.source && r.source !== 'Robinhood';
      sub.append(el('span', null, `${price}¢ ${book ? (/Robinhood-style/.test(r.source_detail || '') ? 'Robinhood-style, from the books' : 'sportsbook average') : `Robinhood ask${num(r.yes_bid) != null ? ` · bid ${r.yes_bid}¢` : ''}`}`));
    }
    if (r.flags) sub.append(el('span', null, r.flags));

    // ---------- Overview ----------
    const ov = $('#sit-p-ov'); ov.replaceChildren();
    const isProj = O.cal === 'proj';
    const P = Math.round(1000 * (isProj && O.P_exp != null ? O.P_exp : O.P)) / 10, edge = price == null ? null : P - price;
    const dir = edge == null ? '' : edge >= 2 ? 'up' : edge <= -2 ? 'down' : '';
    const cond = O.cond ? O.cond : isTd ? '1+ rushing or receiving TD' : rhLabel(`x: Over ${line} ${O.suffix || ({ rec: 'Receptions', recyd: 'Receiving Yards', rushyd: 'Rush Yards', rryd: 'Rush+Receiving Yards', passyd: 'Pass Yards', passtd: 'Pass TDs', int: 'Interceptions' })[stat] || ''}`).replace('x: ', '');
    const hero = el('div', 'wg-hero2');
    const c1 = el('div', 'wg-card');
    c1.append(el('div', 'wg-lab', isProj ? (isTd ? 'Our chance he scores · no price yet' : 'Wedge chance if it posts at 50¢') : 'Wedge chance it settles Yes'));
    const r1 = el('div', 'wg-hrow'); const n1 = el('span', 'wg-big ' + dir); const n1v = el('span'); n1.append(n1v, el('small', 'pct', '%')); r1.append(n1);
    if (edge != null) { const e = Math.round(edge); r1.append(el('span', 'wg-chip ' + dir, `${e > 0 ? '+' : e < 0 ? '−' : '±'}${Math.abs(e)} pts vs ${price}¢ price`)); }
    const gauge = el('div', 'wg-gauge' + (dir === 'down' ? ' down' : '')); const gf = el('span'); gauge.append(gf);
    if (price != null) { const gi = el('i'); gi.style.left = price + '%'; gi.dataset.l = `Price ${price}¢`; gauge.append(gi); }
    if (O.P_mkt != null && O.mkt_src === 'books' && !(r.source && r.source !== 'Robinhood')) { const bk = el('i', 'bk'); bk.style.left = (100 * O.P_mkt) + '%'; bk.dataset.l = `Books ${pctR(100 * O.P_mkt)}`; gauge.append(bk); }
    const mix = el('div', 'wg-mix');
    [[O.cases.by === 'minutes' ? 'Minutes cases (history)' : 'Usage cases (history)', O.P_cases], ['Projection model', O.P_model], [O.mkt_src === 'books' ? "Books' fair price" : (O.mkt_src || 'Market'), O.P_mkt]].forEach(([a, v]) => {
      if (v == null) return; mix.append(el('span', null, a), meter(100 * v, price, 'var(--wg-base)'), el('b', null, pctR(100 * v)));
    });
    const rmPts = (O_, P_) => { if (!O_.rm) return ''; const p = P_ / 100, z = Math.log(p / (1 - p)) - O_.rm, p0 = 1 / (1 + Math.exp(-z)); const d = Math.round(100 * (p - p0) * 10) / 10; return Math.abs(d) < 0.3 ? '' : `${d > 0 ? '+' : '−'}${Math.abs(d).toFixed(1)} pts`; };
    const pickTxt = r.sit_pick ? `Best side: ${r.sit_pick} (+${Math.round(num(r.sit_pedge))} pts vs its price). ` : '';
    const nflNote = isProj
      ? `No price yet. Our read alone${O.rff != null && !isTd ? ` (random-features model, projection ${fmtStat(stat, O.rff)})` : ''}: ${pctR(100 * O.P)}${O.P_l4 != null ? `; last-4 read ${pctR(100 * O.P_l4)}` : ''}. ${isTd ? 'Shown with the TD calibration (Week 6–7 anytime TDs came true a little less often than their price).' : `If the line posts at ${line} for 50¢, Wedge would be about ${pctR(P)}: model v5 shifts the price by how often these overs came true at their price in Weeks 6–8 (passing yards more often, rushing and receiving yards less).`} Yes = ${cond}.`
      : O.cal === 'v5'
        ? `Wedge (model v5) = the price shown${O.P_price != null ? ` (${pctR(100 * O.P_price)})` : ''}, shifted by how often ${({ passyd: 'passing-yard', passtd: 'passing-TD', int: 'interception', rushyd: 'rushing-yard', rryd: 'rushing', recyd: 'receiving-yard', rec: 'reception', td: 'anytime-TD' })[stat] || 'these'} overs came true at their price on 1,333 settled Week 6–8 lines (${O.shift5 >= 0 ? '+' : '−'}${Math.abs(O.shift5 || 0).toFixed(2)} in log-odds: at 50¢ that is ${pctR(100 / (1 + Math.exp(-(O.shift5 || 0))))}). Our matchup read${O.P_v4 != null ? ` (${pctR(100 * O.P_v4)} under last week’s model)` : ''} no longer moves the number: in the backtest it pointed the wrong way.${O.rff != null && !isTd ? ` Random-features projection ${fmtStat(stat, O.rff)}${O.proj_best != null ? `; best estimate ${fmtStat(stat, O.proj_best)}` : ''}.` : ''}${O.P_l4 != null ? ` Last-4 view: ${pctR(100 * O.P_l4)}.` : ''} ${pickTxt}Yes = ${cond}.`
      : O.cal === 'v4'
        ? `Wedge = 85% market + 15% our read${O.P_v1 != null ? ` (${pctR(100 * O.P_v1)} before calibration)` : ''}, calibrated on 706 settled Week 6–7 lines (a Yes priced near 50¢ came true about 45% for receiving and anytime TDs, 40% for rushing, 56% for passing)${rmPts(O, P) ? `, then ${rmPts(O, P)} for how players in his role have done in spots like this (2023–25)` : ''}.${O.P_l4 != null ? ` Last-4 view: ${pctR(100 * O.P_l4)}.` : ''} ${pickTxt}Yes = ${cond}.`
      : O.cal === 'v3'
        ? `Wedge = 85% market + 15% our read${O.P_v1 != null ? ` (${pctR(100 * O.P_v1)} before calibration)` : ''}, re-fit Tue Oct 27 on 706 settled Week 6–7 lines: a Yes priced near 50¢ came true about 45% of the time for receiving and anytime TDs, 40% for rushing and 56% for passing.${O.P_l4 != null ? ` Last-4 view: ${pctR(100 * O.P_l4)}.` : ''} ${pickTxt}Yes = ${cond}.`
        : `Wedge = 70% market + 30% our read${O.P_v1 != null ? ` (${pctR(100 * O.P_v1)})` : ''}, ${O.cal === 'v2.1' ? 'recalibrated Mon Oct 26 on 678 settled Week 6–7 lines: Yes sides came true 45% of the time at ~50¢; rushing and TD overs a bit less, passing overs more' : `recalibrated on 385 settled Week 6–7 lines: Yes sides came true 45% of the time at ~50¢; rushing and TD overs less, passing overs more${O.thin ? `, and players with under 12 games for their team much less (he has ${O.n_hist})` : ''}`}. ${r.sit_pick ? `Best side: ${r.sit_pick} (+${Math.round(num(r.sit_pedge))} pts vs its price). ` : ''}Yes = ${cond}.`;
    c1.append(r1, gauge, mix, el('p', 'wg-note', ctx.sport === 'nba' ? `Wedge = 70% market + 30% our read (cases and projection, calibrated on past results). Yes = ${cond}.` : nflNote));
    countUp(n1v, P, (x) => String(Math.round(x)));
    grow(gf, 'width', Math.max(0, Math.min(100, P)) + '%');
    const c2 = el('div', 'wg-card');
    c2.append(el('div', 'wg-lab', isTd ? 'Projected touchdowns' : `Projected ${word}`));
    const r2 = el('div', 'wg-hrow'); const n2 = el('span', 'wg-big'); const n2v = el('span'); n2.append(n2v, el('small', null, unit)); r2.append(n2);
    if (!isTd) { const d = O.m - line; const big = BIG.has(stat) ? 2 : 0.2; r2.append(el('span', 'wg-chip ' + (d >= big ? 'up' : d <= -big ? 'down' : ''), `Line ${line} · ${Math.abs(d) < 0.05 ? 'even' : (d > 0 ? '+' : '−') + avg1(Math.abs(d))}`)); }
    c2.append(r2);
    countUp(n2v, O.m, (x) => (BIG.has(stat) ? String(Math.round(x)) : (Math.round(x * 100) / 100).toFixed(isTd || stat === 'passtd' || stat === 'int' ? 2 : 1)));
    const C = O.cases, adj = C.T.map((t) => (t.m == null ? null : t.m * O.prod));
    const vals = adj.filter((x) => x != null).concat([line, O.m]);
    const lo = Math.min(...vals), hi = Math.max(...vals), pad = (hi - lo) * 0.12 || 1, x0 = lo - pad, x1 = hi + pad;
    const pos = (v) => (100 * (v - x0) / (x1 - x0)) + '%';
    const rng = el('div', 'wg-rng'); rng.setAttribute('aria-hidden', 'true'); rng.append(el('div', 'wg-rng-track'));
    const ln = el('div', 'wg-rng-line'); ln.style.left = pos(line); rng.append(ln);
    ['bear', 'base', 'bull'].forEach((k, t) => { if (adj[t] == null) return; const d = el('div', 'wg-rng-dot'); d.style.background = `var(--wg-${k})`; d.style.left = pos(line); rng.append(d); grow(d, 'left', pos(adj[t])); });
    const pj = el('div', 'wg-rng-proj'); pj.style.left = pos(line); rng.append(pj); grow(pj, 'left', pos(O.m));
    const lab = el('div', 'wg-rng-lab');
    ['Bear', 'Base', 'Bull'].forEach((k, t) => { const s = el('span', null, k + ' '); s.append(el('b', null, fmtStat(stat, adj[t]))); lab.append(s); });
    const ls = el('span', null, 'Line '); ls.append(el('b', null, String(line))); lab.append(ls);
    c2.append(rng, lab, el('p', 'wg-note', 'Dots: bear, base and bull averages after the adjustments below. Diamond: the projection. Dashed: the line.' + (O.cal === 'v5' && !isTd && O.proj_best != null ? ` Best estimate (v5): ${fmtStat(stat, O.proj_best)}. In Weeks 6–8 the line was closer to the result than this projection, so the best estimate starts at the line and moves toward the random-features projection (${fmtStat(stat, O.rff)}) only as far as tested best.` : '')));
    hero.append(c1, c2);
    ov.append(hero);

    // waterfall
    const wf = el('div', 'wg-wf');
    const steps = [{ label: 'History', why: O.ve && O.m0_cases != null ? `Usage cases since '23 (${fmtStat(stat, O.m0_cases)}) blended 50/50 with recent volume × long-run efficiency (${avg1(O.ve.vol)} ${VUNIT_S[stat] || 'touches'}/g × ${(Math.round(O.ve.eff * 100) / 100).toFixed(stat === 'rec' ? 2 : 1)} = ${fmtStat(stat, O.ve.m)})` : `${C.by === 'minutes' ? 'Minutes' : 'Usage'} cases since ${sp.sinceLab || "'" + String(sp.since).slice(2)}, weighted for ${sp.when || 'this week'}`, v: O.m0, tot: true }];
    let cur = O.m0; let prodF = 1;
    O.F.forEach((f) => { const nv = cur * f.f; prodF *= f.f; steps.push({ label: f.label, why: f.why, from: cur, v: nv, d: nv - cur }); cur = nv; });
    if (Math.abs(prodF - O.prod) > 0.002) { const nv = O.m0 * O.prod; steps.push({ label: 'Cap on total adjustment', why: `Adjustments are capped at ${sp.cap || '−30% / +35%'} combined`, from: cur, v: nv, d: nv - cur }); cur = nv; }
    steps.push({ label: 'Projection', why: `${fmtStat(stat, O.m)} ${unit} vs line ${line}`, v: O.m, tot: true });
    const all = steps.flatMap((s) => [s.v, s.from ?? s.v]).concat([line]);
    const wlo = Math.min(0, ...all), whi = Math.max(...all) * 1.08;
    const wp = (v) => (100 * (v - wlo) / (whi - wlo));
    steps.forEach((s) => {
      const row = el('div', 'wg-wf-row' + (s.tot ? ' tot' : ''));
      const l = el('div', 'wg-wf-l'); l.append(el('b', null, s.label)); if (s.why) l.append(el('small', null, s.why));
      const tr = el('div', 'wg-wf-track');
      const seg = el('span', 'wg-wf-seg ' + (s.tot ? 'tot' : (s.d >= 0 ? 'up' : 'down')));
      const a = s.tot ? wlo : Math.min(s.from, s.v), b = s.tot ? s.v : Math.max(s.from, s.v);
      seg.style.left = wp(s.tot ? wlo : s.from) + '%'; seg.style.width = '0%';
      tr.append(seg); const lmk = el('span', 'wg-wf-line'); lmk.style.left = wp(line) + '%'; tr.append(lmk);
      grow(seg, 'left', wp(a) + '%'); grow(seg, 'width', Math.max(0.6, wp(b) - wp(a)) + '%');
      const v = el('div', 'wg-wf-v ' + (s.tot ? '' : (Math.abs(s.d) < 0.05 ? '' : s.d > 0 ? 'up' : 'down')),
        s.tot ? fmtStat(stat, s.v) : (Math.abs(s.d) < 0.05 ? '±0' : `${s.d > 0 ? '+' : '−'}${BIG.has(stat) ? avg1(Math.abs(s.d)) : (Math.round(Math.abs(s.d) * 100) / 100).toFixed(2)}`));
      row.append(l, tr, v); wf.append(row);
    });
    ov.append(sec('What moves the projection', 'Dashed mark = the line', wf));

    // recent form (last 4 games vs season)
    const MO = O.mom;
    if (MO && MO.mom_type && ctx.sport !== 'nba') {
      const mc = el('div', 'wg-chips');
      const mchip = (b, s2, cls) => { const c = el('div', 'wg-card'); const bb = el('b', null, b); if (cls != null) { bb.className = 'wg-mom-chip ' + cls; } c.append(bb, el('small', null, s2)); mc.append(c); };
      mchip(MO.mom_type, MOM_WHY[MO.mom_type] || '', MOM_CLS[MO.mom_type] || '');
      mchip(`${fmtStat(stat, MO.mom_l4)} vs ${fmtStat(stat, MO.mom_s)} ${unit}`, 'Last 4 games vs his 2026 season');
      if (MO.mom_snap) mchip(MO.mom_snap, 'Snap share: season → last 4');
      if (MO.mom_vol) mchip(MO.mom_vol, 'Volume: season → last 4');
      if (O.P_l4 != null) mchip(pctR(100 * O.P_l4), `Last-4 view${O.m_l4 != null ? ` · projects ${fmtStat(stat, O.m_l4)} ${unit}` : ''}. It tested worse than the standard read on real Week 6–7 prices, so it isn’t in Wedge %.`);
      ov.append(sec('Recent form', 'Last 4 games vs the season', mc));
    }
    // his role + how players like him have done in spots like this
    const RO = O.role;
    if (RO && RO.arch && RO.arch !== 'Unknown' && ctx.sport !== 'nba') {
      const m = RO.m || {}, g = el('div', 'wg-roleg');
      const cell = (v, lab, f) => { if (v == null) return; const d = el('div'); d.append(el('b', null, f(v)), el('small', null, lab)); g.append(d); };
      const P1 = (v) => Math.round(100 * v) + '%', D1 = (v) => (Math.round(v * 10) / 10).toFixed(1);
      if (O.pos === 'RB' || O.pos === 'FB') {
        cell(m.p_cshare, 'of team carries', P1); cell(m.p_cpg, 'carries / game', D1); cell(m.p_tshare, 'target share', P1); cell(m.p_tpg, 'targets / game', D1);
        cell(m.p_i10sh, 'of team carries inside the 10', P1); cell(m.p_outside, 'runs outside', P1); cell(m.p_ybc, 'yds before contact / carry', D1); cell(m.p_yacr, 'yds after contact / carry', D1); cell(m.p_ryoe, 'rush yds over expected / carry', D1);
      } else if (O.pos === 'QB') {
        cell(m.p_qadot, 'air yds / attempt', D1); cell(m.p_pa, 'play-action dropbacks', P1); cell(m.p_scr, 'scrambles / game', D1);
      } else {
        cell(m.p_tshare, 'target share', P1); cell(m.p_tpg, 'targets / game', D1); cell(m.p_adot, 'air yds / target (aDOT)', D1); cell(m.p_deep, 'targets 20+ yds downfield', P1);
        cell(m.p_mid, 'targets over the middle', P1); cell(m.p_screen, 'screens', P1); cell(m.p_yacsh, 'of yards after the catch', P1); cell(m.p_ypt, 'yds / target', D1);
      }
      cell(m.p_snap, 'snap share', (v) => Math.round(v) + '%');
      const kids = [el('p', 'wg-note', `${RO.arch}${RO.tier && !RO.arch.includes(RO.tier) ? ' · ' + RO.tier : ''}. From his ${m.games || ''} ${m.src === 'prev' ? 'most recent games (incl. last season)' : 'games with this team this season'}.`), g];
      const rows = (RO.rows || []);
      if (rows.length) {
        const t = el('table', 'wg-dh'); const th = el('tr');
        ['Spot like this (' + (SIT_WORD[stat] || stat) + ')', '2026', 'Wks 4–7', '2023–25'].forEach((h, i) => { const x = el('th', null, h); if (i) x.style.textAlign = 'right'; th.append(x); });
        const tb = el('tbody');
        rows.forEach(([lab, n, o, n47, o47, nh, oh, bs, bh]) => {
          const tr = el('tr'); tr.append(el('td', null, lab));
          const cl = (v, b) => (v == null ? '' : v >= b + 3 ? 'n up' : v <= b - 3 ? 'n down' : 'n');
          tr.append(el('td', cl(o, bs), `${pct1(o)} · ${n}`), el('td', cl(o47, bs), o47 == null ? '—' : `${pct1(o47)} · ${n47}`), el('td', cl(oh, bh), oh == null ? '—' : `${pct1(oh)} · ${nh}`));
          tb.append(tr);
        });
        const hd = el('thead'); hd.append(th); t.append(hd, tb);
        const bx = el('div', 'wg-dhbox'); bx.append(t); kids.push(bx);
        const bs = rows[0] ? rows[0][7] : null, bh = rows[0] ? rows[0][8] : null;
        kids.push(el('p', 'wg-note', `How often the over cleared the line books would set for players in these spots. All ${SIT_WORD[stat] || ''} props: ${bs != null ? pct1(bs) : '—'} in 2026, ${bh != null ? pct1(bh) : '—'} in 2023–25 (green = 3+ pts better, red = 3+ worse).${rmPts(O, P) ? ` Together these move Wedge % by ${rmPts(O, P)}.` : ''}`));
      }
      ov.append(sec('His role', 'How he is used, and how players like him do in spots like this', ...kids));
    }

    // cases
    const scen = el('div', 'wg-sd-scen');
    ['bear', 'base', 'bull'].forEach((k, t) => {
      const T = C.T[t];
      scen.append(caseCard(k, k + ' case', C.labels[t], 100 * T.p, isTd ? 'chance to score' : 'chance to clear', price,
        [[sp.when === 'tonight' ? 'Odds tonight' : 'Odds this week', pctR(100 * C.W[t])], ['Average', T.m == null ? '—' : `${fmtStat(stat, adj[t])} ${unit}`], ['Record', `${T.h} of ${T.n}`]]));
    });
    ov.append(sec(C.by === 'minutes' ? 'Minutes cases' : 'Usage cases', `His games split into thirds by ${C.by || C.labels[1].replace(/^[\d–\s]+/, '')}`,
      oddsBar([{ k: 'bear', label: 'Bear', w: C.W[0] }, { k: 'base', label: 'Base', w: C.W[1] }, { k: 'bull', label: 'Bull', w: C.W[2] }]), scen));

    // ---------- Matchup & script ----------
    const mu = $('#sit-p-mu'); mu.replaceChildren();
    const chips = el('div', 'wg-chips');
    const chip = (b, s) => { const c = el('div', 'wg-card'); c.append(el('b', null, b), el('small', null, s)); chips.append(c); };
    if (G.spread_home != null) {
      const sh = G.spread_home; const fav = sh < 0 ? G.home : G.away; const sAbs = Math.abs(sh);
      chip(sAbs < 0.5 ? 'Pick’em' : `${tname(fav)} −${avg1(sAbs).replace('.0', '')}`, G.implied ? `Total ${G.total} · implied ${tname(G.away)} ${G.implied[G.away]}, ${tname(G.home)} ${G.implied[G.home]}` : 'Spread from Robinhood prices');
    }
    if (G.stadium || G.venue) chip(G.stadium || G.venue, [G.roof, G.surface].filter(Boolean).join(' · ') || `${tname(G.home)} home court`);
    if (G.weather) chip(`${G.weather.temp}°F · wind ${Math.round(G.weather.wind)} mph`, `Gusts ${G.weather.gust} mph · ${G.weather.precip_prob}% rain chance`);
    else if (G.roof) chip(G.roof === 'dome' || G.roof === 'closed' ? 'Indoors' : 'Retractable roof', 'Weather not a factor');
    if (G.coach) chip(`${(G.coach[G.away] || '').split(' ').slice(-1)[0]} vs ${(G.coach[G.home] || '').split(' ').slice(-1)[0]}`, 'Head coaches');
    if (G.rest) chip(`${G.rest[team]} vs ${G.rest[opp]} days`, `Rest: ${team} vs ${opp}`);
    if (G.extra) G.extra.forEach(([b, s]) => chip(b, s));
    mu.append(sec('Game', null, chips));
    if (ctx.sport !== 'nba') {
      const dh = dash.data('defhist');
      const grp = O.pos === 'FB' ? 'RB' : O.pos;
      if (dh.status === 'ok') {
        const rows = dh.data.filter((x) => x.def === opp && x.pos === grp).sort((a, b) => num(b.week) - num(a.week) || num(b.resid_main) - num(a.resid_main));
        if (rows.length) {
          const myArch = O.role && O.role.arch;
          const t = el('table', 'wg-dh wide'); const hr = el('tr');
          ['Wk', 'Player', 'Result vs his usual', 'How', 'Why'].forEach((h) => hr.append(el('th', null, h)));
          const tb = el('tbody');
          const U = { rushyd: 'rush yds', recyd: 'rec yds', passyd: 'pass yds' };
          if (grp === 'RB' && (stat === 'recyd' || stat === 'rec')) rows.sort((a, b) => num(b.week) - num(a.week) || num(b.recyd) - num(a.recyd));
          rows.slice(0, 24).forEach((x) => {
            const tr = el('tr', x.arch && x.arch === myArch ? 'same' : '');
            tr.append(el('td', 'n', x.week));
            const pc = el('td'); pc.append(el('div', null, `${x.player} (${x.team})`)); if (x.arch && x.arch !== 'Unknown') pc.append(el('span', 'wg-role-chip' + (x.arch === myArch ? ' same' : ''), x.arch)); tr.append(pc);
            const mk = (grp === 'RB' && (stat === 'recyd' || stat === 'rec')) ? 'recyd' : x.main;
            const v = num(x[mk]), b = num(x['base_' + mk]), dv = b == null ? null : v - b;
            tr.append(el('td', 'n ' + (dv == null ? '' : dv >= 10 ? 'up' : dv <= -10 ? 'down' : ''), `${v} ${U[mk]}` + (dv == null ? '' : ` (${dv > 0 ? '+' : ''}${Math.round(dv)})`)));
            const how = x.pos === 'RB' ? `${x.car} car${x.ybc_pc !== '' ? ` · ${x.ybc_pc} before / ${x.yac_pc} after contact` : ''}${x.long_rush !== '' ? ` · long ${x.long_rush}` : ''}${x.tgt > 0 ? ` · ${x.rec}/${x.tgt} for ${x.recyd}` : ''}`
              : x.pos === 'QB' ? `${x.att} att · ${x.passyd} yds` : `${x.rec}/${x.tgt} · aDOT ${x.adot} · YAC ${x.yac}${x.long_rec !== '' ? ` · long ${x.long_rec}` : ''}`;
            tr.append(el('td', 'why', how));
            const whyTxt = (grp === 'RB' && (stat === 'recyd' || stat === 'rec')) ? (x.why_rec || (x.tgt > 0 ? `${x.tgt} targets` : 'no targets')) : [x.why, x.why_rec].filter(Boolean).join('; ');
            tr.append(el('td', 'why', whyTxt + (x.score ? ` · ${x.team} ${Number(x.margin) >= 0 ? 'won' : 'lost'} ${x.score}` : '')));
            tb.append(tr);
          });
          const hd = el('thead'); hd.append(hr); t.append(hd, tb);
          const bx = el('div', 'wg-dhbox'); bx.append(t);
          const df = (O.F || []).find((f) => f.k === 'def');
          const note = el('p', 'wg-note', `Every ${grp} who faced ${tname(opp)} in 2026, against his own usual (the line books would have set for him). Green bar = same role as ${O.team ? 'this player' : 'him'}. ` +
            (grp === 'RB' ? 'Extra carries a defense allows and yards before contact (its front and the blocking it faces) have carried into the next game; yards after contact and one long run belong to the runner and mostly have not. ' : grp === 'QB' ? 'Pass defense is mostly a team-level effect; it carries over a little. ' : 'For receivers, what one player did against a defense has told us almost nothing about the next one (2023–26), so this weighs very little. ') +
            (df ? `In the projection: ${df.why}.` : ''));
          mu.append(sec(`Against this defense: ${grp}s vs ${opp}`, 'Who did it, and why', note, bx));
        }
      }
    }
    if (O.S && O.S.length) {
      const scen2 = el('div', 'wg-sd-scen');
      O.S.forEach((s) => scen2.append(caseCard(s.k, s.label, `${s.n} game${s.n === 1 ? '' : 's'}`, 100 * s.hit, isTd ? 'chance to score' : 'chance to clear', price,
        [['Odds', pctR(100 * s.prob)], ['His average', `${fmtStat(stat, s.avg)} ${unit}`], ['Games', String(s.n)]])));
      mu.append(sec('Game script', 'Odds from the spread; his results in each script since ' + sp.since,
        oddsBar(O.S.map((s) => ({ k: s.k, label: s.label, short: s.short || ({ lead8: 'Win 8+', close: 'Close', trail8: 'Lose 8+' })[s.k] || s.label, w: s.prob }))), scen2));
    }
    if (MB) {
      const two = el('div', 'wg-two');
      const dc = el('div', 'wg-card'); dc.append(el('div', 'wg-lab', `${MB.title}${MB.coach ? ' · HC ' + MB.coach : ''}`));
      const met = el('div', 'wg-met'); met.style.marginTop = '10px';
      (MB.metrics || []).forEach((m) => {
        const l = el('div', 'lbl', m.label); if (m.lg) l.append(el('small', null, `League ${m.lg}`));
        const rk = el('span', 'rk wg-chip ' + (m.tone || ''), m.rk ? `#${m.rk} of ${m.n}` : '—');
        rk.title = m.tone === 'good' ? `Favors ${team}` : m.tone === 'bad' ? `Tough for ${team}` : 'Neutral';
        met.append(l, el('div', 'val', m.v), rk);
      });
      dc.append(met, el('p', 'wg-note', MB.note || `Rank 1 = most allowed (or most pressure). Green favors ${team}, red is tough for ${team}.`));
      if (MB.shells) {
        const sh = el('div'); sh.style.marginTop = '12px'; sh.append(el('div', 'wg-lab', MB.shells.title));
        const mx = el('div', 'wg-mix'); MB.shells.rows.forEach(([a, v]) => mx.append(el('span', null, a), meter(v, null, 'var(--wg-base)'), el('b', null, Math.round(v) + '%')));
        sh.append(mx); dc.append(sh);
      }
      two.append(dc);
      const tbl = (P0) => {
        const box = el('div', 'wg-card'); box.append(el('div', 'wg-lab', P0.title));
        const t = el('table', 'wg-tbl'); t.style.marginTop = '8px'; const hd = t.createTHead().insertRow();
        const isNum = P0.cols.map((c, j) => P0.rows.some((rw) => typeof rw[j] === 'number'));
        P0.cols.forEach((c, j) => hd.append(el('th', isNum[j] ? 'num' : null, c)));
        const tb = t.createTBody();
        const mx = Math.max(1, ...P0.rows.map((rw) => +rw[P0.bar] || 0), P0.lg || 0);
        P0.rows.forEach((rw) => {
          const tr = tb.insertRow();
          rw.forEach((v, j) => {
            const td = tr.insertCell();
            if (j === P0.cols.length - 1 && P0.cols[j] === 'Status') { if (v) { const s = el('span', 'wg-st' + (/Limited|Questionable/.test(v) ? ' lim' : ''), v); td.append(s); } return; }
            td.textContent = v; if (isNum[j]) td.className = 'num';
            if (P0.bar != null && j === P0.bar) {
              td.className = 'num barc'; const b = el('div', 'wg-tbar'); const f = el('span');
              f.style.background = P0.lg ? (+v > P0.lg ? 'var(--wg-green)' : 'var(--cds-chart-muted)') : 'var(--wg-base)';
              b.append(f); if (P0.lg) { const i = el('i'); i.style.left = (100 * P0.lg / mx) + '%'; b.append(i); }
              td.append(b); grow(f, 'width', (100 * (+v || 0) / mx) + '%');
            }
          });
        });
        box.append(t);
        if (P0.note) box.append(el('p', 'wg-note', P0.note)); else if (P0.lg) box.append(el('p', 'wg-note', `Tick = league average (${P0.lg}). Green = allows more than average.`));
        return box;
      };
      const right = el('div'); right.style.display = 'grid'; right.style.gap = '12px';
      if (MB.players && MB.players.rows && MB.players.rows.length) right.append(tbl(MB.players));
      if (MB.players && MB.players.extra) right.append(tbl(MB.players.extra));
      if (right.childElementCount) two.append(right);
      mu.append(sec('Defensive matchup', `${MB.games ? MB.games + ' games' : ''}`, two));
    }

    // ---------- History ----------
    const L = det ? det.log : [];
    const sincey = !L.length ? '' : det.snames ? det.snames[L[0][0]] : "'" + String(L[0][0]).padStart(2, '0');
    const likeLab = sp.like || 'Games like this week';
    $('#sit-sp-h').textContent = likeLab;
    const pool = det ? det.sets.filter((s) => s.pool) : [];
    const pooledUnique = det ? [...new Set(pool.flatMap((s) => s.idx))].sort((x, y) => x - y) : [];
    sit.sel = { id: 'pool', idx: pooledUnique, label: likeLab };
    const spl = $('#sit-splits'); spl.replaceChildren();
    const row = (label, small, idx, id, opts = {}) => {
      const S = sitSum(det, stat, line, idx);
      const b = el('button', 'wg-sp-row' + (opts.alt ? ' alt' : '')); b.type = 'button'; b.dataset.id = id;
      b.setAttribute('aria-pressed', String(sit.sel.id === id)); if (!S.n) b.disabled = true;
      const l = el('span', 'wg-sp-l'); const lb = el('b', null, label); if (opts.pill) lb.append(el('span', 'wg-pill', 'In model')); l.append(lb);
      if (small) l.append(el('small', null, small));
      const v = el('span', 'wg-sp-v');
      if (S.n) {
        v.append(el('b', null, pctR(S.p)));
        const sm = el('small', null, `${S.h} of ${S.n} · avg ${fmtStat(stat, S.avg)}`);
        if (opts.vs) { const d = opts.vs.avg - S.avg; sm.append(el('span', 'wg-sp-diff ' + (d >= 0 ? 'up' : 'down'), `${sp.when === 'tonight' ? 'Like tonight' : 'Like this week'}: ${d >= 0 ? '+' : '−'}${fmtStat(stat, Math.abs(d))} per game`)); }
        v.append(sm);
      } else v.append(el('small', null, 'no games'));
      b.append(l, meter(S.p, price, S.p != null && price != null && S.p > price ? 'var(--wg-green)' : 'var(--cds-chart-muted)'), v);
      b.addEventListener('click', () => selectSit({ id, idx: [...new Set(idx)], label: opts.selLabel || label }));
      return { b, S };
    };
    const wrap = (...nodes) => { const w = el('div', 'wg-sp'); w.append(...nodes); spl.append(w); };
    if (det) {
      wrap(row(likeLab, `Every game in a split marked In model (${pool.length})`, pooledUnique, 'pool').b);
      wrap(row(`Every game since ${sincey}`, det.kind === 'nba' ? 'Every game he played, any team' : `With ${det.team}; games he left early or sat out are left out`, det.base, 'all').b);
      for (const s of det.sets) {
        const main = row(s.label, s.now + ((s.skipped || []).length ? ` · ${s.skipped.length} left out` : ''), s.idx, s.k, { pill: s.pool });
        const nodes = [main.b];
        if (s.alt) nodes.push(row(`vs ${s.alt.label.charAt(0).toLowerCase() + s.alt.label.slice(1)}`, null, s.alt.idx, s.k + '-alt', { alt: true, vs: main.S.n ? main.S : null, selLabel: s.alt.label }).b);
        wrap(...nodes);
      }
    }
    const more = $('#sit-moreb'); more.replaceChildren();
    const comp = det && det.sets.find((s) => s.k === 'comp' && s.who && s.who.length);
    if (comp) {
      const box = el('div'); box.append(el('h4', null, 'No. 1 competitor by season'));
      const t = el('table', 'wg-tbl'); const hd = t.createTHead().insertRow();
      ['Season', 'Player', 'Per game', 'Share'].forEach((x, j) => hd.append(el('th', j > 1 ? 'num' : null, x)));
      const tb = t.createTBody(); comp.who.forEach((w) => { const tr = tb.insertRow(); [String(w.season), w.name, String(w.vol), w.share + '%'].forEach((x, j) => { const td = tr.insertCell(); td.textContent = x; if (j > 1) td.className = 'num'; }); });
      box.append(t); more.append(box);
    }
    if (det && det.mates && det.mates.length) {
      const box = el('div'); box.append(el('h4', null, 'With and without teammates'));
      const list = el('div', 'wg-sd-splits');
      for (const m of det.mates) {
        const last = m.name.split(' ').slice(-1)[0]; const w = el('div', 'wg-sp');
        w.append(row(`With ${m.name}`, m.now === 'out' ? 'Out this week' : 'Active this week', m.with, 'm-w-' + m.name).b);
        if ((m.missed || []).length) w.append(row(`${last} missed`, null, m.missed, 'm-x-' + m.name, { alt: true, selLabel: `Games ${m.name} missed` }).b);
        if ((m.off || []).length) w.append(row(`${last} not on the team`, null, m.off, 'm-o-' + m.name, { alt: true }).b);
        list.append(w);
      }
      box.append(list); more.append(box);
    }
    $('#sit-more').hidden = !more.childElementCount; $('#sit-more').open = false;
    $('#sit-foot').textContent = sp.foot || '';
  }

  function selectSit(sel) {
    sit.sel = sel;
    sitDlg.querySelectorAll('.wg-sp-row').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.id === sel.id)));
    drawSitLog(false);
  }

  function drawSitLog(animate) {
    const box = $('#sit-log');
    const { det, O } = sit; if (!det || !O || $('#sit-p-hi').hidden) return;
    const stat = O.stat, line = O.line, L = det.log, unit = O.unit || SIT_UNIT[stat] || '', isTd = stat === 'td';
    const cols = statOf(det, stat);
    const val = (i) => cols.reduce((s, c) => s + (L[i][c] || 0), 0);
    const selSet = new Set(sit.sel.idx);
    const S = sitSum(det, stat, line, [...selSet]);
    $('#sit-lognote').textContent = `Green = ${isTd ? 'scored' : `over ${line}`}. Lit: ${sit.sel.label} — ${S.n ? `${S.h} of ${S.n} (${pctR(S.p)}), avg ${fmtStat(stat, S.avg)}` : 'no games'}`;
    const W = Math.max(300, Math.round(box.clientWidth || 640)), H = 220;
    const m = { l: 34, r: 50, t: 14, b: 38 };
    const svg = freshSvg(box, W, H);
    svg.attr('aria-label', `${det.p}: ${unit} in each game, against the line of ${line}. ${sit.sel.label}: ${S.h} of ${S.n} over.`);
    const n = L.length;
    const x = d3.scaleBand().domain(d3.range(n)).range([m.l, W - m.r]).paddingInner(n > 36 ? 0.16 : 0.26).paddingOuter(0.15);
    const vals = L.map((_, i) => val(i));
    const y = d3.scaleLinear().domain([Math.min(0, d3.min(vals)), Math.max(d3.max(vals) || 1, line) * 1.1]).nice().range([H - m.b, m.t]);
    const g0 = svg.append('g');
    for (const t of y.ticks(4)) {
      g0.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(t)).attr('y2', y(t)).style('stroke', 'var(--cds-chart-grid)');
      g0.append('text').attr('x', m.l - 6).attr('y', y(t)).attr('dy', '0.32em').attr('text-anchor', 'end').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(t);
    }
    const step = x.step();
    d3.groups(d3.range(n), (i) => L[i][0]).forEach(([yy, ids], k) => {
      const x0 = x(ids[0]), x1 = x(ids[ids.length - 1]) + x.bandwidth();
      if (k > 0) g0.append('line').attr('x1', x0 - (step - x.bandwidth()) / 2).attr('x2', x0 - (step - x.bandwidth()) / 2).attr('y1', m.t - 6).attr('y2', H - m.b + 26).style('stroke', 'var(--color-border-line)');
      g0.append('text').attr('x', (x0 + x1) / 2).attr('y', H - 6).attr('text-anchor', 'middle').style('font-size', '10px').style('font-weight', 600).style('fill', 'var(--color-fg-muted)').text(det.snames ? det.snames[yy] : (x1 - x0 > 26 ? '20' + String(yy).padStart(2, '0') : "'" + String(yy).padStart(2, '0')));
    });
    if (x.bandwidth() >= 11 && !det.noWeeks) L.forEach((r, i) => g0.append('text').attr('x', x(i) + x.bandwidth() / 2).attr('y', H - m.b + 13).attr('text-anchor', 'middle').style('font-size', '9px').style('fill', 'var(--color-fg-muted)').text(r[1]));
    const gb = svg.append('g');
    const anim = animate && !reduced();
    L.forEach((r, i) => {
      const v = vals[i], on = selSet.has(i), ex = !!r[12];
      const h = Math.max(1.5, Math.abs(y(v) - y(0))), yTop = v >= 0 ? y(0) - h : y(0);
      const rect = gb.append('rect').attr('class', 'bar').attr('x', x(i)).attr('width', x.bandwidth()).attr('rx', Math.min(2, x.bandwidth() / 4)).attr('y', anim ? y(0) : yTop).attr('height', anim ? 0 : h);
      if (ex) rect.style('fill', 'none').style('stroke', 'var(--color-fg-muted)').style('stroke-dasharray', '2 2').style('opacity', 0.8);
      else rect.style('fill', v > line ? 'var(--wg-green)' : 'var(--cds-chart-muted)').style('opacity', on ? 1 : 0.16);
      if (anim) rect.transition().delay(Math.min(450, i * 8)).duration(480).ease(d3.easeCubicOut).attr('y', yTop).attr('height', h);
    });
    const gl = svg.append('g');
    gl.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(line)).attr('y2', y(line)).style('stroke', 'var(--color-fg)').style('stroke-width', 1.25).style('stroke-dasharray', '5 4').style('opacity', 0.75);
    gl.append('text').attr('x', W - m.r + 6).attr('y', y(line)).attr('dy', '0.32em').style('font-size', '10px').style('font-weight', 600).style('fill', 'var(--color-fg)').text(isTd ? '1+ TD' : `Line ${line}`);
    const gh = svg.append('g');
    const tips = det.tipcols || [['targets', 13], ['carries', 14], ['att', 15]];
    L.forEach((r, i) => {
      gh.append('rect').attr('x', x(i) - (step - x.bandwidth()) / 2).attr('y', m.t - 6).attr('width', step).attr('height', H - m.b - m.t + 8).style('fill', 'transparent')
        .on('mousemove', (ev) => showTip(box, ev, [
          det.kind === 'nba' ? `${r[13]} ${r[2][0] === '@' ? '@ ' + r[2].slice(1) : 'vs ' + r[2]} · ${r[9] > 0 ? 'won' : 'lost'} by ${Math.abs(r[9])}${r[14] ? '' : ' · bench'}` : `'${String(r[0]).padStart(2, '0')} Week ${r[1]} vs ${r[2]}`,
          `${vals[i]} ${unit}${r[12] ? '' : (vals[i] > line ? (isTd ? ' · scored' : ' · over') : '')}`,
          tips.filter(([, c]) => r[c]).map(([lb, c]) => `${r[c]} ${lb}`).join(' · ') + (r[3] != null && !det.noSnaps ? ` · ${r[3]}% of snaps` : ''),
          ...(r[11] != null && det.names ? [`QB ${det.names[r[11]]}`] : []),
          ...(r[12] ? [r[12] === 'r' ? 'Rested (left out)' : 'Left early hurt (left out)'] : []),
        ]))
        .on('mouseleave', () => hideTip(box));
    });
  }
  let sitResize = 0;
  window.addEventListener('resize', () => { if (!sitDlg.open || !sit.O) return; cancelAnimationFrame(sitResize); sitResize = requestAnimationFrame(() => { moveInk(); drawSitLog(false); }); });

  // ---------------- Wedge certification ----------------
  // Shared doc wedger/certs = {picks: [key, ...]}; only the owner sees the boxes, everyone sees the badge.
  const CERT_WEEK = 'w9';
  const certKey = (game, market, contract) => [CERT_WEEK, game, market, contract].join('|');
  const keyOfLine = (r) => certKey(r.game, r.market, r.contract);
  const keyOfAtd = (r) => certKey(r.game, 'Anytime Touchdown', r.player);
  const keyOfResult = (r) => ['w' + (r.week || 6), r.game, r.group === 'ATD filter picks' ? 'Anytime Touchdown' : r.market, r.contract].join('|');
  let certReady = false, certUnavailable = false;
  let certs = new Set(), certOwner = false, certRef = null, certPending = 0, certQueue = Promise.resolve();
  const certNote = (msg) => { const el = $('#certnote'); el.textContent = msg || ''; el.hidden = !msg; };
  const redrawPicks = () => { drawLines(); catPages.forEach((draw) => draw()); drawAtd(); drawResults(); drawRecord(); drawProfit(); drawAnalysts(); };
  const applyCertSnap = (snap) => {
    if (certPending) return;
    const picks = snap.exists ? snap.data().picks : null;
    certs = new Set(Array.isArray(picks) ? picks.filter((k) => typeof k === 'string') : []);
    certReady = true;
    redrawPicks();
  };
  const setCert = (key, on) => {
    if (!certRef || !certOwner) return;
    const next = new Set(certs);
    if (on) next.add(key); else next.delete(key);
    certs = next;
    redrawPicks();
    const body = { picks: [...next].sort(), updated: new Date().toISOString() };
    certPending += 1;
    certQueue = certQueue.then(() => certRef.set(body)).then(() => certNote(''), () => {
      certNote("Couldn't save that Wedge certification. Try again.");
    }).finally(() => {
      certPending -= 1;
      if (!certPending) certRef.get().then(applyCertSnap, () => {});
    });
  };
  const certCell = (tr, key, label) => {
    const c = document.createElement('td'); c.className = 'wg-certcol';
    if (certOwner) {
      const box = document.createElement('input');
      box.type = 'checkbox'; box.className = 'wg-certbox'; box.checked = certs.has(key);
      box.setAttribute('aria-label', 'Wedge certify ' + label);
      box.addEventListener('change', () => setCert(key, box.checked));
      c.appendChild(box);
    }
    tr.appendChild(c);
    if (certs.has(key)) tr.classList.add('wg-certified');
  };
  const certBadge = (cell, key) => {
    if (!certs.has(key)) return;
    const b = document.createElement('span'); b.className = 'wg-cert'; b.title = 'Wedge certified';
    b.append(document.createElement('i'), 'Wedge');
    cell.appendChild(b);
  };
  (async () => {
    await new Promise((r) => setTimeout(r, 0));
    const cl = window.claude;
    if (!cl || typeof cl.use !== 'function') { certUnavailable = true; drawRecord(); drawProfit(); drawAnalysts(); return; }
    const [db, user] = await Promise.all([cl.use('db'), cl.use('user')]);
    if (!db) { certUnavailable = true; drawRecord(); drawProfit(); drawAnalysts(); return; }
    certRef = db.doc('wedger/certs');
    certRef.onSnapshot(applyCertSnap, () => {});
    anRef = db.doc('wedger/analysts');
    anRef.onSnapshot(applyAnSnap, () => {});
    if (user && await user.isOwner()) {
      certOwner = true;
      document.querySelector('.rs-wrap').classList.add('wg-owner');
      redrawPicks();
    }
  })();

  // Wedge record: every certified pick that has settled, across weeks
  function drawRecord() {
    const box = $('#wg-record');
    const pctEl = $('.wg-record-pct', box), fracEl = $('.wg-record-frac', box), subEl = $('.wg-record-sub', box);
    box.classList.remove('wg-up', 'wg-down');
    const d = dash.data('results');
    if (d.status !== 'ok' || !certReady) {
      pctEl.textContent = '—'; fracEl.textContent = '';
      subEl.textContent = d.status === 'error' ? 'Failed to load' : (certUnavailable ? 'Record unavailable in this view' : 'Certified picks, settled');
      return;
    }
    const settled = new Map();
    for (const r of d.data) { const k = keyOfResult(r); if (!settled.has(k) || r.group !== 'ATD filter picks') settled.set(k, r); }
    let w = 0, n = 0, pending = 0;
    const weeks = new Map();
    for (const k of certs) {
      const r = settled.get(k);
      if (!r) { pending += 1; continue; }
      if (r.outcome !== 'Won' && r.outcome !== 'Lost') continue;
      const won = r.outcome === 'Won';
      n += 1; if (won) w += 1;
      const wk = Number(r.week || 6), e = weeks.get(wk) || { w: 0, n: 0 };
      e.n += 1; if (won) e.w += 1; weeks.set(wk, e);
    }
    if (n) {
      const p = Math.round(1000 * w / n) / 10;
      pctEl.textContent = (p % 1 ? p.toFixed(1) : p) + '%';
      fracEl.textContent = `(${w}/${n})`;
      wzRecord(p, w, n);
      if (p > 50) box.classList.add('wg-up'); else if (p < 50) box.classList.add('wg-down');
    } else { pctEl.textContent = '—'; fracEl.textContent = '(0/0)'; wzRecord(null, 0, 0); }
    const parts = [...weeks.entries()].sort((a, b) => a[0] - b[0]).map(([wk, e]) => `Week ${wk}: ${e.w}/${e.n}`);
    if (pending) parts.push(`${pending} pending`);
    subEl.textContent = parts.length ? parts.join(' · ') : 'No certified picks settled yet';
  }

  // Lobby: net profit on certified picks, one Yes contract per pick at its listed price
  function drawProfit() {
    const el = $('#wg-profit');
    const d = dash.data('results');
    if (d.status !== 'ok' || !certReady) {
      el.textContent = d.status === 'error' ? 'Failed to load'
        : (certUnavailable ? 'Net profit on Wedge-certified picks is unavailable in this view.' : 'Net profit on Wedge-certified picks so far: —');
      return;
    }
    const byKey = new Map();
    for (const r of d.data) { const k = keyOfResult(r); if (!byKey.has(k) || r.group !== 'ATD filter picks') byKey.set(k, r); }
    const settled = [...certs].map((k) => byKey.get(k)).filter((r) => r && (r.outcome === 'Won' || r.outcome === 'Lost'));
    if (!settled.length) { el.textContent = 'Net profit on Wedge-certified picks: no certified picks have settled yet.'; return; }
    const cost = settled.reduce((a, r) => a + Number(r.yes_price), 0);
    const profit = settled.reduce((a, r) => a + Number(r.profit_c), 0);
    const pct = Math.round(1000 * profit / cost) / 10;
    const big = document.createElement('span');
    big.className = 'wg-profit-pct' + (pct > 0 ? ' wg-pos' : (pct < 0 ? ' wg-neg' : ''));
    big.textContent = (pct > 0 ? '+' : (pct < 0 ? '−' : '')) + Math.abs(pct).toFixed(1) + '%';
    el.replaceChildren('Net profit on Wedge-certified picks so far: ', big);
    wzSet('cert-profit', big.textContent, true);
  }

  // ---------------- analysts ----------------
  // Shared doc wedger/analysts = {order: [names], picks: {name: [key, ...]}}; only the owner edits.
  const ANALYSTS_DEFAULT = ['Jason', 'Will', 'Chris', 'Sean'];
  let analysts = { order: ANALYSTS_DEFAULT.slice(), picks: {} }, anRef = null, anReady = false, anPending = 0, anQueue = Promise.resolve();
  const applyAnSnap = (snap) => {
    if (anPending) return;
    const d = snap.exists ? snap.data() : null;
    const order = d && Array.isArray(d.order) ? d.order.filter((x) => typeof x === 'string' && x) : ANALYSTS_DEFAULT.slice();
    const picks = {};
    for (const n of order) { const p = d && d.picks ? d.picks[n] : null; picks[n] = Array.isArray(p) ? p.filter((k) => typeof k === 'string') : []; }
    analysts = { order, picks };
    anReady = true;
    drawAnalysts();
  };
  const saveAnalysts = (next) => {
    if (!anRef || !certOwner) return;
    analysts = next;
    drawAnalysts();
    const body = { order: next.order, picks: next.picks, updated: new Date().toISOString() };
    anPending += 1;
    anQueue = anQueue.then(() => anRef.set(body)).then(() => certNote(''), () => {
      certNote("Couldn't save that analyst pick. Try again.");
    }).finally(() => {
      anPending -= 1;
      if (!anPending) anRef.get().then(applyAnSnap, () => {});
    });
  };
  // every line Wedge knows about, keyed like certifications; settled results win over open lines
  const pickIndex = () => {
    const idx = new Map();
    const put = (k, v) => { const cur = idx.get(k); if (!cur || (!cur.settled && v.settled)) idx.set(k, v); };
    const L = dash.data('lines'), A = dash.data('atd'), R = dash.data('results');
    if (L.status === 'ok') for (const r of L.data) put(keyOfLine(r), { week: 9, game: r.game, market: r.market, contract: r.contract, yes_price: r.yes_price, outcome: 'Pending', detail: '', profit_c: '', settled: false });
    if (A.status === 'ok') for (const r of A.data) if (r.yes_price !== '' && r.yes_price != null) put(keyOfAtd(r), { week: 9, game: r.game, market: 'Anytime Touchdown', contract: r.player, yes_price: r.yes_price, outcome: 'Pending', detail: '', profit_c: '', settled: false });
    const X = dash.data('pick_prices');
    if (X.status === 'ok') for (const r of X.data) put(r.key, { week: Number(r.week || 7), game: r.game, market: r.market, contract: r.contract, yes_price: r.yes_price, outcome: 'Pending', detail: '', profit_c: '', settled: false });
    if (R.status === 'ok') for (const r of R.data) {
      const k = keyOfResult(r), cur = idx.get(k);
      if (cur && cur.settled && r.group === 'ATD filter picks') continue;
      idx.set(k, { week: Number(r.week || 6), game: r.game, market: r.group === 'ATD filter picks' ? 'Anytime Touchdown' : r.market, contract: r.contract, yes_price: r.yes_price, outcome: r.outcome, detail: r.week6_result, profit_c: r.profit_c, settled: r.outcome === 'Won' || r.outcome === 'Lost' });
    }
    return idx;
  };
  const pickInfo = (idx, k) => {
    const hit = idx.get(k);
    if (hit) return hit;
    const [w, game, market, ...rest] = k.split('|');
    return { week: Number(String(w).replace(/\D/g, '')) || '', game: game || '', market: market || '', contract: rest.join('|'), yes_price: '', outcome: 'Pending', detail: '', profit_c: '', settled: false };
  };
  const ans = { who: '', week: '', outcome: '', q: '', sortK: 'week', sortDir: -1 };
  const ANNUM = new Set(['week', 'yes_price', 'profit_c']);
  const anTable = $('#an-table');
  const anWho = $('.an-who'), anFilter = $('.an-filter'), anWeek = $('.an-week'), anOut = $('.an-outcome'), anSearch = $('.an-search'), anPick = $('.an-pick'), anMsg = $('.an-msg');
  anFilter.addEventListener('change', () => { ans.who = anFilter.value; drawAnalysts(); });
  anWeek.addEventListener('change', () => { ans.week = anWeek.value; drawAnalysts(); });
  anOut.addEventListener('change', () => { ans.outcome = anOut.value; drawAnalysts(); });
  anSearch.addEventListener('input', () => { ans.q = anSearch.value.trim().toLowerCase(); drawAnalysts(); });
  wireSort(anTable, ans, ANNUM, () => drawAnalysts());
  let anLabels = new Map(), anOptCount = -1;
  const pickLabel = (v) => `W${v.week} · ${v.game} · ${v.contract}${v.market && !v.contract.includes(':') ? ' (' + v.market + ')' : ''}${v.yes_price !== '' ? ' · ' + v.yes_price + '¢' : ''}`;
  $('.an-addbtn').addEventListener('click', () => {
    const who = anWho.value, key = anLabels.get(anPick.value);
    if (!who) { anMsg.textContent = 'Choose an analyst.'; return; }
    if (!key) { anMsg.textContent = 'Pick a line from the list.'; return; }
    const cur = analysts.picks[who] || [];
    if (cur.includes(key)) { anMsg.textContent = `Already in ${who}'s picks.`; return; }
    saveAnalysts({ order: analysts.order, picks: { ...analysts.picks, [who]: [...cur, key] } });
    anPick.value = ''; anMsg.textContent = `Added to ${who}.`;
  });
  const fillSel = (sel, items, first) => {
    const want = (first ? [first] : []).concat(items.map((x) => [x, x]));
    const sig = want.map((o) => o[0]).join('\u0001');
    if (sel.dataset.sig === sig) return;
    const cur = sel.value;
    sel.replaceChildren(...want.map(([v, t]) => new Option(t, v)));
    sel.dataset.sig = sig;
    if (want.some((o) => o[0] === cur)) sel.value = cur;
  };
  function drawAnalysts() {
    const board = $('#an-board'), tbody = $('tbody', anTable);
    markSort(anTable, ans);
    const R = dash.data('results');
    if (R.status !== 'ok' || !anReady) {
      board.replaceChildren(); tbody.replaceChildren();
      if (certUnavailable) { const wb = $('#wz-board'); if (wb) wb.replaceChildren(el('p', 'wx-empty', 'Analyst standings are unavailable in this view.')); const tg = $('#pf-tgrid'); if (tg) tg.replaceChildren(el('p', 'wx-empty', 'Analyst picks are unavailable in this view.')); }
      $('.an-count').textContent = R.status === 'error' ? 'Failed to load' : (certUnavailable ? 'Analyst picks are unavailable in this view' : '');
      return;
    }
    const idx = pickIndex();
    // standings
    const stats = analysts.order.map((name) => {
      const keys = analysts.picks[name] || [];
      const info = keys.map((k) => pickInfo(idx, k));
      const settled = info.filter((v) => v.settled);
      const wins = settled.filter((v) => v.outcome === 'Won').length;
      const cost = settled.reduce((a, v) => a + Number(v.yes_price), 0);
      const profit = settled.reduce((a, v) => a + Number(v.profit_c), 0);
      const pending = info.filter((v) => v.outcome === 'Pending').length;
      return { name, n: settled.length, wins, winPct: settled.length ? Math.round(1000 * wins / settled.length) / 10 : null,
        profitPct: cost ? Math.round(1000 * profit / cost) / 10 : null, pending, total: keys.length };
    });
    const ranked = stats.slice().sort((a, b) => (b.winPct ?? -1) - (a.winPct ?? -1) || (b.profitPct ?? -1e9) - (a.profitPct ?? -1e9) || b.n - a.n);
    try { wzAnalysts(ranked); } catch (e) { /* the lobby board is optional */ }
    try { wzTeamPicks(); } catch (e) { console.error('team picks', e); }
    const fmtPct = (p, signedPct) => (signedPct ? (p > 0 ? '+' : (p < 0 ? '−' : '')) : '') + (Math.abs(p) % 1 ? Math.abs(p).toFixed(1) : Math.abs(p)) + '%';
    board.replaceChildren(...ranked.map((st, i) => {
      const card = document.createElement('div'); card.className = 'wg-an' + (i === 0 && st.n ? ' wg-lead' : ''); card.dataset.key = st.name;
      const head = document.createElement('div'); head.className = 'wg-an-head';
      const av = document.createElement('span'); av.className = 'wg-an-av'; av.textContent = st.name.slice(0, 1).toUpperCase(); av.setAttribute('aria-hidden', 'true');
      const nm = document.createElement('span'); nm.className = 'wg-an-name'; nm.textContent = st.name;
      const rk = document.createElement('span'); rk.className = 'wg-an-rank'; rk.textContent = st.n ? '#' + (i + 1) : '—';
      head.append(av, nm, rk);
      const stat = (label, value, cls, small) => {
        const d = document.createElement('div');
        const l = document.createElement('div'); l.className = 'wg-an-lab'; l.textContent = label;
        const v = document.createElement('div'); v.className = 'wg-an-val' + (cls ? ' ' + cls : ''); v.textContent = value;
        if (small) { const sm = document.createElement('small'); sm.textContent = small; v.appendChild(sm); }
        d.append(l, v); return d;
      };
      const grid = document.createElement('div'); grid.className = 'wg-an-stats';
      grid.append(
        stat('Win %', st.winPct == null ? '—' : fmtPct(st.winPct), st.winPct == null ? '' : (st.winPct > 50 ? 'wg-pos' : (st.winPct < 50 ? 'wg-neg' : '')), st.n ? `(${st.wins}/${st.n})` : ''),
        stat('Net profit', st.profitPct == null ? '—' : fmtPct(st.profitPct, true), st.profitPct == null ? '' : (st.profitPct > 0 ? 'wg-pos' : (st.profitPct < 0 ? 'wg-neg' : ''))));
      const foot = document.createElement('div'); foot.className = 'wg-an-foot';
      foot.textContent = st.total ? `${st.n} settled · ${st.pending} pending` : 'No picks yet';
      card.append(head, grid, foot);
      return card;
    }));
    // controls
    fillSel(anWho, analysts.order, null);
    fillSel(anFilter, analysts.order, ['', 'All analysts']);
    // picks table
    let rows = [];
    for (const name of analysts.order) for (const k of analysts.picks[name] || []) {
      const v = pickInfo(idx, k);
      rows.push({ id: name + '|' + k, key: k, analyst: name, week: v.week, game: v.game, market: v.market, contract: v.contract, yes_price: v.yes_price, outcome: v.outcome, detail: v.detail, profit_c: v.profit_c });
    }
    fillSel(anWeek, [...new Set(rows.map((r) => String(r.week)).filter(Boolean))].sort((a, b) => b - a).map((w) => w), ['', 'All weeks']);
    [...anWeek.options].forEach((o) => { if (o.value) o.textContent = 'Week ' + o.value; });
    const v = rows.filter((r) => (!ans.who || r.analyst === ans.who) && (!ans.week || String(r.week) === ans.week) && (!ans.outcome || r.outcome === ans.outcome) &&
      (!ans.q || (r.analyst + ' ' + r.game + ' ' + r.market + ' ' + r.contract).toLowerCase().includes(ans.q)))
      .sort((a, b) => makeSorter(ans, ANNUM)(a, b) || a.analyst.localeCompare(b.analyst) || a.game.localeCompare(b.game));
    const w = v.filter((r) => r.outcome === 'Won').length, l = v.filter((r) => r.outcome === 'Lost').length;
    $('.an-count').textContent = `${fmt(v.length)} picks · ${w}–${l}`;
    const frag = document.createDocumentFragment();
    for (const r of v) {
      const tr = document.createElement('tr'); tr.dataset.key = r.id;
      const td = mkTd(tr);
      td(r.analyst, 'rs-contract');
      td(r.week, 'num rs-sub');
      wzGameCell(td(r.game, 'rs-sub'), r.game);
      td(r.market, 'rs-hide-narrow rs-sub');
      certBadge(td(r.contract, 'rs-contract'), r.key);
      td(r.yes_price === '' ? '—' : r.yes_price, 'num');
      td(r.outcome, r.outcome === 'Won' ? 'an-won' : (r.outcome === 'Lost' ? 'an-lost' : 'an-pending'));
      td(r.detail || '', 'rs-hide-narrow rs-results');
      const pc = num(r.profit_c);
      td(pc == null ? '—' : (pc > 0 ? '+' : '') + r.profit_c, 'num' + (pc > 0 ? ' rs-hi' : (pc == null ? ' rs-sub' : ' rs-sub')));
      const ec = document.createElement('td'); ec.className = 'wg-certcol';
      if (certOwner) {
        const b = document.createElement('button'); b.type = 'button'; b.className = 'an-rm'; b.textContent = '×';
        b.setAttribute('aria-label', `Remove ${r.contract} from ${r.analyst}'s picks`);
        b.addEventListener('click', () => {
          const cur = analysts.picks[r.analyst] || [];
          saveAnalysts({ order: analysts.order, picks: { ...analysts.picks, [r.analyst]: cur.filter((k) => k !== r.key) } });
        });
        ec.appendChild(b);
      }
      tr.appendChild(ec);
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
    // add-pick options (owner only)
    if (certOwner && idx.size !== anOptCount) {
      anOptCount = idx.size;
      anLabels = new Map();
      const opts = [...idx.entries()].sort((a, b) => (b[1].week - a[1].week) || a[1].game.localeCompare(b[1].game) || a[1].contract.localeCompare(b[1].contract))
        .map(([k, val]) => { const lab = pickLabel(val); anLabels.set(lab, k); const o = document.createElement('option'); o.value = lab; return o; });
      $('#an-options').replaceChildren(...opts);
    }
  }

  // ---------------- all-lines page ----------------
  const FULL = new Set(['Moneyline', 'Spreads', 'Totals', 'Winning Margin', 'Overtime', '1st Half / Fulltime Result', 'Most Receiving Yards']);
  const groupOf = (m) => FULL.has(m) ? (m === 'Most Receiving Yards' ? 'Player props' : 'Full game')
    : (/Quarter|Half/.test(m) ? 'Quarters & halves' : 'Player props');
  const ls = { show: 'q', game: '', group: '', src: '', mom: '', role: '', px: '', lim: 500, clean: false, upcoming: false, certOnly: false, q: '', sortK: 'hit_rate', sortDir: -1 };
  const pxOk = (r) => { if (!ls.px) return true; const [a, b] = ls.px.split('-').map(Number), p = num(r.yes_price); return p != null && p >= a && p <= b; };
  const LNUM = new Set(['yes_price', 'yes_bid', 'hit_rate', 'sit_hit', 'hits', 'games']);
  const linesTable = $('#lines-table');
  const showSel = $('.rs-show'), gameSel = $('.rs-game'), groupSel = $('.rs-group'), cleanBox = $('.rs-clean'), upBox = $('.rs-upcoming'), search = $('.rs-search');
  showSel.addEventListener('change', () => { ls.show = showSel.value; ls.lim = 500; const ev = ls.show === 'every'; $('.rs-px').hidden = !ev; $('.rl-every-note').hidden = !ev; if (!ev) { ls.px = ''; $('.rs-px').value = ''; } drawLines(); });
  $('.rs-px').addEventListener('change', (e) => { ls.px = e.target.value; ls.lim = 500; drawLines(); });
  $('.rl-more').addEventListener('click', () => { ls.lim += 500; drawLines(); });
  gameSel.addEventListener('change', () => { ls.game = gameSel.value; drawLines(); });
  groupSel.addEventListener('change', () => { ls.group = groupSel.value; drawLines(); });
  $('.rs-src').addEventListener('change', (e) => { ls.src = e.target.value; drawLines(); });
  $('.rs-mom').addEventListener('change', (e) => { ls.mom = e.target.value; drawLines(); });
  $('.rs-role').addEventListener('change', (e) => { ls.role = e.target.value; drawLines(); });
  cleanBox.addEventListener('change', () => { ls.clean = cleanBox.checked; drawLines(); });
  upBox.addEventListener('change', () => { ls.upcoming = upBox.checked; drawLines(); });
  search.addEventListener('input', () => { ls.q = search.value.trim().toLowerCase(); drawLines(); });
  $('.rs-certonly').addEventListener('change', (e) => { ls.certOnly = e.target.checked; drawLines(); });
  wireSort(linesTable, ls, LNUM, () => drawLines());

  function drawLines() {
    const d = ls.show === 'every' ? dash.data('lines_all') : dash.data('lines');
    const tbody = $('tbody', linesTable);
    markSort(linesTable, ls);
    if (d.status !== 'ok') { tbody.replaceChildren(); $('.rl-count').textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
    const rows = d.data;
    fillGames(gameSel, rows, ls.game);
    let v = rows.filter((r) =>
      (ls.certOnly ? certs.has(keyOfLine(r)) : (ls.show === 'all' || ls.show === 'every' || (ls.show === 'pick' ? !!r.sit_pick : r.qualifies === 'Yes'))) &&
      pxOk(r) &&
      (!ls.game || r.game === ls.game) &&
      (!ls.group || groupOf(r.market) === ls.group) &&
      (!ls.src || (r.source || 'Robinhood') === ls.src) &&
      momOk(r, ls.mom, num(r.yes_price)) &&
      roleOk(r, ls.role) &&
      (!ls.clean || !r.flags) &&
      (!ls.upcoming || !started(r)) &&
      (!ls.q || (r.game + ' ' + r.market + ' ' + r.contract + ' ' + r.sample).toLowerCase().includes(ls.q)));
    v = v.slice().sort(makeSorter(ls, LNUM));
    const shown = ls.show === 'every' ? v.slice(0, ls.lim) : v;
    $('.rl-count').textContent = ls.certOnly ? fmt(v.length) + ' Wedge certified' : fmt(v.length) + ' of ' + fmt(rows.length) + ' lines' + (shown.length < v.length ? ` · showing ${fmt(shown.length)}` : '');
    const more = $('.rl-more'); more.hidden = shown.length >= v.length; more.textContent = `Show ${fmt(Math.min(500, v.length - shown.length))} more`;
    const frag = document.createDocumentFragment();
    for (const r of shown) {
      const tr = document.createElement('tr'); tr.dataset.key = r.id; if (started(r)) tr.className = 'rs-started'; wzTint(tr, r);
      const ck = keyOfLine(r);
      certCell(tr, ck, r.game + ' ' + r.contract);
      const td = mkTd(tr);
      totalStar(td(r.game), r);
      td(r.kickoff, 'rs-hide-narrow rs-sub');
      td(r.market, 'rs-sub');
      const lc = td(wzLabel(r), 'rs-contract'); if (lc.textContent !== r.contract) lc.title = r.contract;
      certBadge(lc, ck);
      wzInj(lc, r.flags);
      td(r.yes_price, 'num');
      srcCell(tr, r);
      td(r.yes_bid === '' ? '—' : r.yes_bid, 'num rs-hide-narrow rs-sub');
      pctCell(tr, r.hit_rate);
      sitCell(tr, r, { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source });
      roleCell(tr, r);
      momCell(tr, r);
      td(r.hits === '' ? '—' : r.hits, 'num');
      td(r.games, 'num');
      td(r.sample, 'rs-hide-narrow rs-sub');
      td(r.season_results, 'rs-hide-narrow rs-results');
      td(r.flags, 'rs-flag');
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
  }

  // ---------------- NBA lines ----------------
  const nbs = { show: 'q', game: '', group: '', mkt: '', clean: false, upcoming: false, q: '', sortK: 'kickoff_utc', sortDir: 1 };
  const NBNUM = new Set(['yes_price', 'yes_bid', 'book_fair', 'hit_rate', 'sit_hit', 'hits', 'games']);
  const nbaTable = $('#nba-table');
  const nbEl = (c) => $('#nba-lines-card .' + c);
  nbEl('nb-show').addEventListener('change', (e) => { nbs.show = e.target.value; drawNba(); });
  nbEl('nb-game').addEventListener('change', (e) => { nbs.game = e.target.value; drawNba(); });
  nbEl('nb-group').addEventListener('change', (e) => { nbs.group = e.target.value; drawNba(); });
  nbEl('nb-mkt').addEventListener('change', (e) => { nbs.mkt = e.target.value; drawNba(); });
  nbEl('nb-clean').addEventListener('change', (e) => { nbs.clean = e.target.checked; drawNba(); });
  nbEl('nb-upcoming').addEventListener('change', (e) => { nbs.upcoming = e.target.checked; drawNba(); });
  nbEl('nb-search').addEventListener('input', (e) => { nbs.q = e.target.value.trim().toLowerCase(); drawNba(); });
  wireSort(nbaTable, nbs, NBNUM, () => drawNba());
  const nbaLabel = (r) => r.contract.replace(/: (\d+)\+ points, rebounds and assists$/, ': $1+ PRA');
  function drawNba() {
    const d = dash.data('nba_lines');
    const tbody = $('tbody', nbaTable);
    markSort(nbaTable, nbs);
    if (d.status !== 'ok') { tbody.replaceChildren(); nbEl('nb-count').textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
    const rows = d.data;
    fillGames(nbEl('nb-game'), rows, nbs.game);
    const q = rows.filter((r) => r.qualifies === 'Yes');
    $('#nba-t-band').textContent = fmt(rows.length);
    $('#nba-t-q').textContent = fmt(q.length);
    $('#nba-t-qn').textContent = `${fmt(q.filter((r) => r.group === 'Player props').length)} player props, ${fmt(q.filter((r) => r.group !== 'Player props').length)} team lines`;
    let v = rows.filter((r) =>
      (nbs.show === 'all' || r.qualifies === 'Yes') &&
      (!nbs.game || r.game === nbs.game) &&
      (!nbs.group || r.group === nbs.group) &&
      (!nbs.mkt || r.market === nbs.mkt) &&
      (!nbs.clean || !r.flags) &&
      (!nbs.upcoming || !started(r)) &&
      (!nbs.q || (r.game + ' ' + r.market + ' ' + r.contract + ' ' + (r.team || '')).toLowerCase().includes(nbs.q)));
    v = v.slice().sort(makeSorter(nbs, NBNUM));
    nbEl('nb-count').textContent = fmt(v.length) + ' of ' + fmt(rows.length) + ' lines';
    const frag = document.createDocumentFragment();
    for (const r of v) {
      const tr = document.createElement('tr'); tr.dataset.key = r.id; if (started(r)) tr.className = 'rs-started'; wzTint(tr, r);
      const td = mkTd(tr);
      wzGameCell(td(r.game), r.game);
      td(r.kickoff, 'rs-hide-narrow rs-sub');
      td(r.market, 'rs-sub');
      const lc = td(nbaLabel(r), 'rs-contract'); if (lc.textContent !== r.contract) lc.title = r.contract;
      td(r.yes_price, 'num');
      td(r.yes_bid === '' ? '—' : r.yes_bid, 'num rs-hide-narrow rs-sub');
      const bf = num(r.book_fair), gap = bf == null ? 0 : bf - num(r.yes_price);
      const bc = td(bf == null ? '—' : Math.round(bf) + '%', 'num rs-hide-narrow ' + (gap >= 5 ? 'wg-bk-up' : gap <= -5 ? 'wg-bk-down' : 'rs-sub'));
      if (r.book_lines) bc.title = r.book_lines;
      pctCell(tr, r.hit_rate);
      sitCell(tr, r, { title: nbaLabel(r), game: r.game, market: r.market, source: r.source, key: `${r.game}|${r.market}|${r.contract}`, sport: 'nba' });
      td(r.hits === '' ? '—' : r.hits, 'num');
      td(r.games, 'num');
      td(r.sample, 'rs-hide-narrow rs-sub');
      td(r.season_results, 'rs-hide-narrow rs-results');
      td(r.flags, 'rs-flag');
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
    // by game
    const games = d3.rollups(rows, (g) => ({ inband: g.length, qualifying: g.filter((r) => r.qualifies === 'Yes').length, t: g[0].kickoff_utc, props: g.some((r) => r.group === 'Player props') }), (r) => r.game)
      .sort((a, b) => String(a[1].t).localeCompare(String(b[1].t)) || a[0].localeCompare(b[0]));
    const max = d3.max(games, (g) => g[1].inband) || 1;
    $('#nba-games').replaceChildren(...games.map(([game, s]) => {
      const row = document.createElement('div'); row.className = 'rs-grow';
      const name = document.createElement('div'); name.textContent = game;
      if (s.props) { const p = document.createElement('span'); p.className = 'wg-pill'; p.textContent = 'Props'; name.append(p); }
      const bar = document.createElement('div'); bar.className = 'rs-gbar';
      const a = document.createElement('span'); a.style.width = (s.inband / max * 100) + '%'; a.style.background = 'var(--cds-chart-muted)';
      const b = document.createElement('span'); b.style.width = (s.qualifying / max * 100) + '%'; b.style.background = 'var(--wg-green)';
      bar.append(a, b);
      const val = document.createElement('div'); val.style.textAlign = 'right'; val.textContent = `${s.qualifying} / ${s.inband}`;
      row.append(name, bar, val); return row;
    }));
  }

  // ---------------- category pages ----------------
  const CNUM = new Set(['team_ml', 'opp_rank_vs_pos', 'yes_price', 'hit_rate', 'sit_hit', 'hits', 'games']);
  const catPages = [...document.querySelectorAll('.rc-page')].map((page) => {
    const st = { cat: page.dataset.cat, show: 'q', game: '', mom: '', role: '', clean: false, upcoming: false, certOnly: false, q: '', sortK: 'hit_rate', sortDir: -1 };
    const table = $('.rc-table', page);
    const els = { show: $('.rc-show', page), game: $('.rc-game', page), mom: $('.rc-mom', page), role: $('.rc-role', page), clean: $('.rc-clean', page), upcoming: $('.rc-upcoming', page), certOnly: $('.rc-certonly', page), search: $('.rc-search', page), count: $('.rc-count', page) };
    const draw = () => {
      const d = dash.data('props');
      const tbody = $('tbody', table);
      markSort(table, st);
      if (d.status !== 'ok') { tbody.replaceChildren(); els.count.textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
      const rows = d.data.filter((r) => r.cat === st.cat);
      fillGames(els.game, rows, st.game);
      let v = rows.filter((r) =>
        (st.certOnly ? certs.has(keyOfLine(r)) : (st.show === 'all' || (st.show === 'pick' ? !!r.sit_pick : r.qualifies === 'Yes'))) &&
        (!st.game || r.game === st.game) &&
        momOk(r, st.mom, num(r.yes_price)) &&
        roleOk(r, st.role) &&
        (!st.clean || !r.flags) &&
        (!st.upcoming || !started(r)) &&
        (!st.q || (r.game + ' ' + r.team + ' ' + r.contract + ' ' + r.market + ' ' + r.pos).toLowerCase().includes(st.q)));
      v = v.slice().sort(makeSorter(st, CNUM));
      els.count.textContent = fmt(v.length) + (st.certOnly ? ' Wedge certified' : ' props');
      const frag = document.createDocumentFragment();
      for (const r of v) {
        const tr = document.createElement('tr'); tr.dataset.key = r.id; if (started(r)) tr.className = 'rs-started'; wzTint(tr, r);
        const ck = keyOfLine(r);
        certCell(tr, ck, r.game + ' ' + r.contract);
        const td = mkTd(tr);
        totalStar(td(r.game, 'rs-sub'), r);
        td(r.kickoff, 'rs-hide-narrow rs-sub');
        const lc = td(rhLabel(r.contract), 'rs-contract'); if (lc.textContent !== r.contract) lc.title = r.contract;
        certBadge(lc, ck);
        td(r.market, 'rs-hide-narrow rs-sub');
        td(r.pos, 'rs-sub');
        td(r.team);
        td(r.team_ml, 'num rs-sub');
        const rank = num(r.opp_rank_vs_pos);
        td(rank == null ? '—' : r.opp_rank_vs_pos, 'num' + (rank != null && rank <= 10 ? ' rs-easy' : ' rs-sub'));
        td(r.yes_price, 'num');
        srcCell(tr, r);
        pctCell(tr, r.hit_rate);
        sitCell(tr, r, { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source });
        roleCell(tr, r);
        momCell(tr, r);
        td(r.hits === '' ? '—' : r.hits, 'num');
        td(r.games, 'num');
        td(r.season_results, 'rs-hide-narrow rs-results');
        td(r.flags, 'rs-flag');
        frag.appendChild(tr);
      }
      tbody.replaceChildren(frag);
    };
    els.show.addEventListener('change', () => { st.show = els.show.value; draw(); });
    els.game.addEventListener('change', () => { st.game = els.game.value; draw(); });
    els.mom.addEventListener('change', () => { st.mom = els.mom.value; draw(); });
    els.role.addEventListener('change', () => { st.role = els.role.value; draw(); });
    els.clean.addEventListener('change', () => { st.clean = els.clean.checked; draw(); });
    els.upcoming.addEventListener('change', () => { st.upcoming = els.upcoming.checked; draw(); });
    els.certOnly.addEventListener('change', () => { st.certOnly = els.certOnly.checked; draw(); });
    els.search.addEventListener('input', () => { st.q = els.search.value.trim().toLowerCase(); draw(); });
    wireSort(table, st, CNUM, draw);
    return draw;
  });

  // ---------------- Week 8 projections ----------------
  const pjs = { game: '', mkt: '', pos: '', mom: '', role: '', q: '', sortK: 'kickoff_utc', sortDir: 1 };
  const PJNUM = new Set(['est_line', 'proj', 'p_over', 'p_wedger', 'mom_p', 'season_avg', 'games']);
  const projTable = $('#proj-table');
  const pjEl = (c) => $('#proj-card .' + c);
  pjEl('pj-game').addEventListener('change', (e) => { pjs.game = e.target.value; drawProj(); });
  pjEl('pj-mkt').addEventListener('change', (e) => { pjs.mkt = e.target.value; drawProj(); });
  pjEl('pj-pos').addEventListener('change', (e) => { pjs.pos = e.target.value; drawProj(); });
  pjEl('pj-mom').addEventListener('change', (e) => { pjs.mom = e.target.value; drawProj(); });
  pjEl('pj-role').addEventListener('change', (e) => { pjs.role = e.target.value; drawProj(); });
  pjEl('pj-search').addEventListener('input', (e) => { pjs.q = e.target.value.trim().toLowerCase(); drawProj(); });
  wireSort(projTable, pjs, PJNUM, () => drawProj());
  const projLabel = (r) => (r.market === 'Anytime Touchdown' ? `${r.player}: anytime TD` : rhLabel(r.contract));
  function drawProj() {
    const d = dash.data('proj');
    const tbody = $('tbody', projTable);
    markSort(projTable, pjs);
    if (d.status !== 'ok') { tbody.replaceChildren(); pjEl('pj-count').textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
    const rows = d.data;
    fillGames(pjEl('pj-game'), rows, pjs.game);
    let v = rows.filter((r) =>
      (!pjs.game || r.game === pjs.game) &&
      (!pjs.mkt || r.market === pjs.mkt) &&
      (!pjs.pos || (r.pos === 'FB' ? 'RB' : r.pos) === pjs.pos) &&
      momOk(r, pjs.mom, num(r.p_over), 5) &&
      roleOk(r, pjs.role) &&
      (!pjs.q || (r.game + ' ' + r.team + ' ' + r.player + ' ' + r.market).toLowerCase().includes(pjs.q)));
    v = v.slice().sort(makeSorter(pjs, PJNUM));
    pjEl('pj-count').textContent = fmt(v.length) + ' of ' + fmt(rows.length) + ' props';
    const frag = document.createDocumentFragment();
    for (const r of v) {
      const tr = document.createElement('tr'); tr.dataset.key = r.id; if (started(r)) tr.className = 'rs-started'; wzTint(tr, r);
      const td = mkTd(tr);
      wzGameCell(td(r.game, 'rs-sub'), r.game);
      td(r.kickoff, 'rs-hide-narrow rs-sub');
      const lc = td(projLabel(r), 'rs-contract'); lc.title = r.market === 'Anytime Touchdown' ? 'Anytime TD (1+ rushing or receiving TD)' : `Expected line ${r.est_line} (season, last 4 and multi-season average, weighted the way books set Week 6–7 lines)`;
      td(r.pos, 'rs-sub rs-hide-narrow');
      td(r.team);
      const isTd = r.market === 'Anytime Touchdown';
      const pc = td(r.proj, 'num'); if (r.proj_lo !== '' && r.proj_hi !== '') pc.title = `Bear ${r.proj_lo} · bull ${r.proj_hi}`;
      sitCell(tr, { ...r, sit_hit: r.p_wedger, yes_price: '', yes_bid: '' }, { title: projLabel(r), game: r.game, market: r.market, key: `${r.game}|${r.market}|${r.contract}` });
      td(r.p_over === '' ? '—' : pctR(num(r.p_over)), 'num');
      td(r.mom_p === '' ? '—' : pctR(num(r.mom_p)), 'num rs-hide-narrow rs-sub');
      roleCell(tr, r);
      momCell(tr, r);
      td(isTd ? (num(r.season_avg) == null ? '—' : num(r.season_avg).toFixed(2)) : r.season_avg, 'num rs-hide-narrow rs-sub');
      td(r.games, 'num rs-hide-narrow rs-sub');
      td(r.flags, 'rs-flag');
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
  }

  // ---------------- defense table ----------------
  const ds = { sortK: 'rb_rank', sortDir: 1 };
  const DNUM = new Set(['games', 'rb_ppr_pg', 'rb_rank', 'rb_yds_pg', 'pc_ppr_pg', 'pc_rank', 'pc_yds_pg']);
  const defTable = $('#defense-table');
  wireSort(defTable, ds, DNUM, () => drawDefense());
  function drawDefense() {
    const d = dash.data('defense');
    const tbody = $('tbody', defTable);
    markSort(defTable, ds);
    if (d.status !== 'ok') { tbody.replaceChildren(); return; }
    const p = dash.data('lines');
    const sunday = new Set(p.status === 'ok' ? p.data.flatMap((r) => r.game.split(' @ ')) : []);
    const rows = d.data.slice().sort(makeSorter(ds, DNUM));
    const frag = document.createDocumentFragment();
    for (const r of rows) {
      const tr = document.createElement('tr'); tr.dataset.key = r.team;
      const td = mkTd(tr);
      td(r.team, sunday.has(r.team) ? 'rs-contract' : 'rs-sub');
      td(r.games, 'num rs-sub');
      td(num(r.rb_ppr_pg).toFixed(1), 'num');
      td(r.rb_rank, 'num' + (num(r.rb_rank) <= 10 ? ' rs-easy' : ''));
      td(num(r.rb_yds_pg).toFixed(1), 'num rs-hide-narrow rs-sub');
      td(num(r.pc_ppr_pg).toFixed(1), 'num');
      td(r.pc_rank, 'num' + (num(r.pc_rank) <= 10 ? ' rs-easy' : ''));
      td(num(r.pc_yds_pg).toFixed(1), 'num rs-hide-narrow rs-sub');
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
  }

  // ---------------- anytime TD page ----------------
  const ATD_DEFAULTS = { atd_rate: 50, games: 3, rz_opp_share: 0, rz_opps_pg: 0, target_share: 0, rz_tgt_share: 0, td_pg: 0, score: 0, pmin: 0, pmax: 100, pos: '', game: '', upcoming: true, clean: false, certOnly: false, q: '' };
  const as = Object.assign({ sortK: 'score', sortDir: -1 }, ATD_DEFAULTS);
  const ANUM = new Set(['yes_price', 'atd_rate', 'sit_hit', 'atd_hits', 'games', 'td_pg', 'rz_opp_share', 'rz_opps_pg', 'target_share', 'rz_tgt_share', 'score', 'rate_minus_price']);
  const PCTL = { atd_rate: 'atd_rate_pctl', td_pg: 'td_pg_pctl', rz_opp_share: 'rz_opp_share_pctl', target_share: 'target_share_pctl', rz_tgt_share: 'rz_tgt_share_pctl' };
  const atdTable = $('#atd-table');
  const aIns = [...document.querySelectorAll('.ra-in')];
  const aPmin = $('.ra-pmin'), aPmax = $('.ra-pmax'), aPos = $('.ra-pos'), aGame = $('.ra-game'), aUp = $('.ra-upcoming'), aClean = $('.ra-clean'), aCert = $('.ra-certonly'), aSearch = $('.ra-search');
  const syncInputs = () => {
    aIns.forEach((el) => { el.value = as[el.dataset.k]; });
    aPmin.value = as.pmin; aPmax.value = as.pmax; aPos.value = as.pos; aUp.checked = as.upcoming; aClean.checked = as.clean; aCert.checked = as.certOnly; aSearch.value = as.q;
  };
  const readNum = (el, fallback) => { const v = parseFloat(el.value); return Number.isFinite(v) ? v : fallback; };
  aIns.forEach((el) => el.addEventListener('input', () => { as[el.dataset.k] = readNum(el, 0); drawAtd(); }));
  aPmin.addEventListener('input', () => { as.pmin = readNum(aPmin, 0); drawAtd(); });
  aPmax.addEventListener('input', () => { as.pmax = readNum(aPmax, 100); drawAtd(); });
  aPos.addEventListener('change', () => { as.pos = aPos.value; drawAtd(); });
  aGame.addEventListener('change', () => { as.game = aGame.value; drawAtd(); });
  aUp.addEventListener('change', () => { as.upcoming = aUp.checked; drawAtd(); });
  aClean.addEventListener('change', () => { as.clean = aClean.checked; drawAtd(); });
  aCert.addEventListener('change', () => { as.certOnly = aCert.checked; drawAtd(); });
  aSearch.addEventListener('input', () => { as.q = aSearch.value.trim().toLowerCase(); drawAtd(); });
  $('.ra-reset').addEventListener('click', () => { Object.assign(as, ATD_DEFAULTS); syncInputs(); drawAtd(); });
  wireSort(atdTable, as, ANUM, () => drawAtd());
  syncInputs();

  const passes = (r) => {
    const n = (k) => num(r[k]) ?? 0;
    if (as.certOnly) { if (!certs.has(keyOfAtd(r))) return false; }
    else {
      if (n('games') < as.games) return false;
      if (as.atd_rate > 0 && !(n('atd_rate') > as.atd_rate)) return false;
      for (const k of ['rz_opp_share', 'rz_opps_pg', 'target_share', 'rz_tgt_share', 'td_pg', 'score']) if (as[k] > 0 && n(k) < as[k]) return false;
      const pr = num(r.yes_price);
      if ((as.pmin > 0 || as.pmax < 100) && (pr == null || pr < as.pmin || pr > as.pmax)) return false;
    }
    if (as.pos && r.pos !== as.pos) return false;
    if (as.game && r.game !== as.game) return false;
    if (as.upcoming && started(r)) return false;
    if (as.clean && r.flags) return false;
    if (as.q && !(r.player + ' ' + r.team + ' ' + r.game).toLowerCase().includes(as.q)) return false;
    return true;
  };

  function drawAtd() {
    const d = dash.data('atd');
    const tbody = $('tbody', atdTable);
    markSort(atdTable, as);
    if (d.status !== 'ok') { tbody.replaceChildren(); $('.ra-count').textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
    const rows = d.data;
    fillGames(aGame, rows, as.game);
    const v = rows.filter(passes).sort(makeSorter(as, ANUM));
    $('.ra-count').textContent = as.certOnly ? fmt(v.length) + ' Wedge certified' : fmt(v.length) + ' of ' + fmt(rows.length) + ' players pass';
    const frag = document.createDocumentFragment();
    for (const r of v) {
      const tr = document.createElement('tr'); tr.dataset.key = r.id; if (started(r)) tr.className = 'rs-started'; wzTint(tr, r);
      const ck = keyOfAtd(r);
      certCell(tr, ck, r.player + ' anytime TD');
      const td = mkTd(tr);
      const hi = (k) => { const p = num(r[PCTL[k]]); return p == null ? '' : (p >= 75 ? ' rs-hi' : (p <= 25 ? ' rs-sub' : '')); };
      const pct = (k) => (r[k] === '' ? '—' : r[k] + '%');
      certBadge(td(r.player, 'rs-contract'), ck);
      td(r.pos, 'rs-sub');
      td(r.team, 'rs-hide-narrow');
      totalStar(td(r.game, 'rs-sub'), r);
      td(r.kickoff, 'rs-hide-narrow rs-sub');
      td(r.yes_price === '' ? '—' : r.yes_price, 'num');
      srcCell(tr, r);
      pctCell(tr, r.atd_rate);
      if ((num(r.atd_rate_pctl) ?? 0) >= 75) tr.lastChild.classList.add('rs-hi');
      sitCell(tr, r, { title: r.player + ': anytime TD', game: r.game, market: 'Anytime Touchdown', source: r.source });
      td(r.atd_hits === '' ? '—' : r.atd_hits, 'num');
      td(r.games, 'num');
      td(r.td_pg === '' ? '—' : r.td_pg, 'num' + hi('td_pg'));
      td(pct('rz_opp_share'), 'num' + hi('rz_opp_share'));
      td(r.rz_opps_pg === '' ? '—' : r.rz_opps_pg, 'num rs-hide-narrow');
      td(pct('target_share'), 'num' + hi('target_share'));
      td(pct('rz_tgt_share'), 'num' + hi('rz_tgt_share'));
      const sc = num(r.score);
      td(sc == null ? '—' : r.score, 'num' + (sc != null && sc >= 80 ? ' rs-hi' : ''));
      const gap = num(r.rate_minus_price);
      td(gap == null ? '—' : (gap > 0 ? '+' : '') + r.rate_minus_price, 'num' + (gap == null ? ' rs-sub' : ''));
      td(r.td_log, 'rs-hide-narrow rs-results');
      td(r.flags, 'rs-flag');
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
  }


  // ---------------- week 6 results ----------------
  dash.calc('w6_summary', {
    title: 'Week 6 record by group',
    description: 'Wins, losses, win % and return (one Yes contract of each line bought at its screen price, fees excluded) for each group of Week 6 lines; voided lines left out.',
    inputs: ['results'],
    fn: (results) => {
      const seg = (segment, label, keep) => {
        const s = results.filter((r) => Number(r.week || 6) === 6 && r.outcome !== 'Void' && keep(r));
        const wins = s.filter((r) => r.outcome === 'Won').length;
        const cost = s.reduce((a, r) => a + Number(r.yes_price), 0);
        const profit = s.reduce((a, r) => a + Number(r.profit_c), 0);
        return { segment, label, wins, losses: s.length - wins,
          win_pct: s.length ? Math.round(1000 * wins / s.length) / 10 : null,
          avg_price: s.length ? Math.round(10 * cost / s.length) / 10 : null,
          roi_pct: cost ? Math.round(1000 * profit / cost) / 10 : null };
      };
      const L = (r) => r.group !== 'ATD filter picks' && r.group !== 'Other Wedge picks';
      const Q = (r) => L(r) && r.qualifies === 'Yes';
      return [
        seg('screen', 'Hit >50% (the screen)', Q),
        seg('rest', 'Rest of the 45–55¢ lines (hit 50% or less)', (r) => L(r) && r.qualifies === 'No'),
        seg('all', 'All 45–55¢ lines', L),
        seg('clean', 'Hit >50%, no flags', (r) => Q(r) && r.flagged === 'No'),
        seg('full', 'Hit >50% · full-game lines', (r) => Q(r) && r.group === 'Full game'),
        seg('periods', 'Hit >50% · quarter & half lines', (r) => Q(r) && r.group === 'Quarters & halves'),
        seg('props', 'Hit >50% · player props', (r) => Q(r) && r.group === 'Player props'),
        seg('b50', 'Hit just over 50–59% this season', (r) => L(r) && r.hit_bucket === 'Over 50–59%'),
        seg('b60', 'Hit 60–74% this season', (r) => L(r) && r.hit_bucket === '60–74%'),
        seg('b75', 'Hit 75–99% this season', (r) => L(r) && r.hit_bucket === '75–99%'),
        seg('b100', 'Hit 100% this season', (r) => L(r) && r.hit_bucket === '100%'),
        seg('cat1', 'Group 1 · RB on favorite (hit >50%)', (r) => Q(r) && r.cat === '1'),
        seg('cat2', 'Group 2 · WR/TE on underdog (hit >50%)', (r) => Q(r) && r.cat === '2'),
        seg('cat3', 'Group 3 · RB vs soft run D (hit >50%)', (r) => Q(r) && r.cat === '3'),
        seg('cat4', 'Group 4 · WR/TE vs soft pass D (hit >50%)', (r) => Q(r) && r.cat === '4'),
        seg('cats', 'Groups 1–4 combined (hit >50%)', (r) => Q(r) && ['1', '2', '3', '4'].includes(r.cat)),
        seg('atd', 'Anytime TD filter picks (3+ games, scored in >50%)', (r) => r.group === 'ATD filter picks'),
      ];
    },
  });

  const signed = (v) => (v == null || v === '' ? '—' : (Number(v) > 0 ? '+' : '') + v + '%');
  const rsTable = $('#results-summary-table');
  const rss = { sortK: '', sortDir: 1 };
  const RSNUM = new Set(['wins', 'losses', 'win_pct', 'avg_price', 'roi_pct']);
  wireSort(rsTable, rss, RSNUM, () => drawResultsSummary());
  function drawResultsSummary() {
    const d = dash.data('w6_summary');
    const tbody = $('tbody', rsTable);
    markSort(rsTable, rss);
    if (d.status !== 'ok') { tbody.replaceChildren(); return; }
    const rows = rss.sortK ? d.data.slice().sort(makeSorter(rss, RSNUM)) : d.data;
    const frag = document.createDocumentFragment();
    for (const r of rows) {
      const tr = document.createElement('tr'); tr.dataset.key = r.segment;
      const td = mkTd(tr);
      td(r.label, r.segment === 'screen' ? 'rs-contract' : '');
      td(r.wins, 'num'); td(r.losses, 'num');
      pctCell(tr, r.win_pct);
      td(r.avg_price == null ? '—' : r.avg_price, 'num rs-sub');
      td(signed(r.roi_pct), 'num' + (Number(r.roi_pct) > 0 ? ' rs-hi' : ''));
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
  }

  const rs = { wk: 8, show: 'q', outcome: '', game: '', certOnly: false, q: '', sortK: 'hit_rate', sortDir: -1 };
  const RNUM = new Set(['yes_price', 'hit_rate', 'profit_c']);
  const rTable = $('#results-table');
  const rShow = $('.rr-show'), rOut = $('.rr-outcome'), rGame = $('.rr-game'), rSearch = $('.rr-search');
  rShow.addEventListener('change', () => { rs.show = rShow.value; drawResults(); });
  $('.rr-week').addEventListener('change', (e) => { rs.wk = Number(e.target.value); rs.game = ''; drawResults(); });
  rOut.addEventListener('change', () => { rs.outcome = rOut.value; drawResults(); });
  rGame.addEventListener('change', () => { rs.game = rGame.value; drawResults(); });
  rSearch.addEventListener('input', () => { rs.q = rSearch.value.trim().toLowerCase(); drawResults(); });
  $('.rr-certonly').addEventListener('change', (e) => { rs.certOnly = e.target.checked; drawResults(); });
  wireSort(rTable, rs, RNUM, () => drawResults());
  function drawResults() {
    const d = dash.data('results');
    const tbody = $('tbody', rTable);
    markSort(rTable, rs);
    if (d.status !== 'ok') { tbody.replaceChildren(); $('.rr-count').textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
    const rows = d.data.filter((r) => Number(r.week || 6) === rs.wk);
    fillGames(rGame, rows, rs.game);
    const lineKeys = new Set(rows.filter((r) => r.group !== 'ATD filter picks').map(keyOfResult));
    const v = rows.filter((r) =>
      (rs.certOnly ? certs.has(keyOfResult(r)) && (r.group !== 'ATD filter picks' || !lineKeys.has(keyOfResult(r)))
        : (rs.show === 'atd' ? r.group === 'ATD filter picks' || (rs.wk >= 7 && r.market === 'Anytime Touchdown') : r.group !== 'ATD filter picks' && r.group !== 'Other Wedge picks' && !/pick\)/.test(r.group) && (rs.wk === 6 || r.market !== 'Anytime Touchdown') && (rs.show === 'all' || r.qualifies === 'Yes'))) &&
      (!rs.outcome || r.outcome === rs.outcome) &&
      (!rs.game || r.game === rs.game) &&
      (!rs.q || (r.game + ' ' + r.market + ' ' + r.contract).toLowerCase().includes(rs.q))).sort(makeSorter(rs, RNUM));
    const w = v.filter((r) => r.outcome === 'Won').length, l = v.filter((r) => r.outcome === 'Lost').length;
    $('.rr-count').textContent = `${fmt(v.length)} ${rs.certOnly ? 'Wedge certified' : 'lines'} · ${w}–${l}`;
    const frag = document.createDocumentFragment();
    for (const r of v) {
      const tr = document.createElement('tr'); tr.dataset.key = r.id;
      const ck = keyOfResult(r);
      certCell(tr, ck, r.game + ' ' + r.contract);
      const td = mkTd(tr);
      wzGameCell(td(r.game, 'rs-sub'), r.game);
      td(r.market, 'rs-hide-narrow rs-sub');
      certBadge(td(r.contract, 'rs-contract'), ck);
      td(r.yes_price, 'num');
      pctCell(tr, r.hit_rate);
      td(r.outcome, r.outcome === 'Won' ? 'rs-hi' : (r.outcome === 'Void' ? 'rs-sub' : ''));
      td(r.week6_result, 'rs-hide-narrow rs-results');
      const pc = Number(r.profit_c);
      td((pc > 0 ? '+' : '') + r.profit_c, 'num' + (pc > 0 ? ' rs-hi' : (pc < 0 ? ' rs-sub' : '')));
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
  }

  // ---------------- weeks 1-5 backtest ----------------
  const BT_DIMS = ['market', 'side', 'venue', 'price_band', 'week', 'liquidity'];
  const bt = { sortK: 'hit_pct', sortDir: -1, min: 5 };
  const BTNUM = new Set(['n', 'wins', 'losses', 'hit_pct', 'avg_price', 'edge_pts', 'roi_pct']);
  const btTable = $('#bt-perms-table');
  const btDims = [...document.querySelectorAll('.bt-dim')];
  btDims.forEach((el) => el.addEventListener('change', () => drawBtPerms()));
  $('.bt-min').addEventListener('input', () => { const v = parseInt($('.bt-min').value, 10); bt.min = Number.isFinite(v) ? v : 1; drawBtPerms(); });
  wireSort(btTable, bt, BTNUM, () => drawBtPerms());
  function drawBtPerms() {
    const d = dash.data('hist_perms');
    const tbody = $('tbody', btTable);
    const sel = BT_DIMS.filter((k) => btDims.find((el) => el.value === k).checked);
    BT_DIMS.forEach((k) => btTable.querySelectorAll('.bt-c-' + k).forEach((el) => { el.style.display = sel.includes(k) ? '' : 'none'; }));
    markSort(btTable, bt);
    if (d.status !== 'ok') { tbody.replaceChildren(); $('.bt-count').textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
    const grouping = sel.length ? sel.join('+') : 'all';
    const all = d.data.filter((r) => r.grouping === grouping);
    const v = all.filter((r) => Number(r.n) >= bt.min).sort(makeSorter(bt, BTNUM));
    $('.bt-count').textContent = `${fmt(v.length)} of ${fmt(all.length)} groups shown`;
    const frag = document.createDocumentFragment();
    for (const r of v) {
      const tr = document.createElement('tr'); tr.dataset.key = r.id;
      const td = mkTd(tr);
      BT_DIMS.forEach((k) => { const c = td(r[k] || 'All', 'bt-c-' + k); if (!sel.includes(k)) c.style.display = 'none'; });
      td(r.n, 'num'); td(r.wins, 'num rs-sub'); td(r.losses, 'num rs-sub');
      pctCell(tr, r.hit_pct);
      td(r.avg_price, 'num rs-sub');
      const e = Number(r.edge_pts);
      td((e > 0 ? '+' : '') + r.edge_pts, 'num' + (e > 0 ? ' rs-hi' : ''));
      td(signed(r.roi_pct), 'num' + (Number(r.roi_pct) > 0 ? ' rs-hi' : ' rs-sub'));
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
  }

  const bl = { market: '', week: '', outcome: '', q: '', sortK: 'week', sortDir: 1 };
  const BLNUM = new Set(['price_c', 'profit_c']);
  const blTable = $('#bt-lines-table');
  const blMarket = $('.bt-market'), blWeek = $('.bt-week'), blOut = $('.bt-outcome'), blSearch = $('.bt-search');
  blMarket.addEventListener('change', () => { bl.market = blMarket.value; drawBtLines(); });
  blWeek.addEventListener('change', () => { bl.week = blWeek.value; drawBtLines(); });
  blOut.addEventListener('change', () => { bl.outcome = blOut.value; drawBtLines(); });
  blSearch.addEventListener('input', () => { bl.q = blSearch.value.trim().toLowerCase(); drawBtLines(); });
  wireSort(blTable, bl, BLNUM, () => drawBtLines());
  function drawBtLines() {
    const d = dash.data('hist_lines');
    const tbody = $('tbody', blTable);
    markSort(blTable, bl);
    if (d.status !== 'ok') { tbody.replaceChildren(); $('.bt-lcount').textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
    const rows = d.data;
    if (blMarket.options.length === 1) {
      [...new Set(rows.map((r) => r.market))].sort().forEach((m) => blMarket.add(new Option(m, m)));
      [...new Set(rows.map((r) => r.week))].sort().forEach((w) => blWeek.add(new Option(w, w)));
    }
    const v = rows.filter((r) => (!bl.market || r.market === bl.market) && (!bl.week || r.week === bl.week) &&
      (!bl.outcome || r.outcome === bl.outcome) &&
      (!bl.q || (r.game + ' ' + r.contract + ' ' + r.market + ' ' + r.team).toLowerCase().includes(bl.q))).sort(makeSorter(bl, BLNUM));
    const w = v.filter((r) => r.outcome === 'Won').length, l = v.filter((r) => r.outcome === 'Lost').length;
    $('.bt-lcount').textContent = `${fmt(v.length)} lines · ${w}–${l}`;
    const frag = document.createDocumentFragment();
    for (const r of v) {
      const tr = document.createElement('tr'); tr.dataset.key = r.id;
      const td = mkTd(tr);
      td(r.week, 'rs-sub'); td(r.game, 'rs-sub'); td(r.market, 'rs-hide-narrow rs-sub');
      td(r.contract, 'rs-contract'); td(r.price_c, 'num');
      td(r.side, 'rs-hide-narrow rs-sub'); td(r.venue, 'rs-hide-narrow rs-sub'); td(r.liquidity, 'rs-hide-narrow rs-sub');
      td(r.outcome, r.outcome === 'Won' ? 'rs-hi' : '');
      td(r.final, 'rs-hide-narrow rs-results');
      const pc = Number(r.profit_c);
      td((pc > 0 ? '+' : '') + r.profit_c, 'num' + (pc > 0 ? ' rs-hi' : ' rs-sub'));
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
  }


  // ---------------- charts tab ----------------
  const DIM_ORDER = ['market', 'side', 'venue', 'price_band', 'week', 'liquidity'];
  const DIM_LABEL = { market: 'Market', side: 'Favorite / underdog', venue: 'Home / away', price_band: 'Price band', week: 'Week', liquidity: 'Liquidity' };
  const VALUE_ORDER = {
    side: ['Favorite', 'Underdog', "Pick'em", 'n/a'], venue: ['Home', 'Away', 'n/a'],
    price_band: ['45–48¢', '49–51¢', '52–55¢'], week: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
    liquidity: ['Under 1k contracts', '1k–50k contracts', '50k+ contracts'],
  };
  const showVal = (dim, v) => (v === 'n/a' ? (dim === 'side' || dim === 'venue' ? 'No side (totals)' : 'n/a') : v);
  const pct1 = (v) => (Number(v) % 1 ? Number(v).toFixed(1) : String(Number(v))) + '%';

  const tipOf = (box) => { let t = box.querySelector(':scope > .wg-tip'); if (!t) { t = document.createElement('div'); t.className = 'wg-tip'; box.appendChild(t); } return t; };
  const showTip = (box, ev, lines) => {
    const t = tipOf(box);
    t.replaceChildren(...lines.map((l, i) => { const d = document.createElement('div'); if (i === 0) d.className = 't'; d.textContent = l; return d; }));
    t.style.opacity = 1;
    const br = box.getBoundingClientRect();
    let x = ev.clientX - br.left + 14, y = ev.clientY - br.top + 14;
    if (x + t.offsetWidth > br.width) x = Math.max(0, ev.clientX - br.left - t.offsetWidth - 14);
    if (y + t.offsetHeight > br.height + 40) y = Math.max(0, ev.clientY - br.top - t.offsetHeight - 10);
    t.style.left = x + 'px'; t.style.top = y + 'px';
  };
  const hideTip = (box) => { const t = box.querySelector(':scope > .wg-tip'); if (t) t.style.opacity = 0; };
  const freshSvg = (box, W, H) => {
    const old = box.querySelector(':scope > svg'); if (old) old.remove();
    const svg = d3.create('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`).attr('height', H).attr('role', 'img');
    box.prepend(svg.node());
    return svg;
  };
  const measure = (svg, texts, size) => {
    const g = svg.append('g').attr('opacity', 0);
    let max = 0;
    for (const t of texts) { const el = g.append('text').style('font-size', size).text(t); max = Math.max(max, el.node().getComputedTextLength()); }
    g.remove();
    return max;
  };
  const fitText = (sel, full, maxw) => {
    if (sel.node().getComputedTextLength() <= maxw) return;
    let t = shortVal(full); sel.text(t);
    while (sel.node().getComputedTextLength() > maxw && t.length > 3) { t = t.slice(0, -1); sel.text(t.trimEnd() + '…'); }
  };
  const shortVal = (v) => String(v).replace(/^Week (\d)/, 'Wk $1').replace(' contracts', '').replace('No side (totals)', 'Totals').replace(/ \(hit >50%\)$/, '').replace('Hit >50% · ', '');
  const emptyNote = (box, msg) => { const old = box.querySelector(':scope > svg'); if (old) old.remove(); box.style.minHeight = '60px'; let p = box.querySelector(':scope > .wg-empty'); if (!p) { p = document.createElement('p'); p.className = 'rs-note wg-empty'; box.appendChild(p); } p.textContent = msg; };
  const clearEmpty = (box) => { const p = box.querySelector(':scope > .wg-empty'); if (p) p.remove(); };

  // horizontal hit-rate bars with a 50% line and an average-price tick
  function hbars(box, rows, o) {
    clearEmpty(box);
    const W = box.clientWidth; if (!W) return;
    if (!rows.length) { emptyNote(box, o.empty || 'No groups meet the minimum size.'); return; }
    const top = 20, bottom = 6, fs = 'var(--cds-font-size-caption)';
    let svg = freshSvg(box, W, 10);
    const bars = rows.filter((r) => !r.heading);
    let lw = Math.min(W * 0.46, measure(svg, bars.map((r) => r.label), fs) + 12);
    let rightW = Math.min(110, Math.max(70, measure(svg, bars.map((r) => r.right), fs) + 12));
    // narrow screens: label and value on one line, full-width bar underneath
    const stacked = W - lw - rightW < Math.max(160, W * 0.4);
    if (stacked) { lw = 0; rightW = 0; }
    const rowH = stacked ? 44 : (o.rowH || 26);
    const H = top + rows.length * rowH + bottom;
    svg = freshSvg(box, W, H);
    box.style.minHeight = H + 'px';
    const x = d3.scaleLinear([0, 100], [lw + (stacked ? 1 : 0), W - rightW - (stacked ? 1 : 0)]);
    const grid = svg.append('g');
    for (const t of (stacked ? [0, 50, 100] : [0, 25, 50, 75, 100])) {
      grid.append('line').attr('x1', x(t)).attr('x2', x(t)).attr('y1', top - 4).attr('y2', H - bottom)
        .style('stroke', t === 50 ? 'var(--cds-chart-reference)' : 'var(--cds-chart-grid)').attr('stroke-width', 1)
        .attr('stroke-dasharray', t === 50 ? '4 3' : null);
      grid.append('text').attr('x', x(t)).attr('y', top - 8).attr('text-anchor', stacked ? (t === 0 ? 'start' : t === 100 ? 'end' : 'middle') : 'middle')
        .style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(t + '%');
    }
    rows.forEach((r, i) => {
      const y = top + i * rowH;
      const bh = stacked ? 12 : Math.min(16, rowH - 10), cy = stacked ? y + rowH - bh / 2 - 5 : y + rowH / 2, ty = stacked ? y + 12 : cy;
      if (r.heading) {
        svg.append('text').attr('x', 0).attr('y', y + rowH - 7).style('font-size', '10px').style('letter-spacing', '.08em').style('font-weight', 600).style('fill', 'var(--color-fg-muted)').text(r.heading.toUpperCase());
        return;
      }
      const g = svg.append('g');
      const valT = g.append('text').attr('x', stacked ? W : W - rightW + 8).attr('y', ty).attr('dy', '0.35em').attr('text-anchor', stacked ? 'end' : 'start')
        .style('font-size', fs).style('fill', 'var(--color-fg-muted)').style('font-variant-numeric', 'tabular-nums').text(r.right);
      const lab = g.append('text').attr('x', stacked ? 0 : lw - 10).attr('y', ty).attr('dy', '0.35em').attr('text-anchor', stacked ? 'start' : 'end').style('font-size', fs).style('fill', 'var(--color-fg)').text(r.label);
      fitText(lab, r.label, stacked ? W - valT.node().getComputedTextLength() - 18 : lw - 12);
      g.append('rect').attr('x', x(0)).attr('y', cy - bh / 2).attr('width', Math.max(1, x(r.value) - x(0))).attr('height', bh).attr('rx', 3)
        .style('fill', r.good ? 'var(--wg-green)' : 'var(--cds-chart-muted)');
      if (r.price != null) g.append('line').attr('x1', x(r.price)).attr('x2', x(r.price)).attr('y1', cy - bh / 2 - 3).attr('y2', cy + bh / 2 + 3).style('stroke', 'var(--color-fg)').attr('stroke-width', 2).attr('stroke-linecap', 'round');
      g.append('rect').attr('x', 0).attr('y', y).attr('width', W).attr('height', rowH).style('fill', 'transparent')
        .on('mousemove', (ev) => { g.select('rect').style('opacity', 0.8); showTip(box, ev, r.tip); })
        .on('mouseleave', () => { g.select('rect').style('opacity', 1); hideTip(box); });
    });
  }

  const permRow = (r, label) => ({
    label, value: Number(r.hit_pct), price: Number(r.avg_price), good: Number(r.hit_pct) > Number(r.avg_price),
    right: `${pct1(r.hit_pct)} · ${r.wins}–${r.losses}`,
    tip: [label, `Hit ${pct1(r.hit_pct)} (${r.wins}–${r.losses})`, `Avg price ${r.avg_price}¢ · edge ${Number(r.edge_pts) > 0 ? '+' : ''}${r.edge_pts} pts`, `Return ${signed(r.roi_pct)}`],
  });
  const valueRank = (dim, v, rowsForDim) => {
    if (VALUE_ORDER[dim]) { const i = VALUE_ORDER[dim].indexOf(v); return i < 0 ? 99 : i; }
    const r = rowsForDim.find((x) => x[dim] === v); return r ? -Number(r.n) : 0;
  };

  function drawFactorCharts(perms) {
    document.querySelectorAll('#ch-factor-grid .wg-chart').forEach((box) => {
      const dim = box.dataset.dim;
      const rows = perms.filter((r) => r.grouping === dim).sort((a, b) => valueRank(dim, a[dim], perms.filter((x) => x.grouping === dim)) - valueRank(dim, b[dim], perms.filter((x) => x.grouping === dim)));
      hbars(box, rows.map((r) => permRow(r, showVal(dim, r[dim]))), { rowH: 28 });
    });
  }

  const chc = { min: 8 };
  const chcDims = [...document.querySelectorAll('.chc-dim')];
  chcDims.forEach((el) => el.addEventListener('change', () => drawCharts()));
  $('.chc-min').addEventListener('input', () => { const v = parseInt($('.chc-min').value, 10); chc.min = Number.isFinite(v) ? v : 1; drawCharts(); });
  function drawComboChart(perms) {
    const box = $('#ch-combo-chart');
    const sel = DIM_ORDER.filter((k) => chcDims.find((el) => el.value === k).checked);
    const grouping = sel.length ? sel.join('+') : 'all';
    const all = perms.filter((r) => r.grouping === grouping);
    const rows = all.filter((r) => Number(r.n) >= chc.min).sort((a, b) => Number(b.hit_pct) - Number(a.hit_pct) || Number(b.n) - Number(a.n));
    $('.chc-count').textContent = `${fmt(rows.length)} of ${fmt(all.length)} groups`;
    hbars(box, rows.map((r) => permRow(r, sel.length ? sel.map((k) => showVal(k, r[k])).join(' · ') : 'All lines')), { rowH: 26, empty: 'No combination has that many lines; lower the minimum.' });
  }

  const chh = { row: 'market', col: 'week', min: 5 };
  const chhRow = $('.chh-row'), chhCol = $('.chh-col');
  for (const sel of [chhRow, chhCol]) DIM_ORDER.forEach((k) => sel.add(new Option(DIM_LABEL[k], k)));
  chhRow.value = chh.row; chhCol.value = chh.col;
  chhRow.addEventListener('change', () => { chh.row = chhRow.value; if (chh.row === chh.col) { chh.col = DIM_ORDER.find((k) => k !== chh.row); chhCol.value = chh.col; } drawCharts(); });
  chhCol.addEventListener('change', () => { chh.col = chhCol.value; if (chh.row === chh.col) { chh.row = DIM_ORDER.find((k) => k !== chh.col); chhRow.value = chh.row; } drawCharts(); });
  $('.chh-min').addEventListener('input', () => { const v = parseInt($('.chh-min').value, 10); chh.min = Number.isFinite(v) ? v : 1; drawCharts(); });
  function drawHeatmap(perms) {
    const box = $('#ch-heat-chart'); clearEmpty(box);
    const W = box.clientWidth; if (!W) return;
    const [d1, d2] = [chh.row, chh.col];
    const grouping = DIM_ORDER.filter((k) => k === d1 || k === d2).join('+');
    const cells = perms.filter((r) => r.grouping === grouping);
    const single = (dim) => perms.filter((r) => r.grouping === dim);
    const vals = (dim) => [...new Set(single(dim).map((r) => r[dim]))].sort((a, b) => valueRank(dim, a, single(dim)) - valueRank(dim, b, single(dim)));
    const rv = vals(d1), cv = vals(d2);
    const fs = 'var(--cds-font-size-caption)';
    let svg = freshSvg(box, W, 10);
    const lw = Math.min(W * 0.32, measure(svg, rv.map((v) => showVal(d1, v)), fs) + 14);
    const top = 34, cellH = 44;
    const cw = (W - lw) / Math.max(1, cv.length);
    const H = top + rv.length * cellH + 4;
    svg = freshSvg(box, W, H); box.style.minHeight = H + 'px';
    cv.forEach((c, j) => {
      const lab = showVal(d2, c);
      const t = svg.append('text').attr('x', lw + cw * j + cw / 2).attr('y', top - 12).attr('text-anchor', 'middle').style('font-size', fs).style('fill', 'var(--color-fg-muted)').text(lab);
      fitText(t, lab, cw - 6);
    });
    rv.forEach((rvv, i) => {
      const rl = svg.append('text').attr('x', lw - 10).attr('y', top + i * cellH + cellH / 2).attr('dy', '0.35em').attr('text-anchor', 'end').style('font-size', fs).style('fill', 'var(--color-fg)').text(showVal(d1, rvv));
      fitText(rl, showVal(d1, rvv), lw - 12);
      cv.forEach((cvv, j) => {
        const r = cells.find((x) => x[d1] === rvv && x[d2] === cvv);
        const x0 = lw + cw * j + 2, y0 = top + i * cellH + 2, w = cw - 4, h = cellH - 4;
        const g = svg.append('g');
        let fill = 'var(--cds-chart-grid)';
        const ok = r && Number(r.n) >= chh.min;
        if (ok) {
          const hp = Number(r.hit_pct), t = Math.max(-1, Math.min(1, (hp - 50) / 30));
          fill = t >= 0 ? `color-mix(in srgb, var(--wg-green) ${Math.round(t * 80) + 10}%, var(--color-bg))` : `color-mix(in srgb, var(--cds-chart-status-critical) ${Math.round(-t * 65) + 10}%, var(--color-bg))`;
        }
        g.append('rect').attr('x', x0).attr('y', y0).attr('width', w).attr('height', h).attr('rx', 4).style('fill', fill);
        if (r) {
          g.append('text').attr('x', x0 + w / 2).attr('y', y0 + h / 2 - 3).attr('text-anchor', 'middle').style('font-size', fs).style('font-weight', ok ? 600 : 400).style('fill', ok ? 'var(--color-fg)' : 'var(--color-fg-muted)').text(ok ? pct1(r.hit_pct) : '—');
          g.append('text').attr('x', x0 + w / 2).attr('y', y0 + h / 2 + 11).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(`${r.wins}–${r.losses}`);
          g.on('mousemove', (ev) => showTip(box, ev, [`${showVal(d1, rvv)} · ${showVal(d2, cvv)}`, `Hit ${pct1(r.hit_pct)} (${r.wins}–${r.losses})`, `Avg price ${r.avg_price}¢ · edge ${Number(r.edge_pts) > 0 ? '+' : ''}${r.edge_pts} pts`, `Return ${signed(r.roi_pct)}`]))
            .on('mouseleave', () => hideTip(box));
        }
      });
    });
  }

  function drawW6Chart() {
    const box = $('#ch-w6-chart');
    const d = dash.data('w6_summary');
    if (d.status !== 'ok') { const s = box.querySelector(':scope > svg'); if (s) s.remove(); return; }
    const SECT = { screen: 'The screen', full: 'Hit >50%, by market', b50: 'All 45–55¢ lines, by 2026 hit rate', cat1: 'Your four prop groups', atd: 'Anytime TD' };
    const rows = d.data.filter((r) => r.win_pct != null).flatMap((r) => [...(SECT[r.segment] ? [{ heading: SECT[r.segment] }] : []), {
      label: r.label, value: Number(r.win_pct), price: Number(r.avg_price), good: Number(r.roi_pct) > 0,
      right: `${pct1(r.win_pct)} · ${r.wins}–${r.losses}`,
      tip: [r.label, `Won ${pct1(r.win_pct)} (${r.wins}–${r.losses})`, `Avg price ${r.avg_price}¢`, `Return ${signed(r.roi_pct)}`],
    }]);
    hbars(box, rows, { rowH: 26 });
  }

  const BOARD_GROUPS = ['Full game', 'Quarters & halves', 'Player props'];
  function drawBoard() {
    const box = $('#ch-board-chart'); clearEmpty(box);
    const W = box.clientWidth; if (!W) return;
    const d = dash.data('lines');
    if (d.status !== 'ok') { const s = box.querySelector(':scope > svg'); if (s) s.remove(); return; }
    const color = (g) => wgColors()[BOARD_GROUPS.indexOf(g) % wgColors().length];
    const key = $('.ch-board-key');
    key.replaceChildren(...BOARD_GROUPS.map((g) => { const s = document.createElement('span'); const i = document.createElement('i'); i.style.background = color(g); s.append(i, g); return s; }),
      (() => { const s = document.createElement('span'); const i = document.createElement('i'); i.className = 'line'; s.append(i, 'Break-even (hit rate = price)'); return s; })());
    const pts = d.data.filter((r) => r.hit_rate !== '' && r.hit_rate != null);
    const H = Math.min(420, Math.max(300, W * 0.5)), m = { t: 12, r: 16, b: 38, l: 52 };
    const svg = freshSvg(box, W, H); box.style.minHeight = H + 'px';
    const x = d3.scaleLinear([44.5, 55.5], [m.l, W - m.r]), y = d3.scaleLinear([0, 100], [H - m.b, m.t]);
    for (const t of [0, 25, 50, 75, 100]) {
      svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(t)).attr('y2', y(t)).style('stroke', 'var(--cds-chart-grid)');
      svg.append('text').attr('x', m.l - 8).attr('y', y(t)).attr('dy', '0.35em').attr('text-anchor', 'end').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(t + '%');
    }
    for (let t = 45; t <= 55; t += (W < 500 ? 2 : 1)) svg.append('text').attr('x', x(t)).attr('y', H - m.b + 16).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(t + '¢');
    svg.append('text').attr('x', (m.l + W - m.r) / 2).attr('y', H - 4).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text('Yes price');
    svg.append('text').attr('transform', `translate(10,${(m.t + H - m.b) / 2}) rotate(-90)`).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text('2026 hit rate');
    svg.append('line').attr('x1', x(44.5)).attr('x2', x(55.5)).attr('y1', y(44.5)).attr('y2', y(55.5)).style('stroke', 'var(--cds-chart-reference)').attr('stroke-dasharray', '4 3');
    const jitter = (s) => { let h = 0; for (const c of s) h = (h * 31 + c.charCodeAt(0)) >>> 0; return ((h % 1000) / 1000 - 0.5) * 0.6; };
    for (const r of pts) {
      const cx = x(Number(r.yes_price) + jitter(r.id)), cy = y(Number(r.hit_rate));
      svg.append('circle').attr('cx', cx).attr('cy', cy).attr('r', 4.5).style('fill', color(groupOf(r.market))).style('fill-opacity', r.qualifies === 'Yes' ? 0.9 : 0.35)
        .style('stroke', 'var(--color-bg)').attr('stroke-width', 1)
        .on('mousemove', (ev) => showTip(box, ev, [r.game + ' · ' + r.market, r.contract, `Price ${r.yes_price}¢ · hit ${pct1(r.hit_rate)} (${r.hits}/${r.games})`]))
        .on('mouseleave', () => hideTip(box));
    }
  }

  // ---------------- week-by-week backtest, props heat table, momentum, teams ----------------
  const chw = { grp: 'Strategy' };
  $('.chw-grp').addEventListener('change', (e) => { chw.grp = e.target.value; drawCharts(); });
  const noSvg = (box) => { const sv = box.querySelector(':scope > svg'); if (sv) sv.remove(); };
  const axTxt = (svg, x, y, t, anchor) => svg.append('text').attr('x', x).attr('y', y).attr('text-anchor', anchor || 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(t);
  const sgn1 = (v, d = 1) => (Number(v) > 0 ? '+' : Number(v) < 0 ? '−' : '±') + Math.abs(Number(v)).toFixed(d);
  function drawWeeks() {
    const box = $('#ch-weeks-chart'); clearEmpty(box);
    const W = box.clientWidth; if (!W) return;
    const d = dash.data('bt_weeks');
    if (d.status !== 'ok') { noSvg(box); return; }
    const rows = d.data.filter((r) => r.seg_group === chw.grp && String(r.week) !== 'all');
    const segs = [...new Set(rows.map((r) => r.segment))].sort((a, b) => /Wedge/.test(b) - /Wedge/.test(a));
    const col = (sg) => wgColors()[segs.indexOf(sg) % wgColors().length];
    keyRow($('.chw-key'), [...segs.map((sg) => [sg, col(sg), 0]), ['50%', null, 'line']]);
    if (!rows.length) { emptyNote(box, 'No weeks for this group.'); return; }
    const H = Math.min(380, Math.max(260, W * 0.46)), m = { t: 12, r: 14, b: 34, l: 40 };
    const svg = freshSvg(box, W, H); box.style.minHeight = H + 'px';
    const weeks = [...new Set(rows.map((r) => String(r.week)))].sort((a, b) => a - b);
    const x = d3.scalePoint(weeks, [m.l, W - m.r]).padding(0.35);
    const lo = Math.max(0, Math.min(20, d3.min(rows, (r) => +r.win_pct) - 5)), hi = Math.min(100, Math.max(80, d3.max(rows, (r) => +r.win_pct) + 5));
    const y = d3.scaleLinear([lo, hi], [H - m.b, m.t]);
    for (const t of y.ticks(5)) {
      svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(t)).attr('y2', y(t)).style('stroke', 'var(--cds-chart-grid)');
      axTxt(svg, m.l - 6, y(t) + 3, t + '%', 'end');
    }
    svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(50)).attr('y2', y(50)).style('stroke', 'var(--cds-chart-reference)').attr('stroke-dasharray', '4 3');
    weeks.forEach((w) => axTxt(svg, x(w), H - m.b + 16, (W < 420 ? 'W' : 'Wk ') + w));
    axTxt(svg, (m.l + W - m.r) / 2, H - 3, 'Week of 2026');
    const maxN = d3.max(rows, (r) => +r.n) || 1;
    const rad = (n) => 2.5 + 5 * Math.sqrt(+n / maxN);
    for (const sg of segs) {
      const pts = weeks.map((w) => rows.find((r) => r.segment === sg && String(r.week) === w) || null);
      const line = d3.line().defined((p) => p).x((p, i) => x(weeks[i])).y((p) => y(+p.win_pct));
      svg.append('path').attr('d', line(pts)).style('fill', 'none').style('stroke', col(sg)).attr('stroke-width', 2).attr('stroke-linejoin', 'round');
      pts.forEach((p, i) => {
        if (!p) return;
        svg.append('circle').attr('cx', x(weeks[i])).attr('cy', y(+p.win_pct)).attr('r', rad(p.n)).style('fill', col(sg)).style('stroke', 'var(--color-bg)').attr('stroke-width', 1.5)
          .on('mousemove', (ev) => showTip(box, ev, [`${sg} · Week ${p.week}`, `Won ${pct1(p.win_pct)} (${p.wins}–${p.losses})`, `Avg price ${p.avg_price}¢ · return ${signed(p.roi_pct)}`]))
          .on('mouseleave', () => hideTip(box));
      });
    }
    // all weeks together
    const all = d.data.filter((r) => r.seg_group === chw.grp && String(r.week) === 'all');
    hbars($('#ch-weeks-all'), all.map((r) => ({
      label: r.segment, value: +r.win_pct, price: +r.avg_price, good: +r.roi_pct > 0, right: `${pct1(r.win_pct)} · ${r.wins}–${r.losses}`,
      tip: [`${r.segment} · Weeks 1–8`, `Won ${pct1(r.win_pct)} (${r.wins}–${r.losses})`, `Avg price ${r.avg_price}¢`, `Return ${signed(r.roi_pct)}`],
    })), { rowH: 26 });
  }

  const chp = { fac: 'Stat' };
  $('.chp-fac').addEventListener('change', (e) => { chp.fac = e.target.value; drawCharts(); });
  const PERIODS = ['Wk 1', 'Wk 2', 'Wk 3', 'Wk 4', 'Wk 5', 'Wk 6', 'Wk 7', 'Wk 8', '2023–25'];
  const LEVEL_ORDER = { Momentum: ['Early season', 'Role up', 'Volume up', 'Stable', 'Hot efficiency', 'Cold efficiency', 'Volume down', 'Role down'], 'Team total': ['Implied under 20.5', 'Implied 20.5–24', 'Implied 24.5+'], Position: ['QB', 'RB', 'WR', 'TE'] };
  function drawPropsHeat() {
    const box = $('#ch-props-chart'); clearEmpty(box);
    const W = box.clientWidth; if (!W) return;
    const d = dash.data('bt_props');
    if (d.status !== 'ok') { noSvg(box); return; }
    const rows = d.data.filter((r) => r.factor === chp.fac);
    const ord = LEVEL_ORDER[chp.fac];
    const nAll = (lv) => -(+((rows.find((r) => r.level === lv && r.period === '2023–25') || {}).n || 0));
    const levels = [...new Set(rows.map((r) => r.level))].sort((a, b) => (ord ? ord.indexOf(a) - ord.indexOf(b) : nAll(a) - nAll(b)));
    const R = ['All props', ...levels];
    const cellOf = (lv, per) => (lv === 'All props' ? d.data.find((r) => r.factor === 'All' && r.period === per) : rows.find((r) => r.level === lv && r.period === per));
    const fs = 'var(--cds-font-size-caption)';
    let svg = freshSvg(box, W, 10);
    const lw = Math.min(W * 0.3, measure(svg, R, fs) + 12);
    const cw = (W - lw) / PERIODS.length, narrow = cw < 46, top = 30, cellH = narrow ? 34 : 40;
    const H = top + R.length * cellH + 4;
    svg = freshSvg(box, W, H); box.style.minHeight = H + 'px';
    PERIODS.forEach((p, j) => { const t = axTxt(svg, lw + cw * j + cw / 2, top - 10, narrow ? p.replace('Wk ', '').replace('2023–25', "'23–25") : p); t.style('font-size', fs); });
    R.forEach((lv, i) => {
      const lab = svg.append('text').attr('x', lw - 8).attr('y', top + i * cellH + cellH / 2).attr('dy', '0.35em').attr('text-anchor', 'end').style('font-size', fs).style('fill', 'var(--color-fg)').style('font-weight', lv === 'All props' ? 600 : 400).text(lv);
      fitText(lab, lv, lw - 10);
      PERIODS.forEach((per, j) => {
        const r = cellOf(lv, per);
        const x0 = lw + cw * j + 2, y0 = top + i * cellH + 2, w = cw - 4, h = cellH - 4;
        const g = svg.append('g');
        let fill = 'var(--cds-chart-grid)';
        const ok = r && +r.n >= 15;
        if (ok && lv !== 'All props') {
          const t = Math.max(-1, Math.min(1, +r.diff / 8));
          fill = t >= 0 ? `color-mix(in srgb, var(--wg-green) ${Math.round(t * 75) + 8}%, var(--color-bg))` : `color-mix(in srgb, var(--cds-chart-status-critical) ${Math.round(-t * 60) + 8}%, var(--color-bg))`;
        }
        g.append('rect').attr('x', x0).attr('y', y0).attr('width', w).attr('height', h).attr('rx', 4).style('fill', fill);
        if (!r) return;
        g.append('text').attr('x', x0 + w / 2).attr('y', y0 + h / 2 - (narrow ? 0 : 4)).attr('dy', narrow ? '0.35em' : null).attr('text-anchor', 'middle').style('font-size', narrow ? '10px' : fs).style('font-weight', ok ? 600 : 400)
          .style('fill', ok ? 'var(--color-fg)' : 'var(--color-fg-muted)').text(ok ? (narrow ? Math.round(+r.over_pct) : pct1(r.over_pct)) : '—');
        if (!narrow) g.append('text').attr('x', x0 + w / 2).attr('y', y0 + h / 2 + 10).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(lv === 'All props' ? 'n ' + fmt(+r.n) : sgn1(r.diff));
        g.on('mousemove', (ev) => showTip(box, ev, [`${lv} · ${per === '2023–25' ? '2023–25 seasons' : per.replace('Wk', 'Week')}`, `Over cleared the book-style line ${pct1(r.over_pct)} of ${fmt(+r.n)}`, lv === 'All props' ? 'Average for every prop that week' : `${sgn1(r.diff)} pts vs all props that week`]))
          .on('mouseleave', () => hideTip(box));
      });
    });
  }

  // diverging bars around a base value (0 or 100)
  function divbars(box, rows, o) {
    clearEmpty(box);
    const W = box.clientWidth; if (!W) return;
    if (!rows.length) { emptyNote(box, 'No data.'); return; }
    const fs = 'var(--cds-font-size-caption)', top = 20, bottom = 4;
    let svg = freshSvg(box, W, 10);
    const bars = rows.filter((r) => !r.heading);
    let lw = Math.min(W * 0.42, measure(svg, bars.map((r) => r.label), fs) + 12);
    let rightW = Math.min(120, measure(svg, bars.map((r) => r.right), fs) + 12);
    const stacked = W - lw - rightW < 150; if (stacked) { lw = 0; rightW = 0; }
    const rowH = stacked ? 40 : 24, H = top + rows.length * rowH + bottom;
    svg = freshSvg(box, W, H); box.style.minHeight = H + 'px';
    const x = d3.scaleLinear(o.domain, [lw + 1, W - rightW - 1]).clamp(true);
    for (const t of o.ticks) {
      svg.append('line').attr('x1', x(t)).attr('x2', x(t)).attr('y1', top - 4).attr('y2', H - bottom).style('stroke', t === o.base ? 'var(--cds-chart-reference)' : 'var(--cds-chart-grid)').attr('stroke-dasharray', t === o.base ? '4 3' : null);
      axTxt(svg, x(t), top - 8, o.fmt(t));
    }
    rows.forEach((r, i) => {
      const yy = top + i * rowH;
      if (r.heading) { svg.append('text').attr('x', 0).attr('y', yy + rowH - 6).style('font-size', '10px').style('letter-spacing', '.08em').style('font-weight', 600).style('fill', 'var(--color-fg-muted)').text(r.heading.toUpperCase()); return; }
      const bh = stacked ? 10 : 12, cy = stacked ? yy + rowH - bh / 2 - 5 : yy + rowH / 2, ty = stacked ? yy + 11 : cy;
      const g = svg.append('g');
      const vt = g.append('text').attr('x', stacked ? W : W - rightW + 8).attr('y', ty).attr('dy', '0.35em').attr('text-anchor', stacked ? 'end' : 'start').style('font-size', fs).style('fill', 'var(--color-fg-muted)').style('font-variant-numeric', 'tabular-nums').text(r.right);
      const lab = g.append('text').attr('x', stacked ? 0 : lw - 10).attr('y', ty).attr('dy', '0.35em').attr('text-anchor', stacked ? 'start' : 'end').style('font-size', fs).style('fill', 'var(--color-fg)').text(r.label);
      fitText(lab, r.label, stacked ? W - vt.node().getComputedTextLength() - 16 : lw - 12);
      const a = x(Math.min(o.base, r.value)), b = x(Math.max(o.base, r.value));
      g.append('rect').attr('x', a).attr('y', cy - bh / 2).attr('width', Math.max(1.5, b - a)).attr('height', bh).attr('rx', 3)
        .style('fill', r.good ? 'var(--wg-green)' : r.bad ? 'var(--cds-chart-status-critical)' : 'var(--cds-chart-muted)');
      g.append('rect').attr('x', 0).attr('y', yy).attr('width', W).attr('height', rowH).style('fill', 'transparent')
        .on('mousemove', (ev) => showTip(box, ev, r.tip)).on('mouseleave', () => hideTip(box));
    });
  }

  const chm = { stat: 'recyd' };
  $('.chm-stat').addEventListener('change', (e) => { chm.stat = e.target.value; drawCharts(); });
  const REAL_ORDER = ['all', 'L4 within 15%', 'L4 above season by 15%+', 'L4 below season by 15%+', 'volume up 15%+', 'volume down 15%+', 'efficiency up, volume flat', 'efficiency down, volume flat', 'snap share up 10+'];
  const REAL_LAB = { all: 'All modeled props', 'L4 within 15%': 'Last 4 within 15% of season', 'L4 above season by 15%+': 'Last 4 above season by 15%+', 'L4 below season by 15%+': 'Last 4 below season by 15%+', 'volume up 15%+': 'Volume up 15%+', 'volume down 15%+': 'Volume down 15%+', 'efficiency up, volume flat': 'Efficiency up, volume flat', 'efficiency down, volume flat': 'Efficiency down, volume flat', 'snap share up 10+': 'Snap share up 10+' };
  function drawMom() {
    const d = dash.data('mom_summary');
    const boxes = ['#ch-mom-persist', '#ch-mom-acc', '#ch-mom-cat', '#ch-mom-real'].map((q) => $(q));
    if (d.status !== 'ok') { boxes.forEach(noSvg); return; }
    const S = (sec) => d.data.filter((r) => r.section === sec);
    // 1. persistence
    const P = [{ heading: 'After a role change (snaps ±10)' }, ...S('persist_role').filter((r) => !/^td/.test(r.key)).map((r) => ({ label: r.label, value: +r.value, good: +r.value >= 25, right: r.value + '%', tip: [`${r.label} · role changed`, `${r.value}% of the last-4 gap showed up next game`, `${fmt(+r.n)} player-games, 2023–25`] })),
      { heading: 'Role unchanged' }, ...S('persist_role').filter((r) => !/^td/.test(r.key)).map((r) => ({ label: r.label, value: +r.value2, good: +r.value2 >= 25, right: r.value2 + '%', tip: [`${r.label} · stable role`, `${r.value2}% of the last-4 gap showed up next game`] })),
      { heading: 'Volume run vs efficiency run' }, ...S('persist_ve').flatMap((r) => [
        { label: `${r.label} · volume`, value: +r.value, good: +r.value >= 25, right: r.value + '%', tip: [`${r.label}: targets / carries / attempts`, `${r.value}% of a volume run carried over`] },
        { label: `${r.label} · per touch`, value: +r.value2, good: +r.value2 >= 25, bad: +r.value2 < 0, right: r.value2 + '%', tip: [`${r.label}: yards per target / carry / attempt`, `${r.value2}% of an efficiency run carried over`] }])];
    divbars(boxes[0], P, { base: 0, domain: [-20, 80], ticks: [-20, 0, 20, 40, 60, 80], fmt: (t) => t + '%' });
    // 2. accuracy
    const A = S('accuracy').slice().sort((a, b) => +a.value - +b.value).map((r) => ({ label: r.label, value: +r.value, good: +r.value < 99.95, bad: +r.value > 100.05, right: (+r.value).toFixed(1),
      tip: [r.label, `Average miss ${(+r.value).toFixed(1)}% of the season average’s`, r.note || `${fmt(+r.n)} player-games, 2023–26`] }));
    divbars(boxes[1], A, { base: 100, domain: [94, 112], ticks: [94, 100, 106, 112], fmt: (t) => String(t) });
    // 3. momentum type vs a book-style line
    const C = S('hist_cat').filter((r) => r.key.startsWith(chm.stat + '|')).map((r) => ({ label: r.label.replace(' (snaps +10)', ' (snaps +10)'), value: +r.value, good: +r.value >= 2, bad: +r.value <= -2,
      right: `${sgn1(r.value)} · ${fmt(+r.n)}`, tip: [`${r.note} · ${r.label}`, `Over cleared the line ${pct1(r.value2)} of ${fmt(+r.n)}`, `${sgn1(r.value)} pts vs his stat’s average, 2023–26`] }));
    divbars(boxes[2], C, { base: 0, domain: [-16, 10], ticks: [-15, -10, -5, 0, 5, 10], fmt: (t) => (t > 0 ? '+' : '') + t });
    // 4. real prices
    const RC = S('real_cat').filter((r) => REAL_ORDER.includes(r.key)).sort((a, b) => REAL_ORDER.indexOf(a.key) - REAL_ORDER.indexOf(b.key));
    hbars(boxes[3], RC.map((r) => ({ label: REAL_LAB[r.key] || r.label, value: +r.value, price: +r.value2, good: +r.value > +r.value2, right: `${pct1(r.value)} · ${fmt(+r.n)}`,
      tip: [REAL_LAB[r.key] || r.label, `Came true ${pct1(r.value)} of ${fmt(+r.n)}`, `Avg price ${r.value2}¢ · ${r.note.replace('edge ', '')} pts vs price`] })), { rowH: 26 });
    // variants + books' weights, as text
    const V = S('variants'), Wt = S('weights');
    const best = (st) => Wt.find((r) => r.key === st + '|best'), bk = (st) => Wt.find((r) => r.key === st + '|books');
    const wtxt = (r) => r.value.split('|').map((x) => Math.round(100 * x)).join(' / ');
    const vp = $('#ch-mom-var');
    if (V.length && Wt.length) vp.textContent = `Model variants on real prices, fit on one week and tested on the other (Brier score, lower is better; Week 7, then Week 6): ${V.map((r) => `${r.label} ${(+r.value).toFixed(4)} / ${(+r.value2).toFixed(4)}`).join(' · ')}. Books’ Week 6–7 lines weighed receiving yards ${wtxt(bk('recyd'))} (season / last 4 / multi-season, R² ${bk('recyd').value2}); the weights that best predicted 2023–24 games were ${wtxt(best('recyd'))}. For receptions books used ${wtxt(bk('rec'))} vs best ${wtxt(best('rec'))}; rushing yards ${wtxt(bk('rushyd'))} vs ${wtxt(best('rushyd'))}.`;
  }

  function drawTeams() {
    const box = $('#ch-teams-chart'); clearEmpty(box);
    const W = box.clientWidth; if (!W) return;
    const d = dash.data('team_mom');
    if (d.status !== 'ok') { noSvg(box); return; }
    const rows = d.data.slice().sort((a, b) => +b.change - +a.change);
    const fs = 'var(--cds-font-size-caption)', top = 24, rowH = 22, bottom = 6;
    let svg = freshSvg(box, W, 10);
    const lw = Math.min(W * 0.36, measure(svg, rows.map((r) => `${r.team}  ${r.week8}`), fs) + 14);
    const rightW = W < 480 ? 42 : 56;
    const H = top + rows.length * rowH + bottom;
    svg = freshSvg(box, W, H); box.style.minHeight = H + 'px';
    const ext = d3.extent(rows.flatMap((r) => [+r.epa_first4, +r.epa_last4]));
    const x = d3.scaleLinear([Math.min(-0.05, ext[0]) - 0.02, Math.max(0.05, ext[1]) + 0.02], [lw, W - rightW]).nice();
    for (const t of x.ticks(W < 480 ? 4 : 6)) {
      svg.append('line').attr('x1', x(t)).attr('x2', x(t)).attr('y1', top - 4).attr('y2', H - bottom).style('stroke', Math.abs(t) < 1e-9 ? 'var(--cds-chart-reference)' : 'var(--cds-chart-grid)').attr('stroke-dasharray', Math.abs(t) < 1e-9 ? '4 3' : null);
      axTxt(svg, x(t), top - 9, (t > 0 ? '+' : t < 0 ? '−' : '') + Math.abs(t).toFixed(2));
    }
    rows.forEach((r, i) => {
      const cy = top + i * rowH + rowH / 2, a = +r.epa_first4, b = +r.epa_last4, up = b >= a;
      const g = svg.append('g');
      const lab = g.append('text').attr('x', lw - 10).attr('y', cy).attr('dy', '0.35em').attr('text-anchor', 'end').style('font-size', fs);
      lab.append('tspan').style('font-weight', 600).style('fill', 'var(--color-fg)').text(r.team);
      lab.append('tspan').style('fill', 'var(--color-fg-muted)').text('  ' + r.week8);
      const c = up ? 'var(--wg-green)' : 'var(--cds-chart-status-critical)';
      g.append('line').attr('x1', x(a)).attr('x2', x(b)).attr('y1', cy).attr('y2', cy).style('stroke', c).attr('stroke-width', 2.5).style('opacity', 0.75);
      g.append('circle').attr('cx', x(a)).attr('cy', cy).attr('r', 4.5).style('fill', 'var(--color-bg)').style('stroke', 'var(--color-fg-muted)').attr('stroke-width', 1.5);
      g.append('circle').attr('cx', x(b)).attr('cy', cy).attr('r', 4.5).style('fill', c);
      g.append('text').attr('x', W - rightW + 8).attr('y', cy).attr('dy', '0.35em').style('font-size', fs).style('fill', 'var(--color-fg-muted)').style('font-variant-numeric', 'tabular-nums').text(sgn1(r.change, 2));
      const qb = r.qbs_last4 !== r.qbs_first4 ? `${r.qbs_first4} → ${r.qbs_last4}` : r.qbs_first4;
      const oe = +r.opp_easier_last4;
      g.append('rect').attr('x', 0).attr('y', cy - rowH / 2).attr('width', W).attr('height', rowH).style('fill', 'transparent')
        .on('mousemove', (ev) => showTip(box, ev, [`${r.team} · Week 8 ${r.week8 === 'Bye' ? 'bye' : r.week8}`, `EPA/play (opponent-adjusted) ${sgn1(a, 3)} → ${sgn1(b, 3)}`, `Points per game ${r.pts_first4} → ${r.pts_last4}`, `Success rate ${r.sr_first4}% → ${r.sr_last4}%`, `QB ${qb}`, `Last-4 defenses ${oe > 0 ? 'easier' : 'tougher'} by ${Math.abs(oe).toFixed(2)} EPA/play`]))
        .on('mouseleave', () => hideTip(box));
    });
  }

  // ---------------- role / script / scheme categories ----------------
  const cts = { kind: 'over', pos: '', stat: '', q: '', sortK: 'over_season', sortDir: -1 };
  const CTNUM = new Set(['over_season', 'n_season', 'over_w47', 'over_hist', 'base_hist']);
  const catsTable = $('#cats-table');
  $('.ct-kind').addEventListener('change', (e) => { cts.kind = e.target.value; cts.sortDir = cts.kind === 'under' ? 1 : -1; drawCats(); });
  $('.ct-pos').addEventListener('change', (e) => { cts.pos = e.target.value; drawCats(); });
  $('.ct-stat').addEventListener('change', (e) => { cts.stat = e.target.value; drawCats(); });
  $('.ct-search').addEventListener('input', (e) => { cts.q = e.target.value.trim().toLowerCase(); drawCats(); });
  wireSort(catsTable, cts, CTNUM, () => drawCats());
  function drawCats() {
    const d = dash.data('cats'); const tbody = $('tbody', catsTable); markSort(catsTable, cts);
    if (d.status !== 'ok') { tbody.replaceChildren(); return; }
    const isT = (v) => v === true || v === 'True' || v === 'true';
    let v = d.data.filter((r) => (cts.kind === 'all' || (cts.kind === 'held' ? (r.kind === 'over' && isT(r.held)) : r.kind === cts.kind)) &&
      (!cts.pos || r.pos === cts.pos) && (!cts.stat || r.stat === cts.stat) && (!cts.q || String(r.label).toLowerCase().includes(cts.q)));
    v = v.slice().sort(makeSorter(cts, CTNUM));
    $('.ct-count').textContent = fmt(v.length) + ' spots';
    const frag = document.createDocumentFragment();
    for (const r of v) {
      const tr = document.createElement('tr'); const td = mkTd(tr);
      td(r.label);
      const c = document.createElement('td'); c.className = 'rs-barcell';
      const o = num(r.over_season);
      const row1 = el('span', 'wg-sit-row1'); row1.append(el('b', null, pct1(o))); c.append(row1);
      const bar = el('div', 'rs-bar'); const f = el('span'); f.style.width = Math.max(0, Math.min(100, o)) + '%'; f.style.background = o > 50 ? 'var(--wg-green)' : o < 40 ? 'var(--cds-chart-status-critical)' : 'var(--cds-chart-muted)';
      const tk = el('i'); tk.style.left = '50%'; bar.append(f, tk); c.append(bar); tr.append(c);
      td(r.n_season, 'num rs-hide-narrow rs-sub');
      td(r.over_w47 === '' || r.over_w47 == null ? '—' : `${pct1(r.over_w47)} · ${r.n_w47}`, 'num');
      td(r.over_hist === '' || r.over_hist == null ? '—' : `${pct1(r.over_hist)} · ${fmt(num(r.n_hist))}`, 'num');
      td(pct1(r.base_hist), 'num rs-hide-narrow rs-sub');
      td(isT(r.held) ? 'Yes' : (r.kind ? 'No' : ''), isT(r.held) ? '' : 'rs-sub');
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
  }
  // ---------------- research charts ----------------
  const rc2 = { comp: 'WR rec' }, ds2 = { grp: 'RB rushing yards' };
  $('.rc2-comp').addEventListener('change', (e) => { rc2.comp = e.target.value; drawCharts(); });
  $('.ds2-grp').addEventListener('change', (e) => { ds2.grp = e.target.value; drawCharts(); });
  function drawResearch() {
    const d = dash.data('research');
    const box = $('#ch-recency'), box2 = $('#ch-defsig');
    if (d.status !== 'ok') { noSvg(box); noSvg(box2); return; }
    const R = (sec) => d.data.filter((r) => r.section === sec);
    // recency curves: extra error vs the best window, by half-life
    clearEmpty(box);
    const W = box.clientWidth;
    if (W) {
      const ser = [['Volume (targets / carries / attempts)', R('recency_vol').filter((r) => r.label === rc2.comp), wgColors()[0]], ['Efficiency (yards per unit)', R('recency_eff').filter((r) => r.label === rc2.comp), wgColors()[1]]];
      keyRow($('.rc2-key'), ser.map(([n, , c]) => [n, c, 0]));
      const H = 240, m = { t: 10, r: 12, b: 34, l: 40 }; const svg = freshSvg(box, W, H); box.style.minHeight = H + 'px';
      const HLS = ['1', '2', '3', '4', '6', '8', '12', '16', '24', '1000'];
      const x = d3.scalePoint(HLS, [m.l, W - m.r]).padding(0.3);
      const ymax = Math.max(2, d3.max(ser.flatMap(([, rows]) => rows.map((r) => +r.value2))) || 2);
      const y = d3.scaleLinear([0, ymax * 1.08], [H - m.b, m.t]);
      for (const t of y.ticks(4)) { svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(t)).attr('y2', y(t)).style('stroke', 'var(--cds-chart-grid)'); axTxt(svg, m.l - 6, y(t) + 3, '+' + t + '%', 'end'); }
      HLS.forEach((h) => axTxt(svg, x(h), H - m.b + 15, h === '1000' ? 'all' : h));
      axTxt(svg, (m.l + W - m.r) / 2, H - 3, 'Half-life in games (how fast older games fade)');
      for (const [n, rows, col] of ser) {
        const pts = HLS.map((h) => rows.find((r) => +r.value === +h)).filter(Boolean);
        svg.append('path').attr('d', d3.line().x((r) => x(String(+r.value))).y((r) => y(+r.value2))(pts)).style('fill', 'none').style('stroke', col).attr('stroke-width', 2);
        pts.forEach((r) => svg.append('circle').attr('cx', x(String(+r.value))).attr('cy', y(+r.value2)).attr('r', 3.5).style('fill', col)
          .on('mousemove', (ev) => showTip(box, ev, [`${n}`, `Half-life ${+r.value === 1000 ? 'none (all games equal)' : +r.value + ' games'}`, `${(+r.value2).toFixed(2)}% more error than the best window`]))
          .on('mouseleave', () => hideTip(box)));
      }
      const b = R('recency_best').find((r) => r.key === rc2.comp);
      if (b) $('#ch-recency-note').textContent = `${b.label}: volume is predicted best with a half-life of ${+b.value} games; efficiency with ${+b.value2 >= 1000 ? 'every game weighted equally' : `a half-life of ${+b.value2} games`} (${b.note}). Lower is better; the dip shows where recent games stop helping. ${fmt(+b.n)} player-games, 2024–26.`;
    }
    // defense signal
    const rows = R('def_signal').filter((r) => r.note === ds2.grp);
    divbars(box2, rows.map((r) => ({ label: r.label, value: +r.value, good: +r.value >= 0.12, bad: +r.value < 0, right: (+r.value).toFixed(2),
      tip: [r.label, `Next player's yards move ${(+r.value).toFixed(2)} for each yard of this per game`, `Correlation ${r.value2} · ${fmt(+r.n)} player-games`] })), { base: 0, domain: [-0.1, 0.3], ticks: [-0.1, 0, 0.1, 0.2, 0.3], fmt: (t) => t.toFixed(1) });
    const bg = R('big_game').filter((r) => r.note === ds2.grp);
    const g1 = bg.find((r) => r.label === 'after big game'), g0 = bg.find((r) => r.label === 'otherwise');
    const gb = bg.find((r) => r.label === 'big game led by blocking'), gr = bg.find((r) => r.label === 'big game led by runner');
    $('#ch-defsig-note').textContent = (g1 && g0 ? `After an opponent beat his own usual by 40+ yards against that defense, the next player beat his usual by ${(+g1.value).toFixed(1)} (n ${g1.n}) vs ${(+g0.value).toFixed(1)} otherwise.` : '') +
      (gb && gr ? ` When that big game came mostly before contact (blocking), the next back gained ${(+gb.value).toFixed(1)}; when it came after contact (the runner), ${(+gr.value).toFixed(1)}.` : '') +
      ' Bars: how much of what a defense allowed per game (vs each opponent’s own usual) showed up for the next player, 2023–26.';
    const V = R('variants'), rmv = R('rm');
    const vtxt = V.map((r) => `${r.label} ${(+r.value).toFixed(4)}`).join(' · ');
    const rb = rmv.find((r) => r.key === 'real_base'), rr = rmv.find((r) => r.key === 'real_rm');
    $('#ch-research-var').textContent = `Tested on the 706 real Week 6–7 lines (Brier, lower is better; fit on one week, tested on the other): ${vtxt}. Adding the role-and-matchup history (fit on 2023–25 only): ${rb ? (+rb.value).toFixed(4) : ''} → ${rr ? (+rr.value).toFixed(4) : ''}. The books' price is still the hardest number to beat; what helps most is knowing which roles and spots the books misprice.`;
  }

  function drawCharts() {
    const page = $('#charts');
    if (!page || page.hidden) return;
    const p = dash.data('hist_perms');
    if (p.status === 'ok') { drawFactorCharts(p.data); drawComboChart(p.data); drawHeatmap(p.data); }
    else document.querySelectorAll('#ch-factor-grid .wg-chart, #ch-combo-chart, #ch-heat-chart').forEach((b) => { const s = b.querySelector(':scope > svg'); if (s) s.remove(); });
    drawW6Chart();
    drawBoard();
    drawWeeks();
    drawPropsHeat();
    drawMom();
    drawTeams();
    drawCats();
    drawResearch();
  }

  let chartResize = 0;
  window.addEventListener('resize', () => { cancelAnimationFrame(chartResize); chartResize = requestAnimationFrame(drawCharts); });

  // ---------------- NBA live record + backtest charts ----------------
  const NR_C = () => ({ f: wgColors()[0], m: wgColors()[1], a: 'var(--color-fg-muted)', p: wgColors()[2] });
  const sgn = (v, d = 1) => (v > 0 ? '+' : v < 0 ? '−' : '±') + Math.abs(v).toFixed(d);
  const nightLab = (d) => new Date(d + 'T12:00:00').toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  const recOf = (rows) => {
    const n = rows.length; if (!n) return null;
    const w = rows.filter((r) => r.outcome === 'Won').length, stake = d3.sum(rows, (r) => +r.yes_price), pl = d3.sum(rows, (r) => +r.profit_c);
    return { n, w, win: 100 * w / n, price: stake / n, roi: 100 * pl / stake };
  };
  const btRec = (a) => (a && a[1] ? { n: a[1], w: a[2], win: a[3], price: a[4], roi: a[5] } : null);
  const ddRow = (label, s, color) => s && ({ label, value: s.win, price: s.price, color, right: `${s.win.toFixed(1)}% · ${sgn(s.roi)}%`,
    tip: [label, `Won ${fmt(s.w)} of ${fmt(s.n)} (${s.win.toFixed(1)}%)`, `Avg price ${s.price.toFixed(1)}¢ · ${s.win > s.price ? '+' : ''}${(s.win - s.price).toFixed(1)} pts vs price`, `Return ${sgn(s.roi)}% before fees`] });
  const keyRow = (el, items) => { if (!el) return; el.replaceChildren(...items.map(([name, color, kind]) => { const s = document.createElement('span'); const i = document.createElement('i'); if (kind) i.className = kind; else { i.style.background = color; if (kind === 0) i.style.borderRadius = '50%'; } s.append(i, name); return s; })); };
  const dKey = (C) => document.querySelectorAll('.wg-dkey').forEach((k) => keyRow(k, [['Filter', C.f, 0], ['Model', C.m, 0], ['Every line', C.a, 0], ['Average price paid', null, 'tick'], ['50%', null, 'line']]));

  // dumbbell: dot = win %, tick = average price, bar between them (green when it beat the price)
  function dumbbell(box, rows, o = {}) {
    rows = rows.filter(Boolean); clearEmpty(box);
    const W = box.clientWidth; if (!W) return;
    const bars = rows.filter((r) => !r.heading);
    if (!bars.length) { emptyNote(box, o.empty || 'Nothing settled yet.'); return; }
    const fs = 'var(--cds-font-size-caption)';
    let svg = freshSvg(box, W, 10);
    let lw = Math.min(W * 0.44, measure(svg, bars.map((r) => r.label), fs) + 12), rw = Math.min(120, Math.max(64, measure(svg, bars.map((r) => r.right), fs) + 10));
    const stacked = W - lw - rw < Math.max(150, W * 0.38); if (stacked) { lw = 0; rw = 0; }
    const top = 20, rowH = stacked ? 42 : 26, H = top + rows.length * rowH + 4;
    svg = freshSvg(box, W, H); box.style.minHeight = H + 'px';
    const vals = bars.flatMap((r) => [r.value, r.price]);
    const lo = Math.max(0, Math.floor((Math.min(50, d3.min(vals)) - 2) / 5) * 5), hi = Math.min(100, Math.ceil((Math.max(50, d3.max(vals)) + 2) / 5) * 5);
    const x = d3.scaleLinear([lo, hi], [lw + 6, W - rw - 6]);
    const g0 = svg.append('g');
    const ticks = x.ticks(stacked || hi - lo <= 15 ? 4 : 6);
    for (const t of new Set([...ticks, 50])) {
      g0.append('line').attr('x1', x(t)).attr('x2', x(t)).attr('y1', top - 4).attr('y2', H - 4).style('stroke', t === 50 ? 'var(--cds-chart-reference)' : 'var(--cds-chart-grid)').attr('stroke-dasharray', t === 50 ? '4 3' : null);
      if (ticks.includes(t)) g0.append('text').attr('x', x(t)).attr('y', top - 8).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(t + '%');
    }
    const anim = !reduced();
    rows.forEach((r, i) => {
      const y = top + i * rowH;
      if (r.heading) { svg.append('text').attr('x', 0).attr('y', y + rowH - 7).style('font-size', '10px').style('letter-spacing', '.08em').style('font-weight', 600).style('fill', 'var(--color-fg-muted)').text(r.heading.toUpperCase()); return; }
      const cy = stacked ? y + rowH - 10 : y + rowH / 2, ty = stacked ? y + 12 : cy;
      const g = svg.append('g');
      const valT = g.append('text').attr('x', stacked ? W : W - rw + 8).attr('y', ty).attr('dy', '0.35em').attr('text-anchor', stacked ? 'end' : 'start').style('font-size', fs).style('fill', 'var(--color-fg-muted)').style('font-variant-numeric', 'tabular-nums').text(r.right);
      const lab = g.append('text').attr('x', stacked ? 0 : lw - 4).attr('y', ty).attr('dy', '0.35em').attr('text-anchor', stacked ? 'start' : 'end').style('font-size', fs).style('fill', 'var(--color-fg)').text(r.label);
      fitText(lab, r.label, stacked ? W - valT.node().getComputedTextLength() - 18 : lw - 8);
      const good = r.value > r.price, col = good ? 'var(--wg-green)' : 'var(--wg-bear)';
      const seg = g.append('line').attr('x1', x(r.price)).attr('x2', anim ? x(r.price) : x(r.value)).attr('y1', cy).attr('y2', cy).style('stroke', col).attr('stroke-width', 4).attr('stroke-linecap', 'round').style('opacity', 0.45);
      g.append('line').attr('x1', x(r.price)).attr('x2', x(r.price)).attr('y1', cy - 7).attr('y2', cy + 7).style('stroke', 'var(--color-fg)').attr('stroke-width', 2).attr('stroke-linecap', 'round');
      const dot = g.append('circle').attr('cx', anim ? x(r.price) : x(r.value)).attr('cy', cy).attr('r', 5.5).style('fill', r.color || 'var(--color-fg-muted)').style('stroke', 'var(--color-panel)').attr('stroke-width', 1.5);
      if (anim) { seg.transition().delay(i * 25).duration(520).ease(d3.easeCubicOut).attr('x2', x(r.value)); dot.transition().delay(i * 25).duration(520).ease(d3.easeCubicOut).attr('cx', x(r.value)); }
      g.append('rect').attr('x', 0).attr('y', y).attr('width', W).attr('height', rowH).style('fill', 'transparent')
        .on('mousemove', (ev) => { dot.attr('r', 7); showTip(box, ev, r.tip); }).on('mouseleave', () => { dot.attr('r', 5.5); hideTip(box); });
    });
  }

  // multi-series line chart; xs = labels (point scale) or Dates (time scale)
  function lineChart(box, xs, series, o = {}) {
    clearEmpty(box); const W = box.clientWidth; if (!W) return;
    const H = o.h || 220, m = { t: 12, r: 12, b: 24, l: 42 };
    const svg = freshSvg(box, W, H); box.style.minHeight = H + 'px';
    const all = series.flatMap((s) => s.vals).filter((v) => v != null).concat(o.ref != null ? [o.ref] : []);
    const y = d3.scaleLinear(d3.extent(all), [H - m.b, m.t]).nice(5);
    const time = xs[0] instanceof Date;
    const x = time ? d3.scaleTime(d3.extent(xs), [m.l, W - m.r]) : d3.scalePoint(xs, [m.l + 14, W - m.r - 14]);
    const yf = o.yfmt || ((v) => v + '%');
    for (const t of y.ticks(4)) {
      svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(t)).attr('y2', y(t)).style('stroke', 'var(--cds-chart-grid)');
      svg.append('text').attr('x', m.l - 6).attr('y', y(t)).attr('dy', '0.32em').attr('text-anchor', 'end').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(yf(t));
    }
    if (o.ref != null) svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(o.ref)).attr('y2', y(o.ref)).style('stroke', 'var(--cds-chart-reference)').attr('stroke-dasharray', '4 3');
    const xl = time ? x.ticks(W < 480 ? 4 : 6) : xs;
    for (const t of xl) svg.append('text').attr('x', x(t)).attr('y', H - 6).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(time ? d3.timeFormat('%b')(t) : t);
    const anim = !reduced();
    for (const s of series) {
      const line = d3.line().defined((v) => v != null).x((_, i) => x(xs[i])).y((v) => y(v)).curve(d3.curveMonotoneX);
      const p = svg.append('path').datum(s.vals).attr('d', line).style('fill', 'none').style('stroke', s.color).attr('stroke-width', s.w || 2).attr('stroke-linejoin', 'round').attr('stroke-linecap', 'round');
      if (s.dash) p.attr('stroke-dasharray', s.dash);
      else if (anim) { const L = p.node().getTotalLength(); p.attr('stroke-dasharray', `${L} ${L}`).attr('stroke-dashoffset', L).transition().duration(900).ease(d3.easeCubicOut).attr('stroke-dashoffset', 0).on('end', () => p.attr('stroke-dasharray', null)); }
      if (!time) s.vals.forEach((v, i) => { if (v != null) svg.append('circle').attr('cx', x(xs[i])).attr('cy', y(v)).attr('r', 3.5).style('fill', s.color).style('stroke', 'var(--color-panel)').attr('stroke-width', 1.5); });
    }
    const guide = svg.append('line').attr('y1', m.t).attr('y2', H - m.b).style('stroke', 'var(--color-fg-muted)').style('opacity', 0);
    svg.append('rect').attr('x', m.l).attr('y', m.t).attr('width', W - m.l - m.r).attr('height', H - m.t - m.b).style('fill', 'transparent')
      .on('mousemove', (ev) => {
        const [px] = d3.pointer(ev);
        let i = 0, best = Infinity; xs.forEach((v, k) => { const d = Math.abs(x(v) - px); if (d < best) { best = d; i = k; } });
        guide.attr('x1', x(xs[i])).attr('x2', x(xs[i])).style('opacity', 0.4);
        showTip(box, ev, [o.xlab ? o.xlab(xs[i], i) : String(xs[i]), ...series.filter((s) => s.vals[i] != null).map((s) => `${s.name}: ${o.tipfmt ? o.tipfmt(s, i) : yf(s.vals[i])}`)]);
      })
      .on('mouseleave', () => { guide.style('opacity', 0); hideTip(box); });
  }

  // calibration: called chance (x) vs how often it hit (y); dot size = lines in the bucket
  function calibChart(box, sets, o = {}) {
    clearEmpty(box); const W = box.clientWidth; if (!W) return;
    const pts = sets.flatMap((s) => s.pts);
    if (!pts.length) { emptyNote(box, o.empty || 'Not enough settled props yet.'); return; }
    const H = Math.min(300, Math.max(220, W * 0.62)), m = { t: 10, r: 12, b: 34, l: 42 };
    const svg = freshSvg(box, W, H); box.style.minHeight = H + 'px';
    const [lo, hi] = o.dom || [30, 70];
    const x = d3.scaleLinear([lo, hi], [m.l, W - m.r]), y = d3.scaleLinear([lo, hi], [H - m.b, m.t]);
    const r = d3.scaleSqrt([0, d3.max(pts, (p) => p.n) || 1], [2.5, o.rmax || 9]);
    for (const t of x.ticks(5)) {
      svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(t)).attr('y2', y(t)).style('stroke', 'var(--cds-chart-grid)');
      svg.append('text').attr('x', m.l - 6).attr('y', y(t)).attr('dy', '0.32em').attr('text-anchor', 'end').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(t + '%');
      svg.append('text').attr('x', x(t)).attr('y', H - m.b + 14).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(t + '%');
    }
    svg.append('text').attr('x', (m.l + W - m.r) / 2).attr('y', H - 4).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text('Called chance');
    svg.append('text').attr('transform', `translate(10,${(m.t + H - m.b) / 2}) rotate(-90)`).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text('Hit rate');
    svg.append('line').attr('x1', x(lo)).attr('x2', x(hi)).attr('y1', y(lo)).attr('y2', y(hi)).style('stroke', 'var(--cds-chart-reference)').attr('stroke-dasharray', '4 3');
    const cl = (v) => Math.max(lo, Math.min(hi, v));
    for (const s of sets) {
      const P = s.pts.filter((p) => p.x != null && p.y != null).sort((a, b) => a.x - b.x);
      svg.append('path').datum(P).attr('d', d3.line().x((p) => x(cl(p.x))).y((p) => y(cl(p.y)))).style('fill', 'none').style('stroke', s.color).attr('stroke-width', 1.25).style('opacity', 0.5);
      for (const p of P) svg.append('circle').attr('cx', x(cl(p.x))).attr('cy', y(cl(p.y))).attr('r', r(p.n)).style('fill', s.color).style('fill-opacity', 0.85).style('stroke', 'var(--color-panel)').attr('stroke-width', 1)
        .on('mousemove', (ev) => showTip(box, ev, [s.name + (p.lab ? ' · ' + p.lab : ''), `Called ${p.x.toFixed(1)}% · hit ${p.y.toFixed(1)}%`, `${fmt(p.n)} lines`]))
        .on('mouseleave', () => hideTip(box));
    }
  }

  let nbtData = null;
  const nbtD = () => { if (!nbtData) { try { nbtData = window.WG_NBT || JSON.parse($('#nbt-data').textContent); } catch (e) { nbtData = {}; } } return nbtData; };
  function drawNbaBt() {
    const B = nbtD(); if (!B.strat || !$('#nbt-strat') || !$('#nbt-strat').clientWidth) return;
    const C = NR_C(); dKey(C);
    const bt = document.querySelectorAll('#nba-bt .wg-nbt-tiles .rs-card'); if (bt[0]) bt[0].style.setProperty('--wg-tile', C.f); if (bt[1]) bt[1].style.setProperty('--wg-tile', C.m);
    dumbbell($('#nbt-strat'), B.strat.map((a) => (a.length === 1 ? { heading: a[0].slice(1) } : ddRow(a[0], btRec(a), /Filter:/.test(a[0]) ? C.f : /Model:/.test(a[0]) ? C.m : null))));
    dumbbell($('#nbt-mkt'), B.mkt.flatMap(([mk, f, mo]) => [{ heading: mk }, ddRow('Filter', btRec([0, ...f]), C.f), ddRow('Model', btRec([0, ...mo]), C.m)]));
    document.querySelectorAll('.nbt-key').forEach((k) => keyRow(k, [['Filter (hit >50%)', C.f], ['Model (Wedge % > price)', C.m], ['Every 45–55¢ line', C.a]]));
    const mo = B.month, mv = (k) => mo.map((r) => (r[k] ? r[k][0] : null));
    lineChart($('#nbt-month'), mo.map((r) => r[0]), [{ name: 'Every line', color: C.a, vals: mv(1) }, { name: 'Filter', color: C.f, vals: mv(2) }, { name: 'Model', color: C.m, vals: mv(3) }],
      { ref: 50, h: 210, tipfmt: (s, i) => { const k = { 'Every line': 1, Filter: 2, Model: 3 }[s.name], c = mo[i][k]; return `${c[0]}% of ${fmt(c[1])} at ${c[2]}¢`; } });
    const cu = B.cum, cd = cu.map((r) => new Date(r[0] + 'T12:00:00'));
    lineChart($('#nbt-cum'), cd, [{ name: 'Every line', color: C.a, vals: cu.map((r) => r[1]) }, { name: 'Filter', color: C.f, vals: cu.map((r) => r[2]) }, { name: 'Model', color: C.m, vals: cu.map((r) => r[3]) }],
      { ref: 0, h: 210, yfmt: (v) => sgn(v, 0) + '%', tipfmt: (s, i) => sgn(s.vals[i], 1) + '%', xlab: (d) => 'Through ' + d3.timeFormat('%b %-d, %Y')(d) });
    keyRow($('#nbt-cal-key'), [['Wedge %', C.m], ['Price alone', C.p]]);
    const cal = B.cal.filter((c) => c[3] >= 50 || c[6] >= 50);
    calibChart($('#nbt-cal'), [{ name: 'Wedge %', color: C.m, pts: cal.filter((c) => c[3] >= 50).map((c) => ({ x: c[1], y: c[2], n: c[3] })) },
      { name: 'Price alone', color: C.p, pts: cal.filter((c) => c[6] >= 50).map((c) => ({ x: c[4], y: c[5], n: c[6] })) }], { dom: [35, 65] });
  }

  const nrs = { show: 'all', night: '', out: '', q: '' };
  const nrEl = (c) => $('#nba-rec .' + c);
  if ($('#nba-rec')) {
    nrEl('nr-show').addEventListener('change', (e) => { nrs.show = e.target.value; drawNbaRecTable(); });
    nrEl('nr-night').addEventListener('change', (e) => { nrs.night = e.target.value; drawNbaRecTable(); });
    nrEl('nr-out').addEventListener('change', (e) => { nrs.out = e.target.value; drawNbaRecTable(); });
    nrEl('nr-search').addEventListener('input', (e) => { nrs.q = e.target.value.trim().toLowerCase(); drawNbaRecTable(); });
  }
  const isF = (r) => r.qualifies === 'Yes', isM = (r) => r.model_pick === 'Yes', isP = (r) => r.group === 'Player props';
  function drawNbaRecTable() {
    const d = dash.data('nba_results'), tb = $('#nr-table tbody'); if (!tb) return;
    if (d.status !== 'ok') { tb.replaceChildren(); nrEl('nr-count').textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
    const rows = d.data, sel = nrEl('nr-night');
    const nights = [...new Set(rows.map((r) => r.date))].sort();
    if (sel.options.length !== nights.length + 1) sel.replaceChildren(new Option('All nights', ''), ...nights.map((n) => new Option(nightLab(n), n)));
    sel.value = nrs.night;
    const v = rows.filter((r) => (nrs.show === 'all' || (nrs.show === 'q' ? isF(r) : nrs.show === 'm' ? isM(r) : isF(r) && isM(r))) && (!nrs.night || r.date === nrs.night) && (!nrs.out || r.outcome === nrs.out)
      && (!nrs.q || (r.game + ' ' + r.contract + ' ' + r.market).toLowerCase().includes(nrs.q)))
      .sort((a, b) => b.date.localeCompare(a.date) || a.game.localeCompare(b.game) || (isP(a) - isP(b)) || a.market.localeCompare(b.market) || a.contract.localeCompare(b.contract));
    nrEl('nr-count').textContent = fmt(v.length) + ' of ' + fmt(rows.length) + ' lines';
    const frag = document.createDocumentFragment();
    for (const r of v) {
      const tr = document.createElement('tr'); const td = mkTd(tr);
      if (r.outcome === 'Pending') tr.className = 'rs-started';
      td(nightLab(r.date), 'rs-sub'); td(r.game); td(r.contract, 'rs-contract'); td(r.yes_price, 'num');
      pctCell(tr, r.hit_rate);
      td(r.sit_hit === '' ? '—' : Math.round(+r.sit_hit) + '%', 'num');
      td([isF(r) ? 'Filter' : '', isM(r) ? 'Model' : ''].filter(Boolean).join(' + ') || '—', 'rs-sub');
      td(r.result, 'rs-sub');
      const oc = td(r.outcome); oc.className = r.outcome === 'Won' ? 'an-won' : r.outcome === 'Lost' ? 'an-lost' : 'rs-sub';
      td(r.profit_c === '' ? '—' : (+r.profit_c > 0 ? '+' : '') + r.profit_c, 'num ' + (+r.profit_c > 0 ? 'an-won' : +r.profit_c < 0 ? 'an-lost' : 'rs-sub'));
      frag.appendChild(tr);
    }
    tb.replaceChildren(frag);
  }
  function drawNbaRec() {
    const d = dash.data('nba_results'), page = $('#nba');
    if (d.status === 'ok') {
      const all = d.data, S = all.filter((r) => r.outcome === 'Won' || r.outcome === 'Lost'), pend = all.filter((r) => r.outcome === 'Pending');
      const C = NR_C(); dKey(C); const F = S.filter(isF), Mo = S.filter(isM), FM = S.filter((r) => isF(r) && isM(r)), Pr = S.filter(isP);
      const nights = [...new Set(S.map((r) => r.date))].sort();
      const tile = (label, s, color) => { const c = document.createElement('div'); c.className = 'rs-card'; if (color) c.style.setProperty('--wg-tile', color);
        c.innerHTML = `<div class="rs-tile-label"></div><div class="rs-tile-num">${s ? s.win.toFixed(1) + '%' : '—'}</div><div class="rs-tile-note">${s ? `${fmt(s.w)}–${fmt(s.n - s.w)} · avg price ${s.price.toFixed(0)}¢ · return <b class="wg-roi ${s.roi > 0 ? 'up' : 'down'}">${sgn(s.roi)}%</b>` : 'Nothing settled yet'}</div>`;
        c.firstChild.textContent = label; return c; };
      $('#nr-tiles').replaceChildren(tile('Filter: hit >50% of his last 20', recOf(F), C.f), tile('Model: Wedge % above the price', recOf(Mo), C.m), tile('Filter and model agree', recOf(FM)), tile('Every posted line', recOf(S)));
      $('#nr-sum').textContent = `${fmt(S.length)} lines settled from ${nights.length} night${nights.length === 1 ? '' : 's'} (${nights.map(nightLab).join(', ')}), ${new Set(S.map((r) => r.game)).size} games` + (pend.length ? `; ${fmt(pend.length)} more from ${((n) => n + (n === 1 ? ' game' : ' games'))(new Set(pend.map((r) => r.game)).size)} tipped off but not yet final.` : '.');
      if (page && !page.hidden && $('#nr-strat').clientWidth) {
        dumbbell($('#nr-strat'), [ddRow('Every posted line', recOf(S), null), ddRow('Filter', recOf(F), C.f), ddRow('Model', recOf(Mo), C.m), ddRow('Filter and model agree', recOf(FM), null),
          { heading: 'Player props only' }, ddRow('Every prop', recOf(Pr), null), ddRow('Filter props', recOf(F.filter(isP)), C.f)]);
        const mk = d3.groups(S, (r) => r.market).sort((a, b) => b[1].length - a[1].length);
        dumbbell($('#nr-mkt'), mk.flatMap(([m, g]) => [{ heading: `${m} · ${g.length} lines` }, ddRow('Filter', recOf(g.filter(isF)), C.f), ddRow('Model', recOf(g.filter(isM)), C.m), ddRow('Every line', recOf(g), null)]));
        dumbbell($('#nr-night'), nights.flatMap((n) => { const g = S.filter((r) => r.date === n); return [{ heading: `${nightLab(n)} · ${new Set(g.map((r) => r.game)).size} games` }, ddRow('Filter', recOf(g.filter(isF)), C.f), ddRow('Model', recOf(g.filter(isM)), C.m), ddRow('Every line', recOf(g), null)]; }));
        const P = S.filter((r) => isP(r) && r.sit_hit !== ''), bk = d3.groups(P, (r) => Math.floor(+r.sit_hit / 5) * 5).sort((a, b) => a[0] - b[0]);
        calibChart($('#nr-cal'), [{ name: 'Wedge %', color: C.m, pts: bk.filter(([, g]) => g.length >= 5).map(([lo, g]) => ({ lab: `${lo}–${lo + 5}%`, x: d3.mean(g, (r) => +r.sit_hit), y: 100 * g.filter((r) => r.outcome === 'Won').length / g.length, n: g.length })) },
          { name: 'Price', color: C.p, pts: d3.groups(P, (r) => Math.floor(+r.yes_price / 5) * 5).filter(([, g]) => g.length >= 5).map(([lo, g]) => ({ lab: `${lo}–${lo + 5}¢`, x: d3.mean(g, (r) => +r.yes_price), y: 100 * g.filter((r) => r.outcome === 'Won').length / g.length, n: g.length })) }],
          { dom: [30, 70], rmax: 8, empty: 'Needs at least 5 settled props per bucket.' });
        keyRow($('#nr-cal-key'), [['Wedge %', C.m], ['Price', C.p]]);
      }
    }
    drawNbaRecTable();
    if (page && !page.hidden) drawNbaBt();
  }
  let nrResize = 0;
  window.addEventListener('resize', () => { const p = $('#nba'); if (!p || p.hidden) return; cancelAnimationFrame(nrResize); nrResize = requestAnimationFrame(drawNbaRec); });


  // ---------------- Wedge identity: chart palette, lobby reads, counts, record ----------------
  function wgColors() {
    const cs = getComputedStyle($('.wg-paper') || document.documentElement);
    return ['--wg-c1', '--wg-c2', '--wg-c3', '--wg-c4'].map((v, i) => cs.getPropertyValue(v).trim() || ['#009A44', '#3F6EB8', '#C27526', '#8C55A8'][i]);
  }
  const WX_MKT = { passyd: 'Passing', passtd: 'Passing', int: 'Passing', rushyd: 'Rushing', rryd: 'Scrimmage', recyd: 'Receiving', rec: 'Receiving', td: 'Touchdown' };
  const wgFmt = (n) => Number(n).toLocaleString('en-US');
  // jump to the Lines tab with a view (and optionally a game and a search) set
  const wxToLines = (show, game, q) => {
    if (game != null) ls.game = game;
    if (q != null) { ls.q = q.toLowerCase(); const f = $('.rs-search'); if (f) f.value = q; }
    const px = $('.rs-px'); if (px && show !== 'every') { px.value = ''; ls.px = ''; }
    const sel = $('.rs-show'); if (sel && [...sel.options].some((o) => o.value === show)) { sel.value = show; sel.dispatchEvent(new Event('change')); }
  };
  document.querySelectorAll('[data-wg-show]').forEach((b) => b.addEventListener('click', () => {
    wxToLines(b.dataset.wgShow, 'wgGame' in b.dataset ? b.dataset.wgGame : null, 'wgGame' in b.dataset ? '' : null);
  }));
  const wxRead = (r, o = {}) => {
    const yes = num(r.yes_price);
    const no = num(r.no_price) != null ? num(r.no_price) : (num(r.yes_bid) != null ? 100 - num(r.yes_bid) : null);
    const side = o.side || r.sit_pick, pYes = num(r.sit_hit), pSide = side === 'Yes' ? pYes : 100 - pYes;
    const edge = o.edge != null ? o.edge : num(r.sit_pedge);
    const label = rhLabel(r.contract);
    const b = el('button', 'wx-read'); b.type = 'button';
    const top = el('span', 'wx-read-top'); top.append(el('span', null, o.rank ? `${String(o.rank).padStart(2, '0')} · ${r.kickoff}` : `${r.game} · ${r.kickoff}`), el('span', null, WX_MKT[r.sit_stat] || r.market));
    const big = el('span', 'wx-read-big'); { const rl = el('span', 'pf-roll'); rl.append(el('span', null, String(Math.round(pSide)))); big.append(rl, el('small', null, '%')); }
    const lab = el('span', 'wx-mono'); lab.append('Wedge', document.createElement('br'), side === 'Yes' ? 'Yes' : 'No');
    const mid = el('span', 'wx-read-mid'); mid.append(big, lab);
    const px = el('span', 'wx-read-px');
    const py = el('span', side === 'Yes' ? 'is-pick' : ''); py.append(el('span', null, 'Yes'), el('span', null, yes == null ? '—' : yes + '¢'));
    const pn = el('span', side === 'No' ? 'is-pick' : ''); pn.append(el('span', null, 'No'), el('span', null, no == null ? '—' : no + '¢'));
    px.append(py, pn);
    const foot = el('span', 'wx-read-foot'); const dot = el('i', 'wx-dot'); dot.setAttribute('aria-hidden', 'true');
    foot.append(dot, `${side}, +${Math.round(edge)} pts vs price`); if (o.rough) foot.append(el('span', 'wx-rough', '· rough guide'));
    foot.append(el('em', null, 'Full read ↗'));
    const hh = num(r.hits), gg = num(r.games);
    let hrow = null;
    if (hh != null && gg) { const k = side === 'Yes' ? hh : gg - hh; hrow = el('span', 'wz-hr'); hrow.append(el('b', null, Math.round(100 * k / gg) + '%'), `${side} in ${k} of ${gg} games this season`); }
    b.classList.add('wz-spot'); wzTint(b, r);
    b.append(top, wzWords(label), mid, px, ...(hrow ? [hrow] : []), foot);
    b.setAttribute('aria-label', `${label}, ${r.game}, ${r.kickoff}. Wedge reads ${side}: ${Math.round(pSide)}% against ${side === 'Yes' ? yes : no} cents. Open the full read.`);
    const ctx = { title: label, game: r.game, market: r.market, source: r.source };
    ctx.key = `${ctx.game}|${ctx.market}|${r.contract}`;
    if (r.sit_key) b.addEventListener('click', () => openSit(r, ctx, b));
    else b.addEventListener('click', () => { showPage('lines'); wxToLines('every', r.game, label.split(':')[0]); ($('#top') || document.body).scrollIntoView({ block: 'start' }); });
    return b;
  };
  // reads by game: the better side priced 25-75c, Wedge % 3+ pts over it, ranked by Kelly growth (chance and price in balance)
  const WX_FAM = { rushyd: 'rush', rryd: 'rush', recyd: 'recv', rec: 'recv', passyd: 'pass', passtd: 'pass' };
  const WX_SKIP = /Questionable|Doubtful|Out\b|Inactive|No bid/i;
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
      if (g) { t.append(wzPips(g), g); const d = (ko.get(g)[1].match(/(Thu|Fri|Sat|Sun|Mon)\b/) || [])[1]; if (d) t.append(el('small', null, d)); } else t.append('All games');
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
    wzMatchup(wxGame);
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
  }
  function drawLobby() {
    const ld = dash.data('lines'), la = dash.data('lines_all');
    if (la.status === 'ok') document.querySelectorAll('[data-wg-count="every"]').forEach((e) => { e.textContent = wgFmt(la.data.length); });
    if (ld.status === 'ok') {
      const picks = ld.data.filter((r) => r.sit_pick && r.sit_key && num(r.sit_hit) != null).sort((a, b) => num(b.sit_pedge) - num(a.sit_pedge));
      document.querySelectorAll('[data-wg-count="lines"]').forEach((e) => { e.textContent = wgFmt(ld.data.length); });
      document.querySelectorAll('[data-wg-count="picks"]').forEach((e) => { e.textContent = wgFmt(picks.length); });
      const per = new Map(), bySide = { Yes: [], No: [] };
      for (const r of picks) { const c = per.get(r.game) || 0; if (c >= 2 || bySide[r.sit_pick].length >= 3) continue; per.set(r.game, c + 1); bySide[r.sit_pick].push(r); }
      const top = []; for (let k = 0; k < 3; k++) { if (bySide.No[k]) top.push(bySide.No[k]); if (bySide.Yes[k]) top.push(bySide.Yes[k]); }
      wxAllTop = top; wxPicksN = picks.length;
    } else if (ld.status === 'error' && !wxGame) { const box = $('#wg-hot-cards'); if (box) box.replaceChildren(el('p', 'wx-empty', 'This week’s lines failed to load. Reload the page to try again.')); }
    if (la.status === 'ok') wxTabs(la.data);
    if (ld.status === 'ok' || la.status === 'ok') wxDraw();
    wzLobby();
    const bt = dash.data('bt_weeks');
    if (bt.status === 'ok') {
      const row = (g, sg) => bt.data.find((r) => String(r.week) === 'all' && r.seg_group === g && r.segment === sg);
      const put = (k, v) => { const e = document.querySelector(`[data-wg-rcpt="${k}"]`); if (e && v != null) e.textContent = v; };
      const sg = (x) => (Number(x) > 0 ? '+' : Number(x) < 0 ? '−' : '') + Math.abs(Number(x)).toFixed(1) + '%';
      const wp = row('Strategy', 'Wedge picks (3+ pts)'), ey = row('Strategy', 'Every Yes'), pa = row('Market', 'Props · passing'), ru = row('Market', 'Props · rushing');
      if (wp) { const e = document.querySelector('[data-wg-rcpt="picks-pct"]'); if (e) { e.replaceChildren((+wp.win_pct).toFixed(1), el('small', null, '%')); } put('picks-txt', `${wp.wins}–${wp.losses} over Weeks 6–8, ${sg(wp.roi_pct)} before fees.`); }
      if (ey) put('yes-roi', sg(ey.roi_pct));
      if (pa) put('pass-pct', (+pa.win_pct).toFixed(1) + '%');
      if (ru) put('rush-pct', (+ru.win_pct).toFixed(1) + '%');
    }
  }

  // ================= Wedge UI round 2: record, analysts, lobby, matchups, accounts, tables, motion =================
  const WZ_REDUCE = (() => { try { return matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { return false; } })();
  // Paste a payment link (for example a Stripe Payment Link) for each plan; empty sends a membership request by email instead.
  const WZ_CHECKOUT = { monthly: '', season: '' };
  // Accounts paused (Wed Nov 4, 10 PM): no Log in / Sign up in the header; Join still goes straight to checkout. Set true to bring accounts back.
  const WZ_ACCOUNTS = false;
  const WZ_PLANS = { free: ['Free', '$0'], monthly: ['Wedge Pro', '$19.99 / month'], season: ['Wedge Pro Season', '$119.99 / year'] };
  const WZ_TEAMS = { ARI: ['Arizona', '#97233F', '#111111'], ATL: ['Atlanta', '#A71930', '#111111'], BAL: ['Baltimore', '#241773', '#9E7C0C'], BUF: ['Buffalo', '#00338D', '#C60C30'],
    CAR: ['Carolina', '#0085CA', '#101820'], CHI: ['Chicago', '#0B162A', '#C83803'], CIN: ['Cincinnati', '#FB4F14', '#111111'], CLE: ['Cleveland', '#311D00', '#FF3C00'],
    DAL: ['Dallas', '#003594', '#869397'], DEN: ['Denver', '#FB4F14', '#002244'], DET: ['Detroit', '#0076B6', '#B0B7BC'], GB: ['Green Bay', '#203731', '#FFB612'],
    HOU: ['Houston', '#03202F', '#A71930'], IND: ['Indianapolis', '#002C5F', '#A2AAAD'], JAX: ['Jacksonville', '#006778', '#D7A22A'], KC: ['Kansas City', '#E31837', '#FFB81C'],
    LV: ['Las Vegas', '#111111', '#A5ACAF'], LAC: ['Los Angeles', '#0080C6', '#FFC20E'], LAR: ['Los Angeles', '#003594', '#FFA300'], MIA: ['Miami', '#008E97', '#FC4C02'],
    MIN: ['Minnesota', '#4F2683', '#FFC62F'], NE: ['New England', '#002244', '#C60C30'], NO: ['New Orleans', '#D3BC8D', '#101820'], NYG: ['New York', '#0B2265', '#A71930'],
    NYJ: ['New York', '#125740', '#FFFFFF'], PHI: ['Philadelphia', '#004C54', '#A5ACAF'], PIT: ['Pittsburgh', '#FFB612', '#101820'], SF: ['San Francisco', '#AA0000', '#B3995D'],
    SEA: ['Seattle', '#002244', '#69BE28'], TB: ['Tampa Bay', '#D50A0A', '#34302B'], TEN: ['Tennessee', '#0C2340', '#4B92DB'], WSH: ['Washington', '#5A1414', '#FFB612'] };
  const wzSides = (game) => { const m = /^(\S+) @ (\S+)$/.exec(String(game || '')); return m ? [m[1], m[2]] : [null, null]; };
  const wzTeam = (t) => WZ_TEAMS[t] || [t || '', '#4A5056', '#9DA3AA'];

  // count-up for headline numbers (first time only)
  function wzCount(e, text) {
    const m = /^([+−-]?)(\d+(?:\.\d+)?)(.*)$/.exec(String(text));
    if (!m || WZ_REDUCE || e.dataset.counted) { e.textContent = text; return; }
    e.dataset.counted = '1';
    const to = Number(m[2]), dec = (m[2].split('.')[1] || '').length, t0 = performance.now(), dur = 1100;
    const step = (t) => { const k = Math.min(1, (t - t0) / dur), v = to * (1 - Math.pow(1 - k, 3)); e.textContent = m[1] + v.toFixed(dec) + m[3]; if (k < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  }
  function wzSet(k, v, count) { document.querySelectorAll(`[data-wz="${k}"]`).forEach((e) => { if (count) wzCount(e, v); else e.textContent = v; }); }
  function wzRecord(p, w, n) {
    const big = document.querySelector('[data-wz="cert-pct"]');
    if (big) {
      if (p == null) big.textContent = '—';
      else { const t = (p % 1 ? p.toFixed(1) : String(p)); if (WZ_REDUCE || big.dataset.counted) { big.replaceChildren(t, el('small', null, '%')); } else { big.dataset.counted = '1'; const sp = el('span', null, '0'); big.replaceChildren(sp, el('small', null, '%')); wzCount(sp, t); } }
    }
    wzSet('cert-wl', n ? `${w}–${n - w}` : '—'); wzSet('cert-pct2', p == null ? '—' : (p % 1 ? p.toFixed(1) : String(p)) + '%');
    wzSet('cert-rec', n ? `${w} of ${n} certified picks won, before fees` : 'No certified picks have settled yet');
  }

  // analysts on the lobby
  function wzAnalysts(ranked) {
    const box = $('#wz-board'); if (!box) return;
    const idx = pickIndex();
    let W = 0, N = 0;
    const fmtP = (p, signed) => (signed ? (p > 0 ? '+' : (p < 0 ? '−' : '')) : '') + (Math.abs(p) % 1 ? Math.abs(p).toFixed(1) : Math.abs(p)) + '%';
    const cards = ranked.map((st, i) => {
      W += st.wins; N += st.n;
      const c = el('article', 'wz-an wz-spot' + (i === 0 && st.n ? ' lead' : ''));
      const top = el('div', 'wz-an-top'); const av = el('span', 'wz-av', st.name.slice(0, 1).toUpperCase()); av.setAttribute('aria-hidden', 'true');
      top.append(av, el('span', 'wz-an-name', st.name), el('span', 'wz-an-rank', st.n ? '#' + (i + 1) : '—'));
      const pct = el('div', 'wz-an-pct');
      if (st.winPct == null) pct.textContent = '—'; else pct.append(String(st.winPct % 1 ? st.winPct.toFixed(1) : st.winPct), el('small', null, '%'));
      const meta = el('div', 'wz-an-meta');
      meta.append(el('span', null, st.n ? `${st.wins}–${st.n - st.wins} settled` : 'No picks settled yet'));
      if (st.profitPct != null) meta.append(el('span', 'wz-chip ' + (st.profitPct > 0 ? 'pos' : st.profitPct < 0 ? 'neg' : 'flat'), fmtP(st.profitPct, true) + ' profit'));
      const keys = analysts.picks[st.name] || [];
      const last = keys.map((k) => pickInfo(idx, k)).filter((v) => v.outcome === 'Won' || v.outcome === 'Lost').sort((a, b) => (Number(a.week) || 0) - (Number(b.week) || 0)).slice(-5);
      const dots = el('div', 'wz-dots'); dots.setAttribute('aria-label', last.length ? 'Last ' + last.length + ': ' + last.map((v) => (v.outcome === 'Won' ? 'win' : 'loss')).join(', ') : 'No settled picks yet');
      last.forEach((v) => dots.append(el('i', v.outcome === 'Won' ? 'w' : '')));
      dots.append(el('small', null, st.pending ? `${st.pending} pending` : (last.length ? 'Last ' + last.length : '')));
      c.append(top, pct, meta, dots);
      return c;
    });
    box.replaceChildren(...(cards.length ? cards : [el('p', 'wx-empty', 'No analysts yet.')]));
    if (N) { wzSet('an-pct', fmtP(Math.round(1000 * W / N) / 10), true); wzSet('an-rec', `${W} of ${N} analyst picks won`); }
    else { wzSet('an-pct', '—'); wzSet('an-rec', 'No analyst picks have settled yet'); }
  }

  // team colors + generic helmets (no logos)
  function wzPips(game) {
    const [a, h] = wzSides(game), p = el('span', 'wz-pips'); p.setAttribute('aria-hidden', 'true');
    for (const t of [a, h]) { const i = el('i'); i.style.background = wzTeam(t)[1]; p.append(i); }
    return p;
  }
  let wzHelmN = 0;
  const WZ_HEX = /^#[0-9A-Fa-f]{6}$/;
  const WZ_MASK = { JAX: '#C9CED4', BAL: '#111111', DEN: '#002244', CAR: '#C9CED4', SF: '#B3995D', LV: '#C9CED4', NO: '#111111', PIT: '#111111', CIN: '#111111', CLE: '#C9CED4', NYJ: '#111111', MIN: '#C9CED4', GB: '#203731', KC: '#C9CED4', MIA: '#C9CED4' };
  const WZ_HELM = {"ARI": "/_blob/09571d421c127f6d89d6d1b61ac36e34", "ATL": "/_blob/f430e62cad8429474e6781ba569fcf78", "BAL": "/_blob/e7fc80491d9cceb09aaca3daebd2086d", "BUF": "/_blob/1c2fd46bf09b7931a2e2d8af5eff2394", "CAR": "/_blob/af67c37bcc511aa333d21866f7ed8e78", "CHI": "/_blob/26c7f09335cf5e67b7e917d8de8b9503", "CIN": "/_blob/9502ca777fbbd183b181e741f642051c", "CLE": "/_blob/bf2befad46b875809d7a486ea90743c0", "DAL": "/_blob/96a6813952b792261c90e03454b0ad3f", "DEN": "/_blob/d5ee0e50da4ae669784f7af4007d8b34", "DET": "/_blob/48d289df31489df1108b6e2b682f1593", "GB": "/_blob/b3cc37ff0215640c7a5acc4715257eac", "HOU": "/_blob/51d6786a4c58b933b424cfa4430c87da", "IND": "/_blob/301591654a706c8710f569b80da4d3ed", "JAX": "/_blob/516e48c6498caefb267dbcd88b238e1e", "KC": "/_blob/6065affebe9d4d0af06501e58f788bf4", "LAC": "/_blob/330bdf4b39600f0638e56f1a64344372", "LAR": "/_blob/32bdd260cc1768e0986e18f1bc48c0f8", "LV": "/_blob/f4c0adb85c236fb8ad3a910dcba7a789", "MIA": "/_blob/b21888775ca2bdb561e656c1a25c1896", "MIN": "/_blob/94cba6405b4103d847a8181d561d7312", "NE": "/_blob/842b65077d5c519fb59ea696f09190e1", "NO": "/_blob/117ac8034e61e0d3b105f1ff75ebe2db", "NYG": "/_blob/31bee21053a52226e196ca158d20df8c", "NYJ": "/_blob/b3577ab4a4da785746a16734518e0e86", "PHI": "/_blob/0722fda8f6e76d7bd9a36f2e928a29f5", "PIT": "/_blob/b0662d2206bccb37a10a47c848eda7ce", "SEA": "/_blob/db8af5e4032948e3ffc288960cb5e7fe", "SF": "/_blob/36db7666653e819e3e09049c1b0f04f2", "TB": "/_blob/5c06a1a9a4f13e5a0c7bd2770467c4a2", "TEN": "/_blob/af0b09c1b89aa77410ebc2bfbf52f937", "WSH": "/_blob/209f075379d5b88eb4b9018a6c9919c4"};
  function wzHelmet(team, flip) {
    const src = WZ_HELM[team];
    if (!src) { const sp = el('span', 'wz-helm wz-helm-none'); sp.setAttribute('aria-hidden', 'true'); return sp; }
    const im = document.createElement('img'); im.src = src; im.alt = ''; im.width = 320; im.height = 277; im.decoding = 'async';
    im.className = 'wz-helm' + (flip ? ' flip' : ''); im.setAttribute('aria-hidden', 'true'); return im;
  }
  // the player's team for a line (from projections, prop groups and anytime TDs), for the team-color sheen
  let wzTM = null, wzTMn = -1;
  function wzPlayerTeam(r) {
    const P = dash.data('proj'), Q = dash.data('props'), A = dash.data('atd');
    const n = [P, Q, A].reduce((a, d) => a + (d.status === 'ok' ? d.data.length : 0), 0);
    if (n !== wzTMn) {
      wzTMn = n; wzTM = new Map();
      for (const d of [P, Q, A]) if (d.status === 'ok') for (const x of d.data) { const nm = x.player || String(x.contract || '').split(':')[0]; if (x.team && nm) wzTM.set(x.game + '|' + nm, x.team); }
    }
    return wzTM.get(r.game + '|' + String(r.player || r.contract || '').split(':')[0]) || null;
  }
  function wzTint(node, r) {
    const t = wzPlayerTeam(r); if (!t || !WZ_TEAMS[t]) return;
    node.classList.add('wz-tc'); node.style.setProperty('--tc1', WZ_TEAMS[t][1]); node.style.setProperty('--tc2', WZ_TEAMS[t][2]);
  }
  function wzGameInfo(rows, game) {
    let spread = null, total = null, ko = '', utc = '';
    for (const r of rows) {
      if (r.game !== game) continue;
      if (!ko) { ko = r.kickoff || ''; utc = r.kickoff_utc || ''; }
      if (total == null && num(r.game_total) != null) total = num(r.game_total);
      if (!spread) { const m = /Books: (\w+) by -?([\d.]+)/.exec(r.book_lines || ''); if (m) spread = [m[1], m[2]]; }
      if (spread && total != null && ko) break;
    }
    return { spread, total, ko, utc };
  }
  function wzMatchup(game) {
    const box = $('#wz-matchup'); if (!box) return;
    if (!game) { box.hidden = true; box.replaceChildren(); return; }
    const [a, h] = wzSides(game); if (!a) { box.hidden = true; return; }
    const la = dash.data('lines_all'), info = la.status === 'ok' ? wzGameInfo(la.data, game) : { spread: null, total: null, ko: '' };
    const side = (t, home) => {
      const d = el('div', 'wz-mt-side' + (home ? ' home' : '')); const txt = el('div'); txt.append(el('b', null, t), el('span', null, wzTeam(t)[0] + (home ? ' · home' : ' · away')));
      if (home) d.append(txt, wzHelmet(t, true)); else d.append(wzHelmet(t, false), txt);
      return d;
    };
    const mid = el('div', 'wz-mt-mid'); mid.append(el('span', 'wz-mt-at', '@'), el('span', 'wz-cap', info.ko || ''));
    const bits = []; if (info.spread) bits.push(`${info.spread[0]} by ${info.spread[1]}`); if (info.total != null) bits.push(`total ${info.total}`);
    if (bits.length) mid.append(el('span', 'wz-cap', bits.join(' · ')));
    box.style.setProperty('--ca', wzTeam(a)[1]); box.style.setProperty('--cb', wzTeam(h)[1]);
    box.setAttribute('aria-label', `${wzTeam(a)[0]} at ${wzTeam(h)[0]}${info.ko ? ', ' + info.ko : ''}`); box.setAttribute('role', 'group');
    box.replaceChildren(side(a, false), mid, side(h, true)); box.hidden = false;
    box.classList.remove('enter'); void box.offsetWidth; box.classList.add('enter');
  }

  // lobby: ticker, schedule, live example, kicker
  let wzTapeDone = false, wzSchedDone = false, wzExDone = false;
  const wzShort = (label) => String(label).replace(/^([^:]+):\s*/, (m0, n) => { const p = n.split(' ').filter((x) => !/^(Jr\.?|Sr\.?|II|III|IV|V)$/.test(x)); return (p[p.length - 1] || n) + ' '; });
  const wzSidePx = (r, side) => (side === 'Yes' ? num(r.yes_price) : (num(r.no_price) != null ? num(r.no_price) : (num(r.yes_bid) != null ? 100 - num(r.yes_bid) : null)));
  function wzTk(r, side, p, q) {
    const b = el('button', 'wz-tk'); b.type = 'button'; b.tabIndex = -1; wzTint(b, r);
    const g = el('b'); g.append(wzPips(r.game), r.game.replace(' @ ', '@'));
    b.append(g, el('span', null, wzShort(rhLabel(r.contract))), el('i', null, `${side} ${q}¢`), el('em', null, `Wedge ${Math.round(p)}%`));
    b.addEventListener('click', () => { if (r.sit_key) { const ctx = { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source }; ctx.key = `${ctx.game}|${ctx.market}|${r.contract}`; openSit(r, ctx, b); } });
    return b;
  }
  function wzFill(track, items) {
    if (!track || !items.length) return;
    const one = items.map((x) => x()), two = items.map((x) => x());
    track.replaceChildren(...one, ...two); track.style.setProperty('--dur', Math.max(40, items.length * 5) + 's');
  }
  function wzLobby() {
    const ld = dash.data('lines'), la = dash.data('lines_all');
    if (!wzTapeDone && ld.status === 'ok' && la.status === 'ok') {
      wzTapeDone = true;
      const picks = ld.data.filter((r) => r.sit_pick && num(r.sit_hit) != null).sort((a, b) => num(b.sit_pedge) - num(a.sit_pedge)).slice(0, 18);
      wzFill($('#wz-tape-1'), picks.map((r) => () => { const s2 = r.sit_pick, p = s2 === 'Yes' ? num(r.sit_hit) : 100 - num(r.sit_hit); return wzTk(r, s2, p, wzSidePx(r, s2)); }));
      const games = [...new Set(la.data.map((r) => r.game))]; const seen = new Set(picks.map((r) => r.id.replace(/^A/, '')));
      const more = [];
      for (const g of games) for (const [b, r] of wxGameReads(la.data, g).top.slice(0, 2)) if (!seen.has(String(r.id).replace(/^A/, ''))) more.push(() => wzTk(r, b.side, b.p, b.q));
      wzFill($('#wz-tape-2'), more.length ? more : picks.map((r) => () => wzTk(r, r.sit_pick, r.sit_pick === 'Yes' ? num(r.sit_hit) : 100 - num(r.sit_hit), wzSidePx(r, r.sit_pick))));
    }
    if (!wzSchedDone && la.status === 'ok') { wzSchedDone = true; wzSchedule(la.data); }
    if (!wzExDone && ld.status === 'ok') { wzExDone = true; wzExample(ld.data); }
  }
  function wzSchedule(rows) {
    const box = $('#wz-days'); if (!box) return;
    const G = new Map(); for (const r of rows) if (!G.has(r.game)) G.set(r.game, { ko: r.kickoff || '', utc: r.kickoff_utc || '' });
    const list = [...G.entries()].sort((a, b) => (a[1].utc < b[1].utc ? -1 : a[1].utc > b[1].utc ? 1 : a[0] < b[0] ? -1 : 1));
    const day = (u) => { try { return new Date(u).toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric', timeZone: 'America/Chicago' }); } catch (e) { return ''; } };
    const now = Date.now(), byDay = new Map();
    for (const [g, v] of list) { const d = day(v.utc) || 'This week'; if (!byDay.has(d)) byDay.set(d, []); byDay.get(d).push([g, v]); }
    const fav = wzP && wzP.team;
    let next = null;
    const cols = [...byDay.entries()].map(([d, gs]) => {
      const sec = el('div', 'wz-day'); sec.append(el('h3', null, d));
      for (const [g, v] of gs) {
        const b = el('button', 'wz-game'); b.type = 'button'; b.dataset.game = g;
        const [a, h] = wzSides(g); if (fav && (fav === a || fav === h)) b.classList.add('fav');
        const mid = el('span'); mid.append(el('b', null, `${wzTeam(a)[0]} at ${wzTeam(h)[0]}`), el('small', null, `${g} · ${String(v.ko).replace(/\s*(Thu|Fri|Sat|Sun|Mon)$/, '')}`));
        const off = v.utc && Date.parse(v.utc) <= now; const n = off ? 0 : wxGameReads(rows, g).top.length;
        if (!off && !next) next = [g, v];
        const st = el('span', 'wz-st' + (!off && n ? ' live' : ''), off ? 'Kicked off' : (n ? `${n} read${n === 1 ? '' : 's'}` : 'Lines open'));
        b.append(wzHelmPair(g), mid, st);
        b.addEventListener('click', () => { wxGame = g; try { localStorage.setItem('wx-read-game', g); } catch (e) { /* storage unavailable */ } wxDraw(); const t = $('#wz-reads'); if (t) t.scrollIntoView({ behavior: WZ_REDUCE ? 'auto' : 'smooth', block: 'start' }); });
        sec.append(b);
      }
      return sec;
    });
    box.replaceChildren(...cols);
    const k = $('#wz-kick'); if (k && next) k.textContent = `NFL · Week 9 · next up ${next[0]}, ${next[1].ko}`;
  }
  function wzExample(rows) {
    const box = $('#wz-example'); if (!box) return;
    const r = rows.filter((x) => x.sit_pick && x.sit_key && num(x.hits) != null && num(x.games)).sort((a, b) => num(b.sit_pedge) - num(a.sit_pedge))[0];
    if (!r) { box.replaceChildren(el('p', 'wx-empty', 'No live example right now.')); return; }
    const side = r.sit_pick, pS = side === 'Yes' ? num(r.sit_hit) : 100 - num(r.sit_hit), q = wzSidePx(r, side);
    const hh = num(r.hits), gg = num(r.games), k = side === 'Yes' ? hh : gg - hh;
    const row = (lab, val, note) => { const d = el('div'); d.append(el('span', null, lab), el('b', null, val)); if (note) d.append(el('small', null, note)); return d; };
    const grid = el('div', 'wz-ex-grid');
    grid.append(row('01 · This season', `${Math.round(100 * k / gg)}%`, `${side} in ${k} of ${gg} games${r.role ? ' · ' + r.role : ''}`),
      row('02 · Recent form', r.mom_type || '—', 'His last four games against his season. The defense, game script and weather are in the full read'),
      row('03 · Wedge % vs price', `${Math.round(pS)}% vs ${q}¢`, `${side}, ${Math.round(num(r.sit_pedge))} points better than the price`));
    const go = el('button', 'wz-btn wz-btn-g', 'Open the full read'); go.type = 'button';
    go.addEventListener('click', () => { const ctx = { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source }; ctx.key = `${ctx.game}|${ctx.market}|${r.contract}`; openSit(r, ctx, go); });
    const cap = el('span', 'wz-cap'); cap.append(`Live example · ${r.game} · ${r.kickoff}`);
    box.replaceChildren(cap, el('b', 'wz-ex-title', rhLabel(r.contract)), grid, go);
  }

  // accounts: a private Wedge profile per viewer, plan choice and checkout
  let wzP = null, wzRef = null, wzMe = '', wzPlan = 'monthly', wzMode = 'signup', wzDelArm = false;
  const wzDlg = $('#wz-dlg');
  async function wzInitAccount() {
    await new Promise((r) => setTimeout(r, 0));
    if (!WZ_ACCOUNTS) { wzHeader(); return; }
    const cl = window.claude; let db = null, user = null;
    if (cl && typeof cl.use === 'function') { try { [db, user] = await Promise.all([cl.use('db'), cl.use('user')]); } catch (e) { /* signed out or not granted */ } }
    let uid = null;
    if (user && typeof user.id === 'function') { try { uid = await user.id(); } catch (e) { uid = null; } }
    if (db && uid) { try { wzRef = db.doc(`data/users/${uid}/wedge-account`); const sn = await wzRef.get(); if (sn && sn.exists) wzP = sn.data(); } catch (e) { wzRef = null; } }
    if (!wzRef) { try { const t = localStorage.getItem('wedge-account'); if (t) wzP = JSON.parse(t); } catch (e) { /* storage unavailable */ } }
    if (user && typeof user.me === 'function') { try { const me = await user.me(); wzMe = ((me && me.name) || '').trim().split(/\s+/)[0] || ''; } catch (e) { /* no profile scope */ } }
    wzHeader(); wzPersonalize();
  }
  async function wzSave(p) {
    wzP = p;
    if (wzRef) { try { await wzRef.set(p); return true; } catch (e) { /* fall through */ } }
    try { if (p) localStorage.setItem('wedge-account', JSON.stringify(p)); else localStorage.removeItem('wedge-account'); return true; } catch (e) { return false; }
  }
  function wzHeader() {
    if (!WZ_ACCOUNTS) { ['#wz-login', '#wz-signup', '#wz-me', '#wz-gopro'].forEach((x) => { $(x).hidden = true; }); return; }
    const has = !!wzP;
    $('#wz-login').hidden = has; $('#wz-signup').hidden = has; $('#wz-me').hidden = !has;
    $('#wz-gopro').hidden = !has || wzP.plan !== 'free';
    if (has) {
      const nm = wzP.first || wzMe || 'Account';
      $('#wz-me-av').textContent = nm.slice(0, 1).toUpperCase(); $('#wz-me-name').textContent = nm;
      const pe = $('#wz-me-plan'); pe.textContent = wzP.plan === 'free' ? 'Free' : (wzP.status === 'active' ? 'Pro' : 'Pro · pending'); pe.className = wzP.plan === 'free' ? '' : 'pro';
    }
  }
  function wzPersonalize() {
    if (!wzP || !wzP.team) return;
    if (!wxGame) {
      const la = dash.data('lines_all');
      if (la.status === 'ok') { const g = [...new Set(la.data.map((r) => r.game))].find((x) => wzSides(x).includes(wzP.team)); if (g) { wxGame = g; wxDraw(); } }
    }
    document.querySelectorAll('.wz-game').forEach((b) => b.classList.toggle('fav', wzSides(b.dataset.game).includes(wzP.team)));
  }
  function wzShow(mode) {
    wzMode = mode;
    wzDlg.querySelectorAll('.wz-mode').forEach((m) => { m.hidden = m.dataset.mode !== mode; });
    const H = { signup: wzP ? 'Your Wedge account' : 'Create your Wedge account', login: 'Welcome back', account: 'Your Wedge account', done: 'You’re all set' };
    const S = { signup: 'Pick a plan. You can change it any time.', login: '', account: '', done: '' };
    if (!WZ_ACCOUNTS) { H.signup = 'Join Wedge Pro'; S.signup = 'Pick a plan. Checkout comes next.'; }
    $('#wz-dlg-h').textContent = H[mode]; const sub = $('#wz-dlg-sub'); sub.textContent = S[mode]; sub.hidden = !S[mode];
    if (mode === 'signup') {
      $('#wz-f-first').value = (wzP && wzP.first) || wzMe || ''; $('#wz-f-email').value = (wzP && wzP.email) || ''; $('#wz-f-team').value = (wzP && wzP.team) || '';
      wzPick(wzPlan); $('#wz-msg').textContent = '';
    }
    if (mode === 'account' && wzP) {
      const dl = $('#wz-acct-dl'); const row = (a, b) => { const d = el('div'); d.append(el('dt', null, a), el('dd', null, b)); return d; };
      dl.replaceChildren(row('Name', wzP.first || '—'), row('Email', wzP.email || '—'), row('Plan', WZ_PLANS[wzP.plan][0] + (wzP.plan !== 'free' && wzP.status !== 'active' ? ' · checkout pending' : '')),
        row('Favorite team', wzP.team ? wzTeam(wzP.team)[0] + ' (' + wzP.team + ')' : '—'));
      $('#wz-upgrade').hidden = wzP.plan !== 'free'; wzDelArm = false; $('#wz-delete').textContent = 'Delete my account';
    }
  }
  function wzOpen(mode) { wzShow(mode); if (!wzDlg.open) { try { wzDlg.showModal(); } catch (e) { wzDlg.setAttribute('open', ''); } } setTimeout(() => { const f = wzDlg.querySelector('.wz-mode:not([hidden]) input, .wz-mode:not([hidden]) .wz-btn'); if (f) f.focus(); }, 40); }
  function wzClose() { try { wzDlg.close(); } catch (e) { wzDlg.removeAttribute('open'); } }
  function wzPick(plan) {
    wzPlan = plan;
    wzDlg.querySelectorAll('.wz-planpick [data-plan]').forEach((b) => { const on = b.dataset.plan === plan; b.setAttribute('aria-checked', on ? 'true' : 'false'); b.tabIndex = on ? 0 : -1; });
    $('#wz-go').textContent = plan === 'free' ? (wzP ? 'Save my account' : 'Create my account') : 'Continue to checkout';
  }
  function wzCheckout(plan, p) {
    const link = $('#wz-done-link'), url = WZ_CHECKOUT[plan];
    if (url) {
      link.href = url; link.textContent = 'Open checkout again'; link.hidden = false;
      $('#wz-done-text').textContent = `Checkout for ${WZ_PLANS[plan][0]} (${WZ_PLANS[plan][1]}) opened in a new tab. Finish there and your access is set up.`;
    } else {
      const sub = `Wedge membership: ${WZ_PLANS[plan][0]} for ${p.first}`;
      const body = `Plan: ${WZ_PLANS[plan][0]} (${WZ_PLANS[plan][1]})\nName: ${p.first}\nEmail: ${p.email}\nFavorite team: ${p.team || 'none'}\n\nSent from the Wedge membership checkout.`;
      link.href = 'mailto:' + WEDGER_EMAIL + '?subject=' + encodeURIComponent(sub) + '&body=' + encodeURIComponent(body); link.textContent = 'Open the email again'; link.hidden = false;
      $('#wz-done-text').textContent = `Your email app opened with your ${WZ_PLANS[plan][0]} request filled in. Hit send and we'll reply with checkout and your access.`;
    }
    wzShow('done');
    try { link.click(); } catch (e) { /* the link stays for the visitor */ }
  }
  async function wzSubmit() {
    const msg = $('#wz-msg'); msg.textContent = '';
    const f = $('#wz-f-first'), e = $('#wz-f-email'); [f, e].forEach((x) => x.removeAttribute('aria-invalid'));
    const first = f.value.trim(), email = e.value.trim(), team = $('#wz-f-team').value;
    if (!first) { f.setAttribute('aria-invalid', 'true'); f.focus(); msg.textContent = 'Please add your first name.'; return; }
    if (!EMAIL_RE.test(email)) { e.setAttribute('aria-invalid', 'true'); e.focus(); msg.textContent = 'Please enter a valid email address.'; return; }
    if (!WZ_ACCOUNTS) { if (wzPlan === 'free') wzPlan = 'monthly'; wzCheckout(wzPlan, { first, email, team }); return; }
    const was = wzP; const now = new Date().toISOString();
    const keepActive = was && was.plan === wzPlan && was.status === 'active';
    const p = { first, email, team, plan: wzPlan, status: wzPlan === 'free' || keepActive ? 'active' : 'pending', created: (was && was.created) || now, updated: now };
    const ok = await wzSave(p);
    wzHeader(); wzPersonalize();
    if (wzPlan !== 'free' && !keepActive) { wzCheckout(wzPlan, p); return; }
    $('#wz-done-link').hidden = true;
    $('#wz-done-text').textContent = (was ? 'Your details are saved.' : `Welcome to Wedge, ${first}.`) + (ok ? '' : ' (Saved for this visit only.)') + (team ? ` The lobby now opens on ${wzTeam(team)[0]}'s game.` : '');
    wzShow('done');
  }
  function wzJoin(plan) {
    if (!WZ_ACCOUNTS && plan === 'free') { showPage('lobby'); const t = $('#wz-reads'); if (t) t.scrollIntoView({ behavior: WZ_REDUCE ? 'auto' : 'smooth', block: 'start' }); return; }
    wzPlan = plan || 'monthly';
    if (wzP && wzP.email && plan !== 'free') {
      if (wzP.plan === plan && wzP.status === 'active') { wzOpen('account'); return; }
      const p = Object.assign({}, wzP, { plan, status: 'pending', updated: new Date().toISOString() });
      wzSave(p).then(() => wzHeader());
      wzOpen('done'); wzCheckout(plan, p); return;
    }
    if (wzP && plan === 'free') { wzOpen('account'); return; }
    wzOpen('signup');
  }
  $('#wz-login').addEventListener('click', () => wzOpen(wzP ? 'account' : 'login'));
  $('#wz-signup').addEventListener('click', () => { wzPlan = 'monthly'; wzOpen('signup'); });
  $('#wz-me').addEventListener('click', () => wzOpen('account'));
  $('#wz-dlg-x').addEventListener('click', wzClose);
  $('#wz-done-ok').addEventListener('click', wzClose);
  $('#wz-go').addEventListener('click', wzSubmit);
  $('#wz-upgrade').addEventListener('click', () => { wzPlan = 'monthly'; wzShow('signup'); });
  $('#wz-delete').addEventListener('click', async () => {
    const b = $('#wz-delete');
    if (!wzDelArm) { wzDelArm = true; b.textContent = 'Select again to delete'; return; }
    if (wzRef) { try { await wzRef.delete(); } catch (e) { /* keep going */ } }
    try { localStorage.removeItem('wedge-account'); } catch (e) { /* storage unavailable */ }
    wzP = null; wzHeader(); wzClose();
  });
  wzDlg.addEventListener('click', (e) => { if (e.target === wzDlg) wzClose(); });
  wzDlg.querySelectorAll('[data-wz-to]').forEach((b) => b.addEventListener('click', () => wzShow(b.dataset.wzTo)));
  const wzPickBtns = [...wzDlg.querySelectorAll('.wz-planpick [data-plan]')];
  wzPickBtns.forEach((b, i) => {
    b.addEventListener('click', () => wzPick(b.dataset.plan));
    b.addEventListener('keydown', (e) => { if (!['ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp'].includes(e.key)) return; e.preventDefault(); const n = wzPickBtns[(i + (/Right|Down/.test(e.key) ? 1 : wzPickBtns.length - 1)) % wzPickBtns.length]; wzPick(n.dataset.plan); n.focus(); });
  });
  ['#wz-f-first', '#wz-f-email'].forEach((sel) => $(sel).addEventListener('keydown', (e) => { if (e.key === 'Enter') wzSubmit(); }));
  document.querySelectorAll('[data-wz-join]').forEach((b) => b.addEventListener('click', () => wzJoin(b.dataset.wzJoin)));
  document.querySelectorAll('[data-wz-jump]').forEach((b) => b.addEventListener('click', () => { const t = document.getElementById(b.dataset.wzJump); if (t) t.scrollIntoView({ behavior: WZ_REDUCE ? 'auto' : 'smooth', block: 'start' }); }));

  // tables: simple columns by default, extra filters folded away
  const WZ_DETAIL = {
    'lines-table': ['kickoff', 'market', 'source', 'yes_bid', 'role', 'mom_type', 'hits', 'games', 'sample', 'season_results', 'flags'],
    'rc': ['kickoff', 'market', 'pos', 'team', 'team_ml', 'opp_rank_vs_pos', 'source', 'role', 'mom_type', 'hits', 'games', 'season_results', 'flags'],
    'proj-table': ['kickoff', 'pos', 'team', 'p_over', 'mom_p', 'role', 'mom_type', 'games', 'flags'],
    'atd-table': ['pos', 'team', 'kickoff', 'source', 'atd_hits', 'games', 'rz_opps_pg', 'rz_tgt_share', 'rate_minus_price', 'td_log', 'flags'],
    'nba-table': ['kickoff', 'market', 'yes_bid', 'book_fair', 'hits', 'games', 'sample', 'season_results', 'flags'],
  };
  const WZ_FOLD = '.rs-src, .rs-group, .rs-mom, .rs-role, .rc-role, .rc-mom, .nb-group, .nb-mkt';
  let wzDetailed = false; try { wzDetailed = localStorage.getItem('wedge-cols') === 'all'; } catch (e) { /* storage unavailable */ }
  function wzTables() {
    const css = [], toggles = [];
    for (const t of document.querySelectorAll('table.rs-table')) {
      const key = WZ_DETAIL[t.id] ? t.id : (t.classList.contains('rc-table') ? 'rc' : null); if (!key || !t.id || !t.tHead) continue;
      [...t.tHead.rows[0].cells].forEach((th, i) => { if (WZ_DETAIL[key].includes(th.dataset.field)) css.push(`#${t.id}.wz-simple > thead > tr > :nth-child(${i + 1}), #${t.id}.wz-simple > tbody > tr > :nth-child(${i + 1})`); });
      t.classList.toggle('wz-simple', !wzDetailed);
      const card = t.closest('.rs-card'), ctr = card && card.querySelector('.rs-controls'); if (!ctr || ctr.querySelector('.wz-cols')) continue;
      const fold = [...ctr.children].filter((c) => c.matches(WZ_FOLD) || (c.tagName === 'LABEL' && c.querySelector('input[type="checkbox"]')));
      if (fold.length) {
        const d = el('details', 'wz-filters'), sm = el('summary', null, 'More filters'), inner = el('div', 'wz-filters-in');
        d.append(sm, inner); fold.forEach((c) => inner.append(c));
        const upd = () => { const n = fold.filter((c) => (c.tagName === 'SELECT' ? !!c.value : !!(c.querySelector('input') || {}).checked)).length; const old = sm.querySelector('b'); if (old) old.remove(); if (n) sm.append(el('b', null, String(n))); };
        inner.addEventListener('change', upd);
        const cnt = ctr.querySelector('.rs-count'); ctr.insertBefore(d, cnt || null);
      }
      const b = el('button', 'wz-btn wz-btn-line wz-btn-sm wz-cols'); b.type = 'button'; b.setAttribute('aria-pressed', wzDetailed ? 'true' : 'false'); b.textContent = wzDetailed ? 'Fewer columns' : 'More columns';
      b.addEventListener('click', () => { wzDetailed = !wzDetailed; try { localStorage.setItem('wedge-cols', wzDetailed ? 'all' : 'simple'); } catch (e) { /* storage unavailable */ } document.querySelectorAll('table.rs-table').forEach((x) => { if (x.dataset.wzs) x.classList.toggle('wz-simple', !wzDetailed); }); toggles.forEach((x) => { x.textContent = wzDetailed ? 'Fewer columns' : 'More columns'; x.setAttribute('aria-pressed', wzDetailed ? 'true' : 'false'); }); });
      toggles.push(b); ctr.append(b); t.dataset.wzs = '1';
    }
    const st = document.createElement('style'); st.textContent = css.length ? css.join(',\n') + ' { display: none; }' : ''; document.head.append(st);
    document.addEventListener('click', (e) => { document.querySelectorAll('details.wz-filters[open]').forEach((d) => { if (!d.contains(e.target)) d.open = false; }); });
  }
  // a touchdown line names only the player; with the market column folded away, say which market it is
  function wzLabel(r) { const lab = rhLabel(r.contract); return /:/.test(lab) || !/Touchdown/i.test(r.market || '') ? lab : lab + ' · ' + (r.market === 'Anytime Touchdown' ? 'anytime TD' : String(r.market).replace(/Touchdowns?/i, 'TDs')); }
  function wzInj(cell, flags) {
    const f = String(flags || ''); const m = /Injury report: (Questionable|Doubtful|Out|Limited in practice)/.exec(f); if (!m) return;
    const t = el('span', 'wz-inj', m[1] === 'Limited in practice' ? 'LTD' : m[1].slice(0, 1)); t.title = f; t.setAttribute('aria-label', 'Injury report: ' + m[1]); cell.append(t);
  }

  // motion: reveal, ripple, spotlight
  function wzMotion() {
    const paper = $('.wg-paper'); if (paper) paper.classList.add('wz-js');
    const rv = [...document.querySelectorAll('.wz-reveal')];
    if (WZ_REDUCE || !('IntersectionObserver' in window)) rv.forEach((x) => x.classList.add('wz-in'));
    else { const io = new IntersectionObserver((es) => es.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('wz-in'); io.unobserve(en.target); } }), { rootMargin: '0px 0px -8% 0px', threshold: 0.06 }); rv.forEach((x) => io.observe(x)); }
    if (WZ_REDUCE) return;
    document.addEventListener('pointerdown', (e) => {
      const t = e.target.closest('.wz-btn, .wx-tab, .wz-game, .wz-planpick button, .wz-me'); if (!t) return;
      const r = t.getBoundingClientRect(), d = Math.max(r.width, r.height) * 2.2, sp = document.createElement('span');
      sp.className = 'wz-ripple'; sp.style.width = sp.style.height = d + 'px'; sp.style.left = (e.clientX - r.left - d / 2) + 'px'; sp.style.top = (e.clientY - r.top - d / 2) + 'px';
      if (getComputedStyle(t).position === 'static') t.style.position = 'relative';
      t.style.overflow = 'hidden'; t.append(sp); sp.addEventListener('animationend', () => sp.remove());
    });
    document.addEventListener('pointermove', (e) => {
      const t = e.target.closest && e.target.closest('.wz-spot'); if (!t) return;
      const r = t.getBoundingClientRect(); t.style.setProperty('--mx', (e.clientX - r.left) + 'px'); t.style.setProperty('--my', (e.clientY - r.top) + 'px');
    }, { passive: true });
  }
  // the NFL menu opens under its tab (the tab row scrolls sideways, so the menu is placed against the header)
  $('#nfl-btn').addEventListener('click', () => { const m = $('#nfl-menu'), t = $('.wz-top'), b = $('#nfl-btn'); if (!m || !t || !b) return; m.style.left = Math.max(8, b.getBoundingClientRect().left - t.getBoundingClientRect().left) + 'px'; });
  // the old membership page is replaced by the plans on the lobby
  document.querySelectorAll('[data-go="unlock"]').forEach((b) => { b.dataset.go = 'lobby'; b.dataset.scrollAfter = 'wz-plans'; });
  if (!WZ_ACCOUNTS) {
    const fp = wzDlg.querySelector('.wz-planpick [data-plan="free"]'); if (fp) fp.hidden = true;
    const pp = wzDlg.querySelector('.wz-planpick'); if (pp) pp.style.gridTemplateColumns = 'repeat(2, minmax(0, 1fr))';
    const fine = wzDlg.querySelector('.wz-mode[data-mode="signup"] .wz-dlg-fine'); if (fine) fine.textContent = 'Paid plans go straight to checkout.';
    document.querySelectorAll('[data-wz-join="free"]').forEach((b) => { b.textContent = 'Start browsing'; });
  }
  wzTables(); wzMotion(); wzInitAccount();

  // ================= Wedge round 3: words, game cells, helmet pairs, analyst picks by team =================
  function wzWords(label) {
    const b = el('b', 'wx-read-title');
    String(label).split(/(\s+)/).forEach((w, k) => { if (/^\s+$/.test(w)) b.append(w); else { const sp = el('span', 'pf-w', w); sp.style.setProperty('--i', String(k)); b.append(sp); } });
    return b;
  }
  function wzGameCell(cell, game) {
    const [a, h] = wzSides(game); if (!cell || !a || !WZ_TEAMS[a] || !WZ_TEAMS[h]) return cell;
    const w = el('span', 'pf-gc'); w.append(wzPips(game), el('span', 'pf-tm', a), ' @ ', el('span', 'pf-tm', h));
    cell.textContent = ''; cell.append(w); return cell;
  }
  function wzHelmPair(game) {
    const [a, h] = wzSides(game), p = el('span', 'pf-hp'); p.setAttribute('aria-hidden', 'true');
    p.append(wzHelmet(a, false), wzHelmet(h, true)); return p;
  }
  // a player's team by name alone (past weeks' games aren't in this week's data); only trusted when it's one of the game's two teams
  let wzNM = null, wzNMn = -1;
  function wzNameTeam(name) {
    const P = dash.data('proj'), Q = dash.data('props'), A = dash.data('atd');
    const n = [P, Q, A].reduce((x, d) => x + (d.status === 'ok' ? d.data.length : 0), 0);
    if (n !== wzNMn) { wzNMn = n; wzNM = new Map(); for (const d of [P, Q, A]) if (d.status === 'ok') for (const x of d.data) { const nm = x.player || String(x.contract || '').split(':')[0]; if (x.team && nm && !wzNM.has(nm)) wzNM.set(nm, x.team); } }
    return wzNM.get(String(name || '').trim()) || null;
  }
  let pfTeam = null;
  function wzPickTeam(v) {
    const [a, h] = wzSides(v.game); const con = String(v.contract || '');
    let t = wzPlayerTeam({ game: v.game, contract: con.split(':')[0] });
    if (!t && a) { const n = wzNameTeam(con.split(':')[0]); if (n === a || n === h) t = n; }
    if (!t && a) for (const x of [a, h]) { const nm = (WZ_TEAMS[x] || [])[0]; if ((nm && con.startsWith(nm)) || new RegExp('\\b' + x + '\\b').test(con)) { t = x; break; } }
    return t && WZ_TEAMS[t] ? t : 'ALL';
  }
  function wzTeamPicks() {
    const grid = $('#pf-tgrid'), panel = $('#pf-tpanel'); if (!grid) return;
    const idx = pickIndex(), by = new Map();
    for (const name of analysts.order) for (const k of (analysts.picks[name] || [])) {
      const v = Object.assign({ who: name }, pickInfo(idx, k)); const t = wzPickTeam(v);
      if (!by.has(t)) by.set(t, []); by.get(t).push(v);
    }
    if (document.querySelector('.rs-wrap.wg-owner')) { const d = $('#pf-allpicks'); if (d && !d.dataset.auto) { d.open = true; d.dataset.auto = '1'; } }
    if (!by.size) { grid.replaceChildren(el('p', 'wx-empty', 'No analyst picks yet.')); panel.hidden = true; return; }
    const rec = (L) => { const w = L.filter((x) => x.outcome === 'Won').length, l = L.filter((x) => x.outcome === 'Lost').length, pe = L.filter((x) => x.outcome === 'Pending').length; return { w, l, pe }; };
    const teams = [...by.keys()].sort((x, y) => (x === 'ALL') - (y === 'ALL') || by.get(y).length - by.get(x).length || (x < y ? -1 : 1));
    if (!pfTeam || !by.has(pfTeam)) pfTeam = teams[0];
    grid.replaceChildren(...teams.map((t) => {
      const L = by.get(t), r = rec(L), b = el('button', 'pf-tt'); b.type = 'button'; b.dataset.team = t; b.setAttribute('aria-pressed', t === pfTeam ? 'true' : 'false');
      if (t !== 'ALL') { b.style.setProperty('--tc1', WZ_TEAMS[t][1]); b.style.setProperty('--tc2', WZ_TEAMS[t][2]); } else { b.style.setProperty('--tc1', '#8A8F95'); b.style.setProperty('--tc2', '#E0E2E5'); }
      b.append(t === 'ALL' ? el('span', 'wz-helm wz-helm-none') : wzHelmet(t, false), el('b', null, t === 'ALL' ? 'More' : t), el('span', null, t === 'ALL' ? 'Totals and game lines' : WZ_TEAMS[t][0]),
        el('small', null, `${L.length} pick${L.length === 1 ? '' : 's'} · ${r.w}–${r.l}${r.pe ? ' · ' + r.pe + ' pending' : ''}`));
      b.setAttribute('aria-label', `${t === 'ALL' ? 'Totals and game lines' : WZ_TEAMS[t][0]}: ${L.length} picks, ${r.w} won, ${r.l} lost`);
      b.addEventListener('click', () => { pfTeam = t; grid.querySelectorAll('.pf-tt').forEach((x) => x.setAttribute('aria-pressed', x.dataset.team === t ? 'true' : 'false')); wzTeamPanel(t, by.get(t)); });
      return b;
    }));
    wzTeamPanel(pfTeam, by.get(pfTeam));
  }
  function wzTeamPanel(t, L) {
    const panel = $('#pf-tpanel'); if (!panel || !L) return;
    const head = el('div', 'pf-tpanel-h'); const txt = el('div');
    const w = L.filter((x) => x.outcome === 'Won').length, l = L.filter((x) => x.outcome === 'Lost').length;
    txt.append(el('b', null, t === 'ALL' ? 'Totals and game lines' : WZ_TEAMS[t][0] + ' · ' + t), el('span', null, `${L.length} analyst pick${L.length === 1 ? '' : 's'} · ${w}–${l} settled`));
    head.append(t === 'ALL' ? el('span') : wzHelmet(t, false), txt);
    const rows = L.slice().sort((x, y) => (Number(y.week) || 0) - (Number(x.week) || 0)).map((v) => {
      const r = el('div', 'pf-pick'); const av = el('span', 'wz-av', String(v.who).slice(0, 1).toUpperCase()); av.setAttribute('aria-hidden', 'true');
      const mid = el('div'); mid.append(el('b', null, v.contract ? (/:/.test(rhLabel(v.contract)) || !/Touchdown/i.test(v.market || '') ? rhLabel(v.contract) : rhLabel(v.contract) + ' · anytime TD') : '—'), el('small', null, `${v.who} · Week ${v.week || '—'} · ${v.game || ''}`));
      const px = el('span', 'pf-px', v.yes_price !== '' && v.yes_price != null ? v.yes_price + '¢' : '');
      const oc = v.outcome || 'Pending', pr = num(v.profit_c);
      const chip = el('span', 'wz-chip ' + (oc === 'Won' ? 'pos' : oc === 'Lost' ? 'neg' : 'flat'), oc === 'Won' || oc === 'Lost' ? `${oc}${pr != null ? ' ' + (pr > 0 ? '+' : pr < 0 ? '−' : '') + Math.abs(pr) + '¢' : ''}` : oc);
      r.append(av, mid, px, chip); return r;
    });
    panel.replaceChildren(head, ...rows); panel.hidden = false;
    panel.style.animation = 'none'; void panel.offsetWidth; panel.style.animation = '';
  }

  // ---------------- render ----------------
  dash.onData(() => {
    const s = dash.data('summary'), cc = dash.data('cat_counts'), at = dash.data('atd_summary');
    document.querySelectorAll('[data-source="summary"][data-field], [data-source="atd_summary"][data-field]').forEach((el) => {
      const src = dash.data(el.dataset.source);
      if (src.status === 'ok' && src.data[0]) { el.classList.remove('dash-skeleton'); el.textContent = fmt(src.data[0][el.dataset.field]); }
      else el.textContent = '—';
    });
    document.querySelectorAll('[data-source="cat_counts"][data-field], [data-source="w6_summary"][data-field], [data-source="hist_perms"][data-field]').forEach((el) => {
      const src = dash.data(el.dataset.source);
      const where = [...new URLSearchParams(el.dataset.where).entries()];
      const row = src.status === 'ok' ? src.data.find((r) => where.every(([k, v]) => String(r[k]) === v)) : null;
      const v = row ? row[el.dataset.field] : null;
      if (row && v != null) {
        el.classList.remove('dash-skeleton');
        el.textContent = el.dataset.fmt === 'pct' ? v + '%' : (el.dataset.fmt === 'signed' ? signed(v) : fmt(v));
      } else el.textContent = '—';
    });
    const box = $('.rs-games');
    const g = dash.data('by_game');
    const ld = dash.data('lines');
    const totals = new Map(ld.status === 'ok' ? ld.data.map((x) => [x.game, x.game_total]) : []);
    if (g.status === 'ok') {
      const rows = g.data.slice().sort((a, b) => String(a.kickoff_utc).localeCompare(String(b.kickoff_utc)) || a.game.localeCompare(b.game));
      const max = d3.max(rows, (r) => r.inband) || 1;
      box.replaceChildren(...rows.map((r) => {
        const row = document.createElement('div'); row.className = 'rs-grow';
        const name = document.createElement('div'); name.textContent = r.game; totalStar(name, { game_total: totals.get(r.game) });
        const bar = document.createElement('div'); bar.className = 'rs-gbar';
        const a = document.createElement('span'); a.style.width = (r.inband / max * 100) + '%'; a.style.background = 'var(--cds-chart-muted)';
        const b = document.createElement('span'); b.style.width = (r.qualifying / max * 100) + '%'; b.style.background = 'var(--wg-green)';
        bar.append(a, b);
        const val = document.createElement('div'); val.style.textAlign = 'right'; val.textContent = `${r.qualifying} / ${r.inband}`;
        row.append(name, bar, val);
        return row;
      }));
    } else box.replaceChildren();
    document.querySelectorAll('.rs-sw-a').forEach((e) => { e.style.background = 'var(--cds-chart-muted)'; });
    document.querySelectorAll('.rs-sw-b').forEach((e) => { e.style.background = 'var(--wg-green)'; });

    drawLines();
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
    drawBtPerms();
    drawBtLines();
    drawCharts();
  });
})();
