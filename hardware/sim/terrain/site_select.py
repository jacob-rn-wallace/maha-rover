"""Choose where to put the 5 x 5 km sandbox inside the LROC Atlas crater DTM (hardware/sim/terrain/atlas_tile.py has the file layout).

Reads the full local .IMG (read-only), averages it to a 20 m grid, and scores every fully covered 5 x 5 km window (500 m steps) on how well it suits driving al-maha:
slope statistics over 20 m cells (the rover climbs 20 degrees by requirement), the share of gentle ground to start on, relief, and the distance to the Hakuto-R impact point.
The criteria are the assistant's proposal, not sourced: they are set at the top of the file.

  python hardware/sim/terrain/site_select.py ~/Downloads/NAC_DTM_ATLAS_E468N0446.IMG CACHE_DIR
"""
import math
import sys
from pathlib import Path

import numpy as np

LINES, SAMPLES, OFFSET = 29426, 10607, 42428
R = 1737400.0
WEST, NORTH = 44.10437844, 47.76639058
POST, CELL = 2.0, 10                       # 2 m posts averaged 10 x 10 into 20 m cells
WIN = 250                                  # 250 cells of 20 m = 5 km
STEP = 25                                  # window steps: 25 cells = 500 m
TARGET = (47.581, 44.094)                  # Hakuto-R impact point (Wikipedia)
# criteria
MAX_FRAC_OVER_20 = 0.02                    # at most 2% of the area steeper than 20 degrees (the rover's slope requirement)
MIN_FLAT_FRAC = 0.10                       # at least 10% under 4 degrees, to start on
P95_RANGE = (8.0, 16.0)                    # enough slope to exercise the suspension, not a wall
RELIEF_RANGE = (60.0, 250.0)               # metres over the window


def to_ll(line, sample):
    lat = NORTH - line * (POST / R) * 180 / math.pi
    lon = WEST + sample * POST / (R * math.cos(math.radians(47))) * 180 / math.pi
    return lat, lon


def to_ls(lat, lon):
    return (NORTH - lat) / ((POST / R) * 180 / math.pi), (lon - WEST) * math.pi / 180 * R * math.cos(math.radians(47)) / POST


def coarse(img, cache):
    cache = Path(cache)
    f = cache / "atlas_20m.npy"
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
    print("20 m grid", h.shape, "valid %.1f%%" % (np.mean(~np.isnan(h)) * 100))
    gy, gx = np.gradient(h, 20.0)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    valid = ~np.isnan(h) & ~np.isnan(slope)
    ii = lambda m: np.pad(m.astype(np.int64).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    box = lambda I, y, x: I[y + WIN, x + WIN] - I[y, x + WIN] - I[y + WIN, x] + I[y, x]
    Iv, I20, Iflat = ii(valid), ii(np.nan_to_num(slope) > 20), ii(np.nan_to_num(slope, nan=99) < 4)
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
            f20 = box(I20, y, x) / WIN ** 2
            ff = box(Iflat, y, x) / WIN ** 2
            lc, sc = (y + WIN / 2) * CELL, (x + WIN / 2) * CELL
            dkm = math.hypot(lc - tl, sc - tc) * POST / 1000
            lat, lon = to_ll(lc, sc)
            rows.append((dkm, lat, lon, float(np.mean(s)), p95, f20, ff, relief, y * CELL, x * CELL))
    print("fully covered windows:", len(rows))
    ok = [r for r in rows if r[5] <= MAX_FRAC_OVER_20 and r[6] >= MIN_FLAT_FRAC and P95_RANGE[0] <= r[4] <= P95_RANGE[1] and RELIEF_RANGE[0] <= r[7] <= RELIEF_RANGE[1]]
    print("windows meeting the criteria:", len(ok))
    hdr = "  km-from-target    lat      lon   mean-slope  p95  >20deg  <4deg  relief  (line, sample of the corner)"
    for name, sel in (("nearest to the target among the windows that meet the criteria", sorted(ok)[:8]),
                      ("for comparison: the nearest covered window of any kind (the tile built so far)", sorted(rows)[:2])):
        print("\n" + name + "\n" + hdr)
        for r in sel:
            print(f"  {r[0]:8.1f}  {r[1]:8.4f} {r[2]:8.4f}   {r[3]:6.1f}   {r[4]:5.1f}  {r[5] * 100:5.1f}% {r[6] * 100:5.1f}%  {r[7]:5.0f}  ({r[8]}, {r[9]})")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
