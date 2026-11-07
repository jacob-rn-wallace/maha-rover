# Suspension specification (replica)

Replica suspension: a passive differential joining two rigid side arms. Decided 2026-11-07.
**This is an interpretation, not the original's layout.** [S25] (MBRSC) states only that Rashid
is four-wheeled with skid steering and uses "a passive differential gear rather than a
rocker-type suspension system", with no springs or dampers. How the differential is arranged is
not published. Everything below is ASSUMPTION. CAD and checks: `hardware/suspension/arms.py`.

## Concept

- One rigid arm per side carries the front and rear wheel (a walking beam).
- Both arms pivot on one common axis along Y at x = 0, below the belly, and each is joined by a
  shaft to a side gear of a bevel differential on the centreline.
- The differential housing (the carrier) is fixed to the body, so the **body pitches by the
  average of the two arm angles**. Body roll is taken by the rigid body, as in a rocker-bogie.
- Each arm is a low beam inboard of the wheels. A strap joins it to each motor's clamp ring,
  passing under the motor terminals (`drive-spec.md`).
- No springs or dampers, as in [S25].

## Numbers

| Item | Value | Status |
|---|---|---|
| Pivot axis height | 76 mm (belly at 124) | ASSUMPTION |
| Beam | y 150 to 158 from the centreline, 10 mm tall, full wheelbase (273) | ASSUMPTION |
| Differential housing | 40 mm diameter, 44 mm long, top at 96 and bottom at 56 | ASSUMPTION |
| Arm angle for a 100 mm step under one front wheel | arm 21.5 degrees from level; body pitch 10.7; **10.7 degrees in the body frame**, front hub moves 25 mm | derived (wheelbase 273) |

The 100 mm figure is the original's obstacle limit [S1].

## CAD checks

- The arms, straps, shafts and differential housing do not touch the wheels, motors or body.
- Sweeping the arms from -15 to +15 degrees in the body frame, with the left arm at +phi and the
  right at -phi, shows no contact with the body, cells or the other side.
- That sweep is weak evidence. It is clear mainly because the arms sit outboard of the body, 29 mm
  from it at the belly. It does not test the ground or the differential's strength.

## Problems this design has

- **Obstacles under the belly.** The belly is 124 mm above the ground line but the differential
  hangs to 56 mm and the shafts to 72 mm. A 100 mm rock passing between the wheels would hit them,
  although the original's body would clear it. Possible fixes: raise the pivot axis towards 100
  (the straps then need risers to pass the motor terminals) and shrink the differential.
- **Shafts and differential strength.** Sizes are placeholders; no loads checked.
- **Backlash.** A bevel differential's backlash lets the body rock a little, which a spring-free
  suspension has no way to damp. A simpler alternative with the same kinematics is a pivoted bar
  linkage (a central rocker with two links to the arms); worth considering for a first prototype.
- **Gear choice.** Hobby bevel gears of this size are plastic or small metal; none chosen.
- **Fidelity.** How closely the real differential matches this is unknown. The external look is
  unaffected: all of it sits under the belly and inboard of the wheels.
