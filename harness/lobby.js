const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, width, scheme] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: Number(width), height: 900 }, colorScheme: scheme || 'light' });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file);
  await p.waitForTimeout(700);
  await p.screenshot({ path: out.replace('.png', '_mid.png') });
  await p.waitForTimeout(2200);
  await p.screenshot({ path: out });
  const vis = await p.evaluate(() => ({ lobby: !document.querySelector('#lobby').hidden, lines: !document.querySelector('#lines').hidden, method: !document.querySelector('#method').hidden, sel: document.querySelector('.rs-tab[aria-selected=true]').id }));
  await p.click('.wg-go-primary'); await p.waitForTimeout(200);
  const after = await p.evaluate(() => ({ lines: !document.querySelector('#lines').hidden, method: !document.querySelector('#method').hidden, sel: document.querySelector('.rs-tab[aria-selected=true]').id, rows: document.querySelectorAll('#lines-table tbody tr').length }));
  console.log(JSON.stringify(vis), JSON.stringify(after), JSON.stringify(logs));
  await b.close();
})();
