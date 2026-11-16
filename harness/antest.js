const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, outDir, width] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: Number(width || 1300), height: 1000 } });
  const logs = []; p.on('pageerror', (e) => logs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text()); });
  await p.goto('file://' + file); await p.waitForTimeout(700);
  await p.click('#tab-analysts'); await p.waitForTimeout(200);
  const cards = await p.$$eval('.wg-an', (els) => els.map((e) => e.innerText.replace(/\n+/g, ' | ')));
  console.log(cards.join('\n'));
  console.log('count', await p.textContent('.an-count'), 'owner add visible', await p.isVisible('.an-add'));
  await p.screenshot({ path: outDir + '/an.png', fullPage: false });
  if (await p.isVisible('.an-add')) {
    await p.selectOption('.an-who', 'Will');
    const opt = await p.$eval('#an-options option', (o) => o.value);
    const target = await p.$$eval('#an-options option', (os) => os.map((o) => o.value).find((v) => v.includes('Rhamondre Stevenson: Over 2.5 Receptions')));
    await p.fill('.an-pick', target); await p.click('.an-addbtn'); await p.waitForTimeout(300);
    console.log('after add', await p.textContent('.an-msg'), JSON.stringify(await p.evaluate(() => window.__store['wedger/analysts'].picks.Will)));
    console.log(await p.$$eval('.wg-an', (els) => els.map((e) => e.innerText.replace(/\n+/g, ' | ')).join('\n')));
    await p.selectOption('.an-filter', 'Will'); await p.waitForTimeout(100);
    await p.click('#an-table tbody tr .an-rm'); await p.waitForTimeout(300);
    console.log('after remove', JSON.stringify(await p.evaluate(() => window.__store['wedger/analysts'].picks.Will)), await p.textContent('.an-count'));
  }
  console.log('logs', JSON.stringify(logs)); await b.close();
})();
