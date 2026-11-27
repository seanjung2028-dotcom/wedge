"""Round 24 (Fri Nov 27 evening): Week 12's finals join the final-line record (bt/w12_record/add_w12.py). The owner counts Week 12
but not Week 11, so the labels come from the data ("Weeks 1–10, 12") instead of "Weeks 1–<thru>", Week 11 shows as not counted
rather than "No final line", and the note says so (plus any Week 12 line still to be graded)."""


def apply(s, js):
    def jr(a, b, n=1):
        nonlocal js
        c = js.count(a); assert c == n, f'r24 js: {a[:70]!r} found {c}'; js = js.replace(a, b)
    jr("        $('#frec-label').textContent = `Final lines · Weeks 1–${thru}`;",
       "        $('#frec-label').textContent = r.label || `Final lines · Weeks 1–${thru}`;\n        frecSkip = String(r.skip || '').split(',').filter(Boolean).map(Number); frecNote = r.note || '';")
    jr("    let thru = 10;\n", "    let thru = 10; let frecSkip = []; let frecNote = '';\n")
    jr("    $('#frec-note').textContent = 'Backtested, brainstormed, and settled.';", "    $('#frec-note').textContent = frecNote || 'Backtested, brainstormed, and settled.';")
    jr("      head.append(el('b', null, 'Week ' + wk), el('span', null, rows.length ? `${w}–${rows.length - w}` : (wk === 1 ? 'No games before it' : 'No final line')));",
       "      head.append(el('b', null, 'Week ' + wk), el('span', null, rows.length ? `${w}–${rows.length - w}` : (frecSkip.includes(wk) ? 'Not counted' : (wk === 1 ? 'No games before it' : 'No final line'))));")
    jr("wzSet('frec-label', `Final-line hit rate · Weeks 1–${fr.thru}, incl. backtest`);", "wzSet('frec-label', `Final-line hit rate · Weeks ${fr.weeks}, incl. backtest`);")
    jr("subEl.textContent = `Final lines, Weeks 1–${fr.thru} (with the backtest)`;", "subEl.textContent = `Final lines, Weeks ${fr.weeks} (with the backtest)`;")
    jr("return { w, n, p: Number(r.win_pct), roi: Number(r.roi_pct), thru: Number(r.thru) || 10 };",
       "return { w, n, p: Number(r.win_pct), roi: Number(r.roi_pct), thru: Number(r.thru) || 10, weeks: r.weeks || ('1–' + (Number(r.thru) || 10)) };")
    return s, js
