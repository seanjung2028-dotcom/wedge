"""Thu Nov 5: Wedge UI round 3 (Sean's Pt. 2 notes + Chris's Motion Lab "Poster fade").
- One continuous surface, edge to edge: grainy graphite poster fade (#34373B -> #8A8F95 -> #E0E2E5, grain overlay) with slow drifting
  light pools; no boxed header, no lifted hero. White text on darker gray; brushed radial metal with darker hues where metal shows.
- Hero after the 36-5 poster: the record as one big wide number over a dark blur, outline chips, crosshair, black / white pill buttons.
- Nav: pills in the header row, a Subscribe tab and page; plans as a ladder that gets more premium per step.
- Reads: stronger team-color sheen, numbers roll and words lift on hover, a real "Full read" pill that pops.
- Photo helmets (recolored from Sean's reference) in matchups, schedule and analyst picks; analyst picks grouped by team.
- Team colors stay in the long lists (game cells, row edge); charts and tables restyled to match.
Runs on the final index.html after patch_w9e.py."""
import json, re
B = '/home/claude/wedger/rh/'
s = open(B + 'index.html').read()
FB = json.load(open('/home/claude/wedger/brand/font_blobs.json'))
HB = json.load(open('/home/claude/wedger/helm/helm_blobs.json'))
WM = json.load(open('/home/claude/wedger/brand/wordmark_blobs.json'))

def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, (old[:110], c); s = s.replace(old, new)
def cut(start, end_marker):
    i = s.index(start); j = s.index(end_marker, i); return i, j

