import json, pandas as pd
B='/home/claude/wedger/final9/'
PL=json.load(open(B+'plays.json')); FR=json.load(open(B+'fresh.json')); Q={m[0]:m for m in FR['m']}
LA=pd.read_csv('/home/claude/wedger/rh/lines_all_w9.csv', low_memory=False)
# evidence adjustments (points), one per play in plays.json order
ADJ=[5,4,4,5,6,4,5,5,4,3,4,5,3,5,5,4,6,5,3,5,4,5,6,2]
MAP={'LA':'LAR','WAS':'WSH'}; STAT={'pass':'Passing Yards','recyd':'Receiving Yards','rec':'Receptions','rush':'Rushing Yards'}
out=[]
for x,adj in zip(PL,ADJ):
    a,h=x['game'].split('@'); gl=f"{MAP.get(a,a)} @ {MAP.get(h,h)}"
    L=LA[(LA.game==gl)&(LA.market==STAT[x['stat']])&LA.contract.str.contains(x['player'].split(' ')[-1],na=False)&LA.contract.str.contains(f"Over {x['line']}",regex=False,na=False)]
    r=L.iloc[0]; fair=r.book_fair; wedge=r.sit_hit; q=Q[x['ticker']]
    price=round(100*float(q[1] if x['side']=='Y' else q[3])); bf=fair if x['side']=='Y' else 100-fair; wd=wedge if x['side']=='Y' else 100-wedge
    base=(bf+wd)/2; mid=base+adj; lo,hi=round(mid-5),round(mid+5); be=price+2
    dec='Final' if lo>=be else ('Lean' if mid>=be else 'Pass')
    out.append((x['game'],x['sub'],x['side'],price,be,round(bf,1),round(wd,1),round(base,1),adj,lo,hi,round(mid-be,1),dec))
json.dump(out,open(B+'est.json','w'))
for o in out: print(o)
