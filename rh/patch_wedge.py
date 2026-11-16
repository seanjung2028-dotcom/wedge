"""Wedge rebrand (Wed Nov 4): the team's Identity Study 01 - silver / steel / black / graphite metal system with a Deep Green
(#104D30) signature, the approved wordmark, bold grotesk headlines with monospace spec labels, brushed-metal surfaces with fine
grain. Replaces the Tuesday-evening photo/meme lobby (patch_brand.py, no longer in the chain). Also adds the Lines tab's
"Every line, any price" view (dataset lines_all). Runs after patch_w9b.py, before gen_page.py."""
import json
B = '/home/claude/wedger/rh/'
s = open(B + 'page_template.html').read()
WM = json.load(open('/home/claude/wedger/brand/wordmark_blobs.json'))   # {'ink': '/_blob/..', 'light': '/_blob/..'}
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, (old[:100], c); s = s.replace(old, new)

# ---------------------------------------------------------------- fonts + tokens + components
s = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800&family=Geist+Mono:wght@400;500;600&display=swap">\n' + s)
GRAIN = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence "
         "type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Cpath fill='%23000' filter='url(%23n)' d='M0 0H180V180H0z'/%3E%3C/svg%3E\")")
CSS = r'''
  /* ---------- Wedge identity: Study 01, Deep Green ----------
     Layout: header (wordmark + spec line) / nav / editorial lobby: split hero, this week's reads, three campaign panels, index, record.
     Material: 65% metal (silver, steel), 27% dark neutrals (black, graphite), 8% Deep Green for rules, dots, labels and one action. */
  .wg-paper {
    --wx-silver: #E4E6E9; --wx-silver-hi: #F3F4F6; --wx-silver-lo: #B9BEC4; --wx-steel: #9DA3AA;
    --wx-black: #0D0F12; --wx-graphite: #2A2D31; --wx-green: #104D30; --wx-green-ink: #104D30; --wx-on-green: #EEF3EF;
    --wx-ink: #16181B; --wx-muted: #50565C; --wx-faint: #6B727A; --wx-rule: #B4B9BF;
    --wx-on-dark: #ECEEF0; --wx-on-dark-muted: #A9AFB6; --wx-dark-rule: #3A3F45;
    --wx-sans: "Geist", "Helvetica Neue", Arial, sans-serif;
    --wx-mono: "Geist Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    --wx-brushed: repeating-linear-gradient(90deg, #ffffff22 0 1px, #00000008 1px 2px, transparent 2px 4px), linear-gradient(145deg, #F3F4F6, #B9BEC4 55%, #E2E4E7);
    --wx-graphite-surface: radial-gradient(120% 90% at 85% 15%, #3A3F45 0%, transparent 55%), linear-gradient(160deg, #2A2D31, #16181B);
    --wx-black-surface: linear-gradient(170deg, #16181B, #0D0F12);
    --wx-grain: GRAIN;
    /* host tokens, re-pointed at the metal system */
    --color-bg: #F1F2F4; --color-panel: #EBEDF0; --color-fg: #16181B; --color-fg-muted: #50565C; --color-border-line: #C2C7CD;
    --color-ok: #104D30; --color-bad: #9A3B2E; --color-warn: #7A5C12;
    --cds-chart-grid: #D2D6DB; --cds-chart-muted: #AAB0B7; --cds-chart-reference: #6B727A; --cds-chart-status-critical: #9A3B2E;
    --cds-radius: 3px; --font-anthropic-sans: var(--wx-sans); --font-anthropic-serif: var(--wx-sans);
    --wg-green: #104D30; --wg-lime: #104D30; --wg-ink: #104D30; --wg-bear: #9A3B2E; --wg-bull: #104D30;
    --wg-soft: color-mix(in srgb, #104D30 10%, transparent); --wg-softer: color-mix(in srgb, #104D30 5%, transparent);
    --wg-c1: #24804F; --wg-c2: #3F6EB8; --wg-c3: #C27526; --wg-c4: #8C55A8;
    color-scheme: light;
    background: var(--wx-silver); background-image: none;
    position: relative; isolation: isolate;
  }
  .wg-paper::before { content: ''; position: fixed; inset: 0; z-index: -1; pointer-events: none; opacity: .07; background-image: var(--wx-grain); mix-blend-mode: multiply; }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) .wg-paper {
      --wx-ink: #E6E8EB; --wx-muted: #A3A9B0; --wx-faint: #8A9098; --wx-rule: #353A40; --wx-green-ink: #6FB38D;
      --color-bg: #1A1D21; --color-panel: #1E2125; --color-fg: #E6E8EB; --color-fg-muted: #A3A9B0; --color-border-line: #33383E;
      --color-ok: #6FB38D; --color-bad: #E0806C; --color-warn: #D6B25E;
      --cds-chart-grid: #2C3136; --cds-chart-muted: #4C535A; --cds-chart-reference: #8A9098; --cds-chart-status-critical: #E0806C;
      --wg-green: #3A8F63; --wg-lime: #3A8F63; --wg-ink: #6FB38D; --wg-bear: #E0806C; --wg-bull: #3A8F63;
      --wg-soft: color-mix(in srgb, #3A8F63 16%, transparent); --wg-softer: color-mix(in srgb, #3A8F63 8%, transparent);
      --wg-c1: #3A8F63; --wg-c2: #5A84C0; --wg-c3: #C4853A; --wg-c4: #9B74BA;
      color-scheme: dark; background: #111316;
    }
    :root:not([data-theme="light"]) .wg-paper::before { mix-blend-mode: screen; opacity: .05; filter: invert(1); }
  }
  :root[data-theme="dark"] .wg-paper {
    --wx-ink: #E6E8EB; --wx-muted: #A3A9B0; --wx-faint: #8A9098; --wx-rule: #353A40; --wx-green-ink: #6FB38D;
    --color-bg: #1A1D21; --color-panel: #1E2125; --color-fg: #E6E8EB; --color-fg-muted: #A3A9B0; --color-border-line: #33383E;
    --color-ok: #6FB38D; --color-bad: #E0806C; --color-warn: #D6B25E;
    --cds-chart-grid: #2C3136; --cds-chart-muted: #4C535A; --cds-chart-reference: #8A9098; --cds-chart-status-critical: #E0806C;
    --wg-green: #3A8F63; --wg-lime: #3A8F63; --wg-ink: #6FB38D; --wg-bear: #E0806C; --wg-bull: #3A8F63;
    --wg-soft: color-mix(in srgb, #3A8F63 16%, transparent); --wg-softer: color-mix(in srgb, #3A8F63 8%, transparent);
    --wg-c1: #3A8F63; --wg-c2: #5A84C0; --wg-c3: #C4853A; --wg-c4: #9B74BA;
    color-scheme: dark; background: #111316;
  }
  :root[data-theme="dark"] .wg-paper::before { mix-blend-mode: screen; opacity: .05; filter: invert(1); }
  .wg-paper, .rs-wrap { font-family: var(--wx-sans); }
  .rs-wrap { gap: 28px; }
  .wx-mono, .wx-label { font-family: var(--wx-mono); font-size: 11px; letter-spacing: .08em; text-transform: uppercase; font-weight: 500; }
  .wx-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--wx-green); flex: none; }
  .wx-rule-g { display: block; width: 50px; height: 3px; background: var(--wx-green); }

  /* header */
  .wg-head { padding: 6px 0 0; border-bottom: 1px solid var(--wx-rule); padding-bottom: 18px; }
  .wg-brand { gap: 18px 22px; align-items: center; }
  .wx-mark { display: block; height: 40px; width: auto; }
  .wx-mark.l { display: none; }
  @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .wx-mark.i { display: none; } :root:not([data-theme="light"]) .wx-mark.l { display: block; } }
  :root[data-theme="dark"] .wx-mark.i { display: none; } :root[data-theme="dark"] .wx-mark.l { display: block; }
  .wg-rule { height: 34px; background: var(--wx-rule); }
  .wg-name { font-family: var(--wx-mono); font-size: 11px; letter-spacing: .08em; text-transform: uppercase; font-weight: 500; color: var(--wx-ink); }
  .wg-sub { font-family: var(--wx-mono); font-size: 10.5px; letter-spacing: .04em; color: var(--wx-muted); }
  .wg-record { background: transparent; border: 1px solid var(--wx-rule); border-radius: 2px; padding: 10px 14px; }
  .wg-record-label { font-family: var(--wx-mono); font-size: 10px; }
  .wg-record-label i { background: var(--wx-green); width: 8px; height: 8px; background-image: none; }
  .wg-record-pct { font-family: var(--wx-sans); font-weight: 700; letter-spacing: -0.04em; font-size: 30px; }
  .wg-record.wg-up { border-color: var(--wx-rule); }
  .wg-record.wg-up :is(.wg-record-pct, .wg-record-frac) { color: var(--wx-ink); }
  .wg-record.wg-up .wg-record-frac { color: var(--wx-green-ink); }

  /* nav: spec-sheet tabs */
  .rs-tabs { background: transparent; border: 0; border-bottom: 1px solid var(--wx-rule); border-radius: 0; padding: 0 0 2px; gap: 0 4px; }
  .rs-tab { font-family: var(--wx-mono); font-size: 11px; letter-spacing: .08em; text-transform: uppercase; font-weight: 500; color: var(--wx-muted); padding: 10px 10px 9px; border-radius: 0; }
  .rs-tab:hover { background: transparent; color: var(--wx-ink); }
  .rs-tab[aria-current=page] { background: transparent; color: var(--wx-ink); box-shadow: inset 0 -2px 0 var(--wx-green); }
  .wg-tab-apply { color: var(--wx-green-ink) !important; }
  .wg-dd-menu { border-radius: 2px; }
  .wg-dd-item, .wg-dd-label { font-family: var(--wx-mono); letter-spacing: .04em; }

  /* surfaces */
  .rs-card { border-radius: 2px; background: var(--color-panel); border-color: var(--color-border-line); }
  .rs-card h2 { font-weight: 700; letter-spacing: -0.03em; font-size: 21px; }
  .rs-tiles .rs-card::before { width: 0; }
  .rs-tile-label { font-family: var(--wx-mono); font-size: 10.5px; letter-spacing: .08em; }
  .rs-tile-num { font-weight: 700; letter-spacing: -0.04em; }
  .rs-table th { font-family: var(--wx-mono); font-size: 10.5px; letter-spacing: .08em; font-weight: 500; }
  .wg-go { border-radius: 999px; font-weight: 500; }
  .wg-go-primary { background: var(--wx-green); border-color: var(--wx-green); color: var(--wx-on-green); }
  .wg-go-primary:hover { background: color-mix(in srgb, var(--wx-green) 86%, #000); border-color: color-mix(in srgb, var(--wx-green) 86%, #000); }
  .wg-big, .wg-an-val, .wg-price b { font-weight: 700; letter-spacing: -0.04em; }
  .wg-un-title, .wg-soon h2 { font-weight: 800; letter-spacing: -0.05em; }
  .wg-kicker { font-family: var(--wx-mono); letter-spacing: .08em; text-transform: uppercase; font-size: 11px; }
  .wg-pop { background: var(--wx-green); color: var(--wx-on-green); font-family: var(--wx-mono); letter-spacing: .06em; text-transform: uppercase; font-size: 10px; border-radius: 2px; }
  .wg-pop-alt { background: var(--wx-graphite); color: var(--wx-on-dark); }
  .wg-plan { border-radius: 2px; }
  .wg-plan-hot { border-color: var(--wx-green); box-shadow: none; }
  .wg-sitdlg { border-radius: 4px; }

  /* lobby */
  .wg-lobby { gap: 0; }
  .wx-hero { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); gap: clamp(28px, 5vw, 64px); align-items: center; padding: clamp(28px, 6vw, 72px) 0 clamp(36px, 6vw, 64px); border-bottom: 1px solid var(--wx-rule); }
  .wx-hero-copy { display: flex; flex-direction: column; gap: 18px; min-width: 0; }
  .wx-hero-copy .wx-label { color: var(--wx-ink); display: flex; align-items: center; gap: 10px; }
  .wx-h1 { margin: 0; font-family: var(--wx-sans); font-weight: 800; font-size: clamp(48px, 7.4vw, 104px); line-height: .9; letter-spacing: -0.07em; color: var(--wx-ink); text-wrap: balance; }
  .wx-h1 em { font-style: normal; color: var(--wx-green-ink); }
  .wx-lede { margin: 0; max-width: 31rem; font-size: 17px; line-height: 1.6; color: var(--wx-muted); }
  .wx-go { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 6px; }
  .wx-go .wg-go { font-size: 14px; padding: 10px 18px; }
  .wx-go .wg-go:not(.wg-go-primary) { background: transparent; border-color: var(--wx-rule); }
  .wx-id { position: relative; isolation: isolate; overflow: hidden; padding: clamp(26px, 4vw, 44px); background: var(--wx-brushed); border: 1px solid #F3F4F5; color: #16181B; min-width: 0; }
  .wx-id::after { content: ''; position: absolute; inset: 0; z-index: -1; opacity: .13; background-image: var(--wx-grain); mix-blend-mode: multiply; pointer-events: none; }
  .wx-id img { display: block; width: 100%; max-width: 420px; height: auto; }
  .wx-id .wx-mono { color: #454B51; }
  .wx-id-cap { display: block; margin: 22px 0 18px; }
  .wx-spec { display: grid; margin: 0; border-top: 1px solid rgba(22, 24, 27, .22); }
  .wx-spec div { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; padding: 9px 0; border-bottom: 1px solid rgba(22, 24, 27, .16); }
  .wx-spec dt { font-family: var(--wx-mono); font-size: 10.5px; letter-spacing: .08em; text-transform: uppercase; color: #454B51; }
  .wx-spec dd { margin: 0; font-weight: 700; font-size: 18px; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; color: #16181B; }
  .wx-id .wg-hero-desc { margin: 16px 0 0; color: #3A3F45; font-size: 13px; text-align: left; max-width: none; }
  .wx-id .wg-profit-pct, .wx-id .wg-profit-pct.wg-pos { color: #104D30; font-weight: 700; }
  .wx-id .wg-profit-pct.wg-neg { color: #9A3B2E; }
  @media (max-width: 860px) { .wx-hero { grid-template-columns: 1fr; } }

  .wx-sec { display: flex; flex-direction: column; gap: 22px; padding: clamp(36px, 5vw, 56px) 0; border-bottom: 1px solid var(--wx-rule); min-width: 0; }
  .wx-sec-head { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-end; gap: 14px 32px; }
  .wx-sec-head .wx-label { color: var(--wx-ink); }
  .wx-h2 { margin: 10px 0 0; font-family: var(--wx-sans); font-weight: 800; font-size: clamp(30px, 3.6vw, 42px); line-height: 1; letter-spacing: -0.05em; color: var(--wx-ink); }
  .wx-sec-sub { margin: 0; max-width: 24rem; font-size: 14px; line-height: 1.6; color: var(--wx-muted); }

  /* this week's reads */
  .wx-reads { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1px; background: var(--wx-rule); border: 1px solid var(--wx-rule); }
  @media (max-width: 1000px) { .wx-reads { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
  @media (max-width: 640px) { .wx-reads { grid-template-columns: 1fr; } }
  .wx-read { all: unset; box-sizing: border-box; cursor: pointer; display: flex; flex-direction: column; gap: 14px; padding: 20px; background: var(--color-panel); min-width: 0; transition: background .2s ease; }
  .wx-read:hover { background: var(--color-bg); }
  .wx-read:focus-visible { outline: 2px solid var(--wx-green); outline-offset: -2px; }
  .wx-read-top { display: flex; justify-content: space-between; gap: 10px; color: var(--wx-muted); font-family: var(--wx-mono); font-size: 10.5px; letter-spacing: .08em; text-transform: uppercase; }
  .wx-read-title { font-weight: 700; font-size: 17px; line-height: 1.25; letter-spacing: -0.02em; color: var(--wx-ink); overflow-wrap: anywhere; }
  .wx-read-mid { display: flex; align-items: flex-end; justify-content: space-between; gap: 12px; }
  .wx-read-big { font-weight: 800; font-size: 54px; line-height: .85; letter-spacing: -0.06em; font-variant-numeric: tabular-nums; color: var(--wx-ink); }
  .wx-read-big small { font-size: 24px; letter-spacing: -0.02em; margin-left: 2px; }
  .wx-read-mid .wx-mono { color: var(--wx-muted); text-align: right; line-height: 1.5; }
  .wx-read-px { display: grid; grid-template-columns: 1fr 1fr; border-top: 1px solid var(--color-border-line); }
  .wx-read-px span { display: flex; justify-content: space-between; padding: 9px 2px 0; font-family: var(--wx-mono); font-size: 12px; letter-spacing: .04em; color: var(--wx-muted); font-variant-numeric: tabular-nums; }
  .wx-read-px span + span { padding-left: 12px; border-left: 1px solid var(--color-border-line); margin-left: 10px; }
  .wx-read-px span.is-pick { color: var(--wx-ink); font-weight: 600; }
  .wx-read-foot { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--wx-ink); }
  .wx-read-foot em { margin-left: auto; font-style: normal; font-family: var(--wx-mono); font-size: 11px; letter-spacing: .06em; text-transform: uppercase; color: var(--wx-green-ink); }
  .wx-empty { margin: 0; padding: 20px; background: var(--color-panel); color: var(--wx-muted); font-size: 13px; }

  /* campaign panels */
  .wx-panels { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr)); gap: 22px; }
  .wx-poster { position: relative; isolation: isolate; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; gap: 28px; min-height: 440px; padding: 28px; min-width: 0; }
  .wx-poster::after { content: ''; position: absolute; inset: 0; z-index: -1; opacity: .13; background-image: var(--wx-grain); mix-blend-mode: multiply; pointer-events: none; }
  .wx-poster.dark { background: var(--wx-graphite-surface); color: var(--wx-on-dark); }
  .wx-poster.black { background: var(--wx-black-surface); color: var(--wx-on-dark); }
  .wx-poster.silver { background: var(--wx-brushed); color: #16181B; }
  .wx-poster.dark::after, .wx-poster.black::after { mix-blend-mode: screen; filter: invert(1); opacity: .06; }
  .wx-p-top { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
  .wx-p-top img { height: 26px; width: auto; display: block; }
  .wx-p-top .wx-mono { font-size: 10px; opacity: .85; }
  .wx-p-big { font-weight: 800; font-size: clamp(64px, 7vw, 92px); line-height: .82; letter-spacing: -0.07em; font-variant-numeric: tabular-nums; }
  .wx-p-big small { font-size: .45em; letter-spacing: -0.03em; margin-left: 4px; }
  .wx-p-h { margin: 0; font-weight: 800; font-size: clamp(32px, 3.4vw, 44px); line-height: .92; letter-spacing: -0.06em; text-transform: uppercase; }
  .wx-p-label { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
  .wx-p-label::before { content: ''; width: 3px; height: 14px; background: var(--wx-green); }
  .wx-poster.dark .wx-p-label::before, .wx-poster.black .wx-p-label::before { background: #2F7D56; }
  .wx-p-note { margin: 12px 0 0; font-size: 14px; line-height: 1.5; opacity: .82; max-width: 22rem; }
  .wx-p-foot { display: flex; justify-content: space-between; align-items: flex-end; gap: 12px; }
  .wx-p-foot .wx-mono { font-size: 10px; opacity: .85; }
  .wx-steps { display: grid; margin: 18px 0 0; }
  .wx-steps div { display: grid; grid-template-columns: 34px 1fr; align-items: baseline; padding: 12px 0; border-bottom: 1px solid currentColor; border-bottom-color: color-mix(in srgb, currentColor 22%, transparent); }
  .wx-steps .wx-mono { color: var(--wx-green); font-size: 11px; }
  .wx-steps b { font-weight: 700; font-size: 17px; letter-spacing: -0.03em; }
  .wx-poster.black .wx-steps .wx-mono { color: #6FB38D; }
  .wx-poster.black .wx-steps div { grid-template-columns: 1fr auto; }
  .wx-poster.black .wx-steps b { font-family: var(--wx-mono); font-weight: 400; font-size: 12px; letter-spacing: .02em; }
  .wx-band-g { height: 6px; background: var(--wx-green); margin: 0 -28px; }
  .wx-poster .wg-go { font-size: 13px; padding: 8px 16px; }
  .wx-poster.silver .wg-go:not(.wg-go-primary) { background: transparent; color: #16181B; border-color: rgba(22, 24, 27, .35); }

  /* index + perspective */
  .wx-index { display: grid; border-top: 1px solid var(--wx-ink); }
  .wx-row { all: unset; box-sizing: border-box; cursor: pointer; display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(0, 2fr) auto; gap: 16px; align-items: baseline; padding: 18px 2px; border-bottom: 1px solid var(--wx-rule); transition: padding .2s ease, background .2s ease; }
  .wx-row:hover { background: color-mix(in srgb, var(--wx-ink) 4%, transparent); padding-left: 10px; }
  .wx-row:focus-visible { outline: 2px solid var(--wx-green); outline-offset: -2px; }
  .wx-row b { font-weight: 800; font-size: clamp(24px, 3vw, 34px); letter-spacing: -0.05em; line-height: 1; color: var(--wx-ink); }
  .wx-row span { font-family: var(--wx-mono); font-size: 11.5px; letter-spacing: .05em; text-transform: uppercase; color: var(--wx-muted); }
  .wx-row em { font-style: normal; font-family: var(--wx-mono); font-size: 12px; color: var(--wx-green-ink); }
  @media (max-width: 640px) { .wx-row { grid-template-columns: 1fr auto; } .wx-row span { grid-column: 1 / -1; grid-row: 2; } }
  .wx-quote { display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr); gap: clamp(24px, 5vw, 64px); align-items: end; }
  .wx-quote blockquote { margin: 0; font-family: Georgia, "Times New Roman", serif; font-size: clamp(30px, 3.8vw, 50px); line-height: 1.08; letter-spacing: -0.03em; color: var(--wx-ink); }
  .wx-quote blockquote::before { content: ''; display: block; width: 50px; height: 3px; background: var(--wx-green); margin-bottom: 26px; }
  .wx-ledger { display: grid; border-top: 1px solid var(--wx-ink); }
  .wx-ledger div { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; padding: 11px 0; border-bottom: 1px solid var(--wx-rule); }
  .wx-ledger span { font-family: var(--wx-mono); font-size: 11px; letter-spacing: .06em; text-transform: uppercase; color: var(--wx-muted); }
  .wx-ledger b { font-weight: 700; font-size: 18px; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; color: var(--wx-ink); }
  @media (max-width: 760px) { .wx-quote { grid-template-columns: 1fr; } }
  .wx-fine { margin: 0; padding: 22px 0 6px; font-family: var(--wx-mono); font-size: 10.5px; letter-spacing: .04em; line-height: 1.7; color: var(--wx-faint); max-width: 70rem; }

  /* inner-page spec bands */
  .wx-band { position: relative; isolation: isolate; overflow: hidden; display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: end; gap: 10px 24px; padding: 26px 28px 24px; background: var(--wx-graphite-surface); color: var(--wx-on-dark); }
  .wx-band::after { content: ''; position: absolute; inset: 0; z-index: -1; opacity: .06; background-image: var(--wx-grain); mix-blend-mode: screen; filter: invert(1); pointer-events: none; }
  .wx-band .wx-label { grid-column: 1 / -1; color: var(--wx-on-dark-muted); display: flex; align-items: center; gap: 10px; }
  .wx-band h2 { margin: 0; font-weight: 800; font-size: clamp(30px, 4vw, 48px); line-height: .95; letter-spacing: -0.06em; color: var(--wx-on-dark); }
  .wx-band p { margin: 0; font-family: var(--wx-mono); font-size: 11px; letter-spacing: .05em; text-transform: uppercase; color: var(--wx-on-dark-muted); text-align: right; line-height: 1.7; max-width: 30rem; }
  .wx-band::before { content: ''; position: absolute; left: 28px; bottom: 0; width: 50px; height: 3px; background: #2F7D56; }
  @media (max-width: 640px) { .wx-band { grid-template-columns: 1fr; } .wx-band p { text-align: left; } }

  /* line tables: one line per row where it fits; the long text columns wrap at a readable width */
  .rs-table td { white-space: nowrap; }
  .rs-table td.rs-contract { white-space: normal; min-width: 11rem; }
  .rs-table td.rs-results { white-space: normal; min-width: 16rem; }
  .rs-table td.rs-flag { white-space: normal; min-width: 12rem; }
  /* every-line view */
  .wx-more { display: flex; justify-content: center; padding: 14px 0 2px; }
  .wg-sitstatic { display: grid; gap: 4px; min-width: 7.5rem; }
  .wg-sitstatic .wg-sit-row1 b { font-weight: 600; }
  .wg-sitstatic small { font-size: 10.5px; color: var(--color-fg-muted); }
'''.replace('GRAIN', GRAIN)
i = s.index('</style>'); s = s[:i] + CSS + s[i:]

