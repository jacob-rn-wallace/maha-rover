"""al-maha mast: replica mast, head and camera, fixed upright.

Replica design guided by the original's CAD figures (original-dimensions.md 3j) and
[S12] (CAM-1 35 x 35 x 73 mm on a pan-tilt gimbal). Dimensions tagged derived are from
the figures; everything else is ASSUMPTION.

The mast is FIXED for now: the original stows flat under 120 mm [S19] and springs up on
landing, but the replica's stowing and deploying are deferred (decision 2026-11-07). A
base block bolts to the deck. Pan and tilt are two servos in the neck and the arm
(Feetech STS3215, docs/electronics-spec.md). The earlier hinged design, with a hinge pin,
pedestal and fold sweep, is in commit 20aec90.

Frame as in body.py.

Run:  .venv/bin/python hardware/mast/mast.py
Out:  hardware/mast/out/mast.step
"""
import math
import sys
from pathlib import Path

from build123d import Box, Compound, Cylinder, Pos, Rot, SlotOverall, extrude, Plane, export_step

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "body"))
import body as B  # noqa: E402

# ---- Positions (3j) ---------------------------------------------------------
TUBE_X = B.MAST_X                  # tube centre; 24.2 ahead of the front axle   derived [3j]
TUBE_W = 58.0                      # tube width, X and Y (about 60 x 59 measured)  derived [3j]
TOP_Z = B.TOP_Z                    # top of the head                              stated [S1]

# ---- Rotating parts, measured along the mast from the hinge ----------------
BASE_Z0, BASE_Z1 = B.DECK_TOP_Z, 420.0   # base block, deck to z 420                    derived [3j]
BASE_X, BASE_Y = 78.0, 90.0        # base block plan. About 90 fore-aft was measured (3j), which would
                                   # overhang the 401 mm deck front by 5 mm: 78 keeps it on the deck. Width ASSUMPTION
TUBE_Z0, TUBE_Z1 = 420.0, 577.0    # tube                                         derived [3j]
NECK_Z1 = 621.0                    # top of the neck / bottom of the head         derived [3j]
WALL = 3.0                         # tube and neck wall                           ASSUMPTION
ARM_Y0, ARM_Y1 = 25.0, 70.0        # C-arm bar, +Y side                           derived [3j], by eye
ARM_X = 50.0
HEAD_X, HEAD_Y, HEAD_Z = 60.0, 72.0, TOP_Z - NECK_Z1   # camera housing           derived [3j]
CAM_Y = B.CAM_Y                    # 28 right of the centreline                   derived [S8], confirmed [3j]
CAM_AXIS_Z = 660.0                 # CAM-1 optical axis height                    stated [S12]
CAM_FRONT_X = B.WHEELBASE / 2 + 77.9   # [S8] 77.9 ahead of the front axle: matches the lens front in [3j]
CAM_TUBE = B.CAM_TUBE              # 73 x 35 x 35                                 stated [S12]
TILT_R, TILT_LEN = 22.0, 40.0      # tilt motor housing between housing and arm   derived [3j], by eye
SERVO = (45.2, 24.7, 35.0)         # Feetech STS3215 (retailers' figures, docs/electronics-spec.md)
SLOTS = dict(cols=2, rows=4, w=10.0, l=24.0)    # lightening slots on the +-Y faces  ASSUMPTION

# ---- Replica masses, kg (ASSUMPTION) ---------------------------------------
MASSES = {"structure": 0.25, "pan and tilt servos": 0.11, "camera module": 0.04, "hardware": 0.02}   # servos: 2 x 55 g (vendor)


def hollow_box(x, y, z0, z1, cx, cy):
    outer = Pos(cx, cy, (z0 + z1) / 2) * Box(x, y, z1 - z0)
    inner = Pos(cx, cy, (z0 + z1) / 2) * Box(x - 2 * WALL, y - 2 * WALL, z1 - z0 - 2 * WALL)
    return outer - inner


def slot_cutters():
    """Oval slots through the two +-Y faces of the tube."""
    cuts = []
    z_lo, z_hi = TUBE_Z0 + 22, TUBE_Z1 - 22
    for r in range(SLOTS["rows"]):
        z = z_lo + (z_hi - z_lo) * r / (SLOTS["rows"] - 1)
        for c in range(SLOTS["cols"]):
            x = TUBE_X + (c - (SLOTS["cols"] - 1) / 2) * 24.0
            slot = extrude(Plane.XZ * SlotOverall(SLOTS["l"], SLOTS["w"], rotation=90), amount=TUBE_W + 4, both=True)
            cuts.append(Pos(x, 0, z) * slot)
    return cuts


