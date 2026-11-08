# Electronics and actuators: parts shortlist (replica)

Candidate parts for the replica, read 2026-11-07. **Nothing is bought or final.** Figures are from
vendor pages and datasheets unless marked; where a source disagreed or a value was not found, that
is said. Sizes feed the interior layout (`interior-spec.md`) and the mast (`mast-spec.md`).

## Summary

| Role | Candidate | Qty | Size (mm) | Mass |
|---|---|---|---|---|
| Controller | Raspberry Pi Zero 2 W | 1 | 65 x 30 | not found |
| Camera | Raspberry Pi High Quality Camera (CS mount, IMX477) with a 4 mm CS lens (changed 2026-11-08 from Camera Module 3: it takes interchangeable lenses; `mast-spec.md`) | 1 | 38 x 38 board, 18.6 deep with the mount; lens 30 x 42, 49 g | not found |
| Drive motor | Pololu 37D, #4746 (see `drive-spec.md`) | 4 | 37 dia x 57 | 175 to 195 g |
| Motor driver | Pololu Dual MC33926 carrier, #1213 | 2 | 28 x 46 (1.10 x 1.8 in), height not found | 7 g (0.25 oz) |
| Pan, tilt servo | Feetech STS3215 C001 (7.4 V) | 2 | 45.2 x 24.7 x 35 | 55 g |
| 5 V supply | Pololu D24V22F5 | 1 | 17.8 x 17.8 x 7.9 | 2.3 g |
| Cells | Samsung INR18650-30Q | 4 | 18.4 dia x 65.0 max | 48 g max each |
| Battery management | generic 2S BMS with balancing | 1 | not chosen | not found |

## Controller and camera

