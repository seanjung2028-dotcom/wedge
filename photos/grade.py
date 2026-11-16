"""Wedger photo treatment: crop, then blend a forest->wedge-green->chalk duotone over the photo so every image shares the brand cast."""
from PIL import Image, ImageOps, ImageEnhance
import numpy as np, os
FOREST = np.array([4, 26, 16]); GREEN = np.array([0, 188, 92]); CHALK = np.array([238, 250, 230])
def duo(im):
    a = np.asarray(ImageOps.grayscale(im), dtype=np.float32) / 255.0
    a = np.clip((a - 0.04) / 0.92, 0, 1)[..., None]
    lo = FOREST + (GREEN - FOREST) * np.clip(a / 0.6, 0, 1)
    out = np.where(a < 0.6, lo, GREEN + (CHALK - GREEN) * np.clip((a - 0.6) / 0.4, 0, 1))
    return Image.fromarray(out.astype(np.uint8))
def treat(src, box, size, mix, out, q=74):
    im = Image.open('raw/' + src).convert('RGB')
    W, H = im.size; x0, y0, x1, y1 = box   # fractional crop box
    im = im.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H))).resize(size, Image.LANCZOS)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    g = Image.blend(im, duo(im), mix)
    g.save('web/' + out, 'JPEG', quality=q, optimize=True, progressive=True)
    return os.path.getsize('web/' + out)
JOBS = [
    # name, src, crop box (fractions), size, duotone mix
    ('hero_night.jpg',  'hero_night.jpg',  (0.0, 0.08, 1.0, 0.52), (1600, 1000), 0.30),
    ('hero_ball.jpg',   'hero_ball.jpg',   (0.0, 0.18, 1.0, 0.82), (1600, 900), 0.28),
    ('hero_hoop.jpg',   'bball_hoop.jpg',  (0.0, 0.0, 1.0, 1.0),   (1600, 1044), 0.30),
    ('banner_turf.jpg', 'turf_lines.jpg',  (0.0, 0.25, 1.0, 0.85), (1600, 600), 0.38),
    ('banner_aerial.jpg','aerial_game.jpg',(0.30, 0.20, 1.0, 0.80), (1600, 690), 0.34),
    ('banner_sunset.jpg','sunset_balls.jpg',(0.0, 0.08, 1.0, 0.50), (1600, 800), 0.30),
    ('banner_soccer.jpg','soccer_stadium.jpg',(0.0, 0.25, 1.0, 0.85),(1600, 640), 0.32),
    ('banner_goal.jpg', 'soccer_goal.jpg', (0.0, 0.25, 1.0, 0.55), (1600, 720), 0.32),
    ('banner_arena.jpg','bball_hoop.jpg',  (0.0, 0.0, 1.0, 0.75),  (1600, 780), 0.34),
    # card thumbnails (square)
    ('t_pass.jpg', 'hero_ball.jpg',   (0.18, 0.28, 0.72, 0.95), (240, 240), 0.22),
    ('t_rush.jpg', 'turf_lines.jpg',  (0.45, 0.10, 0.95, 0.85), (240, 240), 0.30),
    ('t_rec.jpg',  'aerial_game.jpg', (0.35, 0.25, 0.75, 0.78), (240, 240), 0.25),
    ('t_td.jpg',   'hero_night.jpg',  (0.15, 0.12, 0.75, 0.52), (240, 240), 0.25),
    ('t_nba.jpg',  'bball_hoop.jpg',  (0.45, 0.0, 0.95, 0.75),  (240, 240), 0.22),
]
for j in JOBS: print(j[0], treat(*j[1:], j[0]) if False else treat(j[1], j[2], j[3], j[4], j[0]))
