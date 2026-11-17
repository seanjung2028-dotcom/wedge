  // ---------------- Line Shopping (live, wedgepicks.com): /api/v1/shop/* ----------------
  // Kalshi's prices read live by the site's server, priced after Kalshi's and Robinhood's fees; Wedge's number on the live
  // price for plans that include the card (the server decides). Sportsbooks are listed without prices until a feed is connected.
  const SH = { games: null, game: '', board: null, sel: '', det: null, side: 'yes', size: 10, q: '', stat: '', timer: 0, err: '', loading: false };
  const SH_STAT = { rec: 'receptions', recyd: 'receiving yards', rushyd: 'rushing yards', rryd: 'rush + rec yards' };
  const shF = (v, d = 1) => (v == null || !isFinite(v) ? '—' : Number(v).toFixed(d));
  const shSg = (v) => (v == null ? '—' : (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(v).toFixed(1));
  const shCT = (iso, opt) => { try { return new Date(iso).toLocaleString('en-US', { timeZone: 'America/Chicago', hour: 'numeric', minute: '2-digit', ...(opt || {}) }) + ' CT'; } catch (e) { return ''; } };
  const shLine = (r, side) => `${r.n} ${side === 'no' ? 'under ' + r.k : r.k + '+'} ${SH_STAT[r.s]}`;
  async function shGet(path, opt) {
    const r = await fetch(path, { credentials: 'same-origin', headers: { accept: 'application/json', 'content-type': 'application/json' }, ...(opt || {}) });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) { const e = new Error(j.message || j.error || 'HTTP ' + r.status); e.code = j.error || r.status; throw e; }
    return j;
  }
  const shWatch = {
    get() { try { return JSON.parse(localStorage.getItem('wedge-watch') || '[]'); } catch (e) { return []; } },
    set(v) { try { localStorage.setItem('wedge-watch', JSON.stringify(v.slice(0, 12))); } catch (e) { /* storage unavailable: the star just won't stick */ } },
    has(t, s) { return this.get().some((w) => w.t === t && w.s === s); },
  };

  async function v2ShopOpen() {
    const st = $('#shop-status'); if (!st) return;
    shBindControls();
    const sd = $('#shop-side'); if (sd) sd.value = SH.side;
    if (!SH.games) {
      try {
        const g = await shGet('/api/v1/shop/games');
        SH.games = g.games || [];
        const first = SH.games.find((x) => x.priced) || SH.games[0];
        SH.game = SH.game || (first ? first.code : '');
      } catch (e) {
        SH.games = null;
        st.textContent = location.protocol === 'file:' || /claude\.ai$/.test(location.hostname) ? 'Line Shopping runs on wedgepicks.com.' : 'Live prices are unavailable right now. Try again in a minute.';
        return;
      }
    }
    shDrawGames();
    shDrawWatch();
    await shLoad();
    clearInterval(SH.timer);
    SH.timer = setInterval(() => { const p = $('#shop'); if (p && !p.hidden && document.visibilityState === 'visible') shLoad(true); else clearInterval(SH.timer); }, 30000);
  }

  function shDrawGames() {
    const box = $('#shop-games'); if (!box) return;
    box.replaceChildren(...(SH.games || []).map((g) => {
      const b = el('button', 'v2-sh-game'); b.type = 'button';
      b.setAttribute('aria-pressed', g.code === SH.game ? 'true' : 'false');
      b.append(el('b', null, g.game), el('small', null, g.ko ? shCT(g.ko, { weekday: 'short' }) : ''));
      if (g.priced) b.append(el('i', 'v2-sh-dot', 'Wedge'));
      b.addEventListener('click', () => { SH.game = g.code; SH.sel = ''; SH.det = null; shDrawGames(); shLoad(); });
      return b;
    }));
  }

  async function shLoad(quiet) {
    if (!SH.game || SH.loading) return;
    SH.loading = true;
    if (!quiet) { $('#shop-list').replaceChildren(el('p', 'v2-sh-empty', 'Reading Kalshi’s prices…')); }
    try {
      SH.board = await shGet(`/api/v1/shop/board?game=${encodeURIComponent(SH.game)}&size=${SH.size}`);
      SH.err = '';
    } catch (e) { SH.err = 'Kalshi’s prices didn’t load. Trying again in 30 seconds.'; }
    SH.loading = false;
    shDrawList();
    if (SH.sel) shDetail(SH.sel, true);
  }

  function shRowSide(r, side) {
    const k = side === 'no' ? r.n_eff : r.y_eff, h = side === 'no' ? r.n_rh : r.y_rh;
    const best = k == null ? h : (h == null ? k : Math.min(k, h));
    let w = null, gap = null, call = null;
    if (r.w) {
      w = side === 'no' ? [100 - r.w[2], 100 - r.w[1], 100 - r.w[0]] : r.w;
      gap = side === 'no' ? r.gn : r.gy; call = side === 'no' ? r.cn : r.cy;
    }
    return { kalshi: k, rh: h, best, w, gap, call, card: side === 'no' ? r.card_n : r.card_y };
  }

  function shDrawList() {
    const B = SH.board, box = $('#shop-list'), st = $('#shop-status');
    if (!box || !st) return;
    if (!B) { box.replaceChildren(el('p', 'v2-sh-empty', SH.err || '')); return; }
    const bits = [`Kalshi prices read ${shCT(B.at, { second: '2-digit' })}`, 'refreshing every 30 seconds'];
    bits.push(B.wedge ? `Wedge’s numbers: the card build’s lens on the live price` : 'Wedge’s numbers are part of Inner Circle');
    st.textContent = (SH.err ? SH.err + ' ' : '') + bits.join(' · ') + (B.partial ? ' · some ladders didn’t load' : '');
    const q = SH.q.trim().toLowerCase();
    let rows = B.rows.filter((r) => (!SH.stat || r.s === SH.stat) && (!q || r.n.toLowerCase().includes(q) || shLine(r, SH.side).toLowerCase().includes(q)));
    const withSide = rows.map((r) => ({ r, x: shRowSide(r, SH.side) })).filter((o) => o.x.best != null && o.x.best > 3 && o.x.best < 97);
    if (B.wedge) withSide.sort((a, b) => (b.x.gap == null ? -99 : b.x.gap) - (a.x.gap == null ? -99 : a.x.gap));
    const shown = withSide.slice(0, 60);
    if (!shown.length) { box.replaceChildren(el('p', 'v2-sh-empty', B.rows.length ? 'No lines match.' : 'Kalshi has no receiving or rushing ladders open for this game yet.')); return; }
    const out = [];
    for (const { r, x } of shown) {
      const b = el('button', 'v2-sh-row' + (SH.sel === r.t ? ' is-sel' : '')); b.type = 'button';
      const mid = el('div', 'v2-sh-row-mid');
      mid.append(el('b', null, shLine(r, SH.side)), el('small', null, `Kalshi ${shF(x.kalshi)}% · Robinhood ${shF(x.rh)}%${r.dy != null && SH.side === 'yes' ? ' · ' + Math.round(r.dy) + ' at the ask' : ''}`));
      const right = el('div', 'v2-sh-row-r');
      if (x.w) {
        const chip = el('span', 'v2-sh-gap' + (x.gap >= 0.5 ? ' is-pos' : ''), shSg(x.gap));
        right.append(el('span', 'v2-sh-w', shF(x.w[1]) + '%'), chip);
      } else right.append(el('span', 'v2-sh-w is-dim', B.wedge ? (r.ws === 'thin' ? 'thin book' : 'not priced') : 'Inner Circle'));
      if (x.card) right.append(el('span', 'v2-sh-card', x.card === 'Final line' ? 'Final' : 'Lean'));
      b.append(r.tm ? wzHelmet(r.tm, false) : el('span'), mid, right);
      b.setAttribute('aria-label', `${shLine(r, SH.side)}: best ${shF(x.best)}% after fees${x.w ? `, Wedge ${shF(x.w[1])}%, gap ${shSg(x.gap)} points` : ''}`);
      b.addEventListener('click', () => { SH.sel = r.t; box.querySelectorAll('.v2-sh-row').forEach((y) => y.classList.toggle('is-sel', y === b)); shDetail(r.t); });
      out.push(b);
    }
    if (withSide.length > shown.length) out.push(el('p', 'v2-sh-more', `Showing ${shown.length} of ${withSide.length}. Search to narrow it down.`));
    box.replaceChildren(...out);
    if (!SH.sel && shown.length && window.matchMedia('(min-width: 900px)').matches) { SH.sel = shown[0].r.t; box.firstChild.classList.add('is-sel'); shDetail(SH.sel); }
  }

  async function shDetail(ticker, quiet) {
    const box = $('#shop-detail'); if (!box) return;
    if (!quiet) box.replaceChildren(el('p', 'v2-sh-empty', 'Opening the line…'));
    try {
      SH.det = await shGet(`/api/v1/shop/market?ticker=${encodeURIComponent(ticker)}&side=${SH.side}&size=${SH.size}`);
    } catch (e) { if (!quiet) box.replaceChildren(el('p', 'v2-sh-empty', 'That line didn’t load. Pick it again in a moment.')); return; }
    box.replaceChildren(shCard(SH.det, true));
    if (!quiet && !window.matchMedia('(min-width: 900px)').matches) box.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // one line, every platform (used by Line Shopping and by the Analyst's answer cards)
  function shCard(d, full) {
    const wrap = el('article', 'v2-sh-det');
    const head = el('header', 'v2-sh-det-h');
    const ttl = el('div'); ttl.append(el('h3', null, d.line), el('p', null, `${d.game}${d.ko ? ' · ' + shCT(d.ko, { weekday: 'short' }) : ''} · prices read ${shCT(d.at, { second: '2-digit' })}`));
    head.append(d.team ? wzHelmet(d.team, false) : el('span'), ttl);
    if (full) {
      const star = el('button', 'v2-sh-star'); star.type = 'button';
      const on = shWatch.has(d.ticker, d.side);
      star.setAttribute('aria-pressed', on ? 'true' : 'false'); star.setAttribute('aria-label', on ? 'Stop watching this line' : 'Watch this line');
      star.textContent = on ? '★' : '☆';
      star.addEventListener('click', () => {
        let W = shWatch.get(); if (shWatch.has(d.ticker, d.side)) W = W.filter((w) => !(w.t === d.ticker && w.s === d.side)); else W.unshift({ t: d.ticker, s: d.side, l: d.line, g: SH.game });
        shWatch.set(W); star.setAttribute('aria-pressed', shWatch.has(d.ticker, d.side) ? 'true' : 'false'); star.textContent = shWatch.has(d.ticker, d.side) ? '★' : '☆'; shDrawWatch();
      });
      head.append(star);
    }
    wrap.append(head);
    if (full) {
      const seg = el('div', 'v2-sh-seg'); seg.setAttribute('role', 'group'); seg.setAttribute('aria-label', 'Side');
      for (const [v, lab] of [['yes', 'Yes · over'], ['no', 'No · under']]) {
        const b = el('button', null, lab); b.type = 'button'; b.setAttribute('aria-pressed', SH.side === v ? 'true' : 'false');
        b.addEventListener('click', () => { if (SH.side === v) return; SH.side = v; const s = $('#shop-side'); if (s) s.value = v; shDrawList(); shDetail(d.ticker); });
        seg.append(b);
      }
      wrap.append(seg);
    }
    // Wedge against the market
    const W = d.wedge, best = d.best_eff;
    const wb = el('section', 'v2-sh-wedge');
    if (W && W.status === 'ok') {
      const lo = Math.max(0, Math.floor(Math.min(W.lo, W.mid, best == null ? W.lo : best) - 4)), hi = Math.min(100, Math.ceil(Math.max(W.hi, W.mid, best == null ? W.hi : best) + 4));
      const X = (v) => `${((v - lo) / (hi - lo)) * 100}%`;
      const bar = el('div', 'v2-sh-bar'); bar.setAttribute('role', 'img');
      bar.setAttribute('aria-label', `Wedge ${shF(W.p)}% (range ${shF(W.lo)} to ${shF(W.hi)}), market middle ${shF(W.mid)}%, best price needs ${shF(best)}%`);
      const band = el('i', 'v2-sh-band'); band.style.left = X(W.lo); band.style.width = `calc(${X(W.hi)} - ${X(W.lo)})`;
      const mk = (cls, v) => { const t = el('i', cls); t.style.left = X(v); return t; };
      bar.append(band, mk('v2-sh-tick is-w', W.p), mk('v2-sh-tick is-m', W.mid));
      if (best != null) bar.append(mk('v2-sh-tick is-n', best));
      const ax = el('div', 'v2-sh-ax'); ax.append(el('span', null, lo + '%'), el('span', null, hi + '%'));
      const keys = el('div', 'v2-sh-keys');
      const key = (cls, k, v, sub) => { const s = el('div', 'v2-sh-key ' + cls); s.append(el('small', null, k), el('b', null, v), el('small', null, sub)); return s; };
      keys.append(key('is-w', 'Wedge', shF(W.p) + '%', `${shF(W.lo)} – ${shF(W.hi)}`), key('is-m', 'Market middle', shF(W.mid) + '%', 'Kalshi bid–ask'), key('is-n', 'Best needs', shF(best) + '%', d.best ? `${d.best}, after fees` : ''));
      wb.append(keys, bar, ax);
      if (d.verdict) {
        const v = el('p', 'v2-sh-ev'); const pill = el('span', 'v2-sh-pill' + (d.verdict.call === 'No edge at this price' ? '' : ' is-pos'), d.verdict.call);
        v.append(pill, document.createTextNode(` Estimated value at the best price: ${shSg(d.verdict.ev_mid)}¢ a contract (range ${shSg(d.verdict.ev_lo)} to ${shSg(d.verdict.ev_hi)}).`));
        wb.append(v);
      }
      if (W.why && W.why.length) wb.append(el('p', 'v2-sh-why', 'What moves it: ' + W.why.map(([k, v]) => `${k} ${shSg(v)}`).join(' · ')));
      if (W.q) wb.append(el('p', 'v2-sh-why', `Injury report at the card build: ${W.q}.`));
      if (d.card) wb.append(el('p', 'v2-sh-cardnote', `On this week’s card: ${d.card.call} at ${d.card.price}¢ (Wedge ${shF(d.card.lo)}–${shF(d.card.mid)}–${shF(d.card.hi)}% then).`));
    } else if (d.wedge_locked) {
      wb.classList.add('is-locked');
      const p = el('p', null, 'Wedge’s number and the estimated value at each price are part of Inner Circle.');
      const go = el('button', 'wz-btn wz-btn-line wz-btn-sm', 'See plans ↗'); go.type = 'button'; go.addEventListener('click', () => { showPage('subscribe'); });
      wb.append(p, go);
    } else wb.append(el('p', 'v2-sh-why', W && W.status === 'thin' ? 'The book is too thin for a live Wedge number (no bid, or a spread over 8¢).' : 'Wedge hasn’t priced this line. Lines are priced at each card build.'));
    wrap.append(wb);
    // platforms
    const tb = el('div', 'v2-sh-plat');
    for (const r of d.rows) {
      const row = el('div', 'v2-sh-prow' + (r.platform === d.best ? ' is-best' : '') + (r.status !== 'live' ? ' is-off' : ''));
      const a = el('div'); a.append(el('b', null, r.platform), el('small', null, r.kind));
      if (r.status === 'live') {
        const m = el('small', 'v2-sh-pm', `ask ${shF(r.ask, 0)}¢ + fee ${r.fee_note ? 'up to ' : ''}${shF(r.fee, 2)}¢${r.depth != null ? ` · ${Math.round(r.depth)} at the ask` : ''}${r.thin ? ' · thin' : ''}`);
        a.append(m);
        const b = el('div', 'v2-sh-pr'); b.append(el('b', null, shF(r.eff) + '%'));
        if (r.platform === d.best) b.append(el('span', 'v2-sh-best', 'Best'));
        row.append(a, b);
      } else { row.append(a, el('div', 'v2-sh-pr', 'No feed')); }
      tb.append(row);
    }
    wrap.append(tb);
    const k = d.rows.find((r) => r.platform === 'Kalshi');
    if (k && k.fill_avg != null) wrap.append(el('p', 'v2-sh-fine', `Filling ${d.size} contracts on Kalshi averages ${shF(k.fill_avg, 2)}¢ (${shF(k.fill_eff)}% after fees)${k.filled < d.size ? `; only ${Math.round(k.filled)} are offered` : ''}. Robinhood fills on the same book. Sportsbooks need a licensed odds feed, which isn’t connected yet.`));
    if (full) {
      // the ladder
      if (d.ladder && d.ladder.length > 1) {
        const lad = el('div', 'v2-sh-lad'); lad.append(el('h4', null, 'Every rung'));
        const t = el('table'); const hr = el('tr'); ['Rung', 'Needs', ...(d.wedge_locked ? [] : ['Wedge', 'Gap'])].forEach((h) => { const th = el('th', null, h); th.scope = 'col'; hr.append(th); });
        const th0 = el('thead'); th0.append(hr); t.append(th0); const tbd = el('tbody');
        for (const l of d.ladder) {
          const tr = el('tr', l.ticker === d.ticker ? 'is-sel' : ''); const c0 = el('th', null, `${d.side === 'no' ? 'under ' : ''}${l.k}${d.side === 'no' ? '' : '+'}`); c0.scope = 'row';
          tr.append(c0, el('td', null, shF(l.eff) + '%'));
          if (!d.wedge_locked) tr.append(el('td', null, l.w != null ? shF(l.w) + '%' : '—'), el('td', l.gap >= 0.5 ? 'is-pos' : '', l.gap != null ? shSg(l.gap) : '—'));
          if (l.ticker !== d.ticker) { tr.tabIndex = 0; tr.addEventListener('click', () => { SH.sel = l.ticker; shDetail(l.ticker); }); tr.addEventListener('keydown', (e) => { if (e.key === 'Enter') { SH.sel = l.ticker; shDetail(l.ticker); } }); }
          tbd.append(tr);
        }
        t.append(tbd); lad.append(t); wrap.append(lad);
      }
      // 72 hours of Kalshi prices
      const H = d.history || [];
      const hist = el('div', 'v2-sh-hist'); hist.append(el('h4', null, 'Kalshi ask, last 72 hours'));
      if (H.length >= 2) {
        const vals = H.map((h) => h.ask), mn = Math.min(...vals) - 2, mx = Math.max(...vals) + 2, w = 320, h = 90;
        const px = (i) => 4 + (i / (H.length - 1)) * (w - 8), py = (v) => h - 6 - ((v - mn) / Math.max(mx - mn, 1)) * (h - 12);
        const ns = 'http://www.w3.org/2000/svg', svg = document.createElementNS(ns, 'svg');
        svg.setAttribute('viewBox', `0 0 ${w} ${h}`); svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', `Kalshi ask moved from ${vals[0]}¢ to ${vals[vals.length - 1]}¢ over ${H.length} hours`);
        const pl = document.createElementNS(ns, 'polyline'); pl.setAttribute('points', H.map((x, i) => `${px(i)},${py(x.ask)}`).join(' ')); pl.setAttribute('fill', 'none'); pl.setAttribute('class', 'v2-sh-line');
        svg.append(pl); hist.append(svg, el('p', 'v2-sh-fine', `${vals[0]}¢ ${shCT(new Date(H[0].t * 1000).toISOString(), { weekday: 'short' })} → ${vals[vals.length - 1]}¢ now`));
      } else hist.append(el('p', 'v2-sh-fine', 'Not enough trading yet to draw a line.'));
      wrap.append(hist);
      if (d.rules && d.rules[0]) { const det = el('details', 'v2-sh-rules'); det.append(el('summary', null, 'How Kalshi settles it'), el('p', null, d.rules[0]), ...(d.rules[1] ? [el('p', null, d.rules[1].split('\n')[0])] : [])); wrap.append(det); }
      const ask = el('button', 'wz-btn wz-btn-w wz-btn-sm v2-sh-ask', 'Ask the Analyst about this line ↗'); ask.type = 'button';
      ask.addEventListener('click', () => v2AskWith(`Is ${d.line.replace(/ \((Yes|No)\)$/, '')} worth it at the best price right now?`));
      wrap.append(ask);
    } else {
      const open = el('button', 'wz-link', 'Open in Line Shopping'); open.type = 'button';
      open.addEventListener('click', () => { SH.game = d.ticker.split('-')[1].slice(7); SH.sel = d.ticker; SH.side = d.side; showPage('shop'); });
      wrap.append(open);
    }
    return wrap;
  }

  async function shDrawWatch() {
    const box = $('#shop-watch'); if (!box) return;
    const W = shWatch.get();
    if (!W.length) { box.hidden = true; return; }
    box.hidden = false;
    const chips = W.map((w) => { const b = el('button', 'v2-sh-wchip'); b.type = 'button'; b.append(el('b', null, w.l)); b.addEventListener('click', () => { SH.game = w.g || SH.game; SH.side = w.s; SH.sel = w.t; shDrawGames(); shLoad(); }); return b; });
    box.replaceChildren(el('span', 'v2-sh-wlab', 'Watching'), ...chips, el('small', 'v2-sh-wnote', 'Saved on this device. Alerts arrive when accounts open.'));
  }

  function shBindControls() {
    const q = $('#shop-q'), st = $('#shop-stat'), sd = $('#shop-side'), sz = $('#shop-size');
    if (!q || q.dataset.bound) return; q.dataset.bound = '1';
    q.addEventListener('input', () => { SH.q = q.value; shDrawList(); });
    st.addEventListener('change', () => { SH.stat = st.value; shDrawList(); });
    sd.addEventListener('change', () => { SH.side = sd.value; shDrawList(); if (SH.sel) shDetail(SH.sel); });
    sz.addEventListener('change', () => { SH.size = Math.min(Math.max(parseInt(sz.value, 10) || 10, 1), 500); sz.value = SH.size; shLoad(); });
  }
