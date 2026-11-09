# المَهَا (al-maha): Rashid lunar rover replica

A scale-1:1, looks-like and works-like replica of the UAE's **Rashid** lunar rover (built by
MBRSC, Dubai), renamed **المَهَا** (al-maha, the Arabian oryx). It is a hobby build in the spirit
of Sawppy or the Beatty sisters' rover replicas, not an exact copy of the flight rover.

## Scope: what "replica" means here
- **Goal:** a rover that externally resembles Rashid and whose function roughly follows it,
  at full size (about 470 x 500 mm, 200 mm wheels), that one person can build and afford.
- **Must be recognisably Rashid** (match the sourced dimensions and shape):
  1. Wedge body with 10 degree sidewalls (panels at 80 degrees).
  2. Skeletonized wheels, 200 x 80 mm, 14 radial grousers of 15 mm.
  3. 5 x 3 solar cell fields on both sloped faces (dummy cells now, with provisions for real ones).
  4. Mast and camera: a square column on the front deck (a 40 mm T-slot extrusion, slimmer than the original's 58 mm tube) carrying a pan-tilt head and camera at the stated
     height. Fixed upright for now; the original's stow-and-deploy (flat under 120 mm, springs up) is deferred.
  5. Overall envelope: about 474 x 497 mm over the wheels, 700 mm tall with the mast up.
- **Must work, roughly as the original does:** four driven wheels, skid steering, a passive
  differential suspension (no rocker, no springs), a mast that pans and tilts, and a live camera on it. No science payload instruments.
- **Free to differ:** materials (the original is magnesium alloy with MLI; the replica can be
  printed plastic, aluminium or whatever builds easily), internal structure, fasteners, motors,
  electronics and battery (choose off-the-shelf parts), thermal and space hardware. **Mass:** the target is
  the original's 10 kg. The first pass is not optimised for mass: size the system (motors, drivers, battery,
  bearings, shafts) for 10 kg. A second pass trims toward 10 kg where it comes out over, but 10 kg is a goal, not a hard limit (owner, 2026-11-08): the ceiling is 10.5 kg, and no part is weakened or made non-metal just to reach 10 (the original uses ultra-light materials). Document each substitution in `docs/bom.md`.
- **Out of scope:** flight qualification, vacuum or thermal fidelity, the science
  instruments (Langmuir probes, microscope, thermal camera, sampler). No cosmetic dummies of them either (owner, 2026-11-08): al-maha is a Rashid-like rover, not Rashid, in the model and in the simulation.

## Dimensional record
- The original's real dimensions remain the reference for the five "must" items above. Design
  choices that affect them follow the sources, not the other way round. Beyond those items,
  accuracy is still preferred wherever a source exists and it does not make the build impractical;
  where there is no source, or accuracy would cost too much, choose for buildability and say so.
- Primary-source figures are recorded in `docs/original-dimensions.md`, with a source tag and a
  status (stated / derived / unverified) on every value. Check it before designing anything and
  update it when a new source is read. Headline: 10 kg; 470 x 505 mm footprint and 700 mm height
  with the mast deployed (MBRSC, EGU 2021); four wheels of 200 mm diameter and about 80 mm width.
- Record every dimension with its source. Mark anything without one **(unverified)**.
- Open gaps are listed in that file (section 7). Settled from the final-configuration CAD and
  MBRSC statements: wheel 200 x 80 mm, width over wheels about 497 mm, sidewall 10 degrees, 5 x 3
  cells per side of about 69 x 39 mm, stowed envelope about 474 x 497 x 468 mm. Still open:
  differential placement and drivetrain layout, the exact cell part, battery and motor
  specifications. Under this scope those gaps no longer block the build: pick a sensible design,
  label it ASSUMPTION, and swap it if a source appears. Do not present it as the original's.

## Repo layout
- `hardware/`: CAD. `hardware/wheel/wheel.py` is the parametric wheel model and `hardware/body/body.py` the body, wheels and deployed-mast envelope (build123d, venv in `.venv`).
- `docs/`: sourced reference material. `frame-spec.md` is the chassis (T-slot frame and panels). `mass-budget.md` is the generated mass and centre-of-mass check. `bom.md` is the BOM skeleton. `original-dimensions.md` is the record of the original rover's dimensions. `wheel-spec.md` is the wheel specification for CAD, built from it.
- `graphic-design/`: wordmark and poster. Has its own README. Separate from the rover engineering.
- `../maha-rover-private` (private GitHub repo `jacob-rn-wallace/maha-rover-private`, cloned beside this one; needs
  credentials): the Rashid papers and abstracts (`papers/INDEX.md` maps the source tags of
  `docs/original-dimensions.md` to files), solar cell datasheets, saved web pages and press photos, and the notes
  from earlier sessions (`previous-context/`, background only, do not edit). Its contents are copyrighted: never copy
  files from it into this repo, record only numerical facts and citations here.