# ---------------------------------------------------------------- header
rep('<img class="wg-logo" src="/_blob/43606eb1e05cb9531db70c83606edd16" alt="Wedger" width="102" height="46">',
    f'<img class="wx-mark i" src="{WM["ink"]}" alt="Wedge" width="112" height="40"><img class="wx-mark l" src="{WM["light"]}" alt="" width="112" height="40" aria-hidden="true">')
rep('<h1 class="wg-name">Wedger</h1>', '<h1 class="wg-name"><span class="wg-visually-hidden">Wedge · </span>Football, understood.</h1>')

# ---------------------------------------------------------------- lobby
i = s.index('    <section class="wg-hero" aria-labelledby="hero-title">'); j = s.index('</section>', i) + len('</section>')
LOBBY = f'''    <section class="wx-hero" aria-labelledby="hero-title">
      <div class="wx-hero-copy">
        <span class="wx-label"><i class="wx-dot" aria-hidden="true"></i>Week 9 / <span data-wg-count="lines">430</span> lines / <span data-wg-count="picks">40</span> reads</span>
        <h2 class="wx-h1" id="hero-title">Football, <em>understood.</em></h2>
        <p class="wx-lede">Wedge prices every Robinhood line that trades like a coin flip, then reads the role, the matchup and the price. Most lines are fair. We mark the few that are not.</p>
        <div class="wx-go">
          <button type="button" class="wg-go wg-go-primary" data-go="lines">View Week 9 lines ↗</button>
          <button type="button" class="wg-go wg-unlock-btn" data-go="unlock">Membership</button>
        </div>
      </div>
      <div class="wx-id">
        <img src="{WM['ink']}" alt="Wedge" width="420" height="150">
        <span class="wx-mono wx-id-cap">Week 9 / priced Wed Nov 4, 3:37 PM CT</span>
        <dl class="wx-spec">
          <div><dt>Lines priced 45–55¢</dt><dd data-wg-count="lines">430</dd></div>
          <div><dt>Every line, any price</dt><dd data-wg-count="every">5,722</dd></div>
          <div><dt>Wedge reads (3+ pts)</dt><dd data-wg-count="picks">40</dd></div>
        </dl>
        <p class="wg-hero-desc" id="wg-profit" data-source="results" aria-live="polite">Net profit on Wedge-certified picks so far: —</p>
      </div>
    </section>

    <section class="wx-sec" aria-labelledby="reads-h">
      <div class="wx-sec-head">
        <div><span class="wx-label">01 / This week</span><h2 class="wx-h2" id="reads-h">The reads.</h2></div>
        <p class="wx-sec-sub">The widest gaps between Wedge % and the price on Robinhood's own Week 9 lines: three Yes, three No, two per game at most. Select one for the full read.</p>
      </div>
      <div class="wx-reads" id="wg-hot-cards"><p class="wx-empty">Loading this week's reads…</p></div>
      <div><button type="button" class="wg-go" data-go="lines" data-wg-show="pick">All <span data-wg-count="picks">40</span> reads ↗</button></div>
    </section>

    <section class="wx-sec" aria-labelledby="method-h">
      <div class="wx-sec-head">
        <div><span class="wx-label">02 / Method</span><h2 class="wx-h2" id="method-h">Process before hindsight.</h2></div>
        <p class="wx-sec-sub">Every read is settled against the box score, the good ones and the bad ones alike.</p>
      </div>
      <div class="wx-panels">
        <article class="wx-poster dark">
          <div class="wx-p-top"><img src="{WM['light']}" alt="" width="73" height="26"><span class="wx-mono">The numbers / 001</span></div>
          <div>
            <span class="wx-mono wx-p-label">Reads won, as posted</span>
            <div class="wx-p-big" data-wg-rcpt="picks-pct">56.6<small>%</small></div>
            <p class="wx-p-note" data-wg-rcpt="picks-txt">248–190 over Weeks 6–8, +4.0% before fees.</p>
          </div>
          <div class="wx-p-foot"><span class="wx-mono">Weeks 6–8 / settled</span><span class="wx-mono">W / 001</span></div>
        </article>
        <article class="wx-poster silver">
          <div class="wx-p-top"><img src="{WM['ink']}" alt="" width="73" height="26"><span class="wx-mono">The Wedge method</span></div>
          <div>
            <h3 class="wx-p-h">Start with the role.</h3>
            <div class="wx-steps">
              <div><span class="wx-mono">01</span><b>Measure opportunity.</b></div>
              <div><span class="wx-mono">02</span><b>Read the matchup.</b></div>
              <div><span class="wx-mono">03</span><b>Evaluate the price.</b></div>
            </div>
          </div>
          <div class="wx-p-foot"><span class="wx-mono">The line comes last.</span><button type="button" class="wg-go wg-go-primary" data-go="charts">Inside the process ↗</button></div>
        </article>
        <article class="wx-poster black">
          <div class="wx-p-top"><img src="{WM['light']}" alt="" width="73" height="26"><span class="wx-mono">Membership</span></div>
          <div>
            <h3 class="wx-p-h">A closer look at the game.</h3>
            <div class="wx-steps">
              <div><span class="wx-mono">01 / Research</span><b>Usage + matchup</b></div>
              <div><span class="wx-mono">02 / Context</span><b>Role + game script</b></div>
              <div><span class="wx-mono">03 / Inner circle</span><b>Exact bets</b></div>
            </div>
          </div>
          <div class="wx-p-foot"><button type="button" class="wg-go wg-go-primary" data-go="unlock">View access ↗</button><span class="wx-mono">Wedge membership</span></div>
        </article>
      </div>
    </section>

    <section class="wx-sec" aria-labelledby="index-h">
      <div class="wx-sec-head"><div><span class="wx-label">03 / Index</span><h2 class="wx-h2" id="index-h">Where to look.</h2></div></div>
      <nav class="wx-index" aria-label="Boards">
        <button type="button" class="wx-row" data-go="lines"><b>NFL</b><span>Week 9 / <span data-wg-count="lines">430</span> lines at 45–55¢ / <span data-wg-count="every">5,722</span> at any price</span><em>Open ↗</em></button>
        <button type="button" class="wx-row" data-go="proj"><b>Projections</b><span>Every starter's main props, before the books post them</span><em>Open ↗</em></button>
        <button type="button" class="wx-row" data-go="nba"><b>NBA</b><span>The 45–55¢ screen, basketball edition</span><em>Open ↗</em></button>
        <button type="button" class="wx-row" data-go="soccer"><b>Soccer</b><span>In preparation / join the waitlist</span><em>Soon</em></button>
      </nav>
    </section>

    <section class="wx-sec" aria-labelledby="persp-h">
      <h2 class="wg-visually-hidden" id="persp-h">Perspective</h2>
      <div class="wx-quote">
        <blockquote>“A good result deserves the same scrutiny as a bad one.”</blockquote>
        <div class="wx-ledger" aria-label="The record">
          <div><span>Buying every Yes since Week 1</span><b data-wg-rcpt="yes-roi">−5.1%</b></div>
          <div><span>Passing props at ~50¢</span><b data-wg-rcpt="pass-pct">58.0%</b></div>
          <div><span>Rushing props at ~50¢</span><b data-wg-rcpt="rush-pct">40.7%</b></div>
          <div><span>Lines settled for this model</span><b>1,333</b></div>
        </div>
      </div>
    </section>
    <p class="wx-fine">Wedge is football research, not financial advice. Prices move and reads lose; every figure is before fees. Perspective / 001.</p>'''
