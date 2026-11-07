# Drive specification (replica)

Replica drive: four brushed DC gearmotors in the wheel hubs, no encoders, open-loop speed and
direction, skid steering. Decided 2026-11-07. This is the replica's own design, not the
original's: the original's motor type is unsourced (`original-dimensions.md` section 5).
CAD check: `hardware/drive/motor.py`.

## Candidate motor: Pololu 37D, no encoder

Vendor figures from the 37D datasheet rev 1.2 (Jan 2020) and the 37D dimension drawing
(10 Jan 2020), read 2026-11-07. These are the vendor's own figures, not independently checked.
The gearbox is **mostly spur gears with a helical first stage, not planetary**. (An earlier
note in this repo called it planetary; that was wrong.)

| Item | Gear ratio | No-load speed at 12 V | Body length | Notes |
|---|---|---|---|---|
| #4746 (recommended) | 131.25:1 | 76 rpm, 0.2 A | 57 mm | 60 kg·mm at max efficiency, 0.74 A |
| #4745 | 102.08:1 | 100 rpm | 57 mm | 42 kg·mm at max efficiency |
| #4744 | 70:1 | 150 rpm | 54 mm | 32 kg·mm at max efficiency; too fast for this rover |
| #2829 | 150:1 | 67 rpm | 57 mm | 65 kg·mm at max efficiency |

Common to all of them: 37 mm gearbox (36.8), 34.8 mm motor can, 12 mm boss on the gearbox face,
6 mm D-shaft 16 mm long, 6 x M3 on a 31 mm circle (3 mm thread depth), weight 175 to 195 g, 5.5 A
extrapolated stall at 12 V. Recommended limits: 100 kg·mm (0.98 N·m) continuous, 250 kg·mm
(2.45 N·m) instantaneous. Prices seen for #4746 and #4744: US$38.95 each, less in quantity
(price for the others not checked). The datasheet gives **no bearing or radial-load rating** for the output
shaft, so the shaft should not carry the wheel (hence the support design below).
Other vendors (for example Cytron's 37D x 59L, shaft 15.5 mm) appeared in search results but their
datasheets were not read.

## Sizing against the replica's targets

Sized for the **10 kg design mass** (the original's mass [S1]; decision 2026-11-07: the first pass is not
optimised for mass, then a second pass brings the build down to 10 kg if it comes out over).

| Quantity | Value | Basis |
|---|---|---|
| Torque per wheel on a 20 degree slope | about 0.84 N.m (86 kg.mm) | 10 kg x 9.81 x sin 20 / 4 x 0.1 m, no losses |
| #4746 continuous limit | 0.98 N.m (100 kg.mm) | datasheet |
| #4746 instantaneous limit | 2.45 N.m (250 kg.mm) | datasheet; 2.9 times the slope torque |
| #4746 best-efficiency torque | 0.59 N.m (60 kg.mm), 0.74 A | datasheet |
| Motor current at the slope torque | about 1.0 A | linear in torque between the datasheet's 0.2 A no-load and 0.74 A at 60 kg.mm; the stall line gives 1.2 A |
| Wheel speed, no load, 12 V | 76 rpm = 0.80 m/s | wheel circumference 0.628 m |
| Wheel speed, no load, 7.4 V (2S pack) | about 47 rpm = 0.49 m/s | no-load speed scales with voltage; derived |
| Original's speed | 0.1 m/s = 9.5 rpm | [S1] |

At 10 kg the slope torque is inside the continuous limit but above the best-efficiency point, so the motors
run warm on a long climb; there is about 15 percent of continuous margin. The torque for the original's
100 mm obstacle depends on traction and the grousers and has not been estimated; the instantaneous limit is
the ceiling. If tests show the motors short of torque, the next ratio steps are the 150:1 (#2829, 65 kg.mm
best-efficiency) or a 24 V pack.

The highest ratio is still fast. Running the 12 V motors from a 2S pack roughly halves the speed,
and PWM brings it down further. Speed under load will be lower than these no-load numbers.
Low-duty PWM on a brushed motor with no encoder can stall under load, so test low speeds on the
real rover.

## Wheel support concept (option 1)

The motor shaft carries torque only. Two bearings sit on the motor's own housing and carry the wheel:

| Bearing | Size (ISO, from memory) | Sits on | Outer race in |
|---|---|---|---|
| Inboard | 6807, 35 x 47 x 7 | the 34.8 mm motor can | a tube extension of the hub, 53 mm outside diameter |
| Outboard | 6701, 12 x 18 x 4 | the 12 mm boss on the gearbox face | a drive flange bonded to the hub tube end |

The flange also drives the shaft through a D-bore collar. A clamp ring on the can, behind the
inboard bearing, holds the motor to the suspension arm. The hub's 44 mm bore is too narrow to hold
a bearing around the motor, which is why the inboard bearing sits beyond the end of the hub tube
and the extension carries its outer race.

CAD result (`hardware/drive/motor.py`, placeholder geometry for the support parts): no
interference between the motor, bearings, clamp and the wheel, and none between the fixed and the
rotating parts.
- The can ends 2.2 mm past the wheel's inner face, and the terminals 7.2 mm past it.
- The clamp ring and the arm reach the motor from the inboard side through the open space
  between the ribs and the inner face.

Things this does not settle:
- **Bearing loads are not checked.** The 6701 is tiny; check its rating against side loads (the
  wheel is 25 N static on Earth, but grouser impacts are larger).
- **Concentricity.** Both bearings sit on different parts of the motor (can and gearbox). If their
  axes differ, the wheel binds. The D-collar should therefore float on the shaft.
- **Clamping the can.** The vendor sells face-plate brackets, but the face plate is at the
  outboard end here, so the can has to be clamped. Check the can will take the clamp.
- Machining of the extension, flange and collar, and the material for them.
- Wiring: the terminals sit inboard, 7 mm past the wheel face.
