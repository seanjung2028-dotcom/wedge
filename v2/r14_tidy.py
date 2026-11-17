"""Round 14 (Tue Nov 17): each play on The Winning Edge drops its closing run-on line ("Market 52.5% (midpoint of bid and ask)
· matchup lens ... · ours ... · needs ... · margin ..."). Every number in it is already on the play: Price, Pays, Needs and
Our number at the top, the matchup lens with its net, and Market and Ours for every rung in the ladder table."""
import re
def apply(s, js):
    pat = re.compile(r"fcLadder\(p\),\n\s*el\('p', 'fc-brk', `[^`]*`\)\);")
    m = pat.findall(js); assert len(m) == 1, f'r14: fc-brk found {len(m)}'
    js = pat.sub("fcLadder(p));", js)
    return s, js
