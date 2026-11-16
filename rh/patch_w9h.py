"""Week 9 final card (Sat Nov 7 evening): every remaining game run through 'How we build the final lines'.
Adds NFL > Week 9 final card: a summary board of final lines and leans, then one card per game with the market and
lineup, keys to win for both teams, three scripts, the plays with their evidence and break-even, rankings, and the
considered-and-passed list. Data comes from final.js (window.WZ_FINAL), published as its own file."""
P = '/home/claude/wedger/rh/index.html'
s = open(P).read()

def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (a[:70], c); s = s.replace(a, b)

# menu item, first in the Week 9 group
rep('<div class="wg-dd-label" aria-hidden="true">Week 9</div>\n        <button type="button" class="wg-dd-item" role="menuitem" data-page="lines">Week 9 lines</button>',
    '<div class="wg-dd-label" aria-hidden="true">Week 9</div>\n        <button type="button" class="wg-dd-item" role="menuitem" data-page="final">Week 9 final card</button>\n        <button type="button" class="wg-dd-item" role="menuitem" data-page="lines">Week 9 lines</button>')

# page markup, before projections
rep('  <div class="rs-page" id="proj" hidden>',
    '''  <div class="rs-page" id="final" hidden>
    <header class="wx-band"><span class="wx-label"><i class="wx-dot" aria-hidden="true"></i>NFL / Week 9</span><h2>Final card.</h2><p>Every remaining game, every threshold, any price<br><span id="fc-when">Prices checked Sat Nov 7</span></p></header>
    <div id="fc-root"><p class="wx-empty">Loading the final card…</p></div>
  </div>
  <div class="rs-page" id="proj" hidden>''')

# navigation: an NFL page, but its own method (not the long methodology card)
rep("const NFL_PAGES = new Set(['lines', 'proj',", "const NFL_PAGES = new Set(['final', 'lines', 'proj',")
rep("const METHOD_PAGES = new Set([...NFL_PAGES, 'charts']);", "const METHOD_PAGES = new Set([...NFL_PAGES, 'charts']); METHOD_PAGES.delete('final');")
rep("    if (id === 'charts') requestAnimationFrame(() => drawCharts());",
    "    if (id === 'charts') requestAnimationFrame(() => drawCharts());\n    if (id === 'final') requestAnimationFrame(() => fcRender());")

JS = r'''
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
'''
rep("  // ---------------- navigation ----------------", JS + "\n  // ---------------- navigation ----------------")

