"""NBA lines for the Wedger NBA page: Robinhood (Kalshi order book) prices, hit rates, Wedger % and outlooks.

Outputs (CSV, one dataset each): nba_lines.csv, nba_sit.csv (player logs + splits), nba_outlook.csv, nba_ctx.csv.
"""
import json, re, csv, math, collections, sys, datetime as dt
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, '/home/claude/wedger/nba')
import nba_model as M

D = '/home/claude/wedger/nba/'
TODAY = '2026-11-19'
PRICED_AT = 'Thu Nov 19, 6:15 AM CT'
SLATE = ('2026-11-19', '2026-11-19')   # CT dates of the games on the board
X = pd.read_pickle(D + 'nba_logs.pkl'); L, T = X['logs'], X['team']
KX = json.load(open(D + 'kalshi_nba_1119.json'))['out']   # Thu Nov 19 browser pull (pull1119/kalshi_nba_raw.json)
SCH = pd.read_parquet(D + 'nba_schedule_2027.parquet')
FIX = {'GS': 'GSW', 'NY': 'NYK', 'SA': 'SAS', 'NO': 'NOP', 'UTAH': 'UTA', 'WSH': 'WAS', 'PHO': 'PHX'}
fx = lambda t: FIX.get(t, t)
NICK = {'ATL': 'Hawks', 'BOS': 'Celtics', 'BKN': 'Nets', 'CHA': 'Hornets', 'CHI': 'Bulls', 'CLE': 'Cavaliers', 'DAL': 'Mavericks', 'DEN': 'Nuggets',
        'DET': 'Pistons', 'GSW': 'Warriors', 'HOU': 'Rockets', 'IND': 'Pacers', 'LAC': 'Clippers', 'LAL': 'Lakers', 'MEM': 'Grizzlies', 'MIA': 'Heat',
        'MIL': 'Bucks', 'MIN': 'Timberwolves', 'NOP': 'Pelicans', 'NYK': 'Knicks', 'OKC': 'Thunder', 'ORL': 'Magic', 'PHI': '76ers', 'PHX': 'Suns',
        'POR': 'Trail Blazers', 'SAC': 'Kings', 'SAS': 'Spurs', 'TOR': 'Raptors', 'UTA': 'Jazz', 'WAS': 'Wizards'}
# injury report (ESPN, Thu Nov 19 6:15 AM CT) for tonight's teams: 'Out' = out tonight; 'GTD' = day-to-day (game-time decision).
INJ_RAW = json.load(open(D + 'pull1119/espn_inj_nba.json'))['inj']
def _resolve(team, nm):
    """'K. Porzingis' -> the full name of the player on that team in the box scores (latest team), else the initials as given."""
    m = re.match(r'^([A-Z])\. (.+)$', nm)
    if not m: return nm
    ini, last = m.group(1), M.norm_name(m.group(2))
    cand = L[(L['team'] == team)].drop_duplicates('name')
    for full in cand['name']:
        n = M.norm_name(full)
        if n.endswith(' ' + last) and n[0] == ini.lower(): return full
    cand = L.drop_duplicates('name')
    for full in cand['name']:
        n = M.norm_name(full)
        if n.endswith(' ' + last) and n[0] == ini.lower(): return full
    return nm
INJ = {t: {_resolve(t, nm): st for nm, st in d.items()} for t, d in INJ_RAW.items()}

# ---------------- schedule / games ----------------
SCH['away'] = SCH['away_abbreviation'].map(fx); SCH['home'] = SCH['home_abbreviation'].map(fx)
SCH['t'] = pd.to_datetime(SCH['date'], utc=True)
ct = lambda t: t.tz_convert('America/Chicago')
def kick_label(t):
    c = ct(t); return c.strftime('%-I:%M %p CT %a').replace(':00 ', ':00 ')
GAMES = {}
for r in SCH.itertuples(index=False):
    c = ct(r.t)
    if not (SLATE[0] <= c.strftime('%Y-%m-%d') <= SLATE[1]): continue
    key = f'{r.away} @ {r.home}'
    GAMES[(c.strftime('%y%b%d').upper(), r.away + r.home)] = {'key': key, 'away': r.away, 'home': r.home, 't': r.t, 'kick': kick_label(r.t),
                                                             'venue': r.venue_full_name, 'date': c.strftime('%Y-%m-%d')}
