"""Keep Wedger-certified Week 7 picks whose line moved in a refresh: re-add the row as certified (old line and price)
and flag where the line is now. Also keeps analyst picks. Run after w7_categorize / w7_atd2, before w7_splits."""
import csv, json
B = '/home/claude/wedger/rh/'
keys = [k for k in json.load(open(B + 'certs_live.json'))['picks'] if k.startswith('w10|')]
an = json.load(open(B + 'analysts_live.json')) if __import__('os').path.exists(B + 'analysts_live.json') else {'picks': {}}
keys += [k for v in an['picks'].values() for k in v if k.startswith('w10|') and k not in keys]
cur = json.load(open(B + 'rows_w10.json'))
def now_line(game, market, player):
    c = [x for x in cur if x['game'] == game and x['market'] == market and x['contract'].split(':')[0] == player]
    return '; '.join(f"{x['contract'].split(': ', 1)[1] if ': ' in x['contract'] else x['contract']} at {round(100 * float(x['yes_ask']))}¢" for x in c) or 'off the board'
for new, olds_f, kind in (('inband_w10.csv', [], 'lines'), ('props_cat_w10.csv', [], 'lines'), ('atd_w10.csv', [], 'atd')):
    rows = list(csv.DictReader(open(B + new))); cols = list(rows[0].keys())
    kf = (lambda r: f"w10|{r['game']}|Anytime Touchdown|{r['player']}") if kind == 'atd' else (lambda r: f"w10|{r['game']}|{r['market']}|{r['contract']}")
    have = {kf(r) for r in rows}
    olds = {}
    for old in reversed(olds_f):
        olds.update({kf(r): r for r in csv.DictReader(open(B + old))})
    added = 0
    for k in keys:
        if k in have or k not in olds: continue
        r = dict(olds[k])
        g, m, c = k.split('|')[1:]
        note = f"Picked at this line; line moved (now {now_line(g, m, c.split(':')[0])})"
        r['flags'] = '; '.join(filter(None, [r.get('flags', ''), note])); r['id'] = 'C' + r['id'].lstrip('C')
        for col in cols: r.setdefault(col, '')
        rows.append({c2: r.get(c2, '') for c2 in cols}); added += 1
        print(new, 'kept', k, '->', note)
    with open(B + new, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
