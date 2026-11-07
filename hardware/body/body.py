"""al-maha body: parametric envelope model (build123d), first pass.

Replica of the Rashid-1 body, wheels and mast as a dimensional
envelope: solid parts, thin solar cell plates, no internal structure, no
suspension. 
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
from build123d import Vector

sys.path.insert(0, str(Path(__file__).parent.parent / "wheel"))
from wheel import build_wheel  # noqa: E402

# ---- Body (section 3e, 3f) -----------------------------------------------
UNDERSIDE_Z = 124.0      # underside above ground                 derived [3f]
DECK_TOP_Z = 348.0       # deck top above ground                  derived [3f]
TOP_WIDTH = 164.0        # width just below the deck lip          derived [3f]
SIDEWALL_DEG = 10.0      # from vertical, panels at 80 degrees    stated [S20], 3f
SIDE_PLATE_LEN = 380.0   # body length (side plates)              derived [3e]
DECK_LEN = 401.0         # top plate length                       stated [S11]
DECK_T = 3.0             # top plate thickness (aluminium sheet, frame.py)   ASSUMPTION
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
MAST_X = WHEELBASE / 2 + 24.2   # mast tube centre ahead of the front axle; measured
                         # on the native side view (3j), refines 35 of [3e]  derived
MAST_D = 20.0            # old placeholder tube (used only by hardware/mass/budget.py)
HEAD_W, HEAD_L, HEAD_H = 50.0, 50.0, 60.0   # old placeholder head (same)
CAM_AXIS_Z = 660.0       # CAM-1 optical axis height              stated [S12]
CAM_X = WHEELBASE / 2 + 77.9 - 36.5   # CAM-1 tube centre: the 77.9 of [S8] matches the
                         # lens FRONT in the side view (3j), less half the 73 mm tube  derived
CAM_Y = -28.0            # 28 right of centreline (Y is left)     derived [S8]
CAM_TUBE = (73.0, 35.0, 35.0)   # L x W x H optical tube          stated [S12]

# ---- Solar cells (section 3g, 3h, 5) -------------------------------------
N_COLS, N_ROWS = 5, 3    # per side, all landscape               derived [3e, 3g]
CELL_W, CELL_H = 69.0, 39.0     # true size on the sloped face    derived [3g]
PITCH_U, PITCH_V = 71.6, 41.0   # along row / across rows         derived [3g]
CLIP = 6.5               # 45 degree clip, both bottom corners    derived [3g]
CELL_T = 1.0             # whole cell stack on the panel: insulating film, adhesive, cell,
                         # 200 um cover glass [S10]. Real cells need about this; the dummy
                         # cells use the same thickness                    ASSUMPTION
HOLE_D = 5.0             # wire hole through the side panel, one beside each end of every cell
                         # row, 17 mm outboard of the end cell's centre (solar provisions,
                         # docs/solar-spec.md)                            ASSUMPTION
HOLE_OFFSET = 17.0
FIELD_Z = (UNDERSIDE_Z + DECK_TOP_Z - DECK_T) / 2
                         # field centre height on the face. The
                         # position on the face is open [7.3]     ASSUMPTION

# ---- Stowed mast (section 3h) --------------------------------------------
MAST_STOWED_MAX = 120.0  # max stowed height above the top cover  stated [S19]
STOW_DIR = -1            # mast folds rearward (-X)               ASSUMPTION

TARGETS = {              # for the printed check
    "length over wheel rims": (470.0, "stated [S1]"),
    "width over wheels":      (505.0, "stated [S1]; CAD 497 [3f]"),
    "height, mast deployed":  (700.0, "stated [S1]"),
}


def body():
    h = DECK_TOP_Z - DECK_T - UNDERSIDE_Z    # the wedge ends under the deck plate
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


def cells():
    """Two 5 x 3 cell fields, one per sloped side face (thin plates)."""
    t = math.tan(math.radians(SIDEWALL_DEG))
    c, sn = math.cos(math.radians(SIDEWALL_DEG)), math.sin(math.radians(SIDEWALL_DEG))
    hw = lambda z: TOP_WIDTH / 2 + (DECK_TOP_Z - DECK_T - z) * t
    W, H, k = CELL_W / 2, CELL_H / 2, CLIP
    pts = [(-W + k, -H), (W - k, -H), (W, -H + k), (W, H), (-W, H), (-W, -H + k)]
    cell = extrude(Polygon(*pts, align=None), amount=CELL_T)
    out = []
    for sy in (1, -1):
        # plane y axis runs up the slope; z is the outward normal
        normal = Vector(0, sy * c, sn)
        xdir = Vector(-sy, 0, 0)
        for i in range(N_COLS):
            for j in range(N_ROWS):
                u, v = (i - (N_COLS - 1) / 2) * PITCH_U, (j - (N_ROWS - 1) / 2) * PITCH_V
                # origin: face point at the field centre, moved up-slope by v
                up = Vector(0, -sy * sn, c)
                o = Vector(BODY_X0, sy * hw(FIELD_Z), FIELD_Z) + up * v
                pl = Plane(origin=o, x_dir=xdir, z_dir=normal)
                out.append(pl * Pos(u, 0, 0) * cell)
    return out


def solar_holes(length=6.0, d=None):
    """Cylinders along the wall normal at the 12 wire-hole positions (6 per side), starting at the outer
    face and running `length` inward. Subtract from the shell to cut the holes."""
    d = HOLE_D if d is None else d
    t = math.tan(math.radians(SIDEWALL_DEG))
    c, sn = math.cos(math.radians(SIDEWALL_DEG)), math.sin(math.radians(SIDEWALL_DEG))
    hw = lambda z: TOP_WIDTH / 2 + (DECK_TOP_Z - DECK_T - z) * t
    out = []
    for sy in (1, -1):
        n = Vector(0, sy * c, sn)
        for j in range(N_ROWS):
            v = (j - (N_ROWS - 1) / 2) * PITCH_V
            for sx in (1, -1):
                u = sx * ((N_COLS - 1) / 2 * PITCH_U + HOLE_OFFSET)
                o = Vector(BODY_X0 + u, sy * hw(FIELD_Z), FIELD_Z) + Vector(0, -sy * sn, c) * v
                pl = Plane(origin=o, z_dir=n)
                out.append(pl * Pos(0, 0, -length / 2) * Cylinder(d / 2, length))
    return out


def mast():
    """The replica mast and camera from hardware/mast/mast.py (fixed upright).
    Imported here, not at the top, because mast.py imports this module."""
    sys.path.insert(0, str(Path(__file__).parent.parent / "mast"))
    import mast as mast_model
    return Compound(list(mast_model.parts().values()))


def build_rover():
    b, bottom_w = body()
    parts = {"body": b, "mast": mast()}
    for i, cl in enumerate(cells()):
        parts[f"cell{i}"] = cl
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

    print(f"cells: {sum(k.startswith('cell') for k in parts)} (target 30), "
          f"all valid {all(p.is_valid for k, p in parts.items() if k.startswith('cell'))}")

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
