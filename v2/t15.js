// both pop-ups land in the middle of the screen, even with a host page that zeroes every margin
const { chromium, devices } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out] = process.argv;
  const b = await chromium.launch();
  for (const [nm, o] of [['d', { viewport: { width: 1440, height: 900 } }], ['m', { ...devices['iPhone 13'] }]]) {
    const ctx = await b.newContext(o); const p = await ctx.newPage();
    await p.goto('file://' + file); await p.waitForTimeout(1400);
    await p.addStyleTag({ content: '*{margin:0}' });   // what a host stylesheet's reset does
    const box = (sel) => p.$eval(sel, (d) => { const r = d.getBoundingClientRect(); return { l: Math.round(r.left), r: Math.round(innerWidth - r.right), t: Math.round(r.top), b: Math.round(innerHeight - r.bottom) }; });
    await p.evaluate(() => document.querySelector('[data-wz-join]').click()); await p.waitForTimeout(700);
    console.log(nm, 'join', JSON.stringify(await box('#wz-dlg')));
    await p.screenshot({ path: `${out}/c_${nm}_join.png` });
    await p.keyboard.press('Escape'); await p.waitForTimeout(400);
    await p.evaluate(() => document.querySelector('.wg-nav [data-page="research"]').click()); await p.waitForTimeout(900);
    await p.evaluate(() => [...document.querySelectorAll('#lines-table tbody tr.v2-click')][2].click()); await p.waitForTimeout(2300);
    console.log(nm, 'folder', JSON.stringify(await box('#sit-dlg')));
    await p.screenshot({ path: `${out}/c_${nm}_folder.png` });
    await ctx.close();
  }
  await b.close();
})();
