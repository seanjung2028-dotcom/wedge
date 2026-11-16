"""Week 8 JS: momentum filter + column, projections table, v3 / projection outlook text, recent-form section, week-by-week and momentum charts."""
B = '/home/claude/wedger/rh/'
s = open(B + 'page_template.html').read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, (old[:100], c); s = s.replace(old, new)

# ---------- momentum helpers (after sitCell) ----------
rep("  const sitDlg = $('#sit-dlg');", r"""  // ---------------- momentum (last 4 games vs season) ----------------
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
  const momCell = (tr, r) => {
    const c = document.createElement('td'); c.className = 'rs-hide-narrow';
    if (!r.mom_type) { c.textContent = '—'; c.classList.add('rs-sub'); tr.appendChild(c); return c; }
    const ch = el('span', 'wg-mom-chip ' + (MOM_CLS[r.mom_type] || ''), MOM_SHORT[r.mom_type] || r.mom_type);
    ch.title = `${r.mom_type}: last 4 ${r.mom_l4} vs season ${r.mom_s}${r.mom_snap ? ` · snaps ${r.mom_snap}` : ''}${r.mom_vol ? ` · ${r.mom_vol}` : ''}${num(r.mom_p) != null ? ` · last-4 view ${pctR(num(r.mom_p))}` : ''}`;
    c.appendChild(ch); tr.appendChild(c); return c;
  };

  const sitDlg = $('#sit-dlg');""")

# ---------- lines table ----------
rep("const ls = { show: 'q', game: '', group: '', src: '', clean: false,", "const ls = { show: 'q', game: '', group: '', src: '', mom: '', clean: false,")
rep("  $('.rs-src').addEventListener('change', (e) => { ls.src = e.target.value; drawLines(); });",
    "  $('.rs-src').addEventListener('change', (e) => { ls.src = e.target.value; drawLines(); });\n  $('.rs-mom').addEventListener('change', (e) => { ls.mom = e.target.value; drawLines(); });")
rep("      (!ls.src || (r.source || 'Robinhood') === ls.src) &&", "      (!ls.src || (r.source || 'Robinhood') === ls.src) &&\n      momOk(r, ls.mom, num(r.yes_price)) &&")
rep("""      sitCell(tr, r, { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source });
      td(r.hits === '' ? '—' : r.hits, 'num');
      td(r.games, 'num');
      td(r.sample, 'rs-hide-narrow rs-sub');""", """      sitCell(tr, r, { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source });
      momCell(tr, r);
      td(r.hits === '' ? '—' : r.hits, 'num');
      td(r.games, 'num');
      td(r.sample, 'rs-hide-narrow rs-sub');""")

# ---------- category tables ----------
rep("const st = { cat: page.dataset.cat, show: 'q', game: '', clean: false,", "const st = { cat: page.dataset.cat, show: 'q', game: '', mom: '', clean: false,")
rep("const els = { show: $('.rc-show', page), game: $('.rc-game', page),", "const els = { show: $('.rc-show', page), game: $('.rc-game', page), mom: $('.rc-mom', page),")
rep("        (!st.game || r.game === st.game) &&\n        (!st.clean || !r.flags) &&", "        (!st.game || r.game === st.game) &&\n        momOk(r, st.mom, num(r.yes_price)) &&\n        (!st.clean || !r.flags) &&")
rep("""        sitCell(tr, r, { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source });
        td(r.hits === '' ? '—' : r.hits, 'num');""", """        sitCell(tr, r, { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source });
        momCell(tr, r);
        td(r.hits === '' ? '—' : r.hits, 'num');""")
rep("    els.game.addEventListener('change', () => { st.game = els.game.value; draw(); });", "    els.game.addEventListener('change', () => { st.game = els.game.value; draw(); });\n    els.mom.addEventListener('change', () => { st.mom = els.mom.value; draw(); });")

