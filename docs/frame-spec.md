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

Revised 2026-11-07 from the owner's sketch and later corrections: **every extrusion is vertical or horizontal; only the side panels
lean, and they are separate plates held off the frame on pivots.** The frame is **stepped**: a wide bottom frame on the floor and a narrow
top frame under the deck, joined by four vertical posts that stand on the bottom end cross rails. Members are modelled as plain sections
(slots ignored): 20 x 20 throughout, except the two bottom side rails, which are **20 x 40**.

- **Bottom frame:** two side rails, each a **single 20 wide x 40 tall member** (HFS5-2040: 0.88 kg/m, 324 mm2) the full length of the body, standing on
  the floor panel (z 126 to 166), joined at the ends by two 20 x 20 end cross rails (z 126 to 146; all four corners closed). Outer faces at
  y = plus or minus 101.5. Each pivot shaft passes **through a 16 mm hole drilled in its side rail** at x = 0, z 145.7, with a flanged plain bushing
  (12 ID x 16 OD x 8 long, ASSUMPTION) at each end of the hole. The rail is 40 mm tall so the hole leaves 12 mm of wall above and below it (an earlier
  20 x 20 rail, raised to put the axle at its centre, could take only a 12 mm hole and left 4 mm of wall; the shaft has since grown, see below).
- **Top frame:** two side rails and two end cross rails under the deck, outer faces at y = plus or minus 70.0, plus the cross rail under the mast.
- **Posts:** y 50 to 70 (under the top rails), x at the ends, standing on the bottom end cross rails (from z 146); they lie 32 mm inboard of the
  bottom frame's outer face.

The frame sits **10 mm inside the side panels** at the outer upper corner of each rail (`PANEL_GAP` in `interior.py`), so no member touches a
side panel.

| Group | Members | Length (mm) |
|---|---|---|
| Vertical posts, on the bottom end rails | 4 | 199.0 |
| Bottom end cross rails (20 x 20) | 2 | 163.1 |
| Bottom side rails (20 x 40), one each, with the pivot hole | 2 | 375.6 |
| Top end cross rails | 2 | 99.9 |
| Cross rail under the mast base | 1 | 99.9 |
| Top side rails | 2 | 335.2 |
| Mid side rails (z 175, between the posts) | 2 | 335.2 |
| Differential cross rails (x = plus or minus 28, z 175) | 2 | 99.9 |

17 members, 3.71 m, **2.14 kg** (0.88 kg/m for the two 20 x 40 rails, 0.50 for the rest). Every extrusion is cut square (zero-cut); the only machining is the
16 mm hole in each bottom side rail. A connectivity check in `frame.py` confirms the 17 members form one piece (each bottom side rail meets both bottom end cross rails).

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
- **Edges of the tub.** The floor lies on the bottom frame, wider than the rails by 17 mm on each side. The floor, end panels and side panels are
  not joined to each other along their seams; the end panels bolt to the end rails and posts. Closing the seams is not designed.
- **Pivot shaft, its supports and the rail (strength check).** The shaft is a **12 mm OD, 8 mm ID steel tube** (it was 8 / 5; see below) with two supports:
  the pair of bushings in the rail hole, and a **bushing in the differential housing wall** (12 ID x 16 OD x 11 long, in a boss on the outside of the wall),
  63 mm inboard of the rail. Beyond the housing wall the tube is turned down to 8 mm OD, 5 mm ID for the side gear. The shaft passes on through a 22 mm
  clearance hole in the side panel (the panel floats on its pivots) to the link plate at y = 133. `hardware/chassis/rail_check.py` is a hand calculation
  (typical material values, 3 times the static load for impacts, wheel scrub at a friction coefficient of 0.6, all assumptions). **The wheel load acts at y = 208,
  100 mm outboard of the rail**, not at the link plate: an earlier version of this check used the link plate and understated the bending by a factor of two.
  - **Reactions at 3x:** 600 N at the rail, 460 N at the housing wall, and a shaft bending moment of **29 N.m** at the rail's outer face (9.8 N.m static).
  - **The 8 / 5 tube would fail.** It sees 695 MPa von Mises at 3x and 247 MPa static (with the torque at the 1.6 A cap), against about 355 MPa for S355 steel.
  - **The 12 / 8 tube passes** at 218 MPa at 3x: a factor of 1.6 in S355 steel, 3.0 in 4140 quenched and tempered, and 1.0 in 304 stainless (so not stainless).
    Static: 77 MPa. **Material to choose: 4140 or S355.**
  - **No radial hole in the bent part.** The 3 mm wire holes at y = 60 and y = 125 are gone: they were at a stress concentration in the highest-moment zone.
    The wires now leave the tube axially at the link plate end, and enter through one radial hole at y = 20 in the 8 mm stub inside the housing, where the bending
    moment is nearly zero (torque alone, 158 MPa at the cap with the concentration).
  - **The rail as a beam is fine:** 603 N at midspan over 376 mm gives 23 MPa net at the hole against about 200 for the alloy (factor 8.8); the 16 mm hole keeps
    about 97 percent of the section's stiffness. **Tear-out** of the 12 mm of wall above the hole is 6 MPa per bushing (allow 116). **Without the housing support
    the two bushings only 12 mm apart would each see about 2.4 kN** at 3x, which no 20 mm rail wall could take.
  - **The housing now carries 460 N at 3x** (153 N static), down through its cradles into the differential cross rails; the cradles are not designed.
  Plain bushings suit the slow oscillation of the differential (a few degrees); check the bushing material and the shaft's surface.
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
| **Total** | **26 brackets, 52 T-nuts, 52 M4 bolts** |

