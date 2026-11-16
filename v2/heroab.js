const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 900 } });
  await p.goto('file://' + file); await p.waitForTimeout(2500);
  await p.evaluate(() => document.getAnimations().forEach((a) => a.pause()));
  await p.screenshot({ path: out + '/hero_a.png' });
  await p.addStyleTag({ content: '.wg-paper .pf-metal, .wg-paper .pf-blob { filter: none !important; }' });
  await p.waitForTimeout(200); await p.screenshot({ path: out + '/hero_b.png' });
  await p.evaluate(() => document.getAnimations().forEach((a) => a.play()));
  const fps = await p.evaluate(async () => { let n = 0; const s = performance.now(); await new Promise((res) => { const f = () => { n++; if (performance.now() - s < 1500) requestAnimationFrame(f); else res(); }; requestAnimationFrame(f); }); return +(n / 1.5).toFixed(1); });
  console.log('fps without live blur, all motion on:', fps);
  await b.close();
})();
