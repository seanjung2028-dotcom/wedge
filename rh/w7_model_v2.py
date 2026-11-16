"""Live Week 7 outlook for every player prop on the site (nfl_model.py applied with this week's context).

Writes sit_* columns on inband_w7.csv / props_cat_w7.csv / atd_w7.csv, sit_w7.csv (player game logs + splits) and
outlook_w7.csv (one row per line: cases, adjustments, script, probabilities).
"""
import sys, csv, json, re, math, os, collections, statistics
sys.argv.append('probe')
exec(open('/home/claude/wedger/rh/w7_splits.py').read())
sys.path.insert(0, B)
import nfl_model as M
import pandas as pd

CTX = json.load(open(B + 'nfl_ctx.json'))
DEFS, GAMES, PPG, LGX, DEFENDERS = CTX['def'], CTX['games'], CTX['ppg'], CTX['lg'], CTX['defenders']
sched = pd.read_csv(S2 + 'dl4/games.csv') if (S2 := '/home/claude/wedger/') else None
sched = sched[sched['game_type'] == 'REG']
MARG = {}
for r in sched.itertuples(index=False):
    if pd.isna(r.home_score): continue
    a, h = fx(r.away_team), fx(r.home_team)
    MARG[(r.season % 100, r.week, h)] = r.home_score - r.away_score; MARG[(r.season % 100, r.week, a)] = r.away_score - r.home_score
PPG_N = collections.Counter()
for (yy, wk, t) in MARG:
    if yy == 26 and wk <= 6: PPG_N[t] += 1
CITY_SHORT = {'LAR': 'Rams', 'LV': 'Raiders', 'NE': 'Patriots', 'CHI': 'Bears', 'PIT': 'Steelers', 'NO': 'Saints', 'SF': '49ers', 'ATL': 'Falcons',
              'CIN': 'Bengals', 'BAL': 'Ravens', 'TB': 'Buccaneers', 'CAR': 'Panthers', 'NYG': 'Giants', 'HOU': 'Texans', 'IND': 'Colts',
              'MIN': 'Vikings', 'MIA': 'Dolphins', 'NYJ': 'Jets', 'CLE': 'Browns', 'TEN': 'Titans', 'DEN': 'Broncos', 'ARI': 'Cardinals',
              'GB': 'Packers', 'DET': 'Lions', 'KC': 'Chiefs', 'SEA': 'Seahawks', 'DAL': 'Cowboys', 'PHI': 'Eagles'}

def cov_text(opp, grp):
    ds = DEFENDERS.get(opp, [])
    poss = {'WR': ('CB',), 'TE': ('S', 'LB'), 'RB': ('LB', 'S'), 'QB': ('CB', 'S')}.get(grp, ('CB',))
    act = [d for d in ds if d['pos'] in poss][:3]
    if not act: return ''
    sh = lambda n: (n.split(' ')[0][0] + '. ' + ' '.join(n.split(' ')[1:])) if ' ' in n else n
    bits = [f"{sh(d['name'])} {d['ypt']} yds/tgt{' (OUT)' if d['out'] else (' (' + d['practice'] + ')' if d['practice'] and d['practice'] != 'Full' else '')}" for d in act]
    return f"{opp} {'/'.join(poss)}s: " + ', '.join(bits) + f" — league {LGX['ypt_cov']}"

def script_text(game, team):
    g = GAMES[game]; sp = g['spread_home'] if team == g['home'] else -g['spread_home']
    fav = 'favored by ' + f"{abs(sp):g}" if sp < 0 else ('underdog by ' + f"{abs(sp):g}" if sp > 0 else 'pick’em')
    s = g['script'][team]
    return f"{CITY_SHORT.get(team, team)} {fav}: win by 8+ {round(100 * s['lead8'])}%, within 7 {round(100 * s['close'])}%, lose by 8+ {round(100 * s['trail8'])}%"

def p_market(r, kind):
    bf = r.get('book_fair')
    if bf not in ('', None): return float(bf) / 100, 'books'
    if r.get('source') and r['source'] != 'Robinhood':
        return float(r['yes_price']) / 100, 'books'
    ya = float(r['yes_price']) / 100 if r.get('yes_price') not in ('', None) else None
    yb = float(r['yes_bid']) / 100 if r.get('yes_bid') not in ('', None) else None
    if ya is not None and yb is not None: return (ya + yb) / 2, 'robinhood mid'
    return ya, 'robinhood ask'

OUT = {}
SITCOLS = ['sit_key', 'sit_stat', 'sit_line', 'sit_hit', 'sit_n', 'sit_proj', 'sit_lo', 'sit_hi', 'sit_model', 'sit_cases', 'sit_mkt', 'sit_edge', 'sit_v1', 'sit_pick', 'sit_pedge']
miss = collections.Counter()

