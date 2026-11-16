import numpy as np, pandas as pd, runpy, sys
from scipy.optimize import minimize
B='/home/claude/wedger/rh/'
c=pd.read_csv(B+'calib_rows.csv'); c=c[c.wedger.notna()].copy()
lg=lambda p: np.log(np.clip(p,1e-4,1-1e-4)/(1-np.clip(p,1e-4,1-1e-4))); sg=lambda z:1/(1+np.exp(-z))
G={'rushyd':'rush','rryd':'rush','td':'td','passyd':'pass','passtd':'pass','int':'pass'}
c['g']=c.stat.map(lambda s:G.get(s,'rec'))
F={'icpt':np.ones(len(c)),'rush':(c.g=='rush').values*1.,'td':(c.g=='td').values*1.,'pass':(c.g=='pass').values*1.,'thin':(c.n_games<12).values*1.}
off=lg(c.wedger.values); y=c.y.values*1.; wk=c.wk.values
def fit(cols,idx,lam):
    X=np.column_stack([F[k] for k in cols])[idx]
    def nll(b):
        p=sg(off[idx]+X@b); return -np.sum(y[idx]*np.log(p)+(1-y[idx])*np.log(1-p))+lam*np.sum(b[1:]**2)+0.5*lam*b[0]**2
    return minimize(nll,np.zeros(len(cols)),method='BFGS').x
def pr(cols,b,idx): return sg(off[idx]+np.column_stack([F[k] for k in cols])[idx]@b)
br=lambda p,yy: np.mean((p-yy)**2)
A=np.arange(len(c))
for cols in (['icpt','rush','td','pass','thin'],['icpt','rush','td','pass'],['icpt','pass'],['icpt']):
  for lam in (2.,4.,8.):
    lo=[br(pr(cols,fit(cols,A[wk!=w],lam),A[wk==w]),y[wk==w]) for w in (6,7)]
    cv=[]
    for rep in range(10):
        perm=np.random.default_rng(rep).permutation(len(c)); P=np.zeros(len(c))
        for f in np.array_split(perm,5): P[f]=pr(cols,fit(cols,np.setdiff1d(A,f),lam),f)
        cv.append(br(P,y))
    b=fit(cols,A,lam)
    print('%-28s lam %.0f  LOWO W6 %.4f W7 %.4f avg %.4f  CV %.4f  coef %s'%('+'.join(cols),lam,lo[0],lo[1],np.mean(lo),np.mean(cv),dict(zip(cols,np.round(b,3)))))
v1=sg(off); print('v1 W6 %.4f W7 %.4f avg %.4f'%(br(v1[wk==6],y[wk==6]),br(v1[wk==7],y[wk==7]),(br(v1[wk==6],y[wk==6])+br(v1[wk==7],y[wk==7]))/2))
pz=c.price.values; print('price W6 %.4f W7 %.4f'%(br(pz[wk==6],y[wk==6]),br(pz[wk==7],y[wk==7])))
