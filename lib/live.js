// Line Shopping, server side. Shared by functions/api/v1/shop/* and the Analyst's tools (lib/analyst.js).
//
// Prices: Kalshi's public market data (no key needed), read through Cloudflare's cache for a few seconds.
// Robinhood has no API for event contracts; the NFL player props it lists are Kalshi contracts, so its price is
// Kalshi's book plus Robinhood's own fees. The five sportsbooks need a licensed odds feed, which isn't connected yet:
// they are listed as "no feed", never guessed.
// Wedge's number: lib/gen/live.js holds the lens move for every rung priced at the last card build (log-odds, middle
// and 10th/90th percentile); the live number is sigmoid(logit(live Kalshi mid) + move). Paid data: callers below the
// card's plan get prices only (see wedgeAllowed).
import { LIVE } from './gen/live.js';

export const KALSHI = 'https://api.elections.kalshi.com/trade-api/v2';
export const SERIES = { KXNFLREC: 'rec', KXNFLRECYDS: 'recyd', KXNFLRSHYDS: 'rushyd', KXNFLRRYDS: 'rryd' };
export const STAT_WORD = { rec: 'receptions', recyd: 'receiving yards', rushyd: 'rushing yards', rryd: 'rush + rec yards' };
export const BOOKS = ['DraftKings', 'FanDuel', 'BetMGM', 'Fanatics', 'Caesars'];
export const FRESH_S = 60;          // a quote older than this isn't "live"
export const MAX_SPREAD = 8;        // cents; wider books are "thin" (the card's own cutoff)
export const TICKER_RE = /^KXNFL(REC|RECYDS|RSHYDS|RRYDS)-[A-Z0-9]{6,20}-[A-Z0-9]{2,30}-\d{1,3}$/;
export const GAME_RE = /^[A-Z]{4,6}$/;

const num = (v) => (v == null || v === '' ? null : Number(v));
const cents = (v) => { const x = num(v); return x == null || !isFinite(x) ? null : Math.round(x * 10000) / 100; };
const r1 = (x) => (x == null ? null : Math.round(x * 10) / 10);
const r2 = (x) => (x == null ? null : Math.round(x * 100) / 100);
const lg = (p) => Math.log(p / (1 - p));
const sg = (z) => 1 / (1 + Math.exp(-z));

// ---------- fees, per contract, in cents ----------
// Kalshi taker fee: 0.07 x contracts x price x (1 - price), rounded up to the cent on the order.
export function kalshiFee(askC, n = 1) {
  const p = askC / 100, c = Math.max(1, Math.floor(n));
  return Math.ceil(0.07 * c * p * (1 - p) * 100 - 1e-9) / c;
}
// Robinhood: commission 10% x price x (1 - price) (5% with Gold), capped at 1c, plus the exchange's fee of up to 1c.
export function robinhoodFee(askC, gold = false) {
  const p = askC / 100;
  return Math.min(1, (gold ? 5 : 10) * p * (1 - p)) + 1;
}

// ---------- Kalshi ----------
export async function kx(path, ttl = 10) {
  const r = await fetch(KALSHI + path, { headers: { accept: 'application/json' }, cf: { cacheTtl: ttl, cacheEverything: true } });
  if (!r.ok) throw new Error(`Kalshi answered ${r.status}`);
  return r.json();
}

export function parseMarket(m) {
  const series = String(m.ticker || '').split('-')[0], stat = SERIES[series];
  if (!stat) return null;
  const sub = m.yes_sub_title || m.title || '', i = sub.lastIndexOf(':');
  const ev = String(m.event_ticker || ''), code = (ev.split('-')[1] || '').slice(7);
  const G = LIVE.games[code];
  const seg = String(m.ticker).split('-')[2] || '', kc = (t) => ({ JAX: 'JAC', WSH: 'WAS' }[t] || t);
  const team = G ? [G.a, G.h].find((t) => seg.startsWith(kc(t))) || null : null;
  return {
    ticker: m.ticker, series, stat, team, name: (i > 0 ? sub.slice(0, i) : sub).trim(), k: Math.round(num(m.floor_strike) + 0.5),
    code, game: G ? G.g : code, ko: G ? G.ko : null,
    ya: cents(m.yes_ask_dollars), yb: cents(m.yes_bid_dollars), na: cents(m.no_ask_dollars), nb: cents(m.no_bid_dollars),
    ya_n: num(m.yes_ask_size_fp), yb_n: num(m.yes_bid_size_fp), vol: num(m.volume_fp), status: m.status, updated: m.updated_time || null,
    rules: [m.rules_primary || '', m.rules_secondary || ''],
  };
}

