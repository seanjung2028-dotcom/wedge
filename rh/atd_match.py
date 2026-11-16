import json, re, unicodedata
import pandas as pd

D = '/home/claude/wedger/nflverse_dl/'
B = '/home/claude/wedger/rh/'

# refresh the Monday-night ATD prices from tonight's scrape
prices = json.load(open(B + 'atd_prices.json'))
mnf = json.load(open(B + 'rh_events_mnf.json'))
fresh = [e for e in mnf if e[1] == 'San Francisco vs Washington: Anytime Touchdown'][0]
for e in prices['events']:
    if e['name'] == 'San Francisco vs Washington: Anytime Touchdown':
        e['c'] = [{'player': c[0], 'ya': c[1], 'yb': c[2], 'na': c[3], 'st': c[6], 'trad': c[5]} for c in fresh[4]]
        e['priced_at'] = '2026-10-19T03:57:40Z'
json.dump(prices, open(B + 'atd_prices.json', 'w'))

ro = pd.read_csv(D + 'roster2026.csv', low_memory=False)
ro = ro.sort_values('week').drop_duplicates('gsis_id', keep='last')

def norm(n):
    n = unicodedata.normalize('NFKD', str(n)).encode('ascii', 'ignore').decode().lower()
    n = re.sub(r"[.'’]", '', n).replace('-', ' ')
    n = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', n)
    return re.sub(r'\s+', ' ', n).strip()

GAME = {'Los Angeles R vs Arizona': ('ARI', 'LA'), 'Kansas City vs Los Angeles C': ('LAC', 'KC'),
        'Las Vegas vs Buffalo': ('BUF', 'LV'), 'Green Bay vs Dallas': ('DAL', 'GB'),
        'San Francisco vs Washington': ('WAS', 'SF')}
idx = {}
for _, r in ro.iterrows():
    for nm in {r['full_name'], f"{r['football_name']} {r['last_name']}"}:
        idx.setdefault((norm(nm), r['team']), []).append(r)
out, miss = [], []
for e in prices['events']:
    g = e['name'].split(':')[0]; teams = GAME[g]
    for c in e['c']:
        cands = []
        for t in teams:
            cands += idx.get((norm(c['player']), t), [])
        if not cands:
            cands = [r for (k, t), v in idx.items() if k == norm(c['player']) for r in v]
        if not cands:
            miss.append((c['player'], g)); continue
        r = cands[-1]
        out.append({'player': c['player'], 'event': g, 'gsis': r['gsis_id'],
                    'espn': None if pd.isna(r['espn_id']) else str(int(r['espn_id'])), 'pos': r['position'],
                    'team': r['team'], 'ya': c['ya'], 'yb': c['yb'], 'na': c['na'], 'st': c['st'], 'trad': c['trad'],
                    'ncand': len(cands)})
json.dump(out, open(B + 'atd_players.json', 'w'))
print('matched', len(out), 'missing', miss)
gl = json.load(open('/root/.claude/projects/-home-claude/7b7587cd-449e-5d94-986d-7a2d5c82d9a5/tool-results/mcp-remote-devices-Claude_Browser__javascript_tool-1792353621605.txt'))[0]['text']
i = gl.find('\n\n(captured'); gl = gl[:i] if i >= 0 else gl
have = set(json.loads(gl)['gl'])
print('espn ids without a game log:', sorted({o['espn'] for o in out if o['espn'] and o['espn'] not in have}))
