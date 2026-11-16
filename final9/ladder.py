import sys, re, pandas as pd
S = '/home/claude/wedger/'
LA = pd.read_csv(S + 'rh/lines_all_w9.csv', low_memory=False)
MAP = {'LA': 'LAR', 'WAS': 'WSH'}
SH = {'Receiving Yards': 'recyd', 'Receptions': 'rec', 'Rushing Yards': 'rush', 'Passing Yards': 'pass', 'Rushing + Receiving Yards': 'rry', 'Passing Touchdowns': 'ptd', 'Anytime Touchdown': 'atd', 'Interceptions': 'int', '2+ Touchdowns': '2td'}
g = sys.argv[1]; a, h = g.split('@'); gl = f"{MAP.get(a, a)} @ {MAP.get(h, h)}"
L = LA[(LA.game == gl) & LA.market.isin(SH)].copy()
L['player'] = L.contract.str.split(':').str[0]
L['ln'] = L.contract.str.extract(r'Over ([\d.]+)')[0].astype(float)
for n in sys.argv[2:]:
    x = L[L.player.str.contains(n, case=False, na=False)]
    for (p, m), d in x.groupby(['player', 'market']):
        d = d[(d.yes_price >= 15) & (d.yes_price <= 88)].sort_values('ln')
        if d.empty: continue
        print(f"{p} {SH[m]}: " + ' | '.join(f"{'' if pd.isna(r.ln) else format(r.ln, 'g')} {r.source[0]}Y{r.yes_price:.0f}/N{'' if pd.isna(r.no_price) else int(r.no_price)} f{'' if pd.isna(r.book_fair) else round(r.book_fair)} h{'' if pd.isna(r.hits) else int(r.hits)}/{'' if pd.isna(r.games) else int(r.games)}" for r in d.itertuples()))
