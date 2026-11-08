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
spindle flange (the whole mast turns on a pan drive in a housing on the deck, below) and carries the bent sheet bracket and head (section "Built head" below) on its top end.

**Pan base (added 2026-11-07, owner's request: the original's pan motor is in the block at the mast base).** `hardware/mast/base.py`: a 76 x 76 printed housing (2.5 mm walls, z 354 to 438) on the base plate holds the pan
servo (STS3215, shaft vertical on the mast axis, z 356 to 393) and a bearing tower with two 30 x 42 x 7 mm bearings (6806 size) 30 mm apart at z 403.5 and 433.5. An aluminium spindle (tube 30/22) runs through them, joined to the servo's upper horn
by a 36 mm coupling disc below and carrying a 60 mm flange at z 440 to 446 on which the extrusion stands (now z 446 to 577, 0.24 kg instead of 0.41 kg). The servo only turns the mast; the bearings carry the weight and bending: at 1 g sideways
45 N on each bearing (135 N at 3 g) from the 1.56 N.m moment, nothing on the servo's own output bearing. The cables run down the extrusion slots, through the hollow spindle (22 mm bore) and out through a 10 mm hole in the coupling disc, then through the deck keep-out.
The original's block is about 90 mm fore-aft [3j]; this one is 76. Not designed: the compliant joint between servo horn and disc, axial retention of the bearings, the hard stop for the 320 degree range, the cable loop, how the housing bolts to the base plate and the plate to the deck, and sealing. Bearing rating and mass (0.024 kg each) are not looked up.
Servo torque: 1.91 N.m stall, 0.64 N.m continuous (`electronics-spec.md`) against a small head inertia; not analysed further.

| Item | Value | Status |
|---|---|---|
| Extrusion | 40 x 40 mm T-slot (Misumi HFS8-4040 class, about 1.86 kg/m; catalogue entries run 1.73 to 1.90 kg/m by variant), z 354 to 577, centre 24.2 mm ahead of the front axle (x 160.7), cut square, 223 mm, 0.41 kg | position and top height derived [3j]; section ASSUMPTION |
| Base plate | 76 x 76 x 6 mm aluminium on the deck (z 348 to 354), 4 M4 bolts at x 141 and 178, y +-30, through the deck into the mast cross rail and front end rail (`frame-spec.md`) | ASSUMPTION |
| Bracket (replaces neck and C-arm) | 2 mm aluminium sheet, 44 mm wide, from z 545 to 697: a 45 degree S-bend towards +y over about z 577 to 626, then an arm at y +27 to +69; the original's arm outline [S18] Fig. 1 | derived by eye [3j], [S18] |
| Head | camera housing 60 x 72 mm, z 621 to 700, centred 28 mm right of the centreline | derived [3j], [S8] |
| Camera | CAM-1 35 x 35 x 73 mm, axis at z 660, lens front 77.9 ahead of the front axle | stated [S12], [S8] |
| Top | z 700 | stated [S1] |

**Departure from the original.** The original's mast tube measures about 58 mm square [3j]. The replica's extrusion is 40 mm, so the
visible column is slimmer below the 58 mm printed neck. A 60 x 60 extrusion would match, but at about 4.17 kg/m it would weigh 0.93 kg
(0.52 kg more) and the mass margin would shrink to about 0.1 kg; a 40 x 60 would be a compromise (not looked up). The extrusion's end is
tapped (M8) to take the neck's base plate; its slots carry the camera and servo cables, and the centre bore can pass a connector lead.

The original's mast is additively manufactured ULTEM 1010 with titanium and aluminium parts [S19]; the replica's neck, arm and head are printed
(material not chosen).

## Actuation and the head's parts (2026-11-07)

(Superseded by the built head below.) The head was no longer solid boxes: `hardware/mast/head.py` builds the neck, C-arm, camera housing and camera tube as **2 mm printed shells** (ASSUMPTION: PETG, solid
walls) with real parts inside. The outer sizes still follow the CAD figures (3j).

