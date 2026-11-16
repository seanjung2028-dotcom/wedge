// hover sheen on lines across the NFL pages
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, tag = 's'] = process.argv;
  const b = await chromium.launch(); const logs = [];
  const p = await b.newPage({ viewport: { width: 1300, height: 900 } }); p.on('pageerror', (e) => logs.push('ERR ' + e.message));
  await p.goto('file://' + file); await p.waitForTimeout(1400);
  const go = async (id) => { await p.evaluate((id) => document.querySelector(`.wg-nav [data-page="${id}"]`).click(), id); await p.waitForTimeout(1100); };
  const shot = async (sel, name, idx = 2) => {
    const h = await p.evaluate(([sel, idx]) => { const r = [...document.querySelectorAll(sel)].filter((x) => x.offsetParent)[idx]; if (!r) return null; r.scrollIntoView({ block: 'center' }); return true; }, [sel, idx]);
    if (!h) { console.log('missing', sel); return; }
    await p.waitForTimeout(300);
    const el = (await p.$$(sel)).filter(Boolean); const vis = [];
    for (const e of el) if (await e.isVisible()) vis.push(e);
    await vis[idx].hover(); await p.waitForTimeout(420);
    const bb = await vis[idx].boundingBox();
    await p.screenshot({ path: `${out}/${tag}_${name}.png`, clip: { x: 0, y: Math.max(0, bb.y - 120), width: 1300, height: Math.min(330, bb.height + 240) } });
    console.log(name, await vis[idx].evaluate((x) => [x.className, x.style.getPropertyValue('--tc1'), x.style.getPropertyValue('--tc2')].join(' | ')));
  };
  await go('research'); await shot('#lines-table tbody tr', 'lines', 3); await shot('#lines-table tbody tr', 'lines_game', 0);
  await go('final'); await shot('.fc-board tbody tr', 'board', 1); await shot('.fc-game > .fc-sum', 'game', 2);
  await go('results'); await shot('.rs-page:not([hidden]) .rs-table tbody tr[data-key]', 'results', 4);
  await go('thesis'); await shot('.v2-th-play', 'thesis', 0);
  await go('nba'); await shot('.rs-page:not([hidden]) .rs-table tbody tr', 'nba', 1);
  console.log(logs.join('\n'));
  await b.close();
})();
