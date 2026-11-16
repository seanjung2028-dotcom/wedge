const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, w = '1300'] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: 900 } });
  const logs = []; p.on('pageerror', (e) => logs.push('ERR ' + e.message));
  await p.goto('file://' + file); await p.waitForTimeout(1500);
  await p.click('#nfl-btn'); await p.waitForTimeout(400);
  await p.screenshot({ path: out + '/nfl_menu.png', clip: { x: 0, y: 0, width: +w, height: 620 } });
  const box = await p.$eval('#nfl-menu', (m) => { const r = m.getBoundingClientRect(); const cs = getComputedStyle(m); return { r: [r.x, r.y, r.width, r.height], pad: cs.padding, bg: cs.backgroundColor, bd: cs.border, rad: cs.borderRadius }; });
  console.log(JSON.stringify(box));
  await p.click('#nfl-menu [data-page="research"]'); await p.waitForTimeout(800);
  await p.screenshot({ path: out + '/research_top.png', clip: { x: 0, y: 0, width: +w, height: 1100 } });
  console.log(logs.join('\n'));
  await b.close();
})();
