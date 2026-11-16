// Monday checks: hero record, home tiles (final vs live), edge results, thesis lens
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, shots] = process.argv;
  const b = await chromium.launch(); const errs = [];
  const p = await b.newPage({ viewport: { width: 1300, height: 900 } });
  p.on('pageerror', (e) => errs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') errs.push('console: ' + m.text().split('\n')[0]); });
  await p.goto('file://' + file); await p.waitForTimeout(2500);
  const home = await p.evaluate(() => ({ wl: [...document.querySelectorAll('[data-wz="cert-wl"]')].map((x) => x.textContent), pct: (document.querySelector('[data-wz="cert-pct"]') || {}).textContent,
    net: [...document.querySelectorAll('[data-wz="cert-profit"]')].map((x) => x.textContent),
    tiles: [...document.querySelectorAll('#v2-mgrid .v2-mt')].slice(0, 4).map((x) => x.innerText.replace(/\s+/g, ' ')) }));
  console.log('HOME', JSON.stringify(home));
  await p.click('#v2-mgrid .v2-mt[data-game="SF @ DAL"]'); await p.waitForTimeout(600);
  console.log('READS', await p.evaluate(() => [document.querySelector('#wx-reads-sub').textContent, [...document.querySelectorAll('#wg-hot-cards .v2-res')].map((x) => x.textContent)]));
  const p2 = await b.newPage({ viewport: { width: 1300, height: 900 } }); p2.on('pageerror', (e) => errs.push(e.message)); await p2.goto('file://' + file + '#final'); await p2.waitForTimeout(2500);
  console.log('EDGE', JSON.stringify(await p2.evaluate(() => ({ when: document.querySelector('#fc-when') && document.querySelector('#fc-when').textContent, stats: [...document.querySelectorAll('.fc-stat')].map((x) => x.innerText.replace(/\s+/g, ' ')),
    res: document.querySelectorAll('#fc-root .v2-res').length, firstRows: [...document.querySelectorAll('.fc-board tbody tr')].slice(0, 5).map((x) => x.innerText.replace(/\s+/g, ' ').slice(0, 120)),
    games: [...document.querySelectorAll('.fc-sum')].slice(0, 3).map((x) => x.innerText.replace(/\s+/g, ' ')), lens: document.querySelectorAll('#fc-root .v2-ledger').length }))));
  if (shots) { await p2.screenshot({ path: shots + '/edge_top.png', fullPage: false }); const g1 = await p2.$('.fc-game'); if (g1) { await p2.evaluate(() => { const d = document.querySelector('.fc-game'); d.open = true; }); await p2.waitForTimeout(300); const pl = await p2.$('.fc-game .fc-play'); if (pl) await pl.screenshot({ path: shots + '/edge_play.png' }); } }
  const p3 = await b.newPage({ viewport: { width: 1300, height: 900 } }); p3.on('pageerror', (e) => errs.push(e.message)); await p3.goto('file://' + file + '#thesis'); await p3.waitForTimeout(2500);
  console.log('THESIS', JSON.stringify(await p3.evaluate(() => ({ when: document.querySelector('#v2-th-when').textContent, sel: (document.querySelector('#v2-th-tabs [aria-selected="true"]') || {}).textContent,
    secs: [...document.querySelectorAll('.v2-th-h h3')].map((x) => x.textContent), lensTables: document.querySelectorAll('.v2-lens .rs-table').length, ledgers: document.querySelectorAll('.v2-th .v2-ledger').length,
    overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth }))));
  if (shots) {
    const L = await p3.$('.v2-lens'); if (L) await L.screenshot({ path: shots + '/lens.png' });
    const P2 = await p3.$('.v2-th-play'); if (P2) await P2.screenshot({ path: shots + '/thplay.png' });
  }
  const m = await b.newPage({ viewport: { width: 390, height: 844 } }); m.on('pageerror', (e) => errs.push('m ' + e.message));
  await m.goto('file://' + file + '#thesis'); await m.waitForTimeout(2500);
  console.log('MOBILE', JSON.stringify(await m.evaluate(() => ({ overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth, lens: !!document.querySelector('.v2-lens') }))));
  if (shots) { const L = await m.$('.v2-lens-side'); if (L) await L.screenshot({ path: shots + '/lens_m.png' }); }
  console.log(errs.length ? 'ERRORS ' + errs.join(' | ') : 'no errors');
  await b.close();
})();
