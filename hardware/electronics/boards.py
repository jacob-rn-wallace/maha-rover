"""al-maha electronics: the boards and small parts as simplified but dimensioned models (build123d), replacing the placeholder boxes of interior.py.

Each function returns a dict with:
    solid  the model, board corner at x = 0, y = 0 (x along the long edge), underside of the PCB at z = 0; standoffs and anything under the PCB at z < 0
    mass   kg
    note   what is sourced and what is ASSUMPTION
Numbers marked [src] come from vendor drawings read 2026-11-07; the component footprints of the MC33926 carrier were measured on Pololu's published 3D
model (a slice at several heights; the model itself is not kept in this repo). Component heights and positions marked ASSUMPTION are not in any source
read: they are plausible fill for the envelope. Millimetres.

Sources:
  Pololu Dual MC33926 carrier #1213: dimension diagram (rev 26 Oct 2018) and STEP model, https://www.pololu.com/product/1213
  Pololu D24V22Fx regulators: product pages #2858 (F5), https://www.pololu.com/product/2858 (diagram not fetched; hole figures from the page)
  Raspberry Pi Zero 2 W product brief (Apr 2024), page 4 (outline and holes), https://pip.raspberrypi.com/documents/RP-008359-DS-raspberry-pi-zero-2-w-product-brief.pdf
  Pi Zero 2 W height: 5.2 mm max, from a retailer listing (Switch Science), not the brief
  Fuse block: Optifuse BLR-I-304, 4-pole, 1.85 x 3.35 x 0.83 in on a retailer listing (axes not stated), https://www.chiefenterprises.com/optifuse-blr-i-304-fuse-block-blr-i-300-ato-atc-led-4-pole
  Switch: SCI R13-112B8-02, round 20 mm rocker, 20.2 mm panel cut-out, 0.7 to 2.5 mm panel, 20 A at 14 VDC, IP65 (retailer listing; body depth not found)

Run:  .venv/bin/python hardware/electronics/boards.py
"""
import math

from build123d import Box, Compound, Cylinder, Pos, Rot

PCB_COLOR_NOTE = "PCB thickness assumed where not stated"


def _box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def _post(x, y, z0, z1, d):
    return Pos(x, y, (z0 + z1) / 2) * Cylinder(d / 2, z1 - z0)


def _holes(shape, pts, d, z0, z1):
    for (x, y) in pts:
        shape = shape - Pos(x, y, (z0 + z1) / 2) * Cylinder(d / 2, z1 - z0 + 2.0)
    return shape


# ---------------------------------------------------------------------------------------------
def mc33926_carrier(standoff=9.0):
    """Pololu Dual MC33926 Motor Driver Carrier #1213. 27.94 x 45.72 mm, PCB 1.57 [src], components to 7.67 above the PCB underside [src]
    (6.1 above the board; 7.8 for boards before Dec 2014). Mounting holes 2.18 mm [src], both 2.5 mm from the right edge, 40.6 apart [src].
    Two 8 x 8 mm ICs to 3.2 mm and a 4.8 x 5.0 mm IC [measured on the vendor model], four 6.8 mm capacitors to 7.67 [measured].
    The three 2-pin 3.5 mm terminal blocks and the 25-pin header are on the underside [the drawing's connector callouts are a bottom view]:
    block bodies 7 x 7.7 x 8.5 mm are ASSUMPTION (not in the vendor model, which is the bare board), at the six pad positions of the drawing.
    The board is raised on four 5 mm posts: two at the holes, two ASSUMPTION at the left corners, so the terminal blocks clear the floor."""
    L, W, T = 45.72, 27.94, 1.57              # long side along x here (the vendor drawing's y)
    pcb = _box(0, L, 0, W, 0, T)
    caps = [(5.2, 6.6), (5.2, 13.6), (40.5, 12.7), (40.5, 19.6)]        # (x, y) in this frame = vendor (y, x)
    solid = pcb
    for (cx, cy) in caps:
        solid = solid + _post(cx, cy, T, 7.67, 6.8)
    solid = solid + _box(11.1, 19.1, 11.9, 19.9, T, 3.2) + _box(26.3, 34.4, 11.9, 19.9, T, 3.2) + _box(6.3, 11.3, 21.5, 26.3, T, 3.2)
    pads = [31.2, 27.7, 24.2, 20.7, 17.2, 13.7]                          # vendor y of the six terminal pads, bottom view
    for k in range(3):
        yv = (pads[2 * k] + pads[2 * k + 1]) / 2
        solid = solid + _box(yv - 3.85, yv + 3.85, 24.4 - 3.5, W, -8.5, 0)                       # block bodies on the underside at the right edge, ASSUMPTION
    holes = [(2.5, W - 2.5), (43.2, W - 2.5)]                             # vendor (x = 25.44 from the left, y = 2.5 and 43.2): mapped to (y, x) here
    solid = _holes(solid, holes, 2.18, -0.5, T + 0.5)
    for (hx, hy) in holes + [(2.5, 2.5), (43.2, 2.5)]:
        solid = solid + (_post(hx, hy, -standoff, 0, 5.0) - _post(hx, hy, -standoff - 0.5, 0.5, 2.18))
    return {"solid": solid, "mass": 0.007, "note": "outline, PCB, holes, height [src]; IC and capacitor footprints measured; terminal blocks, underside and the left posts ASSUMPTION"}


