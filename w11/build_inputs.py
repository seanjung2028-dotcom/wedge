"""Week 11 inputs for the line pipeline (Tue Nov 17 ~6:23 AM CT pull: game lines for all 13 games, props for Thursday IND @ HOU).

- Game lines: Kalshi's spread, total and winner ladders for all 14 games (Robinhood lists the same contracts), shaped as
  Robinhood game-line events (spreads, totals, winner). The books' consensus columns are filled from the same ladders.
- Player props: every Kalshi player-prop ladder open Tuesday night (receiving, rushing, passing yards, passing TDs,
  receptions, rush+rec yards, 1+/2+ TDs). More games and rungs open through the week.
- History: nflverse 2026 Weeks 1-10 (box scores, rosters).
Writes rh/rh_w11_gamelines.json, rh/rh_w11_consensus.json, rh/kalshi_props_w11.json, rh/an_w11.json, rh/espn_thru10.json,
rh/roster_pos_w11.json, rh/player_ids_w11.json, rh/w11_build_inband_ko.py."""
import json, re, collections
import numpy as np, pandas as pd
S = '/home/claude/wedger/'; R = S + 'rh/'; D = S + 'dl18/'
FIX = {'LA': 'LAR', 'WAS': 'WSH', 'JAC': 'JAX'}; fx = lambda t: FIX.get(t, t)
CITY = {'ARI': 'Arizona', 'LAR': 'Los Angeles R', 'BAL': 'Baltimore', 'CLE': 'Cleveland', 'BUF': 'Buffalo', 'LV': 'Las Vegas',
        'CAR': 'Carolina', 'PHI': 'Philadelphia', 'CHI': 'Chicago', 'ATL': 'Atlanta', 'DAL': 'Dallas', 'GB': 'Green Bay',
        'HOU': 'Houston', 'JAX': 'Jacksonville', 'LAC': 'Los Angeles C', 'KC': 'Kansas City', 'NO': 'New Orleans',
        'NYG': 'New York G', 'NYJ': 'New York J', 'NE': 'New England', 'PIT': 'Pittsburgh', 'TB': 'Tampa Bay',
        'TEN': 'Tennessee', 'IND': 'Indianapolis', 'SF': 'San Francisco', 'WSH': 'Washington', 'MIN': 'Minnesota',
        'MIA': 'Miami', 'CIN': 'Cincinnati', 'DET': 'Detroit', 'DEN': 'Denver', 'SEA': 'Seattle'}
KXC = {'JAX': 'JAC', 'WSH': 'WAS'}            # Kalshi's codes
SLUG = lambda s: s.lower().replace(' ', '-')
KG = json.load(open(S + 'pull1117/kalshi_games_w11.json')); KP = json.load(open(S + 'pull1117/kalshi_props_w11.json'))
AT = KG['at']
g = pd.read_csv(D + 'games.csv'); w11 = g[(g.season == 2026) & (g.week == 11)]
q = collections.defaultdict(list)
for ser, blob in KG['q'].items():
    for row in blob.split(';'):
        f = row.split('|'); q[(ser, f[0])].append(f)
