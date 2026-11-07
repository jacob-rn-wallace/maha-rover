# Differential: bevel gear train (replica)

Decided 2026-11-07: a **bevel gear differential**, as [S25] says the original has ("a passive differential gear"), in preference to a bar linkage. The
body is the carrier. The linkage would carry about a third of the force and cost less, but it is a different mechanism from the original's. CAD and
numbers: `hardware/suspension/differential.py`; the housing and shafts are in `hardware/suspension/arms.py`. Everything is the replica's own design and
ASSUMPTION unless tagged; the original's gearing is not published. Nothing is bought.

## Loads (arithmetic)

The wheels' ground thrust acts at the ground line, 145.7 mm below the pivot axis. Each newton of thrust therefore puts 0.1457 N.m of pitching moment
into the arms, and the differential carries it into the body. A differential splits torque equally, so each side gear carries the same torque T and the
carrier takes 2 T.

| Case | Torque at each wheel | Torque in each side gear |
|---|---|---|
| Climbing a 20 degree slope at 9.24 kg | 0.78 N.m | 2.3 N.m |
| **Firmware cap, 1.6 A a motor (about 1.5 N.m)** | 1.5 N.m | **4.5 N.m** |
| Gearbox instantaneous limit (2.45 N.m) | 2.45 N.m | 7.1 N.m |

The wheel torque from current uses the gearmotor datasheet's 0.2 A no-load and 0.74 A at 60 kg.mm, assumed linear. The MC33926 driver has no programmable
current limit, so the cap is a **design requirement**: the controller must read the driver's current-sense output and hold each motor to 1.6 A. It still leaves
1.5 N.m a wheel against 0.78 N.m for the slope. The reaction through the differential is large because the pivot is high: 7.1 N.m at the gearbox limit.

## Gears

Four steel mitre gears (1:1, 45 degree cones): two side gears on the pivot shafts and two spider gears on a cross pin, each side gear meshing with both spiders.
Bending stress by the Lewis form, tooth load shared between the two spiders, at the mean pitch radius; the allowable of 200 MPa is an assumption for hardened steel:

| Module | Teeth | Face (mm) | Pitch dia (mm) | Slope | Firmware cap | Gearbox limit |
|---|---|---|---|---|---|---|
| 1.0 | 20 | 7 | 20 | 56 MPa | 110 MPa | 177 MPa |
| 1.25 | 16 | 8 | 20 | 44 MPa | 87 MPa | 139 MPa |
| **1.5** | **16** | **8** | **24** | **29 MPa** | **57 MPa** | **91 MPa** |
| 1.5 | 18 | 9 | 27 | 22 MPa | 43 MPa | 69 MPa |
| 2.0 | 16 | 10 | 32 | 13 MPa | 25 MPa | 40 MPa |

**Chosen: module 1.5, 16 teeth, 8 mm face, 24 mm pitch diameter.** It is the smallest that keeps the stress at a third of the allowable at the cap and under half at the
gearbox limit. **Stock availability:** a hardened steel mitre gear of module 1.5 with 16 teeth and an 8 mm bore was found as an RS PRO listing (face width not seen);
other 16-tooth listings are module 2 with a 10 mm bore (RS PRO; KHK SM2-16, which is unhardened) and QTC Gears' induction-hardened KSMS line (50 to 60 HRC,
modules 1 to 8, a KSM1.5-20 with an 8 mm bore). The 8 mm bore sets the shaft size below. None was bought or checked against a drawing.

## Housing (`arms.py`, `differential.py`)

- **Layout:** the side gears on the pivot axis (along Y), the spider gears on a horizontal cross pin (along X), so the housing is wide, not tall.
- **Size:** a box 48 (x) x 50 (y) x 36 (z) mm with 3 mm walls, centred on the pivot axis at z 145.7: z 127.7 to 163.7, between the floor panel's top (126) and the
  cross rails' underside (165), and x within 24 mm. The simplified gears (tooth-tip cones and hubs) fit inside with 2 mm to spare in height; the cross pin ends reach the walls.
- **Mass:** about 0.09 kg of steel and 0.08 kg of aluminium (0.17 kg), with bushings, the pin and hardware taken as 0.30 kg in the mass estimate.
- **Mounting:** the housing hangs from the two cross rails by four integral aluminium lugs, M4 into T-nuts (`frame-spec.md`); the bus bar moved to x -52 to keep 6 mm clear of it.

## Shafts and bearings (changed from the first design)

- **Shaft (changed 2026-11-07):** a **12 mm OD, 8 mm ID** steel tube from the link plate to the housing wall, plus a **separate 8 mm OD, 5 mm ID stub tube** bonded 15 mm into its
  end, which carries the side gear (an 8 mm bore cannot be turned down to an 8 mm OD, so the stub is not one piece with the tube). The earlier 8 / 5 tube was too thin for the
  bending of the wheel loads (`hardware/chassis/rail_check.py`: 702 MPa at 3x, 249 MPa static); the 12 / 8 tube sees 220 MPa at 3x. **Material: 4130 chromoly tube, normalized
  (factor 2.0 at 3x; size 12 x 2 unverified), fallback E355 precision tube (factor 1.6); 304 stainless is not enough (1.0).** The motor wires (four 22 AWG, about 3.4 mm across in a
  2 x 2 bundle) run through the bore, leave axially at the link plate end, and enter through one 3 mm radial hole at y = 20 in the stub, inside the housing between the gear hub and the wall.
- **Supports:** two igus GFM-1214-09 type flanged plain bushings (12 bore, 14 OD, 9 long) in a bonded 16 / 14 mm aluminium sleeve in a 16 mm hole through the bottom side rail
  (`frame-spec.md`), and **a third bushing in the housing wall** (12 bore, 14 OD, 12 long, in a 14 mm H7 bore through the 3 mm wall and a 22 mm boss, 63 mm inboard of the rail). The
  shoulder at the end of the 12 mm tube bears on the wall's inner face. At 3x the housing bushing carries 467 N (156 N static, 3.2 MPa); the housing hangs from the differential cross
  rails by four integral lugs, M4 into T-nuts (about 360 N on the worst bolt at 3x with the torque at the gearbox limit).
- **Shear:** the 8 / 5 stub in torsion alone sees 53 MPa at the firmware cap, and 158 MPa at the cross hole with a stress-concentration factor of 3; at the gearbox limit 83 and 250 MPa.
  That is too high for plain steel at the hole, which is another reason for the cap. The hole is where the bending moment is nearly zero. The stub may be a stronger steel than the tube
  (4140 Q&T would do); not chosen.

## Open

- **Backlash and fit:** a mitre gear set carries backlash, so the body can rock slightly; there are no springs to damp it. Tolerances were not specified.
- **Fixing the gears to the tube:** a set screw would crush a thin tube; a roll pin, a clamp hub or a D-flat is needed. The same for the **link plate to the shaft**, which
  must transmit the full torque (4.5 N.m at the cap): not designed.
- **Lubrication, bushings or bearings for the spider gears and the cross pin, and the housing's two halves and fasteners:** not designed.
- **Gears:** stock availability and drawings; allowable stress and hardness; whether the 24 mm gears mesh cleanly on a 1:1 mitre mounting distance.
- **Current cap:** firmware to read the driver's current sense is not written; the sense output's accuracy is a datasheet figure (0.525 V/A, unreliable below 0.5 A).
- The mesh in the CAD overlaps by design; an involute tooth model and an interference check were not done.
