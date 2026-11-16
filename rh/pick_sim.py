import numpy as np, pandas as pd
from scipy.optimize import minimize
B='/home/claude/wedger/rh/'
c=pd.read_csv(B+'calib_rows.csv'); c=c[c.wedger.notna()].copy()
lg=lambda p: np.log(np.clip(p,1e-4,1-1e-4)/(1-np.clip(p,1e-4,1-1e-4))); sg=lambda z:1/(1+np.exp(-z))
G={'rushyd':'rush','rryd':'rush','td':'td','passyd':'pass','passtd':'pass','int':'pass'}
c['g']=c.stat.map(lambda s:G.get(s,'rec'))
def fit(d,lam=4.):
    X=np.column_stack([np.ones(len(d)),d.g=='rush',d.g=='td',d.g=='pass']).astype(float); o=lg(d.wedger.values); y=d.y.values*1.
    f=lambda b: -np.sum(y*np.log(sg(o+X@b))+(1-y)*np.log(1-sg(o+X@b)))+lam*np.sum(b[1:]**2)+0.5*lam*b[0]**2
    return minimize(f,np.zeros(4),method='BFGS').x
bW6=fit(c[c.wk==6]); bAll=fit(c)
print('W6-only', np.round(bW6,3), 'all', np.round(bAll,3))
L=pd.read_csv(B+'live_eval_w7_rows.csv')
GM={'Rushing / R+R':'rush','Anytime TD':'td','Passing':'pass','Receiving':'rec'}
L['g']=L.grp.map(GM); L=L[(L.src=='Robinhood')&L.no_ask.notna()].copy()
def P(b): X=np.column_stack([np.ones(len(L)),L.g=='rush',L.g=='td',L.g=='pass']).astype(float); return 100*sg(lg(L.v1.values/100)+X@b)
def rec(p, ty=3, tn=3):
    ey=p-L.price.values; en=(100-p)-L.no_ask.values
    side=np.where(ey>=ty,'Yes',np.where(en>=tn,'No',''))
    out={}
    for s in ('Yes','No'):
        m=side==s; y=L.y.values[m]
        cost=np.where(s=='Yes',L.price.values[m],L.no_ask.values[m]); win=(y==1) if s=='Yes' else (y==0)
        prof=np.where(win,100-cost,-cost); out[s]=(int(m.sum()),int(win.sum()),round(100*prof.sum()/max(cost.sum(),1),1))
    m=side!=''; y=L.y.values[m]; s_=side[m]
    cost=np.where(s_=='Yes',L.price.values[m],L.no_ask.values[m]); win=np.where(s_=='Yes',y==1,y==0); prof=np.where(win,100-cost,-cost)
    out['all']=(int(m.sum()),int(win.sum()),round(100*prof.sum()/max(cost.sum(),1),1),int(prof.sum()))
    return out
print('posted v2 (actual)', rec(L.v2.values))
print('v1', rec(L.v1.values))
for nm,b in (('v2.1 trained W6 only (out of sample)',bW6),('v2.1 trained W6+W7 (in sample)',bAll)):
    for ty in (3,5,100):
        print(nm,'yes thr',ty, rec(P(b),ty,3))
br=lambda p: round(float(np.mean((p/100-L.y.values)**2)),4)
print('brier on these', 'price',br(L.price.values),'v1',br(L.v1.values),'v2',br(L.v2.values),'v2.1W6',br(P(bW6)),'v2.1all',br(P(bAll)))
