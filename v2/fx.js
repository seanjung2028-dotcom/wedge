// every on-screen element using a blur, blend or mask (the expensive effects)
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, page = 'lobby'] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 900 } });
  await p.goto('file://' + file); await p.waitForTimeout(2500);
  if (page !== 'lobby') { await p.evaluate((id) => document.querySelector(`.wg-nav [data-page="${id}"]`).click(), page); await p.waitForTimeout(1200); }
  const rows = await p.evaluate(() => [...document.querySelectorAll('*')].filter((e) => {
    const cs = getComputedStyle(e), r = e.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && ((cs.backdropFilter && cs.backdropFilter !== 'none') || (cs.filter && cs.filter !== 'none') || cs.mixBlendMode !== 'normal' || (cs.maskImage && cs.maskImage !== 'none'));
  }).map((e) => {
    const cs = getComputedStyle(e), r = e.getBoundingClientRect();
    const nm = typeof e.className === 'string' ? e.className.split(' ').slice(0, 2).join('.') : e.tagName;
    return `${nm} pos=${cs.position} bf=${cs.backdropFilter} f=${cs.filter} blend=${cs.mixBlendMode} mask=${cs.maskImage !== 'none'} ${Math.round(r.width)}x${Math.round(r.height)}`;
  }));
  const counts = {}; rows.forEach((r) => { const k = r.replace(/ \d+x\d+$/, ''); counts[k] = (counts[k] || 0) + 1; });
  Object.entries(counts).forEach(([k, n]) => console.log(n + ' × ' + k));
  await b.close();
})();
