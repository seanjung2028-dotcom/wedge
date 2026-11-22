"""Round 20 (Sun Nov 22): the Week 11 card is marked as the final draft of finals and leans, and the header says when the card lines'
Kalshi prices were last re-checked (F.draft and F.recheck_at from final11/build.py)."""


def apply(s, js):
    def jr(a, b, n=1):
        nonlocal js
        c = js.count(a); assert c == n, f'r20 js: {a[:70]!r} found {c}'; js = js.replace(a, b)
    jr("if (when) when.textContent = 'Prices checked ' + fcTime(F.at) + (F.mnf_at ? ' · BUF @ MIN re-checked ' + fcTime(F.mnf_at) : '');",
       "if (when) when.textContent = (F.draft ? F.draft + ' · ' : '') + 'Prices checked ' + fcTime(F.at) + (F.recheck_at ? ' · card lines re-checked ' + fcTime(F.recheck_at) : '') + (F.mnf_at ? ' · BUF @ MIN re-checked ' + fcTime(F.mnf_at) : '');")
    return s, js
