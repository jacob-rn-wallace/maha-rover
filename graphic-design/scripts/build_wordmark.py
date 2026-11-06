import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wordmark

u = wordmark.merged
geoms = wordmark.geoms
minx, miny, maxx, maxy = u.bounds
pad = 20
ox, oy = pad - minx, pad - miny

d = wordmark.path_d(ox, oy)
W, H = maxx - minx + 2 * pad, maxy - miny + 2 * pad
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.2f} {H:.2f}">\n'
       f'<title>almaha wordmark, square kufic, 15 degree slanted grid</title>\n'
       f'<path fill="#000" fill-rule="evenodd" d="{d}"/>\n</svg>\n')
out = os.path.join(HERE, "..", "wordmark", "almaha-wordmark.svg")
open(out, "w").write(svg)
print("islands:", len(geoms), "holes:", sum(len(g.interiors) for g in geoms), "size:", round(W,2), round(H,2))
