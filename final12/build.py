"""Week 12 card. Sunday and Monday (from Fri Nov 27): rules v3 with the research method Independent Sports Research v1 (brain/rules.py,
brain/isr.py, brain/sig.py); Wedge % is the v6 lens alone (the earlier research projection is retired) and prices with every game
through Week 11 (v6.WEEK = 12; Tuesday's build left Week 11 out, a bug fixed Fri Nov 27). Wednesday-Friday games keep Tuesday's
card as posted (W12_PREV, W12_LOCK). Tuesday's note follows.
Week 12 card (Tue Nov 24, Kalshi ladders checked 2:39 PM CT), picked under rules v2 (brain/rules.py): ranked by the chance the
exact line hits, price second (75c cap, 70% bar), on Wedge % v6 with the 5% research projection (bt/w12_model/report.json: on Week 11's
board it called hits as well as Kalshi's own mid, and its card did best of the five numbers tested). Kalshi lists player ladders for the
Wednesday, Thursday and Friday games so far (GB @ LAR, CHI @ DET, PHI @ DAL, KC @ BUF, DEN @ PIT); Sunday and Monday open later.
Writes final12/final_w12.json, final12/final_w12.csv and the game lens blocks."""
import json, csv, math, os, re, sys, collections
import numpy as np, pandas as pd
W = '/home/claude/wedger/'
sys.path.insert(0, W + 'lens'); import core, v6, blocks
sys.path.insert(0, W + 'final12'); import brain_layer as BR
# pick rules: v1 (edge over the price, Weeks 7-11, the default here) or v2 (chance first, brain/rules.py, from Week 12).
# WEDGE_RULES=v2 WEDGE_OUT=<folder/> runs Week 12's board under v2 without touching the posted card (bt/w12_likely/build/).
RULES = os.environ.get('WEDGE_RULES', 'v3'); V3 = RULES == 'v3'; V2 = RULES in ('v2', 'v3')   # Week 12 Wed-Fri: v2; Sunday on: v3
OUTD = os.environ.get('WEDGE_OUT', W + 'final12/')
if V2: sys.path.insert(0, W + 'brain'); import rules as RV
BACKUP = getattr(BR, 'BACKUP', {})
v6.WEEK = 12   # price with every game before Week 12 (Tuesday's build defaulted to 11 and left Week 11 out)
if V3: v6.BLEND = None   # v3: the earlier method's research projection no longer enters Wedge %
T, ST = v6.tables(12)
KP = json.load(open(W + 'rh/kalshi_props_w12.json')); AT = KP['at']
import datetime as _d0, zoneinfo as _z0
CHK = _d0.datetime.fromisoformat(AT.replace('Z', '+00:00')).astimezone(_z0.ZoneInfo('America/Chicago'))
CHK_AT = CHK.strftime('%a %b %-d, %-I:%M %p CT')   # when the Kalshi ladders were checked
INJ_AT = os.environ.get('W12_INJ_AT', 'Tue Nov 24, 2:42 PM CT')   # when ESPN's injury report was read
CON = json.load(open(W + 'rh/rh_w12_consensus.json'))['consensus']
exec(open(W + 'rh/w12_build_inband_ko.py').read())  # KO
INJ = pd.read_csv(W + 'w12/espn_inj_1124.csv')
g = pd.read_csv(W + 'dl18/games.csv'); g = g[(g.season == 2026) & (g.week == 12)]
REP = json.load(open(W + 'bt/rep_v6.json'))
FX = {'LA': 'LAR', 'WAS': 'WSH', 'JAC': 'JAX'}; fx = lambda t: FX.get(t, t)
CITY = {'ARI': 'Arizona', 'LAR': 'Los Angeles', 'BAL': 'Baltimore', 'CLE': 'Cleveland', 'BUF': 'Buffalo', 'LV': 'Las Vegas', 'CAR': 'Carolina', 'PHI': 'Philadelphia',
        'CHI': 'Chicago', 'ATL': 'Atlanta', 'DAL': 'Dallas', 'GB': 'Green Bay', 'HOU': 'Houston', 'JAX': 'Jacksonville', 'LAC': 'Los Angeles', 'KC': 'Kansas City',
        'NO': 'New Orleans', 'NYG': 'New York', 'NYJ': 'New York', 'NE': 'New England', 'PIT': 'Pittsburgh', 'TB': 'Tampa Bay', 'TEN': 'Tennessee', 'IND': 'Indianapolis',
        'SF': 'San Francisco', 'WSH': 'Washington', 'MIN': 'Minnesota', 'MIA': 'Miami', 'CIN': 'Cincinnati', 'DET': 'Detroit', 'DEN': 'Denver', 'SEA': 'Seattle'}
VENUE = {r.home_team: ({'Reliant Stadium': 'NRG Stadium'}.get(r.stadium, r.stadium) if isinstance(r.stadium, str) else '') for r in g.itertuples(index=False)}
SER = {'KXNFLRECYDS': 'recyd', 'KXNFLREC': 'rec', 'KXNFLRSHYDS': 'rushyd', 'KXNFLRRYDS': 'rryd'}
WORD = {'rushyd': 'rushing yards', 'rec': 'receptions', 'recyd': 'receiving yards', 'rryd': 'rush + rec yards'}
SHORT = {'rushyd': 'rush yds', 'rec': 'rec', 'recyd': 'rec yds', 'rryd': 'rush+rec yds'}
COL = {'rushyd': 'rushing_yards', 'rec': 'receptions', 'recyd': 'receiving_yards'}
FEE = 2
ordn = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
def rank(col, team, most=True):
    s = T.D[col]; r = int(s.rank(ascending=not most, method='min')[team]); n = len(s)
    return f"{ordn(r)} most" if r <= n / 2 else f"{ordn(n + 1 - r)} fewest"
def rankw(col, team, hi='highest', lo='lowest'):
    s = T.D[col]; r = int(s.rank(ascending=False, method='min')[team]); n = len(s)
    return f"{ordn(r)} {hi}" if r <= n / 2 else f"{ordn(n + 1 - r)} {lo}"
pc = lambda x: f"{100 * x:.1f}%"
# --- who is out / limited
STATUS = {}
for r in INJ.itertuples(index=False):
    STATUS[(core.nn(r.full_name), fx(r.team))] = r.report_status
def status(name, team): return STATUS.get((core.nn(name), team), '')
# --- player game logs (2026, before Week 12)
def logs(pid, stat):
    s = ST[(ST.player_id == pid) & (ST.week < 12)].sort_values('week')
    if stat == 'rryd': v = (s.rushing_yards.fillna(0) + s.receiving_yards.fillna(0))
    else: v = s[COL[stat]].fillna(0)
    return list(zip(s.week.astype(int), v.astype(float), s.opponent_team))
