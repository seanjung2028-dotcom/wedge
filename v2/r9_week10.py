"""Round 9 (Tue Nov 10): the site moves to Week 10 and Wedge % v6 (market midpoint moved by the backtested matchup lens)."""
import re
def apply(s, js):
    def jr(a, b, n=None):
        nonlocal js
        c = js.count(a); assert c >= 1 and (n is None or c == n), f'r9: {a[:70]!r} found {c}'; js = js.replace(a, b)
    jr("const CERT_WEEK = 'w9';", "const CERT_WEEK = 'w10';", 1)
    jr("{ week: 9, game:", "{ week: 10, game:", 2)
    jr("['Our number', 'The market’s curve, shifted by role, matchup, script and personnel.'],",
       "['Our number', 'The market’s midpoint, moved by the matchup lens. Weights fit on 10,123 settled Weeks 7–9 lines; range = 10th–90th percentile across refits.'],", 1)
    jr("['Pass', 'Nothing beats Needs at our middle, or the evidence is thin.'],", "['Pass', 'Nothing beats Needs at our middle.'],", 1)
    jr("our shift ${p.shift > 0 ? '+' : '−'}${Math.abs(p.shift)} ${unit} from ${p.pts} evidence points",
       "matchup lens ${p.pts > 0 ? '+' : '−'}${Math.abs(p.pts)} pts (about ${p.shift > 0 ? '+' : '−'}${Math.abs(p.shift)} ${unit})", 1)
    jr("Wedge %: the price shifted by its market’s over bias.", "Wedge %: the market midpoint moved by the matchup lens, fit on settled Weeks 7–9 lines.")

    jr("      : O.cal === 'v5'\n        ? `Wedge (model v5)",
       "      : O.cal === 'v6'\n        ? (O.lens ? `Wedge (v6) = the market midpoint (${pctR(O.lens.mid)}), moved by the matchup lens: ${Object.entries(O.lens.c).filter(([, v]) => Math.abs(v) >= 0.15).map(([k, v]) => `${({ dvp: 'what the defense allows', overlap: 'where the targets go', look: 'against the blitz', volume: 'volume the defense faces', comp: 'comparable defenses', consist: 'consistency', dir: 'run direction', box: 'box count' })[k] || k} ${v > 0 ? '+' : '−'}${Math.abs(v).toFixed(1)}`).join(', ') || 'no step moves it'} points. Weights fit on 10,123 settled Weeks 7–9 Robinhood props; range ${pctR(O.lens.lo)}–${pctR(O.lens.hi)} across refits. ${pickTxt}Yes = ${cond}.` : `Wedge (v6) = the market midpoint. The lens didn’t beat the market on passing, TD or interception lines in the backtest, so these stay at the market. ${pickTxt}Yes = ${cond}.`)\n      : O.cal === 'v5'\n        ? `Wedge (model v5)", 1)
    jr("If the line posts at ${line} for 50¢, Wedge would be about ${pctR(P)}: model v5 shifts the price by how often these overs came true at their price in Weeks 6–8 (passing yards more often, rushing and receiving yards less).",
       "If the line posts at ${line} for 50¢, Wedge would be about ${pctR(P)}: v6 moves 50¢ by the matchup lens (receiving and rushing lines; passing stays at the market).", 1)

    def sr(a, b):
        nonlocal s
        c = s.count(a); assert c >= 1, f'r9 page: {a[:70]!r}'; s = s.replace(a, b)
    import re as _re
    s = _re.sub(r'title="Wedge’s chance it settles Yes \(model v5\):[^"]*"', 'title="Wedge’s chance it settles Yes (v6): the market midpoint, moved by the matchup lens. Weights fit on 10,123 settled Weeks 7–9 Robinhood props, kept for receiving and rushing lines where they beat the market out of sample; passing, TD and interception lines stay at the market."', s)
    s = _re.sub(r'title="Yards and catches: Wedge % if the line posts at this number for 50¢ \(model v5:[^"]*"', 'title="Yards and catches: Wedge % if the line posts at this number for 50¢ (v6: 50¢ moved by the matchup lens). Anytime TDs: our read with the TD calibration. Click for the outlook."', s)
    s = s.replace("Since Week 9 (model v5), Wedge % is the market price shifted by its market's over bias on Weeks 6–8 and our read is shown for reference", "Since Week 10 (v6), Wedge % is the market midpoint moved by the backtested matchup lens; last week (v5) it was the price shifted by its market's over bias, with our read shown for reference")
    for t in ('s', 'js'):
        v = s if t == 's' else js
        v = re.sub(r'\bWeek 9\b', 'Week 10', v)
        v = v.replace('Sat Nov 7 at 2:25 PM CT', 'Mon Nov 16 at 9:27 AM CT').replace('Sat Nov 7, 2:25 PM CT', 'Mon Nov 16, 9:27 AM CT')
        if t == 's': s = v
        else: js = v
    return s, js