# ---------- projections table ----------
rep("  // ---------------- defense table ----------------", r"""  // ---------------- Week 8 projections ----------------
  const pjs = { game: '', mkt: '', pos: '', mom: '', q: '', sortK: 'kickoff_utc', sortDir: 1 };
  const PJNUM = new Set(['est_line', 'proj', 'p_over', 'p_wedger', 'mom_p', 'season_avg', 'games']);
  const projTable = $('#proj-table');
  const pjEl = (c) => $('#proj-card .' + c);
  pjEl('pj-game').addEventListener('change', (e) => { pjs.game = e.target.value; drawProj(); });
  pjEl('pj-mkt').addEventListener('change', (e) => { pjs.mkt = e.target.value; drawProj(); });
  pjEl('pj-pos').addEventListener('change', (e) => { pjs.pos = e.target.value; drawProj(); });
  pjEl('pj-mom').addEventListener('change', (e) => { pjs.mom = e.target.value; drawProj(); });
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
      (!pjs.q || (r.game + ' ' + r.team + ' ' + r.player + ' ' + r.market).toLowerCase().includes(pjs.q)));
    v = v.slice().sort(makeSorter(pjs, PJNUM));
    pjEl('pj-count').textContent = fmt(v.length) + ' of ' + fmt(rows.length) + ' props';
    const frag = document.createDocumentFragment();
    for (const r of v) {
      const tr = document.createElement('tr'); tr.dataset.key = r.id; if (started(r)) tr.className = 'rs-started';
      const td = mkTd(tr);
      td(r.game, 'rs-sub');
      td(r.kickoff, 'rs-hide-narrow rs-sub');
      const lc = td(projLabel(r), 'rs-contract'); lc.title = r.market === 'Anytime Touchdown' ? 'Anytime TD (1+ rushing or receiving TD)' : `Expected line ${r.est_line} (season, last 4 and multi-season average, weighted the way books set Week 6–7 lines)`;
      td(r.pos, 'rs-sub rs-hide-narrow');
      td(r.team);
      const isTd = r.market === 'Anytime Touchdown';
      const pc = td(r.proj, 'num'); if (r.proj_lo !== '' && r.proj_hi !== '') pc.title = `Bear ${r.proj_lo} · bull ${r.proj_hi}`;
      sitCell(tr, { ...r, sit_hit: r.p_wedger, yes_price: '', yes_bid: '' }, { title: projLabel(r), game: r.game, market: r.market, key: `${r.game}|${r.market}|${r.contract}` });
      td(r.p_over === '' ? '—' : pctR(num(r.p_over)), 'num');
      td(r.mom_p === '' ? '—' : pctR(num(r.mom_p)), 'num rs-hide-narrow rs-sub');
      momCell(tr, r);
      td(isTd ? (num(r.season_avg) == null ? '—' : num(r.season_avg).toFixed(2)) : r.season_avg, 'num rs-hide-narrow rs-sub');
      td(r.games, 'num rs-hide-narrow rs-sub');
      td(r.flags, 'rs-flag');
      frag.appendChild(tr);
    }
    tbody.replaceChildren(frag);
  }

  // ---------------- defense table ----------------""")

# ---------- outlook: v3 / projection text, recent form ----------
rep("    const P = Math.round(1000 * O.P) / 10, edge = price == null ? null : P - price;",
    "    const isProj = O.cal === 'proj';\n    const P = Math.round(1000 * (isProj && O.P_exp != null ? O.P_exp : O.P)) / 10, edge = price == null ? null : P - price;")
rep("    c1.append(el('div', 'wg-lab', 'Wedger chance it settles Yes'));",
    "    c1.append(el('div', 'wg-lab', isProj ? (isTd ? 'Our chance he scores · no price yet' : 'Wedger chance if it posts at 50¢') : 'Wedger chance it settles Yes'));")
i = s.index("    c1.append(r1, gauge, mix, el('p', 'wg-note', ctx.sport === 'nba' ?"); j = s.index('\n', i)
old_note = s[i:j]
nfl_old = old_note[old_note.index(": `Wedger = 70% market + 30% our read${O.P_v1") + 2: old_note.rindex('));')]
s = s[:i] + r"""    const pickTxt = r.sit_pick ? `Best side: ${r.sit_pick} (+${Math.round(num(r.sit_pedge))} pts vs its price). ` : '';
    const nflNote = isProj
      ? `No price yet. Our read alone: ${pctR(100 * O.P)}${O.P_l4 != null ? `; last-4 read ${pctR(100 * O.P_l4)}` : ''}. ${isTd ? 'Shown with the TD calibration (Week 6–7 anytime TDs came true a little less often than their price).' : `If the line posts at ${line} for 50¢, Wedger would be about ${pctR(P)}: 85% the price + 15% our read, then the Week 6–7 calibration (passing overs have come true more often than their price, rushing overs less).`} Yes = ${cond}.`
      : O.cal === 'v3'
        ? `Wedger = 85% market + 15% our read${O.P_v1 != null ? ` (${pctR(100 * O.P_v1)} before calibration)` : ''}, re-fit Tue Oct 27 on 706 settled Week 6–7 lines: a Yes priced near 50¢ came true about 45% of the time for receiving and anytime TDs, 40% for rushing and 56% for passing.${O.P_l4 != null ? ` Last-4 view: ${pctR(100 * O.P_l4)}.` : ''} ${pickTxt}Yes = ${cond}.`
        : """ + nfl_old + r""";
    c1.append(r1, gauge, mix, el('p', 'wg-note', ctx.sport === 'nba' ? `Wedger = 70% market + 30% our read (cases and projection, calibrated on past results). Yes = ${cond}.` : nflNote));""" + s[j:]
