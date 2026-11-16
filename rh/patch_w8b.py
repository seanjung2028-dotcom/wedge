"""Week 8 evening update (Tue Oct 27 ~4:23 PM CT): re-priced board, model v4, player roles, 'against this defense' history,
role/script/scheme categories and the research charts. Runs after patch_w8_page.py and patch_w8_js.py."""
B = '/home/claude/wedger/rh/'
s = open(B + 'page_template.html').read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, (old[:100], c); s = s.replace(old, new)

# ---------------- header + lines note ----------------
rep('Week 8 prices as of Tue Oct 27, 10:11 AM CT', 'Week 8 prices as of Tue Oct 27, 4:23 PM CT')
i = s.index('<p class="rs-note">Week 8, priced Tue Oct 27 ~10:11 AM CT.'); j = s.index('</p>', i) + 4
s = s[:i] + ('<p class="rs-note">Week 8, re-priced Tue Oct 27 ~4:23 PM CT. Robinhood lists every game\'s moneyline, spread and total ladders, plus player props '
             'for Thursday\'s CAR @ GB and Sunday\'s MIN @ DET (Kalshi\'s ladders) and anytime TDs for most games; Robinhood\'s price is shown and the sportsbooks\' '
             'consensus is the books\' price inside Wedger % (spreads, totals and moneylines from Caesars, DraftKings, FanDuel, BetRivers and BetMGM, turned into a '
             'fair chance for every rung). Sunday\'s other player props are now posted by the books: Robinhood-style rungs priced from those five books, or from the '
             'books\' consensus line where none of the five has posted yet. Injuries: Tuesday\'s practice reports (Matthew Golden did not practice Monday or Tuesday, '
             'so his teammates are projected without him; Jalen Coker practiced fully Tuesday; Bryce Young full), ESPN statuses and Monday news (Jalen Hurts and '
             'Terry McLaurin out for the season). Hit rate = share of his 2026 games (Weeks 1–7) where the line came true. Wedger % = 85% the books\' price, 15% our '
             'read, then the Week 6–7 calibration and a small role-and-matchup adjustment (model v4, see Charts). Role = how he is used: deep threat, slot / underneath, '
             'workhorse, pass-catching back and so on. Momentum = his last 4 games vs his season. Click any player prop for the outlook, including how players like him '
             'have done in spots like this and what other players did against this defense. ★ = projected game total above 49.5.</p>') + s[j:]
ROLESEL = ('<select class="{cls}" aria-label="Role">\n          <option value="">Any role</option>\n'
           '          <option value="Workhorse · three-down">RB · workhorse, three-down</option>\n          <option value="Workhorse · early-down">RB · workhorse, early-down</option>\n'
           '          <option value="Pass-catching back">RB · pass-catching back</option>\n          <option value="Early-down / goal-line">RB · early-down / goal-line</option>\n'
           '          <option value="Committee / change-of-pace">RB · committee / change-of-pace</option>\n          <option value="Deep threat">WR · deep threat</option>\n'
           '          <option value="Intermediate">WR · intermediate</option>\n          <option value="Slot / underneath">WR · slot / underneath</option>\n'
           '          <option value="Receiving TE">TE · receiving TE</option>\n          <option value="Secondary TE">TE · secondary TE</option>\n'
           '          <option value="Dual-threat">QB · dual-threat</option>\n          <option value="pocket">QB · pocket passers</option>\n        </select>')
rep('''        <label><input type="checkbox" class="rs-clean"> Hide flagged</label>''', ROLESEL.format(cls='rs-role') + '''
        <label><input type="checkbox" class="rs-clean"> Hide flagged</label>''')
ROLETH = '<th data-field="role" class="rs-hide-narrow"><button data-k="role" title="How he is used this season (falls back to last season before Week 4): WR deep threat (aDOT 13+ or 28%+ deep targets), slot / underneath (aDOT under 8.5 with middle or screen targets) or intermediate; RB workhorse (55%+ of team carries), pass-catching (10%+ target share), early-down / goal-line or committee; TE receiving (15%+ target share) or secondary; QB dual-threat or pocket.">Role</button></th>'
rep('''            <th data-field="mom_type" class="rs-hide-narrow"><button data-k="mom_type" title="His last 4 games vs his 2026 season. Role = snap share moved 10+ pts; Volume = targets / carries moved 15%+; Efficiency = yards per target / carry moved 15%+ with volume flat. Hover a chip for the numbers and the last-4 view (the model with his last 4 games weighted most).">Momentum</button></th>''',
    ROLETH + '''
            <th data-field="mom_type" class="rs-hide-narrow"><button data-k="mom_type" title="His last 4 games vs his 2026 season. Role = snap share moved 10+ pts; Volume = targets / carries moved 15%+; Efficiency = yards per target / carry moved 15%+ with volume flat. Hover a chip for the numbers and the last-4 view (the model with his last 4 games weighted most).">Momentum</button></th>''', count=2)
