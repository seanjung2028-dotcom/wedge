"""Build the standalone, read-only Wedge website into /home/claude/wedger/site.

It is the same page the dashboard artifact serves (v2/out: index.html, wg.js, wg.css, final.js, brain.js), with:
  - every /_blob/<id> asset written to site/assets/ under a readable name,
  - every dataset written to site/data/<id>.csv (same files the artifact's datasets point to),
  - the shared record (certified picks, analysts) written to site/data/*.json, read-only,
  - runtime.js standing in for the dashboard runtime (dash.data / onData / calc / setLink) and for the
    shared store (window.claude.use('db' | 'user')): it loads the data, then the page scripts. No one is the owner,
    so the certify boxes never show; the record is updated by rebuilding and pushing.
Run after every site update:  python3 /home/claude/wedger/v2/build_site.py
"""
import json, os, re, shutil, sys
W = '/home/claude/wedger/'; R = W + 'rh/'; OUT = W + 'site/'; SRC = W + 'v2/out/'
DS = {'lines': 'inband_w10.csv', 'lines_all': 'lines_all_w10.csv', 'props': 'props_cat_w10.csv', 'defense': 'defense_w10.csv', 'atd': 'atd_w10.csv',
      'results': 'results_w6_w10.csv', 'hist_perms': 'hist_perms.csv', 'hist_lines': 'hist_lines.csv', 'sit': W + 'v2/data/sit_w10_v2.csv',
      'outlook': 'outlook_w10.csv', 'nflctx': 'nflctx_w10.csv', 'nba_lines': '../nba/nba_lines.csv', 'nba_sit': '../nba/nba_sit.csv',
      'nba_outlook': '../nba/nba_outlook.csv', 'nba_ctx': '../nba/nba_ctx.csv', 'pick_prices': 'pick_prices_w7.csv', 'nba_results': '../nba/nba_results.csv',
      'proj': 'proj_w10.csv', 'bt_weeks': 'bt_weeks.csv', 'bt_props': 'bt_props.csv', 'mom_summary': 'mom_summary.csv', 'team_mom': 'team_mom.csv',
      'defhist': 'defhist_w10.csv', 'cats': 'cats.csv', 'research': 'research.csv', 'inj': W + 'v2/data/inj_w10.csv'}
CERTS = R + 'certs_seed.json'          # local copy of the live wedger/certs doc (refresh it whenever certs change)
ANALYSTS = R + 'analysts_seed.json'    # local copy of the live wedger/analysts doc

def assets():
    """blob id -> (source file, published path)"""
    m = {}
    for v, f in (('43606eb1e05cb9531db70c83606edd16', 'wedger-logo.png'), ('0343890db162cebaef69169009468273', 'wedger-tri.png'), ('17e72076470b258f8b23a2bfba6065a6', 'wedger-letters.png')):
        m[v] = (R + 'assets/' + f, 'assets/img/' + f)
    for v, f in (('574a1535b4f45851e0d51298efe3d357', 'wordmark_ink.png'), ('ee61fb3a382bb851df8754438f5fc0d6', 'wordmark_light.png')):
        m[v] = (W + 'brand/' + f, 'assets/img/' + f)
    FF = {'archivo': 'archivo-latin-wght-normal', 'geist400': 'geist-sans-latin-400-normal', 'geist500': 'geist-sans-latin-500-normal', 'geist600': 'geist-sans-latin-600-normal',
          'geist700': 'geist-sans-latin-700-normal', 'mono400': 'geist-mono-latin-400-normal', 'mono500': 'geist-mono-latin-500-normal', 'archivowide': 'archivo-latin-wdth-normal'}
    for k, v in json.load(open(W + 'brand/font_blobs.json')).items():
        m[v] = (W + 'brand/fonts/' + FF[k] + '.woff2', 'assets/fonts/' + FF[k] + '.woff2')
    for v, f in (('cb3e379850ce2f3eab2050b2876e9f7f', 'kodchasan-500'), ('28e26ef48c0a46a1b873963434da73e9', 'kodchasan-600'), ('97527b50379fa5df66d261f6a12986a4', 'handlee')):
        m[v] = (W + 'brand/fonts/' + f + '.woff2', 'assets/fonts/' + f + '.woff2')
    m['8fed206d21c4646deccb0619517a2658'] = (W + 'brand/bake/metal.webp', 'assets/img/metal.webp')
    for k, v in json.load(open(W + 'helm/helm_blobs.json')).items():
        m[v] = (W + 'helm/out/' + k + '.webp', 'assets/helmets/' + k + '.webp')
    for k, v in json.load(open(W + 'photos/blob_map.json')).items():
        m[v] = (W + 'photos/web/' + k + '.jpg', 'assets/players/' + k + '.jpg')
    return m

