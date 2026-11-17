# Wedge

Wedge screens NFL player-prop and game lines on Kalshi and Robinhood, prices them with its own model, and publishes a weekly card of final lines and conditional leans. The card, the board, projections and a graded record all live on a hosted dashboard page. This repo is the code behind that page and the weekly pipeline that feeds it.

This is a working snapshot from Week 10 of the 2026 season, exported from the session workspace. Raw downloads and generated datasets are left out; see **Not in this repo** below.

## How a week runs

1. **Pull inputs.**
   - nflverse player stats, play-by-play, snap counts and schedules come from GitHub releases into `dlNN/` (not committed).
   - Kalshi ladders (props, spreads, totals, winners) and ESPN injury reports come in through a browser pull and are saved as JSON in `pullMMDD/`.
   - Kickoff-hour weather comes from open-meteo.
2. **Build inputs.** `w10/build_inj.py` and `w10/build_inputs.py` turn the pulls into the files the chain reads.
3. **Run the chain.**
   - Features and adjustments run first: `mom/pg_next_w10.py`, `arch/build_feat_w10.py` and `bt/rff_w10.py`.
   - Then the board chain in `rh/w10_*.py` runs in this order: `events, analyze, build_inband, categorize, atd, keep_certs, totals, splits, matchup, reads_cand, model, proj_exp, build_all, injflags, game_reads`.
   - Last, `v2/data_v2_w10.py` builds the site's data files.
4. **Build the card.** `final10/build.py` builds each game's card (final lines, conditional leans and passes), then `final10/make_final_js.py` writes `final.js` and `brain.js`.
5. **Build the site.**
   - Build with `v2/build_v2.py`, then `v2/split_v2.py`, then `v2/hbuild.py`. The last one writes a local harness page you can test.
   - Run the checks: `node v2/t16.js <harness.html>` covers every page, and `node v2/t17.js <harness.html> <shots dir>` saves screenshots.
6. **Publish.**
   - The page is a dashboard artifact. Each dataset is a CSV uploaded as an asset and pointed to by a `datasets/<id>` document.
   - The page itself is the `files/` documents: `index.html`, `wg.js`, `wg.css`, `final.js` and `brain.js`.
   - `v2/blobmap.json` maps local asset ids to the live ones.
   - The standalone website is `site/`, built by `v2/build_site.py` (see **Standalone website** below).
7. **Settle.**
   - `bt/settle_w10.py` (Thursday) and `bt/settle_w10s.py` (Sunday) grade every posted line from the box scores.
   - `bt/results_w10.py` writes the record file, `rh/results_w6_w10.csv`.
   - Certified picks are the `wedger/certs` document; `rh/certs_seed.json` is the local copy.
   - `python3 bt/card_bt/summary.py` refreshes the card records on Results (backtest vs. live card) from every graded `finalNN/final_wNN.json`.
8. **Card backtest, Weeks 1–9** (`bt/card_bt/`, shown on Results):
   - `pool_real.py`: Weeks 7–9 real Robinhood main lines from the record, with point-in-time lens features.
   - `pool_rebuilt.py`: Weeks 2–6 lines rebuilt from box scores the way the books set them (fit and checked on the real Week 7–9 lines; `rebuild_check.json`). Robinhood kept no prop prices before Week 7.
   - `card_bt.py`: the Week 11 card rules (v6 range, the checks, one line per player, four per game, the card mix), with v6 refit without the week for Weeks 7–9. Writes `rh/card_bt.csv` and `rh/card_bt_sum.csv` through `summary.py`. Results shows the final-line record (Weeks 1–9) at the top; `EXCLUDE` in `summary.py` lists the four lines the owner left out (noted on the page). `ADDED` lists Wedge picks the owner added to it by hand, and the Week 10 card's certified finals follow; together they are `rh/final_record.csv`.

## Website and memberships (live at https://wedgepicks.com)

`site/` is the public website: the same pages as the dashboard artifact, served by Cloudflare Pages with a small server in `functions/` for sign-in and paid access.

- **Who sees what:**
  - Everyone: Home, the Subscribe and Sign-in pages, and the headline record.
  - Research (Tier 1, $19.99 a month): Research, Charts & Trends, Analysts and Results, for the NFL and NBA.
  - Inner Circle (Tier 2, $119.99 for the season): everything in Research, plus The Winning Edge (final lines and leans) and the Thesis.
  - Analysts: everything.
  - Locked pages show a blurred picture of the page (`site/assets/locked/`) with a way to subscribe or sign in. The paid data itself never reaches a visitor without access.
