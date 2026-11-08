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
| Body wedge (side plates, floor) | 1 | Wedge, 10 degree sidewalls, side plates about 380 long, underside 124 and deck 348 above ground. Magnesium alloy, covered in ITO-coated MLI [S10]; CFRP, magnesium and aluminium per the manufacturer [S24] | stated / derived | Aluminium sheet panels, 2 mm (floor, sides, ends), on a T-slot frame (`frame-spec.md`) | panels 2.41 (all, incl. deck), ASSUMPTION |
| Top plate (deck) | 1 | 401 long, about 164 wide | stated [S11] / derived | 3 mm aluminium sheet, 401 x 164 | in the panels above |
| T-slot frame, 20 x 20 mm (5 series, 6 mm slot) | 17 members, 3.71 m, all vertical or horizontal (stepped frame); the two bottom side rails are 20 x 40 (HFS5-2040, 0.88 kg/m) with a 16 mm hole drilled through each | Not in the original | n/a | Catalogue 20 x 20 profile, 0.50 kg/m, cut square to the list in `frame-spec.md` | 2.14 |
| Corner brackets, 20-series | 26 | Not found | (unverified) | Standard 20-series L brackets (`frame-spec.md`) | not known |
| T-nuts (M4) and M4 bolts | 102 each (52 for the brackets, 50 for the panels) | Not found | (unverified) | Standard 20-series slot hardware; lengths not chosen | not known |
| Side panel pivot standoffs | 8 | Side panels stand proud of the body on spacers ([S18] Fig. 1; gap about 10 mm by eye) | derived | 8 mm stud, about 12.5 mm long, with a rod end or ball joint and M4 bolt; parts not chosen | about 0.12, ASSUMPTION |
| Mast extrusion, 40 x 40 T-slot | 1 x 223 mm | About 58 mm square tube (ULTEM) [3j], [S19] | derived | Catalogue 40 x 40 profile, about 1.86 kg/m (catalogue entries differ), plus a 76 x 76 x 6 mm aluminium base plate | 0.24 + 0.09 (shorter: stands on the pan spindle) |
| Thermal blankets | - | ITO-coated MLI [S10] | stated | - | not known |
| Fasteners, harness | - | not found | (unverified) | - | not known |

## Power

