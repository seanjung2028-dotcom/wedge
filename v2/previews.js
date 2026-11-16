// Screenshots of the members-only pages for the blurred previews: node previews.js <base url> <out dir> <page ids...>
const { chromium } = require('playwright');
(async () => {
  const [base, out, ...pages] = process.argv.slice(2);
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 1, reducedMotion: 'reduce', colorScheme: 'dark' });
  const p = await ctx.newPage();
  for (const id of pages) {
    await p.goto(`${base}?pv=${id}#${id}`, { waitUntil: 'load' });
    await p.waitForFunction(() => !document.getElementById('wz-boot'), null, { timeout: 60000 });
    await p.waitForTimeout(1500);
    const box = await p.evaluate((id) => {
      const pg = document.getElementById(id); if (!pg || pg.hidden) return null;
      const sn = pg.querySelector(':scope > .v2-subnav') || pg.querySelector(':scope > .wx-band');
      return { y: Math.round(sn.getBoundingClientRect().bottom + scrollY + 24), end: Math.round(pg.getBoundingClientRect().bottom + scrollY) };
    }, id);
    if (!box) { console.log('skip', id); continue; }
    const height = Math.min(1300, Math.max(600, box.end - box.y));
    await p.screenshot({ path: `${out}/${id}.png`, fullPage: true, clip: { x: 0, y: box.y, width: 1280, height } });
    console.log('shot', id, height);
  }
  await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
