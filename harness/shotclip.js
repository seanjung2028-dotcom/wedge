const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, w, h, sel] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: +h } });
  await p.goto('file://' + file); await p.waitForTimeout(1500);
  const e = await p.$(sel); await e.screenshot({ path: out });
  console.log(await p.evaluate(() => document.documentElement.scrollWidth - innerWidth)); await b.close();
})();
