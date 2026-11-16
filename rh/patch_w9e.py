"""Wed Nov 4, 10:30 PM: Signal Green (#009A44) everywhere the brand green was, sheen silver (polished, not brushed),
rendered helmets, and a faint team-color sheen on each pick under the cursor. Runs on the final index.html after patch_w9d.py."""
import re
B = '/home/claude/wedger/rh/'
s = open(B + 'index.html').read()

def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, (old[:100], c); s = s.replace(old, new)

# ---------------------------------------------------------------- one green: Signal Green #009A44
for a, b in [('#104D30', '#009A44'), ('#104d30', '#009A44'), ('#3A8F63', '#009A44'), ('#2F7D56', '#009A44'), ('#2F8A5B', '#009A44'), ('#6FB38D', '#009A44'),
             ('#24804F', '#009A44'), ('#0C3D26', '#00843A'), ('rgba(16, 77, 48', 'rgba(0, 154, 68'), ('rgba(47, 138, 91', 'rgba(0, 154, 68'),
             ('%23EEF3EF', '%2306120B')]:
    s = s.replace(a, b)
# text on green fills is near-black (white on #009A44 is too faint at button sizes)
s = s.replace('--wz-on-g: #EEF3EF;', '--wz-on-g: #06120B;').replace('--wx-on-green: #EEF3EF;', '--wx-on-green: #06120B;').replace('--wz-pos-fg: #EEF3EF;', '--wz-pos-fg: #06120B;')
assert '#104D30' not in s and '#6FB38D' not in s

CSS = r'''
  /* ===================== Signal Green + sheen silver ===================== */
  .wg-paper {
    --wz-g: #009A44; --wz-g-hi: #00843A; --wz-on-g: #06120B;
    /* small green text on silver uses a deeper step of the same green so it stays readable */
    --wx-green-ink: #007A36; --wg-ink: #007A36; --color-ok: #007A36;
    --wz-metal: linear-gradient(118deg, rgba(255, 255, 255, 0) 28%, rgba(255, 255, 255, .7) 44%, rgba(255, 255, 255, 0) 58%),
      linear-gradient(135deg, #FBFBFC 0%, #E3E6E9 20%, #C6CBD1 40%, #F4F5F7 56%, #D3D7DC 74%, #EDEFF1 88%, #DADDE1 100%);
    --wx-brushed: var(--wz-metal);
    --wz-page: radial-gradient(1400px 700px at 12% -8%, #FFFFFF 0%, rgba(255, 255, 255, 0) 60%), radial-gradient(1100px 600px at 100% 30%, rgba(255, 255, 255, .7) 0%, rgba(255, 255, 255, 0) 60%), linear-gradient(165deg, #F2F3F5 0%, #E3E6E9 46%, #ECEEF0 100%);
    background: var(--wz-page);
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) .wg-paper { --wx-green-ink: #009A44; --wg-ink: #009A44; --color-ok: #009A44; background: #111316; }
  }
  :root[data-theme="dark"] .wg-paper { --wx-green-ink: #009A44; --wg-ink: #009A44; --color-ok: #009A44; background: #111316; }
  .wz-hero { background: var(--wz-metal); background-size: 100% 100%; animation: none; }
  .wz-hero::before { content: ''; position: absolute; inset: -20% 0; z-index: -1; pointer-events: none; background: linear-gradient(104deg, transparent 38%, rgba(255, 255, 255, .75) 49%, rgba(255, 255, 255, .15) 54%, transparent 62%); transform: translateX(-120%); animation: wzGlint 9s cubic-bezier(.45, .05, .25, 1) infinite; }
  @keyframes wzGlint { 0%, 62% { transform: translateX(-120%); } 100% { transform: translateX(120%); } }
  .wz-hero::after { opacity: .05; }
  .wz-an.lead, .wz-plan.hot, .wz-ex { background: var(--wz-metal); box-shadow: inset 0 1px 0 rgba(255, 255, 255, .9), 0 30px 60px -40px rgba(0, 0, 0, .6); }
  .wz-big { background: linear-gradient(180deg, #FFFFFF 8%, #E3E6E9 40%, #A9AFB6 62%, #F4F5F7 80%, #B9BEC4 100%); -webkit-background-clip: text; background-clip: text; }
  .wz-top .rs-tab::after { background: linear-gradient(90deg, #FFFFFF, #C6CBD1 50%, #F4F5F7); }
  .wz-h1 em { color: #009A44; }
  .wz-h1 { font-size: clamp(42px, 11.5vw, 112px); }
  @media (min-width: 921px) { .wz-h1 { font-size: clamp(64px, 8vw, 112px); } }
  .wz-btn-g { color: #06120B; font-weight: 800; }
  .wz-btn-g:hover { color: #06120B; }
  .wz-badge, .wz-st.live, .wz-cover em.live, .wz-tk em, .wz-me em.pro, .wz-filters > summary b, .wz-chip.pos { color: #06120B; font-weight: 600; }
  .wz-dots i.w { box-shadow: none; }
  .wz-helm { width: clamp(96px, 13vw, 160px); }

  /* a faint sheen in the player's team colors when the cursor is over a pick */
  .wz-tc { --tc1: transparent; --tc2: transparent; }
  .wx-read.wz-tc::before { content: ''; position: absolute; inset: 0; z-index: 0; pointer-events: none; opacity: 0; transition: opacity .45s ease;
    background: linear-gradient(115deg, color-mix(in srgb, var(--tc1) 15%, transparent) 0%, transparent 42%, color-mix(in srgb, var(--tc2) 11%, transparent) 68%, transparent 100%),
      linear-gradient(100deg, transparent 30%, color-mix(in srgb, var(--tc1) 10%, rgba(255, 255, 255, .35)) 50%, transparent 70%);
    background-size: 100% 100%, 220% 100%; background-position: 0 0, 120% 0; }
  .wx-read.wz-tc:hover::before { opacity: 1; animation: wzTcSweep 1.4s cubic-bezier(.3, .6, .2, 1) both; }
  @keyframes wzTcSweep { from { background-position: 0 0, 120% 0; } to { background-position: 0 0, -20% 0; } }
  .rs-table tbody tr.wz-tc:hover { background: linear-gradient(90deg, color-mix(in srgb, var(--tc1) 9%, transparent), color-mix(in srgb, var(--tc2) 6%, transparent) 45%, transparent 85%); }
  .rs-table tbody tr.wz-tc:hover > td { background-color: transparent; }
  .wz-tk.wz-tc:hover { background: linear-gradient(90deg, color-mix(in srgb, var(--tc1) 22%, #0D0F12), color-mix(in srgb, var(--tc2) 14%, #0D0F12)); }
  @media (prefers-reduced-motion: reduce) { .wz-hero::before { animation: none; display: none; } .wx-read.wz-tc:hover::before { animation: none; background-position: 0 0, 50% 0; } }
'''
assert s.count('</style>') == 1
s = s.replace('</style>', CSS + '</style>')

