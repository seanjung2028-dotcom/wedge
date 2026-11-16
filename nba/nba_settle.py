"""Settle every NBA line Wedger posted (45-55c band) once its game is final, and score the screen and the model.

Posted lines: each game's last pre-tip version of the NBA table (Thu Oct 22 11:05 AM for Oct 22 games, Fri Oct 23 9:30 AM for
Oct 23 games, and so on). Box scores: ESPN (hoopR player boxes, plus nba_box_extra.json for games hoopR hasn't added yet).
Writes nba_results.csv (one row per settled line) and nba_record.json (summaries for the page).
"""
import csv, json, re, os, collections, sys
import numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/wedger/nba')
import nba_model as M

D = '/home/claude/wedger/nba/'
POSTED = [('nba_lines_1022.csv', 'Thu Oct 22 ~11:05 AM CT'), ('nba_lines_1023am.csv', 'Fri Oct 23 ~9:30 AM CT')]
POSTED += [(f, lab) for f, lab in json.load(open(D + 'nba_posted_extra.json'))] if os.path.exists(D + 'nba_posted_extra.json') else []
X = pd.read_pickle(D + 'nba_logs.pkl'); L, T = X['logs'], X['team']
FIX = {'GS': 'GSW', 'NY': 'NYK', 'SA': 'SAS', 'NO': 'NOP', 'UTAH': 'UTA', 'WSH': 'WAS', 'PHO': 'PHX'}
# extra box scores (ESPN summary API) for games hoopR hasn't published yet
box_rows, team_rows = [], []
if os.path.exists(D + 'nba_box_extra.json'):
    ex = json.load(open(D + 'nba_box_extra.json'))
    for g in ex['games']:
        if not g.get('final'): continue
        for side in ('away', 'home'):
            t, o = g[side], g['home' if side == 'away' else 'away']
            team_rows.append({'date': g['date'], 'team': t['abbr'], 'opp': o['abbr'], 'score': t['score'], 'opp_score': o['score']})
            for p in t['players']:
                box_rows.append({'date': g['date'], 'team': t['abbr'], 'name': p['name'], 'min': p['min'], 'pts': p['pts'], 'reb': p['reb'],
                                 'ast': p['ast'], '3pm': p['3pm'], 'dnp': p['dnp']})
TB = pd.concat([T[['date', 'team', 'opp', 'score', 'opp_score']], pd.DataFrame(team_rows, columns=['date', 'team', 'opp', 'score', 'opp_score'])], ignore_index=True)
TB = TB.drop_duplicates(['date', 'team'], keep='first')
PB = L[['date', 'team', 'name', 'min', 'pts', 'reb', 'ast', '3pm', 'dnp']].copy()
if box_rows: PB = pd.concat([PB, pd.DataFrame(box_rows)], ignore_index=True).drop_duplicates(['date', 'team', 'name'], keep='first')
PB['nn'] = PB['name'].map(M.norm_name); PB['pra'] = PB['pts'] + PB['reb'] + PB['ast']; PB = PB.rename(columns={'3pm': 'tpm'})
score = {(r.date, r.team): (r.score, r.opp_score) for r in TB.itertuples(index=False)}
pbox = {(r.date, r.nn): r for r in PB.itertuples(index=False)}
pbox_any = collections.defaultdict(list)
for r in PB.itertuples(index=False): pbox_any[(r.date, r.team)].append(r)
NAME = {'Atlanta': 'ATL', 'Boston': 'BOS', 'Brooklyn': 'BKN', 'Charlotte': 'CHA', 'Chicago': 'CHI', 'Cleveland': 'CLE', 'Dallas': 'DAL', 'Denver': 'DEN', 'Detroit': 'DET',
        'Golden State': 'GSW', 'Houston': 'HOU', 'Indiana': 'IND', 'LA Clippers': 'LAC', 'Los Angeles C': 'LAC', 'LA Lakers': 'LAL', 'Los Angeles L': 'LAL', 'Memphis': 'MEM',
        'Miami': 'MIA', 'Milwaukee': 'MIL', 'Minnesota': 'MIN', 'New Orleans': 'NOP', 'New York': 'NYK', 'Oklahoma City': 'OKC', 'Orlando': 'ORL', 'Philadelphia': 'PHI',
        'Phoenix': 'PHX', 'Portland': 'POR', 'Sacramento': 'SAC', 'San Antonio': 'SAS', 'Toronto': 'TOR', 'Utah': 'UTA', 'Washington': 'WAS'}
