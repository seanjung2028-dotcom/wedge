const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, outdir] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 900 } });
  const logs = []; p.on('pageerror', (e) => logs.push('ERR ' + e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(2000);
  // header state
  console.log('hdr', await p.evaluate(() => ['#wz-login', '#wz-signup', '#wz-me', '#wz-gopro'].map((s) => s + ':' + (getComputedStyle(document.querySelector(s)).display !== 'none')).join(' ')));
  // sign up free
  await p.click('#wz-signup'); await p.waitForTimeout(400);
  console.log('dlg open', await p.evaluate(() => document.querySelector('#wz-dlg').open), await p.textContent('#wz-dlg-h'), 'first prefill', await p.inputValue('#wz-f-first'));
  await p.screenshot({ path: outdir + '/wz_dlg.png' });
  await p.click('.wz-planpick [data-plan="free"]'); await p.fill('#wz-f-email', 'bad'); await p.click('#wz-go'); await p.waitForTimeout(200);
  console.log('invalid msg', await p.textContent('#wz-msg'));
  await p.fill('#wz-f-email', 'fan@example.com'); await p.selectOption('#wz-f-team', 'DEN'); await p.click('#wz-go'); await p.waitForTimeout(400);
  console.log('done', await p.textContent('#wz-done-text'), 'store', await p.evaluate(() => JSON.stringify(window.__store['data/users/u_harness_viewer/wedge-account'] || null)));
  await p.click('#wz-done-ok'); await p.waitForTimeout(300);
  console.log('hdr2', await p.evaluate(() => ['#wz-login', '#wz-me', '#wz-gopro'].map((s) => s + ':' + (getComputedStyle(document.querySelector(s)).display !== 'none')).join(' ')), await p.textContent('#wz-me'));
  console.log('fav tab', await p.evaluate(() => (document.querySelector('.wx-tab[aria-selected="true"]') || {}).dataset.game), 'banner', await p.evaluate(() => !document.querySelector('#wz-matchup').hidden && document.querySelector('#wz-matchup').getAttribute('aria-label')));
  // banner screenshot
  await p.evaluate(() => document.querySelector('#wz-reads').scrollIntoView()); await p.waitForTimeout(900);
  await p.screenshot({ path: outdir + '/wz_reads_game.png' });
  // go pro (monthly) with an existing profile -> straight to checkout (mailto)
  await p.evaluate(() => { const a = document.querySelector('#wz-done-link'); a.addEventListener('click', (e) => { window.__mail = a.href; e.preventDefault(); }); });
  await p.click('#wz-gopro'); await p.waitForTimeout(400);
  console.log('checkout', await p.textContent('#wz-done-text'), (await p.evaluate(() => window.__mail || '')).slice(0, 90));
  await p.click('#wz-done-ok'); await p.waitForTimeout(200);
  console.log('plan chip', await p.textContent('#wz-me-plan'));
  // account view
  await p.click('#wz-me'); await p.waitForTimeout(300);
  console.log('acct', (await p.textContent('#wz-acct-dl')).replace(/\s+/g, ' '));
  await p.keyboard.press('Escape'); await p.waitForTimeout(200);
  // nav: NFL menu position and lines page
  await p.click('#nfl-btn'); await p.waitForTimeout(200);
  const mb = await p.evaluate(() => { const m = document.querySelector('#nfl-menu').getBoundingClientRect(), b = document.querySelector('#nfl-btn').getBoundingClientRect(); return [Math.round(m.left), Math.round(b.left), Math.round(m.top), Math.round(b.bottom), !document.querySelector('#nfl-menu').hidden]; });
  console.log('menu', JSON.stringify(mb));
  await p.screenshot({ path: outdir + '/wz_menu.png', clip: { x: 0, y: 0, width: 700, height: 600 } });
  await p.click('#nfl-menu [data-page="lines"]'); await p.waitForTimeout(800);
  const cols = await p.evaluate(() => { const t = document.querySelector('#lines-table'); const vis = [...t.tHead.rows[0].cells].filter((c) => getComputedStyle(c).display !== 'none').map((c) => c.dataset.field || c.className); const r = t.tBodies[0].rows[0]; return { vis, head: t.tHead.rows[0].cells.length, body: r ? r.cells.length : 0, bodyVis: r ? [...r.cells].filter((c) => getComputedStyle(c).display !== 'none').length : 0 }; });
  console.log('cols', JSON.stringify(cols));
  await p.screenshot({ path: outdir + '/wz_lines.png' });
  await p.click('#lines-card .wz-filters > summary'); await p.waitForTimeout(250);
  await p.screenshot({ path: outdir + '/wz_filters.png' });
  await p.selectOption('#lines-card .rs-src', 'Robinhood'); await p.waitForTimeout(200);
  console.log('filter badge', await p.textContent('#lines-card .wz-filters > summary'), await p.textContent('.rl-count'));
  await p.click('#lines-card h2'); await p.waitForTimeout(150);
  console.log('popover closed', await p.evaluate(() => !document.querySelector('#lines-card .wz-filters').open));
  await p.click('#lines-card .wz-cols'); await p.waitForTimeout(200);
  console.log('more cols', await p.evaluate(() => [...document.querySelector('#lines-table').tHead.rows[0].cells].filter((c) => getComputedStyle(c).display !== 'none').length), await p.textContent('#lines-card .wz-cols'));
  await p.click('#lines-card .wz-cols');
  // logo -> lobby
  await p.click('.wz-logo'); await p.waitForTimeout(500);
  console.log('logo->lobby', await p.evaluate(() => !document.querySelector('#lobby').hidden && document.querySelector('#lines').hidden));
  // cat page + atd simple
  for (const pg of ['cat-1', 'atd', 'proj', 'nba']) {
    await p.evaluate((pg) => { const b = document.querySelector(`[data-page="${pg}"]`); b.click(); }, pg); await p.waitForTimeout(500);
    console.log(pg, await p.evaluate((pg) => { const t = document.querySelector(`#${pg === 'cat-1' ? 'cat-1-table' : pg === 'nba' ? 'nba-table' : pg + '-table'}`); const r = t.tBodies[0].rows[0]; return [ [...t.tHead.rows[0].cells].filter((c) => getComputedStyle(c).display !== 'none').map((c) => c.dataset.field || 'x').join(','), r ? r.cells.length + '/' + t.tHead.rows[0].cells.length : 'norow']; }, pg));
  }
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