LIGHT = """--color-bg:#ffffff;--color-fg:#1f1e1d;--color-fg-muted:#6b6a68;--color-border-line:#e5e3df;--color-panel:#faf9f7;--color-ok:#2e7d4f;--color-warn:#b26a00;--color-bad:#c0392b;
--cds-border:#dedcd8;--cds-chart-grid:#ecebe8;--cds-chart-muted:#c9c7c2;--cds-chart-reference:#8a8883;--cds-chart-status-critical:#d0453a;--cds-surface-popover:#fff;--cds-text-secondary:#6b6a68;--cds-shadow-popover:0 4px 16px rgba(0,0,0,.12);"""
DARK = """--color-bg:#1f1e1d;--color-fg:#f0eee9;--color-fg-muted:#a3a19c;--color-border-line:#3a3936;--color-panel:#262624;--color-ok:#5fbf86;--color-warn:#e0a040;--color-bad:#e46a5e;
--cds-border:#3d3c39;--cds-chart-grid:#33322f;--cds-chart-muted:#55534f;--cds-chart-reference:#8f8d88;--cds-chart-status-critical:#e05a4e;--cds-surface-popover:#2c2b29;--cds-text-secondary:#a3a19c;--cds-shadow-popover:0 4px 16px rgba(0,0,0,.5);"""
COMMON = """--cds-dur-slow:.2s;--cds-font-size-body:14px;--cds-font-size-caption:12px;--cds-font-size-heading:18px;--cds-font-size-title:26px;--cds-font-weight-medium:500;
--cds-gap-xs:4px;--cds-gap-sm:8px;--cds-gap-md:16px;--cds-gap-lg:24px;--cds-pad-xs:4px;--cds-pad-sm:8px;--cds-pad-md:12px;--cds-pad-lg:20px;--cds-radius:8px;
--font-anthropic-sans:system-ui,-apple-system,'Segoe UI',sans-serif;--font-anthropic-serif:Georgia,serif;"""

RUNTIME = r"""/* Wedge standalone runtime: stands in for the dashboard runtime and the shared store (read-only). */
(function () {
  'use strict';
  var IDS = __IDS__;
  var raw = {}, calcs = {}, subs = [], booted = false;
  window.dash = {
    colors: ['#2a6fdb', '#e07b39', '#7a5cc4', '#3aa17e'],
    calc: function (id, def) { calcs[id] = def; },
    data: function (id) {
      if (raw[id]) return { status: 'ok', data: raw[id], refreshing: false, truncated: false };
      var c = calcs[id];
      if (c) {
        var ins = c.inputs.map(function (i) { return raw[i]; });
        if (ins.some(function (x) { return !x; })) return { status: 'loading', data: null };
        return { status: 'ok', data: c.fn.apply(null, ins) };
      }
      return { status: booted ? 'missing' : 'loading', data: [] };
    },
    onData: function (fn) { subs.push(fn); try { fn(); } catch (e) { console.error(e); } },
    setLink: function () {},
    params: function () { return {}; }, setParams: function () {}, resetParams: function () {}, refresh: function () {}
  };
  var store = {};
  var snap = function (p) { return { id: p.split('/').pop(), exists: !!store[p], data: function () { return store[p]; }, metadata: { fromCache: false, hasPendingWrites: false } }; };
  var ready;
  var db = { doc: function (p) { return {
    path: p,
    get: function () { return ready.then(function () { return snap(p); }); },
    set: function () { return Promise.reject(new Error('This site is read-only.')); },
    delete: function () { return Promise.reject(new Error('This site is read-only.')); },
    onSnapshot: function (f) { ready.then(function () { f(snap(p)); }); return function () {}; }
  }; } };
  var user = { isOwner: function () { return Promise.resolve(false); }, id: function () { return Promise.resolve(null); }, me: function () { return Promise.resolve(null); } };
  window.claude = { use: function (n) { return Promise.resolve(n === 'db' ? db : n === 'user' ? user : null); } };

  var getText = function (u) { return fetch(u, { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw new Error(u + ' ' + r.status); return r.text(); }); };
  var loadScript = function (src) { return new Promise(function (res, rej) { var s = document.createElement('script'); s.src = src; s.onload = res; s.onerror = function () { rej(new Error(src)); }; document.body.appendChild(s); }); };
  window.WedgeRuntime = { boot: function (scripts) {
    var veil = document.getElementById('wz-boot');
    ready = Promise.all([getText('data/certs.json'), getText('data/analysts.json')]).then(function (t) {
      store['wedger/certs'] = JSON.parse(t[0]); store['wedger/analysts'] = JSON.parse(t[1]);
    });
    return Promise.all(IDS.map(function (id) { return getText('data/' + id + '.csv').then(function (t) { raw[id] = d3.csvParse(t); }); }))
      .then(function () { booted = true; return scripts.reduce(function (p, s) { return p.then(function () { return loadScript(s); }); }, Promise.resolve()); })
      .then(function () { subs.forEach(function (f) { try { f(); } catch (e) { console.error(e); } }); if (veil) veil.remove(); })
      .catch(function (e) { console.error(e); if (veil) veil.textContent = 'Wedge couldn’t load its data. Refresh to try again.'; });
  } };
})();
"""

