// GET /api/v1/shop/board?game=INDHOU&size=10 -> every open Kalshi receiving and rushing rung in one game, both sides,
// with the effective price on Kalshi and on Robinhood and, for plans that include it, Wedge's number on the live price.
import { json } from '../../../../lib/wedge.js';
import { levelOf } from '../../../../lib/gate.js';
import { GAME_RE, gameBoard } from '../../../../lib/live.js';
export async function onRequestGet({ request, env }) {
  const u = new URL(request.url), game = (u.searchParams.get('game') || '').toUpperCase();
  const size = Math.min(Math.max(parseInt(u.searchParams.get('size') || '10', 10) || 10, 1), 500);
  if (!GAME_RE.test(game)) return json({ error: 'game code like INDHOU required' }, 400);
  try {
    const lv = await levelOf(env, request);
    return json(await gameBoard(game, { wedge: lv >= 2, size }));
  } catch (e) {
    return json({ error: 'Kalshi did not answer', detail: String(e.message || e).slice(0, 120) }, 502);
  }
}
