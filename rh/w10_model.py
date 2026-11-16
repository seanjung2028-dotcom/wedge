"""Live Week 8 outlook for every player prop on the site (nfl_model.py applied with this week's context).

Writes sit_* columns on inband_w10.csv / props_cat_w10.csv / atd_w10.csv, sit_w10.csv (player game logs + splits) and
outlook_w10.csv (one row per line: cases, adjustments, script, probabilities).
"""
import sys, csv, json, re, math, os, collections, statistics
sys.argv.append('probe')
exec(open('/home/claude/wedger/rh/w10_splits.py').read())
sys.path.insert(0, B)
import nfl_model as M
import pandas as pd

CTX = json.load(open(B + 'nfl_ctx.json'))
DEFS, GAMES, PPG, LGX, DEFENDERS = CTX['def'], CTX['games'], CTX['ppg'], CTX['lg'], CTX['defenders']
sched = pd.read_csv(S2 + 'dl18/games.csv') if (S2 := '/home/claude/wedger/') else None
sched = sched[sched['game_type'] == 'REG']
MARG = {}
for r in sched.itertuples(index=False):
    if pd.isna(r.home_score): continue
    a, h = fx(r.away_team), fx(r.home_team)
    MARG[(r.season % 100, r.week, h)] = r.home_score - r.away_score; MARG[(r.season % 100, r.week, a)] = r.away_score - r.home_score
PPG_N = collections.Counter()
for (yy, wk, t) in MARG:
    if yy == 26 and wk <= 9: PPG_N[t] += 1
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

# ---- v4 (Tue Oct 27 evening): volume x efficiency anchor, opponent-adjusted defense, role-matchup prior ----
M.VE_W, M.DEF_MODE, M.RM_K = 0.5, 'adj', 0.5
DADJ = json.load(open(B + 'def_adj_w10.json'))
ROLES = json.load(open(B + 'roles_w10.json'))
import unicodedata as _ud
def _nn(s):
    s = _ud.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower(); s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', s); return re.sub(r'[^a-z]', '', s)
ROLE_N = {(_nn(k.split('|')[0]), k.split('|')[1]): v for k, v in ROLES.items()}
def role_of(player, team): return ROLE_N.get((_nn(player), team))
def role_payload(R, stat):
    if not R: return None
    c = R['cells'].get(stat, {})
    return {'arch': R['arch'], 'tier': R['tier'], 'm': R['m'], 'ctx': R['ctx'], 'rows': c.get('rows', []), 'used': c.get('used', []), 'rm': R['rm'].get(stat, 0.0)}
# ---- model v5 (Tue Nov 3): Wedger % = Robinhood price shifted by each market's over bias (Weeks 6-8, 1,000+ settled lines);
# our matchup read is kept for display only (it was slightly anti-predictive vs the price). Projections: RFF ridge (AQR, Kelly-Malamud-Zhou)
CAL5 = json.load(open('/home/claude/wedger/bt/cal_v51.json'))['cal_v5']
import sys as _sys; _sys.path.insert(0, '/home/claude/wedger/lens'); import v6 as V6   # v6 (Tue Nov 10): market mid + backtested matchup lens   # v5.1: passing yards / TDs / INTs split
G5 = {'rec': 'rec', 'recyd': 'recyd', 'rushyd': 'rush', 'rryd': 'rush', 'td': 'td', 'passyd': 'passyd', 'passtd': 'passtd', 'int': 'int'}
def v5(price_c, stat):
    pp = min(max(price_c / 100, 0.01), 0.99); z = math.log(pp / (1 - pp)) + CAL5[G5[stat]]
    return 100 / (1 + math.exp(-z))
