# Graphic design: wordmark, poster and headers

Branding for the al-maha project. Separate from the rover engineering; none of
this constrains the rover's dimensions.

## Layout
```
graphic-design/
  wordmark/        almaha-wordmark.svg
  poster/          almaha-poster-trapezoid.svg / .jpg
  headers/         README banners (SVG), one per source photo / grid size
  source-photos/   NASA Artemis II photographs the mosaics are built from
  social-preview/  GitHub social preview image (1280 x 640)
  scripts/         Python that generates the wordmark, poster and headers
```

### Wordmark: `wordmark/almaha-wordmark.svg`
Final wordmark, 4 merged closed outlines, viewBox 440 x 152, cut-ready (untested in cutting software).

### Poster: `poster/`
Final poster, 2:3, Earthset mosaic with the wordmark at the bottom. The SVG is vector; the JPG is 2288 x 3434.

### Social preview: `social-preview/`
`almaha-social-preview.png` is the 1280 x 640 image uploaded in the GitHub repo settings (Settings, Social preview; GitHub has no API for this). Same coarse grid as `edge-coarse`, wordmark centred between the Earth and the limb. Regenerate with `python3 header.py social ../../social-preview/almaha-social-preview.png` from `scripts/mosaic/`.

### Headers: `headers/`
Wide banners (about 3.2 : 1), all built from the same 15 degree trapezoid mosaic with the wordmark on the mosaic lattice.

| File | Photo | Notes |
|---|---|---|
| `almaha-header-edge-coarse.svg` | `art002e009285` | **Used in the root README.** 18 px cells, so the trapezoids' short edge equals the wordmark stem width. Wordmark between the Earth's crescent and the lunar limb. 140 KB. |
| `almaha-header-edge.svg` | `art002e009285` | Same, 6 px cells. 1.2 MB. |
| `almaha-header-earthset.svg` | `art002e009288` | Earthset, wordmark on the left. 15 px cells. |
| `almaha-header-crescent.svg` | `art002e021110` | Crescent Earth beside the limb. 1.2 MB. |
| `almaha-header-horizon.svg` | `art002e021219` | Earthset over a cratered horizon. 0.9 MB. |

Photo titles and NASA URLs are in [`../NOTICE.md`](../NOTICE.md).

## Wordmark design
- Square Kufic spelling المَهَا on a slanted lattice, 15 degree lean, coarse-grid version with a continuous baseline.
- Lattice: diagonals 20 units apart horizontally, rows 37.32 apart.
- Stems 20 wide and 3 rows tall. Horizontal strokes 10. Fatha bars 7. Alif-lam gap 20.
- The baseline is what distinguishes lam from the final alif. Don't remove it without reader testing.
- The square Kufic construction is the designer's own, not an attested historical form. The medial ha is a best reading of the standard shape.

## Poster design
- Source photo: "Earthset", NASA / Artemis II, April 6, 2026. Working size 2576 x 1717 px.
- Crop: 2:3, 1144 x 1717 source px, centred on the Earth.
- Mosaic: trapezoids of 3 triangles, 15 degree legs, no grout, each cell filled with the average photo colour.
- Wordmark: scale 1.2, centred, baseline on mosaic row 72, colour `#f4f2ee`.

## Decisions
- Avoid hexagram motifs.
- 15 degrees is the shared angle between wordmark and mosaic grid.
- Rejected: 30 degree equilateral trapezoids (wordmark angle no longer matched), 8-fold and 12-fold grids.

## Open items
- Legibility untested with Arabic readers. Show it without saying what it says, then cover the fathas and ask again.
- Check the 7-unit fatha bars and 20-unit gap against cutter or printer minimums.
- Edge cells on the poster crop not inspected. Contrast of wordmark on the Moon judged in preview only.
- Possible: print-resolution poster export (7200 x 10800 px for 24 x 36 in), title text at top, per-cell lightness variation.
- The poster's PNG/JPG exports and two comparison sheets were made with inline code that wasn't saved (see below).

## Scripts (`scripts/`)
Setup (from the repo root): `pip install -r requirements.txt`. Only `numpy pillow shapely` are needed unless you export PNGs (`cairosvg`).

- `wordmark.py`: shared module. The wordmark polygons live here once, plus the photo loader.
- `build_wordmark.py`: `python3 scripts/build_wordmark.py` writes `wordmark/almaha-wordmark.svg`.
- `mosaic/header.py`: `python3 header.py <preset> [preview.png]` (from `scripts/mosaic/`) writes a banner (or the social preview) under `graphic-design/`. Presets: `earthset`, `edge`, `edge-coarse`, `crescent`, `horizon`, `social` (`--list` shows them). A preset sets photo, cell size, wordmark scale and position; the wordmark is snapped onto the lattice automatically. The optional PNG is a Pillow preview.
- `mosaic/poster_trap.py`: writes the poster SVG into the current directory (it does not overwrite `poster/`).
- Comparison and exploration scripts (run from `scripts/mosaic/`; outputs land in the current directory and are gitignored):
  - `tri_mosaic.py <base_px> <out.svg>`: triangle mosaic. Bases used were 48, 24 and 12.
  - `tri_mosaic.py 12 earthset-tri-xfine.svg`, then `poster.py`: the earlier triangle poster.
  - `poster_equi.py 18 almaha-poster-hex`: 30 degree grouted comparison.
  - `tess_all.py`: no-grout, 8-fold star and 3.4.6.4 comparisons.
- `mosaic/trap.py`: helper; must sit next to the scripts that import it.

**Photo size:** `art002e009288orig.jpg` is 5568 x 3712 px, but the poster's grid and crop constants (12 px cells, crop centre 1188, width 1144) assume 2576 x 1717, so `wordmark.load_photo()` downscales it with LANCZOS. This reproduces the poster's geometry exactly (5005 trapezoids); cell colours differ from the checked-in JPG by at most 2/255 per channel, because the original downscale method is unknown. The other photos are used at native 1920 x 1280.

PNG/JPG export (not saved as a script originally):
`cairosvg.svg2png(url=NAME+'.svg', write_to=NAME+'.png', output_width=2288, background_color='black')`, then
`Image.open(png).convert('RGB').save(NAME+'.jpg', quality=95, subsampling=0)`.

Not recovered: `grid_check.py` (13-line debug script, not needed), and the code behind `tessellation-comparison.jpg` and `zoom-compare.jpg`.