def game_of(ev):
    m = re.match(r'^[A-Z0-9]+-(\d\d)([A-Z]{3})(\d\d)([A-Z]{6})$', ev)
    if not m: return None
    yy, mon, dd, teams = m.groups()
    return GAMES.get((f'{yy}{mon}{dd}', teams))

mid = lambda r: (r[4] + r[5]) / 2 if (r[4] is not None and r[5] is not None and r[5] > 0) else (r[6] if r[6] else r[4])

# ---------------- market context from Kalshi ladders: spread, total, team totals ----------------
def ladder_median(pts):
    """pts: [(x, P(value > x))]; returns x where P = 0.5 (linear interpolation)."""
    pts = sorted(pts)
    for (x1, p1), (x2, p2) in zip(pts, pts[1:]):
        if (p1 - 0.5) * (p2 - 0.5) <= 0 and p1 != p2:
            return x1 + (0.5 - p1) * (x2 - x1) / (p2 - p1)
    return None
CTXG = collections.defaultdict(dict)
sp_pts = collections.defaultdict(list)
for r in KX['KXNBASPREAD']:
    g = game_of(r[1]); m_ = re.match(r'^(.*) wins by over ([\d.]+) points', r[2])
    if not g or not m_: continue
    p = mid(r)
    if p is None: continue
    team = r[0].rstrip('0123456789')
    team = {'GS': 'GSW', 'NY': 'NYK', 'SA': 'SAS', 'NO': 'NOP'}.get(team, team)
    sp_pts[(g['key'], team)].append((float(m_.group(2)), p / 100))
for r in KX['KXNBAGAME']:
    g = game_of(r[1]); p = mid(r)
    if g and p is not None: CTXG[g['key']].setdefault('ml', {})[r[0]] = p / 100
for key in {k for k, _ in sp_pts}:
    g = next(v for v in GAMES.values() if v['key'] == key)
    est = []
    for team, sign in ((g['home'], 1), (g['away'], -1)):
        pts = sp_pts.get((key, team), [])
        # include P(margin > 0) from the moneyline for a better anchor
        ml = CTXG[key].get('ml', {}).get(team)
        if ml is not None: pts = pts + [(0.0, ml)]
        med = ladder_median(pts) if len(pts) >= 2 else None
        if med is not None: est.append(sign * med)
    if est: CTXG[key]['margin_home'] = float(np.mean(est))
for key, c in CTXG.items():
    if 'margin_home' not in c and c.get('ml'):
        g = next(v for v in GAMES.values() if v['key'] == key)
        ph = c['ml'].get(g['home']); pa = c['ml'].get(g['away'])
        if ph is not None and pa is not None: c['margin_home'] = float(stats.norm.ppf(ph / (ph + pa)) * M.SD_MARGIN)
tot_pts = collections.defaultdict(list)
for r in KX['KXNBATOTAL']:
    g = game_of(r[1]); p = mid(r)
    if g and p is not None and r[3] is not None: tot_pts[g['key']].append((r[3], p / 100))
for k, pts in tot_pts.items():
    t_ = ladder_median(pts)
    if t_: CTXG[k]['total'] = t_
tt_pts = collections.defaultdict(list)
for r in KX['KXNBATEAMTOTAL']:
    g = game_of(r[1]); p = mid(r); m_ = re.match(r'^(.*) over ([\d.]+) points', r[2])
    if g and p is not None and m_:
        team = r[0].rstrip('0123456789'); team = {'GS': 'GSW', 'NY': 'NYK', 'SA': 'SAS', 'NO': 'NOP'}.get(team, team)
        tt_pts[(g['key'], team)].append((float(m_.group(2)), p / 100))
for (k, team), pts in tt_pts.items():
    t_ = ladder_median(pts)
    if t_: CTXG[k].setdefault('tt', {})[team] = t_
for k, c in CTXG.items():
    g = next(v for v in GAMES.values() if v['key'] == k)
    if 'total' in c and 'margin_home' in c:
        c.setdefault('tt', {})
        c['implied'] = {g['home']: round(c['tt'].get(g['home'], (c['total'] + c['margin_home']) / 2), 1),
                        g['away']: round(c['tt'].get(g['away'], (c['total'] - c['margin_home']) / 2), 1)}

