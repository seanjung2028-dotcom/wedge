"""Backtest pool, Weeks 2-6 (rebuilt lines). Robinhood didn't keep player-prop prices before Week 7, so each line is rebuilt
the way the books set them, fit on the real Week 7-9 main lines:
  line = a + b1 * season average + b2 * last-4 average, both shrunk toward the player's 2024-26 average (k games),
  rounded to the nearest real rung (x.5 for receptions, x4.5 / x9.5 for yards), priced at the chance the rebuilt
  median clears that rung (normal spread fit on Weeks 7-9), Yes ask = that price, No = 100 - Yes + 1.
Which players get a line: the same share of each stat and position as the real Week 7-9 boards (about 23 a game).
Only players who took an offensive snap that week (Robinhood voids the rest); point-in-time lens features.
Validated on Weeks 7-9 against the real lines. Writes bt/card_bt/pool_rebuilt.pkl and rebuild_check.json."""
import json, sys, math
import numpy as np, pandas as pd
W = '/home/claude/wedger/'; N = W + 'nfl/'
sys.path.insert(0, W + 'lens'); import core
live, st26, pos26 = core.load(W + 'dl18/')
SW = {2026: 1.0, 2025: 0.75, 2024: 0.5}
frames = []
for yr in (2024, 2025, 2026):
    s = pd.read_csv(N + f'stats_player_week_{yr}.csv', low_memory=False); s = s[s.season_type == 'REG']
    s = s[['player_id', 'player_display_name', 'position', 'season', 'week', 'team', 'opponent_team', 'receptions', 'receiving_yards', 'rushing_yards']].copy()
    frames.append(s)
S = pd.concat(frames, ignore_index=True)
for c in ('receptions', 'receiving_yards', 'rushing_yards'): S[c] = S[c].fillna(0)
S['rec'], S['recyd'], S['rushyd'] = S.receptions, S.receiving_yards, S.rushing_yards; S['rryd'] = S.recyd + S.rushyd
S['team'] = S.team.map(core.fx); S['opponent_team'] = S.opponent_team.map(core.fx); S['nn'] = S.player_display_name.map(core.nn)
S['ord'] = S.season * 100 + S.week
sn = pd.read_csv(N + 'snap_counts_2026.csv'); sn = sn[(sn.game_type == 'REG') & (sn.offense_snaps.fillna(0) > 0)].copy()
sn['team'] = sn.team.map(core.fx); sn['opponent'] = sn.opponent.map(core.fx); sn['nn'] = sn.player.map(core.nn)
PLAY = {(int(r.week), r.nn): (r.team, r.opponent) for r in sn.itertuples(index=False)}
STATS = {'recyd': ('WR', 'TE', 'RB'), 'rec': ('WR', 'TE', 'RB'), 'rushyd': ('RB', 'QB'), 'rryd': ('RB',)}
G = {pid: d.sort_values('ord') for pid, d in S.groupby('player_id')}
P26 = S[S.season == 2026]
def cands(wk):
    """every player with a 2026 game before this week who took an offensive snap this week -> base numbers per stat"""
    prior = P26[P26.week < wk].sort_values('week').drop_duplicates('player_id', keep='last')
    out = []
    for r in prior.itertuples(index=False):
        if r.position not in ('WR', 'TE', 'RB', 'QB'): continue
        pl = PLAY.get((wk, r.nn))
        if not pl: continue
        team, opp = pl
        d = G[r.player_id]; h = d[d.ord < 202600 + wk]; cur = h[h.season == 2026]
        now = d[(d.season == 2026) & (d.week == wk)]
        for stt, poss in STATS.items():
            if r.position not in poss: continue
            w = h.season.map(SW).values; C = float(np.sum(w * h[stt].values) / np.sum(w))
            out.append({'wk': wk, 'pid': r.player_id, 'player': r.player_display_name, 'nn': r.nn, 'pos': r.position, 'team': team, 'opp': opp, 'stat': stt,
                        'n': len(cur), 'Sv': float(cur[stt].mean()), 'L4': float(cur[stt].tail(4).mean()), 'C': C,
                        'actual': float(now[stt].iloc[0]) if len(now) else 0.0})
    return pd.DataFrame(out)
