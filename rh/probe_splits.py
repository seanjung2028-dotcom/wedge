import sys, json
sys.argv.append('probe')
exec(open('w7_splits.py').read())
print('FORCE_OUT', [disp.get(g) for g in FORCE_OUT])
for player, game, market, line in [('Luther Burden III','NE @ CHI','Receiving Yards',59.5),('Puka Nacua','LAR @ ?','Receiving Yards',None)]:
    pass
import csv
rows = list(csv.DictReader(open(B+'inband_w7.csv'))) + list(csv.DictReader(open(B+'props_cat_w7.csv')))
for r in rows:
    if any(k in r['contract'] for k in ('Burden','Nacua')):
        print(r['game'], r['market'], r['contract'], r.get('yes_price'))
