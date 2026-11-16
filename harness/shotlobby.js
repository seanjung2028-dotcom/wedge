const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, w = '1300', h = '950', full = ''] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: +h } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message));
  await p.goto('file://' + file); await p.waitForTimeout(1500);
  await p.screenshot({ path: out, fullPage: !!full });
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