# ============================================================================ CSS
CSS = r'''
  /* ===================== Wedge round 3: poster fade, one surface ===================== */
  #dash-root { --dash-gutter: 0; }
  @font-face { font-family: "Archivo Wide"; src: url("/_blob/@archivowide") format("woff2"); font-weight: 100 900; font-stretch: 62% 125%; font-style: normal; font-display: swap; }
  .wg-paper.wg-paper.wg-paper.wg-paper {
    --pf-wide: "Archivo Wide", "Archivo", "Helvetica Neue", Arial, sans-serif;
    --pf-ink: #F6F7F8; --pf-muted: #B9BEC4; --pf-faint: #8A9098; --pf-line: rgba(255, 255, 255, .14); --pf-glass: rgba(255, 255, 255, .055); --pf-glass-hi: rgba(255, 255, 255, .09);
    --pf-metal-light: conic-gradient(from 214deg at 64% 36%, #9AA0A7 0deg, #D2D6DA 38deg, #F6F7F8 72deg, #B5BAC0 112deg, #868B92 158deg, #A7ACB2 204deg, #ECEEF0 252deg, #C0C5CA 300deg, #9AA0A7 360deg);
    --pf-metal-dark: conic-gradient(from 210deg at 50% 50%, #2B2E33 0deg, #6F757C 32deg, #DDE0E3 64deg, #8A8F95 96deg, #34373B 142deg, #1E2125 190deg, #5E636A 236deg, #C8CCD1 272deg, #7D838A 312deg, #2B2E33 360deg);
    --pf-fade: linear-gradient(42deg, #34373B 0%, #8A8F95 55%, #E0E2E5 100%);
    --wx-ink: #F6F7F8; --wx-muted: #B9BEC4; --wx-faint: #8A9098; --wx-rule: rgba(255, 255, 255, .14); --wx-green-ink: #00B04E;
    --color-bg: #1B1D21; --color-panel: #23262B; --color-fg: #F6F7F8; --color-fg-muted: #B9BEC4; --color-border-line: rgba(255, 255, 255, .12);
    --color-ok: #00B04E; --color-bad: #F08A76; --color-warn: #E3B95E;
    --cds-chart-grid: rgba(255, 255, 255, .08); --cds-chart-muted: #5A6067; --cds-chart-reference: #9DA3AA; --cds-chart-status-critical: #F08A76;
    --cds-surface-popover: #23262B; --cds-border: rgba(255, 255, 255, .14); --cds-text-secondary: #B9BEC4; --cds-shadow-popover: 0 18px 40px -16px rgba(0, 0, 0, .8);
    --wg-green: #009A44; --wg-lime: #009A44; --wg-ink: #00B04E; --wg-bull: #009A44; --wg-bear: #F08A76;
    --wg-soft: rgba(0, 154, 68, .2); --wg-softer: rgba(0, 154, 68, .1);
    --wg-c1: #00B04E; --wg-c2: #6E9BD6; --wg-c3: #D59A4F; --wg-c4: #A98BD0;
    --wz-spot: rgba(255, 255, 255, .10);
    color-scheme: dark; color: #F6F7F8;
    position: relative; isolation: isolate; overflow: clip; min-height: 100vh;
    background: linear-gradient(180deg, #24272B 0%, #1D2024 30%, #22252A 62%, #1A1C20 100%);
  }
  .wg-paper::before { display: none !important; }
  .wg-paper::after { content: ''; position: absolute; inset: 0; z-index: 3; pointer-events: none; background-image: var(--wx-grain); background-size: 180px 180px; opacity: .22; mix-blend-mode: overlay; }
  .pf-bg { position: absolute; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
  .pf-bg i { position: absolute; display: block; width: 72vmax; height: 72vmax; border-radius: 50%; will-change: transform; animation: pfDrift 38s ease-in-out infinite alternate; }
  .pf-bg i:nth-child(1) { top: 2%; left: 52%; background: radial-gradient(closest-side, rgba(224, 226, 229, .34), rgba(138, 143, 149, .12) 55%, transparent); }
  .pf-bg i:nth-child(2) { top: 22%; left: -24%; background: radial-gradient(closest-side, rgba(138, 143, 149, .26), transparent 70%); animation-duration: 46s; animation-delay: -12s; }
  .pf-bg i:nth-child(3) { top: 41%; left: 48%; background: radial-gradient(closest-side, rgba(224, 226, 229, .2), rgba(138, 143, 149, .08) 55%, transparent); animation-duration: 52s; animation-delay: -20s; }
  .pf-bg i:nth-child(4) { top: 60%; left: -18%; background: radial-gradient(closest-side, rgba(10, 11, 13, .55), transparent 70%); animation-duration: 44s; animation-delay: -6s; }
  .pf-bg i:nth-child(5) { top: 76%; left: 40%; background: radial-gradient(closest-side, rgba(200, 204, 209, .22), transparent 70%); animation-duration: 58s; animation-delay: -30s; }
  .pf-bg i:nth-child(6) { top: 92%; left: -10%; background: radial-gradient(closest-side, rgba(138, 143, 149, .2), transparent 70%); animation-duration: 40s; }
  @keyframes pfDrift { 0% { transform: translate3d(0, 0, 0) scale(1); } 50% { transform: translate3d(6vw, -3vh, 0) scale(1.08); } 100% { transform: translate3d(-5vw, 4vh, 0) scale(.94); } }
  .wg-paper > .rs-wrap { position: relative; z-index: 1; max-width: 1440px; padding: 0 clamp(16px, 4.2vw, 64px) 72px; gap: 22px; }
  .wg-paper .wx-mark.i { display: none !important; } .wg-paper .wx-mark.l { display: block !important; }

  /* type */
  .pf-wide, .pf-h2, .pf-h1, .pf-big, .pf-price, .wx-band h2, .wx-read-big, .wz-an-pct, .pf-tt b, .pf-mt b { font-family: var(--pf-wide); font-stretch: 118%; }
  .pf-label, .wz-label { font-family: var(--wx-mono); font-size: 12.5px; letter-spacing: .1em; text-transform: uppercase; color: var(--pf-muted); }
  .pf-h2 { margin: 12px 0 0; font-weight: 850; font-size: clamp(34px, 5vw, 68px); line-height: .92; letter-spacing: -0.02em; text-transform: uppercase; color: var(--pf-ink); }
  .pf-sub { margin: 0; max-width: 30rem; font-size: 17px; line-height: 1.6; color: var(--pf-muted); }
  .pf-head { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-end; gap: 14px 44px; }
  .pf-sec { position: relative; display: flex; flex-direction: column; gap: 26px; padding: clamp(48px, 7vw, 104px) 0 0; min-width: 0; }
  .pf-row { display: flex; flex-wrap: wrap; align-items: center; gap: 12px 18px; }

  /* pills: buttons and chips */
  .wz-btn { padding: 14px 24px; border-radius: 999px; font-family: var(--wz-display); font-weight: 700; font-size: 15.5px; letter-spacing: -0.005em; border: 1px solid transparent; }
  .wz-btn-lg { padding: 17px 30px; font-size: 17px; }
  .wz-btn-sm { padding: 10px 17px; font-size: 14px; }
  .wz-btn-g { background: #009A44; color: #06120B; border-color: rgba(255, 255, 255, .18); box-shadow: 0 14px 30px -16px rgba(0, 154, 68, .9); }
  .wz-btn-g:hover { background: #00B04E; color: #06120B; }
  .wz-btn-w { background: #F6F7F8; color: #0D0F12; box-shadow: 0 14px 30px -18px rgba(0, 0, 0, .9); }
  .wz-btn-w:hover { background: #FFFFFF; }
  .wz-btn-k { background: #0D0F12; color: #F6F7F8; box-shadow: 0 14px 30px -16px rgba(0, 0, 0, .8); }
  .wz-btn-k:hover { background: #000; }
  .wz-btn-line, .wz-btn-ghost { background: rgba(255, 255, 255, .02); color: #F6F7F8; border-color: rgba(255, 255, 255, .42); }
  .wz-btn-line:hover, .wz-btn-ghost:hover { background: rgba(255, 255, 255, .1); border-color: rgba(255, 255, 255, .7); }
  .wz-btn:focus-visible { outline: 2px solid #F6F7F8; outline-offset: 3px; }
  .wz-link { color: #F6F7F8; }
  .pf-chips { display: flex; flex-wrap: wrap; gap: 8px; }
  .pf-chip { display: inline-flex; align-items: center; gap: 7px; padding: 7px 13px; border-radius: 999px; border: 1.5px solid rgba(255, 255, 255, .55); font-family: var(--wx-mono); font-size: 13px; letter-spacing: .04em; text-transform: uppercase; color: #F6F7F8; background: rgba(13, 15, 18, .18); -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px); }
  .pf-chip b { font-weight: 500; color: #FFFFFF; }
  .pf-chip.g { border-color: #009A44; }
  .pf-chip .wx-dot { width: 7px; height: 7px; background: #009A44; }

  /* header: one row on the surface, no box */
  .wz-top { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; grid-template-areas: "logo nav right" "note note note"; align-items: center; gap: 8px 24px;
    background: none; border: 0; border-radius: 0; box-shadow: none; padding: 22px 0 6px; margin: 0; color: #F6F7F8; }
  .wz-bar { display: contents; }
  .wz-logo { grid-area: logo; }
  .wz-logo img { height: 36px; }
  .wz-bar-r { grid-area: right; margin: 0; }
  .wz-top #certnote { grid-area: note; }
  .wz-top .rs-tabs { grid-area: nav; justify-self: center; gap: 4px; margin: 0; padding: 4px; border-radius: 999px; border: 1px solid rgba(255, 255, 255, .14); background: rgba(13, 15, 18, .42); max-width: 100%; }  /* no backdrop-filter here: it would trap the NFL menu inside the scrolling tab row */
  .wz-top .rs-tab { font-family: var(--wz-display); font-size: 15.5px; font-weight: 600; padding: 9px 15px; border-radius: 999px; color: rgba(246, 247, 248, .78); border: 1px solid transparent; transition: background .25s, color .2s, border-color .25s; }
  .wz-top .rs-tab::after { display: none; }
  .wz-top .rs-tab:hover { color: #FFFFFF; background: rgba(255, 255, 255, .08); }
  .wz-top .rs-tab[aria-current=page] { color: #0D0F12; background: #F6F7F8; }
  .wz-top .rs-tab[aria-current=page] .wg-dd-cur { color: #2A2D31; }
  .wz-top .pf-subtab { color: #F6F7F8; border-color: rgba(0, 154, 68, .85); }
  .wz-top .pf-subtab:hover { background: #009A44; color: #06120B; }
  .wz-top .pf-subtab[aria-current=page] { background: #009A44; color: #06120B; }
  .wz-top .wg-tabsep { background: rgba(255, 255, 255, .16); height: 20px; margin: 0 4px; }
  .wz-top .wg-record { flex-direction: row; align-items: center; gap: 10px; padding: 7px 14px; margin: 0; border: 1px solid rgba(255, 255, 255, .22); border-radius: 999px; background: rgba(13, 15, 18, .25); }
  .wz-top .wg-record-label { font-size: 11px; color: var(--pf-muted); }
  .wz-top .wg-record-pct, .wz-top .wg-record.wg-up .wg-record-pct { font-size: 18px; }
  .wz-top .wg-dd-menu { background: rgba(28, 31, 35, .96); border: 1px solid rgba(255, 255, 255, .14); border-radius: 14px; padding: 8px; -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px); box-shadow: 0 30px 60px -24px rgba(0, 0, 0, .85); }
  .wz-top .wg-dd-item { color: #E6E8EB; border-radius: 8px; }
  .wz-top .wg-dd-item:hover { background: rgba(255, 255, 255, .08); }
  .wz-top .wg-dd-label { color: var(--pf-faint); }
  @media (max-width: 1520px) { .wz-top .wg-record-label { font-size: 0; gap: 0; } .wz-top .wg-record-frac { display: none; } .wz-top .rs-tab { padding-inline: 13px; } }
  @media (max-width: 1120px) { .wz-top { grid-template-columns: auto minmax(0, 1fr); grid-template-areas: "logo right" "nav nav" "note note"; } .wz-top .rs-tabs { justify-self: stretch; } .wz-bar-r { justify-self: end; } }
  @media (max-width: 720px) { .wz-top .wg-record { display: none; } .wz-top .rs-tab { font-size: 15px; padding: 8px 12px; } }

  /* hero: the 36-5 poster */
  .pf-hero { position: relative; isolation: isolate; display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(0, .95fr); align-items: center; gap: clamp(24px, 4vw, 60px); min-height: min(74vh, 740px); padding: clamp(28px, 4vw, 56px) 0 clamp(56px, 7vw, 96px); }
  .pf-hero-bg { position: absolute; z-index: -1; top: -140px; bottom: -40px; left: calc(50% - 50vw); right: calc(50% - 50vw); overflow: hidden; pointer-events: none;
    -webkit-mask-image: linear-gradient(180deg, #000 0%, #000 70%, transparent 100%); mask-image: linear-gradient(180deg, #000 0%, #000 70%, transparent 100%); }
  .pf-metal { position: absolute; left: 50%; top: 46%; width: 170vmax; height: 170vmax; margin: -85vmax 0 0 -85vmax; background: var(--pf-metal-dark); filter: blur(38px) saturate(.9); opacity: .9; will-change: transform; animation: pfSpin 140s linear infinite; }
  @keyframes pfSpin { to { transform: rotate(360deg); } }
  .pf-scrim { position: absolute; inset: 0; background: linear-gradient(90deg, rgba(20, 22, 25, .82) 0%, rgba(20, 22, 25, .5) 40%, rgba(20, 22, 25, .1) 64%, rgba(20, 22, 25, .25) 100%), linear-gradient(180deg, rgba(20, 22, 25, .55) 0%, transparent 30%); }
  .pf-hero-copy { position: relative; display: flex; flex-direction: column; gap: 24px; min-width: 0; }
  .pf-h1 { margin: 0; font-weight: 900; font-size: clamp(36px, 4.9vw, 72px); line-height: .9; letter-spacing: -0.015em; text-transform: uppercase; color: #F6F7F8; text-shadow: 0 2px 30px rgba(0, 0, 0, .35); }
  .pf-h1 em { font-style: normal; color: #009A44; }
  .pf-lede { margin: 0; max-width: 32rem; font-size: 19px; line-height: 1.55; color: #D6D9DD; }
  .pf-fine { margin: 0; font-family: var(--wx-mono); font-size: 12.5px; letter-spacing: .04em; color: var(--pf-muted); }
  .pf-proof { position: relative; display: flex; flex-direction: column; align-items: flex-start; gap: 18px; min-width: 0; padding: clamp(24px, 4vw, 48px) 0; }
  .pf-blob { position: absolute; z-index: -1; left: -6%; top: 2%; width: 92%; height: 92%; border-radius: 46%; background: radial-gradient(closest-side, rgba(12, 13, 16, .94), rgba(12, 13, 16, .62) 52%, rgba(12, 13, 16, 0)); filter: blur(26px); animation: pfBlob 18s ease-in-out infinite alternate; }
  @keyframes pfBlob { from { transform: translate(0, 0) scale(1); } to { transform: translate(4%, -3%) scale(1.06); } }
  .pf-cross { position: absolute; z-index: -1; inset: -20% -40% -20% -10%; pointer-events: none; background: linear-gradient(90deg, transparent calc(42% - .5px), rgba(255, 255, 255, .32) 42%, transparent calc(42% + .5px)), linear-gradient(180deg, transparent calc(56% - .5px), rgba(255, 255, 255, .32) 56%, transparent calc(56% + .5px)); }
  .pf-big { font-weight: 900; font-stretch: 125%; font-size: clamp(80px, 10.5vw, 168px); line-height: .82; letter-spacing: -0.03em; color: #F6F7F8; font-variant-numeric: tabular-nums; text-shadow: 0 6px 40px rgba(0, 0, 0, .35); }
  .pf-big small { font-size: .38em; letter-spacing: 0; margin-left: .06em; }
  .pf-cap { font-family: var(--wx-mono); font-size: 12.5px; letter-spacing: .07em; line-height: 1.7; text-transform: uppercase; color: #D6D9DD; max-width: 30rem; }
  @media (max-width: 940px) { .pf-hero { grid-template-columns: 1fr; min-height: 0; } .pf-proof { padding-top: 8px; } .pf-cross { display: none; } }

  /* ticker: two thin strips on the surface */
  .wz-ticker { margin: 0 calc(50% - 50vw); border-radius: 0; background: rgba(10, 11, 13, .38); border-top: 1px solid rgba(255, 255, 255, .1); border-bottom: 1px solid rgba(255, 255, 255, .1); -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px); }
  .wz-tape + .wz-tape { border-top-color: rgba(255, 255, 255, .07); }
  .wz-tk { border-right-color: rgba(255, 255, 255, .07); color: #C9CED4; font-size: 13.5px; }

  /* cards on the surface: glass, rounded, no grid of boxes */
  .wx-reads { gap: 16px; }
  .wx-read { position: relative; overflow: hidden; background: var(--pf-glass); border: 1px solid rgba(255, 255, 255, .12); border-radius: 20px; padding: 24px; color: #F6F7F8; -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px);
    transition: transform .4s cubic-bezier(.2, .7, .2, 1), border-color .4s, box-shadow .4s, background-color .4s; }
  .wx-read:hover { background: var(--pf-glass-hi); transform: translateY(-6px); box-shadow: 0 34px 60px -34px rgba(0, 0, 0, .9); border-color: rgba(255, 255, 255, .28); }
  .wx-read.wz-tc { box-shadow: inset 3px 0 0 color-mix(in srgb, var(--tc1) 85%, #fff); }
  .wx-read.wz-tc:hover { border-color: color-mix(in srgb, var(--tc1) 55%, rgba(255, 255, 255, .45)); box-shadow: inset 3px 0 0 var(--tc1), 0 34px 60px -30px color-mix(in srgb, var(--tc1) 55%, rgba(0, 0, 0, .9)); }
  .wx-read.wz-tc::before { background: linear-gradient(118deg, color-mix(in srgb, var(--tc1) 42%, transparent) 0%, color-mix(in srgb, var(--tc1) 14%, transparent) 38%, color-mix(in srgb, var(--tc2) 30%, transparent) 72%, color-mix(in srgb, var(--tc2) 8%, transparent) 100%),
      linear-gradient(100deg, transparent 32%, color-mix(in srgb, var(--tc2) 26%, rgba(255, 255, 255, .22)) 50%, transparent 68%); background-size: 100% 100%, 230% 100%; }
  .wx-read-top { color: var(--pf-muted); font-size: 12px; }
  .wx-read-title { color: #F6F7F8; font-size: 20px; }
  .pf-w { display: inline-block; transition: transform .45s cubic-bezier(.2, .7, .2, 1), color .3s; transition-delay: calc(var(--i, 0) * 28ms); }
  .wx-read:hover .pf-w { transform: translateY(-3px); }
  .wx-read-big { color: #F6F7F8; font-weight: 900; font-size: 64px; letter-spacing: -0.02em; transition: transform .45s cubic-bezier(.2, .7, .2, 1); transform-origin: left bottom; }
  .wx-read:hover .wx-read-big { transform: scale(1.06); }
  .pf-roll { display: inline-block; height: 1em; line-height: 1; overflow: hidden; vertical-align: bottom; }
  .pf-roll > span { display: block; text-shadow: 0 1em 0 currentColor; }
  .wx-read:hover .pf-roll > span { animation: pfRoll .75s cubic-bezier(.3, .7, .2, 1); }
  @keyframes pfRoll { from { transform: translateY(0); } to { transform: translateY(-1em); } }
  .wx-read-mid .wx-mono { color: var(--pf-muted); }
  .wx-read-px { border-top-color: rgba(255, 255, 255, .14); }
  .wx-read-px span { color: var(--pf-muted); }
  .wx-read-px span.is-pick { color: #FFFFFF; }
  .wx-read-px span + span { border-left-color: rgba(255, 255, 255, .14); }
  .wz-hr { color: var(--pf-muted); }
  .wz-hr b { color: #FFFFFF; font-family: var(--pf-wide); font-stretch: 112%; font-size: 22px; }
  .wx-read-foot { color: #E6E8EB; }
  .wx-read-foot .wx-dot { background: #009A44; }
  .wx-read-foot em { margin-left: auto; padding: 8px 15px; border-radius: 999px; border: 1.5px solid rgba(255, 255, 255, .5); font-family: var(--wz-display); font-size: 13.5px; font-weight: 700; letter-spacing: 0; text-transform: none; color: #F6F7F8;
    transition: background .3s, color .3s, transform .35s cubic-bezier(.2, .7, .2, 1), box-shadow .3s, border-color .3s; }
  .wx-read:hover .wx-read-foot em { background: #F6F7F8; color: #0D0F12; border-color: #F6F7F8; transform: translateY(-3px) scale(1.07); box-shadow: 0 14px 28px -12px rgba(0, 0, 0, .9); }
  .wx-reads .wx-empty { background: var(--pf-glass); border: 1px solid rgba(255, 255, 255, .1); border-radius: 20px; color: var(--pf-muted); }
  .wx-tabs { border-bottom: 0; gap: 8px; padding: 2px 0 6px; }
  .wx-tab { border: 1px solid rgba(255, 255, 255, .18); border-radius: 999px; padding: 10px 15px; margin: 0; color: #D6D9DD; font-size: 12.5px; background: rgba(255, 255, 255, .03); }
  .wx-tab:hover { color: #FFFFFF; border-color: rgba(255, 255, 255, .45); }
  .wx-tab[aria-selected="true"] { color: #0D0F12; background: #F6F7F8; border-color: #F6F7F8; }

  /* matchup banner with photo helmets */
  .wz-matchup { border-radius: 24px; min-height: 190px; padding: 18px clamp(16px, 3vw, 40px);
    background: radial-gradient(120% 140% at 0% 50%, color-mix(in srgb, var(--ca) 92%, #000) 0%, color-mix(in srgb, var(--ca) 55%, #0D0F12) 42%, transparent 62%), radial-gradient(120% 140% at 100% 50%, color-mix(in srgb, var(--cb) 92%, #000) 0%, color-mix(in srgb, var(--cb) 55%, #0D0F12) 42%, transparent 62%), #0D0F12; }
  .wz-matchup::after { background: linear-gradient(180deg, rgba(255, 255, 255, .1), transparent 40%, rgba(0, 0, 0, .28)), var(--wx-grain); background-size: auto, 180px 180px; opacity: .55; mix-blend-mode: overlay; }
  .wz-helm { display: block; width: clamp(120px, 15vw, 230px); height: auto; filter: drop-shadow(0 18px 22px rgba(0, 0, 0, .55)); }
  .wz-helm.flip { transform: scaleX(-1); }
  .wz-matchup:hover .wz-mt-side:not(.home) .wz-helm { transform: translateX(8px) rotate(-3deg); }
  .wz-matchup:hover .wz-mt-side.home .wz-helm { transform: scaleX(-1) translateX(8px) rotate(-3deg); }
  .wz-matchup.enter .wz-mt-side.home .wz-helm { animation: pfInR .8s cubic-bezier(.2, .7, .2, 1) both; }
  @keyframes pfInR { from { opacity: 0; transform: scaleX(-1) translateX(-50px); } to { opacity: 1; transform: scaleX(-1); } }
  .wz-mt-side b { font-weight: 900; font-size: clamp(32px, 4.4vw, 58px); }
  .wz-helm-none { display: block; width: 60px; height: 60px; }

  /* analysts */
  .wz-an { background: var(--pf-glass); border: 1px solid rgba(255, 255, 255, .12); border-radius: 20px; color: #F6F7F8; -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); }
  .wz-an.lead { background: var(--pf-metal-light); color: #121417; border-color: rgba(255, 255, 255, .6); --wz-spot: rgba(255, 255, 255, .55); }
  .wz-an.lead .wz-an-meta span, .wz-an.lead .wz-dots small { opacity: .85; }
  .wz-an-pct { font-weight: 900; letter-spacing: -0.02em; }
  .wz-an .wz-av { background: linear-gradient(145deg, #F7F8F9, #8A8F95); }
  .wz-dots i.w { background: #009A44; border-color: #009A44; }

  /* plans: a ladder that gets more premium each step */
  .pf-ladder { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; align-items: end; }
  .pf-tier { position: relative; isolation: isolate; overflow: hidden; display: flex; flex-direction: column; gap: 18px; min-width: 0; padding: 30px 28px; border-radius: 26px; transition: transform .45s cubic-bezier(.2, .7, .2, 1), box-shadow .45s; }
  .pf-tier:hover { transform: translateY(-8px); }
  .pf-tier h3 { margin: 0; font-family: var(--wz-display); font-weight: 800; font-size: 22px; letter-spacing: -0.01em; }
  .pf-tk { font-family: var(--wx-mono); font-size: 12px; letter-spacing: .1em; text-transform: uppercase; opacity: .8; }
  .pf-top { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
  .pf-price { display: flex; align-items: baseline; gap: 8px; font-weight: 900; line-height: .9; letter-spacing: -0.03em; font-variant-numeric: tabular-nums; }
  .pf-price span { font-family: var(--wz-display); font-stretch: 100%; font-weight: 500; font-size: 16px; letter-spacing: 0; opacity: .75; }
  .pf-tier p { margin: -6px 0 0; font-size: 15px; opacity: .85; }
  .pf-tier .wz-feats { border-top-color: currentColor; }
  .pf-tier .wz-btn { margin-top: auto; width: 100%; text-align: center; }
  .pf-flag { font-family: var(--wx-mono); font-size: 11.5px; letter-spacing: .08em; text-transform: uppercase; padding: 6px 11px; border-radius: 999px; border: 1.5px solid currentColor; }
  .pf-tier.t1 { background: var(--pf-glass); border: 1px solid rgba(255, 255, 255, .14); color: #E6E8EB; -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); }
  .pf-tier.t1 .pf-price { font-size: 44px; }
  .pf-tier.t1 { padding-block: 26px; }
  .pf-tier.t1 .wz-feats li::before { background-color: rgba(255, 255, 255, .22); }
  .pf-tier.t2 { padding-block: 38px; background: var(--pf-metal-light); color: #121417; box-shadow: inset 0 1px 0 rgba(255, 255, 255, .9), 0 40px 70px -40px rgba(0, 0, 0, .9); --wz-spot: rgba(255, 255, 255, .55); }
  .pf-tier.t2::before { content: ''; position: absolute; inset: 0; z-index: -1; background-image: var(--wx-grain); background-size: 180px 180px; opacity: .35; mix-blend-mode: overlay; }
  .pf-tier.t2 .pf-price { font-size: 54px; }
  .pf-tier.t3 { padding-block: 50px; color: #F6F7F8; border: 1.5px solid transparent;
    background: linear-gradient(165deg, #121417, #070809) padding-box, conic-gradient(from var(--pf-a, 0deg), #009A44, #9BE15D, #E0E2E5, #8A8F95, #009A44) border-box;
    box-shadow: 0 0 80px -30px rgba(0, 154, 68, .65), 0 50px 80px -40px rgba(0, 0, 0, .95); animation: pfBorder 8s linear infinite; }
  @property --pf-a { syntax: '<angle>'; inherits: false; initial-value: 0deg; }
  @keyframes pfBorder { to { --pf-a: 360deg; } }
  .pf-tier.t3::before { content: ''; position: absolute; inset: 0; z-index: -1; background: radial-gradient(80% 60% at 85% 0%, rgba(0, 154, 68, .28), transparent 60%), radial-gradient(70% 50% at 0% 100%, rgba(224, 226, 229, .1), transparent 60%); }
  .pf-tier.t3 .pf-price { font-size: 64px; background: linear-gradient(180deg, #FFFFFF 10%, #DADDE1 45%, #8A8F95 70%, #F4F5F7 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
  .pf-tier.t3 .pf-price span { color: #B9BEC4; -webkit-text-fill-color: #B9BEC4; }
  .pf-tier.t3 .pf-flag { border-color: #009A44; background: #009A44; color: #06120B; }
  @media (max-width: 980px) { .pf-ladder { grid-template-columns: 1fr; } .pf-tier.t2, .pf-tier.t3 { padding-block: 30px; } }
  .pf-price { font-stretch: 110%; }

  /* schedule + coverage */
  .wz-game { border-bottom-color: rgba(255, 255, 255, .1); border-radius: 14px; color: #F6F7F8; }
  .wz-game:hover { background: rgba(255, 255, 255, .06); }
  .wz-game small { color: var(--pf-muted); }
  .wz-st { border-color: rgba(255, 255, 255, .2); color: var(--pf-muted); border-radius: 999px; }
  .pf-hp { display: inline-flex; align-items: center; }
  .pf-hp .wz-helm { width: 54px; filter: drop-shadow(0 6px 8px rgba(0, 0, 0, .5)); }
  .pf-hp .wz-helm { width: 50px; }
  .pf-hp .wz-helm + .wz-helm { margin-left: 4px; }
  .wz-cover { background: var(--pf-glass); border: 1px solid rgba(255, 255, 255, .12); border-radius: 22px; -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); }
  .wz-cover > div { border-bottom-color: rgba(255, 255, 255, .1); }
  .wz-cover em { border-radius: 999px; }

  /* how a read works + closing line */
  .wz-steps { border-top: 1px solid rgba(255, 255, 255, .3); }
  .wz-steps li { border-bottom-color: rgba(255, 255, 255, .1); }
  .wz-steps .n { color: #009A44; font-family: var(--pf-wide); font-stretch: 120%; }
  .wz-steps b { color: #F6F7F8; }
  .wz-steps p { color: var(--pf-muted); }
  .wz-ex { background: var(--pf-metal-light); border-radius: 24px; border-color: rgba(255, 255, 255, .6); }
  .pf-quote { position: relative; display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr); gap: clamp(28px, 5vw, 64px); align-items: end; padding: clamp(60px, 9vw, 130px) 0 clamp(30px, 4vw, 50px); }
  .pf-quote blockquote { margin: 0; font-family: var(--pf-wide); font-stretch: 118%; font-weight: 850; text-transform: uppercase; font-size: clamp(32px, 4.6vw, 64px); line-height: .96; letter-spacing: -0.015em; color: #F6F7F8; }
  .pf-quote blockquote::before { content: ''; display: block; width: 64px; height: 4px; border-radius: 4px; background: #009A44; margin-bottom: 30px; }
  .pf-quote .wx-ledger { border-top: 1px solid rgba(255, 255, 255, .45); }
  .pf-quote .wx-ledger div { border-bottom-color: rgba(255, 255, 255, .1); }
  .pf-quote .wx-ledger span { color: var(--pf-muted); font-size: 12px; }
  .pf-quote .wx-ledger b { color: #F6F7F8; font-family: var(--pf-wide); font-stretch: 112%; font-weight: 800; font-size: 22px; }
  @media (max-width: 760px) { .pf-quote { grid-template-columns: 1fr; } }
  .wg-lobby .wx-fine, .pf-subpage .wx-fine { color: var(--pf-faint); padding-top: 34px; }

  /* subscribe page */
  .pf-subhero { display: grid; gap: 18px; padding: clamp(40px, 7vw, 96px) 0 clamp(24px, 4vw, 40px); max-width: 60rem; }
  .pf-perks { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 230px), 1fr)); gap: 16px; padding-top: clamp(40px, 6vw, 80px); }
  .pf-perk { padding: 24px; border-radius: 20px; background: var(--pf-glass); border: 1px solid rgba(255, 255, 255, .12); }
  .pf-perk b { display: block; font-family: var(--pf-wide); font-stretch: 112%; font-weight: 800; font-size: 20px; margin: 10px 0 6px; }
  .pf-perk p { margin: 0; color: var(--pf-muted); font-size: 15px; line-height: 1.55; }
  .pf-perk .n { font-family: var(--wx-mono); font-size: 12px; letter-spacing: .1em; color: #009A44; }

  /* inner pages: headers on the surface, glass cards, team colors in rows */
  .wx-band { background: none; padding: clamp(28px, 5vw, 64px) 0 6px; color: #F6F7F8; }
  .wx-band::before, .wx-band::after { display: none; }
  .wx-band h2 { font-weight: 900; text-transform: uppercase; font-size: clamp(36px, 5.6vw, 76px); letter-spacing: -0.015em; color: #F6F7F8; }
  .wx-band p, .wx-band .wx-label { color: var(--pf-muted); }
  .rs-card { background: var(--pf-glass); border: 1px solid rgba(255, 255, 255, .11); border-radius: 22px; -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); }
  .rs-card h2 { color: #F6F7F8; }
  .rs-note { color: var(--pf-muted); }
  .rs-controls select, .rs-controls input[type="search"], .wz-filters > summary { background: rgba(255, 255, 255, .06); color: #F6F7F8; border: 1px solid rgba(255, 255, 255, .18); border-radius: 999px; padding-inline: 16px; }
  .wz-filters-in { background: #23262B; border-color: rgba(255, 255, 255, .14); border-radius: 16px; }
  .rs-table th { color: var(--pf-muted); }
  .rs-table tbody tr.wz-tc { background: linear-gradient(90deg, color-mix(in srgb, var(--tc1) 16%, transparent), transparent 38%); }
  .rs-table tbody tr.wz-tc > td:nth-child(2) { box-shadow: inset 3px 0 0 color-mix(in srgb, var(--tc1) 85%, #fff); }
  .rs-table tbody tr.wz-tc:hover { background: linear-gradient(90deg, color-mix(in srgb, var(--tc1) 34%, transparent), color-mix(in srgb, var(--tc2) 18%, transparent) 50%, transparent 90%); }
  .pf-gc { display: inline-flex; align-items: center; gap: 0; white-space: nowrap; }
  .pf-gc .wz-pips { margin-right: 9px; }
  .pf-gc .pf-tm { font-weight: 600; }
  .rs-tile-num, .rs-card .wg-big { color: #F6F7F8; }
  .rs-page:not([hidden]) .rs-card { animation: wzUp .6s both; }
  .rs-page:not([hidden]) .rs-card:nth-of-type(2) { animation-delay: .06s; } .rs-page:not([hidden]) .rs-card:nth-of-type(3) { animation-delay: .12s; }
  .rs-card:hover { border-color: rgba(255, 255, 255, .2); }
  #charts .rs-card svg path[fill="none"] { filter: drop-shadow(0 0 6px rgba(0, 176, 78, .25)); }
  #charts .rs-card { background: linear-gradient(160deg, rgba(255, 255, 255, .07), rgba(255, 255, 255, .025)); }
  #charts .rs-card h2::before { content: ''; display: block; width: 36px; height: 3px; border-radius: 3px; background: #009A44; margin-bottom: 14px; }

  /* analyst picks by team */
  .pf-teams { display: grid; gap: 20px; }
  .pf-tgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 176px), 1fr)); gap: 12px; }
  .pf-tt { all: unset; box-sizing: border-box; cursor: pointer; position: relative; overflow: hidden; isolation: isolate; display: grid; gap: 4px; padding: 14px 16px 16px; border-radius: 18px; background: var(--pf-glass); border: 1px solid rgba(255, 255, 255, .12); color: #F6F7F8;
    transition: transform .35s cubic-bezier(.2, .7, .2, 1), border-color .3s, background .3s; }
  .pf-tt::before { content: ''; position: absolute; inset: 0; z-index: -1; opacity: .55; transition: opacity .35s; background: radial-gradient(120% 90% at 100% 0%, color-mix(in srgb, var(--tc1) 55%, transparent), transparent 62%), radial-gradient(80% 70% at 0% 100%, color-mix(in srgb, var(--tc2) 28%, transparent), transparent 70%); }
  .pf-tt:hover { transform: translateY(-4px); border-color: rgba(255, 255, 255, .3); }
  .pf-tt:hover::before, .pf-tt[aria-pressed="true"]::before { opacity: 1; }
  .pf-tt[aria-pressed="true"] { border-color: #F6F7F8; }
  .pf-tt:focus-visible { outline: 2px solid #F6F7F8; outline-offset: 2px; }
  .pf-tt .wz-helm { width: 92px; margin: -4px 0 2px auto; transition: transform .45s cubic-bezier(.2, .7, .2, 1); }
  .pf-tt:hover .wz-helm { transform: rotate(-6deg) translateX(-4px); }
  .pf-tt b { font-weight: 900; font-size: 26px; line-height: 1; }
  .pf-tt span { font-size: 13.5px; color: #D6D9DD; }
  .pf-tt small { font-family: var(--wx-mono); font-size: 11.5px; letter-spacing: .05em; text-transform: uppercase; color: var(--pf-muted); }
  .pf-tpanel { border-radius: 22px; padding: 22px; background: var(--pf-glass); border: 1px solid rgba(255, 255, 255, .14); -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); animation: wzUp .45s both; }
  .pf-tpanel-h { display: flex; align-items: center; gap: 16px; margin-bottom: 10px; }
  .pf-tpanel-h .wz-helm { width: 110px; }
  .pf-tpanel-h b { display: block; font-family: var(--pf-wide); font-stretch: 118%; font-weight: 900; font-size: 30px; text-transform: uppercase; }
  .pf-tpanel-h span { color: var(--pf-muted); font-size: 14px; }
  .pf-pick { display: grid; grid-template-columns: auto minmax(0, 1fr) auto auto; gap: 6px 14px; align-items: center; padding: 12px 6px; border-top: 1px solid rgba(255, 255, 255, .09); }
  .pf-pick .wz-av { width: 32px; height: 32px; font-size: 14px; }
  .pf-pick b { font-weight: 600; }
  .pf-pick small { display: block; color: var(--pf-muted); font-size: 12.5px; margin-top: 2px; }
  .pf-pick .pf-px { font-family: var(--wx-mono); font-size: 13px; color: var(--pf-muted); }
  .pf-allpicks > summary { cursor: pointer; list-style: none; display: inline-flex; align-items: center; gap: 10px; padding: 12px 20px; border-radius: 999px; border: 1px solid rgba(255, 255, 255, .3); font-weight: 600; margin-bottom: 14px; }
  .pf-allpicks > summary::-webkit-details-marker { display: none; }
  .pf-allpicks > summary:hover { background: rgba(255, 255, 255, .06); }
  @media (max-width: 640px) { .pf-pick { grid-template-columns: auto minmax(0, 1fr) auto; } .pf-pick .pf-px { display: none; } }

  /* dialog */
  .wz-dlg.wz-dlg { background: #1E2125; color: #F6F7F8; border: 1px solid rgba(255, 255, 255, .14); border-radius: 24px; }
  .wz-dlg .wz-dlg-top { background: var(--pf-metal-dark); }
  .wz-planpick button, .wz-field input, .wz-field select { background: rgba(255, 255, 255, .05); border-color: rgba(255, 255, 255, .18); color: #F6F7F8; }
  .wz-planpick button[aria-checked="true"] { border-color: #009A44; }
  .wz-msg { color: #F08A76; }

  @media (prefers-reduced-motion: reduce) {
    .pf-bg i, .pf-metal, .pf-blob, .pf-tier.t3 { animation: none !important; }
    .wx-read:hover .pf-roll > span { animation: none; }
    .pf-w, .wx-read-big, .pf-tt, .pf-tier { transition: none !important; }
  }
'''
CSS = CSS.replace('/_blob/@archivowide', '/_blob/' + FB['archivowide'])
assert s.count('</style>') == 1
s = s.replace('</style>', CSS + '</style>')

