import sys, pandas as pd
L = pd.read_csv('/home/claude/wedger/final9/logs.csv', low_memory=False); L = L[L.season == 2026]
t = sys.argv[1]; kinds = sys.argv[2:] or ['QB', 'RB', 'WR', 'TE']
d = L[L.opp == t].sort_values('week')
for w, g in d.groupby('week'):
    tm = g.posteam.iloc[0]; s = f"w{int(w)} {tm} {int(g.pf.iloc[0])}-{int(g.pa.iloc[0])} tA{int(g.team_att.iloc[0] or 0)} tR{int(g.team_rush.iloc[0] or 0)}:"
    q = g[g.db > 0].sort_values('db', ascending=False).head(1)
    if 'QB' in kinds and len(q): r = q.iloc[0]; s += f" QB {r['name']} {int(r.cmp)}/{int(r.att)} {int(r.pyd)}y{' run ' + str(int(r.car)) + '-' + str(int(r.rushyd)) if r.car else ''} |"
    if 'RB' in kinds:
        for r in g[(g.pos == 'RB') & (g.car >= 5)].sort_values('car', ascending=False).head(2).itertuples(): s += f" {r.name.split(' ')[-1]} {int(r.car)}-{int(r.rushyd)} {int(r.rec)}r |"
    for k in ('WR', 'TE'):
        if k in kinds:
            for r in g[(g.pos == k) & (g.tgt >= 3)].sort_values('recyd', ascending=False).head(3 if k == 'WR' else 1).itertuples(): s += f" {k}{r.name.split(' ')[-1]} {int(r.rec)}/{int(r.tgt)}-{int(r.recyd)}"
    print(s)
