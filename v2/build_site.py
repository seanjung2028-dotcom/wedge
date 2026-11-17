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
import hashlib, json, os, re, shutil, subprocess, sys
W = '/home/claude/wedger/'; R = W + 'rh/'; OUT = W + 'site/'; SRC = W + 'v2/out/'
P16 = 'pub1116/'   # static datasets as published Mon Nov 16 (used when the workspace copy is missing)
DS = {'lines': 'inband_w11.csv', 'lines_all': 'lines_all_w11.csv', 'props': 'props_cat_w11.csv', 'defense': 'defense_w11.csv', 'atd': 'atd_w11.csv',
      'results': 'results_w6_w11.csv', 'hist_perms': 'hist_perms.csv', 'hist_lines': 'hist_lines.csv', 'sit': W + 'v2/data/sit_w11_v2.csv',
      'outlook': 'outlook_w11.csv', 'nflctx': 'nflctx_w11.csv', 'nba_lines': '../nba/nba_lines.csv', 'nba_sit': '../nba/nba_sit.csv',
      'nba_outlook': '../nba/nba_outlook.csv', 'nba_ctx': '../nba/nba_ctx.csv', 'pick_prices': 'pick_prices_w7.csv', 'nba_results': '../nba/nba_results.csv',
      'proj': 'proj_w11.csv', 'bt_weeks': 'bt_weeks.csv', 'bt_props': 'bt_props.csv', 'mom_summary': 'mom_summary.csv', 'team_mom': 'team_mom.csv',
      'defhist': 'defhist_w11.csv', 'cats': 'cats.csv', 'research': 'research.csv', 'inj': W + 'v2/data/inj_w11.csv',
      'card_bt': 'card_bt.csv', 'card_bt_sum': 'card_bt_sum.csv', 'final_record': 'final_record.csv', 'frec': 'frec.csv'}
def ds_path(k, v):
    f = v if v.startswith('/') else R + v
    if os.path.exists(f): return f
    alt = R + P16 + k + '.csv'
    return alt if os.path.exists(alt) else f