- **Pan servo (vertical axis, now in the base, see above; its description here applies):** a Feetech STS3215-class servo modelled from the Waveshare ST3215 2D drawing (2022-06-08) and its STEP model: body
  45.22 x 24.72 x 32 mm, output shaft 10.11 mm from one end of the long side, a 19.2 mm horn disc at each end, 37.25 mm overall along the shaft. The Waveshare part is the same
  size as the 45.2 x 24.7 x 35 mm STS3215 of the retailers and the Feetech datasheet; the equivalence is assumed, and the Feetech datasheet read has no drawing. The shaft is on
  the mast axis and the long side points +y. It stands on the housing floor (the earlier neck position is replaced). The horn hole pattern (a 14 mm pattern on the drawing) and the
  mounting ears are not modelled, and the compliant coupling between the horn and the coupling disc is not designed.
- **Tilt servo (horizontal axis, in the C-arm):** the same servo, shaft along y at z 660, body below the shaft, centred in the arm (y 28.9 to 66.1 in a 27 to 68 cavity).
- **Camera:** a Raspberry Pi Camera Module 3 (standard lens) modelled from the product brief p. 4 (PCB 25 x 23.862 x 1.12, four 2.2 mm holes, 10.8 mm square lens block, 11.3 mm
  total, lens centre 12.5 mm from the side and 14.4 mm from the bottom edge) inside the printed 35 x 35 x 73 mm CAM-1 tube [S12], its lens against a 12 mm aperture in the front wall.
  The FPC connector block is ASSUMPTION. The standard lens (75 degrees) is closer to the original's 80 degrees [S12] than the wide one (120).
- **Wires:** from the head down the extrusion's slots; the cable path, strain relief and the connector at the lid are not designed.

## CAD checks

- Top at 700 (stated); camera axis 660; lens front 214.4 (front axle at 136.5 + 77.9), which is 24 mm ahead of the body's front end (190).
- The base plate lies wholly on the deck plate (5776 of 5776 mm2) and does not touch the body or the cells.
- **Fit:** both servos and the camera module lie wholly inside their shells; no part of the head clashes with another.
- **Pan sweep, plus or minus 180 degrees:** the whole turning mast (spindle, extrusion, neck, arm, head) clears the base plate, housing, servo and bearings (0 mm3 at every 30 degree step).
- **(Superseded by the built head below, which tilts 90 degrees.) Tilt sweep of the printed-shell head: it fails.** With the head as designed, the camera tube touches the housing after **5 degrees** of tilt in either direction, and the whole head tilting as one unit touches
  the neck after 5 degrees too. The original tilts plus or minus 75 degrees [S19]. The cause is the stated geometry: the head occupies z 621 to 700 about the camera axis (z 660), so
  its lower corners sweep down to about z 610 against the neck top at 621, over the part of the neck (y -29 to 8) that lies under the head. **This needs a design decision;** the options
  are in the Open list below.

## Loads

With catalogue and CAD masses (extrusion 0.24 kg and base plate 0.09 kg; pan housing 0.145 kg; spindle, flange and disc 0.09 kg; bearings 0.05 kg; bracket 0.096 kg; printed enclosure, hat and lens parts and the disk (0.015 kg, ASSUMPTION); camera body stand-in 0.010 kg (ASSUMPTION); two servos 0.11 kg; hardware 0.05 kg;
total 1.05 kg) the centre of mass is 151 mm above the deck. A sideways acceleration of 1 g (a tipping rover) puts about **1.56 N.m** on the base joint; 0.46 N.m on a 20 degree
slope. The extrusion is a stiff column (40 x 40 section); the joint at the plate is the weak point and no stress check has been done.

## Open

