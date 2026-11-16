"""Settle every Week 10 line the site posted for Thursday WSH @ NYG (Thu Nov 12 6:44 PM CT board). Sunday/Monday settle after they are final.
Writes bt/w10_settled.csv (all rows, model fields kept)."""
import pandas as pd, numpy as np, re, unicodedata, csv, json
W = '/home/claude/wedger/'
def nn(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', s); return re.sub(r'[^a-z]', '', s)
FIX = {'LA': 'LAR', 'WAS': 'WSH', 'JAC': 'JAX'}; fx = lambda t: FIX.get(t, t)
st = pd.read_csv(W + 'dl19/stats_player_week_2026.csv', low_memory=False); st = st[(st.week == 10) & (st.season_type == 'REG')].copy()
st['team'] = st['team'].map(fx)
for c in ['receptions', 'receiving_yards', 'rushing_yards', 'passing_yards', 'passing_tds', 'passing_interceptions', 'rushing_tds', 'receiving_tds', 'carries', 'targets']:
    st[c] = pd.to_numeric(st[c], errors='coerce').fillna(0)
P = {(nn(r.player_display_name), r.team): r for r in st.itertuples(index=False)}
PN = {}
for r in st.itertuples(index=False): PN.setdefault(nn(r.player_display_name), []).append(r)
sn = pd.read_csv(W + 'dl19/snap_counts_2026.csv'); sn = sn[(sn.week == 10)]; sn['team'] = sn['team'].map(fx)
PLAYED = {(nn(r.player), r.team) for r in sn.itertuples(index=False) if (r.offense_snaps or 0) > 0}
PLAYED_N = {nn(r.player) for r in sn.itertuples(index=False) if (r.offense_snaps or 0) > 0}
g = pd.read_csv(W + 'dl19/games.csv'); g = g[(g.season == 2026) & (g.week == 10) & g.home_score.notna()]
SC = {f"{fx(r.away_team)} @ {fx(r.home_team)}": (fx(r.away_team), fx(r.home_team), int(r.away_score), int(r.home_score), r.game_id) for r in g.itertuples(index=False)}
pbp = pd.read_csv(W + 'dl19/play_by_play_2026.csv.gz', usecols=['game_id', 'week', 'qtr', 'total_home_score', 'total_away_score'], low_memory=False)
pbp = pbp[pbp.week == 10]
H1 = {gid: (int(d[d.qtr <= 2].total_away_score.max()), int(d[d.qtr <= 2].total_home_score.max())) for gid, d in pbp.groupby('game_id')}
CITY = {'ARI': 'Arizona', 'ATL': 'Atlanta', 'BAL': 'Baltimore', 'BUF': 'Buffalo', 'CAR': 'Carolina', 'CHI': 'Chicago', 'CIN': 'Cincinnati', 'CLE': 'Cleveland',
        'DAL': 'Dallas', 'DEN': 'Denver', 'DET': 'Detroit', 'GB': 'Green Bay', 'HOU': 'Houston', 'IND': 'Indianapolis', 'JAX': 'Jacksonville', 'KC': 'Kansas City', 'LV': 'Las Vegas',
        'LAC': 'Los Angeles C', 'LAR': 'Los Angeles R', 'MIA': 'Miami', 'MIN': 'Minnesota', 'NE': 'New England', 'NO': 'New Orleans', 'NYG': 'New York G', 'NYJ': 'New York J',
        'PHI': 'Philadelphia', 'PIT': 'Pittsburgh', 'SF': 'San Francisco', 'SEA': 'Seattle', 'TB': 'Tampa Bay', 'TEN': 'Tennessee', 'WSH': 'Washington'}
STAT = {'Receiving Yards': ('receiving_yards', 'rec yds', 'recyd'), 'Receptions': ('receptions', 'rec', 'rec'), 'Rushing Yards': ('rushing_yards', 'rush yds', 'rushyd'),
        'Passing Yards': ('passing_yards', 'pass yds', 'passyd'), 'Passing Touchdowns': ('passing_tds', 'pass TDs', 'passtd'),
        'Interceptions': ('passing_interceptions', 'INTs', 'int'), 'Rushing + Receiving Yards': ('rr', 'rush + rec yds', 'rryd')}
def player(name, teams):
    k = nn(name)
    for t in teams:
        if (k, t) in P: return P[(k, t)], True
    played = any((k, t) in PLAYED for t in teams) or (k in PLAYED_N)
    return None, played
def val(p, col):
    if p is None: return 0.0
    if col == 'rr': return float(p.rushing_yards) + float(p.receiving_yards)
    return float(getattr(p, col))
rows = []
L = pd.read_csv(W + 'pull1112/thu_out/inband_w10.csv', dtype=str, keep_default_na=False)  # Thu Nov 12 6:44 PM CT board
L = L[L.game == 'WSH @ NYG']
for r in L.to_dict('records'):
    if r['game'] not in SC: continue
    a, h, sa, sh, gid = SC[r['game']]; m, c = r['market'], r['contract']; out, det, stat, line, pl = None, '', '', None, ''
    if m in STAT:
        mm = re.match(r'^(.*?): Over ([\d.]+) ', c)
        if not mm: continue
        pl, line = mm.group(1), float(mm.group(2)); col, unit, stat = STAT[m]
        p, played = player(pl, [a, h])
        if p is None and not played: out, det = 'Void', 'did not play'
        else: v = val(p, col); out = 'Won' if v > line else 'Lost'; det = f'{v:g} {unit}'
    elif m == 'Anytime Touchdown':
        pl = c; stat = 'td'; line = 0.5
        p, played = player(pl, [a, h])
        if p is None and not played: out, det = 'Void', 'did not play'
        else: td = 0 if p is None else int(p.rushing_tds + p.receiving_tds); out = 'Won' if td >= 1 else 'Lost'; det = f'{td} TD'
    elif m == 'Moneyline':
        t = fx(c.strip()); won = (t == h and sh > sa) or (t == a and sa > sh); out = 'Won' if won else 'Lost'; stat = 'ml'
    elif m == 'Spreads':
        mm = re.match(r'^(.*) wins by over ([\d.]+) points', c); team = a if mm.group(1) == CITY[a] else h
        line = float(mm.group(2)); marg = (sh - sa) if team == h else (sa - sh); out = 'Won' if marg > line else 'Lost'; stat = 'spread'
    elif m == 'Totals':
        line = float(re.search(r'Over ([\d.]+)', c).group(1)); out = 'Won' if sa + sh > line else 'Lost'; stat = 'total'
    elif m == '1st Half / Fulltime Result':
        x, y = c.split(' / '); ha, hh = H1[gid]
        def res(s, A, Hh):
            s = s.replace(' 1H', '').replace(' game', '')
            return ('Tie' if A == Hh else (CITY[a] if A > Hh else CITY[h])) == s
        out = 'Won' if res(x, ha, hh) and res(y, sa, sh) else 'Lost'; stat = 'htft'
    else: continue
    if not det: det = f'{h} {sh}, {a} {sa}'
    rows.append({**r, 'stat': stat, 'line': line, 'player': pl, 'outcome': out, 'detail': det, 'src_table': 'lines'})
seen = {(r['game'], 'Anytime Touchdown', r['contract']) for r in rows if r['market'] == 'Anytime Touchdown'}
A = pd.read_csv(W + 'pull1112/thu_out/atd_w10.csv', dtype=str, keep_default_na=False); A = A[A.game == 'WSH @ NYG']
for r in A.to_dict('records'):
    if r['game'] not in SC or (r['game'], 'Anytime Touchdown', r['player']) in seen or r['yes_price'] == '': continue
    a, h, sa, sh, gid = SC[r['game']]; p, played = player(r['player'], [a, h])
    if p is None and not played: out, det = 'Void', 'did not play'
    else: td = 0 if p is None else int(p.rushing_tds + p.receiving_tds); out = 'Won' if td >= 1 else 'Lost'; det = f'{td} TD'
    rows.append({**r, 'market': 'Anytime Touchdown', 'contract': r['player'], 'stat': 'td', 'line': 0.5, 'outcome': out, 'detail': det, 'src_table': 'atd'})
S = pd.DataFrame(rows)
S['price'] = pd.to_numeric(S['yes_price'], errors='coerce') / 100
S['y'] = (S['outcome'] == 'Won').astype(float); S.loc[S['outcome'] == 'Void', 'y'] = np.nan
S['actual'] = pd.to_numeric(S['detail'].str.extract(r'^([\d.]+) ')[0], errors='coerce')
S.to_csv(W + 'bt/w10_settled.csv', index=False)
print(len(S), S.outcome.value_counts().to_dict()); print(S.groupby('market').outcome.value_counts().unstack(fill_value=0))
