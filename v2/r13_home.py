"""Round 13 (Tue Nov 17): Home's record shows the final-line record (rh/frec.csv, from bt/card_bt/summary.py) in place of
the certified record, in the same layout: hit rate, record, net, and the header chip. The words under the numbers name
what they are (final lines, with the backtest) and "See the record" opens Results, where the record and its note live.
The certified record itself stays on Analysts."""
def apply(s, js):
    def sr(a, b, n=1):
        nonlocal s
        c = s.count(a); assert c == n, f'r13 html: {a[:70]!r} found {c}'; s = s.replace(a, b)
    def jr(a, b, n=1):
        nonlocal js
        c = js.count(a); assert c == n, f'r13 js: {a[:70]!r} found {c}'; js = js.replace(a, b)
    sr('<span class="pf-label">Certified hit rate · Week 11</span>', '<span class="pf-label" data-wz="frec-label">Final-line hit rate · incl. backtest</span>')
    sr('<span class="v2-ps"><b data-wz="cert-wl">—</b>certified</span>', '<span class="v2-ps"><b data-wz="cert-wl">—</b>final lines</span>')
    sr('<button type="button" class="wz-btn wz-btn-w" data-go="analysts">See the record ↗</button>', '<button type="button" class="wz-btn wz-btn-w" data-go="results">See the record ↗</button>')
    sr('<div class="wg-record" id="wg-record" data-source="results" role="status" aria-label="Wedge record">',
       '<div class="wg-record" id="wg-record" data-source="frec" role="status" aria-label="Final-line record">')
    sr('<span class="wg-record-label"><i aria-hidden="true"></i>Certified hit rate</span>', '<span class="wg-record-label"><i aria-hidden="true"></i>Final-line hit rate</span>')
    sr('<span class="wg-record-sub">Certified picks, settled</span>', '<span class="wg-record-sub">Final lines, settled</span>')
    # the header chip and the hero: the final-line record when it's loaded (everyone gets it in data/public.json)
    jr("""    const box = $('#wg-record');
    const pctEl = $('.wg-record-pct', box), fracEl = $('.wg-record-frac', box), subEl = $('.wg-record-sub', box);
    box.classList.remove('wg-up', 'wg-down');
""", """    const box = $('#wg-record');
    const pctEl = $('.wg-record-pct', box), fracEl = $('.wg-record-frac', box), subEl = $('.wg-record-sub', box);
    box.classList.remove('wg-up', 'wg-down');
    const fr = v2Frec();
    if (fr) {
      pctEl.textContent = (fr.p % 1 ? fr.p.toFixed(1) : fr.p) + '%'; fracEl.textContent = `(${fr.w}/${fr.n})`;
      subEl.textContent = `Final lines, Weeks 1–${fr.thru} (with the backtest)`;
      wzRecord(fr.p, fr.w, fr.n); box.classList.add(fr.p > 50 ? 'wg-up' : 'wg-down');
      wzSet('frec-label', `Final-line hit rate · Weeks 1–${fr.thru}, incl. backtest`);
      return;
    }
""")
    jr("""  function drawProfit() {
    const el = $('#wg-profit');
""", """  function v2Frec() {
    const d = dash.data('frec'); const r = d.status === 'ok' ? d.data[0] : null;
    if (!r || r.wins === '' || r.wins == null) return null;
    const w = Number(r.wins), n = w + Number(r.losses);
    return { w, n, p: Number(r.win_pct), roi: Number(r.roi_pct), thru: Number(r.thru) || 10 };
  }
  function drawProfit() {
    const el = $('#wg-profit');
    const fr = v2Frec();
    if (fr) {
      const big = document.createElement('span');
      big.className = 'wg-profit-pct' + (fr.roi > 0 ? ' wg-pos' : (fr.roi < 0 ? ' wg-neg' : ''));
      big.textContent = (fr.roi > 0 ? '+' : (fr.roi < 0 ? '−' : '')) + Math.abs(fr.roi).toFixed(1) + '%';
      el.replaceChildren(`Net profit on final lines, Weeks 1–${fr.thru} with the backtest: `, big);
      wzSet('cert-profit', big.textContent, true);
      return;
    }
""")
    return s, js
