"""Wed Nov 4 night: Wedge UI round 2 (Sean's notes).
- Brand type served from the artifact (Archivo for display and nav, matching the wordmark; Geist / Geist Mono for text),
  bigger text everywhere, one green (Deep Green #104D30), metal-first surfaces (65 / 27 / 8).
- Header: clickable wordmark back to the lobby, large nav, record chip, Log in / Sign up.
- New lobby: hero with the track record up front, scrolling board ticker, analyst standings, reads by game with team-color
  matchups, membership plans with one-step checkout, this week's schedule and coverage, how a read works, the closing line.
- Accounts: a Wedge profile per viewer (private to them), plan choice and checkout (payment links when set, else an email request).
- Lines and other tables: simple columns by default (More columns to expand), extra filters folded into a popover.
- Motion: reveal on scroll, button sheen and press, click ripple, cursor spotlight, count-up numbers, ticker; all off for reduced motion.
Runs on the final index.html after patch_w9c.py."""
import json
B = '/home/claude/wedger/rh/'
s = open(B + 'index.html').read()
WM = json.load(open('/home/claude/wedger/brand/wordmark_blobs.json'))
FB = json.load(open('/home/claude/wedger/brand/font_blobs.json'))

def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, (old[:100], c); s = s.replace(old, new)

def cut(start, end_marker):
    """Return (i, j) of s[start: end_marker) where end_marker is excluded."""
    i = s.index(start); j = s.index(end_marker, i); return i, j

