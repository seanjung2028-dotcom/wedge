"""Round 19 (Sat Nov 21): two projections, one number.
Wedge % on receiving and rushing lines is now the lens number joined with the research method's own projection for the exact line
(bt/next_steps/brain_blend.py): lens x cos^2(theta) + research x sin^2(theta), theta averaged over 1,000 fits (bt/brain_blend.json).
This round updates the page's definitions to say so; the numbers themselves come from lens/v6.py."""
import json, math
W = '/home/claude/wedger/'
BB = json.load(open(W + 'bt/brain_blend.json'))
TH = BB['params'][0]; WPCT = round(100 * math.sin(TH) ** 2)
JOIN = (f"Since Nov 21 it is joined with the research method’s own projection for the exact line (his hit rate there over all 2026 games, "
        f"games in the expected script, one-score games and his last 3, shrunk to the price): lens × cos²θ + research × sin²θ, "
        f"with θ = {TH:.3f} averaged over {BB['runs']:,} fits, so the research projection carries {WPCT}%.")


def apply(s, js):
    def sr(a, b, n=1):
        nonlocal s
        c = s.count(a); assert c == n, f'r19 html: {a[:70]!r} found {c}'; s = s.replace(a, b)

    def jr(a, b, n=1):
        nonlocal js
        c = js.count(a); assert c == n, f'r19 js: {a[:70]!r} found {c}'; js = js.replace(a, b)
    jr("['Our number', 'The market’s midpoint, moved by the matchup lens. Weights fit on 10,123 settled Weeks 7–9 lines; range = 10th–90th percentile across refits.'],",
       "['Our number', 'The market’s midpoint, moved by the matchup lens (weights fit on 10,123 settled Weeks 7–9 lines). " + JOIN + " Range = 10th–90th percentile across refits.'],")
    jr("box: 'box count' })[k] || k}",
       "box: 'box count', research: 'research projection', look_x_volume: 'blitz split × pass volume' })[k] || k}")
    jr("Weights fit on 10,123 settled Weeks 7–9 Robinhood props; range ${pctR(O.lens.lo)}–${pctR(O.lens.hi)} across refits.",
       "Weights fit on 10,123 settled Weeks 7–9 Robinhood props; the research projection for this exact line is joined in at " + str(WPCT) + "% (the average of " + f"{BB['runs']:,}" + " fits); range ${pctR(O.lens.lo)}–${pctR(O.lens.hi)} across refits.")
    jr("Wedge %: the market midpoint moved by the matchup lens, fit on settled Weeks 7–9 lines.",
       "Wedge %: the market midpoint moved by the matchup lens, fit on settled Weeks 7–9 lines, then joined with the research projection for the exact line (" + str(WPCT) + "% weight, averaged over " + f"{BB['runs']:,}" + " fits).")
    sr('title="Wedge’s chance it settles Yes (v6): the market midpoint, moved by the matchup lens. Weights fit on 10,123 settled Weeks 7–9 Robinhood props, kept for receiving and rushing lines where they beat the market out of sample; passing, TD and interception lines stay at the market."',
       'title="Wedge’s chance it settles Yes (v6): the market midpoint, moved by the matchup lens. Weights fit on 10,123 settled Weeks 7–9 Robinhood props, kept for receiving and rushing lines where they beat the market out of sample; passing, TD and interception lines stay at the market. '
       + f'On receiving and rushing lines it is joined with the research projection for the exact line ({WPCT}% weight, θ averaged over {BB["runs"]:,} fits)."')
    return s, js
