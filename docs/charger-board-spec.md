# Solar charger board (BQ25798) specification

The charger for the Futurlec string (7.2 V, `solar-spec.md`) into the 2S pack (8.4 V). No small ready-made board was found, in
two rounds of searching. **A custom board is the last resort** (the owner's call, 2026-11-07); the order of routes is under
"Routes, in order" below. Everything marked "datasheet" was read in the BQ25798 datasheet SLUSDV2C (June 2026); other values
are my choices. **No board has been designed in CAD or built.**

## Search for an off-the-shelf board (2026-11-07)

Nothing ready-made fits a 7.2 V string charging a 2S pack.

| Found | What | Why not |
|---|---|---|
| TI BQ25798EVM | evaluation board, US$156.45 on TI's page (not available on TI.com when read); the BKUPEVM was on AliExpress at about US$333 | the cheapest way to try the chip, but costly; TI's guide lists an EV2400 or USB2ANY adapter for I2C control, which the Pi's I2C could replace (not confirmed) |
| BQ25798 breakouts on Adafruit, SparkFun, Tindie, Crowd Supply | none found (Adafruit has a blog post and an Arduino library only) | not sold |
| BQ25798 chip, LCSC BQ25798RQMR | from US$1.72, QFN-29 (4 x 4 mm), thousands in stock when read | a bare chip, so a board is needed |
| An open KiCad BQ25798 breakout from an element14 blog post | schematic and project zip, about two years old; licence not checked | a starting point; "not all IO broken out" |
| Amazon-type modules for 3.7 V or 7.4 V lithium "from 9 V or 18 V panels", and BQ24650 or CN3722 2S modules (5 to 28 V in) | buck chargers, MPPT claims unverified | a buck cannot charge 8.4 V from 7.2 V |
| ZK-4KX buck-boost CC/CV module | 5 to 30 V in, 0.5 to 30 V out, 3 A continuous (4 A with cooling), about 88 percent; no MPPT mode documented | could charge a 2S pack from 7.2 V as a bench stopgap, but with no MPPT the input may sag and restart; untested |
| Analog Devices LT8490 | buck-boost MPPT controller, PV 6 to 80 V | a bare controller with external MOSFETs, larger and more work |

Sources: the TI [BQ25798 page](https://www.ti.com/product/BQ25798) and [BQ25798EVM](https://www.ti.com/tool/BQ25798EVM), the
[LCSC listing](https://www.lcsc.com/product-detail/C2876593.html), the Adafruit
[Eye on NPI post](https://blog.adafruit.com/2025/05/15/eye-on-npi-ti-bq25798-i2c-controlled-1-to-4-cell-5-a-buck-boost-battery-charger-mppt-for-solar-panels-eyeonnpi-digikey-digikey-adafruit/),
the [element14 post](https://community.element14.com/challenges-projects/design-challenges/eye-on-intelligence-challenge/b/blog/posts/adas-and-vehicle-monitoring-system-battery-charging-and-management),
the [ZK-4KX manual](https://diydsolar.sytes.net/wp-content/uploads/2022/10/ZK-4KX_English_Castellano.pdf).

## Broader search (2026-11-07, second round)

Searched beyond the BQ25798: other buck-boost charger chips, solar modules for 2S packs, and chains of modules. Still **no
small ready-made 2S buck-boost MPPT board**. What exists:

| Found | What | Fit |
|---|---|---|
| TI BQ25756EVM | evaluation board, 1 to 14 cells, buck-boost controller, 4.2 to 55 V in, 10 A, built-in MPPT, resistor-programmable standalone mode plus I2C; price not stated; the page shows stock as both "in stock" and "out of stock on TI.com"; the page lists an EV2400 for communication | electrically fine; board size not stated, and built for far more power than needed |
| TI BQ25798EVM | as above: US$156.45, availability unclear | electrically the best fit; I2C setup is needed for MPPT |
| Analog Devices DC2703A-A-KIT | LT8491 demo board plus a USB-to-I2C controller; buck-boost, 6 to 80 V in; factory setup is a 12 V lead-acid battery at up to 16.6 A; DigiKey listing about US$32 with a 10 week lead time (a surprisingly low price: verify) | would need reconfiguring for 2S lithium; not confirmed; a larger board built for 200 W class |
| Analog Devices DC2069A (LT8490 demo) | 17 to 54 V in, 12 V lead-acid out | input too high, no |
| LTC4162 breakout from a Particle forum post | homemade, 1 to 4 cells, 35 V maximum input, about 6 years old | not a product; the LTC4162 is a buck charger, so it cannot charge 8.4 V from 7.2 V |
| SparkFun Sunny Buddy (LT3652), Adafruit Solar Lipoly, Voltaic, Waveshare and DFRobot solar managers | single-cell lithium MPPT boards | wrong cell count, and buck |
| Icstation MPPT buck module, 6 to 36 V in | adjustable output | buck, needs more than 8.4 V in |
| An Amazon 6 V-panel board with 2 A | one lithium cell | wrong cell count |

Sources: TI [BQ25756EVM](https://www.ti.com/tool/BQ25756EVM) and [BQ25756](https://www.ti.com/product/BQ25756), Analog Devices
[DC2703A-A-KIT](https://www.analog.com/en/resources/evaluation-hardware-and-software/evaluation-boards-kits/dc2703a-a.html),
[DC2069A](https://www.analog.com/en/resources/evaluation-hardware-and-software/evaluation-boards-kits/dc2069a.html), the
[Particle forum post](https://community.particle.io/t/mppt-solar-charging-solution/58694), the
[Sunny Buddy hookup guide](https://learn.sparkfun.com/tutorials/sunny-buddy-solar-charger-v13-hookup-guide-/all).

**Chained modules.** A cheap boost module in front of a cheap 2S buck MPPT module (CN3722 or BQ24650 type, 5 to 28 V in, widely
sold) is not supported by anything found. The buck stage would track its own source, the boost output, not the panel, so
nothing tracks the panel's maximum power point; with irradiance changing, the boost stage's input could collapse and restart.
TI's application note on solar chargers points to a single buck-boost stage instead.

**Changing the panel instead.** A buck 2S module needs the string's Vmp above about 10.5 V, which is 22 or more Futurlec
cells in series. Fifteen per side gives 7.2 V. Putting both sides in series does not work, since only one side is lit. Adding
rows to reach 5 x 5 cells would break the original's 5 x 3 grid, which is one of the "must look like Rashid" features.

**Space.** Evaluation boards are larger than a breakout, but the front floor has room: a box of 84 x 66 x 30 mm at the
front right, where the charger placeholder is, clears the frame and the other parts (CAD check), and more if the
other parts move. The EVMs' sizes were not found, so whether one fits is unknown.

## Routes, in order

1. **Evaluation board, as the charger.** The BQ25798EVM is the best electrical fit (about US$156, availability unclear, the
   Pi's I2C can run the settings in `hardware/charger/init_bq25798.py`). The BQ25756EVM is the alternative (price and size
   not found). Check its size before buying. Try one on a real panel first; that also settles the open question about
   the cell's output.
2. **A buck 2S module with a higher-voltage string.** The Futurlec cells (7.2 V per side) cannot do this, but AnySolar's multi-cell
   modules can: columns of three in series give about 17 to 21 V (`solar-spec.md`, AnySolar section), which suits the cheap 5 to 28 V
   2S buck MPPT modules (BQ24650 or CN3722 type) with no buck-boost board. This would mean changing the cells.
3. **A bench stopgap** (ZK-4KX) for first tests only.
4. **A custom board** around the BQ25798, as specified below: the last resort.

## Why the BQ25798 fits (datasheet)

- Buck-boost, 1 to 4 cells, 5 A; VBUS operating range 3.6 to 24 V (absolute maximum 30 V when not switching; starts
  switching at 3.4 V). The string's 7.2 V Vmp and 8.25 V Voc sit well inside it.
- Built-in MPPT by open-circuit-voltage scaling: it stops switching, waits 50 ms to 5 s (default 300 ms), measures Voc
  and sets the input voltage to a fraction of it, re-measuring every 30 s to 30 min (default 2 min). The fraction is selectable
  from 0.5625 to 1.0; the default 0.875 matches the string's Vmp/Voc of 7.2/8.25 = 0.873. The datasheet says the MPP is
  usually 70 to 90 percent of Voc.
- The 2S cell count comes from a resistor on the PROG pin: 8.2 kohm for 2S at 750 kHz (with a 2.2 uH inductor) or
  6.04 kohm for 2S at 1.5 MHz (with a 1 uH inductor). At power-up that sets VREG = 8.4 V, charge current 1 A and
  minimal system voltage 7 V.
- I2C, 7-bit address 0x6B.

## Board contents, if a custom board is built (from the datasheet's typical application, without the optional input mux)

| Item | Value | Source |
|---|---|---|
| U1 | BQ25798RQMR, QFN-29, 4 x 4 mm | datasheet |
| Inductor | 2.2 uH, saturation current at least 2 A (750 kHz option), or 1 uH SPM6530T-1R0M120 (1.5 MHz option); the 1.5 MHz setting works only with 1 uH and 750 kHz only with 2.2 uH | datasheet |
| VBUS capacitors | 2 x 10 uF plus 0.1 uF | datasheet |
| PMID capacitors | 3 x 10 uF plus 0.1 uF | datasheet |
| SYS capacitors | 5 x 10 uF plus 0.1 uF | datasheet |
| BAT capacitors | 2 x 10 uF | datasheet |
| Capacitor voltage ratings | 25 V or 35 V ceramic on VBUS and PMID (the pins go to 30 V), 16 V or 25 V on SYS and BAT; note that ceramics lose capacitance under bias | my choice |
| Bootstrap | 47 nF, 10 V or more, between SW2 and BTST2 (and the same pattern for SW1 and BTST1: check the datasheet figure) | datasheet |
| BATP | 100 ohm in series with the battery positive | datasheet |
| SDRV | 1 nF, 50 V, 0402, to ground, when the ship FET is not used | datasheet |
| PROG | 8.2 kohm, 1 percent, to ground (2S, 750 kHz) | datasheet |
| INT | 10 kohm pull-up to the logic rail | datasheet |
| ILIM_HIZ | to REGN for the maximum input current | datasheet |
| TS | a 10 kohm 103AT-2 thermistor with a divider from REGN, or a fixed divider if not used (the fixed values were not read) | datasheet |
| Input diodes | one Schottky per side (a dark side must not load the lit one), at least 1 A and 20 V; joined at VBUS | `solar-spec.md`, my choice |
| Left out | the dual-input selector FETs (ACFET, RBFET) and backup mode | datasheet: only needed for those features |

Size: well inside the 50 x 30 x 12 mm space reserved at the front floor; a 30 x 30 mm board is my estimate, not a layout.

Connections: solar in (two 2-pin, one per side, to the diodes); battery (2-pin, to the pack's charge port through its BMS, so
the BMS stays in charge of cell protection); Pi header (SDA, SCL, INT, ground; the Pi's own pull-ups serve the I2C lines, and the pins
tolerate 6 V, so 3.3 V logic is fine). The rover's loads stay on the pack, not on SYS: SYS is the charger's output, limited to its
own power, so the motors would not be supplied from it.

## Firmware

`hardware/charger/init_bq25798.py` (untested; it has a dry-run) does three things over I2C after each power-up: disables the
40 s watchdog (default 5h), lowers the minimal system voltage from the 2S default of 7 V to 6 V because MPPT cannot be
enabled while the battery is below it and a 2S pack runs from 6 V, and sets VOC_PCT to 0.875 and enables MPPT. Until the Pi
runs it, MPPT is off (the datasheet default), so the panel is loaded at the default input limit rather than tracked;
a power-up service on the Pi would do it.

## Open

- Layout (only if route 4 is needed): a KiCad schematic and board are not drawn; the datasheet's typical-application figure
  and layout guidelines were not studied beyond the values above.
- The TS thermistor choice, the bootstrap and REGN capacitors, and the diode and inductor part numbers.
- Whether the bench stopgap (the ZK-4KX) is worth buying.
- Soldering a QFN-29 by hand needs hot air or a reflow oven; a board house assembly service is the alternative.
- Testing: nothing here has run on a charger.