# ============================================================================ CSS
CSS = r'''
  /* ===================== Wedge UI round 2 ===================== */
  @font-face { font-family: "Archivo"; src: url("/_blob/@archivo") format("woff2"); font-weight: 100 900; font-style: normal; font-display: swap; }
  @font-face { font-family: "Geist"; src: url("/_blob/@geist400") format("woff2"); font-weight: 400; font-style: normal; font-display: swap; }
  @font-face { font-family: "Geist"; src: url("/_blob/@geist500") format("woff2"); font-weight: 500; font-style: normal; font-display: swap; }
  @font-face { font-family: "Geist"; src: url("/_blob/@geist600") format("woff2"); font-weight: 600; font-style: normal; font-display: swap; }
  @font-face { font-family: "Geist"; src: url("/_blob/@geist700") format("woff2"); font-weight: 700 900; font-style: normal; font-display: swap; }
  @font-face { font-family: "Geist Mono"; src: url("/_blob/@mono400") format("woff2"); font-weight: 400; font-style: normal; font-display: swap; }
  @font-face { font-family: "Geist Mono"; src: url("/_blob/@mono500") format("woff2"); font-weight: 500 700; font-style: normal; font-display: swap; }
  .wg-paper {
    --wz-display: "Archivo", "Helvetica Neue", Arial, sans-serif;
    --wz-g: #104D30; --wz-g-hi: #0C3D26; --wz-on-g: #EEF3EF;
    --wz-metal: repeating-linear-gradient(90deg, rgba(255,255,255,.16) 0 1px, rgba(0,0,0,.035) 1px 2px, transparent 2px 4px), linear-gradient(135deg, #F4F5F7 0%, #CDD1D6 38%, #E9EBEE 58%, #B6BBC1 100%);
    --wz-black: linear-gradient(165deg, #191C20 0%, #0D0F12 70%);
    --wz-pos-bg: #104D30; --wz-pos-fg: #EEF3EF; --wz-neg-bg: #5A2A22; --wz-neg-fg: #F6E7E3;
    --wz-spot: rgba(255, 255, 255, .55);
    --wx-silver: #D9DCE0; --wg-c1: #104D30;
    background: var(--wz-metal);
  }
  .wz-top [hidden], .wz-dlg [hidden], .wg-lobby [hidden] { display: none !important; }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) .wg-paper { --wx-green-ink: #C9CED4; --wg-ink: #E6E8EB; --color-ok: #3A8F63; --wz-spot: rgba(255, 255, 255, .10); background: #111316; }
  }
  :root[data-theme="dark"] .wg-paper { --wx-green-ink: #C9CED4; --wg-ink: #E6E8EB; --color-ok: #3A8F63; --wz-spot: rgba(255, 255, 255, .10); background: #111316; }

  /* readable sizes */
  .wg-paper .rs-wrap { font-size: 15.5px; }
  .wx-mono, .wx-label { font-size: 12px; }
  .rs-note { font-size: 15px; line-height: 1.6; max-width: 62rem; }
  .rs-card h2 { font-family: var(--wz-display); font-weight: 800; font-size: 24px; letter-spacing: -0.03em; }
  .rs-table { font-size: 14.5px; }
  .rs-table th { font-size: 12px; }
  .rs-table td { padding-top: 11px; padding-bottom: 11px; }
  .rs-table td.rs-barcell { font-weight: 700; font-size: 15.5px; font-variant-numeric: tabular-nums; }
  .rs-table td.rs-barcell .rs-bar { height: 6px; }
  .rs-controls { gap: 10px; }
  .rs-controls select, .rs-controls input[type="search"] { font-size: 15px; min-height: 42px; border-radius: 6px; }
  .rs-controls label { font-size: 14.5px; }
  .rs-count { font-size: 14px; }
  .rs-tile-label { font-size: 12px; }
  .rs-tile-num { font-family: var(--wz-display); font-weight: 900; }
  .wx-read-top { font-size: 12px; }
  .wx-band p { font-size: 12px; }
  .wx-band h2, .wx-h2, .wx-h1 { font-family: var(--wz-display); font-weight: 900; }
  .wg-dd-item { font-size: 15.5px; padding-top: 10px; padding-bottom: 10px; }
  .wg-dd-label { font-size: 11.5px; }
  .wx-band::before { background: var(--wz-g); }

  /* buttons, links, motion primitives */
  .wz-btn { all: unset; box-sizing: border-box; cursor: pointer; position: relative; overflow: hidden; isolation: isolate; display: inline-block; vertical-align: middle;
    padding: 12px 20px; border-radius: 999px; border: 1px solid transparent; font-family: var(--wz-display); font-weight: 700; font-size: 15px; letter-spacing: -0.01em; line-height: 1.1; text-align: center;
    transition: transform .18s cubic-bezier(.2, .7, .2, 1), box-shadow .2s ease, background-color .2s ease, color .2s ease, border-color .2s ease; -webkit-tap-highlight-color: transparent; }
  .wz-btn::before { content: ''; position: absolute; z-index: -1; top: 0; bottom: 0; left: -70%; width: 45%; background: linear-gradient(100deg, transparent, rgba(255, 255, 255, .38), transparent); transform: skewX(-20deg); transition: left .7s ease; pointer-events: none; }
  .wz-btn:hover::before { left: 130%; }
  .wz-btn:hover { transform: translateY(-2px); }
  .wz-btn:active { transform: translateY(0) scale(.97); }
  .wz-btn:focus-visible { outline: 2px solid var(--wz-g); outline-offset: 3px; }
  .wz-btn-lg { padding: 16px 26px; font-size: 17px; }
  .wz-btn-g { background: var(--wz-g); color: var(--wz-on-g); border-color: rgba(255, 255, 255, .14); box-shadow: 0 12px 26px -16px rgba(16, 77, 48, .95); }
  .wz-btn-g:hover { background: var(--wz-g-hi); box-shadow: 0 18px 32px -16px rgba(16, 77, 48, .95); }
  .wz-btn-line { color: inherit; border-color: currentColor; background: transparent; }
  .wz-btn-line:hover { background: color-mix(in srgb, currentColor 8%, transparent); }
  .wz-btn-ghost { color: #E6E8EB; border-color: rgba(255, 255, 255, .24); background: rgba(255, 255, 255, .02); }
  .wz-btn-ghost:hover { background: rgba(255, 255, 255, .09); border-color: rgba(255, 255, 255, .4); }
  .wz-btn-sm { padding: 9px 15px; font-size: 14px; }
  .wz-link { all: unset; cursor: pointer; font-weight: 600; text-decoration: underline; text-underline-offset: 3px; text-decoration-thickness: 1px; transition: opacity .2s; }
  .wz-link:hover { opacity: .72; }
  .wz-link:focus-visible { outline: 2px solid var(--wz-g); outline-offset: 2px; }
  .wz-ripple { position: absolute; z-index: 0; border-radius: 50%; pointer-events: none; background: currentColor; opacity: .22; transform: scale(0); animation: wzRipple .65s ease-out forwards; }
  @keyframes wzRipple { to { transform: scale(1); opacity: 0; } }
  .wz-spot { position: relative; isolation: isolate; }
  .wz-spot::after { content: ''; position: absolute; inset: 0; z-index: 0; pointer-events: none; opacity: 0; transition: opacity .35s ease;
    background: radial-gradient(280px circle at var(--mx, 50%) var(--my, 50%), var(--wz-spot), transparent 65%); }
  .wz-spot:hover::after { opacity: 1; }
  .wz-spot > * { position: relative; z-index: 1; }
  .wz-js .wz-reveal:not(.wz-in) { opacity: 0; transform: translateY(22px); }
  .wz-reveal { transition: opacity .8s ease, transform .8s cubic-bezier(.2, .7, .2, 1); }
  @keyframes wzUp { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
  @keyframes wzSheen { 0%, 100% { background-position: 0 0, 0% 50%; } 50% { background-position: 0 0, 100% 50%; } }
  .wz-chip { display: inline-block; padding: 3px 8px; border-radius: 3px; font-family: var(--wx-mono); font-size: 12px; font-weight: 500; letter-spacing: .03em; font-variant-numeric: tabular-nums; }
  .wz-chip.pos { background: var(--wz-pos-bg); color: var(--wz-pos-fg); }
  .wz-chip.neg { background: var(--wz-neg-bg); color: var(--wz-neg-fg); }
  .wz-chip.flat { background: color-mix(in srgb, currentColor 12%, transparent); }
  .wz-cap { font-family: var(--wx-mono); font-size: 12px; letter-spacing: .07em; text-transform: uppercase; }

  /* header: black bar, wordmark home, big tabs */
  .rs-wrap > .wz-top { margin: 0; }
  .wz-top { position: relative; z-index: 30; background: var(--wz-black); color: #E6E8EB; border: 0; border-radius: 6px; padding: 16px clamp(16px, 3vw, 28px) 0; box-shadow: 0 20px 40px -32px rgba(0, 0, 0, .8); }
  .wz-bar { display: flex; align-items: center; gap: 14px 20px; flex-wrap: wrap; padding-bottom: 14px; border-bottom: 1px solid #262A2F; }
  .wz-logo { all: unset; cursor: pointer; display: block; border-radius: 6px; padding: 4px 6px 4px 0; transition: transform .25s cubic-bezier(.2, .7, .2, 1), opacity .2s; }
  .wz-logo img { display: block; height: 40px; width: auto; }
  .wz-logo:hover { transform: translateY(-1px); opacity: .9; }
  .wz-logo:active { transform: scale(.96); }
  .wz-logo:focus-visible { outline: 2px solid #D9DCE0; outline-offset: 4px; }
  .wz-bar-r { margin-left: auto; display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  .wz-top .wg-record { display: flex; flex-direction: column; gap: 2px; border: 0; padding: 4px 14px 4px 0; margin-right: 6px; border-right: 1px solid #262A2F; border-radius: 0; background: none; color: #E6E8EB; }
  .wz-top .wg-record-label { font-family: var(--wx-mono); font-size: 11px; letter-spacing: .07em; text-transform: uppercase; color: #A3A9B0; display: flex; align-items: center; gap: 7px; }
  .wz-top .wg-record-label i { width: 7px; height: 7px; border-radius: 50%; background: #2F8A5B; box-shadow: 0 0 0 3px rgba(47, 138, 91, .22); animation: wzPulse 2.4s ease-in-out infinite; }
  @keyframes wzPulse { 50% { box-shadow: 0 0 0 6px rgba(47, 138, 91, 0); } }
  .wz-top .wg-record-main { display: flex; align-items: baseline; gap: 8px; }
  .wz-top .wg-record-pct, .wz-top .wg-record.wg-up .wg-record-pct { font-family: var(--wz-display); font-weight: 900; font-size: 26px; letter-spacing: -0.04em; color: #F3F4F6; }
  .wz-top .wg-record-frac, .wz-top .wg-record.wg-up .wg-record-frac { font-family: var(--wx-mono); font-size: 12px; color: #A3A9B0; }
  .wz-top .wg-record-sub { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
  .wz-me { all: unset; cursor: pointer; display: inline-flex; align-items: center; gap: 9px; padding: 5px 12px 5px 5px; border-radius: 999px; border: 1px solid rgba(255, 255, 255, .2); color: #E6E8EB; font-weight: 600; font-size: 14.5px; transition: background .2s, transform .18s; }
  .wz-me:hover { background: rgba(255, 255, 255, .08); transform: translateY(-1px); }
  .wz-me:focus-visible { outline: 2px solid #D9DCE0; outline-offset: 3px; }
  .wz-av { flex: none; display: grid; place-items: center; width: 30px; height: 30px; border-radius: 50%; font-family: var(--wz-display); font-weight: 800; font-size: 14px; color: #16181B; background: linear-gradient(145deg, #F7F8F9, #A4AAB1); box-shadow: inset 0 1px 0 #fff, 0 2px 6px rgba(0, 0, 0, .3); }
  .wz-me em { font-style: normal; font-family: var(--wx-mono); font-size: 11px; letter-spacing: .06em; text-transform: uppercase; padding: 3px 7px; border-radius: 3px; background: rgba(255, 255, 255, .1); color: #C9CED4; }
  .wz-me em.pro { background: var(--wz-g); color: var(--wz-on-g); }
  .wz-top .wg-certnote { margin: 10px 0 0; }
  .wz-top .rs-tabs { display: flex; align-items: stretch; flex-wrap: nowrap; gap: 2px; overflow-x: auto; overflow-y: visible; scrollbar-width: none; border: 0; padding: 0; margin: 0 -6px; background: none; position: static; }
  .wz-top .rs-tabs::-webkit-scrollbar { display: none; }
  .wz-top .rs-tab { position: relative; flex: none; font-family: var(--wz-display); font-size: 17px; font-weight: 700; letter-spacing: -0.015em; text-transform: none; color: #A3A9B0; padding: 15px 14px 17px; border-radius: 0; background: none; white-space: nowrap; transition: color .2s ease; }
  .wz-top .rs-tab::after { content: ''; position: absolute; left: 14px; right: 14px; bottom: 0; height: 3px; border-radius: 3px 3px 0 0; background: linear-gradient(90deg, #F4F5F7, #9DA3AA); transform: scaleX(0); transform-origin: left; transition: transform .35s cubic-bezier(.2, .7, .2, 1); }
  .wz-top .rs-tab:hover { color: #F3F4F6; background: none; }
  .wz-top .rs-tab:hover::after { transform: scaleX(.35); }
  .wz-top .rs-tab[aria-current=page] { color: #FFFFFF; background: none; box-shadow: none; }
  .wz-top .rs-tab[aria-current=page]::after { transform: scaleX(1); }
  .wz-top .rs-tab:focus-visible { outline: 2px solid #D9DCE0; outline-offset: -4px; }
  .wz-top .wg-dd-cur { font-weight: 600; color: #C9CED4; }
  .wz-top .wg-caret { width: 11px; height: 7px; margin-left: 6px; }
  .wz-top .wg-tabsep { align-self: center; width: 1px; height: 22px; background: #2F343A; margin: 0 8px; flex: none; }
  .wz-top .wg-dd { position: static; }
  .wz-top .wg-dd-menu { z-index: 60; top: calc(100% + 6px); }
  .wz-top .wg-dd-item { font-family: var(--wx-sans); font-size: 16px; letter-spacing: 0; font-weight: 500; border-radius: 4px; transition: background .15s, padding-left .2s; }
  .wz-top .wg-dd-item:hover { padding-left: 16px; }
  @media (max-width: 720px) {
    .wz-top .wg-record { display: none; }
    .wz-logo img { height: 32px; }
    .wz-top .rs-tab { font-size: 16px; padding: 13px 11px 15px; }
    .wz-bar-r .wz-btn { padding: 9px 14px; font-size: 14px; }
  }

  /* lobby */
  .wg-lobby { gap: 0; }
  .wz-hero { position: relative; isolation: isolate; overflow: hidden; display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(0, .8fr); gap: clamp(24px, 4vw, 56px); align-items: stretch;
    margin-top: 18px; padding: clamp(26px, 5vw, 64px); border-radius: 6px; color: #121417; background: var(--wz-metal); background-size: auto, 220% 220%; animation: wzSheen 16s ease-in-out infinite; border: 1px solid #F5F6F7; box-shadow: 0 40px 70px -50px rgba(0, 0, 0, .7); }
  .wz-hero::after { content: ''; position: absolute; inset: 0; z-index: -1; opacity: .12; background-image: var(--wx-grain); mix-blend-mode: multiply; pointer-events: none; }
  .wz-hero-copy { display: flex; flex-direction: column; justify-content: center; gap: 22px; min-width: 0; }
  .wz-kick { display: flex; align-items: center; gap: 10px; font-family: var(--wx-mono); font-size: 12.5px; letter-spacing: .07em; text-transform: uppercase; color: #2A2D31; }
  .wz-kick .wx-dot { background: var(--wz-g); }
  .wz-h1 { margin: 0; font-family: var(--wz-display); font-weight: 900; font-size: clamp(42px, 11.5vw, 128px); line-height: .84; letter-spacing: -0.055em; color: #121417; }
  .wz-h1 em { font-style: normal; color: #104D30; }
  .wz-lede { margin: 0; max-width: 31rem; font-size: 18.5px; line-height: 1.55; color: #33383E; }
  .wz-cta { display: flex; flex-wrap: wrap; gap: 12px; }
  .wz-hero .wz-btn-line { color: #16181B; }
  .wz-micro { margin: 0; font-family: var(--wx-mono); font-size: 12.5px; letter-spacing: .04em; color: #454B51; }
  .wz-proof { position: relative; isolation: isolate; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; gap: 18px; min-width: 0; padding: clamp(22px, 3vw, 34px); border-radius: 6px; color: #E6E8EB; background: var(--wz-black); box-shadow: 0 34px 60px -34px rgba(0, 0, 0, .75), inset 0 1px 0 rgba(255, 255, 255, .06); }
  .wz-proof .wz-cap { color: #A3A9B0; }
  .wz-big { font-family: var(--wz-display); font-weight: 900; font-size: clamp(84px, 10vw, 148px); line-height: .8; letter-spacing: -0.065em; font-variant-numeric: tabular-nums;
    background: linear-gradient(180deg, #FFFFFF 10%, #C4C9CF 60%, #8E959C 100%); -webkit-background-clip: text; background-clip: text; color: transparent; padding-bottom: .06em; }
  .wz-big small { font-size: .42em; letter-spacing: -0.03em; margin-left: .04em; }
  .wz-proof-lead { display: grid; gap: 12px; }
  .wz-cap2 { font-size: 15px; line-height: 1.5; color: #C9CED4; }
  .wz-proof-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0 16px; border-top: 1px solid #2A2E33; }
  .wz-proof-row > div { padding-top: 16px; display: grid; gap: 8px; min-width: 0; }
  .wz-proof-row b { font-family: var(--wz-display); font-weight: 800; font-size: clamp(26px, 2.6vw, 34px); letter-spacing: -0.04em; color: #F3F4F6; font-variant-numeric: tabular-nums; }
  .wz-proof-row small { font-size: 13px; color: #A3A9B0; }
  .wz-proof .wz-btn { align-self: flex-start; }
  @media (max-width: 920px) { .wz-hero { grid-template-columns: 1fr; } }

  .wz-ticker { margin-top: 14px; border-radius: 6px; overflow: hidden; background: #0D0F12; color: #C9CED4; -webkit-mask-image: linear-gradient(90deg, transparent, #000 5%, #000 95%, transparent); mask-image: linear-gradient(90deg, transparent, #000 5%, #000 95%, transparent); }
  .wz-tape { overflow: hidden; }
  .wz-tape + .wz-tape { border-top: 1px solid #1E2226; }
  .wz-track { display: flex; width: max-content; animation: wzTape var(--dur, 90s) linear infinite; }
  .wz-tape.rev .wz-track { animation-direction: reverse; }
  .wz-ticker:hover .wz-track { animation-play-state: paused; }
  @keyframes wzTape { from { transform: translateX(0); } to { transform: translateX(-50%); } }
  .wz-tk { all: unset; cursor: pointer; display: inline-flex; align-items: center; gap: 10px; padding: 12px 22px; border-right: 1px solid #1E2226; white-space: nowrap; font-family: var(--wx-mono); font-size: 13px; letter-spacing: .03em; text-transform: uppercase; transition: background .2s, color .2s; }
  .wz-tk:hover { background: #171A1E; color: #fff; }
  .wz-tk b { font-weight: 500; color: #F3F4F6; }
  .wz-tk i { font-style: normal; color: #8A9098; }
  .wz-tk em { font-style: normal; padding: 2px 7px; border-radius: 3px; background: var(--wz-g); color: var(--wz-on-g); }
  .wz-tk .wz-pips { gap: 2px; }
  .wz-tk .wz-pips i { width: 5px; height: 14px; }

  .wz-sec { display: flex; flex-direction: column; gap: 26px; padding: clamp(44px, 6vw, 80px) 0; border-bottom: 1px solid var(--wx-rule); min-width: 0; }
  .wz-head { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-end; gap: 14px 44px; }
  .wz-label { font-family: var(--wx-mono); font-size: 12.5px; letter-spacing: .08em; text-transform: uppercase; color: var(--wx-ink); }
  .wz-h2 { margin: 12px 0 0; font-family: var(--wz-display); font-weight: 900; font-size: clamp(38px, 5vw, 64px); line-height: .92; letter-spacing: -0.05em; color: var(--wx-ink); }
  .wz-sub { margin: 0; max-width: 29rem; font-size: 16.5px; line-height: 1.6; color: var(--wx-muted); }
  .wz-row-cta { display: flex; flex-wrap: wrap; align-items: center; gap: 12px 18px; }

  /* analysts */
  .wz-board { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 240px), 1fr)); gap: 14px; }
  .wz-an { display: flex; flex-direction: column; gap: 16px; min-width: 0; padding: 22px; border-radius: 6px; background: var(--color-panel); border: 1px solid var(--color-border-line); color: var(--wx-ink);
    transition: transform .3s cubic-bezier(.2, .7, .2, 1), box-shadow .3s ease; animation: wzUp .6s both; }
  .wz-an:nth-child(2) { animation-delay: .07s; } .wz-an:nth-child(3) { animation-delay: .14s; } .wz-an:nth-child(4) { animation-delay: .21s; }
  .wz-an:hover { transform: translateY(-5px); box-shadow: 0 28px 44px -30px rgba(0, 0, 0, .55); }
  .wz-an.lead { background: var(--wz-metal); color: #16181B; border-color: #F5F6F7; --wz-spot: rgba(255, 255, 255, .6); }
  .wz-an-top { display: flex; align-items: center; gap: 12px; }
  .wz-an-top .wz-av { width: 42px; height: 42px; font-size: 19px; }
  .wz-an-name { font-family: var(--wz-display); font-weight: 800; font-size: 21px; letter-spacing: -0.02em; }
  .wz-an-rank { margin-left: auto; font-family: var(--wx-mono); font-size: 12px; letter-spacing: .06em; opacity: .75; }
  .wz-an-pct { font-family: var(--wz-display); font-weight: 900; font-size: 62px; line-height: .86; letter-spacing: -0.055em; font-variant-numeric: tabular-nums; }
  .wz-an-pct small { font-size: .42em; margin-left: 2px; }
  @media (max-width: 640px) { .wz-board { grid-template-columns: 1fr 1fr; gap: 10px; } .wz-an { padding: 16px; gap: 10px; } .wz-an-pct { font-size: 40px; } .wz-an-meta { font-size: 12.5px; } .wz-an-top { gap: 8px; } .wz-an-top .wz-av { width: 30px; height: 30px; font-size: 14px; } .wz-an-name { font-size: 16px; } .wz-dots i { width: 9px; height: 9px; } }
  .wz-an-meta { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px; font-size: 14px; }
  .wz-an-meta span { opacity: .8; }
  .wz-dots { display: flex; gap: 6px; align-items: center; }
  .wz-dots i { width: 11px; height: 11px; border-radius: 50%; border: 1.5px solid currentColor; opacity: .45; }
  .wz-dots i.w { background: #104D30; border-color: #104D30; opacity: 1; box-shadow: 0 0 0 1px rgba(255, 255, 255, .28); }
  .wz-dots small { font-family: var(--wx-mono); font-size: 11px; letter-spacing: .06em; text-transform: uppercase; opacity: .7; margin-left: 4px; }

  /* reads: game tabs with team colors, matchup banner, cards */
  .wz-pips { display: inline-flex; gap: 3px; margin-right: 8px; vertical-align: -2px; }
  .wz-pips i { display: block; width: 6px; height: 15px; border-radius: 1px; transform: skewX(-14deg); }
  .wx-tab { font-size: 13px; padding: 12px 14px 13px; }
  .wz-matchup { position: relative; isolation: isolate; overflow: hidden; display: grid; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); align-items: center; gap: 12px; padding: 18px clamp(16px, 3vw, 34px); border-radius: 6px; color: #F5F6F7;
    background: linear-gradient(100deg, color-mix(in srgb, var(--ca) 82%, #0D0F12) 0 49.7%, #0D0F12 49.7% 50.3%, color-mix(in srgb, var(--cb) 82%, #0D0F12) 50.3% 100%); }
  .wz-matchup::after { content: ''; position: absolute; inset: 0; z-index: -1; pointer-events: none; background: linear-gradient(180deg, rgba(255, 255, 255, .1), transparent 45%, rgba(0, 0, 0, .25)); }
  .wz-matchup[hidden] { display: none; }
  .wz-mt-side { display: flex; align-items: center; gap: 16px; min-width: 0; }
  .wz-mt-side.home { justify-content: flex-end; text-align: right; }
  .wz-mt-side b { display: block; font-family: var(--wz-display); font-weight: 900; font-size: clamp(30px, 4.2vw, 48px); line-height: .9; letter-spacing: -0.045em; }
  .wz-mt-side span { display: block; margin-top: 4px; font-size: 14px; opacity: .85; }
  .wz-helm { flex: none; width: clamp(78px, 11vw, 132px); height: auto; filter: drop-shadow(0 12px 14px rgba(0, 0, 0, .45)); transition: transform .6s cubic-bezier(.2, .7, .2, 1); }
  .wz-matchup:hover .wz-mt-side:not(.home) .wz-helm { transform: translateX(6px) rotate(-3deg); }
  .wz-matchup:hover .wz-mt-side.home .wz-helm { transform: translateX(-6px) rotate(3deg); }
  .wz-matchup.enter .wz-mt-side:not(.home) .wz-helm { animation: wzInL .7s cubic-bezier(.2, .7, .2, 1) both; }
  .wz-matchup.enter .wz-mt-side.home .wz-helm { animation: wzInR .7s cubic-bezier(.2, .7, .2, 1) both; }
  @keyframes wzInL { from { opacity: 0; transform: translateX(-40px); } to { opacity: 1; transform: none; } }
  @keyframes wzInR { from { opacity: 0; transform: translateX(40px); } to { opacity: 1; transform: none; } }
  .wz-mt-mid { display: grid; justify-items: center; gap: 6px; text-align: center; }
  .wz-mt-at { font-family: var(--wz-display); font-weight: 900; font-size: 30px; opacity: .75; line-height: 1; }
  .wz-mt-mid .wz-cap { color: #E6E8EB; opacity: .9; }
  @media (max-width: 640px) { .wz-matchup { grid-template-columns: 1fr 1fr; } .wz-mt-mid { grid-column: 1 / -1; grid-row: 2; } .wz-mt-side { flex-direction: column; align-items: flex-start; gap: 8px; } .wz-mt-side.home { align-items: flex-end; } }
  .wx-reads { gap: 12px; background: none; border: 0; border-radius: 0; overflow: visible; }
  .wx-read { border: 1px solid var(--color-border-line); border-radius: 6px; }
  .wx-reads .wx-empty { border-radius: 6px; }
  .wx-read { gap: 14px; padding: 22px; }
  .wx-reads .wx-read { animation: wzUp .5s both; }
  .wx-reads .wx-read:nth-child(2) { animation-delay: .05s; } .wx-reads .wx-read:nth-child(3) { animation-delay: .1s; } .wx-reads .wx-read:nth-child(4) { animation-delay: .15s; } .wx-reads .wx-read:nth-child(5) { animation-delay: .2s; } .wx-reads .wx-read:nth-child(6) { animation-delay: .25s; }
  .wx-read:hover { background: var(--color-panel); }
  .wx-read-title { font-family: var(--wz-display); font-weight: 800; font-size: 19px; }
  .wx-read-big { font-family: var(--wz-display); font-weight: 900; font-size: 62px; }
  .wx-read-px span { font-size: 13px; }
  .wx-read-foot { font-size: 14px; }
  .wx-read-foot em { font-size: 12px; color: var(--wx-ink); }
  .wz-hr { display: flex; align-items: baseline; gap: 8px; font-size: 14px; color: var(--wx-muted); }
  .wz-hr b { font-family: var(--wz-display); font-weight: 800; font-size: 20px; letter-spacing: -0.03em; color: var(--wx-ink); }

  /* membership */
  .wz-plans { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 270px), 1fr)); gap: 16px; align-items: stretch; }
  .wz-plan { display: flex; flex-direction: column; gap: 18px; min-width: 0; padding: 30px 28px; border-radius: 6px; background: var(--color-panel); border: 1px solid var(--color-border-line); color: var(--wx-ink);
    transition: transform .3s cubic-bezier(.2, .7, .2, 1), box-shadow .3s ease; }
  .wz-plan:hover { transform: translateY(-6px); box-shadow: 0 34px 50px -34px rgba(0, 0, 0, .6); }
  .wz-plan.hot { background: var(--wz-metal); color: #16181B; border-color: #F5F6F7; box-shadow: 0 30px 60px -40px rgba(0, 0, 0, .7); --wz-spot: rgba(255, 255, 255, .65); }
  .wz-plan.dark { background: var(--wz-black); color: #E6E8EB; border-color: #22262B; --wz-spot: rgba(255, 255, 255, .1); }
  .wz-plan-top { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
  .wz-plan h3 { margin: 0; font-family: var(--wz-display); font-weight: 800; font-size: 22px; letter-spacing: -0.02em; }
  .wz-badge { font-family: var(--wx-mono); font-size: 11px; letter-spacing: .07em; text-transform: uppercase; padding: 5px 9px; border-radius: 3px; background: var(--wz-g); color: var(--wz-on-g); }
  .wz-plan.dark .wz-badge { background: #F3F4F6; color: #16181B; }
  .wz-price { display: flex; align-items: baseline; gap: 6px; font-family: var(--wz-display); font-weight: 900; font-size: 56px; line-height: .9; letter-spacing: -0.055em; font-variant-numeric: tabular-nums; }
  .wz-price span { font-family: var(--wx-sans); font-weight: 500; font-size: 16px; letter-spacing: 0; opacity: .75; }
  .wz-plan-note { margin: -8px 0 0; font-size: 14.5px; opacity: .8; }
  .wz-feats { list-style: none; margin: 0; padding: 18px 0 0; display: grid; gap: 11px; border-top: 1px solid color-mix(in srgb, currentColor 18%, transparent); font-size: 15px; line-height: 1.4; }
  .wz-feats li { display: grid; grid-template-columns: 20px 1fr; gap: 10px; align-items: start; }
  .wz-feats li::before { content: ''; width: 18px; height: 18px; margin-top: 1px; border-radius: 50%; background: #104D30 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 18 18'%3E%3Cpath d='M5 9.3l2.6 2.6L13 6.5' fill='none' stroke='%23EEF3EF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center / 18px no-repeat; }
  .wz-plan .wz-btn { margin-top: auto; width: 100%; }
  .wz-plan.dark .wz-btn-line, .wz-plan .wz-btn-line { color: inherit; }
  .wz-fine2 { margin: 0; font-size: 13px; color: var(--wx-muted); }

  /* schedule + coverage */
  .wz-sched { display: grid; grid-template-columns: minmax(0, 1.8fr) minmax(0, 1fr); gap: 24px; align-items: start; }
  .wz-days { display: grid; gap: 22px; }
  .wz-day h3 { margin: 0 0 6px; font-family: var(--wx-mono); font-size: 12.5px; font-weight: 500; letter-spacing: .08em; text-transform: uppercase; color: var(--wx-muted); }
  .wz-game { all: unset; box-sizing: border-box; cursor: pointer; width: 100%; display: grid; grid-template-columns: auto minmax(0, 1fr) auto; align-items: center; gap: 14px; padding: 13px 12px; border-bottom: 1px solid var(--wx-rule); color: var(--wx-ink); transition: background .2s, padding-left .25s cubic-bezier(.2, .7, .2, 1); }
  .wz-game:hover { background: color-mix(in srgb, var(--wx-ink) 5%, transparent); padding-left: 20px; }
  .wz-game:focus-visible { outline: 2px solid var(--wz-g); outline-offset: -2px; }
  .wz-game.fav { box-shadow: inset 3px 0 0 var(--wz-g); }
  .wz-game .wz-pips i { width: 9px; height: 26px; }
  .wz-game b { font-family: var(--wz-display); font-weight: 800; font-size: 19px; letter-spacing: -0.02em; }
  .wz-game small { display: block; margin-top: 2px; font-family: var(--wx-mono); font-size: 12px; letter-spacing: .04em; color: var(--wx-muted); }
  .wz-st { font-family: var(--wx-mono); font-size: 11.5px; letter-spacing: .06em; text-transform: uppercase; padding: 5px 9px; border-radius: 3px; border: 1px solid var(--wx-rule); color: var(--wx-muted); white-space: nowrap; }
  .wz-st.live { background: var(--wz-g); border-color: var(--wz-g); color: var(--wz-on-g); }
  .wz-cover { display: grid; padding: 26px; border-radius: 6px; background: var(--wz-black); color: #E6E8EB; }
  .wz-cover h3 { margin: 0 0 6px; font-family: var(--wz-display); font-weight: 800; font-size: 22px; letter-spacing: -0.02em; }
  .wz-cover > div { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 4px 12px; align-items: center; padding: 15px 0; border-bottom: 1px solid #262A2F; }
  .wz-cover b { font-family: var(--wz-display); font-weight: 800; font-size: 19px; }
  .wz-cover span { grid-column: 1; font-size: 14px; color: #A3A9B0; }
  .wz-cover em { grid-column: 2; grid-row: 1 / span 2; font-style: normal; font-family: var(--wx-mono); font-size: 11px; letter-spacing: .06em; text-transform: uppercase; padding: 5px 9px; border-radius: 3px; background: rgba(255, 255, 255, .08); color: #C9CED4; }
  .wz-cover em.live { background: var(--wz-g); color: var(--wz-on-g); }
  .wz-cover .wz-btn { margin-top: 18px; justify-self: start; }
  @media (max-width: 900px) { .wz-sched { grid-template-columns: 1fr; } }

  /* how a read works */
  .wz-how { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: clamp(20px, 4vw, 48px); align-items: stretch; }
  .wz-steps { list-style: none; margin: 0; padding: 0; display: grid; border-top: 2px solid var(--wx-ink); }
  .wz-steps li { display: grid; grid-template-columns: 64px minmax(0, 1fr); gap: 4px 14px; padding: 22px 0; border-bottom: 1px solid var(--wx-rule); }
  .wz-steps .n { grid-row: 1 / span 2; font-family: var(--wz-display); font-weight: 900; font-size: 36px; line-height: 1; letter-spacing: -0.04em; color: var(--wz-g); }
  .wz-steps b { font-family: var(--wz-display); font-weight: 800; font-size: 23px; letter-spacing: -0.025em; color: var(--wx-ink); }
  .wz-steps p { margin: 0; font-size: 15.5px; line-height: 1.55; color: var(--wx-muted); }
  .wz-ex { display: flex; flex-direction: column; gap: 18px; padding: clamp(22px, 3vw, 32px); border-radius: 6px; background: var(--wz-metal); color: #16181B; border: 1px solid #F5F6F7; --wz-spot: rgba(255, 255, 255, .65); }
  .wz-ex .wz-cap { color: #454B51; }
  .wz-ex-title { font-family: var(--wz-display); font-weight: 900; font-size: clamp(26px, 3vw, 36px); line-height: 1; letter-spacing: -0.04em; }
  .wz-ex-grid { display: grid; border-top: 1px solid rgba(22, 24, 27, .25); }
  .wz-ex-grid > div { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 4px 12px; align-items: baseline; padding: 13px 0; border-bottom: 1px solid rgba(22, 24, 27, .16); }
  .wz-ex-grid span { font-family: var(--wx-mono); font-size: 12px; letter-spacing: .06em; text-transform: uppercase; color: #454B51; }
  .wz-ex-grid b { font-family: var(--wz-display); font-weight: 800; font-size: 22px; letter-spacing: -0.03em; text-align: right; }
  .wz-ex-grid small { grid-column: 1 / -1; font-size: 13.5px; color: #454B51; }
  .wz-ex .wz-btn { align-self: flex-start; }
  @media (max-width: 860px) { .wz-how { grid-template-columns: 1fr; } }
  @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .wz-steps .n { color: #C9CED4; } }
  :root[data-theme="dark"] .wz-steps .n { color: #C9CED4; }

  /* closing line */
  .wz-quote { display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(0, 1fr); gap: clamp(28px, 5vw, 64px); align-items: end; margin-top: clamp(44px, 6vw, 80px); padding: clamp(32px, 6vw, 72px); border-radius: 6px; background: var(--wz-black); color: #E6E8EB; }
  .wz-quote blockquote { margin: 0; font-family: var(--wz-display); font-weight: 800; font-size: clamp(34px, 4.6vw, 62px); line-height: .98; letter-spacing: -0.045em; color: #F3F4F6; }
  .wz-quote blockquote::before { content: ''; display: block; width: 56px; height: 4px; background: var(--wz-g); margin-bottom: 28px; box-shadow: 0 0 0 1px rgba(255, 255, 255, .12); }
  .wz-quote .wx-ledger { border-top-color: #E6E8EB; }
  .wz-quote .wx-ledger div { border-bottom-color: #2A2E33; }
  .wz-quote .wx-ledger span { color: #A3A9B0; font-size: 12px; }
  .wz-quote .wx-ledger b { color: #F3F4F6; font-family: var(--wz-display); font-weight: 800; font-size: 22px; }
  @media (max-width: 760px) { .wz-quote { grid-template-columns: 1fr; } }
  .wg-lobby .wx-fine { font-size: 12px; }

  /* account dialog */
  .wz-dlg { border: 0; padding: 0; border-radius: 10px; width: min(580px, calc(100vw - 24px)); max-height: calc(100vh - 24px); overflow: auto; color: var(--wx-ink); background: #EEF0F2; box-shadow: 0 50px 100px -30px rgba(0, 0, 0, .7); }
  @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .wz-dlg { background: #1A1D21; } }
  :root[data-theme="dark"] .wz-dlg { background: #1A1D21; }
  .wz-dlg::backdrop { background: rgba(10, 12, 14, .62); -webkit-backdrop-filter: blur(5px); backdrop-filter: blur(5px); }
  .wz-dlg[open] { animation: wzPop .32s cubic-bezier(.2, .7, .2, 1); }
  @keyframes wzPop { from { opacity: 0; transform: translateY(16px) scale(.98); } to { opacity: 1; transform: none; } }
  .wz-dlg-in { position: relative; display: flex; flex-direction: column; gap: 16px; padding: 30px clamp(20px, 4vw, 34px) 28px; }
  .wz-dlg-top { height: 6px; margin: -30px calc(-1 * clamp(20px, 4vw, 34px)) 10px; background: var(--wz-metal); }
  .wz-x { all: unset; cursor: pointer; position: absolute; top: 18px; right: 18px; display: grid; place-items: center; width: 36px; height: 36px; border-radius: 50%; font-size: 22px; line-height: 1; transition: background .2s, transform .2s; }
  .wz-x:hover { background: color-mix(in srgb, currentColor 10%, transparent); transform: rotate(90deg); }
  .wz-x:focus-visible { outline: 2px solid var(--wz-g); }
  .wz-dlg .wx-mark { height: 30px; }
  .wz-dlg-h { margin: 0; font-family: var(--wz-display); font-weight: 900; font-size: 32px; line-height: 1; letter-spacing: -0.045em; }
  .wz-dlg-sub, .wz-dlg-body { margin: 0; font-size: 15.5px; line-height: 1.55; color: var(--wx-muted); }
  .wz-planpick { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
  .wz-planpick button { all: unset; box-sizing: border-box; cursor: pointer; display: grid; gap: 3px; padding: 13px 14px; border-radius: 6px; border: 1px solid var(--wx-rule); background: var(--color-panel); transition: border-color .2s, box-shadow .2s, transform .18s; }
  .wz-planpick button:hover { transform: translateY(-1px); border-color: var(--wx-ink); }
  .wz-planpick button[aria-checked="true"] { border-color: var(--wz-g); box-shadow: inset 0 0 0 1px var(--wz-g), 0 10px 20px -16px rgba(16, 77, 48, .9); }
  .wz-planpick button:focus-visible { outline: 2px solid var(--wz-g); outline-offset: 2px; }
  .wz-planpick b { font-family: var(--wz-display); font-weight: 800; font-size: 16px; }
  .wz-planpick span { font-size: 13.5px; color: var(--wx-muted); }
  .wz-fields { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .wz-field { display: grid; gap: 6px; font-size: 14px; font-weight: 600; }
  .wz-field.full { grid-column: 1 / -1; }
  .wz-opt { font-weight: 400; color: var(--wx-muted); }
  .wz-field input, .wz-field select { box-sizing: border-box; width: 100%; font: inherit; font-weight: 400; font-size: 15.5px; padding: 11px 12px; border-radius: 6px; border: 1px solid var(--wx-rule); background: var(--color-panel); color: var(--wx-ink); transition: border-color .2s, box-shadow .2s; }
  .wz-field input:focus, .wz-field select:focus { outline: none; border-color: var(--wz-g); box-shadow: 0 0 0 3px color-mix(in srgb, var(--wz-g) 22%, transparent); }
  .wz-field input[aria-invalid="true"] { border-color: #9A3B2E; }
  .wz-dlg-act { display: flex; flex-wrap: wrap; align-items: center; gap: 12px 16px; }
  .wz-msg { font-size: 14px; color: #9A3B2E; }
  .wz-dlg-fine { margin: 0; font-size: 13px; line-height: 1.5; color: var(--wx-muted); }
  .wz-acct-dl { display: grid; margin: 0; border-top: 1px solid var(--wx-rule); }
  .wz-acct-dl div { display: flex; justify-content: space-between; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--wx-rule); }
  .wz-acct-dl dt { font-family: var(--wx-mono); font-size: 12px; letter-spacing: .06em; text-transform: uppercase; color: var(--wx-muted); }
  .wz-acct-dl dd { margin: 0; font-weight: 600; text-align: right; overflow-wrap: anywhere; }
  .wz-danger { color: #9A3B2E; }
  @media (max-width: 520px) { .wz-planpick, .wz-fields { grid-template-columns: 1fr; } }

  /* simple tables + folded filters */
  .wz-cols { margin-left: auto; }
  .wz-filters { position: relative; }
  .wz-filters > summary { list-style: none; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; min-height: 42px; box-sizing: border-box; padding: 0 16px; border-radius: 999px; border: 1px solid var(--wx-rule); font-weight: 600; font-size: 14.5px; transition: background .2s, border-color .2s; }
  .wz-filters > summary::-webkit-details-marker { display: none; }
  .wz-filters > summary::after { content: ''; width: 7px; height: 7px; border-right: 2px solid currentColor; border-bottom: 2px solid currentColor; transform: rotate(45deg) translateY(-2px); transition: transform .2s; }
  .wz-filters[open] > summary::after { transform: rotate(225deg) translateY(-2px); }
  .wz-filters > summary:hover { border-color: var(--wx-ink); }
  .wz-filters > summary:focus-visible { outline: 2px solid var(--wz-g); outline-offset: 2px; }
  .wz-filters > summary b { font-family: var(--wx-mono); font-size: 11px; padding: 2px 6px; border-radius: 3px; background: var(--wz-g); color: var(--wz-on-g); }
  .wz-filters-in { position: absolute; z-index: 40; top: calc(100% + 8px); left: 0; display: grid; gap: 10px; min-width: min(320px, calc(100vw - 48px)); padding: 16px; border-radius: 8px; background: var(--color-panel); border: 1px solid var(--color-border-line); box-shadow: 0 24px 50px -24px rgba(0, 0, 0, .55); animation: wzPop .22s ease both; }
  .wz-filters-in select { width: 100%; }
  .wz-inj { display: inline-block; margin-left: 8px; padding: 1px 5px; border-radius: 3px; font-family: var(--wx-mono); font-size: 10.5px; font-weight: 500; letter-spacing: .04em; vertical-align: 1px; background: color-mix(in srgb, #9A3B2E 16%, transparent); color: var(--wx-ink); border: 1px solid color-mix(in srgb, #9A3B2E 45%, transparent); }
  .rs-table tbody tr { transition: background-color .15s ease; }

  @media (prefers-reduced-motion: reduce) {
    .wz-track, .wz-hero, .wz-top .wg-record-label i { animation: none !important; }
    .wz-js .wz-reveal:not(.wz-in) { opacity: 1; transform: none; }
    .wz-btn::before, .wz-ripple { display: none; }
    .wz-btn, .wz-an, .wz-plan, .wz-game, .wz-helm, .wz-logo { transition: none !important; }
    .wz-an, .wx-reads .wx-read, .wz-dlg[open], .wz-matchup.enter .wz-helm, .wz-filters-in { animation: none !important; }
  }
'''
for k, v in FB.items():
    CSS = CSS.replace('/_blob/@' + k + '"', '/_blob/' + v + '"')
