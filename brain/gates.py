"""Research checks from the pick-development method, made computable for every candidate line.

Each check answers one question in the method's causal chain and returns the evidence it used, so a card can show
why a line passed or failed. Thresholds are fixed in advance from the written method (not fit to results):
  QB      - neither team starts a backup quarterback (this slate's exclusion rule).
  ROLE    - deployment link: for an over/Yes, the player's recent share of his team's carries (rushing) or targets
            (receiving) is at least 85% of his season share, and he played each of the team's last 3 games;
            for an under/No, his recent share is not rising past 125% of his season share.
  SCRIPT  - the side cleared in at least half of his games in the script the spread points to AND in close games
            (only buckets with 2+ games count; fewer is 'thin', not a fail).
  LOG     - the side cleared in at least half of all his 2026 games at this exact threshold (misses included).
  LATE    - an over/Yes that leans on fourth-quarter work (35%+ of his yards in that stat came in the 4th) is flagged.
All inputs are taken only from games before the week being picked."""
import numpy as np, pandas as pd

RUSH = {'rushyd', 'rryd'}; RECV = {'rec', 'recyd'}
COL = {'rushyd': 'rushing_yards', 'recyd': 'receiving_yards', 'rec': 'receptions', 'rryd': None}


def stat_value(df, stat):
    if stat == 'rryd': return df.rushing_yards.fillna(0) + df.receiving_yards.fillna(0)
    return df[COL[stat]].fillna(0)


class Ctx:
    """Everything the checks need for one week, built from games before that week."""
    def __init__(self, stats, pbp, games, week):
        self.w = week
        s = stats[(stats.week < week) & (stats.season_type == 'REG')].copy()
        self.s = s
        tm = s.groupby(['team', 'week'])[['carries', 'targets']].sum().reset_index()
        self.team_wk = tm
        g = games[(games.season == 2026) & (games.week < week) & games.home_score.notna()]
        rows = []
        for r in g.itertuples(index=False):
            rows.append((r.home_team, r.week, r.home_score - r.away_score)); rows.append((r.away_team, r.week, r.away_score - r.home_score))
        self.margin = {(t, wk): m for t, wk, m in rows}
        p = pbp[(pbp.week < week)]
        self.q4 = {}
        for col, idc in (('rushing_yards', 'rusher_player_id'), ('receiving_yards', 'receiver_player_id')):
            q = p[p[idc].notna()].groupby([idc, p.qtr >= 4])[col].sum().unstack(fill_value=0)
            for pid, r in q.iterrows():
                d = self.q4.setdefault(pid, {}); d[col] = (float(r.get(True, 0)), float(r.get(True, 0)) + float(r.get(False, 0)))
        # starting QB by team-week: the QB with the most pass attempts
        qb = stats[(stats.position == 'QB') & (stats.season_type == 'REG')].sort_values('attempts', ascending=False).groupby(['team', 'week']).head(1)
        self.qb_wk = {(r.team, r.week): (r.player_id, r.player_display_name) for r in qb.itertuples(index=False)}

    def primary_qb(self, team):
        c = {}
        for (t, wk), (pid, nm) in self.qb_wk.items():
            if t == team and wk < self.w: c[(pid, nm)] = c.get((pid, nm), 0) + 1
        return max(c, key=c.get) if c else (None, None)

    def role(self, pid, team, stat):
        col = 'carries' if stat in RUSH else 'targets'
        mine = self.s[(self.s.player_id == pid) & (self.s.team == team)].set_index('week')[col]
        tw = self.team_wk[self.team_wk.team == team].set_index('week')[col]
        wks = sorted(tw.index); last3 = wks[-3:]
        if not len(mine) or not len(tw): return None
        sea = float(mine.sum() / tw.loc[mine.index].sum()) if tw.loc[mine.index].sum() else 0.0
        l3_mine = float(sum(mine.get(w_, 0) for w_ in last3)); l3_team = float(tw.loc[last3].sum())
        l3 = l3_mine / l3_team if l3_team else 0.0
        played = sum(1 for w_ in last3 if w_ in mine.index)
        per = float(np.median([mine.get(w_, 0) for w_ in last3])) if last3 else 0.0
        return {'col': col, 'season_share': round(sea, 3), 'last3_share': round(l3, 3), 'played_last3': played, 'last3_median': per, 'team_last3_per_game': round(l3_team / max(len(last3), 1), 1)}

    def logs(self, pid, team, stat):
        d = self.s[(self.s.player_id == pid)].sort_values('week')
        v = stat_value(d, stat)
        return [(int(w_), float(x), t, o, self.margin.get((t, w_))) for w_, x, t, o in zip(d.week, v, d.team, d.opponent_team)]

    def q4_share(self, pid, stat):
        d = self.q4.get(pid, {})
        cols = ['rushing_yards'] if stat == 'rushyd' else (['receiving_yards'] if stat == 'recyd' else (['rushing_yards', 'receiving_yards'] if stat == 'rryd' else []))
        if not cols: return None
        a = sum(d.get(c, (0, 0))[0] for c in cols); b = sum(d.get(c, (0, 0))[1] for c in cols)
        return round(a / b, 3) if b > 0 else None


