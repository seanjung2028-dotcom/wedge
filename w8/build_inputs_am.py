"""Week 8 inputs for the line pipeline (Tue Oct 27 ~10 AM CT pull).

Robinhood has no Week 8 Sunday lines yet and the browser bridge is down, so:
- Game lines are priced from the sportsbook consensus: spreads from 8 books + Kalshi (VegasInsider), moneylines from
  DraftKings (nflverse/ESPN) and Kalshi's winner markets, totals from DraftKings with Covers' range as a check.
  Each Robinhood-style rung (team wins by over N.5, game total over N.5) is priced from a normal margin / total around the
  consensus (SD 12.6 margin, 13.1 total: 2021-25 results vs closing lines).
- Thursday's CAR @ GB player props: Kalshi's ladders (Robinhood lists the same contracts) for receptions, receiving,
  rushing, passing yards, passing TDs, rush+rec yards and TDs.
- Sunday/Monday player props: not posted by the books yet; the projections tab covers them.
Writes rh/rh_w8_gamelines.json, rh/kalshi_props_w8.json, rh/an_w8.json, rh/espn_thru7.json, rh/roster_pos_w8.json,
rh/player_ids_w8.json, rh/w8_build_inband_ko.py.
"""
import csv, json, math, statistics, collections, re, unicodedata
import numpy as np, pandas as pd
from scipy import stats
S = '/home/claude/wedger/'
W8 = S + 'w8/'; R = S + 'rh/'
FIX = {'LA': 'LAR', 'WAS': 'WSH', 'JAC': 'JAX'}
fx = lambda t: FIX.get(t, t)
CITY = {'ARI': 'Arizona', 'LAR': 'Los Angeles R', 'BAL': 'Baltimore', 'CLE': 'Cleveland', 'BUF': 'Buffalo', 'LV': 'Las Vegas',
        'CAR': 'Carolina', 'PHI': 'Philadelphia', 'CHI': 'Chicago', 'ATL': 'Atlanta', 'DAL': 'Dallas', 'GB': 'Green Bay',
        'HOU': 'Houston', 'JAX': 'Jacksonville', 'LAC': 'Los Angeles C', 'KC': 'Kansas City', 'NO': 'New Orleans',
        'NYG': 'New York G', 'NYJ': 'New York J', 'NE': 'New England', 'PIT': 'Pittsburgh', 'TB': 'Tampa Bay',
        'TEN': 'Tennessee', 'IND': 'Indianapolis', 'SF': 'San Francisco', 'WSH': 'Washington', 'MIN': 'Minnesota',
        'MIA': 'Miami', 'CIN': 'Cincinnati', 'DET': 'Detroit', 'DEN': 'Denver', 'SEA': 'Seattle'}
SLUG = lambda s: s.lower().replace(' ', '-')
SD_M, SD_T = 12.6, 13.1
imp = lambda o: 100 / (o + 100) if o > 0 else -o / (-o + 100)

