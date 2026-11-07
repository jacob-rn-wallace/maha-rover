# Solar cells: provisions for real cells (replica)

The replica's 30 cells (5 x 3 on each sloped side) are dummy plates today. This records what is built in so real
cells can be fitted later, the cell data behind it, and what is still open. CAD and checks:
`hardware/solar/solar.py` (with `hardware/body/body.py` for the cells and holes). Everything here is ASSUMPTION
unless tagged; cell data are quoted from the sources noted, with their caveats.

## What the original uses

The cell grid is 5 x 3 per side of about 69 x 39 mm with 6.5 mm clipped bottom corners (`original-dimensions.md` 3g,
derived), the size of a standard 26.5 cm2 triple-junction cell cut in half; the cover glass is 200 um cerium-doped
borosilicate [S10]; the supplier is not named. The stated peak generation is 15 W [S3].

## Cell data read for this note

| Cell | Figures | Caveat |
|---|---|---|
| CESI CTJ30 (triple junction, the size class above) | datasheet v2025.1 table: Voc 2.6 V, Jsc 17.8, Jm 17.1 mA/cm2, Vm 2.3 V, Pmax 39.8 mW/cm2, 29.1 percent, beginning of life | read from text extracted from the PDF, so the column alignment is unchecked; test conditions not read; thickness and mass of the standard cell not found (the thin version is 80 um, 50 mg/cm2) |
| Spectrolab UTJ, 26.62 cm2 bare | Voc 2.718 V, Isc 0.459 A, Vmp 2.417 V, fill factor 86.7 percent | from a NASA paper, a production-cell figure the paper gives alongside research results; not a datasheet |
| Silicon, C60-class 125 x 125 mm | 22.5 percent, 0.582 V, 5.93 A | a rounded database entry, not a measured pair; a retail "C60 5x5" listing gives 0.6 V and 3.6 W |

Availability and price of space-grade triple-junction cells were not looked up; they are sold for flight, so a hobby
build would need surplus or a supplier willing to sell a few. Treat option A below as the original's choice, and option B
as the practical one.

## Electrical options (derived)

| | Option A: triple junction | Option B: silicon cut to 69 x 39 |
|---|---|---|
| Per cell | 2.3 V, 0.45 A, 1.05 W (AM0, beginning of life) | 0.58 V, 1.03 A, 0.60 W (one sun, perpendicular; cutting losses ignored) |
| One row of 5 in series | 11.5 V, 0.45 A, 5.2 W | 2.9 V, 1.03 A |
| One side, 3 rows in parallel | 11.5 V, 1.36 A, **15.6 W** | too low in voltage |
| One side, all 15 in one series string | 34.5 V | 8.7 V, 1.03 A, **9.0 W** |
| Charger | buck MPPT, input above 13 V (5 x 2.6 V open circuit) | buck-boost MPPT, input about 8.7 V |

The triple-junction side comes to 15.6 W at normal incidence, within 5 percent of the stated 15 W peak [S3] if one
side faces the sun at a time. That is a consistency check on the numbers, not proof the original is wired that way.
Both sides together would be 31 W but only one faces the sun. Output on a near-vertical panel scales with
cos(sun elevation minus 10 degrees) times the cosine of the azimuth off the panel normal: 0.94 at 30 degrees
elevation, 0.77 at 50, 0.50 at 70.

For the 2S pack (8.4 V full, 43 Wh) a side delivers roughly 9 to 16 W at best, against about 35 W driving
(`electronics-spec.md`): solar charges the pack, it does not run the rover.

## Built in

- **Stack.** The panel carries a 1.0 mm stack: insulating film (the panel is conductive aluminium), adhesive, cell,
  and cover glass. The dummy plates use the same thickness, so the envelope will not change. Real cells need
  an insulating layer; the film and adhesive are not chosen.
- **Wire holes.** Twelve 5 mm holes, six per side panel: one beside each end of each cell row, 17 mm outboard of the
  end cell's centre (x = plus or minus 160.2, under the cell's outer half). Row heights z 194, 234 and 275. All string
  ends come inside the cavity, so the series and parallel wiring is chosen on a terminal block and either option
  above can be wired. The holes are under the dummy cells and so invisible; real cells will need their rear contact
  and a lead brought to the hole, which depends on the cell type.
- **Clearance.** Nothing in the frame, wedge strips, bearing plates or shaft path lies within 6 mm of any hole's axis,
  14 mm deep. The nearest member is the mid side rail, 9 mm below the lowest hole row; the posts are 5 mm from the
  hole edges. Wires should pass between the panel and the mid rail and drop to the floor.
- **Harness.** The longest straight run from a hole to the charge controller is 353 mm; allow about 460 mm of wire per
  lead. Grommets for the 12 holes are not chosen.
- **Charge controller.** A 50 x 30 x 12 mm box is reserved in the front compartment of the interior (x 110, y -85,
  on the floor, 30 g assumed), clear of the other parts. The part is not chosen: it must be an MPPT charger for a 2S
  lithium pack (8.4 V, constant current then constant voltage) taking the input of the chosen option, with at least
  2 A out for option A.

## Open

- Which cells: the electrical option, a supplier, and the real cell outline and rear contact. The 69 x 39 mm clipped
  outline holds for a half-cut triple-junction cell; silicon cut to that outline needs a cutting method.
- The charge controller, fuses, per-string diodes, terminal blocks and the grommets.
- Bonding and insulating the cells, interconnect tabs, and cover glass or encapsulation.
- Testing. Output at the actual sun angle on the panels is not measured; the table is arithmetic from datasheet values.
- Whether to put a dark border and the clipped outline on the dummy cells so they look like the real ones; they are
  plain clipped plates in the CAD.
