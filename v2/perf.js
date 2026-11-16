// load and scroll cost: long tasks during load, frame times while scrolling each page
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, tag = 'base'] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 900 } });
  await p.addInitScript(() => { window.__lt = []; new PerformanceObserver((l) => l.getEntries().forEach((e) => window.__lt.push([Math.round(e.startTime), Math.round(e.duration)]))).observe({ type: 'longtask', buffered: true }); });
  const t0 = Date.now(); await p.goto('file://' + file); await p.waitForTimeout(4000);
  const lt = await p.evaluate(() => window.__lt);
  console.log(tag, 'long tasks during load:', lt.length, 'total ms', lt.reduce((a, x) => a + x[1], 0), 'max', Math.max(0, ...lt.map((x) => x[1])), 'DOM nodes', await p.evaluate(() => document.getElementsByTagName('*').length));
  const scroll = async (label) => {
    const r = await p.evaluate(async () => {
      const ft = []; let last = performance.now(), run = true;
      const loop = (t) => { ft.push(t - last); last = t; if (run) requestAnimationFrame(loop); }; requestAnimationFrame(loop);
      const H = document.documentElement.scrollHeight - innerHeight;
      for (let y = 0; y <= Math.min(H, 6000); y += 120) { scrollTo(0, y); await new Promise((r) => requestAnimationFrame(r)); }
      run = false; await new Promise((r) => setTimeout(r, 50)); scrollTo(0, 0);
      ft.sort((a, b) => a - b); const n = ft.length;
      return { frames: n, median: +ft[n >> 1].toFixed(1), p90: +ft[Math.floor(n * .9)].toFixed(1), max: +ft[n - 1].toFixed(1), over50: ft.filter((x) => x > 50).length };
    });
    console.log(tag, label.padEnd(10), JSON.stringify(r));
  };
  await scroll('home');
  for (const id of ['research', 'final', 'charts', 'results']) {
    const t = Date.now(); await p.evaluate((id) => document.querySelector(`.wg-nav [data-page="${id}"]`).click(), id); await p.waitForTimeout(1500);
    await scroll(id);
  }
  // idle cost: frames per second with nothing happening (infinite animations, blurs)
  const idle = await p.evaluate(async () => { document.querySelector('.wg-nav [data-page="lobby"]').click(); await new Promise((r) => setTimeout(r, 800)); let n = 0; const s = performance.now(); await new Promise((res) => { const f = () => { n++; if (performance.now() - s < 2000) requestAnimationFrame(f); else res(); }; requestAnimationFrame(f); }); return n / 2; });
  const anims = await p.evaluate(() => document.getAnimations().filter((a) => a.effect && a.effect.getComputedTiming().endTime === Infinity && a.playState === 'running').map((a) => a.animationName + '@' + (a.effect.target.className || a.effect.target.tagName || '').toString().split(' ')[0]));
  console.log(tag, 'idle fps', idle, 'running infinite animations', anims.length, [...new Set(anims)].slice(0, 20).join(' '));
  const bf = await p.evaluate(() => [...document.querySelectorAll('*')].filter((e) => { const cs = getComputedStyle(e); return e.offsetParent && cs.backdropFilter && cs.backdropFilter !== 'none'; }).length);
  console.log(tag, 'visible elements with backdrop blur', bf);
  await b.close();
})();
