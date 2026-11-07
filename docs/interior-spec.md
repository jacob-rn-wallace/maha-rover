# Body interior (replica)

Layout inside the body: shell, differential mount, shaft bearings through the wall, and where
the battery and electronics go. Replica design, all ASSUMPTION except the outer shape
(`original-dimensions.md`) and the pivot position (3i). CAD and fit checks:
`hardware/body/interior.py`. The electronics follow the candidates in `electronics-spec.md` (not bought);
the battery box is still a size class.

## Panels

The panels are aluminium sheet on a T-slot frame (`frame-spec.md`).

| Item | Value | Status |
|---|---|---|
| Side panels (separate plates on pivot standoffs, 10 mm off the frame), end walls | 2 mm | ASSUMPTION |
| Floor | 2 mm, top at z 126 (belly at 124) | ASSUMPTION |
| Deck | 3 mm | ASSUMPTION |
| Cavity | x -188 to 188, half-width 119 at the floor, z 126 to 345, about 16.4 L | derived from the above |

## Differential mount and bearings

- Two extrusion cross rails at x = plus or minus 28, z 175, hold the differential housing (a 48 x 50 x 36 mm box,
  44 mm long) on printed cradles between them (`frame-spec.md`).
- Each pivot shaft (an 8 mm tube) passes through a 12 mm hole drilled in the single bottom side rail at x = 0, z = 145.7 (the bottom frame is centred on the
  pivot axis), with a flanged plain bushing at each end, then through a 22 mm clearance hole in the side panel, and enters the housing (`differential-spec.md`).
- Fit: the housing lies wholly inside the cavity; the shafts clear every frame member and turn freely in the
  bearings. The rails top out at z 156, below the cell field (from about 172).

## Compartments


The differential cross rails split the upper cavity; the floor is open from end to end.

| Item | Size class (mm) | Mass (kg) | Placed |
|---|---|---|---|
| Battery, 2S2P 18650 | 68 x 38 x 38 | 0.22 | rear compartment, on the floor |
| Controller, Raspberry Pi Zero 2 W | 65 x 30 x 8 (height assumed) | 0.015 (assumed) | front compartment, on the floor |
| Motor drivers, two Pololu MC33926 boards side by side | 46 x 56 x 12 (28 x 46 each; height assumed) | 0.014 | front compartment, on the floor |
| 5 V converter, Pololu D24V22F5 | 18 x 18 x 8 | 0.0023 | front compartment, on the floor |
| Solar charge controller (part not chosen) | 50 x 30 x 12 | 0.03 (assumed) | front compartment, on the floor at x 112, y -70, between the drivers and the bottom side rail (`solar-spec.md`) |
| Keep-out under the mast base | 15 x 40 x 30 | n/a | front, in the gap between the mast cross rail and the front end rail, for the cable entry from the mast |

All of them fit the cavity and none clash with each other, the frame or the housing. Together
the electronics are about 0.28 kg with their centre at x -67, z 142, which puts the heavy mast
(front, high) opposite the battery (rear, low). This is a first placement, not a balance: the
replica's mass and centre of mass have not been recomputed.

## Open

- The battery is a size class. A 2S2P pack of 3 Ah cells is about 43 Wh (cell capacity is an
  assumption); runtime depends on the real motor and camera draw, which is untested.
- The controller, camera, drivers and converter are not chosen; wiring runs, connectors and a
  battery charge and protection board have no space reserved.
- The mast is fixed and carries its own servos (`mast-spec.md`); only the cable entry through the deck and a clamp for the wires are reserved, as a 15 x 40 x 30 mm keep-out. The entry itself is not designed.
- The way in to the cavity is the deck, as a lid with the mast attached (`frame-spec.md`); the walls need the shaft
  holes in the bottom side rails (modelled in `frame.py`).
- The cell fields are 0.5 mm plates on the wall; nothing is behind them, and their wiring and
  mounting are not designed.
- Mass of the panels and frame: see `frame-spec.md`.
