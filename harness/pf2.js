const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, outdir, scheme] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1440, height: 900 }, colorScheme: scheme || 'light' });
  const logs = []; p.on('pageerror', (e) => logs.push('ERR ' + e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(2200);
  await p.screenshot({ path: outdir + '/pf_hero.png' });
  // hover a read card
  await p.click('#wx-read-tabs .wx-tab[data-game="JAX @ BAL"]'); await p.waitForTimeout(300);
  await p.evaluate(() => { document.querySelector('#wz-reads').scrollIntoView(); window.scrollBy(0, 120); }); await p.waitForTimeout(900);
  const c = await (await p.$('#wg-hot-cards .wx-read:nth-child(2)')).boundingBox(); await p.mouse.move(c.x + c.width * .5, c.y + c.height * .5); await p.waitForTimeout(500);
  await p.screenshot({ path: outdir + '/pf_reads.png' });
  // subscribe tab
  await p.click('.wz-top [data-page="subscribe"]'); await p.waitForTimeout(700);
  await p.screenshot({ path: outdir + '/pf_sub.png', fullPage: true });
  // analysts page by team
  await p.click('.wz-top [data-page="analysts"]'); await p.waitForTimeout(900);
  console.log('team tiles', await p.$$eval('#pf-tgrid .pf-tt', (x) => x.map((t) => t.dataset.team + ':' + t.querySelector('small').textContent).join(' | ')));
  console.log('panel rows', await p.$$eval('#pf-tpanel .pf-pick', (x) => x.length), 'list open', await p.evaluate(() => document.querySelector('#pf-allpicks').open));
  await p.click('#pf-tgrid .pf-tt:nth-child(3)'); await p.waitForTimeout(500);
  await p.screenshot({ path: outdir + '/pf_an.png', fullPage: true });
  // lines page
  await p.click('#nfl-btn'); await p.click('#nfl-menu [data-page="lines"]'); await p.waitForTimeout(900);
  const r = await (await p.$('#lines-table tbody tr:nth-child(3)')).boundingBox(); await p.mouse.move(r.x + 400, r.y + r.height / 2); await p.waitForTimeout(300);
  await p.screenshot({ path: outdir + '/pf_lines.png' });
  console.log('game cells', await p.$$eval('#lines-table tbody .pf-gc', (x) => x.length), 'hscroll', await p.evaluate(() => document.documentElement.scrollWidth - innerWidth));
  // charts
  await p.click('.wz-top [data-page="charts"]'); await p.waitForTimeout(1200);
  await p.screenshot({ path: outdir + '/pf_charts.png' });
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