RFF = json.load(open('/home/claude/wedger/rh/rff_w10.json'))
RFF_N = {(_nn(k.split('|')[0]), k.split('|')[1], k.split('|')[2]): v for k, v in RFF.items() if not k.startswith('_map')}
KBLEND = {'passyd': 1.0, 'rec': 0.5, 'recyd': 0.25, 'rushyd': 0.0}       # line + k x (RFF - line): best weights on Weeks 6-8 real lines
def rff_of(player, team, stat): return RFF_N.get((_nn(player), team, stat))
def rff_pover(player, team, stat, line, fallback):
    f = rff_of(player, team, stat); mp = RFF.get(f'_map|{stat}')
    if f is None or mp is None or line is None: return round(fallback, 1)
    return round(100 / (1 + math.exp(-(mp['a'] + mp['b'] * (f['rff'] - line) / mp['sc']))), 1)
def best_proj(player, team, stat, line, m_model):
    f = rff_of(player, team, stat)
    if f is None: return None, None
    k = KBLEND.get(stat)
    return f['rff'], (round(line + k * (f['rff'] - line), 1) if k is not None and line is not None else None)
OUT = {}
SITCOLS = ['sit_key', 'sit_stat', 'sit_line', 'sit_hit', 'sit_n', 'sit_proj', 'sit_lo', 'sit_hi', 'sit_model', 'sit_cases', 'sit_mkt', 'sit_edge', 'sit_v1', 'sit_pick', 'sit_pedge',
           'mom_type', 'mom_s', 'mom_l4', 'mom_snap', 'mom_vol', 'mom_p', 'mom_proj', 'role']
miss = collections.Counter()

VOLI = {'rec': 13, 'recyd': 13, 'rushyd': 14, 'rryd': None, 'passyd': 15, 'passtd': 15, 'int': 15, 'td': None}
def momentum(L, base, stat):
    """Last 4 games vs his season so far (2026, same team): role = snap share, volume = targets/carries/attempts,
    efficiency = yards per unit. Types follow the Oct 27 study (mom/): role moves persist, efficiency spikes don't."""
    cur = sorted([i for i in base if L[i][0] == 26], key=lambda i: L[i][1])
    if len(cur) < 5: return None
    v = lambda i: M.val(L, i, stat)
    s_all, s4 = statistics.mean(v(i) for i in cur), statistics.mean(v(i) for i in cur[-4:])
    sn = [L[i][3] for i in cur if L[i][3] is not None]; sn4 = [L[i][3] for i in cur[-4:] if L[i][3] is not None]
    dsn = (statistics.mean(sn4) - statistics.mean(sn)) if len(sn) >= 4 and len(sn4) >= 3 else 0
    col = VOLI.get(stat)
    vm = em = 0; vtxt = ''
    if col is not None:
        vol_all = statistics.mean((L[i][col] or 0) for i in cur); vol4 = statistics.mean((L[i][col] or 0) for i in cur[-4:])
        if vol_all > 0:
            vm = (vol4 - vol_all) / vol_all
            e_all = sum(v(i) for i in cur) / max(1, sum((L[i][col] or 0) for i in cur)); e4 = sum(v(i) for i in cur[-4:]) / max(1, sum((L[i][col] or 0) for i in cur[-4:]))
            em = (e4 - e_all) / max(abs(e_all), 0.1)
            vtxt = f"{vol_all:.1f}→{vol4:.1f} {M.VUNIT[stat]}/g"
    t = ('Role up' if dsn >= 10 else 'Role down' if dsn <= -10 else 'Volume up' if vm >= 0.15 else 'Volume down' if vm <= -0.15
         else 'Hot efficiency' if (em >= 0.15 and stat in ('recyd', 'rushyd', 'passyd', 'rryd')) else 'Cold efficiency' if (em <= -0.15 and stat in ('recyd', 'rushyd', 'passyd', 'rryd')) else 'Stable')
    dig = 2 if stat in ('td', 'passtd', 'int') else 1
    return {'mom_type': t, 'mom_s': round(s_all, dig), 'mom_l4': round(s4, dig), 'mom_snap': f"{statistics.mean(sn):.0f}%→{statistics.mean(sn4):.0f}%" if sn and sn4 else '',
            'mom_vol': vtxt}

