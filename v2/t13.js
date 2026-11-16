// a full-outlook research file's text (a 45–55¢ line with a read)
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 900 } });
  await p.goto('file://' + file); await p.waitForTimeout(1500);
  await p.evaluate(() => document.querySelector('.wg-nav [data-page="research"]').click()); await p.waitForTimeout(800);
  await p.selectOption('#lines-card .rs-show', 'q'); await p.waitForTimeout(800);
  let found = -1;
  for (let k = 0; k < 25 && found < 0; k++) {
    const ok = await p.evaluate((k) => { const rows = [...document.querySelectorAll('#lines-table tbody tr.v2-click')]; const r = rows[k]; if (!r) return null; r.click(); return true; }, k);
    if (!ok) break; await p.waitForTimeout(1500);
    const lite = await p.evaluate(() => /Wedge %/.test(document.querySelector('#sit-p-ov').innerText) && !document.querySelector('#sit-dlg').classList.contains('v2-nohist'));
    if (lite) found = k; else { await p.keyboard.press('Escape'); await p.waitForTimeout(400); }
  }
  console.log('found', found);
  for (const t of ['sit-t-ov', 'sit-t-inj', 'sit-t-mu']) {
    await p.click('#' + t); await p.waitForTimeout(900);
    const txt = await p.evaluate(() => { const out = []; document.querySelectorAll('#sit-dlg .wg-sd-panel:not([hidden]) p, #sit-dlg .wg-sd-panel:not([hidden]) small, #sit-dlg .wg-sd-panel:not([hidden]) .wg-sd-hint, #sit-dlg .wg-sd-panel:not([hidden]) li, #sit-dlg .wg-sd-foot, #sit-dlg .wg-sd-panel:not([hidden]) summary, #sit-dlg .wg-sd-panel:not([hidden]) .wg-lab').forEach((e) => { const s = e.innerText.trim().replace(/\s+/g, ' '); if (s.length > 30) out.push(e.className + ' | ' + s.slice(0, 300)); }); return [...new Set(out)]; });
    console.log('#### ' + t); txt.forEach((x) => console.log(x));
  }
  await b.close();
})();
