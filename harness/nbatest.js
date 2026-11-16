const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, outDir, tag, w, h] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: +(w || 1300), height: +(h || 950) } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(900);
  await p.click('.rs-tab[data-page="nba"]'); await p.waitForTimeout(400);
  const txt = (sel) => p.evaluate((s) => [...document.querySelectorAll(s)].map((c) => c.innerText.replace(/\s+/g, ' ').slice(0, 220)), sel);
  console.log('tiles', await txt('#nba-tiles .rs-card'));
  console.log('rows', (await txt('#nba-table tbody tr')).slice(0, 8));
  await p.screenshot({ path: `${outDir}/n_${tag}_top.png` });
  await p.evaluate(() => document.querySelector('#nba-lines-card').scrollIntoView()); await p.waitForTimeout(200);
  await p.screenshot({ path: `${outDir}/n_${tag}_table.png` });
  await p.selectOption('.nb-group', 'Player props'); await p.waitForTimeout(150);
  console.log('count', await p.textContent('.nb-count'));
  const btn = await p.$('#nba-table tbody .wg-sitbtn'); await btn.click(); await p.waitForTimeout(1200);
  console.log('head', await txt('.wg-sd-head'));
  console.log('hero', await txt('#sit-p-ov .wg-hero2 .wg-card'));
  console.log('wf', await txt('#sit-p-ov .wg-wf-row'));
  console.log('cases', await txt('#sit-p-ov .wg-sc'));
  await p.screenshot({ path: `${outDir}/n_${tag}_ov.png` });
  await p.click('#sit-t-mu'); await p.waitForTimeout(900);
  console.log('mu chips', await txt('#sit-p-mu .wg-chips .wg-card'));
  console.log('mu scen', await txt('#sit-p-mu .wg-sc'));
  console.log('mu def', await txt('#sit-p-mu .wg-met'));
  console.log('mu tbl', await txt('#sit-p-mu .wg-tbl tbody tr'));
  await p.screenshot({ path: `${outDir}/n_${tag}_mu.png` });
  await p.click('#sit-t-hi'); await p.waitForTimeout(900);
  console.log('lognote', await p.textContent('#sit-lognote'));
  console.log('splits', await txt('#sit-splits .wg-sp'));
  await p.screenshot({ path: `${outDir}/n_${tag}_hi.png` });
  const bars = await p.$$('#sit-log rect'); if (bars.length > 30) { const bb = await bars[bars.length - 3].boundingBox(); await p.mouse.move(bb.x + bb.width / 2, bb.y + 5); await p.waitForTimeout(200);
    console.log('tip', await p.evaluate(() => { const t = document.querySelector('#sit-log .wg-tip'); return t ? t.innerText.replace(/\n/g, ' | ') : null; })); }
  await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  // open every NBA outlook once
  const btns = await p.$$('#nba-table tbody .wg-sitbtn'); let bad = 0;
  for (let k = 0; k < btns.length; k += 3) { await btns[k].click(); await p.waitForTimeout(500); const ok = await p.evaluate(() => document.querySelector('#sit-dlg').open && document.querySelector('#sit-p-ov').childElementCount > 2); if (!ok) bad++; await p.click('#sit-t-mu'); await p.click('#sit-t-hi'); await p.keyboard.press('Escape'); await p.waitForTimeout(220); }
  console.log('opened', Math.ceil(btns.length / 3), 'bad', bad);
  await p.evaluate(() => document.querySelector('#nba-by-game').scrollIntoView()); await p.waitForTimeout(200);
  await p.screenshot({ path: `${outDir}/n_${tag}_bygame.png` });
  await p.click('.rs-tab[data-page="soccer"]'); await p.waitForTimeout(300);
  await p.screenshot({ path: `${outDir}/n_${tag}_soccer.png` });
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
