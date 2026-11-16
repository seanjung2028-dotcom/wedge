(() => {
const num = (x) => (x === '' || x == null) ? null : Number(x);
const fmt = d3.format(',');
const $ = (s, root) => (root || document).querySelector(s);
const started = (r) => r.kickoff_utc && Date.parse(r.kickoff_utc) <= Date.now();
dash.calc('summary', {
title: 'Screen totals',
description: 'Counts of 45–55¢ lines, those whose condition hit in more than half of 2026 games, the unflagged subset, and 100% hits over 4+ games.',
inputs: ['lines'],
fn: (lines) => {
const q = lines.filter((r) => r.qualifies === 'Yes');
return [{
inband: lines.length,
qualifying: q.length,
clean: q.filter((r) => !r.flags).length,
perfect: q.filter((r) => Number(r.hit_rate) === 100 && Number(r.games) >= 4).length,
}];
},
});
dash.calc('by_game', {
title: 'Lines per game',
description: 'Per game: lines priced 45–55¢ and how many hit more than 50% in 2026.',
inputs: ['lines'],
fn: (lines) => {
const m = new Map();
for (const r of lines) {
const g = m.get(r.game) || { game: r.game, kickoff_utc: r.kickoff_utc, inband: 0, qualifying: 0 };
g.inband += 1; if (r.qualifies === 'Yes') g.qualifying += 1;
m.set(r.game, g);
}
return [...m.values()];
},
});
dash.calc('cat_counts', {
title: 'Props per category',
description: 'Per category: player props priced 45–55¢, and how many of them hit more than 50% in 2026.',
inputs: ['props'],
fn: (props) => ['1', '2', '3', '4', '-'].map((cat) => {
const rows = props.filter((r) => r.cat === cat);
return { cat, all: rows.length, qualifying: rows.filter((r) => r.qualifies === 'Yes').length };
}),
});
dash.calc('atd_summary', {
title: 'Anytime TD totals',
description: 'Anytime TD lines with a price, players with 3+ games who scored in more than half of them, and how many of those have an ATD score of 80 or more.',
inputs: ['atd'],
fn: (atd) => {
const q = atd.filter((r) => Number(r.games) >= 3 && Number(r.atd_rate) > 50);
return [{
lines: atd.filter((r) => r.yes_price !== '').length,
qualified: q.length,
strong: q.filter((r) => Number(r.score) >= 80).length,
}];
},
});
const NFL_PAGES = new Set(['lines', 'cat-1', 'cat-2', 'cat-3', 'cat-4', 'defense', 'atd', 'results', 'backtest']);
const METHOD_PAGES = new Set([...NFL_PAGES, 'charts']);
const PAGES = [...document.querySelectorAll('.rs-page')].map((p) => p.id);
const navBtns = [...document.querySelectorAll('.wg-nav [data-page]')];
const ddBtn = $('#nfl-btn'), ddMenu = $('#nfl-menu'), ddCur = $('.wg-dd-cur', ddBtn);
const ddItems = [...ddMenu.querySelectorAll('.wg-dd-item')];
const closeMenu = (focusBtn) => { ddMenu.hidden = true; ddBtn.setAttribute('aria-expanded', 'false'); if (focusBtn) ddBtn.focus(); };
const openMenu = (focusItem) => {
ddMenu.hidden = false; ddBtn.setAttribute('aria-expanded', 'true');
if (focusItem) (ddItems.find((i) => i.getAttribute('aria-current') === 'page') || ddItems[0]).focus();
};
ddBtn.addEventListener('click', (e) => { if (ddMenu.hidden) openMenu(e.detail === 0); else closeMenu(false); });
ddBtn.addEventListener('keydown', (e) => { if (e.key === 'ArrowDown') { e.preventDefault(); openMenu(true); } else if (e.key === 'Escape') closeMenu(false); });
ddMenu.addEventListener('keydown', (e) => {
const i = ddItems.indexOf(document.activeElement);
if (e.key === 'ArrowDown') { e.preventDefault(); ddItems[(i + 1) % ddItems.length].focus(); }
else if (e.key === 'ArrowUp') { e.preventDefault(); ddItems[(i - 1 + ddItems.length) % ddItems.length].focus(); }
else if (e.key === 'Home') { e.preventDefault(); ddItems[0].focus(); }
else if (e.key === 'End') { e.preventDefault(); ddItems[ddItems.length - 1].focus(); }
else if (e.key === 'Escape') { e.preventDefault(); closeMenu(true); }
else if (e.key === 'Tab') closeMenu(false);
});
document.addEventListener('click', (e) => { if (!ddMenu.hidden && !e.target.closest('#nfl-dd')) closeMenu(false); });
const showPage = (id) => {
if (!PAGES.includes(id)) return;
navBtns.forEach((b) => { if (b.dataset.page === id) b.setAttribute('aria-current', 'page'); else b.removeAttribute('aria-current'); });
if (NFL_PAGES.has(id)) ddBtn.setAttribute('aria-current', 'page'); else ddBtn.removeAttribute('aria-current');
const cur = ddItems.find((b) => b.dataset.page === id);
ddCur.textContent = cur ? cur.textContent : '';
closeMenu(false);
document.querySelectorAll('.rs-page').forEach((p) => { p.hidden = p.id !== id; });
$('#method').hidden = !METHOD_PAGES.has(id);
dash.setLink(id);
if (id === 'charts') requestAnimationFrame(() => drawCharts());
if (id === 'lobby') { const l = $('#lobby'); l.classList.remove('wg-play'); void l.offsetWidth; l.classList.add('wg-play'); }
};
navBtns.forEach((b) => b.addEventListener('click', () => showPage(b.dataset.page)));
document.querySelectorAll('[data-go]').forEach((b) => b.addEventListener('click', () => {
showPage(b.dataset.go);
const after = b.dataset.scrollAfter && document.getElementById(b.dataset.scrollAfter);
(after || $('#top')).scrollIntoView({ block: 'start', behavior: after ? 'smooth' : 'auto' });
}));
document.querySelectorAll('[data-scroll]').forEach((b) => b.addEventListener('click', () => {
const t = document.getElementById(b.dataset.scroll);
if (t) { t.scrollIntoView({ block: 'start', behavior: 'smooth' }); const f = t.querySelector('input'); if (f) setTimeout(() => f.focus({ preventScroll: true }), 400); }
}));
(() => {
const shine = $('.wg-hero-shine'), mask = 'url("' + $('.wg-hero-letters').src + '"), url("' + $('.wg-hero-tri').src + '")';
shine.style.webkitMaskImage = mask; shine.style.maskImage = mask;
})();
const WEDGER_EMAIL = 'seanjung2028@u.northwestern.edu';
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const wireMailForm = (root, subject, body) => {
const btn = $('.wg-submit', root), msg = $('.wg-form-msg', root), done = $('.wg-form-done', root), link = $('.wg-mailto', root);
$('.wg-addr', root).textContent = WEDGER_EMAIL;
btn.addEventListener('click', () => {
msg.textContent = '';
const fields = [...root.querySelectorAll('[data-f]')];
const groups = [...root.querySelectorAll('[data-group]')];
[...fields, ...groups].forEach((f) => f.removeAttribute('aria-invalid'));
const v = {};
for (const f of fields) v[f.dataset.f] = f.value.trim();
for (const g of groups) v[g.dataset.group] = [...g.querySelectorAll('input:checked')].map((c) => c.value);
const missing = fields.find((f) => f.required && !v[f.dataset.f]);
if (missing) { missing.setAttribute('aria-invalid', 'true'); missing.focus(); msg.textContent = 'Please fill in the required fields.'; return; }
const em = fields.find((f) => f.dataset.f === 'email');
if (em && !EMAIL_RE.test(v.email)) { em.setAttribute('aria-invalid', 'true'); em.focus(); msg.textContent = 'Please enter a valid email address.'; return; }
const emptyGroup = groups.find((g) => !v[g.dataset.group].length);
if (emptyGroup) { emptyGroup.setAttribute('aria-invalid', 'true'); msg.textContent = 'Please pick at least one sport.'; return; }
link.href = 'mailto:' + WEDGER_EMAIL + '?subject=' + encodeURIComponent(subject(v)) + '&body=' + encodeURIComponent(body(v));
done.hidden = false;
try { link.click(); } catch (e) { /* the link stays for the visitor to use */ }
});
};
wireMailForm($('#waitlist-form'), (v) => `Wedge Pro waitlist: ${v.first} ${v.last}`,
(v) => `Name: ${v.first} ${v.last}\nEmail: ${v.email}\n\nMessage:\n${v.message || '(none)'}\n\nSent from the Wedger waitlist form.`);
wireMailForm($('#apply-form'), (v) => `Wedger analyst application: ${v.first} ${v.last}`,
(v) => `Name: ${v.first} ${v.last}\nEmail: ${v.email}\nSports: ${v.sports.join(', ')}\nExperience: ${v.experience}\nTrack record or socials: ${v.links || '(none)'}\n\nHow I find an edge:\n${v.edge}\n\nAnything else:\n${v.message || '(none)'}\n\nSent from the Wedger analyst application.`);
const hash = location.hash.slice(1);
if (PAGES.includes(hash)) showPage(hash);
const pctCell = (tr, value) => {
const c = document.createElement('td'); c.className = 'rs-barcell';
const hr = num(value);
c.textContent = hr == null ? '—' : (hr % 1 ? hr.toFixed(1) : hr) + '%';
if (hr != null) {
const bar = document.createElement('div'); bar.className = 'rs-bar';
const fill = document.createElement('span'); fill.style.width = Math.max(0, Math.min(100, hr)) + '%';
fill.style.background = hr > 50 ? 'var(--wg-green)' : 'var(--cds-chart-muted)';
bar.append(fill, document.createElement('i')); c.appendChild(bar);
}
tr.appendChild(c);
};
const makeSorter = (state, numKeys) => (a, b) => {
const k = state.sortK; let x = a[k], y = b[k];
if (numKeys.has(k)) { x = num(x) ?? -1e9; y = num(y) ?? -1e9; }
else { x = String(x || ''); y = String(y || ''); }
if (x < y) return -1 * state.sortDir; if (x > y) return 1 * state.sortDir;
return (num(b.hit_rate ?? b.score) ?? 0) - (num(a.hit_rate ?? a.score) ?? 0) || (num(b.games) ?? 0) - (num(a.games) ?? 0);
};
const wireSort = (table, state, numKeys, redraw) => {
table.querySelectorAll('th button').forEach((b) => b.addEventListener('click', () => {
const k = b.dataset.k;
if (state.sortK === k) state.sortDir *= -1; else { state.sortK = k; state.sortDir = numKeys.has(k) && !/rank/.test(k) ? -1 : 1; }
redraw();
}));
};
const markSort = (table, state) => table.querySelectorAll('th').forEach((th) => {
const btn = th.querySelector('button'); if (!btn) return;
const k = btn.dataset.k;
th.setAttribute('aria-sort', k === state.sortK ? (state.sortDir > 0 ? 'ascending' : 'descending') : 'none');
});
const fillGames = (sel, rows, current) => {
if (!sel.options.length) {
const games = [...new Map(rows.map((r) => [r.game, r.kickoff_utc])).entries()]
.sort((a, b) => String(a[1]).localeCompare(String(b[1])) || a[0].localeCompare(b[0])).map((e) => e[0]);
sel.replaceChildren(new Option('All games', ''), ...games.map((g) => new Option(g, g)));
}
sel.value = current;
};
const srcCell = (tr, r) => {
const c = document.createElement('td'); c.className = 'rs-hide-narrow';
const book = r.source && r.source !== 'Robinhood';
const s = document.createElement('span'); s.className = 'wg-src' + (book ? ' wg-src-book' : '');
s.textContent = !book ? 'Robinhood' : (/Robinhood-style/.test(r.source_detail || '') ? 'Books · RH-style' : 'Sportsbook avg');
if (book) s.title = (r.source_detail || '') + (r.book_lines ? ' · ' + r.book_lines : '');
c.appendChild(s); tr.appendChild(c); return c;
};
const mkTd = (tr) => (text, cls) => { const c = document.createElement('td'); if (cls) c.className = cls; c.textContent = text; tr.appendChild(c); return c; };
const SIT_COL = { rec: [4], recyd: [5], rushyd: [6], rryd: [5, 6], passyd: [7], passtd: [8], int: [9], td: [10] };
const SIT_VOL = { rec: [13], recyd: [13], rushyd: [14], rryd: [13, 14], td: [13, 14], passyd: [15], passtd: [15], int: [15] };
const SIT_UNIT = { rec: 'rec', recyd: 'rec yds', rushyd: 'rush yds', rryd: 'rush + rec yds', passyd: 'pass yds', passtd: 'pass TDs', int: 'INTs', td: 'TDs' };
const SIT_WORD = { rec: 'receptions', recyd: 'receiving yards', rushyd: 'rushing yards', rryd: 'rushing + receiving yards', passyd: 'passing yards', passtd: 'passing TDs', int: 'interceptions', td: 'touchdowns' };
const SIT_VUNIT = { rec: 'targets', recyd: 'targets', rushyd: 'carries', rryd: 'touches', td: 'touches', passyd: 'attempts', passtd: 'attempts', int: 'attempts' };
const RH_SHORT = { 'Receiving Yards': 'rec yds', 'Rec Yards': 'rec yds', 'Rush Yards': 'rush yds', 'Pass Yards': 'pass yds', 'Pass TDs': 'pass TDs', 'Receptions': 'receptions', 'Rush+Receiving Yards': 'rush + rec yds', 'Interceptions': 'INTs' };
const rhLabel = (c) => { const m = /^(.*?): Over (\d+)\.5 (.+)$/.exec(c || ''); return m && RH_SHORT[m[3]] ? `${m[1]}: ${+m[2] + 1}+ ${RH_SHORT[m[3]]}` : c; };
const reduced = () => window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const pctR = (v) => (v == null ? '—' : Math.round(v) + '%');
const avg1 = (v) => (v == null ? '—' : (Math.round(v * 10) / 10).toFixed(1));
const fmtStat = (stat, v) => (v == null ? '—' : (['recyd', 'rushyd', 'rryd', 'passyd'].includes(stat) ? String(Math.round(v)) : avg1(v)));
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
const grow = (node, prop, value) => { if (reduced()) { node.style[prop] = value; return; } requestAnimationFrame(() => requestAnimationFrame(() => { node.style[prop] = value; })); };
const countUp = (node, to, fmtFn) => {
if (to == null) { node.textContent = '—'; return; }
if (reduced()) { node.textContent = fmtFn(to); return; }
const t0 = performance.now(), dur = 650;
const step = (t) => { const k = Math.min(1, (t - t0) / dur); node.textContent = fmtFn(to * (1 - Math.pow(1 - k, 3))); if (k < 1 && node.isConnected) requestAnimationFrame(step); };
node.textContent = fmtFn(0); requestAnimationFrame(step);
};
const totalStar = (cell, r) => {
const t = num(r.game_total);
if (t == null || t <= 49.5) return;
const s = el('span', 'wg-star', '★'); s.title = `Projected total ${t} points (Robinhood game-total market), above 49.5`;
s.setAttribute('aria-label', `Projected total ${t} points`); cell.appendChild(s);
};
let sitRows = null, sitIndex = new Map();
const sitCache = new Map();
const sitDetail = (key) => {
const d = dash.data('sit');
if (!key || d.status !== 'ok') return null;
if (sitRows !== d.data) { sitRows = d.data; sitCache.clear(); sitIndex = new Map(d.data.map((r) => [String(r.key), r])); }
if (!sitCache.has(key)) {
const row = sitIndex.get(String(key)); let v = null;
try { v = row ? (typeof row.detail === 'string' ? JSON.parse(row.detail) : row.detail) : null; } catch (e) { v = null; }
sitCache.set(key, v);
}
return sitCache.get(key);
};
function sitModel(det, stat, line, keep) {
const L = det.log;
const val = (i) => SIT_COL[stat].reduce((s, c) => s + (L[i][c] || 0), 0);
const vol = (i) => SIT_VOL[stat].reduce((s, c) => s + (L[i][c] || 0), 0);
const base = det.base.filter(keep);
if (base.length < 4) return null;
const v = base.map(vol).sort((x, y) => x - y);
const q1 = d3.quantileSorted(v, 1 / 3), q2 = d3.quantileSorted(v, 2 / 3);
let a = Math.ceil(q1 - 1e-9), b = Math.floor(q2 + 1e-9);
if (a > b) a = b = Math.floor((q1 + q2) / 2 + 0.5);
const tier = (i) => (vol(i) < a ? 0 : vol(i) > b ? 2 : 1);
const hit = (i) => val(i) > line;
const n = base.length, Pall = base.filter(hit).length / n;
const T = [0, 1, 2].map((t) => {
const ids = base.filter((i) => tier(i) === t), h = ids.filter(hit).length;
return { ids, n: ids.length, h, p: (h + 2 * Pall) / (ids.length + 2), m: ids.length ? d3.sum(ids, val) / ids.length : null, share: ids.length / n };
});
if (T.filter((t) => t.n).length < 2) return null;
const pools = det.sets.filter((s) => s.pool).map((s) => s.idx.filter(keep));
let W = [0, 0, 0];
if (pools.length) pools.forEach((ids) => { for (let t = 0; t < 3; t++) W[t] += (ids.filter((i) => tier(i) === t).length + 3 * T[t].share) / (ids.length + 3) / pools.length; });
else W = T.map((t) => t.share);
const live = [0, 1, 2].filter((t) => T[t].m != null);
const p = d3.sum([0, 1, 2], (t) => W[t] * T[t].p);
const proj = d3.sum(live, (t) => W[t] * T[t].m) / d3.sum(live, (t) => W[t]);
const unit = SIT_VUNIT[stat];
const labels = [`≤ ${a - 1} ${unit}`, a === b ? `${a} ${unit}` : `${a}–${b} ${unit}`, `${b + 1}+ ${unit}`];
return { a, b, T, W, p, proj, n, tier, vol, val, labels, unit };
}
const sitCell = (tr, r, ctx) => {
const c = document.createElement('td'); c.className = 'rs-barcell wg-sitcell';
const hr = num(r.sit_hit), price = num(r.yes_price);
if (hr == null || !r.sit_key) { c.textContent = '—'; c.classList.add('rs-sub'); tr.appendChild(c); return c; }
const b = el('button', 'wg-sitbtn'); b.type = 'button';
b.setAttribute('aria-haspopup', 'dialog');
const edge = price == null ? null : Math.round(hr - price);
b.setAttribute('aria-label', `Situational chance ${pctR(hr)}${edge == null ? '' : `, ${edge >= 0 ? '+' : ''}${edge} points vs price`}. Open the outlook for ${ctx.title}`);
const row1 = el('span', 'wg-sit-row1');
row1.append(el('b', null, pctR(hr)));
if (edge != null) row1.append(el('span', 'wg-sit-edge ' + (edge >= 2 ? 'up' : edge <= -2 ? 'down' : 'flat'), (edge > 0 ? '+' : '') + edge));
const go = el('span', 'wg-sit-go', 'Outlook ›'); go.setAttribute('aria-hidden', 'true'); row1.append(go);
const bar = el('div', 'rs-bar'); const fill = el('span');
fill.style.width = Math.max(0, Math.min(100, hr)) + '%';
fill.style.background = price != null && hr > price ? 'var(--wg-green)' : 'var(--cds-chart-muted)';
const tick = el('i'); if (price != null) tick.style.left = Math.max(0, Math.min(100, price)) + '%';
bar.append(fill, tick);
b.append(row1, bar);
const open = () => openSit(r, ctx, b);
b.addEventListener('click', (e) => { e.stopPropagation(); open(); });
tr.classList.add('wg-click');
tr.addEventListener('click', (e) => {
if (e.target.closest('input, button, a, select, label, textarea')) return;
if (window.getSelection && String(window.getSelection())) return;
open();
});
c.appendChild(b); tr.appendChild(c); return c;
};
const sitDlg = $('#sit-dlg');
const sit = { r: null, ctx: null, det: null, sel: null, role: false, stat: 'rec', line: 0, price: null, fresh: false };
let sitOpener = null;
const closeSit = () => {
if (!sitDlg.open || sitDlg.classList.contains('closing')) return;
if (reduced()) { sitDlg.close(); return; }
sitDlg.classList.add('closing');
setTimeout(() => { sitDlg.classList.remove('closing'); sitDlg.close(); }, 160);
};
sitDlg.querySelector('.wg-sd-close').addEventListener('click', closeSit);
sitDlg.addEventListener('click', (e) => { if (e.target === sitDlg) closeSit(); });
sitDlg.addEventListener('cancel', (e) => { e.preventDefault(); closeSit(); });
sitDlg.addEventListener('close', () => { hideTip($('#sit-log')); hideTip($('#sit-range')); if (sitOpener && sitOpener.isConnected) sitOpener.focus(); });
$('#sit-role').addEventListener('change', (e) => { sit.role = e.target.checked; sit.sel = null; sit.fresh = false; renderSit(); });
function openSit(r, ctx, opener) {
const det = sitDetail(r.sit_key);
if (!det) return;
Object.assign(sit, { r, ctx, det, sel: null, role: false, stat: r.sit_stat || 'rec', line: num(r.sit_line) ?? 0.5, price: num(r.yes_price), fresh: true });
$('#sit-role').checked = false;
$('#sit-more').open = false;
sitOpener = opener;
if (!sitDlg.open) { try { sitDlg.showModal(); } catch (e) { sitDlg.setAttribute('open', ''); } }
const body = $('.wg-sd-body', sitDlg);
body.scrollTop = 0;
body.classList.add('wg-anim');
setTimeout(() => body.classList.remove('wg-anim'), 1100);
renderSit();
}
function sitTools() {
const { det } = sit; const L = det.log;
const snaps26 = det.base.filter((i) => L[i][0] === 26 && L[i][3] != null).map((i) => L[i][3]);
const avg26 = snaps26.length ? d3.mean(snaps26) : null;
const roleMin = avg26 != null ? Math.round(0.75 * avg26) : null;
const keep = (i) => !sit.role || roleMin == null || (L[i][3] != null && L[i][3] >= roleMin);
return { L, avg26, roleMin, keep, F: (idx) => (idx || []).filter(keep) };
}
const sitSum = (det, stat, line, idx) => {
let h = 0, s = 0;
for (const i of idx) { const v = SIT_COL[stat].reduce((a, c) => a + (det.log[i][c] || 0), 0); s += v; if (v > line) h += 1; }
return { h, n: idx.length, avg: idx.length ? s / idx.length : null, p: idx.length ? 100 * h / idx.length : null };
};
function renderSit() {
const { det, ctx, stat, line, price, r } = sit;
const T0 = sitTools(); const { L, F } = T0;
const unit = SIT_UNIT[stat], isTd = stat === 'td';
const M = sitModel(det, stat, line, T0.keep);
sit.model = M;
const since = "'" + String(L[0][0]).padStart(2, '0');
const pool = det.sets.filter((s) => s.pool);
const pooledUnique = [...new Set(pool.flatMap((s) => F(s.idx)))].sort((x, y) => x - y);
if (!sit.sel) sit.sel = { id: 'pool', idx: pooledUnique, label: 'Games like this week' };
const cond = isTd ? 'score' : `clear ${rhLabel(`x: Over ${line} ${({ rec: 'Receptions', recyd: 'Receiving Yards', rushyd: 'Rush Yards', rryd: 'Rush+Receiving Yards', passyd: 'Pass Yards', passtd: 'Pass TDs', int: 'Interceptions' })[stat]}`).replace('x: ', '')}`;
$('#sit-kicker').textContent = `Situational outlook · ${det.team} ${det.pos}`;
$('#sit-title').textContent = ctx.title;
const sub = $('#sit-sub'); sub.replaceChildren();
const gs = el('span', null, ctx.game); totalStar(gs, r); sub.append(gs);
if (num(r.game_total) != null) sub.append(el('span', null, `Projected total ${r.game_total}`));
if (price != null) sub.append(el('span', null, `${price}¢ · ${ctx.source && ctx.source !== 'Robinhood' ? (/Robinhood-style/.test(r.source_detail || '') ? 'Robinhood-style, from the books' : 'sportsbook average') : 'Robinhood'}`));
sub.append(el('span', null, `${L.length} games for ${det.team} since ${since}`));
const roleBox = $('#sit-role'); roleBox.disabled = T0.roleMin == null;
$('#sit-role-lab').textContent = T0.roleMin == null ? 'Current role only (no 2026 snaps yet)' : `Current role only (${T0.roleMin}%+ of snaps)`;
const hero = $('#sit-hero'); hero.replaceChildren();
const p0 = M ? 100 * M.p : sitSum(det, stat, line, F(det.base)).p;
const p = p0 == null ? null : Math.round(p0 * 10) / 10;
const edge = p == null || price == null ? null : p - price;
const dir = edge == null ? '' : edge >= 2 ? 'up' : edge <= -2 ? 'down' : '';
const c1 = el('div', 'wg-hero-card'); c1.style.setProperty('--i', 0);
c1.append(el('div', 'wg-hero-lab', 'Chance it settles Yes'));
const r1 = el('div', 'wg-hero-row'); const n1 = el('span', 'wg-hero-num ' + dir); const n1v = el('span'); n1.append(n1v, el('small', 'pct', '%'));
r1.append(n1);
if (edge != null) r1.append(el('span', 'wg-chip ' + dir, `${edge >= 0 ? '+' : '−'}${Math.abs(Math.round(edge))} pts vs ${price}¢ price`));
const gauge = el('div', 'wg-gauge' + (dir === 'down' ? ' down' : '')); const gf = el('span'); const gi = el('i');
if (price != null) { gi.style.left = price + '%'; gi.dataset.l = `Price ${price}¢`; } else gi.hidden = true;
gauge.append(gf, gi);
c1.append(r1, gauge, el('p', 'wg-hero-note', M ? `Blends the bear, base and bull cases below, weighted for this week's situation. ${isTd ? 'Yes = 1+ rushing or receiving TD.' : `Yes = ${cond.replace('clear ', '')}.`}` : 'Too few games for cases; this is his hit rate in every game since ' + since + '.'));
hero.append(c1);
countUp(n1v, p, (x) => String(Math.round(x)));
grow(gf, 'width', Math.max(0, Math.min(100, p ?? 0)) + '%');
const c2 = el('div', 'wg-hero-card'); c2.style.setProperty('--i', 1);
c2.append(el('div', 'wg-hero-lab', isTd ? 'Projected touchdowns' : `Projected ${SIT_WORD[stat]}`));
const r2 = el('div', 'wg-hero-row'); const n2 = el('span', 'wg-hero-num'); const n2v = el('span'); n2.append(n2v, el('small', null, unit));
const proj = M ? M.proj : sitSum(det, stat, line, F(det.base)).avg;
r2.append(n2);
if (proj != null && !isTd) { const d = proj - line; const big = ['recyd', 'rushyd', 'rryd', 'passyd'].includes(stat) ? 2 : 0.2; r2.append(el('span', 'wg-chip ' + (d >= big ? 'up' : d <= -big ? 'down' : ''), `Line ${line} · ${Math.abs(d) < 0.05 ? 'even' : (d > 0 ? '+' : '−') + avg1(Math.abs(d))}`)); }
c2.append(r2);
countUp(n2v, proj, (x) => (isTd || ['rec', 'passtd', 'int'].includes(stat) ? (Math.round(x * 100) / 100).toFixed(stat === 'rec' ? 1 : 2) : String(Math.round(x))));
if (M) {
const ms = M.T.map((t) => t.m);
const lo = Math.min(...ms.filter((x) => x != null), line), hi = Math.max(...ms.filter((x) => x != null), line);
const pad = (hi - lo) * 0.12 || 1; const x0 = lo - pad, x1 = hi + pad;
const pos = (v) => (100 * (v - x0) / (x1 - x0)) + '%';
const rng = el('div', 'wg-rng'); rng.setAttribute('aria-hidden', 'true');
rng.append(el('div', 'wg-rng-track'));
const ln = el('div', 'wg-rng-line'); ln.style.left = pos(line); ln.title = `Line ${line}`; rng.append(ln);
['bear', 'base', 'bull'].forEach((k, t) => { if (M.T[t].m == null) return; const d = el('div', 'wg-rng-dot'); d.style.background = `var(--wg-${k})`; d.style.left = pos(line); d.title = `${k[0].toUpperCase() + k.slice(1)} case average ${fmtStat(stat, M.T[t].m)} ${unit}`; rng.append(d); grow(d, 'left', pos(M.T[t].m)); });
const pj = el('div', 'wg-rng-proj'); pj.style.left = pos(line); pj.title = `Projection ${fmtStat(stat, proj)} ${unit}`; rng.append(pj); grow(pj, 'left', pos(proj));
const lab = el('div', 'wg-rng-lab');
['Bear', 'Base', 'Bull'].forEach((k, t) => { const s = el('span', null, k + ' '); s.append(el('b', null, fmtStat(stat, M.T[t].m))); lab.append(s); });
const ls = el('span', null, 'Line '); ls.append(el('b', null, String(line))); lab.append(ls);
c2.append(rng, lab);
c2.append(el('p', 'wg-hero-note', `Dots are each case's average; the diamond is the projection (cases weighted by this week's odds); the dashed mark is the line.`));
}
hero.append(c2);
const odds = $('#sit-odds'), scen = $('#sit-scen'); odds.replaceChildren(); scen.replaceChildren();
$('#sit-scen-hint').textContent = M ? `His games since ${since}, split into thirds by ${M.unit}` : '';
odds.hidden = scen.hidden = !M;
if (M) {
odds.setAttribute('aria-label', `Case odds this week: bear ${pctR(100 * M.W[0])}, base ${pctR(100 * M.W[1])}, bull ${pctR(100 * M.W[2])}`);
['bear', 'base', 'bull'].forEach((k, t) => {
const seg = el('span', k, M.W[t] >= 0.12 ? `${k[0].toUpperCase() + k.slice(1)} ${pctR(100 * M.W[t])}` : '');
odds.append(seg); grow(seg, 'flexBasis', (100 * M.W[t]) + '%');
const T = M.T[t];
const card = el('div', 'wg-sc ' + k); card.style.setProperty('--i', t + 2);
const top = el('div', 'wg-sc-top'); top.append(el('span', 'wg-sc-tag', k + ' case'), el('span', 'wg-sc-vol', M.labels[t]));
const pr = el('div', 'wg-sc-p'); const pb = el('b'); pr.append(pb, el('span', null, isTd ? 'chance to score' : `to ${cond}`));
const met = el('div', 'wg-meter'); const mf = el('span'); const mi = el('i'); if (price != null) mi.style.left = price + '%'; else mi.hidden = true; met.append(mf, mi);
const dl = el('dl', 'wg-sc-stats');
[['Odds this week', pctR(100 * M.W[t])], ['Average', T.m == null ? '—' : `${fmtStat(stat, T.m)} ${isTd ? 'TDs' : unit}`], [isTd ? 'Scored' : 'Cleared', `${T.h} of ${T.n}`]].forEach(([a, b]) => { const d = el('div'); d.append(el('dt', null, a), el('dd', null, b)); dl.append(d); });
card.append(top, pr, met, dl);
scen.append(card);
countUp(pb, 100 * T.p, (x) => Math.round(x) + '%');
grow(mf, 'width', (100 * T.p) + '%');
});
}
drawSitRange();
const sp = $('#sit-splits'); sp.replaceChildren();
let k = 4;
const row = (label, small, idx, id, opts = {}) => {
const S = sitSum(det, stat, line, idx);
const b = el('button', 'wg-sp-row' + (opts.alt ? ' alt' : '')); b.type = 'button'; b.dataset.id = id;
b.setAttribute('aria-pressed', String(sit.sel.id === id)); if (!S.n) b.disabled = true;
const l = el('span', 'wg-sp-l'); const lb = el('b', null, label); if (opts.pill) lb.append(el('span', 'wg-pill', 'In model')); l.append(lb);
if (small) l.append(el('small', null, small));
const met = el('span', 'wg-meter'); met.style.setProperty('--c', S.p != null && price != null && S.p > price ? 'var(--wg-green)' : 'var(--cds-chart-muted)');
const mf = el('span'); const mi = el('i'); if (price != null) mi.style.left = price + '%'; else mi.hidden = true; met.append(mf, mi);
const v = el('span', 'wg-sp-v');
if (S.n) {
v.append(el('b', null, pctR(S.p)));
const sm = el('small', null, `${S.h} of ${S.n} · avg ${fmtStat(stat, S.avg)}`);
if (opts.vs) { const d = opts.vs.avg - S.avg; const dd = el('span', 'wg-sp-diff ' + (d >= 0 ? 'up' : 'down'), `Like this week: ${d >= 0 ? '+' : '−'}${fmtStat(stat, Math.abs(d))} per game`); sm.append(dd); }
v.append(sm);
} else v.append(el('small', null, 'no games'));
b.setAttribute('aria-label', `${label}: ${S.n ? `${isTd ? 'scored' : 'cleared'} in ${S.h} of ${S.n} games, ${pctR(S.p)}, average ${fmtStat(stat, S.avg)} ${unit}` : 'no games'}`);
b.append(l, met, v);
b.addEventListener('click', () => selectSit({ id, idx: [...new Set(idx)], label: opts.selLabel || label }));
grow(mf, 'width', (S.p ?? 0) + '%');
return { b, S };
};
const wrap = (...nodes) => { const w = el('div', 'wg-sp'); w.style.setProperty('--i', k++); w.append(...nodes); sp.append(w); return w; };
wrap(row('Games like this week', `Every game in a split marked In model (${pool.length} split${pool.length === 1 ? '' : 's'})`, pooledUnique, 'pool').b);
wrap(row(`Every game since ${since}`, `With ${det.team}; games he left early or was rested are left out`, F(det.base), 'all').b);
for (const s of det.sets) {
const main = row(s.label, s.now + (F(s.skipped || []).length ? ` · ${F(s.skipped).length} left out (${s.k === 'qb' ? 'the QB left hurt or split snaps' : 'that competitor left early hurt'})` : ''), F(s.idx), s.k, { pill: s.pool });
const nodes = [main.b];
if (s.alt) {
const alt = row(`vs ${s.alt.label.charAt(0).toLowerCase() + s.alt.label.slice(1)}`, null, F(s.alt.idx), s.k + '-alt',
{ alt: true, vs: main.S.n ? main.S : null, selLabel: s.k === 'comp' ? (s.label.startsWith('Without') ? s.label.replace(/^Without/, 'With') : s.label.replace(/^With/, 'Without')) : s.alt.label });
nodes.push(alt.b);
}
wrap(...nodes);
}
const more = $('#sit-moreb'); more.replaceChildren();
const comp = det.sets.find((s) => s.k === 'comp' && s.who && s.who.length);
if (comp) {
const box = el('div'); box.append(el('h4', null, 'No. 1 competitor by season'));
const t = el('table', 'wg-sd-who'); const hd = t.createTHead().insertRow();
['Season', 'Player', det.pos === 'RB' || det.pos === 'FB' ? 'Touches/g' : 'Targets/g', 'Share'].forEach((x, j) => { const th = el('th', j > 1 ? 'num' : null, x); hd.appendChild(th); });
const tb = t.createTBody();
comp.who.forEach((w) => { const tr = tb.insertRow(); [String(w.season), w.name, String(w.vol), w.share + '%'].forEach((x, j) => { const td = tr.insertCell(); td.textContent = x; if (j > 1) td.className = 'num'; }); });
box.append(t); more.append(box);
}
if (det.mates && det.mates.length) {
const box = el('div'); box.append(el('h4', null, 'With and without teammates'));
const list = el('div', 'wg-sd-splits');
for (const m of det.mates) {
const last = m.name.split(' ').slice(-1)[0];
const w = el('div', 'wg-sp');
w.append(row(`With ${m.name}`, m.now === 'out' ? 'Out this week' : 'Active this week', F(m.with), 'm-w-' + m.name).b);
if (F(m.missed).length) w.append(row(`${last} missed`, null, F(m.missed), 'm-x-' + m.name, { alt: true, selLabel: `Games ${m.name} missed` }).b);
if (F(m.off).length) w.append(row(`${last} not on the team`, null, F(m.off), 'm-o-' + m.name, { alt: true, selLabel: `Games before or after ${m.name}'s time on the team` }).b);
list.append(w);
}
box.append(list); more.append(box);
}
$('#sit-more').hidden = !more.childElementCount;
const gl = (i) => `'${String(L[i][0]).padStart(2, '0')} W${L[i][1]}`;
const ex = L.map((x, i) => [x, i]).filter(([x]) => x[12]);
$('#sit-foot').textContent = (M ? `How it works: his clean games since ${since} are split into thirds by ${M.unit}. Each case's chance is his hit rate in those games, nudged toward his overall rate; the case odds come from how this week's splits (marked In model) fall across the three, so a missing QB or teammate shifts the odds. ` : '')
+ (ex.length ? 'Left out everywhere: ' + ex.map(([x, i]) => `${gl(i)} vs ${x[2]} (${x[12] === 'r' ? 'rested' : 'left early hurt'}, ${x[3]}% of snaps)`).join('; ') + '. ' : '')
+ `Regular-season games with ${det.team} only, 2026 through Week 6 (nflverse).`;
drawSitLog(sit.fresh);
sit.fresh = false;
}
function selectSit(sel) {
sit.sel = sel;
sitDlg.querySelectorAll('.wg-sp-row').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.id === sel.id)));
drawSitLog(false);
}
function drawSitRange() {
const box = $('#sit-range'); const M = sit.model; const { det, stat, line } = sit;
const sec = box.closest('.wg-sd-sec'); sec.hidden = !M; if (!M) return;
const L = det.log, unit = SIT_UNIT[stat], isTd = stat === 'td';
const W = Math.max(300, Math.round(box.clientWidth || 640)), lane = 40, mt = 22, mb = 26, ml = 92, mr = 16;
const H = mt + lane * 3 + mb;
const svg = freshSvg(box, W, H);
svg.attr('aria-label', `${det.p}: ${SIT_WORD[stat]} in each past game, grouped into bear, base and bull cases by ${M.unit}, against the line of ${line}`);
const all = M.T.flatMap((t) => t.ids);
const vals = all.map(M.val);
const x = d3.scaleLinear().domain([Math.min(0, d3.min(vals)), Math.max(d3.max(vals), line) * 1.04]).nice().range([ml, W - mr]);
const g = svg.append('g');
x.ticks(W < 480 ? 4 : 7).forEach((t) => {
g.append('line').attr('x1', x(t)).attr('x2', x(t)).attr('y1', mt - 4).attr('y2', mt + lane * 3).style('stroke', 'var(--cds-chart-grid)');
g.append('text').attr('x', x(t)).attr('y', H - 8).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(t);
});
['bear', 'base', 'bull'].forEach((k, t) => {
const y0 = mt + lane * t;
if (t) g.append('line').attr('x1', ml).attr('x2', W - mr).attr('y1', y0).attr('y2', y0).style('stroke', 'var(--color-border-line)');
g.append('text').attr('x', 0).attr('y', y0 + lane / 2 - 3).style('font-size', '10.5px').style('font-weight', 600).style('letter-spacing', '.06em').style('fill', `var(--wg-${k})`).text(k.toUpperCase());
g.append('text').attr('x', 0).attr('y', y0 + lane / 2 + 10).style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(M.labels[t].replace(' attempts', ' att').replace(' targets', ' tgt').replace(' carries', ' car'));
if (M.T[t].m != null) {
g.append('line').attr('x1', x(M.T[t].m)).attr('x2', x(M.T[t].m)).attr('y1', y0 + 6).attr('y2', y0 + lane - 6).style('stroke', `var(--wg-${k})`).style('stroke-width', 3).style('stroke-linecap', 'round').style('opacity', 0.9)
.append('title').text(`${k} case average ${fmtStat(stat, M.T[t].m)} ${unit}`);
}
});
g.append('line').attr('x1', x(line)).attr('x2', x(line)).attr('y1', mt - 8).attr('y2', mt + lane * 3).style('stroke', 'var(--color-fg)').style('stroke-dasharray', '4 3').style('opacity', 0.7);
g.append('text').attr('x', x(line)).attr('y', mt - 11).attr('text-anchor', 'middle').style('font-size', '10px').style('font-weight', 600).style('fill', 'var(--color-fg)').text(isTd ? '1+ TD' : `Line ${line}`);
const gd = svg.append('g');
const anim = !reduced();
M.T.forEach((T, t) => T.ids.forEach((i, j) => {
const v = M.val(i), y = mt + lane * t + lane / 2 + (((i * 37) % 17) / 16 - 0.5) * (lane - 16);
const c = gd.append('circle').attr('cx', anim ? x(line) : x(v)).attr('cy', y).attr('r', 4.2)
.style('fill', v > line ? 'var(--wg-green)' : 'var(--cds-chart-muted)').style('stroke', 'var(--color-bg)').style('stroke-width', 1).style('opacity', anim ? 0 : 0.95)
.on('mousemove', (ev) => showTip(box, ev, [`'${String(L[i][0]).padStart(2, '0')} Week ${L[i][1]} vs ${L[i][2]}`, `${v} ${unit}${v > line ? (isTd ? ' · scored' : ' · over') : ''}`, `${M.vol(i)} ${M.unit}${L[i][3] != null ? ` · ${L[i][3]}% of snaps` : ''}`]))
.on('mouseleave', () => hideTip(box));
if (anim) c.transition().delay(120 + Math.min(420, j * 18 + t * 60)).duration(520).ease(d3.easeCubicOut).attr('cx', x(v)).style('opacity', 0.95);
}));
}
function drawSitLog(animate) {
const box = $('#sit-log');
const { det, stat, line } = sit; if (!det) return;
const T0 = sitTools(); const L = T0.L;
const unit = SIT_UNIT[stat], isTd = stat === 'td';
const val = (i) => SIT_COL[stat].reduce((s, c) => s + (L[i][c] || 0), 0);
const selSet = new Set(sit.sel.idx);
const S = sitSum(det, stat, line, [...selSet]);
$('#sit-lognote').textContent = `Green bars ${isTd ? 'scored' : `went over ${line}`}; outlined bars were left out (hurt early or rested). Lit up: ${sit.sel.label} — ${S.n ? `${S.n} game${S.n > 1 ? 's' : ''}, ${S.h} ${isTd ? 'with a TD' : 'over'} (${pctR(S.p)}), avg ${fmtStat(stat, S.avg)} ${unit}` : 'no games'}.`;
const W = Math.max(300, Math.round(box.clientWidth || 640)), H = 220;
const m = { l: 34, r: 50, t: 14, b: 38 };
const svg = freshSvg(box, W, H);
svg.attr('aria-label', `${det.p}: ${SIT_WORD[stat]} in each game for ${det.team}, against the line of ${line}. ${sit.sel.label}: ${S.h} of ${S.n} over.`);
const n = L.length;
const x = d3.scaleBand().domain(d3.range(n)).range([m.l, W - m.r]).paddingInner(n > 36 ? 0.16 : 0.26).paddingOuter(0.15);
const vals = L.map((_, i) => val(i));
const y = d3.scaleLinear().domain([Math.min(0, d3.min(vals)), Math.max(d3.max(vals) || 1, line) * 1.1]).nice().range([H - m.b, m.t]);
const g0 = svg.append('g');
for (const t of y.ticks(4)) {
g0.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(t)).attr('y2', y(t)).style('stroke', 'var(--cds-chart-grid)');
g0.append('text').attr('x', m.l - 6).attr('y', y(t)).attr('dy', '0.32em').attr('text-anchor', 'end').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(t);
}
const step = x.step();
d3.groups(d3.range(n), (i) => L[i][0]).forEach(([yy, ids], k) => {
const x0 = x(ids[0]), x1 = x(ids[ids.length - 1]) + x.bandwidth();
if (k > 0) g0.append('line').attr('x1', x0 - (step - x.bandwidth()) / 2).attr('x2', x0 - (step - x.bandwidth()) / 2).attr('y1', m.t - 6).attr('y2', H - m.b + 26).style('stroke', 'var(--color-border-line)');
g0.append('text').attr('x', (x0 + x1) / 2).attr('y', H - 6).attr('text-anchor', 'middle').style('font-size', '10px').style('font-weight', 600).style('fill', 'var(--color-fg-muted)').text(x1 - x0 > 26 ? '20' + String(yy).padStart(2, '0') : "'" + String(yy).padStart(2, '0'));
});
if (x.bandwidth() >= 11) L.forEach((r, i) => g0.append('text').attr('x', x(i) + x.bandwidth() / 2).attr('y', H - m.b + 13).attr('text-anchor', 'middle').style('font-size', '9px').style('fill', 'var(--color-fg-muted)').text(r[1]));
const gb = svg.append('g');
const anim = animate && !reduced();
L.forEach((r, i) => {
const v = vals[i], on = selSet.has(i), ex = !!r[12];
const h = Math.max(1.5, Math.abs(y(v) - y(0))), yTop = v >= 0 ? y(0) - h : y(0);
const rect = gb.append('rect').attr('class', 'bar').attr('x', x(i)).attr('width', x.bandwidth()).attr('rx', Math.min(2, x.bandwidth() / 4))
.attr('y', anim ? y(0) : yTop).attr('height', anim ? 0 : h);
if (ex) rect.style('fill', 'none').style('stroke', 'var(--color-fg-muted)').style('stroke-dasharray', '2 2').style('opacity', 0.8);
else rect.style('fill', v > line ? 'var(--wg-green)' : 'var(--cds-chart-muted)').style('opacity', on ? 1 : 0.16);
if (anim) rect.transition().delay(Math.min(500, i * 9)).duration(480).ease(d3.easeCubicOut).attr('y', yTop).attr('height', h);
});
const gl = svg.append('g');
gl.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(line)).attr('y2', y(line)).style('stroke', 'var(--color-fg)').style('stroke-width', 1.25).style('stroke-dasharray', '5 4').style('opacity', 0.75);
gl.append('text').attr('x', W - m.r + 6).attr('y', y(line)).attr('dy', '0.32em').attr('text-anchor', 'start').style('font-size', '10px').style('font-weight', 600).style('fill', 'var(--color-fg)').text(isTd ? '1+ TD' : `Line ${line}`);
const gh = svg.append('g');
L.forEach((r, i) => {
gh.append('rect').attr('x', x(i) - (step - x.bandwidth()) / 2).attr('y', m.t - 6).attr('width', step).attr('height', H - m.b - m.t + 8).style('fill', 'transparent')
.on('mousemove', (ev) => showTip(box, ev, [
`'${String(r[0]).padStart(2, '0')} Week ${r[1]} vs ${r[2]}`,
`${vals[i]} ${unit}${r[12] ? '' : (vals[i] > line ? (isTd ? ' · scored' : ' · over') : '')}`,
`${r[13] ?? 0} targets${r[14] ? ` · ${r[14]} carries` : ''}${r[15] ? ` · ${r[15]} att` : ''}${r[3] != null ? ` · ${r[3]}% of snaps` : ''}`,
r[11] != null ? `QB ${det.names[r[11]]}` : 'QB —',
...(r[12] ? [r[12] === 'r' ? 'Rested in the final week (left out)' : 'Left early hurt (left out)'] : []),
]))
.on('mouseleave', () => hideTip(box));
});
}
let sitResize = 0;
window.addEventListener('resize', () => { if (!sitDlg.open || !sit.det) return; cancelAnimationFrame(sitResize); sitResize = requestAnimationFrame(() => { drawSitRange(); drawSitLog(false); }); });
const CERT_WEEK = 'w7';
const certKey = (game, market, contract) => [CERT_WEEK, game, market, contract].join('|');
const keyOfLine = (r) => certKey(r.game, r.market, r.contract);
const keyOfAtd = (r) => certKey(r.game, 'Anytime Touchdown', r.player);
const keyOfResult = (r) => ['w' + (r.week || 6), r.game, r.group === 'ATD filter picks' ? 'Anytime Touchdown' : r.market, r.contract].join('|');
let certReady = false, certUnavailable = false;
let certs = new Set(), certOwner = false, certRef = null, certPending = 0, certQueue = Promise.resolve();
const certNote = (msg) => { const el = $('#certnote'); el.textContent = msg || ''; el.hidden = !msg; };
const redrawPicks = () => { drawLines(); catPages.forEach((draw) => draw()); drawAtd(); drawResults(); drawRecord(); drawProfit(); drawAnalysts(); };
const applyCertSnap = (snap) => {
if (certPending) return;
const picks = snap.exists ? snap.data().picks : null;
certs = new Set(Array.isArray(picks) ? picks.filter((k) => typeof k === 'string') : []);
certReady = true;
redrawPicks();
};
const setCert = (key, on) => {
if (!certRef || !certOwner) return;
const next = new Set(certs);
if (on) next.add(key); else next.delete(key);
certs = next;
redrawPicks();
const body = { picks: [...next].sort(), updated: new Date().toISOString() };
certPending += 1;
certQueue = certQueue.then(() => certRef.set(body)).then(() => certNote(''), () => {
certNote("Couldn't save that Wedger certification. Try again.");
}).finally(() => {
certPending -= 1;
if (!certPending) certRef.get().then(applyCertSnap, () => {});
});
};
const certCell = (tr, key, label) => {
const c = document.createElement('td'); c.className = 'wg-certcol';
if (certOwner) {
const box = document.createElement('input');
box.type = 'checkbox'; box.className = 'wg-certbox'; box.checked = certs.has(key);
box.setAttribute('aria-label', 'Wedger certify ' + label);
box.addEventListener('change', () => setCert(key, box.checked));
c.appendChild(box);
}
tr.appendChild(c);
if (certs.has(key)) tr.classList.add('wg-certified');
};
const certBadge = (cell, key) => {
if (!certs.has(key)) return;
const b = document.createElement('span'); b.className = 'wg-cert'; b.title = 'Wedger certified';
b.append(document.createElement('i'), 'Wedger');
cell.appendChild(b);
};
(async () => {
const cl = window.claude;
if (!cl || typeof cl.use !== 'function') { certUnavailable = true; drawRecord(); drawProfit(); drawAnalysts(); return; }
const [db, user] = await Promise.all([cl.use('db'), cl.use('user')]);
if (!db) { certUnavailable = true; drawRecord(); drawProfit(); drawAnalysts(); return; }
certRef = db.doc('wedger/certs');
certRef.onSnapshot(applyCertSnap, () => {});
anRef = db.doc('wedger/analysts');
anRef.onSnapshot(applyAnSnap, () => {});
if (user && await user.isOwner()) {
certOwner = true;
document.querySelector('.rs-wrap').classList.add('wg-owner');
redrawPicks();
}
})();
function drawRecord() {
const box = $('#wg-record');
const pctEl = $('.wg-record-pct', box), fracEl = $('.wg-record-frac', box), subEl = $('.wg-record-sub', box);
box.classList.remove('wg-up', 'wg-down');
const d = dash.data('results');
if (d.status !== 'ok' || !certReady) {
pctEl.textContent = '—'; fracEl.textContent = '';
subEl.textContent = d.status === 'error' ? 'Failed to load' : (certUnavailable ? 'Record unavailable in this view' : 'Certified picks, settled');
return;
}
const settled = new Map();
for (const r of d.data) { const k = keyOfResult(r); if (!settled.has(k) || r.group !== 'ATD filter picks') settled.set(k, r); }
let w = 0, n = 0, pending = 0;
const weeks = new Map();
for (const k of certs) {
const r = settled.get(k);
if (!r) { pending += 1; continue; }
if (r.outcome !== 'Won' && r.outcome !== 'Lost') continue;
const won = r.outcome === 'Won';
n += 1; if (won) w += 1;
const wk = Number(r.week || 6), e = weeks.get(wk) || { w: 0, n: 0 };
e.n += 1; if (won) e.w += 1; weeks.set(wk, e);
}
if (n) {
const p = Math.round(1000 * w / n) / 10;
pctEl.textContent = (p % 1 ? p.toFixed(1) : p) + '%';
fracEl.textContent = `(${w}/${n})`;
if (p > 50) box.classList.add('wg-up'); else if (p < 50) box.classList.add('wg-down');
} else { pctEl.textContent = '—'; fracEl.textContent = '(0/0)'; }
const parts = [...weeks.entries()].sort((a, b) => a[0] - b[0]).map(([wk, e]) => `Week ${wk}: ${e.w}/${e.n}`);
if (pending) parts.push(`${pending} pending`);
subEl.textContent = parts.length ? parts.join(' · ') : 'No certified picks settled yet';
}
function drawProfit() {
const el = $('#wg-profit');
const d = dash.data('results');
if (d.status !== 'ok' || !certReady) {
el.textContent = d.status === 'error' ? 'Failed to load'
: (certUnavailable ? 'Net profit on Wedger-certified picks is unavailable in this view.' : 'Net profit on Wedger-certified picks so far: —');
return;
}
const byKey = new Map();
for (const r of d.data) { const k = keyOfResult(r); if (!byKey.has(k) || r.group !== 'ATD filter picks') byKey.set(k, r); }
const settled = [...certs].map((k) => byKey.get(k)).filter((r) => r && (r.outcome === 'Won' || r.outcome === 'Lost'));
if (!settled.length) { el.textContent = 'Net profit on Wedger-certified picks: no certified picks have settled yet.'; return; }
const cost = settled.reduce((a, r) => a + Number(r.yes_price), 0);
const profit = settled.reduce((a, r) => a + Number(r.profit_c), 0);
const pct = Math.round(1000 * profit / cost) / 10;
const big = document.createElement('span');
big.className = 'wg-profit-pct' + (pct > 0 ? ' wg-pos' : (pct < 0 ? ' wg-neg' : ''));
big.textContent = (pct > 0 ? '+' : (pct < 0 ? '−' : '')) + Math.abs(pct).toFixed(1) + '%';
el.replaceChildren('Net profit on Wedger-certified picks so far: ', big);
}
const ANALYSTS_DEFAULT = ['Jason', 'Will', 'Chris', 'Sean'];
let analysts = { order: ANALYSTS_DEFAULT.slice(), picks: {} }, anRef = null, anReady = false, anPending = 0, anQueue = Promise.resolve();
const applyAnSnap = (snap) => {
if (anPending) return;
const d = snap.exists ? snap.data() : null;
const order = d && Array.isArray(d.order) ? d.order.filter((x) => typeof x === 'string' && x) : ANALYSTS_DEFAULT.slice();
const picks = {};
for (const n of order) { const p = d && d.picks ? d.picks[n] : null; picks[n] = Array.isArray(p) ? p.filter((k) => typeof k === 'string') : []; }
analysts = { order, picks };
anReady = true;
drawAnalysts();
};
const saveAnalysts = (next) => {
if (!anRef || !certOwner) return;
analysts = next;
drawAnalysts();
const body = { order: next.order, picks: next.picks, updated: new Date().toISOString() };
anPending += 1;
anQueue = anQueue.then(() => anRef.set(body)).then(() => certNote(''), () => {
certNote("Couldn't save that analyst pick. Try again.");
}).finally(() => {
anPending -= 1;
if (!anPending) anRef.get().then(applyAnSnap, () => {});
});
};
const pickIndex = () => {
const idx = new Map();
const put = (k, v) => { const cur = idx.get(k); if (!cur || (!cur.settled && v.settled)) idx.set(k, v); };
const L = dash.data('lines'), A = dash.data('atd'), R = dash.data('results');
if (L.status === 'ok') for (const r of L.data) put(keyOfLine(r), { week: 7, game: r.game, market: r.market, contract: r.contract, yes_price: r.yes_price, outcome: 'Pending', detail: '', profit_c: '', settled: false });
if (A.status === 'ok') for (const r of A.data) if (r.yes_price !== '' && r.yes_price != null) put(keyOfAtd(r), { week: 7, game: r.game, market: 'Anytime Touchdown', contract: r.player, yes_price: r.yes_price, outcome: 'Pending', detail: '', profit_c: '', settled: false });
if (R.status === 'ok') for (const r of R.data) {
const k = keyOfResult(r), cur = idx.get(k);
if (cur && cur.settled && r.group === 'ATD filter picks') continue;
idx.set(k, { week: Number(r.week || 6), game: r.game, market: r.group === 'ATD filter picks' ? 'Anytime Touchdown' : r.market, contract: r.contract, yes_price: r.yes_price, outcome: r.outcome, detail: r.week6_result, profit_c: r.profit_c, settled: r.outcome === 'Won' || r.outcome === 'Lost' });
}
return idx;
};
const pickInfo = (idx, k) => {
const hit = idx.get(k);
if (hit) return hit;
const [w, game, market, ...rest] = k.split('|');
return { week: Number(String(w).replace(/\D/g, '')) || '', game: game || '', market: market || '', contract: rest.join('|'), yes_price: '', outcome: 'Pending', detail: '', profit_c: '', settled: false };
};
const ans = { who: '', week: '', outcome: '', q: '', sortK: 'week', sortDir: -1 };
const ANNUM = new Set(['week', 'yes_price', 'profit_c']);
const anTable = $('#an-table');
const anWho = $('.an-who'), anFilter = $('.an-filter'), anWeek = $('.an-week'), anOut = $('.an-outcome'), anSearch = $('.an-search'), anPick = $('.an-pick'), anMsg = $('.an-msg');
anFilter.addEventListener('change', () => { ans.who = anFilter.value; drawAnalysts(); });
anWeek.addEventListener('change', () => { ans.week = anWeek.value; drawAnalysts(); });
anOut.addEventListener('change', () => { ans.outcome = anOut.value; drawAnalysts(); });
anSearch.addEventListener('input', () => { ans.q = anSearch.value.trim().toLowerCase(); drawAnalysts(); });
wireSort(anTable, ans, ANNUM, () => drawAnalysts());
let anLabels = new Map(), anOptCount = -1;
const pickLabel = (v) => `W${v.week} · ${v.game} · ${v.contract}${v.market && !v.contract.includes(':') ? ' (' + v.market + ')' : ''}${v.yes_price !== '' ? ' · ' + v.yes_price + '¢' : ''}`;
$('.an-addbtn').addEventListener('click', () => {
const who = anWho.value, key = anLabels.get(anPick.value);
if (!who) { anMsg.textContent = 'Choose an analyst.'; return; }
if (!key) { anMsg.textContent = 'Pick a line from the list.'; return; }
const cur = analysts.picks[who] || [];
if (cur.includes(key)) { anMsg.textContent = `Already in ${who}'s picks.`; return; }
saveAnalysts({ order: analysts.order, picks: { ...analysts.picks, [who]: [...cur, key] } });
anPick.value = ''; anMsg.textContent = `Added to ${who}.`;
});
const fillSel = (sel, items, first) => {
const want = (first ? [first] : []).concat(items.map((x) => [x, x]));
const sig = want.map((o) => o[0]).join('\u0001');
if (sel.dataset.sig === sig) return;
const cur = sel.value;
sel.replaceChildren(...want.map(([v, t]) => new Option(t, v)));
sel.dataset.sig = sig;
if (want.some((o) => o[0] === cur)) sel.value = cur;
};
function drawAnalysts() {
const board = $('#an-board'), tbody = $('tbody', anTable);
markSort(anTable, ans);
const R = dash.data('results');
if (R.status !== 'ok' || !anReady) {
board.replaceChildren(); tbody.replaceChildren();
$('.an-count').textContent = R.status === 'error' ? 'Failed to load' : (certUnavailable ? 'Analyst picks are unavailable in this view' : '');
return;
}
const idx = pickIndex();
const stats = analysts.order.map((name) => {
const keys = analysts.picks[name] || [];
const info = keys.map((k) => pickInfo(idx, k));
const settled = info.filter((v) => v.settled);
const wins = settled.filter((v) => v.outcome === 'Won').length;
const cost = settled.reduce((a, v) => a + Number(v.yes_price), 0);
const profit = settled.reduce((a, v) => a + Number(v.profit_c), 0);
const pending = info.filter((v) => v.outcome === 'Pending').length;
return { name, n: settled.length, wins, winPct: settled.length ? Math.round(1000 * wins / settled.length) / 10 : null,
profitPct: cost ? Math.round(1000 * profit / cost) / 10 : null, pending, total: keys.length };
});
const ranked = stats.slice().sort((a, b) => (b.winPct ?? -1) - (a.winPct ?? -1) || (b.profitPct ?? -1e9) - (a.profitPct ?? -1e9) || b.n - a.n);
const fmtPct = (p, signedPct) => (signedPct ? (p > 0 ? '+' : (p < 0 ? '−' : '')) : '') + (Math.abs(p) % 1 ? Math.abs(p).toFixed(1) : Math.abs(p)) + '%';
board.replaceChildren(...ranked.map((st, i) => {
const card = document.createElement('div'); card.className = 'wg-an' + (i === 0 && st.n ? ' wg-lead' : ''); card.dataset.key = st.name;
const head = document.createElement('div'); head.className = 'wg-an-head';
const av = document.createElement('span'); av.className = 'wg-an-av'; av.textContent = st.name.slice(0, 1).toUpperCase(); av.setAttribute('aria-hidden', 'true');
const nm = document.createElement('span'); nm.className = 'wg-an-name'; nm.textContent = st.name;
const rk = document.createElement('span'); rk.className = 'wg-an-rank'; rk.textContent = st.n ? '#' + (i + 1) : '—';
head.append(av, nm, rk);
const stat = (label, value, cls, small) => {
const d = document.createElement('div');
const l = document.createElement('div'); l.className = 'wg-an-lab'; l.textContent = label;
const v = document.createElement('div'); v.className = 'wg-an-val' + (cls ? ' ' + cls : ''); v.textContent = value;
if (small) { const sm = document.createElement('small'); sm.textContent = small; v.appendChild(sm); }
d.append(l, v); return d;
};
const grid = document.createElement('div'); grid.className = 'wg-an-stats';
grid.append(
stat('Win %', st.winPct == null ? '—' : fmtPct(st.winPct), st.winPct == null ? '' : (st.winPct > 50 ? 'wg-pos' : (st.winPct < 50 ? 'wg-neg' : '')), st.n ? `(${st.wins}/${st.n})` : ''),
stat('Net profit', st.profitPct == null ? '—' : fmtPct(st.profitPct, true), st.profitPct == null ? '' : (st.profitPct > 0 ? 'wg-pos' : (st.profitPct < 0 ? 'wg-neg' : ''))));
const foot = document.createElement('div'); foot.className = 'wg-an-foot';
foot.textContent = st.total ? `${st.n} settled · ${st.pending} pending` : 'No picks yet';
card.append(head, grid, foot);
return card;
}));
fillSel(anWho, analysts.order, null);
fillSel(anFilter, analysts.order, ['', 'All analysts']);
let rows = [];
for (const name of analysts.order) for (const k of analysts.picks[name] || []) {
const v = pickInfo(idx, k);
rows.push({ id: name + '|' + k, key: k, analyst: name, week: v.week, game: v.game, market: v.market, contract: v.contract, yes_price: v.yes_price, outcome: v.outcome, detail: v.detail, profit_c: v.profit_c });
}
fillSel(anWeek, [...new Set(rows.map((r) => String(r.week)).filter(Boolean))].sort((a, b) => b - a).map((w) => w), ['', 'All weeks']);
[...anWeek.options].forEach((o) => { if (o.value) o.textContent = 'Week ' + o.value; });
const v = rows.filter((r) => (!ans.who || r.analyst === ans.who) && (!ans.week || String(r.week) === ans.week) && (!ans.outcome || r.outcome === ans.outcome) &&
(!ans.q || (r.analyst + ' ' + r.game + ' ' + r.market + ' ' + r.contract).toLowerCase().includes(ans.q)))
.sort((a, b) => makeSorter(ans, ANNUM)(a, b) || a.analyst.localeCompare(b.analyst) || a.game.localeCompare(b.game));
const w = v.filter((r) => r.outcome === 'Won').length, l = v.filter((r) => r.outcome === 'Lost').length;
$('.an-count').textContent = `${fmt(v.length)} picks · ${w}–${l}`;
const frag = document.createDocumentFragment();
for (const r of v) {
const tr = document.createElement('tr'); tr.dataset.key = r.id;
const td = mkTd(tr);
td(r.analyst, 'rs-contract');
td(r.week, 'num rs-sub');
td(r.game, 'rs-sub');
td(r.market, 'rs-hide-narrow rs-sub');
certBadge(td(r.contract, 'rs-contract'), r.key);
td(r.yes_price === '' ? '—' : r.yes_price, 'num');
td(r.outcome, r.outcome === 'Won' ? 'an-won' : (r.outcome === 'Lost' ? 'an-lost' : 'an-pending'));
td(r.detail || '', 'rs-hide-narrow rs-results');
const pc = num(r.profit_c);
td(pc == null ? '—' : (pc > 0 ? '+' : '') + r.profit_c, 'num' + (pc > 0 ? ' rs-hi' : (pc == null ? ' rs-sub' : ' rs-sub')));
const ec = document.createElement('td'); ec.className = 'wg-certcol';
if (certOwner) {
const b = document.createElement('button'); b.type = 'button'; b.className = 'an-rm'; b.textContent = '×';
b.setAttribute('aria-label', `Remove ${r.contract} from ${r.analyst}'s picks`);
b.addEventListener('click', () => {
const cur = analysts.picks[r.analyst] || [];
saveAnalysts({ order: analysts.order, picks: { ...analysts.picks, [r.analyst]: cur.filter((k) => k !== r.key) } });
});
ec.appendChild(b);
}
tr.appendChild(ec);
frag.appendChild(tr);
}
tbody.replaceChildren(frag);
if (certOwner && idx.size !== anOptCount) {
anOptCount = idx.size;
anLabels = new Map();
const opts = [...idx.entries()].sort((a, b) => (b[1].week - a[1].week) || a[1].game.localeCompare(b[1].game) || a[1].contract.localeCompare(b[1].contract))
.map(([k, val]) => { const lab = pickLabel(val); anLabels.set(lab, k); const o = document.createElement('option'); o.value = lab; return o; });
$('#an-options').replaceChildren(...opts);
}
}
const FULL = new Set(['Moneyline', 'Spreads', 'Totals', 'Winning Margin', 'Overtime', '1st Half / Fulltime Result', 'Most Receiving Yards']);
const groupOf = (m) => FULL.has(m) ? (m === 'Most Receiving Yards' ? 'Player props' : 'Full game')
: (/Quarter|Half/.test(m) ? 'Quarters & halves' : 'Player props');
const ls = { show: 'q', game: '', group: '', src: '', clean: false, upcoming: false, certOnly: false, q: '', sortK: 'hit_rate', sortDir: -1 };
const LNUM = new Set(['yes_price', 'yes_bid', 'hit_rate', 'sit_hit', 'hits', 'games']);
const linesTable = $('#lines-table');
const showSel = $('.rs-show'), gameSel = $('.rs-game'), groupSel = $('.rs-group'), cleanBox = $('.rs-clean'), upBox = $('.rs-upcoming'), search = $('.rs-search');
showSel.addEventListener('change', () => { ls.show = showSel.value; drawLines(); });
gameSel.addEventListener('change', () => { ls.game = gameSel.value; drawLines(); });
groupSel.addEventListener('change', () => { ls.group = groupSel.value; drawLines(); });
$('.rs-src').addEventListener('change', (e) => { ls.src = e.target.value; drawLines(); });
cleanBox.addEventListener('change', () => { ls.clean = cleanBox.checked; drawLines(); });
upBox.addEventListener('change', () => { ls.upcoming = upBox.checked; drawLines(); });
search.addEventListener('input', () => { ls.q = search.value.trim().toLowerCase(); drawLines(); });
$('.rs-certonly').addEventListener('change', (e) => { ls.certOnly = e.target.checked; drawLines(); });
wireSort(linesTable, ls, LNUM, () => drawLines());
function drawLines() {
const d = dash.data('lines');
const tbody = $('tbody', linesTable);
markSort(linesTable, ls);
if (d.status !== 'ok') { tbody.replaceChildren(); $('.rl-count').textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
const rows = d.data;
fillGames(gameSel, rows, ls.game);
let v = rows.filter((r) =>
(ls.certOnly ? certs.has(keyOfLine(r)) : (ls.show === 'all' || r.qualifies === 'Yes')) &&
(!ls.game || r.game === ls.game) &&
(!ls.group || groupOf(r.market) === ls.group) &&
(!ls.src || (r.source || 'Robinhood') === ls.src) &&
(!ls.clean || !r.flags) &&
(!ls.upcoming || !started(r)) &&
(!ls.q || (r.game + ' ' + r.market + ' ' + r.contract + ' ' + r.sample).toLowerCase().includes(ls.q)));
v = v.slice().sort(makeSorter(ls, LNUM));
$('.rl-count').textContent = ls.certOnly ? fmt(v.length) + ' Wedger certified' : fmt(v.length) + ' of ' + fmt(rows.length) + ' lines';
const frag = document.createDocumentFragment();
for (const r of v) {
const tr = document.createElement('tr'); tr.dataset.key = r.id; if (started(r)) tr.className = 'rs-started';
const ck = keyOfLine(r);
certCell(tr, ck, r.game + ' ' + r.contract);
const td = mkTd(tr);
totalStar(td(r.game), r);
td(r.kickoff, 'rs-hide-narrow rs-sub');
td(r.market, 'rs-sub');
const lc = td(rhLabel(r.contract), 'rs-contract'); if (lc.textContent !== r.contract) lc.title = r.contract;
certBadge(lc, ck);
td(r.yes_price, 'num');
srcCell(tr, r);
td(r.yes_bid === '' ? '—' : r.yes_bid, 'num rs-hide-narrow rs-sub');
pctCell(tr, r.hit_rate);
sitCell(tr, r, { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source });
td(r.hits === '' ? '—' : r.hits, 'num');
td(r.games, 'num');
td(r.sample, 'rs-hide-narrow rs-sub');
td(r.season_results, 'rs-hide-narrow rs-results');
td(r.flags, 'rs-flag');
frag.appendChild(tr);
}
tbody.replaceChildren(frag);
}
const CNUM = new Set(['team_ml', 'opp_rank_vs_pos', 'yes_price', 'hit_rate', 'sit_hit', 'hits', 'games']);
const catPages = [...document.querySelectorAll('.rc-page')].map((page) => {
const st = { cat: page.dataset.cat, show: 'q', game: '', clean: false, upcoming: false, certOnly: false, q: '', sortK: 'hit_rate', sortDir: -1 };
const table = $('.rc-table', page);
const els = { show: $('.rc-show', page), game: $('.rc-game', page), clean: $('.rc-clean', page), upcoming: $('.rc-upcoming', page), certOnly: $('.rc-certonly', page), search: $('.rc-search', page), count: $('.rc-count', page) };
const draw = () => {
const d = dash.data('props');
const tbody = $('tbody', table);
markSort(table, st);
if (d.status !== 'ok') { tbody.replaceChildren(); els.count.textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
const rows = d.data.filter((r) => r.cat === st.cat);
fillGames(els.game, rows, st.game);
let v = rows.filter((r) =>
(st.certOnly ? certs.has(keyOfLine(r)) : (st.show === 'all' || r.qualifies === 'Yes')) &&
(!st.game || r.game === st.game) &&
(!st.clean || !r.flags) &&
(!st.upcoming || !started(r)) &&
(!st.q || (r.game + ' ' + r.team + ' ' + r.contract + ' ' + r.market + ' ' + r.pos).toLowerCase().includes(st.q)));
v = v.slice().sort(makeSorter(st, CNUM));
els.count.textContent = fmt(v.length) + (st.certOnly ? ' Wedger certified' : ' props');
const frag = document.createDocumentFragment();
for (const r of v) {
const tr = document.createElement('tr'); tr.dataset.key = r.id; if (started(r)) tr.className = 'rs-started';
const ck = keyOfLine(r);
certCell(tr, ck, r.game + ' ' + r.contract);
const td = mkTd(tr);
totalStar(td(r.game, 'rs-sub'), r);
td(r.kickoff, 'rs-hide-narrow rs-sub');
const lc = td(rhLabel(r.contract), 'rs-contract'); if (lc.textContent !== r.contract) lc.title = r.contract;
certBadge(lc, ck);
td(r.market, 'rs-hide-narrow rs-sub');
td(r.pos, 'rs-sub');
td(r.team);
td(r.team_ml, 'num rs-sub');
const rank = num(r.opp_rank_vs_pos);
td(rank == null ? '—' : r.opp_rank_vs_pos, 'num' + (rank != null && rank <= 10 ? ' rs-easy' : ' rs-sub'));
td(r.yes_price, 'num');
srcCell(tr, r);
pctCell(tr, r.hit_rate);
sitCell(tr, r, { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source });
td(r.hits === '' ? '—' : r.hits, 'num');
td(r.games, 'num');
td(r.season_results, 'rs-hide-narrow rs-results');
td(r.flags, 'rs-flag');
frag.appendChild(tr);
}
tbody.replaceChildren(frag);
};
els.show.addEventListener('change', () => { st.show = els.show.value; draw(); });
els.game.addEventListener('change', () => { st.game = els.game.value; draw(); });
els.clean.addEventListener('change', () => { st.clean = els.clean.checked; draw(); });
els.upcoming.addEventListener('change', () => { st.upcoming = els.upcoming.checked; draw(); });
els.certOnly.addEventListener('change', () => { st.certOnly = els.certOnly.checked; draw(); });
els.search.addEventListener('input', () => { st.q = els.search.value.trim().toLowerCase(); draw(); });
wireSort(table, st, CNUM, draw);
return draw;
});
const ds = { sortK: 'rb_rank', sortDir: 1 };
const DNUM = new Set(['games', 'rb_ppr_pg', 'rb_rank', 'rb_yds_pg', 'pc_ppr_pg', 'pc_rank', 'pc_yds_pg']);
const defTable = $('#defense-table');
wireSort(defTable, ds, DNUM, () => drawDefense());
function drawDefense() {
const d = dash.data('defense');
const tbody = $('tbody', defTable);
markSort(defTable, ds);
if (d.status !== 'ok') { tbody.replaceChildren(); return; }
const p = dash.data('lines');
const sunday = new Set(p.status === 'ok' ? p.data.flatMap((r) => r.game.split(' @ ')) : []);
const rows = d.data.slice().sort(makeSorter(ds, DNUM));
const frag = document.createDocumentFragment();
for (const r of rows) {
const tr = document.createElement('tr'); tr.dataset.key = r.team;
const td = mkTd(tr);
td(r.team, sunday.has(r.team) ? 'rs-contract' : 'rs-sub');
td(r.games, 'num rs-sub');
td(num(r.rb_ppr_pg).toFixed(1), 'num');
td(r.rb_rank, 'num' + (num(r.rb_rank) <= 10 ? ' rs-easy' : ''));
td(num(r.rb_yds_pg).toFixed(1), 'num rs-hide-narrow rs-sub');
td(num(r.pc_ppr_pg).toFixed(1), 'num');
td(r.pc_rank, 'num' + (num(r.pc_rank) <= 10 ? ' rs-easy' : ''));
td(num(r.pc_yds_pg).toFixed(1), 'num rs-hide-narrow rs-sub');
frag.appendChild(tr);
}
tbody.replaceChildren(frag);
}
const ATD_DEFAULTS = { atd_rate: 50, games: 3, rz_opp_share: 0, rz_opps_pg: 0, target_share: 0, rz_tgt_share: 0, td_pg: 0, score: 0, pmin: 0, pmax: 100, pos: '', game: '', upcoming: true, clean: false, certOnly: false, q: '' };
const as = Object.assign({ sortK: 'score', sortDir: -1 }, ATD_DEFAULTS);
const ANUM = new Set(['yes_price', 'atd_rate', 'sit_hit', 'atd_hits', 'games', 'td_pg', 'rz_opp_share', 'rz_opps_pg', 'target_share', 'rz_tgt_share', 'score', 'rate_minus_price']);
const PCTL = { atd_rate: 'atd_rate_pctl', td_pg: 'td_pg_pctl', rz_opp_share: 'rz_opp_share_pctl', target_share: 'target_share_pctl', rz_tgt_share: 'rz_tgt_share_pctl' };
const atdTable = $('#atd-table');
const aIns = [...document.querySelectorAll('.ra-in')];
const aPmin = $('.ra-pmin'), aPmax = $('.ra-pmax'), aPos = $('.ra-pos'), aGame = $('.ra-game'), aUp = $('.ra-upcoming'), aClean = $('.ra-clean'), aCert = $('.ra-certonly'), aSearch = $('.ra-search');
const syncInputs = () => {
aIns.forEach((el) => { el.value = as[el.dataset.k]; });
aPmin.value = as.pmin; aPmax.value = as.pmax; aPos.value = as.pos; aUp.checked = as.upcoming; aClean.checked = as.clean; aCert.checked = as.certOnly; aSearch.value = as.q;
};
const readNum = (el, fallback) => { const v = parseFloat(el.value); return Number.isFinite(v) ? v : fallback; };
aIns.forEach((el) => el.addEventListener('input', () => { as[el.dataset.k] = readNum(el, 0); drawAtd(); }));
aPmin.addEventListener('input', () => { as.pmin = readNum(aPmin, 0); drawAtd(); });
aPmax.addEventListener('input', () => { as.pmax = readNum(aPmax, 100); drawAtd(); });
aPos.addEventListener('change', () => { as.pos = aPos.value; drawAtd(); });
aGame.addEventListener('change', () => { as.game = aGame.value; drawAtd(); });
aUp.addEventListener('change', () => { as.upcoming = aUp.checked; drawAtd(); });
aClean.addEventListener('change', () => { as.clean = aClean.checked; drawAtd(); });
aCert.addEventListener('change', () => { as.certOnly = aCert.checked; drawAtd(); });
aSearch.addEventListener('input', () => { as.q = aSearch.value.trim().toLowerCase(); drawAtd(); });
$('.ra-reset').addEventListener('click', () => { Object.assign(as, ATD_DEFAULTS); syncInputs(); drawAtd(); });
wireSort(atdTable, as, ANUM, () => drawAtd());
syncInputs();
const passes = (r) => {
const n = (k) => num(r[k]) ?? 0;
if (as.certOnly) { if (!certs.has(keyOfAtd(r))) return false; }
else {
if (n('games') < as.games) return false;
if (as.atd_rate > 0 && !(n('atd_rate') > as.atd_rate)) return false;
for (const k of ['rz_opp_share', 'rz_opps_pg', 'target_share', 'rz_tgt_share', 'td_pg', 'score']) if (as[k] > 0 && n(k) < as[k]) return false;
const pr = num(r.yes_price);
if ((as.pmin > 0 || as.pmax < 100) && (pr == null || pr < as.pmin || pr > as.pmax)) return false;
}
if (as.pos && r.pos !== as.pos) return false;
if (as.game && r.game !== as.game) return false;
if (as.upcoming && started(r)) return false;
if (as.clean && r.flags) return false;
if (as.q && !(r.player + ' ' + r.team + ' ' + r.game).toLowerCase().includes(as.q)) return false;
return true;
};
function drawAtd() {
const d = dash.data('atd');
const tbody = $('tbody', atdTable);
markSort(atdTable, as);
if (d.status !== 'ok') { tbody.replaceChildren(); $('.ra-count').textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
const rows = d.data;
fillGames(aGame, rows, as.game);
const v = rows.filter(passes).sort(makeSorter(as, ANUM));
$('.ra-count').textContent = as.certOnly ? fmt(v.length) + ' Wedger certified' : fmt(v.length) + ' of ' + fmt(rows.length) + ' players pass';
const frag = document.createDocumentFragment();
for (const r of v) {
const tr = document.createElement('tr'); tr.dataset.key = r.id; if (started(r)) tr.className = 'rs-started';
const ck = keyOfAtd(r);
certCell(tr, ck, r.player + ' anytime TD');
const td = mkTd(tr);
const hi = (k) => { const p = num(r[PCTL[k]]); return p == null ? '' : (p >= 75 ? ' rs-hi' : (p <= 25 ? ' rs-sub' : '')); };
const pct = (k) => (r[k] === '' ? '—' : r[k] + '%');
certBadge(td(r.player, 'rs-contract'), ck);
td(r.pos, 'rs-sub');
td(r.team, 'rs-hide-narrow');
totalStar(td(r.game, 'rs-sub'), r);
td(r.kickoff, 'rs-hide-narrow rs-sub');
td(r.yes_price === '' ? '—' : r.yes_price, 'num');
srcCell(tr, r);
pctCell(tr, r.atd_rate);
if ((num(r.atd_rate_pctl) ?? 0) >= 75) tr.lastChild.classList.add('rs-hi');
sitCell(tr, r, { title: r.player + ': anytime TD', game: r.game, market: 'Anytime Touchdown', source: r.source });
td(r.atd_hits === '' ? '—' : r.atd_hits, 'num');
td(r.games, 'num');
td(r.td_pg === '' ? '—' : r.td_pg, 'num' + hi('td_pg'));
td(pct('rz_opp_share'), 'num' + hi('rz_opp_share'));
td(r.rz_opps_pg === '' ? '—' : r.rz_opps_pg, 'num rs-hide-narrow');
td(pct('target_share'), 'num' + hi('target_share'));
td(pct('rz_tgt_share'), 'num' + hi('rz_tgt_share'));
const sc = num(r.score);
td(sc == null ? '—' : r.score, 'num' + (sc != null && sc >= 80 ? ' rs-hi' : ''));
const gap = num(r.rate_minus_price);
td(gap == null ? '—' : (gap > 0 ? '+' : '') + r.rate_minus_price, 'num' + (gap == null ? ' rs-sub' : ''));
td(r.td_log, 'rs-hide-narrow rs-results');
td(r.flags, 'rs-flag');
frag.appendChild(tr);
}
tbody.replaceChildren(frag);
}
dash.calc('w6_summary', {
title: 'Week 6 record by group',
description: 'Wins, losses, win % and return (one Yes contract of each line bought at its screen price, fees excluded) for each group of Week 6 lines; voided lines left out.',
inputs: ['results'],
fn: (results) => {
const seg = (segment, label, keep) => {
const s = results.filter((r) => r.outcome !== 'Void' && keep(r));
const wins = s.filter((r) => r.outcome === 'Won').length;
const cost = s.reduce((a, r) => a + Number(r.yes_price), 0);
const profit = s.reduce((a, r) => a + Number(r.profit_c), 0);
return { segment, label, wins, losses: s.length - wins,
win_pct: s.length ? Math.round(1000 * wins / s.length) / 10 : null,
avg_price: s.length ? Math.round(10 * cost / s.length) / 10 : null,
roi_pct: cost ? Math.round(1000 * profit / cost) / 10 : null };
};
const L = (r) => r.group !== 'ATD filter picks' && r.group !== 'Other Wedger picks';
const Q = (r) => L(r) && r.qualifies === 'Yes';
return [
seg('screen', 'Hit >50% (the screen)', Q),
seg('rest', 'Rest of the 45–55¢ lines (hit 50% or less)', (r) => L(r) && r.qualifies === 'No'),
seg('all', 'All 45–55¢ lines', L),
seg('clean', 'Hit >50%, no flags', (r) => Q(r) && r.flagged === 'No'),
seg('full', 'Hit >50% · full-game lines', (r) => Q(r) && r.group === 'Full game'),
seg('periods', 'Hit >50% · quarter & half lines', (r) => Q(r) && r.group === 'Quarters & halves'),
seg('props', 'Hit >50% · player props', (r) => Q(r) && r.group === 'Player props'),
seg('b50', 'Hit just over 50–59% this season', (r) => L(r) && r.hit_bucket === 'Over 50–59%'),
seg('b60', 'Hit 60–74% this season', (r) => L(r) && r.hit_bucket === '60–74%'),
seg('b75', 'Hit 75–99% this season', (r) => L(r) && r.hit_bucket === '75–99%'),
seg('b100', 'Hit 100% this season', (r) => L(r) && r.hit_bucket === '100%'),
seg('cat1', 'Group 1 · RB on favorite (hit >50%)', (r) => Q(r) && r.cat === '1'),
seg('cat2', 'Group 2 · WR/TE on underdog (hit >50%)', (r) => Q(r) && r.cat === '2'),
seg('cat3', 'Group 3 · RB vs soft run D (hit >50%)', (r) => Q(r) && r.cat === '3'),
seg('cat4', 'Group 4 · WR/TE vs soft pass D (hit >50%)', (r) => Q(r) && r.cat === '4'),
seg('cats', 'Groups 1–4 combined (hit >50%)', (r) => Q(r) && ['1', '2', '3', '4'].includes(r.cat)),
seg('atd', 'Anytime TD filter picks (3+ games, scored in >50%)', (r) => r.group === 'ATD filter picks'),
];
},
});
const signed = (v) => (v == null || v === '' ? '—' : (Number(v) > 0 ? '+' : '') + v + '%');
const rsTable = $('#results-summary-table');
const rss = { sortK: '', sortDir: 1 };
const RSNUM = new Set(['wins', 'losses', 'win_pct', 'avg_price', 'roi_pct']);
wireSort(rsTable, rss, RSNUM, () => drawResultsSummary());
function drawResultsSummary() {
const d = dash.data('w6_summary');
const tbody = $('tbody', rsTable);
markSort(rsTable, rss);
if (d.status !== 'ok') { tbody.replaceChildren(); return; }
const rows = rss.sortK ? d.data.slice().sort(makeSorter(rss, RSNUM)) : d.data;
const frag = document.createDocumentFragment();
for (const r of rows) {
const tr = document.createElement('tr'); tr.dataset.key = r.segment;
const td = mkTd(tr);
td(r.label, r.segment === 'screen' ? 'rs-contract' : '');
td(r.wins, 'num'); td(r.losses, 'num');
pctCell(tr, r.win_pct);
td(r.avg_price == null ? '—' : r.avg_price, 'num rs-sub');
td(signed(r.roi_pct), 'num' + (Number(r.roi_pct) > 0 ? ' rs-hi' : ''));
frag.appendChild(tr);
}
tbody.replaceChildren(frag);
}
const rs = { show: 'q', outcome: '', game: '', certOnly: false, q: '', sortK: 'hit_rate', sortDir: -1 };
const RNUM = new Set(['yes_price', 'hit_rate', 'profit_c']);
const rTable = $('#results-table');
const rShow = $('.rr-show'), rOut = $('.rr-outcome'), rGame = $('.rr-game'), rSearch = $('.rr-search');
rShow.addEventListener('change', () => { rs.show = rShow.value; drawResults(); });
rOut.addEventListener('change', () => { rs.outcome = rOut.value; drawResults(); });
rGame.addEventListener('change', () => { rs.game = rGame.value; drawResults(); });
rSearch.addEventListener('input', () => { rs.q = rSearch.value.trim().toLowerCase(); drawResults(); });
$('.rr-certonly').addEventListener('change', (e) => { rs.certOnly = e.target.checked; drawResults(); });
wireSort(rTable, rs, RNUM, () => drawResults());
function drawResults() {
const d = dash.data('results');
const tbody = $('tbody', rTable);
markSort(rTable, rs);
if (d.status !== 'ok') { tbody.replaceChildren(); $('.rr-count').textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
const rows = d.data;
fillGames(rGame, rows, rs.game);
const lineKeys = new Set(rows.filter((r) => r.group !== 'ATD filter picks').map(keyOfResult));
const v = rows.filter((r) =>
(rs.certOnly ? certs.has(keyOfResult(r)) && (r.group !== 'ATD filter picks' || !lineKeys.has(keyOfResult(r)))
: (rs.show === 'atd' ? r.group === 'ATD filter picks' : r.group !== 'ATD filter picks' && r.group !== 'Other Wedger picks' && (rs.show === 'all' || r.qualifies === 'Yes'))) &&
(!rs.outcome || r.outcome === rs.outcome) &&
(!rs.game || r.game === rs.game) &&
(!rs.q || (r.game + ' ' + r.market + ' ' + r.contract).toLowerCase().includes(rs.q))).sort(makeSorter(rs, RNUM));
const w = v.filter((r) => r.outcome === 'Won').length, l = v.filter((r) => r.outcome === 'Lost').length;
$('.rr-count').textContent = `${fmt(v.length)} ${rs.certOnly ? 'Wedger certified' : 'lines'} · ${w}–${l}`;
const frag = document.createDocumentFragment();
for (const r of v) {
const tr = document.createElement('tr'); tr.dataset.key = r.id;
const ck = keyOfResult(r);
certCell(tr, ck, r.game + ' ' + r.contract);
const td = mkTd(tr);
td(r.game, 'rs-sub');
td(r.market, 'rs-hide-narrow rs-sub');
certBadge(td(r.contract, 'rs-contract'), ck);
td(r.yes_price, 'num');
pctCell(tr, r.hit_rate);
td(r.outcome, r.outcome === 'Won' ? 'rs-hi' : (r.outcome === 'Void' ? 'rs-sub' : ''));
td(r.week6_result, 'rs-hide-narrow rs-results');
const pc = Number(r.profit_c);
td((pc > 0 ? '+' : '') + r.profit_c, 'num' + (pc > 0 ? ' rs-hi' : (pc < 0 ? ' rs-sub' : '')));
frag.appendChild(tr);
}
tbody.replaceChildren(frag);
}
const BT_DIMS = ['market', 'side', 'venue', 'price_band', 'week', 'liquidity'];
const bt = { sortK: 'hit_pct', sortDir: -1, min: 5 };
const BTNUM = new Set(['n', 'wins', 'losses', 'hit_pct', 'avg_price', 'edge_pts', 'roi_pct']);
const btTable = $('#bt-perms-table');
const btDims = [...document.querySelectorAll('.bt-dim')];
btDims.forEach((el) => el.addEventListener('change', () => drawBtPerms()));
$('.bt-min').addEventListener('input', () => { const v = parseInt($('.bt-min').value, 10); bt.min = Number.isFinite(v) ? v : 1; drawBtPerms(); });
wireSort(btTable, bt, BTNUM, () => drawBtPerms());
function drawBtPerms() {
const d = dash.data('hist_perms');
const tbody = $('tbody', btTable);
const sel = BT_DIMS.filter((k) => btDims.find((el) => el.value === k).checked);
BT_DIMS.forEach((k) => btTable.querySelectorAll('.bt-c-' + k).forEach((el) => { el.style.display = sel.includes(k) ? '' : 'none'; }));
markSort(btTable, bt);
if (d.status !== 'ok') { tbody.replaceChildren(); $('.bt-count').textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
const grouping = sel.length ? sel.join('+') : 'all';
const all = d.data.filter((r) => r.grouping === grouping);
const v = all.filter((r) => Number(r.n) >= bt.min).sort(makeSorter(bt, BTNUM));
$('.bt-count').textContent = `${fmt(v.length)} of ${fmt(all.length)} groups shown`;
const frag = document.createDocumentFragment();
for (const r of v) {
const tr = document.createElement('tr'); tr.dataset.key = r.id;
const td = mkTd(tr);
BT_DIMS.forEach((k) => { const c = td(r[k] || 'All', 'bt-c-' + k); if (!sel.includes(k)) c.style.display = 'none'; });
td(r.n, 'num'); td(r.wins, 'num rs-sub'); td(r.losses, 'num rs-sub');
pctCell(tr, r.hit_pct);
td(r.avg_price, 'num rs-sub');
const e = Number(r.edge_pts);
td((e > 0 ? '+' : '') + r.edge_pts, 'num' + (e > 0 ? ' rs-hi' : ''));
td(signed(r.roi_pct), 'num' + (Number(r.roi_pct) > 0 ? ' rs-hi' : ' rs-sub'));
frag.appendChild(tr);
}
tbody.replaceChildren(frag);
}
const bl = { market: '', week: '', outcome: '', q: '', sortK: 'week', sortDir: 1 };
const BLNUM = new Set(['price_c', 'profit_c']);
const blTable = $('#bt-lines-table');
const blMarket = $('.bt-market'), blWeek = $('.bt-week'), blOut = $('.bt-outcome'), blSearch = $('.bt-search');
blMarket.addEventListener('change', () => { bl.market = blMarket.value; drawBtLines(); });
blWeek.addEventListener('change', () => { bl.week = blWeek.value; drawBtLines(); });
blOut.addEventListener('change', () => { bl.outcome = blOut.value; drawBtLines(); });
blSearch.addEventListener('input', () => { bl.q = blSearch.value.trim().toLowerCase(); drawBtLines(); });
wireSort(blTable, bl, BLNUM, () => drawBtLines());
function drawBtLines() {
const d = dash.data('hist_lines');
const tbody = $('tbody', blTable);
markSort(blTable, bl);
if (d.status !== 'ok') { tbody.replaceChildren(); $('.bt-lcount').textContent = d.status === 'error' ? 'Failed to load' : ''; return; }
const rows = d.data;
if (blMarket.options.length === 1) {
[...new Set(rows.map((r) => r.market))].sort().forEach((m) => blMarket.add(new Option(m, m)));
[...new Set(rows.map((r) => r.week))].sort().forEach((w) => blWeek.add(new Option(w, w)));
}
const v = rows.filter((r) => (!bl.market || r.market === bl.market) && (!bl.week || r.week === bl.week) &&
(!bl.outcome || r.outcome === bl.outcome) &&
(!bl.q || (r.game + ' ' + r.contract + ' ' + r.market + ' ' + r.team).toLowerCase().includes(bl.q))).sort(makeSorter(bl, BLNUM));
const w = v.filter((r) => r.outcome === 'Won').length, l = v.filter((r) => r.outcome === 'Lost').length;
$('.bt-lcount').textContent = `${fmt(v.length)} lines · ${w}–${l}`;
const frag = document.createDocumentFragment();
for (const r of v) {
const tr = document.createElement('tr'); tr.dataset.key = r.id;
const td = mkTd(tr);
td(r.week, 'rs-sub'); td(r.game, 'rs-sub'); td(r.market, 'rs-hide-narrow rs-sub');
td(r.contract, 'rs-contract'); td(r.price_c, 'num');
td(r.side, 'rs-hide-narrow rs-sub'); td(r.venue, 'rs-hide-narrow rs-sub'); td(r.liquidity, 'rs-hide-narrow rs-sub');
td(r.outcome, r.outcome === 'Won' ? 'rs-hi' : '');
td(r.final, 'rs-hide-narrow rs-results');
const pc = Number(r.profit_c);
td((pc > 0 ? '+' : '') + r.profit_c, 'num' + (pc > 0 ? ' rs-hi' : ' rs-sub'));
frag.appendChild(tr);
}
tbody.replaceChildren(frag);
}
const DIM_ORDER = ['market', 'side', 'venue', 'price_band', 'week', 'liquidity'];
const DIM_LABEL = { market: 'Market', side: 'Favorite / underdog', venue: 'Home / away', price_band: 'Price band', week: 'Week', liquidity: 'Liquidity' };
const VALUE_ORDER = {
side: ['Favorite', 'Underdog', "Pick'em", 'n/a'], venue: ['Home', 'Away', 'n/a'],
price_band: ['45–48¢', '49–51¢', '52–55¢'], week: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
liquidity: ['Under 1k contracts', '1k–50k contracts', '50k+ contracts'],
};
const showVal = (dim, v) => (v === 'n/a' ? (dim === 'side' || dim === 'venue' ? 'No side (totals)' : 'n/a') : v);
const pct1 = (v) => (Number(v) % 1 ? Number(v).toFixed(1) : String(Number(v))) + '%';
const tipOf = (box) => { let t = box.querySelector(':scope > .wg-tip'); if (!t) { t = document.createElement('div'); t.className = 'wg-tip'; box.appendChild(t); } return t; };
const showTip = (box, ev, lines) => {
const t = tipOf(box);
t.replaceChildren(...lines.map((l, i) => { const d = document.createElement('div'); if (i === 0) d.className = 't'; d.textContent = l; return d; }));
t.style.opacity = 1;
const br = box.getBoundingClientRect();
let x = ev.clientX - br.left + 14, y = ev.clientY - br.top + 14;
if (x + t.offsetWidth > br.width) x = Math.max(0, ev.clientX - br.left - t.offsetWidth - 14);
if (y + t.offsetHeight > br.height + 40) y = Math.max(0, ev.clientY - br.top - t.offsetHeight - 10);
t.style.left = x + 'px'; t.style.top = y + 'px';
};
const hideTip = (box) => { const t = box.querySelector(':scope > .wg-tip'); if (t) t.style.opacity = 0; };
const freshSvg = (box, W, H) => {
const old = box.querySelector(':scope > svg'); if (old) old.remove();
const svg = d3.create('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`).attr('height', H).attr('role', 'img');
box.prepend(svg.node());
return svg;
};
const measure = (svg, texts, size) => {
const g = svg.append('g').attr('opacity', 0);
let max = 0;
for (const t of texts) { const el = g.append('text').style('font-size', size).text(t); max = Math.max(max, el.node().getComputedTextLength()); }
g.remove();
return max;
};
const fitText = (sel, full, maxw) => {
if (sel.node().getComputedTextLength() <= maxw) return;
let t = shortVal(full); sel.text(t);
while (sel.node().getComputedTextLength() > maxw && t.length > 3) { t = t.slice(0, -1); sel.text(t.trimEnd() + '…'); }
};
const shortVal = (v) => String(v).replace(/^Week (\d)/, 'Wk $1').replace(' contracts', '').replace('No side (totals)', 'Totals').replace(/ \(hit >50%\)$/, '').replace('Hit >50% · ', '');
const emptyNote = (box, msg) => { const old = box.querySelector(':scope > svg'); if (old) old.remove(); box.style.minHeight = '60px'; let p = box.querySelector(':scope > .wg-empty'); if (!p) { p = document.createElement('p'); p.className = 'rs-note wg-empty'; box.appendChild(p); } p.textContent = msg; };
const clearEmpty = (box) => { const p = box.querySelector(':scope > .wg-empty'); if (p) p.remove(); };
function hbars(box, rows, o) {
clearEmpty(box);
const W = box.clientWidth; if (!W) return;
if (!rows.length) { emptyNote(box, o.empty || 'No groups meet the minimum size.'); return; }
const top = 20, bottom = 6, fs = 'var(--cds-font-size-caption)';
let svg = freshSvg(box, W, 10);
const bars = rows.filter((r) => !r.heading);
let lw = Math.min(W * 0.46, measure(svg, bars.map((r) => r.label), fs) + 12);
let rightW = Math.min(110, Math.max(70, measure(svg, bars.map((r) => r.right), fs) + 12));
const stacked = W - lw - rightW < Math.max(160, W * 0.4);
if (stacked) { lw = 0; rightW = 0; }
const rowH = stacked ? 44 : (o.rowH || 26);
const H = top + rows.length * rowH + bottom;
svg = freshSvg(box, W, H);
box.style.minHeight = H + 'px';
const x = d3.scaleLinear([0, 100], [lw + (stacked ? 1 : 0), W - rightW - (stacked ? 1 : 0)]);
const grid = svg.append('g');
for (const t of (stacked ? [0, 50, 100] : [0, 25, 50, 75, 100])) {
grid.append('line').attr('x1', x(t)).attr('x2', x(t)).attr('y1', top - 4).attr('y2', H - bottom)
.style('stroke', t === 50 ? 'var(--cds-chart-reference)' : 'var(--cds-chart-grid)').attr('stroke-width', 1)
.attr('stroke-dasharray', t === 50 ? '4 3' : null);
grid.append('text').attr('x', x(t)).attr('y', top - 8).attr('text-anchor', stacked ? (t === 0 ? 'start' : t === 100 ? 'end' : 'middle') : 'middle')
.style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(t + '%');
}
rows.forEach((r, i) => {
const y = top + i * rowH;
const bh = stacked ? 12 : Math.min(16, rowH - 10), cy = stacked ? y + rowH - bh / 2 - 5 : y + rowH / 2, ty = stacked ? y + 12 : cy;
if (r.heading) {
svg.append('text').attr('x', 0).attr('y', y + rowH - 7).style('font-size', '10px').style('letter-spacing', '.08em').style('font-weight', 600).style('fill', 'var(--color-fg-muted)').text(r.heading.toUpperCase());
return;
}
const g = svg.append('g');
const valT = g.append('text').attr('x', stacked ? W : W - rightW + 8).attr('y', ty).attr('dy', '0.35em').attr('text-anchor', stacked ? 'end' : 'start')
.style('font-size', fs).style('fill', 'var(--color-fg-muted)').style('font-variant-numeric', 'tabular-nums').text(r.right);
const lab = g.append('text').attr('x', stacked ? 0 : lw - 10).attr('y', ty).attr('dy', '0.35em').attr('text-anchor', stacked ? 'start' : 'end').style('font-size', fs).style('fill', 'var(--color-fg)').text(r.label);
fitText(lab, r.label, stacked ? W - valT.node().getComputedTextLength() - 18 : lw - 12);
g.append('rect').attr('x', x(0)).attr('y', cy - bh / 2).attr('width', Math.max(1, x(r.value) - x(0))).attr('height', bh).attr('rx', 3)
.style('fill', r.good ? 'var(--wg-green)' : 'var(--cds-chart-muted)');
if (r.price != null) g.append('line').attr('x1', x(r.price)).attr('x2', x(r.price)).attr('y1', cy - bh / 2 - 3).attr('y2', cy + bh / 2 + 3).style('stroke', 'var(--color-fg)').attr('stroke-width', 2).attr('stroke-linecap', 'round');
g.append('rect').attr('x', 0).attr('y', y).attr('width', W).attr('height', rowH).style('fill', 'transparent')
.on('mousemove', (ev) => { g.select('rect').style('opacity', 0.8); showTip(box, ev, r.tip); })
.on('mouseleave', () => { g.select('rect').style('opacity', 1); hideTip(box); });
});
}
const permRow = (r, label) => ({
label, value: Number(r.hit_pct), price: Number(r.avg_price), good: Number(r.hit_pct) > Number(r.avg_price),
right: `${pct1(r.hit_pct)} · ${r.wins}–${r.losses}`,
tip: [label, `Hit ${pct1(r.hit_pct)} (${r.wins}–${r.losses})`, `Avg price ${r.avg_price}¢ · edge ${Number(r.edge_pts) > 0 ? '+' : ''}${r.edge_pts} pts`, `Return ${signed(r.roi_pct)}`],
});
const valueRank = (dim, v, rowsForDim) => {
if (VALUE_ORDER[dim]) { const i = VALUE_ORDER[dim].indexOf(v); return i < 0 ? 99 : i; }
const r = rowsForDim.find((x) => x[dim] === v); return r ? -Number(r.n) : 0;
};
function drawFactorCharts(perms) {
document.querySelectorAll('#ch-factor-grid .wg-chart').forEach((box) => {
const dim = box.dataset.dim;
const rows = perms.filter((r) => r.grouping === dim).sort((a, b) => valueRank(dim, a[dim], perms.filter((x) => x.grouping === dim)) - valueRank(dim, b[dim], perms.filter((x) => x.grouping === dim)));
hbars(box, rows.map((r) => permRow(r, showVal(dim, r[dim]))), { rowH: 28 });
});
}
const chc = { min: 8 };
const chcDims = [...document.querySelectorAll('.chc-dim')];
chcDims.forEach((el) => el.addEventListener('change', () => drawCharts()));
$('.chc-min').addEventListener('input', () => { const v = parseInt($('.chc-min').value, 10); chc.min = Number.isFinite(v) ? v : 1; drawCharts(); });
function drawComboChart(perms) {
const box = $('#ch-combo-chart');
const sel = DIM_ORDER.filter((k) => chcDims.find((el) => el.value === k).checked);
const grouping = sel.length ? sel.join('+') : 'all';
const all = perms.filter((r) => r.grouping === grouping);
const rows = all.filter((r) => Number(r.n) >= chc.min).sort((a, b) => Number(b.hit_pct) - Number(a.hit_pct) || Number(b.n) - Number(a.n));
$('.chc-count').textContent = `${fmt(rows.length)} of ${fmt(all.length)} groups`;
hbars(box, rows.map((r) => permRow(r, sel.length ? sel.map((k) => showVal(k, r[k])).join(' · ') : 'All lines')), { rowH: 26, empty: 'No combination has that many lines; lower the minimum.' });
}
const chh = { row: 'market', col: 'week', min: 5 };
const chhRow = $('.chh-row'), chhCol = $('.chh-col');
for (const sel of [chhRow, chhCol]) DIM_ORDER.forEach((k) => sel.add(new Option(DIM_LABEL[k], k)));
chhRow.value = chh.row; chhCol.value = chh.col;
chhRow.addEventListener('change', () => { chh.row = chhRow.value; if (chh.row === chh.col) { chh.col = DIM_ORDER.find((k) => k !== chh.row); chhCol.value = chh.col; } drawCharts(); });
chhCol.addEventListener('change', () => { chh.col = chhCol.value; if (chh.row === chh.col) { chh.row = DIM_ORDER.find((k) => k !== chh.col); chhRow.value = chh.row; } drawCharts(); });
$('.chh-min').addEventListener('input', () => { const v = parseInt($('.chh-min').value, 10); chh.min = Number.isFinite(v) ? v : 1; drawCharts(); });
function drawHeatmap(perms) {
const box = $('#ch-heat-chart'); clearEmpty(box);
const W = box.clientWidth; if (!W) return;
const [d1, d2] = [chh.row, chh.col];
const grouping = DIM_ORDER.filter((k) => k === d1 || k === d2).join('+');
const cells = perms.filter((r) => r.grouping === grouping);
const single = (dim) => perms.filter((r) => r.grouping === dim);
const vals = (dim) => [...new Set(single(dim).map((r) => r[dim]))].sort((a, b) => valueRank(dim, a, single(dim)) - valueRank(dim, b, single(dim)));
const rv = vals(d1), cv = vals(d2);
const fs = 'var(--cds-font-size-caption)';
let svg = freshSvg(box, W, 10);
const lw = Math.min(W * 0.32, measure(svg, rv.map((v) => showVal(d1, v)), fs) + 14);
const top = 34, cellH = 44;
const cw = (W - lw) / Math.max(1, cv.length);
const H = top + rv.length * cellH + 4;
svg = freshSvg(box, W, H); box.style.minHeight = H + 'px';
cv.forEach((c, j) => {
const lab = showVal(d2, c);
const t = svg.append('text').attr('x', lw + cw * j + cw / 2).attr('y', top - 12).attr('text-anchor', 'middle').style('font-size', fs).style('fill', 'var(--color-fg-muted)').text(lab);
fitText(t, lab, cw - 6);
});
rv.forEach((rvv, i) => {
const rl = svg.append('text').attr('x', lw - 10).attr('y', top + i * cellH + cellH / 2).attr('dy', '0.35em').attr('text-anchor', 'end').style('font-size', fs).style('fill', 'var(--color-fg)').text(showVal(d1, rvv));
fitText(rl, showVal(d1, rvv), lw - 12);
cv.forEach((cvv, j) => {
const r = cells.find((x) => x[d1] === rvv && x[d2] === cvv);
const x0 = lw + cw * j + 2, y0 = top + i * cellH + 2, w = cw - 4, h = cellH - 4;
const g = svg.append('g');
let fill = 'var(--cds-chart-grid)';
const ok = r && Number(r.n) >= chh.min;
if (ok) {
const hp = Number(r.hit_pct), t = Math.max(-1, Math.min(1, (hp - 50) / 30));
fill = t >= 0 ? `color-mix(in srgb, var(--wg-green) ${Math.round(t * 80) + 10}%, var(--color-bg))` : `color-mix(in srgb, var(--cds-chart-status-critical) ${Math.round(-t * 65) + 10}%, var(--color-bg))`;
}
g.append('rect').attr('x', x0).attr('y', y0).attr('width', w).attr('height', h).attr('rx', 4).style('fill', fill);
if (r) {
g.append('text').attr('x', x0 + w / 2).attr('y', y0 + h / 2 - 3).attr('text-anchor', 'middle').style('font-size', fs).style('font-weight', ok ? 600 : 400).style('fill', ok ? 'var(--color-fg)' : 'var(--color-fg-muted)').text(ok ? pct1(r.hit_pct) : '—');
g.append('text').attr('x', x0 + w / 2).attr('y', y0 + h / 2 + 11).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(`${r.wins}–${r.losses}`);
g.on('mousemove', (ev) => showTip(box, ev, [`${showVal(d1, rvv)} · ${showVal(d2, cvv)}`, `Hit ${pct1(r.hit_pct)} (${r.wins}–${r.losses})`, `Avg price ${r.avg_price}¢ · edge ${Number(r.edge_pts) > 0 ? '+' : ''}${r.edge_pts} pts`, `Return ${signed(r.roi_pct)}`]))
.on('mouseleave', () => hideTip(box));
}
});
});
}
function drawW6Chart() {
const box = $('#ch-w6-chart');
const d = dash.data('w6_summary');
if (d.status !== 'ok') { const s = box.querySelector(':scope > svg'); if (s) s.remove(); return; }
const SECT = { screen: 'The screen', full: 'Hit >50%, by market', b50: 'All 45–55¢ lines, by 2026 hit rate', cat1: 'Your four prop groups', atd: 'Anytime TD' };
const rows = d.data.filter((r) => r.win_pct != null).flatMap((r) => [...(SECT[r.segment] ? [{ heading: SECT[r.segment] }] : []), {
label: r.label, value: Number(r.win_pct), price: Number(r.avg_price), good: Number(r.roi_pct) > 0,
right: `${pct1(r.win_pct)} · ${r.wins}–${r.losses}`,
tip: [r.label, `Won ${pct1(r.win_pct)} (${r.wins}–${r.losses})`, `Avg price ${r.avg_price}¢`, `Return ${signed(r.roi_pct)}`],
}]);
hbars(box, rows, { rowH: 26 });
}
const BOARD_GROUPS = ['Full game', 'Quarters & halves', 'Player props'];
function drawBoard() {
const box = $('#ch-board-chart'); clearEmpty(box);
const W = box.clientWidth; if (!W) return;
const d = dash.data('lines');
if (d.status !== 'ok') { const s = box.querySelector(':scope > svg'); if (s) s.remove(); return; }
const color = (g) => dash.colors[BOARD_GROUPS.indexOf(g) % dash.colors.length];
const key = $('.ch-board-key');
key.replaceChildren(...BOARD_GROUPS.map((g) => { const s = document.createElement('span'); const i = document.createElement('i'); i.style.background = color(g); s.append(i, g); return s; }),
(() => { const s = document.createElement('span'); const i = document.createElement('i'); i.className = 'line'; s.append(i, 'Break-even (hit rate = price)'); return s; })());
const pts = d.data.filter((r) => r.hit_rate !== '' && r.hit_rate != null);
const H = Math.min(420, Math.max(300, W * 0.5)), m = { t: 12, r: 16, b: 38, l: 52 };
const svg = freshSvg(box, W, H); box.style.minHeight = H + 'px';
const x = d3.scaleLinear([44.5, 55.5], [m.l, W - m.r]), y = d3.scaleLinear([0, 100], [H - m.b, m.t]);
for (const t of [0, 25, 50, 75, 100]) {
svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(t)).attr('y2', y(t)).style('stroke', 'var(--cds-chart-grid)');
svg.append('text').attr('x', m.l - 8).attr('y', y(t)).attr('dy', '0.35em').attr('text-anchor', 'end').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(t + '%');
}
for (let t = 45; t <= 55; t += (W < 500 ? 2 : 1)) svg.append('text').attr('x', x(t)).attr('y', H - m.b + 16).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text(t + '¢');
svg.append('text').attr('x', (m.l + W - m.r) / 2).attr('y', H - 4).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text('Yes price');
svg.append('text').attr('transform', `translate(10,${(m.t + H - m.b) / 2}) rotate(-90)`).attr('text-anchor', 'middle').style('font-size', '10px').style('fill', 'var(--color-fg-muted)').text('2026 hit rate');
svg.append('line').attr('x1', x(44.5)).attr('x2', x(55.5)).attr('y1', y(44.5)).attr('y2', y(55.5)).style('stroke', 'var(--cds-chart-reference)').attr('stroke-dasharray', '4 3');
const jitter = (s) => { let h = 0; for (const c of s) h = (h * 31 + c.charCodeAt(0)) >>> 0; return ((h % 1000) / 1000 - 0.5) * 0.6; };
for (const r of pts) {
const cx = x(Number(r.yes_price) + jitter(r.id)), cy = y(Number(r.hit_rate));
svg.append('circle').attr('cx', cx).attr('cy', cy).attr('r', 4.5).style('fill', color(groupOf(r.market))).style('fill-opacity', r.qualifies === 'Yes' ? 0.9 : 0.35)
.style('stroke', 'var(--color-bg)').attr('stroke-width', 1)
.on('mousemove', (ev) => showTip(box, ev, [r.game + ' · ' + r.market, r.contract, `Price ${r.yes_price}¢ · hit ${pct1(r.hit_rate)} (${r.hits}/${r.games})`]))
.on('mouseleave', () => hideTip(box));
}
}
function drawCharts() {
const page = $('#charts');
if (!page || page.hidden) return;
const p = dash.data('hist_perms');
if (p.status === 'ok') { drawFactorCharts(p.data); drawComboChart(p.data); drawHeatmap(p.data); }
else document.querySelectorAll('#ch-factor-grid .wg-chart, #ch-combo-chart, #ch-heat-chart').forEach((b) => { const s = b.querySelector(':scope > svg'); if (s) s.remove(); });
drawW6Chart();
drawBoard();
}
let chartResize = 0;
window.addEventListener('resize', () => { cancelAnimationFrame(chartResize); chartResize = requestAnimationFrame(drawCharts); });
dash.onData(() => {
const s = dash.data('summary'), cc = dash.data('cat_counts'), at = dash.data('atd_summary');
document.querySelectorAll('[data-source="summary"][data-field], [data-source="atd_summary"][data-field]').forEach((el) => {
const src = dash.data(el.dataset.source);
if (src.status === 'ok' && src.data[0]) { el.classList.remove('dash-skeleton'); el.textContent = fmt(src.data[0][el.dataset.field]); }
else el.textContent = '—';
});
document.querySelectorAll('[data-source="cat_counts"][data-field], [data-source="w6_summary"][data-field], [data-source="hist_perms"][data-field]').forEach((el) => {
const src = dash.data(el.dataset.source);
const where = [...new URLSearchParams(el.dataset.where).entries()];
const row = src.status === 'ok' ? src.data.find((r) => where.every(([k, v]) => String(r[k]) === v)) : null;
const v = row ? row[el.dataset.field] : null;
if (row && v != null) {
el.classList.remove('dash-skeleton');
el.textContent = el.dataset.fmt === 'pct' ? v + '%' : (el.dataset.fmt === 'signed' ? signed(v) : fmt(v));
} else el.textContent = '—';
});
const box = $('.rs-games');
const g = dash.data('by_game');
const ld = dash.data('lines');
const totals = new Map(ld.status === 'ok' ? ld.data.map((x) => [x.game, x.game_total]) : []);
if (g.status === 'ok') {
const rows = g.data.slice().sort((a, b) => String(a.kickoff_utc).localeCompare(String(b.kickoff_utc)) || a.game.localeCompare(b.game));
const max = d3.max(rows, (r) => r.inband) || 1;
box.replaceChildren(...rows.map((r) => {
const row = document.createElement('div'); row.className = 'rs-grow';
const name = document.createElement('div'); name.textContent = r.game; totalStar(name, { game_total: totals.get(r.game) });
const bar = document.createElement('div'); bar.className = 'rs-gbar';
const a = document.createElement('span'); a.style.width = (r.inband / max * 100) + '%'; a.style.background = 'var(--cds-chart-muted)';
const b = document.createElement('span'); b.style.width = (r.qualifying / max * 100) + '%'; b.style.background = 'var(--wg-green)';
bar.append(a, b);
const val = document.createElement('div'); val.style.textAlign = 'right'; val.textContent = `${r.qualifying} / ${r.inband}`;
row.append(name, bar, val);
return row;
}));
} else box.replaceChildren();
document.querySelectorAll('.rs-sw-a').forEach((e) => { e.style.background = 'var(--cds-chart-muted)'; });
document.querySelectorAll('.rs-sw-b').forEach((e) => { e.style.background = 'var(--wg-green)'; });
drawLines();
catPages.forEach((draw) => draw());
drawDefense();
drawAtd();
drawResultsSummary();
drawResults();
drawRecord();
drawProfit();
drawAnalysts();
drawBtPerms();
drawBtLines();
drawCharts();
});
})();
