# Chassis: T-slot frame and panels (replica)

Decided 2026-11-07, revised the same day to vertical and horizontal members only: build the chassis from T-slot aluminium extrusion and attach sheet panels to it
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

Revised 2026-11-07 (owner's request): **every extrusion is vertical or horizontal; only the panels lean.** The frame is a plain
rectangular box, as wide as the cavity is at its narrowest, under the deck. Every member's outer face is vertical at y = plus or
minus 79.8 mm (0.2 mm inside the side panels at the deck). The earlier version leaned the four posts 10 degrees and needed
printed wedge strips and shims; those are gone. Members are modelled as plain 20 x 20 sections (slots ignored); the floor
is 237 mm wide, so at the bottom the side panels are 38.6 mm outboard of the frame (3.5 mm at the lower edge of the top rail).

| Group | Members | Length (mm) |
|---|---|---|
| Vertical corner posts | 4 | 219.0 |
| Bottom end cross rails | 2 | 119.5 |
| Bottom side rails, split at the pivot shafts | 4 | 132.6 |
| Top end cross rails | 2 | 119.5 |
| Cross rail under the mast base | 1 | 119.5 |
| Top side rails | 2 | 335.2 |
| Mid side rails (z 175) | 2 | 335.2 |
| Differential cross rails (x = plus or minus 28, z 175) | 2 | 119.5 |

19 members, 3.58 m, **1.79 kg** (was 1.92 kg). Every extrusion is cut square (zero-cut), and all cuts are the simplest
possible: the vendor's cut-to-length service needs no angle at all.

- **Sloped side panels stand off the frame on printed ribs.** Each side panel is 2 mm sheet leaning at 10 degrees (stated [S20]); the
  frame's outer faces are vertical, so the gap between them grows from 3.5 mm at the top rail to 38.6 mm at the floor. Two
  **printed ribs per side** (x = plus or minus 100, 6 mm thick, a trapezoid in the YZ plane, about 25 cm3 each, 0.13 kg in PETG
  for all four) fill it: the flat edge lies against the outer faces of the bottom, mid and top side rails (fixed with T-nuts
  through the rib into the rails' outer slots), the sloped edge carries the panel on heat-set M3 inserts.
  ASSUMPTION: the rib count and thickness are not analysed.
- **Edges of the tub.** Because the floor is wider than the frame, the floor-to-side and side-to-end edges need
  something to hold the panels together: a 15 x 15 x 2 mm aluminium angle along each of the four floor edges and the four
  sloped corner seams, riveted or screwed. Not modelled or massed here (about 0.05 kg); the harness-and-fasteners allowance covers it.
  The top edge of the side panels meets the deck's lip; how it is held is not designed.
- **Bearing plates and standoffs.** The pivot shafts at z 145.7 would pass through a bottom side rail, so those rails are split
  (no rail for |x| < 35 mm). On each side a 6 mm aluminium plate (x plus or minus 60, z 126 to 166) lies in the XZ plane against the
  rails' outer faces, bolted over the rail ends, with a 16 mm bore for a 688 bearing. A 22 mm square standoff tube (3 mm wall,
  16 mm bore) runs from the plate out to the side panel, its end cut by the panel's slope. A second 688 sits in the tube's outer
  end. The two bearings are about 27 mm apart, and the outer one is about 21 mm inboard of the link plate (inner face y = 133), so the
  link plate is supported much as before. Plate and tube are 0.19 kg together for both sides (0.08 kg before).
- **Differential.** Two cross rails at x = plus or minus 28 hold the 48 x 50 x 36 mm differential housing between them, on printed cradles
  (not modelled), 1.3 mm above its top. They now span y plus or minus 59.8 (was plus or minus 93).
- **Mast.** The base plate (x 123 to 199) lies over the mast cross rail (x 131 to 151) and the front end rail
  (x 168 to 188); a 17 mm gap between them is left for the cable entry.

## Joints (revised 2026-11-07)

Every rail-to-rail and rail-to-post joint is a plain 90 degree butt joint with a standard 20-series
**corner bracket** (2 T-nuts, 2 M4 bolts). Nothing else is needed: no shims, no angle cuts.

| Joint | Count |
|---|---|
| End cross rail to post | 8 |
| Side rail to end cross rail | 8 |
| Mid side rail to post | 4 |
| Differential cross rail to mid side rail | 4 |
| Mast cross rail to top side rail | 2 |
| Bottom side rail to bearing plate (the plate is bolted over the rail end, 2 bolts) | 4 |
| **Total** | **30 brackets, 60 T-nuts, 60 M4 bolts** |

Bracket sizes, T-nut type and bolt lengths are standard 20-series items, not chosen from a catalogue.

## Panel fixing

| Panel | Fixing | Count |
|---|---|---|
| Floor | M4 button-head screws into T-nuts in the bottom rails' slots, about 100 mm pitch, at least 2 per member (ASSUMPTION) | 12 |
| Deck (the lid) | same, into the top rails and the mast cross rail | 14 |
| End panels (2) | same, into the end cross rails and the posts | 20 |
| Side panels (2) | M3 screws into heat-set inserts in the ribs (4 per rib) and in the standoff tubes (4 per side) | 24 |
| **M4 screws and T-nuts** | | **46** |

The side panels no longer touch the frame, so they take no T-nuts. Panel holes are clearance holes.

**Access to the cavity: the deck is the lid.** Undoing its 14 screws lifts off the deck with the mast attached
(0.8 kg now); the 160 mm wide opening reaches the battery, drivers and controller. The mast's wires need a connector
at the lid so the two can be parted. The mast base plate is held by 4 M4 bolts through the plate and deck into the
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

- All 19 members and both bearing plates (with their standoff tubes) lie inside the cavity; no member touches another.
- The frame does not touch the battery, controller, drivers, converter, differential housing, or the cable entry zone (15 x 40 x 30 mm, in the gap
  under the mast). **Four placeholder parts had to move** because the rails now run at y plus or minus 60 to 80: the 5 V converter (to y 40), the fuse block
  (y -40), the servo regulator (y -50) and the solar charge controller (y -45); see `interior-spec.md`.
- The ribs lie inside the cavity and clear every member and plate; the 12 solar wire holes and the four terminal boards clear the frame.
- The pivot shafts clear every member and turn freely in the plate bores and bearings.
- Frame, plates and standoffs take about 1.5 L of the 16.35 L cavity. The frame no longer fills the lower corners: the 38.6 mm wedges between the
  frame and the side panels are enclosed but unusable except as dead space.

## Mass

| Item | kg | Status |
|---|---|---|
| Frame | 1.79 | catalogue linear mass x lengths |
| Panels | 2.41 | 2 mm sides, ends, floor; 3 mm deck |
| Bearing plates and standoff tubes | 0.19 | |
| Printed ribs | 0.13 | PETG, solid |
| **Chassis** | **4.52** | the original's structure is 2 kg, excluding mobility [S26] |

Replica total from the CAD: **9.60 kg** (`replica-mass.md`; was 9.20 kg: the T-slot mast adds 0.38 kg, the frame saves 0.13 kg, the plates and
standoffs add 0.11 kg and the ribs replace the old wedges at +0.04 kg). Decision 2026-11-07: the first pass is not optimised for mass, and the motors, drivers, battery and
bearings are sized for 10 kg (`drive-spec.md`); a second pass brings the build down to 10 kg if the real parts come out over. If it
does, the first places to save mass are the side plates, the panel thickness, the redundant top and mid rails, and a 30 x 30 mast.

## Open

- Bracket, T-nut and bolt sizes are not picked from a catalogue; the screw pitch and counts are estimates.
- Rib count and thickness are not analysed; the ribs, edge angles and the top edge of the side panels are not designed in detail.
- The bearing plate's fixing to the rails (2 bolts per end, in the CAD as a plain overlap), and the cradles that hold the differential housing (printed), are
  not modelled. The standoff tube's end flange and its fixing to the panel are not designed.
- The lid's gasket-free fit: no dust sealing, and no connector chosen for the mast cable.
- Panel material and thickness.
- Mid rails and top side rails may be partly unnecessary; no stiffness analysis has been done.
- Cells: their mounting on the side panels (glued dummy cells) and any wiring are not designed.
