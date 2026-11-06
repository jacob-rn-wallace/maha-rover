import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import wordmark
import sys, math
import numpy as np
from PIL import Image

b = float(sys.argv[1])               # triangle base width in source pixels
out = sys.argv[2]
h = b * (37.32 / 20.0)               # same 20 : 37.32 proportion as the wordmark grid (15 deg lean)

im = np.asarray(wordmark.load_photo()).astype(np.float64)
H, W, _ = im.shape
ys, xs = np.mgrid[0:H, 0:W]
ys = ys + 0.5; xs = xs + 0.5

r = np.floor(ys / h).astype(np.int64)
u = (ys - r * h) / h
s = (r % 2) * b / 2.0
xp = xs - s
t = xp / b
k0 = np.floor(t).astype(np.int64)
f = t - k0
kn = np.where(f < 0.5, k0, k0 + 1)
d = np.abs(xp - kn * b)
is_up = d <= (b / 2.0) * u
k = np.where(is_up, kn, k0)
typ = is_up.astype(np.int64)

M = int(W / b) + 6
key = ((r * 2 + typ) * M + (k + 2)).ravel()
cnt = np.bincount(key)
cols = []
for c in range(3):
    cols.append(np.bincount(key, weights=im[..., c].ravel()) / np.maximum(cnt, 1))
mean = np.stack(cols, axis=1)

def hexc(v): return "#%02x%02x%02x" % tuple(int(round(min(255, max(0, x)))) for x in v)

polys = []
nrows = int(H / h) + 2
ncols = int(W / b) + 3
for rr in range(nrows):
    y0, y1 = rr * h, (rr + 1) * h
    sh = (rr % 2) * b / 2.0
    for kk in range(-2, ncols):
        for tp in (0, 1):
            kid = ((rr * 2 + tp) * M + (kk + 2))
            if kid >= len(cnt) or cnt[kid] == 0:
                continue
            if tp == 1:
                pts = [(sh + kk*b, y0), (sh + kk*b - b/2, y1), (sh + kk*b + b/2, y1)]
            else:
                pts = [(sh + kk*b, y0), (sh + (kk+1)*b, y0), (sh + kk*b + b/2, y1)]
            polys.append((pts, hexc(mean[kid])))

sw = max(0.6, b * 0.02)
lines = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         f'<rect width="{W}" height="{H}" fill="#000"/>',
         f'<g stroke-width="{sw:.2f}" stroke-linejoin="round">']
for pts, c in polys:
    p = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    lines.append(f'<polygon points="{p}" fill="{c}" stroke="{c}"/>')
lines += ['</g>', '</svg>']
open(out, "w").write("\n".join(lines))
print(out, "triangles:", len(polys), "base", b, "height", round(h, 2))