# ============================================================================ markup
rep('<div class="wg-paper">', '<div class="wg-paper">\n<div class="pf-bg" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i></div>')
# nav: Subscribe tab; header: a Join button
rep('    <button type="button" class="rs-tab" data-page="charts">Charts</button>\n',
    '    <button type="button" class="rs-tab" data-page="charts">Charts</button>\n    <button type="button" class="rs-tab pf-subtab" data-page="subscribe">Subscribe</button>\n')
rep('<button type="button" class="wz-btn wz-btn-g wz-btn-sm" id="wz-gopro" data-wz-join="monthly" hidden>Go Pro</button>',
    '<button type="button" class="wz-btn wz-btn-g wz-btn-sm" id="wz-gopro" data-wz-join="monthly" hidden>Go Pro</button>\n        <button type="button" class="wz-btn wz-btn-w wz-btn-sm pf-join" data-wz-join="monthly">Join ↗</button>')

PLANS = '''      <div class="pf-ladder">
        <article class="pf-tier t1 wz-spot">
          <div class="pf-top"><span class="pf-tk">01 / Free</span></div>
          <h3>Free</h3>
          <div class="pf-price pf-wide">$0</div>
          <p>See how Wedge works</p>
          <ul class="wz-feats"><li>The lobby and the track record</li><li>Analyst standings</li><li>Charts and research</li></ul>
          <button type="button" class="wz-btn wz-btn-line" data-wz-join="free">Start browsing</button>
        </article>
        <article class="pf-tier t2 wz-spot">
          <div class="pf-top"><span class="pf-tk">02 / Pro</span><span class="pf-flag">Most popular</span></div>
          <h3>Wedge Pro</h3>
          <div class="pf-price pf-wide">$19.99<span>/ month</span></div>
          <p>Cancel anytime</p>
          <ul class="wz-feats"><li>Every analyst pick as it's posted</li><li>Wedge-certified picks every week</li><li>The full NFL board with 2026 hit rates</li><li>The read behind every line</li><li>Anytime TD model and prop groups</li><li>NBA now, soccer at launch</li></ul>
          <button type="button" class="wz-btn wz-btn-k wz-btn-lg" data-wz-join="monthly">Join monthly ↗</button>
        </article>
        <article class="pf-tier t3 wz-spot">
          <div class="pf-top"><span class="pf-tk">03 / Season</span><span class="pf-flag">Best value</span></div>
          <h3>Wedge Pro Season</h3>
          <div class="pf-price pf-wide">$119.99<span>/ year</span></div>
          <p>About $10 a month, half the monthly price</p>
          <ul class="wz-feats"><li>Everything in Wedge Pro</li><li>Every NFL week and NBA night of the season</li><li>First access to new features</li></ul>
          <button type="button" class="wz-btn wz-btn-g wz-btn-lg" data-wz-join="season">Join for the season ↗</button>
        </article>
      </div>'''

