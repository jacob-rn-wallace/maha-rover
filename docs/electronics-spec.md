# Electronics and actuators: parts shortlist (replica)

Candidate parts for the replica, read 2026-11-07. **Nothing is bought or final.** Figures are from
vendor pages and datasheets unless marked; where a source disagreed or a value was not found, that
is said. Sizes feed the interior layout (`interior-spec.md`) and the mast (`mast-spec.md`).

## Summary

| Role | Candidate | Qty | Size (mm) | Mass |
|---|---|---|---|---|
| Controller | Raspberry Pi Zero 2 W | 1 | 65 x 30 | not found |
| Camera | Raspberry Pi Camera Module 3 (75 or 120 degree) | 1 | 25 x 24 x 11.5 (12.4 wide) | not found |
| Drive motor | Pololu 37D, #4746 (see `drive-spec.md`) | 4 | 37 dia x 57 | 175 to 195 g |
| Motor driver | Pololu Dual MC33926 carrier, #1213 | 2 | 28 x 46 (1.10 x 1.8 in), height not found | 7 g (0.25 oz) |
| Pan, tilt servo | Feetech STS3215 C001 (7.4 V) | 2 | 45.2 x 24.7 x 35 | 55 g |
| Hinge servo (recommended, see below) | Feetech STS3215 C044 (7.4 V, 1/191) | 1 | 45.2 x 24.7 x 35 | 55 g |
| 5 V supply | Pololu D24V22F5 | 1 | 17.8 x 17.8 x 7.9 | 2.3 g |
| Cells | Samsung INR18650-30Q | 4 | 18.4 dia x 65.0 max | 48 g max each |
| Battery management | generic 2S BMS with balancing | 1 | not chosen | not found |

## Controller and camera

- **Raspberry Pi Zero 2 W** (product brief, Apr 2024): 65 x 30 mm, quad-core Cortex-A53 at 1 GHz, 512 MB,
  2.4 GHz wireless LAN and Bluetooth 4.2, a CSI-2 camera connector, a 40-pin footprint (unpopulated),
  H.264 encode to 1080p30, 5 V DC at 2.5 A input (the brief's supply rating, not a measured draw).
  Mass and board height were not found.
- **Camera Module 3** (raspberrypi.com): 12 MP Sony IMX708, autofocus, 75 or 120 degree diagonal field
  of view (the wide one is 12.4 mm tall), 25 x 24 x 11.5 mm, 15 x 1 mm FPC with a 200 mm cable; a Zero needs
  a separate Zero camera cable. 1080p50, 720p120. From US$25.
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
- Fit to the load: the motor draws about 0.6 A at the 20 degree slope torque (0.74 A at 60 kg·mm, from the
  datasheet; derived by proportion) and about 1.5 A at 1.2 N·m. Both are within one channel, so one dual
  board drives each side with margin, **if the supply sags no lower than about 6 V**.
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
- Its size, 45.2 x 24.7 x 35, matches the 45 x 24 x 35 placeholder in the mast model; the neck cavity
  (52 x 52 x 38) holds it with 3 mm of height to spare.
- Free-run and stall current, and the mounting hole pattern, were not found.
- A bus servo needs a half-duplex serial adapter between the controller and the bus; not chosen.
- Pan range of the original is plus or minus 179 degrees [S19]; a bus servo at 360 degrees covers it,
  with a software limit to protect the camera cable.
- Micro servo for a latch (MG90S class: 22.8 x 12.2 x 28.5 mm, about 13 g, 2.0 to 2.8 kg·cm at 4.8 to 6 V,
  retailers' figures) is only needed if the spring-and-latch mast is kept; see the next section.

## Mast hinge: the spring route does not fit

The mast spec assumed two torsion springs and a latch. A hand check says the springs are too big.
The mast lying flat needs about 0.86 N·m on Earth (`mast-spec.md`, from guessed masses). For two springs
sharing a swing from 0.6 N·m down to 0.1 N·m over 90 degrees, the rate is about 0.32 N·m per radian each.
With the textbook round-wire formula, k = E d^4 / (10.8 D N) (E = 200 GPa), a 2.0 mm wire (a bending stress of
about 760 MPa at 0.6 N·m, which is acceptable) needs about 66 coils at a 14 mm mean diameter, or about 31
coils at 30 mm. Either is longer or wider than the 28 mm pedestal and 102 mm width allow. This is a rough
calculation, not a spring design.

**Recommendation:** drive the hinge with a bus servo (C044, 27.4 kg·cm stall, so holding 0.86 N·m = 8.8 kg·cm
is about a third of stall) instead of springs and a latch. It deploys and stows repeatedly and removes
the latch servo. It changes the mast model: the pedestal must hold a 45 x 25 x 35 mm servo on the hinge axis,
which the 28 mm pedestal cannot. That redesign is not done; it needs your go-ahead because it departs from the
original's spring hinge. It is the main open mast question.

## Power

- **Cells:** four Samsung 30Q, 3000 mAh nominal, 15 A continuous, 48 g max, 18.4 x 65.0 mm max. As a 2S2P pack:
  6.0 Ah at 7.2 V nominal, about 43 Wh, 8.4 V full, about 0.19 kg of cells.
- **5 V supply:** D24V22F5, 5.3 to 36 V in, 5 V out, 2.5 A typical maximum at 24 V in (graphs for 7.4 V not
  read), minimum input about 5.8 V at 2.5 A. A fully discharged pack must stay above that: stop at 3.3 V a cell.
- **Runtime estimate (rough):** driving: four motors at about 0.6 A and 7.4 V is about 18 W; the Pi and camera, if
  they draw about 1 A at 5 V (an assumption), about 5 W; so about 23 W and roughly 1.9 h from 43 Wh. At rest
  with the Pi alone, about 5 W and several hours. The motor figure assumes the slope load; real use will differ.
- **Solar:** the original's panels give 15 W peak [S3]; the replica's cells are dummies.

## Open

- Battery management board, bus-servo adapter, fuses, switches, connectors, a charger for 2S: not chosen.
- Pi Zero 2 W, camera module and driver masses and heights: not found.
- The STS3215 datasheet and SKU voltage window; mounting hole pattern.
- Wiring harness and the cable path across the mast hinge.
