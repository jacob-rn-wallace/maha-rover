"""al-maha camera-link cable: how long the round cable (the CSI extender's RJ45 cord) has to be, from the CAD positions.

As in the flight-model photographs the harness is not routed through the mast: it hangs in a loose loop from the head's -y side down to the body (`headb.camera_link_cable`). The length is
the straight run from the Tx pod's jack to the deck gland over the Rx board's jack, plus slack for the tilt (+-90 degrees round the pod's swing) and the pan (+-160 degrees: the pod circles the
mast axis at 72 mm), plus strain reliefs. The kit's cord is 1 m long.

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
    xc = HB.ENC_X1 - HB.ENC_X / 2
    y1 = HB.CY - HB.ENC_Y / 2
    pod = (xc, y1 - 12.0, HB.AZ - 18.0)
    gland = (I.DECK_HOLE_X, I.DECK_HOLE_Y, B.DECK_TOP_Z)
    return [("Tx jack (pod floor) to the deck gland, straight", d(pod, gland)),
            ("deck gland down to the Rx board's jack under the deck", d(gland, rx_jack))]


if __name__ == "__main__":
    pl = I.placed_parts()
    bb = pl["CSI extender Rx board (Arducam kit)"].bounding_box()
    segs = route((I.DECK_HOLE_X, I.DECK_HOLE_Y, (bb.min.Z + bb.max.Z) / 2))
    tot = sum(L for _, L in segs)
    for n, L in segs:
        print(f"  {n:60s}{L:7.0f} mm")
    pan = 2 * 72.0                                          # the pod's end-to-end distance changes by up to the diameter of its circle round the mast axis
    tilt, relief = 100.0, 2 * 20.0
    print(f"  slack: pan {pan:.0f} + tilt {tilt:.0f} + strain relief {relief:.0f}; total {tot + pan + tilt + relief:.0f} mm; with a 10 percent sag and routing allowance {1.1 * (tot + pan + tilt + relief):.0f} mm (the kit's cord is 1000 mm)")
    cab = HB.camera_link_cable()
    print(f"  the modelled loop (a spline through six points) is {cab.volume / (math.pi * 2.75 ** 2):.0f} mm of cord")
