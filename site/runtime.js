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

  // One versioned, compressed bundle: { ds: {id: csv text}, certs, analysts }. Shows progress while it downloads.
  var getBundle = function (u, onProgress) {
    return fetch(u).then(function (r) {
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
  window.WedgeRuntime = { boot: function (bundle, scripts) {
    var veil = document.getElementById('wz-boot'), msg = document.getElementById('wz-boot-msg') || veil, sub = document.getElementById('wz-boot-sub');
    var slow = setTimeout(function () { if (sub) sub.textContent = 'Still loading. This can take a moment on a slow connection.'; }, 8000);
    var fail = function (e) { console.error(e); clearTimeout(slow); if (msg) msg.textContent = 'Wedge couldn’t load this week’s card.'; if (sub) sub.innerHTML = 'Check your connection, then <a href="" style="color:inherit">reload the page</a>.'; };
    return getBundle(bundle, function (n) { if (sub && n > 150000) sub.textContent = (n / 1e6).toFixed(1) + ' MB loaded'; })
      .then(function (b) {
        store['wedger/certs'] = b.certs; store['wedger/analysts'] = b.analysts; resolveReady();
        IDS.forEach(function (id) { raw[id] = d3.csvParse(b.ds[id] || ''); });
        booted = true;
        return scripts.reduce(function (p, s) { return p.then(function () { return loadScript(s); }); }, Promise.resolve());
      })
      .then(function () { clearTimeout(slow); subs.forEach(function (f) { try { f(); } catch (e) { console.error(e); } }); if (veil) veil.remove(); })
      .catch(fail);
  } };
})();
