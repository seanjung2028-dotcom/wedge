const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, w, who] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: 950 } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message));
  await p.goto('file://' + file); await p.waitForTimeout(900);
  await p.click('#nfl-btn'); await p.click('#nfl-menu [data-page="lines"]'); await p.waitForTimeout(300);
  await p.selectOption('.rs-show', 'all'); await p.fill('.rs-search', who); await p.waitForTimeout(200);
  await p.evaluate(() => document.querySelector('#lines-table .wg-sitbtn').click()); await p.waitForTimeout(800);
  await p.evaluate(() => { const h = [...document.querySelectorAll('#sit-p-ov h3')].find((x) => x.textContent === 'His role'); if (h) h.scrollIntoView(); });
  await p.waitForTimeout(300); await p.screenshot({ path: out + '_ov.png' });
  await p.evaluate(() => document.querySelector('#sit-t-mu').click()); await p.waitForTimeout(400);
  await p.evaluate(() => { const h = [...document.querySelectorAll('#sit-p-mu h3')].find((x) => x.textContent.startsWith('Against')); if (h) h.scrollIntoView(); });
  await p.waitForTimeout(300); await p.screenshot({ path: out + '_mu.png' });
  console.log(JSON.stringify(logs)); await b.close();
})();
