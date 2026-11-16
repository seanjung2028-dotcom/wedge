const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, outDir] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1300, height: 950 } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(900);
  const nav = async (pg) => { await p.click('#nfl-btn'); await p.click(`#nfl-menu [data-page="${pg}"]`); await p.waitForTimeout(300); };
  await nav('results');
  console.log('w7 q', await p.textContent('.rr-count'));
  await p.selectOption('.rr-show', 'all'); await p.waitForTimeout(150); console.log('w7 all', await p.textContent('.rr-count'));
  await p.selectOption('.rr-show', 'atd'); await p.waitForTimeout(150); console.log('w7 atd', await p.textContent('.rr-count'));
  await p.selectOption('.rr-show', 'q'); await p.screenshot({ path: outDir + '/results_w7.png' });
  await p.selectOption('.rr-week', '6'); await p.waitForTimeout(150); console.log('w6 q', await p.textContent('.rr-count'));
  console.log('games w6', await p.evaluate(() => document.querySelector('.rr-game').options.length));
  await nav('lines');
  const txt = await p.evaluate(() => [...document.querySelectorAll('#lines tbody tr')].filter((tr) => tr.textContent.includes('Tanner McKee')).map((tr) => tr.textContent.slice(0, 160)));
  console.log('lemon rows', txt.length, txt[0]);
  const btn = await p.$$('#lines tbody tr:has-text("Tanner McKee") .wg-sitbtn');
  if (btn.length) { await btn[0].click(); await p.waitForTimeout(600); const note = await p.evaluate(() => [...document.querySelectorAll('.wg-sitdlg .wg-note')].map((n) => n.textContent)); console.log('note', note[0]); await p.screenshot({ path: outDir + '/dalphi_outlook.png' }); await p.keyboard.press('Escape'); await p.waitForTimeout(300); }
  const b2 = await p.$$('#lines tbody tr:has-text("Ja\'Marr Chase") .wg-sitbtn');
  if (b2.length) { await b2[0].click(); await p.waitForTimeout(600); const note = await p.evaluate(() => [...document.querySelectorAll('.wg-sitdlg .wg-note')].map((n) => n.textContent)); console.log('note sunday', note[0]); await p.keyboard.press('Escape'); }
  await nav('backtest');
  console.log('para', (await p.evaluate(() => [...document.querySelectorAll('.rs-page p')].map((x) => x.textContent).find((t) => t.startsWith('Live check')) || 'MISSING')).slice(0, 200));
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
