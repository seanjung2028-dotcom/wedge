const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, outDir] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1300, height: 950 } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(800);
  const nav = async (pg) => { await p.click('#nfl-btn'); await p.click(`#nfl-menu [data-page="${pg}"]`); await p.waitForTimeout(250); };
  await nav('lines');
  console.log('lines', await p.textContent('.rl-count'));
  await p.selectOption('.rs-src', 'Sportsbook avg'); await p.waitForTimeout(150);
  console.log('book lines', await p.textContent('.rl-count'));
  await p.screenshot({ path: outDir + '/w7_lines.png' });
  await p.selectOption('.rs-src', ''); 
  for (const k of ['cat-1', 'cat-2', 'cat-3', 'cat-4']) { await nav(k); console.log(k, await p.textContent(`#${k} .rc-count`)); }
  await nav('cat-2'); await p.screenshot({ path: outDir + '/w7_cat2.png' });
  await nav('atd'); console.log('atd', await p.textContent('.ra-count'));
  await p.screenshot({ path: outDir + '/w7_atd.png' });
  await nav('defense');
  console.log('by_game rows', await p.evaluate(() => document.querySelectorAll('.rs-grow').length));
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