# projections: role filter + note
rep('''        <input type="search" class="pj-search"''', ROLESEL.format(cls='pj-role') + '''
        <input type="search" class="pj-search"''')
rep("Books hadn't posted most Sunday player props on Tuesday morning, so this is every starter's main props with the line we expect:",
    "Every starter's main props with the line we expect (most Sunday props are now on the Week 8 lines tab too, at real prices):")
# ---------------- charts: categories + research ----------------
CH = '''
    <section class="rs-card" id="ch-cats">
      <h2>Role, game script and scheme · which spots clear the line</h2>
      <p class="rs-note">Every starter's receiving yards, receptions, rushing yards and passing yards against the line books would set (season average, last 4 and multi-season average, weighted the way books set the real Week 6–7 lines), split by the player's role, the spread, the team total, home or away and the opposing defense's scheme (coverage, blitz rate, box count, deep and middle-of-field throws allowed, all from its games so far). A spot is listed above 50% only if it cleared the line more than half the time over all of 2026 and over Weeks 4–7; "held" means it also beat that stat's average in 2023–25, which separates real patterns from a lucky seven weeks. Overs at these lines hit about 45% overall.</p>
      <div class="rs-controls">
        <select class="ct-kind" aria-label="Which spots"><option value="over">Above 50% (2026 and Weeks 4–7)</option><option value="held">Above 50% and held in 2023–25</option><option value="under">Unders: below 40% (overs miss 60%+)</option><option value="all">Every spot (20+ props)</option></select>
        <select class="ct-pos" aria-label="Position"><option value="">All positions</option><option>RB</option><option>WR</option><option>TE</option><option>QB</option></select>
        <select class="ct-stat" aria-label="Stat"><option value="">All stats</option><option value="rushyd">Rushing yards</option><option value="recyd">Receiving yards</option><option value="rec">Receptions</option><option value="passyd">Passing yards</option></select>
        <input type="search" class="ct-search" placeholder="Search: favorite, blitz, deep threat…" aria-label="Search spots">
        <span class="rs-count ct-count"></span>
      </div>
      <div class="rs-tablebox">
        <table class="rs-table" id="cats-table" data-source="cats" data-row-key="label">
          <thead><tr>
            <th data-field="label"><button data-k="label">Spot</button></th>
            <th data-field="over_season" class="rs-barcell"><button data-k="over_season">2026 over %</button></th>
            <th data-field="n_season" class="num rs-hide-narrow"><button data-k="n_season">Props</button></th>
            <th data-field="over_w47" class="num"><button data-k="over_w47">Weeks 4–7</button></th>
            <th data-field="over_hist" class="num"><button data-k="over_hist">2023–25</button></th>
            <th data-field="base_hist" class="num rs-hide-narrow"><button data-k="base_hist" title="That position and stat, all spots, 2023–25">Stat avg</button></th>
            <th data-field="held"><button data-k="held">Held?</button></th>
          </tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </section>

    <section class="rs-card" id="ch-research">
      <h2>Research · what other prop models weigh, tested on 2023–26</h2>
      <p class="rs-note">Public projection systems build a prop as volume times efficiency: volume (targets, carries, attempts) from the most recent games because roles are sticky, efficiency (yards per target or carry) from a long window pulled hard toward the league average because it is mostly noise (yards per carry needs about 2,000 carries before it is half skill). We tested both on every 2023–26 player-game.</p>
      <div class="wg-grid2">
        <div class="wg-mini"><h3>Which window predicts the next game?</h3>
          <div class="rs-controls"><select class="rc2-comp" aria-label="Component"><option>WR rec</option><option>RB rush</option><option>QB pass</option><option>TE rec</option><option>RB rec</option></select></div>
          <div class="wg-key rc2-key"></div>
          <div class="wg-chart" id="ch-recency" data-source="research"></div>
          <p class="rs-note" id="ch-recency-note" data-source="research"></p>
        </div>
        <div class="wg-mini"><h3>Other players vs this defense: what carries over</h3>
          <div class="rs-controls"><select class="ds2-grp" aria-label="Position"><option>RB rushing yards</option><option>WR receiving yards</option><option>TE receiving yards</option><option>RB receiving yards</option><option>WR receptions</option><option>QB passing yards</option></select></div>
          <div class="wg-chart" id="ch-defsig" data-source="research"></div>
          <p class="rs-note" id="ch-defsig-note" data-source="research"></p>
        </div>
      </div>
      <p class="rs-note" id="ch-research-var" data-source="research"></p>
    </section>
'''
rep('''    <section class="rs-card" id="ch-weeks">''', CH + '''
    <section class="rs-card" id="ch-weeks">''')
