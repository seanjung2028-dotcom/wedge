// /p/... -> the paid data. Research files need level 1, Inner Circle files level 2, analysts get everything.
// The files aren't static assets (nothing in /site can reach them): they're bundled into this function, gzipped,
// by v2/build_site.py (lib/protected). While WEDGE_GATING isn't "on", everyone gets everything (the site stays open).
import { access, gatingOn, json } from '../../lib/wedge.js';
import { FILES } from '../../lib/protected/manifest.js';

export async function onRequest({ request, env, params }) {
  if (request.method !== 'GET' && request.method !== 'HEAD') return json({ error: 'method not allowed' }, 405);
  const key = [].concat(params.path || []).join('/');
  const f = FILES[key];
  if (!f) return json({ error: 'not found' }, 404);
  const [body, type, need] = f;
  if (gatingOn(env)) {
    const a = await access(env, request);
    if (a.level < need) return json({ error: a.signedIn ? 'upgrade' : 'sign in' }, a.signedIn ? 403 : 401);
  }
  const h = new Headers({
    'content-type': type, 'content-encoding': 'gzip', vary: 'cookie, accept-encoding', 'x-robots-tag': 'noindex', 'x-content-type-options': 'nosniff',
    'cache-control': gatingOn(env) ? 'private, max-age=31536000' : 'public, max-age=31536000, immutable',
  });
  return new Response(request.method === 'HEAD' ? null : body, { status: 200, headers: h, encodeBody: 'manual' });
}