def main():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    for d in ('data', 'assets/img', 'assets/fonts', 'assets/helmets', 'assets/players', 'vendor'): os.makedirs(OUT + d, exist_ok=True)
    A = assets(); used = set()
    def fix(t):
        def sub(m):
            k = m.group(1); used.add(k); return A[k][1]
        return re.sub(r'/_blob/([0-9a-f]{32})', sub, t)
    page = fix(open(SRC + 'index.html').read())
    links = ''.join(re.findall(r'<link[^>]+>\s*', page[:2000]))
    body = page.replace(links, '', 1) if page.startswith(links) else page
    body = re.sub(r'\s*<script src="final\.js"></script><script src="brain\.js"></script><script src="wg\.js"></script>\s*$', '\n', body)
    assert '<script src="wg.js">' not in body, 'page scripts not stripped'
    for f in ('wg.js', 'wg.css', 'final.js', 'brain.js'):
        open(OUT + f, 'w').write(fix(open(SRC + f).read()))
    for k in used:
        src, dst = A[k]; shutil.copy2(src, OUT + dst)
    tot = 0
    for k, v in DS.items():
        p = v if v.startswith('/') else R + v; shutil.copy2(p, OUT + 'data/' + k + '.csv'); tot += os.path.getsize(p)
    json.dump({'picks': json.load(open(CERTS))['picks']}, open(OUT + 'data/certs.json', 'w'))
    a = json.load(open(ANALYSTS)); a = a.get('data', a)
    json.dump(a, open(OUT + 'data/analysts.json', 'w'), ensure_ascii=False)
    shutil.copy2('/opt/npm-tools/node_modules/d3/dist/d3.min.js', OUT + 'vendor/d3.min.js')
    open(OUT + 'runtime.js', 'w').write(RUNTIME.replace('__IDS__', json.dumps(list(DS))))
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wedge · Football, understood.</title>
<meta name="description" content="Wedge screens NFL prediction-market lines, prices them with its own model and posts a weekly card of final lines and leans, with a graded record.">
<link rel="icon" type="image/png" href="assets/img/wedger-tri.png">
{links.strip()}
<style>
:root{{{LIGHT}{COMMON}}}
@media (prefers-color-scheme: dark){{:root{{{DARK}}}}}
html,body{{margin:0;padding:0;background:var(--color-bg);color:var(--color-fg);font-family:var(--font-anthropic-sans);font-size:14px}}
.rs-card{{background:var(--color-panel)}} .dash-skeleton{{opacity:.6}}
#wz-boot{{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:#151614;color:#e9e7e1;font:500 14px/1.4 system-ui,sans-serif;z-index:9999;letter-spacing:.02em}}
</style>
<script src="vendor/d3.min.js"></script>
<script src="runtime.js"></script>
</head>
<body>
<div id="wz-boot" role="status">Loading this week’s card…</div>
<noscript><p style="padding:24px">Wedge needs JavaScript to draw the board and the card.</p></noscript>
<div id="dash-root">
{body.strip()}
</div>
<script>WedgeRuntime.boot(['final.js', 'brain.js', 'wg.js']);</script>
</body>
</html>
"""
    open(OUT + 'index.html', 'w').write(html)
    open(OUT + '_headers', 'w').write("""/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
/data/*
  Cache-Control: public, max-age=300, must-revalidate
/assets/*
  Cache-Control: public, max-age=31536000, immutable
/vendor/*
  Cache-Control: public, max-age=31536000, immutable
""")
    open(OUT + 'robots.txt', 'w').write('User-agent: *\nAllow: /\n')
    size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(OUT) for f in fs)
    print(f'site built: {len(used)} assets, {len(DS)} datasets ({tot / 1e6:.1f} MB of data), {size / 1e6:.1f} MB total')

if __name__ == '__main__':
    main()
