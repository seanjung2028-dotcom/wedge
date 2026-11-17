"""V2 data: (1) injury file per player for the Research folder's Injury Report, (2) extra history splits
(head coach, game result, home/away) added to each player's history for the Game Script tab."""
import csv, json, re, sys, collections
import pandas as pd
csv.field_size_limit(10 ** 9)
B = '/home/claude/wedger/'
OUT = B + 'v2/data/'
import os; os.makedirs(OUT, exist_ok=True)

def norm(n):
    n = re.sub(r'\b(Jr|Sr|II|III|IV|V)\.?$', '', str(n).strip())
    return re.sub(r'[^a-z]', '', n.lower())

TM = {'LA': 'LAR', 'WAS': 'WSH'}
tm = lambda t: TM.get(t, t)

# ---------------- players we need ----------------
la = pd.read_csv(B + 'rh/lines_all_w11.csv', dtype=str).fillna('')
pj = pd.read_csv(B + 'rh/proj_w11.csv', dtype=str).fillna('')
SIT = {r['key']: r for r in csv.DictReader(open(B + 'rh/sit_w11.csv'))}
PROPS = {'Receiving Yards', 'Receptions', 'Rushing Yards', 'Anytime Touchdown', 'Passing Yards', '2+ Touchdowns', 'Passing Touchdowns',
         'Rushing + Receiving Yards', '3+ Touchdowns', 'Interceptions'}
names = {}
for r in la.itertuples():
    if r.market in PROPS:
        nm = r.contract.split(':')[0].strip()
        names.setdefault(norm(nm), {'p': nm, 'game': r.game})
for r in pj.itertuples():
    names.setdefault(norm(r.player), {'p': r.player, 'game': r.game}); names[norm(r.player)].update(team=r.team, pos=r.pos, key=r.sit_key)
for k, r in SIT.items():
    names.setdefault(norm(r['player']), {'p': r['player']}); names[norm(r['player'])].update(team=r['team'], pos=r['pos'], key=k)
print('players', len(names))

# ---------------- injuries ----------------
E = json.load(open(B + 'pull1107/espn_inj.json'))
ESPN = {}
for row in E['rows']:
    team, abbr, nm, pos, st, part, news, _, at, ret, eid = row
    ESPN[(norm(nm), tm(abbr))] = dict(st=st, part=part, news=news, at=at, ret=ret, pos=pos)
    ESPN.setdefault((norm(nm), None), dict(st=st, part=part, news=news, at=at, ret=ret, pos=pos, team=tm(abbr)))
sys.path.insert(0, B + 'rh')
NOTE = {}
try:
    src = open(B + 'rh/w11_injflags.py').read()
    m = re.search(r'NOTE = \{([\s\S]*?)\n\}', src)
    NOTE = eval('{' + m.group(1) + '}') if m else {}
except Exception as e:
    print('note parse failed', e)
INJ = {}
for yr in (2023, 2024, 2025):
    INJ[yr] = pd.read_csv(B + f'nflverse_dl3/injuries_{yr}.csv', dtype=str).fillna('')
INJ[2026] = pd.read_csv(B + 'dl18/injuries_w11.csv', dtype=str).fillna('')
for yr, d in INJ.items():
    d['nk'] = d.full_name.map(norm); d['week'] = d.week.astype(int); d['team'] = d.team.map(tm)
NOTINJ = re.compile(r'Not injury related|^$|Rest|Coach|decision|Suspen|Personal', re.I)
PRAC = {'Full Participation in Practice': 'Full', 'Limited Participation in Practice': 'Limited', 'Did Not Participate In Practice': 'Did not practice',
        'Out (Definitely Will Not Play)': 'Out'}

def tone_of(status, prac):
    s = (status or '').lower(); p = (prac or '').lower()
    if s in ('out', 'injured reserve', 'doubtful', 'physically unable to perform', 'suspension') or 'did not' in p and s not in ('', 'active', 'questionable'): return 'red'
    if s == 'questionable' or 'limited' in p or 'did not' in p: return 'yellow'
    return 'green'