- **Raspberry Pi Zero 2 W** (product brief, Apr 2024): 65 x 30 mm, quad-core Cortex-A53 at 1 GHz, 512 MB,
  2.4 GHz wireless LAN and Bluetooth 4.2, a CSI-2 camera connector, a 40-pin footprint (unpopulated),
  H.264 encode to 1080p30, 5 V DC at 2.5 A input (the brief's supply rating, not a measured draw).
  Mass and board height were not found.
- **Raspberry Pi High Quality Camera** (product brief, Jan 2023): Sony IMX477, 12.3 MP, 7.9 mm diagonal sensor, 1.55 um pixels, back focus 12.5 to 22.4 mm (CS variant), integrated IR cut filter, 200 mm cable, board 38 x 38 mm with four Ø2.5 holes; early Zero models lack the connector and later ones need an adapter cable. With the 4 mm CS lens (retailer: 80 degrees horizontal, f/1.2, 30 x 42 mm, 49 g) about 76 degrees horizontal on this sensor (arithmetic). Replaced the Camera Module 3 below as the replica's camera (2026-11-08).
- **Camera Module 3** (raspberrypi.com), the earlier choice: 12 MP Sony IMX708, autofocus, 75 or 120 degree diagonal field
  of view (the wide one is 12.4 mm tall), 25 x 24 x 11.5 mm, 15 x 1 mm FPC with a 200 mm cable; a Zero needs
  a separate Zero camera cable. 1080p50, 720p120. From US$25.
- **Camera Module 3 mechanical drawing** (brief p. 4, standard lens): PCB 25 x 23.862 x 1.12 mm, four 2.2 mm holes at 2.0 mm from the edges (21 mm apart across, 14.5 mm apart along), lens block 10.8 mm square,
  lens centre 12.5 mm from one side edge and 14.4 mm from the bottom edge, 11.3 mm overall thickness (12.0 for the wide lens; the text of the brief says 11.5 and 12.4, so the figures disagree by 0.2 to 0.4 mm). Tolerance 0.2 mm.
- CAM-1 in the original is a 35 x 35 x 73 mm optical tube [S12]. The replica's camera tube is a printed
  shell of that size with a module inside and the lens at the front. The 80 degree field of view [S12]
  sits between the two Module 3 options.
- Alternatives not checked: an ESP32-CAM (smaller, lower quality, no real video encode on the board).

## Motor drivers

- **Dual MC33926 carrier** (#1213): 5 to 28 V, two channels, "almost 3 A" continuous per channel and 5 A
  for a few seconds in the description, but **2.5 A in the spec table** (use that), current sense about
  0.525 V/A, PWM up to 20 kHz, 2.5 to 5.5 V logic, reverse-voltage protection on the motor supply. Size
  1.10 x 1.8 in; weight 0.25 oz; US$39.95. **Operation from 5 to 8 V reduces the maximum current**, and our
  2S pack runs 6 to 8.4 V, so expect less than 2.5 A. Pololu's test: 5 A for 5 s, then derated.
- Fit to the load: at the 10 kg design mass the motor draws about 1.0 A at the 20 degree slope torque
  (`drive-spec.md`) and about 2.4 A at the gearbox's instantaneous limit (2.45 N.m, interpolated). The slope load is
  within one channel, so one dual board drives each side; the peaks sit at the 2.5 A rating (5 A for a few
  seconds), **if the supply sags no lower than about 6 V**, where the rating falls.
- The current-sense output gives stall detection for free, replacing encoders.
- A cheaper option, the DRV8833 dual carrier (2.7 to 10.8 V, 1.2 A continuous per channel, 2 A peak), is
  enough for the slope but not for the 1.5 A obstacle case; not chosen.

## Servos

- **Feetech STS3215**: serial bus (TTL, 38.4 kbps to 1 Mbps, up to 254 on one bus), magnetic encoder,
  45.2 x 24.7 x 35 mm, 55 g, 360 degree range, 25-tooth output spline. Retailers' figures, **not a Feetech
  datasheet**; the SKU matters:
  - C001, 7.4 V: 19.5 kg·cm stall, 52 rpm stall speed, gear 1/345; continuous rating listed at 6.5 kg·cm
    (at 6 V). The listings disagree on the voltage window (6 to 7.4, 6 to 8.4, 5 to 8.4 V): a fully charged
    2S pack is 8.4 V, so check before relying on it.
  - C044, 7.4 V: 27.4 kg·cm, 1/191. C046: 14.4 kg·cm, 1/147. C018 and C047 are 12 V versions.
- Its size, 45.2 x 24.7 x 35, matches the Waveshare ST3215's 2D drawing (45.22 x 24.72, body 32 mm thick with a 19.2 mm horn at each end, 37.25 over both; the shaft 10.11 mm from one end) and its
  3D model, which the mast head model uses (`mast-spec.md`; the Waveshare part's equivalence to the Feetech STS3215 is assumed). The Feetech datasheet read (2020) has no drawing.
- Free-run and stall current, and the mounting ear hole pattern, were not found. The horn has a 14 mm hole pattern on the Waveshare drawing.
- **Supply:** a full 2S pack is 8.4 V, above the servos' 6 to 7.4 V listings, so they run from a 6 V regulator (`power-spec.md`).
- A bus servo needs a half-duplex serial adapter between the controller and the bus; not chosen.
- Pan range of the original is plus or minus 179 degrees [S19]; a bus servo at 360 degrees covers it,
  with a software limit to protect the camera cable.

## Solar charge controller (shortlist, none bought)

The pack is charged from the side panels' cells (`solar-spec.md`). Needed: an MPPT charger for a 2S lithium pack (8.4 V,
constant current then constant voltage), fed by the chosen cells (tiled back-contact pieces: 18.75 V Vmpp, about 21 V Voc, 9.6 W a side at one sun; decided: a cheap BQ24650 or CN3722 buck module, `charger-board-spec.md`), in the
50 x 30 x 12 mm box reserved at the front floor. The deciding factor is the input voltage against the pack's 8.4 V:

| Cell option | String voltage at maximum power | Charger topology it needs |
|---|---|---|
| Tiled back-contact pieces, 2 per slot, decided (30 in series) | 18.75 V Vmpp, about 21 V Voc | buck is enough: well above 8.4 V; a cheap BQ24650 or CN3722 module |
| AnySolar SM261K10TF (3 in series per column, 5 columns in parallel) | 16.7 V Vmpp, 20.7 V Voc | buck is enough: well above 8.4 V |
| Futurlec SZGD6030, fallback (15 in series) | 7.2 V (15 x 0.48 V) | **buck-boost**: below a full pack's 8.4 V, so a buck cannot charge it |
| Silicon cut to 69 x 39 mm (15 in series) | about 8.7 V | **buck-boost**: only 0.3 V above a full pack, too little for a buck |
| Silicon, F3 (tiled, 30 in series) | 15 V listed, 20 V measured | buck is enough |
| Triple junction (rows in parallel) | 11.5 V, up to 13 V open circuit | buck is enough |

The buck-only limit is my reasoning from the topology; the chips' headroom specifications were not read.

| Candidate | What it is | Figures read | Fits | Caveats |
|---|---|---|---|---|
| **TI BQ25798** (needed for the Futurlec fallback; also works for the AnySolar string) | buck-boost charger IC, 1 to 4 cells, built-in MPPT (open-circuit-voltage scaling), I2C control | input 3.6 to 24 V; 5 A; 2S charge voltage accuracy -0.25 to +0.65 percent | all three options | a 4 x 4 mm QFN chip, so it needs a custom board or a third-party breakout (none found); TI's evaluation modules need an EV2400 or USB2ANY adapter and stock listings disagree; I2C from the Pi Zero would set it up and read its telemetry |
| Analog Devices **LT3652** (or a module built on it) | buck charger with input-voltage regulation as its MPPT | input 4.95 to 32 V (40 V absolute maximum); up to 2 A, set by resistor; float voltage up to 14.4 V, so 8.4 V works | triple junction, tiled silicon | buck only; a 2 A limit is just enough for the triple-junction side (15.6 W at 8.4 V is 1.9 A); no 2S module found, and a module sold for one cell would need its output voltage reset |
| Consonance **CN3722** (or a module built on it) | buck charge controller with MPPT for one or several lithium cells | input 7.5 to 28 V in one datasheet copy | triple junction, tiled silicon | the current rating differs between copies (the title says 5 A, not confirmed); buck only; copy of the datasheet to confirm before relying on it |

None of the three was found as a ready-made 2S solar module. The sources for this table are the chip datasheets and TI's
product and evaluation pages: [BQ25798](https://www.ti.com/product/BQ25798), [LT3652](https://www.analog.com/en/products/lt3652.html),
[CN3722 datasheet](https://www.mikrocontroller.net/attachment/563792/CN3722-CONSONANCE.pdf).

Both sides: the BQ25798 and the others take one input, so the left and right strings meet at a pair of blocking diodes
(`solar-spec.md` wiring) before the charger. A two-input charger was not found.

No small ready-made board was found in two rounds of searching (`charger-board-spec.md`). The plan is to try an evaluation board first (BQ25798EVM, or BQ25756EVM); a custom board is the last resort.

Open: the board's schematic and layout; the fuse and diode parts; the
firmware to set the BQ25798 over I2C if it is chosen.

## Mast stowing (deferred)

The mast is fixed for now (`mast-spec.md`), so no hinge parts are chosen. For when stowing is wanted:
the mast lying flat needed about 0.86 N.m on Earth with the earlier guessed masses. A hand check found that two
torsion springs sharing a swing from 0.6 down to 0.1 N.m over 90 degrees would need a rate of about 0.32 N.m per
radian each; with the textbook round-wire formula k = E d^4 / (10.8 D N) (E = 200 GPa) a 2.0 mm wire (about
760 MPa at 0.6 N.m) needs about 66 coils at a 14 mm mean diameter, or about 31 at 30 mm, which does not fit a
28 mm pedestal. That is a rough calculation, not a spring design. A bus servo on the hinge (Feetech C044,
27.4 kg.cm stall, 1/191, so holding 0.86 N.m = 8.8 kg.cm is about a third of stall) would deploy and stow
repeatedly but needs a pedestal that can hold a 45 x 25 x 35 mm servo on the hinge axis.

## Power

- **Cells:** four Samsung 30Q, 3000 mAh nominal, 15 A continuous, 48 g max, 18.4 x 65.0 mm max. As a 2S2P pack:
  6.0 Ah at 7.2 V nominal, about 43 Wh, 8.4 V full, about 0.19 kg of cells.
- **5 V supply:** D24V22F5, 5.3 to 36 V in, 5 V out, 2.5 A typical maximum at 24 V in (graphs for 7.4 V not
  read), minimum input about 5.8 V at 2.5 A. A fully discharged pack must stay above that: stop at 3.3 V a cell.
- **Runtime estimate (rough):** driving at the 10 kg slope load: four motors at about 1.0 A and 7.4 V is about 30 W; the Pi
  and camera, if they draw about 1 A at 5 V (an assumption), about 5 W; so about 35 W and roughly 1.1 to 1.2 h from 43 Wh (`power-spec.md` has the full current budget). At rest
  with the Pi alone, about 5 W and several hours. The motor figure assumes the slope load, which is the worst case; flat driving takes far less.
- **Solar:** the original's panels give 15 W peak [S3]; the replica's cells are dummies.

## Dimensioned board models (2026-11-07)

`hardware/electronics/boards.py` replaces the placeholder boxes with dimensioned models; the interior (`interior-spec.md`) places them. What each rests on:

| Part | Sourced | Measured | ASSUMPTION |
|---|---|---|---|
| Pololu MC33926 carrier #1213 | 27.94 x 45.72 mm, PCB 1.57, components to 7.67 above the underside (6.1 above the board; 7.8 for boards before Dec 2014), holes 2.18 mm, both 2.5 mm from one long edge and 40.6 apart (vendor dimension diagram, rev 26 Oct 2018) | two 8 x 8 mm ICs to 3.2 mm, one 4.8 x 5.0 IC, four 6.8 mm capacitors to 7.67 (slices of Pololu's 3D model; the model is not kept in this repo) | the three 2-pin 3.5 mm terminal blocks (7 x 7.7 x 8.5 mm bodies) and the 25-pin header are on the **underside** (the drawing's connector callouts are a bottom view), so the board is raised on 9 mm posts; the two posts at the far corners |
| Pololu D24V22F5 and F6 | 17.8 x 17.8 x 7.9 mm; two 2.18 mm holes on opposite corners 13.21 mm apart in each direction; 0.1 inch pin pitch (product page) | - | PCB 1.6 mm, inductor footprint 10 x 10 mm |
| Raspberry Pi Zero 2 W | 65 x 30 mm, holes 3.5 mm from the corners (58 x 23 apart), connector centres on one long edge at 12.4, 41.4 and 54 mm (product brief p. 4); 5.2 mm maximum height (a retailer listing, not the brief) | - | PCB 1.0 mm, hole 2.75 mm, connector sizes, the microSD slot, the CSI connector, the RF shield and the SoC |
| 4-way blade fuse block | candidate Optifuse BLR-I-304, 1.85 x 3.35 x 0.83 in = 47 x 85 x 21 mm (retailer listing) | - | which axis is which; the shape of the base and fuse positions; mass |
| Master switch | candidate SCI R13-112B8-02, round, 20.2 mm cut-out, 20 A at 14 VDC, IP65 (retailer listing) | - | bezel 23 mm, body depth 28 mm and tab length |

Findings that changed the layout:
- **The fuse block is bigger than the placeholder:** 85 x 47 x 21 mm against 60 x 36 x 20, if the listing's axes are as assumed. It no longer fits where it was; it sits at x -70, y -50, and the servo regulator moved to x -10, y -60.
- **The driver carriers stand 16.7 mm tall once mounted** (9 mm of posts plus 7.67), against the placeholder's 12 mm, because their connectors are on the underside (assumed).
- **The master switch needs a hole**: the rear panel now has a 20.2 mm hole at y 35, z 165; the bezel stands 2 mm proud of the panel and the body reaches 28 mm inside.
- The two driver boards are modelled separately, side by side at y -16 and y -44, 45.7 mm long in x.

Still boxes (no usable dimensions found): the battery pack (a 2 x 2 arrangement of 18.4 x 65 mm cells, 68 x 38 x 38 box), the BMS (generic listing sizes), the power node (bus bar), and the solar charge module (listings for the BQ24650 and CN3722 modules disagree: 45 x 20 x 9.5, 49 x 31, 54 x 38 and 50 x 25 x 17 mm were all seen).
Fetches of Pololu's regulator dimension drawing, the WAGO and Eaton datasheets failed or timed out, so those are not read.

## Open

- Battery management board, bus-servo adapter, fuses, switches, connectors, a charger for 2S: not chosen.
- Pi Zero 2 W and camera module masses, and the heights of the Pi's individual connectors: not found. The terminal block heights on the MC33926 carrier are assumed.
- The STS3215 datasheet and SKU voltage window; mounting hole pattern.
- Wiring harness and the cable path from the mast head down into the body.
