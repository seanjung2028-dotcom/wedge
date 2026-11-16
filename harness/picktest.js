const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, w] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +(w || 1300), height: 1000 } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message));
  await p.goto('file://' + file); await p.waitForTimeout(900);
  await p.click('#nfl-btn'); await p.click('#nfl-menu [data-page="lines"]'); await p.waitForTimeout(300);
  await p.selectOption('.rs-show', 'pick'); await p.waitForTimeout(300);
  console.log('picks', await p.textContent('.rl-count'));
  await p.evaluate(() => document.querySelector('.rs-show').scrollIntoView()); await p.waitForTimeout(200);
  await p.screenshot({ path: out + '_picks.png' });
  console.log('chips', await p.evaluate(() => { const c = {}; document.querySelectorAll('.wg-sit-edge').forEach((e) => { const k = e.className.split(' ').pop(); c[k] = (c[k] || 0) + 1; }); return c; }));
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
