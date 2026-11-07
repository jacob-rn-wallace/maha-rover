# Chassis: T-slot frame and panels (replica)

Decided 2026-11-07: build the chassis from T-slot aluminium extrusion and attach sheet panels to it
(a return to the earlier idea, now sized to the replica). Everything here is the replica's own design and
ASSUMPTION unless tagged. CAD and checks: `hardware/chassis/frame.py` (with `hardware/body/interior.py`).

## Why 20 x 20 and not 40 x 40

The earlier sessions used 4040 and 40120. At the top of the body the interior is only about 160 mm wide
(164 mm outside), and two 40 mm posts would take half of it. A 20 x 20, 6 mm slot section (the "5 series")
is the natural size for a 380 mm long body. Catalogue figures for the Misumi HFS5-2020: 0.50 kg/m, 183 mm2,
second moment of area about 0.74 x 10^4 mm4, lengths from 50 to 4000 mm in 0.5 mm steps, length tolerance
plus or minus 0.5 mm (plus or minus 0.2 mm for the precision cut). A second 20 x 20 datasheet also gives 0.50 kg/m.
One other listing gave 0.745 kg/m; the section properties differ between makers, so get them from the
vendor you buy from.

## Frame

Members are modelled as plain 20 x 20 sections (slots ignored); each sits 0.2 mm inside the panels.

| Group | Members | Length (mm) |
|---|---|---|
| Corner posts, 10 degrees from vertical, square cut | 4 | 222.4 |
| Bottom end cross rails | 2 | 229.7 |
| Bottom side rails, split at the pivot shafts | 4 | 132.6 |
| Top end cross rails | 2 | 166.6 |
| Cross rail under the mast base | 1 | 166.6 |
| Top side rails | 2 | 335.2 |
| Mid side rails (z 175) | 2 | 335.2 |
| Differential cross rails (x = plus or minus 28, z 175) | 2 | 216.0 |

19 members, 4.15 m, **1.92 kg**. Lengths are for the 10 degree geometry of `body.py`. Every extrusion is cut square (zero-cut).

- **Posts.** The walls lean 10 degrees (stated [S20]), so the posts do too. They are cut square (the vendor's
  cut-to-length service lists only 45 degree cuts, so there are no mitres): a square-cut end sits up to 3.5 mm short
  of the floor and deck planes, which does not matter because the posts do not bear on those panels. Their length
  along the axis is 222.4 mm at the outer edge.
- **Bearing plates.** The pivot shafts at z 145.7 would pass through a bottom side rail, so those rails are split
  (no rail for |x| < 35 mm) and a 6 mm plate (0.04 kg each) bridges the gap, with a seat for the 688 bearing.
- **Differential.** Two cross rails at x = plus or minus 28 hold the 48 x 50 x 36 mm differential housing between them, on printed cradles
  (not modelled), 1.3 mm above its top.
- **Mast.** The base block (x 122 to 200) lies over the mast cross rail (x 131 to 151) and the front end rail
  (x 168 to 188); a 17 mm gap between them is left for the cable entry.

## Joints (decided 2026-11-07)

Rails stay axis-aligned, so rail-to-rail joints are plain 90 degree butt joints with a standard 20-series
**corner bracket** (2 T-nuts, 2 M4 bolts). The 10 degree lean shows up in only two places, each solved with a small
printed part, so no extrusion needs an angle cut:

- **End cross rail to post:** the post's inner face leans, leaving a 0 to 3.5 mm wedge at the rail end. A printed
  **10 degree shim** fills it (8 shims), clamped by the bracket.
- **Side panel to side rail:** a vertical rail face under a sloped panel leaves the same wedge. A printed **tapered
  strip**, 20 mm wide and 0 to 3.5 mm thick (8 strips, 132 to 335 mm), fills it. The posts are flush with the panel
  and need none.

| Joint | Count |
|---|---|
| End cross rail to post (bracket and shim) | 8 |
| Side rail to end cross rail | 8 |
| Mid side rail to post | 4 |
| Differential cross rail to mid side rail | 4 |
| Mast cross rail to top side rail | 2 |
| Bottom side rail to bearing plate | 4 |
| **Total** | **30 brackets, 60 T-nuts, 60 M4 bolts** |

