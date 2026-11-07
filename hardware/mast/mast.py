"""al-maha mast: replica mast, head and camera, fixed upright.

Replica design guided by the original's CAD figures (original-dimensions.md 3j) and
[S12] (CAM-1 35 x 35 x 73 mm on a pan-tilt gimbal). Dimensions tagged derived are from
the figures; everything else is ASSUMPTION.

The mast is FIXED for now: the original stows flat under 120 mm [S19] and springs up on
landing, but the replica's stowing and deploying are deferred (decision 2026-11-07). A
T-slot extrusion (40 x 40, decided 2026-11-07) stands on a base plate bolted to the deck and carries the printed
neck, arm and head on its end. Pan and tilt are two servos in the neck and the arm
(Feetech STS3215, docs/electronics-spec.md). The earlier hinged design, with a hinge pin,
pedestal and fold sweep, is in commit 20aec90.

Frame as in body.py.

Run:  .venv/bin/python hardware/mast/mast.py
Out:  hardware/mast/out/mast.step
"""
import math
import sys
from pathlib import Path

from build123d import Box, Compound, Cylinder, Pos, Rot, export_step

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "body"))
import body as B  # noqa: E402

# ---- Positions (3j) ---------------------------------------------------------
TUBE_X = B.MAST_X                  # tube centre; 24.2 ahead of the front axle   derived [3j]
TUBE_W = 58.0                      # width of the printed neck, X and Y (the original's tube measures about 60 x 59)  derived [3j]
EXT = 40.0                         # mast extrusion section, 40 x 40 (narrower than the original's 58 mm tube)  ASSUMPTION
EXT_KG_PER_M = 1.86                # Misumi HFS8-4040 catalogue (sources list 1.73 to 1.90 by variant; get it from the vendor)  stated (catalogue)
PLATE_XY, PLATE_T = 76.0, 6.0      # aluminium base plate on the deck, 4 M4 bolts at x +-19 / y +-30 from the tube centre  ASSUMPTION
TOP_Z = B.TOP_Z                    # top of the head                              stated [S1]

# ---- Rotating parts, measured along the mast from the hinge ----------------
BASE_Z0, BASE_Z1 = B.DECK_TOP_Z, B.DECK_TOP_Z + PLATE_T   # base plate on the deck
TUBE_Z0, TUBE_Z1 = BASE_Z1, 577.0  # extrusion from the plate to the neck; top at 577 as the original's tube   derived [3j]
NECK_Z1 = 621.0                    # top of the neck / bottom of the head         derived [3j]
WALL = 3.0                         # neck and arm wall (printed)                  ASSUMPTION
ARM_Y0, ARM_Y1 = 25.0, 70.0        # C-arm bar, +Y side                           derived [3j], by eye
ARM_X = 50.0
HEAD_X, HEAD_Y, HEAD_Z = 60.0, 72.0, TOP_Z - NECK_Z1   # camera housing           derived [3j]
CAM_Y = B.CAM_Y                    # 28 right of the centreline                   derived [S8], confirmed [3j]
CAM_AXIS_Z = 660.0                 # CAM-1 optical axis height                    stated [S12]
CAM_FRONT_X = B.WHEELBASE / 2 + 77.9   # [S8] 77.9 ahead of the front axle: matches the lens front in [3j]
CAM_TUBE = B.CAM_TUBE              # 73 x 35 x 35                                 stated [S12]
TILT_R, TILT_LEN = 22.0, 40.0      # tilt motor housing between housing and arm   derived [3j], by eye
SERVO = (45.2, 24.7, 35.0)         # Feetech STS3215 (retailers' figures, docs/electronics-spec.md)

# ---- Replica masses, kg (ASSUMPTION) ---------------------------------------
PRINTED = 0.12                     # neck, arm, head and tilt housing, printed (hollow, ASSUMPTION)
MASSES = {"printed parts": PRINTED, "pan and tilt servos": 0.11, "camera module": 0.04, "hardware": 0.02}   # servos: 2 x 55 g (vendor)


