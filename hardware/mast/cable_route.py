"""al-maha camera cable route: how long the cable from the camera to the Pi has to be, from the CAD positions.

The HQ camera ships with a 200 mm ribbon; Raspberry Pi only supports a 15 cm ribbon on CSI (forum reports: 1 m often works, 0.75 to 1.5 m shows pink bars sometimes). Route:
camera board connector, through the box wall's cable hole into the disk, out of the rim slot, a service loop round the rim for the +-90 degree tilt, down the -y slot of the extrusion,
through the spindle bore and the coupling disc's cable hole, past the servo, through the box floor and the deck, then under the deck to the Pi's CSI connector.

Run:  .venv/bin/python hardware/mast/cable_route.py
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
for d in ("body", "mast", "electronics", "suspension", "chassis"):
    sys.path.insert(0, str(HERE.parent / d))
import body as B  # noqa: E402
import headb as HB  # noqa: E402
import base as BS  # noqa: E402
import interior as I  # noqa: E402
import mast as M  # noqa: E402


def d(a, b):
    return math.dist(a, b)


def route(pi_csi):
    tx, cy, az = HB.TX, HB.CY, HB.AZ
    wall_y = cy + HB.ENC_Y / 2
    pts = [
        ("camera connector to the box wall hole", (tx - 10.0, cy, az - 11.0), (tx, wall_y - 1.0, az - 8.0)),
        ("through the wall and the disk to the rim slot", (tx, wall_y - 1.0, az - 8.0), (tx, wall_y + 8.0, az - 20.0)),
        ("rim slot to the extrusion top (-y slot)", (tx, wall_y + 8.0, az - 20.0), (tx, -20.0, M.TUBE_Z1)),
        ("down the extrusion slot", (tx, -20.0, M.TUBE_Z1), (tx, -20.0, M.TUBE_Z0)),
        ("flange to the spindle bore and out of its lower end", (tx, -20.0, M.TUBE_Z0), (tx, 0.0, M.TUBE_Z0 - 30.0)),
        ("coupling disc hole, past the servo, to the deck", (tx, -BS.CABLE_R, M.TUBE_Z0 - 34.0), (tx, -BS.CABLE_R, B.DECK_TOP_Z - B.DECK_T)),
        ("under the deck to the Pi's CSI connector", (tx, -BS.CABLE_R, B.DECK_TOP_Z - B.DECK_T), pi_csi),
    ]
    return [(n, d(a, b)) for n, a, b in pts]


if __name__ == "__main__":
    pl = I.placed_parts()
    bb = pl["controller (Pi Zero 2 W)"].bounding_box()
    for label, csi in (("Pi under the deck (now)", (bb.max.X, (bb.min.Y + bb.max.Y) / 2, bb.min.Z + 3.0)), ("Pi on the floor at 60, 35 (before)", (95.0, 35.0, I.floor_z() + 5.0))):
        segs = route(csi)
        print(label)
        tot = 0.0
        for n, L in segs:
            print(f"  {n:58s}{L:7.0f} mm")
            tot += L
        slack = 70.0 + 2 * 15.0
        print(f"  {'straight-line total':58s}{tot:7.0f} mm; + 70 tilt service loop + 2 x 15 strain relief = {tot + slack:.0f} mm; with 10 % routing allowance {1.1 * (tot + slack):.0f} mm")
