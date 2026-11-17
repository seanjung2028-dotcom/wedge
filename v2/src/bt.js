  // ---------------- Results: the final-line record (backtest + added picks + the card's certified finals) ----------------
  // datasets: card_bt_sum (key final_record) and final_record (every line in it), from bt/card_bt/summary.py
  function v2DrawFrec() {
    const box = $('#results-frec'); if (!box) return;
    const S = dash.data('card_bt_sum'), P = dash.data('final_record');
    let thru = 10;
    if (S.status === 'ok') {
      const r = S.data.find((x) => x.key === 'final_record');
      if (r) {
        thru = Number(r.thru) || thru;
        const pct = $('#frec-pct'); pct.classList.remove('dash-skeleton');
        pct.replaceChildren(document.createTextNode(String(Number(r.win_pct))), el('small', null, '%'));
        $('#frec-wl').textContent = `${r.wins}–${r.losses}`;
        $('#frec-net').textContent = signed(r.roi_pct);
        $('#frec-label').textContent = `Final lines · Weeks 1–${thru}`;
      }
    }
    const list = $('#results-frec-list');
    if (P.status !== 'ok') { list.replaceChildren(); return; }
    $('#frec-note').textContent = 'Includes backtested lines and picks added by hand. Net: one contract each at the price, before fees.';
    const out = [];
    for (let wk = 1; wk <= thru; wk++) {
      const rows = P.data.filter((x) => Number(x.week) === wk);
      const w = rows.filter((x) => x.outcome === 'Won').length;
      const head = el('div', 'v2-frec-wk');
      head.append(el('b', null, 'Week ' + wk), el('span', null, rows.length ? `${w}–${rows.length - w}` : (wk === 1 ? 'No games before it' : 'No final line')));
      out.push(head);
      for (const x of rows) {
        const row = el('div', 'pf-pick v2-frec-pick');
        const mid = el('div'); const sm = el('small');
        sm.append(document.createTextNode(`${x.game} · ${x.price}¢${x.mid !== '' && x.mid != null ? ' · ours ' + Math.round(Number(x.mid)) + '%' : ''} · ${x.result.replace(/^W\d+: /, '')}`));
        mid.append(el('b', null, x.line), sm);
        const pc = Number(x.profit_c);
        const chip = el('span', 'wz-chip ' + (x.outcome === 'Won' ? 'pos' : 'neg'), `${x.outcome} ${pc > 0 ? '+' : '−'}${Math.abs(pc)}¢`);
        row.append(wzHelmet(x.team, false), mid, chip);
        row.setAttribute('aria-label', `Week ${wk}: ${x.line} at ${x.price} cents, ${x.outcome.toLowerCase()}, ${pc > 0 ? 'plus' : 'minus'} ${Math.abs(pc)} cents`);
        out.push(row);
      }
    }
    list.replaceChildren(...out);
  }