s = s[:i] + LOBBY + s[j:]

# ---------------------------------------------------------------- inner-page spec bands
def band(page, label, title, meta):
    tag = f'  <div class="rs-page" id="{page}" hidden>\n'
    rep(tag, tag + f'''    <header class="wx-band"><span class="wx-label"><i class="wx-dot" aria-hidden="true"></i>{label}</span><h2>{title}</h2><p>{meta}</p></header>\n''')
band('lines', 'NFL / Week 9', 'Week 9 lines.', '<span data-wg-count="lines">430</span> at 45–55¢ · <span data-wg-count="every">5,722</span> at any price<br>Priced Wed Nov 4, 3:37 PM CT')
band('proj', 'NFL / Week 9', 'Projections.', 'Every starter, before the books post<br>Re-run Wed Nov 4')
band('atd', 'NFL / Week 9', 'Anytime touchdown.', 'Red-zone usage, target share, TD rate<br>Priced Wed Nov 4')
band('results', 'Settled', 'Results.', 'Every line posted, settled from the box score')
band('charts', 'Weeks 1–8', 'The record.', 'Every 45–55¢ line at Robinhood\'s price')
band('nba', 'NBA', 'NBA lines.', 'The 45–55¢ screen')
band('soccer', 'Soccer', 'In preparation.', 'Premier League, Champions League, MLS')

