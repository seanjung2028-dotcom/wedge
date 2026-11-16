// every longer piece of text on each page (and in the research file), to edit the copy
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 900 } });
  await p.goto('file://' + file); await p.waitForTimeout(1500);
  const dump = async (label, rootSel) => {
    const rows = await p.evaluate((rootSel) => {
      const out = [], seen = new Set();
      const root = document.querySelector(rootSel); if (!root) return ['(missing)'];
      const w = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT);
      let n; while ((n = w.nextNode())) {
        if (!n.offsetParent && getComputedStyle(n).position !== 'fixed') continue;
        if (['SCRIPT', 'STYLE', 'svg'].includes(n.tagName) || n.closest('svg, table, .wx-read, .v2-th-play, .fc-play, .fc-game[open] .fc-body, select')) continue;
        const own = [...n.childNodes].filter((c) => c.nodeType === 3).map((c) => c.textContent).join('').trim();
        const txt = n.innerText ? n.innerText.trim() : '';
        if (own.length >= 45 && !seen.has(txt)) { seen.add(txt); out.push(n.tagName.toLowerCase() + '.' + (typeof n.className === 'string' ? n.className.split(' ')[0] : '') + ' | ' + txt.replace(/\s+/g, ' ').slice(0, 400)); }
      }
      return out;
    }, rootSel);
    console.log('\n######## ' + label); rows.forEach((r) => console.log(r));
  };
  await dump('home', '#lobby');
  for (const id of ['research', 'final', 'thesis', 'charts', 'analysts', 'results', 'nba', 'nba-edge', 'nba-thesis', 'nba-charts', 'nba-analysts', 'nba-results', 'soccer']) {
    await p.evaluate((id) => { const b2 = document.querySelector(`.wg-nav [data-page="${id}"]`); if (b2) b2.click(); }, id); await p.waitForTimeout(900);
    if (id === 'analysts') await p.evaluate(() => { const d = document.querySelector('#pf-allpicks'); if (d) d.open = true; });
    await dump(id, '#' + id);
  }
  // the research file: a full outlook and a lite one
  await p.evaluate(() => document.querySelector('.wg-nav [data-page="research"]').click()); await p.waitForTimeout(800);
  for (const k of [0, 3]) {
    await p.evaluate((k) => { const r = [...document.querySelectorAll('#lines-table tbody tr.v2-click')][k]; r.click(); }, k); await p.waitForTimeout(1900);
    for (const t of ['sit-t-ov', 'sit-t-inj', 'sit-t-mu']) { await p.click('#' + t); await p.waitForTimeout(900); await dump('file' + k + ' ' + t, '#sit-dlg'); }
    await p.keyboard.press('Escape'); await p.waitForTimeout(500);
  }
  await b.close();
})();
