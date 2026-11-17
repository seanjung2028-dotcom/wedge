  // ---------------- Analyst (wedgepicks.com): /api/v1/ask ----------------
  // The question goes to the site's server, which runs Claude with Wedge's tools and checks every number before answering.
  // The conversation stays in this tab (sessionStorage); nothing is saved on the server.
  const AK = { log: [], busy: false, ready: null, offline: false };
  const AK_START = ['Which lines does Wedge like most this week?', 'Best price for Nico Collins 5+ receptions right now?', 'How does Wedge pick final lines?', 'Josh Allen’s passing yards this season'];
  const akSave = () => { try { sessionStorage.setItem('wedge-ask', JSON.stringify(AK.log.slice(-20))); } catch (e) { /* storage unavailable */ } };
  const akLoad = () => { try { AK.log = JSON.parse(sessionStorage.getItem('wedge-ask') || '[]'); } catch (e) { AK.log = []; } };

  function v2AskOpen() {
    if (!$('#ask-log')) return;
    if (!AK.log.length) akLoad();
    akBind(); akDraw();
    if (AK.ready == null) {
      shGet('/api/v1/ask').then((j) => { AK.ready = !!j.ready; akDraw(); }).catch(() => { AK.ready = false; AK.offline = true; akDraw(); });
    }
  }
  function v2AskWith(q) { showPage('ask'); v2Top(); v2AskOpen(); akSend(q); }

  function akText(t) {
    const box = el('div', 'v2-ak-text');
    String(t || '').replace(/\*\*/g, '').split(/\n{2,}/).forEach((p) => { if (p.trim()) box.append(el('p', null, p.trim())); });
    return box;
  }

  function akDraw() {
    const log = $('#ask-log'), start = $('#ask-start'), note = $('#ask-note'); if (!log) return;
    note.hidden = AK.ready !== false;
    note.textContent = AK.offline ? 'The Analyst runs on wedgepicks.com.' : 'The Analyst isn’t switched on yet. Check back soon.';
    start.hidden = AK.log.length > 0;
    if (!start.dataset.drawn) {
      start.dataset.drawn = '1';
      start.replaceChildren(...AK_START.map((q) => { const b = el('button', 'v2-ak-chip', q); b.type = 'button'; b.addEventListener('click', () => akSend(q)); return b; }));
    }
    const out = [];
    AK.log.forEach((m, i) => {
      if (m.role === 'user') { out.push(el('div', 'v2-ak-q', m.content)); return; }
      const a = el('article', 'v2-ak-a' + (m.error ? ' is-err' : ''));
      a.append(akText(m.content));
      for (const c of m.cards || []) a.append(shCard(c, false));
      if (m.tools && m.tools.length) {
        const d = el('details', 'v2-ak-how'); d.append(el('summary', null, `How this was worked out · ${m.tools.length} lookup${m.tools.length > 1 ? 's' : ''}`));
        const ul = el('ul'); m.tools.forEach((t) => ul.append(el('li', null, `${t.name.replace(/_/g, ' ')}${t.input && (t.input.player || t.input.ticker || t.input.topic) ? ': ' + (t.input.player || t.input.ticker || t.input.topic) : ''}${t.ok ? '' : ' (no result)'}`)));
        d.append(ul, el('p', null, `Every number above was checked against these results${m.at ? ' at ' + shCT(m.at, { second: '2-digit' }) : ''}. Prices: Kalshi, live. Wedge’s numbers: the card build’s lens on the live price. Statistics: nflverse.`));
        a.append(d);
      }
      if (i === AK.log.length - 1 && m.follow_ups && m.follow_ups.length) {
        const f = el('div', 'v2-ak-follow'); m.follow_ups.forEach((q) => { const b = el('button', 'v2-ak-chip', q); b.type = 'button'; b.addEventListener('click', () => akSend(q)); f.append(b); });
        a.append(f);
      }
      out.push(a);
    });
    if (AK.busy) { const w = el('div', 'v2-ak-a is-wait'); w.setAttribute('role', 'status'); w.append(el('p', null, 'Looking it up in Wedge’s data…')); out.push(w); }
    log.replaceChildren(...out);
    const btn = $('#ask-go'); if (btn) btn.disabled = AK.busy || AK.ready === false;
    const clr = $('#ask-clear'); if (clr) clr.hidden = !AK.log.length || AK.busy;
  }

  async function akSend(q) {
    q = String(q || '').trim();
    if (!q || AK.busy) return;
    if (AK.ready === false) { akDraw(); return; }
    AK.log.push({ role: 'user', content: q.slice(0, 2000) }); AK.busy = true; akDraw();
    const box = $('#ask-q'); if (box) box.value = '';
    try {
      const j = await shGet('/api/v1/ask', { method: 'POST', body: JSON.stringify({ messages: AK.log.filter((m) => !m.error).map((m) => ({ role: m.role, content: m.content })) }) });
      AK.log.push({ role: 'assistant', content: j.text, cards: j.cards || [], follow_ups: j.follow_ups || [], tools: j.tools || [], verified: j.verified, at: j.at });
    } catch (e) {
      const msg = e.code === 'not_configured' ? 'The Analyst isn’t switched on yet. Check back soon.' : (e.message && !/^HTTP/.test(e.message) ? e.message : 'The Analyst couldn’t answer just now. Try again in a minute.');
      if (e.code === 'not_configured') AK.ready = false;
      AK.log.push({ role: 'assistant', content: msg, error: true });
    }
    AK.busy = false; akSave(); akDraw();
    const last = $('#ask-log').lastElementChild; if (last) last.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function akBind() {
    const f = $('#ask-form'); if (!f || f.dataset.bound) return; f.dataset.bound = '1';
    const q = $('#ask-q');
    f.addEventListener('submit', (e) => { e.preventDefault(); akSend(q.value); });
    q.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); akSend(q.value); } });
    $('#ask-clear').addEventListener('click', () => { AK.log = []; akSave(); akDraw(); q.focus(); });
  }
