"""Moskowitz (AQR), 'Asset Pricing and Sports Betting': do early-to-late price moves over-react and reverse by the result?
Kalshi player-prop ladders for Week 8, five snapshots (Tue AM -> Sun 10:50 AM). Mid price = (Yes ask + Yes bid) / 2."""
import json, re, unicodedata, numpy as np, pandas as pd
W = '/home/claude/wedger/'; R = W + 'rh/'
def nn(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', s); return re.sub(r'[^a-z]', '', s)
SNAP = [('tue_am', 'kalshi_props_w8_am.json'), ('tue_pm', 'kalshi_props_w8_1027pm.json'), ('wed', 'kalshi_props_w8_1028.json'), ('thu', 'kalshi_props_w8_1029.json'), ('sun', 'kalshi_props_w8_1101.json')]
COL = {'KXNFLRECYDS': 'receiving_yards', 'KXNFLRSHYDS': 'rushing_yards', 'KXNFLPASSYDS': 'passing_yards', 'KXNFLPASSTDS': 'passing_tds', 'KXNFLREC': 'receptions', 'KXNFLTD': 'td', 'KXNFLRRYDS': 'rr'}
rows = {}
for tag, f in SNAP:
    d = json.load(open(R + f))
    for ser, rs in d['series'].items():
        if ser not in COL: continue
        for ev, tick, sub, strike, ya, yb, na, last, vol, status in rs:
            try: ya, yb = float(ya), float(yb)
            except Exception: continue
            if ya <= 0 or yb <= 0: continue
            r = rows.setdefault(tick, {'ser': ser, 'player': sub.split(':')[0].strip(), 'strike': float(strike), 'game': ev.split('-')[1]})
            r[tag] = (ya + yb) / 2; r[tag + '_sp'] = ya - yb
D = pd.DataFrame.from_dict(rows, orient='index')
st = pd.read_csv(W + 'dl8/stats_player_week_2026.csv', low_memory=False); st = st[(st.week == 8) & (st.season_type == 'REG')].copy()
for c in ['receptions', 'receiving_yards', 'rushing_yards', 'passing_yards', 'passing_tds', 'rushing_tds', 'receiving_tds']: st[c] = pd.to_numeric(st[c], errors='coerce').fillna(0)
st['td'] = st.rushing_tds + st.receiving_tds; st['rr'] = st.rushing_yards + st.receiving_yards
S = {nn(r.player_display_name): r for r in st.itertuples(index=False)}
sn = pd.read_csv(W + 'dl8/snap_counts_2026.csv'); played = {nn(p) for p, o in zip(sn[sn.week == 8].player, sn[sn.week == 8].offense_snaps) if o > 0}
def settle(r):
    k = nn(r.player); p = S.get(k)
    if p is None: return np.nan if k not in played else 0.0
    return float(getattr(p, COL[r.ser]) > r.strike)
D['y'] = [settle(r) for r in D.itertuples()]
D = D[D.y.notna()]
print('contracts settled', len(D), D.ser.value_counts().to_dict())
def test(a, b, lo=0.15, hi=0.85, maxsp=0.06):
    d = D.dropna(subset=[a, b]); d = d[d[b].between(lo, hi) & (d[b + '_sp'] <= maxsp) & (d[a + '_sp'] <= maxsp)]
    mv = d[b] - d[a]; res = d.y - d[b]
    X = np.column_stack([np.ones(len(d)), mv]); beta = np.linalg.lstsq(X, res, rcond=None)[0]
    e = res - X @ beta; se = np.sqrt(np.sum(e ** 2) / (len(d) - 2) / np.sum((mv - mv.mean()) ** 2))
    # by game cluster robust-ish: report n games
    print(f'{a:>6s} -> {b:<4s} n={len(d):5d}  mean |move| {mv.abs().mean():.3f}   slope of (result - late price) on move = {beta[1]:+.3f} (se {se:.3f})   '
          f'moved up: hit-late {res[mv > 0.03].mean():+.3f} (n {int((mv > 0.03).sum())}), moved down: {res[mv < -0.03].mean():+.3f} (n {int((mv < -0.03).sum())})')
for a, b in [('tue_pm', 'thu'), ('wed', 'thu'), ('tue_pm', 'sun'), ('wed', 'sun'), ('thu', 'sun')]:
    test(a, b)
print('\nper-snapshot Brier on the same contracts (all with Wed and Sun prices, 15-85c):')
d = D.dropna(subset=['wed', 'thu', 'sun']); d = d[d.sun.between(0.15, 0.85)]
for t in ['wed', 'thu', 'sun']: print(t, len(d), round(np.mean((d[t] - d.y) ** 2), 4))
D.to_pickle(W + 'bt/linemove.pkl')
