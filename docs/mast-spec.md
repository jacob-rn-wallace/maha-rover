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

**Pan base (added 2026-11-07, owner's request: the original's pan motor is in the block at the mast base; redone 2026-11-08 around a die-cast box).** `hardware/mast/base.py`: a **Takachi AL080807** IP65 die-cast aluminium box (80 x 75 x 70 mm, 347 g, gasketed, M4
cover screws; drawing AL080807 (2025): cavity 70.5 x 66.8 at the mouth, interior height 62.75, base 55 deep, cover 15 deep; stated) stands on the base plate with its **lid on top** (z 354 to 424). The original's base block measures about 79 mm wide and 73 mm tall with its
top near z 425 (measured on Fig. 1, `original-dimensions.md` 3m): the box matches it. Inside: the pan servo (STS3215, shaft vertical on the mast axis, long side along y so the 45.2 mm body clears the 70.5 mm cavity by 0.1 mm; z 357.6 to 394.8), a coupling disc
on its upper horn, and an aluminium bearing tower (OD 52) hung under the lid holding two 30 x 42 x 7 mm bearings (6806 size) 12.6 mm apart, the upper one against the lid's underside (z 404.3 and 416.9). The aluminium spindle (tube 30/22) runs up through them and
a 36 mm hole in the lid to a 60 mm flange at z 426 to 432 on which the extrusion stands (now z 432 to 597). The servo only turns the mast; the bearings carry the weight and bending, with the lid carrying the bearings: mast, bearings, tower, lid, four M4 cover screws, base,
box, plate. With the bearings only 12.6 mm apart the radial load at 1 g sideways is 157 N each (471 N at 3 g) from the 1.98 N.m moment, three times the earlier 30 mm spacing; far below a 6806 bearing's rating (not checked). The cables run down the extrusion slots, through the hollow
spindle (22 mm bore) and out through a 10 mm hole in the coupling disc. Not designed: the lid's stiffness under that load (a 3.6 mm cast cap; a plate under it may be needed), the gasket and a seal where the spindle leaves the lid, fixing the box to the base plate (the box has two M4
external mounting holes) and the plate to the deck, the compliant joint between servo horn and disc, axial retention of the bearings, the hard stop for the 320 degree range, the cable loop. Mass: the box is 0.347 kg against 0.145 kg for the printed housing it replaces.

| Item | Value | Status |
|---|---|---|
| Extrusion | 40 x 40 mm T-slot (Misumi HFS8-4040 class, about 1.86 kg/m; catalogue entries run 1.73 to 1.90 kg/m by variant), z 354 to 597, centre 24.2 mm ahead of the front axle (x 160.7), cut square, 223 mm, 0.41 kg | position and top height derived [3j]; section ASSUMPTION |
| Base plate | 75 x 80 x 6 mm aluminium on the deck (z 348 to 354) under the die-cast box; the earlier 4 M4 bolts at x 141 and 178, y +-30 into the mast cross rail and front end rail (`frame-spec.md`) need re-checking for the new plate | ASSUMPTION |
| Bracket (replaces neck and C-arm) | a 2 mm aluminium web with two edge flanges, z 545 to 690, on the extrusion's +y face; the flange outline is the original's arm outline traced from [S18] Fig. 1 | derived by eye [3j], [S18] |
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

With catalogue and CAD masses (extrusion 0.31 kg and base plate 0.08 kg; die-cast pan box 0.347 kg; spindle, flange, disc and bearing tower 0.12 kg; bearings 0.05 kg; bracket 0.069 kg; die-cast camera box 0.162 kg, printed hat and lens parts and the disk (0.015 kg, ASSUMPTION); camera body stand-in 0.010 kg (ASSUMPTION); two servos 0.11 kg; hardware 0.05 kg;
total 1.42 kg) the centre of mass is 142 mm above the deck. A sideways acceleration of 1 g (a tipping rover) puts about **1.98 N.m** on the base joint; 0.46 N.m on a 20 degree
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