def X(d, k):
    n4 = d.n.clip(upper=4)
    Sh = (d.n * d.Sv + k * d.C) / (d.n + k); L4h = (n4 * d.L4 + k * d.C) / (n4 + k)
    return np.column_stack([np.ones(len(d)), Sh, L4h])
# ---- fit on the real Week 7-9 main lines
R = pd.read_pickle(W + 'bt/card_bt/pool_real.pkl')
C79 = pd.concat([cands(w) for w in (7, 8, 9)], ignore_index=True)
M = C79.merge(R[['wk', 'pid', 'stat', 'line', 'ya', 'y']], on=['wk', 'pid', 'stat'], how='left')
FIT, chk = {}, {}
for stt in STATS:
    d = M[(M.stat == stt) & M.line.notna()]
    best = None
    for k in (0, 1, 2, 3, 4, 6, 8, 12):
        b, *_ = np.linalg.lstsq(X(d, k), d.line.values, rcond=None); mae = float(np.mean(np.abs(X(d, k) @ b - d.line.values)))
        if best is None or mae < best[0]: best = (mae, k, b)
    mae, k, b = best
    res = d.actual.values - (X(d, k) @ b); sd = np.polyfit(X(d, k) @ b, np.abs(res) * 1.25, 1)
    FIT[stt] = {'k': k, 'b': b.tolist(), 'sd': sd.tolist()}; chk[stt] = {'n_real': int(len(d)), 'mae_vs_real_line': round(mae, 2), 'k': k, 'b': [round(float(x), 3) for x in b]}
def rung(stt, m):
    if stt == 'rec': return max(0.5, math.floor(m) + 0.5)
    return max(4.5, 5 * round((m - 4.5) / 5) + 4.5)
def lines(d):
    d = d.copy(); f = [FIT[s] for s in d.stat]
    d = d.reset_index(drop=True); d['med'] = 0.0
    for stt, fi in FIT.items():
        ix = d.index[d.stat == stt]
        if len(ix): d.loc[ix, 'med'] = X(d.loc[ix], fi['k']) @ np.array(fi['b']) + DELTA.get(stt, 0.0)
    f = [FIT[s] for s in d.stat]
    d['line'] = [rung(s, m) for s, m in zip(d.stat, d.med)]
    sdv = np.array([max(0.6 if s == 'rec' else 8.0, fi['sd'][0] * m + fi['sd'][1]) for s, m, fi in zip(d.stat, d.med, f)])
    p = 1 - pd.Series([0.5 * (1 + math.erf((l - m) / (s * math.sqrt(2)))) for l, m, s in zip(d.line, d.med, sdv)])
    d['mid'] = p.clip(0.35, 0.65).values; d['ya'] = np.round(100 * d.mid + 0.5); d['na'] = 101.0 - d.ya; d['mid'] = (d.ya - 0.5) / 100
    d['y'] = (d.actual > d.line).astype(float)
    return d
# ---- level: shift each stat's rebuilt line so it clears as often as the real lines did in Weeks 7-9 (the books' over/under lean)
DELTA = {}
def sel_rate(stt, dl):
    DELTA[stt] = dl; L = lines(C79[C79.stat == stt]); L = L.merge(R[['wk', 'pid', 'stat']].assign(has=1), on=['wk', 'pid', 'stat'], how='left')
    want = int((R.stat == stt).sum()); top = L.sort_values('med', ascending=False).head(want)
    return float(top.y.mean()), float(top.ya.mean())
