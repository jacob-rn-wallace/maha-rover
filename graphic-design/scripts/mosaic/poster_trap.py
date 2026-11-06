import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import wordmark
import numpy as np
from PIL import Image
from trap import group_geometry, labels

b = 12.0
h = b * 37.32 / 20.0
S = 1.2
cx, Wc = 1188, 1144
x0 = cx - Wc // 2

im = np.asarray(wordmark.load_photo()).astype(np.float64)
H, W, _ = im.shape
r, g, (tr, tu, tk) = labels(W, H, b, h)

G0 = 12
GM = int(2 * W / b / 3) + 30
key = ((r + 2) * GM + (g + G0)).ravel()
cnt = np.bincount(key)
mean = np.stack([np.bincount(key, weights=im[..., c].ravel()) / np.maximum(cnt, 1) for c in range(3)], axis=1)

# sanity: interior groups must hold exactly 3 distinct triangles
tri_key = ((tr * 2 + tu) * (int(W / b) + 12) + (tk + 4)).ravel()
pair = np.unique(np.stack([key, tri_key], axis=1), axis=0)
per_group = np.bincount(pair[:, 0], minlength=len(cnt))
interior = [kid for kid in range(len(cnt)) if cnt[kid] > 0]
bad = [kid for kid in interior if per_group[kid] != 3]
print("groups:", len(interior), "groups without exactly 3 triangles (edge-clipped):", len(bad))

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

# wordmark, same placement as before (edges follow the 12 px triangle lattice)
d = wordmark.path_d()
tx = cx - 250 * S
ty = 72 * h - 245 * S

sw = max(0.6, b * 0.02)
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} 0 {Wc} {H}" width="{Wc}" height="{H}">',
       f'<rect x="{x0}" y="0" width="{Wc}" height="{H}" fill="#000"/>',
       f'<g stroke-width="{sw:.2f}" stroke-linejoin="round">']
for pts, c in polys:
    out.append('<polygon points="%s" fill="%s" stroke="%s"/>' % (" ".join(f"{x:.2f},{y:.2f}" for x, y in pts), c, c))
out += ['</g>', f'<path transform="translate({tx:.3f} {ty:.3f}) scale({S})" fill="#f4f2ee" fill-rule="evenodd" d="{d}"/>', '</svg>']
open("almaha-poster-trapezoid.svg", "w").write("\n".join(out))
print("trapezoids drawn:", len(polys))