assert '/_blob/@' not in CSS
# grain token is already defined on .wg-paper (--wx-grain)
assert s.count('</style>') == 1
s = s.replace('</style>', CSS + '</style>')

# ============================================================================ header + nav
i, j = cut('  <header class="wg-head" id="top">', '  <!-- ============ LOBBY ============ -->')
old = s[i:j]
nav_i = old.index('  <nav class="rs-tabs wg-nav"'); nav = old[nav_i:].rstrip()
nav = nav.replace('    <button type="button" class="rs-tab wg-tab-apply" data-page="apply">Apply to be an analyst</button>\n', '')
assert 'wg-tab-apply' not in nav
rec_i = old.index('      <div class="wg-record" id="wg-record"'); rec_j = old.index('</div>\n', old.index('<span class="wg-record-sub">', rec_i)) + len('</div>\n')
record = old[rec_i:rec_j].strip()
HEADER = f'''  <header class="wg-head wz-top" id="top">
    <h1 class="wg-visually-hidden">Wedge · Football, understood.</h1>
    <div class="wz-bar">
      <button type="button" class="wz-logo" data-go="lobby" aria-label="Wedge home"><img src="{WM['light']}" alt="Wedge" width="112" height="40"></button>
      <div class="wz-bar-r">
        {record}
        <button type="button" class="wz-btn wz-btn-ghost wz-btn-sm" id="wz-login">Log in</button>
        <button type="button" class="wz-btn wz-btn-g wz-btn-sm" id="wz-signup">Sign up</button>
        <button type="button" class="wz-me" id="wz-me" hidden><span class="wz-av" id="wz-me-av">W</span><span id="wz-me-name">Account</span><em id="wz-me-plan">Free</em></button>
        <button type="button" class="wz-btn wz-btn-g wz-btn-sm" id="wz-gopro" data-wz-join="monthly" hidden>Go Pro</button>
      </div>
    </div>
    <p class="wg-certnote" id="certnote" role="status" hidden></p>
  {nav.strip()}
  </header>

'''
s = s[:i] + HEADER + s[j:]
rep('<i aria-hidden="true"></i>Wedge record</span>', '<i aria-hidden="true"></i>Certified hit rate</span>')

