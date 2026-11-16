const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const [,, file, ids] = process.argv;
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 900 } });
  await p.goto('file://' + file); await p.waitForTimeout(1500);
  for (const id of ids.split(',')) {
    await p.evaluate((id) => document.querySelector(`.wg-nav [data-page="${id}"]`).click(), id); await p.waitForTimeout(1200);
    const r = await p.evaluate(([id, MAXD]) => {
      const out = [];
      const walk = (el, d) => {
        if (d > MAXD) return;
        for (const c of el.children) {
          const cs = getComputedStyle(c);
          const deco = (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' ? ' bg=' + cs.backgroundColor : '') + (cs.borderTopWidth !== '0px' ? ' bd=' + cs.borderTopWidth + ' ' + cs.borderTopColor : '') + (cs.borderRadius !== '0px' ? ' r=' + cs.borderRadius : '') + (cs.padding !== '0px' ? ' pad=' + cs.padding : '') + (cs.backdropFilter && cs.backdropFilter !== 'none' ? ' bf' : '');
          out.push('  '.repeat(d) + c.tagName.toLowerCase() + (c.id ? '#' + c.id : '') + (c.className && typeof c.className === 'string' ? '.' + c.className.trim().split(/\s+/).join('.') : '') + (c.hidden ? ' [hidden]' : '') + deco);
          walk(c, d + 1);
        }
      };
      walk(document.getElementById(id), 0);
      return out.join('\n');
    }, [id, +(process.env.D || 3)]);
    console.log('==== ' + id + '\n' + r);
  }
  await b.close();
})();
