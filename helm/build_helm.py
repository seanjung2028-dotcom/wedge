"""Team helmets from Sean's reference photo (two generic helmets, no logos): cut out, recolor shell and facemask, export facing right."""
from PIL import Image, ImageFilter
import numpy as np, json
from scipy import ndimage as ndi
im = Image.open('ref.png').convert('RGB'); A = np.asarray(im).astype(float) / 255
H, W, _ = A.shape
# smooth background model from the four corners
c = {k: A[y0:y1, x0:x1].reshape(-1, 3).mean(0) for k, (y0, y1, x0, x1) in {'tl': (0, 20, 0, 20), 'tr': (0, 20, W - 20, W), 'bl': (H - 20, H, 0, 20), 'br': (H - 20, H, W - 20, W)}.items()}
yy, xx = np.mgrid[0:H, 0:W]; fy = (yy / (H - 1))[..., None]; fx = (xx / (W - 1))[..., None]
BG = (c['tl'] * (1 - fx) + c['tr'] * fx) * (1 - fy) + (c['bl'] * (1 - fx) + c['br'] * fx) * fy

def hsv(arr):
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]; mx = arr.max(-1); mn = arr.min(-1); d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return h, np.where(mx > 0, (mx - mn) / (mx + 1e-9), 0), mx
def lum(arr): return arr[..., 0] * .2126 + arr[..., 1] * .7152 + arr[..., 2] * .0722
def hex2(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) / 255
def rgb2hsl(rgb):
    import colorsys; return colorsys.rgb_to_hls(*rgb)

def cut(x0, x1, y0, y1, shell_hue, gold=False):
    a = A[y0:y1, x0:x1]; bg = BG[y0:y1, x0:x1]
    d = np.abs(a - bg).max(-1); dl = lum(bg) - lum(a)
    h, s, v = hsv(a)
    shell = ((h >= shell_hue[0]) & (h <= shell_hue[1]) & (s > .18))
    shell = ndi.binary_closing(shell, iterations=4)
    shell = ndi.binary_fill_holes(shell)                      # keeps glossy highlights inside the shell
    core = (d > .16) | shell
    core = ndi.binary_opening(core, iterations=1)
    lab, n = ndi.label(core); sizes = ndi.sum(core, lab, range(1, n + 1)); keep = np.isin(lab, 1 + np.where(sizes > 400)[0])
    core = keep
    alpha = np.clip((d - .04) / (.16 - .04), 0, 1)
    alpha = np.maximum(alpha, core.astype(float))
    alpha[shell] = 1
    # soft shadow below: darker, unsaturated pixels outside the solid body -> black at partial alpha
    body = ndi.binary_dilation(core, iterations=3)
    sh = (~body) & (dl > .01) & (s < .12)
    rgb = a.copy()
    # decontaminate semi-transparent edge pixels from the light background
    al = np.clip(alpha, 1e-3, 1)[..., None]
    rgb = np.clip((a - (1 - al) * bg) / al, 0, 1)
    sha = np.clip(dl / .22, 0, 1) * .8
    rgb[sh] = 0; alpha = np.where(sh, sha, alpha)
    alpha[(~body) & (~sh) & (d < .06)] = 0
    msk = None
    if gold:
        msk = (h > 25) & (h < 70) & (s > .15) & (v > .25) & (~shell)
        msk = ndi.binary_dilation(msk, iterations=1) & ((h > 20) & (h < 75) & (s > .08)) & (~shell)
    return rgb, alpha, shell, msk

def recolor(rgb, region, target, base_rgb_mean):
    """Map region's colors onto target keeping shading: lightness maps base->target, highlights to white, shadows to black."""
    import colorsys
    tr = hex2(target); th, tl, ts = colorsys.rgb_to_hls(*tr)
    bh, bl, bs = colorsys.rgb_to_hls(*base_rgb_mean)
    out = rgb.copy(); idx = np.where(region)
    px = rgb[idx]
    mx = px.max(1); mn = px.min(1); L = (mx + mn) / 2; S = np.where(mx == mn, 0, np.where(L < .5, (mx - mn) / (mx + mn + 1e-9), (mx - mn) / (2 - mx - mn + 1e-9)))
    Ln = np.where(L >= bl, tl + (L - bl) / (1 - bl + 1e-9) * (1 - tl), tl * L / (bl + 1e-9))
    Sn = np.clip(ts * S / (bs + 1e-9), 0, 1)
    # hls -> rgb vectorized
    def hue2(p, q, t):
        t = t % 1
        return np.where(t < 1 / 6, p + (q - p) * 6 * t, np.where(t < 1 / 2, q, np.where(t < 2 / 3, p + (q - p) * (2 / 3 - t) * 6, p)))
    q = np.where(Ln < .5, Ln * (1 + Sn), Ln + Sn - Ln * Sn); p = 2 * Ln - q
    r = hue2(p, q, th + 1 / 3); g = hue2(p, q, th); b = hue2(p, q, th - 1 / 3)
    out[idx] = np.stack([r, g, b], 1)
    return out

# left helmet: teal shell, black facemask; right helmet: purple shell, gold facemask
L = cut(60, 470, 115, 470, (165, 215))
R = cut(455, 928, 115, 470, (230, 305), gold=True)
def mean_of(rgb, m):
    px = rgb[m]; lm = lum(px); sel = (lm > np.percentile(lm, 35)) & (lm < np.percentile(lm, 65)); return px[sel].mean(0)
L_shell = mean_of(L[0], L[2]); R_shell = mean_of(R[0], R[2]); R_gold = mean_of(R[0], R[3])
print('base colors', (L_shell * 255).round(), (R_shell * 255).round(), (R_gold * 255).round())
TEAMS = json.load(open('teams.json'))
out = {}
for t, (name, c1, c2, mask) in TEAMS.items():
    dark = mask.lower() in ('#111111', '#0b162a', '#03202f', '#101820', '#0c2340')
    if dark:
        rgb, al, sh, _ = L; img = recolor(rgb, sh, c1, L_shell)
    else:
        rgb, al, sh, gm = R; img = recolor(rgb, sh, c1, R_shell); img = recolor(img, gm, mask, R_gold); img = img[:, ::-1]; al = al[:, ::-1]
    rgba = np.dstack([img, al]); ys, xs = np.where(al > .02)
    rgba = rgba[max(0, ys.min() - 4):ys.max() + 5, max(0, xs.min() - 4):xs.max() + 5]
    pil = Image.fromarray((rgba * 255).round().astype('uint8'), 'RGBA')
    w = 320; pil = pil.resize((w, round(pil.height * w / pil.width)), Image.LANCZOS)
    pil.save(f'out/{t}.webp', 'WEBP', quality=88, method=6); pil.save(f'out/{t}.png')
    out[t] = pil.size
print(len(out), list(out.items())[:3])
