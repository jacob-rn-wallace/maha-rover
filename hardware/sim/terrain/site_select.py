"""Choose where to put the 5 x 5 km sandbox inside the LROC Atlas crater DTM (hardware/sim/terrain/atlas_tile.py has the file layout).

Reads the full local .IMG (read-only), averages it to an 8 m grid (the papers' slope maps are from the 7.4 m/px Kaguya TC mosaic), and scores every fully covered 5 x 5 km window (about 500 m steps).
The criteria come from the Rashid-1 site-selection paper, Flahaut et al., Space Science Reviews 220:53 (2024), doi 10.1007/s11214-024-01086-x:
  - a candidate area must have at least 95% of its slopes under 15 degrees (their verification step, Sect. 3.3, and the ellipse requirement of slopes under 15 degrees);
  - among the areas that pass, the lowest mean slope is preferred; their Atlas ellipses (Table 2) have mean slope 6.8 to 7.3 degrees (standard deviation 4.2 to 4.6) at 7.4 m/px and 94 to 96% of pixels under 15 degrees;
  - the prime ellipse, FR-11, is at 47.53 N, 44.33 E (mean slope 6.8, 96% under 15 degrees): the search is centred there.
The paper's ellipse is an 8 km circle; the sandbox is a 5 km square, so the statistics are close but not identical.
Reported but not used as criteria: the share of gentle ground (under 4 degrees, for a start area) and the relief.

  python hardware/sim/terrain/site_select.py ~/Downloads/NAC_DTM_ATLAS_E468N0446.IMG CACHE_DIR
"""
import math
import sys
from pathlib import Path

import numpy as np

LINES, SAMPLES, OFFSET = 29426, 10607, 42428
R = 1737400.0
WEST, NORTH = 44.10437844, 47.76639058
POST, CELL = 2.0, 4                        # 2 m posts averaged 4 x 4 into 8 m cells
WIN = 625                                  # 625 cells of 8 m = 5 km
STEP = 63                                  # window steps: 63 cells = 504 m
TARGET = (47.53, 44.33)                    # centre of the prime landing ellipse FR-11 (Flahaut et al. 2024, Table 2); the Hakuto-R impact point is at 47.581 N, 44.094 E (Wikipedia)
# criteria (Flahaut et al. 2024)
MIN_FRAC_UNDER_15 = 0.95                   # at least 95% of slopes under 15 degrees
MAX_MEAN_SLOPE = 7.3                       # the highest mean slope among their Atlas candidate ellipses


def to_ll(line, sample):
    lat = NORTH - line * (POST / R) * 180 / math.pi
    lon = WEST + sample * POST / (R * math.cos(math.radians(47))) * 180 / math.pi
    return lat, lon


def to_ls(lat, lon):
    return (NORTH - lat) / ((POST / R) * 180 / math.pi), (lon - WEST) * math.pi / 180 * R * math.cos(math.radians(47)) / POST


def coarse(img, cache):
    cache = Path(cache)
    f = cache / "atlas_8m.npy"
    if f.exists():
        return np.load(f)
    a = np.memmap(img, dtype="<f4", mode="r", offset=OFFSET, shape=(LINES, SAMPLES))
    ny, nx = LINES // CELL, SAMPLES // CELL
    out = np.full((ny, nx), np.nan, dtype=np.float32)
    for y0 in range(0, ny, 100):
        blk = np.array(a[y0 * CELL:min(ny, y0 + 100) * CELL, :nx * CELL], dtype=np.float32)
        blk[blk < -3e38] = np.nan
        b = blk.reshape(-1, CELL, nx, CELL)
        n = np.sum(~np.isnan(b), axis=(1, 3))
        m = np.nanmean(b, axis=(1, 3))
        m[n < CELL * CELL] = np.nan                                  # any gap in the 20 m cell: treat the cell as missing
        out[y0:y0 + m.shape[0]] = m
    np.save(f, out)
    return out


def main(img, cache):
    Path(cache).mkdir(parents=True, exist_ok=True)
    h = coarse(img, cache)
    print("8 m grid", h.shape, "valid %.1f%%" % (np.mean(~np.isnan(h)) * 100))
    gy, gx = np.gradient(h, 8.0)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    valid = ~np.isnan(h) & ~np.isnan(slope)
    ii = lambda m: np.pad(m.astype(np.int64).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    box = lambda I, y, x: I[y + WIN, x + WIN] - I[y, x + WIN] - I[y + WIN, x] + I[y, x]
    Iv, I15, Iflat = ii(valid), ii(np.nan_to_num(slope) >= 15), ii(np.nan_to_num(slope, nan=99) < 4)
    ny, nx = h.shape
    # block min and max (500 m) for the relief
    bh = np.nan_to_num(h, nan=np.nan)
    nb_y, nb_x = ny // STEP, nx // STEP
    blk = bh[:nb_y * STEP, :nb_x * STEP].reshape(nb_y, STEP, nb_x, STEP)
    with np.errstate(all="ignore"):
        bmin, bmax = np.nanmin(blk, axis=(1, 3)), np.nanmax(blk, axis=(1, 3))
    tl, tc = to_ls(*TARGET)
    rows = []
    for y in range(0, ny - WIN + 1, STEP):
        for x in range(0, nx - WIN + 1, STEP):
            if box(Iv, y, x) != WIN * WIN:
                continue
            by, bx, k = y // STEP, x // STEP, WIN // STEP
            relief = float(np.nanmax(bmax[by:by + k, bx:bx + k]) - np.nanmin(bmin[by:by + k, bx:bx + k]))
            s = slope[y:y + WIN, x:x + WIN]
            p95 = float(np.percentile(s, 95))
            f15 = 1 - box(I15, y, x) / WIN ** 2
            ff = box(Iflat, y, x) / WIN ** 2
            lc, sc = (y + WIN / 2) * CELL, (x + WIN / 2) * CELL
            dkm = math.hypot(lc - tl, sc - tc) * POST / 1000
            lat, lon = to_ll(lc, sc)
            rows.append((dkm, lat, lon, float(np.mean(s)), p95, f15, ff, relief, y * CELL, x * CELL))
    print("fully covered windows:", len(rows))
    ok = [r for r in rows if r[5] >= MIN_FRAC_UNDER_15 and r[3] <= MAX_MEAN_SLOPE]
    print("windows meeting the criteria:", len(ok))
    hdr = "  km-from-FR-11    lat      lon   mean-slope  p95  under-15deg  under-4deg  relief  (line, sample of the corner)"
    for name, sel in (("nearest to FR-11 among the windows that meet the criteria", sorted(ok)[:8]),
                      ("lowest mean slope among the windows that meet the criteria", sorted(ok, key=lambda r: r[3])[:5]),
                      ("for comparison: the window used so far (47.3047 N, 44.8055 E)", [r for r in rows if abs(r[1] - 47.3047) < 0.02 and abs(r[2] - 44.8055) < 0.03][:2])):
        print("\n" + name + "\n" + hdr)
        for r in sel:
            print(f"  {r[0]:8.1f}  {r[1]:8.4f} {r[2]:8.4f}   {r[3]:6.1f}   {r[4]:5.1f}   {r[5] * 100:6.1f}%    {r[6] * 100:6.1f}%  {r[7]:5.0f}  ({r[8]}, {r[9]})")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