| Item | Qty | Original | Status | Replica | Mass (kg) |
|---|---|---|---|---|---|
| Solar cell pieces | 60 (30 per side, two in each of 5 x 3 slots) | About 69 x 39 mm, 6.5 mm clipped bottom corners, pitch 71.6 x 41; the size matches a 26.5 cm2 half-wafer cell. Exact part not named | derived [3g]; part (unverified) | SunPower-type back-contact silicon pieces, 31 x 41.6 mm, cut from 125 x 41.6 mm third-cut strips (LinkSolar lots of 20 at US$16.96, or full cells at US$43.60 for 10); 15 strips needed, 30 bought; about 0.32 W, 0.625 V, 0.51 A each at one sun (retailer's figures scaled); 30 in series per side, 18.75 V; US$34 to 44 (decided 2026-11-07; `solar-spec.md`) | not known |
| Cover glass | 30 | 200 um cerium-doped borosilicate, Qioptiq [S10] | stated | - | not known |
| Panel substrate | 2 | not found | (unverified) | The 2 mm aluminium side panels, with an insulating film under real cells and 6 wire holes each | in the panels |
| Battery | 1 | "Small", capacity not found [S3]. Power model in [S27] gives no figures | (unverified) | 2S2P pack of four Samsung INR18650-30Q (3000 mAh nominal, 15 A, 48 g max each), about 43 Wh, with a 2S BMS (not chosen); see `electronics-spec.md` | 0.22, ASSUMPTION |
| Controller | 1 | Not found | (unverified) | Raspberry Pi Zero 2 W, 65 x 30 mm, CSI-2 camera port (`electronics-spec.md`), not bought | not found |
| 5 V converter | 1 | Not found | (unverified) | Pololu D24V22F5, 17.8 x 17.8 x 7.9 mm | 0.0023 (vendor) |
| Solar charge controller | 1 | Not found | (unverified) | A cheap buck 2S MPPT module, BQ24650 or CN3722 type (decided 2026-11-07; ended eBay BQ24650 listings US$11 to 17, LaskaKit CN3722 EUR 10.19), about 50 x 25 x 17 mm; verify output set to 8.4 V and the input set point near 17.5 V; `charger-board-spec.md` | 0.03, ASSUMPTION |
| Wire grommets, 5 mm | 12 | Not in the original | n/a | One per side-panel wire hole | not known |
| Power electronics | - | Peak generation 15 W [S3]; no board data | (unverified) | - | not known |

## Mobility

| Item | Qty | Original | Status | Replica | Mass (kg) |
|---|---|---|---|---|---|
| Wheel | 4 | 200 x 80 mm, 14 radial grousers of 15 mm, skeletonized, Mg alloy (`hardware/wheel/`, `wheel-spec.md`) | stated / derived | - | 0.398 each, ASSUMPTION (model volume at AZ91E density) |
| Drive motor | 4 | In-wheel electric motors [S3]; type, size and gearing not found | stated qty; spec (unverified) | Pololu 37D without encoder, candidate #4746 (131.25:1, spur/helical), open-loop speed and direction (decision 2026-11-07). See `drive-spec.md` | 0.195 each (vendor, upper bound) |
| Motor driver | 2 | not found | (unverified) | Pololu Dual MC33926 carrier (#1213), 2.5 A per channel, four channels in total; pairs can be commanded together or separately. Heading hold from an IMU later if the rover drifts | 0.007 each (vendor) |
| Battery management board | 1 | Not found | (unverified) | 2S, common port, balancing, 20 A class (listings: about 48 x 20 x 4 mm, 13 A continuous and 20 A peak on one); `power-spec.md` | 0.012, ASSUMPTION |
| Fuse block and fuses | 1 block, 5 fuses | Not found | (unverified) | 4-way blade block plus a 15 A main; `power-spec.md` | 0.04, ASSUMPTION |
| Power node (bus bar), master switch | 1 + 1 | Not found | (unverified) | bus bar about 40 x 20 x 15 mm; panel switch with a 15 A DC rating on the rear panel | 0.03 and 0.02, ASSUMPTION |
| Servo regulator | 1 | Not found | (unverified) | Pololu D24V22F6, 6 V, 2.5 A, 17.8 x 17.8 x 7.9 mm | 0.0023 (vendor) |
| Pivot bushings | 4 | Not found | (unverified) | igus GFM-1214-09 type flanged plain bushings (12 bore, 14 OD, 9 long), two per bottom side rail in a bonded 16 / 14 mm aluminium sleeve, plus one 12 bore x 14 OD x 12 long in each differential housing wall; replacing the 688 bearings; verify flange size, pressure rating and fit | 0.02 (rail ones), ASSUMPTION |
| Pivot shaft | 2 | Not found | (unverified) | 12 x 2 mm 4130 chromoly seamless tube, normalized (fallback E355 precision tube), about 135 mm each, with a bonded 8 / 5 mm stub tube; ground or hard-chromed | in the suspension mass |
| Retaining compound | - | Not found | (unverified) | for the shaft in the link plate boss (20 mm), the stub in the tube (15 mm) and the sleeve in the rail hole; grade not chosen | not known |
| Differential gears | 4 | A passive differential gear [S25] | stated; layout (unverified) | steel mitre gears, module 1.5, 16 teeth, 8 mm bore, 8 mm face: two side gears and two spiders, plus a 6 mm cross pin (`differential-spec.md`); RS PRO lists a hardened 8 mm-bore one | about 0.1 kg of steel with the pin |
| Wheel bearings | 8 | Not found | (unverified) | 4 x 6807 (35 x 47 x 7) inboard, 4 x 6701 (12 x 18 x 4) outboard, see `drive-spec.md`. ISO sizes from memory, verify | not known |
| Differential | 1 | Passive differential gear, in place of a rocker; no springs or dampers [S25]. Layout not found | stated; layout (unverified) | Bevel differential on the centreline inside the body at pivot height 146, body as carrier, joined to two side plates (`suspension-spec.md`); a bar linkage is the alternative | not known |
| Side link plates | 2 | One plate per side joining the front and rear hubs, with a boss at the wheelbase midpoint about 147 above the ground line (3i, figures only) | derived; shape (unverified) | 8 mm plate with a sleeve to each motor's clamp ring, from `suspension-spec.md` | not known |
| Steering | none | Skid steering [S25], [S20] | stated | - | - |

## Mast and cameras

| Item | Qty | Original | Status | Replica | Mass (kg) |
|---|---|---|---|---|---|
| Mast and gimbal | 1 | About 300 long, ULTEM 1010 with titanium and aluminium parts, fuse-wire hold-down, spring hinge rotating it 90 degrees. Pan 179 degrees either way, tilt 75 degrees either way [S19] | stated | 40 x 40 T-slot extrusion on a base plate, fixed upright (stowing deferred), with a 2 mm aluminium sheet bracket (bent, laser cut) holding the tilt servo, a printed disk, cube enclosure, lens assembly and hat, and a pan servo in the base (Feetech STS3215 C001, 55 g each) (`mast-spec.md`, `electronics-spec.md`); tilts 90 degrees either way as modelled (original 75) | 1.237 (EM, stated [S19]); under 1.4 flight. Replica 1.05 (with the pan base, bracket and lens stack) from the CAD and catalogue figures, shells ASSUMPTION |
| CAM-1 | 1 | 35 x 35 x 73 mm optical tube, on the gimbal [S12] | stated | Raspberry Pi Camera Module 3, standard lens (25 x 23.862 x 11.3 mm per the brief's drawing) in a printed 35 x 35 x 73 mm tube, 2 mm walls | 0.210 stated [S12] (replica not weighed) |
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
