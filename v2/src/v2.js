  // ================= V2 · the Wedge: Home matchups, Research files, The Winning Edge, Thesis, ink =================
  const v2Norm = (n) => String(n || '').trim().replace(/\s+(Jr\.?|Sr\.?|II|III|IV|V)$/i, '').toLowerCase().replace(/[^a-z]/g, '');
  const v2F = () => window.WZ_FINAL || null;
  const v2Card = (g) => { const F = v2F(); return (F && F.cards && F.cards.find((c) => c.game === g)) || null; };
  const v2Kick = (c) => String(c.kick || '').replace(/\s*CT.*$/, '');
  const v2Counts = (c) => { const f = c.plays.filter((p) => p.decision === 'Final line').length; return [f, c.plays.length - f]; };
  function v2PlayN(g) { const c = v2Card(g); return c ? c.plays.length : 0; }
  function v2PlayTag(g) {
    const c = v2Card(g); if (!c) return 'Lines open';
    const [f, l] = v2Counts(c);
    return f || l ? [f ? `${f} final` : '', l ? `${l} lean${l > 1 ? 's' : ''}` : ''].filter(Boolean).join(' · ') : 'Pass';
  }
  const V2_STAT = { 'Receiving Yards': 'recyd', Receptions: 'rec', 'Rushing Yards': 'rushyd', 'Passing Yards': 'passyd', 'Rushing + Receiving Yards': 'rryd',
    'Passing Touchdowns': 'passtd', Interceptions: 'int', 'Anytime Touchdown': 'td', '2+ Touchdowns': 'td', '3+ Touchdowns': 'td' };
  const V2_WORD = { receptions: 'Receptions', 'receiving yards': 'Receiving Yards', 'rushing yards': 'Rushing Yards', 'passing yards': 'Passing Yards' };
  const v2LineOf = (r) => {
    const m = /Over (\d+(?:\.\d+)?)/.exec(r.contract || ''); if (m) return +m[1];
    return { 'Anytime Touchdown': 0.5, '2+ Touchdowns': 1.5, '3+ Touchdowns': 2.5 }[r.market] ?? null;
  };
  const v2PlayerName = (r) => r.player || (V2_STAT[r.market] ? String(r.contract || '').split(':')[0].trim() : '');
  const v2ProjMarket = (m) => (m === '2+ Touchdowns' || m === '3+ Touchdowns' ? 'Anytime Touchdown' : m);
  let v2PJ = null, v2PJsrc = null;
  function v2Proj(name, market) {
    const d = dash.data('proj'); if (d.status !== 'ok' || !name) return null;
    if (v2PJsrc !== d.data) { v2PJsrc = d.data; v2PJ = new Map(); for (const x of d.data) v2PJ.set(v2Norm(x.player) + '|' + x.market, x); }
    return v2PJ.get(v2Norm(name) + '|' + v2ProjMarket(market)) || null;
  }
  let v2SK = null, v2SKsrc = null;
  function v2SitKey(name) {
    const d = dash.data('sit'); if (d.status !== 'ok' || !name) return null;
    if (v2SKsrc !== d.data) { v2SKsrc = d.data; v2SK = new Map(d.data.map((x) => [v2Norm(x.player), String(x.key)])); }
    return v2SK.get(v2Norm(name)) || null;
  }
  const v2Inj = lazyMap('inj', (r) => r.key);
  const svgEl = (tag, attrs) => { const e = document.createElementNS('http://www.w3.org/2000/svg', tag); for (const k in attrs || {}) e.setAttribute(k, attrs[k]); return e; };
  // graded results (after the game) and the matchup lens (Mon Nov 9)
  function v2Res(r, small) {
    const cls = { Won: 'is-won', Lost: 'is-lost' }[r.outcome] || 'is-void';
    const t = r.outcome === 'Void' ? 'Void · did not play' : `${r.outcome} · ${r.text}` + (small ? '' : ` · ${r.profit_c > 0 ? '+' : r.profit_c < 0 ? '−' : ''}${Math.abs(r.profit_c)}¢`);
    return el('span', 'v2-res ' + cls + (small ? ' sm' : ''), t);
  }
  const v2Rec = (c) => { const g = c.plays.filter((p) => p.result && p.result.outcome !== 'Void'); const w = g.filter((p) => p.result.outcome === 'Won').length; return g.length ? `${w}–${g.length - w}` : ''; };
  const v2Checked = (c) => (c && c.plays[0] && c.plays[0].checked) || (v2F() || {}).at;
  function v2Ledger(L) {
    const ul = el('ul', 'v2-ledger'); let net = 0;
    for (const x of L) { net += x.pts; const li = el('li'); li.append(el('b', 'v2-lg-p' + (x.pts > 0 ? ' up' : x.pts < 0 ? ' down' : ''), (x.pts > 0 ? '+' : x.pts < 0 ? '−' : '±') + Math.abs(x.pts)), el('span', 'v2-lg-s', x.step), el('span', 'v2-lg-t', x.text)); ul.append(li); }
    net = Math.round(net * 10) / 10;
    const li = el('li', 'v2-lg-net'); li.append(el('b', null, (net > 0 ? '+' : net < 0 ? '−' : '±') + Math.abs(net)), el('span', 'v2-lg-s', 'Net'), el('span', 'v2-lg-t', 'points of chance on this line, from weights fit on settled Weeks 7–9 prices')); ul.append(li);
    return ul;
  }
  function v2Tbl(head, rows, cls) {
    const box = el('div', 'rs-tablebox v2-lens-tb' + (cls ? ' ' + cls : '')); const t = el('table', 'rs-table'); const th = el('thead'); const hr = el('tr');
    head.forEach((h) => hr.append(el('th', null, h))); th.append(hr); const tb = el('tbody');
    rows.forEach((r) => { const tr = el('tr'); r.forEach((v, i) => { const td = el('td', i ? 'fc-n' : null); if (v instanceof Node) td.append(v); else td.textContent = v; tr.append(td); }); tb.append(tr); });
    t.append(th, tb); box.append(t); return box;
  }
  function v2Lens(c) {
    const F0 = v2F() || {};
    const L = Object.assign({ how: F0.lens_how, check: F0.lens_check, check_title: F0.lens_check_title, check_head: F0.lens_check_head }, c.lens), w = el('div', 'v2-lens');
    w.append(el('p', 'v2-lens-how', L.how));
    const sides = el('div', 'v2-lens-sides');
    for (const S of L.sides) {
      const card = el('div', 'rs-card v2-lens-side'); card.style.setProperty('--tc', wzTeam(S.off)[1]);
      card.append(el('h4', null, `${S.off} offense vs ${S.def} defense`));
      card.append(el('h5', null, `What ${S.def} allows`), v2Tbl(['Per game', 'Value', 'Rank'], S.facts));
      card.append(el('h5', null, 'Where the ball goes'), v2Tbl(['Targets to', `${S.qb}'s share`, `${S.def} allows`, ''], S.where.map((r) => [r[0], r[1], r[2], el('span', 'v2-ov' + (r[3] === 'Overlap' ? ' on' : ''), r[3])])));
      card.append(el('h5', null, 'Against the look'), v2Tbl(['Player', 'Share', 'vs blitz', 'No blitz', 'Change'], S.looks), el('p', 'wg-note', S.look_note));
      card.append(el('h5', null, 'Run matchup'), v2Tbl(['Runs', `${S.off} yds · success`, `${S.def} allows`, 'Share'], S.runs), el('p', 'wg-note', S.run_note));
      const ul = el('ul', 'v2-lens-comps'); S.comps.forEach((x) => ul.append(el('li', null, x))); card.append(el('h5', null, 'Comparable games'), ul);
      sides.append(card);
    }
    w.append(sides);
    if (L.check && L.check.length) {
      const ck = el('div', 'rs-card v2-lens-check'); ck.append(el('h4', null, L.check_title || 'How the lens tested'));
      ck.append(v2Tbl(L.check_head || ['Test', 'Result', ''], L.check, 'v2-lens-ck'));
      w.append(ck);
    }
    if (L.verdict) w.append(el('p', 'v2-lens-verdict', L.verdict));
    return w;
  }

  // ---------------- Home: picks by matchup, and the reads they open ----------------
  let v2HomeDone = false;
  function v2Home() {
    const grid = $('#v2-mgrid'); if (!grid || v2HomeDone) return;
    const F = v2F();
    if (!F || !F.cards) { grid.replaceChildren(el('p', 'wx-empty', 'This week’s matchups failed to load.')); return; }
    v2HomeDone = true;
    grid.replaceChildren(...F.cards.map((c) => {
      const [a, h] = wzSides(c.game); const [f, l] = v2Counts(c);
      const b = el('button', 'pf-tt v2-mt'); b.type = 'button'; b.dataset.game = c.game; b.setAttribute('aria-pressed', 'false');
      b.style.setProperty('--tc1', wzTeam(a)[1]); b.style.setProperty('--tc2', wzTeam(h)[1]);
      const helms = el('span', 'v2-mt-h'); helms.setAttribute('aria-hidden', 'true'); helms.append(wzHelmet(a, false), wzHelmet(h, true));
      const tags = el('span', 'v2-mt-tags');
      if (c.status === 'Final') { tags.append(el('i', 'fc-badge v2-fin', 'Final')); const rc = v2Rec(c); if (rc) tags.append(el('i', 'fc-badge fc-lean', `Card ${rc}`)); b.classList.add('is-done'); }
      else {
        if (f) tags.append(el('i', 'fc-badge fc-final', `${f} final`));
        if (l) tags.append(el('i', 'fc-badge fc-lean', `${l} lean${l > 1 ? 's' : ''}`));
        if (!f && !l) tags.append(el('i', 'fc-badge fc-pass', 'Pass'));
      }
      b.append(helms, el('b', null, c.game), el('small', null, c.status === 'Final' && c.score ? c.score : v2Kick(c)), tags);
      b.setAttribute('aria-label', `${wzTeam(a)[0]} at ${wzTeam(h)[0]}, ${c.kick}: ${f} final line${f === 1 ? '' : 's'}, ${l} conditional lean${l === 1 ? '' : 's'}. Show its reads.`);
      b.addEventListener('click', () => v2SelectGame(c.game, true));
      return b;
    }));
    $('#v2-reads-edge').addEventListener('click', () => v2GoEdge(V2.game));
    $('#v2-reads-thesis').addEventListener('click', () => v2GoThesis(V2.game));
    $('#v2-reads-close').addEventListener('click', () => {
      $('#wz-reads').hidden = true; V2.game = '';
      grid.querySelectorAll('.v2-mt').forEach((x) => x.setAttribute('aria-pressed', 'false'));
      $('#v2-matchups').scrollIntoView({ behavior: WZ_REDUCE ? 'auto' : 'smooth', block: 'start' }); v2InkSoon();
    });
  }
  function v2SelectGame(g, scroll) {
    if (!v2Card(g)) return;
    V2.game = g;
    document.querySelectorAll('#v2-mgrid .v2-mt').forEach((x) => x.setAttribute('aria-pressed', x.dataset.game === g ? 'true' : 'false'));
    const sec = $('#wz-reads'); sec.hidden = false;
    v2Reads(g);
    sec.classList.remove('v2-enter'); void sec.offsetWidth; sec.classList.add('v2-enter');
    if (scroll) requestAnimationFrame(() => sec.scrollIntoView({ behavior: WZ_REDUCE ? 'auto' : 'smooth', block: 'start' }));
    v2InkSoon();
  }
  function v2Reads(g) {
    const c = v2Card(g), box = $('#wg-hot-cards'), sub = $('#wx-reads-sub');
    wzMatchup(g);
    const [f, l] = v2Counts(c);
    sub.textContent = c.status === 'Final'
      ? `Final: ${c.score}. The card went ${v2Rec(c) || '0–0'}.`
      : c.plays.length
      ? `${f} final line${f === 1 ? '' : 's'} and ${l} conditional lean${l === 1 ? '' : 's'} from The Winning Edge, best first. ${c.kick} · ${c.venue}.`
      : ((v2B() && v2B().games && v2B().games[g] && !v2B().games[g].qb.ok) ? `Left off this week’s card: ${v2B().games[g].qb.t}` : `Nothing in ${g} clears break-even. Pass.`);
    box.replaceChildren(...(c.plays.length ? c.plays.map((p, i) => v2ReadCard(c, p, i)) : [v2PassCard(c)]));
  }
  function v2ReadCard(c, p, i) {
    const fin = p.decision === 'Final line';
    const b = el('button', 'wx-read v2-read ' + (fin ? 'is-final' : 'is-lean')); b.type = 'button';
    const top = el('span', 'wx-read-top'); top.append(el('span', null, `${String(i + 1).padStart(2, '0')} · ${v2Kick(c)}`), fcBadge(p.decision));
    const title = p.line.replace(/ \((Yes|No)\)$/, '');
    const big = el('span', 'wx-read-big'); { const rl = el('span', 'pf-roll'); rl.append(el('span', null, String(Math.round(p.mid)))); big.append(rl, el('small', null, '%')); }
    const lab = el('span', 'wx-mono'); lab.append('Our', document.createElement('br'), 'number');
    const mid = el('span', 'wx-read-mid'); mid.append(big, lab);
    const px = el('span', 'wx-read-px');
    const a1 = el('span', 'is-pick'); a1.append(el('span', null, p.side), el('span', null, p.price + '¢'));
    const a2 = el('span'); a2.append(el('span', null, 'Needs'), el('span', null, p.be + '%'));
    px.append(a1, a2);
    const hr = el('span', 'wz-hr'); hr.append(el('b', null, `${p.est[0]}–${p.est[1]}%`), 'our range' + (p.tier ? ` · ${p.tier.toLowerCase()} likelihood` : ''));
    const why = el('span', 'v2-read-why', p.why);
    const foot = el('span', 'wx-read-foot'); const dot = el('i', 'wx-dot'); dot.setAttribute('aria-hidden', 'true');
    foot.append(dot, el('span', 'v2-read-cond', p.cond), el('em', null, 'Full record ↗'));
    b.classList.add('wz-spot'); b.dataset.game = c.game; b.dataset.player = p.player || ''; v2Tint(b);
    b.append(top, wzWords(title), mid, px, hr, why);
    if (p.result) { b.classList.add('is-graded'); b.append(v2Res(p.result)); }
    b.append(foot);
    b.setAttribute('aria-label', `${p.decision}: ${title}, ${p.side} at ${p.price} cents, needs ${p.be}%, our number ${p.est[0]} to ${p.est[1]}%. Open the full record in The Winning Edge.`);
    b.addEventListener('click', () => v2GoEdge(c.game, i));
    return b;
  }
  function v2PassCard(c) {
    const d = el('div', 'wx-read v2-read is-pass');
    const top = el('span', 'wx-read-top'); top.append(el('span', null, v2Kick(c)), fcBadge('Pass'));
    const ul = el('ul', 'v2-pass-list');
    c.passed.filter((x) => x.thesis).slice(0, 4).forEach((x) => { const li = el('li'); li.append(el('b', null, x.name), el('span', null, x.why)); ul.append(li); });
    d.append(top, wzWords('Nothing clears at any price.'), el('span', 'v2-read-why', `${c.passed.length} lines passed. Closest calls:`), ul);
    return d;
  }
  function v2GoEdge(g, i) {
    showPage('final'); v2Top();
    requestAnimationFrame(() => requestAnimationFrame(() => {
      fcRender();
      const d = g && document.getElementById(fcId(g)); if (!d) return;
      d.open = true;
      const t = (i != null && d.querySelectorAll('.fc-play')[i]) || d;
      t.scrollIntoView({ block: 'start' });
      v2InkSoon();
    }));
  }
  function v2GoThesis(g) { if (g) V2.th = g; showPage('thesis'); v2Top(); }
  function v2ThesisLink(c) {
    const d = el('div', 'v2-thlink');
    d.append(el('p', null, `The full thesis for ${c.game}.`));
    const b = el('button', 'wz-btn wz-btn-line wz-btn-sm', 'Read the thesis ↗'); b.type = 'button';
    b.addEventListener('click', (e) => { e.preventDefault(); e.stopPropagation(); v2GoThesis(c.game); });
    d.append(b); return d;
  }

  // ---------------- Research: one page for lines and projections ----------------
  function v2ResearchView(v) {
    ['lines', 'proj'].forEach((k) => {
      const on = k === v, b = $('#v2-rv-' + k), p = $('#v2-rv-' + k + '-p');
      if (b) { b.setAttribute('aria-selected', String(on)); b.tabIndex = on ? 0 : -1; }
      if (p) p.hidden = !on;
    });
    v2InkSoon();
  }
  document.querySelectorAll('.v2-seg-b').forEach((b) => {
    b.addEventListener('click', () => v2ResearchView(b.dataset.view));
    b.addEventListener('keydown', (e) => { if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); const o = $(b.dataset.view === 'lines' ? '#v2-rv-proj' : '#v2-rv-lines'); o.focus(); o.click(); } });
  });
  { const px = $('.rs-px'), nt = $('.rl-every-note'), ev = ls.show === 'every'; if (px) px.hidden = !ev; if (nt) nt.hidden = !ev; }
  function v2ProjCell(tr, r) {
    const c = el('td', 'v2-pj'); tr.appendChild(c);
    const nm = v2PlayerName(r), P = nm ? v2Proj(nm, r.market) : null, st = V2_STAT[v2ProjMarket(r.market)];
    if (!P || P.proj === '' || !st) { c.textContent = '—'; c.classList.add('rs-sub'); return c; }
    const f = (v) => fmtStat(st, num(v)), line = v2LineOf(r);
    const b = el('b', null, f(P.proj));
    if (line != null && st !== 'td') b.className = num(P.proj) > line ? 'up' : 'down';
    c.append(el('span', null, f(P.proj_lo)), el('i', null, ' · '), b, el('i', null, ' · '), el('span', null, f(P.proj_hi)));
    c.title = `${nm}: bear ${f(P.proj_lo)}, base ${f(P.proj)}, bull ${f(P.proj_hi)}${line != null && st !== 'td' ? ` · this line ${line}` : ''}. Select the row for the file.`;
    return c;
  }
  function v2Clickable(tr, r) {
    tr.classList.add('wg-click', 'v2-click'); tr.tabIndex = 0;
    tr.setAttribute('aria-label', `Open the research file for ${rhLabel(r.contract)}, ${r.game}`);
    const go = () => v2OpenFile(r, tr);
    tr.addEventListener('click', (e) => { if (e.target.closest('input, button, a, select, label, textarea')) return; if (window.getSelection && String(window.getSelection())) return; go(); });
    tr.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); go(); } });
  }

  // ---------------- the research file (folder): lite version for lines without a full outlook ----------------
  function v2OpenFile(r, opener) {
    const nm = v2PlayerName(r), st = V2_STAT[r.market] || null, line = v2LineOf(r);
    const ctx = { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source };
    const key = r.sit_key || (nm ? v2SitKey(nm) : null);
    const rr = Object.assign({}, r, key ? { sit_key: key } : {});
    Object.assign(sit, { r: rr, ctx, O: null, sp: SPORTS.nfl, det: key ? SPORTS.nfl.sit(key) : null, sel: null, tab: 'ov', lite: true });
    if (sit.det && st && line != null) sit.O = { stat: st, line, unit: SIT_UNIT[st] };
    sitOpener = opener;
    if (!sitDlg.open) { try { sitDlg.showModal(); } catch (e) { sitDlg.setAttribute('open', ''); } }
    $('.wg-sd-body', sitDlg).scrollTop = 0;
    v2RenderLite(rr, nm, st, line);
    v2AfterFile();
    showTab('ov');
  }
  function v2GameChips(box, G, team, opp) {
    const tname = (t) => (G.names && G.names[t]) || t;
    const chips = el('div', 'wg-chips');
    const chip = (b, s2) => { const c = el('div', 'wg-card'); c.append(el('b', null, b), el('small', null, s2)); chips.append(c); };
    if (G.spread_home != null) {
      const sh = G.spread_home, fav = sh < 0 ? G.home : G.away, a = Math.abs(sh);
      chip(a < 0.5 ? 'Pick’em' : `${tname(fav)} −${avg1(a).replace('.0', '')}`, G.implied ? `Total ${G.total} · implied ${G.away} ${G.implied[G.away]}, ${G.home} ${G.implied[G.home]}` : 'Spread');
    }
    if (G.stadium) chip(G.stadium, [G.roof, G.surface].filter(Boolean).join(' · '));
    if (G.weather) chip(`${G.weather.temp}°F · wind ${Math.round(G.weather.wind)} mph`, `Gusts ${G.weather.gust} mph · ${G.weather.precip_prob}% rain chance`);
    else if (G.roof) chip(G.roof === 'dome' || G.roof === 'closed' ? 'Indoors' : 'Retractable roof', 'Weather not a factor');
    if (G.coach) chip(`${(G.coach[G.away] || '').split(' ').slice(-1)[0]} vs ${(G.coach[G.home] || '').split(' ').slice(-1)[0]}`, 'Head coaches');
    if (G.rest && team && opp) chip(`${G.rest[team]} vs ${G.rest[opp]} days`, `Rest: ${team} vs ${opp}`);
    box.append(sec('Game environment', null, chips));
  }
  function v2ScriptBar(box, G, team) {
    if (!G.script) return;
    const teams = team && G.script[team] ? [team] : [G.away, G.home].filter((t) => G.script[t]);
    const wrap = el('div', 'v2-scripts');
    for (const t of teams) {
      const S = G.script[t]; const row = el('div', 'v2-scr');
      row.append(el('b', null, `${t}: the three scripts`));
      const bar = el('div', 'v2-scr-bar'); bar.setAttribute('role', 'img');
      const parts = [['Control', S.lead8, `${t} wins by 8+`, 'c'], ['Competitive', S.close, 'Within one score', 'm'], ['Reversal', S.trail8, `${t} loses by 8+`, 'r']];
      bar.setAttribute('aria-label', parts.map(([n, w, d]) => `${n} (${d}) ${pctR(100 * w)}`).join(', '));
      parts.forEach(([n, w, d2, k]) => { const s2 = el('span', 'v2-scr-' + k); const lb = el('em', null, `${n} ${pctR(100 * w)}`); s2.title = `${d2}: ${pctR(100 * w)}`; s2.append(lb); bar.append(s2); grow(s2, 'flexBasis', (100 * w) + '%'); });
      row.append(bar, el('small', null, `Books: ${t} ${pctR(100 * S.win)} to win.`));
      wrap.append(row);
    }
    box.append(sec('Game script', 'Control · competitive · reversal', wrap));
  }
  function v2RenderLite(r, nm, st, line) {
    const price = num(r.yes_price), G = SPORTS.nfl.ctx('game|' + r.game) || {};
    const [aw, hm] = wzSides(r.game);
    const P = nm ? v2Proj(nm, r.market) : null;
    const team = (P && P.team) || (sit.det && sit.det.team) || (nm ? wzPlayerTeam({ game: r.game, contract: nm }) : null);
    const opp = team ? (team === aw ? hm : aw) : null;
    const pos = (P && P.pos) || (sit.det && sit.det.pos) || '';
    $('#sit-kicker').textContent = nm ? `Research file · ${[team, pos].filter(Boolean).join(' ')}${opp ? ' vs ' + opp : ''}` : `Research file · ${r.market}`;
    $('#sit-title').textContent = rhLabel(r.contract);
    const sub = $('#sit-sub'); sub.replaceChildren(el('span', null, r.game));
    if (r.kickoff) sub.append(el('span', null, r.kickoff));
    if (price != null) sub.append(el('span', null, `${price}¢ ${r.source && r.source !== 'Robinhood' ? 'sportsbook average' : `Robinhood ask${num(r.yes_bid) != null ? ` · bid ${r.yes_bid}¢` : ''}`}`));
    if (r.flags) sub.append(el('span', null, r.flags));
    // ---- The Bull, the Bear, and the Base
    const ov = $('#sit-p-ov'); ov.replaceChildren();
    const unit = st ? SIT_UNIT[st] : '';
    if (P && st && P.proj !== '') {
      const f = (v) => fmtStat(st, num(v));
      const S3 = [['Bear', num(P.proj_lo), 'bear'], ['Base', num(P.proj), 'base'], ['Bull', num(P.proj_hi), 'bull']];
      const row = el('div', 'v2-bbb');
      for (const [k, v, cls] of S3) {
        const c = el('div', 'wg-card v2-bbb-c ' + cls);
        const n = el('span', 'wg-big'); const nv = el('span'); n.append(nv, el('small', null, unit)); countUp(nv, v, (x) => f(x));
        c.append(el('div', 'wg-lab', `The ${k.toLowerCase()}`), n);
        if (line != null && st !== 'td') { const d = v - line; c.append(el('span', 'wg-chip ' + (d >= 0 ? 'up' : 'down'), `${d >= 0 ? 'Over' : 'Under'} the ${line} line by ${fmtStat(st, Math.abs(d))}`)); }
        row.append(c);
      }
      // the three on one axis with the line
      const vals = S3.map((x) => x[1]).concat(line != null ? [line] : []).filter((x) => x != null);
      const lo = Math.min(...vals), hi = Math.max(...vals), pad = (hi - lo) * 0.14 || 1, x0 = lo - pad, x1 = hi + pad, pos2 = (v) => (100 * (v - x0) / (x1 - x0)) + '%';
      const rng = el('div', 'wg-rng v2-rng'); rng.setAttribute('aria-hidden', 'true'); rng.append(el('div', 'wg-rng-track'));
      if (line != null) { const ln = el('div', 'wg-rng-line'); ln.style.left = pos2(line); rng.append(ln); }
      S3.forEach(([k, v, cls]) => { const d = el('div', 'wg-rng-dot'); d.style.background = `var(--wg-${cls})`; d.style.left = pos2(line ?? v); rng.append(d); grow(d, 'left', pos2(v)); });
      const lab = el('div', 'wg-rng-lab'); S3.forEach(([k, v]) => { const s2 = el('span', null, k + ' '); s2.append(el('b', null, f(v))); lab.append(s2); });
      if (line != null) { const s2 = el('span', null, 'Line '); s2.append(el('b', null, String(line))); lab.append(s2); }
      const card = el('div', 'wg-card'); card.append(el('div', 'wg-lab', `Projected ${SIT_WORD[st] || unit}`), rng, lab,
        el('p', 'wg-note', `Our low, middle and high cases this week. Expected opener ${P.est_line}${P.p_over !== '' ? ` (${pctR(num(P.p_over))} over)` : ''}.`));
      ov.append(sec('The Bull, the Bear, and the Base', 'Our projection', row, card));
    } else if (st) {
      ov.append(sec('The Bull, the Bear, and the Base', null, el('p', 'wg-note', `No projection for this stat. His games are in Game Script.`)));
    } else {
      const S = team && G.script ? G.script[team] : (G.script ? G.script[G.home] : null);
      const box = el('div', 'v2-bbb');
      if (G.script) {
        const t2 = team || G.home, S2 = G.script[t2];
        [['The bear', S2.trail8, `${t2} loses by 8+`, 'bear'], ['The base', S2.close, 'Within one score', 'base'], ['The bull', S2.lead8, `${t2} wins by 8+`, 'bull']].forEach(([k, w, d, cls]) => {
          const c = el('div', 'wg-card v2-bbb-c ' + cls); const n = el('span', 'wg-big'); const nv = el('span'); n.append(nv, el('small', null, '%')); countUp(nv, 100 * w, (x) => String(Math.round(x)));
          c.append(el('div', 'wg-lab', k), n, el('span', 'wg-chip', d)); box.append(c);
        });
      }
      ov.append(sec('The Bull, the Bear, and the Base', 'The game’s three scripts', box,
        el('p', 'wg-note', `The three ways the game can go, from the books${G.implied ? ` (${G.away} ${G.implied[G.away]}, ${G.home} ${G.implied[G.home]})` : ''}.`)));
      void S;
    }
    if (sit.det && st && line != null) {
      const idx = sit.det.base.filter((i) => sit.det.log[i][0] === 26);
      const S = sitSum(sit.det, st, line, idx);
      if (S.n) {
        const c = el('div', 'wg-card v2-season'); const n = el('span', 'wg-big'); const nv = el('span'); n.append(nv, el('small', 'pct', '%')); countUp(nv, S.p, (x) => String(Math.round(x)));
        c.append(el('div', 'wg-lab', `Over ${line} this season`), n, meter(S.p, price, S.p != null && price != null && S.p > price ? 'var(--wg-green)' : 'var(--cds-chart-muted)'),
          el('p', 'wg-note', `${S.h} of ${S.n} games in 2026 · avg ${fmtStat(st, S.avg)} ${unit}${price != null ? ` · ${price}¢` : ''}`));
        ov.append(c);
      }
    }
    // ---- Game Script: environment, scripts, history with splits
    const mu = $('#sit-p-mu'); mu.replaceChildren();
    v2GameChips(mu, G, team, opp);
    v2ScriptBar(mu, G, team);
    if (sit.det && sit.O) { sitHistory(sit.det, st, line, price, SPORTS.nfl); sitDlg.classList.remove('v2-nohist'); }
    else { sitDlg.classList.add('v2-nohist'); $('#sit-foot').textContent = ''; }
  }
  function v2AfterFile() {
    const r = sit.r || {}, nm = v2PlayerName(r);
    v2RenderInjury(nm, r);
    if (!sit.lite) sitDlg.classList.remove('v2-nohist');
    const who = $('#sit-p-inj'); if (who) who.dataset.player = nm || '';
    if (!reduced()) {
      sitDlg.classList.remove('v2-opening'); void sitDlg.offsetWidth; sitDlg.classList.add('v2-opening');
      clearTimeout(V2.openT); V2.openT = setTimeout(() => sitDlg.classList.remove('v2-opening'), 1800);
    }
  }
  // a page turn: copy the sheet as it looks now onto a loose leaf, then turn the leaf away
  function v2LeafStart(prev, k) {
    if (reduced() || !prev || prev === k || sitDlg.classList.contains('v2-opening')) return null;
    const body = $('.wg-sd-body', sitDlg), host = $('.wg-sd-in', sitDlg); if (!body || !host) return null;
    host.querySelectorAll('.v2-leaf').forEach((x) => x.remove());
    const order = ['ov', 'inj', 'mu'], fwd = order.indexOf(k) > order.indexOf(prev);
    const leaf = el('div', 'v2-leaf ' + (fwd ? 'up' : 'down')); leaf.setAttribute('aria-hidden', 'true'); leaf.inert = true;
    Object.assign(leaf.style, { left: body.offsetLeft + 'px', top: body.offsetTop + 'px', width: body.offsetWidth + 'px', height: body.offsetHeight + 'px' });
    const cs = getComputedStyle(body), st = body.scrollTop;
    const card = el('div', 'v2-leaf-card'), f = el('div', 'v2-leaf-f'), bk = el('div', 'v2-leaf-b'), inn = el('div', 'v2-leaf-in');
    f.style.backgroundImage = cs.backgroundImage; f.style.backgroundSize = cs.backgroundSize;
    f.style.backgroundPosition = cs.backgroundPosition.split(',').map((x, i) => (i === 1 ? x.trim().replace(/(-?[\d.]+)px$/, (m, v) => (parseFloat(v) - st) + 'px') : x.trim())).join(', ');
    inn.style.padding = cs.padding; inn.style.transform = `translateY(${-st}px)`;
    [...body.children].forEach((c) => { if (!c.hidden) inn.append(c.cloneNode(true)); });
    f.append(inn); card.append(f, bk); leaf.append(card);
    return leaf;
  }
  function v2Flip(prev, k, leaf) {
    const body = $('.wg-sd-body', sitDlg); if (!body) return;
    body.scrollTop = 0;
    const tab = $('.wg-sd-tab[aria-selected="true"]', sitDlg);
    if (tab && !reduced() && prev && prev !== k) { tab.classList.remove('v2-tab-pop'); void tab.offsetWidth; tab.classList.add('v2-tab-pop'); }
    if (!leaf) return;
    $('.wg-sd-in', sitDlg).append(leaf);
    body.classList.remove('v2-under'); void body.offsetWidth; body.classList.add('v2-under');
    clearTimeout(V2.flipT); V2.flipT = setTimeout(() => { leaf.remove(); body.classList.remove('v2-under'); if (tab) tab.classList.remove('v2-tab-pop'); }, 780);
  }

  // ---------------- Injury Report: the body chart and the reports ----------------
  const V2_TONE = { red: '#D2402B', yellow: '#D99A00', green: '#1E9E52', past: '#8C857A' };
  const V2_TONE_WORD = { red: 'Out, doubtful or on IR', yellow: 'Questionable or limited', green: 'Cleared or practicing fully', past: 'Earlier seasons (2023–25)' };
  // [view, x offset from the figure's center (+ = the player's right), y] on a 300-tall figure
  const V2_SPOT = [
    [/concussion|head|eye|face|jaw|nose|dental/i, 'f', 0, 26], [/neck/i, 'b', 0, 50], [/collarbone|clavicle/i, 'f', 12, 58], [/shoulder|ac joint|rotator/i, 'f', 25, 62],
    [/pectoral|chest|sternum/i, 'f', 11, 80], [/rib|oblique/i, 'f', 19, 100], [/abdom|core|stomach/i, 'f', 0, 114], [/lung|illness|personal|rest|other|not injury/i, null],
    [/back|spine|lumbar/i, 'b', 0, 104], [/glute/i, 'b', 12, 140], [/hip/i, 'f', 19, 134], [/groin|adductor|pelvis/i, 'f', 6, 146],
    [/hamstring/i, 'b', 11, 168], [/quad|thigh/i, 'f', 12, 166], [/knee|acl|mcl|patella|menisc/i, 'f', 11, 196], [/fibula|tibia|shin/i, 'f', 11, 222],
    [/calf/i, 'b', 11, 218], [/achilles|heel/i, 'b', 10, 254], [/ankle/i, 'f', 10, 254], [/foot|toe|plantar/i, 'f', 11, 268],
    [/tricep|elbow/i, 'b', 33, 100], [/bicep/i, 'f', 31, 86], [/forearm/i, 'f', 35, 116], [/wrist/i, 'f', 38, 130], [/hand|finger|thumb/i, 'f', 41, 142],
  ];
  // one side of the outline (x offset, y), neck to toe and back up the inside of the leg
  const V2_HALF = [[6, 40], [7, 48], [20, 54], [31, 60], [35, 76], [37, 98], [40, 118], [42, 132], [45, 146], [41, 156], [36, 147], [35, 132], [31, 117], [29, 98], [26, 76],
    [24, 92], [21, 114], [24, 134], [25, 164], [21, 196], [21, 220], [15, 252], [18, 266], [8, 271], [5, 264], [6, 252], [7, 222], [8, 196], [6, 164], [0, 146]];
  const v2Smooth = (pts) => {
    const n = pts.length; let d = `M${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`;
    for (let i = 0; i < n; i++) {
      const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n];
      const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6], c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
      d += `C${c1[0].toFixed(1)},${c1[1].toFixed(1)} ${c2[0].toFixed(1)},${c2[1].toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`;
    }
    return d + 'Z';
  };
  function v2Body(spots, name) {
    const W = 320, H = 300, CX = { f: 84, b: 236 };
    const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, class: 'v2-body', role: 'img', width: '100%' });
    svg.setAttribute('aria-label', spots.length ? `Body chart for ${name}: ${spots.map((s) => `${s.part} (${V2_TONE_WORD[s.tone] || s.tone}, ${s.when})`).join('; ')}` : `Body chart for ${name}: no injuries on the 2023–26 reports`);
    for (const v of ['f', 'b']) {
      const cx = CX[v];
      const half = V2_HALF.map(([x, y]) => [cx - x, y]), other = V2_HALF.slice().reverse().map(([x, y]) => [cx + x, y]);
      const g = svgEl('g', { class: 'v2-fig' });
      g.append(svgEl('ellipse', { cx, cy: 24, rx: 12.5, ry: 15, class: 'v2-ink' }));
      g.append(svgEl('path', { d: v2Smooth(half.concat(other.slice(1, -1))), class: 'v2-ink' }));
      g.append(svgEl('line', { x1: cx, y1: 6, x2: cx, y2: 286, class: 'v2-mid' }));
      if (v === 'f') { g.append(svgEl('path', { d: `M${cx - 9},70 q9,7 18,0 M${cx - 15},118 q15,5 30,0`, class: 'v2-ink v2-thin' })); }
      else { g.append(svgEl('path', { d: `M${cx - 14},62 q14,-6 28,0 M${cx},104 l0,24 M${cx - 13},146 q13,10 26,0`, class: 'v2-ink v2-thin' })); }
      const lab = svgEl('text', { x: cx, y: 298, class: 'v2-lab', 'text-anchor': 'middle' }); lab.textContent = v === 'f' ? 'ANTERIOR' : 'POSTERIOR'; g.append(lab);
      const rl = svgEl('text', { x: cx - 48, y: 64, class: 'v2-lab sm', 'text-anchor': 'middle' }); rl.textContent = v === 'f' ? 'R' : 'L'; g.append(rl);
      const ll = svgEl('text', { x: cx + 48, y: 64, class: 'v2-lab sm', 'text-anchor': 'middle' }); ll.textContent = v === 'f' ? 'L' : 'R'; g.append(ll);
      svg.append(g);
    }
    const placed = [];
    spots.forEach((s, i) => {
      const hit = V2_SPOT.find(([re]) => re.test(s.part)); if (!hit || !hit[1]) return;
      const [, view, off, y] = hit; const side = /\bleft\b/i.test(s.part) ? -1 : 1;
      const cx = CX[view], x = view === 'f' ? cx - side * off : cx + side * off;
      let yy = y; while (placed.some(([px, py]) => Math.abs(px - x) < 8 && Math.abs(py - yy) < 8)) yy += 9;
      placed.push([x, yy]);
      const col = V2_TONE[s.tone] || V2_TONE.past;
      const g = svgEl('g', { class: 'v2-spot' + (s.now ? ' now' : '') + (s.tone === 'past' ? ' past' : ''), style: `--d:${0.25 + i * 0.12}s` });
      if (s.now) g.append(svgEl('circle', { cx: x, cy: yy, r: 15, fill: 'none', stroke: col, 'stroke-width': 1.4, class: 'v2-pulse' }));
      g.append(svgEl('circle', { cx: x, cy: yy, r: s.now ? 9.5 : 7.5, fill: col, 'fill-opacity': s.tone === 'past' ? 0.12 : 0.22, stroke: col, 'stroke-width': s.now ? 2.6 : 1.8, 'stroke-dasharray': s.tone === 'past' ? '3 2.4' : '' }));
      const t = svgEl('title'); t.textContent = `${s.part}: ${s.when}`; g.append(t);
      svg.append(g);
    });
    return svg;
  }
  function v2RenderInjury(nm, r) {
    const box = $('#sit-p-inj'); if (!box) return; box.replaceChildren();
    const d = dash.data('inj');
    if (d.status !== 'ok') { box.append(el('p', 'wg-note', d.status === 'error' ? 'The injury reports failed to load.' : 'Loading the injury reports…')); return; }
    if (!nm) {
      const [a, h] = wzSides(r.game || '');
      for (const t of [a, h]) {
        if (!t) continue;
        const L = d.data.filter((x) => x.team === t && x.status && x.status !== 'No designation').map((x) => { try { return JSON.parse(x.detail); } catch (e) { return null; } }).filter(Boolean);
        const ul = el('ul', 'v2-teaminj');
        L.forEach((D) => { const li = el('li', 'v2-ti ' + D.tone); li.append(el('i', 'v2-dot'), el('b', null, D.p), el('span', null, `${D.pos} · ${D.status}${D.part ? ' · ' + D.part : ''}`)); ul.append(li); });
        if (!L.length) ul.append(el('li', 'v2-ti empty', 'Nobody with a line is on the report.'));
        box.append(sec(`${wzTeam(t)[0]} · ${t}`, 'Players with a line this week', ul));
      }
      box.append(el('p', 'wg-note', 'Players with a line this week and an injury tag.'));
      return;
    }
    const D = v2Inj(v2Norm(nm));
    const grid = el('div', 'v2-inj');
    const left = el('div', 'v2-inj-fig');
    left.append(v2Body(D ? D.spots : [], nm));
    const key = el('div', 'v2-inj-key');
    ['red', 'yellow', 'green', 'past'].forEach((t) => { const s2 = el('span'); const i = el('i'); i.style.setProperty('--c', V2_TONE[t]); if (t === 'past') i.classList.add('past'); s2.append(i, V2_TONE_WORD[t]); key.append(s2); });
    left.append(key);
    const right = el('div', 'v2-inj-txt');
    const tone = D ? D.tone : 'green';
    const stamp = el('div', 'v2-stamp ' + tone, D && D.status !== 'No designation' ? D.status : 'No designation');
    right.append(stamp);
    const facts = [];
    if (D && D.part) facts.push(['Injury', D.part]);
    if (D && D.prac) facts.push(['This week’s practice', D.prac + ' (last report of the week)']);
    if (D && D.rep) facts.push(['Game status', D.rep]);
    if (D && D.ret) facts.push(['Earliest return', new Date(D.ret + 'T12:00:00').toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })]);
    if (facts.length) { const dl = el('dl', 'v2-facts'); facts.forEach(([k, v]) => { const x = el('div'); x.append(el('dt', null, k), el('dd', null, v)); dl.append(x); }); right.append(dl); }
    if (D && D.news) {
      const q = el('blockquote', 'v2-news'); q.append(el('p', null, D.news));
      if (D.news_at) q.append(el('cite', null, `Latest report · ${fcTime(D.news_at.replace(/Z?$/, 'Z'))}`)); right.append(q);
    }
    if (D && D.note) right.append(el('p', 'v2-note', `Our Saturday read of the reports: ${D.note}.`));
    if (!D) right.append(el('p', 'v2-note', `No injury reports since 2023.`));
    else if (!D.news && D.status === 'No designation' && !D.trail.length) right.append(el('p', 'v2-note', 'Clean this week and this season.'));
    grid.append(left, right);
    box.append(sec('Injury report', D && D.status !== 'No designation' ? 'Status, practice and history' : 'Healthy this week', grid));
    if (D && D.trail.length) {
      const t = el('table', 'wg-tbl v2-trail'); const hd = t.createTHead().insertRow();
      ['Week', 'Listed for', 'Practice (final)', 'Game status'].forEach((x) => hd.append(el('th', null, x)));
      const tb = t.createTBody();
      D.trail.forEach((x) => { const tr = tb.insertRow(); [`Week ${x.wk}`, x.part, x.prac || '—', x.rep || 'No designation'].forEach((v, j) => { const c = tr.insertCell(); c.textContent = v; if (j === 3 && /Out|Doubtful/.test(v)) c.className = 'bad'; else if (j === 3 && /Questionable/.test(v)) c.className = 'warn'; }); });
      box.append(sec('2026 practice and game reports', `${D.trail.length} week${D.trail.length === 1 ? '' : 's'} listed`, t));
    }
    if (D && D.hist.length) {
      const ul = el('ul', 'v2-hist');
      D.hist.forEach((h) => { const li = el('li'); li.append(el('b', null, String(h.season)), el('span', null, h.parts.map(([p, n]) => `${p} (${n} wk${n > 1 ? 's' : ''})`).join(', ')), el('em', null, h.out ? `${h.out} week${h.out > 1 ? 's' : ''} out or doubtful` : 'never ruled out')); ul.append(li); });
      box.append(sec('Injury history', 'Weeks on the report, 2023–25', ul));
    }
    box.append(el('p', 'wg-note v2-src', 'Sources: NFL injury reports and ESPN.'));
  }

  // ---------------- Thesis ----------------
  let v2ThBuilt = false;
  function v2Thesis() {
    const F = v2F(), root = $('#v2-th-root'), bar = $('#v2-th-tabs'); if (!root || !bar) return;
    if (!F || !F.cards) { root.replaceChildren(el('p', 'wx-empty', 'The thesis failed to load.')); return; }
    if (!V2.th || !v2Card(V2.th)) V2.th = (V2.game && v2Card(V2.game)) ? V2.game : (F.cards.find((c) => c.status !== 'Final') || F.cards[0]).game;
    $('#v2-th-when').textContent = `Prices checked ${fcTime(v2Checked(v2Card(V2.th)))}`;
    if (!v2ThBuilt) {
      v2ThBuilt = true;
      bar.replaceChildren(...F.cards.map((c) => {
        const t = el('button', 'wx-tab'); t.type = 'button'; t.setAttribute('role', 'tab'); t.dataset.game = c.game;
        t.append(wzPips(c.game), c.game); const dd = c.status === 'Final' ? 'Final' : (c.kick.match(/^(Thu|Fri|Sat|Sun|Mon)/) || [])[1]; if (dd) t.append(el('small', null, dd));
        t.addEventListener('click', () => { V2.th = c.game; v2Thesis(); });
        return t;
      }));
      bar.addEventListener('keydown', (e) => {
        if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
        const tabs = [...bar.querySelectorAll('.wx-tab')], i = tabs.indexOf(document.activeElement); if (i < 0) return;
        const n = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length]; n.focus(); n.click(); e.preventDefault();
      });
    }
    bar.querySelectorAll('.wx-tab').forEach((t) => { const on = t.dataset.game === V2.th; t.setAttribute('aria-selected', String(on)); t.tabIndex = on ? 0 : -1; });
    root.replaceChildren(v2ThesisGame(v2Card(V2.th)));
    v2InkSoon();
  }
  function v2ThBanner(c) {
    const [a, h] = wzSides(c.game);
    const box = el('div', 'wz-matchup v2-th-ban enter');
    const side = (t, home) => { const d = el('div', 'wz-mt-side' + (home ? ' home' : '')); const txt = el('div'); txt.append(el('b', null, t), el('span', null, wzTeam(t)[0] + (home ? ' · home' : ' · away'))); if (home) d.append(txt, wzHelmet(t, true)); else d.append(wzHelmet(t, false), txt); return d; };
    const mid = el('div', 'wz-mt-mid'); mid.append(el('span', 'wz-mt-at', '@'), el('span', 'wz-cap', c.kick), el('span', 'wz-cap', c.venue));
    box.style.setProperty('--ca', wzTeam(a)[1]); box.style.setProperty('--cb', wzTeam(h)[1]);
    box.append(side(a, false), mid, side(h, true)); return box;
  }
  const v2ThSec = (n, t, sub) => { const s2 = el('section', 'v2-th-sec'); const hd = el('div', 'v2-th-h'); hd.append(el('span', 'pf-label', n), el('h3', null, t)); if (sub) hd.append(el('p', null, sub)); s2.append(hd); return s2; };
  function v2ThesisGame(c) {
    const w = el('div', 'v2-th');
    w.append(v2ThBanner(c));
    // 1. the game
    const g = v2ThSec('01 / The game', 'What each team has to do to win.', null);
    const ml = el('div', 'rs-card v2-th-card'); ml.append(el('h4', null, 'Market and lineup'), el('p', null, c.market), el('p', null, c.lineup)); if (c.branches) ml.append(el('p', 'fc-branch', 'Personnel branches: ' + c.branches));
    const kg = el('div', 'fc-keys');
    for (const k of c.keys) { const kc = el('div', 'fc-key rs-card'); kc.style.setProperty('--tc', wzTeam(k.team)[1]); kc.append(el('h4', null, k.team + ' must take away'), el('p', 'v2-take', k.take), fcDl([['How', k.how], ['What it gives up', k.gives], ['Best counter', k.counter]])); kg.append(kc); }
    const sc = el('div', 'v2-th-scripts');
    [['Control', 'The favorite controls the game', c.scripts.control], ['Competitive', 'The game stays close', c.scripts.competitive], ['Reversal', 'The expected script breaks', c.scripts.reversal]].forEach(([k, sub, t], i) => {
      const d = el('div', 'rs-card v2-th-sc'); d.append(el('span', 'v2-th-n', String(i + 1).padStart(2, '0')), el('h4', null, k), el('small', null, sub), el('p', null, t)); sc.append(d);
    });
    if (c.status === 'Final' && c.score) ml.append(el('p', 'v2-th-final', `Final: ${c.score}. The card went ${v2Rec(c) || '0–0'}.`));
    g.append(ml);
    { const gb = v2GameBrain(c); if (gb) g.append(gb); }
    g.append(kg, sc);
    let n2 = 2, lens = null;
    if (c.lens) { lens = v2ThSec('02 / The matchup lens', 'Where the matchup moves the number.', c.rerun || null); lens.append(v2Lens(c)); n2 = 3; }
    // the lines and the players
    const l = v2ThSec(`0${n2} / The lines`, c.plays.length ? 'Why each line is on the card, and the player behind it.' : 'Nothing on the card in this game.',
      c.plays.length ? null : 'No line cleared break-even. Closest calls:');
    if (c.plays.length) c.plays.forEach((p, i) => l.append(v2ThPlay(c, p, i)));
    else { const ul = el('ul', 'fc-passed'); c.passed.filter((x) => x.thesis).forEach((x) => { const li = el('li'); li.append(el('b', null, x.name), el('span', null, x.why), el('em', null, 'What would change it: ' + x.move)); ul.append(li); }); l.append(ul); }
    const row = el('div', 'pf-row v2-thlink');
    const b1 = el('button', 'wz-btn wz-btn-line', 'See the full record in The Winning Edge ↗'); b1.type = 'button'; b1.addEventListener('click', () => v2GoEdge(c.game));
    row.append(b1);
    w.append(g); if (lens) w.append(lens); w.append(l, row);
    return w;
  }
  function v2ThPlay(c, p, i) {
    const card = el('article', 'rs-card v2-th-play ' + (p.decision === 'Final line' ? 'is-final' : 'is-lean'));
    v2Sheen(card, { game: c.game, contract: p.player });
    const top = el('div', 'v2-th-pt'); top.append(fcBadge(p.decision), el('h4', null, p.line), el('span', 'v2-th-px', `${p.side} ${p.price}¢ · needs ${p.be}% · ours ${p.est[0]}–${p.est[1]}%`));
    if (p.result) top.append(v2Res(p.result));
    const two = el('div', 'v2-th-two');
    const txt = el('div'); txt.append(fcDl([['Why it’s on the card', p.why], ['Strongest support', p.support], ['Where it loses', p.loses], ['Matchup lens', p.lens ? v2Ledger(p.lens) : null], ['Decision', `${p.decision}. ${p.cond}`]]));
    two.append(txt, v2Perf(c, p));
    card.append(top, two);
    const rb = v2Brain(c, p); if (rb) card.append(rb);
    return card;
  }
  const v2B = () => window.WZ_BRAIN || null;
  function v2Brain(c, p) {
    const B = v2B(), d = B && B.plays ? B.plays[c.game + '|' + p.line] : null;
    if (!d) return null;
    const box = el('div', 'v2-brain');
    const head = el('div', 'v2-br-head');
    const t = el('span', 'v2-tier v2-tier-' + String(p.tier || '').toLowerCase().replace(/\s+/g, '-'), (p.tier || '—') + ' likelihood');
    head.append(t, el('span', null, `Our number ${Math.round(p.mid)}% (range ${p.est[0]}–${p.est[1]}%). Value is a separate call: ${p.decision.toLowerCase()} at ${p.price}¢, needs ${p.be}%.`));
    box.append(head);
    const sec = (title, node) => { const s2 = el('div', 'v2-br-sec'); s2.append(el('span', 'wg-lab', title), node); box.append(s2); };
    if (d.chain) { const dl = el('dl', 'v2-br-chain'); d.chain.forEach((x) => { dl.append(el('dt', null, x.k), el('dd', null, x.t)); }); sec('The chain from matchup to number', dl); }
    if (d.checks) {
      const ul = el('ul', 'v2-br-checks');
      d.checks.forEach((x) => { const li = el('li', x.info ? 'is-info' : (x.ok ? 'is-ok' : 'is-no')); const m = el('span', 'v2-br-mark', x.info ? '•' : (x.ok ? '✓' : '✕')); m.setAttribute('aria-label', x.info ? 'For reference' : (x.ok ? 'Passes' : 'Fails')); li.append(m, el('b', null, x.k), el('span', null, x.t)); ul.append(li); });
      sec('Research checks', ul);
    }
    if (d.log && d.log.length) {
      const lg = el('p', 'v2-br-log');
      d.log.forEach(([w, o, v, ok]) => { const s2 = el('span', ok ? 'is-ok' : 'is-no', `W${w} ${o} ${Math.round(v)}`); lg.append(s2); });
      sec(`Every 2026 game at ${p.thr} (${p.side === 'No' ? 'under' : 'over'} side)`, lg);
    }
    if (d.alts && d.alts.length) {
      const tb = el('table', 'v2-br-alts'); const th = el('tr'); ['Nearest alternative', 'Price', 'Needs', 'Ours', 'Why this one wins'].forEach((h) => th.append(el('th', null, h))); const tbody = el('tbody'); tb.append(el('thead'), tbody); tb.firstChild.append(th);
      d.alts.forEach((a) => { const tr = el('tr'); tr.append(el('td', null, a.line), el('td', 'num', a.ask + '¢'), el('td', 'num', a.be + '%'), el('td', 'num', a.ours), el('td', null, a.why)); tbody.append(tr); });
      const wrap = el('div', 'v2-br-tw'); wrap.append(tb); sec('Compared at the exact numbers', wrap);
    }
    sec('Strongest objection', el('p', null, d.objection));
    sec('How it misses even if the read is right', el('p', null, d.miss));
    sec('What changes the call', el('p', null, d.change));
    if (d.research) {
      const ul = el('ul', 'v2-br-news'); (d.research.notes || []).forEach((n) => ul.append(el('li', null, n)));
      const src = el('p', 'v2-br-src'); (d.research.src || []).forEach((x, j) => { const a = el('a', null, x.t); a.href = x.u; a.target = '_blank'; a.rel = 'noopener noreferrer'; if (j) src.append(' · '); src.append(a); });
      const w2 = el('div'); w2.append(ul, src); sec('News checked Saturday night', w2);
    }
    return box;
  }
  function v2GameBrain(c) {
    const B = v2B(), g = B && B.games ? B.games[c.game] : null;
    if (!g) return null;
    const box = el('div', 'rs-card v2-th-card v2-br-game');
    box.append(el('h4', null, 'Before any line: the checks on this game'));
    const q = el('p', 'v2-br-qb ' + (g.qb.ok ? 'is-ok' : 'is-no')); q.append(el('b', null, g.qb.ok ? 'Quarterbacks: eligible. ' : 'Quarterbacks: left off this week. '), g.qb.t); box.append(q);
    if (g.interaction && g.interaction.length) { const ul = el('ul', 'v2-br-news'); g.interaction.forEach((x) => ul.append(el('li', null, x))); const s2 = el('div', 'v2-br-sec'); s2.append(el('span', 'wg-lab', 'How the lines here fail together'), ul); box.append(s2); }
    if (g.coverage) { const s2 = el('div', 'v2-br-sec'); s2.append(el('span', 'wg-lab', 'Lines checked'), el('p', null, `${g.coverage.assessed} player ladders run through the lens and the checks. Offered here: ${g.coverage.offered.join(', ') || 'none yet'}. ${g.coverage.gaps}`)); box.append(s2); }
    if (g.revisions && g.revisions.length) {
      const tb = el('table', 'v2-br-alts'); const th = el('tr'); ['Last card’s line', 'Was', 'Now', 'Why'].forEach((h) => th.append(el('th', null, h))); const tbody = el('tbody'); tb.append(el('thead'), tbody); tb.firstChild.append(th);
      g.revisions.forEach((r) => { const tr = el('tr'); tr.append(el('td', null, r.line), el('td', null, r.was), el('td', null, r.v === 'Pass' ? 'Pass' : r.now), el('td', null, r.why)); tbody.append(tr); });
      const wrap = el('div', 'v2-br-tw'); wrap.append(tb); const s2 = el('div', 'v2-br-sec'); s2.append(el('span', 'wg-lab', 'Changes since the last card'), wrap); box.append(s2);
    }
    return box;
  }
  function v2Perf(c, p) {
    const box = el('div', 'v2-perf');
    const m = /^(under )?(\d+)\+? (receptions|receiving yards|rushing yards|passing yards)$/.exec(p.thr || '');
    if (!m) { box.append(el('p', 'wg-note', 'No projection for this market.')); return box; }
    const under = !!m[1], k = +m[2], market = V2_WORD[m[3]], st = V2_STAT[market], unit = SIT_UNIT[st];
    const P = v2Proj(p.player, market);
    const key = (P && P.sit_key) || v2SitKey(p.player), det = key ? SPORTS.nfl.sit(key) : null;
    const f = (v) => fmtStat(st, v);
    box.append(el('span', 'wg-lab', `${p.player} · ${m[3]}`));
    if (P && P.proj !== '') {
      const S3 = [['Bear', num(P.proj_lo), 'bear'], ['Base', num(P.proj), 'base'], ['Bull', num(P.proj_hi), 'bull']];
      const vals = S3.map((x) => x[1]).concat([k]), lo = Math.min(...vals), hi = Math.max(...vals), pad = (hi - lo) * 0.16 || 1, x0 = lo - pad, x1 = hi + pad, pos = (v) => (100 * (v - x0) / (x1 - x0)) + '%';
      const rng = el('div', 'wg-rng v2-rng'); rng.setAttribute('aria-hidden', 'true'); rng.append(el('div', 'wg-rng-track'));
      const ln = el('div', 'wg-rng-line'); ln.style.left = pos(k); rng.append(ln);
      S3.forEach(([, v, cls]) => { const d = el('div', 'wg-rng-dot'); d.style.background = `var(--wg-${cls})`; d.style.left = pos(k); rng.append(d); grow(d, 'left', pos(v)); });
      const lab = el('div', 'wg-rng-lab'); S3.forEach(([nm2, v]) => { const s2 = el('span', null, nm2 + ' '); s2.append(el('b', null, f(v))); lab.append(s2); }); const s3 = el('span', null, 'Line '); s3.append(el('b', null, String(k))); lab.append(s3);
      const clear = S3.filter(([, v]) => (under ? v < k : v >= k)).map(([nm2]) => nm2.toLowerCase());
      box.append(rng, lab, el('p', 'wg-note', clear.length === 3 ? `All three cases: ${under ? 'under' : 'over'} ${k}.` : clear.length ? `${clear.join(' and ').replace(/^./, (x) => x.toUpperCase())}: ${under ? 'under' : 'over'} ${k}.` : `No case reaches ${under ? 'under' : 'over'} ${k}. The read rests on the game.`));
    } else box.append(el('p', 'wg-note', 'No projection for this stat.'));
    if (det) {
      const cols = statOf(det, st), L = det.log, idx = det.base.filter((i) => L[i][0] === 26);
      const vals = idx.map((i) => [L[i][1], L[i][2], cols.reduce((s2, cc) => s2 + (L[i][cc] || 0), 0)]);
      if (vals.length) {
        const W = 300, H = 92, bw = Math.min(26, (W - 30) / vals.length - 4), mx = Math.max(k * 1.25, ...vals.map((x) => x[2])) || 1;
        const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H + 16}`, width: '100%', class: 'v2-bars', role: 'img' });
        let hits = 0;
        vals.forEach(([wk, opp, v], j) => {
          const ok = under ? v < k : v >= k; if (ok) hits += 1;
          const h = Math.max(2, (v / mx) * H), x = 4 + j * (bw + 4);
          const r2 = svgEl('rect', { x, y: H - h, width: bw, height: h, rx: 2, class: ok ? 'ok' : 'no' }); const t = svgEl('title'); t.textContent = `Week ${wk} vs ${String(opp).replace('@', '')}: ${v} ${unit}`; r2.append(t); svg.append(r2);
          const tx = svgEl('text', { x: x + bw / 2, y: H + 12, 'text-anchor': 'middle', class: 'v2-bx' }); tx.textContent = String(wk); svg.append(tx);
        });
        const ly = H - (k / mx) * H; svg.append(svgEl('line', { x1: 0, x2: W, y1: ly, y2: ly, class: 'v2-bl' }));
        const lt = svgEl('text', { x: W - 2, y: ly - 4, 'text-anchor': 'end', class: 'v2-bx' }); lt.textContent = String(k); svg.append(lt);
        svg.setAttribute('aria-label', `${p.player}, 2026 games: ${vals.map((x) => x[2]).join(', ')} ${unit}; ${hits} of ${vals.length} on the ${under ? 'under' : 'over'} side of ${k}.`);
        box.append(svg, el('p', 'wg-note', `2026: ${hits} of ${vals.length} games ${under ? 'under' : 'over'} ${k}.`));
      }
    }
    const go = el('button', 'wz-btn wz-btn-line wz-btn-sm', 'Open his research file'); go.type = 'button';
    go.addEventListener('click', () => {
      const la = dash.data('lines_all');
      const row = la.status === 'ok' ? la.data.find((x) => x.game === c.game && x.market === market && v2Norm(String(x.contract).split(':')[0]) === v2Norm(p.player) && v2LineOf(x) === k - 0.5) : null;
      const r = row || { game: c.game, market, contract: `${p.player}: Over ${k - 0.5} ${({ Receptions: 'Receptions', 'Receiving Yards': 'Receiving Yards', 'Rushing Yards': 'Rush Yards', 'Passing Yards': 'Pass Yards' })[market]}`, yes_price: under ? '' : String(p.price), source: 'Robinhood' };
      const ctx = { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source }; ctx.key = `${ctx.game}|${ctx.market}|${r.contract}`;
      if (r.sit_key && SPORTS.nfl.out(ctx.key)) openSit(r, ctx, go); else v2OpenFile(r, go);
    });
    box.append(go);
    return box;
  }

  // ---------------- ink: the page runs white to grey to black; text on it flips to stay readable ----------------
  const V2_SURF = '.wz-top, .wx-band, .pf-head, .pf-hero-copy, .pf-proof, .pf-row, .wx-fine, .wx-tabs, .v2-seg, .wz-day > h3, .wz-game, .wz-steps > li, .wz-how, .fc-post, .v2-th > .v2-thlink, .v2-th-h, .rs-page > p, .rs-page > .rs-note, .v2-mgrid, .pf-allpicks > summary';
  const V2_CARD = '.wx-read, .wz-an:not(.lead), .wz-cover, .rs-card, .pf-tt, .pf-tpanel, .fc-stat, .fc-how, .fc-game, .wx-reads .wx-empty, .v2-soon, .wg-soon';
  const V2_GRAD = [[0, [243, 244, 245]], [0.14, [225, 227, 230]], [0.38, [180, 185, 191]], [0.58, [118, 124, 131]], [0.78, [46, 50, 55]], [1, [11, 12, 14]]];
  const v2Lum = (t) => {
    let i = 1; while (i < V2_GRAD.length - 1 && V2_GRAD[i][0] < t) i++;
    const [t0, c0] = V2_GRAD[i - 1], [t1, c1] = V2_GRAD[i], k = Math.max(0, Math.min(1, (t - t0) / (t1 - t0 || 1)));
    const lin = (v) => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    const c = c0.map((v, j) => v + (c1[j] - v) * k);
    return 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
  };
  function v2Ink() { return; /* V1's look: one dark page, no ink flipping */ }
  function v2InkOld() {
    const paper = $('.wg-paper'); if (!paper) return;
    const pr = paper.getBoundingClientRect(), H = paper.offsetHeight || 1;
    paper.querySelectorAll(V2_SURF + ', ' + V2_CARD).forEach((e) => {
      if (e.closest('dialog')) return;
      const r = e.getBoundingClientRect(); if (!r.width && !r.height) return;
      const card = e.matches(V2_CARD);
      const t = (r.top - pr.top + (card ? r.height / 2 : Math.min(r.height, 80) / 2)) / H;
      const ink = v2Lum(t) > 0.2 ? 'd' : 'l';
      if (e.dataset.ink !== ink) e.dataset.ink = ink;
    });
    paper.dataset.v2 = '1';
  }
  function v2InkSoon() {
    cancelAnimationFrame(V2.inkRaf); V2.inkRaf = requestAnimationFrame(v2Ink);
    clearTimeout(V2.inkT); V2.inkT = setTimeout(v2Ink, 450);
  }
  (() => {
    const paper = $('.wg-paper'); if (!paper) return;
    if (window.ResizeObserver) { const ro = new ResizeObserver(() => v2InkSoon()); ro.observe(paper); }
    window.addEventListener('resize', v2InkSoon);
    document.addEventListener('toggle', v2InkSoon, true);
    v2InkSoon();
  })();
  // a read card's team colors: the player's team once the rosters have loaded, the two teams in the game until then
  function v2Tint(b) {
    const r = { game: b.dataset.game, contract: b.dataset.player };
    if (wzPlayerTeam(r)) { wzTint(b, r); b.classList.add('v2-tc-player'); return; }
    const [a, h] = wzSides(r.game || '');
    if (a && h && WZ_TEAMS[a] && WZ_TEAMS[h]) { b.classList.add('wz-tc'); b.style.setProperty('--tc1', WZ_TEAMS[a][1]); b.style.setProperty('--tc2', WZ_TEAMS[h][1]); }
  }
  function v2OnData() {
    document.querySelectorAll('.wx-read.v2-read[data-game]:not(.v2-tc-player)').forEach((b) => v2Tint(b));
    v2Home();
    const th = $('#thesis'); if (th && !th.hidden) v2Thesis();
    v2InkSoon();
  }

  // ---------------- the read card's sheen on every line ----------------
  // Rows and cards get the colors of the player's team; game lines get the two teams' colors; NBA rows get Wedge green.
  function v2Sheen(node, r, nba) {
    if (!node) return node;
    node.classList.add('v2-sheen');
    if (nba) return node;
    let c1 = node.style.getPropertyValue('--tc1'), c2 = node.style.getPropertyValue('--tc2');
    if (!c1) {
      const t = r ? wzPlayerTeam(r) : null, [a, h] = wzSides((r && r.game) || '');
      if (t && WZ_TEAMS[t]) { c1 = WZ_TEAMS[t][1]; c2 = WZ_TEAMS[t][2]; }
      else if (a && h && WZ_TEAMS[a] && WZ_TEAMS[h]) { c1 = WZ_TEAMS[a][1]; c2 = WZ_TEAMS[h][1]; }
    }
    if (c1) { node.style.setProperty('--tc1', c1); node.style.setProperty('--tc2', c2 || c1); node.classList.add('v2-sheen-t'); }
    return node;
  }

  // ---------------- The Winning Edge in Home's language ----------------
  function v2Head(n, label, title, sub) {
    const h = el('div', 'pf-head v2-head'), l = el('div');
    l.append(el('span', 'pf-label', `${String(n).padStart(2, '0')} / ${label}`), el('h2', 'pf-h2 v2-h2', title));
    h.append(l); if (sub) h.append(el('p', 'pf-sub', sub));
    return h;
  }
  function v2EdgeLayout(all, top, games) {
    const fin = all.filter(([, p]) => p.decision === 'Final line').sort((x, y) => !!x[1].result - !!y[1].result);
    const s1 = el('section', 'v2-edge-sec');
    s1.append(v2Head(1, 'Final lines', 'This week’s final lines.', null));
    const row = el('div', 'wx-reads v2-edge-reads');
    fin.forEach(([c, p], n) => {
      const card = v2ReadCard(c, p, c.plays.indexOf(p));
      const k = card.querySelector('.wx-read-top > span'); if (k) k.textContent = `${String(n + 1).padStart(2, '0')} · ${c.game} · ${v2Kick(c)}`;
      row.append(card);
    });
    if (!fin.length) row.append(el('p', 'wx-empty', 'No final lines yet. Leans are below.'));
    else if (fin.every(([, p]) => p.result)) row.prepend(el('p', 'wx-empty v2-edge-note', 'No final line for Monday night. Sunday’s, graded:'));
    s1.append(row);
    top.prepend(v2Head(2, 'The card', 'Every call.', null));
    const s3 = el('section', 'v2-edge-sec v2-edge-games');
    s3.append(v2Head(3, 'Game by game', 'Every game.', null), games);
    return [s1, top, s3];
  }

  // ---------------- speed: the hero's background motion runs only while the hero is on screen ----------------
  (() => {
    const hero = document.querySelector('.pf-hero'); if (!hero || !('IntersectionObserver' in window)) return;
    new IntersectionObserver((es) => es.forEach((e) => hero.classList.toggle('v2-still', !e.isIntersecting)), { rootMargin: '80px 0px' }).observe(hero);
    document.addEventListener('visibilitychange', () => hero.classList.toggle('v2-still', document.hidden));
  })();

  // ---------------- speed: draw what's on screen, fetch the research files' data ahead of the first click ----------------
  // Everything here can be reached before this part of the script has run (a link straight to #research opens that
  // page while the script is still loading), so it uses hoisted functions and vars that start out undefined.
  var V2_DRAWS, v2Dirty, v2RedrawRaf, v2Fetched;
  function v2DrawsInit() {
    if (V2_DRAWS) return;
    // each page's tables; Charts and the NBA record pages already redraw each time they open
    V2_DRAWS = { research: () => { drawLines(); drawProj(); }, nba: () => drawNba(), results: () => { drawResultsSummary(); drawResults(); }, analysts: () => drawAnalysts() };
    v2Dirty = new Set(Object.keys(V2_DRAWS));
  }
  function v2CurPage() { const c = document.querySelector('.rs-page:not([hidden])'); return c ? c.id : ''; }
  function v2Redraw() {
    v2RedrawRaf = 0; v2DrawsInit();
    drawRecord(); drawProfit(); drawLobby(); v2OnData();
    Object.keys(V2_DRAWS).forEach((k) => v2Dirty.add(k));
    const cur = v2CurPage();
    v2DrawIfDirty(cur);
    if (cur === 'charts') drawCharts();
    if (NBA_PAGES.has(cur)) drawNbaRec();
  }
  function v2RedrawSoon() { if (!v2RedrawRaf) v2RedrawRaf = requestAnimationFrame(v2Redraw); }
  function v2DrawIfDirty(id) { v2DrawsInit(); if (V2_DRAWS[id] && v2Dirty.has(id)) { v2Dirty.delete(id); V2_DRAWS[id](); } }
  // the research file's data: outlook, player histories, game context, injury reports
  function v2Prefetch() { if (v2Fetched) return; v2Fetched = true; ['outlook', 'sit', 'nflctx', 'inj', 'defhist'].forEach((id) => { try { dash.data(id); } catch (e) { /* loads on first open instead */ } }); }
  function v2Idle(fn, ms) { return window.requestIdleCallback ? window.requestIdleCallback(fn, { timeout: ms }) : setTimeout(fn, ms); }
  function v2PrefetchFor(id) { if (['research', 'final', 'thesis'].includes(id)) v2Idle(v2Prefetch, 400); }
  // on Home, fetch it once the page has settled; any line row or matchup touched fetches it at once
  setTimeout(() => v2Idle(v2Prefetch, 3000), 4000);
  document.addEventListener('pointerover', (e) => { if (!v2Fetched && e.target.closest && e.target.closest('.rs-table tbody tr, .v2-mt, .wx-read')) v2Prefetch(); }, { passive: true });