# ---------------------------------------------------------------- lines: every line, any price
rep('<option value="all">All 45–55¢ lines</option>\n        </select>\n        <select class="rs-game" aria-label="Game"></select>',
    '<option value="all">All 45–55¢ lines</option>\n          <option value="every">Every line, any price</option>\n        </select>\n'
    '        <select class="rs-px" aria-label="Price range" hidden>\n          <option value="">Any price</option>\n          <option value="0-10">10¢ or less</option>\n'
    '          <option value="11-44">11–44¢</option>\n          <option value="45-55">45–55¢</option>\n          <option value="56-89">56–89¢</option>\n          <option value="90-100">90¢ or more</option>\n'
    '        </select>\n        <select class="rs-game" aria-label="Game"></select>')
i = s.index('<table class="rs-table" id="lines-table"'); j = s.index('</table>', i) + len('</table>'); k = s.index('</div>', j) + len('</div>')
s = s[:k] + '\n      <div class="wx-more"><button type="button" class="wg-go rl-more" hidden>Show 500 more</button></div>' + s[k:]
i = s.index('<p class="rs-note">Week 9, re-priced Wed Nov 4'); j = s.index('</p>', i) + 4
s = s[:j] + ('\n      <p class="rs-note rl-every-note" hidden>Every Week 9 line Wedge priced, at any price: Robinhood\'s own contracts and the Robinhood-style '
             'rungs priced from the sportsbooks, each with its 2026 hit rate. Inside 45–55¢ the columns are the same as the main screen. Outside it, '
             'Wedge % applies the same market shifts (fit on lines priced 40–60¢), so read it as a rough guide; reads are only made inside 45–55¢. '
             'Rows without an outlook show Wedge % as plain text.</p>') + s[j:]