# --- explain one lens step for one player, in words, with the numbers behind it
def explain(k, stat, name, team, opp, pid, feats):
    pos = T.pos.get(pid, ''); b = 'TE' if pos == 'TE' else ('RB' if pos in ('RB', 'FB') else 'WR'); D = T.D.loc[opp]
    if k == 'dvp':
        if stat in ('rushyd', 'rryd'): return f"{opp} allows {D.ypc:.2f} yards a carry ({rank('ypc', opp)}) and {D.rush_yds:.0f} rushing yards a game."
        col = f"{b}_{'yds' if stat == 'recyd' else 'rec'}"; unit = 'yards' if stat == 'recyd' else 'catches'
        return f"{opp} allows {D[col]:.1f} {b} receiving {unit} a game ({rank(col, opp)})."
    if k == 'overlap':
        if b == 'WR':
            m = T.P.get(pid, {}).get('mid', 0.25)
            return f"{int(round(100 * m))}% of his targets come in the middle; {opp} allows {pc(D.sh_WRm)} of targets to WRs in the middle ({rank('sh_WRm', opp)}) and {pc(D.sh_WRo)} outside ({rank('sh_WRo', opp)})."
        return f"{opp} sends {pc(D['sh_' + b])} of the targets it allows to {b}s ({rank('sh_' + b, opp)}; league {pc(T.lgsh[b])})."
    if k == 'look':
        bl = T.P.get(pid, {}).get('bl', 0.0)
        return f"{opp} blitzes on {pc(D.blitz)} of dropbacks ({rankw('blitz', opp)}; league {pc(T.lg_blitz)}); his target share runs {abs(100 * bl):.0f}% {'higher' if bl > 0 else 'lower'} against the blitz."
    if k == 'look_x_volume':
        bl = T.P.get(pid, {}).get('bl', 0.0)
        return (f"The two together: his target share runs {abs(100 * bl):.0f}% {'higher' if bl > 0 else 'lower'} against the blitz, and {opp} blitzes on {pc(D.blitz)} of dropbacks "
                f"while facing {D.pass_att:.1f} pass attempts a game ({rank('pass_att', opp)}). On held-out weeks this pairing beat both the market and the lens without it.")
    if k == 'volume':
        if stat in ('rushyd', 'rryd'): return f"{opp} faces {D.rush_att:.1f} rush attempts a game ({rank('rush_att', opp)})."
        return f"{opp} faces {D.pass_att:.1f} pass attempts a game ({rank('pass_att', opp)}). In the backtest, receiving overs against heavy-volume defenses cleared less often than priced."
    if k == 'dir':
        i = float(T.O.in_share.get(team, 0.6))
        return f"{team} runs inside {100 * i:.0f}% of the time; {opp} allows {D.ypc_in:.2f} inside ({rank('ypc_in', opp)}) and {D.ypc_out:.2f} outside ({rank('ypc_out', opp)})."
    if k == 'box': return f"{opp} averages {D.box:.2f} defenders in the box on runs ({rank('box', opp)})."
    if k == 'comp': return "Against the defenses most like this one, his production runs " + ('above' if feats.get('comp', 0) > 0 else 'below') + " his average."
    if k == 'consist': return 'His 2026 hit rate at this line, against the price.'
    return ''
# --- ladders
LAD = collections.defaultdict(list)
for ser, rows in KP['series'].items():
    stat = SER.get(ser)
    if not stat: continue
    for ev, tick, sub, strike, ya, yb, na, last, vol, st_ in rows:
        code = ev.split('-')[1][7:]; LAD[(code, sub.split(':')[0].strip(), stat)].append((int(strike + 0.5), round(100 * float(ya)), round(100 * float(yb)), round(100 * float(na)), tick))
# expected Kalshi ladders from the sportsbooks, for player markets Kalshi hasn't listed yet (final12/book_ladders.py)
import book_ladders as BL
# only where 3+ books post a two-sided line: the calibration was fit on multi-book players, and one book's line is too thin to price a ladder
EARLY = {k: [r_[:5] for r_ in v] for k, v in BL.LAD.items() if k[2] in WORD and k not in LAD and ((BL.META.get(k) or {}).get('det') or {}).get('n', 0) >= 3}
GAMES = {}
for r in g.itertuples(index=False):
    a, h = fx(r.away_team), fx(r.home_team); code = {'JAX': 'JAC', 'WSH': 'WAS'}.get(a, a) + {'JAX': 'JAC', 'WSH': 'WAS'}.get(h, h); GAMES[code] = (a, h)
res = collections.defaultdict(list)
for (code, name, stat), rungs, early in [(k_, v_, False) for k_, v_ in LAD.items()] + [(k_, v_, True) for k_, v_ in EARLY.items()]:
    if code not in GAMES: continue
    a, h = GAMES[code]; game = f'{a} @ {h}'
    pid = None
    for tm in (a, h):
        p_ = v6.pid_of(name, tm)
        if p_ is not None:
            s_ = ST[(ST.player_id == p_)].sort_values('week'); team = s_.team.iloc[-1] if len(s_) else tm
            if team in (a, h): pid = p_; break
    if pid is None: continue
    opp = h if team == a else a
    stt = status(name, team)
    if stt in ('Out', 'Doubtful'): continue
    rows = []
    rungs = sorted(set(rungs))
    two = [x for x in rungs if x[2] > 0 and x[1] > 0 and x[1] - x[2] <= 8 and x[0] >= (2 if stat == 'rec' else 10)]   # skip zero-catch / under-10-yard rungs
    em = CON[game]['home_margin'] if team == h else -CON[game]['home_margin']
    for k, ya, yb, na, tick in two:
        mid = (ya + yb) / 2; d = v6.detail(name, team, opp, stat, k - 0.5, mid, margin=em)
        if not d['moved']: continue
        for side in ('Yes', 'No'):
            ask = ya if side == 'Yes' else na
            if not (3 < ask < 97): continue
            if side == 'Yes': p, lo, hi, mk = d['p'], d['lo'], d['hi'], mid
            else: p, lo, hi, mk = 100 - d['p'], 100 - d['hi'], 100 - d['lo'], 100 - mid
            be = ask + FEE
            rows.append({'k': k, 'side': side, 'ask': ask, 'pays': round(100 / ask, 2), 'be': be, 'mkt': round(mk, 1), 'lo': round(lo, 1), 'mid': round(p, 1), 'hi': round(hi, 1),
                         'edge_lo': round(lo - be, 1), 'edge_mid': round(p - be, 1), 'tick': tick, 'd': d})
    if not rows: continue
    L = logs(pid, stat)
    for x in rows:
        x['chk'] = BR.run_checks(game, pid, team, stat, x['k'], x['side'], em)
        if V2:   # the quarterback row becomes information: a backup starter is a research factor, not an exclusion
            x['chk']['QB'] = {'pass': True, 'note': x['chk']['QB']['note'], 'info': True}
            x['call'], x['note'] = (RV.decide3 if V3 else RV.decide)(x, stat, BACKUP.get(team), stt)
        else: x['call'], x['note'] = BR.decide(x)
        hits = [v for _, v, _ in L if (v >= x['k'] if x['side'] == 'Yes' else v < x['k'])]; x['n_hit'], x['n'] = len(hits), len(L)
    # within a tier, an over that clears is preferred to an under that clears (card mix: about one under per three overs)
    fin = sorted([x for x in rows if x['call'] == 'Final line'], key=lambda x: (x['side'] != 'Yes', -x['edge_lo'], -x['edge_mid']))
    lea = sorted([x for x in rows if x['call'] == 'Conditional lean'], key=lambda x: (x['side'] != 'Yes', -x['edge_mid'], -x['edge_lo']))
    pick = (fin or lea or [None])[0]
    close = sorted(rows, key=lambda x: -x['edge_mid'])[0]
    if V2:   # chance first: his likeliest final, else his likeliest lean
        fin = sorted([x for x in rows if x['call'] == 'Final line'], key=RV.key, reverse=True)
        lea = sorted([x for x in rows if x['call'] == 'Conditional lean'], key=RV.key, reverse=True)
        pick = (fin or lea or [None])[0]; close = RV.closest(rows)
    res[game].append({'name': name, 'team': team, 'opp': opp, 'pid': pid, 'stat': stat, 'status': stt, 'rows': rows, 'pick': pick, 'close': close, 'logs': L,
                      'early': early, 'books': BL.META.get((code, name, stat), {}).get('det') if early else None})
