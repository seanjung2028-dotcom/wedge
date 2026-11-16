const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, w = '1300', pages = 'final,thesis,charts,analysts,results'] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: 900 } });
  const logs = []; p.on('pageerror', (e) => logs.push('ERR ' + e.message));
  await p.goto('file://' + file); await p.waitForTimeout(1500);
  for (const id of pages.split(',')) {
    await p.click('#nfl-btn'); await p.waitForTimeout(150);
    await p.click(`#nfl-menu [data-page="${id}"]`); await p.waitForTimeout(1200);
    await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(200);
    const H = await p.evaluate(() => document.documentElement.scrollHeight);
    await p.screenshot({ path: `${out}/pg_${id}.png`, fullPage: true });
    console.log(id, H);
  }
  console.log(logs.join('\n'));
  await b.close();
})();
