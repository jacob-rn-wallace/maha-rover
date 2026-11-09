"""Cut a 5 x 5 km tile of real lunar terrain around the Rashid / Hakuto-R target site out of the LROC Atlas crater DTM.

Source: LROC NAC DTM "NAC_DTM_ATLAS_E468N0446" (Arizona State University, 2012), 2.0 m posts, float32 elevation, equirectangular (standard parallel 47 deg,
planetocentric, R 1737.4 km), 29426 lines x 10607 samples, extents 45.826 to 47.766 N and 44.104 to 45.130 E. Stated vertical precision 2.89 m; RMS difference to LOLA tracks 3.47 to 13.0 m
(product README). Reference: Henriksen et al., Icarus (2016), doi 10.1016/j.icarus.2016.05.012. Terms: LROC states that data products on the LROC Data Node of the PDS and the NASA PDS interfaces are in the public domain (https://lroc.im-ldi.com/about/terms); credit NASA/GSFC/Arizona State University.

The product is 1.25 GB; this tool reads only the 2500 lines it needs (13 sequential range requests of 200 full lines, about 106 MB in all) and crops the columns.
The archive's CDN rate-limited a first attempt of 2500 parallel row requests (HTTP 429, retry-after 3600 s): this tool never sends more than one request at a time, pauses between them,
and stops at the first 429 instead of retrying.

  python hardware/sim/terrain/atlas_tile.py fetch CACHE_DIR            # downloads the blocks (resumable) into CACHE_DIR
  python hardware/sim/terrain/atlas_tile.py build CACHE_DIR OUT_DIR    # crops, fills gaps, writes atlas_5km.png (16 bit) and atlas_5km.json
  python hardware/sim/terrain/atlas_tile.py build-local IMG OUT_DIR    # the same from a full local copy of NAC_DTM_ATLAS_E468N0446.IMG (1.25 GB, downloaded by hand)
"""
import json
import math
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

URL = ("https://pds.mcp.nasa.gov/data/store/img/lunar_reconnaissance_orbiter/pds4/lroc/lro-l-lroc-5-rdr/LROLRC_2001/DATA/SDP/NAC_DTM/ATLAS/NAC_DTM_ATLAS_E468N0446.IMG")
LINES, SAMPLES, OFFSET = 29426, 10607, 42428                      # from the PDS4 label (the file size checks: 42428 + 29426 * 10607 * 4 = 1248528756)
R, PHI1 = 1737400.0, math.radians(47.0)
WEST, NORTH, POST = 44.10437844, 47.76639058, 2.0
CENTRE_LAT, CENTRE_LON, N = 47.3047, 44.8055, 2500                # 5 x 5 km, chosen by hardware/sim/terrain/site_select.py: the nearest fully covered window to the Hakuto-R impact point
#   (47.581 N, 44.094 E, outside the raster; the DTM is three strips with a large empty north-west part) that meets the driving criteria listed there, 16.9 km from it.
#   The nearest covered window of any kind is 14.7 km away (47.58 N, 44.81 E) but has 299 m of relief, over the 250 m limit.
BLOCK = 200
MISSING = -3.0e38                                                 # the label's missing constant is 0xFF7FFFFB (about -3.4e38)


def window():
    """first line, first sample of the tile in the DTM"""
    sample_c = round((CENTRE_LON - WEST) * math.pi / 180 * R * math.cos(PHI1) / POST)
    line_c = round((NORTH - CENTRE_LAT) / (POST / R * 180 / math.pi))
    s0, l0 = sample_c - N // 2, line_c - N // 2
    assert 0 <= s0 and s0 + N <= SAMPLES and 0 <= l0 and l0 + N <= LINES, (s0, l0)
    return l0, s0


