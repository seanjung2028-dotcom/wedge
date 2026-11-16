const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, outDir, tag, w, h, who] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: +(w || 1300), height: +(h || 950) } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(900);
  const nav = async (pg) => { await p.click('#nfl-btn'); await p.click(`#nfl-menu [data-page="${pg}"]`); await p.waitForTimeout(250); };
  await nav('lines');
  await p.selectOption('.rs-show', 'all'); await p.fill('.rs-search', who || 'Nacua'); await p.waitForTimeout(200);
  console.log('rows', await p.evaluate(() => [...document.querySelectorAll('#lines-table tbody tr')].slice(0, 8).map((tr) => tr.innerText.replace(/\s+/g, ' ').slice(0, 170))));
  const btn = await p.$('#lines-table tbody .wg-sitbtn');
  await btn.click(); await p.waitForTimeout(160);
  await p.screenshot({ path: `${outDir}/s3_${tag}_anim.png` });
  await p.waitForTimeout(1100);
  const txt = (sel) => p.evaluate((s) => [...document.querySelectorAll(s)].map((c) => c.innerText.replace(/\s+/g, ' ').slice(0, 260)), sel);
  console.log('head', await txt('.wg-sd-head'));
  console.log('hero', await txt('#sit-p-ov .wg-hero2 .wg-card'));
  console.log('wf', await txt('#sit-p-ov .wg-wf-row'));
  console.log('cases', await txt('#sit-p-ov .wg-sc'));
  await p.screenshot({ path: `${outDir}/s3_${tag}_ov.png` });
  await p.evaluate(() => { document.querySelector('.wg-sd-body').scrollTop = 99999; }); await p.waitForTimeout(250);
  await p.screenshot({ path: `${outDir}/s3_${tag}_ov2.png` });
  await p.click('#sit-t-mu'); await p.waitForTimeout(900);
  console.log('mu chips', await txt('#sit-p-mu .wg-chips .wg-card'));
  console.log('mu scen', await txt('#sit-p-mu .wg-sc'));
  console.log('mu def', await txt('#sit-p-mu .wg-met'));
  console.log('mu tbl', await txt('#sit-p-mu .wg-tbl tbody tr'));
  await p.screenshot({ path: `${outDir}/s3_${tag}_mu.png` });
  await p.evaluate(() => { document.querySelector('.wg-sd-body').scrollTop = 99999; }); await p.waitForTimeout(250);
  await p.screenshot({ path: `${outDir}/s3_${tag}_mu2.png` });
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(900);
  console.log('active tab', await p.evaluate(() => document.activeElement.id));
  console.log('lognote', await p.textContent('#sit-lognote'));
  console.log('splits', await txt('#sit-splits .wg-sp'));
  await p.screenshot({ path: `${outDir}/s3_${tag}_hi.png` });
  const r2 = await p.$('#sit-splits .wg-sp-row:not([aria-pressed=true])'); if (r2) { await r2.click(); await p.waitForTimeout(300); console.log('lognote2', await p.textContent('#sit-lognote')); }
  await p.keyboard.press('Escape'); await p.waitForTimeout(80);
  console.log('closing class', await p.evaluate(() => document.querySelector('#sit-dlg').className));
  await p.waitForTimeout(300);
  console.log('closed', await p.evaluate(() => !document.querySelector('#sit-dlg').open), 'focus', await p.evaluate(() => document.activeElement && document.activeElement.className));
  // consistency table vs hero, and every outlook opens without errors
  await p.fill('.rs-search', ''); await p.selectOption('.rs-group', 'Player props'); await p.waitForTimeout(200);
  const btns = await p.$$('#lines-table tbody .wg-sitbtn'); let mism = 0, checked = 0, noopen = 0;
  for (let k = 0; k < btns.length && checked < 30; k += Math.max(1, Math.floor(btns.length / 30))) {
    const tableV = await btns[k].evaluate((x) => x.querySelector('b').textContent);
    await btns[k].click(); await p.waitForTimeout(750);
    const open = await p.evaluate(() => document.querySelector('#sit-dlg').open);
    if (!open) { noopen++; checked++; continue; }
    const heroV = await p.evaluate(() => document.querySelector('#sit-p-ov .wg-big span').textContent + '%');
    if (tableV !== heroV) { mism++; console.log('MISMATCH', tableV, heroV, await p.textContent('#sit-title')); }
    await p.click('#sit-t-mu'); await p.waitForTimeout(120); await p.click('#sit-t-hi'); await p.waitForTimeout(120);
    checked++;
    await p.keyboard.press('Escape'); await p.waitForTimeout(260);
  }
  console.log('model check', checked, 'mismatches', mism, 'not opened', noopen, 'buttons', btns.length);
  await nav('atd'); await p.click('.ra-reset'); await p.waitForTimeout(150);
  await p.fill('.ra-search', 'Gibbs'); await p.fill('.ra-in[data-k="atd_rate"]', '0'); await p.fill('.ra-in[data-k="games"]', '0'); await p.waitForTimeout(200);
  const ab = await p.$('#atd-table tbody tr .wg-sitbtn');
  if (ab) { await ab.click(); await p.waitForTimeout(1100); console.log('atd hero', await txt('#sit-p-ov .wg-hero2 .wg-card')); await p.screenshot({ path: `${outDir}/s3_${tag}_atd.png` });
    await p.click('#sit-t-mu'); await p.waitForTimeout(900); await p.screenshot({ path: `${outDir}/s3_${tag}_atd_mu.png` }); await p.keyboard.press('Escape'); await p.waitForTimeout(300); }
  await nav('backtest'); await p.evaluate(() => document.querySelector('#bt-model').scrollIntoView()); await p.waitForTimeout(900);
  await p.screenshot({ path: `${outDir}/s3_${tag}_bt.png` });
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
