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
  4. Deployable mast and camera: stows flat along the top panel, rotates up to vertical.
  5. Overall envelope: about 474 x 497 mm over the wheels, 700 mm tall with the mast up.
- **Must work, roughly as the original does:** four driven wheels, skid steering, a passive
  differential suspension (no rocker, no springs), a mast that deploys and pans and tilts, and a
  live camera on it. No science payload instruments.
- **Free to differ:** materials (the original is magnesium alloy with MLI; the replica can be
  printed plastic, aluminium or whatever builds easily), internal structure, fasteners, motors,
  electronics and battery (choose off-the-shelf parts), the 10 kg mass, thermal and space
  hardware. Document each substitution in `docs/bom.md`.
- **Out of scope:** flight qualification, vacuum or thermal fidelity, exact mass, the science
  instruments (Langmuir probes, microscope, thermal camera, sampler).

## Dimensional record
- The original's real dimensions remain the reference for the five "must" items above. Design
  choices that affect them follow the sources, not the other way round. Where something is not
  one of those items, choose for buildability, and say so.
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
- `docs/`: sourced reference material. `mass-budget.md` is the generated mass and centre-of-mass check. `bom.md` is the BOM skeleton. `original-dimensions.md` is the record of the original rover's dimensions. `wheel-spec.md` is the wheel specification for CAD, built from it.
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
- Mast: about 300 mm, stowed along the top panel, spring hinge to vertical; CAM-1 on a
  pan and tilt gimbal. Both deployed and stowed (folded rearward, an assumption) envelopes are in the body model;
  the mast cross-section and gimbal head are placeholder sizes.
- Drive and suspension: 4 in-wheel motors [S3]; skid steering; passive differential gear
  suspension, no rocker, no springs or dampers [S25]. Layout and motor type still unsourced.
- Structure mass: 2 kg excluding mobility [S26].

Still provisional, from earlier AI chat sessions, NOT checked against the original (it
does not bind the replica; the original wins):
- Frame: "zero-cut" box core of supplier-cut 40120 / 4040 aluminum extrusion with 1.5 mm
  cladding. The original is a magnesium alloy frame with MLI. Extrusions are ground and
  testbed hardware only, not a flight design.
- Dropped: the 6U CubeSat envelope (100 x 200 x 340.5), 15 degree sidewalls, the
  170 x 112 mm PET panels (4 per side), and the Nomad-style rocker with Double Ackermann
  steering (the original is a passive differential with skid steering [S25]).

## Licensing
- **Code** (scripts, firmware, tools): Apache-2.0 (`LICENSE`)
- **Hardware** (CAD, drawings, schematics, mechanical docs, BOM): CERN-OHL-S-2.0 (`LICENSE-HARDWARE.txt`)
- **Graphics and other docs** (wordmark, poster, headers, READMEs): CC BY 4.0 (`LICENSE-DOCUMENTATION.txt`)
- Third-party material (NASA photos in `graphic-design/source-photos/`) is covered by `NOTICE.md`, not these licences.

## Status
- Done: first pass at sourcing the original's dimensions from MBRSC and
  instrument-team papers (`docs/original-dimensions.md`). A WebAR model of the
  rover from 2023 was looked for and is gone (hosted on 8th Wall, now offline).
- Done: wheel CAD (`hardware/wheel/`); body envelope with cells and stowed mast
  (`hardware/body/`); mass budget and centre-of-mass range (`docs/mass-budget.md`); BOM skeleton
  (`docs/bom.md`). The mass budget is a record of the original (4.75 kg of its 10 kg is
  unallocated); the replica's own mass is free under the scope above.
- Still to do, in rough order: choose and place the drive motors, the passive differential and
  the electronics (off the shelf); design the mast, its deploy hinge and pan-tilt, and pick the
  camera; turn the envelope body into a buildable one (material, joints, cell mounting); reassess
  the mass and centre of mass for the replica's own parts; fill the BOM's "Replica" column.
  Closing the section 7 gaps is now optional: only chase a source when it changes one of the
  five "must" items.

## Conventions
- Hardware units are millimetres.
- Label unverified facts as such. Do not state remembered figures as sourced.
- Keep Arabic text with its diacritics: المَهَا.