- **Bracket (owner's simplified redesign, 2026-11-08, from `mast_simplified_in_situ.step`; outline traced by the owner from the original's front view [S18] Fig. 1):** a 2 mm aluminium **web**, 40 mm wide, z 545 to 690, lying flat on the extrusion's
  +y face (y 20 to 22) with three Ø6.8 holes (z 555, 569 and 583; the first two are the owner's, the third was added with the taller extrusion) for M6 into the centre slot of that face, and a 2 mm **flange** along each side edge (x +-18 to +-20 from the mast axis) standing out to y 54: a point at the extrusion at z 545, a slant to full depth by
  z 566, vertical to z 635, then a slant in to y 36 at the top (z 690). It reaches 93 mm above the extrusion top (597) and carries the head; nothing straddles the extrusion. The tilt servo (STS3215, y 19.5 to 56.7) sits between the flanges against the web, its
  horn through a Ø19.2 hole at z 660, to the disk. Mass 0.070 kg. **The extrusion was raised from 577 to 597** (2026-11-08, on the owner's suggestion) to give the web 52 mm of bolted contact instead of 32: swept by the tilting camera box, contact with the extrusion starts at 65 degrees of tilt with the top at 605, so 597 keeps a margin (clear to 90 degrees both ways, checked in `mast.py`). The original's tube tops out at 577 [3j]; the extra 20 mm is hidden behind the bracket's web from the side but shows in the front view above the original's neck line. **Overlaid on the original's front view the outline follows the original's arm (outer edge, diagonal shoulder, top)**; the flat blank is simply a plate with two edge flanges, so it
  is one bent part (two bends along the long edges, no bends across the flanges). The earlier attempts (flanges running round the bends; mitred flanges; S-shaped plates) were my misreadings or an unmakeable blank and are replaced. Camera lateral
  position: in this version y -30.5 (the sourced figure is 28 right of the centreline [S8]); the disk is 20 mm long (y -0.5 to 19.5).
- **Camera unit** (tilts as one; positions measured against the original's Fig. 1, `original-dimensions.md` 3m): a sideways disk (printed, 40 mm across and 15.5 mm thick, y 4 to 19.5; the original's is about 56 mm across and 20.7 thick), a **die-cast aluminium box, Takachi AL060605**
  (IP65, 64 x 58 x 46 mm, 162 g, gasketed, grey, M4 cover screws on 52 x 46 mm; drawing AL060605 (2025): walls 3.7, cavity 56.6 x 50.6, cover cap 9 deep; stated) with the cover at the front (as the cover screws are on the front of the original's camera box), 64 mm wide across y, 58 mm tall, 46 deep,
  centred on the tilt axis, and the CASPEX-look lens assembly in front of it (40 mm cradle plate inside, collar through a 35 mm hole in the cover, slotted baffle ring, black hood with a square window turned 8 degrees; [S5], [S12], `original-dimensions.md` 3l), a flat round hat (70 mm, 4 mm thick,
  z 696 to 700) on top. The camera body inside is a 35 x 35 x 25 mm stand-in for a Camera Module 3 and its mount, against the back wall. The lens stands 31 mm out of the cover. **How cubic:** 64 x 58 x 46 (smallest over largest 0.72); the earlier TD6-6-4 was 60 x 60 x 35 (0.58); the original's box is
  about 57 wide x 56 tall x 59 deep (from Fig. 1, by eye). The AL series' smallest footprint is 64 x 58, so no AL model is closer to the original's 57 mm square; the AL080807 (80 x 75 x 70, 0.88) is more cubic but 40 percent wider than the original. **Position:** camera axis and tilt axis at **z 667**
  (lens centre and the original's motor disc centre both measure z 667 to 668 in the front view; the side view agrees; [S12] states 660 and an earlier side-view reading gave 664: the owner asked for the closest match to the original), camera at y -28 [S8], so the box edge is at y +4 and the disk fills the 15.5 mm from there to the web's pass-through hole (the web hole at z 667).
  Not checked: that the module and its 40 mm plate clear the cast screw posts (modelled as round 11 mm posts; the drawing leaves only 31.7 and 32.8 mm between them), drilling and tapping the box, the cable route.
- **Checks (`mast.py`):** no overlaps among bracket, extrusion, servo, disk and enclosure; the pan sweep of the whole turning mast clears the base (0 mm3 at every 30 degrees); **the camera stack clears the box (0 mm3) and the camera unit tilts plus or minus 90
  degrees without touching the bracket, tilt servo or extrusion** (the original tilts 75 degrees [S19]).
- **Not designed:** drilling and tapping the die-cast box for the disk and the hat (ADC12 takes M3 taps), the lens hole in the cover (Ø35 in the model) and a cable slot in the base for the camera lead (the module's real connector and the 5.8 mm of spare depth are unchecked), servo horn to disk attachment, cable route through the bracket and down the extrusion slots, the open top of the extrusion under the bend, a hard stop for tilt, bend reliefs and the flat pattern,
  bracket stiffness (the web window is 36 mm of its 44 mm width), whether the printed enclosure is split for assembly, the octagonal hollow mast and lightening slots (not copied) and what the pink surface in the flight photo is (not known).
