"""Thesis-page lens block for one game: both offenses against both defenses, from 2026 games before the week.
lens_block(away, home, week) -> {how, thru, sides: [...], check, check_title, check_head, verdict}"""
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, '/home/claude/wedger/lens'); import core
W = '/home/claude/wedger/'
_C = {}
def _data(week, dl=W + 'dl18/'):
    if week not in _C:
        live, st, pos = core.load(dl); _C[week] = (live[live.week < week].copy(), st[st.week < week].copy(), pos, core.Tables(live, st, pos, week))
    return _C[week]
ordn = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
pc = lambda x: f"{100 * x:.1f}%"
def rk(s, team, most='most', few='fewest'):
    s = s.dropna(); r = int(s.rank(ascending=False, method='min')[team]); n = len(s)
    return f"{ordn(r)} {most}" if r <= n / 2 else f"{ordn(n + 1 - r)} {few}"
BACKTEST = None
def backtest_rows():
    rep = json.load(open(W + 'bt/rep_v6.json')); cal = json.load(open(W + 'bt/cal_v6.json'))['coef']
    a = rep['all']; rows = [
        ['All settled props, Weeks 7-9 (each week held out)', f"log loss {a['p_mkt']['logloss']:.4f} → {a['p6']['logloss']:.4f}", f"{a['p6']['picks']['n']} picks, {100 * a['p6']['picks']['won']:.1f}% won, {100 * a['p6']['picks']['roi']:+.1f}% ROI"]]
    for wk in (7, 8, 9):
        r = rep[f'w{wk}']; rows.append([f'Week {wk} (held out)', f"log loss {r['p_mkt']['logloss']:.4f} → {r['p6']['logloss']:.4f}", f"{r['p6']['picks']['n']} picks, {100 * r['p6']['picks']['won']:.1f}% won, {100 * r['p6']['picks']['roi']:+.1f}% ROI"])
    for k, lab in (('g_rush', 'Rushing lines'), ('g_recyd', 'Receiving yards'), ('g_rec', 'Receptions'), ('g_passyd', 'Passing yards (left at the market)'), ('g_td', 'Anytime TDs (left at the market)')):
        r = rep[k]; rows.append([lab, f"log loss {r['p_mkt']['logloss']:.4f} → {r['p6']['logloss']:.4f}", (f"{r['p6']['picks']['n']} picks, {100 * r['p6']['picks']['roi']:+.1f}% ROI" if r['p6']['picks']['n'] else 'no picks')])
    W_ = [('Run direction (rushing)', cal['rush.dir']), ('Yards per carry allowed (rushing)', cal['rush.dvp']), ('Light boxes (rushing)', cal['rush.box']),
          ('Pass attempts the defense faces (receiving)', cal['recv.volume']), ('Position yards allowed (receiving)', cal['recv.dvp']), ('Blitz split (receiving)', cal['recv.look'])]
    for lab, v in W_: rows.append([f'Weight: {lab}', f'{v:+.3f} per unit', 'toward the over' if v > 0 else 'toward the under'])
    return rows
