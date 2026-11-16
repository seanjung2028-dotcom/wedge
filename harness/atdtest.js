const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1300, height: 900 } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message));
  await p.goto('file://' + file); await p.waitForTimeout(600);
  await p.click('#tab-atd'); await p.waitForTimeout(100);
  await p.check('.ra-certonly'); await p.waitForTimeout(100);
  console.log(await p.textContent('.ra-count'), await p.evaluate(() => ({ badges: document.querySelectorAll('#atd-table .wg-cert').length, boxes: document.querySelectorAll('#atd-table .wg-certbox:checked').length })));
  await p.uncheck('.ra-certonly'); await p.fill('.ra-in[data-k="atd_rate"]', '0'); await p.waitForTimeout(100);
  console.log(await p.textContent('.ra-count'));
  const el = await p.$('#atd-table'); await el.scrollIntoViewIfNeeded();
  await p.screenshot({ path: out });
  console.log(JSON.stringify(logs)); await b.close();
})();