i, j = cut('  <div class="rs-page wg-lobby wg-play" id="lobby">', '  <!-- ============ ALL LINES (original screen) ============ -->')
old = s[i:j]
dlg = old[old.index('    <dialog class="wz-dlg" id="wz-dlg"'):old.index('    </dialog>') + len('    </dialog>')]
ledger = old[old.index('        <div class="wx-ledger"'):old.index('</div>\n    </section>', old.index('        <div class="wx-ledger"')) + len('</div>')]
assert ledger.count('<div') == ledger.count('</div>'), 'ledger markup unbalanced'
LOBBY = f'''  <div class="rs-page wg-lobby wg-play" id="lobby">
    <section class="pf-hero" aria-labelledby="hero-title">
      <div class="pf-hero-bg" aria-hidden="true"><div class="pf-metal"></div><div class="pf-scrim"></div></div>
      <div class="pf-hero-copy">
        <div class="pf-chips"><span class="pf-chip"><i class="wx-dot" aria-hidden="true"></i><span id="wz-kick">NFL · Week 9</span></span></div>
        <h2 class="pf-h1" id="hero-title">Football,<br><em>understood.</em></h2>
        <p class="pf-lede">Analyst picks and certified reads on Robinhood's football markets. Every result stays on the record.</p>
        <div class="pf-row">
          <button type="button" class="wz-btn wz-btn-g wz-btn-lg" data-wz-join="monthly">Join Wedge Pro ↗</button>
          <button type="button" class="wz-btn wz-btn-line wz-btn-lg" data-wz-jump="wz-reads">This week's reads</button>
        </div>
        <p class="pf-fine">$19.99 a month or $119.99 a season · cancel anytime</p>
        <p class="wg-hero-desc wg-visually-hidden" id="wg-profit" data-source="results" aria-live="polite">Net profit on Wedge-certified picks so far: —</p>
      </div>
      <div class="pf-proof" data-source="results" aria-label="Track record">
        <div class="pf-blob" aria-hidden="true"></div><div class="pf-cross" aria-hidden="true"></div>
        <span class="pf-label">Certified hit rate · Week 9</span>
        <div class="pf-big" data-wz="cert-pct">—</div>
        <div class="pf-chips">
          <span class="pf-chip"><b data-wz="cert-wl">—</b> certified</span>
          <span class="pf-chip"><b data-wz="cert-profit">—</b> net</span>
          <span class="pf-chip g"><b data-wz="an-pct">—</b> analysts</span>
        </div>
        <span class="pf-cap"><span data-wz="cert-rec">Settled picks, before fees</span> · positions, not returns · misses stay posted</span>
        <button type="button" class="wz-btn wz-btn-w" data-wz-jump="wz-analysts">See the record ↗</button>
      </div>
    </section>

    <div class="wz-ticker" id="wz-ticker" data-source="lines lines_all" aria-hidden="true">
      <div class="wz-tape"><div class="wz-track" id="wz-tape-1"></div></div>
      <div class="wz-tape rev"><div class="wz-track" id="wz-tape-2"></div></div>
    </div>

    <section class="pf-sec wz-reveal" id="wz-analysts" aria-labelledby="an-h">
      <div class="pf-head">
        <div><span class="pf-label">01 / Track record</span><h2 class="pf-h2" id="an-h">The analysts.</h2></div>
        <p class="pf-sub">Every pick is tracked and settled against the box score, wins and losses alike. Members see each pick as it's posted.</p>
      </div>
      <div class="wz-board" id="wz-board" data-source="results"><p class="wx-empty">Loading the standings…</p></div>
      <div class="pf-row">
        <button type="button" class="wz-btn wz-btn-g" data-wz-join="monthly">Get every analyst pick ↗</button>
        <button type="button" class="wz-btn wz-btn-line" data-go="analysts">Picks by team</button>
        <button type="button" class="wz-link" data-go="apply">Apply to be an analyst</button>
      </div>
    </section>

    <section class="pf-sec wz-reveal" id="wz-reads" aria-labelledby="reads-h">
      <div class="pf-head">
        <div><span class="pf-label">02 / This week</span><h2 class="pf-h2" id="reads-h">The reads.</h2></div>
        <p class="pf-sub" id="wx-reads-sub">The biggest gaps between Wedge % and the price this week. Pick a game for its own reads.</p>
      </div>
      <div class="wx-tabs" role="tablist" id="wx-read-tabs" aria-label="Reads by game"><button type="button" class="wx-tab" role="tab" aria-selected="true" data-game="">All games</button></div>
      <div class="wz-matchup" id="wz-matchup" hidden></div>
      <div class="wx-reads" id="wg-hot-cards" role="tabpanel" aria-labelledby="reads-h"><p class="wx-empty">Loading this week's reads…</p></div>
      <div class="pf-row"><button type="button" class="wz-btn wz-btn-line" id="wx-reads-more" data-go="lines" data-wg-show="pick" data-wg-game="">All <span data-wg-count="picks">40</span> reads ↗</button><button type="button" class="wz-btn wz-btn-g" data-wz-join="monthly">Unlock every read ↗</button></div>
    </section>

    <section class="pf-sec wz-reveal" id="wz-plans" aria-labelledby="plans-h">
      <div class="pf-head">
        <div><span class="pf-label">03 / Membership</span><h2 class="pf-h2" id="plans-h">Join the inner circle.</h2></div>
        <p class="pf-sub">Every analyst pick and certified read, the full board, and the read behind every line.</p>
      </div>
{PLANS}
    </section>

    <section class="pf-sec wz-reveal" id="wz-schedule" aria-labelledby="sched-h">
      <div class="pf-head">
        <div><span class="pf-label">04 / Schedule</span><h2 class="pf-h2" id="sched-h">This week on Wedge.</h2></div>
        <p class="pf-sub">Reads open as Robinhood lists each game. Select a game for its reads.</p>
      </div>
      <div class="wz-sched">
        <div class="wz-days" id="wz-days" data-source="lines_all"><p class="wx-empty">Loading the schedule…</p></div>
        <aside class="wz-cover" aria-label="Coverage">
          <h3>Coverage</h3>
          <div><b>NFL</b><span>Every game, every week</span><em class="live">Live</em></div>
          <div><b>Analyst picks</b><span>NFL, tracked all season</span><em class="live">Live</em></div>
          <div><b>NBA</b><span>The nightly board</span><em>Beta</em></div>
          <div><b>Soccer</b><span>Premier League, Champions League, MLS</span><em>Coming soon</em></div>
          <button type="button" class="wz-btn wz-btn-line" data-wz-join="season">Lock in the season ↗</button>
        </aside>
      </div>
    </section>

    <section class="pf-sec wz-reveal" id="wz-method" aria-labelledby="how-h">
      <div class="pf-head">
        <div><span class="pf-label">05 / Method</span><h2 class="pf-h2" id="how-h">How a read works.</h2></div>
        <p class="pf-sub">Three steps, in order. The price comes last.</p>
      </div>
      <div class="wz-how">
        <ol class="wz-steps">
          <li><span class="n">01</span><b>Measure opportunity.</b><p>How often the line came true in his games this season, and how he is used.</p></li>
          <li><span class="n">02</span><b>Read the matchup.</b><p>The defense, the game script, the weather and the injury report, all in the full read.</p></li>
          <li><span class="n">03</span><b>Evaluate the price.</b><p>Wedge % against Robinhood's price. A read needs a 3-point edge.</p></li>
        </ol>
        <div class="wz-ex wz-spot" id="wz-example" data-source="lines"><p class="wx-empty">Loading a live example…</p></div>
      </div>
    </section>

    <section class="pf-quote wz-reveal" aria-labelledby="persp-h">
      <h2 class="wg-visually-hidden" id="persp-h">Perspective</h2>
      <blockquote>A good result deserves the same scrutiny as a bad one.</blockquote>
{ledger}
    </section>
    <p class="wx-fine">Wedge is football research, not financial advice. Prices move and reads lose; every figure is before fees. 21+ · Not available in all states · 1-800-GAMBLER</p>

{dlg}
    <svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
      <radialGradient id="wzHelmShade" cx="34%" cy="24%" r="82%"><stop offset="0" stop-color="#fff" stop-opacity=".62"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient>
    </defs></svg>
  </div>

  <!-- ============ SUBSCRIBE ============ -->
  <div class="rs-page pf-subpage" id="subscribe" hidden>
    <section class="pf-subhero" aria-labelledby="sub-h">
      <span class="pf-label">Membership</span>
      <h2 class="pf-h2" id="sub-h">Join the inner circle.</h2>
      <p class="pf-sub">Every analyst pick as it's posted, the certified reads, the full board and the read behind every line. Pick a plan; checkout is the next step.</p>
      <div class="pf-chips"><span class="pf-chip"><i class="wx-dot" aria-hidden="true"></i>Cancel anytime</span><span class="pf-chip"><b data-wz="cert-pct2">74.1%</b> certified hit rate</span><span class="pf-chip g">Season pass saves half</span></div>
    </section>
{PLANS}
    <section class="pf-perks" aria-label="What members get">
      <div class="pf-perk"><span class="n">01</span><b>Analyst picks</b><p>Every pick from Jason, Will, Chris and Sean as it's posted, with each analyst's record next to it.</p></div>
      <div class="pf-perk"><span class="n">02</span><b>Certified reads</b><p>The lines that clear their price, settled against the box score every week.</p></div>
      <div class="pf-perk"><span class="n">03</span><b>The full board</b><p>Every Week 9 line with its 2026 hit rate, team by team, and the read behind each one.</p></div>
      <div class="pf-perk"><span class="n">04</span><b>More sports</b><p>The NBA board now, soccer when it launches.</p></div>
    </section>
    <p class="wx-fine">Prices in US dollars. Wedge is research, not financial advice. 21+ · Not available in all states · 1-800-GAMBLER</p>
  </div>

'''
s = s[:i] + LOBBY + s[j:]

