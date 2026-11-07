# Bill of materials (skeleton)

Replica parts list for al-maha. Hardware documentation, licensed CERN-OHL-S-2.0
(`LICENSE-HARDWARE.txt`). Source tags and statuses follow `original-dimensions.md`.

This is a skeleton. The original's parts are listed with what is known about them; the
"Replica" column is what the project builds or buys, and is mostly **not yet decided**. A
dash means no decision, not that the part is absent. Fill it in as sources and CAD arrive.
Masses are from `mass-budget.md`; blank means no source and no assumption.

Status: **stated** / **derived** / **(unverified)** / **ASSUMPTION** (modelling choice).

## Structure

| Item | Qty | Original | Status | Replica | Mass (kg) |
|---|---|---|---|---|---|
| Body wedge (side plates, floor) | 1 | Wedge, 10 degree sidewalls, side plates about 380 long, underside 124 and deck 348 above ground. Magnesium alloy, covered in ITO-coated MLI [S10]; CFRP, magnesium and aluminium per the manufacturer [S24] | stated / derived | - (CAD: `hardware/body/`) | structure total 2.0 (stated [S26]) |
| Top plate (deck) | 1 | 401 long, about 164 wide | stated [S11] / derived | - | in structure |
| Thermal blankets | - | ITO-coated MLI [S10] | stated | - | not known |
| Fasteners, harness | - | not found | (unverified) | - | not known |

## Power

| Item | Qty | Original | Status | Replica | Mass (kg) |
|---|---|---|---|---|---|
| Solar cells | 30 (15 per side, 5 x 3) | About 69 x 39 mm, 6.5 mm clipped bottom corners, pitch 71.6 x 41; the size matches a 26.5 cm2 half-wafer cell. Exact part not named | derived [3g]; part (unverified) | - | not known |
| Cover glass | 30 | 200 um cerium-doped borosilicate, Qioptiq [S10] | stated | - | not known |
| Panel substrate | 2 | not found | (unverified) | - | not known |
| Battery | 1 | "Small", capacity not found [S3]. Power model in [S27] gives no figures | (unverified) | - | not known |
| Power electronics | - | Peak generation 15 W [S3]; no board data | (unverified) | - | not known |

## Mobility

| Item | Qty | Original | Status | Replica | Mass (kg) |
|---|---|---|---|---|---|
| Wheel | 4 | 200 x 80 mm, 14 radial grousers of 15 mm, skeletonized, Mg alloy (`hardware/wheel/`, `wheel-spec.md`) | stated / derived | - | 0.398 each, ASSUMPTION (model volume at AZ91E density) |
| Drive motor | 4 | In-wheel electric motors [S3]; type, size and gearing not found | stated qty; spec (unverified) | Pololu 37D without encoder, candidate #4746 (131.25:1, spur/helical), open-loop speed and direction (decision 2026-11-07). See `drive-spec.md` | 0.195 each (vendor, upper bound) |
| Motor driver | 2 | not found | (unverified) | Dual-channel brushed DC drivers, four channels in total, so pairs can be commanded together or separately. Heading hold from an IMU later if the rover drifts | not known |
| Wheel bearings | 8 | Not found | (unverified) | 4 x 6807 (35 x 47 x 7) inboard, 4 x 6701 (12 x 18 x 4) outboard, see `drive-spec.md`. ISO sizes from memory, verify | not known |
| Differential | 1 | Passive differential gear, in place of a rocker; no springs or dampers [S25]. Layout not found | stated; layout (unverified) | - | not known |
| Steering | none | Skid steering [S25], [S20] | stated | - | - |

## Mast and cameras

| Item | Qty | Original | Status | Replica | Mass (kg) |
|---|---|---|---|---|---|
| Mast and gimbal | 1 | About 300 long, ULTEM 1010 with titanium and aluminium parts, fuse-wire hold-down, spring hinge rotating it 90 degrees. Pan 179 degrees either way, tilt 75 degrees either way [S19] | stated | - | 1.237 (EM, stated [S19]); under 1.4 flight |
| CAM-1 | 1 | 35 x 35 x 73 mm optical tube, on the gimbal [S12] | stated | - | 0.210 stated [S12] |
| CAM-2 | 1 | Fixed, rear, axis about 250 high [S12] | stated | - | 0.210 stated [S12] |
| CAM-M (microscope) | 1 | Front, aperture about 210 high [S13] | stated / derived | - | not known |
| CAM-T (thermal imager) | 1 | Rear [S2], [S12] | stated | - | not known |
| Langmuir probes | 4 | 4 identical, 80 long, mounted between about 150 and 650 high [S14], [S15] | stated | - | not known |

## Other

| Item | Original | Status |
|---|---|---|
| Passive Regolith Sampler | In the rover documentation [S8]; mounting and mass not recorded in this repo | (unverified) |
| Onboard computer, radio and antenna | Not found. A dipole antenna sits 290 from the mast [S11] | (unverified) |

## Totals

Stated design mass 10 kg [S1]. Accounted for by a source or assumption: 5.25 kg (structure 2.0,
mast and gimbal 1.237, wheels 1.592, cameras 0.42). Unaccounted: 4.75 kg. See `mass-budget.md`.

## Replica notes

The extrusion frame and other testbed hardware from the earlier sessions are ground-test
items only, not a flight design (see `CLAUDE.md`). If the replica is built from testbed parts,
record each substitution in the "Replica" column with the reason and the mass difference.
