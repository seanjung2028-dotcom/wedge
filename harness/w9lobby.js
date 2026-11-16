const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 950 } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1500);
  console.log('cards', await p.$$eval('.wg-mk', (x) => x.length), 'tick items', await p.$$eval('.wg-tick-item', (x) => x.length));
  await p.click('.wg-mk'); await p.waitForTimeout(700);
  console.log('card outlook', await p.evaluate(() => { const d = document.querySelector('#sit-dlg'); return d && d.open ? d.querySelector('#sit-title').textContent : 'closed'; }));
  await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  await p.click('.wg-hx-dot:nth-child(2)'); await p.waitForTimeout(900);
  console.log('slide2 on', await p.evaluate(() => document.querySelectorAll('.wg-hx-slide')[1].classList.contains('is-on')));
  await p.screenshot({ path: process.argv[3] + '/slide2.png', clip: { x: 0, y: 200, width: 1300, height: 500 } });
  await p.click('.wg-hx-slide.is-on [data-wg-show="pick"]'); await p.waitForTimeout(400);
  console.log('after pick btn', await p.evaluate(() => [document.querySelector('#lines').hidden, document.querySelector('.rs-show').value, document.querySelector('.rl-count').textContent]));
  for (const pg of ['proj', 'atd', 'results']) { await p.click('#nfl-btn'); await p.click(`#nfl-menu [data-page="${pg}"]`); await p.waitForTimeout(250); console.log(pg, 'banner', await p.$eval(`#${pg} .wg-pb-title`, (e) => e.textContent)); }
  await p.click('.rs-tab[data-page="nba"]'); await p.waitForTimeout(500); await p.screenshot({ path: process.argv[3] + '/nba_banner.png', clip: { x: 0, y: 180, width: 1300, height: 420 } });
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
