// Which plan level a request has, for the live tools. While WEDGE_GATING isn't "on" the whole site is open (level 3),
// exactly like /p/. Wedge's numbers and the card need level 2 (Inner Circle), the record list level 1 (Research).
import { access, gatingOn } from './wedge.js';
export async function levelOf(env, request) {
  if (!gatingOn(env)) return 3;
  try { return (await access(env, request)).level || 0; } catch (e) { return 0; }
}
export const clientIp = (request) => request.headers.get('cf-connecting-ip') || request.headers.get('x-forwarded-for') || 'unknown';