# ---------------------------------------------------------------- rendered helmets (generic shell, stripe and facemask in team colors; no logos)
i = s.index('  function wzHelmet(team, flip) {'); j = s.index('\n  }\n', i) + len('\n  }\n')
HELM = r'''  let wzHelmN = 0;
  const WZ_HEX = /^#[0-9A-Fa-f]{6}$/;
  const WZ_MASK = { JAX: '#C9CED4', BAL: '#111111', DEN: '#002244', CAR: '#C9CED4', SF: '#B3995D', LV: '#C9CED4', NO: '#111111', PIT: '#111111', CIN: '#111111', CLE: '#C9CED4', NYJ: '#111111', MIN: '#C9CED4', GB: '#203731', KC: '#C9CED4', MIA: '#C9CED4' };
  function wzHelmet(team, flip) {
    const T = wzTeam(team), c1 = WZ_HEX.test(T[1]) ? T[1] : '#4A5056', c2 = WZ_HEX.test(T[2]) ? T[2] : '#9DA3AA', mk = WZ_MASK[team] || '#C9CED4', u = 'h' + (++wzHelmN);
    const shell = 'M44 126 C24 110 17 80 28 56 C42 26 78 11 118 12 C154 13 180 34 188 62 C191 71 189 79 181 81 L160 83 C153 90 151 104 155 117 C158 128 152 139 139 143 L108 146 C95 147 86 141 82 132 C70 136 55 134 44 126 Z';
    const stripe = 'M30 58 C44 30 80 16 118 17 C152 18 176 37 184 63';
    const jaw = 'M151 88 C146 100 147 114 151 124 C153 131 149 137 141 139 L112 141 C103 141 97 137 95 131 C104 128 111 121 114 112 C122 104 136 92 151 88 Z';
    const bars = 'M176 84 C188 85 197 87 204 90 M155 101 L206 101 M154 117 L205 116 M204 90 C207 104 207 118 203 131 C199 139 189 143 176 143 L146 143 M180 85 L182 141';
    const g = flip ? ' transform="translate(214 0) scale(-1 1)"' : '';
    const svg = `<defs><clipPath id="${u}c"><path d="${shell}"/></clipPath>
<linearGradient id="${u}v" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".34"/><stop offset=".38" stop-color="#fff" stop-opacity="0"/><stop offset=".72" stop-color="#000" stop-opacity=".18"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></linearGradient>
<radialGradient id="${u}r" cx=".36" cy=".26" r=".7"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".45" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<linearGradient id="${u}b" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity=".45"/><stop offset=".22" stop-color="#000" stop-opacity="0"/><stop offset=".8" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".25"/></linearGradient>
<linearGradient id="${u}m" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".35"/></linearGradient>
<filter id="${u}f" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.4"/></filter>
<filter id="${u}s" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="5"/></filter></defs>
<g${g}><ellipse cx="112" cy="158" rx="78" ry="7" fill="#000" opacity=".28" filter="url(#${u}s)"/>
<path d="M138 140 C150 148 166 150 178 147" fill="none" stroke="#15171A" stroke-width="4" stroke-linecap="round" opacity=".85"/>
<path d="${shell}" fill="${c1}"/>
<g clip-path="url(#${u}c)"><path d="${stripe}" fill="none" stroke="${c2}" stroke-width="13" stroke-linecap="round" transform="translate(0 6)"/>
<path d="${stripe}" fill="none" stroke="#fff" stroke-width="2" stroke-opacity=".55" transform="translate(0 -1)"/><path d="${stripe}" fill="none" stroke="#fff" stroke-width="2" stroke-opacity=".55" transform="translate(0 13)"/>
<path d="${shell}" fill="url(#${u}v)"/><path d="${shell}" fill="url(#${u}b)"/><path d="${shell}" fill="url(#${u}r)"/><path d="${jaw}" fill="#000" opacity=".22"/>
<ellipse cx="92" cy="33" rx="40" ry="8" fill="#fff" opacity=".7" transform="rotate(-14 92 33)" filter="url(#${u}f)"/><ellipse cx="86" cy="30" rx="16" ry="3" fill="#fff" opacity=".85" transform="rotate(-16 86 30)"/>
<path d="M30 70 C28 90 34 108 46 122" fill="none" stroke="#fff" stroke-width="3" stroke-opacity=".28" filter="url(#${u}f)"/></g>
<path d="${shell}" fill="none" stroke="#000" stroke-opacity=".35" stroke-width="1.2"/>
<ellipse cx="112" cy="96" rx="10" ry="11.5" fill="#0D0F12" opacity=".78"/><ellipse cx="112" cy="96" rx="10" ry="11.5" fill="none" stroke="#fff" stroke-opacity=".28" stroke-width="1.4"/>
<circle cx="98" cy="60" r="2.6" fill="#C9CED4" stroke="#000" stroke-opacity=".35"/>
<rect x="171" y="78" width="11" height="9" rx="2.5" fill="#BFC4CA" stroke="#000" stroke-opacity=".35"/><rect x="146" y="136" width="10" height="9" rx="2.5" fill="#BFC4CA" stroke="#000" stroke-opacity=".35"/>
<path d="${bars}" fill="none" stroke="#0B0C0E" stroke-opacity=".55" stroke-width="7.5" stroke-linecap="round" stroke-linejoin="round" transform="translate(1 1.6)"/>
<path d="${bars}" fill="none" stroke="${mk}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
<path d="${bars}" fill="none" stroke="url(#${u}m)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
<path d="${bars}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" transform="translate(-.6 -1.4)"/></g>`;
    const ns = 'http://www.w3.org/2000/svg', el2 = document.createElementNS(ns, 'svg');
    el2.setAttribute('viewBox', '0 0 214 168'); el2.setAttribute('class', 'wz-helm'); el2.setAttribute('aria-hidden', 'true');
    el2.innerHTML = svg;   // built only from fixed shapes and validated hex colors
    return el2;
  }
  // the player's team for a line (from projections, prop groups and anytime TDs), for the team-color sheen
  let wzTM = null, wzTMn = -1;
  function wzPlayerTeam(r) {
    const P = dash.data('proj'), Q = dash.data('props'), A = dash.data('atd');
    const n = [P, Q, A].reduce((a, d) => a + (d.status === 'ok' ? d.data.length : 0), 0);
    if (n !== wzTMn) {
      wzTMn = n; wzTM = new Map();
      for (const d of [P, Q, A]) if (d.status === 'ok') for (const x of d.data) { const nm = x.player || String(x.contract || '').split(':')[0]; if (x.team && nm) wzTM.set(x.game + '|' + nm, x.team); }
    }
    return wzTM.get(r.game + '|' + String(r.player || r.contract || '').split(':')[0]) || null;
  }
  function wzTint(node, r) {
    const t = wzPlayerTeam(r); if (!t || !WZ_TEAMS[t]) return;
    node.classList.add('wz-tc'); node.style.setProperty('--tc1', WZ_TEAMS[t][1]); node.style.setProperty('--tc2', WZ_TEAMS[t][2]);
  }
'''
s = s[:i] + HELM + s[j:]

# hooks: read cards, ticker items, table rows
rep("    b.classList.add('wz-spot');\n", "    b.classList.add('wz-spot'); wzTint(b, r);\n")
rep("    const b = el('button', 'wz-tk'); b.type = 'button'; b.tabIndex = -1;\n", "    const b = el('button', 'wz-tk'); b.type = 'button'; b.tabIndex = -1; wzTint(b, r);\n")
rep("if (started(r)) tr.className = 'rs-started';", "if (started(r)) tr.className = 'rs-started'; wzTint(tr, r);", count=5)

open(B + 'index.html', 'w').write(s)
print('w9e ok', len(s))
