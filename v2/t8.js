const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 900 } });
  await p.goto('file://' + file); await p.waitForTimeout(2500);
  await p.screenshot({ path: out + '/h_top.png' });
  await p.evaluate(() => document.querySelector('#v2-matchups').scrollIntoView()); await p.waitForTimeout(700);
  await p.screenshot({ path: out + '/h_match.png' });
  await p.click('#v2-mgrid .v2-mt[data-game="DEN @ CAR"]'); await p.waitForTimeout(1300);
  await p.evaluate(() => document.querySelector('#wz-reads').scrollIntoView()); await p.waitForTimeout(700);
  await p.hover('.v2-read'); await p.waitForTimeout(900);
  await p.screenshot({ path: out + '/h_reads.png' });
  await p.evaluate(() => document.querySelector('#lobby .wz-sched, #wz-sched, [id*=sched]').scrollIntoView()); await p.waitForTimeout(700);
  await p.screenshot({ path: out + '/h_sched.png' });
  await b.close();
})();
