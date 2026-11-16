const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 950 } });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1500);
  const pages = await p.$$eval('[data-page]', (x) => [...new Set(x.map((e) => e.dataset.page))]);
  const out = {};
  for (const pg of pages) {
    await p.evaluate((pg) => { const b = document.querySelector(`nav [data-page="${pg}"]`) || document.querySelector(`[data-page="${pg}"]`); if (b) b.click(); }, pg);
    await p.waitForTimeout(500);
    out[pg] = await p.evaluate(() => [...document.querySelectorAll('p, .wg-note, .wx-sec-sub, figcaption, li, small')].filter((e) => e.offsetParent && e.textContent.trim().length > 90 && !e.closest('table') && !e.closest('dialog')).map((e) => ({ cls: e.className, n: e.textContent.trim().length, t: e.textContent.trim().replace(/\s+/g, ' ') })));
  }
  require('fs').writeFileSync(process.argv[3], JSON.stringify({ pages, out }, null, 1));
  await b.close();
})();
