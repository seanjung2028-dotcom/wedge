// the Thesis page's line cards, desktop and phone, resting and hovered
const { chromium, devices } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, tag = 'th'] = process.argv;
  const b = await chromium.launch(); const logs = [];
  for (const [nm, ctxo] of [['d', { viewport: { width: 1300, height: 900 } }], ['m', { ...devices['iPhone 13'] }]]) {
    const ctx = await b.newContext(ctxo); const p = await ctx.newPage(); p.on('pageerror', (e) => logs.push('ERR ' + e.message));
    await p.goto('file://' + file); await p.waitForTimeout(1400);
    await p.evaluate(() => document.querySelector('.wg-nav [data-page="thesis"]').click()); await p.waitForTimeout(1200);
    const y = await p.evaluate(() => { const h = [...document.querySelectorAll('#thesis h3, #thesis h2')].find((x) => /WHY EACH LINE/i.test(x.textContent)); h.scrollIntoView({ block: 'start' }); return Math.round(scrollY); });
    await p.waitForTimeout(400); await p.screenshot({ path: `${out}/${tag}_${nm}1.png` });
    if (nm === 'd') { await p.hover('.v2-th-play'); await p.waitForTimeout(500); await p.screenshot({ path: `${out}/${tag}_${nm}hover.png` }); }
    await p.evaluate(() => scrollBy(0, innerHeight * .8)); await p.waitForTimeout(300); await p.screenshot({ path: `${out}/${tag}_${nm}2.png` });
    // anything poking past the page's content column
    console.log(nm, await p.evaluate(() => { const col = document.querySelector('#thesis').getBoundingClientRect(); const bad = []; document.querySelectorAll('#thesis *').forEach((e) => { const r = e.getBoundingClientRect(); if (r.width && (r.left < col.left - 1 || r.right > col.right + 1)) bad.push((e.className && e.className.baseVal === undefined ? e.className : e.tagName) + ' ' + Math.round(r.left) + '-' + Math.round(r.right)); }); return [Math.round(col.left), Math.round(col.right), bad.slice(0, 12)]; }));
    await ctx.close();
  }
  console.log(logs.join('\n')); await b.close();
})();
