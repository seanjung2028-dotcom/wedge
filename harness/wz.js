const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, scheme, out, w] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +(w || 1300), height: 900 }, colorScheme: scheme || 'light' });
  const logs = []; p.on('pageerror', (e) => logs.push('ERR ' + e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(2000);
  const H = await p.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < H; y += 500) { await p.evaluate((y) => window.scrollTo(0, y), y); await p.waitForTimeout(60); }
  await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(1500);
  const info = await p.evaluate(() => ({
    rec: document.querySelector('[data-wz="cert-pct"]').textContent, profit: document.querySelector('[data-wz="cert-profit"]').textContent,
    an: document.querySelector('[data-wz="an-pct"]').textContent, anrec: document.querySelector('[data-wz="an-rec"]').textContent,
    board: document.querySelectorAll('#wz-board .wz-an').length, t1: document.querySelectorAll('#wz-tape-1 .wz-tk').length, t2: document.querySelectorAll('#wz-tape-2 .wz-tk').length,
    days: [...document.querySelectorAll('.wz-day h3')].map((h) => h.textContent), games: document.querySelectorAll('.wz-game').length, kick: document.querySelector('#wz-kick').textContent,
    ex: (document.querySelector('.wz-ex-title') || {}).textContent, font: getComputedStyle(document.querySelector('.wz-h1')).fontFamily,
    fontsOk: [...document.fonts].filter((f) => f.status === 'loaded').map((f) => f.family + f.weight).join(','),
    hscroll: document.documentElement.scrollWidth - innerWidth }));
  console.log(JSON.stringify(info));
  if (out) await p.screenshot({ path: out, fullPage: true });
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
