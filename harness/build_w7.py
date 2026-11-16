import csv, json, sys
R = sys.argv[1]; OUT = sys.argv[2]; theme = sys.argv[3]; role = sys.argv[4] if len(sys.argv) > 4 else 'none'
ds = {'lines':'inband_w7.csv','props':'props_cat_w7.csv','defense':'defense_w7.csv','atd':'atd_w7.csv','results':'results_w6_w7.csv','hist_perms':'hist_perms.csv','hist_lines':'hist_lines.csv','sit':'sit_w7.csv','outlook':'outlook_w7.csv','nflctx':'nflctx_w7.csv','nba_lines':'../nba/nba_lines.csv','nba_sit':'../nba/nba_sit.csv','nba_outlook':'../nba/nba_outlook.csv','nba_ctx':'../nba/nba_ctx.csv','pick_prices':'pick_prices_w7.csv','nba_results':'../nba/nba_results.csv'}
data = {k: list(csv.DictReader(open(R + v))) for k, v in ds.items()}
page = open(R + (sys.argv[5] if len(sys.argv) > 5 else 'index.html')).read()
import base64 as _b64
for _u, _f in (('/_blob/43606eb1e05cb9531db70c83606edd16', 'wedger-logo.png'), ('/_blob/0343890db162cebaef69169009468273', 'wedger-tri.png'), ('/_blob/17e72076470b258f8b23a2bfba6065a6', 'wedger-letters.png')):
    page = page.replace(_u, 'data:image/png;base64,' + _b64.b64encode(open(R + 'assets/' + _f, 'rb').read()).decode())
light = """--color-bg:#ffffff;--color-fg:#1f1e1d;--color-fg-muted:#6b6a68;--color-border-line:#e5e3df;--color-panel:#faf9f7;--color-ok:#2e7d4f;--color-warn:#b26a00;--color-bad:#c0392b;
--cds-border:#dedcd8;--cds-chart-grid:#ecebe8;--cds-chart-muted:#c9c7c2;--cds-chart-reference:#8a8883;--cds-chart-status-critical:#d0453a;--cds-surface-popover:#fff;--cds-text-secondary:#6b6a68;--cds-shadow-popover:0 4px 16px rgba(0,0,0,.12);"""
dark = """--color-bg:#1f1e1d;--color-fg:#f0eee9;--color-fg-muted:#a3a19c;--color-border-line:#3a3936;--color-panel:#262624;--color-ok:#5fbf86;--color-warn:#e0a040;--color-bad:#e46a5e;
--cds-border:#3d3c39;--cds-chart-grid:#33322f;--cds-chart-muted:#55534f;--cds-chart-reference:#8f8d88;--cds-chart-status-critical:#e05a4e;--cds-surface-popover:#2c2b29;--cds-text-secondary:#a3a19c;--cds-shadow-popover:0 4px 16px rgba(0,0,0,.5);"""
common = """--cds-dur-slow:.2s;--cds-font-size-body:14px;--cds-font-size-caption:12px;--cds-font-size-heading:18px;--cds-font-size-title:26px;--cds-font-weight-medium:500;
--cds-gap-xs:4px;--cds-gap-sm:8px;--cds-gap-md:16px;--cds-gap-lg:24px;--cds-pad-xs:4px;--cds-pad-sm:8px;--cds-pad-md:12px;--cds-pad-lg:20px;--cds-radius:8px;
--font-anthropic-sans:system-ui,sans-serif;--font-anthropic-serif:Georgia,serif;"""
mock = """<script>
window.__errs = [];
window.addEventListener('error', (e) => window.__errs.push(String(e.message)));

if ('__ROLE__' !== 'none') {
  const store = { 'wedger/certs': __SEED__, 'wedger/analysts': __ANSEED__ };
  const subs = {};
  const snap = (p) => ({ id: p.split('/').pop(), exists: !!store[p], data: () => store[p], metadata: { fromCache: false, hasPendingWrites: false } });
  const db = { doc: (p) => ({ path: p,
    get: async () => snap(p),
    set: async (d) => { await new Promise((r) => setTimeout(r, 50)); store[p] = JSON.parse(JSON.stringify(d)); window.__writes = (window.__writes || 0) + 1; (subs[p] || []).forEach((f) => f(snap(p))); },
    onSnapshot: (f) => { (subs[p] = subs[p] || []).push(f); setTimeout(() => f(snap(p)), 20); return () => {}; } }) };
  const user = { isOwner: async () => '__ROLE__' === 'owner' };
  window.claude = { use: (n) => new Promise((r) => setTimeout(() => r(n === 'db' ? db : n === 'user' ? user : null), 100)) };
  window.__store = store;
}
window.dash = (() => {
  const raw = %s; const calcs = {};
  return {
    colors: ['#2a6fdb', '#e07b39', '#7a5cc4', '#3aa17e'],
    calc(id, def) { calcs[id] = def; },
    data(id) { if (raw[id]) return { status: 'ok', data: raw[id] }; if (calcs[id]) return { status: 'ok', data: calcs[id].fn(...calcs[id].inputs.map((i) => raw[i])) }; return { status: 'error', data: null }; },
    onData(fn) { setTimeout(fn, 30); },
    setLink() {},
  };
})();
</script>""" % json.dumps(data)
mock = mock.replace('__ROLE__', role).replace('__SEED__', open(R + 'certs_seed.json').read()).replace('__ANSEED__', open(R + 'analysts_seed.json').read())
html = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<style>:root{{{light if theme=='light' else dark}{common}}} body{{margin:0;padding:0;background:var(--color-bg);color:var(--color-fg);font-family:var(--font-anthropic-sans);font-size:14px}}
.rs-card{{background:var(--color-panel)}} .dash-skeleton{{opacity:.6}}</style>
<script src="/opt/npm-tools/node_modules/d3/dist/d3.min.js"></script>{mock}</head><body>{page}</body></html>"""
open(OUT, 'w').write(html)