// ---------- Wedge's number on the live price ----------
export function wedgeAt(ticker, x) {
  const L = LIVE.lens[ticker];
  if (!L) return { status: 'not_priced' };
  if (x.ya == null || x.yb == null || x.yb <= 0 || x.ya - x.yb > MAX_SPREAD) return { status: 'thin', mid0: L.mid0, why: L.why, q: L.q };
  const mid = (x.ya + x.yb) / 2, z = lg(Math.min(Math.max(mid / 100, 0.01), 0.99));
  return { status: 'ok', mid: r1(mid), p: r1(100 * sg(z + L.m)), lo: r1(100 * sg(z + L.ml)), hi: r1(100 * sg(z + L.mh)), mid0: L.mid0, why: L.why, q: L.q };
}
const flip = (w) => (w && w.status === 'ok' ? { ...w, mid: r1(100 - w.mid), p: r1(100 - w.p), lo: r1(100 - w.hi), hi: r1(100 - w.lo) } : w);
export function verdict(w, needs) {
  if (!w || w.status !== 'ok' || needs == null) return null;
  const call = w.lo - needs >= 0.5 ? 'Final-line price' : (w.p - needs >= 0.5 ? 'Lean price' : 'No edge at this price');
  return { call, gap: r1(w.p - needs), ev_mid: r1(w.p - needs), ev_lo: r1(w.lo - needs), ev_hi: r1(w.hi - needs) };
}
export const cardCall = (ticker, side) => LIVE.card[`${ticker}|${side === 'no' ? 'N' : 'Y'}`] || null;

// the side's numbers on one platform: ask, fee, effective price (all in cents = % of a $1 contract)
function sideQuote(x, side, size) {
  const ask = side === 'no' ? x.na : x.ya, bid = side === 'no' ? x.nb : x.yb;
  if (ask == null || ask <= 0 || ask >= 100) return null;
  const kf = kalshiFee(ask, size), rf = robinhoodFee(ask);
  return { ask, bid, spread: bid != null ? r1(ask - bid) : null, kalshi_fee: r2(kf), kalshi_eff: r2(ask + kf), rh_fee_max: r2(rf), rh_eff: r2(ask + rf) };
}

// ---------- one game's board ----------
export async function gameBoard(code, { wedge, size = 10 }) {
  const G = LIVE.games[code];
  if (!G) return { error: 'unknown game' };
  const at = new Date().toISOString();
  const lists = await Promise.all(Object.keys(SERIES).map((s) => kx(`/markets?event_ticker=${s}-${G.dc}${code}&limit=500`).then((d) => d.markets || []).catch(() => null)));
  const failed = lists.filter((l) => l == null).length;
  const rows = [];
  for (const m of lists.flat().filter(Boolean)) {
    const x = parseMarket(m);
    if (!x || x.status !== 'active' || x.ya == null) continue;
    const y = sideQuote(x, 'yes', size), n = sideQuote(x, 'no', size);
    const row = { t: x.ticker, n: x.name, tm: x.team, s: x.stat, k: x.k, ya: x.ya, yb: x.yb, na: x.na, dy: x.ya_n, y_eff: y && y.kalshi_eff, n_eff: n && n.kalshi_eff, y_rh: y && y.rh_eff, n_rh: n && n.rh_eff, up: x.updated };
    if (wedge) {
      const w = wedgeAt(x.ticker, x);
      if (w.status === 'ok') {
        row.w = [w.lo, w.p, w.hi];
        const vy = y && verdict(w, Math.min(y.kalshi_eff, y.rh_eff)), vn = n && verdict(flip(w), Math.min(n.kalshi_eff, n.rh_eff));
        row.gy = vy && vy.gap; row.gn = vn && vn.gap; row.cy = vy && vy.call; row.cn = vn && vn.call;
      } else row.ws = w.status;
      const cy = cardCall(x.ticker, 'yes'), cn = cardCall(x.ticker, 'no');
      if (cy) row.card_y = cy.call; if (cn) row.card_n = cn.call;
    }
    rows.push(row);
  }
  rows.sort((a, b) => a.n.localeCompare(b.n) || a.s.localeCompare(b.s) || a.k - b.k);
  return { at, game: G.g, code, ko: G.ko, rows, wedge: !!wedge, wedge_built: LIVE.built, card_at: LIVE.card_at, size, partial: failed > 0, failed_series: failed };
}

export function gameList() {
  const now = Date.now() - 4 * 3600e3;   // keep a game until about the end of it
  return Object.entries(LIVE.games).map(([code, g]) => ({ code, game: g.g, ko: g.ko, week: g.wk, priced: Object.keys(LIVE.lens).some((t) => t.includes(g.dc + code)) }))
    .filter((g) => !g.ko || Date.parse(g.ko) > now).sort((a, b) => (a.ko || '').localeCompare(b.ko || '') || a.game.localeCompare(b.game));
}

// ---------- one market, every platform ----------
function walk(levels, size) {
  // levels: [[priceC, contracts], ...] best first. Average price to fill `size` contracts.
  let need = size, cost = 0, got = 0;
  for (const [p, q] of levels) { const take = Math.min(need, q); cost += take * p; got += take; need -= take; if (need <= 0) break; }
  return got ? { avg: r2(cost / got), filled: got } : { avg: null, filled: 0 };
}

