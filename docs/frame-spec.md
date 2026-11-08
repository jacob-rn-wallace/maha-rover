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
  y = plus or minus 101.5. Each pivot shaft passes **through a 16 mm hole drilled in its side rail** at x = 0, z 145.7, in a bonded sleeve with a flanged plain bushing at each end (below). The rail is 40 mm tall so the hole leaves 12 mm of wall above and below it (an earlier
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
- **Pivot shaft, its supports and the rail (strength check and design).** `hardware/chassis/rail_check.py` is a hand calculation (typical material values,
  3 times the static load for impacts, wheel scrub at a friction coefficient of 0.6, all assumptions). **The wheel load acts at y = 208, 100 mm outboard of the
  rail**, not at the link plate: an earlier version of this check used the link plate and understated the bending by a factor of two.
  - **Shaft:** a **12 mm OD, 8 mm ID** steel tube from the link plate to the housing wall. At 3x the peak bending moment is 30 N.m (9.9 static) at the rail's outer
    face, which gives 220 MPa von Mises with the torque at the 1.6 A cap (78 MPa static). The earlier 8 / 5 tube would see 702 MPa. **Material decided:** 4130
    chromoly seamless tube, normalized (yield 435 MPa, the lowest of three supplier figures that disagree: 435, 460, 483), a factor of 2.0 at 3x and 5.6 static.
    A 12 x 2 mm size was not found in the listings I saw, so availability is unverified; **fallback: E355 (DIN 2391) precision tube**, 12 x 2 mm, factor 1.6 at 3x and
    4.5 static. 304 stainless (factor 1.0) is not strong enough. No radial hole in the 12 mm tube: wires leave axially at the boss tip.
  - **Two supports.** (1) The rail: a 16 mm hole drilled through the 20 x 40 rail takes a **16 OD / 14 ID aluminium sleeve, 20 mm long, bonded in** (a bushing
    pressed straight into the 2 mm extrusion walls would not stay put), and an **igus GFM-1214-09 type flanged plain bushing** (12 bore, 14 OD, 9 long, H7 press fit;
    [listing](https://uk.rs-online.com/web/p/plain-bearings/2724568)) pressed into each end. (2) The differential housing wall: a 14 mm H7 bore through the wall and its
    boss, with a **12 mm long** flanged bushing of the same family, 63 mm inboard. The flange diameter and the permissible surface pressure were not found in the listings; the
    pressures here are 2.8 MPa (rail) and 3.2 MPa (housing) at 3x against a deliberately low 20 MPa limit. The shaft needs a hard, smooth surface (the listing gives h9 or
    better; hardness and roughness not looked up), so a ground, hard-chromed or nitrided tube. **Plain bushings suit the slow oscillation of the differential (a few degrees).**
  - **Rail and hole.** The 20 x 40 section's 40 mm face leaves 12 mm of wall above and below the 16 mm hole. The rail as a beam sees 23 MPa net at 3x (factor 8.7);
    the face-wall tear-out is 6 MPa. **Check the hole against the profile drawing:** a 14 to 16 mm hole in the middle of the 40 mm face may fall across the two
    6 mm slots (they are 20 mm apart, centre to centre), and the Misumi drawing has not been read for the web between them.
  - **Housing mount.** The housing's four lugs (10 x 14 x 2 mm, integral to the aluminium housing, at x = 24 to 34, y = +-14) take M4 bolts into T-nuts in the bottom
    slot of the differential cross rails (x = plus or minus 28), with 1.3 mm shim washers across the gap. At 3x with the torque at the gearbox limit the worst bolt pulls
    360 N against an M4 8.8 proof load of about 5 kN. The cross rails see 16 MPa at 3x. These replace the "printed cradles" of the earlier text: printed plastic would
    creep under the 460 N.
  - **Link plate to shaft.** The shaft is **bonded with retaining compound into a 12 mm bore through the 4 mm plate and a 16 mm boss** (20 mm engagement; the plate was 8 mm and the boss 12 before the mass second pass of 2026-11-08, and the boss grown from 6 before that
    mm). At 3x the moment at the plate face is 24 N.m, a peak contact pressure of 30 MPa on the aluminium (factor 8.0). The bond (15 MPa assumed shear; datasheet values
    for retaining compounds run higher, not verified) carries 68 N.m against 7.1 N.m at the gearbox limit (factor 9.6). There are **no cross pins**: a cross hole at the plate
    would see about three times the bending stress. The wires leave the open tube end at the boss tip and run back to the motor sleeves.
  - **Shaft step.** An 8 mm bore cannot be turned down to an 8 mm OD, so the **8 / 5 gear stub is a separate tube**, bonded 15 mm into the 12 / 8 tube at the housing wall (the
    12 mm end bears on the wall's inner face). The bond carries 22.6 N.m against 7.1 N.m at the gearbox limit (factor 3.2); a pin is not used because it would cross the
    wire bore. The bending moment there is nearly zero.
  - **The housing carries 467 N at 3x** (156 N static) at each wall. The CAD shows the bosses, bushings, stub insertion and lugs clear the frame.
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
  under the mast). The tall rails now run through x = 0 at y 81 to 101, so the servo regulator moved to y -60 and the charger to y -65 (and later, with the real fuse block, the regulator to x -10).
- The 12 solar wire holes and the four terminal boards clear the frame.
- Frame takes about 1.8 L of the 16.35 L cavity.

## Mass

| Item | kg | Status |
|---|---|---|
| Frame | 2.14 | catalogue linear mass x lengths (the hole's removed metal ignored) |
| Panels | 2.41 | 2 mm sides, ends, floor; 3 mm deck |
| Pivot standoffs | 0.12 | 8 x 0.015 kg, ASSUMPTION |
| Sleeves and bushings | 0.02 | ASSUMPTION |
| **Chassis** | **4.69** | the original's structure is 2 kg, excluding mobility [S26] |

Replica total from the CAD: **9.92 kg when this was written, now 9.93 kg after the mast pan base, the new head, the die-cast boxes and the mass second pass** (`replica-mass.md`): the 20 x 40 rails add 0.35 kg, the 12 mm shafts and thicker link plate bosses 0.13 kg. Decision
2026-11-07: the first pass is not optimised for mass, and the motors, drivers, battery and bearings are sized for 10 kg (`drive-spec.md`); a second pass
brings the build down to 10 kg if the real parts come out over. If it does, the first places to save mass are the link plates, the panel thickness, the
redundant top and mid rails, and a 30 x 30 mast.

## Open

- Bracket, T-nut and bolt sizes are not picked from a catalogue; the screw pitch and counts are estimates.
- The pivot: the 4130 tube size (12 x 2) is unverified; the drilled hole against the profile's slots; the bushing flange size and rated pressure; retaining compound grades
  and the real bond strength; surface hardness and finish of the shaft; shim washers at the housing lugs; no gland or slot is designed for the wires entering the stub inside the housing.
- The pivot standoffs: rod end, ball joint or hinge, how thermal expansion of the panel is taken up, whether four points hold a 2 mm sheet flat, and the true gap (about 10 mm by eye).
- Sealing: no side wall, so the sides, the floor-to-panel seams and the end seams are open.
- The lid's gasket-free fit: no dust sealing, and no connector chosen for the mast cable.
- Panel material and thickness.
- Mid rails and top side rails may be partly unnecessary; no stiffness analysis has been done.
- Cells: their mounting on the side panels (glued dummy cells) and any wiring are not designed.