events, KO, consensus = [], {}, {}
mid = lambda f: (int(f[2]) + int(f[3])) / 200 if int(f[3]) > 0 else int(f[2]) / 100
dd = lambda s: f"{float(s):.2f}" if s not in ('', None) else ''
for r in w11.itertuples(index=False):
    a, h = fx(r.away_team), fx(r.home_team); key = f'{a} @ {h}'
    code = KXC.get(a, a) + KXC.get(h, h)
    day = pd.Timestamp(r.gameday).strftime('%b-%d').lower()
    base = f"{SLUG(CITY[a])}-vs-{SLUG(CITY[h])}"; nm = f"{CITY[a]} vs {CITY[h]}"
    ko = pd.Timestamp(f'{r.gameday} {r.gametime}', tz='America/New_York').tz_convert('UTC'); ct_ = ko.tz_convert('America/Chicago')
    KO[key] = (ct_.strftime('%-I:%M %p CT ') + ct_.strftime('%a'), ko.strftime('%Y-%m-%dT%H:%M:%SZ'))
    pid = f'kx{code.lower()}'
    def cts(rows, desc):
        out = []
        for i, f in enumerate(rows):
            nm_ = f[6] if len(f) > 6 else f[1]
            out.append([f'{pid}{i:03d}', nm_, nm_, 'EVENT_CONTRACT_TRADABILITY_TRADABLE' if f[5] == '1' else 'EVENT_CONTRACT_TRADABILITY_UNTRADABLE',
                        dd(int(f[2]) / 100) if int(f[2]) > 0 else '', dd(int(f[3]) / 100) if int(f[3]) > 0 else '', dd(int(f[4]) / 100) if int(f[4]) > 0 else '', '', 'active', desc(nm_), ''])
        return out
    # winner
    win = q[('KXNFLGAME', code)]
    wc = []
    for f in win:
        t = fx(f[1]); wc.append([f'{pid}w{t}', f'{CITY[t]} wins', t, 'EVENT_CONTRACT_TRADABILITY_TRADABLE', dd(int(f[2]) / 100), dd(int(f[3]) / 100) if int(f[3]) else '', dd(int(f[4]) / 100), '', 'active', f'Will {CITY[t]} win the {nm} Pro Football game?', ''])
    events.append([f'{base}-{day}-2026-' + __import__('hashlib').md5(code.encode()).hexdigest()[:8], nm, pid, 'ARSENAL_EVENT_STATE_ACTIVE', None, 'EVENT_TYPE_WINNER', wc])
    sp = sorted(q[('KXNFLSPREAD', code)], key=lambda f: (f[6].split(' wins')[0], float(re.search(r'over ([\d.]+)', f[6]).group(1))))
    events.append([f'{base}-spreads-{day}-2026', nm + ' Spreads', pid + 's', 'ARSENAL_EVENT_STATE_ACTIVE', pid, 'EVENT_TYPE_SPREAD',
                   cts(sp, lambda c: f"Will {c.split(' wins')[0]} win by more than {re.search(r'over ([\d.]+)', c).group(1)} points in the {nm} Pro Football game?")])
    to = sorted(q[('KXNFLTOTAL', code)], key=lambda f: float(re.search(r'Over ([\d.]+)', f[6]).group(1)))
    events.append([f'{base}-totals-{day}-2026', nm + ' Totals', pid + 't', 'ARSENAL_EVENT_STATE_ACTIVE', pid, 'EVENT_TYPE_TOTALS',
                   cts(to, lambda c: f"Will the {nm} Pro Football game have {c.lower()} total points?")])
    # consensus from the ladders: margin where "home wins by over x" crosses 50%, total where "over x" crosses 50%
    def cross(pts):
        pts = sorted(pts)
        for (x0, p0), (x1, p1) in zip(pts, pts[1:]):
            if p0 >= 0.5 >= p1: return x0 + (p0 - 0.5) / (p0 - p1) * (x1 - x0) if p0 != p1 else x0
        return pts[0][0] if pts and pts[0][1] < 0.5 else (pts[-1][0] if pts else 0)
    hp = [(float(re.search(r'over ([\d.]+)', f[6]).group(1)), mid(f)) for f in sp if f[6].startswith(CITY[h])]
    ap = [(float(re.search(r'over ([\d.]+)', f[6]).group(1)), mid(f)) for f in sp if f[6].startswith(CITY[a])]
    # home margin: P(home margin > x) for x>0 from home ladder; for x<0 from away ladder
    pts = sorted([(x, p) for x, p in hp] + [(-x, 1 - p) for x, p in ap])
    hm = cross(pts) if pts else 0
    tot = cross([(float(re.search(r'Over ([\d.]+)', f[6]).group(1)), mid(f)) for f in to])
    wp = {fx(f[1]): mid(f) for f in win}; ph = wp.get(h, 0.5) / max(wp.get(h, 0.5) + wp.get(a, 0.5), 1e-9)
    consensus[key] = {'home_margin': round(hm, 1), 'total': round(tot, 1), 'p_home': round(ph, 3), 'p_dk': round(ph, 3), 'p_kalshi': round(ph, 3), 'p_spread': round(ph, 3),
                      'spread_books': [f'Kalshi ladder: {h} by {hm:+.1f}'], 'total_note': f'Kalshi ladder {tot:.1f}'}
json.dump({'at': AT, 'events': [], 'consensus': consensus}, open(R + 'rh_w11_consensus.json', 'w'))
json.dump({'at': AT, 'events': events}, open(R + 'rh_w11_gamelines.json', 'w'))
with open(R + 'w11_build_inband_ko.py', 'w') as f: f.write('KO = ' + json.dumps(KO, indent=1).replace('[', '(').replace(']', ')') + '\n')
print('games', len(KO), 'events', len(events)); [print(' ', k, v) for k, v in consensus.items()]
# player props, in the Kalshi series format the events step reads
SERIES = collections.defaultdict(list); names = KP['n']; DAYS = {}
for r in w11.itertuples(index=False):
    a, h = fx(r.away_team), fx(r.home_team); DAYS[KXC.get(a, a) + KXC.get(h, h)] = pd.Timestamp(r.gameday).strftime('%d')
for ser, blob in KP['q'].items():
    if not blob: continue
    for row in blob.split(';'):
        f = row.split('|'); code, tail = f[0], f[1]
        pc, k = tail.rsplit('-', 1); k = int(k)
        ev = f'{ser}-26NOV{DAYS.get(code, "15")}{code}'
        sub = f'{names.get(pc, pc)}: {k}+'
        SERIES[ser].append([ev, f'{ev}-{tail}', sub, k - 0.5, f'{int(f[2]) / 100:.4f}', f'{int(f[3]) / 100:.4f}', f'{int(f[4]) / 100:.4f}', '0.0000', '0.00', 'active'])
