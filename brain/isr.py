"""The research method's computable checks, from Sunday of Week 12 (Fri Nov 27): Independent Sports Research, v1
(brain/ISR_Clone_v1_2026-11-24.md, the owner's spec; kept private). It replaces the earlier research checks (brain/gates.py, kept
unchanged for the cards posted through Friday of Week 12) and is not derived from them: each check below is one question the
method's own workflow asks of the numbers, cited by section. Everything the numbers can't see (team analysts, coaching quotes,
film, human context) is the hand research pass in the week's brain_layer.py, which can veto or approve any line.

  ROLE      sec. 2 and 3.9: the current role, not a stale season average. Over/Yes: his share of the team's carries (rushing) or
            targets (receiving) over the team's last 3 games is at least 85% of his season share, and he played all 3.
            Under/No: that share isn't rising past 125% of his season share (a growing role sinks an under).
  SCRIPT    sec. 3.2 and 6: the likely game script and the close-game alternative. The side cleared in at least half of his games
            in the script the spread points to and in one-score games (a bucket needs 2+ games; fewer is thin, not a fail).
  LATE      sec. 3.3: production that came late. An over/Yes whose yards lean on the fourth quarter (35%+ of them) is flagged.
  MOMENTUM  sec. 2 and 3.4: recent production against his own baseline. Hot (last 3 games' median 40%+ over his season median)
            or cold (40%+ under) sends the line to the hand research for the cause; it never decides a line by itself
            ("never assume a bounce-back or correction is due merely because of a streak").
  LOG       sec. 2 (consistency): how often this exact side cleared in his 2026 games. Shown as evidence; not a veto (the method
            warns against chasing recent hit rates).
All inputs come only from games before the week being picked.

Markets (sec. 3.11): rushing attempts and yards, receptions and receiving yards, rush + rec yards, passing attempts, yards and TDs,
player TDs, spreads, team totals and team defensive sacks. Individual sacks are never used. The model prices only the receiving
and rushing ladders; the others are read at the market's own number and reach the card only through the research."""
import numpy as np, pandas as pd

RUSH = {'rushyd', 'rryd', 'rushatt'}
COL = {'rushyd': 'rushing_yards', 'recyd': 'receiving_yards', 'rec': 'receptions', 'rryd': None, 'rushatt': 'carries'}
VETO = ('ROLE', 'SCRIPT', 'LATE')
ELIGIBLE = {'KXNFLRSHATT': 'rushing attempts', 'KXNFLRSHYDS': 'rushing yards', 'KXNFLREC': 'receptions', 'KXNFLRECYDS': 'receiving yards',
            'KXNFLRRYDS': 'rush + rec yards', 'KXNFLPASSATT': 'passing attempts', 'KXNFLPASSYDS': 'passing yards', 'KXNFLPASSTDS': 'passing TDs',
            'KXNFLTD': 'player TDs', 'KXNFLSPREAD': 'spread', 'KXNFLTEAMTOTAL': 'team total', 'KXNFLTEAMSACK': 'team sacks'}
NEVER = {'KXNFLSACK': 'individual sacks'}
HOT, COLD = 1.4, 0.6


def stat_value(df, stat):
    if stat == 'rryd': return df.rushing_yards.fillna(0) + df.receiving_yards.fillna(0)
    return df[COL[stat]].fillna(0)


