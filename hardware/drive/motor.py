"""al-maha drive: motor, wheel support and hub clearance check.

Motor: Pololu 37D metal gearmotor without encoder, 131.25:1, item #4746
(candidate; any 37D without encoder shares the 36.8 mm gearbox, the 34.8 mm can
and the 6 x M3 / 31 mm face pattern, only the gearbox length differs).
Dimensions are from the vendor's 37D dimension drawing and datasheet rev 1.2
(2020): see docs/drive-spec.md. Bearings are standard ISO sizes, from memory:
verify against the supplier's catalogue.

Support concept ("option 1"): the motor shaft carries torque only. The wheel is
carried by two bearings that sit on the motor's own housing:
  inboard   6807 (35 x 47 x 7) on the motor can, outer race in a tube extension
            of the wheel hub
  outboard  6701 (12 x 18 x 4) on the 12 mm boss of the gearbox face, outer race
            in a drive flange that is bonded to the hub tube end and also
            drives the shaft through a D-bore collar
A clamp ring on the can, behind the inboard bearing, holds the motor to the
suspension arm (arm not modelled).

Wheel frame as in wheel.py: axle along Z, centred on the origin, wheel spans
z = +-40, hub tube z = +-20.

Run:  .venv/bin/python hardware/drive/motor.py
"""
import sys
from pathlib import Path

from build123d import Cylinder, Pos

sys.path.insert(0, str(Path(__file__).parent.parent / "wheel"))
import wheel as W  # noqa: E402

# ---- Motor: vendor drawing and datasheet ----------------------------------
GEARBOX_D, GEARBOX_L = 36.8, 26.5   # 131:1 gearbox            stated (vendor)
CAN_D, CAN_L = 34.8, 30.7           # motor can, behind gearbox   stated (vendor)
BOSS_D, BOSS_L = 12.0, 6.0          # boss on the gearbox face    stated (vendor)
SHAFT_D, SHAFT_L = 6.0, 16.0        # D-shaft past the boss       stated (vendor)
TERMINALS = 5.0                     # terminals past the can      stated (vendor)
MOTOR_MASS = 0.195                  # kg, upper end of 175-195 g  stated (vendor)

# ---- Placement -------------------------------------------------------------
SHAFT_TIP_Z = W.WIDTH / 2 - 3.0     # shaft tip 3 mm inside the wheel's outer face  ASSUMPTION
FACE_Z = SHAFT_TIP_Z - SHAFT_L - BOSS_L   # gearbox face (outboard end of the body)

# ---- Bearings (ISO sizes, from memory) ------------------------------------
B_IN = dict(id=35.0, od=47.0, w=7.0)       # 6807, on the can
B_OUT = dict(id=12.0, od=18.0, w=4.0)      # 6701, on the gearbox boss
RING_GAP = 0.2                              # radial gap between rings in the model

# ---- Support parts ---------------------------------------------------------
EXT_OD = 53.0            # hub tube extension outer diameter      ASSUMPTION
EXT_LEN = 15.0           # extension past the hub tube end         ASSUMPTION
FLANGE_T = 4.0           # outboard drive flange thickness         ASSUMPTION
COLLAR_OD = 16.0         # D-bore shaft collar outer diameter      ASSUMPTION
CLAMP_T, CLAMP_OD = 6.0, 44.0   # clamp ring on the can           ASSUMPTION
OVERLAP = 0.5


def ring(r_in, r_out, z0, z1):
    h = z1 - z0
    return Pos(0, 0, (z0 + z1) / 2) * (Cylinder(r_out, h) - Cylinder(r_in, h))


def disc(r, z0, z1):
    return Pos(0, 0, (z0 + z1) / 2) * Cylinder(r, z1 - z0)


