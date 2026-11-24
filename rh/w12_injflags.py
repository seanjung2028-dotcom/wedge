"""Flag Week 9 props for players on the official final injury report (Out / Doubtful / Questionable), from dl18/injuries_w12.csv."""
import pandas as pd, re, unicodedata
S = '/home/claude/wedger/'
def nn(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', s); return re.sub(r'[^a-z]', '', s)
inj = pd.read_csv(S + 'dl18/injuries_w12.csv'); inj = inj[inj['week'] == 12]
LIM = ('Did Not Participate In Practice', 'Limited Participation in Practice')
inj = inj[inj['report_status'].isin(['Out', 'Doubtful', 'Questionable']) | (inj['practice_status'].isin(LIM) & inj['position'].isin(['QB', 'RB', 'WR', 'TE']))]
NOTE = {}  # Week 12: statuses come from the official reports and ESPN (Tue Nov 17); hand notes added as news lands
def _txt(r):
    rs = r.report_status if isinstance(r.report_status, str) else ''
    sun = r.team not in ('CAR', 'GB')
    pr = {'Did Not Participate In Practice': 'did not practice' + ('' if sun else ''), 'Limited Participation in Practice': 'limited in practice' + ('' if sun else '')}.get(r.practice_status, '')
    if pr and str(r.practice_primary_injury).startswith('Not injury related'): pr = 'rest day' + ('' if sun else '')
    if rs and pr: return rs + ' · ' + pr
    return rs or (pr[0].upper() + pr[1:])
ST = {nn(r.full_name): NOTE.get(nn(r.full_name), _txt(r)) for r in inj.itertuples(index=False)}
ST.update(NOTE)
UNPLAYED = None  # every Week 8 game
def add(flags, st):
    f = [x for x in str(flags if isinstance(flags, str) else '').split('; ') if x and not x.startswith('Injury report:')]
    return '; '.join([f'Injury report: {st}'] + f)
for fn, col in (('inband_w12.csv', None), ('props_cat_w12.csv', 'player'), ('atd_w12.csv', 'player'), ('lines_all_w12.csv', None)):
    d = pd.read_csv(S + 'rh/' + fn, dtype=str, keep_default_na=False)
    n = 0; drop = []
    for i, r in d.iterrows():
        name = r[col] if col else (r['contract'].split(':')[0] if ':' in r['contract'] else r['contract'])
        st = ST.get(nn(name))
        if st: d.at[i, 'flags'] = add(r['flags'], st); n += 1
        # Monday refresh: a sportsbook line still up for a player ruled Out is stale; drop it for the unplayed game
        if st and st.startswith('Out') and True and r.get('source', '') != 'Robinhood' and not str(r.get('id', '')).startswith('C'): drop.append(i)
    d = d.drop(index=drop)
    d.to_csv(S + 'rh/' + fn, index=False)
    print(fn, 'flagged', n, 'dropped stale Out lines', len(drop))