# ---------------- team-level history for game lines ----------------
TG = T.sort_values('date')
team_games = {t: g for t, g in TG.groupby('team')}
def last_team(team, n=20):
    g = team_games.get(team)
    return g.tail(n) if g is not None else None

# ---------------- current tables for the model ----------------
DEF, LGD, RK = M.defense_table(L, TODAY, 27)
TT, LGT = M.team_table(T, TODAY, 27)
L['nn'] = L['name'].map(M.norm_name)
played = L[~L['dnp']]
latest_team = played.sort_values('date').groupby('pid').tail(1).set_index('pid')['team'].to_dict()
PID = {}
for r in played.sort_values('date').itertuples(index=False):
    PID[(r.nn, r.team)] = r.pid; PID.setdefault((r.nn, None), r.pid); PID[(r.nn, None)] = r.pid
by_pid = {pid: g.sort_values('date').reset_index(drop=True) for pid, g in L.groupby('pid')}
rest_tonight = {}
SCH['cdate'] = SCH['t'].map(lambda t: ct(t).strftime('%Y-%m-%d'))
for g in GAMES.values():
    for t in (g['away'], g['home']):
        prev = SCH[((SCH['away'] == t) | (SCH['home'] == t)) & (SCH['cdate'] < g['date'])]['cdate'].max()
        rest_tonight[(g['key'], t)] = (pd.Timestamp(g['date']) - pd.Timestamp(prev)).days - 1 if isinstance(prev, str) else None

# ---------------- sportsbook prices for the same players (Action Network, DraftKings / FanDuel / BetRivers / BetMGM ...) ----------------
from scipy.optimize import brentq
import os
# Action Network book lines are pulled per slate; none were pulled for Nov 19, so Wedge % falls back to the Robinhood mid.
AN_FILE = D + 'an_cur_1119.json'
AN = json.load(open(AN_FILE))['d'] if os.path.exists(AN_FILE) else {}
MK5 = {'pts': 'pts', 'reb': 'reb', 'ast': 'ast', '3pm': '3pm', 'pra': 'pra'}
BOOKS = {}
for ds, day in AN.items():
    date = f'{ds[:4]}-{ds[4:6]}-{ds[6:]}'
    for eid, name, team, m, mains in day['r']:
        BOOKS[(date, M.norm_name(name), m)] = mains
BOOK_NAME = {68: 'DraftKings', 69: 'FanDuel', 71: 'BetRivers', 75: 'BetMGM', 49: 'Caesars', 79: 'bet365'}
def book_fair(date, nn, stat, k, cv):
    mains = BOOKS.get((date, nn, stat))
    if not mains: return None, None
    ms = []
    for b, line, p in mains:
        f = lambda m: M.p_over(stat, m, cv, line) - p
        try: ms.append(brentq(f, 0.05, 4 * line + 10))
        except Exception: pass
    if not ms: return None, None
    mean = float(np.mean(ms))
    detail = ' · '.join(f"{BOOK_NAME.get(b, b)} {line} ({round(100 * p)}% over)" for b, line, p in mains)
    return M.p_over(stat, mean, cv, k - 0.5), detail

PROP = {'KXNBAPTS': ('Points', 'pts'), 'KXNBAREB': ('Rebounds', 'reb'), 'KXNBAAST': ('Assists', 'ast'), 'KXNBA3PT': ('Threes', '3pm'), 'KXNBAPRA': ('Pts + Reb + Ast', 'pra')}
rows, OUT, SIT = [], {}, {}
def flags_of(ya, yb, n, extra=()):
    f = []
    if yb is None or yb == 0: f.append('No bid')
    elif ya is not None and ya - yb > 5: f.append('Wide spread')
    if n < 10: f.append('Small sample')
    return ', '.join(list(f) + list(extra))

