// Wedge membership: email sign-in, sessions and tiers. Shared by the Cloudflare Pages Functions in /functions.
//
// Levels: 0 free, 1 Research, 2 Inner Circle, 3 Analyst (everything).
// Where a level comes from, highest wins:
//   ANALYST_EMAILS / INNER_EMAILS / RESEARCH_EMAILS  comma-separated lists set in the Pages project (manual access, comps)
//   KV key m:<email>                                  written by the Stripe webhook (paid members)
//
// Settings (Pages project > Settings > Variables and Secrets; KV under Settings > Bindings):
//   WEDGE_GATING      "on" to lock paid pages. Anything else: the whole site stays open (the default).
//   SESSION_SECRET    secret, any long random string. Signs the sign-in cookie.
//   RESEND_API_KEY    secret, from resend.com. Sends the sign-in codes.
//   MAIL_FROM         e.g. Wedge <login@wedgepicks.com> (the domain must be verified in Resend)
//   STRIPE_WEBHOOK_SECRET  secret, from the Stripe webhook endpoint (whsec_...)
//   CHECKOUT_RESEARCH, CHECKOUT_INNER   checkout links (Stripe Payment Links or any processor)
//   BILLING_PORTAL    optional: Stripe customer portal link, shown to members
//   SEASON_END        YYYY-MM-DD when season passes run out (default 2027-02-15)
//   WEDGE (KV binding) members, sign-in codes, rate limits

export const LEVELS = { free: 0, research: 1, inner: 2, analyst: 3 };
export const PLAN_NAME = ['Free', 'Research', 'Inner Circle', 'Analyst'];
const COOKIE = 'wedge_s';
const SESSION_DAYS = 30;
const enc = new TextEncoder();

export const gatingOn = (env) => String(env.WEDGE_GATING || '').toLowerCase() === 'on';
export const isLocal = (req) => /^(localhost|127\.0\.0\.1|\[::1\])$/.test(new URL(req.url).hostname);
export const normEmail = (e) => String(e || '').trim().toLowerCase();
export const validEmail = (e) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(e) && e.length <= 254;
const list = (v) => String(v || '').split(/[\s,;]+/).map(normEmail).filter(Boolean);

export function json(body, status = 200, headers = {}) {
  return new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...headers } });
}

// ---------- signing ----------
const b64u = (buf) => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const unb64u = (s) => { s = s.replace(/-/g, '+').replace(/_/g, '/'); while (s.length % 4) s += '='; return Uint8Array.from(atob(s), (c) => c.charCodeAt(0)); };
async function hmacKey(secret) {
  return crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign', 'verify']);
}
export async function hmacHex(secret, msg) {
  const sig = await crypto.subtle.sign('HMAC', await hmacKey(secret), enc.encode(msg));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, '0')).join('');
}
export async function sha256Hex(msg) {
  const d = await crypto.subtle.digest('SHA-256', enc.encode(msg));
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, '0')).join('');
}
export function safeEqual(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string' || a.length !== b.length) return false;
  let x = 0; for (let i = 0; i < a.length; i++) x |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return x === 0;
}

// ---------- sessions ----------
export async function makeSession(env, email, req) {
  if (!env.SESSION_SECRET) throw new Error('SESSION_SECRET is not set');
  const body = b64u(enc.encode(JSON.stringify({ e: email, x: Math.floor(Date.now() / 1000) + SESSION_DAYS * 86400 })));
  const sig = b64u(await crypto.subtle.sign('HMAC', await hmacKey(env.SESSION_SECRET), enc.encode(body)));
  return `${COOKIE}=${body}.${sig}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${SESSION_DAYS * 86400}${isLocal(req) ? '' : '; Secure'}`;
}
export function clearSession(req) {
  return `${COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0${isLocal(req) ? '' : '; Secure'}`;
}
export async function readSession(env, req) {
  if (!env.SESSION_SECRET) return null;
  const m = new RegExp(`(?:^|;\\s*)${COOKIE}=([A-Za-z0-9_-]+)\\.([A-Za-z0-9_-]+)`).exec(req.headers.get('cookie') || '');
  if (!m) return null;
  try {
    const ok = await crypto.subtle.verify('HMAC', await hmacKey(env.SESSION_SECRET), unb64u(m[2]), enc.encode(m[1]));
    if (!ok) return null;
    const p = JSON.parse(new TextDecoder().decode(unb64u(m[1])));
    if (!p.e || !p.x || p.x < Date.now() / 1000) return null;
    return { email: p.e };
  } catch (e) { return null; }
}

