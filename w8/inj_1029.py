"""Thu Oct 29: merge the official Wednesday practice report (nflverse, dl11) for Sunday/Monday teams into dl8/injuries_w8.csv."""
import pandas as pd
S = '/home/claude/wedger/'
old = pd.read_csv(S + 'dl8/injuries_w8_1028.csv')
new = pd.read_csv(S + 'dl11/injuries_2026.csv')
w8n = new[(new['week'] == 8) & ~new['team'].isin(['CAR', 'GB'])].copy()
w8n['date_modified'] = '2026-10-29'
o8 = old[old['week'] == 8].copy(); rest = old[old['week'] != 8]
idx = {g: i for i, g in zip(o8.index, o8['gsis_id'])}
added = upd = cleared = 0
for r in w8n.itertuples(index=False):
    i = idx.get(r.gsis_id)
    if i is None:
        o8 = pd.concat([o8, pd.DataFrame([r._asdict()])], ignore_index=False); added += 1; continue
    for c in ('practice_primary_injury', 'practice_secondary_injury', 'practice_status'):
        o8.at[i, c] = getattr(r, c)
    if not isinstance(o8.at[i, 'report_primary_injury'], str) and isinstance(r.practice_primary_injury, str):
        o8.at[i, 'report_primary_injury'] = r.practice_primary_injury
    o8.at[i, 'date_modified'] = '2026-10-29'; upd += 1
    # listed Out on ESPN earlier in the week but on the field Wednesday -> no longer treated as Out
    if o8.at[i, 'report_status'] == 'Out' and r.practice_status in ('Full Participation in Practice', 'Limited Participation in Practice'):
        o8.at[i, 'report_status'] = float('nan'); cleared += 1
# Dameon Pierce went to injured reserve
o8.loc[o8['full_name'] == 'Dameon Pierce', 'report_status'] = 'Out'
out = pd.concat([rest, o8], ignore_index=True)
out.to_csv(S + 'dl8/injuries_w8.csv', index=False)
print('week 8 rows', len(o8), 'added', added, 'updated', upd, 'Out cleared (practicing)', cleared)
print(o8[o8['full_name'].isin(['Beaux Collins', 'Tyrell Shavers', 'Ben Skowronek', 'Jack Bech', 'Carter Runyon', 'Dameon Pierce'])][['team', 'full_name', 'report_status', 'practice_status']].to_string())