def parts_of(s):
    s = str(s or '')
    if not s or NOTINJ.search(s): return []
    return [x.strip() for x in re.split(r'[/,;&]| and ', s) if x.strip()]

det_out = []
for nk, P in names.items():
    team = P.get('team'); key = P.get('key')
    es = ESPN.get((nk, team)) or ESPN.get((nk, None))
    if es and team and es.get('team') and es['team'] != team and (nk, team) not in ESPN: es = None
    def mine(d):
        x = d[d.gsis_id == key] if key else d.iloc[0:0]
        if x.empty: x = d[(d.nk == nk) & ((d.team == team) if team else True)]
        return x
    cur = mine(INJ[2026])
    trail = []
    for r in cur.sort_values('week').itertuples():
        part = r.report_primary_injury or r.practice_primary_injury
        if NOTINJ.search(part or '') and not r.report_status: continue
        trail.append({'wk': int(r.week), 'part': part, 'rep': r.report_status or '', 'prac': PRAC.get(r.practice_status, r.practice_status)})
    w9 = [t for t in trail if t['wk'] == 10]
    hist = []
    for yr in (2023, 2024, 2025):
        h = mine(INJ[yr])
        if h.empty: continue
        weeks = collections.Counter(); outw = set(); parts_set = collections.OrderedDict()
        for r in h.itertuples():
            part = r.report_primary_injury or r.practice_primary_injury
            if NOTINJ.search(part or ''): continue
            for pp in parts_of(part): weeks[pp] += 1; parts_set[pp] = 1
            if r.report_status in ('Out', 'Doubtful'): outw.add(r.week)
        if weeks: hist.append({'season': yr, 'parts': [[k, v] for k, v in weeks.most_common()], 'out': len(outw)})
    status = es['st'] if es else ''
    if status == 'Active': status = ''
    part = (es['part'] if es else '') or (w9[0]['part'] if w9 else '')
    prac = w9[0]['prac'] if w9 else ''
    rep = w9[0]['rep'] if w9 else ''
    if not status and rep: status = rep
    note = NOTE.get(nk, '')
    spots = []
    for pp in parts_of(part):
        spots.append({'part': pp, 'tone': tone_of(status, prac), 'when': 'This week', 'now': True})
    seen = {s['part'].lower() for s in spots}
    for t in reversed(trail):
        for pp in parts_of(t['part']):
            if pp.lower() in seen: continue
            seen.add(pp.lower()); spots.append({'part': pp, 'tone': 'green' if t['wk'] < 10 else tone_of(t['rep'], t['prac']), 'when': f"2026 Week {t['wk']}", 'now': False})
    for h in hist:
        for pp, n in h['parts']:
            if pp.lower() in seen: continue
            seen.add(pp.lower()); spots.append({'part': pp, 'tone': 'past', 'when': f"{h['season']} ({n} wk{'s' if n > 1 else ''} listed)", 'now': False})
    news = es['news'] if es else ''
    if not (status or trail or hist or news or note): continue
    det_out.append({'k': nk, 'p': P['p'], 'team': team or (es or {}).get('team', ''), 'pos': P.get('pos') or (es or {}).get('pos', ''),
                    'status': status or 'No designation', 'part': part, 'tone': tone_of(status, prac) if (status or prac) else 'green',
                    'prac': prac, 'rep': rep, 'news': news, 'news_at': es['at'] if es else '', 'ret': (es or {}).get('ret', '') if status in ('Out', 'Injured Reserve', 'Doubtful') else '',
                    'note': note, 'trail': trail, 'hist': hist, 'spots': spots})