# --- write-ups
def thr(x, stat, short=False): return (f"{x['k']}+ " if x['side'] == 'Yes' else f"under {x['k']} ") + (SHORT if short else WORD)[stat]
def research_text(d, x):
    """the research method's own number for the exact line, and the weight the 1,000-run average gives it"""
    r = d.get('research') or {}; k = x['k']; a, s_, c_, l3 = r.get('all', [0, 0]), r.get('script', [0, 0, 'close']), r.get('close', [0, 0]), r.get('last3', [0, 0])
    p2 = r.get('p2', 50.0) if x['side'] == 'Yes' else 100 - r.get('p2', 50.0)
    sc = {'control': 'games his team won by 8+', 'trail': 'games his team lost by 8+', 'close': 'one-score games'}[s_[2]]
    return (f"The research method's own number for {k}+: he got there in {a[0]} of {a[1]} games this season, {s_[0]} of {s_[1]} in {sc} (the script the spread points to)"
            + (f", {c_[0]} of {c_[1]} in one-score games" if s_[2] != 'close' else '') + f" and {l3[0]} of his last {l3[1]}. Pooled and shrunk to the price with 6 games of weight, "
            + f"that is {p2:.0f}% for this side. Averaged over 1,000 fits, it carries {100 * r.get('w', 0):.0f}% of the number and the lens the rest.")
def ledger(o, x):
    d = x['d']; sgn = 1 if x['side'] == 'Yes' else -1; out = []
    for k, c in sorted(d['contrib'].items(), key=lambda kv: -abs(kv[1])):
        if abs(c) < 0.15: continue
        out.append({'step': v6.LABEL.get(k, k), 'pts': round(sgn * c, 1), 'text': research_text(d, x) if k == 'research' else explain(k, o['stat'], o['name'], o['team'], o['opp'], o['pid'], d['feats'])})
    return out
def slope_shift(o, x):
    rr = sorted({(r['k'], r['mkt'] if r['side'] == 'Yes' else 100 - r['mkt']) for r in o['rows']})
    if len(rr) < 2: return 0.0
    ks = np.array([a for a, _ in rr]); ps = np.array([b for _, b in rr]); sl = abs(np.polyfit(ks, ps, 1)[0]) or 1.0
    dp = (x['mid'] - x['mkt']) if x['side'] == 'Yes' else (x['mkt'] - x['mid'])
    v = dp / sl; return round(v, 1) if o['stat'] == 'rec' else round(v)
CARDS, CSV, ECSV = [], [], []
# the last card posted (Thu Nov 19, Kalshi checked 6:04 AM CT; bt/w12_thu_board/): what changed since, per game
THU = {}   # no earlier Week 12 card yet
# the last card posted before this one (Sat Nov 21, Kalshi checked 10:56 PM CT; bt/w12_sat23_board/): the revisions table compares against it
PREV = os.environ.get('W12_PREV')   # an earlier Week 12 board folder (bt/w12_*_board) to compare against, once one is posted
FRI = {c['game']: c for c in json.load(open(W + PREV + '/final_w12.json'))['cards']} if PREV else {}
SATB = {'games': {}, 'plays': {}}
from datetime import datetime as _dt, timezone as _tz
from zoneinfo import ZoneInfo as _ZI
NOW = _dt.fromisoformat(KP['at'].replace('Z', '+00:00')) if isinstance(KP.get('at'), str) else _dt.now(_tz.utc)
def kicked(r):   # kickoff at or before this price check (plus 5 minutes): the card stays as published before kickoff
    ko = _dt.fromisoformat(f"{r.gameday}T{r.gametime}").replace(tzinfo=_ZI('America/New_York'))
    return ko.timestamp() <= NOW.timestamp() + 300
LOCKED = set()
LOCK = {x.strip() for x in os.environ.get('W12_LOCK', '').split(',') if x.strip()}   # games that keep the posted card even before kickoff
CODE = {f'{a_} @ {h_}': c_ for c_, (a_, h_) in GAMES.items()}
FAMN = {'KXNFLRECYDS': 'receiving yards', 'KXNFLREC': 'receptions', 'KXNFLRSHYDS': 'rushing yards', 'KXNFLRRYDS': 'rush + rec yards', 'KXNFLPASSYDS': 'passing yards', 'KXNFLPASSTDS': 'passing TDs', 'KXNFLTD': 'anytime TD'}
def coverage(game, nprops):
    code = CODE.get(game); cnt = collections.Counter()
    for ser, rows_ in KP['series'].items():
        for rw in rows_:
            if rw[0].split('-')[1][7:] == code: cnt[ser] += 1
    fam = [f"{FAMN[s_]} {n_}" for s_, n_ in cnt.most_common() if s_ in FAMN]
    return {'offered': fam, 'assessed': nprops,
            'gaps': 'Kalshi lists no carries, targets, pass attempts, completions, sacks, interceptions or longest-play markets for this game. Passing yards, passing TDs and anytime TDs stay at the market price: the lens did not beat it there in testing.'}
def revisions(game, plays, cand):
    out = []; now = {p['line']: p for p in plays}
    for p in FRI.get(game, {}).get('plays', []):
        if p['line'] in now:
            q = now[p['line']]; out.append({'line': p['line'], 'was': p['decision'], 'now': q['decision'], 'v': 'Keep', 'why': ('Same line; ' + ('call unchanged.' if q['decision'] == p['decision'] else f"now a {q['decision'].lower()}: {q['cond']}"))})
            continue
        same = [q for q in plays if q['player'] == p['player']]
        if same:
            out.append({'line': p['line'], 'was': p['decision'], 'now': same[0]['decision'], 'v': 'Replace', 'why': f"Now {same[0]['line']} at {same[0]['price']}¢: the price moved along his ladder."}); continue
        why = ''
        if not BR.QB.get(game, (True,))[0] and not V2: why = 'Game left off: a backup quarterback starts.'
        else:
            for o in cand:
                if o['name'] != p['player']: continue
                for y in o['rows']:
                    if f"{o['name']} {thr(y, o['stat'])} ({y['side']})" == p['line']:
                        why = y['note'] or (f"Price moved: needs {y['be']}%, ours {y['lo']:.0f}–{y['hi']:.0f}%." if y['edge_mid'] < 0.5 else 'Same read as a line already on the card.')
                        if V2: why = y['note'] or (RV.passed_move(y) if y['call'] == 'Pass' else 'Same player or game limit: another line took the slot.')
                if not why: why = 'That rung is no longer listed or tradable.'
            if not why: why = 'He is no longer on the board (ruled out or no ladder).'
        out.append({'line': p['line'], 'was': p['decision'], 'now': 'Pass', 'v': 'Pass', 'why': why})
    return out
