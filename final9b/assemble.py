"""Build the Week 9 final card from the full-ladder analysis (every two-sided rung, any price) and the written record."""
import json, sys, csv, re, copy
sys.path.insert(0, '/home/claude/wedger/final9b')
from narr import PLAY, PASS, EXTRA_FIX, TEXT_FIX
B = '/home/claude/wedger/'
A = json.load(open(B + 'final9b/analysis.json'))
AT = A['at']
ORDER = ['CIN@ATL', 'NYG@PHI', 'DEN@CAR', 'DET@MIA', 'NYJ@KC', 'CLE@NO', 'LA@WAS', 'DAL@IND', 'HOU@LAC', 'LV@SF', 'ARI@SEA', 'GB@NE', 'TB@CHI', 'BUF@MIN']
WORD = {'pass': 'passing yards', 'rush': 'rushing yards', 'rec': 'receptions', 'recyd': 'receiving yards'}
SHORT = {'pass': 'pass yds', 'rush': 'rush yds', 'rec': 'rec', 'recyd': 'rec yds'}
def thr(r, st, short=False):
    w = SHORT[st] if short else WORD[st]
    return (f"{int(r['k'])}+ {w}" if r['side'] == 'Yes' else f"under {int(r['k'])} {w}")
def pct(x): return f"{x:.0f}%"
def rng(r): return f"{r['lo']:.0f}–{r['hi']:.0f}%"
def sgn(x): return ('+' if x >= 0 else '−') + f"{abs(x):.1f}"
def fmtv(v, st): return str(int(v))
TH = {(o['game'], o['name']): o for o in A['res']}
def ladder_rows(o):
    out = []
    p, a = o['pick'], o['alt']
    for r in sorted(o['rows'], key=lambda r: (r['side'], r['k'])):
        tag = ''
        if p and (r['k'], r['side']) == (p['k'], p['side']): tag = 'card'
        elif a and o['pick'] and (r['k'], r['side']) == (a['k'], a['side']): tag = 'alt'
        out.append({'t': thr(r, o['stat'], True), 'side': r['side'], 'ask': r['ask'], 'pays': r['pays'], 'be': r['be'], 'mkt': r['mkt'], 'lo': r['lo'], 'mid': r['mid'], 'hi': r['hi'],
                    'hits': f"{r['n_hit']}/{r['n']}", 'call': r['call'], 'tag': tag})
    return out
def vs_text(o):
    p, a = o['pick'], o['alt']
    if not a: return ''
    fin = p['call'] == 'Final line'
    ep, ea = (p['edge_lo'], a['edge_lo']) if fin else (p['edge_mid'], a['edge_mid'])
    yard = 'at the low end of our number' if fin else 'at the middle of our number'
    head = f"Beat {thr(a, o['stat'])} ({a['side']} {a['ask']}¢, needs {a['be']}%, ours {rng(a)}). "
    if abs(ep - ea) < 0.05:
        lo_p, lo_a = p['edge_lo'], a['edge_lo']
        if not fin and abs(lo_p - lo_a) >= 0.05:
            body = f"Both clear break-even by {sgn(ep)} points {yard}; this one holds up better at the low end ({sgn(lo_p)} vs {sgn(lo_a)})" + (f" and pays more ({p['pays']:.2f}× vs {a['pays']:.2f}×)." if p['pays'] > a['pays'] else f" and hits more often ({pct(p['mid'])} vs {pct(a['mid'])}).")
        elif p['mid'] >= a['mid']:
            body = f"Both clear break-even by {sgn(ep)} points {yard}; this one hits more often ({pct(p['mid'])} vs {pct(a['mid'])} by our number)."
        else:
            body = f"Both clear break-even by {sgn(ep)} points {yard}; this one pays more ({p['pays']:.2f}× vs {a['pays']:.2f}×)."
    elif a['mid'] > p['mid']:
        body = f"That rung hits more often ({pct(a['mid'])} vs {pct(p['mid'])}), but its price leaves {sgn(ea)} points over break-even {yard}, against {sgn(ep)} here."
    else:
        body = f"That rung pays more ({a['pays']:.2f}× vs {p['pays']:.2f}×) but hits less often ({pct(a['mid'])} vs {pct(p['mid'])}), leaving {sgn(ea)} points over break-even {yard}, against {sgn(ep)} here."
    if fin and a['call'] != 'Final line': body += ' It doesn\'t clear once the uncertainty is applied.'
    return head + body
def sample_text(o, r):
    vals = [fmtv(v, o['stat']) for _, v, _ in o['vals']]
    lab = (f"{int(r['k'])}+" if r['side'] == 'Yes' else f"Under {int(r['k'])}")
    return f"{lab} in {r['n_hit']} of {r['n']} games this season ({', '.join(vals)}, in order)."
