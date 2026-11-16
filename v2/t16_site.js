// open the site straight onto each page (as a shared link would) and make sure nothing throws and the data shows
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file] = process.argv;
  const b = await chromium.launch();
  for (const h of ['', '#lobby', '#research', '#final', '#thesis', '#charts', '#analysts', '#results', '#nba', '#nba-results', '#soccer', '#lines', '#proj']) {
    const p = await b.newPage({ viewport: { width: 1300, height: 900 } }); const errs = [];
    p.on('pageerror', (e) => errs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') errs.push('console: ' + m.text().split('\n')[0]); });
    await p.goto(file + h); await p.waitForTimeout(3500);
    const s = await p.evaluate(() => ({ page: (document.querySelector('.rs-page:not([hidden])') || {}).id, hero: (document.querySelector('[data-wz="cert-pct"]') || {}).textContent, tiles: document.querySelectorAll('#v2-mgrid .v2-mt').length,
      rows: document.querySelectorAll('.rs-page:not([hidden]) .rs-table tbody tr').length, login: [...document.querySelectorAll('.wz-top button, .wz-top a')].filter((x) => /log in|sign up/i.test(x.textContent) && x.offsetParent).length }));
    console.log((h || '(none)').padEnd(13), JSON.stringify(s), errs.length ? 'ERRORS: ' + errs.slice(0, 3).join(' | ') : 'ok');
    await p.close();
  }
  await b.close();
})();