def parts():
    base = Pos(TUBE_X, 0, (BASE_Z0 + BASE_Z1) / 2) * Box(PLATE_XY, PLATE_XY, PLATE_T)
    tube = Pos(TUBE_X, 0, (TUBE_Z0 + TUBE_Z1) / 2) * Box(EXT, EXT, TUBE_Z1 - TUBE_Z0)   # slots ignored, as in frame.py
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
    pts = []   # (mass, x, z)
    c = lambda n: rot[n].center()
    pts.append((PLATE_XY * PLATE_XY * PLATE_T / 1e3 * 2.70 / 1000.0, c("base").X, c("base").Z))                 # aluminium plate
    pts.append(((TUBE_Z1 - TUBE_Z0) / 1000.0 * EXT_KG_PER_M, c("tube").X, c("tube").Z))                          # extrusion
    vol = {n: rot[n].volume for n in ("neck", "arm", "head", "tilt")}
    vt = sum(vol.values())
    for n, v in vol.items():
        pts.append((MASSES["printed parts"] * v / vt, c(n).X, c(n).Z))
    pts += [(MASSES["pan and tilt servos"] / 2, c("neck").X, c("neck").Z), (MASSES["pan and tilt servos"] / 2, c("arm").X, c("arm").Z)]
    pts.append((MASSES["camera module"], c("camera").X, c("camera").Z))
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
    print(f"base plate x {TUBE_X - PLATE_XY / 2:.0f}..{TUBE_X + PLATE_XY / 2:.0f}, y +-{PLATE_XY / 2:.0f}; extrusion {EXT:.0f} x {EXT:.0f}, z {TUBE_Z0:.0f}..{TUBE_Z1:.0f}; deck half-width {B.TOP_WIDTH / 2:.0f}, "
          f"deck x +-{B.DECK_LEN / 2:.0f}")
    print(f"overlap with body+cells (mm3, want 0): {(allp & hull).volume:.1f}")
    # the base plate must sit on the deck
    deck_top = Pos(B.BODY_X0, 0, B.DECK_TOP_Z + 0.5) * Box(B.DECK_LEN, B.TOP_WIDTH, 1.0)   # 1 mm slab just above the deck
    print(f"base plate footprint on the deck plate (mm2): {(p['base'] & deck_top).volume / 1.0:.0f} of {PLATE_XY * PLATE_XY:.0f}")

    m, xc, zc, h, tq = cg_and_moment()
    print(f"\nreplica mast (ASSUMPTION masses): {m:.2f} kg, centre of mass {h:.0f} mm above the deck")
    print(f"moment at the base for a sideways acceleration of 1 g: {tq:.2f} N.m "
          f"(rover tilted 45 degrees: the same; a 20 degree slope gives {tq * math.sin(math.radians(20)):.2f} N.m)")

    print(f"extrusion {(TUBE_Z1 - TUBE_Z0):.0f} mm x {EXT_KG_PER_M} kg/m = {(TUBE_Z1 - TUBE_Z0) / 1000 * EXT_KG_PER_M:.2f} kg; its slots carry the camera and servo cables")
    neck_in = (TUBE_W - 2 * WALL, TUBE_W - 2 * WALL, NECK_Z1 - TUBE_Z1 - 2 * WALL)
    arm_in = (ARM_X - 2 * WALL, ARM_Y1 - ARM_Y0 - 2 * WALL, TOP_Z - 10 - NECK_Z1 - 2 * WALL)
    print(f"neck cavity {neck_in[0]:.0f} x {neck_in[1]:.0f} x {neck_in[2]:.0f}; servo {SERVO}; "
          f"arm cavity {arm_in[0]:.0f} x {arm_in[1]:.0f} x {arm_in[2]:.0f} (sizes only; the neck and arm are solid in this model)")

    export_step(Compound(list(p.values()), label="mast"), str(out / "mast.step"))