# ---- v3: research picks in markets the model doesn't price (rushing and passing attempts, team totals, team sacks)
EXTRA = json.load(open(W + os.environ.get('W12_PULL', 'pull1124') + '/kalshi_extra_w12.json')) if os.path.exists(W + os.environ.get('W12_PULL', 'pull1124') + '/kalshi_extra_w12.json') else None
MKW = {'KXNFLPASSATT': 'passing attempts', 'KXNFLRSHATT': 'rushing attempts', 'KXNFLTEAMTOTAL': 'points', 'KXNFLTEAMSACK': 'sacks'}
def market_play(game, key, R, r):
    """one research pick from the market list: price and chance read from Kalshi's own book (chance = the side's mid; range = bid to ask)"""
    if EXTRA is None: return None
    _, ser, who, k, side = key; code = CODE.get(game)
    if ser in EXTRA['props']:
        pcs = {pc for pc, nm in EXTRA['n'].items() if nm == who}
        hit = [x for x in EXTRA['props'][ser] if x[0] == code and x[1] in pcs and x[2] == k]
        if not hit: return None
        _, pc, _, ya, yb, na = hit[0]; sub = pc
    else:
        hit = [x for x in EXTRA['games'].get(ser, []) if x[0] == code and x[1] == who and x[2] == k]
        if not hit: return None
        _, team, _, ya, yb, na, tr = hit[0]; sub = f'{team}{k}'
    ask = ya if side == 'Yes' else na; bid = yb if side == 'Yes' else 100 - ya
    if not ask or not bid: return None
    mid = round((ask + bid) / 2, 1); lo, hi = float(bid), float(ask); be = ask + FEE
    word = MKW[ser]; t_ = (f"{k}+ {word}" if side == 'Yes' else f"under {k} {word}")
    line = f"{who} {t_} ({side})"
    if lo >= RV.BAR and ask <= RV.CAP and R.get('decision') == 'Final line': call = 'Final line'
    elif mid >= RV.BAR and ask <= RV.CAP and R.get('decision') in ('Final line', 'Conditional lean'): call = 'Conditional lean'
    else: call = 'Pass'
    cond = (R.get('why', '') + ' ' + ('Holds as a final line up to 75¢ while the news holds.' if call == 'Final line' else
            (f"A lean: the market’s own range runs {lo:.0f}–{hi:.0f}%, and a final needs {RV.BAR}% at the low end." if call == 'Conditional lean' else
             f"Passed: the market’s range ({lo:.0f}–{hi:.0f}%) or the price ({ask}¢) misses the card’s bar."))).strip()
    dcode = _dt.strptime(r.gameday, '%Y-%m-%d').strftime('%y%b%d').upper()
    x_ = {'ask': ask, 'mid': mid}
    return {'decision': call, 'player': who, 'line': line, 'thr': t_, 'side': side, 'price': ask, 'payout': round(100 / ask, 2), 'be': be, 'mkt': mid,
            'est': [round(lo), round(hi)], 'lo': lo, 'mid': mid, 'hi': hi, 'edge_lo': round(lo - be, 1), 'edge_mid': round(mid - be, 1),
            'platform': 'Robinhood (Kalshi contract)', 'checked': AT, 'ticker': f"{ser}-{dcode}{code}-{sub}" + (f"-{k}" if ser in EXTRA['props'] else ''),
            'why': R['notes'][0] if R.get('notes') else '', 'support': '', 'sample': '', 'counter': next((n for n in R.get('notes', []) if n.startswith('Against it')), 'No single factor stands out against it.'),
            'loses': 'The game script turns against the read.', 'cond': cond, 'vs': '', 'pts': 0, 'shift': 0, 'lens': [], 'tier': BR.tier(mid),
            'chain': [{'k': 'The research case', 't': ' '.join(n for n in R.get('notes', []) if not n.startswith('Against it'))},
                      {'k': 'What the number is', 't': 'The market’s own chance (the middle of Kalshi’s bid and ask). Our model doesn’t price this market, so there is no Wedge % here.'}],
            'checks': [{'k': 'Research', 'ok': True, 't': 'Picked on the research case; the model’s checks cover receiving and rushing yards only.', 'info': True}],
            'log': [], 'alts': [], 'objection': next((n for n in R.get('notes', []) if n.startswith('Against it')), ''), 'miss': 'The game script turns against the read.',
            'change': 'A change at quarterback or a late scratch voids the read.', '_stat': 'research', '_team': '', '_qb': False,
            'ladder': [], 'value': RV.value(x_), 'path': 'R', 'sig_low': None, 'research': {'notes': R.get('notes', []), 'src': R.get('src', [])}, 'market_only': True}
from datetime import datetime as _dt
# games already played keep the card as it was posted before kickoff, graded (Thu Nov 12 6:44 PM CT card for WSH @ NYG)
PRIOR = {}   # games played this week, graded from the card as posted (none yet)
SUNB = {'games': {}, 'plays': {}}
ST10 = pd.read_csv(W + 'dl18/stats_player_week_2026.csv', low_memory=False); ST10 = ST10[(ST10.week == 12) & (ST10.season_type == 'REG')]
G10 = pd.read_csv(W + 'dl18/games.csv'); G10 = G10[(G10.season == 2026) & (G10.week == 12) & G10.home_score.notna()]
DONE = {f"{fx(x.away_team)} @ {fx(x.home_team)}": x for x in G10.itertuples(index=False)}
def grade(c, x):
    c = json.loads(json.dumps(c)); a, h = c['game'].split(' @ ')
    c['status'] = 'Final'; c['score'] = f"{a} {int(x.away_score)}, {h} {int(x.home_score)}"
    COLS = {'rushing yards': ('rushing_yards', 'rush yds'), 'receiving yards': ('receiving_yards', 'rec yds'), 'receptions': ('receptions', 'rec'), 'rush + rec yards': ('rr', 'rush + rec yds')}
    for p in c['plays']:
        m = re.search(r'(\d+)\+? (rushing yards|receiving yards|receptions|rush \+ rec yards)', p['thr']) or re.search(r'under (\d+) (rushing yards|receiving yards|receptions|rush \+ rec yards)', p['thr'])
        k = int(m.group(1)); col, unit = COLS[m.group(2)]
        s_ = ST10[ST10.player_display_name == p['player']]
        if not len(s_): p['result'] = {'outcome': 'Void', 'actual': None, 'text': 'did not play', 'profit_c': 0}; continue
        s_ = s_.iloc[0]; v = float(s_.rushing_yards) + float(s_.receiving_yards) if col == 'rr' else float(s_[col])
        yes = v >= k; won = yes if p['side'] == 'Yes' else not yes
        p['result'] = {'outcome': 'Won' if won else 'Lost', 'actual': v, 'text': f'{v:g} {unit}', 'profit_c': (100 - p['price']) if won else -p['price']}
    return c
