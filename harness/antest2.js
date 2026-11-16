const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 950 } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message));
  await p.goto('file://' + file); await p.waitForTimeout(1500);
  console.log('record', await p.evaluate(() => document.querySelector('#wg-record').innerText.replace(/\s+/g, ' ')));
  await p.click('.rs-tab[data-page="analysts"]'); await p.waitForTimeout(600);
  console.log('board', await p.evaluate(() => document.querySelector('#an-board').innerText.replace(/\s+/g, ' ').slice(0, 600)));
  console.log('kw', await p.evaluate(() => [...document.querySelectorAll('#an-table tbody tr')].map((tr) => tr.innerText.replace(/\s+/g, ' ')).filter((t) => /Kyle Williams|NE @ CHI/.test(t)).slice(0, 14)));
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