def nba_det(pid, team, opp, g, stat_for_def='pts'):
    """History tab detail for a player: log rows + splits that look like tonight."""
    H = by_pid[pid]; Hp = H[~H['dnp']].reset_index(drop=True)
    if len(Hp) < 8: return None
    log, base = [], []
    gno = collections.Counter()
    for i, r in Hp.iterrows():
        gno[r.yy] += 1
        log.append([int(r.yy), gno[r.yy], ('@' if not r.home else '') + r.opp, int(round(r['min'])), int(r.pts), int(r.reb), int(r.ast), int(r['3pm']), int(r.pra),
                    int(r.margin), None, None, 0, pd.Timestamp(r.date).strftime('%b %-d'), 1 if r.starter else 0, None if pd.isna(r.rest) else int(r.rest)])
        base.append(i)
    idx_team = [i for i in base if Hp.loc[i, 'team'] == team]
    last_start = bool(Hp.iloc[-1]['starter'])
    st_idx = [i for i in base if bool(Hp.loc[i, 'starter']) == last_start]
    rt = rest_tonight.get((g['key'], team))
    b2b = rt == 0
    rest_idx = [i for i in base if (Hp.loc[i, 'rest'] == 0) == b2b and not pd.isna(Hp.loc[i, 'rest'])]
    rest_alt = [i for i in base if (Hp.loc[i, 'rest'] == 0) != b2b and not pd.isna(Hp.loc[i, 'rest'])]
    home = team == g['home']
    loc_idx = [i for i in base if bool(Hp.loc[i, 'home']) == home]; loc_alt = [i for i in base if bool(Hp.loc[i, 'home']) != home]
    grp = Hp.iloc[-1]['grp']
    rk_now = RK.get((opp, grp, stat_for_def))
    near = {t for (t, g2, s), rk in RK.items() if g2 == grp and s == stat_for_def and rk_now and abs(rk - rk_now) <= 7}
    def_idx = [i for i in base if Hp.loc[i, 'opp'] in near]
    gname = {'G': 'guards', 'F': 'forwards', 'C': 'centers'}[grp]
    sets = [
        {'k': 'team', 'label': f'With the {NICK.get(team, team)}', 'now': f'His games for {team} since 2025-26', 'idx': idx_team, 'pool': len(idx_team) < len(base)},
        {'k': 'start', 'label': 'As a starter' if last_start else 'Off the bench', 'now': f"Tonight: {'started' if last_start else 'came off the bench'} in his last game", 'idx': st_idx, 'pool': True,
         'alt': {'label': 'Off the bench' if last_start else 'As a starter', 'idx': [i for i in base if i not in set(st_idx)]}},
        {'k': 'rest', 'label': 'On the second night of a back-to-back' if b2b else 'With at least a day of rest', 'now': f"Tonight: {'back-to-back' if b2b else (str(rt) + ' day' + ('s' if rt != 1 else '') + ' of rest') if rt is not None else 'first game'}",
         'idx': rest_idx, 'pool': True, 'alt': {'label': 'With rest' if b2b else 'On a back-to-back', 'idx': rest_alt}},
        {'k': 'loc', 'label': 'At home' if home else 'On the road', 'now': f"Tonight: {'home' if home else 'away'} vs {opp}", 'idx': loc_idx, 'pool': True,
         'alt': {'label': 'On the road' if home else 'At home', 'idx': loc_alt}},
        {'k': 'def', 'label': f'Vs defenses ranked {max(1, rk_now - 7)}–{min(30, rk_now + 7)} vs {gname}' if rk_now else 'Vs similar defenses',
         'now': f"Tonight: {opp} rank #{rk_now} in points allowed to {gname} (1 = most)", 'idx': def_idx, 'pool': True},
    ]
    mates = []
    for nm, stt in INJ.get(team, {}).items():
        if stt != 'Out': continue
        mp = PID.get((M.norm_name(nm), team)) or PID.get((M.norm_name(nm), None))
        if mp is None: continue
        mg = L[(L['pid'] == mp)]
        mg_played = set(mg[~mg['dnp']]['game_id'])
        same = [i for i in idx_team]
        with_ = [i for i in same if Hp.loc[i, 'game_id'] in mg_played]
        miss = [i for i in same if Hp.loc[i, 'game_id'] not in mg_played and (mg['game_id'] == Hp.loc[i, 'game_id']).any()]
        off = [i for i in same if not (mg['game_id'] == Hp.loc[i, 'game_id']).any() and Hp.loc[i, 'game_id'] not in mg_played]
        avg_min = mg[~mg['dnp']]['min'].mean() if len(mg_played) else 0
        if avg_min and avg_min >= 18 and len(with_) >= 3:
            mates.append({'name': nm, 'now': 'out', 'with': with_, 'missed': miss + off, 'off': []})
    return {'p': Hp.iloc[-1]['name'], 'team': team, 'pos': Hp.iloc[-1]['pos'], 'kind': 'nba', 'log': log, 'base': base, 'sets': sets, 'mates': mates,
            'statcols': {'pts': [4], 'reb': [5], 'ast': [6], '3pm': [7], 'pra': [8]}, 'tipcols': [['min', 3]], 'snames': {'26': '2025-26', '27': '2026-27'}, 'noSnaps': True, 'noWeeks': True}