# ============================================================================ lobby
TEAM_OPTS = ''.join(f'<option value="{k}">{v}</option>' for k, v in [
    ('ARI', 'Arizona'), ('ATL', 'Atlanta'), ('BAL', 'Baltimore'), ('BUF', 'Buffalo'), ('CAR', 'Carolina'), ('CHI', 'Chicago'), ('CIN', 'Cincinnati'), ('CLE', 'Cleveland'),
    ('DAL', 'Dallas'), ('DEN', 'Denver'), ('DET', 'Detroit'), ('GB', 'Green Bay'), ('HOU', 'Houston'), ('IND', 'Indianapolis'), ('JAX', 'Jacksonville'), ('KC', 'Kansas City'),
    ('LV', 'Las Vegas'), ('LAC', 'Los Angeles (LAC)'), ('LAR', 'Los Angeles (LAR)'), ('MIA', 'Miami'), ('MIN', 'Minnesota'), ('NE', 'New England'), ('NO', 'New Orleans'),
    ('NYG', 'New York (NYG)'), ('NYJ', 'New York (NYJ)'), ('PHI', 'Philadelphia'), ('PIT', 'Pittsburgh'), ('SF', 'San Francisco'), ('SEA', 'Seattle'), ('TB', 'Tampa Bay'),
    ('TEN', 'Tennessee'), ('WSH', 'Washington')])
