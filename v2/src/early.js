  // ---------------- r18 · early lines: player markets Kalshi hasn't listed, priced from the sportsbooks ----------------
  let v2EarlyDone = false;
  const v2EaPct = (x) => (x == null ? '—' : `${Math.round(x)}%`);
  function v2EarlyCard(c, p) {
    const fin = p.decision === 'Final line';
    const d = el('article', 'v2-ea-card ' + (fin ? 'is-final' : 'is-lean'));
    const top = el('div', 'v2-ea-top');
    top.append(el('span', 'v2-ea-game', `${c.game} · ${String(c.kick || '').replace(/\s*CT\s*/, ' ')}`), el('span', 'v2-ea-tag', fin ? 'Early final' : 'Early lean'));
    const title = el('h4', null, p.line.replace(/ \((Yes|No)\)$/, ''));
    const nums = el('div', 'v2-ea-nums');
    const cell = (k, v, s) => { const b = el('div', 'v2-ea-n'); b.append(el('small', null, k), el('b', null, v)); if (s) b.append(el('span', null, s)); return b; };
    nums.append(cell('Expected price', `${p.side} ${p.price}¢`, `mid ${Math.round(p.mkt)}¢`), cell('Needs', `${p.be}%`, 'price + 2¢ fees'),
      cell('Our number', `${p.est[0]}–${p.est[1]}%`, `middle ${v2EaPct(p.mid)}`));
    const bk = p.books || {};
    const bl = el('p', 'v2-ea-books');
    bl.textContent = bk.n ? `Books: ${bk.n} lines, average ${bk.line} (Over ${Math.round(100 * bk.p_over)}% with the vig removed).` : 'Books: priced from the sportsbooks.';
    const cond = el('p', 'v2-ea-cond', p.cond);
    const why = el('p', 'v2-ea-why', p.why);
    const more = el('details', 'v2-ea-more'); more.append(el('summary', null, 'Book lines, ladder and record'));
    if (bk.text) more.append(el('p', 'v2-ea-small', bk.text));
    if (p.sample) more.append(el('p', 'v2-ea-small', p.sample));
    if (p.counter) more.append(el('p', 'v2-ea-small', 'Against it: ' + p.counter));
    if (p.ladder && p.ladder.length) {
      const box = el('div', 'rs-tablebox'); const t = el('table', 'rs-table v2-ea-lad'); const th = el('thead'); const hr = el('tr');
      ['Rung', 'Expected', 'Needs', 'Ours', 'Call'].forEach((h) => hr.append(el('th', null, h))); th.append(hr);
      const tb = el('tbody');
      p.ladder.forEach((r) => {
        const tr = el('tr', r.tag === 'card' ? 'is-pick' : null);
        [`${r.t} (${r.side})`, `${r.ask}¢`, `${r.be}%`, `${Math.round(r.lo)}–${Math.round(r.hi)}%`, r.call === 'Pass' ? 'Pass' : r.call === 'Final line' ? 'Final' : 'Lean'].forEach((v, i) => tr.append(el('td', i ? 'fc-n' : null, v)));
        tb.append(tr);
      });
      t.append(th, tb); box.append(t); more.append(box);
    }
    d.append(top, title, nums, cond, why, bl, more);
    return d;
  }
  function v2EarlyRender() {
    const box = $('#fc-early'); const F = v2F();
    if (!box || v2EarlyDone || !F || !F.early) return;
    v2EarlyDone = true;
    const E = F.early, C = E.cal || {};
    const list = []; (F.cards || []).forEach((c) => (c.early || []).forEach((p) => list.push([c, p])));
    list.sort((a, b) => (a[1].decision !== 'Final line') - (b[1].decision !== 'Final line') || b[1].edge_mid - a[1].edge_mid);
    const head = el('header', 'v2-ea-head');
    head.append(el('span', 'v2-ea-k', 'Early lines · not on Kalshi yet'),
      el('h3', null, list.length ? `${E.final} early final line${E.final === 1 ? '' : 's'} and ${E.lean} early lean${E.lean === 1 ? '' : 's'}` : 'Nothing clears at the expected prices yet'),
      el('p', 'v2-ea-lede', `Kalshi hasn’t listed ${E.assessed} player markets on this slate yet: receptions and rush + rec yards in most games, and every prop in NYJ @ LAC and CIN @ WSH. `
        + `We priced each one from ${E.books.length} sportsbooks (${E.books.join(', ')}), checked ${fcTime(E.at)}, moved it onto Kalshi’s scale and ran it through the same final-lines process as the card. `
        + 'The price is where we expect the rung to open, not a quote you can trade. Each line names the most it can cost and still hold.'));
    const stats = el('div', 'v2-ea-stats');
    const st = (n, t) => { const s = el('div', 'v2-ea-stat'); s.append(el('b', null, String(n)), el('span', null, t)); return s; };
    stats.append(st(E.final, 'early final lines'), st(E.lean, 'early leans'), st(E.assessed, 'player markets priced from the books'),
      st(`${Number(C.mae_cal).toFixed(1)}¢`, `average miss vs Kalshi on ${Number(C.n || 0).toLocaleString('en-US')} rungs both list`));
    const grid = el('div', 'v2-ea-grid');
    list.forEach(([c, p]) => grid.append(v2EarlyCard(c, p)));
    const bandGap = (k) => { const x = (C.bands || []).find((r) => r.band === k); return x && x.yds != null ? Math.round(-x.yds) : null; };
    const g1 = bandGap('80-90'), g2 = bandGap('90-97');
    const gapTxt = g1 > 0 && g2 > 0 ? `about ${g1} points at 80–90% and ${g2} at 90% or more` : '';
    const fine = el('p', 'v2-tool-fine', `How the expected price is set: each book’s main line is taken without the vig, the player’s distribution is fit to all of them, and every Kalshi rung is priced from that curve. `
      + (gapTxt ? `Kalshi runs below the books on the likely yardage rungs (${gapTxt}), so ` : 'So ') + `each rung is moved by the gap seen on the ${Number(C.n || 0).toLocaleString('en-US')} rungs both list today `
      + `(${C.players} players in ${C.games} games), and given Kalshi’s typical ${C.spread_med}¢ bid-ask spread. Tested one game at a time, the expected price landed within 3¢ of Kalshi’s mid ${C.within3}% of the time. `
      + 'Only markets with three or more books are priced. Quarterback rule, research checks and the one-under-per-three-overs mix apply as on the card. Estimates, not promises. 21+. Gambling problem? Call 1-800-GAMBLER.');
    box.replaceChildren(head, stats, list.length ? grid : el('p', 'wx-empty', 'Nothing clears break-even at the expected prices yet.'), fine);
    box.hidden = false;
  }
