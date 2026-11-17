// GET /api/v1/shop/market?ticker=KXNFLREC-...&side=yes&size=10 -> one line on every platform: price after fees,
// depth, the best price, Wedge's number and estimated value (plans that include it), the ladder and 72 hours of prices.
import { json } from '../../../../lib/wedge.js';
import { levelOf } from '../../../../lib/gate.js';
import { TICKER_RE, marketDetail } from '../../../../lib/live.js';
export async function onRequestGet({ request, env }) {
  const u = new URL(request.url), ticker = (u.searchParams.get('ticker') || '').toUpperCase();
  const side = u.searchParams.get('side') === 'no' ? 'no' : 'yes';
  const size = Math.min(Math.max(parseInt(u.searchParams.get('size') || '10', 10) || 10, 1), 500);
  if (!TICKER_RE.test(ticker)) return json({ error: 'not a line Line Shopping covers' }, 400);
  try {
    const lv = await levelOf(env, request);
    const d = await marketDetail(ticker, { side, size, wedge: lv >= 2 });
    return json(d, d.error ? 404 : 200);
  } catch (e) {
    return json({ error: 'Kalshi did not answer', detail: String(e.message || e).slice(0, 120) }, 502);
  }
}
