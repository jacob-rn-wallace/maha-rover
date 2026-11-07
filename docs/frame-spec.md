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

Revised 2026-11-07 from the owner's sketch and a second correction: **every extrusion is vertical or horizontal; only the side panels
lean, and they are separate plates held off the frame on pivots.** The frame is **stepped**: a wide bottom frame on the floor and a narrow
top frame under the deck, joined by four vertical posts that stand on the bottom end cross rails. Members are modelled as plain 20 x 20
sections (slots ignored).

- **Bottom frame:** two side rails the full length of the body, joined at the ends by two end cross rails (so all four corners are
  closed; an earlier version stopped the side rails short and left the corners unjoined). Outer faces at y = plus or minus 105.1. The
  floor lies on it. The side rails are split at |x| < 35 for the pivot shafts, where a bearing plate bridges them.
- **Top frame:** two side rails and two end cross rails under the deck, outer faces at y = plus or minus 70.0, plus the cross rail under the mast.
- **Posts:** y 50 to 70 (under the top rails), x at the ends, standing on the bottom end cross rails; they lie 35 mm inboard of the
  bottom frame's outer face.

The frame sits **10 mm inside the side panels** at the outer upper corner of each rail (`PANEL_GAP` in `interior.py`), so no member touches a
side panel.

| Group | Members | Length (mm) |
|---|---|---|
| Vertical posts, on the bottom end rails | 4 | 199.0 |
| Bottom end cross rails | 2 | 170.1 |
| Bottom side rails, split at the pivot shafts | 4 | 152.8 |
| Top end cross rails | 2 | 99.9 |
| Cross rail under the mast base | 1 | 99.9 |
| Top side rails | 2 | 335.2 |
| Mid side rails (z 175, between the posts) | 2 | 335.2 |
| Differential cross rails (x = plus or minus 28, z 175) | 2 | 99.9 |

19 members, 3.59 m, **1.79 kg**. Every extrusion is cut square (zero-cut). A connectivity check in `frame.py` confirms the 19 members form one piece
(each bottom side rail meets an end cross rail at one end and the bearing plate at the other).

