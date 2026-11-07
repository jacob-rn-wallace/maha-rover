# Mast specification (replica)

Replica mast, hinge, head and camera. Dimensions are from the original's CAD figures
(`original-dimensions.md` 3j, derived) where they exist; the mechanism and everything inside is the
replica's own design and is ASSUMPTION. CAD and checks: `hardware/mast/mast.py`.

## Geometry

| Item | Value | Status |
|---|---|---|
| Tube | 58 x 58 mm, z 420 to 577, centre 24.2 mm ahead of the front axle (x 160.7), 3 mm wall, 2 x 4 oval lightening slots on each side face | size and position derived [3j]; wall and slots ASSUMPTION |
| Base block (rotating) | 90 mm fore-aft x 90 wide, z 376 to 420 | fore-aft derived [3j]; width ASSUMPTION |
| Neck and C-arm | neck z 577 to 621; arm bar 50 x 45 mm at y +25 to +70, to z 690 | derived by eye [3j] |
| Head | camera housing 60 x 72 mm, z 621 to 700, centred 28 mm right of the centreline | derived [3j], [S8] |
| Camera | CAM-1 35 x 35 x 73 mm, axis at z 660, lens front 77.9 ahead of the front axle | stated [S12], [S8] |
| Top | z 700 | stated [S1] |
| Hinge pin | along Y at the tube's rear face (x 131.7), z 376 (28 above the deck) | about 30 above the deck, derived by eye [3j]; position ASSUMPTION |
| Pedestal | 70 x 102 mm, 28 mm tall, lugs outside the base block | ASSUMPTION |

The original's mast is additively manufactured ULTEM 1010 with titanium and aluminium parts [S19];
the replica's material is not chosen (a printed tube is the obvious candidate).

## Mechanism (replica)

- **Deploy (as modelled; under review):** torsion springs on the hinge pin swing the mast up through 90 degrees
  to a stop; a servo-pulled latch holds it down. A hand check in `electronics-spec.md` finds the springs
  too long for the 28 mm pedestal and recommends a bus-servo hinge instead; the CAD still shows springs. This copies [S19]'s spring hinge and hold-down, with a servo in
  place of the fuse wire. Re-stowing is by hand against the springs.
- **Pan and tilt:** two servos, one in the neck (vertical axis) and one in the arm (horizontal axis),
  for the original's pan of plus or minus 179 degrees and tilt of plus or minus 75 degrees [S19]. The
  neck cavity is 52 x 52 x 38 mm and the arm cavity 44 x 39 x 63 mm; the candidate Feetech STS3215 is
  45.2 x 24.7 x 35 mm (`electronics-spec.md`), which fits with 3 mm of height spare in the neck. The CAD neck
  and arm are solid, so this is a size check only.
- **Camera:** a small module on the mast, wired down the tube. Not chosen.

## CAD checks

- **Deployed:** top at 700 (stated); camera axis 660; lens front 214.4 (front axle at 136.5 + 77.9).
- **Stowed (folded rearward, an assumption):** the mast lies along the deck, 118 mm above it against
  the stated limit of 120 [S19]. That clearance is a fit: the hinge height was chosen for it, and a
  hinge 2 mm higher would break the limit. The rear end is at x -192, inside the deck (rear edge at -200).
  With the mast folded the lens points up.
- **Sweep:** folding from 0 to 90 degrees in 15 degree steps, the mast never touches the deck, the
  cells or the pedestal.
- The hinge pin sits in the base block's corner, so the block shows an overlap with it; in reality
  the block has a hole there.

## Loads

With the assumed masses (structure 0.25 kg, servos 0.12, camera 0.04, springs and latch 0.04; total
0.45 kg) the centre of mass is 195 mm along the mast from the hinge. With the mast lying flat that is
**0.86 N.m** about the hinge on Earth (0.14 on the Moon). A sketch of the spring sizing: a spring torque
of about 1.2 N.m at the stowed position falling to about 0.2 N.m at the stop (a rate of about 0.64 N.m
per radian, with preload) lifts the mast on Earth and still presses it against the stop. Gravity
helps as the mast rises. The mass figures are guesses; weigh the real parts and redo this.

## Open

- Candidates are in `electronics-spec.md`; none bought. The hinge mechanism (springs or servo) is undecided.
- Wiring from the head through the hinge to the body (a flexing loop at the pin) is not designed.
- The base block's inside, the hinge pin hole and the stop block are not modelled.
- The keep-out under the deck (`interior-spec.md`) is reserved for the mast drive, but this design
  needs no drive under the deck: only the latch servo on the pedestal and the cable in. The keep-out
  could shrink, and the cable entry through the deck needs a place.
- The folded direction (rearward) and the exact stowed layout of the head are assumptions.
