const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, outDir] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 950 } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message));
  await p.goto('file://' + file); await p.waitForTimeout(900);
  console.log('record', await p.evaluate(() => document.querySelector('#wg-record').innerText.replace(/\s+/g, ' ')));
  await p.click('#nfl-btn'); await p.click('#nfl-menu [data-page="lines"]'); await p.waitForTimeout(200);
  await p.check('.rs-certonly'); await p.waitForTimeout(200);
  console.log(await p.textContent('.rl-count'));
  console.log(await p.evaluate(() => [...document.querySelectorAll('#lines-table tbody tr')].map((tr) => tr.innerText.replace(/\s+/g, ' ').slice(0, 220))));
  await p.screenshot({ path: outDir + '/certonly.png' });
  // open Walker kept row
  const rows = await p.$$('#lines-table tbody tr'); for (const r of rows) if ((await r.innerText()).includes('Walker')) { await (await r.$('.wg-sitbtn')).click(); break; }
  await p.waitForTimeout(300);
  console.log('walker', await p.evaluate(() => [...document.querySelectorAll('#sit-tiles .rs-card')].map((c) => c.innerText.replace(/\s+/g, ' '))), await p.evaluate(() => [...document.querySelectorAll('#sit-cards .wg-sd-card h4')].map((c) => c.innerText)));
  await p.screenshot({ path: outDir + '/walker.png' });
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
