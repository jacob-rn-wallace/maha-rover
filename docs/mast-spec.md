# Mast specification (replica)

Replica mast, head and camera, **fixed upright**. Dimensions are from the original's CAD figures
(`original-dimensions.md` 3j, derived) where they exist; the rest is the replica's own design and
ASSUMPTION. CAD and checks: `hardware/mast/mast.py`.

**Stowing and deploying are deferred** (decision 2026-11-07). The original folds the mast flat under
120 mm and springs it up on landing [S19]; the replica's mast stands fixed for now. The earlier hinged design
(pedestal, hinge pin, fold sweep) is in commit `20aec90`, and the reasons a spring hinge does not fit are in
`electronics-spec.md` (a bus-servo hinge is the likely route when stowing is wanted).

## Geometry

| Item | Value | Status |
|---|---|---|
| Tube | 58 x 58 mm, z 420 to 577, centre 24.2 mm ahead of the front axle (x 160.7), 3 mm wall, 2 x 4 oval lightening slots on each side face | size and position derived [3j]; wall and slots ASSUMPTION |
| Base block | 78 x 90 mm, deck (348) to z 420, bolted through the deck into the mast cross rail and front end rail (`frame-spec.md`) | height derived [3j]; about 90 fore-aft was measured, which would overhang the 401 mm deck front by 5 mm, so 78; width ASSUMPTION |
| Neck and C-arm | neck z 577 to 621; arm bar 50 x 45 mm at y +25 to +70, to z 690 | derived by eye [3j] |
| Head | camera housing 60 x 72 mm, z 621 to 700, centred 28 mm right of the centreline | derived [3j], [S8] |
| Camera | CAM-1 35 x 35 x 73 mm, axis at z 660, lens front 77.9 ahead of the front axle | stated [S12], [S8] |
| Top | z 700 | stated [S1] |

The original's mast is additively manufactured ULTEM 1010 with titanium and aluminium parts [S19];
the replica's material is not chosen (a printed tube is the obvious candidate).

## Actuation

- **Pan and tilt:** two servos, one in the neck (vertical axis) and one in the arm (horizontal axis), for the
  original's pan of plus or minus 179 degrees and tilt of plus or minus 75 degrees [S19]. The candidate
  Feetech STS3215 is 45.2 x 24.7 x 35 mm (`electronics-spec.md`); the neck cavity is 52 x 52 x 38 mm and the
  arm cavity 44 x 39 x 63 mm, so it fits with 3 mm of height spare in the neck. The CAD neck and arm are
  solid, so this is a size check only.
- **Camera:** a small module in a printed 35 x 35 x 73 mm tube, wired down the mast. Not bought.

## CAD checks

- Top at 700 (stated); camera axis 660; lens front 214.4 (front axle at 136.5 + 77.9), which is 24 mm
  ahead of the body's front end (190).
- The base block lies wholly on the deck plate and does not touch the body or the cells.

## Loads

With the assumed masses (structure 0.25 kg, servos 0.11, camera 0.04, hardware 0.02; total 0.42 kg) the
centre of mass is 211 mm above the deck. A sideways acceleration of 1 g (a tipping rover) puts about
**0.87 N.m** on the base joint; 0.30 N.m on a 20 degree slope. The mast is a 58 mm printed tube with 3 mm
walls on a 78 x 90 mm base; no stress check has been done.

## Open

- Servos and camera module are candidates only (`electronics-spec.md`), none bought.
- The wires from the head down the tube and into the body: where they enter the deck is reserved in
  `interior-spec.md` (a 40 x 40 x 30 mm zone under the base), but the entry is not designed.
- The base is held by 4 M4 bolts through the deck into two frame rails (`frame-spec.md`); the bolts themselves, the
  tube's internal ribs and the base joint's strength are not modelled.
- Stowing: deferred. The stowed height limit (120 mm above the deck [S19]) is not met by this mast.
