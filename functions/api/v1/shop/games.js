// GET /api/v1/shop/games -> this week's and next week's games, soonest first, and whether Wedge has priced each one
import { json } from '../../../../lib/wedge.js';
import { gameList } from '../../../../lib/live.js';
import { LIVE } from '../../../../lib/gen/live.js';
export async function onRequestGet() {
  return json({ week: LIVE.week, games: gameList(), card_at: LIVE.card_at, sportsbooks: 'not connected' }, 200, { 'cache-control': 'public, max-age=60' });
}
