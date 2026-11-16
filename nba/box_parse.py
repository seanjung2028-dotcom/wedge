"""Parse ESPN summary transcriptions (box1023/*.txt) into nba_box_extra.json; checks that player points sum to the team score."""
import json, glob, os, sys
D = '/home/claude/wedger/nba/'
FIX = {'GS': 'GSW', 'NY': 'NYK', 'SA': 'SAS', 'NO': 'NOP', 'UTAH': 'UTA', 'WSH': 'WAS', 'PHO': 'PHX'}
fx = lambda t: FIX.get(t, t)
games = []
for f in sorted(glob.glob(D + 'box*/*.txt')):
    date = {'box1023': '2026-10-23'}[os.path.basename(os.path.dirname(f))]
    st, teams, pl, tt = None, {}, {}, {}
    for ln in open(f):
        p = [x.strip() for x in ln.strip().split('|')]
        if p[0] == 'STATUS': st = p
        elif p[0] == 'TEAM': teams[p[2]] = {'abbr': fx(p[1]), 'score': int(p[3]), 'players': []}
        elif p[0] == 'T':
            fg, tp, ft = [list(map(int, x.split('-'))) for x in p[2:5]]
            tt.setdefault(fx(p[1]), {'fga': fg[1], '3pa': tp[1], 'fta': ft[1], 'oreb': int(p[5]), 'reb': int(p[6]), 'ast': int(p[7]), 'tov': int(p[8]), 'tpm': tp[0]})
        elif p[0] == 'P':
            t = fx(p[1]); dnp = p[-1] == 'true'
            nums = p[3:8] if len(p) >= 9 else ['', '', '', '', '']
            iv = lambda x: int(x) if x not in ('', '--') else 0
            mn = iv(nums[0]) if not dnp else 0
            pl.setdefault(t, []).append({'name': p[2], 'min': mn, 'pts': 0 if dnp else iv(nums[1]), 'reb': 0 if dnp else iv(nums[2]),
                                         'ast': 0 if dnp else iv(nums[3]), '3pm': 0 if dnp else iv(nums[4]), 'dnp': dnp or mn == 0})
    final = st[1] == 'STATUS_FINAL'
    for side in teams.values():
        side['players'] = pl.get(side['abbr'], []); side['totals'] = tt.get(side['abbr'])
        for i, x in enumerate(side['players']): x['starter'] = i < 5
        s = sum(x['pts'] for x in side['players'])
        if s != side['score']: print('SUM MISMATCH', f, side['abbr'], s, side['score'])
        if side['totals']:
            for k, tk in (('3pm', 'tpm'), ('reb', 'reb'), ('ast', 'ast')):
                s2 = sum(x[k] for x in side['players'])
                if s2 != side['totals'][tk]: print('TOTAL MISMATCH', f, side['abbr'], k, s2, side['totals'][tk])
    games.append({'date': date, 'event': os.path.basename(f)[:-4], 'final': final, 'away': teams['away'], 'home': teams['home']})
    print(date, teams['away']['abbr'], teams['away']['score'], '@', teams['home']['abbr'], teams['home']['score'], 'final' if final else st[3])
json.dump({'games': games}, open(D + 'nba_box_extra.json', 'w'))