cards, rows_csv, board = [], [], []
for g in ORDER:
    c = json.load(open(B + f'final9/cards_v1/{g}.json')) if False else json.load(open(B + f'final9/cards/{g}.json'))
    c = copy.deepcopy(c)
    # text fixes on keys/scripts
    def fx(t):
        for a_, b_ in TEXT_FIX: t = t.replace(a_, b_)
        return t
    for k in c['keys']:
        for kk in ('take', 'how', 'gives', 'counter'): k[kk] = fx(k[kk])
    c['scripts'] = {k: fx(v) for k, v in c['scripts'].items()}
    c['market'], c['lineup'] = fx(c['market']), fx(c['lineup'])
    TS = [o for o in A['res'] if o['game'] == g]
    plays, passed = [], []
    for o in TS:
        p = o['pick']; nm = o['name']
        if p:
            T = PLAY[nm]; pers = T.get('pers', '')
            price_cond = (f"Holds as a final line up to {p['final_at']}¢." if p['call'] == 'Final line' else f"Becomes a final line at {p['final_at']}¢ or less.")
            line = f"{o['player']} {thr(p, o['stat'])} ({p['side']})"
            pl = {'decision': p['call'], 'player': o['player'], 'line': line, 'thr': thr(p, o['stat']), 'side': p['side'], 'price': p['ask'], 'payout': p['pays'], 'be': p['be'],
                  'mkt': p['mkt'], 'est': [round(p['lo']), round(p['hi'])], 'lo': p['lo'], 'mid': p['mid'], 'hi': p['hi'], 'edge_lo': p['edge_lo'], 'edge_mid': p['edge_mid'],
                  'platform': 'Robinhood (Kalshi contract)', 'checked': AT, 'ticker': o['prefix'] + '-' + str(int(p['k'])),
                  'why': T['why'], 'support': T['support'], 'sample': sample_text(o, p) + ' ' + T['note'], 'counter': T['counter'], 'loses': T['loses'],
                  'cond': (pers + ' ' if pers else '') + price_cond, 'vs': vs_text(o), 'pts': o['pts'], 'shift': o['delta'], 'ladder': ladder_rows(o)}
            plays.append(pl)
        else:
            T = PASS[nm]; cl = o['closest']; pers = T.get('pers', '')
            name = f"{o['player']} {WORD[o['stat']]}"
            why = T['why']
            if cl and o['delta'] != 0 and not (o['why_thin'].startswith('only one')):
                why += f" Closest rung: {thr(cl, o['stat'])} ({cl['side']} {cl['ask']}¢, needs {cl['be']}%, ours {rng(cl)})."
            elif cl and o['why_thin'].startswith('only one'):
                why += f" The one quoted rung: {thr(cl, o['stat'])} ({cl['side']} {cl['ask']}¢, needs {cl['be']}%)."
            mv = T['move'] or (f"A price of {cl['lean_at']}¢ or less on {thr(cl, o['stat'])} makes it a lean." if cl else 'None pregame.')
            if pers: mv = pers + ' ' + mv
            passed.append({'name': name, 'why': why, 'move': mv, 'thesis': True})
            if cl:
                rows_csv.append({'game': c['game'], 'decision': 'Pass', 'line': f"{o['player']} {thr(cl, o['stat'])} ({cl['side']})", 'side': cl['side'], 'price': cl['ask'], 'payout': cl['pays'],
                                 'breakeven': cl['be'], 'market_mid': cl['mkt'], 'our_lo': cl['lo'], 'our_mid': cl['mid'], 'our_hi': cl['hi'], 'edge_lo': cl['edge_lo'], 'edge_mid': cl['edge_mid'],
                                 'evidence_pts': o['pts'], 'shift': o['delta'], 'condition': mv, 'ticker': o['prefix'] + '-' + str(int(cl['k'])), 'checked': AT, 'result': '', 'grade_read': '', 'grade_price': ''})
    # carry over non-thesis passes
    thesis_names = [o['name'].split()[-1] for o in TS] + [o['player'].split()[1] if len(o['player'].split()) > 1 else o['player'] for o in TS]
    for x in c['passed']:
        nm0 = x['name']
        if any(t in nm0 for t in ['Higgins', 'Bijan', 'Pitts', 'Chase Brown', 'Gibbs', 'Walker', 'Shough', 'Olave', 'Lamb', 'Taylor', 'Javonte', 'Marks', 'McCaffrey', 'Allgeier', 'Stevenson',
                                  'Swift', 'Josh Allen', 'Cook', 'Hockenson', 'Wentz', 'Young', 'Smith-Njigba', 'Jeanty', 'Fannin', 'Daniels']):
            continue
        y = dict(x); y.update(EXTRA_FIX.get(nm0, {})); y['thesis'] = False
        assert 'backtest' not in (y['why'] + y['move']), nm0
        passed.append(y)
    KEYP = lambda p: (p['decision'] != 'Final line', -(p['edge_lo'] if p['decision'] == 'Final line' else p['edge_mid']))
    plays.sort(key=KEYP)
    # side-by-side rankings across every rung of every thesis with a view in this game
    cand = [o for o in TS if o['delta'] != 0 and not o['why_thin'].startswith('only one')]
    lk = []
    for o in cand:
        r = sorted(o['rows'], key=lambda r: -r['mid'])[0]
        lk.append((r['mid'], f"{o['player']} {thr(r, o['stat'], True)} ({r['side']} {r['ask']}¢): ours {pct(r['mid'])}, needs {r['be']}%" + (' · clears' if r['edge_lo'] >= 0.5 else ' · priced at or past our number' if r['edge_mid'] < 0.5 else ' · clears only at our middle')))
    c['likely'] = [t for _, t in sorted(lk, key=lambda x: -x[0])[:3]]
    val = []
    for o in cand:
        if o['thin']: continue
        for r in o['rows']:
            if r['edge_lo'] >= 0.5: val.append((r['edge_lo'], f"{o['player']} {thr(r, o['stat'], True)} ({r['side']} {r['ask']}¢): needs {r['be']}%, ours {rng(r)}, clears by {sgn(r['edge_lo'])} at the low end"))
    val.sort(key=lambda x: -x[0])
    if val: c['value'] = [t for _, t in val[:4]]
    else:
        ls = [p for p in plays]
        c['value'] = ['Nothing clears break-even after fees and uncertainty.'] + ([f"Closest: {ls[0]['line']} at {ls[0]['price']}¢ (needs {ls[0]['be']}%, ours {ls[0]['est'][0]}–{ls[0]['est'][1]}%), a conditional lean."] if ls else [])
    c['plays'], c['passed'] = plays, passed
    # sources, ordered by what they can prove: official -> reporting -> team/analysis specialists -> logs -> market
    def rank(s):
        u, t = s['u'], s['t']
        if re.search(r'seahawks\.com|vikings\.com|panthers\.com|detroitlions\.com|therams\.com|newyorkjets\.com|nfl\.com|espn\.com/nfl/injuries', u): return 0, 'Official'
        if t.startswith('AP') or 'tsn.ca' in u: return 1, 'Reporting'
        if 'nflverse' in u: return 3, 'Logs'
        if re.search(r'kalshi|actionnetwork|/betting/', u): return 4, 'Market'
        return 2, 'Analysis'
    src = [s for s in c.get('sources', [])]
    if not any('nflverse' in s['u'] for s in src): src.append({'t': 'nflverse play-by-play, 2026 Weeks 1–8 (game logs, scrambles vs designed runs)', 'u': 'https://github.com/nflverse/nflverse-data/releases'})
    src.append({'t': f"Kalshi ladders (traded on Robinhood), every rung checked 9:15–9:16 PM CT Sat", 'u': 'https://kalshi.com'})
    src.append({'t': 'Action Network consensus props (attempts, carries, spread, total)', 'u': 'https://www.actionnetwork.com/nfl/props'})
    for s in src: s['k'] = rank(s)[1]
    c['sources'] = sorted(src, key=lambda s: rank(s)[0])
    for p in plays:
        rows_csv.append({'game': c['game'], 'decision': p['decision'], 'line': p['line'], 'side': p['side'], 'price': p['price'], 'payout': p['payout'], 'breakeven': p['be'],
                         'market_mid': p['mkt'], 'our_lo': p['lo'], 'our_mid': p['mid'], 'our_hi': p['hi'], 'edge_lo': p['edge_lo'], 'edge_mid': p['edge_mid'], 'evidence_pts': p['pts'],
                         'shift': p['shift'], 'condition': p['cond'], 'ticker': p['ticker'], 'checked': AT, 'result': '', 'grade_read': '', 'grade_price': ''})
    cards.append(c)
