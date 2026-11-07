# Solar charger board (BQ25798) specification

The charger for the primary cells' string (AnySolar SM261K10, 16.7 V Vmpp and 20.7 V Voc per side, `solar-spec.md`) into the 2S pack (8.4 V).
The original plan assumed the 7.2 V Futurlec string, which only a buck-boost can charge from; the AnySolar string is above the
pack, so a buck charger works and the options widen. The Futurlec fallback still needs the buck-boost. No small ready-made board was found, in
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

## Is a converter needed at all? (2026-11-07)

Some kind of charger is needed with every cell option. The pack must be charged at constant current and then constant voltage to 8.4 V,
and the panel's voltage moves with light and temperature. What changes with the cells is the type of charger:

| Cells | String voltage at maximum power | What it needs |
|---|---|---|
| Futurlec, 15 in series | 7.2 V | a buck-boost (below the pack's 8.4 V) |
| AnySolar SM261K10, 3 in series per column | 16.7 V | a buck is enough; no buck-boost board (this is what was meant earlier: the buck-boost goes, not the charger) |
| Tiled back-contact pieces, 1 per slot, 15 in series | about 9.4 V | a buck-boost, or possibly none (below) |
| Tiled back-contact pieces, 2 per slot, 30 in series | about 18.8 V | a buck is enough (Voc near 24 V when cold) |

**The one case that could drop the converter: the tiled pieces, one per slot.** At 9.4 V the string is just above the pack, so a Schottky
diode between the string and a 2S pack with its battery management board might charge it directly, with no MPPT: the pack
voltage (6 to 8.4 V) holds the panel below its maximum power voltage, where the current is nearly flat, so the panel delivers about
the pack voltage times its 1.0 A. My arithmetic: at a pack voltage of 6.0 V about 6 W of the 9.5 W maximum (63 percent), at 7.4 V
about 7.4 W (78 percent), at 8.4 V about 8.4 W (88 percent). Problems:
- the panel's Vmp falls about 0.2 percent per kelvin of heating: on a hot panel the string may not reach the 8.4 V plus the
  diode's 0.3 V needed to finish the charge (the temperature coefficient and the real Vmp are not known for these cells);
- when the pack is full and the BMS opens its charge switch, the panel's open-circuit voltage (about 10.5 V by my estimate) appears
  across that switch: the BMS must tolerate it, and no 2S BMS rating was checked;
- the BMS is then the only protection against overcharge, and there is no current control for a cold or deeply discharged pack.
This is a hobby shortcut that gives up 12 to 37 percent of the energy and some safety, for saving the charger. Not recommended
for the first build; it could be tried later as an experiment.

## Cheap buck 2S MPPT modules found (2026-11-07)

For the arrays above a pack's 8.4 V (AnySolar 16.7 V; tiled pieces at 2 per slot, 18.8 V). Listings only; none bought or measured, and Amazon's
pages did not load, so prices were not read.

| Module | Chip | What the listings claim | Notes |
|---|---|---|---|
| BQ24650 MPPT charger, 50 x 25 x 17 mm ([Amazon](https://www.amazon.com/BQ24650-MPPT-Solar-Charger-Module/dp/B0H8P8P4TS), [AU listing for 2S to 4S](https://www.amazon.com.au/Charging-Portable-Controller-Intelligent-Temperature/dp/B0H4W46SX7)) | TI BQ24650 | 5 to 28 V in, up to 8 A, adjustable output (one says 4.2 to 28 V, another lists 7.2, 8.4, 12.6 and 16.8 V), 96 percent efficiency at 16 V in and 12 V out; recommends under 24 V in | the chip is documented; the 8 A is a board rating, not checked; the array draws only about 0.5 A |
| CN3722 MPPT module ([LaskaKit MPPT-V08A](https://www.laskakit.cz/en/solarni-nabijecka-li-ion--lifepo4-clanku-mppt-v08a-cn3722/), [Circuit Mall, 5 A](https://circuitmall.ng/product/cn3722-5a-mppt-charge-controller-module/), AliExpress 2 A and 3 A versions) | Consonance CN3722 | 8 to 28 V in (one listing 9 to 24 V); 2, 3 or 5 A by listing; 2S output 8.4 V among the choices | a teardown found an adjustable voltage pot and an unpopulated fixed-resistor pad; a LaskaKit buyer called it "pseudo-MPPT"; board size not found |
| eletechsup 9 V, 12 V, 18 V, 24 V MPPT module ([Amazon](https://www.amazon.com/clp/B0CKXLW4HL)) | not stated | 3.6 to 24 V in, 4 A, lithium and LiFePO4; selectable panel voltage 9, 12, 18 or 24 V | details not read: the 18 V setting is just above the AnySolar string's 16.7 V Vmpp |

**What "MPPT" means on these.** The BQ24650 datasheet (SLUSA75B) says the input voltage is regulated to a set point you choose with a
divider from the panel to the MPPSET pin (it regulates MPPSET to 1.2 V): a fixed-voltage method, not a search. BeyondLogic's review of a
BQ24650 module says the same, and a DIY Solar Forum member says the CN3722 and BQ24650 modules advertising MPPT only regulate a
constant input voltage (an opinion, not a measurement). The BQ24650's other facts from the datasheet: operating input 5 to 28 V; battery
2.1 to 26 V; three-phase charging that ends at one tenth of the fast-charge current; it goes to sleep when the input falls
below the battery voltage (the sleep threshold is about 100 mV, with 500 mV of hysteresis). A fixed point near the array's Vmpp is a
fair approximation for a small panel but gives up some energy when the temperature or light moves the real Vmpp; the BQ25798 re-measures
Voc every two minutes and tracks better. For scale: the AnySolar string's Vmpp falls about 1.3 V for a panel 25 K hotter (from the
datasheet's -17.4 mV/K per module, three in series, assuming Vmpp moves like Voc), so a set point at 16.5 V would sit above the hot Vmpp;
choosing about 15.5 V trades a little at STC for a little when hot (not computed).

**What to check on a module before wiring a pack.** The output voltage with no battery (set it to 8.4 V first: a wrong chemistry setting
overcharges the cells); the input set point (and change the divider resistors if needed: it is a fixed point); the termination current;
and the input voltage under a lamp. No module here was found with a published test of its tracking. The pack's battery management board still
guards the cells.

## Routes, in order

1. **A cheap buck 2S MPPT module** (BQ24650 or CN3722 type, 5 to 28 V in; listings in the section above, none verified).
   With the AnySolar string at 16.7 V (Voc 20.7 V, 23.1 V at -20 C) this is the simplest and cheapest route. Verify before buying
   that the MPPT is real (a forum thread warns that many are not), the 8.4 V cutoff setting, and the input limit.
2. **An evaluation board.** The BQ25798EVM is the best electrical fit (about US$156, availability unclear; the Pi's I2C can run the
   settings in `hardware/charger/init_bq25798.py`); the BQ25756EVM is the alternative (price and size not found). Check the size
   before buying. Trying one on a real panel also measures the panels' real output.
3. **A bench stopgap** (ZK-4KX) for first tests only.
4. **A custom board** around the BQ25798, as specified below: the last resort.

## Why the BQ25798 fits (datasheet)

- Buck-boost, 1 to 4 cells, 5 A; VBUS operating range 3.6 to 24 V (absolute maximum 30 V when not switching; starts
  switching at 3.4 V). The Futurlec string's 7.2 V Vmp and 8.25 V Voc sit well inside it; the AnySolar string's 20.7 V Voc
  (23.1 V at -20 C) fits, but only just.
- Built-in MPPT by open-circuit-voltage scaling: it stops switching, waits 50 ms to 5 s (default 300 ms), measures Voc
  and sets the input voltage to a fraction of it, re-measuring every 30 s to 30 min (default 2 min). The fraction is selectable
  from 0.5625 to 1.0; the default 0.875 would match the Futurlec string's Vmp/Voc of 7.2/8.25 = 0.873, and the AnySolar string's
  16.74/20.73 = 0.808 calls for 0.8125. The datasheet says the MPP is usually 70 to 90 percent of Voc.
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
enabled while the battery is below it and a 2S pack runs from 6 V, and sets VOC_PCT to 0.8125 (for the AnySolar string; 0.875 for the Futurlec one) and enables MPPT. Until the Pi
runs it, MPPT is off (the datasheet default), so the panel is loaded at the default input limit rather than tracked;
a power-up service on the Pi would do it.

## Open

- Layout (only if route 4 is needed): a KiCad schematic and board are not drawn; the datasheet's typical-application figure
  and layout guidelines were not studied beyond the values above.
- The TS thermistor choice, the bootstrap and REGN capacitors, and the diode and inductor part numbers.
- Whether the bench stopgap (the ZK-4KX) is worth buying.
- Soldering a QFN-29 by hand needs hot air or a reflow oven; a board house assembly service is the alternative.
- Testing: nothing here has run on a charger.
