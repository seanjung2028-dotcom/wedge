"""Data for the two live tools (Line Shopping and the Analyst), written as ES modules the server functions import.

  lib/gen/live.js   Wedge's number for every Kalshi rung on this week's receiving and rushing ladders, as a lens move in
                    log-odds (middle, 10th and 90th percentile), so the server can apply it to the live Kalshi price:
                    p = sigmoid(logit(live mid) + move). Also the card's calls by ticker and each game's teams and kickoff.
                    Paid data: the functions only hand it to callers whose plan includes the card (or anyone while gating is off).
  lib/gen/logs.js   2026 game logs (games before this week) for every player on those ladders, with his team's final margin.
                    Public statistics (nflverse).
Run by v2/build_site.py on every site build."""
import json, math, os, sys, collections
from datetime import datetime, timezone
import pandas as pd
W = '/home/claude/wedger/'
sys.path.insert(0, W + 'lens'); import core, v6
OUT = W + 'lib/gen/'
SER = {'KXNFLREC': 'rec', 'KXNFLRECYDS': 'recyd', 'KXNFLRSHYDS': 'rushyd', 'KXNFLRRYDS': 'rryd'}
FX = {'LA': 'LAR', 'WAS': 'WSH', 'JAC': 'JAX'}; fx = lambda t: FX.get(t, t)
CODE = lambda t: {'JAX': 'JAC', 'WSH': 'WAS'}.get(t, t)
lg = lambda p: math.log(p / (1 - p))