order = {'Final line': 0, 'Conditional lean': 1, 'Pass': 2}
rows_csv.sort(key=lambda r: (ORDER.index([g for g in ORDER if json.load(open(B + f'final9/cards/{g}.json'))['game'] == r['game']][0]), order[r['decision']]))
F = {'at': AT, 'books_at': '2026-11-07T23:47:21Z', 'rh_at': AT, 'rules': {'fee': 2, 'final': 0.5, 'lean': 0.5, 'spread': 8}, 'cards': cards}
json.dump(F, open(B + 'final9/final_w9.json', 'w'), ensure_ascii=False)
with open(B + 'final9/final_w9.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows_csv[0].keys())); w.writeheader(); w.writerows(rows_csv)
nF = sum(p['decision'] == 'Final line' for c in cards for p in c['plays']); nL = sum(p['decision'] == 'Conditional lean' for c in cards for p in c['plays']); nP = sum(len(c['passed']) for c in cards)
print('final', nF, 'lean', nL, 'passed', nP, 'csv rows', len(rows_csv))
for c in cards:
    print('==', c['game'])
    for p in c['plays']: print('  ', p['decision'][:5], p['line'], p['price'], '| BE', p['be'], 'ours', p['est'], '|', p['cond'])
    print('   likely:', c['likely']); print('   value:', c['value'])