# analysts page: picks by team above the list; the long list folds away
rep('    <section class="rs-card" id="an-picks">',
    '''    <section class="pf-teams" id="pf-teams" aria-labelledby="pf-teams-h" data-source="results lines">
      <div class="pf-head"><div><span class="pf-label">Analyst picks</span><h2 class="pf-h2" id="pf-teams-h">Picks by team.</h2></div><p class="pf-sub">Every analyst pick, filed under the team it's on. Select a team for its picks.</p></div>
      <div class="pf-tgrid" id="pf-tgrid"><p class="wx-empty">Loading picks by team…</p></div>
      <div class="pf-tpanel" id="pf-tpanel" hidden></div>
    </section>
    <details class="pf-allpicks" id="pf-allpicks"><summary>Every pick, as a list</summary>
    <section class="rs-card" id="an-picks">''')
i = s.index('<section class="rs-card" id="an-picks">'); j = s.index('</section>', i) + len('</section>')
s = s[:j] + '\n    </details>' + s[j:]

# ============================================================================ JS hooks
rep("    const big = el('span', 'wx-read-big'); big.append(String(Math.round(pSide)), el('small', null, '%'));",
    "    const big = el('span', 'wx-read-big'); { const rl = el('span', 'pf-roll'); rl.append(el('span', null, String(Math.round(pSide)))); big.append(rl, el('small', null, '%')); }")
