// POST /api/verify {email, code} -> sets the sign-in cookie
import { json, normEmail, sha256Hex, safeEqual, makeSession, levelFor, PLAN_NAME } from '../../lib/wedge.js';

export async function onRequestPost({ request, env }) {
  let body = {};
  try { body = await request.json(); } catch (e) { /* empty */ }
  const email = normEmail(body.email), code = String(body.code || '').replace(/\D/g, '');
  if (!env.WEDGE || !env.SESSION_SECRET) return json({ ok: false, error: 'Sign-in isn’t set up yet.' }, 503);
  const k = 'otp:' + email;
  const rec = email && code.length === 6 ? await env.WEDGE.get(k, 'json') : null;
  const bad = (msg) => json({ ok: false, error: msg || 'That code didn’t work. Check it, or ask for a new one.' }, 400);
  if (!rec) return bad('That code has expired or was already used. Ask for a new one.');
  if (rec.n >= 5) { await env.WEDGE.delete(k); return bad('Too many wrong codes. Ask for a new one.'); }
  if (!safeEqual(rec.h, await sha256Hex(`${code}:${email}:${env.SESSION_SECRET}`))) {
    await env.WEDGE.put(k, JSON.stringify({ ...rec, n: rec.n + 1 }), { expirationTtl: 600 });
    return bad();
  }
  await env.WEDGE.delete(k);
  const lv = await levelFor(env, email);
  return json({ ok: true, email, level: lv.level, planName: PLAN_NAME[lv.level] }, 200, { 'set-cookie': await makeSession(env, email, request) });
}