def run(path, kind):
    rows = list(csv.DictReader(open(path)))
    cols = [c for c in rows[0].keys() if not c.startswith('sit_') and c not in SITCOLS] + SITCOLS
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
               'implied': game['implied'][team], 'ppg': PPG.get(team), 'ppg_n': PPG_N.get(team, 6), 'wx': game['weather'], 'roof': game['roof'],
               'dadj': DADJ.get(opp, {})}
        L = det['log']
        margin = lambda i: MARG.get((L[i][0], L[i][1], team))
        pools = [s['idx'] for s in det['sets'] if s['pool']]
        pm, msrc = p_market(r, kind)
        RL = role_of(player, team); rms = (RL or {}).get('rm', {}).get(stat, 0.0) if RL else 0.0
        cal_v = 'v4'
        M.CAL = dict(M.CAL_V3); M.MODE = 'season'; M.ROLE_ON = True
        E = M.evaluate(L, det['base'], stat, line, pos, pools, ctx, margin, game['script'][team], CITY_SHORT.get(team, team), 26, p_books=pm, w_mkt=M.W_MKT_V3, rm_shift=rms)
        M.MODE = 'l4'; M.ROLE_ON = False
        E4 = M.evaluate(L, det['base'], stat, line, pos, pools, ctx, margin, game['script'][team], CITY_SHORT.get(team, team), 26, p_books=pm, w_mkt=M.W_MKT_V3, rm_shift=rms)
        M.MODE = 'season'; M.ROLE_ON = True
        MOM = momentum(L, det['base'], stat)
        if not E: continue
        C = E['C']
        price = float(r['yes_price']) if r.get('yes_price') not in ('', None) else None
        P_read = 100 * E['P']                       # v4 number (85% market + 15% read, Week 6-7 calibration): shown, not used
        bidv = float(r['yes_bid']) if r.get('yes_bid') not in ('', None) else None
        midc = (price + bidv) / 2 if (price is not None and bidv) else (price - 1 if price is not None else None)
        LZ = V6.detail(player, team, opp, stat, line, midc) if midc is not None else None
        P = LZ['p'] if LZ is not None else P_read
        RFFP, BEST = best_proj(player, team, stat, line, E['m'])
        r.update({'sit_key': g, 'sit_stat': stat, 'sit_line': line, 'sit_hit': round(P, 1), 'sit_n': len(det['base']),
                  'sit_proj': BEST if BEST is not None else round(E['m'], 2 if stat in ('td', 'passtd', 'int') else 1),
                  'sit_lo': round(C['T'][0]['m'] * E['prod'], 1) if C['T'][0]['m'] is not None else '',
                  'sit_hi': round(C['T'][2]['m'] * E['prod'], 1) if C['T'][2]['m'] is not None else '',
                  'sit_model': round(100 * E['P_model'], 1), 'sit_cases': round(100 * C['p'], 1),
                  'sit_mkt': round(100 * pm, 1) if pm is not None else '', 'sit_edge': round(P - price, 1) if price is not None else '',
                  'sit_v1': round(P_read, 1)})
        if MOM: r.update(MOM)
        r['role'] = RL['arch'] if RL and RL['arch'] not in ('Unknown',) else ''
        if E4: r.update({'mom_p': round(100 * E4['P'], 1), 'mom_proj': round(E4['m'], 2 if stat in ('td', 'passtd', 'int') else 1)})
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
                        'P_mkt': round(pm, 4) if pm is not None else None, 'mkt_src': msrc, 'P': round(P / 100, 4), 'P_v1': round(E['P_v1'], 4), 'P_v4': round(P_read / 100, 4),
                        'P_price': round(price / 100, 4) if price is not None else None, 'shift5': CAL5[G5[stat]], 'rff': RFFP, 'proj_best': BEST,
                        'thin': E['n_hist'] < M.THIN_GAMES and M.CAL['thin'] != 0, 'n_hist': E['n_hist'], 'cal': 'v6', 'lens': ({'lo': round(LZ['lo'], 1), 'hi': round(LZ['hi'], 1), 'f': LZ['feats'], 'c': LZ['contrib'], 'mid': round(midc, 1)} if LZ and LZ['moved'] else None),
                        'mom': MOM or None, 'P_l4': round(E4['P'], 4) if E4 else None, 'm_l4': round(E4['m'], 2) if E4 else None,
                        'role': role_payload(RL, stat), 'rm': round(E.get('rm', 0.0), 4),
                        've': ({k: round(v, 3) for k, v in C['ve'].items()} if C.get('ve') else None), 'm0_cases': round(C['m0_cases'], 2) if C.get('m0_cases') is not None else None}
        done += 1
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction='ignore'); w.writeheader(); w.writerows(rows)
    return done, len(rows)

