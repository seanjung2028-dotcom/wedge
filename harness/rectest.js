const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, outDir, width] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: Number(width || 1300), height: 900 } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(700);
  const rec = await p.evaluate(() => ({ pct: document.querySelector('.wg-record-pct').textContent, frac: document.querySelector('.wg-record-frac').textContent, sub: document.querySelector('.wg-record-sub').textContent, cls: document.querySelector('#wg-record').className }));
  console.log('record', JSON.stringify(rec));
  await p.screenshot({ path: outDir + '/rec_top.png', clip: { x: 0, y: 0, width: Number(width || 1300), height: 260 } });
  await p.click('#tab-results'); await p.waitForTimeout(150);
  await p.check('.rr-certonly'); await p.waitForTimeout(150);
  console.log('certOnly', await p.textContent('.rr-count'), await p.evaluate(() => document.querySelectorAll('#results-table tbody tr.wg-certified').length));
  const el = await p.$('#results-lines'); await el.scrollIntoViewIfNeeded();
  await p.screenshot({ path: outDir + '/rec_results.png' });
  // untick one loss -> record should change
  const owner = await p.evaluate(() => document.querySelectorAll('#results-table .wg-certbox').length);
  if (owner) {
    const row = await p.$('#results-table tbody tr:has-text("Patrick Mahomes") .wg-certbox');
    await row.click(); await p.waitForTimeout(400);
    console.log('after untick', await p.evaluate(() => document.querySelector('.wg-record-pct').textContent + ' ' + document.querySelector('.wg-record-frac').textContent));
  }
  await p.uncheck('.rr-certonly'); await p.waitForTimeout(100);
  console.log('default view', await p.textContent('.rr-count'));
  await p.click('#tab-charts'); await p.waitForTimeout(300);
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