rep("  const ls = { show: 'q', game: '', group: '', src: '', mom: '', role: '', clean: false, upcoming: false, certOnly: false, q: '', sortK: 'hit_rate', sortDir: -1 };",
    "  const ls = { show: 'q', game: '', group: '', src: '', mom: '', role: '', px: '', lim: 500, clean: false, upcoming: false, certOnly: false, q: '', sortK: 'hit_rate', sortDir: -1 };\n"
    "  const pxOk = (r) => { if (!ls.px) return true; const [a, b] = ls.px.split('-').map(Number), p = num(r.yes_price); return p != null && p >= a && p <= b; };")
rep("  showSel.addEventListener('change', () => { ls.show = showSel.value; drawLines(); });",
    "  showSel.addEventListener('change', () => { ls.show = showSel.value; ls.lim = 500; const ev = ls.show === 'every'; $('.rs-px').hidden = !ev; $('.rl-every-note').hidden = !ev; if (!ev) { ls.px = ''; $('.rs-px').value = ''; } drawLines(); });\n"
    "  $('.rs-px').addEventListener('change', (e) => { ls.px = e.target.value; ls.lim = 500; drawLines(); });\n"
    "  $('.rl-more').addEventListener('click', () => { ls.lim += 500; drawLines(); });")
rep("  function drawLines() {\n    const d = dash.data('lines');", "  function drawLines() {\n    const d = ls.show === 'every' ? dash.data('lines_all') : dash.data('lines');")
rep("      (ls.certOnly ? certs.has(keyOfLine(r)) : (ls.show === 'all' || (ls.show === 'pick' ? !!r.sit_pick : r.qualifies === 'Yes'))) &&",
    "      (ls.certOnly ? certs.has(keyOfLine(r)) : (ls.show === 'all' || ls.show === 'every' || (ls.show === 'pick' ? !!r.sit_pick : r.qualifies === 'Yes'))) &&\n      pxOk(r) &&")
