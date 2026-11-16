const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 950 }, colorScheme: process.argv[3] || 'light' });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1500);
  console.log('reads', await p.$$eval('.wx-read', (x) => x.length), 'h1', await p.$eval('h1', (x) => x.textContent.trim()));
  await p.click('.wx-read'); await p.waitForTimeout(700);
  console.log('read outlook', await p.evaluate(() => { const d = document.querySelector('#sit-dlg'); return d && d.open ? d.querySelector('#sit-title').textContent : 'closed'; }));
  await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  const cta = await p.$('[data-wg-show]'); if (cta) { await cta.click(); await p.waitForTimeout(600); }
  console.log('after cta', await p.evaluate(() => { const v = [...document.querySelectorAll('[data-view]')].find((x) => !x.hidden && x.offsetParent); return v ? v.dataset.view : (document.querySelector('.rs-count') || {}).textContent; }));
  console.log('hscroll', await p.evaluate(() => document.documentElement.scrollWidth - innerWidth));
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