i, j = cut('  <div class="rs-page wg-lobby wg-play" id="lobby">', '  <!-- ============ ALL LINES (original screen) ============ -->')
old = s[i:j]
reads_i = old.index('    <section class="wx-sec" aria-labelledby="reads-h">'); reads_j = old.index('    </section>', reads_i) + len('    </section>')
reads = old[reads_i:reads_j]
reads = reads.replace('<section class="wx-sec" aria-labelledby="reads-h">', '<section class="wz-sec wz-reveal" id="wz-reads" aria-labelledby="reads-h">')
reads = reads.replace('<div class="wx-sec-head">', '<div class="wz-head">').replace('<span class="wx-label">01 / This week</span><h2 class="wx-h2" id="reads-h">', '<span class="wz-label">02 / This week</span><h2 class="wz-h2" id="reads-h">')
reads = reads.replace('<p class="wx-sec-sub" id="wx-reads-sub">', '<p class="wz-sub" id="wx-reads-sub">')
reads = reads.replace('      <div class="wx-reads" id="wg-hot-cards"', '      <div class="wz-matchup" id="wz-matchup" hidden></div>\n      <div class="wx-reads" id="wg-hot-cards"')
reads = reads.replace('<div><button type="button" class="wg-go" id="wx-reads-more"', '<div class="wz-row-cta"><button type="button" class="wz-btn wz-btn-line" id="wx-reads-more"')
reads = reads.replace('reads ↗</button></div>', 'reads ↗</button><button type="button" class="wz-btn wz-btn-g" data-wz-join="monthly">Unlock every read</button></div>')
assert 'wz-matchup' in reads and 'Unlock every read' in reads and 'wz-btn wz-btn-line' in reads
quote_i = old.index('      <div class="wx-quote">'); quote_j = old.index('      </div>\n    </section>', quote_i)
ledger = old[old.index('        <div class="wx-ledger"', quote_i):quote_j].rstrip()
assert ledger.endswith('</div>')
LOBBY = f'''  <div class="rs-page wg-lobby wg-play" id="lobby">
    <section class="wz-hero" aria-labelledby="hero-title">
      <div class="wz-hero-copy">
        <span class="wz-kick"><i class="wx-dot" aria-hidden="true"></i><span id="wz-kick">NFL · Week 9</span></span>
        <h2 class="wz-h1" id="hero-title">Football,<br><em>understood.</em></h2>
        <p class="wz-lede">Analyst picks and certified reads on Robinhood's football markets, with every result kept on the record.</p>
        <div class="wz-cta">
          <button type="button" class="wz-btn wz-btn-g wz-btn-lg" data-wz-join="monthly">Join Wedge Pro</button>
          <button type="button" class="wz-btn wz-btn-line wz-btn-lg" data-wz-jump="wz-reads">This week's reads</button>
        </div>
        <p class="wz-micro">$19.99 a month or $119.99 a season · cancel anytime</p>
        <p class="wg-hero-desc wg-visually-hidden" id="wg-profit" data-source="results" aria-live="polite">Net profit on Wedge-certified picks so far: —</p>
      </div>
      <div class="wz-proof wz-spot" data-source="results" aria-label="Track record">
        <div class="wz-proof-lead">
          <span class="wz-cap">Wedge-certified picks · hit rate</span>
          <div class="wz-big" data-wz="cert-pct">—</div>
          <span class="wz-cap2" data-wz="cert-rec">Settled picks, before fees</span>
        </div>
        <div class="wz-proof-row">
          <div><span class="wz-cap">Net profit</span><b data-wz="cert-profit">—</b><small>Certified picks, at the posted price</small></div>
          <div><span class="wz-cap">Analysts</span><b data-wz="an-pct">—</b><small data-wz="an-rec">Every analyst pick, settled</small></div>
        </div>
        <button type="button" class="wz-btn wz-btn-ghost" data-wz-jump="wz-analysts">See the track record</button>
      </div>
    </section>

    <div class="wz-ticker" id="wz-ticker" data-source="lines lines_all" aria-hidden="true">
      <div class="wz-tape"><div class="wz-track" id="wz-tape-1"></div></div>
      <div class="wz-tape rev"><div class="wz-track" id="wz-tape-2"></div></div>
    </div>

    <section class="wz-sec wz-reveal" id="wz-analysts" aria-labelledby="an-h">
      <div class="wz-head">
        <div><span class="wz-label">01 / Track record</span><h2 class="wz-h2" id="an-h">The analysts.</h2></div>
        <p class="wz-sub">Every pick is tracked and settled against the box score, wins and losses alike. Members see each pick as it's posted.</p>
      </div>
      <div class="wz-board" id="wz-board" data-source="results"><p class="wx-empty">Loading the standings…</p></div>
      <div class="wz-row-cta">
        <button type="button" class="wz-btn wz-btn-g" data-wz-join="monthly">Get every analyst pick</button>
        <button type="button" class="wz-btn wz-btn-line" data-go="analysts">Full standings</button>
        <button type="button" class="wz-link" data-go="apply">Apply to be an analyst</button>
      </div>
    </section>

{reads}

    <section class="wz-sec wz-reveal" id="wz-plans" aria-labelledby="plans-h">
      <div class="wz-head">
        <div><span class="wz-label">03 / Membership</span><h2 class="wz-h2" id="plans-h">Join the inner circle.</h2></div>
        <p class="wz-sub">Every analyst pick and certified read, the full board, and the read behind every line.</p>
      </div>
      <div class="wz-plans">
        <article class="wz-plan wz-spot">
          <div class="wz-plan-top"><h3>Free</h3></div>
          <div class="wz-price">$0</div>
          <p class="wz-plan-note">See how Wedge works</p>
          <ul class="wz-feats"><li>The lobby and the track record</li><li>Analyst standings</li><li>Charts and research</li></ul>
          <button type="button" class="wz-btn wz-btn-line" data-wz-join="free">Create a free account</button>
        </article>
        <article class="wz-plan hot wz-spot">
          <div class="wz-plan-top"><h3>Wedge Pro</h3><span class="wz-badge">Most popular</span></div>
          <div class="wz-price">$19.99<span>/ month</span></div>
          <p class="wz-plan-note">Cancel anytime</p>
          <ul class="wz-feats"><li>Every analyst pick as it's posted</li><li>Wedge-certified picks every week</li><li>The full NFL board with 2026 hit rates</li><li>The read behind every line</li><li>Anytime TD model and prop groups</li><li>NBA now, soccer at launch</li></ul>
          <button type="button" class="wz-btn wz-btn-g wz-btn-lg" data-wz-join="monthly">Join monthly</button>
        </article>
        <article class="wz-plan dark wz-spot">
          <div class="wz-plan-top"><h3>Wedge Pro Season</h3><span class="wz-badge">Best value</span></div>
          <div class="wz-price">$119.99<span>/ year</span></div>
          <p class="wz-plan-note">About $10 a month</p>
          <ul class="wz-feats"><li>Everything in Wedge Pro</li><li>Every NFL week and NBA night of the season</li><li>First access to new features</li></ul>
          <button type="button" class="wz-btn wz-btn-ghost wz-btn-lg" data-wz-join="season">Join for the season</button>
        </article>
      </div>
      <p class="wz-fine2">Prices in US dollars. Wedge is research, not financial advice.</p>
    </section>

    <section class="wz-sec wz-reveal" id="wz-schedule" aria-labelledby="sched-h">
      <div class="wz-head">
        <div><span class="wz-label">04 / Schedule</span><h2 class="wz-h2" id="sched-h">This week on Wedge.</h2></div>
        <p class="wz-sub">Reads open as Robinhood lists each game. Select a game for its reads.</p>
      </div>
      <div class="wz-sched">
        <div class="wz-days" id="wz-days" data-source="lines_all"><p class="wx-empty">Loading the schedule…</p></div>
        <aside class="wz-cover" aria-label="Coverage">
          <h3>Coverage</h3>
          <div><b>NFL</b><span>Every game, every week</span><em class="live">Live</em></div>
          <div><b>Analyst picks</b><span>NFL, tracked all season</span><em class="live">Live</em></div>
          <div><b>NBA</b><span>The nightly board</span><em>Beta</em></div>
          <div><b>Soccer</b><span>Premier League, Champions League, MLS</span><em>Coming soon</em></div>
          <button type="button" class="wz-btn wz-btn-ghost" data-wz-join="season">Lock in the season</button>
        </aside>
      </div>
    </section>

    <section class="wz-sec wz-reveal" id="wz-method" aria-labelledby="how-h">
      <div class="wz-head">
        <div><span class="wz-label">05 / Method</span><h2 class="wz-h2" id="how-h">How a read works.</h2></div>
        <p class="wz-sub">Three steps, in order. The price comes last.</p>
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

    <section class="wz-quote wz-reveal" aria-labelledby="persp-h">
      <h2 class="wg-visually-hidden" id="persp-h">Perspective</h2>
      <blockquote>A good result deserves the same scrutiny as a bad one.</blockquote>
{ledger}
    </section>
    <p class="wx-fine">Wedge is football research, not financial advice. Prices move and reads lose; every figure is before fees.</p>

    <dialog class="wz-dlg" id="wz-dlg" aria-labelledby="wz-dlg-h">
      <div class="wz-dlg-in">
        <div class="wz-dlg-top" aria-hidden="true"></div>
        <button type="button" class="wz-x" id="wz-dlg-x" aria-label="Close">×</button>
        <div><img class="wx-mark i" src="{WM['ink']}" alt="" width="84" height="30"><img class="wx-mark l" src="{WM['light']}" alt="" width="84" height="30" aria-hidden="true"></div>
        <h2 class="wz-dlg-h" id="wz-dlg-h">Create your Wedge account</h2>
        <p class="wz-dlg-sub" id="wz-dlg-sub">Pick a plan. You can change it any time.</p>
        <div class="wz-mode" data-mode="signup">
          <div class="wz-planpick" role="radiogroup" aria-label="Plan">
            <button type="button" role="radio" aria-checked="false" data-plan="free"><b>Free</b><span>$0</span></button>
            <button type="button" role="radio" aria-checked="true" data-plan="monthly"><b>Wedge Pro</b><span>$19.99 / month</span></button>
            <button type="button" role="radio" aria-checked="false" data-plan="season"><b>Pro Season</b><span>$119.99 / year</span></button>
          </div>
          <div class="wz-fields" style="margin-top:16px">
            <label class="wz-field">First name<input type="text" id="wz-f-first" autocomplete="given-name" maxlength="60"></label>
            <label class="wz-field">Email<input type="email" id="wz-f-email" autocomplete="email" maxlength="120"></label>
            <label class="wz-field full"><span>Favorite team <span class="wz-opt">(optional)</span></span><select id="wz-f-team"><option value="">No favorite</option>{TEAM_OPTS}</select></label>
          </div>
          <div class="wz-dlg-act" style="margin-top:18px"><button type="button" class="wz-btn wz-btn-g wz-btn-lg" id="wz-go">Continue to checkout</button><span class="wz-msg" id="wz-msg" role="alert"></span></div>
          <p class="wz-dlg-fine" style="margin-top:14px">Your account is tied to the sign-in you use to view Wedge, and your details stay private to you. Paid plans go straight to checkout.</p>
        </div>
        <div class="wz-mode" data-mode="login" hidden>
          <p class="wz-dlg-body">You're signed in, but there's no Wedge account on this sign-in yet. Creating one takes a single step.</p>
          <div class="wz-dlg-act" style="margin-top:16px"><button type="button" class="wz-btn wz-btn-g wz-btn-lg" data-wz-to="signup">Create my account</button></div>
        </div>
        <div class="wz-mode" data-mode="account" hidden>
          <dl class="wz-acct-dl" id="wz-acct-dl"></dl>
          <div class="wz-dlg-act" style="margin-top:16px"><button type="button" class="wz-btn wz-btn-g" id="wz-upgrade">Upgrade to Pro</button><button type="button" class="wz-btn wz-btn-line" data-wz-to="signup">Edit details</button><button type="button" class="wz-link wz-danger" id="wz-delete">Delete my account</button></div>
        </div>
        <div class="wz-mode" data-mode="done" hidden>
          <p class="wz-dlg-body" id="wz-done-text"></p>
          <p class="wz-dlg-body"><a class="wz-link" id="wz-done-link" href="#" target="_blank" rel="noopener" hidden>Open it again</a></p>
          <div class="wz-dlg-act" style="margin-top:8px"><button type="button" class="wz-btn wz-btn-g" id="wz-done-ok">Back to Wedge</button></div>
        </div>
      </div>
    </dialog>
    <svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
      <radialGradient id="wzHelmShade" cx="34%" cy="24%" r="82%"><stop offset="0" stop-color="#fff" stop-opacity=".62"/><stop offset=".32" stop-color="#fff" stop-opacity=".08"/><stop offset=".7" stop-color="#000" stop-opacity=".12"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient>
    </defs></svg>
  </div>

'''
s = s[:i] + LOBBY + s[j:]

# ============================================================================ JS: hooks into existing renderers
rep("      fracEl.textContent = `(${w}/${n})`;\n", "      fracEl.textContent = `(${w}/${n})`;\n      wzRecord(p, w, n);\n")
rep("    } else { pctEl.textContent = '—'; fracEl.textContent = '(0/0)'; }", "    } else { pctEl.textContent = '—'; fracEl.textContent = '(0/0)'; wzRecord(null, 0, 0); }")
rep("    el.replaceChildren('Net profit on Wedge-certified picks so far: ', big);\n", "    el.replaceChildren('Net profit on Wedge-certified picks so far: ', big);\n    wzSet('cert-profit', big.textContent, true);\n")
rep("    const ranked = stats.slice().sort((a, b) => (b.winPct ?? -1) - (a.winPct ?? -1) || (b.profitPct ?? -1e9) - (a.profitPct ?? -1e9) || b.n - a.n);\n",
    "    const ranked = stats.slice().sort((a, b) => (b.winPct ?? -1) - (a.winPct ?? -1) || (b.profitPct ?? -1e9) - (a.profitPct ?? -1e9) || b.n - a.n);\n    try { wzAnalysts(ranked); } catch (e) { /* the lobby board is optional */ }\n")
rep("      board.replaceChildren(); tbody.replaceChildren();\n",
    "      board.replaceChildren(); tbody.replaceChildren();\n      if (certUnavailable) { const wb = $('#wz-board'); if (wb) wb.replaceChildren(el('p', 'wx-empty', 'Analyst standings are unavailable in this view.')); }\n")
rep("    if (ld.status === 'ok' || la.status === 'ok') wxDraw();", "    if (ld.status === 'ok' || la.status === 'ok') wxDraw();\n    wzLobby();")
# read cards: side record this season + spotlight
rep("    b.append(top, el('b', 'wx-read-title', label), mid, px, foot);",
    """    const hh = num(r.hits), gg = num(r.games);
    let hrow = null;
    if (hh != null && gg) { const k = side === 'Yes' ? hh : gg - hh; hrow = el('span', 'wz-hr'); hrow.append(el('b', null, Math.round(100 * k / gg) + '%'), `${side} in ${k} of ${gg} games this season`); }
    b.classList.add('wz-spot');
    b.append(top, el('b', 'wx-read-title', label), mid, px, ...(hrow ? [hrow] : []), foot);""")
# game tabs: team-color pips
rep("      if (g) { t.append(g); const d", "      if (g) { t.append(wzPips(g), g); const d")
# matchup banner
rep("    if (!box) return;\n    if (!wxGame) {", "    if (!box) return;\n    wzMatchup(wxGame);\n    if (!wxGame) {")
# lines: injury chip in the line cell
rep("      const lc = td(rhLabel(r.contract), 'rs-contract'); if (lc.textContent !== r.contract) lc.title = r.contract;\n      certBadge(lc, ck);\n      td(r.yes_price, 'num');",
    "      const lc = td(wzLabel(r), 'rs-contract'); if (lc.textContent !== r.contract) lc.title = r.contract;\n      certBadge(lc, ck);\n      td(r.yes_price, 'num');")