rep("    ov.append(sec('What moves the projection', 'Dashed mark = the line', wf));", r"""    ov.append(sec('What moves the projection', 'Dashed mark = the line', wf));

    // recent form (last 4 games vs season)
    const MO = O.mom;
    if (MO && MO.mom_type && ctx.sport !== 'nba') {
      const mc = el('div', 'wg-chips');
      const mchip = (b, s2, cls) => { const c = el('div', 'wg-card'); const bb = el('b', null, b); if (cls != null) { bb.className = 'wg-mom-chip ' + cls; } c.append(bb, el('small', null, s2)); mc.append(c); };
      mchip(MO.mom_type, MOM_WHY[MO.mom_type] || '', MOM_CLS[MO.mom_type] || '');
      mchip(`${fmtStat(stat, MO.mom_l4)} vs ${fmtStat(stat, MO.mom_s)} ${unit}`, 'Last 4 games vs his 2026 season');
      if (MO.mom_snap) mchip(MO.mom_snap, 'Snap share: season → last 4');
      if (MO.mom_vol) mchip(MO.mom_vol, 'Volume: season → last 4');
      if (O.P_l4 != null) mchip(pctR(100 * O.P_l4), `Last-4 view${O.m_l4 != null ? ` · projects ${fmtStat(stat, O.m_l4)} ${unit}` : ''}. It tested worse than the standard read on real Week 6–7 prices, so it isn’t in Wedger %.`);
      ov.append(sec('Recent form', 'Last 4 games vs the season', mc));
    }""")
rep("the Wedger chance is 70% market + 30% our read, recalibrated on settled Week 6–7 lines (Yes premium by market). Backtest, 3,436 player lines from 2025: Brier 0.238 vs 0.250 for a coin flip. On 334 real Week 6 prices: Wedger 0.2483 vs 0.2486 for the price alone, so the market is hard to beat.",
    "the Wedger chance is 85% market + 15% our read, re-fit Tue Oct 27 on 706 settled Week 6–7 lines (Yes premium by market); a recent-role factor moves the projection when his snap share over the last 4 games moved 10+ points. Backtest, 3,436 player lines from 2025: Brier 0.238 vs 0.250 for a coin flip. On 706 real Week 6–7 prices (fit on one week, tested on the other): Wedger 0.2474 vs 0.2512 for the price alone, so the market is hard to beat.")

# ---------- charts ----------
CH = r"""
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
    const segs = [...new Set(rows.map((r) => r.segment))];
    const col = (sg) => dash.colors[segs.indexOf(sg) % dash.colors.length];
    keyRow($('.chw-key'), [...segs.map((sg) => [sg, col(sg), 0]), ['50%', null, 'line']]);
    if (!rows.length) { emptyNote(box, 'No weeks for this group.'); return; }
    const H = Math.min(380, Math.max(260, W * 0.46)), m = { t: 12, r: 14, b: 34, l: 40 };
    const svg = freshSvg(box, W, H); box.style.minHeight = H + 'px';
    const weeks = ['1', '2', '3', '4', '5', '6', '7'];
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
      tip: [`${r.segment} · Weeks 1–7`, `Won ${pct1(r.win_pct)} (${r.wins}–${r.losses})`, `Avg price ${r.avg_price}¢`, `Return ${signed(r.roi_pct)}`],
    })), { rowH: 26 });
  }

  const chp = { fac: 'Stat' };
  $('.chp-fac').addEventListener('change', (e) => { chp.fac = e.target.value; drawCharts(); });
  const PERIODS = ['Wk 1', 'Wk 2', 'Wk 3', 'Wk 4', 'Wk 5', 'Wk 6', 'Wk 7', '2023–25'];
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

  function drawCharts() {"""
rep("\n  function drawCharts() {", CH)
rep("    drawW6Chart();\n    drawBoard();\n  }", "    drawW6Chart();\n    drawBoard();\n    drawWeeks();\n    drawPropsHeat();\n    drawMom();\n    drawTeams();\n  }")
rep("    catPages.forEach((draw) => draw());\n    drawDefense();", "    catPages.forEach((draw) => draw());\n    drawProj();\n    drawDefense();")
open(B + 'page_template.html', 'w').write(s)
print('js ok', len(s))

# NBA backtest data: the dashboard strips <script type="application/json">, so wg.js carries it as window.WG_NBT
s = open(B + 'page_template.html').read()
old = "nbtData = JSON.parse($('#nbt-data').textContent);"
assert s.count(old) == 1
s = s.replace(old, "nbtData = window.WG_NBT || JSON.parse($('#nbt-data').textContent);")
open(B + 'page_template.html', 'w').write(s)
print('nbt ok')
