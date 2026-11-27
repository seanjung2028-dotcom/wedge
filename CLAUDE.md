# Wedge repo

This repo mirrors the Wedge workspace (the weekly NFL pipeline, model, research checks and site source). The site is a dashboard artifact; this repo is its code and records.

The public site is **https://wedgepicks.com** (and www). It's the Cloudflare Pages project `wedgepicks`, connected to this repo: production branch `main`, no build command, output directory `site`. Every push to `main` redeploys it, and `wedgepicks.pages.dev` is the same deploy. The domain is registered at Namecheap, and its DNS is on Cloudflare (two proxied CNAMEs, `@` and `www`, both pointing to `wedgepicks.pages.dev`).

**Standing instruction from the owner:** every time the site is updated (new prices, settled results, card changes, record changes, code changes), sync this repo and push to `main` in the same turn.

- First rebuild the website: `python3 /home/claude/wedger/v2/build_site.py` (after `build_v2.py` and `split_v2.py` when the page changed). It writes `site/` from `v2/out/`, the dataset CSVs and `rh/certs_seed.json` / `rh/analysts_seed.json`. Refresh those two seeds from the live `wedger/certs` and `wedger/analysts` docs whenever they change. The host redeploys `site/` on every push to `main`.
- Sync with `python3 /home/claude/wedger/sync_repo.py "<what changed>"`. A copy of the script is at `sync_repo.py` in the repo root. It copies code, configs, records and raw pulls from the workspace into this repo, commits, and pushes. If nothing changed, it pushes nothing.
- Leave out raw downloads, generated datasets, store snapshots and anything with personal notes. The script's filter already does this.
- Keep the repo private. `rh/check.js`, `v2/v1_js.js` and the built `wg.js` files (including `site/wg.js`) contain the owner's contact email.
- Memberships (see README, "Website and memberships"): never put paid data in `site/`. The build puts it in `lib/protected/`, which the `/p/` function serves only to signed-in members of the right tier. The paywall is off until `WEDGE_GATING=on` is set in the Cloudflare project.
- The claude.ai artifacts (Wedge, Wedger) are being made private by the owner; wedgepicks.com is the public site.
- Pick rules: from Sunday of Week 12 the card uses `brain/rules.py` v3 (set by the owner Fri Nov 27) with the research method Independent Sports Research v1 (`brain/ISR_Clone_v1_2026-11-24.md`, `brain/isr.py`), which replaces the earlier method. The 70% bar and 75¢ cap stay; a line priced 50–75¢ under the bar is a final only if our number is significantly above its break-even (`brain/sig.py`); up to five lines a game; the method's extra markets reach the card only on a research case, at the market's number. Never show the spec's 51/60 ledger on the site. Wednesday–Friday of Week 12 stay as posted under v2 (ranked by chance, 75¢ cap, 70% bar, backup-QB games kept, no under/over mix); Weeks 7–11 under v1. See README, "The model".