# ---------------------------------------------------------------------------------------------
def d24v22fx(standoff=4.0):
    """Pololu D24V22F5 / F6 step-down regulator: 17.8 x 17.8 x 7.9 [src, product page]; two 2.18 mm holes on opposite corners 13.21 apart in x and y
    [src]; five 0.1 inch pins along one edge [src]. PCB 1.6 and the inductor footprint (10 x 10) are ASSUMPTION; the inductor is the tall part."""
    S, T = 17.8, 1.6
    solid = _box(0, S, 0, S, 0, T)
    solid = solid + _box(4.0, 14.0, 5.5, 15.5, T, 7.9)                                # inductor, ASSUMPTION
    solid = solid + _box(2.0, 3.0, 1.0, 4.0, T, 3.0)                                  # a couple of small parts, ASSUMPTION
    holes = [(2.29, 2.29), (2.29 + 13.21, 2.29 + 13.21)]
    solid = _holes(solid, holes, 2.18, -0.5, T + 0.5)
    for (hx, hy) in holes:
        solid = solid + (_post(hx, hy, -standoff, 0, 4.5) - _post(hx, hy, -standoff - 0.5, 0.5, 2.18))
    return {"solid": solid, "mass": 0.0023, "note": "outline, height, holes, pin pitch [src]; PCB thickness and inductor footprint ASSUMPTION"}


# ---------------------------------------------------------------------------------------------
def pi_zero_2w(standoff=5.0):
    """Raspberry Pi Zero 2 W: 65 x 30 mm, four mounting holes 3.5 mm from the corners (58 x 23 apart), connector centres on the bottom long edge at
    x = 12.4 (mini HDMI), 41.4 (USB data) and 54 (power) [src, brief p. 4]; the 40-pin GPIO footprint along the top edge, unpopulated [src];
    5.2 mm maximum height [retailer]. PCB 1.0 mm, hole 2.75 mm, connector sizes, the microSD slot at the left, the CSI connector at the right
    and the RF shield and SoC are ASSUMPTION."""
    L, W, T = 65.0, 30.0, 1.0
    top = 5.2
    solid = _box(0, L, 0, W, 0, T)
    solid = solid + _box(12.4 - 5.6, 12.4 + 5.6, -1.0, 6.0, T, T + 3.0)              # mini HDMI, ASSUMPTION
    solid = solid + _box(41.4 - 3.75, 41.4 + 3.75, -1.0, 4.6, T, T + 2.6)           # micro USB data, ASSUMPTION
    solid = solid + _box(54.0 - 3.75, 54.0 + 3.75, -1.0, 4.6, T, T + 2.6)           # micro USB power, ASSUMPTION
    solid = solid + _box(-1.0, 14.0, 3.0, 14.0, T, top)                              # microSD slot (the 5.2 mm tallest part), ASSUMPTION
    solid = solid + _box(L - 3.0, L + 0.3, 12.0, 24.0, T, T + 2.0)                    # CSI connector, ASSUMPTION
    solid = solid + _box(20.0, 32.0, 8.0, 20.0, T, T + 2.2)                           # RF shield, ASSUMPTION
    solid = solid + _box(36.0, 48.0, 10.0, 22.0, T, T + 1.2)                          # SoC package, ASSUMPTION
    holes = [(3.5, 3.5), (L - 3.5, 3.5), (3.5, W - 3.5), (L - 3.5, W - 3.5)]
    solid = _holes(solid, holes, 2.75, -0.5, T + 0.5)
    for (hx, hy) in holes:
        solid = solid + (_post(hx, hy, -standoff, 0, 5.0) - _post(hx, hy, -standoff - 0.5, 0.5, 2.75))
    return {"solid": solid, "mass": 0.011, "note": "outline, holes, connector centres [src]; height 5.2 [retailer]; the rest ASSUMPTION; mass ASSUMPTION"}


