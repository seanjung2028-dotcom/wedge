"""Flag Week 7 props for players on the official final injury report (Out / Doubtful / Questionable), from dl4/injuries_2026.csv."""
import pandas as pd, re, unicodedata
S = '/home/claude/wedger/'
def nn(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b\.?', '', s); return re.sub(r'[^a-z]', '', s)
inj = pd.read_csv(S + 'dl4/injuries_2026.csv'); inj = inj[(inj['week'] == 7) & inj['report_status'].isin(['Out', 'Doubtful', 'Questionable'])]
ST = {nn(r.full_name): r.report_status for r in inj.itertuples(index=False)}
UNPLAYED = {'DAL @ PHI'}
def add(flags, st):
    f = [x for x in str(flags if isinstance(flags, str) else '').split('; ') if x and not x.startswith('Injury report:')]
    return '; '.join([f'Injury report: {st}'] + f)
for fn, col in (('inband_w7.csv', None), ('props_cat_w7.csv', 'player'), ('atd_w7.csv', 'player')):
    d = pd.read_csv(S + 'rh/' + fn, dtype=str, keep_default_na=False)
    n = 0; drop = []
    for i, r in d.iterrows():
        if r['game'] == 'NE @ CHI': continue
        name = r[col] if col else (r['contract'].split(':')[0] if ':' in r['contract'] else r['contract'])
        st = ST.get(nn(name))
        if st: d.at[i, 'flags'] = add(r['flags'], st); n += 1
        # Monday refresh: a sportsbook line still up for a player ruled Out is stale; drop it for the unplayed game
        if st == 'Out' and r['game'] in UNPLAYED and r.get('source', '') != 'Robinhood' and not str(r.get('id', '')).startswith('C'): drop.append(i)
    d = d.drop(index=drop)
    d.to_csv(S + 'rh/' + fn, index=False)
    print(fn, 'flagged', n, 'dropped stale Out lines', len(drop))
