# Power system (replica)

How the 2S pack, its protection, the solar charger and every load connect. Designed 2026-11-07; candidates only, nothing bought (purchases are
deferred). CAD fit: `hardware/body/interior.py` (placeholders for each part), `hardware/suspension/arms.py` (the hollow pivot shaft),
`hardware/chassis/frame.py`. Figures from vendor pages are marked; derived numbers are my arithmetic; wire resistances are standard table
values for copper (16 AWG 13.2, 18 AWG 21.0, 22 AWG 53.0, 24 AWG 84.2 milliohm per metre) and are from memory.

## Architecture

```
solar side L ---|>|--+                                    +--> motor drivers A and B (2 x dual MC33926) --> 4 motors
solar side R ---|>|--+--> buck 2S MPPT module              |      (fuse 7.5 A each)
                                |  (8.4 V out)             +--> 5 V converter --> Pi Zero 2 W + camera      (fuse 3 A)
                                |                          +--> 6 V servo regulator --> pan and tilt servos (fuse 3 A)
                    [fuse 3 A]  |                                      ^
                                v                                      |
pack 2S2P (4 x 18650) --- BMS (2S, common port) --- P+ ---- NODE (bus bar) --- main fuse 15 A --- master switch --- fuse block
                                                     |
                                                  P- ---- common ground
```

- **The charger joins at the node, ahead of the main switch**, so the panels charge the pack with the rover switched off.
- **The BMS stands between the cells and everything else.** The pack, charger and all loads meet at its common port (P+ and P-).
  It is the only guard against over-charge, over-discharge, over-current and short circuit, and it balances the two series groups.
- The two solar sides each go through a Schottky blocking diode into the charger's input (`solar-spec.md`).

## Parts (candidates)

| Part | Candidate | Size (mm) | Mass | Source and caveats |
|---|---|---|---|---|
| Pack | 4 x Samsung INR18650-30Q, 2S2P (cells lying along x) | 68 x 38 x 38 | 0.22 kg | 3000 mAh, standard charge 1.5 A (0.5 C) at 4.2 V with a 150 mA cut-off, rapid 4 A, discharge cut-off 2.5 V; continuous discharge 15 A (retailers; one summary says 10 A) |
| BMS | 2S 20 A, balanced, common port | about 48 x 20 x 4 | 12 g (assumed) | listings: 45 to 48 mm long, 15 to 20 mm wide; one lists 13 A continuous with 20 A peak, passive balance about 100 mA; check continuous against peak |
| Main fuse and branch fuses | blade (ATO) 15 A main; mini or standard 4-way block for the branches | block about 60 x 36 x 20 (assumed) | 0.04 kg | blocks found: standard ATO 4-way 47 x 86 x 36, Blue Sea compact 94 x 44 x 33 (30 A per circuit, 32 V); mini ATM 4-way blocks are limited to 15 A per circuit and 12 V |
| Power node | bus bar or terminal block | about 40 x 20 x 15 | 0.03 kg | assumed |
| Master switch | panel-mount, rated for 15 A or more **DC** | body about 20 x 14 x 28 behind the rear panel | 0.02 kg | many rockers list an AC rating only: check the DC rating |
| Servo regulator | Pololu D24V22F6 (6 V, 2.5 A) | 17.8 x 17.8 x 7.9 | 2.3 g | vendor: 5 V, 2.5 A version read earlier; F6 is the 6 V part; its minimum input was not read |
| Connectors | XT60 class for the pack, XT30 class for branches, JST-XH for the balance leads | | | hobby-standard, from memory; not chosen |

