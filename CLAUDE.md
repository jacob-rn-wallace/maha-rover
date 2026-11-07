# المَهَا (al-maha): Rashid lunar rover replica

A replica of the UAE's **Rashid** lunar rover (built by MBRSC, Dubai), renamed
**المَهَا** (al-maha, the Arabian oryx). The goal is to match the original
rover's dimensions as faithfully as possible.

## Primary goal: dimensional fidelity
- The original rover's real dimensions are the source of truth. Design choices
  follow them, not the other way round.
- Primary-source figures are recorded in `docs/original-dimensions.md`, with a
  source tag and a status (stated / derived / unverified) on every value. That
  file is the dimension record. Check it before designing anything, and update
  it when a new source is read. Headline: 10 kg; 470 x 505 mm footprint and
  700 mm height with the mast deployed (MBRSC, EGU 2021); four wheels of 200 mm
  diameter and about 80 mm width. Press figures (50 x 50 cm) agree roughly and
  are superseded.
- Record every dimension with its source. Mark anything without one **(unverified)**.
- Open gaps are listed in that file (section 7). Settled from the final-configuration CAD
  and MBRSC statements: wheel 200 x 80 mm, width over wheels about 497 mm, sidewall 10 degrees
  (panels at 80 degrees), 5 x 3 cells per side of about 69 x 39 mm, stowed envelope about
  474 x 497 x 468 mm. Still open: suspension and drivetrain layout, the exact cell part,
  battery and motor specifications. Do not paper over them.

## Repo layout
- `hardware/`: CAD. `hardware/wheel/wheel.py` is the parametric wheel model and `hardware/body/body.py` the body, wheels and deployed-mast envelope (build123d, venv in `.venv`).
- `docs/`: sourced reference material. `original-dimensions.md` is the record of the original rover's dimensions. `wheel-spec.md` is the wheel specification for CAD, built from it.
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
- Drive: 4 in-wheel motors [S3], with a differential gear or linkage [S1] (unresolved).

Still provisional, from earlier AI chat sessions, NOT checked against the original (they
do not bind the replica; the original wins):
- Suspension and steering: 4-wheel rocker with Nomad-style Double Ackermann. The original's
  steering is not described, so do not carry Ackermann over.
- Frame: "zero-cut" box core of supplier-cut 40120 / 4040 aluminum extrusion with 1.5 mm
  cladding. The original is a magnesium alloy frame with MLI. Extrusions are ground and
  testbed hardware only, not a flight design.
- Dropped: the 6U CubeSat envelope (100 x 200 x 340.5), 15 degree sidewalls, and the
  170 x 112 mm PET panels, 4 per side.

## Licensing
- **Code** (scripts, firmware, tools): Apache-2.0 (`LICENSE`)
- **Hardware** (CAD, drawings, schematics, mechanical docs, BOM): CERN-OHL-S-2.0 (`LICENSE-HARDWARE.txt`)
- **Graphics and other docs** (wordmark, poster, headers, READMEs): CC BY 4.0 (`LICENSE-DOCUMENTATION.txt`)
- Third-party material (NASA photos in `graphic-design/source-photos/`) is covered by `NOTICE.md`, not these licences.

## Status
- Done: first pass at sourcing the original's dimensions from MBRSC and
  instrument-team papers (`docs/original-dimensions.md`). A WebAR model of the
  rover from 2023 was looked for and is gone (hosted on 8th Wall, now offline).
- Still to do: close the remaining gaps in section 7 of that file (suspension and
  drivetrain layout, cell part, a dimensioned drawing), power and battery sizing,
  centre-of-mass check, BOM. First wheel CAD model (`hardware/wheel/`) and first body envelope model (`hardware/body/`) done; refine their unsourced choices as sources arrive. Body model still lacks suspension and internals, and its mast is a placeholder.

## Conventions
- Hardware units are millimetres.
- Label unverified facts as such. Do not state remembered figures as sourced.
- Keep Arabic text with its diacritics: المَهَا.
