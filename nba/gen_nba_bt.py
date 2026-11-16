"""Build the NBA backtest section (static HTML) from nba_bt.json -> rh/nba_bt_section.html, plus the tile text."""
import json, html
D = '/home/claude/wedger/'
B = json.load(open(D + 'nba/nba_bt.json'))
S = B['screen']; A = B['all']
esc = html.escape

def pct(x): return f"{x:.1f}%"
def roi(x): return ('+' if x > 0 else '−' if x < 0 else '±') + f"{abs(x):.1f}%"

def tile(label, s, note):
    if not s.get('n'): return ''
    cls = 'up' if s['roi'] > 0 else 'down'
    return f'''<div class="rs-card"><div class="rs-tile-label">{label}</div><div class="rs-tile-num">{pct(s['win_pct'])}</div>
<div class="rs-tile-note">{s['won']:,}–{s['n'] - s['won']:,} · avg price {s['avg_price']:.0f}¢ · return <b class="wg-roi {cls}">{roi(s['roi'])}</b>{(' · ' + note) if note else ''}</div></div>'''

def bar_rows(rows):
    """rows: [(label, sub, strat)] -> diverging ROI bars."""
    lim = max(5.0, max(abs(s['roi']) for _, _, s in rows if s.get('n')))
    out = []
    for lab, sub, s in rows:
        if not s.get('n'): continue
        w = min(abs(s['roi']), lim) / lim * 50
        cls = 'up' if s['roi'] >= 0 else 'down'
        left = 50 if s['roi'] >= 0 else 50 - w
        out.append(f'''<div class="wg-bt-row"><span class="wg-bt-l"><b>{esc(lab)}</b><small>{esc(sub)} · {s['won']:,} of {s['n']:,} won ({pct(s['win_pct'])}), avg price {s['avg_price']:.0f}¢</small></span>
<span class="wg-bt-bar"><span class="{cls}" style="left:{left:.1f}%;width:{w:.1f}%"></span><i></i></span><span class="wg-bt-v {cls}"><b>{roi(s['roi'])}</b><small>return</small></span></div>''')
    return ''.join(out)

def brier_rows(src, items):
    out = []
    for k, lab, sub in items:
        b = src[k]['brier']; sk = 100 * (0.25 - b) / 0.25
        lim = 6.0; w = min(abs(sk), lim) / lim * 50; cls = 'up' if sk >= 0 else 'down'; left = 50 if sk >= 0 else 50 - w
        clip = ' clip' if abs(sk) > lim else ''
        out.append(f'''<div class="wg-bt-row"><span class="wg-bt-l"><b>{esc(lab)}</b><small>{esc(sub)}</small></span>
<span class="wg-bt-bar"><span class="{cls}{clip}" style="left:{left:.1f}%;width:{w:.1f}%"></span><i></i></span><span class="wg-bt-v {cls}"><b>{'+' if sk >= 0 else '−'}{abs(sk):.1f}%</b><small>Brier {b:.4f}</small></span></div>''')
    return ''.join(out)

STAT = {'pts': 'Points', 'reb': 'Rebounds', 'ast': 'Assists', '3pm': 'Threes', 'pra': 'Pts + Reb + Ast'}
by_stat_rows = ''.join(
    f"<tr><td>{STAT[s]}</td><td class='num'>{v['n']:,}</td><td class='num'>{pct(v['hit_rate'])}</td>"
    f"<td class='num'>{(pct(v['screen']['win_pct']) + ' · ' + format(v['screen']['n'], ',')) if v['screen'].get('n') else '—'}</td>"
    f"<td class='num'>{roi(v['screen']['roi']) if v['screen'].get('n') else '—'}</td>"
    f"<td class='num'>{v['brier']['p']:.4f}</td><td class='num'>{v['brier']['ours_cal']:.4f}</td><td class='num'>{v['brier']['wedger']:.4f}</td></tr>"
    for s, v in B['by_stat'].items())
MON = {'2025-10': 'Oct', '2025-11': 'Nov', '2025-12': 'Dec', '2026-01': 'Jan', '2026-02': 'Feb', '2026-03': 'Mar', '2026-04': 'Apr'}
month_rows = ''.join(
    f"<tr><td>{MON.get(m, m)}</td><td class='num'>{v['screen']['n'] if v['screen'].get('n') else 0:,}</td>"
    f"<td class='num'>{pct(v['screen']['win_pct']) if v['screen'].get('n') else '—'}</td><td class='num'>{roi(v['screen']['roi']) if v['screen'].get('n') else '—'}</td>"
    f"<td class='num'>{pct(v['band']['win_pct']) if v['band'].get('n') else '—'}</td><td class='num'>{roi(v['band']['roi']) if v['band'].get('n') else '—'}</td></tr>"
    for m, v in B['by_month'].items())
