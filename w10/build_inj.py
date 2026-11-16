"""Week 10 injury table (Mon Nov 16 ~9:28 AM CT): nflverse official reports for Weeks 1-9 and ESPN's current statuses
(Out / Doubtful / Questionable / IR) for Week 10. Writes dl18/injuries_w10.csv and w10/espn_inj_1116.csv."""
import json, re, unicodedata
import pandas as pd
S = '/home/claude/wedger/'
def nn(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', s); return re.sub(r'[^a-z]', '', s)
NICK = {'Cardinals': 'ARI', 'Falcons': 'ATL', 'Ravens': 'BAL', 'Bills': 'BUF', 'Panthers': 'CAR', 'Bears': 'CHI', 'Bengals': 'CIN', 'Browns': 'CLE',
        'Cowboys': 'DAL', 'Broncos': 'DEN', 'Lions': 'DET', 'Packers': 'GB', 'Texans': 'HOU', 'Colts': 'IND', 'Jaguars': 'JAX', 'Chiefs': 'KC',
        'Raiders': 'LV', 'Chargers': 'LAC', 'Rams': 'LA', 'Dolphins': 'MIA', 'Vikings': 'MIN', 'Patriots': 'NE', 'Saints': 'NO', 'Giants': 'NYG',
        'Jets': 'NYJ', 'Eagles': 'PHI', 'Steelers': 'PIT', '49ers': 'SF', 'Seahawks': 'SEA', 'Buccaneers': 'TB', 'Titans': 'TEN', 'Commanders': 'WAS'}
nv = pd.read_csv(S + 'dl18/injuries_2026.csv')
cols = list(nv.columns) + ['date_modified']
base = nv[nv['week'] <= 9].copy(); base['date_modified'] = ''
rw = pd.read_csv(S + 'dl18/roster_weekly_2026.csv', low_memory=False); rw = rw[rw['week'] == rw['week'].max()]
by_name = {(nn(r.full_name), r.team): r for r in rw.itertuples(index=False)}
by_name1 = {}
for r in rw.itertuples(index=False): by_name1.setdefault(nn(r.full_name), r)
E = json.load(open(S + 'pull1116/espn_inj_w10.json'))
MAP = {'Injured Reserve': 'Out', 'Out': 'Out', 'Doubtful': 'Doubtful', 'Questionable': 'Questionable'}
rows, miss = [], 0
for line in E['rows']:
    team_name, name, pos, status, typ, ret, short, date = line.split('|')
    ab = NICK.get(team_name.split(' ')[-1], '')
    if status not in MAP: continue
    r = by_name.get((nn(name), ab)) or by_name1.get(nn(name))
    if r is None: miss += 1
    rows.append({'season': 2026, 'season_type': 'REG', 'game_type': 'REG', 'team': (r.team if r is not None else ab), 'week': 10,
                 'gsis_id': (r.gsis_id if r is not None else ''), 'position': pos, 'full_name': name, 'first_name': name.split(' ')[0], 'last_name': name.split(' ')[-1],
                 'report_primary_injury': typ, 'report_secondary_injury': '', 'report_status': MAP[status],
                 'practice_primary_injury': '', 'practice_secondary_injury': '', 'practice_status': '', 'date_modified': (date or '')[:10],
                 'espn_status': status, 'espn_comment': short})
espn = pd.DataFrame(rows); espn.to_csv(S + 'w10/espn_inj_1116.csv', index=False)
out = pd.concat([base[cols], espn[cols]], ignore_index=True); out.to_csv(S + 'dl18/injuries_w10.csv', index=False)
print('espn rows', len(espn), 'unmatched', miss, 'total wk10', (out['week'] == 10).sum())
w = out[(out['week'] == 10) & out['position'].isin(['QB', 'RB', 'WR', 'TE']) & out['report_status'].isin(['Out', 'Doubtful'])]
print(len(w)); print(w[['team', 'full_name', 'position', 'report_status']].head(40).to_string())
