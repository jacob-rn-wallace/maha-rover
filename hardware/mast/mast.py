"""al-maha mast: replica mast, hinge, head and camera, deployed and stowed.

Replica design guided by the original's CAD figures (original-dimensions.md 3j) and
[S19] (stowed parallel to the top panel, under 120 mm above the top cover, spring
hinge to vertical) and [S12] (CAM-1 35 x 35 x 73 mm on a pan-tilt gimbal).
Dimensions tagged derived are from the figures; everything else is ASSUMPTION.

Mechanism (replica): a hinge pin on the deck at the mast's rear face, torsion springs
that swing the mast up, and a servo-pulled latch holding it down. Re-stowing is by
hand. Pan and tilt are two servos in the neck and the arm (parts not chosen).

Frame as in body.py. The mast is built deployed, then folded about the hinge axis
(along Y at x = HINGE_X, z = HINGE_Z).

Run:  .venv/bin/python hardware/mast/mast.py
Out:  hardware/mast/out/mast_deployed.step, mast_stowed.step
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
HINGE_X = TUBE_X - TUBE_W / 2      # hinge pin on the tube's rear face            ASSUMPTION
HINGE_Z = B.DECK_TOP_Z + 28.0      # pin about 30 above the deck (ring seen in [S18] side view,
                                   # by eye); 28 leaves 2 mm under the stowed limit of [S19]  ASSUMPTION
TOP_Z = B.TOP_Z                    # top of the head                              stated [S1]

# ---- Rotating parts, measured along the mast from the hinge ----------------
BASE_Z0, BASE_Z1 = HINGE_Z, 420.0  # base block, z 378 to 420                     derived [3j]
BASE_X, BASE_Y = 90.0, 90.0        # base block plan; 90 fore-aft measured; width ASSUMPTION
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

# ---- Fixed parts on the deck ------------------------------------------------
PED_X0, PED_X1 = HINGE_X - 15.0, HINGE_X + 55.0   # pedestal                      ASSUMPTION
PED_Y = 102.0                      # wider than the base block so the lugs stand outside it
LUG_Y, LUG_T = 48.0, 6.0
PIN_R = 4.0
LATCH = (23.0, 12.0, 25.0)         # micro servo size class                        ASSUMPTION

# ---- Replica masses, kg (ASSUMPTION) ---------------------------------------
MASSES = {"structure": 0.25, "pan and tilt servos": 0.12, "camera module": 0.04, "springs, latch, hardware": 0.04}
STOW_MAX = 120.0                   # stowed height above the top cover            stated [S19]


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


def rotating_parts():
    base = Pos(HINGE_X + BASE_X / 2, 0, (BASE_Z0 + BASE_Z1) / 2) * Box(BASE_X, BASE_Y, BASE_Z1 - BASE_Z0)
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


def fixed_parts():
    ped = Pos((PED_X0 + PED_X1) / 2, 0, (B.DECK_TOP_Z + HINGE_Z) / 2) * Box(PED_X1 - PED_X0, PED_Y, HINGE_Z - B.DECK_TOP_Z)
    lugs = [Pos(HINGE_X, sy * LUG_Y, HINGE_Z) * Box(24.0, LUG_T, 24.0) for sy in (1, -1)]
    pin = Pos(HINGE_X, 0, HINGE_Z) * Rot(90, 0, 0) * Cylinder(PIN_R, 2 * (LUG_Y + LUG_T / 2)) 
    latch = Pos(HINGE_X + 40, 0, B.DECK_TOP_Z + LATCH[2] / 2) * Box(*LATCH)
    return {"pedestal": ped, "lug+": lugs[0], "lug-": lugs[1], "pin": pin, "latch servo": latch}


def fold(shape, fold_deg):
    """Fold the mast rearward by fold_deg about the hinge axis (0 = deployed)."""
    if fold_deg == 0:
        return shape
    return Pos(HINGE_X, 0, HINGE_Z) * Rot(0, -fold_deg, 0) * Pos(-HINGE_X, 0, -HINGE_Z) * shape


def build(fold_deg=0.0):
    return {n: fold(p, fold_deg) for n, p in rotating_parts().items()}, fixed_parts()


def cg_and_torque():
    rot = rotating_parts()
    # mass split by part (ASSUMPTION): structure by volume, servos in neck and arm, camera, hardware at the hinge
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
    pts.append((MASSES["springs, latch, hardware"], HINGE_X, HINGE_Z))
    m = sum(p[0] for p in pts)
    zc = sum(p[0] * p[2] for p in pts) / m
    xc = sum(p[0] * p[1] for p in pts) / m
    h = zc - HINGE_Z                       # distance along the mast, hinge to centre of mass
    return m, xc, zc, h, m * 9.81 * h / 1000.0   # N.m about the hinge when the mast lies flat, Earth gravity (h in mm)


if __name__ == "__main__":
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    body_parts, _ = B.build_rover()
    deck = body_parts["body"]
    cells = Compound([v for k, v in body_parts.items() if k.startswith("cell")])
    hull = Compound([deck, cells])

    for label, ang in (("deployed", 0.0), ("stowed", 90.0)):
        rot, fx = build(ang)
        allr = Compound(list(rot.values()))
        bb = allr.bounding_box()
        print(f"[{label}] mast x {bb.min.X:.0f}..{bb.max.X:.0f}, z {bb.min.Z:.0f}..{bb.max.Z:.0f}, y {bb.min.Y:.0f}..{bb.max.Y:.0f}")
        if label == "deployed":
            print(f"   top z {bb.max.Z:.0f} (stated 700); camera axis z {CAM_AXIS_Z:.0f}; lens front x {CAM_FRONT_X:.1f} "
                  f"({B.WHEELBASE / 2:.1f} + 77.9)")
        else:
            print(f"   stowed height above the deck {bb.max.Z - B.DECK_TOP_Z:.1f} (limit {STOW_MAX:.0f}, stated [S19]); "
                  f"overall height {bb.max.Z:.0f}; rear end x {bb.min.X:.0f} (deck rear {B.BODY_X0 - B.DECK_LEN / 2:.1f})")
        print("   overlaps (mm3, want 0 except the pin, which sits in a hole in the base block):  mast vs body+cells {:.1f};  mast vs pedestal/lugs {:.1f};  mast vs pin {:.1f}".format(
            (allr & hull).volume,
            sum((allr & fx[k]).volume for k in ("pedestal", "lug+", "lug-")),
            (allr & fx["pin"]).volume))

    print("\nfold sweep, mast vs body+cells and pedestal (mm3):")
    for a in (0, 15, 30, 45, 60, 75, 90):
        rot, fx = build(float(a))
        allr = Compound(list(rot.values()))
        print(f"  {a:3d} deg: {(allr & hull).volume:8.1f}  {sum((allr & fx[k]).volume for k in ('pedestal','lug+','lug-')):8.1f}")

    m, xc, zc, h, tq = cg_and_torque()
    print(f"\nreplica mast (ASSUMPTION masses): {m:.2f} kg, centre of mass {h:.0f} mm along the mast from the hinge")
    print(f"torque about the hinge with the mast lying flat, Earth gravity: {tq:.2f} N.m "
          f"({tq / 6:.2f} N.m on the Moon)")

    # inner volume for servos: neck and arm
    neck_in = (TUBE_W - 2 * WALL, TUBE_W - 2 * WALL, NECK_Z1 - TUBE_Z1 - 2 * WALL)
    arm_in = (ARM_X - 2 * WALL, ARM_Y1 - ARM_Y0 - 2 * WALL, TOP_Z - 10 - NECK_Z1 - 2 * WALL)
    print(f"neck cavity {neck_in[0]:.0f} x {neck_in[1]:.0f} x {neck_in[2]:.0f}; servo {SERVO}; "
          f"arm cavity {arm_in[0]:.0f} x {arm_in[1]:.0f} x {arm_in[2]:.0f} (sizes only; the neck and arm are solid in this model)")

    rot, fx = build(0.0)
    export_step(Compound(list(rot.values()) + list(fx.values()), label="mast-deployed"), str(out / "mast_deployed.step"))
    rot, fx = build(90.0)
    export_step(Compound(list(rot.values()) + list(fx.values()), label="mast-stowed"), str(out / "mast_stowed.step"))