for r in g.sort_values(['gameday', 'gametime']).itertuples(index=False):
    a, h = fx(r.away_team), fx(r.home_team); game = f'{a} @ {h}'
    if game not in DONE and (kicked(r) or game in LOCK) and game in FRI:
        c0 = json.loads(json.dumps(FRI[game]))
        c0['locked'] = ('Kicked off before this price check: the card stays as published before kickoff.' if kicked(r) else
                        'Picked Tuesday under the earlier pick rules; it stays as posted. The new research method starts with Sunday’s games.')
        c0['market'] = c0['locked'] + ' ' + c0.get('market', '')
        CARDS.append(c0); LOCKED.add(game)
        for row in (csv.DictReader(open(W + PREV + '/final_w12.csv')) if PREV else []):
            if row['game'] == game: CSV.append(row)
        continue
    if game in DONE:
        gc = grade(PRIOR[game], DONE[game]); CARDS.append(gc); RES = {p['line']: p['result'] for p in gc['plays']}
        for row in []:
            if row['game'] == game:
                rr = RES.get(row['line']); row['result'] = f"{rr['outcome']} ({rr['text']}, {rr['profit_c']:+d}¢)" if rr else row['result']; CSV.append(row)
        continue
    c_ = CON[game]
    fav, dog = (h, a) if c_['home_margin'] >= 0 else (a, h); by = abs(c_['home_margin']); pf = c_['p_home'] if fav == h else 1 - c_['p_home']
    out_ = [f"{x}" for x in []]
    lineup = []
    for t in (a, h):
        ii = INJ[(INJ.team.map(fx) == t) & INJ.position.isin(['QB', 'RB', 'WR', 'TE']) & INJ.report_status.isin(['Out', 'Doubtful', 'Questionable'])]
        if len(ii): lineup.append(f"{t}: " + '; '.join(f"{x.full_name} ({x.position}) {x.report_status.lower()}" for x in ii.itertuples(index=False)))
    plays, passed, eplays, epassed = [], [], [], []
    for o in sorted(res.get(game, []), key=lambda o: -(o['pick']['edge_mid'] if o['pick'] else o['close']['edge_mid'])):
        x = o['pick']; PL, PS, CS = (eplays, epassed, ECSV) if o['early'] else (plays, passed, CSV)
        if x:
            lg_ = ledger(o, x); top = [l for l in lg_ if l['pts'] > 0][:2]; neg = [l for l in lg_ if l['pts'] < 0][:1]
            why = ' '.join(l['text'] for l in top) or 'The lens nets in this direction.'
            vals = ', '.join(str(int(v)) for _, v, _ in o['logs'][-6:])
            cond = (f"Only if {o['name']} plays ({o['status'].lower()})." + ' ' if o['status'] == 'Questionable' else '') + \
                   (f"Holds as a final line up to {int(math.floor(x['lo'] - FEE - 0.5))}¢." if x['call'] == 'Final line' else
                    f"Becomes a final line at {int(math.floor(x['lo'] - FEE - 0.5))}¢ or less.")
            alt = sorted([y for y in o['rows'] if (y['k'], y['side']) != (x['k'], x['side']) and y['call'] != 'Pass'], key=lambda y: -y['edge_mid'])
            vs = (f"Beat {thr(alt[0], o['stat'])} ({alt[0]['side']} {alt[0]['ask']}¢, needs {alt[0]['be']}%, ours {alt[0]['lo']:.0f}–{alt[0]['hi']:.0f}%): "
                  f"{'this one clears by more' if x['edge_mid'] >= alt[0]['edge_mid'] else 'this one is likelier'}.") if alt else ''
            if V2:
                cond = RV.cond(x, x['call'], x['note'])
                oth = [y for y in o['rows'] if (y['k'], y['side']) != (x['k'], x['side'])]; ins = [y for y in oth if y['ask'] <= RV.CAP]
                alt = sorted([y for y in ins if y['call'] != 'Pass'] or ins or oth, key=RV.key, reverse=True)
                vs = RV.vs(x, alt[0] if alt else None, thr(x, o['stat']), thr(alt[0], o['stat']) if alt else '')
            pts = round(sum(l['pts'] for l in lg_), 1)
            pl_ = {'decision': x['call'], 'player': o['name'], 'line': f"{o['name']} {thr(x, o['stat'])} ({x['side']})", 'thr': thr(x, o['stat']), 'side': x['side'],
                          'price': x['ask'], 'payout': x['pays'], 'be': x['be'], 'mkt': x['mkt'], 'est': [round(x['lo']), round(x['hi'])], 'lo': x['lo'], 'mid': x['mid'], 'hi': x['hi'],
                          'edge_lo': x['edge_lo'], 'edge_mid': x['edge_mid'], 'platform': 'Robinhood (Kalshi contract)', 'checked': AT, 'ticker': x['tick'],
                          'why': why, 'support': f"{o['name']}'s last games: {vals}." if vals else '', 'sample': f"{'Hit' if x['side'] == 'Yes' else 'Stayed under'} in {x['n_hit']} of {x['n']} games this season ({vals}).",
                          'counter': (neg[0]['text'] if neg else 'Nothing in the lens points the other way.'), 'loses': 'Game script turns, or the volume goes elsewhere.' if o['stat'] in ('rec', 'recyd') else 'The game script takes the carries away, or the carries split.',
                          'cond': cond, 'vs': vs, 'pts': pts, 'shift': slope_shift(o, x), 'lens': lg_,
                          'tier': BR.tier(x['mid']), 'chain': BR.chain(x, o, T, rank), 'checks': BR.check_rows(x, o, WORD[o['stat']]),
                          'log': [[w_, op_, v_, int((v_ >= x['k']) if x['side'] == 'Yes' else (v_ < x['k']))] for w_, v_, op_ in x['chk']['LOG']['games']],
                          'alts': BR.alts(x, o, res[game], thr, WORD[o['stat']]), 'objection': BR.objection({**x, '_lens': lg_}, o, WORD[o['stat']]), 'miss': BR.miss_path(x, o),
                          'change': BR.change(x, o, cond), '_stat': o['stat'], '_team': o['team'], '_qb': T.pos.get(o['pid'], '') == 'QB',
                          'ladder': [{'t': thr(y, o['stat'], True), 'side': y['side'], 'ask': y['ask'], 'pays': y['pays'], 'be': y['be'], 'mkt': y['mkt'], 'lo': y['lo'], 'mid': y['mid'], 'hi': y['hi'],
                                      'hits': f"{y['n_hit']}/{y['n']}", 'call': y['call'], 'tag': 'card' if y is x else ''} for y in sorted(o['rows'], key=lambda y: (y['side'], y['k']))]}
            if V2:   # chance-first extras: the separate price read, alternatives by chance, the QB row as information
                pl_['value'] = RV.value(x); pl_['alts'] = RV.alts(x, o, res[game], thr)
                if V3: pl_['path'] = x.get('path', ''); pl_['sig_low'] = x.get('sig_low')
                for ck in pl_['checks']:
                    if ck['k'] == BR.LBL['QB']: ck['info'] = True
            if o['early']:
                bk_ = o['books'] or {}; cap_ = int(math.floor(x['lo'] - FEE - 0.5))
                pl_.update({'early': True, 'platform': 'Not on Kalshi yet: expected price from the sportsbooks', 'books': bk_,
                            'cond': (f"Only if {o['name']} plays ({o['status'].lower()}). " if o['status'] == 'Questionable' else '') +
                                    (f"Final if Kalshi lists it at {cap_}¢ or less." if x['call'] == 'Final line' else f"A lean; final if Kalshi lists it at {cap_}¢ or less.")})
                if V2: pl_['cond'] = (f"Final if Kalshi lists it at {RV.CAP}¢ or less." if x['call'] == 'Final line' else f"A lean while it is not on Kalshi. {x['note']}".strip())
            PL.append(pl_)
            CS.append({'game': game, 'decision': x['call'], 'line': pl_['line'], 'side': x['side'], 'price': x['ask'], 'payout': x['pays'], 'breakeven': x['be'], 'market_mid': x['mkt'],
                        'our_lo': x['lo'], 'our_mid': x['mid'], 'our_hi': x['hi'], 'edge_lo': x['edge_lo'], 'edge_mid': x['edge_mid'], 'evidence_pts': pts, 'shift': pl_['shift'],
                        'condition': cond, 'ticker': x['tick'], 'checked': AT, 'result': '', 'grade_read': '', 'grade_price': ''})
        else:
            y = o['close']; lg_ = ledger(o, y)
            nt = y.get('note') or ''
            mv = nt if nt else f"A price of {int(math.floor(y['mid'] - FEE - 0.5))}¢ or less on {thr(y, o['stat'])} ({y['side']}) makes it a lean."
            if V2: mv = (nt + ' ' if nt else '') + RV.passed_move(y)
            PS.append({'name': f"{o['name']} {WORD[o['stat']]}", 'why': f"Closest rung: {thr(y, o['stat'])} ({y['side']} {y['ask']}¢, needs {y['be']}%, ours {y['lo']:.0f}–{y['hi']:.0f}%).",
                           'move': mv, 'thesis': True, 'lens': lg_})
            if V2: PS[-1]['kind'] = RV.kind(y)
            CS.append({'game': game, 'decision': 'Pass', 'line': f"{o['name']} {thr(y, o['stat'])} ({y['side']})", 'side': y['side'], 'price': y['ask'], 'payout': y['pays'], 'breakeven': y['be'],
                        'market_mid': y['mkt'], 'our_lo': y['lo'], 'our_mid': y['mid'], 'our_hi': y['hi'], 'edge_lo': y['edge_lo'], 'edge_mid': y['edge_mid'], 'evidence_pts': round(sum(l['pts'] for l in lg_), 1),
                        'shift': '', 'condition': mv, 'ticker': y['tick'], 'checked': AT, 'result': '', 'grade_read': '', 'grade_price': ''})
    for p in plays:   # research pass: news that supports or defeats each line's key assumption
        rs = BR.RESEARCH.get((game, p['line'])) or getattr(BR, 'RESEARCH_PLAYER', {}).get((game, p['player'], p['side']))
        if not rs: continue
        p['research'] = {'notes': rs.get('notes', []), 'src': rs.get('src', [])}
        if rs.get('decision') and rs['decision'] != p['decision']:
            p['research']['was'] = p['decision']; p['decision'] = rs['decision']; p['cond'] = rs['why']
            for row in CSV:
                if row['line'] == p['line'] and row['game'] == game: row['decision'] = rs['decision']; row['condition'] = rs['why']
    for p in [p for p in plays if p['decision'] == 'Pass']:
        passed.insert(0, {'name': p['line'], 'why': p['cond'], 'move': 'Re-check if the news changes.', 'thesis': True, 'lens': p['lens'], **({'kind': 'research'} if V2 else {})}); plays.remove(p)
    plays.sort(key=lambda p: (p['decision'] != 'Final line', p['side'] != 'Yes', -(p['edge_lo'] if p['decision'] == 'Final line' else p['edge_mid'])))
    # one line per player, four per game: the rest go to the passed list so one game's read isn't stacked
    seen, keep, cut = set(), [], []
    for p in plays:
        if p['player'] in seen or len(keep) >= 4: cut.append(p); continue
        seen.add(p['player']); keep.append(p)
    if V2:   # same limit, best chance first, no over/under preference
        keep, cut = RV.card(plays)
        for p in cut:
            nth = {4: 'fifth', 5: 'sixth'}.get(RV.PER_GAME, f'{RV.PER_GAME + 1}th'); nw = {4: 'four', 5: 'five'}.get(RV.PER_GAME, str(RV.PER_GAME))
            passed.insert(0, {'name': p['line'], 'why': f"Also makes the card’s bar ({p['price']}¢, needs {p['be']}%, ours {p['est'][0]}–{p['est'][1]}%), but it would be a second line on {p['player']} or a {nth} in this game.",
                              'move': f'Left off by the card limit: one line per player, {nw} per game.', 'thesis': True, 'lens': p['lens'], 'kind': 'limit'})
            for row in CSV:
                if row['line'] == p['line'] and row['game'] == game: row['decision'] = 'Pass'; row['condition'] = f'Card limit: one line per player, {nw} per game'
        cut = []
    for p in cut:
        passed.insert(0, {'name': p['line'], 'why': f"Also clears at our middle ({p['price']}¢, needs {p['be']}%, ours {p['est'][0]}–{p['est'][1]}%), but it rides the same read as a line already on the card.",
                          'move': 'Left off to avoid stacking one game’s read.', 'thesis': True, 'lens': p['lens']})
        for row in CSV:
            if row['line'] == p['line'] and row['game'] == game: row['decision'] = 'Pass'; row['condition'] = 'Same read as a line already on the card'
    plays = keep
    if V3:   # the method's other markets: research picks at the market's own number (brain_layer.RESEARCH_MARKET), inside the same card limit
        for key, R in getattr(BR, 'RESEARCH_MARKET', {}).items():
            if key[0] != game: continue
            mp = market_play(game, key, R, r)
            if mp is None: continue
            if mp['decision'] == 'Pass' or len(plays) >= RV.PER_GAME or any(q['player'] == mp['player'] for q in plays):
                passed.insert(0, {'name': mp['line'], 'why': mp['cond'] if mp['decision'] == 'Pass' else 'A research pick, left off by the card limit.', 'move': 'Re-check if the news changes.', 'kind': 'research'}); continue
            plays.append(mp)
            CSV.append({'game': game, 'decision': mp['decision'], 'line': mp['line'], 'side': mp['side'], 'price': mp['price'], 'payout': mp['payout'], 'breakeven': mp['be'], 'market_mid': mp['mkt'],
                        'our_lo': mp['lo'], 'our_mid': mp['mid'], 'our_hi': mp['hi'], 'edge_lo': mp['edge_lo'], 'edge_mid': mp['edge_mid'], 'evidence_pts': 0, 'shift': 0,
                        'condition': mp['cond'], 'ticker': mp['ticker'], 'checked': AT, 'result': '', 'grade_read': '', 'grade_price': ''})
    passed = RV.order_passed(passed) if V2 else passed[:8]
    for p in eplays:
        rs = BR.RESEARCH.get((game, p['line'])) or getattr(BR, 'RESEARCH_PLAYER', {}).get((game, p['player'], p['side']))
        if rs and rs.get('decision') and rs['decision'] != p['decision']: p['decision'] = rs['decision']; p['cond'] = rs['why']
    eplays = [p for p in eplays if p['decision'] != 'Pass']
    eplays.sort(key=lambda p: (p['decision'] != 'Final line', p['side'] != 'Yes', -(p['edge_lo'] if p['decision'] == 'Final line' else p['edge_mid'])))
    if V2: eplays.sort(key=lambda p: (p['decision'] != 'Final line', -p['lo'], -p['mid']))
    seen = {p['player'] for p in plays}; ekeep = []
    for p in eplays:
        if p['player'] in seen or len(ekeep) >= 4:
            epassed.insert(0, {'name': p['line'], 'why': f"Clears at the expected price ({p['price']}¢, needs {p['be']}%, ours {p['est'][0]}–{p['est'][1]}%), but rides the same read as a line already listed.", 'move': 'Left off to avoid stacking one game’s read.'})
            continue
        seen.add(p['player']); ekeep.append(p)
    eplays = ekeep
    neprops = len([o for o in res.get(game, []) if o['early']])
    nprops = len([o for o in res.get(game, []) if not o['early']])
    # keys and scripts from the lens tables
    def key_for(off, de):
        D = T.D.loc[de]
        strengths = sorted([('ypc', D.ypc, 'the run game'), ('pass_yds', D.pass_yds, 'the passing game'), ('TE_yds', D.TE_yds, 'tight ends'), ('RB_yds', D.RB_yds, 'backs in the passing game'), ('WR_yds', D.WR_yds, 'wide receivers')],
                           key=lambda t: (t[1] - T.mu[t[0]]) / T.sd[t[0]])
        best, worst = strengths[0], strengths[-1]
        return {'team': de, 'take': f"{off}'s {best[2]}.", 'how': f"{de} allows {best[1]:.1f} {'yards a carry' if best[0] == 'ypc' else 'yards a game'} there ({rank(best[0], de)}) and blitzes on {pc(D.blitz)} of dropbacks ({rankw('blitz', de)}).",
                'gives': f"{worst[2][0].upper() + worst[2][1:]}: {worst[1]:.1f} {'yards a carry' if worst[0] == 'ypc' else 'yards a game'} allowed ({rank(worst[0], de)}).", 'counter': f"{off} leans on {worst[2]}."}
    keys = [key_for(a, h), key_for(h, a)]
    scripts = {'control': f"{fav} leads as the {by:.1f}-point favorite and runs the clock; {dog}'s passing volume climbs.",
               'competitive': f"A one-score game around the {c_['total']:.1f}-point total; volume follows each team's usual shape.",
               'reversal': f"{dog} leads early and {fav} chases, so {fav}'s passing volume climbs and its run game shrinks."}
    tag = 'No player-prop ladders are open yet for this game. They post through the week.' if nprops == 0 else f"{nprops} player ladders open (receiving and rushing) were run through the lens."
    card = {'game': game, 'wait': nprops == 0, 'kick': KO[game][0], 'venue': VENUE.get(r.home_team, ''), 'market': f"{fav} −{by:.1f} (Kalshi: {fav} {100 * pf:.0f}%), total {c_['total']:.1f}. Ladders checked {CHK_AT}. {tag}",
            'lineup': ' '.join(lineup) or 'No skill-position player is listed out or questionable yet.', 'branches': ('Thursday’s game: practice reports post Monday through Wednesday. ' if KO[game][0].endswith('Thu') else 'Practice reports start Wednesday; final designations come Friday. ') + 'Inactives post 90 minutes before kickoff; a late scratch changes any line that leans on the player.',
            'keys': keys, 'scripts': scripts, 'plays': plays, 'passed': passed, 'likely': [f"{p['line']} ({p['price']}¢): ours {p['mid']:.0f}%, needs {p['be']}%" for p in sorted(plays, key=lambda p: -p['mid'])[:3]],
            'value': ([f"{p['line']} at {p['price']}¢ (needs {p['be']}%, ours {p['est'][0]}–{p['est'][1]}%): {p['decision'].lower()}." for p in plays[:3]] or (['Nothing clears break-even after fees yet.'] if nprops else ['Player ladders open later in the week.'])),
            'sources': [{'t': f'Kalshi ladders (traded on Robinhood), checked {CHK_AT}', 'u': 'https://kalshi.com', 'k': 'Market'},
                        {'t': 'nflverse play-by-play and FTN charting, 2026 Weeks 1-11', 'u': 'https://github.com/nflverse/nflverse-data/releases', 'k': 'Logs'},
                        {'t': f'ESPN injury report, {INJ_AT}', 'u': 'https://www.espn.com/nfl/injuries', 'k': 'Official'}]}
    card['lens'] = blocks.lens_block(a, h, 12, (f"The lens put {len(plays)} line{'s' if len(plays) != 1 else ''} on the card here: " + '; '.join(f"{p['line']}: {p['decision'].lower()}" for p in plays) + '.') if plays else
                                     ((f'Nothing reaches a {RV.BAR}% chance at {RV.CAP}¢ or less yet.' if V2 else 'Nothing clears break-even after fees yet.') if nprops else 'Player ladders for this game open later in the week; the lens tables are ready for them.'))
    qok, qt = BR.QB.get(game, (True, ''))
    if V2: qok = True   # v2: a backup starter is a research factor; the game stays on the board
    card['brain'] = {'qb': {'ok': qok, 't': qt}, 'interaction': BR.interaction(plays) if plays else [], 'coverage': coverage(game, nprops), 'revisions': revisions(game, plays, res.get(game, []))}
    card['early'] = eplays; card['early_n'] = neprops; card['early_passed'] = [{k: v for k, v in x_.items() if k != 'lens'} for x_ in epassed[:6]]
    CARDS.append(card)