print('lines', run(B + 'inband_w10.csv', 'lines'))
print('props', run(B + 'props_cat_w10.csv', 'lines'))
print('atd', run(B + 'atd_w10.csv', 'atd'))
if os.path.exists(B + 'reads_cand_w10.csv'): print('reads', run(B + 'reads_cand_w10.csv', 'lines'))
print('unmatched', miss.most_common(10))
# ---------------- Week 8 projections: every starter's main props, for games whose prop lines aren't posted yet ----------------
# Estimated book line = the weights books used on the real Week 6-7 lines (season avg, last 4, multi-season avg; mom/real_analysis.json),
# rounded to a book-style half point. Wedger's read (no market blend: there is no price yet) gives the chance of clearing it.
import json as _json
from w10_build_inband_ko import KO as KO8
RAW = _json.load(open(S2 + 'mom/real_analysis.json'))['line_fit']
LW = {k: (v['w_S'], v['w_L4'], v['w_C']) for k, v in RAW.items() if v['n'] >= 40}
st26 = pd.read_csv(S2 + 'dl18/stats_player_week_2026.csv', low_memory=False)
st26 = st26[(st26['season_type'] == 'REG') & (st26['week'] <= 9)].copy(); st26['team'] = st26['team'].map(fx)
PMK = {'passyd': ('Passing Yards', 'Pass Yards'), 'rushyd': ('Rushing Yards', 'Rush Yards'), 'recyd': ('Receiving Yards', 'Receiving Yards'),
       'rec': ('Receptions', 'Receptions'), 'td': ('Anytime Touchdown', None)}
SWT = {0: 1.0, 1: 0.75, 2: 0.5, 3: 0.35}
PROJ = []
def est_line(L, base, stat):
    cur = sorted([i for i in base if L[i][0] == 26], key=lambda i: L[i][1])
    if stat == 'td': return 0.5
    allv = [(SWT.get(26 - L[i][0], 0.3), M.val(L, i, stat)) for i in base]
    C = sum(w * v for w, v in allv) / sum(w for w, _ in allv)
    if len(cur) >= 3:
        Sv = statistics.mean(M.val(L, i, stat) for i in cur); L4v = statistics.mean(M.val(L, i, stat) for i in cur[-4:])
        wS, w4, wC = LW.get(stat, (0.3, 0.2, 0.5)); x = wS * Sv + w4 * L4v + wC * C
    else:
        x = C
    return math.floor(x) + 0.5 if stat != 'rec' else max(0.5, math.floor(x) + 0.5)
