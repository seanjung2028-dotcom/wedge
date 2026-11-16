const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, scheme, out, w] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +(w || 1440), height: 900 }, colorScheme: scheme || 'light' });
  const logs = []; p.on('pageerror', (e) => logs.push('ERR ' + e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(2200);
  const H = await p.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < H; y += 500) { await p.evaluate((y) => window.scrollTo(0, y), y); await p.waitForTimeout(50); }
  await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(1600);
  const q = (s) => p.evaluate((s) => { const e = document.querySelector(s); return e ? e.textContent.trim().slice(0, 80) : null; }, s);
  console.log(JSON.stringify({ big: await q('.pf-big'), wl: await q('[data-wz="cert-wl"]'), profit: await q('.pf-proof [data-wz="cert-profit"]'), an: await q('.pf-proof [data-wz="an-pct"]'),
    kick: await q('#wz-kick'), board: await p.$$eval('#wz-board .wz-an', (x) => x.length), days: await p.$$eval('.wz-game .pf-hp img', (x) => x.length),
    tiers: await p.$$eval('#lobby .pf-tier', (x) => x.length), hscroll: await p.evaluate(() => document.documentElement.scrollWidth - innerWidth),
    font: await p.evaluate(() => getComputedStyle(document.querySelector('.pf-h1')).fontFamily) }));
  if (out) await p.screenshot({ path: out, fullPage: true });
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