rep("      certBadge(lc, ck);\n      td(r.yes_price, 'num');\n      srcCell(tr, r);",
    "      certBadge(lc, ck);\n      wzInj(lc, r.flags);\n      td(r.yes_price, 'num');\n      srcCell(tr, r);")

JS = r'''
  // ================= Wedge UI round 2: record, analysts, lobby, matchups, accounts, tables, motion =================
  const WZ_REDUCE = (() => { try { return matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { return false; } })();
  // Paste a payment link (for example a Stripe Payment Link) for each plan; empty sends a membership request by email instead.
  const WZ_CHECKOUT = { monthly: '', season: '' };
  // Accounts paused (Wed Nov 4, 10 PM): no Log in / Sign up in the header; Join still goes straight to checkout. Set true to bring accounts back.
  const WZ_ACCOUNTS = false;
  const WZ_PLANS = { free: ['Free', '$0'], monthly: ['Wedge Pro', '$19.99 / month'], season: ['Wedge Pro Season', '$119.99 / year'] };
  const WZ_TEAMS = { ARI: ['Arizona', '#97233F', '#111111'], ATL: ['Atlanta', '#A71930', '#111111'], BAL: ['Baltimore', '#241773', '#9E7C0C'], BUF: ['Buffalo', '#00338D', '#C60C30'],
    CAR: ['Carolina', '#0085CA', '#101820'], CHI: ['Chicago', '#0B162A', '#C83803'], CIN: ['Cincinnati', '#FB4F14', '#111111'], CLE: ['Cleveland', '#311D00', '#FF3C00'],
    DAL: ['Dallas', '#003594', '#869397'], DEN: ['Denver', '#FB4F14', '#002244'], DET: ['Detroit', '#0076B6', '#B0B7BC'], GB: ['Green Bay', '#203731', '#FFB612'],
    HOU: ['Houston', '#03202F', '#A71930'], IND: ['Indianapolis', '#002C5F', '#A2AAAD'], JAX: ['Jacksonville', '#006778', '#D7A22A'], KC: ['Kansas City', '#E31837', '#FFB81C'],
    LV: ['Las Vegas', '#111111', '#A5ACAF'], LAC: ['Los Angeles', '#0080C6', '#FFC20E'], LAR: ['Los Angeles', '#003594', '#FFA300'], MIA: ['Miami', '#008E97', '#FC4C02'],
    MIN: ['Minnesota', '#4F2683', '#FFC62F'], NE: ['New England', '#002244', '#C60C30'], NO: ['New Orleans', '#D3BC8D', '#101820'], NYG: ['New York', '#0B2265', '#A71930'],
    NYJ: ['New York', '#125740', '#FFFFFF'], PHI: ['Philadelphia', '#004C54', '#A5ACAF'], PIT: ['Pittsburgh', '#FFB612', '#101820'], SF: ['San Francisco', '#AA0000', '#B3995D'],
    SEA: ['Seattle', '#002244', '#69BE28'], TB: ['Tampa Bay', '#D50A0A', '#34302B'], TEN: ['Tennessee', '#0C2340', '#4B92DB'], WSH: ['Washington', '#5A1414', '#FFB612'] };
  const wzSides = (game) => { const m = /^(\S+) @ (\S+)$/.exec(String(game || '')); return m ? [m[1], m[2]] : [null, null]; };
  const wzTeam = (t) => WZ_TEAMS[t] || [t || '', '#4A5056', '#9DA3AA'];

  // count-up for headline numbers (first time only)
  function wzCount(e, text) {
    const m = /^([+−-]?)(\d+(?:\.\d+)?)(.*)$/.exec(String(text));
    if (!m || WZ_REDUCE || e.dataset.counted) { e.textContent = text; return; }
    e.dataset.counted = '1';
    const to = Number(m[2]), dec = (m[2].split('.')[1] || '').length, t0 = performance.now(), dur = 1100;
    const step = (t) => { const k = Math.min(1, (t - t0) / dur), v = to * (1 - Math.pow(1 - k, 3)); e.textContent = m[1] + v.toFixed(dec) + m[3]; if (k < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  }
  function wzSet(k, v, count) { document.querySelectorAll(`[data-wz="${k}"]`).forEach((e) => { if (count) wzCount(e, v); else e.textContent = v; }); }
  function wzRecord(p, w, n) {
    const big = document.querySelector('[data-wz="cert-pct"]');
    if (big) {
      if (p == null) big.textContent = '—';
      else { const t = (p % 1 ? p.toFixed(1) : String(p)); if (WZ_REDUCE || big.dataset.counted) { big.replaceChildren(t, el('small', null, '%')); } else { big.dataset.counted = '1'; const sp = el('span', null, '0'); big.replaceChildren(sp, el('small', null, '%')); wzCount(sp, t); } }
    }
    wzSet('cert-rec', n ? `${w} of ${n} certified picks won, before fees` : 'No certified picks have settled yet');
  }

  // analysts on the lobby
  function wzAnalysts(ranked) {
    const box = $('#wz-board'); if (!box) return;
    const idx = pickIndex();
    let W = 0, N = 0;
    const fmtP = (p, signed) => (signed ? (p > 0 ? '+' : (p < 0 ? '−' : '')) : '') + (Math.abs(p) % 1 ? Math.abs(p).toFixed(1) : Math.abs(p)) + '%';
    const cards = ranked.map((st, i) => {
      W += st.wins; N += st.n;
      const c = el('article', 'wz-an wz-spot' + (i === 0 && st.n ? ' lead' : ''));
      const top = el('div', 'wz-an-top'); const av = el('span', 'wz-av', st.name.slice(0, 1).toUpperCase()); av.setAttribute('aria-hidden', 'true');
      top.append(av, el('span', 'wz-an-name', st.name), el('span', 'wz-an-rank', st.n ? '#' + (i + 1) : '—'));
      const pct = el('div', 'wz-an-pct');
      if (st.winPct == null) pct.textContent = '—'; else pct.append(String(st.winPct % 1 ? st.winPct.toFixed(1) : st.winPct), el('small', null, '%'));
      const meta = el('div', 'wz-an-meta');
      meta.append(el('span', null, st.n ? `${st.wins}–${st.n - st.wins} settled` : 'No picks settled yet'));
      if (st.profitPct != null) meta.append(el('span', 'wz-chip ' + (st.profitPct > 0 ? 'pos' : st.profitPct < 0 ? 'neg' : 'flat'), fmtP(st.profitPct, true) + ' profit'));
      const keys = analysts.picks[st.name] || [];
      const last = keys.map((k) => pickInfo(idx, k)).filter((v) => v.outcome === 'Won' || v.outcome === 'Lost').sort((a, b) => (Number(a.week) || 0) - (Number(b.week) || 0)).slice(-5);
      const dots = el('div', 'wz-dots'); dots.setAttribute('aria-label', last.length ? 'Last ' + last.length + ': ' + last.map((v) => (v.outcome === 'Won' ? 'win' : 'loss')).join(', ') : 'No settled picks yet');
      last.forEach((v) => dots.append(el('i', v.outcome === 'Won' ? 'w' : '')));
      dots.append(el('small', null, st.pending ? `${st.pending} pending` : (last.length ? 'Last ' + last.length : '')));
      c.append(top, pct, meta, dots);
      return c;
    });
    box.replaceChildren(...(cards.length ? cards : [el('p', 'wx-empty', 'No analysts yet.')]));
    if (N) { wzSet('an-pct', fmtP(Math.round(1000 * W / N) / 10), true); wzSet('an-rec', `${W} of ${N} analyst picks won`); }
    else { wzSet('an-pct', '—'); wzSet('an-rec', 'No analyst picks have settled yet'); }
  }

  // team colors + generic helmets (no logos)
  function wzPips(game) {
    const [a, h] = wzSides(game), p = el('span', 'wz-pips'); p.setAttribute('aria-hidden', 'true');
    for (const t of [a, h]) { const i = el('i'); i.style.background = wzTeam(t)[1]; p.append(i); }
    return p;
  }
  function wzHelmet(team, flip) {
    const [, c1, c2] = wzTeam(team);
    const ns = 'http://www.w3.org/2000/svg', svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('viewBox', '0 0 160 122'); svg.setAttribute('class', 'wz-helm'); svg.setAttribute('aria-hidden', 'true');
    const g = document.createElementNS(ns, 'g'); if (flip) g.setAttribute('transform', 'translate(160 0) scale(-1 1)');
    const shell = 'M22 70 C16 37 42 9 80 9 C114 9 138 33 140 61 L140 70 C140 76 135 80 129 80 L112 80 L108 95 C106 102 99 107 92 107 L58 107 C44 107 34 100 30 91 C26 86 23 79 22 70 Z';
    const add = (tag, at) => { const n = document.createElementNS(ns, tag); for (const k in at) n.setAttribute(k, at[k]); g.append(n); return n; };
    add('ellipse', { cx: 80, cy: 115, rx: 58, ry: 5, fill: '#000', opacity: '.22' });
    add('path', { d: shell, fill: c1 });
    add('path', { d: shell, fill: 'url(#wzHelmShade)' });
    add('path', { d: 'M34 58 C42 32 66 19 98 21', fill: 'none', stroke: '#fff', 'stroke-opacity': '.42', 'stroke-width': 5, 'stroke-linecap': 'round' });
    add('circle', { cx: 74, cy: 70, r: 8, fill: '#000', opacity: '.38' });
    add('path', { d: 'M112 63 H152 M116 78 H152 M120 93 H147 M152 57 V97 C152 104 146 109 139 109 H104', fill: 'none', stroke: c2, 'stroke-width': 5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' });
    add('path', { d: 'M112 63 H152 M116 78 H152', fill: 'none', stroke: '#fff', 'stroke-opacity': '.25', 'stroke-width': 1.5 });
    svg.append(g); return svg;
  }
  function wzGameInfo(rows, game) {
    let spread = null, total = null, ko = '', utc = '';
    for (const r of rows) {
      if (r.game !== game) continue;
      if (!ko) { ko = r.kickoff || ''; utc = r.kickoff_utc || ''; }
      if (total == null && num(r.game_total) != null) total = num(r.game_total);
      if (!spread) { const m = /Books: (\w+) by -?([\d.]+)/.exec(r.book_lines || ''); if (m) spread = [m[1], m[2]]; }
      if (spread && total != null && ko) break;
    }
    return { spread, total, ko, utc };
  }
  function wzMatchup(game) {
    const box = $('#wz-matchup'); if (!box) return;
    if (!game) { box.hidden = true; box.replaceChildren(); return; }
    const [a, h] = wzSides(game); if (!a) { box.hidden = true; return; }
    const la = dash.data('lines_all'), info = la.status === 'ok' ? wzGameInfo(la.data, game) : { spread: null, total: null, ko: '' };
    const side = (t, home) => {
      const d = el('div', 'wz-mt-side' + (home ? ' home' : '')); const txt = el('div'); txt.append(el('b', null, t), el('span', null, wzTeam(t)[0] + (home ? ' · home' : ' · away')));
      if (home) d.append(txt, wzHelmet(t, true)); else d.append(wzHelmet(t, false), txt);
      return d;
    };
    const mid = el('div', 'wz-mt-mid'); mid.append(el('span', 'wz-mt-at', '@'), el('span', 'wz-cap', info.ko || ''));
    const bits = []; if (info.spread) bits.push(`${info.spread[0]} by ${info.spread[1]}`); if (info.total != null) bits.push(`total ${info.total}`);
    if (bits.length) mid.append(el('span', 'wz-cap', bits.join(' · ')));
    box.style.setProperty('--ca', wzTeam(a)[1]); box.style.setProperty('--cb', wzTeam(h)[1]);
    box.setAttribute('aria-label', `${wzTeam(a)[0]} at ${wzTeam(h)[0]}${info.ko ? ', ' + info.ko : ''}`); box.setAttribute('role', 'group');
    box.replaceChildren(side(a, false), mid, side(h, true)); box.hidden = false;
    box.classList.remove('enter'); void box.offsetWidth; box.classList.add('enter');
  }

  // lobby: ticker, schedule, live example, kicker
  let wzTapeDone = false, wzSchedDone = false, wzExDone = false;
  const wzShort = (label) => String(label).replace(/^([^:]+):\s*/, (m0, n) => { const p = n.split(' ').filter((x) => !/^(Jr\.?|Sr\.?|II|III|IV|V)$/.test(x)); return (p[p.length - 1] || n) + ' '; });
  const wzSidePx = (r, side) => (side === 'Yes' ? num(r.yes_price) : (num(r.no_price) != null ? num(r.no_price) : (num(r.yes_bid) != null ? 100 - num(r.yes_bid) : null)));
  function wzTk(r, side, p, q) {
    const b = el('button', 'wz-tk'); b.type = 'button'; b.tabIndex = -1;
    const g = el('b'); g.append(wzPips(r.game), r.game.replace(' @ ', '@'));
    b.append(g, el('span', null, wzShort(rhLabel(r.contract))), el('i', null, `${side} ${q}¢`), el('em', null, `Wedge ${Math.round(p)}%`));
    b.addEventListener('click', () => { if (r.sit_key) { const ctx = { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source }; ctx.key = `${ctx.game}|${ctx.market}|${r.contract}`; openSit(r, ctx, b); } });
    return b;
  }
  function wzFill(track, items) {
    if (!track || !items.length) return;
    const one = items.map((x) => x()), two = items.map((x) => x());
    track.replaceChildren(...one, ...two); track.style.setProperty('--dur', Math.max(40, items.length * 5) + 's');
  }
  function wzLobby() {
    const ld = dash.data('lines'), la = dash.data('lines_all');
    if (!wzTapeDone && ld.status === 'ok' && la.status === 'ok') {
      wzTapeDone = true;
      const picks = ld.data.filter((r) => r.sit_pick && num(r.sit_hit) != null).sort((a, b) => num(b.sit_pedge) - num(a.sit_pedge)).slice(0, 18);
      wzFill($('#wz-tape-1'), picks.map((r) => () => { const s2 = r.sit_pick, p = s2 === 'Yes' ? num(r.sit_hit) : 100 - num(r.sit_hit); return wzTk(r, s2, p, wzSidePx(r, s2)); }));
      const games = [...new Set(la.data.map((r) => r.game))]; const seen = new Set(picks.map((r) => r.id.replace(/^A/, '')));
      const more = [];
      for (const g of games) for (const [b, r] of wxGameReads(la.data, g).top.slice(0, 2)) if (!seen.has(String(r.id).replace(/^A/, ''))) more.push(() => wzTk(r, b.side, b.p, b.q));
      wzFill($('#wz-tape-2'), more.length ? more : picks.map((r) => () => wzTk(r, r.sit_pick, r.sit_pick === 'Yes' ? num(r.sit_hit) : 100 - num(r.sit_hit), wzSidePx(r, r.sit_pick))));
    }
    if (!wzSchedDone && la.status === 'ok') { wzSchedDone = true; wzSchedule(la.data); }
    if (!wzExDone && ld.status === 'ok') { wzExDone = true; wzExample(ld.data); }
  }
  function wzSchedule(rows) {
    const box = $('#wz-days'); if (!box) return;
    const G = new Map(); for (const r of rows) if (!G.has(r.game)) G.set(r.game, { ko: r.kickoff || '', utc: r.kickoff_utc || '' });
    const list = [...G.entries()].sort((a, b) => (a[1].utc < b[1].utc ? -1 : a[1].utc > b[1].utc ? 1 : a[0] < b[0] ? -1 : 1));
    const day = (u) => { try { return new Date(u).toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric', timeZone: 'America/Chicago' }); } catch (e) { return ''; } };
    const now = Date.now(), byDay = new Map();
    for (const [g, v] of list) { const d = day(v.utc) || 'This week'; if (!byDay.has(d)) byDay.set(d, []); byDay.get(d).push([g, v]); }
    const fav = wzP && wzP.team;
    let next = null;
    const cols = [...byDay.entries()].map(([d, gs]) => {
      const sec = el('div', 'wz-day'); sec.append(el('h3', null, d));
      for (const [g, v] of gs) {
        const b = el('button', 'wz-game'); b.type = 'button'; b.dataset.game = g;
        const [a, h] = wzSides(g); if (fav && (fav === a || fav === h)) b.classList.add('fav');
        const mid = el('span'); mid.append(el('b', null, `${wzTeam(a)[0]} at ${wzTeam(h)[0]}`), el('small', null, `${g} · ${String(v.ko).replace(/\s*(Thu|Fri|Sat|Sun|Mon)$/, '')}`));
        const off = v.utc && Date.parse(v.utc) <= now; const n = off ? 0 : wxGameReads(rows, g).top.length;
        if (!off && !next) next = [g, v];
        const st = el('span', 'wz-st' + (!off && n ? ' live' : ''), off ? 'Kicked off' : (n ? `${n} read${n === 1 ? '' : 's'}` : 'Lines open'));
        b.append(wzPips(g), mid, st);
        b.addEventListener('click', () => { wxGame = g; try { localStorage.setItem('wx-read-game', g); } catch (e) { /* storage unavailable */ } wxDraw(); const t = $('#wz-reads'); if (t) t.scrollIntoView({ behavior: WZ_REDUCE ? 'auto' : 'smooth', block: 'start' }); });
        sec.append(b);
      }
      return sec;
    });
    box.replaceChildren(...cols);
    const k = $('#wz-kick'); if (k && next) k.textContent = `NFL · Week 9 · next up ${next[0]}, ${next[1].ko}`;
  }
  function wzExample(rows) {
    const box = $('#wz-example'); if (!box) return;
    const r = rows.filter((x) => x.sit_pick && x.sit_key && num(x.hits) != null && num(x.games)).sort((a, b) => num(b.sit_pedge) - num(a.sit_pedge))[0];
    if (!r) { box.replaceChildren(el('p', 'wx-empty', 'No live example right now.')); return; }
    const side = r.sit_pick, pS = side === 'Yes' ? num(r.sit_hit) : 100 - num(r.sit_hit), q = wzSidePx(r, side);
    const hh = num(r.hits), gg = num(r.games), k = side === 'Yes' ? hh : gg - hh;
    const row = (lab, val, note) => { const d = el('div'); d.append(el('span', null, lab), el('b', null, val)); if (note) d.append(el('small', null, note)); return d; };
    const grid = el('div', 'wz-ex-grid');
    grid.append(row('01 · This season', `${Math.round(100 * k / gg)}%`, `${side} in ${k} of ${gg} games${r.role ? ' · ' + r.role : ''}`),
      row('02 · Recent form', r.mom_type || '—', 'His last four games against his season. The defense, game script and weather are in the full read'),
      row('03 · Wedge % vs price', `${Math.round(pS)}% vs ${q}¢`, `${side}, ${Math.round(num(r.sit_pedge))} points better than the price`));
    const go = el('button', 'wz-btn wz-btn-g', 'Open the full read'); go.type = 'button';
    go.addEventListener('click', () => { const ctx = { title: rhLabel(r.contract), game: r.game, market: r.market, source: r.source }; ctx.key = `${ctx.game}|${ctx.market}|${r.contract}`; openSit(r, ctx, go); });
    const cap = el('span', 'wz-cap'); cap.append(`Live example · ${r.game} · ${r.kickoff}`);
    box.replaceChildren(cap, el('b', 'wz-ex-title', rhLabel(r.contract)), grid, go);
  }

  // accounts: a private Wedge profile per viewer, plan choice and checkout
  let wzP = null, wzRef = null, wzMe = '', wzPlan = 'monthly', wzMode = 'signup', wzDelArm = false;
  const wzDlg = $('#wz-dlg');
  async function wzInitAccount() {
    await new Promise((r) => setTimeout(r, 0));
    if (!WZ_ACCOUNTS) { wzHeader(); return; }
    const cl = window.claude; let db = null, user = null;
    if (cl && typeof cl.use === 'function') { try { [db, user] = await Promise.all([cl.use('db'), cl.use('user')]); } catch (e) { /* signed out or not granted */ } }
    let uid = null;
    if (user && typeof user.id === 'function') { try { uid = await user.id(); } catch (e) { uid = null; } }
    if (db && uid) { try { wzRef = db.doc(`data/users/${uid}/wedge-account`); const sn = await wzRef.get(); if (sn && sn.exists) wzP = sn.data(); } catch (e) { wzRef = null; } }
    if (!wzRef) { try { const t = localStorage.getItem('wedge-account'); if (t) wzP = JSON.parse(t); } catch (e) { /* storage unavailable */ } }
    if (user && typeof user.me === 'function') { try { const me = await user.me(); wzMe = ((me && me.name) || '').trim().split(/\s+/)[0] || ''; } catch (e) { /* no profile scope */ } }
    wzHeader(); wzPersonalize();
  }
  async function wzSave(p) {
    wzP = p;
    if (wzRef) { try { await wzRef.set(p); return true; } catch (e) { /* fall through */ } }
    try { if (p) localStorage.setItem('wedge-account', JSON.stringify(p)); else localStorage.removeItem('wedge-account'); return true; } catch (e) { return false; }
  }
  function wzHeader() {
    if (!WZ_ACCOUNTS) { ['#wz-login', '#wz-signup', '#wz-me', '#wz-gopro'].forEach((x) => { $(x).hidden = true; }); return; }
    const has = !!wzP;
    $('#wz-login').hidden = has; $('#wz-signup').hidden = has; $('#wz-me').hidden = !has;
    $('#wz-gopro').hidden = !has || wzP.plan !== 'free';
    if (has) {
      const nm = wzP.first || wzMe || 'Account';
      $('#wz-me-av').textContent = nm.slice(0, 1).toUpperCase(); $('#wz-me-name').textContent = nm;
      const pe = $('#wz-me-plan'); pe.textContent = wzP.plan === 'free' ? 'Free' : (wzP.status === 'active' ? 'Pro' : 'Pro · pending'); pe.className = wzP.plan === 'free' ? '' : 'pro';
    }
  }
  function wzPersonalize() {
    if (!wzP || !wzP.team) return;
    if (!wxGame) {
      const la = dash.data('lines_all');
      if (la.status === 'ok') { const g = [...new Set(la.data.map((r) => r.game))].find((x) => wzSides(x).includes(wzP.team)); if (g) { wxGame = g; wxDraw(); } }
    }
    document.querySelectorAll('.wz-game').forEach((b) => b.classList.toggle('fav', wzSides(b.dataset.game).includes(wzP.team)));
  }
  function wzShow(mode) {
    wzMode = mode;
    wzDlg.querySelectorAll('.wz-mode').forEach((m) => { m.hidden = m.dataset.mode !== mode; });
    const H = { signup: wzP ? 'Your Wedge account' : 'Create your Wedge account', login: 'Welcome back', account: 'Your Wedge account', done: 'You’re all set' };
    const S = { signup: 'Pick a plan. You can change it any time.', login: '', account: '', done: '' };
    if (!WZ_ACCOUNTS) { H.signup = 'Join Wedge Pro'; S.signup = 'Pick a plan. Checkout comes next.'; }
    $('#wz-dlg-h').textContent = H[mode]; const sub = $('#wz-dlg-sub'); sub.textContent = S[mode]; sub.hidden = !S[mode];
    if (mode === 'signup') {
      $('#wz-f-first').value = (wzP && wzP.first) || wzMe || ''; $('#wz-f-email').value = (wzP && wzP.email) || ''; $('#wz-f-team').value = (wzP && wzP.team) || '';
      wzPick(wzPlan); $('#wz-msg').textContent = '';
    }
    if (mode === 'account' && wzP) {
      const dl = $('#wz-acct-dl'); const row = (a, b) => { const d = el('div'); d.append(el('dt', null, a), el('dd', null, b)); return d; };
      dl.replaceChildren(row('Name', wzP.first || '—'), row('Email', wzP.email || '—'), row('Plan', WZ_PLANS[wzP.plan][0] + (wzP.plan !== 'free' && wzP.status !== 'active' ? ' · checkout pending' : '')),
        row('Favorite team', wzP.team ? wzTeam(wzP.team)[0] + ' (' + wzP.team + ')' : '—'));
      $('#wz-upgrade').hidden = wzP.plan !== 'free'; wzDelArm = false; $('#wz-delete').textContent = 'Delete my account';
    }
  }
  function wzOpen(mode) { wzShow(mode); if (!wzDlg.open) { try { wzDlg.showModal(); } catch (e) { wzDlg.setAttribute('open', ''); } } setTimeout(() => { const f = wzDlg.querySelector('.wz-mode:not([hidden]) input, .wz-mode:not([hidden]) .wz-btn'); if (f) f.focus(); }, 40); }
  function wzClose() { try { wzDlg.close(); } catch (e) { wzDlg.removeAttribute('open'); } }
  function wzPick(plan) {
    wzPlan = plan;
    wzDlg.querySelectorAll('.wz-planpick [data-plan]').forEach((b) => { const on = b.dataset.plan === plan; b.setAttribute('aria-checked', on ? 'true' : 'false'); b.tabIndex = on ? 0 : -1; });
    $('#wz-go').textContent = plan === 'free' ? (wzP ? 'Save my account' : 'Create my account') : 'Continue to checkout';
  }
  function wzCheckout(plan, p) {
    const link = $('#wz-done-link'), url = WZ_CHECKOUT[plan];
    if (url) {
      link.href = url; link.textContent = 'Open checkout again'; link.hidden = false;
      $('#wz-done-text').textContent = `Checkout for ${WZ_PLANS[plan][0]} (${WZ_PLANS[plan][1]}) opened in a new tab. Finish there and your access is set up.`;
    } else {
      const sub = `Wedge membership: ${WZ_PLANS[plan][0]} for ${p.first}`;
      const body = `Plan: ${WZ_PLANS[plan][0]} (${WZ_PLANS[plan][1]})\nName: ${p.first}\nEmail: ${p.email}\nFavorite team: ${p.team || 'none'}\n\nSent from the Wedge membership checkout.`;
      link.href = 'mailto:' + WEDGER_EMAIL + '?subject=' + encodeURIComponent(sub) + '&body=' + encodeURIComponent(body); link.textContent = 'Open the email again'; link.hidden = false;
      $('#wz-done-text').textContent = `Your email app opened with your ${WZ_PLANS[plan][0]} request filled in. Hit send and we'll reply with checkout and your access.`;
    }
    wzShow('done');
    try { link.click(); } catch (e) { /* the link stays for the visitor */ }
  }
  async function wzSubmit() {
    const msg = $('#wz-msg'); msg.textContent = '';
    const f = $('#wz-f-first'), e = $('#wz-f-email'); [f, e].forEach((x) => x.removeAttribute('aria-invalid'));
    const first = f.value.trim(), email = e.value.trim(), team = $('#wz-f-team').value;
    if (!first) { f.setAttribute('aria-invalid', 'true'); f.focus(); msg.textContent = 'Please add your first name.'; return; }
    if (!EMAIL_RE.test(email)) { e.setAttribute('aria-invalid', 'true'); e.focus(); msg.textContent = 'Please enter a valid email address.'; return; }
    if (!WZ_ACCOUNTS) { if (wzPlan === 'free') wzPlan = 'monthly'; wzCheckout(wzPlan, { first, email, team }); return; }
    const was = wzP; const now = new Date().toISOString();
    const keepActive = was && was.plan === wzPlan && was.status === 'active';
    const p = { first, email, team, plan: wzPlan, status: wzPlan === 'free' || keepActive ? 'active' : 'pending', created: (was && was.created) || now, updated: now };
    const ok = await wzSave(p);
    wzHeader(); wzPersonalize();
    if (wzPlan !== 'free' && !keepActive) { wzCheckout(wzPlan, p); return; }
    $('#wz-done-link').hidden = true;
    $('#wz-done-text').textContent = (was ? 'Your details are saved.' : `Welcome to Wedge, ${first}.`) + (ok ? '' : ' (Saved for this visit only.)') + (team ? ` The lobby now opens on ${wzTeam(team)[0]}'s game.` : '');
    wzShow('done');
  }
  function wzJoin(plan) {
    if (!WZ_ACCOUNTS && plan === 'free') { const t = $('#wz-reads'); if (t) t.scrollIntoView({ behavior: WZ_REDUCE ? 'auto' : 'smooth', block: 'start' }); return; }
    wzPlan = plan || 'monthly';
    if (wzP && wzP.email && plan !== 'free') {
      if (wzP.plan === plan && wzP.status === 'active') { wzOpen('account'); return; }
      const p = Object.assign({}, wzP, { plan, status: 'pending', updated: new Date().toISOString() });
      wzSave(p).then(() => wzHeader());
      wzOpen('done'); wzCheckout(plan, p); return;
    }
    if (wzP && plan === 'free') { wzOpen('account'); return; }
    wzOpen('signup');
  }
  $('#wz-login').addEventListener('click', () => wzOpen(wzP ? 'account' : 'login'));
  $('#wz-signup').addEventListener('click', () => { wzPlan = 'monthly'; wzOpen('signup'); });
  $('#wz-me').addEventListener('click', () => wzOpen('account'));
  $('#wz-dlg-x').addEventListener('click', wzClose);
  $('#wz-done-ok').addEventListener('click', wzClose);
  $('#wz-go').addEventListener('click', wzSubmit);
  $('#wz-upgrade').addEventListener('click', () => { wzPlan = 'monthly'; wzShow('signup'); });
  $('#wz-delete').addEventListener('click', async () => {
    const b = $('#wz-delete');
    if (!wzDelArm) { wzDelArm = true; b.textContent = 'Select again to delete'; return; }
    if (wzRef) { try { await wzRef.delete(); } catch (e) { /* keep going */ } }
    try { localStorage.removeItem('wedge-account'); } catch (e) { /* storage unavailable */ }
    wzP = null; wzHeader(); wzClose();
  });
  wzDlg.addEventListener('click', (e) => { if (e.target === wzDlg) wzClose(); });
  wzDlg.querySelectorAll('[data-wz-to]').forEach((b) => b.addEventListener('click', () => wzShow(b.dataset.wzTo)));
  const wzPickBtns = [...wzDlg.querySelectorAll('.wz-planpick [data-plan]')];
  wzPickBtns.forEach((b, i) => {
    b.addEventListener('click', () => wzPick(b.dataset.plan));
    b.addEventListener('keydown', (e) => { if (!['ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp'].includes(e.key)) return; e.preventDefault(); const n = wzPickBtns[(i + (/Right|Down/.test(e.key) ? 1 : wzPickBtns.length - 1)) % wzPickBtns.length]; wzPick(n.dataset.plan); n.focus(); });
  });
  ['#wz-f-first', '#wz-f-email'].forEach((sel) => $(sel).addEventListener('keydown', (e) => { if (e.key === 'Enter') wzSubmit(); }));
  document.querySelectorAll('[data-wz-join]').forEach((b) => b.addEventListener('click', () => wzJoin(b.dataset.wzJoin)));
  document.querySelectorAll('[data-wz-jump]').forEach((b) => b.addEventListener('click', () => { const t = document.getElementById(b.dataset.wzJump); if (t) t.scrollIntoView({ behavior: WZ_REDUCE ? 'auto' : 'smooth', block: 'start' }); }));

  // tables: simple columns by default, extra filters folded away
  const WZ_DETAIL = {
    'lines-table': ['kickoff', 'market', 'source', 'yes_bid', 'role', 'mom_type', 'hits', 'games', 'sample', 'season_results', 'flags'],
    'rc': ['kickoff', 'market', 'pos', 'team', 'team_ml', 'opp_rank_vs_pos', 'source', 'role', 'mom_type', 'hits', 'games', 'season_results', 'flags'],
    'proj-table': ['kickoff', 'pos', 'team', 'p_over', 'mom_p', 'role', 'mom_type', 'games', 'flags'],
    'atd-table': ['pos', 'team', 'kickoff', 'source', 'atd_hits', 'games', 'rz_opps_pg', 'rz_tgt_share', 'rate_minus_price', 'td_log', 'flags'],
    'nba-table': ['kickoff', 'market', 'yes_bid', 'book_fair', 'hits', 'games', 'sample', 'season_results', 'flags'],
  };
  const WZ_FOLD = '.rs-src, .rs-group, .rs-mom, .rs-role, .rc-role, .rc-mom, .nb-group, .nb-mkt';
  let wzDetailed = false; try { wzDetailed = localStorage.getItem('wedge-cols') === 'all'; } catch (e) { /* storage unavailable */ }
  function wzTables() {
    const css = [], toggles = [];
    for (const t of document.querySelectorAll('table.rs-table')) {
      const key = WZ_DETAIL[t.id] ? t.id : (t.classList.contains('rc-table') ? 'rc' : null); if (!key || !t.id || !t.tHead) continue;
      [...t.tHead.rows[0].cells].forEach((th, i) => { if (WZ_DETAIL[key].includes(th.dataset.field)) css.push(`#${t.id}.wz-simple > thead > tr > :nth-child(${i + 1}), #${t.id}.wz-simple > tbody > tr > :nth-child(${i + 1})`); });
      t.classList.toggle('wz-simple', !wzDetailed);
      const card = t.closest('.rs-card'), ctr = card && card.querySelector('.rs-controls'); if (!ctr || ctr.querySelector('.wz-cols')) continue;
      const fold = [...ctr.children].filter((c) => c.matches(WZ_FOLD) || (c.tagName === 'LABEL' && c.querySelector('input[type="checkbox"]')));
      if (fold.length) {
        const d = el('details', 'wz-filters'), sm = el('summary', null, 'More filters'), inner = el('div', 'wz-filters-in');
        d.append(sm, inner); fold.forEach((c) => inner.append(c));
        const upd = () => { const n = fold.filter((c) => (c.tagName === 'SELECT' ? !!c.value : !!(c.querySelector('input') || {}).checked)).length; const old = sm.querySelector('b'); if (old) old.remove(); if (n) sm.append(el('b', null, String(n))); };
        inner.addEventListener('change', upd);
        const cnt = ctr.querySelector('.rs-count'); ctr.insertBefore(d, cnt || null);
      }
      const b = el('button', 'wz-btn wz-btn-line wz-btn-sm wz-cols'); b.type = 'button'; b.setAttribute('aria-pressed', wzDetailed ? 'true' : 'false'); b.textContent = wzDetailed ? 'Fewer columns' : 'More columns';
      b.addEventListener('click', () => { wzDetailed = !wzDetailed; try { localStorage.setItem('wedge-cols', wzDetailed ? 'all' : 'simple'); } catch (e) { /* storage unavailable */ } document.querySelectorAll('table.rs-table').forEach((x) => { if (x.dataset.wzs) x.classList.toggle('wz-simple', !wzDetailed); }); toggles.forEach((x) => { x.textContent = wzDetailed ? 'Fewer columns' : 'More columns'; x.setAttribute('aria-pressed', wzDetailed ? 'true' : 'false'); }); });
      toggles.push(b); ctr.append(b); t.dataset.wzs = '1';
    }
    const st = document.createElement('style'); st.textContent = css.length ? css.join(',\n') + ' { display: none; }' : ''; document.head.append(st);
    document.addEventListener('click', (e) => { document.querySelectorAll('details.wz-filters[open]').forEach((d) => { if (!d.contains(e.target)) d.open = false; }); });
  }
  // a touchdown line names only the player; with the market column folded away, say which market it is
  function wzLabel(r) { const lab = rhLabel(r.contract); return /:/.test(lab) || !/Touchdown/i.test(r.market || '') ? lab : lab + ' · ' + (r.market === 'Anytime Touchdown' ? 'anytime TD' : String(r.market).replace(/Touchdowns?/i, 'TDs')); }
  function wzInj(cell, flags) {
    const f = String(flags || ''); const m = /Injury report: (Questionable|Doubtful|Out|Limited in practice)/.exec(f); if (!m) return;
    const t = el('span', 'wz-inj', m[1] === 'Limited in practice' ? 'LTD' : m[1].slice(0, 1)); t.title = f; t.setAttribute('aria-label', 'Injury report: ' + m[1]); cell.append(t);
  }

  // motion: reveal, ripple, spotlight
  function wzMotion() {
    const paper = $('.wg-paper'); if (paper) paper.classList.add('wz-js');
    const rv = [...document.querySelectorAll('.wz-reveal')];
    if (WZ_REDUCE || !('IntersectionObserver' in window)) rv.forEach((x) => x.classList.add('wz-in'));
    else { const io = new IntersectionObserver((es) => es.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('wz-in'); io.unobserve(en.target); } }), { rootMargin: '0px 0px -8% 0px', threshold: 0.06 }); rv.forEach((x) => io.observe(x)); }
    if (WZ_REDUCE) return;
    document.addEventListener('pointerdown', (e) => {
      const t = e.target.closest('.wz-btn, .wx-tab, .wz-game, .wz-planpick button, .wz-me'); if (!t) return;
      const r = t.getBoundingClientRect(), d = Math.max(r.width, r.height) * 2.2, sp = document.createElement('span');
      sp.className = 'wz-ripple'; sp.style.width = sp.style.height = d + 'px'; sp.style.left = (e.clientX - r.left - d / 2) + 'px'; sp.style.top = (e.clientY - r.top - d / 2) + 'px';
      if (getComputedStyle(t).position === 'static') t.style.position = 'relative';
      t.style.overflow = 'hidden'; t.append(sp); sp.addEventListener('animationend', () => sp.remove());
    });
    document.addEventListener('pointermove', (e) => {
      const t = e.target.closest && e.target.closest('.wz-spot'); if (!t) return;
      const r = t.getBoundingClientRect(); t.style.setProperty('--mx', (e.clientX - r.left) + 'px'); t.style.setProperty('--my', (e.clientY - r.top) + 'px');
    }, { passive: true });
  }
  // the NFL menu opens under its tab (the tab row scrolls sideways, so the menu is placed against the header)
  $('#nfl-btn').addEventListener('click', () => { const m = $('#nfl-menu'), t = $('.wz-top'), b = $('#nfl-btn'); if (!m || !t || !b) return; m.style.left = Math.max(8, b.getBoundingClientRect().left - t.getBoundingClientRect().left) + 'px'; });
  // the old membership page is replaced by the plans on the lobby
  document.querySelectorAll('[data-go="unlock"]').forEach((b) => { b.dataset.go = 'lobby'; b.dataset.scrollAfter = 'wz-plans'; });
  if (!WZ_ACCOUNTS) {
    const fp = wzDlg.querySelector('.wz-planpick [data-plan="free"]'); if (fp) fp.hidden = true;
    const pp = wzDlg.querySelector('.wz-planpick'); if (pp) pp.style.gridTemplateColumns = 'repeat(2, minmax(0, 1fr))';
    const fine = wzDlg.querySelector('.wz-mode[data-mode="signup"] .wz-dlg-fine'); if (fine) fine.textContent = 'Paid plans go straight to checkout.';
    document.querySelectorAll('[data-wz-join="free"]').forEach((b) => { b.textContent = 'Start browsing'; });
  }
  wzTables(); wzMotion(); wzInitAccount();
'''
rep('\n  // ---------------- render ----------------\n  dash.onData(() => {', JS + '\n  // ---------------- render ----------------\n  dash.onData(() => {')

open(B + 'index.html', 'w').write(s)
print('w9d ok', len(s))