json.dump({'at': KP['at'], 'series': SERIES}, open(R + 'kalshi_props_w11.json', 'w'))
print('props', {k: len(v) for k, v in SERIES.items()})
json.dump({'rows': [], 'picks': {}, 'glines': [], 'at': AT}, open(R + 'an_w11.json', 'w'))   # no sportsbook prop rows this week
# ESPN-style results file from nflverse (Weeks 1-9)
pbp = pd.read_csv(D + 'play_by_play_2026.csv', usecols=['game_id', 'week', 'qtr', 'home_team', 'away_team', 'total_home_score', 'total_away_score', 'season_type'], low_memory=False)
pbp = pbp[pbp['season_type'] == 'REG']
gg = g[(g['season'] == 2026) & (g['week'] <= 10) & g['home_score'].notna()]
games = []
for r in gg.itertuples(index=False):
    p = pbp[pbp['game_id'] == r.game_id]; hl, al = [], []; prev_h = prev_a = 0
    for qq in sorted(p['qtr'].dropna().unique()):
        e = p[p['qtr'] == qq]; hq, aq = int(e['total_home_score'].max()), int(e['total_away_score'].max())
        hl.append(hq - prev_h); al.append(aq - prev_a); prev_h, prev_a = hq, aq
    if sum(hl) != r.home_score or sum(al) != r.away_score:
        if hl: hl[min(3, len(hl) - 1)] += int(r.home_score) - sum(hl)
        if al: al[min(3, len(al) - 1)] += int(r.away_score) - sum(al)
    games.append({'id': r.game_id, 'w': int(r.week), 'st': 'STATUS_FINAL', 'h': {'t': fx(r.home_team), 's': int(r.home_score), 'ls': hl}, 'a': {'t': fx(r.away_team), 's': int(r.away_score), 'ls': al}})
st = pd.read_csv(D + 'stats_player_week_2026.csv', low_memory=False); st = st[(st['season_type'] == 'REG') & (st['week'] <= 10)]
rw = pd.read_csv(D + 'roster_weekly_2026.csv', low_memory=False)
espn_of = {r.gsis_id: str(int(r.espn_id)) for r in rw.itertuples(index=False) if not pd.isna(r.espn_id)}
gid_of = {(int(r.week), fx(r.home_team)): r.game_id for r in gg.itertuples(index=False)}; gid_of.update({(int(r.week), fx(r.away_team)): r.game_id for r in gg.itertuples(index=False)})
box = collections.defaultdict(lambda: collections.defaultdict(lambda: {'passing': {'l': ['C/ATT', 'YDS', 'AVG', 'TD', 'INT'], 'a': []}, 'rushing': {'l': ['CAR', 'YDS', 'AVG', 'TD', 'LONG'], 'a': []},
                                                                       'receiving': {'l': ['REC', 'YDS', 'AVG', 'TD', 'LONG', 'TGTS'], 'a': []}}))
for r in st.itertuples(index=False):
    t = fx(r.team); gid = gid_of.get((int(r.week), t))
    if not gid: continue
    pid = espn_of.get(r.player_id, r.player_id); nm = r.player_display_name; c = box[gid][t]
    if (r.attempts or 0) > 0: c['passing']['a'].append([pid, nm, [f'{int(r.completions)}/{int(r.attempts)}', str(int(r.passing_yards)), '', str(int(r.passing_tds)), str(int(r.passing_interceptions))]])
    if (r.carries or 0) > 0: c['rushing']['a'].append([pid, nm, [str(int(r.carries)), str(int(r.rushing_yards)), '', str(int(r.rushing_tds)), '']])
    if (r.targets or 0) > 0 or (r.receptions or 0) > 0: c['receiving']['a'].append([pid, nm, [str(int(r.receptions)), str(int(r.receiving_yards)), '', str(int(r.receiving_tds)), '', str(int(r.targets))]])
BOX = {gid: [{'t': t, 'c': {k: v for k, v in c.items() if v['a']}} for t, c in teams.items()] for gid, teams in box.items()}
json.dump({'games': games, 'box': BOX}, open(R + 'espn_thru10.json', 'w')); print('espn-like games', len(games))
lat = rw.sort_values('week').groupby('gsis_id').tail(1); POS, TM, IDS = {}, {}, {}
for r in lat.itertuples(index=False):
    pid = str(int(r.espn_id)) if not pd.isna(r.espn_id) else r.gsis_id; POS[pid] = r.position; TM[pid] = fx(r.team); IDS[r.full_name] = pid
for r in st.itertuples(index=False):
    pid = espn_of.get(r.player_id, r.player_id); POS.setdefault(pid, r.position); IDS.setdefault(r.player_display_name, pid)
json.dump({'pos': POS, 'tm': TM}, open(R + 'roster_pos_w11.json', 'w')); json.dump(IDS, open(R + 'player_ids_w11.json', 'w')); print('roster', len(POS))