for gk, game in GAMES.items():
    if gk not in KO8: continue   # played (Sat Nov 7 re-pull drops JAX @ BAL)
    for team in (game['away'], game['home']):
        opp = game['home'] if team == game['away'] else game['away']
        d = st26[st26['team'] == team]
        if not len(d): continue
        wks = sorted(d['week'].unique())[-4:]
        r4 = d[d['week'].isin(wks)].groupby(['player_id', 'player_display_name', 'position']).agg(tgt=('targets', 'sum'), car=('carries', 'sum'), att=('attempts', 'sum')).reset_index()
        picks = []
        qb = expected_qb(team)
        if isinstance(qb, str): picks.append((qb, 'QB'))
        picks += [(r.player_id, 'RB') for r in r4[r4['position'] == 'RB'].assign(u=lambda x: x['car'] + x['tgt']).sort_values('u', ascending=False).head(2).itertuples() if (r.car + r.tgt) / len(wks) >= 5]
        picks += [(r.player_id, 'WR') for r in r4[r4['position'] == 'WR'].sort_values('tgt', ascending=False).head(3).itertuples() if r.tgt / len(wks) >= 3]
        picks += [(r.player_id, 'TE') for r in r4[r4['position'] == 'TE'].sort_values('tgt', ascending=False).head(2).itertuples() if r.tgt / len(wks) >= 2.5]
        for g, posg in picks:
            if out_this_week(g): continue
            det = build(g, team, opp)
            if not det: continue
            pos = det['pos']; grp = 'RB' if pos in ('RB', 'FB') else ('TE' if pos == 'TE' else ('WR' if pos == 'WR' else 'QB'))
            D = DEFS.get(opp, {})
            ctx = {'def': D, 'lg': LGX, 'cov': D.get(f'cov_{grp}') if grp in ('WR', 'TE', 'RB') else D.get('cov_WR'),
                   'cov_why': cov_text(opp, grp), 'script_why': script_text(gk, team),
                   'implied': game['implied'][team], 'ppg': PPG.get(team), 'ppg_n': PPG_N.get(team, 6), 'wx': game['weather'], 'roof': game['roof'],
                   'dadj': DADJ.get(opp, {})}
            L = det['log']
            margin = lambda i, L=L: MARG.get((L[i][0], L[i][1], team))
            pools = [x['idx'] for x in det['sets'] if x['pool']]
            stats_for = {'QB': ['passyd', 'rushyd'], 'RB': ['rushyd', 'recyd', 'rec', 'td'], 'WR': ['recyd', 'rec', 'td'], 'TE': ['recyd', 'rec', 'td']}[grp]
            for stat in stats_for:
                base = det['base']
                cur = [i for i in base if L[i][0] == 26]
                if not cur: continue
                avg26 = statistics.mean(M.val(L, i, stat) for i in cur)
                if stat == 'rushyd' and grp == 'QB' and avg26 < 15: continue
                if stat in ('recyd',) and avg26 < 12: continue
                if stat == 'rec' and avg26 < 1.5: continue
                line = est_line(L, base, stat)
                M.MODE = 'season'; M.ROLE_ON = True
                E = M.evaluate(L, base, stat, line, pos, pools, ctx, margin, game['script'][team], CITY_SHORT.get(team, team), 26, p_books=None)
                M.MODE = 'l4'; M.ROLE_ON = False
                E4 = M.evaluate(L, base, stat, line, pos, pools, ctx, margin, game['script'][team], CITY_SHORT.get(team, team), 26, p_books=None)
                M.MODE = 'season'; M.ROLE_ON = True
                if not E: continue
                MOM = momentum(L, base, stat) or {}
                mk, suf = PMK[stat]
                player = disp.get(g, det.get('p', ''))
                contract = f'{player}: Over {line} {suf}' if suf else player
                key = f'{gk}|{mk}|{contract}'
                C_ = E['C']
                PROJ.append({'id': 'P' + str(len(PROJ) + 1), 'game': gk, 'kickoff': KO8[gk][0], 'kickoff_utc': KO8[gk][1], 'team': team, 'opp': opp,
                             'player': player, 'pos': pos, 'market': mk, 'contract': contract, 'est_line': line,
                             'role': ((role_of(player, team) or {}).get('arch', '') or '').replace('Unknown', ''),
                             'proj': (rff_of(player, team, stat) or {}).get('rff', round(E['m'], 2 if stat == 'td' else 1)) if stat != 'td' else round(E['m'], 2), 'proj_lo': round(C_['T'][0]['m'] * E['prod'], 1) if C_['T'][0]['m'] is not None else '',
                             'proj_hi': round(C_['T'][2]['m'] * E['prod'], 1) if C_['T'][2]['m'] is not None else '',
                             'p_over': rff_pover(player, team, stat, line, 100 * E['P']), 'mom_p': round(100 * E4['P'], 1) if E4 else '', 'mom_proj': round(E4['m'], 2 if stat == 'td' else 1) if E4 else '',
                             'season_avg': round(avg26, 2 if stat == 'td' else 1), 'games': len(cur), 'sit_key': g,
                             'flags': ('Injury report: ' + inj7[g]) if inj7.get(g) in ('Questionable', 'Doubtful') else '', **{k: MOM.get(k, '') for k in ('mom_type', 'mom_s', 'mom_l4', 'mom_snap', 'mom_vol')}})
                if key not in OUT:
                    OUT[key] = {'stat': stat, 'line': line, 'pos': pos, 'team': team, 'opp': opp, 'game': gk, 'mkey': f"{opp}|{'rec-' + grp if stat in ('rec', 'recyd') and grp in ('WR', 'TE', 'RB') else ('rush' if stat == 'rushyd' else ('td-' + grp if stat == 'td' else 'pass'))}",
                                'cases': {'labels': C_['labels'], 'T': [{'n': t['n'], 'h': t['h'], 'p': round(t['p'], 4), 'm': round(t['m'], 2) if t['m'] is not None else None} for t in C_['T']], 'W': [round(x, 4) for x in C_['W']]},
                                'm0': round(C_['m0'], 2), 'prod': round(E['prod'], 4), 'm': round(E['m'], 2), 'cv': round(E['cv'], 3),
                                'F': [{'k': f['k'], 'label': f['label'], 'f': round(f['f'], 4), 'why': f['why']} for f in E['F']], 'S': E['S']['rows'] if E['S'] else None,
                                'P_cases': round(C_['p'], 4), 'P_model': round(E['P_model'], 4), 'P_raw': round(E['P_raw'], 4), 'P_ours': round(E['P_ours'], 4),
                                'P_mkt': None, 'mkt_src': 'no line yet', 'P': round(E['P'], 4), 'P_v1': round(E['P_v1'], 4), 'thin': False, 'n_hist': E['n_hist'],
                                'cal': 'proj', 'rff': (rff_of(player, team, stat) or {}).get('rff'), 'mom': MOM or None, 'P_l4': round(E4['P'], 4) if E4 else None, 'm_l4': round(E4['m'], 2) if E4 else None,
                                'role': role_payload(role_of(player, team), stat), 'rm': round(M.RM_K * ((role_of(player, team) or {}).get('rm', {}).get(stat, 0.0)), 4),
                                've': ({k: round(v, 3) for k, v in C_['ve'].items()} if C_.get('ve') else None), 'm0_cases': round(C_['m0_cases'], 2) if C_.get('m0_cases') is not None else None}
