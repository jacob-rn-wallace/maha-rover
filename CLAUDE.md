# المَهَا (al-maha): Rashid lunar rover replica

A replica of the UAE's **Rashid** lunar rover (built by MBRSC, Dubai), renamed
**المَهَا** (al-maha, the Arabian oryx). The goal is to match the original
rover's dimensions as faithfully as possible.

## Primary goal: dimensional fidelity
- The original rover's real dimensions are the source of truth. Design choices
  follow them, not the other way round.
- Reported figures: about 10 kg, about 50 cm x 50 cm, four wheels (Gulf News,
  CNN). These are press figures. Find primary sources (MBRSC, mission
  documentation, photos with known scale) before treating any number as final.
- Record every dimension with its source. Mark anything without one **(unverified)**.

## Repo layout
- `graphic-design/`: wordmark and poster. Has its own README. Separate from the rover engineering.
- `previous-context-do-not-track/`: notes from earlier sessions. Background only. Gitignored, so it never goes on GitHub. Do not edit.

## Provisional design (from earlier sessions, NOT checked against the original)
These came from earlier AI chat sessions, before the project became a faithful
replica. Where they conflict with the original rover's dimensions, the original wins.
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
- Not started: sourcing the original's dimensions, reconciling the provisional
  design with them, power and battery sizing, centre-of-mass check, CAD, BOM.

## Conventions
- Hardware units are millimetres.
- Label unverified facts as such. Do not state remembered figures as sourced.
- Keep Arabic text with its diacritics: المَهَا.
