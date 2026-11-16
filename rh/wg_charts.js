
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
  const emptyNote = (box, msg) => { const old = box.querySelector(':scope > svg'); if (old) old.remove(); box.style.minHeight = '60px'; let p = box.querySelector(':scope > .wg-empty'); if (!p) { p = document.createElement('p'); p.className = 'rs-note wg-empty'; box.appendChild(p); } p.textContent = msg; };
  const clearEmpty = (box) => { const p = box.querySelector(':scope > .wg-empty'); if (p) p.remove(); };

  // horizontal hit-rate bars with a 50% line and an average-price tick
  function hbars(box, rows, o) {
    clearEmpty(box);
    const W = box.clientWidth; if (!W) return;
    if (!rows.length) { emptyNote(box, o.empty || 'No groups meet the minimum size.'); return; }
    const rowH = o.rowH || 26, top = 20, bottom = 6, fs = 'var(--cds-font-size-caption)';
    let svg = freshSvg(box, W, 10);
    const bars = rows.filter((r) => !r.heading);
    const lw = Math.min(W * 0.46, measure(svg, bars.map((r) => r.label), fs) + 12);
    const rightW = Math.min(110, Math.max(70, measure(svg, bars.map((r) => r.right), fs) + 12));
    const H = top + rows.length * rowH + bottom;
    svg = freshSvg(box, W, H);
    box.style.minHeight = H + 'px';
    const x = d3.scaleLinear([0, 100], [lw, W - rightW]);
    const grid = svg.append('g');
    for (const t of [0, 25, 50, 75, 100]) {
      grid.append('line').attr('x1', x(t)).attr('x2', x(t)).attr('y1', top - 4).attr('y2', H - bottom)
        .style('stroke', t === 50 ? 'var(--cds-chart-reference)' : 'var(--cds-chart-grid)').attr('stroke-width', 1)
        .attr('stroke-dasharray', t === 50 ? '4 3' : null);
      grid.append('text').attr('x', x(t)).attr('y', top - 8).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(t + '%');
    }
    rows.forEach((r, i) => {
      const y = top + i * rowH, bh = Math.min(16, rowH - 10), cy = y + rowH / 2;
      if (r.heading) {
        svg.append('text').attr('x', 0).attr('y', y + rowH - 7).style('font-size', '10px').style('letter-spacing', '.08em').style('font-weight', 600).style('fill', 'var(--color-fg-muted)').text(r.heading.toUpperCase());
        return;
      }
      const g = svg.append('g');
      g.append('text').attr('x', lw - 10).attr('y', cy).attr('dy', '0.35em').attr('text-anchor', 'end').style('font-size', fs).style('fill', 'var(--color-fg)').text(r.label);
      g.append('rect').attr('x', x(0)).attr('y', cy - bh / 2).attr('width', Math.max(1, x(r.value) - x(0))).attr('height', bh).attr('rx', 3)
        .style('fill', r.good ? 'var(--wg-green)' : 'var(--cds-chart-muted)');
      if (r.price != null) g.append('line').attr('x1', x(r.price)).attr('x2', x(r.price)).attr('y1', cy - bh / 2 - 3).attr('y2', cy + bh / 2 + 3).style('stroke', 'var(--color-fg)').attr('stroke-width', 2).attr('stroke-linecap', 'round');
      g.append('text').attr('x', W - rightW + 8).attr('y', cy).attr('dy', '0.35em').style('font-size', fs).style('fill', 'var(--color-fg-muted)').style('font-variant-numeric', 'tabular-nums').text(r.right);
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
      const maxw = cw - 6; let s = lab;
      while (t.node().getComputedTextLength() > maxw && s.length > 4) { s = s.slice(0, -2); t.text(s + '…'); }
    });
    rv.forEach((rvv, i) => {
      svg.append('text').attr('x', lw - 10).attr('y', top + i * cellH + cellH / 2).attr('dy', '0.35em').attr('text-anchor', 'end').style('font-size', fs).style('fill', 'var(--color-fg)').text(showVal(d1, rvv));
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
    const color = (g) => dash.colors[BOARD_GROUPS.indexOf(g) % dash.colors.length];
    const key = $('.ch-board-key');
    key.replaceChildren(...BOARD_GROUPS.map((g) => { const s = document.createElement('span'); const i = document.createElement('i'); i.style.background = color(g); s.append(i, g); return s; }),
      (() => { const s = document.createElement('span'); const i = document.createElement('i'); i.className = 'line'; s.append(i, 'Break-even (hit rate = price)'); return s; })());
    const pts = d.data.filter((r) => r.hit_rate !== '' && r.hit_rate != null);
    const H = Math.min(420, Math.max(300, W * 0.5)), m = { t: 12, r: 16, b: 38, l: 44 };
    const svg = freshSvg(box, W, H); box.style.minHeight = H + 'px';
    const x = d3.scaleLinear([44.5, 55.5], [m.l, W - m.r]), y = d3.scaleLinear([0, 100], [H - m.b, m.t]);
    for (const t of [0, 25, 50, 75, 100]) {
      svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(t)).attr('y2', y(t)).style('stroke', 'var(--cds-chart-grid)');
      svg.append('text').attr('x', m.l - 8).attr('y', y(t)).attr('dy', '0.35em').attr('text-anchor', 'end').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(t + '%');
    }
    for (let t = 45; t <= 55; t += (W < 500 ? 2 : 1)) svg.append('text').attr('x', x(t)).attr('y', H - m.b + 16).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(t + '¢');
    svg.append('text').attr('x', (m.l + W - m.r) / 2).attr('y', H - 4).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text('Yes price');
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

  function drawCharts() {
    const page = $('#charts');
    if (!page || page.hidden) return;
    const p = dash.data('hist_perms');
    if (p.status === 'ok') { drawFactorCharts(p.data); drawComboChart(p.data); drawHeatmap(p.data); }
    else document.querySelectorAll('#ch-factor-grid .wg-chart, #ch-combo-chart, #ch-heat-chart').forEach((b) => { const s = b.querySelector(':scope > svg'); if (s) s.remove(); });
    drawW6Chart();
    drawBoard();
  }

  let chartResize = 0;
  window.addEventListener('resize', () => { cancelAnimationFrame(chartResize); chartResize = requestAnimationFrame(drawCharts); });
