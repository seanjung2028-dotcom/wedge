const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, outDir] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 950 } });
  await p.goto('file://' + file); await p.waitForTimeout(900);
  await p.click('.rs-tab[data-page="charts"]'); await p.waitForTimeout(400);
  const r = await p.evaluate(() => { const ps = [...document.querySelectorAll('p')].filter((x) => x.textContent.includes('Live check')); return ps.map((x) => [x.closest('.rs-page')?.id, x.textContent.slice(0, 120)]); });
  console.log(JSON.stringify(r));
  const el = await p.$('p:has-text("Live check and re-fit")'); if (el) { await el.scrollIntoViewIfNeeded(); await p.waitForTimeout(200); await el.screenshot({ path: outDir + '/livecheck.png' }); }
  await b.close();
})();
