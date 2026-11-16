"""Matchup lens: point-in-time tables and per-line features.

The lens reads a game in six steps, each turned into a number we can test against settled prices:
  dvp      what the opponent allows to this player's position, per game (z-score across defenses)
  overlap  where this player's targets go (middle vs outside for WRs; TE / RB share) against where the opponent allows targets
  look     how this player's target share moves when defenses blitz, scaled by how much more or less this opponent blitzes
           than the league (FTN charting; public coverage charting doesn't exist for 2026, so the blitz is the look we can measure)
  volume   pass attempts (or rush attempts) the opponent faces per game
  dir      run matchup: this team's inside/outside run mix against the yards per carry the opponent allows inside and outside
  box      defenders in the box on runs (FTN)
  pressure sacks per game by the opponent (passing lines)
  comp     the player's production against the defenses most like this opponent on its most extreme trait, vs his own average
  consist  how often he cleared this line in 2026 before this week, against the price
Every table only uses games played before the week being priced."""
import re, unicodedata
import numpy as np, pandas as pd

FIX = {'LA': 'LAR', 'WAS': 'WSH', 'JAC': 'JAX'}
fx = lambda t: FIX.get(t, t)
def nn(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', s); return re.sub(r'[^a-z]', '', s)

def load(dl):
    p = pd.read_csv(dl + 'play_by_play_2026.csv', low_memory=False)
    p = p[p.season_type == 'REG'].copy()
    for c in ('posteam', 'defteam'): p[c] = p[c].map(fx)
    f = pd.read_csv(dl + 'ftn_charting_2026.csv', low_memory=False).rename(columns={'nflverse_game_id': 'game_id', 'nflverse_play_id': 'play_id'})
    p = p.merge(f[['game_id', 'play_id', 'n_blitzers', 'n_defense_box']], on=['game_id', 'play_id'], how='left')
    st = pd.read_csv(dl + 'stats_player_week_2026.csv', low_memory=False); st = st[st.season_type == 'REG'].copy()
    st['team'] = st.team.map(fx); st['opponent_team'] = st.opponent_team.map(fx); st['nn'] = st.player_display_name.map(nn)
    pos = st.drop_duplicates('player_id', keep='last').set_index('player_id').position.to_dict()
    p['rpos'] = p.receiver_player_id.map(pos)
    live = p[(p.two_point_attempt != 1) & p.play_type.isin(['pass', 'run']) & (p.qb_kneel != 1) & (p.qb_spike != 1)].copy()
    live['is_pass'] = (live.pass_attempt == 1) & (live.sack != 1)
    live['bucket'] = np.where(live.rpos == 'TE', 'TE', np.where(live.rpos.isin(['RB', 'FB']), 'RB', np.where(live.pass_location == 'middle', 'WRm', 'WRo')))
    live.loc[~live.rpos.isin(['TE', 'RB', 'FB', 'WR']), 'bucket'] = 'oth'
    live['dir'] = np.where((live.run_location == 'middle') | (live.run_gap == 'guard'), 'in', np.where(live.run_gap.isin(['tackle', 'end']), 'out', ''))
    return live, st, pos

class Tables:
    """Every lens table as of the start of week w (games before w only)."""
    def __init__(self, live, st, pos, w):
        self.w = w; L = live[live.week < w]; S = st[st.week < w]; self.S = S; self.pos = pos
        G = L.groupby('defteam').game_id.nunique()
        pas = L[L.is_pass]; tgt = pas[pas.receiver_player_id.notna() & (pas.bucket != 'oth')]
        run = L[(L.rush_attempt == 1)]; drun = run[run.qb_scramble != 1]
        D = pd.DataFrame(index=G.index)
        D['pass_att'] = pas.groupby('defteam').size() / G
        D['pass_yds'] = pas.groupby('defteam').passing_yards.sum() / G
        D['pass_td'] = pas.groupby('defteam').pass_touchdown.sum() / G
        D['rush_att'] = run.groupby('defteam').size() / G
        D['rush_yds'] = run.groupby('defteam').rushing_yards.sum() / G
        D['ypc'] = drun.groupby('defteam').rushing_yards.mean()
        D['sacks'] = L.groupby('defteam').sack.sum() / G
        for b, ps in (('WR', ['WR']), ('TE', ['TE']), ('RB', ['RB', 'FB'])):
            tb = tgt[tgt.rpos.isin(ps)]
            D[f'{b}_tgt'] = tb.groupby('defteam').size() / G
            D[f'{b}_rec'] = tb.groupby('defteam').complete_pass.sum() / G
            D[f'{b}_yds'] = tb.groupby('defteam').receiving_yards.sum() / G
            D[f'{b}_td'] = tb.groupby('defteam').pass_touchdown.sum() / G
        D['RB_rtd'] = drun.groupby('defteam').rush_touchdown.sum() / G
        sh = tgt.groupby(['defteam', 'bucket']).size().unstack(fill_value=0); sh = sh.div(sh.sum(1), axis=0)
        for b in ('TE', 'RB', 'WRm', 'WRo'): D['sh_' + b] = sh.get(b, 0)
        dr = L[(L.qb_dropback == 1) & L.n_blitzers.notna()]
        D['blitz'] = dr.groupby('defteam').n_blitzers.apply(lambda s: (s > 0).mean())
        D['box'] = drun[drun.n_defense_box.notna()].groupby('defteam').n_defense_box.mean()
        for d in ('in', 'out'): D['ypc_' + d] = drun[drun.dir == d].groupby('defteam').rushing_yards.mean()
        rz = L[L.drive_inside20 == 1].drop_duplicates(['game_id', 'fixed_drive'])
        D['rz_td'] = rz.groupby('defteam').fixed_drive_result.apply(lambda s: (s == 'Touchdown').mean())
        self.D = D.fillna(D.mean()); self.mu = self.D.mean(); self.sd = self.D.std().replace(0, 1)
        # offense run mix
        O = pd.DataFrame(index=drun.posteam.unique())
        O['in_share'] = drun[drun.dir != ''].groupby('posteam').dir.apply(lambda s: (s == 'in').mean())
        self.O = O.fillna(0.6)
        # player target profiles (location, blitz split) and rush direction
        tq = pas[pas.receiver_player_id.notna()]
        P = {}
        for pid, g in tq.groupby('receiver_player_id'):
            n = len(g); mid = (g.pass_location == 'middle').sum()
            P[pid] = {'tg': n, 'mid': (mid + 0.25 * 12) / (n + 12)}
        # blitz split: his share of team targets in his games, with and without the blitz
        tb = tq[tq.n_blitzers.notna()]
        for (team, gid), g in tb.groupby(['posteam', 'game_id']): pass
        tb = tb.assign(bl=tb.n_blitzers > 0)
        games_of = tb.groupby('receiver_player_id').game_id.unique()
        for pid, gids in games_of.items():
            sub = tb[tb.game_id.isin(gids) & (tb.posteam == tb[tb.receiver_player_id == pid].posteam.iloc[-1])]
            a = sub[sub.bl]; b = sub[~sub.bl]
            if len(a) < 10 or len(b) < 10: continue
            sa = ((a.receiver_player_id == pid).sum() + 1) / (len(a) + 8); sb = ((b.receiver_player_id == pid).sum() + 1) / (len(b) + 8)
            sall = ((sub.receiver_player_id == pid).sum() + 1) / (len(sub) + 8)
            P.setdefault(pid, {})['bl'] = (sa - sb) / max(sall, 0.03)
        self.P = P
        self.lg_blitz = float(self.D.blitz.mean())
        lgsh = tgt.bucket.value_counts(normalize=True); self.lgsh = {b: float(lgsh.get(b, 0.25)) for b in ('TE', 'RB', 'WRm', 'WRo')}
        self.lg_in, self.lg_out = float(self.D.ypc_in.mean()), float(self.D.ypc_out.mean()); self.sd_ypc = float(self.D.ypc.std())

    def z(self, team, col): return float((self.D.at[team, col] - self.mu[col]) / self.sd[col]) if team in self.D.index else 0.0

    def comp(self, pid, opp, col):
        """Player's mean in col against the 3 defenses closest to opp on opp's most extreme trait, vs his own mean."""
        traits = ['blitz', 'pass_att', 'sh_TE', 'sh_RB', 'sh_WRm', 'ypc', 'box', 'sacks']
        if opp not in self.D.index: return 0.0
        zz = {t: abs(self.z(opp, t)) for t in traits}; t = max(zz, key=zz.get)
        if zz[t] < 1.0: return 0.0
        near = (self.D[t].drop(opp) - self.D.at[opp, t]).abs().sort_values().index[:3]
        g = self.S[self.S.player_id == pid]
        if len(g) < 3 or col not in g: return 0.0
        m_all = g[col].mean()
        if m_all <= 0: return 0.0
        gc = g[g.opponent_team.isin(near)]
        if not len(gc): return 0.0
        return float((gc[col].mean() / m_all - 1) * len(gc) / (len(gc) + 2))

STATCOL = {'recyd': 'receiving_yards', 'rec': 'receptions', 'rushyd': 'rushing_yards', 'passyd': 'passing_yards', 'passtd': 'passing_tds', 'rryd': None, 'td': None}

def features(T, pid, team, opp, stat, line, price):
    pos = T.pos.get(pid, '')
    b = 'TE' if pos == 'TE' else ('RB' if pos in ('RB', 'FB') else ('WR' if pos == 'WR' else ('QB' if pos == 'QB' else '')))
    f = dict.fromkeys(['dvp', 'overlap', 'look', 'volume', 'dir', 'box', 'pressure', 'comp', 'consist'], 0.0)
    if opp not in T.D.index: return f
    pr = T.P.get(pid, {})
    if stat in ('recyd', 'rec') and b in ('WR', 'TE', 'RB'):
        f['dvp'] = T.z(opp, f"{b}_{'yds' if stat == 'recyd' else 'rec'}")
        if b == 'WR':
            m = pr.get('mid', 0.25); D = T.D.loc[opp]
            f['overlap'] = m * (D.sh_WRm / T.lgsh['WRm']) + (1 - m) * (D.sh_WRo / T.lgsh['WRo']) - 1
        else: f['overlap'] = T.D.at[opp, 'sh_' + b] / T.lgsh[b] - 1
        f['look'] = pr.get('bl', 0.0) * (T.D.at[opp, 'blitz'] - T.lg_blitz) / 0.1
        f['volume'] = T.z(opp, 'pass_att')
        f['comp'] = T.comp(pid, opp, STATCOL[stat])
    elif stat in ('rushyd', 'rryd') and b in ('RB', 'QB', 'WR'):
        f['dvp'] = T.z(opp, 'ypc') if stat == 'rushyd' else 0.5 * (T.z(opp, 'ypc') + T.z(opp, 'RB_yds'))
        i = float(T.O.in_share.get(team, 0.6)) if team in T.O.index else 0.6
        f['dir'] = (i * (T.D.at[opp, 'ypc_in'] - T.lg_in) + (1 - i) * (T.D.at[opp, 'ypc_out'] - T.lg_out)) / max(T.sd_ypc, 0.2)
        f['box'] = -T.z(opp, 'box')
        f['volume'] = T.z(opp, 'rush_att')
        f['comp'] = T.comp(pid, opp, 'rushing_yards')
    elif stat in ('passyd', 'passtd') and b == 'QB':
        f['dvp'] = T.z(opp, 'pass_yds' if stat == 'passyd' else 'pass_td')
        f['volume'] = T.z(opp, 'pass_att'); f['pressure'] = -T.z(opp, 'sacks')
        f['comp'] = T.comp(pid, opp, STATCOL[stat])
    elif stat == 'td' and b in ('WR', 'TE', 'RB'):
        f['dvp'] = T.z(opp, 'RB_rtd') if b == 'RB' else T.z(opp, f'{b}_td')
        f['overlap'] = T.z(opp, 'rz_td')
    # consistency: his 2026 hit rate at this line before this week, shrunk to the price
    col = STATCOL.get(stat)
    g = T.S[T.S.player_id == pid]
    if len(g):
        if stat == 'rryd': v = (g.rushing_yards.fillna(0) + g.receiving_yards.fillna(0)).values
        elif stat == 'td': v = (g.rushing_tds.fillna(0) + g.receiving_tds.fillna(0)).values; line = 0.5
        else: v = g[col].fillna(0).values
        h = (v > line).sum(); f['consist'] = float((h + 6 * price) / (len(v) + 6) - price)
    return f
