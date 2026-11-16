import json, csv, re, collections

BASE = '/home/claude/wedger/rh/'
espn = json.load(open(BASE + 'espn_thru8.json'))
roster = json.load(open(BASE + 'roster_pos_w9.json'))
POS, TM = roster['pos'], roster['tm']
pids = json.load(open(BASE + 'player_ids_w9.json'))
import unicodedata
def _norm(n):
    n = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode().lower().replace('.', '').replace("'", '').replace('-', ' ')
    n = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', n)
    return re.sub(r'\s+', ' ', n).strip()
BOXID = {}
for _gid, _teams in espn['box'].items():
    for _t in _teams:
        for _cat, _d in _t['c'].items():
            for _pid, _nm, _st in _d['a']:
                BOXID[_norm(_nm)] = _pid
lines = list(csv.DictReader(open(BASE + 'inband_w9.csv')))
NFLV = {}  # nflverse 2026 roster fallback (latest week): norm name -> (team, position)
for _r in sorted(csv.DictReader(open(BASE + '../dl8/roster_weekly_2026.csv')), key=lambda r: int(r['week'] or 0)):
    NFLV[_norm(_r['full_name'])] = ({'LA': 'LAR', 'WAS': 'WSH'}.get(_r['team'], _r['team']), _r['position'])

EASY_N = 10  # "easy" = among the 10 defenses allowing the most PPR points per game to the position

# ---------------- defense: PPR points allowed per game ----------------
def grp(pos):
    if pos in ('RB', 'FB'): return 'RB'
    if pos in ('WR', 'TE'): return 'PC'
    return None

finals = [g for g in espn['games'] if g['st'] == 'STATUS_FINAL']
opp_of = {}
games_played = collections.Counter()
for g in finals:
    opp_of[(g['id'], g['h']['t'])] = g['a']['t']
    opp_of[(g['id'], g['a']['t'])] = g['h']['t']
    games_played[g['h']['t']] += 1
    games_played[g['a']['t']] += 1

allowed = collections.defaultdict(lambda: {'RB_pts': 0.0, 'RB_yds': 0.0, 'PC_pts': 0.0, 'PC_yds': 0.0})
unknown = collections.Counter()
for gid, teams in espn['box'].items():
    for t in teams:
        d = opp_of[(gid, t['t'])]
        for cat in ('rushing', 'receiving'):
            if cat not in t['c']:
                continue
            L = t['c'][cat]['l']
            for pid, nm, st in t['c'][cat]['a']:
                gname = grp(POS.get(pid))
                if not gname:
                    unknown[POS.get(pid)] += 1
                    continue
                val = lambda lbl: float(st[L.index(lbl)]) if lbl in L and st[L.index(lbl)] not in ('', '-') else 0.0
                if cat == 'rushing':
                    pts = 0.1 * val('YDS') + 6 * val('TD'); yds = val('YDS')
                else:
                    pts = val('REC') + 0.1 * val('YDS') + 6 * val('TD'); yds = val('YDS')
                allowed[d][gname + '_pts'] += pts
                allowed[d][gname + '_yds'] += yds

defense = []
for team, a in allowed.items():
    n = games_played[team]
    defense.append({'team': team, 'games': n,
                    'rb_ppr_pg': round(a['RB_pts'] / n, 1), 'rb_yds_pg': round(a['RB_yds'] / n, 1),
                    'pc_ppr_pg': round(a['PC_pts'] / n, 1), 'pc_yds_pg': round(a['PC_yds'] / n, 1)})
for key, rk in (('rb_ppr_pg', 'rb_rank'), ('pc_ppr_pg', 'pc_rank')):
    for i, r in enumerate(sorted(defense, key=lambda r: -r[key])):
        r[rk] = i + 1
defense.sort(key=lambda r: r['team'])
DEF = {r['team']: r for r in defense}

# ---------------- favorites (Robinhood moneyline, pregame) ----------------
# 1 PM+ games: prices at 11:15 AM CT Sun; HOU @ JAX was already live, so its pregame snapshot (Sat ~10:30 PM CT) is used.
# Robinhood moneyline Yes price (Tue Oct 20 ~8:20 PM CT refresh)
ML = collections.defaultdict(dict)
for _r in json.load(open(BASE + 'rows_w9.json')):
    if _r['market'] == 'Moneyline' and _r['yes_ask']:
        ML[_r['game']][{'WAS': 'WSH', 'LA': 'LAR'}.get(_r['contract'], _r['contract'])] = round(float(_r['yes_ask']) * 100)