def run(path, kind):
    rows = list(csv.DictReader(open(path)))
    cols = [c for c in rows[0].keys() if not c.startswith('sit_')] + SITCOLS
    done = 0
    for r in rows:
        for c in SITCOLS: r[c] = ''
        if kind == 'atd':
            market, player, line = 'Anytime Touchdown', r['player'], 0.5; key = f"{r['game']}|Anytime Touchdown|{r['player']}"
        else:
            market = r['market']
            if market not in STAT: continue
            m = re.match(r'^(.*?): Over ([\d.]+) ', r['contract'])
            player, line = (m.group(1), float(m.group(2))) if m else (r['contract'], 0.5)
            key = f"{r['game']}|{market}|{r['contract']}"
        g, team, opp = who(player, r['game'])
        if not g: miss[player] += 1; continue
        det = build(g, team, opp)
        if not det: continue
        stat = STAT[market]
        pos = det['pos']
        grp = 'RB' if pos in ('RB', 'FB') else ('TE' if pos == 'TE' else ('WR' if pos == 'WR' else 'QB'))
        game = GAMES.get(r['game'])
        if not game: continue
        D = DEFS.get(opp, {})
        ctx = {'def': D, 'lg': LGX, 'cov': D.get(f'cov_{grp}') if grp in ('WR', 'TE', 'RB') else D.get('cov_WR'),
               'cov_why': cov_text(opp, grp), 'script_why': script_text(r['game'], team),
               'implied': game['implied'][team], 'ppg': PPG.get(team), 'ppg_n': PPG_N.get(team, 6), 'wx': game['weather'], 'roof': game['roof']}
        L = det['log']
        margin = lambda i: MARG.get((L[i][0], L[i][1], team))
        pools = [s['idx'] for s in det['sets'] if s['pool']]
        pm, msrc = p_market(r, kind)
        E = M.evaluate(L, det['base'], stat, line, pos, pools, ctx, margin, game['script'][team], CITY_SHORT.get(team, team), 26, p_books=pm)
        if not E: continue
        C = E['C']
        price = float(r['yes_price']) if r.get('yes_price') not in ('', None) else None
        P = 100 * E['P']
        r.update({'sit_key': g, 'sit_stat': stat, 'sit_line': line, 'sit_hit': round(P, 1), 'sit_n': len(det['base']),
                  'sit_proj': round(E['m'], 2 if stat in ('td', 'passtd', 'int') else 1),
                  'sit_lo': round(C['T'][0]['m'] * E['prod'], 1) if C['T'][0]['m'] is not None else '',
                  'sit_hi': round(C['T'][2]['m'] * E['prod'], 1) if C['T'][2]['m'] is not None else '',
                  'sit_model': round(100 * E['P_model'], 1), 'sit_cases': round(100 * C['p'], 1),
                  'sit_mkt': round(100 * pm, 1) if pm is not None else '', 'sit_edge': round(P - price, 1) if price is not None else '',
                  'sit_v1': round(100 * E['P_v1'], 1)})
        # best side: Yes if Wedger beats the Yes ask by 3+, No if (100 - Wedger) beats the No ask (100 - Yes bid) by 3+
        nob = float(r['no_price']) if r.get('no_price') not in ('', None) else (100 - float(r['yes_bid']) if r.get('yes_bid') not in ('', None) else None)
        tradable = not (r.get('source') and r.get('source') != 'Robinhood')
        if price is not None and tradable:
            ey, en = P - price, ((100 - P) - nob) if nob is not None else None
            if ey >= 3: r.update({'sit_pick': 'Yes', 'sit_pedge': round(ey, 1)})
            elif en is not None and en >= 3: r.update({'sit_pick': 'No', 'sit_pedge': round(en, 1)})
        if key not in OUT:
            mkind = (f'rec-{grp}' if grp in ('WR', 'TE', 'RB') else 'pass') if stat in ('rec', 'recyd', 'rryd') else \
                   ('rush' if stat == 'rushyd' else (f'td-{grp}' if stat == 'td' else 'pass'))
            OUT[key] = {'stat': stat, 'line': line, 'pos': pos, 'team': team, 'opp': opp, 'game': r['game'], 'mkey': f'{opp}|{mkind}',
                        'cases': {'labels': C['labels'], 'T': [{'n': t['n'], 'h': t['h'], 'p': round(t['p'], 4), 'm': round(t['m'], 2) if t['m'] is not None else None} for t in C['T']],
                                  'W': [round(x, 4) for x in C['W']]},
                        'm0': round(C['m0'], 2), 'prod': round(E['prod'], 4), 'm': round(E['m'], 2), 'cv': round(E['cv'], 3),
                        'F': [{'k': f['k'], 'label': f['label'], 'f': round(f['f'], 4), 'why': f['why']} for f in E['F']],
                        'S': E['S']['rows'] if E['S'] else None,
                        'P_cases': round(C['p'], 4), 'P_model': round(E['P_model'], 4), 'P_raw': round(E['P_raw'], 4), 'P_ours': round(E['P_ours'], 4),
                        'P_mkt': round(pm, 4) if pm is not None else None, 'mkt_src': msrc, 'P': round(E['P'], 4), 'P_v1': round(E['P_v1'], 4),
                        'thin': E['n_hist'] < M.THIN_GAMES, 'n_hist': E['n_hist']}
        done += 1
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    return done, len(rows)

print('lines', run(B + 'inband_w7.csv', 'lines'))
print('props', run(B + 'props_cat_w7.csv', 'lines'))
print('atd', run(B + 'atd_w7.csv', 'atd'))
print('unmatched', miss.most_common(10))
with open(B + 'sit_w7.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['key', 'player', 'team', 'pos', 'detail'])
    for g, det in sorted(PLAYERS.items(), key=lambda x: (x[1] or {}).get('p') or ''):
        if det: w.writerow([g, det['p'], det['team'], det['pos'], json.dumps(det, separators=(',', ':'), ensure_ascii=False)])
with open(B + 'outlook_w7.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['key', 'detail'])
    for k, v in sorted(OUT.items()):
        w.writerow([k, json.dumps(v, separators=(',', ':'), ensure_ascii=False)])
print('players', sum(1 for d in PLAYERS.values() if d), 'sit bytes', os.path.getsize(B + 'sit_w7.csv'), 'outlooks', len(OUT), 'bytes', os.path.getsize(B + 'outlook_w7.csv'))