def build_parts():
    """Return (fixed, rotating): the two assemblies that must not touch."""
    can_end = FACE_Z - GEARBOX_L - CAN_L
    body = (disc(GEARBOX_D / 2, FACE_Z - GEARBOX_L, FACE_Z)
            + disc(CAN_D / 2, can_end, FACE_Z - GEARBOX_L)
            + disc(BOSS_D / 2, FACE_Z, FACE_Z + BOSS_L))
    hub_end = -W.HUB_LEN / 2

    # inboard bearing, just inboard of the hub tube extension's far end
    ext_z0, ext_z1 = hub_end - EXT_LEN, hub_end + OVERLAP
    bi_z1 = ext_z0 + B_IN["w"] + 2.0
    bi_z0 = bi_z1 - B_IN["w"]
    bi_inner = ring(B_IN["id"] / 2, B_IN["od"] / 2 - 3.0 - RING_GAP, bi_z0, bi_z1)
    bi_outer = ring(B_IN["od"] / 2 - 3.0, B_IN["od"] / 2, bi_z0, bi_z1)
    # clamp ring behind the inboard bearing, on the can
    cl_z1 = bi_z0 - 1.0
    clamp = ring(CAN_D / 2, CLAMP_OD / 2, cl_z1 - CLAMP_T, cl_z1)
    # outboard bearing on the boss
    bo_z0 = FACE_Z + 0.5
    bo_z1 = bo_z0 + B_OUT["w"]
    bo_inner = ring(B_OUT["id"] / 2, B_OUT["id"] / 2 + 1.5 - RING_GAP, bo_z0, bo_z1)
    bo_outer = ring(B_OUT["od"] / 2 - 1.5, B_OUT["od"] / 2, bo_z0, bo_z1)
    # outboard drive flange (closes the hub end, holds the bearing, drives the shaft)
    fl_z0 = W.HUB_LEN / 2 - OVERLAP
    fl_z1 = fl_z0 + OVERLAP + FLANGE_T
    flange = ring(COLLAR_OD / 2, W.HUB_D / 2, fl_z0, fl_z1)   # fused to the collar below
    collar = ring(SHAFT_D / 2, COLLAR_OD / 2, FACE_Z + BOSS_L + 0.3, SHAFT_TIP_Z)
    shaft = disc(SHAFT_D / 2, FACE_Z + BOSS_L + 0.3, SHAFT_TIP_Z)
    ext = ring(B_IN["od"] / 2, EXT_OD / 2, ext_z0, ext_z1)

    fixed = {"motor": body, "clamp": clamp, "bearing_in_inner": bi_inner,
             "bearing_out_inner": bo_inner}
    rotating = {"shaft": shaft, "collar": collar, "flange": flange, "extension": ext,
                "bearing_in_outer": bi_outer, "bearing_out_outer": bo_outer}
    return fixed, rotating, dict(can_end=can_end, bi=(bi_z0, bi_z1), cl=(cl_z1 - CLAMP_T, cl_z1),
                                 bo=(bo_z0, bo_z1), fl=(fl_z0, fl_z1))


if __name__ == "__main__":
    fixed, rotating, z = build_parts()
    wheel = W.build_wheel()
    wh = -W.WIDTH / 2
    print(f"motor body z      : {z['can_end']:.1f} .. {FACE_Z:.1f}; terminals to {z['can_end'] - TERMINALS:.1f}")
    print(f"wheel inner face z: {wh:.0f}; the can ends {max(0.0, wh - z['can_end']):.1f} mm past it, "
          f"the terminals {max(0.0, wh - (z['can_end'] - TERMINALS)):.1f} mm past it")
    print(f"inboard bearing z : {z['bi'][0]:.1f} .. {z['bi'][1]:.1f}   clamp z: {z['cl'][0]:.1f} .. {z['cl'][1]:.1f}")
    print(f"outboard bearing z: {z['bo'][0]:.1f} .. {z['bo'][1]:.1f}   flange z: {z['fl'][0]:.1f} .. {z['fl'][1]:.1f}")
    print()
    print("overlaps (mm3, want 0 unless noted)")
    for n, p in fixed.items():
        print(f"  fixed {n:18s} with wheel : {(p & wheel).volume:8.1f}")
    for n, p in rotating.items():
        v = sum((p & f).volume for f in fixed.values())
        print(f"  rotating {n:18s} with fixed: {v:8.1f}")
