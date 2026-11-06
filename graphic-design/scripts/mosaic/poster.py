import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import wordmark
import re

SRC_W, SRC_H = 2576, 1717
b = 12.0
h = b * 37.32 / 20.0           # mosaic row height (22.392)
S = 1.2                        # wordmark scale: 20-unit cell -> 24 px = 2 mosaic cells; 37.32 row -> 2 mosaic rows

# --- crop: 2:3 portrait, centred on the Earth (col multiple of 12 so grids line up)
cx = 1188
W = 1144
x0 = cx - W // 2               # 616
H = SRC_H

# --- wordmark (merged outline, original design coordinates)
d = wordmark.path_d()
# wordmark art spans x 50..450 (centre 250), baseline bottom edge at y=245
m = 72                                         # even mosaic row line for the baseline
base_y = m * h                                 # 1612.22
tx = cx - 250 * S                              # centre the art on the crop centre (multiple of 12)
ty = base_y - 245 * S
assert abs(tx / 12 - round(tx / 12)) < 1e-9

# --- keep only mosaic triangles that touch the crop
src = open("earthset-tri-xfine.svg").read().splitlines()
keep = []
for line in src:
    if line.startswith("<polygon"):
        pts = re.search(r'points="([^"]+)"', line).group(1).split()
        xs = [float(p.split(",")[0]) for p in pts]
        if max(xs) >= x0 - 1 and min(xs) <= x0 + W + 1:
            keep.append(line)

sw = max(0.6, b * 0.02)
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} 0 {W} {H}" width="{W}" height="{H}">',
       f'<rect x="{x0}" y="0" width="{W}" height="{H}" fill="#000"/>',
       f'<g stroke-width="{sw:.2f}" stroke-linejoin="round">'] + keep + ['</g>',
       f'<path transform="translate({tx:.3f} {ty:.3f}) scale({S})" fill="#f4f2ee" fill-rule="evenodd" d="{d}"/>',
       '</svg>']
open("almaha-poster-2x3.svg", "w").write("\n".join(out))
print("triangles kept:", len(keep), "crop x0:", x0, "tx:", tx, "baseline y:", round(base_y, 2),
      "wordmark box y:", round(ty + 133.04 * S, 1), "->", round(base_y, 1))
