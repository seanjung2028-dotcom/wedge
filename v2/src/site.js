  // ---------------- membership: plans, email sign-in and members-only pages (wedgepicks.com) ----------------
  // window.WEDGE_ACCESS comes from the site's runtime (/api/me). On the dashboard artifact it's absent: everything is open.
  var v2SiteOn = false;  // set once this module has run; hooks in navigation and Home check it first
  function v2GateHook(id) { if (!v2SiteOn) return; v2GateApply(id); if (id === 'signin') v2SiOpen(); }
  const V2_TIER = { research: 1, charts: 1, analysts: 1, results: 1, nba: 1, 'nba-charts': 1, 'nba-analysts': 1, 'nba-results': 1,
    final: 2, thesis: 2, 'nba-edge': 2, 'nba-thesis': 2 };
  const V2_PLAN = { 1: 'research', 2: 'inner' };
  const V2_LOCK = {
    1: { k: 'Research', h: 'Members only.', p: 'Every line at every price with our projection and the research file behind it, plus Charts & Trends, the analysts and the full record.' },
    2: { k: 'Inner Circle', h: 'Inner Circle only.', p: 'The Winning Edge: our final lines and conditional leans for every game, every week, with the thesis behind each one.' },
  };
  const V2_LOCK_ICON = '<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="3" y="7" width="10" height="7" rx="1.6" fill="currentColor"/><path d="M5.2 7V5.2a2.8 2.8 0 0 1 5.6 0V7" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>';
  const v2Acc = () => window.WEDGE_ACCESS || null;
  const v2Level = () => { const A = v2Acc(); return !A || !A.gating ? 3 : (A.level || 0); };
  const v2Can = (id) => v2Level() >= (V2_TIER[id] || 0);
  const v2Remember = (id) => { try { sessionStorage.setItem('wedge-return', id); } catch (e) { /* storage unavailable */ } };
  const v2Recall = () => { try { const v = sessionStorage.getItem('wedge-return'); sessionStorage.removeItem('wedge-return'); return v; } catch (e) { return null; } };
  const v2Go = (id) => { showPage(id); v2Top(); };

  // a locked page keeps its title and page strip; the body is a blurred picture of the page with a way in
  function v2GateApply(id) {
    const p = document.getElementById(id); if (!p) return;
    const need = V2_TIER[id] || 0, lv = v2Level();
    if (!need || lv >= need) { p.classList.remove('v2-locked'); return; }
    p.classList.add('v2-locked');
    let lk = p.querySelector(':scope > .v2-lock');
    if (!lk) {
      lk = el('section', 'v2-lock'); lk.setAttribute('aria-labelledby', id + '-lock-h');
      const shot = el('div', 'v2-lock-shot'); shot.setAttribute('aria-hidden', 'true');
      const pv = (window.WEDGE_PREVIEWS || {})[id];
      if (pv) shot.style.backgroundImage = `url("${pv}")`; else shot.classList.add('is-generic');
      const card = el('div', 'v2-lock-card');
      lk.append(shot, card);
      const after = p.querySelector(':scope > .v2-subnav') || p.querySelector(':scope > .wx-band');
      if (after) after.after(lk); else p.prepend(lk);
    }
    const A = v2Acc() || {}, C = V2_LOCK[need];
    const card = lk.querySelector('.v2-lock-card');
    const k = el('span', 'v2-lock-k'); k.innerHTML = V2_LOCK_ICON; k.append(C.k);
    const h = el('h3', null, C.h); h.id = id + '-lock-h';
    const row = el('div', 'v2-lock-row');
    const go = el('button', 'wz-btn wz-btn-g wz-btn-lg'); go.type = 'button';
    go.textContent = A.signedIn && lv >= 1 ? 'Upgrade to Inner Circle ↗' : 'See plans ↗';
    go.addEventListener('click', () => { v2Remember(id); v2Go('subscribe'); });
    row.append(go);
    if (!A.signedIn) {
      const si = el('button', 'wz-btn wz-btn-line wz-btn-lg', 'Sign in'); si.type = 'button';
      si.addEventListener('click', () => { v2Remember(id); v2Go('signin'); });
      row.append(si);
    }
    const fine = el('p', 'v2-lock-fine', A.signedIn
      ? `Signed in as ${A.email} · ${A.planName || 'Free'}`
      : (need === 1 ? 'Research is $19.99 a month. Inner Circle includes it.' : 'Inner Circle is $119.99 for the season and includes Research.'));
    card.replaceChildren(k, h, el('p', 'v2-lock-p', C.p), row, fine);
  }

  // header, menus and Home follow the visitor's plan
  function v2GateChrome() {
    const A = v2Acc(), lv = v2Level();
    document.querySelectorAll('.wg-nav [data-page], .v2-subnav [data-page]').forEach((b) => b.classList.toggle('is-locked', !v2Can(b.dataset.page)));
    const acct = $('#v2-acct');
    if (acct) {
      acct.hidden = !(A && A.api && A.gating);
      acct.textContent = A && A.signedIn ? 'Account' : 'Sign in';
    }
    const join = document.querySelector('.wz-bar .pf-join');
    if (join) { join.hidden = !!(A && A.gating && lv >= 2); join.textContent = A && A.gating && lv === 1 ? 'Upgrade ↗' : 'Join ↗'; }
    document.querySelectorAll('.v2-plan').forEach((card) => {
      const need = card.dataset.plan === 'inner' ? 2 : 1;
      const btn = $('.v2-plan-go', card), note = $('.v2-plan-note', card);
      const url = A && A.checkout ? A.checkout[card.dataset.plan] : '';
      card.classList.toggle('is-current', !!(A && A.gating && lv >= need && lv < 3 && (need === lv)));
      if (A && A.gating && lv >= need) { btn.textContent = need === 2 || lv >= 2 ? 'Open The Winning Edge ↗' : 'Open Research ↗'; btn.dataset.mode = 'open'; note.textContent = lv === 3 ? 'Analyst access includes every page.' : 'This is your plan.'; }
      else if (url) { btn.textContent = need === 2 ? (lv === 1 ? 'Upgrade to Inner Circle ↗' : 'Join the Inner Circle ↗') : 'Start Research ↗'; btn.dataset.mode = 'buy'; note.textContent = 'Secure checkout. Then sign in with the same email.'; }
      else { btn.textContent = 'Get notified ↗'; btn.dataset.mode = 'wait'; note.textContent = 'Checkout opens soon. We’ll email you when it does.'; }
    });
  }

  // ---------------- plans page ----------------
  document.querySelectorAll('.v2-plan-go').forEach((b) => b.addEventListener('click', () => {
    const plan = b.closest('.v2-plan').dataset.plan, A = v2Acc() || {};
    if (b.dataset.mode === 'open') { v2Go(plan === 'inner' ? 'final' : 'research'); return; }
    const url = A.checkout && A.checkout[plan];
    if (url) {
      let u = url;
      try { const x = new URL(url); if (A.email && /stripe\.com$/.test(x.hostname)) x.searchParams.set('prefilled_email', A.email); u = x.toString(); } catch (e) { /* use as given */ }
      location.href = u; return;
    }
    const name = plan === 'inner' ? 'Inner Circle' : 'Research';
    location.href = 'mailto:' + WEDGER_EMAIL + '?subject=' + encodeURIComponent(`Wedge ${name}: let me know when checkout opens`) + '&body=' + encodeURIComponent(`Please email me when Wedge ${name} opens.`);
  }));
  document.querySelectorAll('[data-v2-signin]').forEach((b) => b.addEventListener('click', () => v2Go('signin')));
  { const acct = $('#v2-acct'); if (acct) acct.addEventListener('click', () => v2Go('signin')); }

  // ---------------- sign in: email -> 6-digit code -> signed in ----------------
  const v2Si = { email: '' };
  const v2SiMsg = (t, bad) => { const m = $('#v2-si-msg'); if (!m) return; m.textContent = t || ''; m.classList.toggle('is-bad', !!bad); };
  const v2SiStep = (s) => {
    ['email', 'code', 'acct'].forEach((k) => { const n = $('#v2-si-' + k); if (n) n.hidden = k !== s; });
    const h = $('#v2-si-h'); if (h) h.textContent = s === 'acct' ? 'Your account.' : 'Sign in.';
  };
  async function v2Api(path, body) {
    const r = await fetch(path, { method: 'POST', headers: { 'content-type': 'application/json' }, credentials: 'same-origin', body: JSON.stringify(body || {}) });
    let j = {}; try { j = await r.json(); } catch (e) { /* not json */ }
    if (!r.ok || j.ok === false) throw new Error(j.error || 'Something went wrong. Try again.');
    return j;
  }
  function v2SiAccount() {
    const A = v2Acc() || {}, dl = $('#v2-si-dl');
    const row = (a, b) => { const d = el('div'); d.append(el('dt', null, a), el('dd', null, b)); return d; };
    const until = A.until ? new Date(A.until * 1000).toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' }) : '';
    const via = { analyst: 'Analyst', comp: 'Added by Wedge', 'season pass': 'Season pass', subscription: 'Monthly subscription' }[A.source] || '';
    dl.replaceChildren(row('Email', A.email || '—'), row('Plan', (A.planName || 'Free') + (via ? ` · ${via}` : '')), ...(until ? [row('Access through', until)] : []));
    const bill = $('#v2-si-bill'); if (bill) { bill.hidden = !(A.portal && A.source === 'subscription'); bill.href = A.portal || '#'; }
    const up = $('#v2-si-up'); if (up) up.hidden = (A.level || 0) >= 2;
    v2SiStep('acct');
  }
  async function v2SiSend(email) {
    v2SiMsg('Sending your code…');
    try {
      const j = await v2Api('/api/login', { email });
      v2Si.email = email; $('#v2-si-to').textContent = email; v2SiStep('code');
      const c = $('#v2-si-c'); c.value = j.devCode || ''; c.focus();
      v2SiMsg(j.message + (j.devCode ? ' (Test mode: the code is filled in for you.)' : ''));
    } catch (e) { v2SiMsg(e.message, true); }
  }
  async function v2SiVerify(email, code) {
    v2SiMsg('Checking your code…');
    try {
      await v2Api('/api/verify', { email, code });
      v2SiMsg('Signed in. Opening your pages…');
      const back = v2Recall();
      location.replace(location.pathname + '#' + (back && V2_TIER[back] ? back : 'lobby'));
      location.reload();
    } catch (e) { v2SiMsg(e.message, true); }
  }
  {
    const fe = $('#v2-si-email'), fc = $('#v2-si-code');
    if (fe) fe.addEventListener('submit', (e) => { e.preventDefault(); const v = $('#v2-si-e').value.trim(); if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) { v2SiMsg('Enter a valid email address.', true); return; } v2SiSend(v); });
    if (fc) fc.addEventListener('submit', (e) => { e.preventDefault(); const v = $('#v2-si-c').value.replace(/\D/g, ''); if (v.length !== 6) { v2SiMsg('The code has 6 digits.', true); return; } v2SiVerify(v2Si.email, v); });
    const back = $('#v2-si-back'); if (back) back.addEventListener('click', () => { v2SiStep('email'); v2SiMsg(''); $('#v2-si-e').focus(); });
    const out = $('#v2-si-out'); if (out) out.addEventListener('click', async () => { try { await v2Api('/api/logout'); } catch (e) { /* signed out anyway */ } location.replace(location.pathname + '#lobby'); location.reload(); });
    const up = $('#v2-si-up'); if (up) up.addEventListener('click', () => v2Go('subscribe'));
  }
  function v2SiOpen() {
    const A = v2Acc();
    if (A && A.signedIn) { v2SiAccount(); return; }
    v2SiStep('email');
    if (A && A.api && !A.signInReady) v2SiMsg('Sign-in opens with memberships. Check back soon.');
  }

  // links from the sign-in email (#signin/<email>/<code>) and back from checkout (#welcome)
  function v2SiFromHash() {
    const m = /^#signin\/([^/]+)\/(\d{6})$/.exec(location.hash);
    if (m) {
      const email = decodeURIComponent(m[1]); history.replaceState(null, '', location.pathname + '#signin');
      showPage('signin'); v2Si.email = email; $('#v2-si-to').textContent = email; $('#v2-si-c').value = m[2]; v2SiStep('code'); v2SiVerify(email, m[2]);
      return true;
    }
    if (location.hash === '#welcome') {
      history.replaceState(null, '', location.pathname + '#signin'); showPage('signin');
      const A = v2Acc();
      if (A && A.signedIn) location.reload(); else v2SiMsg('Payment received. Welcome to Wedge. Sign in with the email you used at checkout.');
      return true;
    }
    return false;
  }

  // Home: matchup tiles and the schedule point locked visitors to The Winning Edge's sign-up
  function v2HomeLocks() {
    if (v2Can('final')) return;
    document.querySelectorAll('#v2-mgrid .v2-mt').forEach((b) => {
      const tags = $('.v2-mt-tags', b); if (!tags || tags.dataset.locked) return;
      tags.dataset.locked = '1';
      const t = el('i', 'fc-badge v2-icb'); t.innerHTML = V2_LOCK_ICON; t.append('Inner Circle');
      if (!b.classList.contains('is-done')) tags.replaceChildren(t);
      b.setAttribute('aria-label', `${b.dataset.game}: final lines and leans are for Inner Circle members.`);
    });
  }

  function v2SiteInit() {
    v2SiteOn = true;
    v2GateChrome();
    v2HomeLocks();
    document.querySelectorAll('.rs-page').forEach((p) => { if (!p.hidden) v2GateApply(p.id); });
    if (!v2SiFromHash() && location.hash === '#signin') v2SiOpen();
  }
