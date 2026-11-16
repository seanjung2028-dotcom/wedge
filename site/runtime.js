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
