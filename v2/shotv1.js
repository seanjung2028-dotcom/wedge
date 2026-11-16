const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 900 } });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1500);
  await p.screenshot({ path: process.argv[3] + '/v1_lobby_full.png', fullPage: true });
  const secs = await p.evaluate(() => [...document.querySelectorAll('#lobby > *, #lobby section')].map((e) => (e.id || e.className).toString().slice(0, 50) + ' @' + Math.round(e.getBoundingClientRect().top + scrollY) + ' h' + Math.round(e.getBoundingClientRect().height)));
  console.log(secs.join('\n'));
  await b.close();
})();
