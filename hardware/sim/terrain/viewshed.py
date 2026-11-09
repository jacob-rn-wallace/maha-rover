"""Viewshed of the 5 x 5 km sandbox: which terrain beyond the tile can be seen from it, as a low-detail ring for the simulation.

Method (the owner's plan, docs/sim-handoff.md step 1): the rover's camera is 0.7 m above the ground; from observer points on the tile's edge and inside it, rays are
swept outward over a combined elevation model (LROC Atlas DTM where it has coverage, LOLA LDEM_128 elsewhere) and a post is visible if its elevation angle,
measured from the observer's local horizontal on the sphere (R 1737.4 km, so the lunar curvature is in the geometry), exceeds that of every nearer post along the ray.
The union over the observers is the part of the ring worth keeping.

Geometry: everything is in an azimuthal equidistant frame about the tile centre (x east, y north, metres). Distances from the centre are exact in it and tangential
distances stretch by delta / sin(delta), 0.05% at 100 km, so rays are straight lines in the plane with the curvature taken in the elevation-angle formula.

Sources (both public domain, see NOTICE.md): LROC NAC DTM NAC_DTM_ATLAS_E468N0446 (2 m posts, block-averaged to 8 m here) and LDEM_128 (237 m/px, pixel registered,
height = DN x 0.5 m above the 1737.4 km sphere). Atlas and LDEM are taken to share that vertical datum; `prep` reports their difference over the Atlas area.

  python hardware/sim/terrain/viewshed.py prep ATLAS.IMG LDEM.img CACHE_DIR     # builds the 8 m Atlas block means and the two combined grids (a few minutes)
  python hardware/sim/terrain/viewshed.py run CACHE_DIR OUT_DIR                 # sweeps the observers, writes ring.png, ring_mask.png, ring.json and a preview
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

R = 1737400.0
PHI1 = math.radians(47.0)
LINES, SAMPLES, OFFSET, POST = 29426, 10607, 42428, 2.0           # Atlas label, as in atlas_tile.py
WEST, NORTH = 44.10437844, 47.76639058
MISSING = -3.0e38
LAT0, LON0 = 47.5676, 44.8102                                      # tile centre (atlas_tile.py)
HALF = 2500.0                                                      # tile half-width, m
BLK = 4                                                            # Atlas 2 m posts to 8 m cells
FINE = dict(half=16000.0, step=8.0)                                # grid A: near field at 8 m
COARSE = dict(half=100000.0, step=48.0)                            # grid B: whole range at 48 m
EYE = 0.7                                                          # camera height above ground, m (the mast head's camera sits at 0.7 m)
RMAX = 100000.0
N_AZ = 1440                                                        # ring: 0.25 degree bins, radial spacing grows with range so cells stay square
R0 = 2500.0
GROW = 1 + 2 * math.pi / N_AZ


def ring_edges():
    n = int(math.ceil(math.log(RMAX / R0) / math.log(GROW)))
    return R0 * GROW ** np.arange(n + 1)


def inverse(x, y):
    """azimuthal equidistant (x east, y north, m) about the tile centre -> lat, lon in degrees"""
    p0, l0 = math.radians(LAT0), math.radians(LON0)
    d = np.hypot(x, y)
    c = d / R
    with np.errstate(invalid="ignore", divide="ignore"):
        s = np.where(d > 0, y / d, 0.0)                            # cos bearing
        t = np.where(d > 0, x / d, 0.0)                            # sin bearing
    lat = np.arcsin(np.clip(math.sin(p0) * np.cos(c) + math.cos(p0) * np.sin(c) * s, -1, 1))
    lon = l0 + np.arctan2(t * np.sin(c) * math.cos(p0), np.cos(c) - math.sin(p0) * np.sin(lat))
    return np.degrees(lat), np.degrees(lon)


def bilinear(a, fy, fx):
    """bilinear sample of a (NaN = missing, propagates) at fractional rows fy and columns fx (pixel centres at integers); outside the array gives NaN"""
    h, w = a.shape
    ok = (fy >= 0) & (fy <= h - 1) & (fx >= 0) & (fx <= w - 1)
    fy, fx = np.clip(fy, 0, h - 1 - 1e-9), np.clip(fx, 0, w - 1 - 1e-9)
    y0, x0 = fy.astype(np.int64), fx.astype(np.int64)
    wy, wx = fy - y0, fx - x0
    v = (a[y0, x0] * (1 - wy) * (1 - wx) + a[y0, x0 + 1] * (1 - wy) * wx + a[y0 + 1, x0] * wy * (1 - wx) + a[y0 + 1, x0 + 1] * wy * wx)
    return np.where(ok, v, np.nan)


def atlas_block_means(img, cache):
    f = Path(cache) / "atlas8.npy"
    if f.exists():
        return np.load(f)
    full = np.memmap(img, dtype="<f4", mode="r", offset=OFFSET, shape=(LINES, SAMPLES))
    nb_l, nb_s = LINES // BLK, SAMPLES // BLK
    out = np.full((nb_l, nb_s), np.nan, np.float32)
    step = 100
    for i0 in range(0, nb_l, step):
        i1 = min(i0 + step, nb_l)
        a = np.array(full[i0 * BLK:i1 * BLK, :nb_s * BLK], dtype=np.float64)
        ok = a > MISSING
        s = np.where(ok, a, 0.0).reshape(i1 - i0, BLK, nb_s, BLK).sum((1, 3))
        n = ok.reshape(i1 - i0, BLK, nb_s, BLK).sum((1, 3))
        out[i0:i1] = np.where(n >= BLK * BLK // 2, s / np.maximum(n, 1), np.nan)   # a cell needs at least half its posts
    np.save(f, out)
    return out


def sample_atlas(a8, lat, lon):
    sample = (lon - WEST) * math.pi / 180 * R * math.cos(PHI1) / POST
    line = (NORTH - lat) * math.pi / 180 * R / POST
    return bilinear(a8, (line - (BLK - 1) / 2) / BLK, (sample - (BLK - 1) / 2) / BLK)


def sample_ldem(crop, r0, c0, lat, lon):
    """LDEM height by cubic spline (a bilinear sample shows the 237 m pixels as blocks in the rendered ring)"""
    from scipy import ndimage
    return ndimage.map_coordinates(crop, [(90 - lat) * 128 - 0.5 - r0, lon * 128 - 0.5 - c0], order=3, mode="nearest").astype(np.float32)


def build_grid(a8, crop, r0, c0, half, step):
    """combined elevation grid (rows north to south, columns west to east): Atlas wherever it has data, LDEM elsewhere, joined without a step.
    The two sources differ by about 17 m (standard deviation) where they meet, which showed up in the simulation as a lit scarp along the Atlas coverage edge. Outside the Atlas
    the LDEM is shifted by the Atlas-minus-LDEM difference averaged over about 200 m round the edge, the shift fading with distance (1.5 km); inside, the Atlas's outer 150 m is
    eased onto the same surface, so the join is continuous. Returns the grid and the Atlas coverage fraction"""
    from scipy import ndimage
    n = int(2 * half / step) + 1
    xs = -half + step * np.arange(n)
    la = np.empty((n, n), np.float32)
    ld = np.empty((n, n), np.float32)
    for i0 in range(0, n, 250):
        i1 = min(i0 + 250, n)
        y = (half - step * np.arange(i0, i1))[:, None] + 0 * xs[None, :]
        x = xs[None, :] + 0 * y
        lat, lon = inverse(x, y)
        la[i0:i1] = sample_atlas(a8, lat, lon)
        ld[i0:i1] = sample_ldem(crop, r0, c0, lat, lon)
    valid = np.isfinite(la)
    cover = float(valid.mean())
    if not valid.any():
        return ld, cover
    sigma = 200.0 / step
    diff = np.where(valid, la - ld, 0.0).astype(np.float64)
    den = ndimage.gaussian_filter(valid.astype(np.float64), sigma)
    local = ndimage.gaussian_filter(diff, sigma) / np.maximum(den, 1e-3)        # mean difference near each point, from the Atlas cells around it
    dist_out = ndimage.distance_transform_edt(~valid) * step                    # metres from the Atlas area (outside it)
    dist_in = ndimage.distance_transform_edt(valid) * step                      # metres from its edge (inside it)
    w = np.exp(-dist_out / 1500.0) * np.clip((den - 0.01) / 0.1, 0.0, 1.0) ** 2         # the local difference is only trusted where Atlas cells surround the point: fades out smoothly (a hard cut left a step)
    outside = ld + (local * w).astype(np.float32)
    inside = la - ((diff - local) * np.exp(-dist_in / 150.0)).astype(np.float32)
    g = np.where(valid, inside, outside).astype(np.float32)
    return g, cover


def prep(img, ldem, cache):
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    a8 = atlas_block_means(img, cache)
    print("Atlas 8 m cells", a8.shape, f"{np.isfinite(a8).mean() * 100:.1f}% valid")
    # LDEM crop covering +-RMAX around the centre (plus margin)
    dlat = RMAX / R * 180 / math.pi * 1.1
    dlon = dlat / math.cos(math.radians(LAT0 + dlat))
    r0, r1 = int((90 - LAT0 - dlat) * 128), int((90 - LAT0 + dlat) * 128) + 2
    c0, c1 = int((LON0 - dlon) * 128), int((LON0 + dlon) * 128) + 2
    full = np.memmap(ldem, dtype="<i2", mode="r", shape=(23040, 46080))
    crop = np.array(full[r0:r1, c0:c1], dtype=np.float32) * 0.5
    print("LDEM crop", crop.shape, f"{crop.min():.0f} to {crop.max():.0f} m")
    # datum check on the Atlas area: Atlas 8 m cells against LDEM at the same places
    ii, jj = np.mgrid[0:a8.shape[0]:16, 0:a8.shape[1]:16]
    m = np.isfinite(a8[ii, jj])
    la_deg = NORTH - (ii[m] * BLK + (BLK - 1) / 2) * POST / R * 180 / math.pi
    lo_deg = WEST + (jj[m] * BLK + (BLK - 1) / 2) * POST / (R * math.cos(PHI1)) * 180 / math.pi
    ld = sample_ldem(crop, r0, c0, la_deg, lo_deg)
    d = a8[ii, jj][m] - ld
    d = d[np.isfinite(d)]
    print(f"Atlas minus LDEM over {d.size} points: mean {d.mean():.1f} m, median {np.median(d):.1f}, std {d.std():.1f}, 5/95%: {np.percentile(d, 5):.1f} {np.percentile(d, 95):.1f}")
    for name, spec in (("fine", FINE), ("coarse", COARSE)):
        g, cov = build_grid(a8, crop, r0, c0, **spec)
        np.save(cache / f"grid_{name}.npy", g)
        print(name, g.shape, f"Atlas covers {cov * 100:.1f}%", f"{np.isnan(g).sum()} NaN")
    json.dump({"fine": FINE, "coarse": COARSE}, open(cache / "grids.json", "w"))


def grid_sample(gf, gc, x, y):
    """height at (x, y) from the fine grid inside its extent, else the coarse grid"""
    nf, nc = gf.shape[0], gc.shape[0]
    fx = (x + FINE["half"]) / FINE["step"]
    fy = (FINE["half"] - y) / FINE["step"]
    inside = (fx >= 0) & (fx <= nf - 1) & (fy >= 0) & (fy <= nf - 1)
    hf = bilinear(gf, fy, fx)
    hc = bilinear(gc, (COARSE["half"] - y) / COARSE["step"], (x + COARSE["half"]) / COARSE["step"])
    return np.where(inside, hf, hc)


def sweep(gf, gc, ox, oy, nrays=7200, block=400):
    """visible posts seen from (ox, oy) as arrays of x, y; the camera is EYE above the ground there"""
    h0 = float(grid_sample(gf, gc, np.array([ox]), np.array([oy]))[0]) + EYE
    ds = np.concatenate([np.arange(4.0, 16000.0, 8.0), np.arange(16000.0, RMAX, 48.0)])
    c = ds / R
    vx, vy = [], []
    for a0 in range(0, nrays, block):
        az = (a0 + np.arange(block) + 0.5) * 2 * math.pi / nrays
        x = ox + np.sin(az)[:, None] * ds[None, :]
        y = oy + np.cos(az)[:, None] * ds[None, :]
        h = grid_sample(gf, gc, x, y)
        # elevation angle (tangent) of a post at height h and central angle c from an eye at height h0, on the sphere of radius R
        tan = ((R + h) * np.cos(c)[None, :] - (R + h0)) / ((R + h) * np.sin(c)[None, :])
        tan = np.where(np.isnan(tan), -np.inf, tan)
        prev = np.maximum.accumulate(tan, axis=1)
        vis = tan >= np.concatenate([np.full((block, 1), -np.inf), prev[:, :-1]], axis=1)
        vis &= np.isfinite(tan)
        vx.append(x[vis])
        vy.append(y[vis])
    return np.concatenate(vx), np.concatenate(vy)


def observers():
    pts = []
    n = 6                                                          # edge: 6 points a side (corners shared) -> 20 points
    for k in range(n):
        t = -HALF + 2 * HALF * k / n
        pts += [(t, -HALF), (HALF, t), (-t, HALF), (-HALF, -t)]
    for gx in (-1, 0, 1):                                          # inside: 3 x 3 lattice at 1.5 km
        for gy in (-1, 0, 1):
            pts.append((gx * 1500.0, gy * 1500.0))
    return pts


def run(cache, out):
    from PIL import Image
    cache, out = Path(cache), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    gf, gc = np.load(cache / "grid_fine.npy"), np.load(cache / "grid_coarse.npy")
    edges = ring_edges()
    nr = len(edges) - 1
    count = np.zeros((nr, N_AZ), np.int32)
    pts = observers()
    for k, (ox, oy) in enumerate(pts):
        vx, vy = sweep(gf, gc, ox, oy)
        r = np.hypot(vx, vy)
        az = np.arctan2(vx, vy) % (2 * math.pi)
        keep = (r >= R0) & (r < edges[-1])
        ri = np.searchsorted(edges, r[keep], side="right") - 1
        ai = np.minimum((az[keep] / (2 * math.pi) * N_AZ).astype(np.int64), N_AZ - 1)
        seen = np.zeros((nr, N_AZ), bool)
        seen[ri, ai] = True
        count += seen
        print(f"observer {k + 1}/{len(pts)} at ({ox:.0f}, {oy:.0f}): {seen.sum()} ring cells, farthest {r.max() / 1000:.1f} km", flush=True)
    # ring geometry and heights at the cell centres
    rc = np.sqrt(edges[:-1] * edges[1:])
    ac = (np.arange(N_AZ) + 0.5) * 2 * math.pi / N_AZ
    X, Y = rc[:, None] * np.sin(ac)[None, :], rc[:, None] * np.cos(ac)[None, :]
    H = grid_sample(gf, gc, X, Y)
    inside_tile = (np.abs(X) <= HALF) & (np.abs(Y) <= HALF)
    frac = count / len(pts)
    frac[inside_tile] = 0
    frac[np.isnan(H)] = 0
    lo, hi = float(np.nanmin(H)), float(np.nanmax(H))
    Image.fromarray(np.round((np.nan_to_num(H, nan=lo) - lo) / (hi - lo) * 65535).astype(np.uint16)).save(out / "ring.png")
    Image.fromarray(np.round(frac * 255).astype(np.uint8)).save(out / "ring_mask.png")
    far = np.where(frac.max(axis=1) > 0)[0]
    meta = {
        "what": "low-detail ring beyond the sandbox: polar grid about the tile centre, rows = range bins from the tile edge outward, columns = azimuth from north clockwise",
        "n_az": N_AZ, "n_range": nr, "range_edges_m": [round(float(e), 2) for e in edges], "r0_m": R0, "growth": GROW,
        "height_min_m": lo, "height_max_m": hi, "height_encoding": "metres above the 1737.4 km sphere = min + value / 65535 * (max - min); row 0 = innermost ring",
        "mask_encoding": "uint8 = fraction of observers (x255) that see the cell with the camera 0.7 m above ground; 0 = never seen, or inside the tile square, or no data",
        "observers": len(pts), "camera_height_m": EYE, "radius_m": R, "range_max_m": RMAX,
        "visible_cells": int((frac > 0).sum()), "ring_cells": int(frac.size), "farthest_visible_m": float(edges[far.max() + 1]) if far.size else 0,
        "sources": "Atlas 8 m block means where covered, LDEM_128 elsewhere; see prep",
    }
    (out / "ring.json").write_text(json.dumps(meta, indent=1))
    print(f"{(frac > 0).sum()} of {frac.size} ring cells visible ({(frac > 0).mean() * 100:.1f}%), farthest {meta['farthest_visible_m'] / 1000:.1f} km, height {lo:.0f} to {hi:.0f} m")
    # top-down preview: heights shaded, visible cells bright
    S = 1000
    px = (np.arange(S) - S / 2 + 0.5) * (2 * 40000.0 / S)
    xx, yy = np.meshgrid(px, -px)
    rr = np.hypot(xx, yy)
    ai = (np.arctan2(xx, yy) % (2 * math.pi) / (2 * math.pi) * N_AZ).astype(int) % N_AZ
    ri = np.clip(np.searchsorted(edges, rr, side="right") - 1, 0, nr - 1)
    hh = (np.nan_to_num(H, nan=lo)[ri, ai] - lo) / (hi - lo)
    vv = frac[ri, ai]
    img = np.stack([hh * 120 + vv * 135, hh * 120 + vv * 135 * 0.8, hh * 120 + vv * 40], -1)
    img[rr < R0 * 0.7] = [255, 60, 60]
    img[(np.abs(xx) <= HALF) & (np.abs(yy) <= HALF)] = [255, 60, 60]
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(out / "ring_preview.png")


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "prep":
        prep(*sys.argv[2:])
    elif len(sys.argv) == 4 and sys.argv[1] == "run":
        run(*sys.argv[2:])
    else:
        sys.exit(__doc__)
