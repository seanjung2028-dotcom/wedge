// which datasets the page reads (and so loads) at startup, and on each page
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 900 } });
  await p.addInitScript(() => {
    window.__ds = []; let real;
    Object.defineProperty(window, 'dash', { configurable: true, get() { return real; }, set(v) {
      const orig = v.data.bind(v); v.data = (id) => { if (!window.__ds.some((x) => x[0] === id)) window.__ds.push([id, Math.round(performance.now()), window.__phase || 'start']); return orig(id); }; real = v; } });
  });
  await p.goto('file://' + file); await p.waitForTimeout(2500);
  const show = async (lab) => { const d = await p.evaluate(() => window.__ds.splice(0)); console.log(lab.padEnd(10), d.map((x) => x[0]).join(' ')); };
  await show('startup');
  for (const id of ['research', 'final', 'thesis', 'charts', 'analysts', 'results', 'nba']) { await p.evaluate((id) => document.querySelector(`.wg-nav [data-page="${id}"]`).click(), id); await p.waitForTimeout(1200); await show(id); }
  await b.close();
})();