## Design status
Settled from the final-configuration CAD and MBRSC statements (sources in
`docs/original-dimensions.md`; section 6 there is the item-by-item comparison):
- Body: wedge with 10 degree sidewalls (panels at 80 degrees, stated [S20]), underside
  about 124 mm and deck top about 348 mm above ground, top width about 164 mm, side
  plates about 380 mm, top plate 401 mm. Envelope model: `hardware/body/body.py`.
- Solar (decided 2026-11-07): 2 panels, one per sloped side, on the original's 5 x 3 slots. Cells: SunPower-type back-contact silicon (no front
  contacts, so a uniform dark look), tiled **two 31 x 41.6 mm pieces per slot** (cut from 125 x 41.6 mm third-cut strips), 30 pieces per side in
  one series string: 18.75 V Vmpp, about 21 V Voc, about 9.6 W at one sun (retailer's figures, scaled). Columns on the original's 71.6 mm pitch, rows at 42.5 mm;
  field at z 193 to 317 (the original's 196 to 314, `original-dimensions.md` 3k). Six 5 mm wire holes per side panel at the row ends (12 in all). Charger: a
  cheap BQ24650 or CN3722 buck 2S MPPT module (`docs/charger-board-spec.md`); no custom board. About US$45 to 61 for cells and charger. Specs and checks:
  `docs/solar-spec.md`, `hardware/solar/solar.py`, `docs/images/solar-cell-mockups.png`. Fallbacks: Futurlec SZGD6030, then one piece per slot. Open: real cells'
  authenticity and rear pad layout, the cutting method, protection.
- Wheels: 200 x 80 mm, 14 radial grousers of 15 mm, skeletonized, Mg alloy
  (`hardware/wheel/`).
- Mast: fixed upright, a 40 x 40 T-slot aluminium extrusion (decided 2026-11-07) on a rotating spindle above a pan drive in a die-cast aluminium box (Takachi AL080807, lid on top; the pan servo is in the base), centred 24.2 mm ahead of the front axle, carrying a head at the stated height: a 2 mm aluminium sheet bracket (a web bolted to the extrusion's +y face with two edge flanges; the owner's simplified redesign, its outline traced from the original's arm) holding the tilt servo, a sideways disk, a die-cast aluminium camera box (Takachi AL060605, 64 x 58 x 46 mm; camera axis at z 667) with a Raspberry Pi HQ camera and 4 mm CS lens behind a printed baffle ring and hood and a flat hat, tilting 90 degrees either way (`hardware/mast/headb.py`) (`docs/mast-spec.md`, `hardware/mast/mast.py`, built into the body model). Sizes from the
  CAD figures (`original-dimensions.md` 3j). Stowing is deferred; the hinged design is in commit `20aec90`.
- Drive and suspension: 4 in-wheel motors [S3]; skid steering; passive differential gear
  suspension, no rocker, no springs or dampers [S25]. Layout and motor type still unsourced.
- Structure mass: 2 kg excluding mobility [S26].

- Chassis: T-slot frame behind sheet panels (`docs/frame-spec.md`, `hardware/chassis/frame.py`).

Dropped from the earlier sessions' provisional design (an AI-chat brainstorm, never checked against the
original): the 6U CubeSat envelope (100 x 200 x 340.5), 15 degree sidewalls, the 170 x 112 mm PET panels
(4 per side), and the Nomad-style rocker with Double Ackermann steering (the original is a passive
differential with skid steering [S25]). The extrusion-frame idea from those sessions is back, resized.

## Licensing
- **Code** (scripts, firmware, tools): Apache-2.0 (`LICENSE`)
- **Hardware** (CAD, drawings, schematics, mechanical docs, BOM): CERN-OHL-S-2.0 (`LICENSE-HARDWARE.txt`)
- **Graphics and other docs** (wordmark, poster, headers, READMEs): CC BY 4.0 (`LICENSE-DOCUMENTATION.txt`)
- Third-party material (NASA photos in `graphic-design/source-photos/`) is covered by `NOTICE.md`, not these licences.

## Status
- Done: first pass at sourcing the original's dimensions from MBRSC and
  instrument-team papers (`docs/original-dimensions.md`). A WebAR model of the
  rover from 2023 was looked for and is gone (hosted on 8th Wall, now offline).
- Done: wheel CAD (`hardware/wheel/`); body envelope with cells and mast
  (`hardware/body/`); mass budget and centre-of-mass range (`docs/mass-budget.md`); BOM skeleton
  (`docs/bom.md`). The mass budget is a record of the original (4.75 kg of its 10 kg is
  unallocated); the replica's own mass goal is 10 kg with a 10.5 kg ceiling (see the scope above).
- Drive decision (2026-11-07): Pololu 37D gearmotors (spur/helical, not planetary) in the hubs, no
  encoders (only speed and direction matter); candidate #4746, 131:1. The shaft carries torque only; the
  wheel rides on two bearings on the motor housing. Spec: `docs/drive-spec.md`. CAD and clearance
  check: `hardware/drive/motor.py`. Open: bearing loads, concentricity, can clamp.
- Suspension decision (2026-11-07): passive bevel gear differential (decided 2026-11-07, `docs/differential-spec.md`: module 1.5 mitre gears, 12 mm tube shafts (8 mm stub in the housing), a motor current
  cap of 1.6 A) inside the body joining two rigid side link plates, body as carrier. The plate and pivot position (about 147 mm above the ground
  line, at the wheelbase midpoint) come from the CAD figures (`original-dimensions.md` 3i); the
  differential itself is an interpretation of [S25]. Spec: `docs/suspension-spec.md`. CAD and
  clearance sweep: `hardware/suspension/arms.py`. Gear train, strength still open.
- Chassis (2026-11-07): the earlier T-slot extrusion idea returns, resized from 4040 to 20 x 20: a T-slot aluminium frame (17 members, all vertical or horizontal, 2.14 kg) behind 2 mm aluminium panels
  (3 mm deck), the differential held by two cross rails, the pivot shafts (12 mm 4130 tubes, checked for bending in `hardware/chassis/rail_check.py`, bonded into the link plate bosses) running through 16 mm holes drilled in single 20 x 40 bottom side rails (bonded sleeve and igus-type flanged bushings) and supported again in the differential housing wall; the housing hangs from the cross rails by four lugs. Every
  extrusion is cut square and either vertical or horizontal (owner's sketch, 2026-11-07): a stepped frame, wide at the bottom and narrow at the top, joined by vertical posts. Only the side panels lean at 10 degrees: they are separate 2 mm plates (the solar panels) held about 10 mm off the frame on four pivot standoffs each near the corners, as the original's panels stand proud of its body (`original-dimensions.md` 3f). Corner brackets join rails, M4 screws fix panels,
  the deck is the lid carrying the mast. Spec: `docs/frame-spec.md`; CAD and checks:
  `hardware/chassis/frame.py`. Chassis 4.1 kg, with the front and rear panels recessed to the wheel axle line over their full height with three gussets per end under the deck's overhang and the mast bolted to the deck alone, no rail under it (`original-dimensions.md` 3n, `interior.py`, `frame.py`); replica mass estimate from the CAD 9.56 kg, 0.44 kg under the 10 kg goal ( levers in `docs/replica-mass.md`) (0.84 kg of it allowances; `docs/replica-mass.md`, `hardware/mass/replica.py`); centre of mass z 235 mm.
- Power system (2026-11-07): 2S2P pack (4 x Samsung 30Q) behind a 2S common-port BMS; node, then a 15 A main fuse, a master switch (rear
  panel) and a 4-way fuse block to the drivers, the 5 V converter and a 6 V servo regulator (the servos are rated 6 to 7.4 V, below a full pack); the solar
  charger joins at the node ahead of the switch. About 5.1 A continuous and 13.2 A peak. Motor wires run through hollow pivot shafts. Spec:
  `docs/power-spec.md`. Candidates only.
- Body interior (2026-11-07): battery rear and electronics front, the Pi, the two driver carriers, the converters, the fuse block and the switch are dimensioned models from vendor drawings (`hardware/electronics/boards.py`, `docs/electronics-spec.md`), the battery, BMS, power node and charger module are still boxes. Spec:
  `docs/interior-spec.md`. Fit check: `hardware/body/interior.py`. Electronics follow the shortlist in `docs/electronics-spec.md` (candidates, not bought).
- Still to do, in rough order: confirm the electronics shortlist (`docs/electronics-spec.md`) and the exact
  drive motor; design the differential's gear train; settle the cell mounting, the cradles that hold the differential,
  the 12 x 2 mm 4130 shaft tube's availability, the drilled rail hole against the profile's slots, the bushing flange size and rating, and a connector for the mast cable; reassess the mass and centre of mass for the
  replica's own parts; then a second pass toward 10 kg (ceiling 10.5) if the real parts come out over; fill the
  rest of the BOM's "Replica" column. Deferred: mast
  stowing. Closing the section 7 gaps is optional: only chase a source when it changes one of the "must" items.

## Constraints
- **Purchases deferred (owner, 2026-11-07), for the foreseeable future:** nothing is to be bought. Work is design, CAD and research; prices in the docs
  are for planning only, and parts "chosen" are candidates. Do not recommend ordering anything or treat a purchase as the next step.

## Conventions
- Hardware units are millimetres.
- Label unverified facts as such. Do not state remembered figures as sourced.
- Keep Arabic text with its diacritics: المَهَا.