def blocks():
    l0, _ = window()
    return [(l0 + b * BLOCK, min(l0 + (b + 1) * BLOCK, l0 + N)) for b in range(-(-N // BLOCK))]


def fetch(cache):
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    for a, b in blocks():
        f = cache / f"lines_{a}_{b}.f32"
        want = (b - a) * SAMPLES * 4
        if f.exists() and f.stat().st_size == want:
            print("have", f.name)
            continue
        lo = OFFSET + a * SAMPLES * 4
        rq = urllib.request.Request(URL, headers={"Range": f"bytes={lo}-{lo + want - 1}"})
        try:
            with urllib.request.urlopen(rq, timeout=120) as r, open(f.with_suffix(".part"), "wb") as out:
                while chunk := r.read(1 << 20):
                    out.write(chunk)
        except urllib.error.HTTPError as e:
            sys.exit(f"stopped: HTTP {e.code} (retry-after {e.headers.get('retry-after')}). Not retrying; wait and run again, finished blocks are kept.")
        if f.with_suffix(".part").stat().st_size != want:
            sys.exit(f"stopped: short read for {f.name}")
        f.with_suffix(".part").rename(f)
        print("got", f.name, f"{want / 1e6:.1f} MB", flush=True)
        time.sleep(3)


def build(cache, out, local_img=None):
    import numpy as np
    from PIL import Image
    l0, s0 = window()
    if local_img:                                                   # a full copy of the product: memory-map it and cut the window
        size = Path(local_img).stat().st_size
        if size != OFFSET + LINES * SAMPLES * 4:
            sys.exit(f"{local_img} is {size} bytes, expected {OFFSET + LINES * SAMPLES * 4}: not the complete .IMG product (not the .TIF extras)")
        full = np.memmap(local_img, dtype="<f4", mode="r", offset=OFFSET, shape=(LINES, SAMPLES))
        h = np.array(full[l0:l0 + N, s0:s0 + N], dtype=np.float64)
    else:
        rows = []
        for a, b in blocks():
            arr = np.fromfile(Path(cache) / f"lines_{a}_{b}.f32", dtype="<f4").reshape(b - a, SAMPLES)
            rows.append(arr[:, s0:s0 + N])
        h = np.concatenate(rows).astype(np.float64)
    bad = h < MISSING
    if bad.any():                                                   # fill gaps with the mean of the valid neighbours, repeated
        print(f"{bad.sum()} missing posts ({bad.mean() * 100:.2f}%), filled")
        h[bad] = np.nan
        for _ in range(50):
            nan = np.isnan(h)
            if not nan.any():
                break
            p = np.pad(h, 1, constant_values=np.nan)
            nb = np.stack([p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]])
            m = np.nanmean(nb, axis=0)
            h[nan] = m[nan]
    lo, hi = float(h.min()), float(h.max())
    q = np.round((h - lo) / (hi - lo) * 65535).astype("<u2")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    Image.fromarray(q.astype(np.uint16)).save(out / "atlas_5km.png")
    meta = {
        "source": "LROC NAC DTM NAC_DTM_ATLAS_E468N0446 (ASU, 2012), https://pds.mcp.nasa.gov/data/store/img/lunar_reconnaissance_orbiter/pds4/lroc/lro-l-lroc-5-rdr/LROLRC_2001/DATA/SDP/NAC_DTM/ATLAS/",
        "reference": "Henriksen et al., Icarus 2016, doi 10.1016/j.icarus.2016.05.012",
        "size_px": N, "post_m": POST, "extent_m": N * POST, "centre_lat": CENTRE_LAT, "centre_lon": CENTRE_LON,
        "height_min_m": lo, "height_max_m": hi, "height_encoding": "metres = min + value / 65535 * (max - min); rows run north to south, columns west to east",
        "dtm_lines": [l0, l0 + N], "dtm_samples": [s0, s0 + N], "vertical_precision_m": 2.89, "rms_vs_lola_m": [3.47, 13.0],
        "note": "metre-scale relief is below the product's vertical precision: the simulation adds procedural detail on top",
        "licence": "public domain (https://lroc.im-ldi.com/about/terms); credit NASA/GSFC/Arizona State University",
    }
    (out / "atlas_5km.json").write_text(json.dumps(meta, indent=1))
    print(f"tile {N} x {N} posts, heights {lo:.1f} to {hi:.1f} m (range {hi - lo:.1f} m), step {(hi - lo) / 65535 * 100:.2f} cm")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "fetch":
        fetch(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == "build":
        build(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 4 and sys.argv[1] == "build-local":
        build(None, sys.argv[3], local_img=sys.argv[2])
    else:
        sys.exit(__doc__)