# ---------------------------------------------------------------------------------------------
def fuse_block_4way():
    """4-way ATC/ATO blade fuse block, candidate Optifuse BLR-I-304: 3.35 x 1.85 x 0.83 in = 85 x 47 x 21 mm on a retailer listing, axes
    ASSUMPTION (the long side along the row of fuses). Modelled as a base 85 x 47 x 7 with four raised fuse positions 14 wide and a bus
    cover along one side; the real part's details are not known."""
    L, W, H = 85.0, 47.0, 21.0
    solid = _box(0, L, 0, W, 0, 7.0)
    for k in range(4):
        x0 = 6.0 + k * 19.0
        solid = solid + _box(x0, x0 + 14.0, 8.0, W - 6.0, 7.0, H)
    solid = _holes(solid, [(5.0, W / 2), (L - 5.0, W / 2)], 4.5, -0.5, 7.5)
    return {"solid": solid, "mass": 0.045, "note": "envelope from a retailer listing, axes and details ASSUMPTION; mass ASSUMPTION"}


def rocker_switch(depth=28.0):
    """Round 20 mm rocker switch, candidate SCI R13-112B8-02: 20.2 mm panel cut-out, 20 A at 14 VDC, IP65 [retailer listing]. Bezel 23 mm
    across and body depth 28 mm ASSUMPTION (not found). Modelled with its axis along +z: the bezel face is at z = 0 and the body goes down to
    -depth; the quick-connect tabs are 4.8 mm wide [listing]."""
    solid = Pos(0, 0, 1.0) * Cylinder(11.5, 2.0)
    solid = solid + Pos(0, 0, -depth / 2) * Cylinder(10.1, depth)
    for dx in (-4.0, 4.0):
        solid = solid + _box(dx - 2.4, dx + 2.4, -0.4, 0.4, -depth - 8.0, -depth)
    return {"solid": solid, "mass": 0.012, "note": "cut-out 20.2 and the electrical rating [listing]; bezel, depth and tab length ASSUMPTION"}


# ---------------------------------------------------------------------------------------------
def gnss_breakout(standoff=5.0):
    """GNSS receiver breakout, candidate SparkFun GPS-15712 (NEO-M9N, u.FL): the board is 1.30 x 1.60 in = 33.0 x 40.6 mm [SparkFun hookup guide]; supply 3.3 V; I2C, UART, PPS and
    SPI pins [same guide]. PCB 1.6 mm, the 12.2 x 16 x 2.4 mm module (u-blox NEO-M9N size, recollection), the u.FL jack and the pin header are ASSUMPTION; mounting holes were not read
    (the model has four 2.5 mm holes 3 mm from the corners as a placeholder). Component height about 5 mm over the PCB is ASSUMPTION; mass 8 g is ASSUMPTION (not found)."""
    L, W, T = 40.6, 33.0, 1.6
    solid = _box(0, L, 0, W, 0, T)
    solid = solid + _box(10.0, 22.2, 9.0, 25.0, T, T + 2.4)                              # NEO-M9N module, ASSUMPTION size
    solid = solid + _box(3.0, 9.0, 14.0, 20.0, T, T + 2.5)                               # u.FL jack, ASSUMPTION
    solid = solid + _box(4.0, L - 4.0, 1.0, 3.5, T, T + 3.0)                             # pin header along one edge, ASSUMPTION
    holes = [(3.0, 3.0), (L - 3.0, 3.0), (3.0, W - 3.0), (L - 3.0, W - 3.0)]
    solid = _holes(solid, holes, 2.5, -0.5, T + 0.5)
    for (hx, hy) in holes:
        solid = solid + (_post(hx, hy, -standoff, 0, 5.0) - _post(hx, hy, -standoff - 0.5, 0.5, 2.5))
    return {"solid": solid, "mass": 0.008, "note": "board size [SparkFun]; module, jack, header, holes, height and mass ASSUMPTION"}