g = pd.read_csv(S + 'dl8/games.csv'); w8 = g[(g['season'] == 2026) & (g['week'] == 8)]
vi = list(csv.DictReader(open(W8 + 'vi_spreads_w8.csv')))
cov = {(fx(r['away']), fx(r['home'])): r for r in csv.DictReader(open(W8 + 'covers_totals_w8.csv'))}
kw = {r['ticker']: r for r in csv.DictReader(open(W8 + 'kalshi_winners_w8.csv'))}
DATE = {'2026-10-29': 'oct-29', '2026-11-01': 'nov-01', '2026-11-02': 'nov-02'}
events, KO, consensus = [], {}, {}
for r in w8.itertuples(index=False):
    a, h = fx(r.away_team), fx(r.home_team); key = f'{a} @ {h}'
    # spread consensus: each book's line + no-vig odds -> expected home margin
    mus, books = [], []
    for v in vi:
        if fx(v['away']) != a or fx(v['home']) != h or v['book'] == 'open': continue
        hs, ho, ao = float(v['home_spread']), float(v['home_odds']), float(v['away_odds'])
        p = imp(ho) / (imp(ho) + imp(ao))                     # P(home covers hs)
        mus.append(-hs + SD_M * stats.norm.ppf(p)); books.append(f"{v['book']} {'+' if hs > 0 else ''}{hs:g} ({'+' if ho > 0 else ''}{ho:g})")
    mu_h = statistics.mean(mus)
    po = imp(r.over_odds) / (imp(r.over_odds) + imp(r.under_odds))
    mu_t = r.total_line + SD_T * stats.norm.ppf(po)
    c = cov.get((a, h))
    tot_note = f"DraftKings {r.total_line:g} (o{r.over_odds:+.0f}/u{r.under_odds:+.0f})" + (f"; Covers books {c['cur_lo']}–{c['cur_hi']}" if c else '')
    # moneyline: average of DraftKings no-vig, Kalshi mid and the spread consensus
    p_dk = imp(r.home_moneyline) / (imp(r.home_moneyline) + imp(r.away_moneyline))
    code = {'JAX': 'JAC', 'LAR': 'LAR', 'WSH': 'WAS'}
    kt = [t for t in kw if t.split('-')[1].endswith(f"{code.get(a, a)}{code.get(h, h)}") and t.endswith('-' + code.get(h, h))]
    p_kx = None
    if kt:
        k = kw[kt[0]]; p_kx = (float(k['yes_ask']) + float(k['yes_bid'])) / 2
    p_sp = 1 - stats.norm.cdf(0.5, mu_h, SD_M) + 0.5 * (stats.norm.cdf(0.5, mu_h, SD_M) - stats.norm.cdf(-0.5, mu_h, SD_M))
    ps = [x for x in (p_dk, p_kx, p_sp) if x is not None]; p_h = statistics.mean(ps)
    consensus[key] = {'home_margin': round(mu_h, 2), 'total': round(mu_t, 2), 'p_home': round(p_h, 4), 'p_dk': round(p_dk, 4),
                      'p_kalshi': round(p_kx, 4) if p_kx else None, 'p_spread': round(p_sp, 4), 'spread_books': books, 'total_note': tot_note}
    d = DATE[r.gameday]; base = f"{SLUG(CITY[a])}-vs-{SLUG(CITY[h])}-{d}-2026"
    name = f'{CITY[a]} vs {CITY[h]}'
    det_ml = f"DraftKings {r.away_moneyline:+.0f}/{r.home_moneyline:+.0f} (no-vig {100 * p_dk:.0f}% {h})" + (f"; Kalshi mid {100 * p_kx:.0f}% {h}" if p_kx else '') + f"; spread consensus {100 * p_sp:.0f}% {h}"
    def ct(nm, short, p, desc, det):
        return ['', nm, short, 'EVENT_CONTRACT_TRADABILITY_TRADABLE', f'{p:.4f}', None, None, None, 'consensus', desc, det]
    events.append([base, name, '', 'CONSENSUS', '', 'EVENT_TYPE_WINNER',
                   [ct(f'{CITY[a]} wins', a, 1 - p_h, f'{a} beats {h}', det_ml), ct(f'{CITY[h]} wins', h, p_h, f'{h} beats {a}', det_ml)]])
    sp = []
    det_sp = f"Consensus {h} by {mu_h:+.1f} from " + '; '.join(books)
    for t, mu in ((h, mu_h), (a, -mu_h)):
        for n in [x + 0.5 for x in range(1, 25)]:
            p = 1 - stats.norm.cdf(n, mu, SD_M)
            if 0.04 <= p <= 0.96:
                sp.append(ct(f'{CITY[t]} wins by over {n} points', f'{CITY[t]} wins by over {n} points', p, f'{t} wins by more than {n}', det_sp))
    events.append([f"{SLUG(CITY[a])}-vs-{SLUG(CITY[h])}-spreads-{d}-2026", f'{name} Spreads', '', 'CONSENSUS', '', 'EVENT_TYPE_SPREAD', sp])
    tt = []
    for n in [x + 0.5 for x in range(int(mu_t) - 16, int(mu_t) + 16)]:
        p = 1 - stats.norm.cdf(n, mu_t, SD_T)
        if 0.04 <= p <= 0.96:
            tt.append(ct(f'Over {n} points', f'Over {n} points', p, f'Game total over {n}', f"Consensus total {mu_t:.1f}: " + tot_note))
    events.append([f"{SLUG(CITY[a])}-vs-{SLUG(CITY[h])}-totals-{d}-2026", f'{name} Totals', '', 'CONSENSUS', '', 'EVENT_TYPE_TOTALS', tt])
    hh, mm = map(int, r.gametime.split(':'))
    ko = pd.Timestamp(f'{r.gameday} {r.gametime}', tz='America/New_York').tz_convert('UTC')
    ct_ = ko.tz_convert('America/Chicago')
    KO[key] = (ct_.strftime('%-I:%M %p CT ') + ct_.strftime('%a'), ko.strftime('%Y-%m-%dT%H:%M:%SZ'))
