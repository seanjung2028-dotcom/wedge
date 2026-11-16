  // ---------------- navigation (V2: Home, NFL and NBA menus, Soccer) ----------------
  const V2 = { game: '', th: '', flipT: 0, openT: 0, inkRaf: 0, inkT: 0 };
  const NFL_PAGES = new Set(['research', 'final', 'thesis', 'charts', 'analysts', 'results']);
  const NBA_PAGES = new Set(['nba', 'nba-edge', 'nba-thesis', 'nba-charts', 'nba-analysts', 'nba-results']);
  const METHOD_PAGES = new Set(['research', 'results', 'charts']);
  // V1 links and bookmarks that point at pages V2 folded in or dropped
  const V2_ALIAS = { lines: 'research', proj: 'research', 'cat-1': 'research', 'cat-2': 'research', 'cat-3': 'research', 'cat-4': 'research', defense: 'research', atd: 'research',
    backtest: 'results', subscribe: 'lobby', unlock: 'lobby', edge: 'final' };
  const PAGES = [...document.querySelectorAll('.rs-page')].map((p) => p.id);
  const navBtns = [...document.querySelectorAll('.wg-nav [data-page]')];
  const DDS = [...document.querySelectorAll('.wg-nav .wg-dd')].map((dd) => ({ dd, btn: $('.wg-dd-btn', dd), menu: $('.wg-dd-menu', dd), cur: $('.wg-dd-cur', dd), items: [...dd.querySelectorAll('.wg-dd-item')] }));
  const closeMenu = (D, focusBtn) => { D.menu.hidden = true; D.btn.setAttribute('aria-expanded', 'false'); if (focusBtn) D.btn.focus(); };
  const closeMenus = () => DDS.forEach((D) => closeMenu(D, false));
  // the nav scrolls sideways on phones, so menus hang from the header: line each one up under its own button
  const placeMenu = (D) => {
    const host = D.menu.offsetParent; if (!host || D.menu.hidden) return;
    const hr = host.getBoundingClientRect(), br = D.btn.getBoundingClientRect(), mw = D.menu.offsetWidth;
    D.menu.style.left = Math.round(Math.max(8, Math.min(br.left - hr.left, hr.width - mw - 8))) + 'px';
  };
  const openMenu = (D, focusItem) => {
    DDS.forEach((o) => { if (o !== D) closeMenu(o, false); });
    D.menu.hidden = false; D.btn.setAttribute('aria-expanded', 'true'); placeMenu(D);
    if (focusItem) (D.items.find((i) => i.getAttribute('aria-current') === 'page') || D.items[0]).focus();
  };
  DDS.forEach((D) => {
    D.btn.addEventListener('click', (e) => { if (D.menu.hidden) openMenu(D, e.detail === 0); else closeMenu(D, false); });
    D.btn.addEventListener('keydown', (e) => { if (e.key === 'ArrowDown') { e.preventDefault(); openMenu(D, true); } else if (e.key === 'Escape') closeMenu(D, false); });
    D.menu.addEventListener('keydown', (e) => {
      const i = D.items.indexOf(document.activeElement);
      if (e.key === 'ArrowDown') { e.preventDefault(); D.items[(i + 1) % D.items.length].focus(); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); D.items[(i - 1 + D.items.length) % D.items.length].focus(); }
      else if (e.key === 'Home') { e.preventDefault(); D.items[0].focus(); }
      else if (e.key === 'End') { e.preventDefault(); D.items[D.items.length - 1].focus(); }
      else if (e.key === 'Escape') { e.preventDefault(); closeMenu(D, true); }
      else if (e.key === 'Tab') closeMenu(D, false);
    });
  });
  document.addEventListener('click', (e) => { if (!e.target.closest('.wg-nav .wg-dd')) closeMenus(); });
  window.addEventListener('resize', () => DDS.forEach(placeMenu));
  { const nv = $('.wg-nav'); if (nv) nv.addEventListener('scroll', () => DDS.forEach(placeMenu), { passive: true }); }
  const v2Top = () => { const t = $('#top'); if (t) t.scrollIntoView({ block: 'start' }); };
  // the strip of each sport's pages under the page title
  const subBtns = [...document.querySelectorAll('.v2-subnav [data-page]')];
  subBtns.forEach((b) => b.addEventListener('click', () => { showPage(b.dataset.page); v2Top(); }));
  const showPage = (id0) => {
    let id = id0;
    if (!PAGES.includes(id) && V2_ALIAS[id]) id = V2_ALIAS[id];
    if (!PAGES.includes(id)) return;
    if (id0 === 'proj') v2ResearchView('proj'); else if (id0 === 'lines') v2ResearchView('lines');
    [...navBtns, ...subBtns].forEach((b) => { if (b.dataset.page === id) b.setAttribute('aria-current', 'page'); else b.removeAttribute('aria-current'); });
    DDS.forEach((D) => {
      const hit = D.items.find((b) => b.dataset.page === id);
      if (hit) D.btn.setAttribute('aria-current', 'page'); else D.btn.removeAttribute('aria-current');
      D.cur.textContent = hit ? hit.textContent : '';
    });
    closeMenus();
    // keep the current page in view in its strip (phones scroll the strip sideways)
    requestAnimationFrame(() => document.querySelectorAll(`#${id} .v2-subnav`).forEach((nv) => {
      const cur = nv.querySelector('[aria-current="page"]'); if (!cur || nv.scrollWidth <= nv.clientWidth) return;
      nv.scrollLeft = Math.max(0, cur.offsetLeft - (nv.clientWidth - cur.offsetWidth) / 2);
    }));
    document.querySelectorAll('.rs-page').forEach((p) => { p.hidden = p.id !== id; });
    requestAnimationFrame(() => { v2DrawIfDirty(id); v2PrefetchFor(id); });  // after the script has finished loading
    { const mt = $('#method'); if (mt) mt.hidden = true; }  // the method write-up is retired from every page
    dash.setLink(id);
    if (id === 'charts') requestAnimationFrame(() => drawCharts());
    if (id === 'final') requestAnimationFrame(() => fcRender());
    if (id === 'thesis') requestAnimationFrame(() => v2Thesis());
    if (NBA_PAGES.has(id)) requestAnimationFrame(() => drawNbaRec());
    if (id === 'lobby') { const l = $('#lobby'); l.classList.remove('wg-play'); void l.offsetWidth; l.classList.add('wg-play'); }
    v2InkSoon();
  };
