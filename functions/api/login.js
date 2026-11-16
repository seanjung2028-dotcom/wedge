// POST /api/login {email} -> emails a 6-digit code to members and analysts.
// The answer is the same whether or not the email has access, so nobody can test which emails are members.
import { json, normEmail, validEmail, levelFor, hit, sha256Hex, sendCode, isLocal } from '../../lib/wedge.js';

export async function onRequestPost({ request, env }) {
  let body = {};
  try { body = await request.json(); } catch (e) { /* empty */ }
  const email = normEmail(body.email);
  if (!validEmail(email)) return json({ ok: false, error: 'Enter a valid email address.' }, 400);
  if (!env.WEDGE || !env.SESSION_SECRET) return json({ ok: false, error: 'Sign-in isn’t set up yet.' }, 503);
  const ip = request.headers.get('cf-connecting-ip') || 'local';
  if (!(await hit(env, 'ip:' + ip, 20, 3600)) || !(await hit(env, 'em:' + email, 5, 900))) {
    return json({ ok: false, error: 'Too many tries. Wait a few minutes, then try again.' }, 429);
  }
  const generic = { ok: true, message: 'If that email has a Wedge membership, a sign-in code is on its way.' };
  const lv = await levelFor(env, email);
  if (lv.level < 1) return json(generic);
  const n = crypto.getRandomValues(new Uint32Array(1))[0] % 1000000;
  const code = String(n).padStart(6, '0');
  await env.WEDGE.put('otp:' + email, JSON.stringify({ h: await sha256Hex(`${code}:${email}:${env.SESSION_SECRET}`), n: 0 }), { expirationTtl: 600 });
  if (!env.RESEND_API_KEY) {
    // local testing only: no email service, so hand the code back
    if (isLocal(request)) return json({ ...generic, devCode: code });
    return json({ ok: false, error: 'Sign-in email isn’t set up yet.' }, 503);
  }
  try { await sendCode(env, email, code, new URL(request.url).origin); }
  catch (e) { console.error(e); return json({ ok: false, error: 'We couldn’t send the email. Try again in a minute.' }, 502); }
  return json(generic);
}