**Why a servo regulator.** The STS3215 servos are rated 6 to 7.4 V in the listings (one manual says 4 to 8 V), and a full 2S pack is
8.4 V: a servo on the raw pack would be over its rating most of the time. A 6 V rail is inside every listing and is the rated point for
the 19.5 kg.cm figure. The cost is that near-empty packs (below about 6.5 V; not checked against the regulator's dropout) cannot hold 6 V.

## Current budget (pack at 7.4 V nominal)

| Branch | Continuous, driving up a 20 degree slope | Worst peak |
|---|---|---|
| Four drive motors | 4.0 A (1.0 A each, `drive-spec.md`) | 9.8 A (the gearbox's instantaneous limit, 2.45 A each) |
| Pi, camera and 5 V converter | 0.8 A (5 W at 5 V, 88 percent converter, both assumed) | 0.8 A |
| Pan and tilt servos through the 6 V regulator | 0.3 A | 2.3 A (one servo stalled at about 2.5 A at 6 V; the servos have a programmable overcurrent limit) |
| **Total from the pack** | **about 5.1 A, 38 W** | **about 13.2 A** |

- Runtime on 43 Wh at the slope load: about 1.1 h. Flat driving takes far less; the Pi alone is about 5 W.
- Cell stress: 13 A over two parallel cells is about 6.6 A each (0.5 C of the 3000 mAh), inside the retailers' 15 A rating.
- The solar module delivers at most 9.6 W at 8.4 V, about 1.1 A, well under the 1.5 A per cell standard charge rate.

## Protection

| Where | Rating | Why |
|---|---|---|
| Main fuse, after the node, before the switch | 15 A blade | covers 13.2 A peaks and protects 18 AWG wire; below the BMS's 20 A peak |
| Motor driver A and B | 7.5 A each | each board's two motors peak at 4.9 A, and a driver channel is rated 2.5 A (5 A for a few seconds) |
| 5 V converter | 3 A | the Pi branch is under 1 A |
| Servo regulator | 3 A | one stalled servo is 2.3 A |
| Charger output into the node | 3 A | the module's limit is higher; the panel gives 1.1 A |
| BMS | over-charge, over-discharge, over-current, short circuit | typical thresholds were not read for a specific board |
| Reverse polarity | none designed | the connectors are keyed (XT60 class) |

## Wire sizes and drops (arithmetic)

| Run | Length (from the CAD positions, with slack) | Current | Wire | Drop |
|---|---|---|---|---|
| BMS to node, node to main fuse | about 0.3 m | 13 A peak | 16 AWG | 0.1 V |
| Fuse block to a motor driver | about 0.3 m | 4.9 A peak | 18 AWG | 0.06 V |
| Driver to a motor, through the pivot shaft | about 0.5 m each way | 2.45 A peak | 22 AWG | 0.13 V |
| Node to the 5 V converter, servo regulator | about 0.3 m | 0.8 A, 2.3 A | 22 AWG | under 0.1 V |

Typical chassis ampacities are 16 AWG about 22 A, 18 AWG about 16 A, 22 AWG about 7 A (from memory, not checked).

## How the motors' wires cross the pivots

The four motors sit on the moving link plates, and their wires must cross from the body to the plates. They run **through the pivot shafts**,
which are now tubes: 8 mm outside, 5 mm inside, with a 3 mm radial hole inside the body (60 mm from the centreline) and another in the 16 mm gap
outside the wall (125 mm out). Four 22 AWG wires (two motors a side) enter the shaft inside the body, run along its axis, leave in the gap, then follow
the inner face of the link plate to each motor's sleeve, which already covers the terminals. The shaft only turns about plus or minus 11 degrees,
so the wires twist, not flex. In the CAD the hollow shaft clears the bearings, plates and frame; the differential's gears are not involved because the
wires leave the shaft well before the housing. Not designed: the clips along the plate, the strain relief, the entry from the sleeves.

## Where the parts sit (all checked for fit and clashes in `interior.py` and `frame.py`)

- Pack at the rear floor (x -110); BMS beside it (x -65, y +45); fuse block (x -65, y -45); power node (x -45, y 0), all on the floor, clear of
  the differential housing (x within 18) and the cross rails.
- Servo regulator next to the fuse block (x -20, y -75); charger and drivers in the front compartment as before.
- The master switch is on the rear end panel (x -178, y +45, z 165), 20 mm deep, clear of the bottom end rail (z up to 146).

## Open

- The BMS: a real 2S board with at least 15 A continuous and a known over-current trip; the 13 A continuous in one listing is thin.
- Switch and fuses: DC ratings, sizes, the connectors.
- Pack construction: a holder or spot-welded strips (none designed), a wrap, mounting, and a way to remove the pack.
- Monitoring: a voltage and current sensor on I2C (an INA226-type part with an external shunt) for state of charge and low-voltage shutdown was not chosen.
- A low-voltage plan: the BMS cuts at about 2.5 V a cell, but the Pi and servos fail earlier.
- The charger module's output (8.4 V) and the servo regulator's dropout at low pack voltage were not measured.
- Motor noise on the supply (capacitors across the motors, ferrites) is not designed.
