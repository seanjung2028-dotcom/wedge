"""Shadow run of the v2 pick rules (brain/rules.py) on Week 11's final-draft board (Sun Nov 22, 10:32 AM CT), graded on Sunday's
results. Week 11 itself stays as posted; this only shows what v2 would have picked. Reads bt/w11_likely/rows.csv (backtest.py).
Writes bt/w11_likely/shadow_v2.csv and shadow_v2.json."""
import json, sys, collections
import pandas as pd
W = '/home/claude/wedger/'
sys.path.insert(0, W + 'brain'); import rules as R
D = pd.read_csv(W + 'bt/w11_likely/rows.csv')
# Week 11's backup starters and how many of their team's last 3 games each started (nflverse, most pass attempts)
BACKUP = {'MIA': {'name': 'Kyle McCord', 'recent': 1}, 'MIN': {'name': 'Kirk Cousins', 'recent': 1}, 'ARI': {'name': 'Josh Johnson', 'recent': 0},
          'PHI': {'name': 'Joe Milton III', 'recent': 1}, 'BAL': {'name': 'Jacoby Brissett', 'recent': 1}}
st = pd.read_csv(W + 'dl19/stats_player_week_2026.csv', low_memory=False); st = st[st.week < 11]
TEAM = st.sort_values('week').drop_duplicates('player_display_name', keep='last').set_index('player_display_name').team.to_dict()
FX = {'LA': 'LAR', 'WAS': 'WSH', 'JAC': 'JAX'}
cards, passed = [], []
for game, G in D.groupby('game', sort=False):
    plays = []
    for (player, stat), P in G.groupby(['player', 'stat'], sort=False):
        team = FX.get(TEAM.get(player, ''), TEAM.get(player, '')); bk = BACKUP.get(team)
        rows = []
        for r in P.to_dict('records'):
            r['chk'] = {'ROLE': {'pass': r['role']}, 'SCRIPT': {'pass': r['script']}, 'LATE': {'pass': r['late']}}
            r['call'], r['note'] = R.decide(r, stat, bk)
            if r['research_pass'] and r['call'] != 'Pass': r['call'], r['note'] = 'Pass', 'Research pass (hand research defeated it).'
            rows.append(r)
        fin = [r for r in rows if r['call'] == 'Final line']; lea = [r for r in rows if r['call'] == 'Conditional lean']
        pick = max(fin, key=R.key) if fin else (max(lea, key=R.key) if lea else None)
        if pick: plays.append({**pick, 'decision': pick['call']}); continue
        # considered and passed: his likeliest rung that reached the bar, and why it stopped
        cand = [r for r in rows if r['mid'] >= R.BAR]
        if not cand: continue
        inside = [r for r in cand if r['ask'] <= R.CAP]
        y = max(inside, key=R.key) if inside else min(cand, key=lambda r: r['ask'])
        why = y['note'] or ('Priced above the cap.' if y['ask'] > R.CAP else '')
        cat = ('Research pass' if 'Research' in why else 'Failed a research check' if 'fails' in why else f'Priced above {R.CAP}¢' if 'cap' in why.lower() else 'Other')
        passed.append({**y, 'why': why, 'cat': cat})
    keep, cut = R.card(plays)
    cards += keep
    for p in cut: passed.append({**p, 'why': 'Fifth line in the game, or a second line on the player.', 'cat': 'Card limit (one per player, four per game)'})
C = pd.DataFrame(cards); P = pd.DataFrame(passed)
C['group'] = C.decision; P['group'] = 'Passed'
A = pd.concat([C, P], ignore_index=True); A['value_read'] = [R.value(r)['v'] for r in A.to_dict('records')]
A[['game', 'group', 'cat', 'line', 'ask', 'lo', 'mid', 'hi', 'value_read', 'why', 'result', 'pl_c']].to_csv(W + 'bt/w11_likely/shadow_v2.csv', index=False)
def s(df):
    g = df[df.result.isin(['Won', 'Lost'])]; w = int((g.result == 'Won').sum())
    return {'n': len(df), 'graded': len(g), 'won': w, 'lost': len(g) - w, 'profit_c': int(g.pl_c.sum()), 'avg_price': round(float(df.ask.mean()), 1) if len(df) else None,
            'avg_ours_mid': round(float(df.mid.mean()), 1) if len(df) else None}
OUT = {'rules': 'v2 (brain/rules.py)', 'board': 'Sun Nov 22, 10:32 AM CT', 'finals': s(C[C.decision == 'Final line']), 'leans': s(C[C.decision == 'Conditional lean']),
       'card': s(C), 'per_game': C.groupby('game').size().to_dict(), 'unders_on_card': int((C.side == 'No').sum()),
       'value_reads_on_card': A[A.group != 'Passed'].value_read.value_counts().to_dict(),
       'passed': {k: s(v) for k, v in P.groupby('cat')}}
json.dump(OUT, open(W + 'bt/w11_likely/shadow_v2.json', 'w'), indent=1); print(json.dumps(OUT, indent=1))
print(C.sort_values(['decision', 'lo'], ascending=[True, False])[['game', 'decision', 'line', 'ask', 'lo', 'mid', 'result', 'pl_c']].to_string(index=False))
