"""al-maha solar charger: power-up settings for the BQ25798 over I2C (UNTESTED: no hardware yet).

Run on the Raspberry Pi after each power-up of the charger board. Register addresses and
fields are from the BQ25798 datasheet SLUSDV2C (read 2026-11-07):
  REG00 (0x00)  minimal system voltage, bits 5:0, 2.5 V + 0.25 V per step (2.5 to 16 V)
  REG10 (0x10)  bits 2:0 WATCHDOG (reset 5h = 40 s; 0 = disabled); bits 7:4 are left as read
  REG15 (0x15)  MPPT: bits 7:5 VOC_PCT (5h = 0.875), 4:3 VOC_DLY (1h = 300 ms),
                2:1 VOC_RATE (1h = 2 min), bit 0 EN_MPPT (reset 0)
7-bit I2C address 0x6B. The cell count (2S: VREG 8.4 V, ICHG 1 A, VSYSMIN 7 V at power-up)
comes from the PROG pin resistor on the board, not from this script.

What it does:
  * disables the watchdog, so the settings are not reset after 40 s without host traffic
  * lowers the minimal system voltage to 6.0 V: MPPT cannot be enabled while the battery is
    below VSYSMIN (datasheet 7.3.6.3), and the default for 2S is 7 V, high for a pack that
    runs 6 to 8.4 V
  * sets VOC_PCT to 0.875 (the string's Vmp/Voc = 7.2 / 8.25 = 0.873) and enables MPPT

Usage:  python3 init_bq25798.py [--dry-run] [--bus 1]
        --dry-run prints the writes without touching the bus (works anywhere)
"""
import argparse
import sys

ADDR = 0x6B
REG_VSYSMIN, REG_CTRL1, REG_MPPT = 0x00, 0x10, 0x15

VSYSMIN_V = 6.0
VOC_PCT = 0x5               # 0.875
VOC_DLY, VOC_RATE = 0x1, 0x1


def vsysmin_code(volts):
    code = round((volts * 1000 - 2500) / 250)
    if not 0 <= code <= 0x3F:
        raise ValueError("VSYSMIN out of the 2.5 to 16 V range")
    return code


def plan(read):
    """Return [(register, new value)] given a function read(register) -> current value."""
    out = []
    v = read(REG_VSYSMIN)
    out.append((REG_VSYSMIN, (v & 0xC0) | vsysmin_code(VSYSMIN_V)))
    c = read(REG_CTRL1)
    out.append((REG_CTRL1, c & ~0x07))                      # watchdog off
    m = (VOC_PCT << 5) | (VOC_DLY << 3) | (VOC_RATE << 1) | 0x01
    out.append((REG_MPPT, m))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--bus", type=int, default=1)
    a = ap.parse_args()
    if a.dry_run:
        defaults = {REG_VSYSMIN: 0x12, REG_CTRL1: 0x85, REG_MPPT: 0xAA}   # power-up values for 2S: 7 V = code 0x12, 0x85 and 0xAA from the datasheet
        for r, v in plan(lambda reg: defaults[reg]):
            print(f"write reg 0x{r:02X} <- 0x{v:02X}")
        return 0
    from smbus2 import SMBus
    with SMBus(a.bus) as bus:
        read = lambda reg: bus.read_byte_data(ADDR, reg)
        for r, v in plan(read):
            bus.write_byte_data(ADDR, r, v)
            back = read(r)
            print(f"reg 0x{r:02X} <- 0x{v:02X}, read back 0x{back:02X}" + ("" if back == v else "  MISMATCH"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
