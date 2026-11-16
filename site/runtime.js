/* Wedge standalone runtime: stands in for the dashboard runtime and the shared store (read-only). */
(function () {
  'use strict';
  var IDS = ["lines", "lines_all", "props", "defense", "atd", "results", "hist_perms", "hist_lines", "sit", "outlook", "nflctx", "nba_lines", "nba_sit", "nba_outlook", "nba_ctx", "pick_prices", "nba_results", "proj", "bt_weeks", "bt_props", "mom_summary", "team_mom", "defhist", "cats", "research", "inj"];
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
