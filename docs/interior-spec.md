# Body interior (replica)

Layout inside the body: shell, differential mount, shaft bearings through the wall, and where
the battery and electronics go. Replica design, all ASSUMPTION except the outer shape
(`original-dimensions.md`) and the pivot position (3i). CAD and fit checks:
`hardware/body/interior.py`. Part choices for the electronics are **not made**; the boxes below are
placeholders for the size class.

## Shell

| Item | Value | Status |
|---|---|---|
| Side walls, end walls | 3 mm | ASSUMPTION |
| Floor | 3 mm, top at z 127 (belly at 124) | ASSUMPTION |
| Deck | 5 mm (as in `body.py`) | ASSUMPTION |
| Cavity | x -187 to 187, half-width 117 at the floor, z 127 to 343, about 15.8 L | derived from the above |

Material and construction (printed, folded sheet, laminated) are not chosen.

## Differential mount and bearings

- Two 3 mm bulkheads at x = +-24, wall to wall, floor to z 176. The differential housing (36 mm
  diameter, 44 mm long) sits between them and is bolted to them. They also stiffen the shell.
- Each pivot shaft (10 mm) passes through a bearing boss in the side wall at x = 0, z = 145.7: a
  26 mm boss with a 19 mm seat for a 6800 bearing (10 x 19 x 5, ISO size from memory), and enters
  the housing.
- Fit: the housing lies wholly inside the cavity; the shafts clear the bulkheads and turn freely in
  the bearings; the boss tops out at z 158.7, below the cell field (from about 172).
- The boss end is flush with the wall at its axis and stands 2.3 mm proud at its top edge, because
  the wall slopes at 10 degrees. Cosmetic, but shorten or recess it if it shows.

## Compartments

The bulkheads split the cavity into a front and rear compartment with a narrow channel between.

| Item | Size class (mm) | Mass (kg) | Placed |
|---|---|---|---|
| Battery, 2S2P 18650 | 68 x 38 x 38 | 0.22 | rear compartment, on the floor |
| Controller (Zero-class) | 65 x 30 x 8 | 0.015 | front compartment, on the floor |
| Motor drivers, two dual boards | 50 x 70 x 15 | 0.05 | front compartment, on the floor |
| 5 V converter | 40 x 20 x 12 | 0.015 | front compartment, on the floor |
| Keep-out under the deck | 70 x 70 x 60 | n/a | front, for the mast hinge and gimbal drive |

All of them fit the cavity and none clash with each other, the bulkheads or the housing. Together
the electronics are about 0.30 kg with their centre at x -61, z 143, which puts the heavy mast
(front, high) opposite the battery (rear, low). This is a first placement, not a balance: the
replica's mass and centre of mass have not been recomputed.

## Open

- The battery is a size class. A 2S2P pack of 3 Ah cells is about 43 Wh (cell capacity is an
  assumption); runtime depends on the real motor and camera draw, which is untested.
- The controller, camera, drivers and converter are not chosen; wiring runs, connectors and a
  battery charge and protection board have no space reserved.
- The mast: hinge, pan and tilt drives, wiring through the deck. Only a keep-out box exists.
- Cutouts: the bulkheads need wire passages; the walls need the shaft holes (the bosses) and a way
  in to the cavity (a lid or the deck) which is not designed.
- The cell fields are 0.5 mm plates on the wall; nothing is behind them, and their wiring and
  mounting are not designed.
- Mass of the shell: not yet computed (material not chosen).
