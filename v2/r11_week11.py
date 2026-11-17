"""Round 11 (Tue Nov 17): the site moves to Week 11. Labels, the cert week and the price-check time move on by one;
"Since Week 10 (v6)" stays, since v6 started then."""
import re
def apply(s, js):
    def jr(a, b, n=None):
        nonlocal js
        c = js.count(a); assert c >= 1 and (n is None or c == n), f'r11: {a[:70]!r} found {c}'; js = js.replace(a, b)
    jr("const CERT_WEEK = 'w10';", "const CERT_WEEK = 'w11';", 1)
    jr("{ week: 10, game:", "{ week: 11, game:", 2)
    # games whose player ladders haven't opened yet say so instead of "Pass" (card field `wait`)
    jr(".filter(Boolean).join(' · ') : 'Pass';", ".filter(Boolean).join(' · ') : (c.wait ? 'Props soon' : 'Pass');", 1)
    jr("if (!f && !l) tags.append(el('i', 'fc-badge fc-pass', 'Pass'));", "if (!f && !l) tags.append(el('i', 'fc-badge fc-pass', c.wait ? 'Props soon' : 'Pass'));", 1)
    jr("if (!nF && !nL) tags.append(el('span', 'fc-badge fc-pass', 'Pass'));", "if (!nF && !nL) tags.append(el('span', 'fc-badge fc-pass', c.wait ? 'Props soon' : 'Pass'));", 1)
    jr("  function v2PassCard(c) {\n    const d = el('div', 'wx-read v2-read is-pass');",
       "  function v2PassCard(c) {\n    if (c.wait) { const w = el('div', 'wx-read v2-read is-pass'); const wt = el('span', 'wx-read-top'); wt.append(el('span', null, v2Kick(c)), fcBadge('Props soon'));"
       " w.append(wt, wzWords('Player props open later in the week.'), el('span', 'v2-read-why', 'The game lines are on the board now. The card fills in once the player ladders post.')); return w; }\n    const d = el('div', 'wx-read v2-read is-pass');", 1)
    out = []
    for v in (s, js):
        v = v.replace('Since Week 10 (v6)', '@@SINCE@@')
        v = re.sub(r'\bWeek 10\b', 'Week 11', v)
        v = v.replace('@@SINCE@@', 'Since Week 10 (v6)')
        v = v.replace('Mon Nov 16 at 9:27 AM CT', 'Tue Nov 17 at 6:23 AM CT').replace('Mon Nov 16, 9:27 AM CT', 'Tue Nov 17, 6:23 AM CT')
        out.append(v)
    return out[0], out[1]
