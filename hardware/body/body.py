"""al-maha body: parametric envelope model (build123d), first pass.

Replica of the Rashid-1 body, wheels and deployed mast as a dimensional
envelope: solid parts, no internal structure, no panels, no suspension.
Millimetres. Rover frame: X forward, Y left, Z up, origin on the ground
(wheel contact line) under the midpoint between the axles, on the centreline.

Every value names its status from docs/original-dimensions.md (section in
brackets): stated / derived / (unverified). ASSUMPTION marks a modelling
choice with no source. Change it when a source appears.

Run:  .venv/bin/python hardware/body/body.py
Out:  hardware/body/out/rover.step, rover.stl, and a printed check table.
"""
import math
import sys
from pathlib import Path

from build123d import (
    Box, Compound, Cylinder, Plane, Polygon, Pos, Rot, extrude, export_step,
    export_stl,
)

sys.path.insert(0, str(Path(__file__).parent.parent / "wheel"))
from wheel import build_wheel  # noqa: E402

# ---- Body (section 3e, 3f) -----------------------------------------------
UNDERSIDE_Z = 124.0      # underside above ground                 derived [3f]
DECK_TOP_Z = 348.0       # deck top above ground                  derived [3f]
TOP_WIDTH = 164.0        # width just below the deck lip          derived [3f]
SIDEWALL_DEG = 10.0      # from vertical, panels at 80 degrees    stated [S20], 3f
SIDE_PLATE_LEN = 380.0   # body length (side plates)              derived [3e]
DECK_LEN = 401.0         # top plate length                       stated [S11]
DECK_T = 5.0             # top plate thickness                    ASSUMPTION
BODY_X0 = 0.0            # body centre along X vs the axle midpoint
                         #                                        (unverified; symmetric)

# ---- Wheels (section 2, 3e, 3f) ------------------------------------------
WHEELBASE = 273.0        # hub to hub; stated 270 rounded         derived [3e]
TRACK = 415.4            # wheel centre to centre                 derived [S8]
HUB_Z = 100.0            # = rim radius, ground at the rim line.
                         # [3e] reads 101. Grouser tips (115) then
                         # sit 15 mm below the line, as in the CAD frame it was
                         # measured in                           derived

# ---- Mast and cameras (section 4) ----------------------------------------
TOP_Z = 700.0            # top of the CAM-1 head, mast deployed   stated [S1]
MAST_X = WHEELBASE / 2 + 35.0   # mast centre ahead of the front axle (35,
                         # low confidence)                        derived [3e]
MAST_D = 20.0            # mast tube outer diameter               ASSUMPTION
HEAD_W, HEAD_L, HEAD_H = 50.0, 50.0, 60.0   # gimbal head block   ASSUMPTION
CAM_AXIS_Z = 650.8       # CAM-1 optical axis height              derived [S8]
CAM_X = WHEELBASE / 2 + 77.9    # CAM-1 forward of front axle     derived [S8]
CAM_Y = -28.0            # 28 right of centreline (Y is left)     derived [S8]
CAM_TUBE = (73.0, 35.0, 35.0)   # L x W x H optical tube          stated [S12]

TARGETS = {              # for the printed check
    "length over wheel rims": (470.0, "stated [S1]"),
    "width over wheels":      (505.0, "stated [S1]; CAD 497 [3f]"),
    "height, mast deployed":  (700.0, "stated [S1]"),
}


def body():
    h = DECK_TOP_Z - UNDERSIDE_Z
    bottom_w = TOP_WIDTH + 2 * h * math.tan(math.radians(SIDEWALL_DEG))
    pts = [(-bottom_w / 2, UNDERSIDE_Z), (bottom_w / 2, UNDERSIDE_Z),
           (TOP_WIDTH / 2, DECK_TOP_Z - DECK_T), (-TOP_WIDTH / 2, DECK_TOP_Z - DECK_T)]
    # Plane.YZ: local x = world Y, local y = world Z, normal +X
    wedge = extrude(Plane.YZ * Polygon(*pts, align=None),
                    amount=SIDE_PLATE_LEN / 2, both=True)
    deck = Pos(0, 0, DECK_TOP_Z - DECK_T / 2) * Box(DECK_LEN, TOP_WIDTH, DECK_T)
    return Pos(BODY_X0, 0, 0) * (wedge + deck), bottom_w


def wheels():
    w = Rot(90, 0, 0) * build_wheel()          # axle Z -> Y
    return [Pos(sx * WHEELBASE / 2, sy * TRACK / 2, HUB_Z) * w
            for sx in (1, -1) for sy in (1, -1)]


def mast():
    base = DECK_TOP_Z
    head_bot = TOP_Z - HEAD_H
    tube = Pos(MAST_X, 0, (base + head_bot) / 2) * Cylinder(MAST_D / 2, head_bot - base)
    head = Pos(MAST_X, 0, TOP_Z - HEAD_H / 2) * Box(HEAD_L, HEAD_W, HEAD_H)
    cam = Pos(CAM_X, CAM_Y, CAM_AXIS_Z) * Box(*CAM_TUBE)
    return tube + head + cam


def build_rover():
    b, bottom_w = body()
    parts = {"body": b, "mast": mast()}
    for i, w in enumerate(wheels()):
        parts[f"wheel{i}"] = w
    return parts, bottom_w


if __name__ == "__main__":
    parts, bottom_w = build_rover()
    rover = Compound(list(parts.values()), label="al-maha")
    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    export_step(rover, str(out / "rover.step"))
    export_stl(rover, str(out / "rover.stl"))

    bb = rover.bounding_box()
    wb = Compound([v for k, v in parts.items() if k.startswith("wheel")]).bounding_box()
    print(f"all parts valid : {all(p.is_valid for p in parts.values())}")
    print(f"body underside width {bottom_w:.0f}  (3a measured about 230, 3f top 164 + 10 deg)")
    print(f"{'check':26s}{'model':>9s}{'target':>9s}   source")
    rows = {
        "length over wheel rims": 2 * (WHEELBASE / 2) + 2 * 100.0,
        "width over wheels": wb.size.Y,
        "height, mast deployed": bb.max.Z,
    }
    for k, v in rows.items():
        t, s = TARGETS[k]
        print(f"{k:26s}{v:9.1f}{t:9.1f}   {s}")
    print(f"bbox over grouser tips: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f}")
    print(f"lowest point Z  : {bb.min.Z:.1f}  (grouser tips below the rim line)")