// ---------- membership ----------
export function seasonEnd(env) {
  const t = Date.parse((env.SEASON_END || '2027-02-15') + 'T23:59:59-06:00');
  return Number.isFinite(t) ? Math.floor(t / 1000) : 0;
}
export async function getMember(env, email) {
  if (!env.WEDGE || !email) return null;
  try { return await env.WEDGE.get('m:' + email, 'json'); } catch (e) { return null; }
}
export async function putMember(env, email, m) {
  m.updated = new Date().toISOString();
  await env.WEDGE.put('m:' + email, JSON.stringify(m));
}
// the highest level an email has right now, with where it came from
export async function levelFor(env, email) {
  const out = { level: 0, plan: 'free', until: null, source: null };
  if (!email) return out;
  const bump = (lv, src, until = null) => { if (lv > out.level) Object.assign(out, { level: lv, source: src, until }); };
  if (list(env.ANALYST_EMAILS).includes(email)) bump(3, 'analyst');
  if (list(env.INNER_EMAILS).includes(email)) bump(2, 'comp');
  if (list(env.RESEARCH_EMAILS).includes(email)) bump(1, 'comp');
  const m = await getMember(env, email);
  const now = Date.now() / 1000;
  if (m && m.inner && m.inner.status === 'active' && (!m.inner.until || m.inner.until > now)) bump(2, 'season pass', m.inner.until || null);
  if (m && m.research && ['active', 'trialing', 'past_due'].includes(m.research.status)) bump(1, 'subscription');
  out.plan = ['free', 'research', 'inner', 'analyst'][out.level];
  return out;
}
export async function access(env, req) {
  const s = await readSession(env, req);
  const lv = await levelFor(env, s && s.email);
  return { gating: gatingOn(env), signedIn: !!s, email: s ? s.email : null, ...lv };
}

// ---------- rate limits (KV, coarse) ----------
export async function hit(env, key, max, ttl) {
  if (!env.WEDGE) return true;
  const k = 'rl:' + key;
  const n = Number((await env.WEDGE.get(k)) || 0);
  if (n >= max) return false;
  await env.WEDGE.put(k, String(n + 1), { expirationTtl: ttl });
  return true;
}

// ---------- email ----------
export async function sendCode(env, to, code, origin) {
  const link = `${origin}/#signin/${encodeURIComponent(to)}/${code}`;
  const html = `<!doctype html><html><body style="margin:0;padding:32px 16px;background:#151614;font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:#e9e7e1">
<table role="presentation" width="100%" style="max-width:480px;margin:0 auto"><tr><td>
<p style="margin:0 0 24px;font-size:22px;font-weight:800;letter-spacing:-.02em;color:#ffffff">wedge<span style="color:#7ED957">.</span></p>
<p style="margin:0 0 8px;font-size:15px;color:#b9b7b0">Your sign-in code</p>
<p style="margin:0 0 24px;font-size:36px;font-weight:700;letter-spacing:.18em;color:#ffffff;font-family:ui-monospace,Menlo,monospace">${code}</p>
<p style="margin:0 0 28px"><a href="${link}" style="display:inline-block;background:#7ED957;color:#111;text-decoration:none;font-weight:700;padding:12px 22px;border-radius:999px">Sign in to Wedge</a></p>
<p style="margin:0;font-size:13px;line-height:1.5;color:#8d8b85">The code works for 10 minutes. If you didn't ask to sign in, you can ignore this email.</p>
</td></tr></table></body></html>`;
  const text = `Your Wedge sign-in code: ${code}\n\nOr open: ${link}\n\nThe code works for 10 minutes. If you didn't ask to sign in, ignore this email.`;
  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { authorization: `Bearer ${env.RESEND_API_KEY}`, 'content-type': 'application/json' },
    body: JSON.stringify({ from: env.MAIL_FROM || 'Wedge <login@wedgepicks.com>', to: [to], subject: `${code} is your Wedge sign-in code`, html, text }),
  });
  if (!r.ok) throw new Error('email failed: ' + r.status + ' ' + (await r.text()).slice(0, 200));
}