class Ctx:
    """the week's inputs: player-week stats, play-by-play (quarters) and final margins, all from games before `week`"""
    def __init__(self, stats, pbp, games, week):
        self.w = week
        s = stats[(stats.week < week) & (stats.season_type == 'REG')].copy()
        self.s = s
        self.team_wk = s.groupby(['team', 'week'])[['carries', 'targets']].sum().reset_index()
        g = games[(games.season == 2026) & (games.week < week) & games.home_score.notna()]
        self.margin = {}
        for r in g.itertuples(index=False):
            self.margin[(r.home_team, r.week)] = r.home_score - r.away_score; self.margin[(r.away_team, r.week)] = r.away_score - r.home_score
        p = pbp[pbp.week < week]; self.q4 = {}
        for col, idc in (('rushing_yards', 'rusher_player_id'), ('receiving_yards', 'receiver_player_id')):
            q = p[p[idc].notna()].groupby([idc, p.qtr >= 4])[col].sum().unstack(fill_value=0)
            for pid, r in q.iterrows():
                self.q4.setdefault(pid, {})[col] = (float(r.get(True, 0)), float(r.get(True, 0)) + float(r.get(False, 0)))

    def role(self, pid, team, stat):
        col = 'carries' if stat in RUSH else 'targets'
        mine = self.s[(self.s.player_id == pid) & (self.s.team == team)].set_index('week')[col]
        tw = self.team_wk[self.team_wk.team == team].set_index('week')[col]
        if not len(mine) or not len(tw): return None
        last3 = sorted(tw.index)[-3:]
        den = tw.loc[mine.index].sum()
        sea = float(mine.sum() / den) if den else 0.0
        l3t = float(tw.loc[last3].sum()); l3 = float(sum(mine.get(w, 0) for w in last3)) / l3t if l3t else 0.0
        return {'col': col, 'season_share': round(sea, 3), 'last3_share': round(l3, 3), 'played_last3': sum(1 for w in last3 if w in mine.index),
                'last3_median': float(np.median([mine.get(w, 0) for w in last3])), 'team_last3_per_game': round(l3t / max(len(last3), 1), 1)}

    def logs(self, pid, team, stat):
        d = self.s[self.s.player_id == pid].sort_values('week'); v = stat_value(d, stat)
        return [(int(w), float(x), t, o, self.margin.get((t, w))) for w, x, t, o in zip(d.week, v, d.team, d.opponent_team)]

    def q4_share(self, pid, stat):
        cols = {'rushyd': ['rushing_yards'], 'recyd': ['receiving_yards'], 'rryd': ['rushing_yards', 'receiving_yards']}.get(stat)
        if not cols: return None
        d = self.q4.get(pid, {}); a = sum(d.get(c, (0, 0))[0] for c in cols); b = sum(d.get(c, (0, 0))[1] for c in cols)
        return round(a / b, 3) if b > 0 else None


def bucket(m):
    if m is None or (isinstance(m, float) and np.isnan(m)): return None
    return 'control' if m >= 8 else ('trail' if m <= -8 else 'close')


def likely_script(exp_margin):
    return 'control' if exp_margin >= 6 else ('trail' if exp_margin <= -6 else 'close')


def momentum(L):
    """his last 3 games against his season median (games for this team only)"""
    vals = [v for _, v, *_ in L]
    if len(vals) < 5: return {'state': 'thin', 'last3': None, 'season': None}
    sea = float(np.median(vals)); l3 = float(np.median(vals[-3:]))
    if sea <= 0: return {'state': 'steady', 'last3': l3, 'season': sea}
    st = 'hot' if l3 >= HOT * sea else ('cold' if l3 <= COLD * sea else 'steady')
    return {'state': st, 'last3': l3, 'season': sea}


def check(ctx, pid, team, stat, k, side, exp_margin, qb_ok=True, qb_note=''):
    """-> the checks for one exact line (k = the threshold as a count; side 'Yes' = k or more, 'No' = under k)"""
    hit = (lambda v: v >= k) if side == 'Yes' else (lambda v: v < k)
    out = {'QB': {'pass': bool(qb_ok), 'note': qb_note}}
    r = ctx.role(pid, team, stat)
    if r is None: out['ROLE'] = {'pass': False, 'note': 'no 2026 role with this team', 'data': None}
    elif side == 'Yes': out['ROLE'] = {'pass': bool(r['last3_share'] >= 0.85 * r['season_share'] and r['played_last3'] >= 3), 'data': r}
    else: out['ROLE'] = {'pass': bool(r['last3_share'] <= 1.25 * r['season_share'] if r['season_share'] > 0 else True), 'data': r}
    L = [x for x in ctx.logs(pid, team, stat) if x[2] == team]
    out['LOG'] = {'hits': sum(hit(v) for _, v, *_ in L), 'n': len(L), 'games': [(w, v, o) for w, v, _, o, _ in L]}
    out['LOG']['pass'] = bool(len(L) and out['LOG']['hits'] >= len(L) / 2)
    ls = likely_script(exp_margin); bk = {}
    for w, v, _, o, m in L:
        b = bucket(m)
        if b: e = bk.setdefault(b, [0, 0]); e[1] += 1; e[0] += int(hit(v))
    need = [ls] if ls == 'close' else [ls, 'close']
    fails = [b for b in need if b in bk and bk[b][1] >= 2 and bk[b][0] < bk[b][1] / 2]
    out['SCRIPT'] = {'pass': not fails, 'likely': ls, 'buckets': bk, 'fails': fails, 'thin': [b for b in need if b not in bk or bk[b][1] < 2]}
    q = ctx.q4_share(pid, stat)
    out['LATE'] = {'pass': not (side == 'Yes' and q is not None and q >= 0.35), 'q4_share': q}
    out['MOMENTUM'] = {'pass': True, **momentum(L)}
    out['all'] = all(out[c]['pass'] for c in ('QB',) + VETO)
    return out