# ---------------- props ----------------
for ser, (mname, stat) in PROP.items():
    for r in KX[ser]:
        g = game_of(r[1])
        if not g: continue
        m_ = re.match(r'^(.*): (\d+)\+ ', r[2])
        if not m_: continue
        player, k = m_.group(1), int(m_.group(2)); line = k - 0.5
        ya, yb, last, vol = r[4], r[5], r[6], r[7]
        if ya is None: continue
        nn = M.norm_name(player)
        tcode = r[0][:3]; tcode = {'GS': 'GSW'}.get(tcode, tcode)
        team = tcode if tcode in (g['away'], g['home']) else None
        pid = PID.get((nn, team)) or PID.get((nn, None))
        contract = f'{player}: {k}+ {mname.lower() if stat != "pra" else "points, rebounds and assists"}'
        row = {'id': f'{r[1]}-{r[0]}', 'game': g['key'], 'kickoff': g['kick'], 'kickoff_utc': g['t'].strftime('%Y-%m-%dT%H:%M:%SZ'), 'market': mname,
               'contract': contract, 'player': player, 'stat': stat, 'line': line, 'yes_price': ya, 'yes_bid': yb if yb else '', 'no_price': 100 - yb if yb else '',
               'volume': int(vol or 0), 'source': 'Robinhood', 'group': 'Player props'}
        if pid is None:
            row.update({'hits': '', 'games': 0, 'hit_rate': '', 'qualifies': 'No', 'sample': 'No NBA games found', 'season_results': '', 'flags': flags_of(ya, yb, 0, ['No history'])})
            rows.append(row); continue
        H = by_pid[pid]; Hp = H[~H['dnp']]
        team = team or latest_team.get(pid)
        opp = g['home'] if team == g['away'] else g['away']
        last20 = Hp.tail(20)
        vals = last20[stat].astype(int).tolist()
        hits = sum(1 for v in vals if v > line); n = len(vals)
        hr = round(100 * hits / n, 1) if n else ''
        q = 'Yes' if (n >= 10 and 45 <= ya <= 55 and hits / n > 0.5) else 'No'
        seasons = sorted(set(last20['yy']))
        row.update({'hits': hits, 'games': n, 'hit_rate': hr, 'qualifies': q,
                    'sample': f"Last {n} games ({' + '.join({26: '2025-26', 27: '2026-27'}[s] for s in seasons)})",
                    'season_results': ', '.join(str(v) for v in vals[-10:]), 'flags': flags_of(ya, yb, n), 'team': team, 'opp': opp, 'pos': Hp.iloc[-1]['pos']})
        # model
        c = CTXG.get(g['key'], {})
        sp_team = None
        if 'margin_home' in c: sp_team = -c['margin_home'] if team == g['home'] else c['margin_home']
        implied = c.get('implied', {}).get(team)
        out_names = [nm for nm, s in INJ.get(team, {}).items() if s == 'Out']
        mo = M.mates_out(L, pid, team, TODAY, 27, out_names, stat)
        grp = Hp.iloc[-1]['grp']
        ctx = {'yy': 27, 'team': team, 'opp': opp, 'grp': grp, 'def': DEF, 'lg': LGD, 'rank': RK, 'teams': TT, 'lgt': LGT, 'spread': sp_team,
               'implied': implied, 'rest': rest_tonight.get((g['key'], team)), 'mates_out': mo, 'team_name': NICK.get(team, team),
               'team_changed': (Hp['team'] != team).any()}
        x_ = Hp[stat].to_numpy(dtype=float); cvp = float(np.std(x_) / np.mean(x_)) if np.mean(x_) > 0 else M.CV_PRIOR[stat]
        cv_ = (len(x_) * cvp + 15 * M.CV_PRIOR[stat]) / (len(x_) + 15)
        bf, bdet = book_fair(g['date'], nn, stat, k, cv_)
        if bf is not None: row.update({'book_fair': round(100 * bf, 1), 'book_lines': bdet})
        pm = bf if bf is not None else ((ya + yb) / 200 if yb else ya / 100)
        E = M.evaluate(Hp, stat, line, ctx, p_mkt=pm)
        if E:
            C = E['C']; P = 100 * E['P']
            key = f"{g['key']}|{mname}|{contract}"
            row.update({'sit_key': str(pid), 'sit_stat': stat, 'sit_line': line, 'sit_hit': round(P, 1), 'sit_n': len(Hp), 'sit_proj': round(E['m'], 1),
                        'sit_model': round(100 * E['P_model'], 1), 'sit_cases': round(100 * C['p'], 1), 'sit_mkt': round(100 * pm, 1), 'sit_edge': round(P - ya, 1)})
            OUT[key] = {'stat': stat, 'line': line, 'pos': row['pos'], 'team': team, 'opp': opp, 'game': g['key'], 'mkey': f'{opp}|{grp}-{stat}',
                        'unit': M.UNIT[stat], 'word': M.WORD[stat], 'cond': f'{k}+ {M.WORD[stat]}',
                        'cases': {'labels': C['labels'], 'T': [{'n': t['n'], 'h': t['h'], 'p': round(t['p'], 4), 'm': round(t['m'], 2) if t['m'] is not None else None} for t in C['T']],
                                  'W': [round(x, 4) for x in C['W']], 'by': 'minutes'},
                        'm0': round(C['m0'], 2), 'prod': round(E['prod'], 4), 'm': round(E['m'], 2), 'cv': round(E['cv'], 3),
                        'F': [{'k': f['k'], 'label': f['label'], 'f': round(f['f'], 4), 'why': f['why']} for f in E['F']], 'S': E['S'],
                        'P_cases': round(E['P_cases'], 4), 'P_model': round(E['P_model'], 4), 'P_raw': round(E['P_raw'], 4), 'P_ours': round(E['P_ours'], 4),
                        'P_mkt': round(pm, 4), 'mkt_src': 'books' if bf is not None else ('Robinhood mid' if yb else 'Robinhood ask'), 'P': round(E['P'], 4)}
            if str(pid) not in SIT:
                SIT[str(pid)] = nba_det(pid, team, opp, g)
        rows.append(row)

