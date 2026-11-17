"""Round 15 (Tue Nov 17): the research file goes from a manila folder to a metal one, in the site's own look.
After the owner's references: a single steel-gray folder under soft studio light, papers held to stainless steel by
magnets, and silver type pressed into a pale metal sheet. The shape stays (three tabs, the front panel dipping under
the open tab, pressed lines along the bottom); the stock is brushed aluminum, the sheet is plain white paper held by two
chrome magnets, and the writing is the site's type: Archivo Wide for the title, pressed into the metal, Geist Mono for
labels and tabs, Geist for the rest. Overrides only; the folder's markup and script are unchanged."""
WIDE = '"Archivo Wide", "Archivo", "Helvetica Neue", Arial, sans-serif'
MONO = '"Geist Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace'
SANS = '"Geist", "Helvetica Neue", Arial, sans-serif'
CSS = f'''
/* ---------------- round 15: the research file, in the site's light metal ---------------- */
.wg-sitdlg.v2-folder {{ --hand: {SANS};
  --mf: #C9CED3; --mf-hi: #E4E7EA; --mf-lo: #A9AFB5; --mf-back: #D9DCE0; --mf-behind: #AEB3B9; --mf-edge: rgba(255, 255, 255, .8);
  --ink: #15181B; --ink-mu: #474D54; --pap: #FBFBFA; --pap-ink: #16181B; --pap-mu: #5B6168; --pap-rule: transparent;
  --brush: linear-gradient(transparent, transparent);
  --metal: conic-gradient(from 214deg at 64% 36%, #9AA0A7 0deg, #D2D6DA 38deg, #F6F7F8 72deg, #B5BAC0 112deg, #868B92 158deg, #A7ACB2 204deg, #ECEEF0 252deg, #C0C5CA 300deg, #9AA0A7 360deg); }}
.v2-folder::backdrop {{ background: radial-gradient(120% 90% at 50% 30%, rgba(30, 33, 37, .55), rgba(6, 7, 9, .82)); }}
/* the back panel and its open tab: brushed aluminum, lit from the top left */
.wg-sitdlg.v2-folder .wg-sd-in {{ border-radius: 0 16px 8px 8px;
  background: linear-gradient(180deg, #EEF0F2 0, var(--mf-back) 70px, #C3C8CD 100%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, .85), inset 0 -1px 0 rgba(0, 0, 0, .18), 0 1px 0 rgba(0, 0, 0, .25),
    0 60px 110px -40px rgba(0, 0, 0, .9), 0 22px 36px -20px rgba(0, 0, 0, .6); }}
/* the front panel: a sheen across the metal, a bright rolled edge, pressed lines along the bottom */
.wg-sitdlg.v2-folder .v2-cover {{ filter: drop-shadow(0 -1px 0 rgba(255, 255, 255, .9)) drop-shadow(0 -2px 3px rgba(0, 0, 0, .28)); }}
.wg-sitdlg.v2-folder .v2-cover::before {{ border-radius: 0 0 8px 8px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, .7) 0 1px, transparent 1px) 0 calc(100% - 46px) / 100% 1px no-repeat,
    repeating-linear-gradient(180deg, transparent 0 10px, rgba(30, 35, 40, .22) 10px 11px, rgba(255, 255, 255, .5) 11px 12px) 0 calc(100% - 6px) / 100% 36px no-repeat,
    linear-gradient(180deg, rgba(0, 0, 0, .14), rgba(0, 0, 0, 0) 4px) 0 calc(100% - 47px) / 100% 5px no-repeat,
    var(--metal); }}
/* the tabs: steel, the open one joined to its panel; labels in the site's mono */
.wg-sitdlg.v2-folder .wg-sd-tab {{ font-family: {MONO} !important; font-weight: 500; font-size: 11.5px; letter-spacing: .12em; text-transform: uppercase; color: #3E444B; }}
.wg-sitdlg.v2-folder .wg-sd-tab::before {{ border-radius: 14px 14px 0 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, .55), rgba(255, 255, 255, 0) 45%, rgba(0, 0, 0, .1) 100%), var(--tabc);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, .8), inset 0 0 0 1px rgba(0, 0, 0, .12); }}
.wg-sitdlg.v2-folder .wg-sd-tab[aria-selected="true"] {{ --tabc: #EEF0F2; color: var(--ink); font-weight: 600; }}
.wg-sitdlg.v2-folder .wg-sd-tab[aria-selected="true"]::before {{ background: linear-gradient(180deg, #F4F5F6, #EEF0F2);
  box-shadow: inset 0 1px 0 #fff, inset 1px 0 0 rgba(0, 0, 0, .1), inset -1px 0 0 rgba(0, 0, 0, .1); }}
.wg-sitdlg.v2-folder .wg-sd-tab:hover {{ color: var(--ink); }}
.wg-sitdlg.v2-folder .wg-sd-tab:focus-visible {{ outline-color: #15181B; }}
/* what's on the folder: a mono label, the title pressed into the metal, plain facts under it */
.wg-sitdlg.v2-folder .wg-sd-kicker {{ font-family: {MONO} !important; font-weight: 500; font-size: 11.5px; letter-spacing: .14em; text-transform: uppercase; color: #4A5057; }}
.wg-sitdlg.v2-folder #sit-title {{ font-family: {WIDE} !important; font-stretch: 125% !important; font-weight: 900; font-size: clamp(26px, 3.4vw, 42px); line-height: 1.02;
  letter-spacing: -.015em; text-transform: uppercase; color: #1A1D21; background: none; padding-bottom: 0; margin-top: 8px;
  text-shadow: 0 1px 0 rgba(255, 255, 255, .7), 0 -1px 0 rgba(0, 0, 0, .22); }}
.wg-sitdlg.v2-folder .wg-sd-sub {{ margin-top: 12px; font-family: {SANS} !important; font-weight: 500; font-size: 14.5px; letter-spacing: 0; font-variant-numeric: tabular-nums; color: #3F454C; }}
.wg-sitdlg.v2-folder .wg-sd-sub > span + span::before {{ margin: 0 .6em; opacity: .5; }}
/* the close button: a chrome stud */
.wg-sitdlg.v2-folder .wg-sd-close {{ width: 38px; height: 38px; font-family: {SANS} !important; font-size: 18px; font-weight: 500; color: #1A1D21;
  background: radial-gradient(circle at 34% 28%, #FFFFFF 0, #E3E6E9 30%, #AEB4BA 72%, #8E959C 100%); border: 1px solid rgba(0, 0, 0, .28);
  box-shadow: inset 0 1px 0 #fff, inset 0 -2px 3px rgba(0, 0, 0, .18), 0 4px 10px -3px rgba(0, 0, 0, .45); }}
.wg-sitdlg.v2-folder .wg-sd-close:hover {{ background: radial-gradient(circle at 34% 28%, #FFFFFF 0, #EEF0F2 36%, #BAC0C6 76%, #98A0A7 100%); }}
/* the sheet: plain white paper held to the metal by two chrome magnets (no ruled lines) */
.wg-sitdlg.v2-folder .wg-sd-body {{ border-radius: 3px; background-color: var(--pap);
  --mag: radial-gradient(circle closest-side at 50% 50%, #F2F4F5 0, #D3D7DB 38%, #A5ACB2 70%, #737A81 90%, #5B6168 97%, transparent 100%);
  --mag-hi: radial-gradient(circle at 36% 30%, rgba(255, 255, 255, .95) 0, rgba(255, 255, 255, .5) 2.5px, rgba(255, 255, 255, 0) 5px);
  --mag-sh: radial-gradient(circle closest-side at 50% 50%, rgba(0, 0, 0, .3) 0, rgba(0, 0, 0, .18) 60%, transparent 100%);
  background-image: var(--mag-hi), var(--mag), var(--mag-sh), var(--mag-hi), var(--mag), var(--mag-sh);
  background-size: 18px 18px, 18px 18px, 22px 22px, 18px 18px, 18px 18px, 22px 22px;
  background-position: 14px 12px, 14px 12px, 13px 13px, calc(100% - 14px) 12px, calc(100% - 14px) 12px, calc(100% - 15px) 13px;
  background-repeat: no-repeat; background-attachment: local;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, .07), 0 2px 3px -1px rgba(0, 0, 0, .18), 0 24px 36px -22px rgba(0, 0, 0, .6); }}
.wg-sitdlg.v2-folder .wg-sd-body {{ --color-fg: #16181B; --color-fg-muted: #5B6168; --color-border-line: rgba(20, 24, 28, .14); --cds-chart-grid: rgba(20, 24, 28, .1); --cds-chart-muted: #AEB4BA;
  --wx-ink: #16181B; --wx-muted: #5B6168; --wx-faint: #7B8188; --wx-rule: rgba(20, 24, 28, .13); --pf-ink: #16181B; --pf-muted: #5B6168; --pf-line: rgba(20, 24, 28, .13); --v2-hi: #16181B; --v2-mu: #5B6168;
  --cds-border: rgba(20, 24, 28, .14); --cds-text-secondary: #5B6168; --cds-chart-reference: #7B8188; --v2-lo: #F6F7F8; --v2-w: 20 24 28; --v2-th: rgba(244, 245, 246, .97); }}
.wg-sitdlg.v2-folder .wg-card, .wg-sitdlg.v2-folder .wg-wf, .wg-sitdlg.v2-folder .wg-chart, .wg-sitdlg.v2-folder .wg-sd-splits .wg-sp, .wg-sitdlg.v2-folder .v2-trail {{
  background: #F4F5F6; color: #16181B; border: 1px solid rgba(20, 24, 28, .1); box-shadow: inset 0 1px 0 #fff, 0 10px 18px -16px rgba(0, 0, 0, .45); }}
/* headings on the sheet in the site's wide type; hints in mono */
.wg-sitdlg.v2-folder .wg-sd-sech h3, .wg-sitdlg.v2-folder .wg-sd-sec > h3 {{ font-family: {WIDE} !important; font-stretch: 118% !important; font-weight: 850; font-size: 16px; line-height: 1.2;
  letter-spacing: .01em; text-transform: uppercase; color: #16181B; }}
.wg-sitdlg.v2-folder .wg-sd-hint, .wg-sitdlg.v2-folder .wg-lab {{ font-family: {MONO} !important; font-weight: 500; font-size: 11px; letter-spacing: .1em; text-transform: uppercase; color: #5B6168; }}
.wg-sitdlg.v2-folder svg text, .wg-sitdlg.v2-folder svg tspan {{ font-family: {SANS} !important; }}
/* the script bars: the middle (competitive) share in steel gray instead of warm taupe */
.wg-sitdlg.v2-folder .v2-scr-bar {{ background: #E3E6E9; }}
.wg-sitdlg.v2-folder .v2-scr-m {{ background: #8E959C; }}
/* room for the magnets above the sheet's first line */
.wg-sitdlg.v2-folder .wg-sd-body {{ padding-top: 40px; }}
.v2-leaf-f {{ background: #FBFBFA; box-shadow: 0 18px 32px -20px rgba(0, 0, 0, .55), 0 0 0 1px rgba(0, 0, 0, .07); }}
@media (max-width: 640px) {{
  .wg-sitdlg.v2-folder .wg-sd-tab {{ font-size: 9.5px; letter-spacing: .06em; padding: 3px 6px 0; }}
  .wg-sitdlg.v2-folder .wg-sd-body {{ background-position: 9px 9px, 9px 9px, 8px 10px, calc(100% - 9px) 9px, calc(100% - 9px) 9px, calc(100% - 10px) 10px; padding-top: 36px; }}
}}
'''
CSS += '''
/* switching tabs: the sheet stays put and only what's written on it changes, with a short fade (no page shuffle, no tab bounce) */
.wg-sitdlg.v2-folder .v2-leaf { display: none !important; }
.wg-sitdlg.v2-folder .wg-sd-tab.v2-tab-pop { animation: none; }
.wg-sitdlg.v2-folder .wg-sd-body.v2-fade > * { animation: v2SheetIn .24s cubic-bezier(.2, .7, .2, 1) both; }
@keyframes v2SheetIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
@media (prefers-reduced-motion: reduce) { .wg-sitdlg.v2-folder .wg-sd-body.v2-fade > * { animation: none; } }
'''
def apply(s, js):
    assert 'class="wg-sitdlg v2-folder"' in s, 'r15: folder markup missing'
    k = s.rindex('</style>'); s = s[:k] + CSS + s[k:]
    a = "  function v2LeafStart(prev, k) {\n    if (reduced() || !prev || prev === k || sitDlg.classList.contains('v2-opening')) return null;\n"
    assert js.count(a) == 1, 'r15: v2LeafStart not found'
    js = js.replace(a, a + "    { const b0 = $('.wg-sd-body', sitDlg); if (b0) { b0.classList.remove('v2-fade'); void b0.offsetWidth; b0.classList.add('v2-fade'); clearTimeout(V2.fadeT); V2.fadeT = setTimeout(() => b0.classList.remove('v2-fade'), 320); } return null; }\n")
    return s, js
