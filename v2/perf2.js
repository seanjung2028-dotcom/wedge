// which piece of Home's motion costs the most: idle fps with each one paused
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 900 } });
  await p.goto('file://' + file); await p.waitForTimeout(3500);
  const fps = () => p.evaluate(async () => { let n = 0; const s = performance.now(); await new Promise((res) => { const f = () => { n++; if (performance.now() - s < 1500) requestAnimationFrame(f); else res(); }; requestAnimationFrame(f); }); return +(n / 1.5).toFixed(1); });
  const pause = (names) => p.evaluate((names) => document.getAnimations().forEach((a) => { if (names === '*' || names.includes(a.animationName)) a.pause(); else a.play(); }), names);
  const only = (keep) => p.evaluate((keep) => document.getAnimations().forEach((a) => { if (keep.includes(a.animationName)) a.play(); else a.pause(); }), keep);
  for (const [lab, keep] of [['only metal', ['v2MetalSpin']], ['only blob', ['pfBlob']], ['only drift', ['pfDrift']], ['only pulse', ['wzPulse']], ['only net', ['v2NetSheen']], ['none', []]]) {
    await only(keep); await p.waitForTimeout(300); console.log(lab.padEnd(16), await fps());
  }
  await p.addStyleTag({ content: '.wg-paper.wg-paper.wg-paper.wg-paper.wg-paper.wg-paper{background:#1d2024 !important}' }); await only(['v2MetalSpin']); await p.waitForTimeout(300); console.log('metal, no grain bg', await fps());
  await only(['pfDrift']); await p.waitForTimeout(300); console.log('drift, no grain bg', await fps());
  console.log(await p.evaluate(() => [...document.querySelectorAll('.pf-bg')].map((e) => e.parentElement.className + ' ' + e.getBoundingClientRect().height)));
  console.log(await p.evaluate(() => [...document.querySelectorAll('.pf-bg i')].map((e) => getComputedStyle(e).filter + ' ' + Math.round(e.getBoundingClientRect().width))));
  await b.close();
})();