cal_rows = ''.join(f"<tr><td>{k}</td><td class='num'>{n:,}</td><td class='num'>{pct(h)}</td></tr>" for k, (n, h) in B['wedger_calibration'].items() if n >= 30)
mae = B['projection_mae']
d0, d1, nd = B['dates']
import datetime as _dt
fmtd = lambda x: _dt.date.fromisoformat(x).strftime('%b %-d, %Y')
scr, band = S['band_hit20_gt50'], S['band_all']
H2 = B['second_half_strats']
st_ = lambda lab, k, src=S: [lab, src[k]['n'], src[k]['won'], src[k]['win_pct'], src[k]['avg_price'], src[k]['roi']]
blob = {
  'strat': [st_('Every 45–55¢ line', 'band_all'), st_('Filter: hit >50% of last 20', 'band_hit20_gt50'), st_('Model: Wedger % above price', 'band_model'),
            st_('Filter and model agree', 'band_screen_model'), st_('Wedger % beats price by 3+', 'band_wedger_plus3')]
           + [['#By his last-20 hit rate']] + [[k, v['n'], v['won'], v['win_pct'], v['avg_price'], v['roi']] for k, v in B['hit20_bands'].items()],
  'mkt': [[STAT[k], [v['screen'][x] for x in ('n', 'won', 'win_pct', 'avg_price', 'roi')], [v['model'][x] for x in ('n', 'won', 'win_pct', 'avg_price', 'roi')]] for k, v in B['by_stat'].items()],
  'month': [[MON.get(m, m), *[[v[k]['win_pct'], v[k]['n'], v[k]['avg_price']] if v[k].get('n') else None for k in ('band', 'screen', 'model')]] for m, v in B['by_month'].items()],
  'cum': [[c['date'], c['band_roi'], c['screen_roi'], c['model_roi']] for i, c in enumerate(B['cum']) if c['band_n'] >= 1500 and (i % 2 == 0 or i == len(B['cum']) - 1)],
  'cal': [[c['lo'], c['w_pred'], c['w_hit'], c['w_n'], c['p_pred'], c['p_hit'], c['p_n']] for c in B['calib_fine']],
}
bt_json = json.dumps(blob, separators=(',', ':'), ensure_ascii=False).replace('</', '<\\/')
lead = (f"The filter (hit &gt;50% of his last 20) won {pct(scr['win_pct'])} of {scr['n']:,} lines at an average price of {scr['avg_price']:.0f}¢, a return of {roi(scr['roi'])} before fees. "
        f"The model (Wedger % above the price) won {pct(S['band_model']['win_pct'])} of {S['band_model']['n']:,} at {S['band_model']['avg_price']:.0f}¢, {roi(S['band_model']['roi'])}: it picked cheaper lines, so it lost less, but it did not win more often. "
        f"Every line in the 45–55¢ band returned {roi(band['roi'])}. In the second half of the season (after the model's settings were fitted), the filter won {pct(H2['band_hit20_gt50']['win_pct'])}, the model {pct(H2['band_model']['win_pct'])} and every line {pct(H2['band_all']['win_pct'])}. ")