The printed parts total about 72 cm3 (a few tens of grams). Bracket sizes, T-nut type and bolt lengths are standard
20-series items, not chosen from a catalogue.

## Panel fixing

M4 button-head screws into T-nuts in the slot facing each panel, at about 100 mm pitch with at least two per
member (ASSUMPTION). The count comes from the member lengths:

| Panel | Screws and T-nuts |
|---|---|
| Floor | 12 |
| Deck (the lid) | 14 |
| End panels (2) | 20 |
| Side panels (2) | 36 |
| **Total** | **82** |

The panels hang off the frame members that face them: the floor on the bottom rails, the deck on the top rails and
the mast cross rail, the end panels on the end cross rails and the posts, and the sloped side panels on the posts and,
through the tapered strips, the side rails. Panel holes are clearance holes; the T-nut sits in the frame.

**Access to the cavity: the deck is the lid.** Undoing its 14 screws lifts off the deck with the mast attached
(0.4 kg); the 160 mm wide opening reaches the battery, drivers and controller. The mast's wires need a connector
at the lid so the two can be parted. The mast base is held by 4 M4 bolts through the base block and deck into the
mast cross rail (x 141) and the front end rail (x 178), at y plus or minus 30, so removing the lid does not
unbolt the mast. The 17 mm gap between those two rails (x 151 to 168) is the cable entry.

## Panels

Aluminium sheet, bolted to the frame through the slots (M4 T-nuts at roughly 80 to 100 mm pitch, not designed):

| Panel | Size (mm) | Thickness |
|---|---|---|
| Floor | 380 x about 242 | 2 |
| Side walls (2, sloped 10 degrees, carry the cells) | 380 x about 224 | 2 |
| End walls (2) | about 242 bottom, 164 top, 221 high | 2 |
| Deck | 401 x 164 | 3 |

Total **2.41 kg** at 2.70 g/cm3 (the standard density of aluminium). Alternatives: 1.5 mm sheet (the earlier idea,
about 0.6 kg lighter), or printed panels. Folding the floor and side walls from one sheet into a tub, with 100 degree
bends, would save three joints; not designed.

## Result of the checks

- All 19 members and both bearing plates lie inside the cavity; no member touches another.
- The frame does not touch the battery, controller, drivers, converter, differential housing, or the cable
  entry zone (now 15 x 40 x 30 mm, in the gap under the mast).
- The pivot shafts clear every member and turn freely in the plate bores.
- Frame and plates take about 1.6 L of the 16.4 L cavity.

## Mass

| Item | kg | Status |
|---|---|---|
| Frame | 1.92 | catalogue linear mass x lengths |
| Panels | 2.41 | 2 mm sides, ends, floor; 3 mm deck |
| Bearing plates | 0.08 | |
| **Chassis** | **4.41** | the original's structure is 2 kg, excluding mobility [S26] |

A first replica total, with every line ASSUMPTION except the mast, motors and battery from the shortlist:
chassis 4.4, side plates 1.1 (8 mm solid aluminium; thinner or printed plates would save most of it), wheels 1.6
(the CAD model's 0.4 kg each), motors 0.8, mast 0.4, differential about 0.2, battery 0.2, electronics and fasteners
about 0.4: **about 9 kg**, close to the 10 kg design target. Decision 2026-11-07: the first pass is not optimised for
mass, and the motors, drivers, battery and bearings are sized for 10 kg (`drive-spec.md`); a second pass brings the
build down to 10 kg if the real parts come out over. Every line except the mast, motors and battery is a guess, so
the real total may be above or below. If it is over, the first places to save mass are the side plates, the panel
thickness and the redundant top and mid rails.

## Open

- Bracket, T-nut and bolt sizes are not picked from a catalogue; the screw pitch and counts are estimates.
- The bearing plate's fixing to the wall panel, and the cradles that hold the differential housing (printed), are
  not modelled.
- The lid's gasket-free fit: no dust sealing, and no connector chosen for the mast cable.
- Panel material and thickness.
- Mid rails and top side rails may be partly unnecessary; no stiffness analysis has been done.
- Cells: their mounting on the side panels (glued dummy cells) and any wiring are not designed.
