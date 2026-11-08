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
  44 mm long) by four integral lugs bolted to their lower slots (`frame-spec.md`).
- Each pivot shaft (a 12 mm tube) passes through a 16 mm hole drilled in the single 20 x 40 bottom side rail at x = 0, z = 145.7, with a flanged plain bushing at each end, then through a 22 mm
  clearance hole in the side panel, and enters the housing through a boss and bushing in its wall, where it steps down to 8 mm (`differential-spec.md`, `frame-spec.md`).
- Fit: the housing lies wholly inside the cavity; the shafts clear every frame member and turn freely in the
  bearings. The rails top out at z 166, below the cell field (from about 172).

## Compartments

Boards are now dimensioned models (`electronics-spec.md`, `hardware/electronics/boards.py`); the battery, BMS, power node and charger module are still boxes.


The differential cross rails split the upper cavity; the floor is open from end to end.

| Item | Size class (mm) | Mass (kg) | Placed |
|---|---|---|---|
| Battery, 2S2P 18650 | 68 x 38 x 38 | 0.22 | rear compartment, on the floor |
| Controller, Raspberry Pi Zero 2 W | model 66 x 31 x 10.2 (board 65 x 30, 5.2 tall, on 5 mm posts) | 0.011 (assumed) | **under the deck**, x 95, y 33 (since 2026-11-08; was on the floor at x 60, y 35), on 5 mm posts from the deck, board flipped, behind the mast cross rail: near the mast cable entry |
| Motor drivers, two Pololu MC33926 boards side by side | model 45.7 x 27.9 x 16.7 each (7.67 tall on 9 mm posts, connectors underneath, assumed) | 0.007 each | front compartment, x 60, y -16 and -44 |
| 5 V converter, Pololu D24V22F5 | model 17.8 x 17.8 x 11.9 (7.9 tall on 4 mm posts) | 0.0023 | front compartment, x 130, y 60 |
| 6 V servo regulator, Pololu D24V22F6 | same model | 0.0023 | x -10, y -60 |
| 4-way fuse block (candidate Optifuse BLR-I-304) | 85 x 47 x 21 (listing, axes assumed) | 0.045 (assumed) | rear compartment, x -70, y -50 |
| Master switch (candidate SCI R13-112B8-02) | 23 mm bezel, 20.2 mm cut-out, 28 mm deep (depth assumed) | 0.012 (assumed) | rear panel, y 35, z 165, the bezel 2 mm proud |
| GNSS receiver breakout (SparkFun NEO-M9N, u.FL) | 40.6 x 33 x 9.6 with posts (`boards.py`) | 0.008 (assumed) | under the deck, x 58, y -30, 5 mm posts (2026-11-08) |
| CSI extender Rx board (Arducam kit) | about 35 x 25 board, jack 13 tall (placeholder) | 0.010 (assumed) | under the deck, x 104, y -36, beside the Pi (2026-11-08); a Ø16 hole in the deck at x 112 admits the round cable |
| Servo bus adapter (Waveshare Bus Servo Adapter A) | 44 x 33 x 16 with posts | 0.021 (retailer) | under the deck, x 104, y -3, beside the Pi: a short USB lead (2026-11-08) |
| Solar charge controller (part not chosen) | 50 x 30 x 12 | 0.03 (assumed) | front compartment, on the floor at x 112, y -65, between the drivers and the bottom side rail (`solar-spec.md`) |
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
