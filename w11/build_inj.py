"""Week 11 injury table (Tue Nov 17 ~6:24 AM CT): nflverse official reports for Weeks 1-10 and ESPN's current statuses
(Out / Doubtful / Questionable / IR) for Week 11. Writes dl18/injuries_w11.csv and w11/espn_inj_1117.csv."""
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
base = nv[nv['week'] <= 10].copy(); base['date_modified'] = ''
rw = pd.read_csv(S + 'dl18/roster_weekly_2026.csv', low_memory=False); rw = rw[rw['week'] == rw['week'].max()]
by_name = {(nn(r.full_name), r.team): r for r in rw.itertuples(index=False)}
by_name1 = {}
for r in rw.itertuples(index=False): by_name1.setdefault(nn(r.full_name), r)
import os
E = json.load(open(S + os.environ.get('W11_INJ', 'pull1117') + '/espn_inj_w11.json'))   # Wed Nov 18 re-pull: W11_INJ=pull1118
MAP = {'Injured Reserve': 'Out', 'Out': 'Out', 'Doubtful': 'Doubtful', 'Questionable': 'Questionable'}
rows, miss = [], 0
for line in E['rows']:
    team_name, name, pos, status, typ, ret, short, date = line.split('|')
    ab = NICK.get(team_name.split(' ')[-1], '')
    if status not in MAP: continue
    # Fri Nov 20: a player on IR whose return window is open shows "Injured Reserve" on ESPN even when the team lists him for the game;
    # ESPN's own note says so ("is listed as questionable for Sunday's game"), and Kalshi lists his ladders. Use the game designation.
    if status == 'Injured Reserve' and (date or '') >= '2026-11-19':
        if re.search(r'\bquestionable\b', short, re.I): status = 'Questionable'
        elif re.search(r'\bdoubtful\b', short, re.I): status = 'Doubtful'
    r = by_name.get((nn(name), ab)) or by_name1.get(nn(name))
    if r is None: miss += 1
    rows.append({'season': 2026, 'season_type': 'REG', 'game_type': 'REG', 'team': (r.team if r is not None else ab), 'week': 11,
                 'gsis_id': (r.gsis_id if r is not None else ''), 'position': pos, 'full_name': name, 'first_name': name.split(' ')[0], 'last_name': name.split(' ')[-1],
                 'report_primary_injury': typ, 'report_secondary_injury': '', 'report_status': MAP[status],
                 'practice_primary_injury': '', 'practice_secondary_injury': '', 'practice_status': '', 'date_modified': (date or '')[:10],
                 'espn_status': status, 'espn_comment': short})
espn = pd.DataFrame(rows); espn.to_csv(S + 'w11/espn_inj_1117.csv', index=False)
out = pd.concat([base[cols], espn[cols]], ignore_index=True); out.to_csv(S + 'dl18/injuries_w11.csv', index=False)
print('espn rows', len(espn), 'unmatched', miss, 'total wk10', (out['week'] == 11).sum())
w = out[(out['week'] == 11) & out['position'].isin(['QB', 'RB', 'WR', 'TE']) & out['report_status'].isin(['Out', 'Doubtful'])]
print(len(w)); print(w[['team', 'full_name', 'position', 'report_status']].head(40).to_string())
