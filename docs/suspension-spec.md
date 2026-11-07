# Suspension specification (replica)

Replica suspension: a passive differential joining two rigid side link plates. Decided
2026-11-07, revised the same day after reading the CAD figures (`original-dimensions.md`
section 3i). **The layout is partly an interpretation.** [S25] (MBRSC) states only that Rashid is
four-wheeled with skid steering and uses "a passive differential gear rather than a rocker-type
suspension system", with no springs or dampers. The CAD figures add what is *seen*: one plate per
side joining the front and rear hubs, a boss at the wheelbase midpoint about 147 mm above the
ground line, and a short stub into the body there. What is inside the body, and whether the boss
rotates, is not shown. CAD and checks: `hardware/suspension/arms.py`.

## Concept

- One rigid plate per side carries the front and rear wheel (a walking beam). [3i]
- The plates pivot on a common axis along Y at x = 0, z = 145.7 (hub height + 45.7). [3i]
- Each plate is joined by a shaft through the body wall to a side gear of a **bevel differential
  inside the body**. (Inside the body is an interpretation of the stub seen in [S18].)
- The housing (the carrier) is fixed to the body, so the **body pitches by the average of the two
  plate angles**. Body roll is taken by the rigid body, as in a rocker-bogie.
- Each motor hangs on its plate through a sleeve joining the plate to the motor's clamp ring; the
  sleeve covers the motor terminals (`drive-spec.md`).
- No springs or dampers, as in [S25].

## Numbers

| Item | Value | Status |
|---|---|---|
| Pivot axis height | 145.7 mm above the ground line (hub 100); belly at 124, cell field from about 172 | derived [3i] |
| Plate inner face from the centreline | 133 mm (body wall 116.8 at the pivot, so 16 mm gap; wheel inner face 167.7) | ASSUMPTION, from the front view [3i] |
| Plate | 8 mm thick, lower edge 105 mm, rising to 178 mm at the middle, ends 22 mm past the hubs, a tab down to 78 behind each sleeve | lower edge derived [3i]; the rest ASSUMPTION |
| Pivot boss | 48 mm diameter, 6 mm proud of the plate | derived by eye [3i] |
| Differential housing | 36 mm diameter, 44 mm long, z 128 to 164, inside the body (a 40 mm one would cut the 3 mm floor) | ASSUMPTION |
| Plate angle for a 100 mm step under one front wheel | plate 21.5 degrees from level; body pitch 10.7; **10.7 degrees in the body frame**, front hub moves 25 mm | derived (wheelbase 273) |

The 100 mm figure is the original's obstacle limit [S1].

## CAD checks

- The plates, boss, sleeves and differential housing do not touch the wheels, the motors (except
  the bonded sleeve-to-clamp joints) or the body. The shaft passes through the body wall by design;
  the body model is a solid envelope, so it shows as an overlap.
- The housing lies entirely inside the body envelope.
- Sweeping the plates from -15 to +15 degrees in the body frame (left at +phi, right at -phi), the
  plate parts, wheels and motors never touch the body or cells or each other. The closest approach
  between plate and body is 12.4 mm, at the belly edge.
- That sweep does not test the ground, the strength of any part, or the gear train.

## What changed from the first version

The first version put the pivot at 76 mm under the belly with the differential hanging below it.
That would have snagged a 100 mm rock, which the original's body clears. With the pivot at about
146 mm, inside the body wall, the differential is inside the body and the belly (124 mm) is the
lowest central part again. The plate hangs outside the wall, as the CAD shows.

## Problems this design still has

- **Inside the body.** The mounts and bearings are laid out in `interior-spec.md`; the gear train
  inside the housing is not designed. The wall at pivot height must stay clear of the cell field
  (it starts at about 172 mm; the bearing boss tops out at 158.7).
- **Shaft and differential strength.** Sizes are placeholders; no loads checked.
- **Backlash.** A bevel differential's backlash lets the body rock a little, which a spring-free
  suspension has no way to damp. A pivoted bar linkage gives the same kinematics without gears and
  may be simpler for a first prototype.
- **Gear choice.** Hobby bevel gears of this size are plastic or small metal; none chosen.
- **Plate shape.** Only the lower edge and pivot are measured; the rest is guessed from a side view
  where the plate merges with the body's lower edge.
