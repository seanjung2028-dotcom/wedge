const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, w] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +(w || 1300), height: 1000 } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(900);
  await p.click('.rs-tab[data-page="nba"]'); await p.waitForTimeout(400);
  for (const [i, sel] of [['1', '#nba-rec'], ['2', '#nr-night'], ['3', '#nr-table'], ['4', '#nba-bt'], ['5', '#nbt-month'], ['6', '#nbt-cal']].entries()) {
    await p.evaluate((s) => document.querySelector(s).scrollIntoView(), sel[1]); await p.waitForTimeout(1300);
    await p.screenshot({ path: `${out}_${sel[0]}.png` });
  }
  const info = await p.evaluate(() => ({ tiles: [...document.querySelectorAll('#nr-tiles .rs-card')].map((c) => c.innerText.replace(/\n/g, ' | ')), sum: document.querySelector('#nr-sum').textContent,
    count: document.querySelector('.nr-count').textContent, svgs: [...document.querySelectorAll('#nba .wg-chart')].map((c) => c.id + ':' + (c.querySelector('svg') ? c.querySelector('svg').getAttribute('viewBox') : 'none')), errs: window.__errs }));
  console.log(JSON.stringify(info, null, 1)); console.log('logs', JSON.stringify(logs)); await b.close();
})();
