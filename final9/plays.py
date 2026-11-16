import json, glob, re
K = json.load(open('/home/claude/wedger/final9/../rh/kalshi_props_w9.json'))
SER = {'pass': 'KXNFLPASSYDS', 'recyd': 'KXNFLRECYDS', 'rec': 'KXNFLREC', 'rush': 'KXNFLRSHYDS'}
P = [('CIN@ATL','Joe Burrow','pass',274.5,'Y'),('CIN@ATL','Tee Higgins','recyd',74.5,'Y'),('NYG@PHI','Dallas Goedert','rec',3.5,'Y'),('NYG@PHI','Malik Nabers','rec',5.5,'Y'),
 ('DEN@CAR','Bryce Young','pass',224.5,'N'),('DEN@CAR','Chuba Hubbard','rec',2.5,'Y'),('DET@MIA','Ollie Gordon','rush',69.5,'N'),('DET@MIA','Greg Dulcich','rec',3.5,'Y'),
 ('NYJ@KC','Braelon Allen','rush',39.5,'N'),('CLE@NO','Harold Fannin','rec',4.5,'Y'),('LA@WAS','Jayden Daniels','rush',39.5,'N'),('LA@WAS','Puka Nacua','rec',7.5,'Y'),
 ('DAL@IND','CeeDee Lamb','rec',6.5,'Y'),('HOU@LAC','Justin Herbert','rush',24.5,'N'),('LV@SF','George Kittle','rec',5.5,'Y'),('LV@SF','Ashton Jeanty','recyd',39.5,'Y'),
 ('ARI@SEA','Smith-Njigba','recyd',99.5,'Y'),('ARI@SEA','Trey McBride','recyd',59.5,'N'),('ARI@SEA','Tyler Allgeier','rush',49.5,'N'),('GB@NE','Matthew Golden','rec',5.5,'Y'),
 ('TB@CHI','Bucky Irving','rush',59.5,'N'),('TB@CHI','Caleb Williams','rush',19.5,'N'),('TB@CHI','Colston Loveland','rec',5.5,'Y'),('BUF@MIN','Josh Allen','rush',29.5,'N')]
AB = {'LA': 'LA', 'WAS': 'WAS'}
out = []
for g, nm, st, ln, side in P:
    a, h = g.split('@'); code = a + h
    rows = [r for r in K['series'][SER[st]] if code in r[0] and nm.split(' ')[-1].lower() in r[2].lower() and abs(float(r[3]) - ln) < 0.01]
    if len(rows) != 1:
        rows2 = [r for r in K['series'][SER[st]] if nm.split(' ')[-1].lower() in r[2].lower() and abs(float(r[3]) - ln) < 0.01]
        print('??', g, nm, st, ln, len(rows), [r[:4] for r in rows2][:4]); rows = rows or rows2
    r = rows[0]; out.append({'game': g, 'player': nm, 'stat': st, 'line': ln, 'side': side, 'ticker': r[1], 'sub': r[2], 'ya': r[4], 'yb': r[5], 'na': r[6]})
json.dump(out, open('/home/claude/wedger/final9/plays.json', 'w'), indent=0)
for o in out: print(o['game'], o['sub'], o['side'], o['ticker'], o['ya'], o['yb'], o['na'])
print(','.join(o['ticker'] for o in out))
