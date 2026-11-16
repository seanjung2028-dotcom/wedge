"""Wedger brand v2 (Tue Nov 3 evening): logo colors everywhere (no more off-brand mint), a validated chart palette led by
wedge green, a photo-led Polymarket-style lobby (hero carousel, ticker, market cards, sport tiles, receipts), photo banners
on the inner pages, and humor hooks. Runs after patch_w9.py, before gen_page.py."""
import json
B = '/home/claude/wedger/rh/'
s = open(B + 'page_template.html').read()
BL = {k: '/_blob/' + v for k, v in json.load(open('/home/claude/wedger/photos/blob_map.json')).items()}
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, (old[:100], c); s = s.replace(old, new)

# ---------- 1. colors: logo green everywhere, text-safe ink, dark ink = logo lime ----------
rep('#00BF63', '#00BC5C', 12)
rep('#4fe39a', '#7ED957', 2)
rep(".wg-paper { --wg-ink: color-mix(in srgb, #00BC5C 62%, #000); }", ".wg-paper { --wg-ink: #00793D; }")

CSS = r'''
  /* ---------- Wedger brand v2 ----------
     Layout: photo-led lobby (hero carousel, ticker, this week's wedges, sport tiles, receipts); inner pages open on a photo banner.
     Color: wedge green and wedge lime from the logo, forest for photo shade, penalty-flag yellow for jokes. */
  .wg-paper {
    --wg-green: #00BC5C; --wg-lime: #7ED957; --wg-forest: #04241A; --wg-flag: #F5C400;
    --wg-ink: #00793D; --wg-no-ink: #B23F2A;
    --wg-on-photo: #FFFFFF; --wg-on-photo-muted: rgba(234, 247, 228, .84); --wg-photo-line: rgba(255, 255, 255, .34);
    --wg-c1: #00A85A; --wg-c2: #2F6FD0; --wg-c3: #EB6834; --wg-c4: #8B5CD6;
    --wg-display: "Archivo", "Arial Narrow", "Helvetica Neue", system-ui, sans-serif;
    --color-ok: var(--wg-ink);
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) .wg-paper { --wg-ink: #7ED957; --wg-no-ink: #FF9F8C; --wg-c1: #10AE5F; --wg-c2: #4B86E0; --wg-c3: #D9682C; --wg-c4: #9A6DE0; }
  }
  :root[data-theme="dark"] .wg-paper { --wg-ink: #7ED957; --wg-no-ink: #FF9F8C; --wg-c1: #10AE5F; --wg-c2: #4B86E0; --wg-c3: #D9682C; --wg-c4: #9A6DE0; }

  .wg-lobby { gap: clamp(22px, 3vw, 34px); }
  .wg-eyebrow { margin: 0; font-family: var(--wg-display); font-weight: 700; font-size: 12px; line-height: 1.2; letter-spacing: .12em; text-transform: uppercase; }

  /* hero carousel */
  .wg-hx { position: relative; isolation: isolate; display: grid; border-radius: 22px; overflow: hidden; background: var(--wg-forest); color: var(--wg-on-photo); min-height: clamp(380px, 44vw, 480px); }
  .wg-hx-slide { grid-area: 1 / 1; position: relative; isolation: isolate; display: flex; align-items: flex-end; min-width: 0; opacity: 0; visibility: hidden; transition: opacity .7s ease, visibility 0s linear .7s; }
  .wg-hx-slide.is-on { opacity: 1; visibility: visible; transition: opacity .7s ease; }
  .wg-hx-photo { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -3; }
  .wg-hx-shade { position: absolute; inset: 0; z-index: -2; background:
      linear-gradient(90deg, color-mix(in srgb, var(--wg-forest) 95%, transparent) 0%, color-mix(in srgb, var(--wg-forest) 78%, transparent) 40%, color-mix(in srgb, var(--wg-forest) 10%, transparent) 80%),
      linear-gradient(0deg, color-mix(in srgb, var(--wg-forest) 75%, transparent), transparent 60%); }
  .wg-hx-wedge { position: absolute; right: 0; bottom: 0; top: 0; width: clamp(150px, 24%, 280px); z-index: -1; background: var(--wg-lime); clip-path: polygon(100% 0, 100% 100%, 0 100%); }
  .wg-hx-stat { position: absolute; right: clamp(14px, 2vw, 24px); bottom: clamp(14px, 2vw, 22px); display: flex; flex-direction: column; align-items: flex-end; text-align: right; gap: 2px; color: var(--wg-forest); max-width: 11rem; }
  .wg-hx-stat b { font-family: var(--wg-display); font-weight: 900; font-stretch: 112%; font-size: clamp(30px, 4vw, 46px); line-height: .95; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }
  .wg-hx-stat span { font-size: 12px; font-weight: 600; line-height: 1.3; }
  .wg-hx-copy { display: flex; flex-direction: column; align-items: flex-start; gap: 12px; padding: clamp(22px, 4.2vw, 52px); padding-right: clamp(22px, 26%, 300px); max-width: 100%; box-sizing: border-box; min-width: 0; }
  .wg-hx-copy .wg-eyebrow { color: var(--wg-lime); }
  .wg-hx-title { margin: 0; font-family: var(--wg-display); font-weight: 800; font-stretch: 112%; font-size: clamp(36px, 5.8vw, 68px); line-height: .96; letter-spacing: -0.025em; text-wrap: balance; color: var(--wg-on-photo); max-width: 13ch; }
  .wg-hx-title em { font-style: normal; color: var(--wg-lime); }
  .wg-hx-sub { margin: 0; max-width: 34rem; font-size: 15px; line-height: 1.55; color: var(--wg-on-photo-muted); }
  .wg-hx .wg-hero-mark { width: min(230px, 56vw); }
  .wg-hx .wg-hero-desc { color: var(--wg-on-photo-muted); max-width: 34rem; }
  .wg-hx .wg-profit-pct { color: var(--wg-on-photo); }
  .wg-hx .wg-profit-pct.wg-pos { color: var(--wg-lime); }
  .wg-hx .wg-profit-pct.wg-neg { color: #FF9F8C; }
  .wg-hx-go { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 4px; }
  .wg-hx .wg-go:not(.wg-go-primary) { background: transparent; color: var(--wg-on-photo); border-color: var(--wg-photo-line); }
  .wg-hx .wg-go:not(.wg-go-primary):hover { background: rgba(255, 255, 255, .12); border-color: var(--wg-on-photo); }
  .wg-hx-dots { position: absolute; top: 18px; left: clamp(22px, 4.2vw, 52px); display: flex; gap: 6px; z-index: 2; }
  .wg-hx-dot { all: unset; cursor: pointer; width: 30px; height: 18px; display: grid; align-items: center; }
  .wg-hx-dot::before { content: ''; height: 4px; border-radius: 2px; background: var(--wg-photo-line); background-image: linear-gradient(var(--wg-lime), var(--wg-lime)); background-repeat: no-repeat; background-size: 0 100%; }
  .wg-hx-dot[aria-current="true"]::before { background-size: 100% 100%; }
  .wg-hx-dot:focus-visible { outline: 2px solid var(--wg-lime); outline-offset: 2px; border-radius: 3px; }
  @media (prefers-reduced-motion: no-preference) {
    .wg-hx.is-auto .wg-hx-dot[aria-current="true"]::before { animation: wgDotFill 7s linear both; }
    .wg-hx-slide.is-on .wg-hx-photo { animation: wgKen 9s ease-out both; }
  }
  @keyframes wgDotFill { from { background-size: 0 100%; } to { background-size: 100% 100%; } }
  @keyframes wgKen { from { transform: scale(1.06); } to { transform: scale(1); } }
  @media (max-width: 640px) {
    .wg-hx-copy { padding-right: clamp(22px, 4.2vw, 52px); padding-top: 56px; padding-bottom: 116px; }
    .wg-hx-wedge { width: 96px; height: 96px; bottom: auto; clip-path: polygon(0 0, 100% 0, 100% 100%); }
    .wg-hx-stat { left: 22px; right: 22px; bottom: 20px; max-width: none; flex-direction: row; align-items: center; justify-content: flex-start; gap: 12px; text-align: left; padding: 10px 14px; border-radius: 14px; background: var(--wg-lime); }
    .wg-hx-stat b { font-size: 28px; flex: none; }
  }

  /* ticker */
  .wg-tick { overflow: hidden; border-radius: 14px; background: var(--wg-forest); color: var(--wg-on-photo); border: 1px solid color-mix(in srgb, var(--wg-green) 45%, transparent);
    -webkit-mask-image: linear-gradient(90deg, transparent, #000 4%, #000 96%, transparent); mask-image: linear-gradient(90deg, transparent, #000 4%, #000 96%, transparent); }
  .wg-tick-run { display: flex; width: max-content; gap: 30px; padding: 11px 24px; }
  .wg-tick-item { display: inline-flex; gap: 8px; align-items: baseline; white-space: nowrap; font-size: 13px; }
  .wg-tick-item b { font-family: var(--wg-display); font-weight: 700; letter-spacing: .01em; }
  .wg-tick-item .y { color: var(--wg-lime); font-weight: 600; } .wg-tick-item .n { color: #FF9F8C; font-weight: 600; }
  .wg-tick-joke { color: var(--wg-flag); font-weight: 600; }
  @media (prefers-reduced-motion: no-preference) {
    .wg-tick.is-live .wg-tick-run { animation: wgTick 70s linear infinite; }
    .wg-tick:hover .wg-tick-run, .wg-tick:focus-within .wg-tick-run { animation-play-state: paused; }
  }
  @media (prefers-reduced-motion: reduce) { .wg-tick { overflow-x: auto; } }
  @keyframes wgTick { to { transform: translateX(-50%); } }

  /* section heads */
  .wg-sec { display: flex; flex-direction: column; gap: 14px; min-width: 0; }
  .wg-sec-head { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: 10px 16px; }
  .wg-sec-title { margin: 0; font-family: var(--wg-display); font-weight: 800; font-stretch: 108%; font-size: clamp(22px, 2.6vw, 30px); line-height: 1.1; letter-spacing: -0.015em; color: var(--color-fg); }
  .wg-sec-sub { margin: 4px 0 0; color: var(--color-fg-muted); font-size: 13.5px; line-height: 1.5; max-width: 44rem; }

  /* market cards */
  .wg-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr)); gap: 14px; }
  .wg-mk { all: unset; box-sizing: border-box; cursor: pointer; display: flex; flex-direction: column; gap: 12px; padding: 14px; min-width: 0; border-radius: 16px; background: var(--color-panel); border: 1px solid var(--color-border-line); transition: transform .15s ease, border-color .15s ease, box-shadow .15s ease; }
  .wg-mk:hover { transform: translateY(-2px); border-color: color-mix(in srgb, var(--wg-green) 55%, var(--color-border-line)); box-shadow: 0 12px 26px color-mix(in srgb, var(--wg-forest) 16%, transparent); }
  .wg-mk:focus-visible { outline: 2px solid var(--wg-green); outline-offset: 2px; }
  .wg-mk-top { display: grid; grid-template-columns: 48px minmax(0, 1fr) 74px; gap: 12px; align-items: center; }
  .wg-mk-img { width: 48px; height: 48px; border-radius: 10px; object-fit: cover; background: var(--wg-forest); }
  .wg-mk-q { display: flex; flex-direction: column; gap: 3px; min-width: 0; }
  .wg-mk-q b { font-weight: 600; font-size: 14.5px; line-height: 1.3; color: var(--color-fg); overflow-wrap: anywhere; }
  .wg-mk-q small { font-size: 12px; color: var(--color-fg-muted); }
  .wg-mk-gauge { position: relative; width: 74px; height: 52px; }
  .wg-mk-gauge svg { position: absolute; inset: 0 0 auto; width: 74px; height: 42px; overflow: visible; }
  .wg-mk-gauge .trk { fill: none; stroke: var(--cds-chart-grid); stroke-width: 6; stroke-linecap: round; }
  .wg-mk-gauge .val { fill: none; stroke: var(--wg-green); stroke-width: 6; stroke-linecap: round; }
  .wg-mk-gauge.no .val { stroke: var(--wg-bear); }
  .wg-mk-gauge b { position: absolute; left: 0; right: 0; top: 21px; text-align: center; font-family: var(--wg-display); font-weight: 800; font-size: 17px; line-height: 1; font-variant-numeric: tabular-nums; color: var(--color-fg); }
  .wg-mk-gauge small { position: absolute; left: 0; right: 0; bottom: 0; text-align: center; font-size: 10.5px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: var(--color-fg-muted); }
  .wg-mk-px { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
  .wg-px { display: flex; justify-content: space-between; align-items: center; gap: 6px; padding: 9px 12px; border-radius: 10px; font-size: 13.5px; font-weight: 600; font-variant-numeric: tabular-nums; }
  .wg-px.yes { background: color-mix(in srgb, var(--wg-green) 13%, transparent); color: var(--wg-ink); }
  .wg-px.no { background: color-mix(in srgb, var(--wg-bear) 13%, transparent); color: var(--wg-no-ink); }
  .wg-px.is-pick { box-shadow: inset 0 0 0 2px currentColor; }
  .wg-px.is-pick span::after { content: ' · Wedger'; font-weight: 500; opacity: .8; }
  .wg-mk-foot { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; font-size: 12px; color: var(--color-fg-muted); }
  .wg-mk-pick { font-weight: 600; color: var(--color-fg); white-space: nowrap; }
  .wg-mk-joke { font-style: italic; text-align: right; }
  .wg-cards-empty { margin: 0; padding: 18px; border: 1px dashed var(--color-border-line); border-radius: 14px; color: var(--color-fg-muted); font-size: 13px; }

  /* sport tiles */
  .wg-sports { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 260px), 1fr)); gap: 14px; }
  .wg-sport { all: unset; box-sizing: border-box; cursor: pointer; position: relative; isolation: isolate; overflow: hidden; min-height: 200px; padding: 18px; border-radius: 18px; display: flex; flex-direction: column; justify-content: flex-end; gap: 4px; color: var(--wg-on-photo); background: var(--wg-forest); }
  .wg-sport img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; transition: transform .5s ease; }
  .wg-sport::after { content: ''; position: absolute; inset: 0; z-index: -1; background: linear-gradient(0deg, color-mix(in srgb, var(--wg-forest) 94%, transparent) 8%, color-mix(in srgb, var(--wg-forest) 20%, transparent) 72%); }
  .wg-sport:hover img { transform: scale(1.05); }
  .wg-sport:focus-visible { outline: 2px solid var(--wg-green); outline-offset: 3px; }
  .wg-sport b { font-family: var(--wg-display); font-weight: 900; font-stretch: 112%; font-size: 32px; line-height: 1; letter-spacing: -0.02em; }
  .wg-sport small { font-size: 13px; color: var(--wg-on-photo-muted); }
  .wg-sticker { position: absolute; top: 14px; left: 14px; padding: 5px 10px; border-radius: 999px; background: var(--wg-flag); color: var(--wg-forest); font-size: 12px; font-weight: 700; line-height: 1.2; transform: rotate(-2deg); box-shadow: 0 2px 0 color-mix(in srgb, var(--wg-forest) 35%, transparent); }

  /* receipts */
  .wg-receipts { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr)); gap: 14px; }
  .wg-rcpt { display: flex; flex-direction: column; gap: 6px; padding: 18px; border-radius: 16px; background: var(--color-panel); border: 1px dashed color-mix(in srgb, var(--wg-green) 45%, var(--color-border-line)); min-width: 0; }
  .wg-rcpt i { font-style: normal; font-size: 11px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--wg-ink); }
  .wg-rcpt b { font-family: var(--wg-display); font-weight: 800; font-stretch: 108%; font-size: clamp(30px, 3.4vw, 40px); line-height: 1; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; color: var(--color-fg); }
  .wg-rcpt span { font-size: 13px; line-height: 1.45; color: var(--color-fg-muted); }
  .wg-fine { margin: 0; font-size: 12px; line-height: 1.55; color: var(--color-fg-muted); max-width: 60rem; }

  /* inner-page photo banners */
  .wg-pb { position: relative; isolation: isolate; overflow: hidden; min-height: 156px; padding: clamp(18px, 3vw, 28px); padding-right: clamp(18px, 12vw, 150px); border-radius: 18px; display: flex; flex-direction: column; justify-content: flex-end; gap: 6px; color: var(--wg-on-photo); background: var(--wg-forest); }
  .wg-pb-photo { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -3; }
  .wg-pb::after { content: ''; position: absolute; inset: 0; z-index: -2; background: linear-gradient(90deg, color-mix(in srgb, var(--wg-forest) 94%, transparent) 0%, color-mix(in srgb, var(--wg-forest) 62%, transparent) 55%, color-mix(in srgb, var(--wg-forest) 10%, transparent) 100%); }
  .wg-pb::before { content: ''; position: absolute; right: 0; top: 0; bottom: 0; width: clamp(56px, 9vw, 96px); z-index: -1; background: var(--wg-lime); clip-path: polygon(100% 0, 100% 100%, 0 100%); }
  .wg-pb .wg-eyebrow { color: var(--wg-lime); }
  .wg-pb-title { margin: 0; font-family: var(--wg-display); font-weight: 800; font-stretch: 110%; font-size: clamp(28px, 3.8vw, 42px); line-height: 1; letter-spacing: -0.02em; color: var(--wg-on-photo); }
  .wg-pb-sub { margin: 0; max-width: 46rem; font-size: 14px; line-height: 1.5; color: var(--wg-on-photo-muted); }
  .wg-pb .wg-sticker { left: auto; right: clamp(70px, 10vw, 112px); top: 16px; transform: rotate(2deg); }
  @media (max-width: 560px) { .wg-pb .wg-sticker { position: static; align-self: flex-start; margin-bottom: 6px; order: -1; } }
'''
i = s.index('</style>'); s = s[:i] + CSS + s[i:]
s = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,500..900&display=swap">\n' + s

