# Mast specification (replica)

Replica mast, head and camera, **fixed upright**. Dimensions are from the original's CAD figures
(`original-dimensions.md` 3j, derived) where they exist; the rest is the replica's own design and
ASSUMPTION. CAD and checks: `hardware/mast/mast.py`.

**Stowing and deploying are deferred** (decision 2026-11-07). The original folds the mast flat under
120 mm and springs it up on landing [S19]; the replica's mast stands fixed for now. The earlier hinged design
(pedestal, hinge pin, fold sweep) is in commit `20aec90`, and the reasons a spring hinge does not fit are in
`electronics-spec.md` (a bus-servo hinge is the likely route when stowing is wanted).

## Geometry

Revised 2026-11-07 (owner's request): **the mast is a T-slot aluminium extrusion itself.** A 40 x 40 mm extrusion stands on a
base plate on the deck and carries the printed neck, arm and head on its top end.

| Item | Value | Status |
|---|---|---|
| Extrusion | 40 x 40 mm T-slot (Misumi HFS8-4040 class, about 1.86 kg/m; catalogue entries run 1.73 to 1.90 kg/m by variant), z 354 to 577, centre 24.2 mm ahead of the front axle (x 160.7), cut square, 223 mm, 0.41 kg | position and top height derived [3j]; section ASSUMPTION |
| Base plate | 76 x 76 x 6 mm aluminium on the deck (z 348 to 354), 4 M4 bolts at x 141 and 178, y +-30, through the deck into the mast cross rail and front end rail (`frame-spec.md`) | ASSUMPTION |
| Neck and C-arm | printed neck 58 x 58 mm, z 577 to 621; arm bar 50 x 45 mm at y +25 to +70, to z 690 | derived by eye [3j] |
| Head | camera housing 60 x 72 mm, z 621 to 700, centred 28 mm right of the centreline | derived [3j], [S8] |
| Camera | CAM-1 35 x 35 x 73 mm, axis at z 660, lens front 77.9 ahead of the front axle | stated [S12], [S8] |
| Top | z 700 | stated [S1] |

**Departure from the original.** The original's mast tube measures about 58 mm square [3j]. The replica's extrusion is 40 mm, so the
visible column is slimmer below the 58 mm printed neck. A 60 x 60 extrusion would match, but at about 4.17 kg/m it would weigh 0.93 kg
(0.52 kg more) and the mass margin would shrink to about 0.1 kg; a 40 x 60 would be a compromise (not looked up). The extrusion's end is
tapped (M8) to take the neck's base plate; its slots carry the camera and servo cables, and the centre bore can pass a connector lead.

The original's mast is additively manufactured ULTEM 1010 with titanium and aluminium parts [S19]; the replica's neck, arm and head are printed
(material not chosen).

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
- The base plate lies wholly on the deck plate (5776 of 5776 mm2) and does not touch the body or the cells.

## Loads

With the assumed masses (extrusion 0.41 kg and base plate 0.09 kg from catalogue and density, printed parts 0.12, servos 0.11, camera 0.04,
hardware 0.02; total 0.80 kg) the centre of mass is 159 mm above the deck (was 211 mm). A sideways acceleration of 1 g (a tipping rover)
puts about **1.25 N.m** on the base joint; 0.43 N.m on a 20 degree slope. The extrusion is a stiff column (40 x 40 section); the joint at
the plate is the weak point and no stress check has been done.

## Open

- Servos and camera module are candidates only (`electronics-spec.md`), none bought.
- The wires from the head down the extrusion's slots and into the body: where they enter the deck is reserved in
  `interior-spec.md` (a 15 x 40 x 30 mm zone under the base), but the entry is not designed.
- The plate is held by 4 M4 bolts through the deck into two frame rails (`frame-spec.md`); the bolts themselves, how the plate fixes to the
  extrusion (corner brackets or end-tapped screws) and the joint's strength are not modelled.
- Servos sit in the printed neck and arm as before; the extrusion has no cavity for them.
- Stowing: deferred. The stowed height limit (120 mm above the deck [S19]) is not met by this mast.
