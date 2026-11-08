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

from build123d import Axis, Box, Compound, Cylinder, Pos, Rot, export_step

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "body"))
sys.path.insert(0, str(HERE))
import body as B  # noqa: E402
import head as H  # noqa: E402

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
ARM_Y0, ARM_Y1 = 25.0, 70.0        # C-arm bar, +Y side                           derived [3j], by eye
ARM_X = 50.0
HEAD_X, HEAD_Y, HEAD_Z = 60.0, 72.0, TOP_Z - NECK_Z1   # camera housing           derived [3j]
CAM_Y = B.CAM_Y                    # 28 right of the centreline                   derived [S8], confirmed [3j]
CAM_AXIS_Z = 660.0                 # CAM-1 optical axis height                    stated [S12]
CAM_FRONT_X = B.WHEELBASE / 2 + 77.9   # [S8] 77.9 ahead of the front axle: matches the lens front in [3j]
CAM_TUBE = B.CAM_TUBE              # 73 x 35 x 35                                 stated [S12]

# ---- Replica masses, kg (ASSUMPTION unless from a catalogue) -----------------------------
# printed shells: volume of the CAD shells x PETG density (head.py); servos 55 g each (retailers); camera module 4 g (ASSUMPTION); hardware 0.02
MASSES = {"pan and tilt servos": 2 * H.SERVO_MASS, "camera module": H.MODULE_MASS, "hardware": 0.02}


def parts():
    base = Pos(TUBE_X, 0, (BASE_Z0 + BASE_Z1) / 2) * Box(PLATE_XY, PLATE_XY, PLATE_T)
    tube = Pos(TUBE_X, 0, (TUBE_Z0 + TUBE_Z1) / 2) * Box(EXT, EXT, TUBE_Z1 - TUBE_Z0)   # slots ignored, as in frame.py
    hp, axes = H.build(TUBE_X, TUBE_Z1, NECK_Z1, TOP_Z, TUBE_W, ARM_X, ARM_Y0, ARM_Y1, HEAD_X, HEAD_Y, CAM_Y, CAM_AXIS_Z, CAM_FRONT_X, CAM_TUBE)
    return {"base": base, "tube": tube, **hp}


def cg_and_moment():
    rot = parts()
    pts = []   # (mass, x, z)
    c = lambda n: rot[n].center()
    pts.append((PLATE_XY * PLATE_XY * PLATE_T / 1e3 * 2.70 / 1000.0, c("base").X, c("base").Z))                 # aluminium plate
    pts.append(((TUBE_Z1 - TUBE_Z0) / 1000.0 * EXT_KG_PER_M, c("tube").X, c("tube").Z))                          # extrusion
    for n in ("neck", "arm", "head", "camera"):                                                                    # printed shells, by volume
        pts.append((H.shell_mass(rot[n]), c(n).X, c(n).Z))
    for n in ("pan servo", "tilt servo"):
        pts.append((H.SERVO_MASS, c(n).X, c(n).Z))
    pts.append((H.MODULE_MASS, c("camera module").X, c("camera module").Z))
    pts.append((MASSES["hardware"], TUBE_X, B.DECK_TOP_Z))
    m = sum(p[0] for p in pts)
    zc = sum(p[0] * p[2] for p in pts) / m
    xc = sum(p[0] * p[1] for p in pts) / m
    h = zc - B.DECK_TOP_Z                  # height of the centre of mass above the deck
    return m, xc, zc, h, m * 9.81 * h / 1000.0   # N.m about the base (h in mm), Earth gravity, sideways acceleration of 1 g


def _vol(a, b):
    r = a & b
    return 0.0 if r is None else r.volume


