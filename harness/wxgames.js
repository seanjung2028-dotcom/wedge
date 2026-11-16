const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, scheme, shot, w] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +(w || 1300), height: 950 }, colorScheme: scheme || 'light' });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(1800);
  const tabs = await p.$$eval('#wx-read-tabs .wx-tab', (x) => x.map((t) => t.textContent));
  console.log('tabs', tabs.length, tabs.join(' | '));
  const res = [];
  for (let i = 1; i < tabs.length; i++) {
    await p.click(`#wx-read-tabs .wx-tab:nth-child(${i + 1})`); await p.waitForTimeout(120);
    res.push(await p.evaluate(() => ({ g: document.querySelector('.wx-tab[aria-selected="true"]').dataset.game, n: document.querySelectorAll('#wg-hot-cards .wx-read').length,
      first: (document.querySelector('#wg-hot-cards .wx-read .wx-read-title') || {}).textContent || document.querySelector('#wg-hot-cards').textContent.trim().slice(0, 60),
      rough: document.querySelectorAll('#wg-hot-cards .wx-rough').length, more: document.querySelector('#wx-reads-more').textContent })));
  }
  res.forEach((r) => console.log(JSON.stringify(r)));
  // JAX @ BAL: open first read
  await p.click('#wx-read-tabs .wx-tab[data-game="JAX @ BAL"]'); await p.waitForTimeout(200);
  if (shot) { const s = await p.$('#reads-h'); await s.scrollIntoViewIfNeeded(); await p.evaluate(() => window.scrollBy(0, -80)); await p.waitForTimeout(300); await p.screenshot({ path: shot }); }
  await p.click('#wg-hot-cards .wx-read'); await p.waitForTimeout(800);
  console.log('dialog', await p.evaluate(() => { const d = document.querySelector('#sit-dlg'); return d && d.open ? d.querySelector('#sit-title').textContent : 'closed'; }));
  await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  // ARI @ SEA: first read has no outlook -> lines tab every view searched
  await p.click('#wx-read-tabs .wx-tab[data-game="ARI @ SEA"]'); await p.waitForTimeout(200);
  await p.click('#wg-hot-cards .wx-read'); await p.waitForTimeout(800);
  console.log('fallback', await p.evaluate(() => [document.querySelector('.rs-show').value, document.querySelector('.rs-game').value, document.querySelector('.rs-search').value, document.querySelector('.rl-count').textContent, !document.querySelector('#lines').hidden]));
  // back to lobby, more button for a game
  await p.evaluate(() => document.querySelector('nav [data-page="lobby"]').click()); await p.waitForTimeout(400);
  await p.click('#wx-read-tabs .wx-tab[data-game="DEN @ CAR"]'); await p.waitForTimeout(200);
  await p.click('#wx-reads-more'); await p.waitForTimeout(700);
  console.log('more', await p.evaluate(() => [document.querySelector('.rs-show').value, document.querySelector('.rs-game').value, document.querySelector('.rs-search').value, document.querySelector('.rl-count').textContent]));
  await p.evaluate(() => document.querySelector('nav [data-page="lobby"]').click()); await p.waitForTimeout(400);
  await p.click('#wx-read-tabs .wx-tab[data-game=""]'); await p.waitForTimeout(200);
  console.log('all', await p.$$eval('#wg-hot-cards .wx-read', (x) => x.length), await p.$eval('#wx-reads-more', (x) => x.textContent));
  await p.click('#wx-reads-more'); await p.waitForTimeout(700);
  console.log('all more', await p.evaluate(() => [document.querySelector('.rs-show').value, document.querySelector('.rs-game').value, document.querySelector('.rl-count').textContent]));
  console.log('hscroll', await p.evaluate(() => document.documentElement.scrollWidth - innerWidth));
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
