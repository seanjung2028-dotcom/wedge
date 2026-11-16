import sys, pandas as pd
L = pd.read_csv('/home/claude/wedger/final9/logs.csv', low_memory=False)
for n in sys.argv[1:]:
    d = L[L.name.fillna('').str.contains(n, case=False)].sort_values(['season', 'week'])
    if d.empty: print('no', n); continue
    print(f"== {d.name.iloc[0]} ({d.pos.iloc[0]})")
    for r in d.itertuples():
        s = f"{r.season%100}w{int(r.week):<2} {r.posteam}-{r.opp:<3} {int(r.pf):>2}-{int(r.pa):<2} tA{int(r.team_att or 0):>2} tR{int(r.team_rush or 0):>2} qb {' '.join(str(r.qb).split(' ')[1:2])[:9]:9s}"
        if r.db > 0: s += f" | {int(r.cmp)}/{int(r.att)} {int(r.pyd)}y {int(r.ptd)}td {int(r.ints)}i sk{int(r.sk)}"
        if r.car > 0: s += f" | car {int(r.car)}-{int(r.rushyd)} scr{int(r.scr)}"
        if r.tgt > 0: s += f" | {int(r.rec)}/{int(r.tgt)}-{int(r.recyd)} ts{100*r.tgt/max(1,r.team_tgt):.0f}%"
        if r.td > 0: s += f" TD{int(r.td)}"
        print('  ' + s)
