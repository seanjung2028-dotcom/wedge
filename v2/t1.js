const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, w = '1300'] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: 900 } });
  const logs = []; p.on('pageerror', (e) => logs.push('ERR ' + e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push('CONSOLE ' + m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(1800);
  const H = await p.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < H; y += 450) { await p.evaluate((y) => scrollTo(0, y), y); await p.waitForTimeout(90); }
  await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(600);
  console.log('pages', await p.evaluate(() => [...document.querySelectorAll('.rs-page')].map((x) => x.id).join(',')));
  console.log('tiles', await p.$$eval('#v2-mgrid .v2-mt', (x) => x.length), 'ink', await p.$$eval('[data-ink]', (x) => x.map((e) => e.dataset.ink).join('')));
  await p.screenshot({ path: out + '/home_full.png', fullPage: true });
  console.log(logs.slice(0, 12).join('\n'));
  await b.close();
})();
