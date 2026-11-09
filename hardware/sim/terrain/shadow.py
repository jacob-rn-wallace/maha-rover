"""Terrain shadows for the simulation's fixed sun: which ground is in the shadow of other terrain (hills, the crater rim), as two textures the terrain shader samples.

The sun is fixed (`sim/src/lunar.ts`: elevation 14 degrees, azimuth 40 degrees; in the sim's world frame, x east, z south, the sun direction is (cos el cos az, sin el, -cos el sin az),
so the ground-plane direction towards the sun is east cos az, north sin az). The dynamic shadow map of the renderer only covers 4 m round the rover (the rover's own shadow and
rocks); this is everything larger.

Method: a point is lit if no terrain between it and the sun stands above the ray towards the sun. In a frame whose u axis points away from the sun, a point k is shadowed when
max over j < k of (h_j + T u_j) exceeds h_k + T u_k, T = tan(sun elevation): a running maximum along u, one pass per column (vectorised). The margin (how far the point stands below
the sun plane of the highest blocker) gives a soft edge: lit fraction = clip(1 + margin / SOFT, 0, 1) with SOFT = 2 m, on the shadow side only (the sun's disc, 0.53 degrees, gives a penumbra of 1% of the
distance to the blocker: 1 m at 100 m, 10 m at 1 km; a fixed width is a simplification). Lunar curvature is not in the shadow geometry (at 10 km it lowers the ground by 29 m, which
would shorten the longest shadows slightly).

Elevation: the 2 m Atlas tile (raw posts, `sim/public/terrain/atlas_5km.png`) inside the tile, the combined 8 m grid out to 16 km, the 48 m grid to 100 km (the viewshed's caches, see viewshed.py); blockers beyond
100 km are not modelled. Outputs (8-bit, 255 = lit, row 0 = north, columns west to east):
  shadow_tile.png    the tile at 4 m (1250 x 1250)
  shadow_coarse.png  +-100 km at 100 m (2000 x 2000)
  shadow.json        extents, sun, softness

  python hardware/sim/terrain/shadow.py CACHE_DIR OUT_DIR [sun_elevation_deg sun_azimuth_deg]
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

SOFT = 2.0                                   # metres of margin over which the shadow edge fades
TILE_HALF, TILE_POST = 2500.0, 2.0
FINE_HALF, FINE_STEP = 16000.0, 8.0          # viewshed.py grids
COARSE_HALF, COARSE_STEP = 100000.0, 48.0


class Model:
    """elevation (m above the sphere) at world positions (x east, y north, metres from the tile centre)"""

    def __init__(self, cache, tile_png, tile_json):
        self.fine = np.load(Path(cache) / "grid_fine.npy")
        self.coarse = np.load(Path(cache) / "grid_coarse.npy")
        t = json.load(open(tile_json))
        raw = np.array(Image.open(tile_png)).astype(np.float32)
        self.tile = raw / 65535 * (t["height_max_m"] - t["height_min_m"]) + t["height_min_m"]

    def _grid(self, g, half, step, x, y):
        return ndimage.map_coordinates(g, [(half - y) / step, (x + half) / step], order=1, mode="nearest")

    def __call__(self, x, y):
        h = self._grid(self.coarse, COARSE_HALF, COARSE_STEP, x, y)
        inf = (np.abs(x) <= FINE_HALF) & (np.abs(y) <= FINE_HALF)
        if inf.any():
            h = np.where(inf, self._grid(self.fine, FINE_HALF, FINE_STEP, x, y), h)
        int_ = (np.abs(x) <= TILE_HALF) & (np.abs(y) <= TILE_HALF)
        if int_.any():
            t = ndimage.map_coordinates(self.tile, [(TILE_HALF - y) / TILE_POST - 0.5, (x + TILE_HALF) / TILE_POST - 0.5], order=1, mode="nearest")
            h = np.where(int_, t, h)
        h = np.where((np.abs(x) > COARSE_HALF) | (np.abs(y) > COARSE_HALF), -1e5, h)    # beyond the model: no blockers
        return h


def shadow_map(model, out_half, out_step, grid_step, lead, el_deg, az_deg):
    """lit fraction (0..1) on a square of half width out_half at out_step; blockers up to `lead` metres towards the sun beyond it"""
    el, az = math.radians(el_deg), math.radians(az_deg)
    T = math.tan(el)
    sx, sy = math.cos(az), math.sin(az)                    # towards the sun, in (east, north)
    ex, ey = -sx, -sy                                      # e_u: away from the sun
    vx, vy = -ey, ex                                       # e_v: perpendicular
    diag = out_half * math.sqrt(2)
    us = np.arange(-(diag + lead), diag + grid_step, grid_step)
    vs = np.arange(-diag, diag + grid_step, grid_step)
    U, V = np.meshgrid(us, vs, indexing="ij")
    H = np.empty(U.shape, np.float32)
    for i0 in range(0, len(us), 400):                      # in chunks: the model lookups are the cost
        u, v = U[i0:i0 + 400], V[i0:i0 + 400]
        H[i0:i0 + 400] = model(u * ex + v * vx, u * ey + v * vy)
    S = H + T * U                                          # height of the sun plane through the point, at u = 0
    prev = np.concatenate([np.full((1, S.shape[1]), -1e9, np.float32), np.maximum.accumulate(S, axis=0)[:-1]], axis=0)
    margin = S - prev                                      # >0: above every blocker towards the sun
    lit = np.clip(1.0 + margin / SOFT, 0, 1).astype(np.float32)           # 1 where the point clears every blocker; falls to 0 within SOFT metres below the sun plane (one-sided: flat lit ground clears the previous sample by only T x step)
    # sample at the output texels
    n = int(round(2 * out_half / out_step))
    c = -out_half + out_step * (np.arange(n) + 0.5)
    X, Y = np.meshgrid(c, c[::-1])                         # row 0 = north
    u, v = X * ex + Y * ey, X * vx + Y * vy
    return ndimage.map_coordinates(lit, [(u - us[0]) / grid_step, (v - vs[0]) / grid_step], order=1, mode="nearest")


def main(cache, out, el=14.0, az=40.0):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    here = Path(__file__).resolve().parents[3] / "sim" / "public" / "terrain"
    model = Model(cache, here / "atlas_5km.png", here / "atlas_5km.json")
    tile = shadow_map(model, TILE_HALF, 4.0, 4.0, 30000.0, el, az)
    Image.fromarray(np.round(tile * 255).astype(np.uint8)).save(out / "shadow_tile.png")
    print(f"tile: {(tile < 0.5).mean() * 100:.1f}% of the ground in shadow")
    coarse = shadow_map(model, COARSE_HALF, 100.0, 100.0, 60000.0, el, az)
    Image.fromarray(np.round(coarse * 255).astype(np.uint8)).save(out / "shadow_coarse.png")
    print(f"coarse: {(coarse < 0.5).mean() * 100:.1f}% in shadow")
    json.dump({"sun_elevation_deg": el, "sun_azimuth_deg": az, "azimuth_note": "sim world frame: sun direction (cos el cos az, sin el, -cos el sin az), x east, z south",
               "tile": {"half_m": TILE_HALF, "size_px": tile.shape[0]}, "coarse": {"half_m": COARSE_HALF, "size_px": coarse.shape[0]}, "soft_m": SOFT,
               "rows": "row 0 = north (z = -half), columns west to east", "values": "255 = lit"}, open(out / "shadow.json", "w"), indent=1)


if __name__ == "__main__":
    if len(sys.argv) not in (3, 5):
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], *(float(a) for a in sys.argv[3:]))
