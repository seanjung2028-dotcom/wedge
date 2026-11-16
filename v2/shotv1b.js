const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, page = 'lobby'] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 900 } });
  await p.goto('file://' + file); await p.waitForTimeout(1200);
  if (page !== 'lobby') { await p.evaluate((pg) => { const b = document.querySelector(`[data-page="${pg}"]`); b.click(); }, page); await p.waitForTimeout(800); }
  const H = await p.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < H; y += 400) { await p.evaluate((y) => scrollTo(0, y), y); await p.waitForTimeout(120); }
  await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(500);
  await p.screenshot({ path: out, fullPage: true });
  await b.close();
})();
