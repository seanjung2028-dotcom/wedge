const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  const logs = []; p.on('pageerror', (e) => logs.push('PE ' + e.message)); p.on('console', (m) => logs.push(m.type() + ' ' + m.text().slice(0, 300)));
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1200);
  console.log(await p.evaluate(() => JSON.stringify({ errs: window.__errs, scripts: window.__emuScripts, root: (document.getElementById('dash-root') || {}).innerHTML?.length, btn: !!document.querySelector('#nfl-btn') })));
  console.log(logs.slice(0, 10).join('\n')); await b.close();
})();