def team_of(txt, g):
    for k, v in NAME.items():
        if txt.startswith(k) and v in g: return v
    return None
ct_date = lambda u: pd.Timestamp(u).tz_convert('America/Chicago').strftime('%Y-%m-%d')

latest = {}   # (game, date, market, contract) -> (row, priced_at): the last posted version before tip
for f, lab in POSTED:
    if not os.path.exists(D + f): continue
    for r in csv.DictReader(open(D + f)):
        k = (r['game'], ct_date(r['kickoff_utc']), r['market'], r['contract'])
        latest[k] = (r, lab)
TIPPED = pd.Timestamp.now(tz='UTC')     # posted lines for games that have tipped off belong on the record
out = []
num = lambda x: None if x in ('', None) else float(x)
for (game, date, market, contract), (r, lab) in latest.items():
    away, home = game.split(' @ ')
    base = {'date': date, 'game': game, 'group': r['group'], 'market': market, 'contract': contract, 'player': r.get('player', ''), 'stat': r.get('stat', ''),
            'kickoff_utc': r['kickoff_utc'], 'yes_price': int(float(r['yes_price'])), 'hit_rate': r['hit_rate'], 'qualifies': r['qualifies'],
            'sit_hit': r.get('sit_hit', ''), 'sit_edge': r.get('sit_edge', ''), 'book_fair': r.get('book_fair', ''), 'priced_at': lab,
            'model_pick': 'Yes' if (num(r.get('sit_edge')) or -1) > 0 else ('No' if r.get('sit_edge') not in ('', None) else '')}
    if (date, home) not in score:
        if pd.Timestamp(r['kickoff_utc']) < TIPPED: out.append({**base, 'outcome': 'Pending', 'profit_c': '', 'result': 'awaiting final box score'})
        continue
    hs, as_ = score[(date, home)]
    if (date, away) in score: as_ = score[(date, away)][0]
    price = int(float(r['yes_price']))
    outcome = detail = None
    if r['group'] == 'Player props':
        stat = r['stat']; k = int(re.search(r': (\d+)\+', contract).group(1))
        p = pbox.get((date, M.norm_name(r['player'])))
        if p is None or p.dnp or pd.isna(p.min) or p.min <= 0:
            outcome, detail = 'Void', 'did not play'
        else:
            v = int(getattr(p, 'tpm' if stat == '3pm' else stat))
            outcome = 'Won' if v >= k else 'Lost'; detail = f"{v} {M.UNIT[stat]}"
    else:
        if market == 'Moneyline':
            t = team_of(contract, game); won = (hs > as_) if t == home else (as_ > hs)
        elif market == 'Spread':
            m_ = re.match(r'^(.*) wins by over ([\d.]+) points', contract); t = team_of(m_.group(1), game)
            marg = hs - as_ if t == home else as_ - hs; won = marg > float(m_.group(2))
        elif market == 'Total':
            won = hs + as_ > float(re.search(r'Over ([\d.]+)', contract).group(1))
        elif market == 'Team total':
            m_ = re.match(r'^(.*) over ([\d.]+) points', contract); t = team_of(m_.group(1), game)
            won = (hs if t == home else as_) > float(m_.group(2))
        else:
            continue
        outcome = 'Won' if won else 'Lost'; detail = f'{away} {int(as_)}, {home} {int(hs)}'
    profit = 0 if outcome == 'Void' else (100 - price if outcome == 'Won' else -price)
    out.append({**base, 'outcome': outcome, 'profit_c': profit, 'result': detail})
