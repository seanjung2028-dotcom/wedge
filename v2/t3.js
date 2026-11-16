const { chromium, devices } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out] = process.argv;
  const b = await chromium.launch(); const ctx = await b.newContext({ ...devices['iPhone 13'] }); const p = await ctx.newPage();
  const logs = []; p.on('pageerror', (e) => logs.push('ERR ' + e.message));
  await p.goto('file://' + file); await p.waitForTimeout(1600);
  console.log('overflow', await p.evaluate(() => [document.documentElement.scrollWidth, innerWidth]));
  await p.screenshot({ path: out + '/m_home.png' });
  await p.evaluate(() => document.querySelector('#v2-matchups').scrollIntoView()); await p.waitForTimeout(500);
  await p.screenshot({ path: out + '/m_match.png' });
  await p.click('#v2-mgrid .v2-mt[data-game="DEN @ CAR"]'); await p.waitForTimeout(1300); await p.screenshot({ path: out + '/m_reads.png' });
  await p.click('#nfl-btn'); await p.click('#nfl-menu [data-page="research"]'); await p.waitForTimeout(800);
  await p.evaluate(() => { const r = [...document.querySelectorAll('#lines-table tbody tr.v2-click')][3]; r.click(); }); await p.waitForTimeout(1300);
  await p.screenshot({ path: out + '/m_file.png' });
  await p.click('#sit-t-inj'); await p.waitForTimeout(1000); await p.screenshot({ path: out + '/m_inj.png' });
  console.log(logs.join('\n'));
  await b.close();
})();
