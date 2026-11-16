const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, w = '1300'] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: 950 } });
  const logs = []; p.on('pageerror', (e) => logs.push('ERR ' + e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push('CONSOLE ' + m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(1600);
  const nav = async (dd, pg) => { await p.click(`#${dd}-btn`); await p.click(`#${dd}-menu [data-page="${pg}"]`); await p.waitForTimeout(700); };
  await nav('nfl', 'research');
  console.log('research', await p.textContent('.rl-count'), 'rows', await p.$$eval('#lines-table tbody tr', (x) => x.length), 'clickable', await p.$$eval('#lines-table tbody tr.wg-click', (x) => x.length), 'pj cells', await p.$$eval('#lines-table td.v2-pj b', (x) => x.length));
  await p.screenshot({ path: out + '/research.png' });
  // a row with a full outlook
  await p.evaluate(() => { const b = document.querySelector('#lines-table .wg-sitbtn'); b.click(); });
  await p.waitForTimeout(1300);
  console.log('file open', await p.evaluate(() => [document.querySelector('#sit-dlg').open, document.querySelector('#sit-title').textContent]));
  await p.screenshot({ path: out + '/file_ov.png' });
  await p.click('#sit-t-inj'); await p.waitForTimeout(900); await p.screenshot({ path: out + '/file_inj.png' });
  await p.click('#sit-t-mu'); await p.waitForTimeout(1000); await p.screenshot({ path: out + '/file_gs.png' });
  await p.evaluate(() => { document.querySelector('.wg-sd-body').scrollTop = 900; }); await p.waitForTimeout(300); await p.screenshot({ path: out + '/file_gs2.png' });
  await p.keyboard.press('Escape'); await p.waitForTimeout(400);
  // a row without a full outlook (lite file): a Pickens line
  await p.fill('.rs-search', 'pickens'); await p.waitForTimeout(400);
  console.log('pickens rows', await p.$$eval('#lines-table tbody tr', (x) => x.length));
  await p.evaluate(() => { const r = [...document.querySelectorAll('#lines-table tbody tr.v2-click')].find((t) => /Receiving Yards/.test(t.textContent)) || document.querySelector('#lines-table tbody tr.v2-click'); r.click(); });
  await p.waitForTimeout(1300);
  console.log('lite open', await p.evaluate(() => [document.querySelector('#sit-dlg').open, document.querySelector('#sit-title').textContent, document.querySelector('#sit-dlg').className]));
  await p.screenshot({ path: out + '/lite_ov.png' });
  await p.click('#sit-t-inj'); await p.waitForTimeout(1000); await p.screenshot({ path: out + '/lite_inj.png' });
  await p.click('#sit-t-mu'); await p.waitForTimeout(1000); await p.screenshot({ path: out + '/lite_gs.png' });
  await p.keyboard.press('Escape'); await p.waitForTimeout(400);
  await p.fill('.rs-search', ''); await p.waitForTimeout(300);
  await nav('nfl', 'final'); await p.waitForTimeout(500);
  await p.screenshot({ path: out + '/edge.png' });
  await nav('nfl', 'thesis'); await p.waitForTimeout(800);
  await p.screenshot({ path: out + '/thesis.png', fullPage: true });
  for (const pg of ['charts', 'analysts', 'results']) { await nav('nfl', pg); await p.screenshot({ path: out + `/db_${pg}.png` }); }
  for (const pg of ['nba', 'nba-edge', 'nba-charts', 'nba-results']) { await nav('nba', pg); await p.waitForTimeout(500); await p.screenshot({ path: out + `/${pg}.png` }); }
  await p.click('.rs-tab[data-page="soccer"]'); await p.waitForTimeout(400); await p.screenshot({ path: out + '/soccer.png' });
  // Home: matchup -> reads
  await p.click('.rs-tab[data-page="lobby"]'); await p.waitForTimeout(600);
  await p.click('#v2-mgrid .v2-mt[data-game="TB @ CHI"]'); await p.waitForTimeout(1400);
  const r = await p.evaluate(() => { const s = document.querySelector('#wz-reads'); return [s.hidden, s.querySelectorAll('.v2-read').length, Math.round(s.getBoundingClientRect().top)]; });
  console.log('reads', r);
  await p.screenshot({ path: out + '/reads.png' });
  await p.click('#wg-hot-cards .v2-read'); await p.waitForTimeout(1200);
  console.log('after read click', await p.evaluate(() => [document.querySelector('#final').hidden, [...document.querySelectorAll('.fc-game')].filter((d) => d.open).map((d) => d.id)]));
  await p.screenshot({ path: out + '/edge_play.png' });
  console.log(logs.slice(0, 15).join('\n'));
  await b.close();
})();
