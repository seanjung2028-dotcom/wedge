"""Mirror the Wedge workspace's code and records into the GitHub repo (seanjung2028-dotcom/wedge) and push.
Run after every site publish:  python3 /home/claude/wedger/v2/build_site.py && python3 /home/claude/wedger/sync_repo.py "what changed"
(build_site.py rebuilds site/, the standalone read-only website; this script pushes all of site/.)
Same filter as the first export: code, configs, records and raw pulls; no downloads, generated datasets,
store snapshots, harness pages or images; files over 2 MB are skipped (except the built site in v2/out)."""
import os, re, shutil, subprocess, sys, tempfile
SRC = '/home/claude/wedger'; REPO = '/home/claude/wedge'
EXD = re.compile(r'^(dl\d+|nflverse_dl\d*|nba_dl\d*|bak_.*|dbsnap.*|dbw|brand|artifact-files|ref|mnf_out|thu_posted|photos/(raw|sheets|web)|harness/(w8|s|anim)|nfl8'
                 r'|v2/(db.*|data|h|v1db)|rh/[^/]+|pull\d+/[^/]*_out|tools|site_protected|nfl|\.wrangler)(/|$)')
KEEP_EXT = {'.py', '.js', '.css', '.sh', '.md', '.json', '.csv', '.txt'}
HTML_OK = {'rh/index_full.html', 'v2/out/index.html'}
SKIP = {'picklog/pick_log_nov8_12.md', 'kx_1023.json', 'blobs_1022.json', 'dash_skill_hits.txt', 'js_calls.txt', 'w7_old_keys.json'}
RH_DATA_OK = {'results_w6_w10.csv', 'results_w6_w11.csv', 'card_bt.csv', 'card_bt_sum.csv', 'final_record.csv', 'frec.csv', 'weather_w11.json', 'certs_seed.json', 'analysts_seed.json', 'weather_w10.json'}   # rh/ keeps code plus these records
REPO_ONLY = {'README.md', '.gitignore', 'CLAUDE.md'}
MAXB = 2 * 1024 * 1024
SITE_MAXB = 50 * 1024 * 1024   # site/ is the standalone website: every file goes, whatever its type

def wanted():
    out = {}
    for root, dirs, files in os.walk(SRC):
        rel = os.path.relpath(root, SRC); rel = '' if rel == '.' else rel
        dirs[:] = [d for d in dirs if d not in ('__pycache__', 'node_modules', '.git') and not EXD.match((rel + '/' + d).lstrip('/'))]
        for f in files:
            rp = (rel + '/' + f).lstrip('/'); ext = os.path.splitext(f)[1].lower(); p = os.path.join(root, f)
            if rp.startswith('site/') or rp.startswith('lib/protected/'):   # the website and the paid files its function serves
                if os.path.getsize(p) <= SITE_MAXB: out[rp] = p
                continue
            if rp in SKIP or rp in REPO_ONLY or (ext not in KEEP_EXT and rp not in HTML_OK): continue
            if rel == 'rh' and ext in ('.csv', '.json', '.txt') and f not in RH_DATA_OK: continue
            if rel.startswith('nba') and ext in ('.csv', '.json') and os.path.getsize(p) > 200 * 1024: continue
            if rel.startswith('final9') and ext == '.json' and os.path.getsize(p) > 300 * 1024: continue
            if os.path.getsize(p) > MAXB and not rp.startswith('v2/out/'): continue
            out[rp] = p
    return out

def run(*a): return subprocess.run(a, cwd=REPO, capture_output=True, text=True)

if __name__ == '__main__':
    msg = sys.argv[1] if len(sys.argv) > 1 else 'Sync with the live site'
    W = wanted()
    tracked = set(run('git', 'ls-files').stdout.split('\n')) - {''}
    for rp in sorted(tracked - set(W) - REPO_ONLY):   # files gone from the workspace (or now filtered out)
        os.remove(os.path.join(REPO, rp))
    for rp, p in W.items():
        d = os.path.join(REPO, rp); os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copy2(p, d)
    run('git', 'add', '-A')
    if not run('git', 'status', '--porcelain').stdout.strip():
        print('repo already matches the workspace; nothing to push'); sys.exit(0)
    stat = run('git', 'diff', '--cached', '--shortstat').stdout.strip()
    c = run('git', '-c', 'user.name=Sean', '-c', 'user.email=sean@wedge.local', 'commit', '-q', '-m',
            msg + '\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01Eg6At73hTNoV12vypBbGHk')
    if c.returncode: print(c.stdout, c.stderr); sys.exit(1)
    p = run('git', '-c', 'push.negotiate=true', 'push', 'origin', 'main')
    print(stat); print((p.stdout + p.stderr).strip().splitlines()[-1] if (p.stdout + p.stderr).strip() else 'pushed')
    sys.exit(p.returncode)