CSS = '''<style>
#final .fc-top{display:grid;gap:18px}
.fc-stats{display:flex;flex-wrap:wrap;gap:10px}
.fc-stat{flex:1 1 140px;min-width:0;padding:14px 16px;border:1px solid var(--pf-line);border-radius:10px;background:var(--pf-glass)}
.fc-stat b{display:block;font-family:var(--pf-wide);font-size:clamp(30px,4vw,44px);font-weight:800;line-height:1;letter-spacing:-.03em;color:var(--pf-ink);font-variant-numeric:tabular-nums}
.fc-stat span{display:block;margin-top:6px;font-family:var(--wx-mono);font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--pf-muted)}
.fc-stat.g b{color:#3fd17f}
.fc-lede{margin:0;max-width:78ch;font-size:16px;line-height:1.55;color:var(--pf-ink)}
.fc-how{border:1px solid var(--pf-line);border-radius:10px;padding:10px 14px;background:var(--pf-glass)}
.fc-how>summary{cursor:pointer;font-weight:600;color:var(--pf-ink)}
.fc-dl{display:grid;grid-template-columns:minmax(120px,170px) minmax(0,1fr);gap:8px 16px;margin:12px 0 0}
.fc-dl dt{font-family:var(--wx-mono);font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:var(--pf-muted);padding-top:2px}
.fc-dl dd{margin:0;font-size:15px;line-height:1.5;color:var(--pf-ink)}
.fc-badge{display:inline-block;padding:3px 9px;border-radius:999px;font-family:var(--wx-mono);font-size:11.5px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;white-space:nowrap;border:1px solid transparent}
.fc-badge.fc-final{background:var(--wz-g);color:#fff}
.fc-badge.fc-lean{border-color:var(--pf-muted);color:var(--pf-ink)}
.fc-badge.fc-pass{border-color:var(--pf-line);color:var(--pf-faint)}
.fc-board .rs-table td{vertical-align:top}
.fc-row{cursor:pointer;transition:background .15s ease}
.fc-row:hover,.fc-row:focus-visible{background:var(--pf-glass-hi);outline:none}
.fc-line{font-weight:600;color:var(--pf-ink);min-width:220px}
.fc-n{font-family:var(--wx-mono);font-variant-numeric:tabular-nums;white-space:nowrap}
.fc-us{color:#3fd17f}
.fc-cond{font-size:13px;color:var(--pf-muted);min-width:200px}
.fc-games{display:grid;gap:12px;margin-top:18px}
.fc-game{position:relative;border:1px solid var(--pf-line);border-radius:12px;background:var(--pf-glass);overflow:hidden}
.fc-game:before{content:"";position:absolute;left:0;top:0;bottom:0;width:5px;background:linear-gradient(var(--ga),var(--gh))}
.fc-game[open]{background:var(--pf-glass-hi)}
.fc-sum{display:flex;align-items:center;gap:14px;padding:12px 16px 12px 20px;cursor:pointer;list-style:none}
.fc-sum::-webkit-details-marker{display:none}
.fc-sum .pf-hp{flex:0 0 auto}
.fc-sum .pf-hp .wz-helm{width:44px;height:auto}
.fc-sum-name{flex:1 1 auto;min-width:0}
.fc-sum-name b{display:block;font-family:var(--pf-wide);font-size:20px;font-weight:800;letter-spacing:-.02em;color:var(--pf-ink)}
.fc-sum-name span{display:block;font-size:13px;color:var(--pf-muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.fc-sum-tags{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.fc-body{padding:4px 20px 20px 22px;display:grid;gap:18px}
.fc-sec h3{margin:0 0 8px;font-family:var(--wx-mono);font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--pf-muted)}
.fc-sec p{margin:0 0 8px;font-size:15px;line-height:1.55;color:var(--pf-ink)}
.fc-branch{border-left:2px solid var(--pf-muted);padding-left:10px}
.fc-keys{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.fc-key{border:1px solid var(--pf-line);border-top:3px solid var(--tc);border-radius:10px;padding:12px 14px;background:rgba(0,0,0,.12)}
.fc-key h4{margin:0;font-size:16px;color:var(--pf-ink)}
.fc-key .fc-dl{grid-template-columns:1fr;gap:2px 0}
.fc-key .fc-dl dd{margin-bottom:8px}
.fc-play{border:1px solid var(--pf-line);border-radius:10px;padding:14px 16px;margin-bottom:12px;background:rgba(0,0,0,.14)}
.fc-play.fc-p-final{border-color:color-mix(in srgb,var(--wz-g) 70%,transparent);box-shadow:inset 3px 0 0 var(--wz-g)}
.fc-play-top{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.fc-play-top h4{margin:0;font-size:18px;color:var(--pf-ink)}
.fc-px{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:12px 0}
.fc-pxc{padding:8px 10px;border:1px solid var(--pf-line);border-radius:8px}
.fc-pxc span{display:block;font-family:var(--wx-mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--pf-muted)}
.fc-pxc b{display:block;margin-top:2px;font-family:var(--pf-wide);font-size:20px;font-weight:800;color:var(--pf-ink);font-variant-numeric:tabular-nums}
.fc-pxc.fc-us b{color:#3fd17f}
.fc-why{font-size:15.5px;font-weight:500;margin:0 0 4px}
.fc-brk{margin:10px 0 0;font-family:var(--wx-mono);font-size:12px;line-height:1.5;color:var(--pf-faint)}
.fc-none{color:var(--pf-muted)}
.fc-rank{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.fc-rank h4{margin:0 0 6px;font-size:14px;color:var(--pf-ink)}
.fc-rank ol{margin:0;padding-left:20px;color:var(--pf-ink);font-size:14.5px;line-height:1.55}
.fc-passed,.fc-src{margin:0;padding:0;list-style:none;display:grid;gap:10px}
.fc-passed li{display:grid;gap:3px;padding:10px 12px;border:1px solid var(--pf-line);border-radius:8px}
.fc-passed b{color:var(--pf-ink);font-size:15px}
.fc-passed span{color:var(--pf-ink);font-size:14.5px;line-height:1.5}
.fc-passed em{font-style:normal;color:var(--pf-muted);font-size:13.5px}
.fc-ev p,.fc-dec p{margin:0 0 6px;font-size:15px;line-height:1.5;color:var(--pf-ink)}
.fc-ev b,.fc-dec b{font-weight:600}
.fc-lad{margin-top:10px;border-top:1px solid var(--pf-line);padding-top:8px}
.fc-lad>summary{cursor:pointer;font-family:var(--wx-mono);font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--pf-muted)}
.fc-ladbox{margin-top:8px;max-height:420px;overflow:auto}
.fc-ladbox .rs-table th,.fc-ladbox .rs-table td{padding:6px 10px;font-size:13.5px}
.fc-lt b{font-weight:600;color:var(--pf-ink)}
.fc-lside{color:var(--pf-muted);font-size:12px}
.fc-ltag{display:inline-block;margin-left:8px;padding:1px 7px;border-radius:999px;font-family:var(--wx-mono);font-size:10.5px;letter-spacing:.04em;text-transform:uppercase;border:1px solid var(--pf-muted);color:var(--pf-ink);white-space:nowrap}
.fc-lr-card{background:color-mix(in srgb,var(--wz-g) 16%,transparent)}
.fc-lr-card .fc-ltag{background:var(--wz-g);border-color:var(--wz-g);color:#fff}
.fc-lr-alt{background:var(--pf-glass-hi)}
.fc-body{grid-template-columns:minmax(0,1fr)}
.fc-sec,.fc-play,.fc-lad,.fc-rank>div{min-width:0}
.fc-dl dd{min-width:0;overflow-wrap:anywhere}
.fc-board .fc-cond{white-space:normal}
.fc-rsub{margin:0 0 6px;font-size:12.5px;color:var(--pf-muted)}
.fc-sk{display:inline-block;min-width:76px;margin-right:8px;font-family:var(--wx-mono);font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--pf-muted)}
.fc-src a{color:var(--pf-ink);text-decoration:underline;text-underline-offset:3px;text-decoration-color:var(--pf-muted)}
.fc-post{margin:18px 0 0;font-size:14px;color:var(--pf-muted);max-width:78ch}
@media (max-width:640px){
 .fc-px{grid-template-columns:repeat(2,minmax(0,1fr))}
 .fc-dl{grid-template-columns:1fr;gap:2px}
 .fc-dl dd{margin-bottom:8px}
 .fc-sum{flex-wrap:wrap}
 .fc-sum .pf-hp{display:none}
 .fc-body{padding:4px 14px 16px 16px}
 .fc-line,.fc-cond{min-width:160px}
 .fc-ltag{display:table;margin:3px 0 0}
}
</style>
'''
rep('  <div class="rs-page" id="final" hidden>', CSS + '  <div class="rs-page" id="final" hidden>')
rep('<div class="pf-row"><button type="button" class="wz-btn wz-btn-line" id="wx-reads-more" data-go="lines" data-wg-show="pick" data-wg-game="">All <span data-wg-count="picks">40</span> reads ↗</button>',
    '<div class="pf-row"><button type="button" class="wz-btn wz-btn-line" id="wx-reads-more" data-go="lines" data-wg-show="pick" data-wg-game="">All <span data-wg-count="picks">40</span> reads ↗</button><button type="button" class="wz-btn wz-btn-line" data-go="final">Week 9 final card ↗</button>')
open(P, 'w').write(s)
print('final card patched')
