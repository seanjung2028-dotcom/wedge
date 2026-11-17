// /api/v1/ask
//   GET  -> whether the Analyst is switched on
//   POST {messages: [{role: "user"|"assistant", content: "..."}]} -> one answer: text, follow-ups, line cards, tools used
// The Claude call and every tool run here, on the server; see lib/analyst.js for the rules it enforces.
import { json, hit } from '../../../lib/wedge.js';
import { levelOf, clientIp } from '../../../lib/gate.js';
import { ask, MODEL } from '../../../lib/analyst.js';

const ready = (env) => !!env.ANTHROPIC_API_KEY && String(env.WEDGE_ANALYST || '').toLowerCase() !== 'off';

export async function onRequestGet({ env, request }) {
  const lv = await levelOf(env, request);
  return json({ ready: ready(env), model: env.ANALYST_MODEL || MODEL, level: lv });
}

export async function onRequestPost({ request, env }) {
  if (!ready(env)) return json({ error: 'not_configured', message: 'The Analyst isn’t switched on yet.' }, 503);
  let body;
  try { body = await request.json(); } catch (e) { return json({ error: 'bad request' }, 400); }
  const msgs = Array.isArray(body && body.messages) ? body.messages : [];
  const history = msgs.slice(-12).filter((m) => m && (m.role === 'user' || m.role === 'assistant') && typeof m.content === 'string' && m.content.trim())
    .map((m) => ({ role: m.role, content: m.content.slice(0, 2000) }));
  while (history.length && history[0].role !== 'user') history.shift();
  if (!history.length || history[history.length - 1].role !== 'user') return json({ error: 'ask a question' }, 400);
  const day = new Date().toISOString().slice(0, 10);
  const perIp = parseInt(env.ANALYST_PER_IP_DAY || '25', 10), total = parseInt(env.ANALYST_TOTAL_DAY || '400', 10);
  if (!(await hit(env, `ask:${day}:${clientIp(request)}`, perIp, 90000))) return json({ error: 'limit', message: `That’s ${perIp} questions today. The Analyst resets at midnight UTC.` }, 429);
  if (!(await hit(env, `ask:${day}:all`, total, 90000))) return json({ error: 'limit', message: 'The Analyst has answered all it can today. Try again tomorrow.' }, 429);
  try {
    const lv = await levelOf(env, request);
    const out = await ask(env, history, lv);
    return json({ ...out, at: new Date().toISOString() });
  } catch (e) {
    return json({ error: 'model_error', message: 'The Analyst couldn’t answer just now. Try again in a minute.', detail: String(e.message || e).slice(0, 160) }, 502);
  }
}
