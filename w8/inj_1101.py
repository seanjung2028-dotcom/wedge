"""Sun Nov 1: official Friday game designations (nflverse, dl12) + Sunday-morning rulings into dl8/injuries_w8.csv."""
import pandas as pd
S = '/home/claude/wedger/'
old = pd.read_csv(S + 'dl8/injuries_w8_1029.csv')
new = pd.read_csv(S + 'dl12/injuries_2026.csv')
w8n = new[(new['week'] == 8) & ~new['team'].isin(['CAR', 'GB'])].copy(); w8n['date_modified'] = '2026-10-30'
o8 = old[old['week'] == 8].copy(); rest = old[old['week'] != 8]
rep = set(w8n['gsis_id'])
# ESPN-style "Questionable" for players with no official designation -> cleared
m = (~o8['team'].isin(['CAR', 'GB'])) & (~o8['gsis_id'].isin(rep)) & (o8['report_status'] == 'Questionable')
cleared = list(o8.loc[m, 'full_name']); o8.loc[m, 'report_status'] = float('nan')
idx = {g: i for i, g in zip(o8.index, o8['gsis_id'])}
cols = ['report_primary_injury', 'report_secondary_injury', 'report_status', 'practice_primary_injury', 'practice_secondary_injury', 'practice_status', 'date_modified']
add = []
for r in w8n.itertuples(index=False):
    i = idx.get(r.gsis_id)
    if i is None: add.append(r._asdict()); continue
    for c in cols: o8.at[i, c] = getattr(r, c)
o8 = pd.concat([o8, pd.DataFrame(add)], ignore_index=True)
# Sunday-morning rulings (CBS Sports live inactives tracker, Nov 1)
for nm in ('A.J. Brown', 'TreVeyon Henderson'):
    o8.loc[o8['full_name'] == nm, ['report_status', 'date_modified']] = ['Out', '2026-11-01']
o8.loc[o8['full_name'] == 'Dameon Pierce', 'report_status'] = 'Out'
pd.concat([rest, o8], ignore_index=True).to_csv(S + 'dl8/injuries_w8.csv', index=False)
print('cleared ESPN-only questionable:', cleared)
sk = o8[o8['position'].isin(['QB', 'RB', 'WR', 'TE'])]
print(sk['report_status'].value_counts(dropna=False).to_dict())
print(sk[sk['full_name'].isin(['Saquon Barkley', 'Lamar Jackson', 'Jahmyr Gibbs', 'Amon-Ra St. Brown', 'Rashee Rice', 'Aaron Jones', 'Breece Hall', 'A.J. Brown'])][['team', 'full_name', 'report_status', 'practice_status']].to_string())
