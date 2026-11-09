"""al-maha camera-link cable: how long the round cable (the CSI extender's HDMI cord) has to be, from the CAD positions.

As in the flight-model photographs the harness is not routed through the mast: it hangs in a loose loop from the head's -y side down to the body (`headb.camera_link_cable`). The length is
the straight run from the camera box's gland hole (the Tx board is inside the box, 2026-11-08) to the deck gland over the Rx board's jack, plus slack for the tilt (+-90 degrees round the gland's swing) and the pan (+-160 degrees: the gland circles the
mast axis at about 61 mm), plus strain reliefs. The B0091 kit sells the two boards and ribbons only: the HDMI cord is the owner's choice (a thin one, 0.7 m or more).

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
    y1 = HB.CY - HB.ENC_Y / 2
    pod = (HB.GLAND_X, y1 - 3.0, HB.AZ)
    gland = (I.DECK_HOLE_X, I.DECK_HOLE_Y, B.DECK_TOP_Z)
    return [("box gland hole to the deck gland, straight", d(pod, gland)),
            ("deck gland down to the Rx board's HDMI jack under the deck", d(gland, rx_jack))]


if __name__ == "__main__":
    pl = I.placed_parts()
    bb = pl["CSI extender Rx board (Arducam kit)"].bounding_box()
    segs = route((I.DECK_HOLE_X, I.DECK_HOLE_Y, (bb.min.Z + bb.max.Z) / 2))
    tot = sum(L for _, L in segs)
    for n, L in segs:
        print(f"  {n:60s}{L:7.0f} mm")
    pan = 2 * math.hypot(HB.GLAND_X - HB.TX, HB.CY - HB.ENC_Y / 2 - 3.0)                  # the gland's end-to-end distance changes by up to the diameter of its circle round the mast axis
    tilt, relief = 100.0, 2 * 20.0
    print(f"  slack: pan {pan:.0f} + tilt {tilt:.0f} + strain relief {relief:.0f}; total {tot + pan + tilt + relief:.0f} mm; with a 10 percent sag and routing allowance {1.1 * (tot + pan + tilt + relief):.0f} mm (a cord of about 0.7 m or more: the kit has none)")
    cab = HB.camera_link_cable()
    print(f"  the modelled loop (a spline through six points) is {cab.volume / (math.pi * 2.75 ** 2):.0f} mm of cord")
