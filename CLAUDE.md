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
- `docs/`: sourced reference material. `original-dimensions.md` is the record of the original rover's dimensions. `wheel-spec.md` is the wheel specification for CAD, built from it.
- `graphic-design/`: wordmark and poster. Has its own README. Separate from the rover engineering.
- `previous-context-do-not-track/`: notes from earlier sessions. Background only. Gitignored, so it never goes on GitHub. Do not edit.

## Provisional design (from earlier sessions, NOT checked against the original)
These came from earlier AI chat sessions. They describe a rover *inspired by*
Rashid, before the project became a faithful replica. They do not bind the
replica. Where they conflict with the original rover's dimensions, the original
wins. `docs/original-dimensions.md` section 6 compares each item. Known
mismatches: the 6U CubeSat envelope (the original is 470 x 505 x 700 mm), the
PET panel size and count, the Ackermann steering, and the missing mast.
- Body: tapered trapezoidal prism with 15 degree sidewalls, sized around a
  6U CubeSat envelope of 100 x 200 x 340.5 mm. The 15 degree angle and the envelope are unverified.
- Frame: "zero-cut" box core of supplier-cut 40120 / 4040 aluminum extrusion
  with 1.5 mm cladding for the wedge.
- Solar: 170 x 112 mm PET panels, 4 per side.
- Wheels: 200 x 80 mm, hub plus TPU tire with chevron grousers, in-wheel planetary motors.
- Suspension and steering: 4-wheel rocker with Nomad-style Double Ackermann, one servo per side.
- Extrusions are ground and testbed hardware only. This is not a flight design.

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
  drivetrain layout, cell part, a dimensioned drawing), reconcile the provisional
  design (sidewall angle, panels and mast already differ), power and battery sizing,
  centre-of-mass check, CAD (the wheel is the natural first part), BOM.

## Conventions
- Hardware units are millimetres.
- Label unverified facts as such. Do not state remembered figures as sourced.
- Keep Arabic text with its diacritics: المَهَا.
