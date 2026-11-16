const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, scheme] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 950 }, colorScheme: scheme || 'light' });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(1500);
  await p.click('#nfl-btn'); await p.click('#nfl-menu [data-page="lines"]'); await p.waitForTimeout(400);
  console.log('default', await p.textContent('.rl-count'));
  const t0 = Date.now(); await p.selectOption('.rs-show', 'every'); await p.waitForTimeout(200);
  console.log('every', await p.textContent('.rl-count'), 'ms', Date.now() - t0, 'rows', await p.$$eval('#lines-table tbody tr', (x) => x.length), 'static', await p.$$eval('.wg-sitstatic', (x) => x.length), 'more hidden', await p.$eval('.rl-more', (e) => e.hidden), 'px hidden', await p.$eval('.rs-px', (e) => e.hidden), 'note hidden', await p.$eval('.rl-every-note', (e) => e.hidden));
  await p.click('.rl-more'); await p.waitForTimeout(200); console.log('more', await p.textContent('.rl-count'));
  await p.selectOption('.rs-px', '0-10'); await p.waitForTimeout(150); console.log('<=10', await p.textContent('.rl-count'));
  await p.selectOption('.rs-px', '90-100'); await p.waitForTimeout(150); console.log('>=90', await p.textContent('.rl-count'));
  await p.selectOption('.rs-px', ''); await p.fill('.rs-search', 'derrick henry'); await p.waitForTimeout(200); console.log('henry', await p.textContent('.rl-count'));
  await p.screenshot({ path: out });
  await p.selectOption('.rs-show', 'pick'); await p.waitForTimeout(150); console.log('pick', await p.textContent('.rl-count'), 'px hidden', await p.$eval('.rs-px', (e) => e.hidden));
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
