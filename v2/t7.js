// the research folder: opening frames, each tab, the phone view
const { chromium, devices } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, out, tag = 'a'] = process.argv;
  const b = await chromium.launch(); const logs = [];
  const p = await b.newPage({ viewport: { width: 1300, height: 940 } }); p.on('pageerror', (e) => logs.push('ERR ' + e.message));
  await p.goto('file://' + file); await p.waitForTimeout(1400);
  await p.evaluate(() => document.querySelector('.wg-nav [data-page="research"]').click()); await p.waitForTimeout(900);
  await p.evaluate(() => { const q = document.querySelector('#lines-card input[type=search], #lines-card input'); if (q) { q.value = 'Kolar'; q.dispatchEvent(new Event('input', { bubbles: true })); } }); await p.waitForTimeout(700);
  await p.evaluate(() => { const r = [...document.querySelectorAll('#lines-table tbody tr.v2-click')][0]; r.click(); });
  for (const t of [80, 260, 520, 1300]) { await p.waitForTimeout(t === 80 ? 80 : t - [80, 260, 520, 1300][[80, 260, 520, 1300].indexOf(t) - 1]); await p.screenshot({ path: `${out}/${tag}_open_${t}.png` }); }
  for (const id of ['sit-t-inj', 'sit-t-mu']) { await p.click('#' + id); await p.waitForTimeout(220); await p.screenshot({ path: `${out}/${tag}_${id}_mid.png` }); await p.waitForTimeout(900); await p.screenshot({ path: `${out}/${tag}_${id}.png` }); }
  const ctx = await b.newContext({ ...devices['iPhone 13'] }); const m = await ctx.newPage(); m.on('pageerror', (e) => logs.push('ERR m ' + e.message));
  await m.goto('file://' + file); await m.waitForTimeout(1400);
  await m.evaluate(() => document.querySelector('.wg-nav [data-page="research"]').click()); await m.waitForTimeout(900);
  await m.evaluate(() => { const r = [...document.querySelectorAll('#lines-table tbody tr.v2-click')][3]; r.click(); }); await m.waitForTimeout(1400);
  await m.screenshot({ path: `${out}/${tag}_m_file.png` });
  console.log(await p.evaluate(() => document.querySelector('#lines-q') ? 'q ok' : 'no q'), logs.join('\n'));
  await b.close();
})();
