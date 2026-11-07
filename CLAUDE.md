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
  3. 5 x 3 solar cell fields on both sloped faces (printed or dummy cells are fine).
  4. Mast and camera: a square tube on the front deck carrying a pan-tilt head and camera at the stated
     height. Fixed upright for now; the original's stow-and-deploy (flat under 120 mm, springs up) is deferred.
  5. Overall envelope: about 474 x 497 mm over the wheels, 700 mm tall with the mast up.
- **Must work, roughly as the original does:** four driven wheels, skid steering, a passive
  differential suspension (no rocker, no springs), a mast that pans and tilts, and a live camera on it. No science payload instruments.
- **Free to differ:** materials (the original is magnesium alloy with MLI; the replica can be
  printed plastic, aluminium or whatever builds easily), internal structure, fasteners, motors,
  electronics and battery (choose off-the-shelf parts), thermal and space hardware. **Mass:** the target is
  the original's 10 kg. The first pass is not optimised for mass: size the system (motors, drivers, battery,
  bearings, shafts) for 10 kg. A second pass brings the build down to 10 kg where it comes out over. Document each substitution in `docs/bom.md`.
- **Out of scope:** flight qualification, vacuum or thermal fidelity, the science
  instruments (Langmuir probes, microscope, thermal camera, sampler).

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
- `previous-context-do-not-track/`: notes from earlier sessions. Background only. Gitignored, so it never goes on GitHub. Do not edit.

## Design status
Settled from the final-configuration CAD and MBRSC statements (sources in
`docs/original-dimensions.md`; section 6 there is the item-by-item comparison):
- Body: wedge with 10 degree sidewalls (panels at 80 degrees, stated [S20]), underside
  about 124 mm and deck top about 348 mm above ground, top width about 164 mm, side
  plates about 380 mm, top plate 401 mm. Envelope model: `hardware/body/body.py`.
- Solar: 2 panels, one per sloped side, 5 x 3 cells of about 69 x 39 mm each, modelled as thin plates in
  `hardware/body/body.py`. Their position on the face is an assumption (centred).
- Wheels: 200 x 80 mm, 14 radial grousers of 15 mm, skeletonized, Mg alloy
  (`hardware/wheel/`).
- Mast: fixed upright, tube 58 x 58 mm centred 24.2 mm ahead of the front axle, pan-tilt head and CAM-1 at
  the stated height (`docs/mast-spec.md`, `hardware/mast/mast.py`, built into the body model). Sizes from the
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
  unallocated); the replica's own mass target is 10 kg (see the scope above).
- Drive decision (2026-11-07): Pololu 37D gearmotors (spur/helical, not planetary) in the hubs, no
  encoders (only speed and direction matter); candidate #4746, 131:1. The shaft carries torque only; the
  wheel rides on two bearings on the motor housing. Spec: `docs/drive-spec.md`. CAD and clearance
  check: `hardware/drive/motor.py`. Open: bearing loads, concentricity, can clamp.
- Suspension decision (2026-11-07): passive bevel differential inside the body joining two rigid
  side link plates, body as carrier. The plate and pivot position (about 147 mm above the ground
  line, at the wheelbase midpoint) come from the CAD figures (`original-dimensions.md` 3i); the
  differential itself is an interpretation of [S25]. Spec: `docs/suspension-spec.md`. CAD and
  clearance sweep: `hardware/suspension/arms.py`. Gear train, strength still open.
- Chassis (2026-11-07): the earlier T-slot extrusion idea returns, resized from 4040 to 20 x 20: a T-slot aluminium frame (19 members, 1.92 kg) behind 2 mm aluminium panels
  (3 mm deck), the differential held by two cross rails, 6800 bearings in 6 mm plates in the side walls. Every
  extrusion is cut square; printed wedges absorb the 10 degrees. Corner brackets join rails, M4 screws fix panels,
  the deck is the lid carrying the mast. Spec: `docs/frame-spec.md`; CAD and checks:
  `hardware/chassis/frame.py`. Chassis 4.4 kg; first replica estimate about 9 kg, under the 10 kg target (every line a guess, see the spec).
- Body interior (2026-11-07): battery rear and electronics front, cable-entry keep-out under the mast base. Spec:
  `docs/interior-spec.md`. Fit check: `hardware/body/interior.py`. Electronics follow the shortlist in `docs/electronics-spec.md` (candidates, not bought).
- Still to do, in rough order: confirm the electronics shortlist (`docs/electronics-spec.md`) and the exact
  drive motor; design the differential's gear train; settle the cell mounting, the cradles that hold the differential,
  the bearing plate fixing and a connector for the mast cable; reassess the mass and centre of mass for the
  replica's own parts; then a second pass to bring the total to 10 kg if the real parts come out over; fill the
  rest of the BOM's "Replica" column. Deferred: mast
  stowing. Closing the section 7 gaps is optional: only chase a source when it changes one of the "must" items.

## Conventions
- Hardware units are millimetres.
- Label unverified facts as such. Do not state remembered figures as sourced.
- Keep Arabic text with its diacritics: المَهَا.
