// exact animation frames of the research folder: pause every animation and step through time
const { chromium, devices } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, tag = 'f', phone = ''] = process.argv;
  const b = await chromium.launch(); const logs = [];
  const p = phone ? await (await b.newContext({ ...devices['iPhone 13'] })).newPage() : await b.newPage({ viewport: { width: 1300, height: 940 } });
  p.on('pageerror', (e) => logs.push('ERR ' + e.message));
  await p.goto('file://' + file); await p.waitForTimeout(1400);
  await p.evaluate(() => document.querySelector('.wg-nav [data-page="research"]').click()); await p.waitForTimeout(900);
  await p.evaluate(() => { const q = document.querySelector('#lines-card input[type=search], #lines-card input'); if (q) { q.value = 'Kolar'; q.dispatchEvent(new Event('input', { bubbles: true })); } }); await p.waitForTimeout(700);
  await p.evaluate(() => { const r = [...document.querySelectorAll('#lines-table tbody tr.v2-click')][0]; r.click(); document.getAnimations().filter((a) => a.effect && a.effect.getComputedTiming().endTime !== Infinity).forEach((a) => a.pause()); });
  const frames = [0, 200, 380, 520, 660, 800, 1000, 1400];
  for (const t of frames) {
    await p.evaluate((t) => document.getAnimations().filter((a) => a.effect && a.effect.getComputedTiming().endTime !== Infinity).forEach((a) => { a.currentTime = t; }), t); await p.waitForTimeout(60);
    await p.screenshot({ path: `${out}/${tag}_t${t}.png` });
  }
  await p.evaluate(() => document.getAnimations().filter((a) => a.effect && a.effect.getComputedTiming().endTime !== Infinity).forEach((a) => a.finish())); await p.waitForTimeout(2000);
  console.log('dlg', await p.evaluate(() => { const d = document.querySelector('#sit-dlg'); const r = d.getBoundingClientRect(); const cs = getComputedStyle(d); return [Math.round(r.top), Math.round(r.height), cs.marginTop, cs.top, cs.position, innerHeight]; }));
  // a page turn, mid-way (fresh page, so the opening animations are left alone)
  await p.reload(); await p.waitForTimeout(1400);
  await p.evaluate(() => document.querySelector('.wg-nav [data-page="research"]').click()); await p.waitForTimeout(900);
  await p.evaluate(() => { const q = document.querySelector('#lines-card input[type=search], #lines-card input'); if (q) { q.value = 'Kolar'; q.dispatchEvent(new Event('input', { bubbles: true })); } }); await p.waitForTimeout(700);
  await p.evaluate(() => { const r = [...document.querySelectorAll('#lines-table tbody tr.v2-click')][0]; r.click(); }); await p.waitForTimeout(2300);
  const LEAF = ['v2LeafUp', 'v2LeafDown', 'v2LeafShade', 'v2Under', 'v2TabPop'];
  await p.click('#sit-t-inj'); await p.evaluate((L) => document.getAnimations().filter((a) => L.includes(a.animationName)).forEach((a) => a.pause()), LEAF);
  for (const t of [120, 300, 480]) { await p.evaluate(([t, L]) => document.getAnimations().filter((a) => L.includes(a.animationName)).forEach((a) => { a.currentTime = t; }), [t, LEAF]); await p.waitForTimeout(60); await p.screenshot({ path: `${out}/${tag}_flip${t}.png` }); }
  await p.evaluate((L) => document.getAnimations().filter((a) => L.includes(a.animationName)).forEach((a) => a.play()), LEAF); await p.waitForTimeout(1200);
  await p.screenshot({ path: `${out}/${tag}_inj.png` });
  await p.click('#sit-t-mu'); await p.waitForTimeout(1200); await p.screenshot({ path: `${out}/${tag}_mu.png` });
  console.log(logs.join('\n'));
  await b.close();
})();
