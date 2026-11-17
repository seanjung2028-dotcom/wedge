  // ---------------- Results: the final-line record (Weeks 1-9, backtested) ----------------
  // datasets: card_bt_sum (records, key final_bt) and card_bt (every backtested pick), from bt/card_bt/summary.py
  function v2DrawFrec() {
    const box = $('#results-frec'); if (!box) return;
    const S = dash.data('card_bt_sum'), P = dash.data('card_bt');
    if (S.status === 'ok') {
      const r = S.data.find((x) => x.key === 'final_bt');
      if (r) {
        const pct = $('#frec-pct'); pct.classList.remove('dash-skeleton');
        pct.replaceChildren(document.createTextNode(String(Number(r.win_pct))), el('small', null, '%'));
        $('#frec-wl').textContent = `${r.wins}–${r.losses}`;
        $('#frec-net').textContent = signed(r.roi_pct);
      }
    }
    const list = $('#results-frec-list');
    if (P.status !== 'ok') { list.replaceChildren(); return; }
    const fin = P.data.filter((x) => x.decision === 'Final line');
    const SRC = { 'Real price': 'Real prices', 'Rebuilt line': 'Rebuilt lines' };
    const out = [];
    for (let wk = 1; wk <= 9; wk++) {
      const rows = fin.filter((x) => Number(x.week) === wk);
      const w = rows.filter((x) => x.outcome === 'Won').length;
      const head = el('div', 'v2-frec-wk');
      head.append(el('b', null, 'Week ' + wk), el('span', null, rows.length ? `${SRC[rows[0].prices] || rows[0].prices} · ${w}–${rows.length - w}` : (wk === 1 ? 'No games before it' : 'No final line')));
      out.push(head);
      for (const x of rows) {
        const row = el('div', 'pf-pick v2-frec-pick');
        const mid = el('div');
        mid.append(el('b', null, x.line), el('small', null, `${x.game} · ${x.price}¢ · ours ${Math.round(Number(x.mid))}% · ${x.result.replace(/^W\d+: /, '')}`));
        const pc = Number(x.profit_c);
        const chip = el('span', 'wz-chip ' + (x.outcome === 'Won' ? 'pos' : 'neg'), `${x.outcome} ${pc > 0 ? '+' : '−'}${Math.abs(pc)}¢`);
        row.append(wzHelmet(x.team, false), mid, chip);
        row.setAttribute('aria-label', `Week ${wk}: ${x.line} at ${x.price} cents, ${x.outcome.toLowerCase()}, ${pc > 0 ? 'plus' : 'minus'} ${Math.abs(pc)} cents`);
        out.push(row);
      }
    }
    list.replaceChildren(...out);
  }