json.dump({'at': '2026-10-27T15:00:00Z', 'events': events, 'consensus': consensus}, open(R + 'rh_w8_consensus.json', 'w'))
# Robinhood's own Week 8 game lines (crawled Tue Oct 27 ~10:11 AM CT): spreads + totals ladders for all 14 games, moneylines,
# CAR @ GB 1st half / full time and overtime. Parent (moneyline) events came back by id; give them slug-style keys.
raw = json.load(open(R + 'rh_w8_robinhood_raw.json'))
DSL = {}
for e in raw['events']:
    m = re.match(r'^(.*)-(?:spreads|totals)-((?:oct|nov)-\d\d)-2026$', e[0])
    if m: DSL[e[1].replace(' Spreads', '').replace(' Totals', '')] = (m.group(1), m.group(2))
rh_events = []
for e in raw['events']:
    key = e[0]
    if re.fullmatch(r'[0-9a-f-]{36}', key):
        base, d = DSL[e[1]]
        key = f'{base}-{d}-2026-{e[2][:8]}'
    rh_events.append([key] + e[1:])
json.dump({'at': raw['at'], 'events': rh_events}, open(R + 'rh_w8_gamelines.json', 'w'))
print('robinhood events', len(rh_events))
with open(R + 'w8_build_inband_ko.py', 'w') as f:
    f.write('KO = ' + json.dumps(KO, indent=1).replace('[', '(').replace(']', ')') + '\n')
print('games', len(KO), 'contracts', sum(len(e[6]) for e in events))
for k, v in consensus.items(): print(k, v['home_margin'], v['total'], v['p_home'], v['p_dk'], v['p_kalshi'], v['p_spread'])

# ---------- Action Network (browser pull, Tue Oct 27 ~10:14 AM CT): book props + game lines ----------
an = json.load(open(R + 'an_w8_raw.json'))
json.dump(an, open(R + 'an_w8.json', 'w'))
print('AN rows', len(an['rows']), 'glines', len(an['glines']))

# ---------- ESPN-style results file from nflverse (Weeks 1-7) ----------
pbp = pd.read_csv(S + 'dl8/play_by_play_2026.csv.gz', usecols=['game_id', 'week', 'qtr', 'home_team', 'away_team', 'total_home_score', 'total_away_score', 'season_type'], low_memory=False)
pbp = pbp[pbp['season_type'] == 'REG']
gg = g[(g['season'] == 2026) & (g['week'] <= 7) & g['home_score'].notna()]
games = []
for r in gg.itertuples(index=False):
    p = pbp[pbp['game_id'] == r.game_id]
    hl, al = [], []
    prev_h = prev_a = 0
    for q in sorted(p['qtr'].dropna().unique()):
        e = p[p['qtr'] == q]
        hq, aq = int(e['total_home_score'].max()), int(e['total_away_score'].max())
        hl.append(hq - prev_h); al.append(aq - prev_a); prev_h, prev_a = hq, aq
    if sum(hl) != r.home_score or sum(al) != r.away_score:   # pbp total mismatch -> put the difference in Q4
        if hl: hl[min(3, len(hl) - 1)] += int(r.home_score) - sum(hl)
        if al: al[min(3, len(al) - 1)] += int(r.away_score) - sum(al)
    games.append({'id': r.game_id, 'w': int(r.week), 'st': 'STATUS_FINAL', 'h': {'t': fx(r.home_team), 's': int(r.home_score), 'ls': hl},
                  'a': {'t': fx(r.away_team), 's': int(r.away_score), 'ls': al}})
