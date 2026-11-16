const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, outDir] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1100, height: 760 }, deviceScaleFactor: 2 });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message));
  await p.goto('file://' + file);
  for (const t of [250, 650, 900, 1150, 2800]) { await p.waitForTimeout(t === 250 ? 250 : (t - [250, 650, 900, 1150, 2800][[250, 650, 900, 1150, 2800].indexOf(t) - 1])); await p.screenshot({ path: `${outDir}/a_${t}.png`, clip: { x: 300, y: 260, width: 500, height: 260 } }); }
  console.log(JSON.stringify(logs)); await b.close();
})();
