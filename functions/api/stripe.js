// POST /api/stripe -> Stripe webhook. Grants and removes access as people pay, renew or cancel.
// Research is the monthly subscription; Inner Circle is the one-time season pass.
// STRIPE_TIERS (optional JSON) maps a Payment Link or Price id to "research" or "inner" if you add more products.
import { json, normEmail, hmacHex, safeEqual, getMember, putMember, seasonEnd } from '../../lib/wedge.js';

async function verify(env, raw, header) {
  if (!env.STRIPE_WEBHOOK_SECRET || !header) return false;
  const parts = Object.fromEntries(header.split(',').map((kv) => kv.split('=')).filter((x) => x.length === 2).map(([k, v]) => [k.trim(), v.trim()]));
  const sigs = header.split(',').filter((kv) => kv.trim().startsWith('v1=')).map((kv) => kv.trim().slice(3));
  const t = Number(parts.t);
  if (!t || Math.abs(Date.now() / 1000 - t) > 300) return false;
  const want = await hmacHex(env.STRIPE_WEBHOOK_SECRET, `${t}.${raw}`);
  return sigs.some((s) => safeEqual(s, want));
}

function tierOf(env, s) {
  let map = {};
  try { map = JSON.parse(env.STRIPE_TIERS || '{}'); } catch (e) { /* ignore */ }
  for (const id of [s.payment_link, s.metadata && s.metadata.price].filter(Boolean)) if (map[id]) return map[id];
  return s.mode === 'subscription' ? 'research' : 'inner';
}

export async function onRequestPost({ request, env }) {
  const raw = await request.text();
  if (!(await verify(env, raw, request.headers.get('stripe-signature')))) return json({ ok: false, error: 'bad signature' }, 400);
  if (!env.WEDGE) return json({ ok: false, error: 'no KV' }, 500);
  const ev = JSON.parse(raw), o = ev.data && ev.data.object;
  if (!o) return json({ ok: true });

  if (ev.type === 'checkout.session.completed' || ev.type === 'checkout.session.async_payment_succeeded') {
    const email = normEmail((o.customer_details && o.customer_details.email) || o.customer_email);
    if (!email) return json({ ok: true, note: 'no email' });
    if (o.mode === 'payment' && o.payment_status !== 'paid') return json({ ok: true, note: 'not paid yet' });
    const tier = tierOf(env, o);
    const m = (await getMember(env, email)) || { email };
    if (tier === 'research') m.research = { status: 'active', sub: o.subscription || null, cust: o.customer || null, since: new Date().toISOString() };
    else m.inner = { status: 'active', until: seasonEnd(env), cust: o.customer || null, paid: o.amount_total || null, since: new Date().toISOString() };
    await putMember(env, email, m);
    if (o.customer) await env.WEDGE.put('c:' + o.customer, email);
    return json({ ok: true, email, tier });
  }

  if (ev.type === 'customer.subscription.updated' || ev.type === 'customer.subscription.deleted') {
    const email = o.customer ? await env.WEDGE.get('c:' + o.customer) : null;
    if (!email) return json({ ok: true, note: 'unknown customer' });
    const m = (await getMember(env, email)) || { email };
    m.research = { ...(m.research || {}), status: ev.type === 'customer.subscription.deleted' ? 'canceled' : o.status, sub: o.id };
    await putMember(env, email, m);
    return json({ ok: true, email, status: m.research.status });
  }

  return json({ ok: true, ignored: ev.type });
}