st = pd.read_csv(S + 'dl8/stats_player_week_2026.csv', low_memory=False)
st = st[(st['season_type'] == 'REG') & (st['week'] <= 7)]
rw = pd.read_csv(S + 'dl8/roster_weekly_2026.csv', low_memory=False)
espn_of = {r.gsis_id: str(int(r.espn_id)) for r in rw.itertuples(index=False) if not pd.isna(r.espn_id)}
gid_of = {(int(r.week), fx(r.home_team)): r.game_id for r in gg.itertuples(index=False)}
gid_of.update({(int(r.week), fx(r.away_team)): r.game_id for r in gg.itertuples(index=False)})
box = collections.defaultdict(lambda: collections.defaultdict(lambda: {'passing': {'l': ['C/ATT', 'YDS', 'AVG', 'TD', 'INT'], 'a': []},
                                                                       'rushing': {'l': ['CAR', 'YDS', 'AVG', 'TD', 'LONG'], 'a': []},
                                                                       'receiving': {'l': ['REC', 'YDS', 'AVG', 'TD', 'LONG', 'TGTS'], 'a': []}}))
for r in st.itertuples(index=False):
    t = fx(r.team); gid = gid_of.get((int(r.week), t))
    if not gid: continue
    pid = espn_of.get(r.player_id, r.player_id); nm = r.player_display_name
    c = box[gid][t]
    if (r.attempts or 0) > 0: c['passing']['a'].append([pid, nm, [f'{int(r.completions)}/{int(r.attempts)}', str(int(r.passing_yards)), '', str(int(r.passing_tds)), str(int(r.passing_interceptions))]])
    if (r.carries or 0) > 0: c['rushing']['a'].append([pid, nm, [str(int(r.carries)), str(int(r.rushing_yards)), '', str(int(r.rushing_tds)), '']])
    if (r.targets or 0) > 0 or (r.receptions or 0) > 0: c['receiving']['a'].append([pid, nm, [str(int(r.receptions)), str(int(r.receiving_yards)), '', str(int(r.receiving_tds)), '', str(int(r.targets))]])
BOX = {gid: [{'t': t, 'c': {k: v for k, v in c.items() if v['a']}} for t, c in teams.items()] for gid, teams in box.items()}
json.dump({'games': games, 'box': BOX}, open(R + 'espn_thru7.json', 'w'))
print('espn-like games', len(games), 'box', len(BOX))
# roster positions / teams keyed by ESPN id (latest week), and name -> id
lat = rw.sort_values('week').groupby('gsis_id').tail(1)
POS, TM, IDS = {}, {}, {}
for r in lat.itertuples(index=False):
    pid = str(int(r.espn_id)) if not pd.isna(r.espn_id) else r.gsis_id
    POS[pid] = r.position; TM[pid] = fx(r.team); IDS[r.full_name] = pid
for r in st.itertuples(index=False):
    pid = espn_of.get(r.player_id, r.player_id)
    POS.setdefault(pid, r.position); IDS.setdefault(r.player_display_name, pid)
json.dump({'pos': POS, 'tm': TM}, open(R + 'roster_pos_w8.json', 'w')); json.dump(IDS, open(R + 'player_ids_w8.json', 'w'))
print('roster', len(POS))
