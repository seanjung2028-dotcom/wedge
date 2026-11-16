const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, outDir] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1300, height: 900 } });
  const logs = [];
  p.on('pageerror', (e) => logs.push('pageerror: ' + e.message));
  p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file);
  await p.waitForTimeout(600);
  const info = await p.evaluate(() => ({
    owner: document.querySelector('.rs-wrap').classList.contains('wg-owner'),
    boxes: document.querySelectorAll('#lines-table .wg-certbox').length,
    badges: document.querySelectorAll('#lines-table .wg-cert').length,
    certifiedRows: document.querySelectorAll('#lines-table tr.wg-certified').length,
    colVisible: getComputedStyle(document.querySelector('#lines-table th.wg-certcol')).display,
  }));
  console.log('initial', JSON.stringify(info));
  await p.screenshot({ path: outDir + '/cert_lines.png', clip: { x: 0, y: 380, width: 1300, height: 520 } });
  if (info.owner) {
    // tick the 3rd line, untick KC
    const boxes = await p.$$('#lines-table tbody tr .wg-certbox');
    await boxes[2].click();
    await p.waitForTimeout(30);
    const b2 = await p.$$('#lines-table tbody tr .wg-certbox');
    await b2[0].click();
    await p.waitForTimeout(400);
    console.log('after', JSON.stringify(await p.evaluate(() => ({ store: window.__store['wedger/certs'].picks, writes: window.__writes, badges: document.querySelectorAll('#lines-table .wg-cert').length }))));
    await p.check('.rs-certonly');
    await p.waitForTimeout(100);
    console.log('certOnly rows', await p.evaluate(() => document.querySelectorAll('#lines-table tbody tr').length), await p.textContent('.rl-count'));
    await p.click('#tab-atd'); await p.waitForTimeout(200);
    console.log('atd', JSON.stringify(await p.evaluate(() => ({ badges: document.querySelectorAll('#atd-table .wg-cert').length, boxes: document.querySelectorAll('#atd-table .wg-certbox').length }))));
    await p.screenshot({ path: outDir + '/cert_atd.png', clip: { x: 0, y: 250, width: 1300, height: 650 } });
    await p.click('#tab-cat-1'); await p.waitForTimeout(200);
    await p.selectOption('#cat-1 .rc-show', 'all'); await p.waitForTimeout(100);
    console.log('cat1', JSON.stringify(await p.evaluate(() => ({ rows: document.querySelectorAll('#cat-1 tbody tr').length, boxes: document.querySelectorAll('#cat-1 .wg-certbox').length, ths: document.querySelectorAll('#cat-1 thead th').length, tds: document.querySelector('#cat-1 tbody tr') ? document.querySelector('#cat-1 tbody tr').children.length : 0 }))));
  }
  console.log('logs', JSON.stringify(logs));
  await b.close();
})();