def bucket(m):
    if m is None or (isinstance(m, float) and np.isnan(m)): return None
    return 'control' if m >= 8 else ('trail' if m <= -8 else 'close')


def likely_script(exp_margin):
    return 'control' if exp_margin >= 6 else ('trail' if exp_margin <= -6 else 'close')


def check(ctx, pid, team, stat, k, side, exp_margin, qb_ok=True, qb_note=''):
    """-> dict of check results for one exact line (k = threshold as an integer count, side 'Yes' (k or more) / 'No' (under k))."""
    hit = (lambda v: v >= k) if side == 'Yes' else (lambda v: v < k)
    out = {'QB': {'pass': bool(qb_ok), 'note': qb_note}}
    r = ctx.role(pid, team, stat)
    if r is None: out['ROLE'] = {'pass': False, 'note': 'no 2026 role with this team', 'data': None}
    elif side == 'Yes':
        ok = r['last3_share'] >= 0.85 * r['season_share'] and r['played_last3'] >= 3
        out['ROLE'] = {'pass': bool(ok), 'data': r}
    else:
        ok = r['last3_share'] <= 1.25 * r['season_share'] if r['season_share'] > 0 else True
        out['ROLE'] = {'pass': bool(ok), 'data': r}
    L = [x for x in ctx.logs(pid, team, stat) if x[2] == team]
    out['LOG'] = {'hits': sum(hit(v) for _, v, *_ in L), 'n': len(L), 'games': [(w_, v, o) for w_, v, _, o, _ in L]}
    out['LOG']['pass'] = bool(len(L) and out['LOG']['hits'] >= len(L) / 2)
    ls = likely_script(exp_margin); bk = {}
    for w_, v, _, o, m in L:
        b = bucket(m)
        if b: e = bk.setdefault(b, [0, 0]); e[1] += 1; e[0] += int(hit(v))
    need = [ls] if ls == 'close' else [ls, 'close']
    fails = [b for b in need if b in bk and bk[b][1] >= 2 and bk[b][0] < bk[b][1] / 2]
    thin = [b for b in need if b not in bk or bk[b][1] < 2]
    out['SCRIPT'] = {'pass': not fails, 'likely': ls, 'buckets': bk, 'fails': fails, 'thin': thin}
    q = ctx.q4_share(pid, stat)
    out['LATE'] = {'pass': not (side == 'Yes' and q is not None and q >= 0.35), 'q4_share': q}
    out['all'] = all(out[c]['pass'] for c in ('QB', 'ROLE', 'SCRIPT', 'LOG', 'LATE'))
    return out
