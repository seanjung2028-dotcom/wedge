// the folder's chart tooltip, and the final-line cards at rest
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1400, height: 900 } }); const errs = []; p.on('pageerror', (e) => errs.push(e.message));
  await p.goto('file://' + file); await p.waitForTimeout(1500);
  await p.evaluate(() => document.querySelector('.wg-nav [data-page="final"]').click()); await p.waitForTimeout(1200);
  const bb = await p.$eval('.v2-edge-reads', (e) => { e.scrollIntoView({ block: 'start' }); const r = e.getBoundingClientRect(); return { x: r.x - 10, y: Math.max(0, r.y - 10), width: r.width + 20, height: 460 }; });
  await p.mouse.move(5, 5); await p.waitForTimeout(600); await p.screenshot({ path: out + '/edge_rest.png', clip: bb });
  await p.evaluate(() => document.querySelector('.wg-nav [data-page="research"]').click()); await p.waitForTimeout(800);
  await p.evaluate(() => { const q = document.querySelector('#lines-card input'); q.value = 'Kolar'; q.dispatchEvent(new Event('input', { bubbles: true })); }); await p.waitForTimeout(700);
  await p.evaluate(() => [...document.querySelectorAll('#lines-table tbody tr.v2-click')][0].click()); await p.waitForTimeout(2200);
  await p.click('#sit-t-mu'); await p.waitForTimeout(1400);
  const bar = await p.$('#sit-log rect, #sit-log .bar, #sit-log svg rect'); 
  const rects = await p.$$('#sit-log svg rect'); let hit = null;
  for (const r of rects) { const b2 = await r.boundingBox(); if (b2 && b2.height > 20 && b2.width > 8) { hit = b2; break; } }
  if (hit) { await p.mouse.move(hit.x + hit.width / 2, hit.y + hit.height / 2); await p.waitForTimeout(500); await p.screenshot({ path: out + '/tip.png', clip: { x: Math.max(0, hit.x - 220), y: Math.max(0, hit.y - 140), width: 520, height: 320 } }); }
  console.log('tip', !!hit, await p.evaluate(() => { const t = document.querySelector('#sit-dlg .wg-tip'); return t ? [getComputedStyle(t).backgroundColor, getComputedStyle(t).color, getComputedStyle(t).opacity] : null; }), errs.join(' | '));
  await b.close();
})();