# ---------- 2. lobby ----------
i = s.index('    <section class="wg-hero" aria-labelledby="hero-title">'); j = s.index('</section>', i) + len('</section>')
GO = '''<div class="wg-hx-go">
            <button type="button" class="wg-go wg-go-primary" data-go="lines">See Week 9 lines</button>
            <button type="button" class="wg-go wg-unlock-btn" data-go="unlock"><svg class="wg-lock" viewBox="0 0 16 16" aria-hidden="true"><rect x="3" y="7" width="10" height="7.5" rx="1.6" fill="currentColor"/><path d="M5.4 7V4.9a2.6 2.6 0 0 1 5.1-.8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>Unlock</button>
          </div>'''
LOBBY = f'''    <section class="wg-hx" aria-roledescription="carousel" aria-label="Wedger this week">
      <h2 class="wg-visually-hidden" id="hero-title">Wedger</h2>
      <div class="wg-hx-dots" role="group" aria-label="Choose a slide">
        <button type="button" class="wg-hx-dot" aria-label="Slide 1: Let's flip for it" aria-current="true"></button>
        <button type="button" class="wg-hx-dot" aria-label="Slide 2: Passing overs" aria-current="false"></button>
        <button type="button" class="wg-hx-dot" aria-label="Slide 3: The receipts" aria-current="false"></button>
      </div>
      <article class="wg-hx-slide is-on" aria-roledescription="slide" aria-label="1 of 3">
        <img class="wg-hx-photo" src="{BL['hero_night']}" alt="Stadium floodlights at night" width="1600" height="1000">
        <span class="wg-hx-shade" aria-hidden="true"></span><span class="wg-hx-wedge" aria-hidden="true"></span>
        <div class="wg-hx-stat"><b>45–55¢</b><span>Every line on the board. Coin flips, priced.</span></div>
        <div class="wg-hx-copy">
          <div class="wg-hero-mark" role="img" aria-label="Wedger logo">
            <img class="wg-hero-tri" alt="" src="/_blob/0343890db162cebaef69169009468273">
            <img class="wg-hero-letters" alt="" src="/_blob/17e72076470b258f8b23a2bfba6065a6">
            <span class="wg-hero-shine" aria-hidden="true"></span>
          </div>
          <p class="wg-hx-title">Let's flip <em>for it.</em></p>
          <p class="wg-hx-sub">Wedger checks every Robinhood line priced like a coin flip and tells you which side of the coin is heavier.</p>
          <p class="wg-hero-desc" id="wg-profit" data-source="results" aria-live="polite">Net profit on Wedger-certified picks so far: —</p>
          {GO}
        </div>
      </article>
      <article class="wg-hx-slide" aria-roledescription="slide" aria-label="2 of 3" aria-hidden="true">
        <img class="wg-hx-photo" src="{BL['hero_ball']}" alt="A football on the turf at the yard line" width="1600" height="900" loading="lazy">
        <span class="wg-hx-shade" aria-hidden="true"></span><span class="wg-hx-wedge" aria-hidden="true"></span>
        <div class="wg-hx-stat"><b>62%</b><span>Passing-yard overs that came true at about 50¢, Weeks 6–8</span></div>
        <div class="wg-hx-copy">
          <p class="wg-eyebrow">Week 9 · model v5</p>
          <p class="wg-hx-title">Passing overs are <em>so back.</em></p>
          <p class="wg-hx-sub">Rushing overs at the same price came true 39–42% of the time. It's so over. Wedger % now prices both in, line by line.</p>
          <div class="wg-hx-go">
            <button type="button" class="wg-go wg-go-primary" data-go="lines" data-wg-show="pick">See this week's picks</button>
            <button type="button" class="wg-go" data-go="charts">How we know</button>
          </div>
        </div>
      </article>
      <article class="wg-hx-slide" aria-roledescription="slide" aria-label="3 of 3" aria-hidden="true">
        <img class="wg-hx-photo" src="{BL['hero_hoop']}" alt="A basketball dropping through the net" width="1600" height="1044" loading="lazy">
        <span class="wg-hx-shade" aria-hidden="true"></span><span class="wg-hx-wedge" aria-hidden="true"></span>
        <div class="wg-hx-stat"><b data-wg-count="settled">1,333</b><span>Lines settled to build this week's model, misses included</span></div>
        <div class="wg-hx-copy">
          <p class="wg-eyebrow">The receipts</p>
          <p class="wg-hx-title">Ball don't lie. <em>Neither do backtests.</em></p>
          <p class="wg-hx-sub">Every pick we post gets settled against the box score, wins and losses alike. The record is on the Charts tab, not in a screenshot.</p>
          <div class="wg-hx-go">
            <button type="button" class="wg-go wg-go-primary" data-go="charts">See the record</button>
            <button type="button" class="wg-go" data-go="analysts">Analysts</button>
          </div>
        </div>
      </article>
    </section>

    <div class="wg-tick" id="wg-tick" aria-label="This week's Wedger leans">
      <div class="wg-tick-run" id="wg-tick-run">
        <span class="wg-tick-item wg-tick-joke">Not financial advice. Just math with a sense of humor.</span>
        <span class="wg-tick-item"><b>Passing-yard overs</b><span class="y">so back</span></span>
        <span class="wg-tick-item"><b>Rushing overs</b><span class="n">so over</span></span>
        <span class="wg-tick-item wg-tick-joke">Sir, this is a prediction market.</span>
      </div>
    </div>

    <section class="wg-sec" aria-labelledby="hot-h">
      <div class="wg-sec-head">
        <div>
          <h2 class="wg-sec-title" id="hot-h">This week's wedges</h2>
          <p class="wg-sec-sub">The biggest gaps between Wedger % and the price on Robinhood's own Week 9 lines, at most two per game. Tap a card for the full outlook.</p>
        </div>
        <button type="button" class="wg-go" data-go="lines" data-wg-show="pick">All <span data-wg-count="picks">19</span> picks</button>
      </div>
      <div class="wg-cards" id="wg-hot-cards"><p class="wg-cards-empty">Loading this week's biggest gaps between Wedger % and the price…</p></div>
    </section>

    <section class="wg-sec" aria-labelledby="sports-h">
      <div class="wg-sec-head"><h2 class="wg-sec-title" id="sports-h">Pick your sport</h2></div>
      <div class="wg-sports">
        <button type="button" class="wg-sport" data-go="lines"><img src="{BL['banner_turf']}" alt="" loading="lazy"><span class="wg-sticker">Tuesday prices, Sunday problems</span><b>NFL</b><small>Week 9 · <span data-wg-count="lines">381</span> lines · <span data-wg-count="picks">19</span> Wedger picks</small></button>
        <button type="button" class="wg-sport" data-go="nba"><img src="{BL['banner_arena']}" alt="" loading="lazy"><span class="wg-sticker">Ball don't lie</span><b>NBA</b><small>The 45–55¢ screen, NBA edition</small></button>
        <button type="button" class="wg-sport" data-go="soccer"><img src="{BL['banner_soccer']}" alt="" loading="lazy"><span class="wg-sticker">It's coming home. Eventually.</span><b>Soccer</b><small>Coming soon</small></button>
      </div>
    </section>

    <section class="wg-sec" aria-labelledby="rcpt-h">
      <div class="wg-sec-head">
        <div>
          <h2 class="wg-sec-title" id="rcpt-h">The receipts</h2>
          <p class="wg-sec-sub">Every 45–55¢ line on Robinhood since Week 1, settled at the price it traded for. Before fees.</p>
        </div>
      </div>
      <div class="wg-receipts">
        <div class="wg-rcpt"><i>Wedger picks, as posted</i><b data-wg-rcpt="picks-rec">248–190</b><span data-wg-rcpt="picks-txt">56.6% won, +4.0% return, Weeks 6–8.</span></div>
        <div class="wg-rcpt"><i>Buying every Yes</i><b data-wg-rcpt="yes-roi">−5.1%</b><span data-wg-rcpt="yes-txt">858–954 since Week 1. We did it so you don't have to.</span></div>
        <div class="wg-rcpt"><i>Passing props</i><b data-wg-rcpt="pass-pct">58.0%</b><span data-wg-rcpt="pass-txt">80–58 at about 50¢. Let him cook.</span></div>
        <div class="wg-rcpt"><i>Rushing props</i><b data-wg-rcpt="rush-pct">40.7%</b><span data-wg-rcpt="rush-txt">98–143 at about 50¢. Touch grass, not the over.</span></div>
      </div>
      <p class="wg-fine">Wedger is research and entertainment, not financial advice. Prices move and picks lose (190 of ours so far), so only stake what you'd spend on nachos. Photos: Unsplash (Daniel van den Berg, Dave Adamson, Markus Spiske, Thomas Park, Ashton Clark, Howard Bouchevereau, Rick Barrett, Logan Weaver, Raymond Petrik).</p>
    </section>'''
