const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, outDir, tag, w, h] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: +(w || 1300), height: +(h || 950) } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(900);
  const nav = async (pg) => { await p.click('#nfl-btn'); await p.click(`#nfl-menu [data-page="${pg}"]`); await p.waitForTimeout(250); };
  await nav('lines');
  await p.selectOption('.rs-show', 'all'); await p.fill('.rs-search', 'Nacua'); await p.waitForTimeout(200);
  console.log('rows', await p.evaluate(() => [...document.querySelectorAll('#lines-table tbody tr')].map((tr) => tr.innerText.replace(/\s+/g, ' ').slice(0, 160))));
  await p.screenshot({ path: `${outDir}/sit_${tag}_table.png` });
  // open via row click on the receiving-yards line
  const rows = await p.$$('#lines-table tbody tr');
  for (const r of rows) { if ((await r.innerText()).includes('95.5')) { await r.click({ position: { x: 300, y: 10 } }); break; } }
  await p.waitForTimeout(400);
  console.log('open', await p.evaluate(() => document.querySelector('#sit-dlg').open));
  console.log('tiles', await p.evaluate(() => [...document.querySelectorAll('#sit-tiles .rs-card')].map((c) => c.innerText.replace(/\s+/g, ' '))));
  console.log('cards', await p.evaluate(() => [...document.querySelectorAll('#sit-cards .wg-sd-card')].map((c) => c.innerText.replace(/\s+/g, ' ').slice(0, 400))));
  await p.screenshot({ path: `${outDir}/sit_${tag}_dlg1.png` });
  await p.evaluate(() => { document.querySelector('.wg-sd-body').scrollTop = 520; }); await p.waitForTimeout(150);
  await p.screenshot({ path: `${outDir}/sit_${tag}_dlg2.png` });
  // select the comp "Like this week" row
  await p.click('#sit-cards .wg-sd-row[data-id="comp"]'); await p.waitForTimeout(200);
  await p.evaluate(() => { document.querySelector('.wg-sd-body').scrollTop = 0; }); await p.waitForTimeout(100);
  console.log('lognote', await p.textContent('#sit-lognote'));
  await p.screenshot({ path: `${outDir}/sit_${tag}_dlg_comp.png` });
  // hover a bar
  const box = await p.$('#sit-log svg'); const bb = await box.boundingBox();
  await p.mouse.move(bb.x + bb.width * 0.82, bb.y + bb.height * 0.5); await p.waitForTimeout(250);
  console.log('tip', await p.evaluate(() => { const t = document.querySelector('#sit-log .wg-tip'); return t ? t.innerText.replace(/\n/g, ' | ') + ' op=' + t.style.opacity : null; }));
  await p.screenshot({ path: `${outDir}/sit_${tag}_tip.png` });
  // role filter
  await p.check('#sit-role'); await p.waitForTimeout(200);
  console.log('role', await p.textContent('#sit-role-lab'), await p.evaluate(() => [...document.querySelectorAll('#sit-tiles .rs-card')].map((c) => c.innerText.replace(/\s+/g, ' '))));
  await p.keyboard.press('Escape'); await p.waitForTimeout(200);
  console.log('closed', await p.evaluate(() => !document.querySelector('#sit-dlg').open), 'focus', await p.evaluate(() => document.activeElement && document.activeElement.className));
  // Burden
  await p.fill('.rs-search', 'Burden'); await p.waitForTimeout(200);
  await p.click('#lines-table tbody tr .wg-sitbtn'); await p.waitForTimeout(400);
  console.log('burden tiles', await p.evaluate(() => [...document.querySelectorAll('#sit-tiles .rs-card')].map((c) => c.innerText.replace(/\s+/g, ' '))));
  console.log('burden qb card', await p.evaluate(() => [...document.querySelectorAll('#sit-cards .wg-sd-card')].map((c) => c.innerText.replace(/\s+/g, ' ')).find((t) => t.includes('QB'))));
  await p.screenshot({ path: `${outDir}/sit_${tag}_burden.png` });
  await p.click('.wg-sd-close'); await p.waitForTimeout(150);
  // ATD
  await nav('atd'); await p.click('.ra-reset'); await p.waitForTimeout(150);
  await p.fill('.ra-search', 'Nacua'); await p.fill('.ra-in[data-k="atd_rate"]', '0'); await p.fill('.ra-in[data-k="games"]', '0'); await p.waitForTimeout(200);
  const ab = await p.$('#atd-table tbody tr .wg-sitbtn'); console.log('atd btn', !!ab);
  if (ab) { await ab.click(); await p.waitForTimeout(400); console.log('atd tiles', await p.evaluate(() => [...document.querySelectorAll('#sit-tiles .rs-card')].map((c) => c.innerText.replace(/\s+/g, ' ')))); await p.screenshot({ path: `${outDir}/sit_${tag}_atd.png` }); await p.click('.wg-sd-close'); }
  // cat page sort by situational
  await nav('cat-2'); await p.click('#cat-2 th[data-field="sit_hit"] button'); await p.waitForTimeout(150);
  console.log('cat2 top', await p.evaluate(() => [...document.querySelectorAll('#cat-2 tbody tr')].slice(0, 3).map((tr) => tr.innerText.replace(/\s+/g, ' ').slice(0, 140))));
  await p.screenshot({ path: `${outDir}/sit_${tag}_cat2.png` });
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