# ---------------- methodology ----------------
i = s.index('<p><b>Model v3 and the momentum study (Tue Oct 27).</b>'); j = s.index('</p>', i) + 4
s = s[:j] + ('\n    <p><b>Model v4, roles and the defense study (Tue Oct 27, evening).</b> Projections now blend the usage cases 50/50 with recent volume × '
             'long-run efficiency: volume is an exponentially weighted average with a half-life of about 4 games for WR targets, RB carries and QB attempts '
             '(longer for TE and RB targets), prior seasons discounted to 30–50%; efficiency uses a 12-game-plus window shrunk toward the position average by '
             '100–200 targets, carries or attempts. The defense factor now measures what a defense allowed against each opponent\'s own average instead of raw '
             'yards allowed: across 2023–26 the raw number barely predicted the next player (WR receiving: correlation 0.00), the adjusted one a little better. '
             'For rushing, only the extra carries a defense allows and the yards before contact its front gives up carry over; what the runner did after contact '
             '(one big Gibbs-style day) does not (slope 0.04 vs 0.19). A role-and-matchup adjustment, fit only on 2023–25, nudges Wedger % by how players in the same '
             'role, game script and scheme fared vs the line (real Week 6–7 prices: Brier 0.2467 vs 0.2472 without it). On real prices our own read still adds '
             'little to the books\' price, so these are small changes; the biggest gains come from roles and spots (Charts).</p>') + s[j:]
# ---------------- CSS ----------------
rep('  .wg-h3 {', '''  .wg-role-chip { display: inline-block; font-size: 11px; line-height: 1.5; padding: 0 7px; border-radius: 9px; white-space: nowrap; border: 1px solid var(--color-border-line); color: var(--color-fg); background: var(--color-bg); }
  .wg-role-chip.same { border-color: var(--wg-green); background: color-mix(in srgb, var(--wg-green) 14%, var(--color-bg)); }
  .wg-dh { width: 100%; border-collapse: collapse; font-size: 12px; }
  .wg-dh th { text-align: left; font-weight: 600; color: var(--color-fg-muted); padding: 4px 6px; border-bottom: 1px solid var(--color-border-line); white-space: nowrap; }
  .wg-dh td { padding: 5px 6px; border-bottom: 1px solid var(--color-border-line); vertical-align: top; }
  .wg-dh td.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
  .wg-dh .up { color: var(--wg-green); font-weight: 600; } .wg-dh .down { color: var(--cds-chart-status-critical); font-weight: 600; }
  .wg-dh tr.same td:first-child { box-shadow: inset 3px 0 0 var(--wg-green); }
  .wg-dh .why { color: var(--color-fg-muted); }
  .wg-dh.wide { min-width: 640px; }
  .wg-dhbox { max-height: 360px; overflow: auto; border: 1px solid var(--color-border-line); border-radius: var(--cds-radius); }
  .wg-roleg { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 8px; margin: 8px 0; }
  .wg-roleg div { border: 1px solid var(--color-border-line); border-radius: 8px; padding: 6px 8px; }
  .wg-roleg b { display: block; font-size: 15px; } .wg-roleg small { color: var(--color-fg-muted); font-size: 11px; }
  .wg-h3 {''')

