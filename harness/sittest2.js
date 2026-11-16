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
  console.log('rows', await p.evaluate(() => [...document.querySelectorAll('#lines-table tbody tr')].map((tr) => tr.innerText.replace(/\s+/g, ' ').slice(0, 170))));
  await p.screenshot({ path: `${outDir}/s2_${tag}_table.png` });
  const rows = await p.$$('#lines-table tbody tr');
  for (const r of rows) { if ((await r.innerText()).includes('100+ rec yds')) { await r.click({ position: { x: 360, y: 12 } }); break; } }
  await p.waitForTimeout(140);
  await p.screenshot({ path: `${outDir}/s2_${tag}_anim.png` });
  await p.waitForTimeout(1100);
  console.log('hero', await p.evaluate(() => [...document.querySelectorAll('#sit-hero .wg-hero-card')].map((c) => c.innerText.replace(/\s+/g, ' '))));
  console.log('odds', await p.evaluate(() => document.querySelector('#sit-odds').getAttribute('aria-label')));
  console.log('scen', await p.evaluate(() => [...document.querySelectorAll('#sit-scen .wg-sc')].map((c) => c.innerText.replace(/\s+/g, ' '))));
  console.log('splits', await p.evaluate(() => [...document.querySelectorAll('#sit-splits .wg-sp')].map((c) => c.innerText.replace(/\s+/g, ' ').slice(0, 220))));
  await p.screenshot({ path: `${outDir}/s2_${tag}_top.png` });
  await p.evaluate(() => { document.querySelector('.wg-sd-body').scrollTop = 560; }); await p.waitForTimeout(250);
  await p.screenshot({ path: `${outDir}/s2_${tag}_mid.png` });
  await p.click('#sit-splits .wg-sp-row[data-id="comp"]'); await p.waitForTimeout(300);
  console.log('lognote', await p.textContent('#sit-lognote'));
  await p.evaluate(() => { document.querySelector('.wg-sd-body').scrollTop = 1100; }); await p.waitForTimeout(250);
  await p.screenshot({ path: `${outDir}/s2_${tag}_low.png` });
  await p.evaluate(() => { document.querySelector('#sit-more').open = true; document.querySelector('.wg-sd-body').scrollTop = 99999; }); await p.waitForTimeout(250);
  await p.screenshot({ path: `${outDir}/s2_${tag}_more.png` });
  // range dot hover
  await p.evaluate(() => { document.querySelector('#sit-range').scrollIntoView(); }); await p.waitForTimeout(150);
  const dot = await p.$('#sit-range circle'); if (dot) { await dot.hover(); await p.waitForTimeout(200); console.log('rtip', await p.evaluate(() => { const t = document.querySelector('#sit-range .wg-tip'); return t ? t.innerText.replace(/\n/g, ' | ') : null; })); }
  await p.check('#sit-role'); await p.waitForTimeout(900);
  console.log('role', await p.textContent('#sit-role-lab'), await p.evaluate(() => [...document.querySelectorAll('#sit-hero .wg-hero-card')].map((c) => c.innerText.replace(/\s+/g, ' ').slice(0, 90))));
  await p.keyboard.press('Escape'); await p.waitForTimeout(80);
  console.log('closing class', await p.evaluate(() => document.querySelector('#sit-dlg').className));
  await p.waitForTimeout(300);
  console.log('closed', await p.evaluate(() => !document.querySelector('#sit-dlg').open), 'focus', await p.evaluate(() => document.activeElement && document.activeElement.className));
  // model consistency: hero vs table for many rows
  await p.fill('.rs-search', ''); await p.selectOption('.rs-group', 'Player props'); await p.waitForTimeout(200);
  const btns = await p.$$('#lines-table tbody .wg-sitbtn'); let mism = 0, checked = 0;
  for (let k = 0; k < btns.length && checked < 40; k += Math.max(1, Math.floor(btns.length / 40))) {
    const tableV = await btns[k].evaluate((x) => x.querySelector('b').textContent);
    await btns[k].click(); await p.waitForTimeout(800);
    const heroV = await p.evaluate(() => document.querySelector('#sit-hero .wg-hero-num span').textContent + '%');
    if (tableV !== heroV) { mism++; console.log('MISMATCH', tableV, heroV, await p.textContent('#sit-title')); }
    checked++;
    await p.keyboard.press('Escape'); await p.waitForTimeout(260);
  }
  console.log('model check', checked, 'mismatches', mism);
  // ATD
  await nav('atd'); await p.click('.ra-reset'); await p.waitForTimeout(150);
  await p.fill('.ra-search', 'Gibbs'); await p.fill('.ra-in[data-k="atd_rate"]', '0'); await p.fill('.ra-in[data-k="games"]', '0'); await p.waitForTimeout(200);
  console.log('atd rows', await p.evaluate(() => [...document.querySelectorAll('#atd-table tbody tr')].map((tr) => tr.innerText.replace(/\s+/g, ' ').slice(0, 120))));
  const ab = await p.$('#atd-table tbody tr .wg-sitbtn');
  if (ab) { await ab.click(); await p.waitForTimeout(1100); console.log('atd hero', await p.evaluate(() => [...document.querySelectorAll('#sit-hero .wg-hero-card')].map((c) => c.innerText.replace(/\s+/g, ' ')))); await p.screenshot({ path: `${outDir}/s2_${tag}_atd.png` }); await p.keyboard.press('Escape'); await p.waitForTimeout(300); }
  await nav('lines'); await p.evaluate(() => document.querySelector('#by-game').scrollIntoView()); await p.waitForTimeout(150);
  await p.screenshot({ path: `${outDir}/s2_${tag}_bygame.png` });
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
