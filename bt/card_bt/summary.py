"""Records for the Results tab: the backtested card (bt/card_bt/card.pkl, from card_bt.py) next to the live card as it settled
(final10/ onward, every graded play) and the Week 9 card as posted. Fast; rerun after each settle.
Writes rh/card_bt.csv (every backtested pick) and rh/card_bt_sum.csv (records)."""
import json, math, os
import numpy as np, pandas as pd
W = '/home/claude/wedger/'; FEE = 2.0
CARD = pd.read_pickle(W + 'bt/card_bt/card.pkl')
# ---------------- the live card, settled (Week 10 onward, v6) and the Week 9 card as posted (before v6)
def live(path, wk, label):
    F = json.load(open(W + path)); out = []
    for c in F['cards']:
        for p in c['plays']:
            r = p.get('result') or {}
            if r.get('outcome') not in ('Won', 'Lost'): continue
            out.append({'src': label, 'week': wk, 'game': c['game'], 'line': p['line'], 'side': p.get('side', 'Yes'), 'price': p['price'], 'be': p.get('be', p['price'] + FEE),
                        'mid': p.get('mid'), 'lo': p.get('lo'), 'hi': p.get('hi'), 'decision': p['decision'], 'win': int(r['outcome'] == 'Won'), 'profit': r['profit_c']})
    return pd.DataFrame(out)
import glob, re as _re
LIVE = pd.concat([live(f'final{n}/final_w{n}.json', n, 'live') for n in range(10, 23) if os.path.exists(W + f'final{n}/final_w{n}.json')] +
                 [live('final9/final_w9.json', 9, 'posted9')], ignore_index=True)
LIVE_THRU = int(LIVE[LIVE.src == 'live'].week.max()) if (LIVE.src == 'live').any() else 10
def rec(x, key, label, group, src, week='', tier=''):
    n = len(x); w = int(x.win.sum()) if n else 0; cost = float(x.price.sum()) if n else 0
    return {'key': key, 'label': label, 'group': group, 'src': src, 'week': week, 'tier': tier, 'wins': w, 'losses': n - w,
            'win_pct': round(100 * w / n, 1) if n else None, 'avg_price': round(cost / n, 1) if n else None,
            'needed': round(float(x.be.mean()), 1) if n else None, 'ours': round(float(pd.to_numeric(x.mid, errors='coerce').mean()), 1) if n and pd.to_numeric(x.mid, errors='coerce').notna().any() else None,
            'profit_c': int(round(float(x.profit.sum()))) if n else 0, 'roi_pct': round(100 * float(x.profit.sum()) / cost, 1) if cost else None}
TN = {'Final line': ('final', 'Final lines'), 'Conditional lean': ('lean', 'Conditional leans')}
S = []
for tier, (tk, tl) in TN.items():
    bt = CARD[(CARD.decision == tier) & CARD.src.isin(['real', 'rebuilt'])]
    S.append(rec(bt, f'{tk}_bt', f'{tl} · backtest, Weeks 1–9', 'compare', 'backtest', '', tk))
    S.append(rec(CARD[(CARD.decision == tier) & (CARD.src == 'real')], f'{tk}_real', f'{tl} · Weeks 7–9, real prices', 'compare', 'real', '', tk))
    S.append(rec(CARD[(CARD.decision == tier) & (CARD.src == 'rebuilt')], f'{tk}_rebuilt', f'{tl} · Weeks 1–6, rebuilt lines', 'compare', 'rebuilt', '', tk))
    S.append(rec(LIVE[(LIVE.decision == tier) & (LIVE.src == 'live')], f'{tk}_live', f'{tl} · live card, since Week 10', 'compare', 'live', '', tk))
for tier, (tk, tl) in TN.items():
    for side, sl in (('Yes', 'overs'), ('No', 'unders')):
        S.append(rec(CARD[(CARD.decision == tier) & CARD.src.isin(['real', 'rebuilt']) & (CARD.side == side)], f'{tk}_bt_{side}', f'{tl} · backtest {sl}', 'side', 'backtest', '', tk))
MIXCUT = pd.read_pickle(W + 'bt/card_bt/mixcut.pkl')
for tier, (tk, tl) in TN.items():
    S.append(rec(MIXCUT[(MIXCUT.decision == tier) & MIXCUT.src.isin(['real', 'rebuilt'])], f'{tk}_mixcut', f'{tl} · unders left off for the card mix', 'side', 'backtest', '', tk))
for wk in range(1, 10):
    src = 'real' if wk >= 7 else 'rebuilt'
    for tier, (tk, tl) in TN.items():
        S.append(rec(CARD[(CARD.decision == tier) & (CARD.src == src) & (CARD.week == wk)], f'w{wk}_{tk}', f'Week {wk} · {tl.lower()}', 'week', src, wk, tk))
for wk in sorted(LIVE[LIVE.src == 'live'].week.unique()):
    for tier, (tk, tl) in TN.items():
        S.append(rec(LIVE[(LIVE.decision == tier) & (LIVE.src == 'live') & (LIVE.week == wk)], f'w{wk}_{tk}', f'Week {wk} · {tl.lower()} (live card)', 'week', 'live', int(wk), tk))
for tier, (tk, tl) in TN.items():
    S.append(rec(LIVE[(LIVE.decision == tier) & (LIVE.src == 'posted9')], f'p9_{tk}', f'Week 9 · {tl.lower()}, card as posted (before v6)', 'check', 'posted9', 9, tk))
    S.append(rec(CARD[(CARD.decision == tier) & (CARD.src == 'real') & (CARD.week == 9)], f'b9_{tk}', f'Week 9 · {tl.lower()}, backtest', 'check', 'real', 9, tk))
    S.append(rec(CARD[(CARD.decision == tier) & (CARD.src == 'check')], f'c79_{tk}', f'Weeks 7–9 · {tl.lower()} on rebuilt lines (check)', 'check', 'check', '', tk))
SUM = pd.DataFrame(S)
PK = CARD[CARD.src.isin(['real', 'rebuilt'])].copy()
PK['outcome'] = np.where(PK.win == 1, 'Won', 'Lost')
UNIT = {'rec': 'rec', 'recyd': 'rec yds', 'rushyd': 'rush yds', 'rryd': 'rush + rec yds'}
PK['result'] = [f"W{w}: {int(a)} {UNIT[s]}" for w, a, s in zip(PK.week, PK.actual, PK.stat)]
PK['prices'] = np.where(PK.src == 'real', 'Real price', 'Rebuilt line')
PK = PK.sort_values(['week', 'decision', 'game', 'line'], ascending=[True, False, True, True]).reset_index(drop=True)
PK['id'] = [f'BT{i + 1:03d}' for i in range(len(PK))]
PK['est'] = [f"{lo:.0f}–{hi:.0f}%" for lo, hi in zip(PK.lo, PK.hi)]
PK[['id', 'week', 'prices', 'game', 'decision', 'line', 'side', 'price', 'be', 'mkt', 'lo', 'mid', 'hi', 'est', 'outcome', 'result', 'profit']].rename(columns={'profit': 'profit_c', 'be': 'needed'}).to_csv(W + 'rh/card_bt.csv', index=False)
SUM.to_csv(W + 'rh/card_bt_sum.csv', index=False)
pd.set_option('display.width', 220)
print(SUM[['key', 'wins', 'losses', 'win_pct', 'avg_price', 'needed', 'ours', 'profit_c', 'roi_pct']].to_string())