def side(off, de, week):
    L, S, pos, T = _data(week)
    D = T.D
    f = [['Pass attempts faced', f"{D.at[de, 'pass_att']:.1f}", rk(D.pass_att, de)], ['Pass yards allowed', f"{D.at[de, 'pass_yds']:.1f}", rk(D.pass_yds, de)],
         ['Yards per carry allowed', f"{D.at[de, 'ypc']:.2f}", rk(D.ypc, de)], ['WR yards allowed', f"{D.at[de, 'WR_yds']:.1f}", rk(D.WR_yds, de)],
         ['TE catches / yards allowed', f"{D.at[de, 'TE_rec']:.1f} / {D.at[de, 'TE_yds']:.1f}", rk(D.TE_yds, de)], ['RB catches / yards allowed', f"{D.at[de, 'RB_rec']:.1f} / {D.at[de, 'RB_yds']:.1f}", rk(D.RB_yds, de)],
         ['Sacks', f"{D.at[de, 'sacks']:.1f}", rk(D.sacks, de)], ['Blitz rate', pc(D.at[de, 'blitz']), rk(D.blitz, de, 'highest', 'lowest')],
         ['Box on runs', f"{D.at[de, 'box']:.2f}", rk(D.box, de, 'heaviest', 'lightest')], ['Red-zone TD rate allowed', pc(D.at[de, 'rz_td']), rk(D.rz_td, de, 'highest', 'lowest')]]
    pas = L[L.is_pass & L.receiver_player_id.notna() & (L.bucket != 'oth')]
    offsh = pas[pas.posteam == off].bucket.value_counts(normalize=True)
    lgoff = pas.groupby('posteam').bucket.value_counts(normalize=True).unstack(fill_value=0)
    where = []
    for lab, b in (('Tight ends', 'TE'), ('Running backs', 'RB'), ('WRs outside', 'WRo'), ('WRs in the middle', 'WRm')):
        qv = float(offsh.get(b, 0)); dv = float(D.at[de, 'sh_' + b])
        qr = int((lgoff[b] > qv).sum() + 1); dr = int((D['sh_' + b] > dv).sum() + 1)
        qhi, dhi = qv > lgoff[b].mean(), dv > D['sh_' + b].mean()
        where.append([lab, f"{pc(qv)} ({qr} of {len(lgoff)})", f"{pc(dv)} ({dr} of {len(D)})", 'Overlap' if (qhi and dhi) else ('Offense only' if qhi else ('Defense only' if dhi else 'Neither'))])
    # blitz splits for the offense's top pass catchers
    q = pas[(pas.posteam == off) & pas.n_blitzers.notna()]
    looks = []
    if len(q):
        allv = q.receiver_player_id.value_counts(normalize=True); bl = q[q.n_blitzers > 0].receiver_player_id.value_counts(normalize=True)
        nb = q[q.n_blitzers == 0].receiver_player_id.value_counts(normalize=True); ob = float(D.at[de, 'blitz'])
        name = S.drop_duplicates('player_id').set_index('player_id').player_display_name.to_dict()
        for pid, v in allv.head(6).items():
            b_, n_ = float(bl.get(pid, 0)), float(nb.get(pid, 0)); exp = ob * b_ + (1 - ob) * n_
            looks.append([name.get(pid, pid), pc(v), pc(b_), pc(n_), ('+' if exp >= v else '−') + f"{abs(100 * (exp - v)):.1f}"])
    run = L[(L.rush_attempt == 1) & (L.qb_scramble != 1) & (L.dir != '')]
    def sr(d): return d.success.mean() if len(d) else np.nan
    runs = []
    for lab, k in (('Inside (middle, guards)', 'in'), ('Outside (tackles, ends)', 'out')):
        o = run[(run.posteam == off) & (run.dir == k)]; dd = run[(run.defteam == de) & (run.dir == k)]
        osr = run[run.dir == k].groupby('posteam').success.mean(); dsr = run[run.dir == k].groupby('defteam').success.mean()
        runs.append([lab, f"{o.rushing_yards.mean():.2f} · {pc(sr(o))} ({rk(osr, off, 'best', 'worst')})", f"{dd.rushing_yards.mean():.2f} · {pc(sr(dd))} ({rk(dsr, de, 'most', 'fewest')})",
                     pc(len(o) / max(len(run[run.posteam == off]), 1))])
    # comparable defenses on this defense's most extreme trait
    traits = {'blitz': 'blitz rate', 'pass_att': 'pass attempts faced', 'sh_TE': 'share of targets to TEs', 'sh_RB': 'share of targets to RBs', 'sh_WRm': 'share of targets to middle WRs',
              'ypc': 'yards per carry allowed', 'box': 'box count on runs', 'sacks': 'sacks'}
    z = {t: (D.at[de, t] - T.mu[t]) / T.sd[t] for t in traits}; t = max(z, key=lambda k: abs(z[k]))
    near = (D[t].drop(de) - D.at[de, t]).abs().sort_values().index[:3].tolist()
    played = S[S.team == off].opponent_team.unique().tolist(); seen = [n for n in near if n in played]
    comps = [f"{de}'s most extreme trait is its {traits[t]} (z = {z[t]:+.2f}). The closest defenses: {', '.join(near)}." + (f" {off} has played {', '.join(seen)}." if seen else f" {off} hasn't faced them.")]
    if seen:
        g = S[(S.team == off) & S.opponent_team.isin(seen)]
        top = S[S.team == off].groupby('player_display_name').fantasy_points_ppr.sum().sort_values(ascending=False).index[:3]
        for nm in top:
            r = g[g.player_display_name == nm]
            if len(r): comps.append(f"{nm} against them: " + ', '.join(f"{int(x.week) and ''}{x.opponent_team} {int(x.receiving_yards or 0) + int(x.rushing_yards or 0)} scrimmage yds" for x in r.itertuples(index=False)) + '.')
    return {'off': off, 'def': de, 'qb': off, 'facts': f, 'where': where, 'looks': looks,
            'look_note': f"{de} blitzes on {pc(D.at[de, 'blitz'])} of dropbacks (league {pc(T.lg_blitz)}). Change = expected share against this blitz rate minus his overall share.",
            'runs': runs, 'run_note': f"{off} runs inside {pc(float(T.O.in_share.get(off, 0.6)))} of the time.", 'comps': comps}
def lens_block(away, home, week, plays_note=''):
    return {'how': ("The matchup lens reads a game in six steps: what each defense allows by position, where the offense sends the ball against where the defense allows it, "
                    "how each pass catcher's share moves against the look this defense shows (the blitz, from FTN charting), the run matchup by direction and box count, "
                    "the closest comparable defenses, and how consistently a player clears his line. Each step became a number, and the weights were fit on every settled "
                    "Robinhood prop from Weeks 7-9 and kept only where they beat the market's own price out of sample."),
            'thru': f'2026 Weeks 1-{week - 1}; FTN charting through Week {week - 1}', 'sides': [side(away, home, week), side(home, away, week)],
            'check_title': 'How the lens tested (each week held out)', 'check_head': ['Test', 'Market → v6', 'Picks at 3+ points'], 'check': backtest_rows(),
            'verdict': plays_note}
