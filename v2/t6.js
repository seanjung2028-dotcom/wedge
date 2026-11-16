const { chromium, devices } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out] = process.argv;
  const b = await chromium.launch();
  const logs = [];
  // desktop: research, nba, analysts tops
  const p = await b.newPage({ viewport: { width: 1300, height: 1000 } }); p.on('pageerror', (e) => logs.push('ERR ' + e.message));
  await p.goto('file://' + file); await p.waitForTimeout(1500);
  for (const id of ['research', 'nba', 'analysts', 'nba-edge']) {
    await p.evaluate((id) => document.querySelector(`.wg-nav [data-page="${id}"]`).click(), id); await p.waitForTimeout(1100);
    await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(150);
    await p.screenshot({ path: `${out}/d_${id}.png` });
  }
  // the final page with a game opened
  await p.evaluate(() => document.querySelector('.wg-nav [data-page="final"]').click()); await p.waitForTimeout(1200);
  await p.evaluate(() => { const g = document.querySelector('#fc-DEN-CAR'); g.open = true; g.scrollIntoView(); }); await p.waitForTimeout(700);
  await p.screenshot({ path: `${out}/d_final_open.png` });
  // phone
  const ctx = await b.newContext({ ...devices['iPhone 13'] }); const m = await ctx.newPage(); m.on('pageerror', (e) => logs.push('ERR m ' + e.message));
  await m.goto('file://' + file); await m.waitForTimeout(1500);
  for (const id of ['final', 'results', 'analysts', 'thesis']) {
    await m.evaluate((id) => document.querySelector(`.wg-nav [data-page="${id}"]`).click(), id); await m.waitForTimeout(1100);
    await m.evaluate(() => scrollTo(0, 0)); await m.waitForTimeout(150);
    console.log(id, 'overflow', await m.evaluate(() => [document.documentElement.scrollWidth, innerWidth]));
    await m.screenshot({ path: `${out}/m_${id}.png`, fullPage: false });
    await m.evaluate(() => scrollBy(0, 700)); await m.waitForTimeout(300);
    await m.screenshot({ path: `${out}/m_${id}2.png` });
  }
  await m.evaluate(() => scrollTo(0, 0)); await m.click('#nfl-btn'); await m.waitForTimeout(300); await m.screenshot({ path: `${out}/m_menu.png` });
  console.log(logs.join('\n'));
  await b.close();
})();
