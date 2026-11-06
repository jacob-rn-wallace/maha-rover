import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import wordmark
import sys
import numpy as np
from PIL import Image
from trap import group_geometry, labels

b = float(sys.argv[1]); name = sys.argv[2]
h = b * 0.8660254               # equilateral triangles: 30 deg legs, like the sketch
S = 1.2
cx, Wc = 1188, 1144
x0 = cx - Wc // 2
GROUT = max(1.0, b * 0.09)
GROUT_COL = "#08080a"

im = np.asarray(wordmark.load_photo()).astype(np.float64)
H, W, _ = im.shape
r, g, (tr, tu, tk) = labels(W, H, b, h)
G0 = 12
GM = int(2 * W / b / 3) + 30
key = ((r + 2) * GM + (g + G0)).ravel()
cnt = np.bincount(key)
mean = np.stack([np.bincount(key, weights=im[..., c].ravel()) / np.maximum(cnt, 1) for c in range(3)], axis=1)

tri_key = ((tr * 2 + tu) * (int(W / b) + 12) + (tk + 4)).ravel()
pair = np.unique(np.stack([key, tri_key], axis=1), axis=0)
per_group = np.bincount(pair[:, 0], minlength=len(cnt))
used = [k for k in range(len(cnt)) if cnt[k] > 0]
print("groups:", len(used), "with !=3 triangles (edge-clipped):", sum(per_group[k] != 3 for k in used))

def hexc(v): return "#%02x%02x%02x" % tuple(int(round(min(255, max(0, x)))) for x in v)
polys = []
for rr in range(-1, int(H / h) + 3):
    for gg in range(-G0 + 1, GM - G0):
        kid = (rr + 2) * GM + (gg + G0)
        if kid < 0 or kid >= len(cnt) or cnt[kid] == 0:
            continue
        pts = group_geometry(b, h, rr, gg)
        xs = [p[0] for p in pts]
        if max(xs) < x0 - 1 or min(xs) > x0 + Wc + 1:
            continue
        polys.append((pts, hexc(mean[kid])))

d = wordmark.path_d()
tx = cx - 250 * S
ty = 1612.2 - 245 * S

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} 0 {Wc} {H}" width="{Wc}" height="{H}">',
       f'<rect x="{x0}" y="0" width="{Wc}" height="{H}" fill="{GROUT_COL}"/>',
       f'<g stroke="{GROUT_COL}" stroke-width="{GROUT:.2f}" stroke-linejoin="miter">']
for pts, c in polys:
    out.append('<polygon points="%s" fill="%s"/>' % (" ".join(f"{x:.2f},{y:.2f}" for x, y in pts), c))
out += ['</g>', f'<path transform="translate({tx:.3f} {ty:.3f}) scale({S})" fill="#f4f2ee" fill-rule="evenodd" d="{d}"/>', '</svg>']
open(f"{name}.svg", "w").write("\n".join(out))
print(name, "cells:", len(polys), "b", b, "h", round(h, 2), "grout", round(GROUT, 2))