rep("    $('.rl-count').textContent = ls.certOnly ? fmt(v.length) + ' Wedger certified' : fmt(v.length) + ' of ' + fmt(rows.length) + ' lines';\n    const frag = document.createDocumentFragment();\n    for (const r of v) {",
    "    const shown = ls.show === 'every' ? v.slice(0, ls.lim) : v;\n"
    "    $('.rl-count').textContent = ls.certOnly ? fmt(v.length) + ' Wedger certified' : fmt(v.length) + ' of ' + fmt(rows.length) + ' lines' + (shown.length < v.length ? ` · showing ${fmt(shown.length)}` : '');\n"
    "    const more = $('.rl-more'); more.hidden = shown.length >= v.length; more.textContent = `Show ${fmt(Math.min(500, v.length - shown.length))} more`;\n"
    "    const frag = document.createDocumentFragment();\n    for (const r of shown) {")
rep("    if (hr == null || !r.sit_key) { c.textContent = '—'; c.classList.add('rs-sub'); tr.appendChild(c); return c; }",
    "    if (hr != null && !r.sit_key) {\n"
    "      const st = el('div', 'wg-sitstatic'), row1 = el('span', 'wg-sit-row1'); row1.append(el('b', null, pctR(hr)));\n"
    "      const ed = price == null ? null : Math.round(hr - price); if (ed != null) row1.append(el('span', 'wg-sit-edge flat', (ed > 0 ? '+' : '') + ed));\n"
    "      const bar = el('div', 'rs-bar'), fill = el('span'); fill.style.width = Math.max(0, Math.min(100, hr)) + '%'; fill.style.background = 'var(--cds-chart-muted)';\n"
    "      const tick = el('i'); if (price != null) tick.style.left = Math.max(0, Math.min(100, price)) + '%'; bar.append(fill, tick);\n"
    "      st.append(row1, bar); st.title = 'Market shift only (no outlook outside 45–55¢)'; c.appendChild(st); tr.appendChild(c); return c;\n"
    "    }\n"
    "    if (hr == null || !r.sit_key) { c.textContent = '—'; c.classList.add('rs-sub'); tr.appendChild(c); return c; }")

