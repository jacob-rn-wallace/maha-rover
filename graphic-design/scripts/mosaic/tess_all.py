import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import wordmark
import math, sys
import numpy as np
from PIL import Image, ImageDraw
from trap import group_geometry

im = np.asarray(wordmark.load_photo()).astype(np.float64)
H, W, _ = im.shape
cx, Wc = 1188, 1144
x0 = cx - Wc // 2
crop = im[:, x0:x0 + Wc]

def vis(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return max(xs) >= x0 - 2 and min(xs) <= x0 + Wc + 2 and max(ys) >= -2 and min(ys) <= H + 2

def hexc(v): return "#%02x%02x%02x" % tuple(int(round(min(255, max(0, x)))) for x in v)

def colorize(polys):
    polys = [p for p in polys if vis(p)]
    lab = Image.new("I", (Wc, H), 0)
    dr = ImageDraw.Draw(lab)
    for i, p in enumerate(polys, 1):
        dr.polygon([(x - x0, y) for x, y in p], fill=i)
    L = np.asarray(lab).ravel()
    cnt = np.bincount(L, minlength=len(polys) + 1)
    cols = np.stack([np.bincount(L, weights=crop[..., c].ravel(), minlength=len(polys) + 1) / np.maximum(cnt, 1)
                     for c in range(3)], axis=1)
    return [(p, hexc(cols[i + 1])) for i, p in enumerate(polys) if cnt[i + 1] > 0]

# ---------- tilings ----------
def tiling_trapezoids(b=18.0):
    h = b * 0.8660254
    out = []
    for r in range(-1, int(H / h) + 3):
        for g in range(-30, int(2 * W / b / 3) + 30):
            out.append(group_geometry(b, h, r, g))
    return out

def tiling_star8(d=28.0):
    e = d / (1 + math.sqrt(2))
    R = (d / 2) / math.cos(math.pi / 8)
    rin = R * 0.76536686
    def ang(a): return (math.cos(math.radians(a)), math.sin(math.radians(a)))
    def V(c, k): u = ang(22.5 + 45 * k); return (c[0] + R * u[0], c[1] + R * u[1])
    def I(c, theta): u = ang(theta); return (c[0] + rin * u[0], c[1] + rin * u[1])
    out = []
    ni = int(Wc / d) + 6; nj = int(H / d) + 6
    ox = x0 - 3 * d
    for j in range(-2, nj):
        for i in range(ni):
            c = (ox + i * d, j * d)
            # star
            star = []
            for k in range(8):
                star.append(V(c, k)); star.append(I(c, 45 * (k + 1)))
            out.append(star)
            # rhombus to the right (edge mid-dir 0) and below (mid-dir 90)
            for th in (0, 90):
                u = ang(th); n = (c[0] + d * u[0], c[1] + d * u[1])
                k = (th // 45 - 1) % 8                      # edge index with mid-dir th
                kn = ((th + 180) // 45 - 1) % 8
                va, vb = V(c, k), V(c, (k + 1) % 8)
                out.append([va, I(c, th), vb, I(n, th + 180)])
            # cross at the hole to the lower-right
            h = (c[0] + d / 2, c[1] + d / 2)
            q = e / math.sqrt(2)
            sq = {"N": (h[0], h[1] - q), "E": (h[0] + q, h[1]), "S": (h[0], h[1] + q), "W": (h[0] - q, h[1])}
            def apex(sx, sy):
                o = (h[0] + sx * d / 2, h[1] + sy * d / 2)
                phi = math.degrees(math.atan2(-sy, -sx))
                return I(o, phi)
            out.append([sq["N"], apex(1, -1), sq["E"], apex(1, 1), sq["S"], apex(-1, 1), sq["W"], apex(-1, -1)])
    return out

def tiling_3464(a=18.0):
    D = a * (1 + math.sqrt(3))
    e1 = (D, 0.0); e2 = (D / 2, D * math.sqrt(3) / 2)
    def site(i, j): return (i * e1[0] + j * e2[0], i * e1[1] + j * e2[1])
    out = []
    jmax = int(H / e2[1]) + 4; imax = int(Wc / D) + 8
    for j in range(-3, jmax):
        for i in range(-imax, imax + imax):
            p = site(i, j); p = (p[0] + x0 - 0, p[1])
            # skip sites far outside
            if p[0] < x0 - 3 * D or p[0] > x0 + Wc + 3 * D: continue
            def S(ii, jj):
                q = site(ii, jj); return (q[0] + x0, q[1])
            c = p
            hexa = [(c[0] + a * math.cos(math.radians(30 + 60 * k)), c[1] + a * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
            out.append(hexa)
            for (di, dj) in ((1, 0), (0, 1), (-1, 1)):
                q = S(i + di, j + dj)
                ux, uy = q[0] - c[0], q[1] - c[1]; L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
                nx, ny = -uy, ux
                mp = (c[0] + a * math.sqrt(3) / 2 * ux, c[1] + a * math.sqrt(3) / 2 * uy)
                mq = (q[0] - a * math.sqrt(3) / 2 * ux, q[1] - a * math.sqrt(3) / 2 * uy)
                out.append([(mp[0] + a / 2 * nx, mp[1] + a / 2 * ny), (mq[0] + a / 2 * nx, mq[1] + a / 2 * ny),
                            (mq[0] - a / 2 * nx, mq[1] - a / 2 * ny), (mp[0] - a / 2 * nx, mp[1] - a / 2 * ny)])
            for tri in (((i, j), (i + 1, j), (i, j + 1)), ((i + 1, j), (i, j + 1), (i + 1, j + 1))):
                ps = [S(*t) for t in tri]
                g = (sum(x for x, _ in ps) / 3, sum(y for _, y in ps) / 3)
                v = []
                for (px, py) in ps:
                    ux, uy = g[0] - px, g[1] - py; L = math.hypot(ux, uy)
                    v.append((px + a * ux / L, py + a * uy / L))
                out.append(v)
    return out

# ---------- wordmark ----------
WM = wordmark.path_d()
S = 1.2
tx = cx - 250 * S; ty = 1612.2 - 245 * S

def write_svg(name, cells):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} 0 {Wc} {H}" width="{Wc}" height="{H}">',
           f'<rect x="{x0}" y="0" width="{Wc}" height="{H}" fill="#000"/>', '<g stroke-width="0.6" stroke-linejoin="round">']
    for pts, c in cells:
        out.append('<polygon points="%s" fill="%s" stroke="%s"/>' % (" ".join(f"{x:.2f},{y:.2f}" for x, y in pts), c, c))
    out += ['</g>', f'<path transform="translate({tx:.3f} {ty:.3f}) scale({S})" fill="#f4f2ee" fill-rule="evenodd" d="{WM}"/>', '</svg>']
    open(f"{name}.svg", "w").write("\n".join(out))

jobs = {"almaha-poster-trapezoid-nogrout": tiling_trapezoids(18.0),
        "almaha-poster-star8": tiling_star8(28.0),
        "almaha-poster-3464": tiling_3464(18.0)}
for name, polys in jobs.items():
    cells = colorize(polys)
    write_svg(name, cells)
    print(name, "cells:", len(cells))