- **(Superseded, see the built head below.) Tilt range.** The printed-shell head cannot tilt plus or minus 75 degrees as modelled. Options (not chosen): (a) tilt only a small barrel or the lens inside a housing with a large front opening, which needs a different mechanism from a servo on the tube; (b) cut the tilt range to what fits (about 5 degrees now; a few tens of degrees if the housing's lower corners are rounded off and the neck narrowed under it, not worked out); (c) move the neck's footprint so it does not lie under the housing (the pan axis then moves off the mast centre line); (d) accept a tilt range far below the original's and note it. The original's actual head mechanism is not known from the sources read.

- Servos and camera module are candidates only (`electronics-spec.md`), none bought.
- The wires from the head down the extrusion's slots and into the body: where they enter the deck is reserved in
  `interior-spec.md` (a 15 x 40 x 30 mm zone under the base), but the entry is not designed.
- The plate is held by 4 M4 bolts through the deck into two frame rails (`frame-spec.md`); the bolts themselves, how the plate fixes to the
  extrusion (corner brackets or end-tapped screws) and the joint's strength are not modelled.
- The pan servo is in the base; the tilt servo sits in the arm; the extrusion has no cavity for them.
- Stowing: deferred. The stowed height limit (120 mm above the deck [S19]) is not met by this mast.


## Built head (2026-11-08): bent sheet bracket, `hardware/mast/headb.py`

**This supersedes the printed-shell head described above** (`head.py`: neck, C-arm, camera housing, camera tube, and the 5 degree tilt limit; `head.py` is kept for its servo and camera models). The head is now in `mast.py`
and the assembly render; `hardware/mast/head_concept.py` renders it alone to `docs/images/head-concept.png`. History: v3 (printed arm on an adapter plate, commit `2abb639`), then the owner's sheet-metal sketches
(2026-11-08) gave the bracket. Owner's rule (2026-11-07): keep what gives the original's silhouette and costs nothing, otherwise design for our parts.

- **Bracket:** one 2 mm aluminium blank, two folds (ASSUMPTION: 5052 sheet; bend radii and allowance not modelled). A web lies on the +y face of the extrusion, kinks out at 45 degrees over about z 577 to 626, and rises vertical
  at y +67 to +69 to z 697; two flanges straddle the extrusion (inner width 40) and follow the band, so the outline matches the arm in [S18] Fig. 1 (45 degree S-bend, arm at y +27 to +69). Fixing: two M6 per flange
  into T-nuts in the extrusion's side slots (4 in all); not yet checked against the profile's slot geometry. The tilt servo (STS3215, shaft along y at z 660) sits between the flanges (y 28.9 to 66.1, z 625 to 670),
  seen through a window in the web (36 x 42 mm). Servo ear screws to the flanges are not modelled. Mass 0.096 kg.
- **Camera unit** (tilts as one): a sideways disk (printed, 40 mm, y 2 to 22, encoder or mount; unknown in the original), a **die-cast aluminium enclosure, Takachi TD6-6-4** (60 x 60 x 35 mm, ADC12, 90 g, black painted or
  unfinished; catalogue drawing TD6-6-4B/N: walls 2 mm, internal maximum 50.3 x 36.3 x 31 mm, four M3.5 countersunk cover screws at +-25 mm; stated) with the cover at the front, and the CASPEX-look lens assembly bolted to the
  outside of the cover (45 mm cradle plate, collar, slotted baffle ring, black hood with a square window turned 8 degrees; [S5], [S12], `original-dimensions.md` 3l), and a flat round hat (70 mm; the CAD figure suggests up to 110 mm,
  planar antenna per the owner's reading) on top. The camera body inside is a 35 x 35 x 25 mm stand-in for a Camera Module 3 and its mount: it fits inside the 36.3 mm clear span with 0.65 mm to spare per side and 5.8 mm of
  depth. The box is only 35 deep, so the lens stack stands 48 mm out of the front (as the standard lens does on the original) and the box sits behind the tilt axis (box x 133.6 to 168.6, axis at 160.7: 9.6 mm ahead of the box
  centre). Sizes of disk, hat, collar and hood are by eye (ASSUMPTION). **Alternative:** Takachi AL060605 (64 x 46 x 58, IP65, gasketed, 162 g, grey, built to order with a 2 month lead time), a better seal but 72 g
  heavier and 11 mm deeper, which puts the box further behind the axis. Neither is bought (purchases deferred).
- **Checks (`mast.py`):** no overlaps among bracket, extrusion, servo, disk and enclosure; the pan sweep of the whole turning mast clears the base (0 mm3 at every 30 degrees); **the camera stack clears the box (0 mm3) and the camera unit tilts plus or minus 90
  degrees without touching the bracket, tilt servo or extrusion** (the original tilts 75 degrees [S19]).
- **Not designed:** drilling and tapping the die-cast box for the disk and the hat (ADC12 takes M3 taps), the lens hole in the cover (Ø35 in the model) and a cable slot in the base for the camera lead (the module's real connector and the 5.8 mm of spare depth are unchecked), servo horn to disk attachment, cable route through the bracket and down the extrusion slots, the open top of the extrusion under the bend, a hard stop for tilt, bend reliefs and the flat pattern,
  bracket stiffness (the web window is 36 mm of its 44 mm width), whether the printed enclosure is split for assembly, the octagonal hollow mast and lightening slots (not copied) and what the pink surface in the flight photo is (not known).
