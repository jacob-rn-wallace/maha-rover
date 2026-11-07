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
- **Mounting:** the housing hangs from the two cross rails on printed cradles (not modelled); the bus bar moved to x -52 to keep 6 mm clear of it.

## Shafts and bearings (changed from the first design)

- **Shaft:** an **8 mm tube with a 5 mm bore** (was 10/6), to suit the 8 mm gear bore; the motor wires still run through it (four 22 AWG are about 3.4 mm across in a 2 x 2
  bundle), through 3 mm radial holes inside the body (60 mm out) and in the gap outside the wall (125 mm out).
- **Bearings:** **flanged plain bushings, 8 ID x 12 OD x 8 long (ASSUMPTION)**, one at each end of a 12 mm hole drilled through each bottom side rail (`frame-spec.md`); the shaft runs through the rail, so the earlier 688 bearing in a wall plate is gone. Check the bushing material and the strength of the drilled rail.
- **Shear:** at the firmware cap the tube sees 52 MPa, and 157 MPa at the cross holes with a stress-concentration factor of 3; at the gearbox limit 84 and 251 MPa.
  That is too high for plain steel at the holes, which is another reason for the cap. A heat-treated or stainless tube, or a thicker wall, would help. No material is chosen.

## Open

- **Backlash and fit:** a mitre gear set carries backlash, so the body can rock slightly; there are no springs to damp it. Tolerances were not specified.
- **Fixing the gears to the tube:** a set screw would crush a thin tube; a roll pin, a clamp hub or a D-flat is needed. The same for the **link plate to the shaft**, which
  must transmit the full torque (4.5 N.m at the cap): not designed.
- **Lubrication, bushings or bearings for the spider gears and the cross pin, and the housing's two halves and fasteners:** not designed.
- **Gears:** stock availability and drawings; allowable stress and hardness; whether the 24 mm gears mesh cleanly on a 1:1 mitre mounting distance.
- **Current cap:** firmware to read the driver's current sense is not written; the sense output's accuracy is a datasheet figure (0.525 V/A, unreliable below 0.5 A).
- The mesh in the CAD overlaps by design; an involute tooth model and an interference check were not done.