with open(OUT + 'inj_w11.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['key', 'player', 'team', 'status', 'detail'])
    for d in det_out: w.writerow([d['k'], d['p'], d['team'], d['status'], json.dumps(d, ensure_ascii=False, separators=(',', ':'))])
print('injury files', len(det_out), 'with designation', sum(d['status'] != 'No designation' for d in det_out), 'bytes', os.path.getsize(OUT + 'inj_w11.csv'))

# ---------------- extra history splits ----------------
G = pd.read_csv(B + 'dl18/games.csv')
G = G[G.season >= 2023].copy()
G['home_team'] = G.home_team.map(tm); G['away_team'] = G.away_team.map(tm)
W9 = G[(G.season == 2026) & (G.week == 11)]
HC = {}
for r in W9.itertuples(): HC[r.home_team] = r.home_coach; HC[r.away_team] = r.away_coach
IDX = {}
for r in G.itertuples():
    for side, opp, me in (('home', r.away_team, r.home_team), ('away', r.home_team, r.away_team)):
        ms = (r.home_score - r.away_score) if side == 'home' else (r.away_score - r.home_score)
        IDX[(int(r.season) % 100, int(r.week), opp)] = (me, r.home_coach if side == 'home' else r.away_coach, ms if pd.notna(ms) else None, side)
SPREAD = {}
for r in W9.itertuples():
    sl = r.spread_line  # positive = home favored
    if pd.notna(sl): SPREAD[r.home_team] = sl; SPREAD[r.away_team] = -sl
added = collections.Counter()
rows_out = []
for k, r in SIT.items():
    d = json.loads(r['detail'])
    L = d['log']; team = tm(d.get('team', '')); base = set(d.get('base', range(len(L))))
    info = [IDX.get((row[0], row[1], tm(str(row[2]).lstrip('@')))) for row in L]
    sets = d.get('sets', [])
    hc = HC.get(team)
    ok = [i for i in range(len(L)) if i in base and info[i]]
    if hc:
        a = [i for i in ok if info[i][1] == hc and info[i][0] == team]; b = [i for i in ok if i not in a]
        if a:
            st = {'k': 'coach', 'label': f'Under {hc} (head coach)', 'now': f'This week: {hc} coaches {team}' + ('' if b else f'; every game here was under {hc}'), 'idx': a}
            if b: st['alt'] = {'label': 'Under other head coaches', 'idx': b}
            sets.append(st); added['coach'] += 1
    sp = SPREAD.get(team)
    if sp is not None:
        fav = f"{team} favored by {abs(sp):g}" if sp > 0 else (f"{team} a {abs(sp):g}-point underdog" if sp < 0 else 'a pick’em')
        win = [i for i in ok if info[i][2] is not None and info[i][2] >= 8]
        close = [i for i in ok if info[i][2] is not None and abs(info[i][2]) <= 7]
        lose = [i for i in ok if info[i][2] is not None and info[i][2] <= -8]
        script_now = f'This week: {fav} (books)'
        if win: sets.append({'k': 'sc-w', 'label': 'His team won by 8+', 'now': script_now + ('; this is the control script' if sp >= 3 else ''), 'idx': win}); added['sc'] += 1
        if close: sets.append({'k': 'sc-c', 'label': 'Within one score either way', 'now': 'The competitive script', 'idx': close})
        if lose: sets.append({'k': 'sc-l', 'label': 'His team lost by 8+', 'now': 'The chase script' + ('; the spread points here' if sp <= -3 else ''), 'idx': lose})
    w9 = W9[(W9.home_team == team) | (W9.away_team == team)]
    if len(w9) and w9.iloc[0].location != 'Neutral':
        home_now = w9.iloc[0].home_team == team
        h = [i for i in ok if info[i][3] == 'home']; a2 = [i for i in ok if info[i][3] == 'away']
        if h and a2:
            sets.append({'k': 'venue', 'label': 'At home' if home_now else 'On the road', 'now': f"This week: {'home' if home_now else 'away'}",
                         'idx': h if home_now else a2, 'alt': {'label': 'On the road' if home_now else 'At home', 'idx': a2 if home_now else h}}); added['venue'] += 1
    d['sets'] = sets
    if hc: d['hc'] = hc
    rows_out.append([k, r['player'], r['team'], r['pos'], json.dumps(d, ensure_ascii=False, separators=(',', ':'))])
with open(OUT + 'sit_w11_v2.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['key', 'player', 'team', 'pos', 'detail']); w.writerows(rows_out)
print('splits added', dict(added), 'of', len(SIT), 'bytes', os.path.getsize(OUT + 'sit_w11_v2.csv'))
