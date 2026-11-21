"""Round 17 (Wed Nov 18; slate moved to Thu Nov 19): the NBA board names the current slate.
The NBA copy written for the Oct 24-27 board now names the current slate, its pricing time and its injury source.
Change SLATE_* below (and nba/nba_lines.py) when the board moves to another slate."""
SLATE_TILE = 'Robinhood, Fri Nov 20'
SLATE_NOTE = "Robinhood NBA lines for Fri Nov 20’s late games, priced at 6:20 PM CT. Hit rate: last 20 games. Wedge %: ours. Books % is blank: book lines weren't pulled for this slate."
SLATE_GAMES = "for Fri Nov 20's 3 late games:"
SLATE_INJ = 'Injuries: ESPN injury report, Fri Nov 20 at 6:20 PM CT.'
SWAPS = [
    ('Robinhood, Sat Oct 24 – Tue Oct 27', SLATE_TILE),
    ("Robinhood NBA lines, Oct 24–27. Hit rate: last 20 games. Books %: sportsbooks' chance. Wedge %: ours.", SLATE_NOTE),
    ('for games from Sat Oct 24 to Tue Oct 27:', SLATE_GAMES),
    ('Injuries: CBS Sports injury report, Fri Oct 23 morning.', SLATE_INJ),
    ("Wedge % = 70% the books' price for that rung + 30% our read.",
     "Wedge % = 70% the books' price for that rung (the Robinhood mid when no book line was pulled) + 30% our read."),
    ('Data: ESPN box scores via hoopR, Action Network book lines, Kalshi.',
     'Data: ESPN box scores via hoopR, Action Network book lines (when pulled), Kalshi.'),
]


def apply(s, js):
    for a, b in SWAPS:
        if a not in s:
            raise ValueError('r17: missing ' + a[:50])
        s = s.replace(a, b)
    return s, js