out.sort(key=lambda r: (r['date'], r['game'], r['group'] != 'Full game', r['market'], r['contract']))
for i, r in enumerate(out): r['id'] = f"nr{i}"
cols = ['id', 'date', 'game', 'kickoff_utc', 'group', 'market', 'contract', 'player', 'stat', 'yes_price', 'hit_rate', 'qualifies', 'sit_hit', 'sit_edge', 'book_fair',
        'model_pick', 'outcome', 'profit_c', 'result', 'priced_at']
with open(D + 'nba_results.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)

R = pd.DataFrame(out); S = R[~R['outcome'].isin(['Void', 'Pending'])].copy()
S['y'] = (S['outcome'] == 'Won').astype(int); S['p'] = S['yes_price'] / 100
S['w'] = pd.to_numeric(S['sit_hit'], errors='coerce') / 100
def rec(df):
    if not len(df): return {'n': 0}
    return {'n': int(len(df)), 'won': int(df['y'].sum()), 'win_pct': round(100 * df['y'].mean(), 1), 'avg_price': round(100 * df['p'].mean(), 1),
            'roi': round(100 * (df['y'] - df['p']).sum() / df['p'].sum(), 1), 'profit_c': int(round(100 * (df['y'] - df['p']).sum()))}
scr = S['qualifies'] == 'Yes'; mdl = S['model_pick'] == 'Yes'; props = S['group'] == 'Player props'
summ = {'settled': int(len(S)), 'void': int((R['outcome'] == 'Void').sum()), 'pending': int((R['outcome'] == 'Pending').sum()), 'nights': sorted(S['date'].unique().tolist()),
        'games': int(S['game'].nunique()) if len(S) else 0,
        'screen': rec(S[scr]), 'all': rec(S), 'model': rec(S[mdl]), 'screen_model': rec(S[scr & mdl]), 'screen_props': rec(S[scr & props]),
        'screen_team': rec(S[scr & ~props]), 'props_all': rec(S[props])}
P = S[props & S['w'].notna()]
if len(P):
    side_ok = ((P['w'] >= 0.5) == (P['y'] == 1))
    summ['model_side_pct'] = round(100 * side_ok.mean(), 1); summ['model_side_n'] = int(len(P))
    summ['brier'] = {'price': round(float(((P['p'] - P['y']) ** 2).mean()), 4), 'wedger': round(float(((P['w'] - P['y']) ** 2).mean()), 4),
                     'hit20': round(float(((pd.to_numeric(P['hit_rate'], errors='coerce') / 100 - P['y']) ** 2).mean()), 4)}
    cal = []
    for lo in range(30, 80, 5):
        b = P[(P['w'] * 100 >= lo) & (P['w'] * 100 < lo + 5)]
        if len(b): cal.append({'lo': lo, 'hi': lo + 5, 'n': int(len(b)), 'pred': round(100 * b['w'].mean(), 1), 'hit': round(100 * b['y'].mean(), 1)})
    summ['calibration'] = cal
by_m = []
for m_, g in S.groupby('market'):
    by_m.append({'market': m_, 'all': rec(g), 'screen': rec(g[g['qualifies'] == 'Yes']), 'model': rec(g[g['model_pick'] == 'Yes'])})
summ['by_market'] = sorted(by_m, key=lambda x: -x['all']['n'])
by_d = []
for d_, g in S.groupby('date'):
    by_d.append({'date': d_, 'all': rec(g), 'screen': rec(g[g['qualifies'] == 'Yes']), 'model': rec(g[g['model_pick'] == 'Yes'])})
summ['by_date'] = by_d
json.dump(summ, open(D + 'nba_record.json', 'w'), indent=1)
print(json.dumps({k: summ[k] for k in ('settled', 'void', 'pending', 'nights', 'games', 'screen', 'all', 'model', 'screen_model')}, indent=0))
print('side', summ.get('model_side_pct'), summ.get('model_side_n'), summ.get('brier'))
for b in summ['by_market']: print(b['market'], b['all'].get('n'), b['screen'].get('win_pct'), b['model'].get('win_pct'))
