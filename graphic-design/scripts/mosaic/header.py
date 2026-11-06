"""README header banners: Artemis II photos as 15-degree trapezoid mosaics with the al-maha wordmark.

Usage (from graphic-design/scripts/mosaic):
    python3 header.py <preset> [preview.png]
    python3 header.py --list

Output goes to graphic-design/headers/. Photos are read from graphic-design/source-photos/.

Lattice alignment: the wordmark is scaled so one 20-unit wordmark cell spans K mosaic triangle
bases (S = K*b/20), and K wordmark rows span exactly K mosaic rows. The wordmark's x offset is
then snapped so its vertices land on mosaic lattice vertices for the chosen baseline row.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import wordmark
import numpy as np
from trap import group_geometry, labels

GD = os.path.join(HERE, "..", "..")      # graphic-design/
PHOTOS = os.path.join(GD, "source-photos")
HEADERS = os.path.join(GD, "headers")

# photo: file in graphic-design/source-photos/; size: working size (None = native); b: triangle base (photo px);
# K: wordmark cell = K bases; crop: x0, y0, width, height; wm: (centre x, baseline y), photo px.
PRESETS = {
    "earthset": dict(photo="art002e009288orig.jpg", size=(2576, 1717), b=15.0, K=2,
                     crop=(0, 620, 1900, 594), wm=(375, 1008), out="almaha-header-earthset.svg"),
    "crescent": dict(photo="art002e021110~large.jpg", size=None, b=6.0, K=3,
                     crop=(0, 330, 1920, 600), wm=(1650, 680), out="almaha-header-crescent.svg"),
    "edge":     dict(photo="art002e009285~large.jpg", size=None, b=6.0, K=3,
                     crop=(0, 346, 1920, 600), wm=(960, 700), out="almaha-header-edge.svg"),
    # K=1: wordmark stem width (20 units) = one triangle base = the trapezoids' short edge
    "edge-coarse": dict(photo="art002e009285~large.jpg", size=None, b=18.0, K=1,
                     crop=(0, 346, 1920, 600), wm=(960, 700), out="almaha-header-edge-coarse.svg"),
    "horizon":  dict(photo="art002e021219~large.jpg", size=None, b=7.0, K=3,
                     crop=(0, 40, 1920, 600), wm=(250, 400), out="almaha-header-horizon.svg"),
}

if len(sys.argv) < 2 or sys.argv[1] == "--list" or sys.argv[1] not in PRESETS:
    print("presets:", ", ".join(PRESETS)); sys.exit(0 if len(sys.argv) > 1 and sys.argv[1] == "--list" else 1)
P = PRESETS[sys.argv[1]]
out_png = sys.argv[2] if len(sys.argv) > 2 else None
out_svg = os.path.join(HEADERS, P["out"])

b, K = P["b"], P["K"]
h = b * 37.32 / 20.0
S = K * b / 20.0
X0, Y0, BW, BH = P["crop"]
WM_CX, WM_BASE = P["wm"]
WM_COL = "#f4f2ee"

im = np.asarray(wordmark.load_photo(os.path.join(PHOTOS, P["photo"]), P["size"])).astype(np.float64)
H, W, _ = im.shape
r, g, _tri = labels(W, H, b, h)
G0 = 12
GM = int(2 * W / b / 3) + 30
key = ((r + 2) * GM + (g + G0)).ravel()
cnt = np.bincount(key)
mean = np.stack([np.bincount(key, weights=im[..., c].ravel()) / np.maximum(cnt, 1) for c in range(3)], axis=1)

def hexc(v): return "#%02x%02x%02x" % tuple(int(round(min(255, max(0, x)))) for x in v)

cells = []
for rr in range(-1, int(H / h) + 3):
    for gg in range(-G0 + 1, GM - G0):
        kid = (rr + 2) * GM + (gg + G0)
        if kid < 0 or kid >= len(cnt) or cnt[kid] == 0:
            continue
        pts = group_geometry(b, h, rr, gg)
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        if max(ys) < Y0 or min(ys) > Y0 + BH or max(xs) < X0 or min(xs) > X0 + BW:
            continue
        cells.append((pts, hexc(mean[kid])))

# wordmark: nearest baseline row, then snap x so art x=10 (mod 20) lands on a lattice vertex
m = round(WM_BASE / h)
ty = m * h - 245 * S
t = (m % 2) * b / 2 - K * b / 2
tx = t + round((WM_CX - 250 * S - t) / b) * b

sw = max(0.6, b * 0.05)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{X0} {Y0} {BW} {BH}" width="{BW}" height="{BH}" role="img" aria-label="al-maha wordmark over an Artemis II photograph rendered as a trapezoid mosaic">',
       '<title>al-maha</title>',
       f'<rect x="{X0}" y="{Y0}" width="{BW}" height="{BH}" fill="#000"/>',
       f'<g stroke-width="{sw:.2f}" stroke-linejoin="round">']
for pts, c in cells:
    svg.append('<polygon points="%s" fill="%s" stroke="%s"/>' % (" ".join(f"{x:.1f},{y:.1f}" for x, y in pts), c, c))
svg += ['</g>',
        f'<path transform="translate({tx:.3f} {ty:.3f}) scale({S})" fill="{WM_COL}" fill-rule="evenodd" d="{wordmark.path_d()}"/>',
        '</svg>']
open(out_svg, "w").write("\n".join(svg))
print(P["out"], "cells:", len(cells), "bytes:", os.path.getsize(out_svg),
      "wordmark x:", round(tx + 50 * S), "-", round(tx + 450 * S), "y:", round(ty + 133.04 * S), "-", round(m * h))

if out_png:
    from PIL import Image, ImageDraw
    k = 2
    img = Image.new("RGB", (BW * k, BH * k), "black")
    dr = ImageDraw.Draw(img)
    for pts, c in cells:
        dr.polygon([((x - X0) * k, (y - Y0) * k) for x, y in pts], fill=c, outline=c)
    T = lambda x, y: ((tx + x * S - X0) * k, (ty + y * S - Y0) * k)
    for gm in wordmark.geoms:
        dr.polygon([T(x, y) for x, y in gm.exterior.coords], fill=WM_COL)
        for hole in gm.interiors:
            dr.polygon([T(x, y) for x, y in hole.coords], fill="black")
    img.resize((BW, BH), Image.LANCZOS).save(out_png)
