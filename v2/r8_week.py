"""Round 8 (Mon Nov 9): graded Sunday results and the matchup lens on The Winning Edge's game cards and board."""
def apply(s, js):
    def jr(a, b, n=1):
        nonlocal js
        c = js.count(a); assert c == n, f'r8: expected {n} of {a[:80]!r}, found {c}'; js = js.replace(a, b)
    jr("    top.append(fcBadge(p.decision), el('h4', null, p.line));",
       "    top.append(fcBadge(p.decision), el('h4', null, p.line));\n    if (p.result) top.append(v2Res(p.result));")
    jr("      ['Where it loses', p.loses],\n", "      ['Where it loses', p.loses],\n      ['Matchup lens', p.lens ? v2Ledger(p.lens) : null],\n")
    jr("    if (!nF && !nL) tags.append(el('span', 'fc-badge fc-pass', 'Pass'));",
       "    if (!nF && !nL) tags.append(el('span', 'fc-badge fc-pass', 'Pass'));\n    if (c.status === 'Final') { const rc = v2Rec(c); tags.prepend(el('span', 'fc-badge v2-fin', 'Final' + (c.score ? ' · ' + c.score : ''))); if (rc) tags.append(el('span', 'fc-badge fc-lean', 'Card ' + rc)); }")
    jr("if (when) when.textContent = 'Prices checked ' + fcTime(F.at);",
       "if (when) when.textContent = 'Prices checked ' + fcTime(F.at) + (F.mnf_at ? ' · BUF @ MIN re-checked ' + fcTime(F.mnf_at) : '');")
    jr("stats.append(st(nF, 'final lines', 'g'), st(nL, 'conditional leans'), st(nP, 'considered and passed'), st(F.cards.length, 'games'));",
       "stats.append(st(nF, 'final lines', 'g'), st(nL, 'conditional leans'), st(nP, 'considered and passed'), st(F.cards.length, 'games'));\n"
       "    if (F.graded) stats.append(st(`${F.graded.final[0]}–${F.graded.final[1]}`, 'final lines, graded'), st(`${F.graded.lean[0]}–${F.graded.lean[1]}`, 'leans, graded'));")
    jr("const tdC = el('td'); tdC.append(fcBadge(p.decision));", "const tdC = el('td'); tdC.append(fcBadge(p.decision)); if (p.result) tdC.append(v2Res(p.result, true));")
    jr("all.sort((x, y) => (x[1].decision", "all.sort((x, y) => (!!x[1].result - !!y[1].result) || (x[1].decision")
    return s, js