MIX = {}
LIVE = [c for c in CARDS if c.get('status') != 'Final' and c['game'] not in LOCKED]
LOCKC = [c for c in CARDS if c['game'] in LOCKED]
for tier, ek in (() if V2 else (('Final line', 'edge_lo'), ('Conditional lean', 'edge_mid'))):   # v2: no under/over mix
    P_ = [(c, p) for c in LIVE for p in c['plays'] if p['decision'] == tier]
    lo_ = sum(p['side'] == 'Yes' for c in LOCKC for p in c['plays'] if p['decision'] == tier); lu_ = sum(p['side'] == 'No' for c in LOCKC for p in c['plays'] if p['decision'] == tier)
    O_ = [x for x in P_ if x[1]['side'] == 'Yes']; U_ = sorted([x for x in P_ if x[1]['side'] == 'No'], key=lambda x: -x[1][ek])
    allow = max(0, (max(1, math.ceil((len(O_) + lo_) / BR.RATIO)) if (U_ or lu_) else 0) - lu_)
    MIX[tier] = {'overs': len(O_) + lo_, 'unders_cleared': len(U_) + lu_, 'unders_kept': min(allow, len(U_)) + lu_, 'locked_games': len(LOCKC)}
    for c, p in U_[allow:]:
        c['plays'].remove(p)
        c['passed'].insert(0, {'name': p['line'], 'why': f"Cleared as a {tier.lower()} on its own numbers ({p['side']} {p['price']}¢, needs {p['be']}%, ours {p['est'][0]}–{p['est'][1]}%) and passed every check.",
                               'move': 'Left off only to keep the card near one under for every three overs.', 'thesis': True, 'lens': p['lens']})
        for row in CSV:
            if row['line'] == p['line'] and row['game'] == c['game']: row['decision'] = 'Pass'; row['condition'] = 'Left off for the card mix (about one under per three overs); still clears on its own numbers'