# ---------------- game lines ----------------
def team_from_ticker(code):
    t = code.rstrip('0123456789'); return {'GS': 'GSW', 'NY': 'NYK', 'SA': 'SAS', 'NO': 'NOP'}.get(t, t)
for ser, mname in (('KXNBAGAME', 'Moneyline'), ('KXNBASPREAD', 'Spread'), ('KXNBATOTAL', 'Total'), ('KXNBATEAMTOTAL', 'Team total')):
    for r in KX[ser]:
        g = game_of(r[1])
        if not g: continue
        ya, yb, vol = r[4], r[5], r[7]
        if ya is None: continue
        title = r[2]
        row = {'id': f'{r[1]}-{r[0]}', 'game': g['key'], 'kickoff': g['kick'], 'kickoff_utc': g['t'].strftime('%Y-%m-%dT%H:%M:%SZ'), 'market': mname,
               'contract': title.replace('Full Game: ', '').replace(' points scored', ' points'), 'yes_price': ya, 'yes_bid': yb if yb else '',
               'no_price': 100 - yb if yb else '', 'volume': int(vol or 0), 'source': 'Robinhood', 'group': 'Full game'}
        if ser == 'KXNBATOTAL':
            line = r[3]
            vals = []
            for t in (g['away'], g['home']):
                tg = last_team(t)
                if tg is not None: vals += (tg['score'] + tg['opp_score']).astype(int).tolist()
            sample = f'Last 20 games of each team'
        else:
            team = team_from_ticker(r[0])
            tg = last_team(team)
            if tg is None: continue
            if ser == 'KXNBAGAME': line = 0.0; vals = (tg['score'] - tg['opp_score']).astype(int).tolist(); sample = f'{team} last {len(tg)} games'
            elif ser == 'KXNBASPREAD': line = r[3]; vals = (tg['score'] - tg['opp_score']).astype(int).tolist(); sample = f'{team} last {len(tg)} games (margin)'
            else: line = r[3]; vals = tg['score'].astype(int).tolist(); sample = f'{team} last {len(tg)} games (points)'
        hits = sum(1 for v in vals if v > line); n = len(vals)
        q = 'Yes' if (n >= 10 and 45 <= ya <= 55 and hits / n > 0.5) else 'No'
        row.update({'hits': hits, 'games': n, 'hit_rate': round(100 * hits / n, 1) if n else '', 'qualifies': q, 'sample': sample,
                    'season_results': ', '.join(str(v) for v in vals[-10:]), 'flags': flags_of(ya, yb, n)})
        rows.append(row)

