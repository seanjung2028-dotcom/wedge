"""Round 12 (Tue Nov 17): the top of Results is the final-line record: Weeks 1-9 backtested with this week's card rules
(bt/card_bt/; four lines left out) plus Wedge picks added by hand, then the card's certified finals (all noted on the page). Like Home's record: the hit rate biggest,
the record medium, the net small; every final line, week by week, on the left. The Week 6 tiles give way to it."""
V = '/home/claude/wedger/v2/'
HERO = '''    <section class="v2-frec" id="results-frec" aria-label="Final-line record">
      <div class="v2-frec-list" id="results-frec-list" aria-label="Every final line, week by week"></div>
      <div class="pf-proof v2-frec-proof">
        <div class="pf-blob" aria-hidden="true"></div>
        <span class="pf-label" id="frec-label">Final lines</span>
        <div class="pf-big dash-skeleton" id="frec-pct">—</div>
        <div class="v2-frec-stats">
          <span class="v2-ps v2-frec-wl"><b id="frec-wl">—</b>record</span>
          <span class="v2-ps v2-ps-net v2-frec-net"><b id="frec-net">—</b>net</span>
        </div>
        <p class="v2-frec-note" id="frec-note"></p>
      </div>
    </section>'''
CSS = '''
/* round 12: the final-line record at the top of Results */
.wg-paper .v2-open .v2-frec { display: grid; grid-template-columns: minmax(0, 1.08fr) minmax(0, 1fr); gap: clamp(28px, 5vw, 80px); align-items: start; margin: clamp(8px, 1.6vw, 20px) 0 clamp(40px, 6vw, 88px); }
.wg-paper .v2-open .v2-frec-proof { position: sticky; top: 96px; isolation: isolate; padding: 6px 0 0; gap: 16px; }
.wg-paper .v2-open .v2-frec-proof .pf-big { font-size: clamp(76px, 9vw, 150px); }
.wg-paper .v2-open .v2-frec-stats { display: flex; flex-direction: column; align-items: flex-start; gap: 12px; }
.wg-paper .pf-proof.v2-frec-proof .v2-frec-wl b { font-size: clamp(36px, 4.2vw, 58px); }
.wg-paper .pf-proof.v2-frec-proof .v2-frec-net { font-size: clamp(12px, 1vw, 14px); }
.wg-paper .pf-proof.v2-frec-proof .v2-frec-net b { font-size: clamp(19px, 1.9vw, 25px); }
.wg-paper .v2-open .v2-frec-note { max-width: 46ch; margin: 6px 0 0; color: var(--pf-muted); font-size: 13.5px; line-height: 1.55; }
.wg-paper .v2-open .v2-frec-list { min-width: 0; }
.wg-paper .v2-open .v2-frec-wk { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; padding: 22px 6px 8px; font-family: var(--wx-mono); font-size: 11.5px; letter-spacing: .1em; text-transform: uppercase; color: var(--pf-muted); }
.wg-paper .v2-open .v2-frec-wk:first-child { padding-top: 0; }
.wg-paper .v2-open .v2-frec-wk b { font-weight: 600; color: var(--pf-ink, #f6f7f8); }
.wg-paper .v2-open .v2-frec-pick { grid-template-columns: auto minmax(0, 1fr) auto; }
.wg-paper .v2-open .v2-frec-pick .wz-helm { width: 44px; height: auto; }
.wg-paper .v2-open .v2-frec-pick b { display: block; line-height: 1.35; }
.wg-paper .v2-open .v2-frec-tag { display: inline-block; margin-right: 7px; padding: 0 6px; border: 1px solid rgba(255,255,255,.18); border-radius: 999px; font: 600 10px/1.6 var(--wx-mono); letter-spacing: .06em; text-transform: uppercase; font-style: normal; color: var(--pf-muted); }
.wg-paper .v2-open .v2-frec-tag.is-add { border-color: rgba(255,255,255,.34); color: #f6f7f8; }
.wg-paper .v2-open .v2-frec-tag.is-card { border-color: var(--wg-green); color: var(--wg-green); }
@media (max-width: 860px) {
  .wg-paper .v2-open .v2-frec { grid-template-columns: minmax(0, 1fr); }
  .wg-paper .v2-open .v2-frec-proof { position: relative; top: 0; order: -1; }
}
'''
def apply(s, js):
    def jr(a, b, n=1):
        nonlocal js
        c = js.count(a); assert c == n, f'r12 js: {a[:70]!r} found {c}'; js = js.replace(a, b)
    i = s.index('<section class="rs-tiles" id="results-tiles">'); j = s.index('</section>', i) + len('</section>')
    s = s[:i] + HERO.lstrip() + s[j:]
    k = s.rindex('</style>'); s = s[:k] + CSS + s[k:]
    jr('  // ---------------- render ----------------', open(V + 'src/bt.js').read() + '\n  // ---------------- render ----------------')
    jr("results: () => { drawResultsSummary(); drawResults(); }", "results: () => { v2DrawFrec(); drawResultsSummary(); drawResults(); }")
    return s, js