ML = dict(ML)

def role(game, team):
    m = ML[game]
    other = [t for t in m if t != team][0]
    if m[team] > m[other]: return 'Favorite'
    if m[team] < m[other]: return 'Underdog'
    return "Pick'em"

PROP_MARKETS = {'Receiving Yards', 'Receptions', 'Rushing Yards', 'Rushing + Receiving Yards', 'Passing Yards',
                'Passing Touchdowns', 'Interceptions', 'Anytime Touchdown', '2+ Touchdowns', '3+ Touchdowns',
                'First Touchdown', 'Most Receiving Yards'}

CAT_NAME = {
    '1': '1 · RB, favored team',
    '2': '2 · Pass catcher, underdog',
    '3': '3 · RB, favored, soft RB defense',
    '4': '4 · Pass catcher, underdog, soft pass defense',
}

out = []
issues = []
for r in lines:
    if r['market'] not in PROP_MARKETS:
        continue
    m = re.match(r'^(.*?): Over', r['contract'])
    player = m.group(1) if m else r['contract']
    pid = pids.get(player) or BOXID.get(_norm(player))
    pos = POS.get(pid) if pid else None
    team = TM.get(pid) if pid else None
    if team is None and _norm(player) in NFLV:
        team, pos = NFLV[_norm(player)]
    away, home = r['game'].split(' @ ')
    if team not in (away, home):
        issues.append((player, team, r['game']))
        continue
    opp = home if team == away else away
    rl = role(r['game'], team)
    g = grp(pos)
    od = DEF[opp]
    cat, why = '', ''
    if g == 'RB' and rl == 'Favorite':
        cat = '3' if od['rb_rank'] <= EASY_N else '1'
    elif g == 'PC' and rl == 'Underdog':
        cat = '4' if od['pc_rank'] <= EASY_N else '2'
    else:
        if g is None:
            why = f'{pos} (not RB/WR/TE)'
        elif rl == "Pick'em":
            why = "Pick'em game"
        elif g == 'RB':
            why = 'RB on underdog'
        else:
            why = 'Pass catcher on favorite'
    status = ''
    out.append({
        'id': r['id'], 'category': CAT_NAME.get(cat, 'Not in a category'), 'cat': cat or '-', 'excluded_reason': why,
        'game': r['game'], 'kickoff': r['kickoff'], 'player': player, 'pos': pos, 'team': team,
        'team_role': rl, 'team_ml': ML[r['game']][team], 'opp': opp,
        'opp_rb_rank': od['rb_rank'], 'opp_rb_ppr_pg': od['rb_ppr_pg'],
        'opp_pc_rank': od['pc_rank'], 'opp_pc_ppr_pg': od['pc_ppr_pg'],
        'opp_rank_vs_pos': od['rb_rank'] if g == 'RB' else (od['pc_rank'] if g == 'PC' else ''),
        'market': r['market'], 'contract': r['contract'], 'yes_price': r['yes_price'], 'yes_bid': r['yes_bid'],
        'hit_rate': r['hit_rate'], 'hits': r['hits'], 'games': r['games'], 'qualifies': r['qualifies'],
        'season_results': r['season_results'], 'flags': '; '.join(x for x in (r['flags'], status) if x), 'kickoff_utc': r['kickoff_utc'],
        'source': r['source'], 'source_detail': r['source_detail'], 'book_lines': r['book_lines'], 'book_fair': r.get('book_fair', ''),
    })

with open(BASE + 'props_cat_w9.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
with open(BASE + 'defense_w9.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['team', 'games', 'rb_ppr_pg', 'rb_rank', 'rb_yds_pg', 'pc_ppr_pg', 'pc_rank', 'pc_yds_pg'])
    w.writeheader(); w.writerows(defense)

print('unknown positions in box (ignored):', unknown)
print('issues:', issues)
print('props in band:', len(out), ' qualifying:', sum(1 for o in out if o['qualifies'] == 'Yes'))
for q in ('Yes', None):
    sel = [o for o in out if q is None or o['qualifies'] == q]
    print('qualifying only' if q else 'all in-band', collections.Counter(o['category'] for o in sel))
print(collections.Counter(o['excluded_reason'] for o in out if o['qualifies'] == 'Yes' and o['cat'] == '-'))
print('positions', collections.Counter(o['pos'] for o in out))