# early (book-priced) lines follow the same mix: about one under for every three overs
for tier, ek in (() if V2 else (('Final line', 'edge_lo'), ('Conditional lean', 'edge_mid'))):   # v2: no under/over mix
    P_ = [(c, p) for c in LIVE for p in c.get('early', []) if p['decision'] == tier]
    O_ = [x for x in P_ if x[1]['side'] == 'Yes']; U_ = sorted([x for x in P_ if x[1]['side'] == 'No'], key=lambda x: -x[1][ek])
    allow = max(1, math.ceil(len(O_) / BR.RATIO)) if U_ else 0
    MIX['early ' + tier] = {'overs': len(O_), 'unders_cleared': len(U_), 'unders_kept': min(allow, len(U_))}
    for c, p in U_[allow:]:
        c['early'].remove(p)
        c['early_passed'].insert(0, {'name': p['line'], 'why': f"Clears as an early {tier.lower()} at the expected price ({p['side']} {p['price']}¢, needs {p['be']}%, ours {p['est'][0]}–{p['est'][1]}%).",
                                     'move': 'Left off only to keep the list near one under for every three overs.'})
for c in LIVE:
    pl = c['plays']
    c['likely'] = [f"{p['line']} ({p['price']}¢): ours {p['mid']:.0f}%, needs {p['be']}%" for p in sorted(pl, key=lambda p: -p['mid'])[:3]]
    c['value'] = [f"{p['line']} at {p['price']}¢ (needs {p['be']}%, ours {p['est'][0]}–{p['est'][1]}%): {p['decision'].lower()}." for p in pl[:3]] or ['Nothing clears break-even after fees yet.']
    if V2: c['value'] = [f"{p['line']} at {p['price']}¢: {p['value']['t']}" for p in pl[:3]] or [f"Nothing reaches a {RV.BAR}% chance at {RV.CAP}¢ or less yet."]
    if pl: c['lens']['verdict'] = f"The lens put {len(pl)} line{'s' if len(pl) != 1 else ''} on the card here: " + '; '.join(f"{p['line']}: {p['decision'].lower()}" for p in pl) + '.'
    c['brain']['interaction'] = BR.interaction(pl) if pl else []
    c['brain']['revisions'] = revisions(c['game'], pl, res.get(c['game'], []))
    for r_ in c['brain']['revisions']:
        if r_['v'] == 'Pass' and any(x['name'] == r_['line'] and 'one under for every three overs' in x.get('move', '') for x in c['passed']): r_['why'] = 'Still clears on its own numbers; left off for the card mix (about one under per three overs).'