Bracket sizes, T-nut type and bolt lengths are standard 20-series items, not chosen from a catalogue.

## Panel fixing

M4 button-head screws into T-nuts in the slot facing each panel, at about 100 mm pitch with at least two per member (ASSUMPTION):

| Panel | Screws and T-nuts |
|---|---|
| Floor (on the bottom side and end rails) | 12 |
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

- All 17 members and the bushings lie inside the cavity (the space inside the side panels); no member touches another; the 17 form one connected frame.
- Frame and bushings are clear of the side panels (0 mm3 overlap); the standoffs clear every member.
- The pivot shafts pass through the rail holes and bushings with no overlap, and the housing bosses clear the frame.
- The frame does not touch the battery, controller, drivers, converter, differential housing, or the cable entry zone (15 x 40 x 30 mm, in the gap
  under the mast). The tall rails now run through x = 0 at y 81 to 101, so the servo regulator moved to y -60 and the charger to y -65.
- The 12 solar wire holes and the four terminal boards clear the frame.
- Frame takes about 1.8 L of the 16.35 L cavity.

## Mass

| Item | kg | Status |
|---|---|---|
| Frame | 2.14 | catalogue linear mass x lengths (the hole's removed metal ignored) |
| Panels | 2.41 | 2 mm sides, ends, floor; 3 mm deck |
| Pivot standoffs | 0.12 | 8 x 0.015 kg, ASSUMPTION |
| Bushings | 0.02 | ASSUMPTION |
| **Chassis** | **4.69** | the original's structure is 2 kg, excluding mobility [S26] |

Replica total from the CAD: **9.82 kg** (`replica-mass.md`), a margin of only 0.18 kg: the 20 x 40 rails add 0.35 kg and the 12 mm shafts 0.06 kg. Decision
2026-11-07: the first pass is not optimised for mass, and the motors, drivers, battery and bearings are sized for 10 kg (`drive-spec.md`); a second pass
brings the build down to 10 kg if the real parts come out over. If it does, the first places to save mass are the link plates, the panel thickness, the
redundant top and mid rails, and a 30 x 30 mast.

## Open

- Bracket, T-nut and bolt sizes are not picked from a catalogue; the screw pitch and counts are estimates.
- The pivot: the shaft material (4140 or S355), the bushing material and fit, the shaft's step at the housing wall (turned or a separate gear stub), the link plate to
  shaft joint, and the housing's cradles, which now carry 460 N at 3x.
- The pivot standoffs: rod end, ball joint or hinge, how thermal expansion of the panel is taken up, whether four points hold a 2 mm sheet flat, and the true gap (about 10 mm by eye).
- Sealing: no side wall, so the sides, the floor-to-panel seams and the end seams are open.
- The lid's gasket-free fit: no dust sealing, and no connector chosen for the mast cable.
- Panel material and thickness.
- Mid rails and top side rails may be partly unnecessary; no stiffness analysis has been done.
- Cells: their mounting on the side panels (glued dummy cells) and any wiring are not designed.
