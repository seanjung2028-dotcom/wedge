const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 950 } });
  await p.goto('file://' + process.argv[2]); await p.waitForTimeout(900);
  await p.click('#nfl-btn'); await p.click('#nfl-menu [data-page="lines"]'); await p.waitForTimeout(300);
  await p.selectOption('.rs-show', 'all'); await p.waitForTimeout(100);
  console.log(await p.evaluate(() => [...document.querySelectorAll('#lines-table tbody tr')].slice(0, 3).map((tr) => tr.getBoundingClientRect().height + ' :: ' + [...tr.children].map((td) => td.textContent.trim().slice(0, 120)).join(' | ')).join('\n')));
  await b.close();
})();