with open(B + 'proj_w10.csv', 'w', newline='') as f:
    cols = ['id', 'game', 'kickoff', 'kickoff_utc', 'team', 'opp', 'player', 'pos', 'role', 'market', 'contract', 'est_line', 'proj', 'proj_lo', 'proj_hi', 'p_over',
            'mom_type', 'mom_s', 'mom_l4', 'mom_snap', 'mom_vol', 'mom_p', 'mom_proj', 'season_avg', 'games', 'sit_key', 'flags']
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(PROJ)
print('projections', len(PROJ), collections.Counter(p['market'] for p in PROJ))
with open(B + 'sit_w10.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['key', 'player', 'team', 'pos', 'detail'])
    for g, det in sorted(PLAYERS.items(), key=lambda x: (x[1] or {}).get('p') or ''):
        if det: w.writerow([g, det['p'], det['team'], det['pos'], json.dumps(det, separators=(',', ':'), ensure_ascii=False)])
with open(B + 'outlook_w10.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['key', 'detail'])
    for k, v in sorted(OUT.items()):
        w.writerow([k, json.dumps(v, separators=(',', ':'), ensure_ascii=False)])
print('players', sum(1 for d in PLAYERS.values() if d), 'sit bytes', os.path.getsize(B + 'sit_w10.csv'), 'outlooks', len(OUT), 'bytes', os.path.getsize(B + 'outlook_w10.csv'))
