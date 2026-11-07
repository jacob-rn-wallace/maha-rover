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
| Corner posts, 10 degrees from vertical, mitred both ends | 4 | 222.4 |
| Bottom end cross rails | 2 | 229.7 |
| Bottom side rails, split at the pivot shafts | 4 | 132.6 |
| Top end cross rails | 2 | 166.6 |
| Cross rail under the mast base | 1 | 166.6 |
| Top side rails | 2 | 335.2 |
| Mid side rails (z 175) | 2 | 335.2 |
| Differential cross rails (x = plus or minus 28, z 175) | 2 | 216.0 |

19 members, 4.15 m, **1.92 kg**. Lengths are for the 10 degree geometry of `body.py`; the joints (corner brackets or
end fasteners, T-nuts) are not modelled.

- **Posts.** The walls lean 10 degrees (stated [S20]), so the posts do too, and their ends must be cut at 10 degrees to
  sit flat on the rails. The vendor's cut-to-length service lists only a 45 degree cut, so the mitres would be made by
  hand, or the posts cut square with printed 10 degree shims at the ends. The wedge is small: over a 20 mm section it
  is 3.5 mm. This breaks the earlier "zero-cut" idea; it is the one place it does.
- **Bearing plates.** The pivot shafts at z 145.7 would pass through a bottom side rail, so those rails are split
  (no rail for |x| < 35 mm) and a 6 mm plate (0.04 kg each) bridges the gap, with a seat for the 6800 bearing.
- **Differential.** Two cross rails at x = plus or minus 28 hold the 36 mm housing between them, on printed cradles
  (not modelled), 1.3 mm above its top.
- **Mast.** The base block (x 122 to 200) lies over the mast cross rail (x 131 to 151) and the front end rail
  (x 168 to 188); a 17 mm gap between them is left for the cable entry.

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
about 0.4: **about 9 kg**. That is nearly twice the 5 kg used to size the motors (`drive-spec.md`): the slope torque
per wheel becomes about 0.77 N.m (79 kg.mm), inside the gearmotor's 100 kg.mm continuous limit but above its
60 kg.mm best-efficiency point, at about 0.9 A per motor. The first places to save mass are the side plates, the
panel thickness and the redundant top and mid rails.

## Open

- The corner joints, fasteners and panel fixing are not designed. Neither is the way into the cavity (a lid on the
  deck, or a removable end panel).
- Panel material and thickness; whether the posts are mitred by hand or shimmed.
- Mid rails and top side rails may be partly unnecessary; no stiffness analysis has been done.
- Cells: their mounting on the side panels (glued dummy cells) and any wiring are not designed.