# ======================= JS =======================
# role helpers next to momentum helpers
rep("  const momCell = (tr, r) => {", r"""  const roleOk = (r, f) => !f || (f === 'pocket' ? /pocket/i.test(r.role || '') : String(r.role || '').startsWith(f));
  const roleCell = (tr, r) => {
    const c = document.createElement('td'); c.className = 'rs-hide-narrow';
    if (!r.role) { c.textContent = '—'; c.classList.add('rs-sub'); tr.appendChild(c); return c; }
    c.appendChild(el('span', 'wg-role-chip', r.role)); tr.appendChild(c); return c;
  };
  const momCell = (tr, r) => {""")
# lines table
rep("const ls = { show: 'q', game: '', group: '', src: '', mom: '',", "const ls = { show: 'q', game: '', group: '', src: '', mom: '', role: '',")
rep("  $('.rs-mom').addEventListener('change', (e) => { ls.mom = e.target.value; drawLines(); });",
    "  $('.rs-mom').addEventListener('change', (e) => { ls.mom = e.target.value; drawLines(); });\n  $('.rs-role').addEventListener('change', (e) => { ls.role = e.target.value; drawLines(); });")
rep("      momOk(r, ls.mom, num(r.yes_price)) &&\n", "      momOk(r, ls.mom, num(r.yes_price)) &&\n      roleOk(r, ls.role) &&\n")
rep("""      sitCell(tr, r, { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source });
      momCell(tr, r);
      td(r.hits === '' ? '—' : r.hits, 'num');
      td(r.games, 'num');
      td(r.sample, 'rs-hide-narrow rs-sub');""", """      sitCell(tr, r, { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source });
      roleCell(tr, r);
      momCell(tr, r);
      td(r.hits === '' ? '—' : r.hits, 'num');
      td(r.games, 'num');
      td(r.sample, 'rs-hide-narrow rs-sub');""")
# category tables
rep("const st = { cat: page.dataset.cat, show: 'q', game: '', mom: '',", "const st = { cat: page.dataset.cat, show: 'q', game: '', mom: '', role: '',")
rep("const els = { show: $('.rc-show', page), game: $('.rc-game', page), mom: $('.rc-mom', page),", "const els = { show: $('.rc-show', page), game: $('.rc-game', page), mom: $('.rc-mom', page), role: $('.rc-role', page),")
rep("        momOk(r, st.mom, num(r.yes_price)) &&\n", "        momOk(r, st.mom, num(r.yes_price)) &&\n        roleOk(r, st.role) &&\n")
rep("""        sitCell(tr, r, { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source });
        momCell(tr, r);""", """        sitCell(tr, r, { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source });
        roleCell(tr, r);
        momCell(tr, r);""")
rep("    els.mom.addEventListener('change', () => { st.mom = els.mom.value; draw(); });", "    els.mom.addEventListener('change', () => { st.mom = els.mom.value; draw(); });\n    els.role.addEventListener('change', () => { st.role = els.role.value; draw(); });")
# projections
rep("const pjs = { game: '', mkt: '', pos: '', mom: '', q: '',", "const pjs = { game: '', mkt: '', pos: '', mom: '', role: '', q: '',")
rep("  pjEl('pj-mom').addEventListener('change', (e) => { pjs.mom = e.target.value; drawProj(); });", "  pjEl('pj-mom').addEventListener('change', (e) => { pjs.mom = e.target.value; drawProj(); });\n  pjEl('pj-role').addEventListener('change', (e) => { pjs.role = e.target.value; drawProj(); });")
rep("      momOk(r, pjs.mom, num(r.p_over), 5) &&\n", "      momOk(r, pjs.mom, num(r.p_over), 5) &&\n      roleOk(r, pjs.role) &&\n")
rep("""      td(r.mom_p === '' ? '—' : pctR(num(r.mom_p)), 'num rs-hide-narrow rs-sub');
      momCell(tr, r);""", """      td(r.mom_p === '' ? '—' : pctR(num(r.mom_p)), 'num rs-hide-narrow rs-sub');
      roleCell(tr, r);
      momCell(tr, r);""")
# ---------------- outlook: v4 note ----------------
rep("""      : O.cal === 'v3'
        ? `Wedger = 85% market""", """      : O.cal === 'v4'
        ? `Wedger = 85% market + 15% our read${O.P_v1 != null ? ` (${pctR(100 * O.P_v1)} before calibration)` : ''}, calibrated on 706 settled Week 6–7 lines (a Yes priced near 50¢ came true about 45% for receiving and anytime TDs, 40% for rushing, 56% for passing)${rmPts(O, P) ? `, then ${rmPts(O, P)} for how players in his role have done in spots like this (2023–25)` : ''}.${O.P_l4 != null ? ` Last-4 view: ${pctR(100 * O.P_l4)}.` : ''} ${pickTxt}Yes = ${cond}.`
      : O.cal === 'v3'
        ? `Wedger = 85% market""")
