  // ---------------- Results: the card, backtested (Weeks 1-9) next to the live card ----------------
  // datasets: card_bt_sum (records, rh/card_bt_sum.csv) and card_bt (every backtested pick, rh/card_bt.csv), from bt/card_bt/
  const CBX = { tier: 'final' };
  const CBP = { wk: '', tier: '', outcome: '', q: '', sortK: 'week', sortDir: 1 };
  const CB_SNUM = new Set(['wins', 'losses', 'win_pct', 'ours', 'needed', 'avg_price', 'roi_pct']);
  const CB_PNUM = new Set(['week', 'price', 'mid', 'needed', 'profit_c']);
  const CB_ORDER = {
    compare: ['final_bt', 'final_real', 'final_rebuilt', 'final_live', 'lean_bt', 'lean_real', 'lean_rebuilt', 'lean_live'],
    sides: ['final_bt_Yes', 'final_bt_No', 'final_mixcut', 'lean_bt_Yes', 'lean_bt_No', 'lean_mixcut', 'p9_final', 'b9_final', 'p9_lean', 'b9_lean', 'c79_final', 'final_real', 'c79_lean', 'lean_real'],
  };
  const CB_LABEL = {
    final_bt: 'Final lines · backtest, Weeks 1–9', final_real: 'Final lines · Weeks 7–9, real prices', final_rebuilt: 'Final lines · Weeks 1–6, rebuilt lines',
    final_live: 'Final lines · live card, settled', lean_bt: 'Conditional leans · backtest, Weeks 1–9', lean_real: 'Conditional leans · Weeks 7–9, real prices',
    lean_rebuilt: 'Conditional leans · Weeks 1–6, rebuilt lines', lean_live: 'Conditional leans · live card, settled',
    final_bt_Yes: 'Final lines · overs (backtest)', final_bt_No: 'Final lines · unders (backtest)', final_mixcut: 'Final-line unders left off for the card mix',
    lean_bt_Yes: 'Conditional leans · overs (backtest)', lean_bt_No: 'Conditional leans · unders (backtest)', lean_mixcut: 'Lean unders left off for the card mix',
    p9_final: 'Week 9 final lines · card as posted (before v6)', b9_final: 'Week 9 final lines · backtest', p9_lean: 'Week 9 leans · card as posted (before v6)', b9_lean: 'Week 9 leans · backtest',
    c79_final: 'Weeks 7–9 final lines · on rebuilt lines (check)', c79_lean: 'Weeks 7–9 leans · on rebuilt lines (check)',
  };
  const CB_SIDE_LABEL = { final_real: 'Weeks 7–9 final lines · on real prices', lean_real: 'Weeks 7–9 leans · on real prices' };
  const cbRec = (r) => (r ? `${r.wins}–${r.losses}` : '—');
  const cbPct = (v) => (v === '' || v == null ? '—' : v + '%');
  function cbSumTable(table, keys, labels) {
    const d = dash.data('card_bt_sum'); const tbody = $('tbody', table);
    if (d.status !== 'ok') { tbody.replaceChildren(); return; }
    const by = new Map(d.data.map((r) => [r.key, r]));
    const frag = document.createDocumentFragment();
    keys.forEach((k, i) => {
      const r = by.get(k); if (!r) return;
      const tr = document.createElement('tr'); tr.dataset.key = k;
      if (i && /^lean_bt$|^lean_bt_Yes$|^p9_final$|^c79_final$/.test(k)) tr.className = 'v2-bt-break';
      const td = mkTd(tr); const n = Number(r.wins) + Number(r.losses);
      td((labels && labels[k]) || CB_LABEL[k] || r.label, /_bt$|_live$/.test(k) ? 'rs-contract' : '');
      td(n ? r.wins : '—', 'num'); td(n ? r.losses : '—', 'num');
      if (n) pctCell(tr, r.win_pct); else td('No plays', 'rs-sub');
      td(cbPct(r.ours), 'num rs-sub'); td(cbPct(r.needed), 'num rs-sub');
      td(r.avg_price === '' ? '—' : r.avg_price, 'num rs-sub');
      td(n ? signed(r.roi_pct) : '—', 'num' + (Number(r.roi_pct) > 0 && n ? ' rs-hi' : ''));
      frag.appendChild(tr);
    });
    tbody.replaceChildren(frag);
  }
  function cbTiles() {
    const d = dash.data('card_bt_sum'); if (d.status !== 'ok') return;
    const by = new Map(d.data.map((r) => [r.key, r]));
    const live = d.data.filter((r) => r.group === 'week' && r.src === 'live').map((r) => Number(r.week));
    const thru = live.length ? Math.max(...live) : 10;
    document.querySelectorAll('#results-tiles [data-bt]').forEach((el) => {
      const r = by.get(el.dataset.bt); if (!r) return;
      const num = $('.rs-tile-num', el), note = $('.rs-tile-note', el);
      num.classList.remove('dash-skeleton'); num.textContent = cbPct(r.win_pct);
      const when = r.src === 'live' ? (thru > 10 ? `Weeks 10–${thru}` : 'Week 10') : 'Weeks 1–9';
      note.textContent = `${cbRec(r)} · ${when} · ${signed(r.roi_pct)} return`;
    });
  }
  function cbWeeks() {
    const table = $('#results-bt-weeks'); const d = dash.data('card_bt_sum'); const tbody = $('tbody', table);
    if (d.status !== 'ok') { tbody.replaceChildren(); return; }
    const rows = d.data.filter((r) => r.group === 'week' && r.tier === CBX.tier).sort((a, b) => Number(a.week) - Number(b.week));
    const SRC = { real: 'Real prices', rebuilt: 'Rebuilt lines', live: 'Live card' };
    const frag = document.createDocumentFragment();
    for (const r of rows) {
      const tr = document.createElement('tr'); tr.dataset.key = r.key; if (r.src === 'live' && Number(r.week) === 10) tr.className = 'v2-bt-break';
      const td = mkTd(tr); const n = Number(r.wins) + Number(r.losses);
      td('Week ' + r.week, r.src === 'live' ? 'rs-contract' : '');
      td(SRC[r.src] || r.src, 'rs-sub');
      td(n ? r.wins : '—', 'num'); td(n ? r.losses : '—', 'num');
      if (n) pctCell(tr, r.win_pct); else td(Number(r.week) === 1 ? 'No games before it' : 'No plays', 'rs-sub');
      td(cbPct(r.ours), 'num rs-sub'); td(cbPct(r.needed), 'num rs-sub');
      td(n ? signed(r.roi_pct) : '—', 'num' + (Number(r.roi_pct) > 0 && n ? ' rs-hi' : ''));
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
  }
  function cbPicks() {
    const table = $('#results-bt-picks'); const d = dash.data('card_bt'); const tbody = $('tbody', table);
    markSort(table, CBP);
    if (d.status !== 'ok') { tbody.replaceChildren(); $('.bt-p-count').textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
    const wsel = $('.bt-p-week');
    if (wsel.options.length < 2) {
      const wks = [...new Set(d.data.map((r) => Number(r.week)))].sort((a, b) => a - b);
      wsel.replaceChildren(new Option('All weeks', ''), ...wks.map((w) => new Option('Week ' + w, String(w))));
    }
    const v = d.data.filter((r) => (!CBP.wk || r.week === CBP.wk) && (!CBP.tier || r.decision === CBP.tier) && (!CBP.outcome || r.outcome === CBP.outcome) &&
      (!CBP.q || (r.game + ' ' + r.line).toLowerCase().includes(CBP.q))).sort(makeSorter(CBP, CB_PNUM));
    const w = v.filter((r) => r.outcome === 'Won').length;
    $('.bt-p-count').textContent = `${fmt(v.length)} picks · ${w}–${v.length - w}`;
    const frag = document.createDocumentFragment();
    for (const r of v) {
      const tr = document.createElement('tr'); tr.dataset.key = r.id;
      const td = mkTd(tr);
      td('Week ' + r.week, 'rs-sub');
      wzGameCell(td(r.game, 'rs-sub'), r.game);
      const lc = td('', 'rs-contract'); lc.append(el('span', 'v2-bt-tag' + (r.decision === 'Final line' ? ' is-final' : ''), r.decision === 'Final line' ? 'Final' : 'Lean'), document.createTextNode(r.line));
      td(r.price, 'num');
      pctCell(tr, r.mid); $('td:last-child', tr).title = `Our range ${r.est}; the market had ${r.mkt}%`;
      td(cbPct(r.needed), 'num rs-sub rs-hide-narrow');
      td(r.outcome, r.outcome === 'Won' ? 'rs-hi' : '');
      td(r.result + (r.prices === 'Rebuilt line' ? ' · rebuilt line' : ''), 'rs-hide-narrow rs-results');
      const pc = Number(r.profit_c);
      td((pc > 0 ? '+' : '') + pc, 'num' + (pc > 0 ? ' rs-hi' : ' rs-sub'));
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
  }
  function v2DrawBt() {
    if (!$('#results-bt')) return;
    cbTiles(); cbSumTable($('#results-bt-compare'), CB_ORDER.compare); cbWeeks(); cbSumTable($('#results-bt-sides'), CB_ORDER.sides, CB_SIDE_LABEL); cbPicks();
  }
  if ($('#results-bt')) {
    $('.bt-w-tier').addEventListener('change', (e) => { CBX.tier = e.target.value; cbWeeks(); });
    $('.bt-p-week').addEventListener('change', (e) => { CBP.wk = e.target.value; cbPicks(); });
    $('.bt-p-tier').addEventListener('change', (e) => { CBP.tier = e.target.value; cbPicks(); });
    $('.bt-p-outcome').addEventListener('change', (e) => { CBP.outcome = e.target.value; cbPicks(); });
    $('.bt-p-search').addEventListener('input', (e) => { CBP.q = e.target.value.trim().toLowerCase(); cbPicks(); });
    wireSort($('#results-bt-picks'), CBP, CB_PNUM, () => cbPicks());
  }
