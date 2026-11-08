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


def route(rx_jack):
    """The round (RJ45) cable of the CSI extender, from the Tx pod to the Rx board: segment lengths in mm. Straight-line pieces from the CAD, plus allowances."""
    tx, cy, az = HB.TX, HB.CY, HB.AZ
    xc = HB.ENC_X1 - HB.ENC_X / 2
    y1 = cy - HB.ENC_Y / 2
    wall_y = cy + HB.ENC_Y / 2
    ring_x = tx - (BS.RING_ID / 2 + BS.RING_T)
    zt = B.DECK_TOP_Z + BS.PLATE_T if hasattr(BS, "PLATE_T") else B.DECK_TOP_Z + 3.0
    segs = [
        ("Tx jack down through the pod floor", (xc, y1 - 12.0, az - 14.0), (xc, y1 - 8.0, az - 33.0)),
        ("under the box to its +y side (clipped to the box)", (xc, y1 - 8.0, az - 33.0), (tx, wall_y + 6.0, az - 33.0)),
        ("up to the disk rim slot", (tx, wall_y + 6.0, az - 33.0), (tx, wall_y + 8.0, az - 20.0)),
        ("rim slot to the top of the extrusion (-y slot)", (tx, wall_y + 8.0, az - 20.0), (tx, -20.0, M.TUBE_Z1)),
        ("down the extrusion slot (plug fed in from the open top)", (tx, -20.0, M.TUBE_Z1), (tx, -20.0, M.TUBE_Z0)),
        ("flange opening to the chamber ring's exit (spiral allowance below)", (tx, -18.0, M.TUBE_Z0), (ring_x, 0.0, B.DECK_TOP_Z + BS.BOX_H - 8.0)),
        ("down the outside of the box to the deck, through a hole beside it", (ring_x, 0.0, B.DECK_TOP_Z + BS.BOX_H - 8.0), (I.DECK_HOLE_X, 0.0, B.DECK_TOP_Z - B.DECK_T)),
        ("under the deck to the Rx board's jack", (I.DECK_HOLE_X, 0.0, B.DECK_TOP_Z - B.DECK_T), rx_jack),
    ]
    return [(n, d(a, b)) for n, a, b in segs]


if __name__ == "__main__":
    pl = I.placed_parts()
    bb = pl["CSI extender Rx board (Arducam kit)"].bounding_box()
    segs = route((bb.max.X, (bb.min.Y + bb.max.Y) / 2, (bb.min.Z + bb.max.Z) / 2))
    tot = 0.0
    for n, L in segs:
        print(f"  {n:70s}{L:7.0f} mm")
        tot += L
    spiral, tilt, relief = 160.0, 70.0, 2 * 20.0
    print(f"  straight-line total {tot:.0f} mm; + chamber spiral {spiral:.0f} (one turn round the spindle for +-160 degrees) + tilt loop {tilt:.0f} (+-90 degrees round the rim) + 2 x 20 strain relief"
          f" = {tot + spiral + tilt + relief:.0f} mm; with a 10 percent routing allowance {1.1 * (tot + spiral + tilt + relief):.0f} mm (the kit's patch cable is 1000 mm)")
    print("  plug 13.5 x 12 mm: passages it must pass: Ø15 pod exit, the extrusion's T-slot channel (fed in from the top end), the 16 x 16 flange opening, the 18 x 14 ring notch, the Ø16 deck hole at x 112")
