# Chassis: T-slot frame and panels (replica)

Decided 2026-11-07, revised the same day to a stepped frame of vertical and horizontal members only (owner's sketch): build the chassis from T-slot aluminium extrusion and attach sheet panels to it
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

Revised 2026-11-07 from the owner's sketch: **every extrusion is vertical or horizontal; only the panels lean.** The frame is
**stepped**: a wide bottom frame on the floor and a narrow top frame under the deck, joined by four vertical posts that stand on the
bottom end cross rails. The side panels run from the outer edge of the bottom side rails to the outer edge of the top side rails, so the
difference in width sets the 10 degrees (stated [S20]) and no member needs an angle. Members are modelled as plain 20 x 20 sections
(slots ignored); each sits 0.2 mm inside the panels.

- **Bottom frame:** outer faces vertical at y = plus or minus 114.9 (touching the panel at the rails' top outer corner), the floor lies on it.
- **Top frame:** outer faces at y = plus or minus 79.8, under the deck.
- **Posts:** y 59.8 to 79.8 (under the top rails), x at the ends, standing on the bottom end cross rails; they are 35 mm inboard of the
  bottom frame's outer face, so the posts never touch the sloped panels.

| Group | Members | Length (mm) |
|---|---|---|
| Vertical posts, on the bottom end rails | 4 | 199.0 |
| Bottom end cross rails | 2 | 189.7 |
| Bottom side rails, split at the pivot shafts | 4 | 132.6 |
| Top end cross rails | 2 | 119.5 |
| Cross rail under the mast base | 1 | 119.5 |
| Top side rails | 2 | 335.2 |
| Mid side rails (z 175, between the posts) | 2 | 335.2 |
| Differential cross rails (x = plus or minus 28, z 175) | 2 | 119.5 |

19 members, 3.64 m, **1.82 kg** (the leaning-post version was 1.92 kg). Every extrusion is cut square (zero-cut), with no angle anywhere.

- **Tapered strips.** A vertical rail face against a sloped panel leaves a wedge, 0 to 3.5 mm over the rail's 20 mm. Six printed strips
  (the four bottom side rails and the two top side rails, 42 cm3, 0.05 kg) fill it; the panel screws through the strip into the rail's
  T-nut. No strips are needed at the posts or mid rails, which do not touch the panels.
- **Unsupported middle.** The side panel is held along its bottom and top edges and at the bearing plate, but not in the middle: 224 mm of
  2 mm sheet between the rails, carrying the cells. It may need a stiffening rib or a printed spacer from a mid rail (a printed block between
  the mid rail and the panel, about 30 mm thick, would do); no stiffness check has been made.
- **Edges of the tub.** The floor lies on the bottom frame, so its edges are supported. The side-to-end seams still want a 15 x 15 x 2 mm
  aluminium angle each (4, about 224 mm; not modelled or massed: about 0.03 kg, inside the fasteners allowance).
- **Bearing plates.** The pivot shafts at z 145.7 would pass through a bottom side rail, so those rails are split
  (no rail for |x| < 35 mm) and a 6 mm sloped plate (0.04 kg each) lies against the side panel and bridges the gap, with a seat for the
  688 bearing, as before.
- **Differential.** Two cross rails at x = plus or minus 28 hold the 48 x 50 x 36 mm differential housing between them, on printed cradles
  (not modelled), 1.3 mm above its top. They span the mid rails, y plus or minus 59.8.
- **Mast.** The base plate (x 123 to 199) lies over the mast cross rail (x 131 to 151) and the front end rail
  (x 168 to 188); a 17 mm gap between them is left for the cable entry.

## Joints (revised 2026-11-07)

Every rail-to-rail and rail-to-post joint is a plain 90 degree butt joint with a standard 20-series
**corner bracket** (2 T-nuts, 2 M4 bolts). Nothing else is needed: no shims, no angle cuts.

| Joint | Count |
|---|---|
| End cross rail to post (post on the bottom rail; top rail between the posts) | 8 |
| Side rail to end cross rail | 8 |
| Mid side rail to post | 4 |
| Differential cross rail to mid side rail | 4 |
| Mast cross rail to top side rail | 2 |
| Bottom side rail to bearing plate | 4 |
| **Total** | **30 brackets, 60 T-nuts, 60 M4 bolts** |

Bracket sizes, T-nut type and bolt lengths are standard 20-series items, not chosen from a catalogue.

## Panel fixing

M4 button-head screws into T-nuts in the slot facing each panel, at about 100 mm pitch with at least two per member (ASSUMPTION):

| Panel | Screws and T-nuts |
|---|---|
| Floor (on the bottom rails and bottom end rails) | 12 |
| Deck (the lid) | 14 |
| End panels (2) | 16 |
| Side panels (2), through the tapered strips into the bottom and top rails, 2 more each into the bearing plate | 20 |
| **Total** | **62** |

Panel holes are clearance holes; the T-nut sits in the frame.

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

- All 19 members and both bearing plates lie inside the cavity; no member touches another.
- The frame does not touch the battery, controller, drivers, converter, differential housing, or the cable entry zone (15 x 40 x 30 mm, in the gap
  under the mast). The wide bottom frame leaves the floor open: the interior parts keep their earlier positions.
- The strips lie inside the cavity and clear every member and plate; the 12 solar wire holes and the four terminal boards clear the frame.
- The pivot shafts clear every member and turn freely in the plate bores.
- Frame and plates take about 1.5 L of the 16.35 L cavity.

## Mass

| Item | kg | Status |
|---|---|---|
| Frame | 1.82 | catalogue linear mass x lengths |
| Panels | 2.41 | 2 mm sides, ends, floor; 3 mm deck |
| Bearing plates | 0.08 | |
| Printed strips | 0.05 | PETG, solid |
| **Chassis** | **4.36** | the original's structure is 2 kg, excluding mobility [S26] |

Replica total from the CAD: **9.44 kg** (`replica-mass.md`; was 9.20 kg before the T-slot mast, which adds 0.38 kg; the frame saves 0.10 kg and the
strips are 0.04 kg lighter than the old wedges and shims). Decision 2026-11-07: the first pass is not optimised for mass, and the motors,
drivers, battery and bearings are sized for 10 kg (`drive-spec.md`); a second pass brings the build down to 10 kg if the real parts come
out over. If it does, the first places to save mass are the side plates, the panel thickness, the redundant top and mid rails, and a 30 x 30 mast.

## Open

- Bracket, T-nut and bolt sizes are not picked from a catalogue; the screw pitch and counts are estimates.
- Stiffness of the side panels between the bottom and top rails (and any spacer from the mid rails); the side-to-end edge angles.
- The bearing plate's fixing to the wall panel, and the cradles that hold the differential housing (printed), are not modelled.
- The lid's gasket-free fit: no dust sealing, and no connector chosen for the mast cable.
- Panel material and thickness.
- Mid rails and top side rails may be partly unnecessary; no stiffness analysis has been done.
- Cells: their mounting on the side panels (glued dummy cells) and any wiring are not designed.
