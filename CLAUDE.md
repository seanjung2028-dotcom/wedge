# Wedge repo

This repo mirrors the Wedge workspace (the weekly NFL pipeline, model, research checks and site source). The live site is a dashboard artifact; this repo is its code and records.

**Standing instruction from the owner:** every time the site is updated (new prices, settled results, card changes, record changes, code changes), sync this repo and push to `main` in the same turn.

- Sync with `python3 /home/claude/wedger/sync_repo.py "<what changed>"`. A copy of the script is at `sync_repo.py` in the repo root. It copies code, configs, records and raw pulls from the workspace into this repo, commits, and pushes. If nothing changed, it pushes nothing.
- Leave out raw downloads, generated datasets, store snapshots and anything with personal notes. The script's filter already does this.
- Keep the repo private. `rh/check.js` and `v2/v1_js.js` contain the owner's contact email.