s = s[:i] + LOBBY + s[j:]

# ---------- 3. inner-page photo banners ----------
def banner(page, img, eyebrow, title, sub, joke):
    tag = f'  <div class="rs-page" id="{page}" hidden>\n'
    rep(tag, tag + f'''    <header class="wg-pb">
      <img class="wg-pb-photo" src="{BL[img]}" alt="" loading="lazy">
      <span class="wg-sticker">{joke}</span>
      <p class="wg-eyebrow">{eyebrow}</p>
      <h2 class="wg-pb-title">{title}</h2>
      <p class="wg-pb-sub">{sub}</p>
    </header>
''')
banner('lines', 'banner_turf', 'NFL · Week 9', 'Week 9 lines',
       '<span data-wg-count="lines">381</span> coin flips priced 45–55¢, <span data-wg-count="picks">19</span> with a Wedger lean. Priced Tue Nov 3, 6:20 PM CT.',
       "Rushing overs at 50¢? It's so over.")
banner('proj', 'banner_aerial', 'NFL · Week 9', 'Projections',
       "Every starter's main props before the books post them. 3,000 random features, zero vibes.", 'Built different (it’s a ridge regression)')
banner('atd', 'hero_night', 'NFL · Week 9', 'Anytime TD',
       'Red-zone usage, target share and touchdown rates for every player with a price.', 'Six points or bust')
