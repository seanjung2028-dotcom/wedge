const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, tab, width, full] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: Number(width || 1300), height: 900 } });
  const logs = [];
  p.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') logs.push(m.type() + ': ' + m.text()); });
  p.on('pageerror', (e) => logs.push('pageerror: ' + e.message));
  await p.goto('file://' + file + (tab ? '#' + tab : ''));
  await p.waitForTimeout(400);
  if (tab) { await p.click('#tab-' + tab); await p.waitForTimeout(400); }
  await p.screenshot({ path: out, fullPage: full === '1' });
  console.log(JSON.stringify({ logs, errs: await p.evaluate(() => window.__errs) }));
  await b.close();
})();