def parts():
    # base block on the deck, centred on the tube (the figures put its centre at 24.5 mm
    # ahead of the front axle against 24.2 for the tube)
    base = Pos(TUBE_X, 0, (BASE_Z0 + BASE_Z1) / 2) * Box(BASE_X, BASE_Y, BASE_Z1 - BASE_Z0)
    tube = hollow_box(TUBE_W, TUBE_W, TUBE_Z0, TUBE_Z1, TUBE_X, 0)
    for c in slot_cutters():
        tube = tube - c
    # neck: tube top to the head, wide enough to carry the C-arm across
    neck_y0, neck_y1 = -TUBE_W / 2, ARM_Y1
    neck = Pos(TUBE_X, (neck_y0 + neck_y1) / 2, (TUBE_Z1 + NECK_Z1) / 2) * Box(TUBE_W, neck_y1 - neck_y0, NECK_Z1 - TUBE_Z1)
    arm = Pos(TUBE_X, (ARM_Y0 + ARM_Y1) / 2, (NECK_Z1 + TOP_Z - 10) / 2) * Box(ARM_X, ARM_Y1 - ARM_Y0, TOP_Z - 10 - NECK_Z1)
    head = Pos(TUBE_X, CAM_Y, (NECK_Z1 + TOP_Z) / 2) * Box(HEAD_X, HEAD_Y, HEAD_Z)
    tilt = Pos(TUBE_X, ARM_Y0 - TILT_LEN / 2 + 0.5, CAM_AXIS_Z) * Rot(90, 0, 0) * Cylinder(TILT_R, TILT_LEN)
    cam = Pos(CAM_FRONT_X - CAM_TUBE[0] / 2, CAM_Y, CAM_AXIS_Z) * Box(*CAM_TUBE)
    return {"base": base, "tube": tube, "neck": neck, "arm": arm, "head": head, "tilt": tilt, "camera": cam}


def cg_and_moment():
    rot = parts()
    # mass split by part (ASSUMPTION): structure by volume, servos in neck and arm, camera, hardware at the base
    vol = {n: p.volume for n, p in rot.items() if n in ("base", "tube", "neck", "arm", "head", "tilt")}
    vt = sum(vol.values())
    pts = []   # (mass, x, z)
    for n, v in vol.items():
        c = rot[n].center()
        pts.append((MASSES["structure"] * v / vt, c.X, c.Z))
    cn, ca = rot["neck"].center(), rot["arm"].center()
    pts += [(MASSES["pan and tilt servos"] / 2, cn.X, cn.Z), (MASSES["pan and tilt servos"] / 2, ca.X, ca.Z)]
    cc = rot["camera"].center()
    pts.append((MASSES["camera module"], cc.X, cc.Z))
    pts.append((MASSES["hardware"], TUBE_X, B.DECK_TOP_Z))
    m = sum(p[0] for p in pts)
    zc = sum(p[0] * p[2] for p in pts) / m
    xc = sum(p[0] * p[1] for p in pts) / m
    h = zc - B.DECK_TOP_Z                  # height of the centre of mass above the deck
    return m, xc, zc, h, m * 9.81 * h / 1000.0   # N.m about the base (h in mm), Earth gravity, sideways acceleration of 1 g


if __name__ == "__main__":
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    body_parts, _ = B.build_rover()
    deck = body_parts["body"]
    cells = Compound([v for k, v in body_parts.items() if k.startswith("cell")])
    hull = Compound([deck, cells])

    p = parts()
    allp = Compound(list(p.values()))
    bb = allp.bounding_box()
    print(f"mast x {bb.min.X:.0f}..{bb.max.X:.0f}, y {bb.min.Y:.0f}..{bb.max.Y:.0f}, z {bb.min.Z:.0f}..{bb.max.Z:.0f}")
    print(f"top z {bb.max.Z:.0f} (stated 700); camera axis z {CAM_AXIS_Z:.0f}; lens front x {CAM_FRONT_X:.1f} "
          f"({B.WHEELBASE / 2:.1f} + 77.9); body front end x {B.BODY_X0 + B.SIDE_PLATE_LEN / 2:.0f}")
    print(f"base block x {TUBE_X - BASE_X / 2:.0f}..{TUBE_X + BASE_X / 2:.0f}, y +-{BASE_Y / 2:.0f}; deck half-width {B.TOP_WIDTH / 2:.0f}, "
          f"deck x +-{B.DECK_LEN / 2:.0f}")
    print(f"overlap with body+cells (mm3, want 0): {(allp & hull).volume:.1f}")
    # the base block must sit on the deck
    deck_top = Pos(B.BODY_X0, 0, B.DECK_TOP_Z + 0.5) * Box(B.DECK_LEN, B.TOP_WIDTH, 1.0)   # 1 mm slab just above the deck
    print(f"base block footprint on the deck plate (mm2): {(p['base'] & deck_top).volume / 1.0:.0f} of {BASE_X * BASE_Y:.0f}")

    m, xc, zc, h, tq = cg_and_moment()
    print(f"\nreplica mast (ASSUMPTION masses): {m:.2f} kg, centre of mass {h:.0f} mm above the deck")
    print(f"moment at the base for a sideways acceleration of 1 g: {tq:.2f} N.m "
          f"(rover tilted 45 degrees: the same; a 20 degree slope gives {tq * math.sin(math.radians(20)):.2f} N.m)")

    neck_in = (TUBE_W - 2 * WALL, TUBE_W - 2 * WALL, NECK_Z1 - TUBE_Z1 - 2 * WALL)
    arm_in = (ARM_X - 2 * WALL, ARM_Y1 - ARM_Y0 - 2 * WALL, TOP_Z - 10 - NECK_Z1 - 2 * WALL)
    print(f"neck cavity {neck_in[0]:.0f} x {neck_in[1]:.0f} x {neck_in[2]:.0f}; servo {SERVO}; "
          f"arm cavity {arm_in[0]:.0f} x {arm_in[1]:.0f} x {arm_in[2]:.0f} (sizes only; the neck and arm are solid in this model)")

    export_step(Compound(list(p.values()), label="mast"), str(out / "mast.step"))