rep("    b.append(top, el('b', 'wx-read-title', label), mid, px, ...(hrow ? [hrow] : []), foot);",
    "    b.append(top, wzWords(label), mid, px, ...(hrow ? [hrow] : []), foot);")
rep("    foot.append(el('em', null, 'Read ↗'));", "    foot.append(el('em', null, 'Full read ↗'));")
rep("    wzSet('cert-rec', n ?", "    wzSet('cert-wl', n ? `${w}–${n - w}` : '—'); wzSet('cert-pct2', p == null ? '—' : (p % 1 ? p.toFixed(1) : String(p)) + '%');\n    wzSet('cert-rec', n ?")
rep("        b.append(wzPips(g), mid, st);", "        b.append(wzHelmPair(g), mid, st);")
rep("  const totalStar = (cell, r) => {\n    const t = num(r.game_total);", "  const totalStar = (cell, r) => {\n    wzGameCell(cell, r.game);\n    const t = num(r.game_total);")
rep("      td(r.game, 'rs-sub');\n", "      wzGameCell(td(r.game, 'rs-sub'), r.game);\n", count=3)
rep("      td(r.game);\n", "      wzGameCell(td(r.game), r.game);\n")
rep("    try { wzAnalysts(ranked); } catch (e) { /* the lobby board is optional */ }\n",
    "    try { wzAnalysts(ranked); } catch (e) { /* the lobby board is optional */ }\n    try { wzTeamPicks(); } catch (e) { console.error('team picks', e); }\n")
