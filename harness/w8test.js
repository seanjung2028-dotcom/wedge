const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, outDir, tag = 'l', w = '1300'] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: +w, height: 950 } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(900);
  const nav = async (pg) => { await p.click('#nfl-btn'); await p.click(`#nfl-menu [data-page="${pg}"]`); await p.waitForTimeout(300); };
  await nav('lines');
  console.log('lines', await p.textContent('.rl-count'));
  await p.selectOption('.rs-show', 'all'); await p.waitForTimeout(100);
  console.log('lines all', await p.textContent('.rl-count'));
  for (const m of ['Workhorse · three-down', 'Deep threat', 'pocket']) { await p.selectOption('.rs-role', m); await p.waitForTimeout(80); console.log(' role', m, await p.textContent('.rl-count')); }
  await p.selectOption('.rs-role', '');
  console.log('role chips', await p.evaluate(() => document.querySelectorAll('#lines-table .wg-role-chip').length));
  for (const m of ['Volume up', 'Stable', 'view']) { await p.selectOption('.rs-mom', m); await p.waitForTimeout(80); console.log(' mom', m, await p.textContent('.rl-count')); }
  await p.selectOption('.rs-mom', '');
  console.log('mom chips', await p.evaluate(() => document.querySelectorAll('#lines-table .wg-mom-chip').length));
  await p.screenshot({ path: `${outDir}/w8_lines_${tag}.png` });
  // outlook on a player prop
  const opened = await p.evaluate(() => { const b = document.querySelector('#lines-table .wg-sitbtn'); if (b) b.click(); return !!b; });
  await p.waitForTimeout(700);
  console.log('outlook open', opened, await p.evaluate(() => { const d = document.querySelector('#sit-dlg'); return d && d.open ? (d.querySelector('#sit-title').textContent + ' | ' + [...d.querySelectorAll('.wg-note')].map((n) => n.textContent).join(' || ').slice(0, 500)) : 'closed'; }));
  console.log('recent form', await p.evaluate(() => [...document.querySelectorAll('#sit-p-ov h3')].map((h) => h.textContent).join(', ')));
  console.log('role rows', await p.evaluate(() => document.querySelectorAll('#sit-p-ov .wg-dh tbody tr').length));
  await p.evaluate(() => document.querySelector('#sit-t-mu').click()); await p.waitForTimeout(400);
  console.log('matchup secs', await p.evaluate(() => [...document.querySelectorAll('#sit-p-mu h3')].map((h) => h.textContent).join(', ')), await p.evaluate(() => document.querySelectorAll('#sit-p-mu .wg-dh tbody tr').length));
  await p.screenshot({ path: `${outDir}/w8_outlook_mu_${tag}.png` });
  await p.evaluate(() => document.querySelector('#sit-t-ov').click()); await p.waitForTimeout(300);
  await p.screenshot({ path: `${outDir}/w8_outlook_${tag}.png` });
  await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  for (const k of ['cat-1', 'cat-2', 'cat-3', 'cat-4']) { await nav(k); await p.selectOption(`#${k} .rc-show`, 'all'); await p.waitForTimeout(60); console.log(k, await p.textContent(`#${k} .rc-count`)); }
  await nav('atd'); console.log('atd', await p.textContent('.ra-count'));
  await nav('proj');
  console.log('proj', await p.textContent('.pj-count'));
  for (const m of ['Role up', 'view']) { await p.selectOption('.pj-mom', m); await p.waitForTimeout(80); console.log(' pj mom', m, await p.textContent('.pj-count')); }
  await p.selectOption('.pj-mom', '');
  await p.selectOption('.pj-mkt', 'Passing Yards'); await p.waitForTimeout(80); console.log(' pj pass', await p.textContent('.pj-count'));
  await p.selectOption('.pj-mkt', '');
  await p.screenshot({ path: `${outDir}/w8_proj_${tag}.png` });
  await p.evaluate(() => { const b = document.querySelector('#proj-table .wg-sitbtn'); if (b) b.click(); });
  await p.waitForTimeout(700);
  console.log('proj outlook', await p.evaluate(() => { const d = document.querySelector('#sit-dlg'); return d && d.open ? (d.querySelector('#sit-title').textContent + ' | ' + d.querySelector('.wg-lab').textContent + ' | ' + d.querySelector('.wg-big').textContent + ' | ' + d.querySelector('.wg-note').textContent.slice(0, 400)) : 'closed'; }));
  await p.screenshot({ path: `${outDir}/w8_projout_${tag}.png` });
  await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  await p.click('.rs-tab[data-page="charts"]'); await p.waitForTimeout(700);
  console.log('chart svgs', await p.evaluate(() => ['#ch-recency', '#ch-defsig', '#ch-weeks-chart', '#ch-weeks-all', '#ch-props-chart', '#ch-mom-persist', '#ch-mom-acc', '#ch-mom-cat', '#ch-mom-real', '#ch-teams-chart'].map((q) => { const b = document.querySelector(q); const s = b && b.querySelector('svg'); return q + ':' + (s ? s.querySelectorAll('rect,circle,path').length : 'none'); }).join(' ')));
  console.log('var text', (await p.textContent('#ch-mom-var')).slice(0, 300));
  console.log('cats', await p.textContent('.ct-count'), (await p.textContent('#ch-research-var')).slice(0, 200));
  for (const k of ['held', 'under', 'all']) { await p.selectOption('.ct-kind', k); await p.waitForTimeout(100); console.log(' cats', k, await p.textContent('.ct-count')); }
  await p.selectOption('.ct-kind', 'held');
  for (const g of ['WR receiving yards', 'QB passing yards']) { await p.selectOption('.ds2-grp', g); await p.waitForTimeout(100); }
  await p.selectOption('.ds2-grp', 'RB rushing yards'); await p.selectOption('.rc2-comp', 'RB rush'); await p.waitForTimeout(200);
  const t0 = await p.evaluate(() => document.querySelector('#ch-cats').getBoundingClientRect().top + window.scrollY);
  await p.evaluate((y) => window.scrollTo(0, y - 10), t0); await p.waitForTimeout(200);
  await p.screenshot({ path: `${outDir}/w8_charts0_${tag}.png` });
  const t5 = await p.evaluate(() => document.querySelector('#ch-research').getBoundingClientRect().top + window.scrollY);
  await p.evaluate((y) => window.scrollTo(0, y - 10), t5); await p.waitForTimeout(200);
  await p.screenshot({ path: `${outDir}/w8_charts5_${tag}.png` });
  for (const g of ['Market', 'Side (game lines)', 'Price band']) { await p.selectOption('.chw-grp', g); await p.waitForTimeout(120); }
  for (const f of ['Momentum', 'Team total', 'Position']) { await p.selectOption('.chp-fac', f); await p.waitForTimeout(120); }
  await p.selectOption('.chm-stat', 'rushyd'); await p.waitForTimeout(120);
  await p.selectOption('.chw-grp', 'Strategy'); await p.selectOption('.chp-fac', 'Stat'); await p.waitForTimeout(200);
  const top = await p.evaluate(() => document.querySelector('#ch-weeks').getBoundingClientRect().top + window.scrollY);
  await p.evaluate((y) => window.scrollTo(0, y - 10), top); await p.waitForTimeout(200);
  await p.screenshot({ path: `${outDir}/w8_charts1_${tag}.png` });
  const t2 = await p.evaluate(() => document.querySelector('#ch-props').getBoundingClientRect().top + window.scrollY);
  await p.evaluate((y) => window.scrollTo(0, y - 10), t2); await p.waitForTimeout(200);
  await p.screenshot({ path: `${outDir}/w8_charts2_${tag}.png` });
  const t3 = await p.evaluate(() => document.querySelector('#ch-mom').getBoundingClientRect().top + window.scrollY);
  await p.evaluate((y) => window.scrollTo(0, y - 10), t3); await p.waitForTimeout(200);
  await p.screenshot({ path: `${outDir}/w8_charts3_${tag}.png` });
  const t4 = await p.evaluate(() => document.querySelector('#ch-teams').getBoundingClientRect().top + window.scrollY);
  await p.evaluate((y) => window.scrollTo(0, y - 10), t4); await p.waitForTimeout(200);
  await p.screenshot({ path: `${outDir}/w8_charts4_${tag}.png` });
  console.log('hscroll', await p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth));
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