def head_checks(p):
    """Fit and sweep checks for the head: servos and camera inside their shells, no clashes, pan and tilt sweeps."""
    ax_p = Axis((TUBE_X, 0, 0), (0, 0, 1))
    ax_t = Axis((TUBE_X, 0, CAM_AXIS_Z), (0, 1, 0))
    print("\nhead: parts inside their shells and clear of each other (mm3, want 0)")
    inner = lambda x0, x1, y0, y1, z0, z1: H._box(x0, x1, y0, y1, z0, z1)
    w = H.WALL
    neck_in = inner(TUBE_X - TUBE_W / 2 + w, TUBE_X + TUBE_W / 2 - w, -TUBE_W / 2 + w, ARM_Y1 - w, TUBE_Z1 + w, NECK_Z1 - w)
    arm_in = inner(TUBE_X - ARM_X / 2 + w, TUBE_X + ARM_X / 2 - w, ARM_Y0 + w, ARM_Y1 - w, NECK_Z1 + w, TOP_Z - 10 - w)
    tube_in = inner(CAM_FRONT_X - CAM_TUBE[0] + w, CAM_FRONT_X - w, CAM_Y - CAM_TUBE[1] / 2 + w, CAM_Y + CAM_TUBE[1] / 2 - w,
                    CAM_AXIS_Z - CAM_TUBE[2] / 2 + w, CAM_AXIS_Z + CAM_TUBE[2] / 2 - w)
    for n, cav in (("pan servo", neck_in), ("tilt servo", arm_in), ("camera module", tube_in)):
        out = p[n].volume - _vol(p[n], cav)
        print(f"  {n:14s} outside its cavity {out:8.1f}")
    for a, b in (("pan servo", "neck"), ("tilt servo", "arm"), ("tilt servo", "head"), ("camera module", "camera"), ("camera", "head"), ("pan servo", "arm"), ("tilt servo", "camera")):
        v = _vol(p[a], p[b])
        print(f"  {a:14s} vs {b:12s}: {v:8.1f}")
    sv = p["pan servo"].bounding_box()
    print(f"  pan servo z {sv.min.Z:.1f}..{sv.max.Z:.1f} in a neck cavity z {TUBE_Z1 + w:.0f}..{NECK_Z1 - w:.0f}: {NECK_Z1 - w - sv.max.Z:.1f} mm spare above the horn")
    tv = p["tilt servo"].bounding_box()
    print(f"  tilt servo y {tv.min.Y:.1f}..{tv.max.Y:.1f} in an arm cavity y {ARM_Y0 + w:.0f}..{ARM_Y1 - w:.0f}; x {tv.min.X:.1f}..{tv.max.X:.1f} in {TUBE_X - ARM_X / 2 + w:.0f}..{TUBE_X + ARM_X / 2 - w:.0f}; "
          f"z {tv.min.Z:.1f}..{tv.max.Z:.1f} in {NECK_Z1 + w:.0f}..{TOP_Z - 10 - w:.0f}")
    # pan sweep: arm, head, camera tube, module, tilt servo turn about the mast axis
    static = [p["neck"], p["tube"], p["base"], p["pan servo"]]
    moving = Compound([p[n] for n in ("arm", "head", "camera", "camera module", "tilt servo")])
    worst = 0.0
    for deg in range(-180, 181, 30):
        m_ = moving.rotate(ax_p, deg)
        v = sum(_vol(m_, s_) for s_ in static)
        worst = max(worst, v)
    print(f"\npan sweep, -180 to +180 degrees in 30 degree steps: overlap of the arm and head with the neck, extrusion, base plate and pan servo: worst {worst:.1f} mm3")
    # tilt sweep: the camera tube and its module turn about the tilt axis
    tilting = Compound([p["camera"], p["camera module"]])
    print("tilt sweep: camera tube and module about the tilt axis (x %.1f, z %.0f), overlap with the head shell, neck, arm and tilt servo (mm3):" % (TUBE_X, CAM_AXIS_Z))
    first_bad = {1: None, -1: None}
    for sgn in (1, -1):
        for deg in range(0, 76, 5):
            t_ = tilting.rotate(ax_t, sgn * deg)
            v = _vol(t_, p["head"]) + _vol(t_, p["neck"]) + _vol(t_, p["arm"]) + _vol(t_, p["tilt servo"])
            if v > 1.0 and first_bad[sgn] is None:
                first_bad[sgn] = deg
    for sgn, nm in ((1, "positive"), (-1, "negative")):
        print(f"  {nm} tilt: first contact at {first_bad[sgn] if first_bad[sgn] is not None else 'none up to 75'} degrees (the original tilts plus or minus 75 degrees [S19])")
    # alternative: the whole camera head (housing, tube, module) tilts as one unit about the same axis
    unit = Compound([p["head"], p["camera"], p["camera module"]])
    first_unit = {1: None, -1: None}
    for sgn in (1, -1):
        for deg in range(0, 76, 5):
            u_ = unit.rotate(ax_t, sgn * deg)
            v = _vol(u_, p["neck"]) + _vol(u_, p["arm"]) + _vol(u_, p["tilt servo"]) + _vol(u_, p["tube"])
            if v > 1.0 and first_unit[sgn] is None:
                first_unit[sgn] = deg
    for sgn, nm in ((1, "positive"), (-1, "negative")):
        print(f"  whole head tilting as one unit, {nm}: first contact at {first_unit[sgn] if first_unit[sgn] is not None else 'none up to 75'} degrees (with the neck, arm, tilt servo or extrusion)")
    ub = unit.bounding_box()
    print(f"  the head unit spans z {ub.min.Z:.0f} to {ub.max.Z:.0f}; its lowest corner at 75 degrees would reach about z {CAM_AXIS_Z - math.hypot(HEAD_X / 2, (TOP_Z - NECK_Z1) / 2):.0f} against the neck top at {NECK_Z1:.0f}")


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
    head_checks(p)

    export_step(Compound(list(p.values()), label="mast"), str(out / "mast.step"))
