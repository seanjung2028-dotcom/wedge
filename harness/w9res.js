const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 950 } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message));
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(1200);
  console.log('record', (await p.evaluate(() => { const e = document.querySelector('.wg-record, #wg-record, [class*="record"]'); return e ? e.textContent.replace(/\s+/g, ' ').trim() : 'none'; })));
  await p.click('#nfl-btn'); await p.click('#nfl-menu [data-page="results"]'); await p.waitForTimeout(400);
  console.log('wk opts', await p.evaluate(() => [...document.querySelectorAll('.rr-week option')].map((o) => o.value + (o.selected ? '*' : '')).join(',')));
  console.log('res q', await p.textContent('.rr-count'));
  await p.selectOption('.rr-show', 'all'); await p.waitForTimeout(100); console.log('res all', await p.textContent('.rr-count'));
  await p.selectOption('.rr-show', 'atd'); await p.waitForTimeout(100); console.log('res atd', await p.textContent('.rr-count'));
  await p.selectOption('.rr-show', 'q');
  await p.check('.rr-certonly'); await p.waitForTimeout(200); console.log('res cert', await p.textContent('.rr-count'),
    await p.evaluate(() => [...document.querySelectorAll('#results-table tbody tr')].map((tr) => [...tr.children].slice(1).map((t) => t.textContent.trim()).join(' | ')).join('\n')));
  await p.screenshot({ path: process.argv[3] + '/w9_results.png' });
  await p.click('.rs-tab[data-page="analysts"]').catch(() => {}); await p.waitForTimeout(500);
  console.log('analysts weeks', await p.evaluate(() => [...document.querySelectorAll('.an-week option')].map((o) => o.textContent).join(',')));
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