# ---------------------------------------------------------------- membership copy
rep('<span class="wg-kicker">Wedge Pro · coming soon</span>', '<span class="wg-kicker">Wedge membership · waitlist</span>')
rep('<h2 class="wg-un-title">Unlock every edge.</h2>', '<h2 class="wg-un-title">A closer look at the game.</h2>')
rep('<span class="wg-pop">Most popular</span>', '<span class="wg-pop">Members</span>')
rep('<span class="wg-pop wg-pop-alt">Best value</span>', '<span class="wg-pop wg-pop-alt">Season</span>')

# ---------------------------------------------------------------- JS: palette, lobby reads, counts, record
rep("const shine = $('.wg-hero-shine'), mask", "if (!$('.wg-hero-shine')) return;\n    const shine = $('.wg-hero-shine'), mask")
n = s.count('dash.colors'); assert n == 9, n
s = s.replace('dash.colors', 'wgColors()')
rep("    const segs = [...new Set(rows.map((r) => r.segment))];\n    const col = (sg) => wgColors()[segs.indexOf(sg) % wgColors().length];",
    "    const segs = [...new Set(rows.map((r) => r.segment))].sort((a, b) => /Wedge/.test(b) - /Wedge/.test(a));\n    const col = (sg) => wgColors()[segs.indexOf(sg) % wgColors().length];")