print('mix', MIX)
nF = sum(p['decision'] == 'Final line' for c in CARDS for p in c['plays']); nL = sum(p['decision'] == 'Conditional lean' for c in CARDS for p in c['plays'])
# keep final.js under the 256 KB document cap: the method text and backtest table once at the top, each play's ladder
# trimmed to its own side within 3 rungs of the pick, and no lens ledger on passed lines
LH = next((c['lens'] for c in CARDS if c.get('status') != 'Final'), {})
for c in CARDS:
    if c.get('status') == 'Final': continue
    for k in ('how', 'check', 'check_title', 'check_head', 'thru'): c['lens'].pop(k, None)
    for p in c['plays']:
        lad = [x for x in p['ladder'] if x['side'] == p['side']]
        i = next((j for j, x in enumerate(lad) if x['tag'] == 'card'), 0)
        p['ladder'] = lad[max(0, i - 3): i + 4]
    c['passed'] = [{k: v for k, v in x.items() if k != 'lens'} for x in c['passed'][:6]]
    for p in c.get('early', []):
        lad = [x for x in p['ladder'] if x['side'] == p['side']]
        i = next((j for j, x in enumerate(lad) if x['tag'] == 'card'), 0)
        p['ladder'] = lad[max(0, i - 3): i + 4]
        for k in ('chain', 'checks', 'log', 'alts', 'objection', 'miss', 'change', '_stat', '_team', '_qb', 'research'): p.pop(k, None)
F = {'at': AT, 'books_at': AT, 'week': 12, 'cards': CARDS, 'model': 'v6', 'backtest': {k: REP[k] for k in ('all', 'w7', 'w8', 'w9', 'band40_60') if k in REP},
     'graded': {'thru': 'Thursday', **{k: [sum(p['result']['outcome'] == 'Won' for c in CARDS for p in c['plays'] if p.get('result') and p['decision'] == d),
                                                      sum(p['result']['outcome'] == 'Lost' for c in CARDS for p in c['plays'] if p.get('result') and p['decision'] == d),
                                                      sum(p['result']['profit_c'] for c in CARDS for p in c['plays'] if p.get('result') and p['decision'] == d)] for k, d in (('final', 'Final line'), ('lean', 'Conditional lean'))}},
     'early': {'at': BL.AN['at'], 'books': sorted(set(BL.AN.get('books', {}).values())), 'cal': BL.CAL,
               'assessed': sum(c.get('early_n', 0) for c in CARDS), 'ladders': len(EARLY),
               'final': sum(p['decision'] == 'Final line' for c in CARDS for p in c.get('early', [])), 'lean': sum(p['decision'] == 'Conditional lean' for c in CARDS for p in c.get('early', []))},
     'lens_how': LH.get('how'), 'lens_check': LH.get('check'), 'lens_check_title': LH.get('check_title'), 'lens_check_head': LH.get('check_head'), 'lens_thru': LH.get('thru')}
# Sun Nov 22: the final draft of the Week 12 card (W12_DRAFT='Final draft', W12_RECHECK_AT=<UTC time the card lines' Kalshi prices were re-checked>)
if os.environ.get('W12_DRAFT'): F['draft'] = os.environ['W12_DRAFT']
if os.environ.get('W12_RECHECK_AT'): F['recheck_at'] = os.environ['W12_RECHECK_AT']
F['rules'] = RULES
if V2: F.update({'rules_since': RV.SINCE, 'cap': RV.CAP, 'bar': RV.BAR, 'rules_text': RV.TEXT})
BRAIN = {'at': AT, 'plays': {}, 'games': {}}
for c in CARDS:
    if c.get('status') == 'Final':
        if c['game'] in SUNB.get('games', {}): BRAIN['games'][c['game']] = SUNB['games'][c['game']]
        for k_, v_ in SUNB.get('plays', {}).items():
            if k_.startswith(c['game'] + '|'): BRAIN['plays'][k_] = v_
        continue
    if c['game'] in LOCKED:
        if c['game'] in SATB['games']: BRAIN['games'][c['game']] = SATB['games'][c['game']]
        for k_, v_ in SATB['plays'].items():
            if k_.startswith(c['game'] + '|'): BRAIN['plays'][k_] = v_
        continue
    BRAIN['games'][c['game']] = c.pop('brain')
    for p in c['plays']:
        BRAIN['plays'][c['game'] + '|' + p['line']] = {k: p.pop(k) for k in ('chain', 'checks', 'log', 'alts', 'objection', 'miss', 'change')}
        if 'research' in p: BRAIN['plays'][c['game'] + '|' + p['line']]['research'] = p.pop('research')
        for k in ('_stat', '_team', '_qb'): p.pop(k, None)
BT = json.load(open(W + 'bt/brain_bt.json'))
BRAIN['rank'] = [{'game': c['game'], 'line': p['line'], 'decision': p['decision'], 'tier': p['tier'], 'mid': p['mid'], 'lo': p['lo'], 'hi': p['hi'], 'price': p['price'], 'be': p['be']}
                 for c in CARDS if c.get('status') != 'Final' for p in c['plays']]
BRAIN['rank'].sort(key=lambda r: -r['mid'])
BRAIN['bt'] = BT; BRAIN['mix'] = MIX
json.dump(BRAIN, open(OUTD + 'brain_w12.json', 'w'), ensure_ascii=False, default=float, separators=(',', ':'))
json.dump(F, open(OUTD + 'final_w12.json', 'w'), ensure_ascii=False, default=float, separators=(',', ':'))
with open(OUTD + 'final_w12.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(CSV[0].keys())); w.writeheader(); w.writerows(CSV)
with open(OUTD + 'early_w12.csv', 'w', newline='') as f:
    if ECSV: w = csv.DictWriter(f, fieldnames=list(ECSV[0].keys())); w.writeheader(); w.writerows(ECSV)   # none until the books are pulled
print('final lines', nF, 'leans', nL, 'csv rows', len(CSV), '| early (book-priced):', F['early']['final'], 'final', F['early']['lean'], 'leans from', F['early']['assessed'], 'player markets')
for c in CARDS:
    print(f"{c['game']:10s} plays {len(c['plays'])} passed {len(c['passed'])}")
    for p in c['plays']: print('   ', p['decision'][:5], p['line'], p['price'], 'needs', p['be'], 'ours', p['lo'], p['mid'], p['hi'], p.get('tier'))
    for p in c.get('early', []): print('    EARLY', p['decision'][:5], p['line'], p['price'], 'needs', p['be'], 'ours', p['lo'], p['mid'], p['hi'], '| books', (p.get('books') or {}).get('line'), (p.get('books') or {}).get('n'))
