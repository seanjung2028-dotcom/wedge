"""Pick log Nov 8-12 (user's payout-ladder log) -> rows for the results file + certified keys.
Every outcome re-checked against nflverse box scores / play-by-play (dl19). Picks that match a line already
on the posted board reuse that row's key (no duplicate row); the rest become 'Other Wedge picks' rows priced at 100 / payout."""
import csv, json, pandas as pd
W = '/home/claude/wedger/'
# (week, game, market, player/team, side, k, payout, stat, verify-name, log actual)
P = [(9, 'CIN @ ATL', 'Receptions', 'Tee Higgins', 'Over', 5, 1.50, 'receptions', 'Tee Higgins'),
     (9, 'CIN @ ATL', 'Receiving Yards', 'Drake London', 'Over', 60, 1.43, 'receiving_yards', 'Drake London'),
     (9, 'CIN @ ATL', 'Rushing Yards', 'Bijan Robinson', 'Over', 80, 1.50, 'rushing_yards', 'Bijan Robinson'),
     (9, 'DEN @ CAR', 'Pass Attempts', 'Bo Nix', 'Under', 38, 1.27, 'attempts', 'Bo Nix'),
     (9, 'DEN @ CAR', 'Team Sacks', 'Denver', 'Over', 3, 1.27, 'sacks:DEN', None),
     (9, 'DEN @ CAR', 'Rushing Yards', 'Jonah Coleman', 'Over', 40, 1.47, 'rushing_yards', 'Jonah Coleman'),
     (9, 'DAL @ IND', 'Receptions', 'Keenan Allen', 'Over', 5, 1.89, 'receptions', 'Keenan Allen'),
     (9, 'DAL @ IND', 'Receptions', 'CeeDee Lamb', 'Over', 7, 1.96, 'receptions', 'CeeDee Lamb'),
     (9, 'DAL @ IND', 'Carries', 'Javonte Williams', 'Over', 18, 1.96, 'carries', 'Javonte Williams'),
     (9, 'CLE @ NO', 'Team Sacks', 'New Orleans', 'Over', 4, 2.17, 'sacks:NO', None),
     (9, 'CLE @ NO', 'Receptions', 'Chris Olave', 'Over', 6, 1.89, 'receptions', 'Chris Olave'),
     (9, 'CLE @ NO', 'Carries', 'Quinshon Judkins', 'Over', 17, 2.00, 'carries', 'Quinshon Judkins'),
     (9, 'BUF @ MIN', 'Receptions', 'Khalil Shakir', 'Over', 3, 1.26, 'receptions', 'Khalil Shakir'),
     (9, 'BUF @ MIN', 'Rushing Yards', 'James Cook', 'Over', 70, 1.49, 'rushing_yards', 'James Cook'),
     (9, 'BUF @ MIN', 'Pass Attempts', 'Josh Allen', 'Under', 36, 1.26, 'attempts', 'Josh Allen'),
     (10, 'WSH @ NYG', 'Receptions', 'Malik Nabers', 'Over', 5, 1.49, 'receptions', 'Malik Nabers'),
     (10, 'WSH @ NYG', 'Receptions', 'Antonio Williams', 'Over', 3, 1.38, 'receptions', 'Antonio Williams'),
     (10, 'WSH @ NYG', 'Receptions', 'Malachi Fields', 'Over', 2, 1.52, 'receptions', 'Malachi Fields'),
     (10, 'WSH @ NYG', 'Carries', 'Cam Skattebo', 'Over', 14, 1.43, 'carries', 'Cam Skattebo')]
UNIT = {'Receptions': 'Receptions', 'Receiving Yards': 'Receiving Yards', 'Rushing Yards': 'Rush Yards', 'Pass Attempts': 'Pass Attempts', 'Team Sacks': 'Sacks', 'Carries': 'Carries'}
st = pd.read_csv(W + 'dl19/stats_player_week_2026.csv', low_memory=False)
pbp = pd.read_csv(W + 'dl19/play_by_play_2026.csv.gz', low_memory=False, usecols=['week', 'defteam', 'sack'])
R = list(csv.DictReader(open(W + 'rh/results_w6_w9.csv'))) + list(csv.DictReader(open(W + 'bt/w10_settled.csv'))) if False else list(csv.DictReader(open(W + 'rh/results_w6_w10.csv')))
have = {f"w{r['week']}|{r['game']}|{r['market']}|{r['contract']}": r for r in R}
rows, keys, out = [], [], []
for i, (wk, game, mkt, who, side, k, pay, stat, nm) in enumerate(P):
    if stat.startswith('sacks:'):
        actual = int(((pbp.week == wk) & (pbp.defteam == stat[6:]) & (pbp.sack == 1)).sum())
    else:
        s = st[(st.week == wk) & (st.player_display_name == nm)]; actual = int(s.iloc[0][stat])
    hit = actual >= k if side == 'Over' else actual < k
    line = k - 0.5
    contract = f"{who}: {side} {line:g} {UNIT[mkt]}"
    key = f"w{wk}|{game}|{mkt}|{contract}"
    price = round(100 / pay)
    if key in have:
        r0 = have[key]; ok = (r0['outcome'] == ('Won' if hit else 'Lost'))
        out.append((key, actual, 'Won' if hit else 'Lost', 'on board', r0['yes_price'], ok)); keys.append(key); continue
    rows.append({'id': f'PL{len(rows) + 1:03d}', 'game': game, 'market': mkt, 'group': 'Other Wedge picks', 'contract': contract, 'yes_price': price,
                 'hit_rate': '', 'hit_bucket': '', 'qualifies': '', 'flagged': 'No', 'cat': 'Pick log Nov 8–12', 'outcome': 'Won' if hit else 'Lost',
                 'profit_c': (100 - price) if hit else -price, 'week6_result': f'W{wk}:{actual}', 'week': wk})
    keys.append(key); out.append((key, actual, 'Won' if hit else 'Lost', f'new row {pay}x={price}c', price, True))
for o in out: print(o)
print(len(rows), 'new rows;', sum(o[2] == 'Won' for o in out), '-', sum(o[2] == 'Lost' for o in out))
with open(W + 'picklog/rows_nov8_12.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(R[0].keys())); w.writeheader(); w.writerows(rows)
json.dump(keys, open(W + 'picklog/keys_nov8_12.json', 'w'), indent=1)