PUB = '/home/claude/wedge/site/'   # repo clone's published site (asset fallback)
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
    for k, v in (json.load(open(W + 'brand/font_blobs.json')) if os.path.exists(W + 'brand/font_blobs.json') else {}).items():
        m[v] = (W + 'brand/fonts/' + FF[k] + '.woff2', 'assets/fonts/' + FF[k] + '.woff2')
    for v, f in (('cb3e379850ce2f3eab2050b2876e9f7f', 'kodchasan-500'), ('28e26ef48c0a46a1b873963434da73e9', 'kodchasan-600'), ('97527b50379fa5df66d261f6a12986a4', 'handlee')):
        m[v] = (W + 'brand/fonts/' + f + '.woff2', 'assets/fonts/' + f + '.woff2')
    m['8fed206d21c4646deccb0619517a2658'] = (W + 'brand/bake/metal.webp', 'assets/img/metal.webp')
    for k, v in json.load(open(W + 'helm/helm_blobs.json')).items():
        m[v] = (W + 'helm/out/' + k + '.webp', 'assets/helmets/' + k + '.webp')
    for k, v in json.load(open(W + 'photos/blob_map.json')).items():
        m[v] = (W + 'photos/web/' + k + '.jpg', 'assets/players/' + k + '.jpg')
    # sources missing from the workspace (brand/, helm/out, photos/web) fall back to the last published copy
    if os.path.exists(W + 'v2/blob_paths.json'):
        for v, dst in json.load(open(W + 'v2/blob_paths.json')).items():
            if v not in m or not os.path.exists(m[v][0]): m[v] = (PUB + dst, dst)
    for v, (src, dst) in list(m.items()):
        if not os.path.exists(src) and os.path.exists(PUB + dst): m[v] = (PUB + dst, dst)
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

  // Data comes in bundles of { ds: {id: csv text}, certs, analysts }: the public one for everyone, the Research one for members.
  var getBundle = function (u, onProgress) {
    return fetch(u, { credentials: 'same-origin' }).then(function (r) {
      if (!r.ok) throw new Error(u + ' ' + r.status);
      if (!r.body || !r.body.getReader || !window.TextDecoder) return r.text();
      var rd = r.body.getReader(), dec = new TextDecoder(), parts = [], got = 0;
      var pump = function () { return rd.read().then(function (x) {
        if (x.done) { parts.push(dec.decode()); return parts.join(''); }
        got += x.value.length; parts.push(dec.decode(x.value, { stream: true })); onProgress(got); return pump();
      }); };
      return pump();
    }).then(JSON.parse);
  };
  var loadScript = function (src) { return new Promise(function (res, rej) { var s = document.createElement('script'); s.src = src; s.onload = res; s.onerror = function () { rej(new Error(src)); }; document.body.appendChild(s); }); };
  var resolveReady;
  ready = new Promise(function (r) { resolveReady = r; });
  // who's here: /api/me on wedgepicks.com; anywhere without it (a local copy) the whole site is open
  var getMe = function () {
    return fetch('/api/me', { credentials: 'same-origin', cache: 'no-store' })
      .then(function (r) { return r.ok && /json/.test(r.headers.get('content-type') || '') ? r.json() : null; })
      .catch(function () { return null; });
  };
  window.WedgeRuntime = { boot: function (C) {
    var veil = document.getElementById('wz-boot'), msg = document.getElementById('wz-boot-msg') || veil, sub = document.getElementById('wz-boot-sub');
    var slow = setTimeout(function () { if (sub) sub.textContent = 'Still loading. This can take a moment on a slow connection.'; }, 8000);
    var fail = function (e) { console.error(e); clearTimeout(slow); if (msg) msg.textContent = 'Wedge couldn’t load this week’s card.'; if (sub) sub.innerHTML = 'Check your connection, then <a href="" style="color:inherit">reload the page</a>.'; };
    var got = {}, prog = function (k) { return function (n) { got[k] = n; var t = 0; for (var x in got) t += got[x]; if (sub && t > 150000) sub.textContent = (t / 1e6).toFixed(1) + ' MB loaded'; }; };
    var A;
    return getMe().then(function (m) {
      A = m ? { api: true, gating: !!m.gating, level: m.gating ? (m.level || 0) : 3, signedIn: !!m.signedIn, email: m.email || null, plan: m.plan || 'free', planName: m.planName || 'Free',
                until: m.until || null, source: m.source || null, signInReady: !!m.signInReady, checkout: m.checkout || {}, portal: m.portal || '' }
            : { api: false, gating: false, level: 3, signedIn: false, checkout: {} };
      window.WEDGE_ACCESS = A;
      var jobs = [getBundle(C.pub, prog('p'))];
      if (A.level >= 1) jobs.push(getBundle(C.t1, prog('t')).catch(function (e) { console.warn(e); A.level = 0; return null; }));
      return Promise.all(jobs);
    }).then(function (bs) {
      var b = { ds: {}, certs: { picks: [] }, analysts: { order: [], picks: {} } };
      bs.forEach(function (x) { if (!x) return; for (var k in x.ds) b.ds[k] = x.ds[k]; if (x.certs) b.certs = x.certs; if (x.analysts) b.analysts = x.analysts; });
      store['wedger/certs'] = b.certs; store['wedger/analysts'] = b.analysts; resolveReady();
      IDS.forEach(function (id) { if (b.ds[id] != null) raw[id] = d3.csvParse(b.ds[id]); });
      booted = true;
      var full = A.level >= 2;
      var card = full ? loadScript(C.fin[0]).then(function () { return loadScript(C.brain[0]); }).catch(function (e) { console.warn(e); A.level = Math.min(A.level, 1); return loadScript(C.fin[1]).then(function () { return loadScript(C.brain[1]); }); })
                      : loadScript(C.fin[1]).then(function () { return loadScript(C.brain[1]); });
      return card.then(function () { return loadScript(C.wg); });
    })
      .then(function () { clearTimeout(slow); subs.forEach(function (f) { try { f(); } catch (e) { console.error(e); } }); if (veil) veil.remove(); })
      .catch(fail);
  } };
})();
"""

# ---------------- tiers ----------------
# Who sees what (the gate itself is functions/p/[[path]].js; pages lock in v2/src/site.js):
#   everyone      data/public.json: the certified picks that have settled (the headline record), no research
#                 data/final-public.js, brain-public.js: this week's games and scores, no plays
#   Research (1)  p/t1/<hash>/data.json: every dataset, the analysts and the full record
#   Inner (2)     p/t2/<hash>/final.js, brain.js: The Winning Edge card and its reasoning
PREVIEW_PAGES = ['research', 'final', 'thesis', 'charts', 'analysts', 'results', 'nba', 'nba-charts', 'nba-results']

def key_of_result(r):
    return '|'.join(['w' + (r.get('week') or '6'), r['game'], 'Anytime Touchdown' if r['group'] == 'ATD filter picks' else r['market'], r['contract']])

def public_record(results_csv, certs):
    import csv, io
    rows = list(csv.DictReader(io.StringIO(results_csv)))
    keep = [r for r in rows if key_of_result(r) in certs and r['outcome'] in ('Won', 'Lost', 'Void')]
    settled = {key_of_result(r) for r in keep}
    out = io.StringIO(); w = csv.DictWriter(out, fieldnames=list(rows[0].keys()), lineterminator='\n'); w.writeheader(); w.writerows(keep)
    return out.getvalue(), [k for k in certs if k in settled]

def read_js_obj(path, name):
    t = open(path, encoding='utf-8').read().strip()
    m = re.match(r'window\.%s\s*=\s*([\s\S]*?);?\s*$' % name, t); assert m, path
    return json.loads(m.group(1))

def public_card(F):
    keep = {k: F.get(k) for k in ('at', 'books_at', 'week', 'model', 'backtest', 'graded') if k in F}
    keep.update({k: None for k in ('lens_how', 'lens_check', 'lens_check_title', 'lens_check_head', 'lens_thru')})
    keep['public'] = True
    keep['cards'] = [{'game': c['game'], 'kick': c.get('kick', ''), 'venue': c.get('venue', ''), 'status': c.get('status', ''), 'score': c.get('score', ''),
                      'market': '', 'lineup': '', 'branches': '', 'keys': [], 'scripts': {}, 'plays': [], 'passed': [], 'likely': [], 'value': [], 'sources': [], 'lens': {'sides': []}}
                     for c in F['cards']]
    return keep

def public_brain(B):
    return {'at': B.get('at'), 'plays': {}, 'games': {}, 'rank': [], 'bt': B.get('bt'), 'mix': B.get('mix'), 'public': True}

def favicons():
    from PIL import Image, ImageDraw
    G = '#7ED957'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><path d="M14 59 L50 59 L50 5 Z" fill="%s"/></svg>' % G)
    open(OUT + 'favicon.svg', 'w').write(svg)
    def tri(n, bg=None):
        s = 8; im = Image.new('RGBA', (n * s, n * s), bg or (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        f = lambda v: v / 64 * n * s
        d.polygon([(f(14), f(59)), (f(50), f(59)), (f(50), f(5))], fill=G)
        return im.resize((n, n), Image.LANCZOS)
    tri(32).save(OUT + 'favicon-32.png')
    tri(48).save(OUT + 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
    tri(180, (21, 22, 20, 255)).save(OUT + 'apple-touch-icon.png')

def previews():
    """Blurred pictures of each members-only page, shown behind the sign-up card. Rendered from the full local build."""
    import socket, subprocess, threading, http.server, functools
    from PIL import Image, ImageFilter
    os.makedirs(OUT + 'assets/locked', exist_ok=True)
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
        def translate_path(self, path):
            q = path.split('?', 1)[0]
            if q.startswith('/p/'): return PROT_RAW + q[1:]
            return super().translate_path(path)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Q, directory=OUT))
    th = threading.Thread(target=srv.serve_forever, daemon=True); th.start()
    try:
        tmp = '/tmp/wedge_pv'; os.makedirs(tmp, exist_ok=True)
        r = subprocess.run(['node', W + 'v2/previews.js', f'http://127.0.0.1:{port}/', tmp] + PREVIEW_PAGES, capture_output=True, text=True, timeout=240)
        if r.returncode: print(r.stdout[-800:], r.stderr[-800:]); raise SystemExit('previews failed')
    finally:
        srv.shutdown()
    out = {}
    for pid in PREVIEW_PAGES:
        src = f'{tmp}/{pid}.png'
        if not os.path.exists(src): continue
        im = Image.open(src).convert('RGB')
        im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS).filter(ImageFilter.GaussianBlur(8))
        dst = f'assets/locked/{pid}.webp'; im.save(OUT + dst, 'WEBP', quality=55, method=6)
        out[pid] = dst + '?v=' + hashlib.sha1(open(OUT + dst, 'rb').read()).hexdigest()[:10]
    return out

# ---------------- paid files: bundled into the /p function, never static ----------------
PROT = W + 'lib/protected/'      # gzipped copies the function serves (deployed with the functions)
PROT_RAW = W + 'site_protected/' # plain copies, only for rendering the previews locally (not deployed, not synced)
_prot = []
def protect(rel, text, ctype, need):
    import gzip
    if not _prot:
        for d in (PROT, PROT_RAW):
            if os.path.exists(d): shutil.rmtree(d)
            os.makedirs(d)
    name = f'f{len(_prot)}.bin'
    open(PROT + name, 'wb').write(gzip.compress(text.encode('utf-8'), 9, mtime=0))
    os.makedirs(os.path.dirname(PROT_RAW + rel), exist_ok=True); open(PROT_RAW + rel, 'w', encoding='utf-8').write(text)
    _prot.append((rel[2:], name, ctype, need))   # key without the leading "p/"

def write_manifest():
    lines = ['// written by v2/build_site.py: the paid files the /p function serves (path under /p/ -> [gzipped body, type, level needed])']
    lines += [f"import {n[:-4]} from './{n}';" for _, n, _, _ in _prot]
    lines.append('export const FILES = {')
    lines += [f"  {json.dumps(k)}: [{n[:-4]}, {json.dumps(ct)}, {lv}]," for k, n, ct, lv in _prot]
    lines.append('};')
    open(PROT + 'manifest.js', 'w').write('\n'.join(lines) + '\n')

def main():
    fast = '--fast' in sys.argv   # skip the blurred previews (keeps the last ones)
    # the live tools' server data (lib/gen: Wedge's lens on each priced rung, the card, game logs); never served from site/
    subprocess.run([sys.executable, '/home/claude/wedger/v2/build_live.py'], check=True)
    keep_pv = {}
    if fast and os.path.exists(OUT + 'assets/locked'):
        shutil.copytree(OUT + 'assets/locked', '/tmp/wedge_pv_keep', dirs_exist_ok=True)
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
    for f in ('wg.js', 'wg.css'):
        open(OUT + f, 'w').write(fix(open(SRC + f).read()))
    for k in used:
        src, dst = A[k]; shutil.copy2(src, OUT + dst)
    hx = lambda b: hashlib.sha1(b if isinstance(b, bytes) else b.encode()).hexdigest()
    put = lambda rel, text: (os.makedirs(os.path.dirname(OUT + rel), exist_ok=True), open(OUT + rel, 'w', encoding='utf-8').write(text))
    # data: Research gets everything; the public bundle is just the settled certified record (the headline numbers)
    tot = 0; ds = {}
    for k, v in DS.items():
        p = ds_path(k, v); ds[k] = open(p, encoding='utf-8').read(); tot += os.path.getsize(p)
    certs = json.load(open(CERTS))['picks']
    a = json.load(open(ANALYSTS)); a = a.get('data', a)
    full = json.dumps({'ds': ds, 'certs': {'picks': certs}, 'analysts': a}, ensure_ascii=False, separators=(',', ':'))
    rec, pub_certs = public_record(ds['results'], set(certs))
    pub = json.dumps({'ds': {'results': rec, 'frec': ds['frec']}, 'certs': {'picks': pub_certs}, 'analysts': {'order': a.get('order', []), 'picks': {}}}, ensure_ascii=False, separators=(',', ':'))
    T1 = f'p/t1/{hx(full)[:16]}/data.json'; protect(T1, full, 'application/json; charset=utf-8', 1)
    put('data/public.json', pub)
    # the card: Inner Circle gets it whole; everyone else gets the games and scores only
    fin_full = fix(open(SRC + 'final.js').read()); brain_full = fix(open(SRC + 'brain.js').read())
    T2 = f'p/t2/{hx(fin_full + brain_full)[:16]}/'
    protect(T2 + 'final.js', fin_full, 'application/javascript; charset=utf-8', 2); protect(T2 + 'brain.js', brain_full, 'application/javascript; charset=utf-8', 2)
    write_manifest()
    put('data/final-public.js', 'window.WZ_FINAL=' + json.dumps(public_card(read_js_obj(SRC + 'final.js', 'WZ_FINAL')), ensure_ascii=False, separators=(',', ':')) + ';\n')
    put('data/brain-public.js', 'window.WZ_BRAIN=' + json.dumps(public_brain(read_js_obj(SRC + 'brain.js', 'WZ_BRAIN')), ensure_ascii=False, separators=(',', ':')) + ';\n')
    shutil.copy2('/opt/npm-tools/node_modules/d3/dist/d3.min.js', OUT + 'vendor/d3.min.js')
    open(OUT + 'runtime.js', 'w').write(RUNTIME.replace('__IDS__', json.dumps(list(DS))))
    favicons()
    # Versioned URLs: the browser can cache each file, and a new build is picked up immediately (the page itself is never cached).
    ver = lambda f: f + '?v=' + hx(open(OUT + f, 'rb').read())[:10]
    boot = {'pub': ver('data/public.json'), 't1': '/' + T1, 'fin': ['/' + T2 + 'final.js', ver('data/final-public.js')],
            'brain': ['/' + T2 + 'brain.js', ver('data/brain-public.js')], 'wg': ver('wg.js')}
    links = links.replace('href="wg.css"', 'href="' + ver('wg.css') + '"')
    def write_index(pv):
        html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>wedge</title>
<meta name="description" content="Wedge screens NFL and NBA prediction-market lines, prices them with its own model and posts a weekly card of final lines and leans, with a graded record.">
<meta name="theme-color" content="#151614">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
{links.strip()}
<style>
:root{{{LIGHT}{COMMON}}}
@media (prefers-color-scheme: dark){{:root{{{DARK}}}}}
html,body{{margin:0;padding:0;background:var(--color-bg);color:var(--color-fg);font-family:var(--font-anthropic-sans);font-size:14px}}
.rs-card{{background:var(--color-panel)}} .dash-skeleton{{opacity:.6}}
#wz-boot{{position:fixed;inset:0;display:flex;flex-direction:column;gap:8px;align-items:center;justify-content:center;padding:0 24px;text-align:center;background:#151614;color:#e9e7e1;font:500 14px/1.4 system-ui,sans-serif;z-index:9999;letter-spacing:.02em}}
#wz-boot-sub{{color:#9a9890;font-weight:400;font-size:13px;min-height:1.4em}}
</style>
<script src="{ver('vendor/d3.min.js')}"></script>
<script src="{ver('runtime.js')}"></script>
</head>
<body>
<div id="wz-boot" role="status"><div id="wz-boot-msg">Loading this week’s card…</div><div id="wz-boot-sub"></div></div>
<noscript><p style="padding:24px">Wedge needs JavaScript to draw the board and the card.</p></noscript>
<div id="dash-root">
{body.strip()}
</div>
<script>
window.WEDGE_PREVIEWS = {json.dumps(pv)};
if (window.WedgeRuntime && window.d3) WedgeRuntime.boot({json.dumps(boot)});
else {{ document.getElementById('wz-boot-msg').textContent = 'Wedge couldn’t load this week’s card.'; document.getElementById('wz-boot-sub').innerHTML = 'Check your connection, then <a href="" style="color:inherit">reload the page</a>.'; }}
</script>
</body>
</html>
"""
        open(OUT + 'index.html', 'w').write(html)
    write_index({})
    if fast and os.path.exists('/tmp/wedge_pv_keep'):
        shutil.copytree('/tmp/wedge_pv_keep', OUT + 'assets/locked', dirs_exist_ok=True)
        pv = {f[:-5]: 'assets/locked/' + f + '?v=' + hx(open(OUT + 'assets/locked/' + f, 'rb').read())[:10] for f in os.listdir(OUT + 'assets/locked') if f.endswith('.webp')}
    else:
        pv = {} if fast else previews()
    write_index(pv)
    open(OUT + '_headers', 'w').write("""/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
/
  Cache-Control: no-cache
/index.html
  Cache-Control: no-cache
/data/*
  Cache-Control: public, max-age=31536000, immutable
/*.js
  Cache-Control: public, max-age=31536000, immutable
/*.css
  Cache-Control: public, max-age=31536000, immutable
/assets/*
  Cache-Control: public, max-age=31536000, immutable
/vendor/*
  Cache-Control: public, max-age=31536000, immutable
/p/*
  X-Robots-Tag: noindex
""")
    open(OUT + '404.html', 'w').write('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>wedge</title>
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/svg+xml" href="/favicon.svg"><meta name="robots" content="noindex">
<style>html,body{margin:0;height:100%;background:#151614;color:#e9e7e1;font:500 16px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}
main{min-height:100%;display:grid;place-items:center;text-align:center;padding:0 24px}h1{margin:0 0 8px;font-size:44px;letter-spacing:-.03em}h1 b{color:#7ED957}
p{margin:0 0 24px;color:#9a9890}a{display:inline-block;padding:12px 22px;border-radius:999px;background:#F6F7F8;color:#0D0F12;text-decoration:none;font-weight:700}</style></head>
<body><main><div><h1>wedge<b>.</b></h1><p>That page isn’t here.</p><a href="/">Back to Wedge</a></div></main></body></html>
''')
    open(OUT + 'robots.txt', 'w').write('User-agent: *\nDisallow: /p/\nDisallow: /api/\nAllow: /\n')
    size = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(OUT) for f in fs)
    print(f'site built: {len(used)} assets, {len(DS)} datasets ({tot / 1e6:.1f} MB of data), public record {len(pub_certs)} settled certified picks, '
          f'{len(pv)} previews, {size / 1e6:.1f} MB total')

if __name__ == '__main__':
    main()
