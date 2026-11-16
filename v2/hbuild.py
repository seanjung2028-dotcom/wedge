import csv, json, sys
R = sys.argv[1]; OUT = sys.argv[2]; theme = sys.argv[3]; role = sys.argv[4] if len(sys.argv) > 4 else 'none'
ds = {'lines':'inband_w10.csv','lines_all':'lines_all_w10.csv','props':'props_cat_w10.csv','defense':'defense_w10.csv','atd':'atd_w10.csv','results':'results_w6_w10.csv','hist_perms':'hist_perms.csv','hist_lines':'hist_lines.csv','sit':'sit_w10.csv','outlook':'outlook_w10.csv','nflctx':'nflctx_w10.csv','nba_lines':'../nba/nba_lines.csv','nba_sit':'../nba/nba_sit.csv','nba_outlook':'../nba/nba_outlook.csv','nba_ctx':'../nba/nba_ctx.csv','pick_prices':'pick_prices_w7.csv','nba_results':'../nba/nba_results.csv','proj':'proj_w10.csv','bt_weeks':'bt_weeks.csv','bt_props':'bt_props.csv','mom_summary':'mom_summary.csv','team_mom':'team_mom.csv','defhist':'defhist_w10.csv','cats':'cats.csv','research':'research.csv'}
ds['sit'] = '/home/claude/wedger/v2/data/sit_w10_v2.csv'; ds['inj'] = '/home/claude/wedger/v2/data/inj_w10.csv'
csv.field_size_limit(10**9)
data = {k: list(csv.DictReader(open(v if v.startswith('/') else R + v))) for k, v in ds.items()}
page = open(sys.argv[5]).read()
import base64 as _b64
for _u, _f in (('/_blob/43606eb1e05cb9531db70c83606edd16', 'wedger-logo.png'), ('/_blob/0343890db162cebaef69169009468273', 'wedger-tri.png'), ('/_blob/17e72076470b258f8b23a2bfba6065a6', 'wedger-letters.png')):
    page = page.replace(_u, 'data:image/png;base64,' + _b64.b64encode(open(R + 'assets/' + _f, 'rb').read()).decode())
import json as _json
for _id, _f in (('574a1535b4f45851e0d51298efe3d357', 'wordmark_ink.png'), ('ee61fb3a382bb851df8754438f5fc0d6', 'wordmark_light.png')):
    page = page.replace('/_blob/' + _id, 'data:image/png;base64,' + _b64.b64encode(open('/home/claude/wedger/brand/' + _f, 'rb').read()).decode())
_FF = {'archivo': 'archivo-latin-wght-normal', 'geist400': 'geist-sans-latin-400-normal', 'geist500': 'geist-sans-latin-500-normal', 'geist600': 'geist-sans-latin-600-normal', 'geist700': 'geist-sans-latin-700-normal', 'mono400': 'geist-mono-latin-400-normal', 'mono500': 'geist-mono-latin-500-normal', 'archivowide': 'archivo-latin-wdth-normal'}
for _k, _id in _json.load(open('/home/claude/wedger/brand/font_blobs.json')).items():
    page = page.replace('/_blob/' + _id, 'data:font/woff2;base64,' + _b64.b64encode(open('/home/claude/wedger/brand/fonts/' + _FF[_k] + '.woff2', 'rb').read()).decode())
for _id, _f in (('cb3e379850ce2f3eab2050b2876e9f7f', 'kodchasan-500'), ('28e26ef48c0a46a1b873963434da73e9', 'kodchasan-600')):
    page = page.replace('/_blob/' + _id, 'data:font/woff2;base64,' + _b64.b64encode(open('/home/claude/wedger/brand/fonts/' + _f + '.woff2', 'rb').read()).decode())
page = page.replace('/_blob/8fed206d21c4646deccb0619517a2658', 'data:image/webp;base64,' + _b64.b64encode(open('/home/claude/wedger/brand/bake/metal.webp', 'rb').read()).decode())
page = page.replace('/_blob/97527b50379fa5df66d261f6a12986a4', 'data:font/woff2;base64,' + _b64.b64encode(open('/home/claude/wedger/brand/fonts/handlee.woff2', 'rb').read()).decode())  # V2's handwriting font
for _k, _id in _json.load(open('/home/claude/wedger/helm/helm_blobs.json')).items():
    page = page.replace('/_blob/' + _id, 'data:image/webp;base64,' + _b64.b64encode(open('/home/claude/wedger/helm/out/' + _k + '.webp', 'rb').read()).decode())
for _k, _id in _json.load(open('/home/claude/wedger/photos/blob_map.json')).items():
    page = page.replace('/_blob/' + _id, 'data:image/jpeg;base64,' + _b64.b64encode(open('/home/claude/wedger/photos/web/' + _k + '.jpg', 'rb').read()).decode())
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
    delete: async () => { delete store[p]; (subs[p] || []).forEach((f) => f(snap(p))); },
    onSnapshot: (f) => { (subs[p] = subs[p] || []).push(f); setTimeout(() => f(snap(p)), 20); return () => {}; } }) };
  const user = { isOwner: async () => '__ROLE__' === 'owner', id: async () => 'u_harness_viewer', me: async () => ({ id: 'u_harness_viewer', name: 'Sean Jung' }) };
  window.claude = { use: (n) => new Promise((r) => setTimeout(() => r(n === 'db' ? db : n === 'user' ? user : null), 100)) };
  window.__store = store;
}
window.dash = (() => {
  const raw = %s; const calcs = {};
  return {
    colors: ['#2a6fdb', '#e07b39', '#7a5cc4', '#3aa17e'],
    calc(id, def) { calcs[id] = def; },
    data(id) { if (raw[id]) return { status: 'ok', data: raw[id] }; if (calcs[id]) return { status: 'ok', data: calcs[id].fn(...calcs[id].inputs.map((i) => raw[i])) }; return { status: 'error', data: null }; },
    onData(fn) { fn(); setTimeout(fn, 30); },
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