rep("    const pickTxt = r.sit_pick ?", """    const rmPts = (O_, P_) => { if (!O_.rm) return ''; const p = P_ / 100, z = Math.log(p / (1 - p)) - O_.rm, p0 = 1 / (1 + Math.exp(-z)); const d = Math.round(100 * (p - p0) * 10) / 10; return Math.abs(d) < 0.3 ? '' : `${d > 0 ? '+' : '−'}${Math.abs(d).toFixed(1)} pts`; };
    const pickTxt = r.sit_pick ?""")
rep("If the line posts at ${line} for 50¢, Wedger would be about ${pctR(P)}: 85% the price + 15% our read, then the Week 6–7 calibration (passing overs have come true more often than their price, rushing overs less).`}",
    "If the line posts at ${line} for 50¢, Wedger would be about ${pctR(P)}: 85% the price + 15% our read, then the Week 6–7 calibration (passing overs have come true more often than their price, rushing overs less)${rmPts(O, P) ? ` and ${rmPts(O, P)} for his role and spot` : ''}.`}")
# waterfall history step mentions the volume x efficiency blend
rep("""    const steps = [{ label: 'History', why: `${C.by === 'minutes' ? 'Minutes' : 'Usage'} cases since ${sp.sinceLab || "'" + String(sp.since).slice(2)}, weighted for ${sp.when || 'this week'}`, v: O.m0, tot: true }];""",
    """    const steps = [{ label: 'History', why: O.ve && O.m0_cases != null ? `Usage cases since '23 (${fmtStat(stat, O.m0_cases)}) blended 50/50 with recent volume × long-run efficiency (${avg1(O.ve.vol)} ${VUNIT_S[stat] || 'touches'}/g × ${(Math.round(O.ve.eff * 100) / 100).toFixed(stat === 'rec' ? 2 : 1)} = ${fmtStat(stat, O.ve.m)})` : `${C.by === 'minutes' ? 'Minutes' : 'Usage'} cases since ${sp.sinceLab || "'" + String(sp.since).slice(2)}, weighted for ${sp.when || 'this week'}`, v: O.m0, tot: true }];""")
rep("  const statOf = (det, stat) =>", "  const VUNIT_S = { rec: 'targets', recyd: 'targets', rushyd: 'carries', passyd: 'attempts' };\n  const statOf = (det, stat) =>")
# role section after Recent form
rep("""      ov.append(sec('Recent form', 'Last 4 games vs the season', mc));
    }""", r"""      ov.append(sec('Recent form', 'Last 4 games vs the season', mc));
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
        kids.push(el('p', 'wg-note', `How often the over cleared the line books would set for players in these spots. All ${SIT_WORD[stat] || ''} props: ${bs != null ? pct1(bs) : '—'} in 2026, ${bh != null ? pct1(bh) : '—'} in 2023–25 (green = 3+ pts better, red = 3+ worse).${rmPts(O, P) ? ` Together these move Wedger % by ${rmPts(O, P)}.` : ''}`));
      }
      ov.append(sec('His role', 'How he is used, and how players like him do in spots like this', ...kids));
    }""")
# against this defense (matchup tab)
rep("""    mu.append(sec('Game', null, chips));""", r"""    mu.append(sec('Game', null, chips));
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
    }""")
# ---------------- charts code ----------------
CJ = r"""
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
      const ser = [['Volume (targets / carries / attempts)', R('recency_vol').filter((r) => r.label === rc2.comp), dash.colors[0]], ['Efficiency (yards per unit)', R('recency_eff').filter((r) => r.label === rc2.comp), dash.colors[1]]];
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
"""
rep("\n  function drawCharts() {", CJ + "\n  function drawCharts() {")
rep("    drawMom();\n    drawTeams();\n  }", "    drawMom();\n    drawTeams();\n    drawCats();\n    drawResearch();\n  }")
open(B + 'page_template.html', 'w').write(s)
print('w8b ok', len(s))
