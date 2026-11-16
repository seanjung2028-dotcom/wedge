// GET /api/me -> who is signed in, their level, and the checkout links
import { access, json, PLAN_NAME } from '../../lib/wedge.js';

export async function onRequestGet({ request, env }) {
  const a = await access(env, request);
  return json({
    gating: a.gating, signedIn: a.signedIn, email: a.email, level: a.level, plan: a.plan, planName: PLAN_NAME[a.level],
    until: a.until, source: a.source,
    signInReady: !!(env.WEDGE && env.SESSION_SECRET && (env.RESEND_API_KEY || false)),
    checkout: { research: env.CHECKOUT_RESEARCH || '', inner: env.CHECKOUT_INNER || '' },
    portal: env.BILLING_PORTAL || '',
  });
}
