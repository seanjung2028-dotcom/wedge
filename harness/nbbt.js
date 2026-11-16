const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, w] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +(w || 1300), height: 1000 } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message));
  await p.goto('file://' + file); await p.waitForTimeout(900);
  await p.click('.rs-tab[data-page="nba"]'); await p.waitForTimeout(300);
  await p.evaluate(() => document.querySelector('#nba-bt').scrollIntoView()); await p.waitForTimeout(1000);
  await p.screenshot({ path: out + '_1.png' });
  await p.evaluate(() => window.scrollBy(0, 900)); await p.waitForTimeout(500);
  await p.screenshot({ path: out + '_2.png' });
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
