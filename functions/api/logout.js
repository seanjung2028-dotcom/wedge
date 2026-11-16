// POST /api/logout -> clears the sign-in cookie
import { json, clearSession } from '../../lib/wedge.js';

export async function onRequestPost({ request }) {
  return json({ ok: true }, 200, { 'set-cookie': clearSession(request) });
}
