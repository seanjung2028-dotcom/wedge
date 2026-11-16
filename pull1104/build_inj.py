"""Week 9 injury table (Wed Nov 4 ~3:40 PM CT): nflverse official reports for Weeks 1-8 plus the Jaguars/Ravens Week 9
practice report, and ESPN's current statuses (Out / Doubtful / Questionable / IR) for Week 9. Tuesday's long-term IR/Out
rows that ESPN no longer lists stay, unless ESPN now lists the player as active. Writes dl8/injuries_w9.csv and
w9/espn_inj_1104.csv."""
import json, re, unicodedata
import pandas as pd
S = '/home/claude/wedger/'
def nn(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', s); return re.sub(r'[^a-z]', '', s)
nv = pd.read_csv(S + 'dl15/injuries_2026.csv')
cols = list(nv.columns) + ['date_modified']
base = nv[nv['week'] <= 8].copy(); base['date_modified'] = ''
wk9_off = nv[nv['week'] == 9].copy(); wk9_off['date_modified'] = '2026-11-03'
rw = pd.read_csv(S + 'dl8/roster_weekly_2026.csv', low_memory=False)
rw = rw[rw['week'] == rw['week'].max()]
by_espn = {str(int(r.espn_id)): r for r in rw.itertuples(index=False) if not pd.isna(r.espn_id)}
by_name = {(nn(r.full_name), r.team): r for r in rw.itertuples(index=False)}
FIX = {'WSH': 'WAS', 'JAX': 'JAX', 'LAR': 'LA'}
E = json.load(open(S + 'pull1104/espn_inj.json'))
MAP = {'Injured Reserve': 'Out', 'Out': 'Out', 'Doubtful': 'Doubtful', 'Questionable': 'Questionable'}
rows, active_today, miss = [], set(), 0
for team_name, ab, name, pos, status, typ, short, long_, date, _, eid in E['rows']:
    r = by_espn.get(str(eid)) or by_name.get((nn(name), FIX.get(ab, ab)))
    gid = r.gsis_id if r is not None else None
    if status == 'Active':
        if gid: active_today.add(gid)
        continue
    if status not in MAP: continue
    if r is None: miss += 1
    rows.append({'season': 2026, 'season_type': 'REG', 'game_type': 'REG', 'team': (r.team if r is not None else FIX.get(ab, ab)), 'week': 9,
                 'gsis_id': gid or '', 'position': pos, 'full_name': name, 'first_name': name.split(' ')[0], 'last_name': name.split(' ')[-1],
                 'report_primary_injury': '', 'report_secondary_injury': '', 'report_status': MAP[status],
                 'practice_primary_injury': '', 'practice_secondary_injury': '', 'practice_status': '', 'date_modified': date[:10],
                 'espn_status': status, 'espn_comment': short})
new = pd.DataFrame(rows)
tue = pd.read_csv(S + 'w9/espn_inj_1103.csv')
keep = tue[tue['espn_status'].isin(['Injured Reserve', 'Out']) & ~tue['gsis_id'].isin(set(new['gsis_id'])) & ~tue['gsis_id'].isin(active_today)]
espn = pd.concat([new, keep], ignore_index=True)
# official Thursday-game practice participation (Jaguars, Ravens)
prac = {r.gsis_id: r.practice_status for r in wk9_off.itertuples(index=False)}
espn['practice_status'] = espn['gsis_id'].map(prac).fillna('')
extra = wk9_off[~wk9_off['gsis_id'].isin(set(espn['gsis_id']))]
espn.to_csv(S + 'w9/espn_inj_1104.csv', index=False)
out = pd.concat([base[cols], espn[cols], extra[cols]], ignore_index=True)
out.to_csv(S + 'dl8/injuries_w9.csv', index=False)
print('espn rows', len(new), 'kept from Tue', len(keep), 'unmatched', miss, 'practice-only', len(extra), 'total wk9', (out['week'] == 9).sum())
w = out[(out['week'] == 9) & out['position'].isin(['QB', 'RB', 'WR', 'TE']) & out['report_status'].isin(['Out', 'Doubtful'])]
print(w[['team', 'full_name', 'report_status']].to_string())