# keep the 45–55¢ band for the table (plus anything Wedger-flagged later)
band = [r for r in rows if 45 <= r['yes_price'] <= 55]
cols = ['id', 'game', 'kickoff', 'kickoff_utc', 'group', 'market', 'contract', 'player', 'team', 'opp', 'pos', 'stat', 'line', 'yes_price', 'yes_bid', 'no_price', 'volume',
        'source', 'book_fair', 'book_lines', 'hits', 'games', 'hit_rate', 'qualifies', 'sample', 'season_results', 'flags',
        'sit_key', 'sit_stat', 'sit_line', 'sit_hit', 'sit_n', 'sit_proj', 'sit_model', 'sit_cases', 'sit_mkt', 'sit_edge']
with open(D + 'nba_lines.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore'); w.writeheader()
    for r in sorted(band, key=lambda r: (r['kickoff_utc'], r['game'], r['group'] != 'Full game', r['market'], r['contract'])): w.writerow({c: r.get(c, '') for c in cols})
keep = {f"{r['game']}|{r['market']}|{r['contract']}" for r in band}
with open(D + 'nba_outlook.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['key', 'detail'])
    for k, v in sorted(OUT.items()):
        if k in keep: w.writerow([k, json.dumps(v, separators=(',', ':'), ensure_ascii=False)])
need = {r['sit_key'] for r in band if r.get('sit_key')}
with open(D + 'nba_sit.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['key', 'player', 'detail'])
    for k, v in SIT.items():
        if v and k in need: w.writerow([k, v['p'], json.dumps(v, separators=(',', ':'), ensure_ascii=False, default=int)])

# ---------------- context: games + defenses ----------------
ctx_rows = []
for g in GAMES.values():
    c = CTXG.get(g['key'], {})
    extra = []
    ta, th = TT.get(g['away']), TT.get(g['home'])
    if ta and th: extra.append([f"Pace {(ta['pace'] + th['pace']) / 2:.1f}", f"Possessions per team: {g['away']} {ta['pace']:.1f}, {g['home']} {th['pace']:.1f} (league {LGT['pace']:.1f})"])
    ra, rh = rest_tonight.get((g['key'], g['away'])), rest_tonight.get((g['key'], g['home']))
    lab = lambda x: 'back-to-back' if x == 0 else (f'{x} day' + ('s' if x != 1 else '') + ' rest' if x is not None and x < 10 else 'season opener')
    extra.append([f"{g['away']} {lab(ra)}", f"{g['home']} {lab(rh)}"])
    outs = []
    for t in (g['away'], g['home']):
        o = [f"{[w for w in nm.split(' ') if w not in ('Jr.', 'Sr.', 'II', 'III', 'IV')][-1]} ({s})" for nm, s in INJ.get(t, {}).items()]
        if o: outs.append(f"{t}: " + ', '.join(o))
    if outs: extra.append(['Injury report', ' · '.join(outs)])
    det = {'away': g['away'], 'home': g['home'], 'venue': g['venue'], 'extra': extra}
    if 'margin_home' in c: det['spread_home'] = round(-c['margin_home'], 1)
    if 'total' in c: det['total'] = round(c['total'], 1)
    if 'implied' in c: det['implied'] = c['implied']
    ctx_rows.append(['game', g['key'], json.dumps(det, separators=(',', ':'), ensure_ascii=False)])
# defensive blocks per opponent x position group x stat
GN = {'G': 'guards', 'F': 'forwards', 'C': 'centers'}
NEED = {(v['opp'], v['mkey'].split('|')[1].split('-')[0]) for k, v in OUT.items() if k in keep}
for (opp, grp), dd in DEF.items():
    tm = TT.get(opp)
    if not tm or (opp, grp) not in NEED: continue
    rk_drtg = sorted(TT, key=lambda t: -(TT[t]['drtg'] or 0)).index(opp) + 1
    rk_pace = sorted(TT, key=lambda t: -TT[t]['pace']).index(opp) + 1
    for stat in M.STATS:
        lg = LGD[grp][stat]; v = dd[stat]; rk = RK.get((opp, grp, stat))
        mets = [{'label': f'{M.UNIT[stat]} allowed to {GN[grp]} / game', 'v': f'{v:.1f}', 'lg': f'{lg:.1f}', 'rk': rk, 'n': 30, 'tone': 'good' if rk <= 10 else ('bad' if rk >= 21 else '')},
                {'label': 'Points allowed per 100 possessions', 'v': f"{tm['drtg']:.1f}", 'lg': f"{LGT['drtg']:.1f}", 'rk': rk_drtg, 'n': 30, 'tone': 'good' if rk_drtg <= 10 else ('bad' if rk_drtg >= 21 else '')},
                {'label': 'Pace (possessions / game)', 'v': f"{tm['pace']:.1f}", 'lg': f"{LGT['pace']:.1f}", 'rk': rk_pace, 'n': 30, 'tone': 'good' if rk_pace <= 10 else ('bad' if rk_pace >= 21 else '')}]
        for s2 in M.STATS:
            if s2 != stat and s2 in ('pts', 'reb', 'ast', '3pm'):
                r2 = RK.get((opp, grp, s2)); mets.append({'label': f'{M.UNIT[s2]} allowed to {GN[grp]} / game', 'v': f'{dd[s2]:.1f}', 'lg': f'{LGD[grp][s2]:.1f}', 'rk': r2, 'n': 30, 'tone': ''})
        # recent opposing lines at this position vs this defense
        rec = L[(L['opp'] == opp) & (L['grp'] == grp) & (~L['dnp']) & (L['min'] >= 20)].sort_values('date')
        recent_games = rec['game_id'].drop_duplicates().tail(6)
        rr = rec[rec['game_id'].isin(recent_games)].sort_values(stat, ascending=False).head(7)
        prow = [[r_['name'], r_['team'], pd.Timestamp(r_.date).strftime('%b %-d'), int(round(r_['min'])), int(r_[stat])] for _, r_ in rr.iterrows()]
        det = {'title': f'{NICK.get(opp, opp)} defense', 'games': int(round(dd['n'])), 'metrics': mets,
               'note': 'Rank 1 = most allowed (or fastest pace) of 30. Green = good for the scorer, red = tough. 2026-27 games count double 2025-26.',
               'players': {'title': f'Best {M.UNIT[stat]} lines by {GN[grp]} vs {opp}, last {len(recent_games)} games', 'cols': ['Player', 'Team', 'Date', 'Min', M.UNIT[stat]],
                           'bar': 4, 'lg': round(float(rec[stat].mean()), 1) if len(rec) else None, 'rows': prow,
                           'note': f"Tick = average for {GN[grp]} playing 20+ minutes against {opp} ({round(float(rec[stat].mean()), 1) if len(rec) else '—'}). Green = above it."}}
        ctx_rows.append(['mb', f'{opp}|{grp}-{stat}', json.dumps(det, separators=(',', ':'), ensure_ascii=False)])
with open(D + 'nba_ctx.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['kind', 'key', 'detail']); w.writerows(ctx_rows)
q = [r for r in band if r['qualifies'] == 'Yes']
print('rows', len(rows), 'band', len(band), 'qualifying', len(q), 'props in band', sum(1 for r in band if r['group'] == 'Player props'),
      'outlooks', len([k for k in OUT if k in keep]), 'players', len(need))
print(collections.Counter((r['group'], r['qualifies']) for r in band))
for r in sorted(q, key=lambda r: -(r.get('sit_edge') or -99))[:12]: print(r['game'], r['contract'], r['yes_price'], r['hit_rate'], r.get('sit_hit'), r.get('sit_edge'))
print({k: v for k, v in list(CTXG.items())[:3]})
