const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, w] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +(w || 1300), height: 1100 } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message));
  await p.goto('file://' + file); await p.waitForTimeout(900);
  await p.click('.rs-tab[data-page="nba"]'); await p.waitForTimeout(800);
  await p.screenshot({ path: out + '_top.png' });
  await p.evaluate(() => document.querySelector('#nba-by-game').scrollIntoView()); await p.waitForTimeout(500);
  await p.screenshot({ path: out + '_bygame.png' });
  console.log(await p.evaluate(() => [document.querySelector('#nba-t-band').textContent, document.querySelector('#nba-t-q').textContent, document.querySelector('#nba-t-qn').textContent, document.querySelector('.nb-count').textContent]));
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