JS = r'''
  // ---------------- Wedge identity: chart palette, lobby reads, counts, record ----------------
  function wgColors() {
    const cs = getComputedStyle($('.wg-paper') || document.documentElement);
    return ['--wg-c1', '--wg-c2', '--wg-c3', '--wg-c4'].map((v, i) => cs.getPropertyValue(v).trim() || ['#24804F', '#3F6EB8', '#C27526', '#8C55A8'][i]);
  }
  const WX_MKT = { passyd: 'Passing', passtd: 'Passing', int: 'Passing', rushyd: 'Rushing', rryd: 'Scrimmage', recyd: 'Receiving', rec: 'Receiving', td: 'Touchdown' };
  const wgFmt = (n) => Number(n).toLocaleString('en-US');
  document.querySelectorAll('[data-wg-show]').forEach((b) => b.addEventListener('click', () => {
    const sel = $('.rs-show'); if (sel && [...sel.options].some((o) => o.value === b.dataset.wgShow)) { sel.value = b.dataset.wgShow; sel.dispatchEvent(new Event('change')); }
  }));
  const wxRead = (r) => {
    const yes = num(r.yes_price);
    const no = num(r.no_price) != null ? num(r.no_price) : (num(r.yes_bid) != null ? 100 - num(r.yes_bid) : null);
    const side = r.sit_pick, pYes = num(r.sit_hit), pSide = side === 'Yes' ? pYes : 100 - pYes;
    const label = rhLabel(r.contract);
    const b = el('button', 'wx-read'); b.type = 'button';
    const top = el('span', 'wx-read-top'); top.append(el('span', null, `${r.game} · ${r.kickoff}`), el('span', null, WX_MKT[r.sit_stat] || r.market));
    const big = el('span', 'wx-read-big'); big.append(String(Math.round(pSide)), el('small', null, '%'));
    const lab = el('span', 'wx-mono'); lab.append('Wedge', document.createElement('br'), side === 'Yes' ? 'Yes' : 'No');
    const mid = el('span', 'wx-read-mid'); mid.append(big, lab);
    const px = el('span', 'wx-read-px');
    const py = el('span', side === 'Yes' ? 'is-pick' : ''); py.append(el('span', null, 'Yes'), el('span', null, yes == null ? '—' : yes + '¢'));
    const pn = el('span', side === 'No' ? 'is-pick' : ''); pn.append(el('span', null, 'No'), el('span', null, no == null ? '—' : no + '¢'));
    px.append(py, pn);
    const foot = el('span', 'wx-read-foot'); const dot = el('i', 'wx-dot'); dot.setAttribute('aria-hidden', 'true');
    foot.append(dot, `${side}, +${Math.round(num(r.sit_pedge))} pts vs price`, el('em', null, 'Read ↗'));
    b.append(top, el('b', 'wx-read-title', label), mid, px, foot);
    b.setAttribute('aria-label', `${label}, ${r.game}, ${r.kickoff}. Wedge reads ${side}: ${Math.round(pSide)}% against ${side === 'Yes' ? yes : no} cents. Open the full read.`);
    const ctx = { title: label, game: r.game, market: r.market, source: r.source };
    ctx.key = `${ctx.game}|${ctx.market}|${r.contract}`;
    b.addEventListener('click', () => openSit(r, ctx, b));
    return b;
  };
  function drawLobby() {
    const ld = dash.data('lines'), la = dash.data('lines_all');
    if (la.status === 'ok') document.querySelectorAll('[data-wg-count="every"]').forEach((e) => { e.textContent = wgFmt(la.data.length); });
    if (ld.status === 'ok') {
      const picks = ld.data.filter((r) => r.sit_pick && r.sit_key && num(r.sit_hit) != null).sort((a, b) => num(b.sit_pedge) - num(a.sit_pedge));
      document.querySelectorAll('[data-wg-count="lines"]').forEach((e) => { e.textContent = wgFmt(ld.data.length); });
      document.querySelectorAll('[data-wg-count="picks"]').forEach((e) => { e.textContent = wgFmt(picks.length); });
      const per = new Map(), bySide = { Yes: [], No: [] };
      for (const r of picks) { const c = per.get(r.game) || 0; if (c >= 2 || bySide[r.sit_pick].length >= 3) continue; per.set(r.game, c + 1); bySide[r.sit_pick].push(r); }
      const top = []; for (let k = 0; k < 3; k++) { if (bySide.No[k]) top.push(bySide.No[k]); if (bySide.Yes[k]) top.push(bySide.Yes[k]); }
      const box = $('#wg-hot-cards');
      if (box) box.replaceChildren(...(top.length ? top.map(wxRead) : [el('p', 'wx-empty', 'No line clears its price by 3+ points right now.')]));
    } else if (ld.status === 'error') { const box = $('#wg-hot-cards'); if (box) box.replaceChildren(el('p', 'wx-empty', 'This week’s lines failed to load. Reload the page to try again.')); }
    const bt = dash.data('bt_weeks');
    if (bt.status === 'ok') {
      const row = (g, sg) => bt.data.find((r) => String(r.week) === 'all' && r.seg_group === g && r.segment === sg);
      const put = (k, v) => { const e = document.querySelector(`[data-wg-rcpt="${k}"]`); if (e && v != null) e.textContent = v; };
      const sg = (x) => (Number(x) > 0 ? '+' : Number(x) < 0 ? '−' : '') + Math.abs(Number(x)).toFixed(1) + '%';
      const wp = row('Strategy', 'Wedge picks (3+ pts)'), ey = row('Strategy', 'Every Yes'), pa = row('Market', 'Props · passing'), ru = row('Market', 'Props · rushing');
      if (wp) { const e = document.querySelector('[data-wg-rcpt="picks-pct"]'); if (e) { e.replaceChildren((+wp.win_pct).toFixed(1), el('small', null, '%')); } put('picks-txt', `${wp.wins}–${wp.losses} over Weeks 6–8, ${sg(wp.roi_pct)} before fees.`); }
      if (ey) put('yes-roi', sg(ey.roi_pct));
      if (pa) put('pass-pct', (+pa.win_pct).toFixed(1) + '%');
      if (ru) put('rush-pct', (+ru.win_pct).toFixed(1) + '%');
    }
  }
'''
rep('  // ---------------- render ----------------\n  dash.onData(() => {', JS + '\n  // ---------------- render ----------------\n  dash.onData(() => {')
rep('    drawProfit();\n    drawAnalysts();\n    drawBtPerms();', '    drawProfit();\n    drawLobby();\n    drawAnalysts();\n    drawBtPerms();')

# ---------------------------------------------------------------- the name: Wedger -> Wedge (visible text and matching code; db paths stay "wedger/...")
s = s.replace('Wedger', 'Wedge')
open(B + 'page_template.html', 'w').write(s)
print('wedge ok')