rep("      if (certUnavailable) { const wb = $('#wz-board'); if (wb) wb.replaceChildren(el('p', 'wx-empty', 'Analyst standings are unavailable in this view.')); }\n",
    "      if (certUnavailable) { const wb = $('#wz-board'); if (wb) wb.replaceChildren(el('p', 'wx-empty', 'Analyst standings are unavailable in this view.')); const tg = $('#pf-tgrid'); if (tg) tg.replaceChildren(el('p', 'wx-empty', 'Analyst picks are unavailable in this view.')); }\n")
rep("    if (!WZ_ACCOUNTS && plan === 'free') { const t = $('#wz-reads');", "    if (!WZ_ACCOUNTS && plan === 'free') { showPage('lobby'); const t = $('#wz-reads');")

# helmets: photo helmets (recolored from the reference) instead of drawn ones
i = s.index('  function wzHelmet(team, flip) {'); j = s.index('    return el2;\n  }\n', i) + len('    return el2;\n  }\n')
HELM = '  const WZ_HELM = ' + json.dumps({k: '/_blob/' + v for k, v in HB.items()}) + ''';
  function wzHelmet(team, flip) {
    const src = WZ_HELM[team];
    if (!src) { const sp = el('span', 'wz-helm wz-helm-none'); sp.setAttribute('aria-hidden', 'true'); return sp; }
    const im = document.createElement('img'); im.src = src; im.alt = ''; im.width = 320; im.height = 277; im.decoding = 'async';
    im.className = 'wz-helm' + (flip ? ' flip' : ''); im.setAttribute('aria-hidden', 'true'); return im;
  }
'''
s = s[:i] + HELM + s[j:]