for stt in STATS:
    grid = np.arange(-1.0, 1.01, 0.1) if stt == 'rec' else np.arange(-10, 10.1, 0.5)
    tgt = float(R[R.stat == stt].y.mean())
    DELTA[stt] = float(min(grid, key=lambda dl: abs(sel_rate(stt, dl)[0] - tgt) + 0.002 * abs(dl)))
    chk[stt]['shift'] = round(DELTA[stt], 2); chk[stt]['over_real'] = round(tgt, 3); chk[stt]['over_rebuilt'], chk[stt]['price_rebuilt'] = [round(v, 3) for v in sel_rate(stt, DELTA[stt])]
# ---- who gets a line: match the real boards' count per stat and position (per game), by rebuilt line size
L79 = lines(C79); L79 = L79.merge(R[['wk', 'pid', 'stat', 'line']].rename(columns={'line': 'real_line'}), on=['wk', 'pid', 'stat'], how='left')
ngames79 = R.groupby('wk').game.nunique().sum()
THR = {}
for (stt, ps), d in L79.groupby(['stat', 'pos']):
    want = int(((R.stat == stt) & (R.pos == ps)).sum())
    if want == 0: THR[(stt, ps)] = 1e9; continue
    THR[(stt, ps)] = float(d.med.sort_values(ascending=False).iloc[min(want, len(d)) - 1])
sel = lambda d: d[[d_med >= THR.get((s, p), 1e9) for d_med, s, p in zip(d.med, d.stat, d.pos)]]
S79 = sel(L79)
both = S79[S79.real_line.notna()]
chk['weeks7_9'] = {'real_lines': int(len(R)), 'rebuilt_lines': int(len(S79)), 'same_player_stat': int(len(both)),
                   'rung_exact': round(float((both.line == both.real_line).mean()), 3), 'mae_rung_vs_real': round(float((both.line - both.real_line).abs().mean()), 2),
                   'over_rate_real': round(float(R.y.mean()), 3), 'over_rate_rebuilt': round(float(S79.y.mean()), 3),
                   'avg_yes_price_real': round(float(R.ya.mean()), 1), 'avg_yes_price_rebuilt': round(float(S79.ya.mean()), 1)}
# ---- Weeks 2-6
out = []
for wk in range(2, 10):   # 7-9 too, only to check the rebuild against the real lines
    T = core.Tables(live, st26, pos26, wk)
    d = sel(lines(cands(wk)))
    for r in d.itertuples(index=False):
        f = core.features(T, r.pid, r.team, r.opp, r.stat, r.line, r.mid)
        out.append({'wk': wk, 'src': 'rebuilt', 'game': None, 'player': r.player, 'pid': r.pid, 'pos': r.pos, 'team': r.team, 'opp': r.opp, 'stat': r.stat,
                    'line': r.line, 'ya': r.ya, 'na': r.na, 'mid': r.mid, 'y': r.y, 'actual': r.actual, 'med': r.med, **f})
P = pd.DataFrame(out)
g = pd.read_csv(N + 'games.csv'); g = g[(g.season == 2026) & (g.game_type == 'REG')]
GM = {}
for x in g.itertuples(index=False):
    a, h = core.fx(x.away_team), core.fx(x.home_team); GM[(x.week, a)] = GM[(x.week, h)] = f'{a} @ {h}'
P['game'] = [GM.get((w, t)) for w, t in zip(P.wk, P.team)]
P.to_pickle(W + 'bt/card_bt/pool_rebuilt.pkl')
chk['weeks2_6'] = {int(w): {'lines': int((P.wk == w).sum()), 'games': int(P[P.wk == w].game.nunique()), 'over_rate': round(float(P[P.wk == w].y.mean()), 3)} for w in range(2, 10)}
json.dump({'fit': FIT, 'shift': DELTA, 'check': chk, 'thresholds': {f'{a}|{b}': c for (a, b), c in THR.items()}}, open(W + 'bt/card_bt/rebuild_check.json', 'w'), indent=1)
print(json.dumps(chk, indent=1))