- **Side panels on pivot standoffs.** In the original the side panels stand proud of the body on spacers, apparently so that the heat
  the cells absorb does not reach the body (front view, [S18] Fig. 1; the gap reads about 10 mm by eye, uncertain by several mm; the
  reason is the owner's reading, not a source). The replica copies this: each side panel is a single 2 mm sloped plate
  (the solar panel itself) held by **four standoffs near its corners**, two on a bottom side rail and two on a top side rail, at
  x = plus or minus 150. A standoff is a horizontal 8 mm stud, about 12.5 mm long, from the rail's outer face to the panel, with a rod end or small ball
  joint at the panel end so the 10 degrees between the stud and the sloped plate and thermal movement are taken up (a hinge is the alternative).
  Each is fixed to its rail by an M4 bolt into a T-nut. **Eight standoffs, 0.015 kg each (ASSUMPTION), 0.12 kg.** The pivot parts are not chosen or modelled.
- **There is no separate body wall at the sides.** The panel is the only side sheet, with air behind it; this keeps the mass down (a second wall
  would add about 0.9 kg) but leaves the sides open to dust and light. A thin inner wall can be added later.
- **Stiffness.** The panel is held at four points only, with 224 mm of 2 mm sheet between them, carrying the cells; no check has been made. A 3 mm sheet,
  a folded edge or a stiffener behind the cells are the options.
- **Edges of the tub.** The floor lies on the bottom frame, wider than the rails by 13 mm on each side. The floor, end panels and side panels are
  not joined to each other along their seams; the end panels bolt to the end rails and posts. Closing the seams is not designed.
- **Bearing plates.** The pivot shafts at z 145.7 would pass through a bottom side rail, so those rails are split. On each side a 6 mm aluminium plate
  (x plus or minus 60, z 126 to 164, 0.07 kg) lies in the XZ plane against the rails' outer faces, bolted over the rail ends, with a 16 mm bore
  for a 688 bearing. The shaft passes on through a 22 mm clearance hole in the side panel (the panel floats on its pivots) to the link plate at
  y = 133, about 25 mm beyond the bearing. There is now one bearing per side, as in the earlier design, and the shaft is cantilevered a little further.
- **Differential.** Two cross rails at x = plus or minus 28 hold the 48 x 50 x 36 mm differential housing between them, on printed cradles
  (not modelled), 1.3 mm above its top. They span the mid rails, y plus or minus 50.
- **Mast.** The base plate (x 123 to 199) lies over the mast cross rail (x 131 to 151) and the front end rail
  (x 168 to 188); a 17 mm gap between them is left for the cable entry.

## Joints (revised 2026-11-07)

Every rail-to-rail and rail-to-post joint is a plain 90 degree butt joint with a standard 20-series
**corner bracket** (2 T-nuts, 2 M4 bolts). Nothing else is needed: no shims, no angle cuts, no printed wedges.

| Joint | Count |
|---|---|
| Bottom end cross rail to bottom side rail | 4 |
| Bottom end cross rail to post (post stands on it) | 4 |
| Top end cross rail to post | 4 |
| Top side rail to post | 4 |
| Mid side rail to post | 4 |
| Differential cross rail to mid side rail | 4 |
| Mast cross rail to top side rail | 2 |
| Bottom side rail to bearing plate (the plate is bolted over the rail end) | 4 |
| **Total** | **30 brackets, 60 T-nuts, 60 M4 bolts** |

Bracket sizes, T-nut type and bolt lengths are standard 20-series items, not chosen from a catalogue.

## Panel fixing

M4 button-head screws into T-nuts in the slot facing each panel, at about 100 mm pitch with at least two per member (ASSUMPTION):

| Panel | Screws and T-nuts |
|---|---|
| Floor (on the bottom rails and bottom end rails) | 12 |
| Deck (the lid) | 14 |
| End panels (2) | 16 |
| Side panels (2), by the 8 pivot standoffs | 8 |
| **Total** | **50** |

Panel holes are clearance holes; the T-nut sits in the frame.

**Access to the cavity: the deck is the lid.** Undoing its 14 screws lifts off the deck with the mast attached
(0.8 kg now); the 140 mm wide opening reaches the battery, drivers and controller. The mast's wires need a connector
at the lid so the two can be parted. The mast base plate is held by 4 M4 bolts through the plate and deck into the
mast cross rail (x 141) and the front end rail (x 178), at y plus or minus 30, so removing the lid does not
unbolt the mast. The 17 mm gap between those two rails (x 151 to 168) is the cable entry.

## Panels

Aluminium sheet. The floor, ends and deck are bolted to the frame through the slots (M4 T-nuts at roughly 80 to 100 mm pitch, not designed); the side panels hang on pivot standoffs:

| Panel | Size (mm) | Thickness |
|---|---|---|
| Floor | 380 x about 242 | 2 |
| Side panels (2, sloped 10 degrees, carry the cells, on pivot standoffs) | 380 x about 224 | 2 |
| End walls (2) | about 242 bottom, 164 top, 221 high | 2 |
| Deck | 401 x 164 | 3 |

Total **2.41 kg** at 2.70 g/cm3 (the standard density of aluminium). Alternatives: 1.5 mm sheet (the earlier idea,
about 0.6 kg lighter), or printed panels. 

## Result of the checks

- All 19 members and both bearing plates lie inside the cavity (the space inside the side panels); no member touches another; the 19 form one connected frame.
- Frame and plates are clear of the side panels (0 mm3 overlap); the standoffs clear every member and plate.
- The frame does not touch the battery, controller, drivers, converter, differential housing, or the cable entry zone (15 x 40 x 30 mm, in the gap
  under the mast). The master switch moved from y 45 to y 35 to clear the post.
- The 12 solar wire holes and the four terminal boards clear the frame; the pivot shafts clear every member and turn freely in the plate bores.
- Frame and plates take about 1.5 L of the 16.35 L cavity.

## Mass

| Item | kg | Status |
|---|---|---|
| Frame | 1.79 | catalogue linear mass x lengths |
| Panels | 2.41 | 2 mm sides, ends, floor; 3 mm deck |
| Bearing plates | 0.14 | |
| Pivot standoffs | 0.12 | 8 x 0.015 kg, ASSUMPTION |
| **Chassis** | **4.46** | the original's structure is 2 kg, excluding mobility [S26] |

Replica total from the CAD: **9.53 kg** (`replica-mass.md`; was 9.20 kg before the T-slot mast, which adds 0.38 kg). Decision 2026-11-07: the first
pass is not optimised for mass, and the motors, drivers, battery and bearings are sized for 10 kg (`drive-spec.md`); a second pass brings the build
down to 10 kg if the real parts come out over. If it does, the first places to save mass are the link plates, the panel thickness, the redundant
top and mid rails, and a 30 x 30 mast.

## Open

- Bracket, T-nut and bolt sizes are not picked from a catalogue; the screw pitch and counts are estimates.
- The pivot standoffs: rod end, ball joint or hinge, how thermal expansion of the panel is taken up, whether four points hold a 2 mm sheet flat, and the true gap (about 10 mm by eye).
- Sealing: no side wall, so the sides, the floor-to-panel seams and the end seams are open.
- The bearing plate's fixing to the rails, and the cradles that hold the differential housing (printed), are not modelled.
- The lid's gasket-free fit: no dust sealing, and no connector chosen for the mast cable.
- Panel material and thickness.
- Mid rails and top side rails may be partly unnecessary; no stiffness analysis has been done.
- Cells: their mounting on the side panels (glued dummy cells) and any wiring are not designed.