JS = r'''
  // ================= Wedge round 3: words, game cells, helmet pairs, analyst picks by team =================
  function wzWords(label) {
    const b = el('b', 'wx-read-title');
    String(label).split(/(\s+)/).forEach((w, k) => { if (/^\s+$/.test(w)) b.append(w); else { const sp = el('span', 'pf-w', w); sp.style.setProperty('--i', String(k)); b.append(sp); } });
    return b;
  }
  function wzGameCell(cell, game) {
    const [a, h] = wzSides(game); if (!cell || !a || !WZ_TEAMS[a] || !WZ_TEAMS[h]) return cell;
    const w = el('span', 'pf-gc'); w.append(wzPips(game), el('span', 'pf-tm', a), ' @ ', el('span', 'pf-tm', h));
    cell.textContent = ''; cell.append(w); return cell;
  }
  function wzHelmPair(game) {
    const [a, h] = wzSides(game), p = el('span', 'pf-hp'); p.setAttribute('aria-hidden', 'true');
    p.append(wzHelmet(a, false), wzHelmet(h, true)); return p;
  }
  // a player's team by name alone (past weeks' games aren't in this week's data); only trusted when it's one of the game's two teams
  let wzNM = null, wzNMn = -1;
  function wzNameTeam(name) {
    const P = dash.data('proj'), Q = dash.data('props'), A = dash.data('atd');
    const n = [P, Q, A].reduce((x, d) => x + (d.status === 'ok' ? d.data.length : 0), 0);
    if (n !== wzNMn) { wzNMn = n; wzNM = new Map(); for (const d of [P, Q, A]) if (d.status === 'ok') for (const x of d.data) { const nm = x.player || String(x.contract || '').split(':')[0]; if (x.team && nm && !wzNM.has(nm)) wzNM.set(nm, x.team); } }
    return wzNM.get(String(name || '').trim()) || null;
  }
  let pfTeam = null;
  function wzPickTeam(v) {
    const [a, h] = wzSides(v.game); const con = String(v.contract || '');
    let t = wzPlayerTeam({ game: v.game, contract: con.split(':')[0] });
    if (!t && a) { const n = wzNameTeam(con.split(':')[0]); if (n === a || n === h) t = n; }
    if (!t && a) for (const x of [a, h]) { const nm = (WZ_TEAMS[x] || [])[0]; if ((nm && con.startsWith(nm)) || new RegExp('\\b' + x + '\\b').test(con)) { t = x; break; } }
    return t && WZ_TEAMS[t] ? t : 'ALL';
  }
  function wzTeamPicks() {
    const grid = $('#pf-tgrid'), panel = $('#pf-tpanel'); if (!grid) return;
    const idx = pickIndex(), by = new Map();
    for (const name of analysts.order) for (const k of (analysts.picks[name] || [])) {
      const v = Object.assign({ who: name }, pickInfo(idx, k)); const t = wzPickTeam(v);
      if (!by.has(t)) by.set(t, []); by.get(t).push(v);
    }
    if (document.querySelector('.rs-wrap.wg-owner')) { const d = $('#pf-allpicks'); if (d && !d.dataset.auto) { d.open = true; d.dataset.auto = '1'; } }
    if (!by.size) { grid.replaceChildren(el('p', 'wx-empty', 'No analyst picks yet.')); panel.hidden = true; return; }
    const rec = (L) => { const w = L.filter((x) => x.outcome === 'Won').length, l = L.filter((x) => x.outcome === 'Lost').length, pe = L.filter((x) => x.outcome === 'Pending').length; return { w, l, pe }; };
    const teams = [...by.keys()].sort((x, y) => (x === 'ALL') - (y === 'ALL') || by.get(y).length - by.get(x).length || (x < y ? -1 : 1));
    if (!pfTeam || !by.has(pfTeam)) pfTeam = teams[0];
    grid.replaceChildren(...teams.map((t) => {
      const L = by.get(t), r = rec(L), b = el('button', 'pf-tt'); b.type = 'button'; b.dataset.team = t; b.setAttribute('aria-pressed', t === pfTeam ? 'true' : 'false');
      if (t !== 'ALL') { b.style.setProperty('--tc1', WZ_TEAMS[t][1]); b.style.setProperty('--tc2', WZ_TEAMS[t][2]); } else { b.style.setProperty('--tc1', '#8A8F95'); b.style.setProperty('--tc2', '#E0E2E5'); }
      b.append(t === 'ALL' ? el('span', 'wz-helm wz-helm-none') : wzHelmet(t, false), el('b', null, t === 'ALL' ? 'More' : t), el('span', null, t === 'ALL' ? 'Totals and game lines' : WZ_TEAMS[t][0]),
        el('small', null, `${L.length} pick${L.length === 1 ? '' : 's'} · ${r.w}–${r.l}${r.pe ? ' · ' + r.pe + ' pending' : ''}`));
      b.setAttribute('aria-label', `${t === 'ALL' ? 'Totals and game lines' : WZ_TEAMS[t][0]}: ${L.length} picks, ${r.w} won, ${r.l} lost`);
      b.addEventListener('click', () => { pfTeam = t; grid.querySelectorAll('.pf-tt').forEach((x) => x.setAttribute('aria-pressed', x.dataset.team === t ? 'true' : 'false')); wzTeamPanel(t, by.get(t)); });
      return b;
    }));
    wzTeamPanel(pfTeam, by.get(pfTeam));
  }
  function wzTeamPanel(t, L) {
    const panel = $('#pf-tpanel'); if (!panel || !L) return;
    const head = el('div', 'pf-tpanel-h'); const txt = el('div');
    const w = L.filter((x) => x.outcome === 'Won').length, l = L.filter((x) => x.outcome === 'Lost').length;
    txt.append(el('b', null, t === 'ALL' ? 'Totals and game lines' : WZ_TEAMS[t][0] + ' · ' + t), el('span', null, `${L.length} analyst pick${L.length === 1 ? '' : 's'} · ${w}–${l} settled`));
    head.append(t === 'ALL' ? el('span') : wzHelmet(t, false), txt);
    const rows = L.slice().sort((x, y) => (Number(y.week) || 0) - (Number(x.week) || 0)).map((v) => {
      const r = el('div', 'pf-pick'); const av = el('span', 'wz-av', String(v.who).slice(0, 1).toUpperCase()); av.setAttribute('aria-hidden', 'true');
      const mid = el('div'); mid.append(el('b', null, v.contract ? (/:/.test(rhLabel(v.contract)) || !/Touchdown/i.test(v.market || '') ? rhLabel(v.contract) : rhLabel(v.contract) + ' · anytime TD') : '—'), el('small', null, `${v.who} · Week ${v.week || '—'} · ${v.game || ''}`));
      const px = el('span', 'pf-px', v.yes_price !== '' && v.yes_price != null ? v.yes_price + '¢' : '');
      const oc = v.outcome || 'Pending', pr = num(v.profit_c);
      const chip = el('span', 'wz-chip ' + (oc === 'Won' ? 'pos' : oc === 'Lost' ? 'neg' : 'flat'), oc === 'Won' || oc === 'Lost' ? `${oc}${pr != null ? ' ' + (pr > 0 ? '+' : pr < 0 ? '−' : '') + Math.abs(pr) + '¢' : ''}` : oc);
      r.append(av, mid, px, chip); return r;
    });
    panel.replaceChildren(head, ...rows); panel.hidden = false;
    panel.style.animation = 'none'; void panel.offsetWidth; panel.style.animation = '';
  }
'''
rep('\n  // ---------------- render ----------------\n  dash.onData(() => {', JS + '\n  // ---------------- render ----------------\n  dash.onData(() => {')

open(B + 'index.html', 'w').write(s)
print('w9f ok', len(s))