banner('results', 'banner_goal', 'Settled', 'Results',
       'Every line we posted, settled from the final box scores. The wins, the losses and the ones we would rather forget.', 'Receipts, not vibes')
banner('charts', 'banner_sunset', 'Eight weeks of data', 'Charts',
       "Every 45–55¢ line at Robinhood's price, week by week, plus the studies behind the model.", 'Number go up? Sometimes.')
banner('nba', 'banner_arena', 'NBA', 'NBA lines', 'Robinhood’s NBA lines through the same 45–55¢ screen.', "Ball don't lie")
banner('soccer', 'banner_soccer', 'Soccer', 'Soccer', 'Premier League, Champions League and MLS lines are next.', "It's coming home. Eventually.")

# ---------- 4. JS: chart palette, carousel, cards, ticker, receipts, counters ----------
rep("const shine = $('.wg-hero-shine'), mask", "if (!$('.wg-hero-shine')) return;\n    const shine = $('.wg-hero-shine'), mask")
n = s.count('dash.colors'); assert n == 9, n
s = s.replace('dash.colors', 'wgColors()')
rep("    const segs = [...new Set(rows.map((r) => r.segment))];\n    const col = (sg) => wgColors()[segs.indexOf(sg) % wgColors().length];",
    "    const segs = [...new Set(rows.map((r) => r.segment))].sort((a, b) => /Wedger/.test(b) - /Wedger/.test(a));\n    const col = (sg) => wgColors()[segs.indexOf(sg) % wgColors().length];")
