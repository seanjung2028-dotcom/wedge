const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, w, h, scheme, full, page] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: +h }, colorScheme: scheme || 'light' });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message));
  await p.goto('file://' + file); await p.waitForTimeout(1500);
  if (page && page !== 'lobby') { await p.evaluate((pg) => { const b = document.querySelector(`[data-page="${pg}"]`); if (b) b.click(); else { document.querySelector('#nfl-btn').click(); document.querySelector(`#nfl-menu [data-page="${pg}"]`).click(); } }, page); await p.waitForTimeout(600); }
  await p.screenshot({ path: out, fullPage: full === 'full' });
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