def bus_servo_adapter(standoff=5.0):
    """Waveshare Bus Servo Adapter (A), for the STS3215 / ST3215 servos: 42 x 33 mm with 2.5 mm mounting holes 37 x 28 mm apart [Waveshare wiki and product page]; 18.5 mm thick
    and 21.2 g on a Digitec listing (Waveshare lists 16 g); a 5.5 x 2.1 mm barrel jack for 9 to 12.6 V, a USB port and a UART header [Waveshare]. The thickness includes the connectors, which
    are modelled as blocks at the ends (ASSUMPTION for their sizes and positions); the standoffs raise the board 5 mm so the underside parts clear the floor."""
    L, W, T = 42.0, 33.0, 1.6
    solid = _box(0, L, 0, W, 0, T)
    solid = solid + _box(-2.0, 9.0, 4.0, 18.0, T, 11.0)                                  # DC barrel jack, ASSUMPTION
    solid = solid + _box(-2.0, 7.0, 21.0, 31.0, T, 5.0)                                  # USB connector, ASSUMPTION
    solid = solid + _box(L - 9.0, L - 1.0, 6.0, 27.0, T, 6.0)                            # servo and UART headers, ASSUMPTION
    solid = solid + _box(14.0, 28.0, 8.0, 24.0, T, 4.0)                                  # driver chip and parts, ASSUMPTION
    holes = [(2.5, 2.5), (2.5 + 37.0, 2.5), (2.5, 2.5 + 28.0), (2.5 + 37.0, 2.5 + 28.0)]
    solid = _holes(solid, holes, 2.5, -0.5, T + 0.5)
    for (hx, hy) in holes:
        solid = solid + (_post(hx, hy, -standoff, 0, 5.0) - _post(hx, hy, -standoff - 0.5, 0.5, 2.5))
    return {"solid": solid, "mass": 0.021, "note": "outline, holes [Waveshare]; thickness and mass from one retailer (Digitec), the other lists 16 g; connectors ASSUMPTION"}



def csi_extender_board(standoff=3.0):
    """One board of the Arducam B0091 CSI-to-HDMI extension kit (Tx and Rx are alike), for the HQ camera. Outline and parts from the manufacturer's 3D drawing UC-392(B0091).STEP (read 2026-11-08;
    sizes only, the file is not copied here): PCB 25.2 x 27.83 x 1.67 mm with four Ø2 mounting holes (M2; datasheet drawing 21.0 x 12.5 apart, the STEP agrees), an HDMI receptacle 15 x 12 x 6.08 above the PCB top at one end (its
    mouth 0.45 mm past the edge), a 15-pin FPC connector 21.3 x 7.6 x 2.65 on the top face and the 3.5 mm audio jack, 12 x 6 x 4.87, on the underside near the far end (datasheet: an unused spare): DESOLDERED in this design (owner, 2026-11-08), so not modelled, and the receptacle's pins stand 0.53 below the PCB. Mass not found (ASSUMPTION 10 g).
    Here the PCB is x 0..27.83, y 0..25.2, the mouth at x = 0; `standoff` is the clearance under the board (3 mm, a stock M2 standoff); the kit ships four M2 screws and spacers."""
    L, W, T = 27.83, 25.2, 1.67
    solid = _box(0, L, 0, W, 0, T)
    solid = solid + _box(-0.45, 11.55, 5.0, 20.0, T, T + 6.08)                           # HDMI receptacle
    solid = solid + _box(16.07, 23.67, 1.85, 23.15, T, T + 2.65)                          # 15-pin FPC connector
    holes = [(13.2, 2.0), (13.2, 23.0), (25.7, 2.0), (25.7, 23.0)]                        # M2 holes: along the board from the mouth edge, across (datasheet 21.0 x 12.5)
    solid = _holes(solid, holes, 2.0, -0.5, T + 0.5)
    for (hx, hy) in holes:
        solid = solid + (_post(hx, hy, -standoff, 0, 4.5) - _post(hx, hy, -standoff - 0.5, 0.5, 2.0))
    return {"solid": solid, "mass": 0.010, "note": "outline, holes [Arducam datasheet Rev 1.0] and parts from the vendor STEP (derived); mass ASSUMPTION"}


def models():
    return {
        "mc33926": mc33926_carrier(), "d24v22fx": d24v22fx(), "pi_zero_2w": pi_zero_2w(),
        "fuse_block": fuse_block_4way(), "rocker_switch": rocker_switch(),
        "gnss_breakout": gnss_breakout(), "bus_servo_adapter": bus_servo_adapter(), "csi_extender": csi_extender_board(),
    }


if __name__ == "__main__":
    for k, m in models().items():
        bb = m["solid"].bounding_box()
        print(f"{k:14s} valid {m['solid'].is_valid}  x {bb.min.X:6.1f}..{bb.max.X:6.1f}  y {bb.min.Y:6.1f}..{bb.max.Y:6.1f}  z {bb.min.Z:6.1f}..{bb.max.Z:6.1f}  "
              f"size {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f}  {m['note']}")