- **Files:**
  - `site/index.html`, `wg.js`, `wg.css`: the page. `runtime.js` asks `/api/me` who is signed in, then loads what that visitor may see.
  - `site/data/public.json`, `final-public.js`, `brain-public.js`: what everyone gets (the settled certified record; this week's games and scores, no picks).
  - `lib/protected/`: the paid files (all datasets, the full card), gzipped. They are bundled into the `/p/` function, not served as static files.
  - `functions/api/`: `me`, `login` (emails a 6-digit code), `verify`, `logout`, `stripe` (webhook). `functions/p/[[path]].js` checks the visitor's level before serving a paid file. Shared code: `lib/wedge.js`.
  - Versioned `?v=<hash>` URLs let browsers cache everything; a new build shows up on the next visit.
- **Settings** (Cloudflare: Workers & Pages > wedgepicks > Settings): `WEDGE_GATING` (`on` locks paid pages; anything else keeps the site open), `SESSION_SECRET`, `RESEND_API_KEY`, `MAIL_FROM`, `STRIPE_WEBHOOK_SECRET`, `CHECKOUT_RESEARCH`, `CHECKOUT_INNER`, `BILLING_PORTAL`, `SEASON_END`, `ANALYST_EMAILS`, `INNER_EMAILS`, `RESEARCH_EMAILS`, and the KV binding `WEDGE`. Each is described at the top of `lib/wedge.js`.
- **Rebuild:** `python3 v2/build_v2.py && python3 v2/split_v2.py && python3 v2/build_site.py`, then sync. `--fast` skips re-rendering the blurred previews.
- **Test locally:** `npm i wrangler@4` in a scratch folder, then from the repo root run `wrangler pages dev site --kv WEDGE --binding WEDGE_GATING=on --binding SESSION_SECRET=test --binding ANALYST_EMAILS=you@example.com`. Without an email key, sign-in shows the code on the page (local only).
- **Host:** Cloudflare Pages project `wedgepicks`, branch `main`, no build command, output directory `site`. Pages builds `functions/` automatically. Each push to `main` redeploys.

## The model

- **Wedge % (v6):** see `lens/v6.py` and `lens/core.py`.
  - It starts from the market midpoint, then moves receiving and rushing lines by backtested matchup features: what the defense allows, where the targets go, the blitz split, run direction, box count, volume, comparable defenses and consistency at the number.
  - Passing, TD and interception lines stay at the market.
  - Weights live in `bt/cal_v6.json` and the out-of-sample report in `bt/rep_v6.json`, both fit with `bt/fit_v6.py`.
- **Research checks:** see `brain/gates.py` and `final10/brain_layer.py`.
  - A line must clear on price and pass several checks before it can be a final:
    - no backup quarterback in the game
    - a steady role
    - the side clearing in the likely game script and in close games
    - for overs, not leaning on fourth-quarter work
  - `bt/brain_bt.py` backtests the checks on Weeks 7–9.
  - The method itself is `brain/OG_Brain_Master_Prompt_Pre_YouTube_2026-11-13.md`. Keep it private.
- **Card mix:** about one under for every three overs, set by `RATIO` in `final10/brain_layer.py`. Unders that still clear but are left off for the mix are marked as passes with that reason.

## Layout

| Folder | What it holds |
|---|---|
| `lens/` | Matchup tables, features and the v6 probability |
| `bt/` | Backtests, model fits, settlement and record building |
| `brain/` | Research checks and the saved method baseline |
| `final10/`, `final9*/` | Card builders for Weeks 10 and 9 |
| `rh/` | Weekly board chain, plus the base page (`index_full.html`, `wg.js`, `wg.css`) |
| `v2/` | Site version 2: source in `v2/src`, patches (`r8_week.py`, `r9_week10.py`), build, harness and tests. `v2/out` is the last built site. |
| `arch/`, `mom/` | Play-level features, defensive adjustments and momentum inputs |
| `w8/`, `w9/`, `w10/` | Per-week input builders and small input files |
| `pullMMDD/` | Raw Kalshi and ESPN pulls by date (inputs that can't be fetched again later) |
| `picklog/`, `certs10/` | Pick log rows and Week 10 certified final rows added to the record |
| `nba/`, `helm/`, `photos/`, `harness/` | NBA work, helmet art build, player photo tooling, older test harness |

## Running it elsewhere

- **Paths:** the scripts use an absolute base path, `W = '/home/claude/wedger/'`. Point that at your clone, or replace it with an environment variable, before running.
- **Python packages:** pandas, numpy, scikit-learn and requests.
- **Node:** Playwright, for the page tests.

## Not in this repo

- nflverse downloads (`dl*/`, `nflverse_dl*/`). They come back with the same release URLs.
- Generated weekly datasets (board, projections, outlooks, splits) and harness pages. Rerun the pipeline to rebuild them.
- Live-site store snapshots, brand studies and image assets.
- The raw Nov 8–12 pick log. Its verified rows are in `picklog/rows_nov8_12.csv`.

`rh/check.js`, `v2/v1_js.js`, `rh/wg.js`, `v2/out/wg.js` and `site/wg.js` contain the site owner's contact email (it's on the published page). Keep the repo private or remove it before sharing.
