"""Flag Week 8 props for players on the official final injury report (Out / Doubtful / Questionable), from dl4/injuries_2026.csv."""
import pandas as pd, re, unicodedata
S = '/home/claude/wedger/'
def nn(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', s); return re.sub(r'[^a-z]', '', s)
inj = pd.read_csv(S + 'dl8/injuries_w8.csv'); inj = inj[(inj['week'] == 8) & inj['report_status'].isin(['Out', 'Doubtful', 'Questionable'])]
NOTE = {'matthewgolden': 'Questionable · limited Wed after missing Mon–Tue', 'lamarjackson': 'Questionable · expected to play', 'amonrastbrown': 'Questionable · expected to play'}
ST = {nn(r.full_name): NOTE.get(nn(r.full_name), r.report_status + (' · did not practice' if r.practice_status == 'Did Not Participate In Practice' else (' · limited in practice' if r.practice_status == 'Limited Participation in Practice' else ''))) for r in inj.itertuples(index=False)}
UNPLAYED = None  # every Week 8 game
def add(flags, st):
    f = [x for x in str(flags if isinstance(flags, str) else '').split('; ') if x and not x.startswith('Injury report:')]
    return '; '.join([f'Injury report: {st}'] + f)
for fn, col in (('inband_w8.csv', None), ('props_cat_w8.csv', 'player'), ('atd_w8.csv', 'player')):
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