export async function marketDetail(ticker, { side = 'yes', size = 10, wedge }) {
  const series = ticker.split('-')[0], event = ticker.split('-').slice(0, 2).join('-'), stem = ticker.slice(0, ticker.lastIndexOf('-'));
  const now = Math.floor(Date.now() / 1000);
  const [m, ob, cs, ev] = await Promise.all([
    kx(`/markets/${ticker}`), kx(`/markets/${ticker}/orderbook?depth=20`).catch(() => null),
    kx(`/series/${series}/markets/${ticker}/candlesticks?start_ts=${now - 72 * 3600}&end_ts=${now}&period_interval=60`, 120).catch(() => null),
    kx(`/markets?event_ticker=${event}&limit=500`).catch(() => null),
  ]);
  const x = parseMarket(m.market || m);
  if (!x) return { error: 'not a market Line Shopping covers' };
  const at = new Date().toISOString();
  const q = sideQuote(x, side, size);
  // asks for this side come from the other side's bids: a Yes ask at p is a No bid at 100 - p
  const bids = ob && ob.orderbook_fp ? (side === 'no' ? ob.orderbook_fp.yes_dollars : ob.orderbook_fp.no_dollars) || [] : [];
  const asks = bids.map(([p, n]) => [Math.round((1 - Number(p)) * 10000) / 100, Number(n)]).sort((a, b) => a[0] - b[0]);
  const fill = walk(asks, size);
  const depth = asks.length ? asks[0][1] : null;
  const age = x.updated ? Math.max(0, Math.round((Date.now() - Date.parse(x.updated)) / 1000)) : null;
  const rows = [];
  if (q) {
    const kfFill = fill.avg != null ? kalshiFee(fill.avg, size) : q.kalshi_fee;
    rows.push({ platform: 'Kalshi', kind: 'Exchange', status: 'live', ask: q.ask, bid: q.bid, spread: q.spread, fee: q.kalshi_fee, eff: q.kalshi_eff,
      depth, fill_avg: fill.avg, filled: fill.filled, fill_eff: fill.avg != null ? r2(fill.avg + kfFill) : null, thin: q.spread == null || q.spread > MAX_SPREAD || (depth != null && depth < size) });
    rows.push({ platform: 'Robinhood', kind: 'Broker, on Kalshi’s book', status: 'live', ask: q.ask, bid: q.bid, spread: q.spread, fee: q.rh_fee_max, fee_note: 'up to', eff: q.rh_eff,
      depth, fill_avg: fill.avg, filled: fill.filled, fill_eff: fill.avg != null ? r2(fill.avg + robinhoodFee(fill.avg)) : null, thin: q.spread == null || q.spread > MAX_SPREAD || (depth != null && depth < size) });
  }
  for (const b of BOOKS) rows.push({ platform: b, kind: 'Sportsbook', status: 'no_feed', note: 'No licensed odds feed connected yet' });
  const live = rows.filter((r) => r.status === 'live' && r.eff != null);
  const best = live.length ? live.reduce((a, b) => (b.eff < a.eff ? b : a)) : null;
  let w = null, ver = null;
  if (wedge) {
    w = wedgeAt(ticker, x); if (side === 'no') w = flip(w);
    if (best) ver = verdict(w, best.eff);
  }
  const ladder = ev && ev.markets ? ev.markets.map(parseMarket).filter((y) => y && y.ticker.startsWith(stem + '-') && y.status === 'active' && y.ya != null).sort((a, b) => a.k - b.k).map((y) => {
    const qq = sideQuote(y, side, size); const o = { ticker: y.ticker, k: y.k, ask: qq && qq.ask, eff: qq && Math.min(qq.kalshi_eff, qq.rh_eff) };
    if (wedge) { let ww = wedgeAt(y.ticker, y); if (side === 'no') ww = flip(ww); if (ww.status === 'ok') { o.w = ww.p; o.gap = o.eff != null ? r1(ww.p - o.eff) : null; } }
    return o;
  }) : [];
  const history = cs && cs.candlesticks ? cs.candlesticks.map((c) => {
    const ya = cents(c.yes_ask && c.yes_ask.close_dollars), yb = cents(c.yes_bid && c.yes_bid.close_dollars);
    const ask = side === 'no' ? (yb != null ? r2(100 - yb) : null) : ya, bid = side === 'no' ? (ya != null ? r2(100 - ya) : null) : yb;
    return { t: c.end_period_ts, ask, bid, vol: num(c.volume_fp) };
  }).filter((h) => h.ask != null) : [];
  return {
    at, ticker, game: x.game, ko: x.ko, name: x.name, team: x.team, stat: x.stat, stat_word: STAT_WORD[x.stat], k: x.k, side, size,
    line: `${x.name} ${side === 'no' ? 'under ' + x.k : x.k + '+'} ${STAT_WORD[x.stat]} (${side === 'no' ? 'No' : 'Yes'})`,
    updated: x.updated, age_s: age, rows, best: best ? best.platform : null, best_eff: best ? best.eff : null,
    wedge: w, verdict: ver, card: wedge ? cardCall(ticker, side) : null, wedge_locked: !wedge, wedge_built: LIVE.built,
    ladder, history, rules: x.rules,
  };
}