JS = r'''
  // ---------------- brand v2: chart palette, lobby carousel, market cards, ticker, receipts ----------------
  function wgColors() {
    const cs = getComputedStyle($('.wg-paper') || document.documentElement);
    return ['--wg-c1', '--wg-c2', '--wg-c3', '--wg-c4'].map((v, i) => cs.getPropertyValue(v).trim() || ['#00A85A', '#2F6FD0', '#EB6834', '#8B5CD6'][i]);
  }
  const WG_T = { pass: '__T_PASS__', rush: '__T_RUSH__', rec: '__T_REC__', td: '__T_TD__' };
  const WG_THUMB = { passyd: WG_T.pass, passtd: WG_T.pass, int: WG_T.pass, rushyd: WG_T.rush, rryd: WG_T.rush, recyd: WG_T.rec, rec: WG_T.rec, td: WG_T.td };
  const WG_JOKE = {
    'passyd|Yes': 'Passing overs: so back.', 'passtd|Yes': 'Let him cook.', 'int|Yes': 'Chaos merchant special.',
    'passyd|No': 'Checkdown city.', 'rushyd|No': 'Rushing overs: so over.', 'rryd|No': 'Running on fumes.',
    'rushyd|Yes': 'Let him cook.', 'recyd|No': 'Ratio’d by the coverage.', 'rec|No': 'Targets aren’t catches.',
    'recyd|Yes': 'Stonks, receiving edition.', 'rec|Yes': 'Volume merchant.', 'td|Yes': 'Paint the end zone.', 'td|No': 'Not in this house.',
  };
  const WG_QUIPS = ['Not financial advice. Just math with a sense of humor.', 'Sir, this is a prediction market.', 'Touch grass, then check the yard lines.',
    'Trust the process (it’s a ridge regression).', 'Stonks only go up. Props, not so much.', 'We’re so back. Unless it’s a rushing over.'];
  const wgFmt = (n) => Number(n).toLocaleString('en-US');
  (() => {
    const hx = $('.wg-hx'); if (!hx) return;
    const slides = [...hx.querySelectorAll('.wg-hx-slide')], dots = [...hx.querySelectorAll('.wg-hx-dot')];
    const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let at = 0, timer = 0;
    const show = (n) => {
      at = (n + slides.length) % slides.length;
      slides.forEach((sl, k) => { const on = k === at; sl.classList.toggle('is-on', on); sl.setAttribute('aria-hidden', on ? 'false' : 'true'); sl.inert = !on; });
      dots.forEach((d, k) => d.setAttribute('aria-current', k === at ? 'true' : 'false'));
    };
    const stop = () => { clearInterval(timer); timer = 0; hx.classList.remove('is-auto'); };
    const play = () => {
      stop(); if (reduce) return;
      hx.classList.add('is-auto');
      timer = setInterval(() => { if (!$('#lobby').hidden && document.visibilityState === 'visible') show(at + 1); }, 7000);
    };
    dots.forEach((d, k) => d.addEventListener('click', () => { show(k); play(); }));
    hx.addEventListener('mouseenter', stop); hx.addEventListener('mouseleave', play);
    hx.addEventListener('focusin', stop); hx.addEventListener('focusout', (e) => { if (!hx.contains(e.relatedTarget)) play(); });
    show(0); play();
  })();
  document.querySelectorAll('[data-wg-show]').forEach((b) => b.addEventListener('click', () => {
    const sel = $('.rs-show'); if (sel && [...sel.options].some((o) => o.value === b.dataset.wgShow)) { sel.value = b.dataset.wgShow; sel.dispatchEvent(new Event('change')); }
  }));
  const wgGauge = (p, side) => {
    const g = el('span', 'wg-mk-gauge ' + (side === 'No' ? 'no' : 'yes'));
    const v = Math.max(0, Math.min(100, p));
    g.innerHTML = `<svg viewBox="0 0 74 42" aria-hidden="true"><path class="trk" d="M7 38a30 30 0 0 1 60 0" pathLength="100"/><path class="val" d="M7 38a30 30 0 0 1 60 0" pathLength="100" stroke-dasharray="${v.toFixed(1)} 100"/></svg>`;
    g.append(el('b', null, Math.round(p) + '%'), el('small', null, side));
    return g;
  };
  const wgCard = (r) => {
    const yes = num(r.yes_price);
    const no = num(r.no_price) != null ? num(r.no_price) : (num(r.yes_bid) != null ? 100 - num(r.yes_bid) : null);
    const side = r.sit_pick, pYes = num(r.sit_hit), pSide = side === 'Yes' ? pYes : 100 - pYes;
    const label = rhLabel(r.contract);
    const b = el('button', 'wg-mk'); b.type = 'button';
    const top = el('span', 'wg-mk-top');
    const img = el('img', 'wg-mk-img'); img.src = WG_THUMB[r.sit_stat] || WG_T.td; img.alt = ''; img.loading = 'lazy';
    const q = el('span', 'wg-mk-q'); q.append(el('b', null, label + '?'), el('small', null, `${r.game} · ${r.kickoff}`));
    top.append(img, q, wgGauge(pSide, side));
    const px = el('span', 'wg-mk-px');
    const py = el('span', 'wg-px yes' + (side === 'Yes' ? ' is-pick' : '')); py.append(el('span', null, 'Yes'), el('b', null, yes == null ? '—' : yes + '¢'));
    const pn = el('span', 'wg-px no' + (side === 'No' ? ' is-pick' : '')); pn.append(el('span', null, 'No'), el('b', null, no == null ? '—' : no + '¢'));
    px.append(py, pn);
    const foot = el('span', 'wg-mk-foot');
    foot.append(el('span', 'wg-mk-pick', `${side} +${Math.round(num(r.sit_pedge))} pts vs price`), el('span', 'wg-mk-joke', WG_JOKE[r.sit_stat + '|' + side] || 'Coin flip, weighted.'));
    b.append(top, px, foot);
    b.setAttribute('aria-label', `${label}, ${r.game}, ${r.kickoff}. Wedger leans ${side}: ${Math.round(pSide)}% vs ${side === 'Yes' ? yes : no} cents. Open the outlook.`);
    const ctx = { title: label, game: r.game, market: r.market, source: r.source };
    ctx.key = `${ctx.game}|${ctx.market}|${r.contract}`;
    b.addEventListener('click', () => openSit(r, ctx, b));
    return b;
  };
  function drawLobby() {
    const ld = dash.data('lines');
    if (ld.status === 'ok') {
      const picks = ld.data.filter((r) => r.sit_pick && r.sit_key && num(r.sit_hit) != null).sort((a, b) => num(b.sit_pedge) - num(a.sit_pedge));
      document.querySelectorAll('[data-wg-count="lines"]').forEach((e) => { e.textContent = wgFmt(ld.data.length); });
      document.querySelectorAll('[data-wg-count="picks"]').forEach((e) => { e.textContent = wgFmt(picks.length); });
      const per = new Map(), top = [];
      for (const r of picks) { const c = per.get(r.game) || 0; if (c >= 2) continue; per.set(r.game, c + 1); top.push(r); if (top.length === 6) break; }
      const box = $('#wg-hot-cards');
      if (box) box.replaceChildren(...(top.length ? top.map(wgCard) : [el('p', 'wg-cards-empty', 'No line clears its price by 3+ points right now. Coin flips all the way down.')]));
      const run = $('#wg-tick-run'), tick = $('#wg-tick');
      if (run && picks.length) {
        const items = [];
        picks.slice(0, 15).forEach((r, k) => {
          const side = r.sit_pick, p = side === 'Yes' ? num(r.sit_hit) : 100 - num(r.sit_hit);
          const it = el('span', 'wg-tick-item'); it.append(el('b', null, rhLabel(r.contract)), el('span', side === 'Yes' ? 'y' : 'n', `${side} ${Math.round(p)}%`));
          items.push(it);
          if (k % 3 === 2) items.push(el('span', 'wg-tick-item wg-tick-joke', WG_QUIPS[Math.floor(k / 3) % WG_QUIPS.length]));
        });
        const copies = items.map((n) => { const c = n.cloneNode(true); c.setAttribute('aria-hidden', 'true'); return c; });
        run.replaceChildren(...items, ...copies); tick.classList.add('is-live');
      }
    } else if (ld.status === 'error') { const box = $('#wg-hot-cards'); if (box) box.replaceChildren(el('p', 'wg-cards-empty', 'This week’s lines failed to load. Reload the page to try again.')); }
    const bt = dash.data('bt_weeks');
    if (bt.status === 'ok') {
      const row = (g, sg) => bt.data.find((r) => String(r.week) === 'all' && r.seg_group === g && r.segment === sg);
      const put = (k, v) => { const e = document.querySelector(`[data-wg-rcpt="${k}"]`); if (e && v != null) e.textContent = v; };
      const sg = (x) => (Number(x) > 0 ? '+' : Number(x) < 0 ? '−' : '') + Math.abs(Number(x)).toFixed(1) + '%';
      const wp = row('Strategy', 'Wedger picks (3+ pts)'), ey = row('Strategy', 'Every Yes'), pa = row('Market', 'Props · passing'), ru = row('Market', 'Props · rushing');
      if (wp) { put('picks-rec', `${wp.wins}–${wp.losses}`); put('picks-txt', `${(+wp.win_pct).toFixed(1)}% won, ${sg(wp.roi_pct)} return on the picks as posted.`); }
      if (ey) { put('yes-roi', sg(ey.roi_pct)); put('yes-txt', `${wgFmt(ey.wins)}–${wgFmt(ey.losses)} since Week 1. We did it so you don't have to.`); }
      if (pa) { put('pass-pct', (+pa.win_pct).toFixed(1) + '%'); put('pass-txt', `${pa.wins}–${pa.losses} at about 50¢. Let him cook.`); }
      if (ru) { put('rush-pct', (+ru.win_pct).toFixed(1) + '%'); put('rush-txt', `${ru.wins}–${ru.losses} at about 50¢. Touch grass, not the over.`); }
    }
  }
'''
for k, v in (('__T_PASS__', BL['t_pass']), ('__T_RUSH__', BL['t_rush']), ('__T_REC__', BL['t_rec']), ('__T_TD__', BL['t_td'])): JS = JS.replace(k, v)
rep('  // ---------------- render ----------------\n  dash.onData(() => {', JS + '\n  // ---------------- render ----------------\n  dash.onData(() => {')
rep('    drawProfit();\n    drawAnalysts();\n    drawBtPerms();', '    drawProfit();\n    drawLobby();\n    drawAnalysts();\n    drawBtPerms();')

open(B + 'page_template.html', 'w').write(s)
print('brand ok')