html_ = f'''
    <section class="rs-card" id="nba-bt">
      <h2>NBA backtest · the filter and the model on 2025-26 prices</h2>
      <p class="rs-note">Closing player-prop lines from DraftKings, FanDuel, BetRivers, BetMGM and other books (via Action Network) on {nd} dates of the 2025-26 regular season ({fmtd(d0)} to {fmtd(d1)}, every other day), {A['n']:,} lines in all, settled against ESPN box scores. Price = the books' average no-vig chance of the Over at their consensus line (Robinhood's NBA ladders weren't trading then, so the books stand in for its price). Everything about a line uses only games played before that night: hit rate over his last 20 games, minutes cases, defense, pace, game script from the closing spread, team total, rest and teammates who sat out. Return = profit buying one Yes contract at the price, fees excluded.</p>
      <div class="rs-tiles wg-nbt-tiles">
        {tile('Filter: hit &gt;50% of his last 20', scr, '')}
        {tile('Model: Wedger % above the price', S['band_model'], '')}
        {tile('Filter and model agree', S['band_screen_model'], '')}
        {tile('Every line priced 45–55¢', band, '')}
      </div>
      <p class="rs-note wg-nbt-lead">{lead}{esc(B.get('takeaway', ''))}</p>
      <div class="wg-key wg-dkey" style="margin-top:14px"></div>
      <div class="wg-grid2">
        <div class="wg-card"><div class="wg-lab">Win % against the price paid</div><p class="wg-note">Dot = how often the Yes came true; tick = average price paid. Green = hit more often than it cost (made money), red = less often.</p><div class="wg-chart" id="nbt-strat"></div></div>
        <div class="wg-card"><div class="wg-lab">Filter vs model by market</div><p class="wg-note">The same two strategies, split by stat. Return on the right.</p><div class="wg-chart" id="nbt-mkt"></div></div>
        <div class="wg-card"><div class="wg-lab">Win % by month</div><div class="wg-key nbt-key"></div><div class="wg-chart" id="nbt-month"></div></div>
        <div class="wg-card"><div class="wg-lab">Return to date through the season</div><div class="wg-key nbt-key"></div><div class="wg-chart" id="nbt-cum"></div></div>
        <div class="wg-card"><div class="wg-lab">Calibration: called chance vs how often it hit</div><p class="wg-note">Every backtest line, bucketed by Wedger % (and by price alone). On the dashed line = the chance was right.</p><div class="wg-key" id="nbt-cal-key"></div><div class="wg-chart" id="nbt-cal"></div></div>
        <div class="wg-bt-col"><div class="wg-lab">How well each read called Yes vs No</div><p class="wg-note">Gain over a coin flip in Brier score (lower Brier is better), every line in the sample.</p><div class="wg-bt-rows">
          {brier_rows(A, [('hit20', 'His last-20 hit rate', 'The filter, read as a chance'), ('cases', 'Minutes cases', 'Bear / base / bull by minutes'), ('model', 'Projection model', 'Matchup-adjusted projection'), ('ours_cal', 'Our read', 'Cases + projection, calibrated'), ('p', 'Price alone', 'Books, no vig'), ('wedger', 'Wedger %', '70% price + 30% our read')])}
          </div><p class="wg-note" style="margin-top:8px">Projection error (average miss): book line {mae['book_line']}, his average {mae['history_avg']}, minutes cases {mae['cases']}, adjusted projection {mae['adjusted']}.</p></div>
      </div>
      <script type="application/json" id="nbt-data">{bt_json}</script>
    </section>
    <section class="rs-card rs-method" id="nba-method">
      <h2>How the NBA screen and outlook work</h2>
      <p><b>Lines.</b> Every Robinhood NBA contract (Kalshi's order book, which Robinhood routes to) for games from Sat Oct 24 to Tue Oct 27: moneylines, spreads, totals, team totals, and player points, rebounds, assists, threes and points + rebounds + assists. Robinhood lists player props about a day ahead, so props cover tonight's games so far.</p>
      <p><b>Hit rate.</b> Player props: his last 20 games (2025-26 and 2026-27, any team). Team lines: that team's last 20 games; game totals: both teams' last 20. A line qualifies when its Yes price is 45–55¢ and the condition came true in more than half of those games (at least 10).</p>
      <p><b>Outlook.</b> Minutes cases: his games split into thirds by minutes, weighted toward this season and his last 15 games; each case's chance is his hit rate in those games nudged toward his overall rate, and tonight's case odds lean on his recent minutes and shift toward the bear case when the spread makes a blowout likelier than usual. Projection: the case average times tonight's adjustments (defense vs his position, pace, game script from the spread, implied team total, back-to-back, teammates out with his with/without record), capped at −25% / +30%. Our read averages the cases' chance with a gamma (points, PRA) or negative-binomial (rebounds, assists, threes) distribution priced at the projection, shrunk toward 50%; Wedger % = 70% the books' price for that rung + 30% our read. Injuries: CBS Sports injury report, Fri Oct 23 morning. Live record: each posted line settled against the final ESPN box score. Data: ESPN box scores via hoopR, Action Network book lines, Kalshi.</p>
    </section>
'''
open(D + 'rh/nba_bt_section.html', 'w').write(html_)
M_ = S['band_model']
tile_txt = {'num': pct(scr['win_pct']), 'note': f"Filter {scr['won']:,}–{scr['n'] - scr['won']:,} ({roi(scr['roi'])}); model {pct(M_['win_pct'])} ({roi(M_['roi'])}) on {A['n']:,} 2025-26 lines"}
json.dump(tile_txt, open(D + 'nba/nba_bt_tile.json', 'w'))
print('section', len(html_), tile_txt)
