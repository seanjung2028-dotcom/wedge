const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, outDir, tag = 'l', w = '1300'] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: +w, height: 950 } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(900);
  await p.click('#nfl-btn'); await p.click('#nfl-menu [data-page="final"]'); await p.waitForTimeout(600);
  const info = await p.evaluate(() => ({
    when: document.querySelector('#fc-when')?.textContent,
    stats: [...document.querySelectorAll('.fc-stat')].map((s) => s.textContent).join(' | '),
    board: document.querySelectorAll('.fc-board tbody tr').length,
    games: document.querySelectorAll('.fc-game').length,
    plays: document.querySelectorAll('.fc-play').length,
    ladders: document.querySelectorAll('.fc-lad').length,
    ladderRows: document.querySelectorAll('.fc-ladbox tbody tr').length,
    cardTags: document.querySelectorAll('.fc-lr-card').length,
    passed: document.querySelectorAll('.fc-passed li').length,
    dts: [...new Set([...document.querySelectorAll('.fc-play .fc-dl dt')].map((d) => d.textContent))].join(', '),
    backtest: document.querySelector('#final').textContent.includes('backtest') ? [...document.querySelector('#final').textContent.matchAll(/.{60}backtest.{40}/g)].map((m) => m[0]) : [],
    overflowX: document.documentElement.scrollWidth > window.innerWidth,
  }));
  console.log(JSON.stringify(info, null, 1));
  await p.screenshot({ path: `${outDir}/fc_top_${tag}.png` });
  // open the Bears game (has a final line and leans) and shoot the first play
  await p.evaluate(() => { const r = [...document.querySelectorAll('.fc-board tbody tr')][0]; r.click(); });
  await p.waitForTimeout(900);
  const g = await p.evaluate(() => { const d = [...document.querySelectorAll('.fc-game')].find((x) => x.open); return d ? d.id : null; });
  console.log('opened', g);
  const play = await p.$('.fc-game[open] .fc-play');
  if (play) await play.screenshot({ path: `${outDir}/fc_play_${tag}.png` });
  const rk = await p.$('.fc-game[open] .fc-rank'); if (rk) await rk.screenshot({ path: `${outDir}/fc_rank_${tag}.png` });
  const ps = await p.$('.fc-game[open] .fc-passed'); if (ps) await ps.screenshot({ path: `${outDir}/fc_passed_${tag}.png` });
  console.log('errors', logs.length, logs.slice(0, 5));
  await b.close();
})();