def main():
    WEEK = v6.WEEK
    KP = json.load(open(W + f'rh/kalshi_props_w{WEEK}.json'))
    F = json.load(open(W + f'final{WEEK}/final_w{WEEK}.json'))
    g = pd.read_csv(W + 'dl18/games.csv'); g = g[(g.season == 2026) & (g.game_type == 'REG')]
    T, ST = v6.tables(WEEK)
    # games this week and next, by Kalshi's event code (away + home), with the kickoff in UTC
    games = {}
    for r in g[g.week.isin([WEEK, WEEK + 1])].itertuples(index=False):
        a, h = fx(r.away_team), fx(r.home_team)
        ko = pd.Timestamp(f'{r.gameday} {r.gametime}', tz='America/New_York').tz_convert('UTC').strftime('%Y-%m-%dT%H:%M:%SZ') if isinstance(r.gametime, str) else ''
        dc = pd.Timestamp(r.gameday).strftime('%y%b%d').upper()   # Kalshi's event date: the game's local (ET) date, e.g. 26NOV19
        games[CODE(a) + CODE(h)] = {'g': f'{a} @ {h}', 'a': a, 'h': h, 'ko': ko, 'wk': int(r.week), 'dc': dc}
    # injury designations at the time of the card
    inj = {}
    p_inj = W + 'w11/espn_inj_1117.csv'
    if os.path.exists(p_inj):
        for r in pd.read_csv(p_inj).itertuples(index=False):
            inj[(core.nn(r.full_name), fx(r.team))] = r.report_status
    lad = collections.defaultdict(list)
    for ser, rows in KP['series'].items():
        stat = SER.get(ser)
        if not stat: continue
        for ev, tick, sub, strike, ya, yb, na, last, vol, st_ in rows:
            code = ev.split('-')[1][7:]
            lad[(code, sub.split(':')[0].strip(), stat)].append((int(strike + 0.5), 100 * float(ya), 100 * float(yb), tick))
    lens, players = {}, {}
    for (code, name, stat), rungs in lad.items():
        if code not in games: continue
        a, h = games[code]['a'], games[code]['h']
        pid = team = None
        for tm in (a, h):
            p_ = v6.pid_of(name, tm)
            if p_ is not None:
                s_ = ST[ST.player_id == p_].sort_values('week'); team = s_.team.iloc[-1] if len(s_) else tm
                if team in (a, h): pid = p_; break
        if pid is None: continue
        opp = h if team == a else a
        players[core.nn(name)] = (pid, name, team)
        for k, ya, yb, tick in sorted(set(rungs)):
            if ya <= 0: continue
            mid = (ya + yb) / 2 if yb > 0 else max(ya - 1, 0.5)
            mid = min(max(mid, 1.0), 99.0)
            d = v6.detail(name, team, opp, stat, k - 0.5, mid)
            if not d['moved']: continue
            m0 = lg(mid / 100)
            mv = lambda q: round(lg(min(max(q / 100, 0.001), 0.999)) - m0, 4)
            top = sorted(d['contrib'].items(), key=lambda kv: -abs(kv[1]))[:3]
            lens[tick] = {'m': mv(d['p']), 'ml': mv(d['lo']), 'mh': mv(d['hi']), 'mid0': round(mid, 1), 'n': name, 't': team, 'o': opp, 's': stat, 'k': k,
                          'q': inj.get((core.nn(name), team), ''), 'why': [[v6.LABEL.get(kk, kk), round(vv, 1)] for kk, vv in top if abs(vv) >= 0.1]}
    card = {}
    for c in F['cards']:
        for p in c.get('plays') or []:
            if p.get('ticker'):
                card[f"{p['ticker']}|{'Y' if p['side'] == 'Yes' else 'N'}"] = {'call': p['decision'], 'line': p['line'], 'price': p['price'], 'lo': p['lo'], 'mid': p['mid'], 'hi': p['hi']}
    import csv
    frec = next(csv.DictReader(open(W + 'rh/frec.csv')), {})
    flist = [{k: r[k] for k in ('week', 'game', 'line', 'price', 'outcome', 'profit_c') if k in r} for r in csv.DictReader(open(W + 'rh/final_record.csv'))]
    plays = [{'game': c['game'], 'line': p['line'], 'call': p['decision'], 'price': p['price'], 'lo': p['lo'], 'mid': p['mid'], 'hi': p['hi'], 'ticker': p.get('ticker', '')}
             for c in F['cards'] for p in (c.get('plays') or [])]
    live = {'week': WEEK, 'record': {'summary': {k: frec.get(k) for k in ('wins', 'losses', 'win_pct', 'roi_pct', 'thru')}, 'lines': flist}, 'plays': plays, 'prices_at': KP['at'], 'built': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'model': 'Wedge % v6 (lens on the market price)',
            'card_at': F.get('at', ''), 'games': games, 'lens': lens, 'card': card}
    # game logs: every 2026 game before this week, with the team's final margin
    st = pd.read_csv(W + 'dl18/stats_player_week_2026.csv', low_memory=False)
    st = st[(st.season_type == 'REG') & (st.week < WEEK)]
    gm = {}
    for r in g[(g.week < WEEK) & g.home_score.notna()].itertuples(index=False):
        gm[(fx(r.home_team), int(r.week))] = (int(r.home_score - r.away_score), 1)
        gm[(fx(r.away_team), int(r.week))] = (int(r.away_score - r.home_score), 0)
    logs = {}
    st = st[st.position.isin(['QB', 'RB', 'WR', 'TE', 'FB'])]
    n0 = lambda v: 0 if pd.isna(v) else int(v)
    for pid, s in st.groupby('player_id'):
        s = s.sort_values('week')
        if (s.receptions.fillna(0).sum() + s.carries.fillna(0).sum() + s.attempts.fillna(0).sum()) < 3: continue
        rows = []
        for r in s.itertuples(index=False):
            mg, home = gm.get((fx(r.team), int(r.week)), (None, None))
            rows.append([int(r.week), fx(r.opponent_team), home, mg, n0(r.receptions), n0(r.targets), n0(r.receiving_yards), n0(r.carries), n0(r.rushing_yards), n0(r.attempts), n0(r.passing_yards)])
        last = s.iloc[-1]
        logs[core.nn(last.player_display_name)] = {'n': last.player_display_name, 't': fx(last.team), 'pos': last.position, 'g': rows}
    os.makedirs(OUT, exist_ok=True)
    hdr = '// written by v2/build_live.py on every site build. Do not edit by hand.\n'
    open(OUT + 'live.js', 'w').write(hdr + 'export const LIVE = ' + json.dumps(live, separators=(',', ':')) + ';\n')
    open(OUT + 'logs.js', 'w').write(hdr + 'export const LOGS = ' + json.dumps({'thru': WEEK - 1, 'cols': ['week', 'opp', 'home', 'margin', 'rec', 'targets', 'rec_yds', 'carries', 'rush_yds', 'pass_att', 'pass_yds'], 'players': logs}, separators=(',', ':')) + ';\n')
    print(f'live tools data: {len(lens)} priced rungs, {len(card)} card plays, {len(logs)} players with logs, games {len(games)}')


if __name__ == '__main__':
    main()
