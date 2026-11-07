"""al-maha suspension: passive differential, side arms, and a clearance sweep.

Replica design, an INTERPRETATION of [S25] (passive differential gear in place of a
rocker, four wheels, no springs). The original's layout is not published, so
everything here is ASSUMPTION unless tagged.

Concept
  * One rigid arm per side carries the front and rear wheel (a walking beam).
  * Both arms pivot on one common axis along Y at x = 0, below the belly, and each
    is joined by a shaft to a side gear of a bevel differential on the centreline.
  * The differential housing is the carrier and is fixed to the body, so the body
    pitches by the AVERAGE of the two arm angles; body roll is taken by the rigid
    body, as in a rocker-bogie.
  * Each arm is a low beam inboard of the wheels, joined to each motor's clamp ring
    by a strap passing under the motor terminals.

Frame as in body.py: X forward, Y left, Z up from the ground, origin under the
axle midpoint. Wheel frame as in wheel.py / motor.py.

Run:  .venv/bin/python hardware/suspension/arms.py
Out:  hardware/suspension/out/rover_drive.step
"""
import math
import sys
from pathlib import Path

from build123d import Box, Compound, Cylinder, Pos, Rot, export_step

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "body"))
sys.path.insert(0, str(HERE.parent / "drive"))
sys.path.insert(0, str(HERE.parent / "wheel"))
import body as B   # noqa: E402
import motor as M  # noqa: E402
import wheel as W  # noqa: E402

PIVOT_Z = 76.0           # arm pivot axis height, along Y, x = 0   ASSUMPTION
BEAM_Y0, BEAM_Y1 = 150.0, 158.0   # beam inboard of the motor terminals (160.5 from the axis)  ASSUMPTION
BEAM_H = 10.0            # beam height                              ASSUMPTION
STRAP_W = 20.0           # strap width along X                      ASSUMPTION
STRAP_END = 172.5        # strap outer end (just short of the hub extension, 172.7)  ASSUMPTION
SHAFT_R = 4.0            # pivot shaft radius                       ASSUMPTION
DIFF_R, DIFF_LEN = 20.0, 44.0     # differential housing           ASSUMPTION
POST = 20.0              # carrier post cross-section               ASSUMPTION
OVERLAP = 0.5


def side(sy):
    """Everything that rides on one arm, for side sy = +1 (left) or -1 (right):
    arm parts, and the two wheels with their motors (fixed and rotating sets)."""
    hx = B.WHEELBASE / 2
    hub_y = sy * B.TRACK / 2
    y0, y1 = sy * BEAM_Y0, sy * BEAM_Y1
    beam = Pos(0, (y0 + y1) / 2, PIVOT_Z) * Box(B.WHEELBASE, BEAM_Y1 - BEAM_Y0, BEAM_H)
    # the beam spans the full wheelbase, so it passes under each strap's inner end
    straps = []
    for sx in (1, -1):
        ys = (sy * BEAM_Y0 + sy * STRAP_END) / 2
        straps.append(Pos(sx * hx, ys, PIVOT_Z) * Box(STRAP_W, STRAP_END - BEAM_Y0, BEAM_H))
    shaft_y0 = 1.0   # the two shafts stop 2 mm apart inside the housing, at the side gears
    shaft = Pos(0, sy * (shaft_y0 + BEAM_Y0) / 2, PIVOT_Z) * Rot(90, 0, 0) * Cylinder(SHAFT_R, BEAM_Y0 - shaft_y0 + OVERLAP)
    arm = {"beam": beam, "strap_f": straps[0], "strap_r": straps[1], "shaft": shaft}

    fixed_m, rot_m, _ = M.build_parts()
    wheel = W.build_wheel()
    place = lambda sx: Pos(sx * hx, hub_y, B.HUB_Z) * Rot(-sy * 90, 0, 0)
    wheels = {f"wheel{'F' if sx > 0 else 'R'}": place(sx) * wheel for sx in (1, -1)}
    motors = {f"motor_{k}{'F' if sx > 0 else 'R'}": place(sx) * v
              for sx in (1, -1) for k, v in fixed_m.items()}
    return arm, wheels, motors


def differential():
    housing = Pos(0, 0, PIVOT_Z) * Rot(90, 0, 0) * Cylinder(DIFF_R, DIFF_LEN)
    top = PIVOT_Z + DIFF_R
    post = Pos(0, 0, (top + B.UNDERSIDE_Z) / 2) * Box(POST, POST, B.UNDERSIDE_Z - top + OVERLAP)
    return {"diff_housing": housing, "diff_post": post}


def rotate_about_pivot(shape, deg):
    return Pos(0, 0, PIVOT_Z) * Rot(0, deg, 0) * Pos(0, 0, -PIVOT_Z) * shape


def overlap(a, b):
    return (a & b).volume


if __name__ == "__main__":
    body_parts, _ = B.build_rover()
    body_group = Compound([v for k, v in body_parts.items() if k == "body" or k.startswith("cell")])
    diff = differential()

    sides = {sy: side(sy) for sy in (1, -1)}
    print(f"pivot axis z = {PIVOT_Z:.0f}; belly z = {B.UNDERSIDE_Z:.0f}; "
          f"differential top z = {PIVOT_Z + DIFF_R:.0f}, bottom z = {PIVOT_Z - DIFF_R:.0f}")
    print(f"beam y {BEAM_Y0:.0f}..{BEAM_Y1:.0f}; body half-width at belly {body_group.bounding_box().max.Y:.0f}; "
          f"wheel inner face y {B.TRACK / 2 + W.WIDTH / 2 - W.WIDTH:.1f}")

    # Arm travel needed. Step of height h under one front wheel: that arm tilts asin(h/wheelbase)
    # from level, the other stays level, the body takes the average, so in the BODY frame
    # each arm turns half of that.
    h = 100.0
    th = math.degrees(math.asin(h / B.WHEELBASE))
    print(f"100 mm step under one front wheel: arm {th:.1f} deg from level, body pitch {th / 2:.1f} deg, "
          f"arm {th / 2:.1f} deg in the body frame; front hub moves {B.WHEELBASE / 2 * math.sin(math.radians(th / 2)):.0f} mm in the body frame")

    print("\nstatic overlaps at nominal (mm3, want 0 except bonded joints)")
    for sy, (arm, wheels, motors) in sides.items():
        tag = "L" if sy > 0 else "R"
        arm_all = Compound(list(arm.values()))
        for n, p in {**wheels, **motors}.items():
            if n.startswith("motor_clamp"):
                continue
            print(f"  {tag} arm vs {n:24s}: {overlap(arm_all, p):8.1f}")
        for n, p in arm.items():
            print(f"  {tag} {n:8s} vs body+cells        : {overlap(p, body_group):8.1f}")
    print(f"  diff housing vs body+cells : {overlap(diff['diff_housing'], body_group):8.1f}")
    print("  (the straps bond to the clamp rings on purpose: see below)")
    for sy, (arm, wheels, motors) in sides.items():
        for k in ("F", "R"):
            strap = arm["strap_f" if k == "F" else "strap_r"]
            print(f"  {'L' if sy > 0 else 'R'} strap_{k} vs clamp ring: {overlap(strap, motors['motor_clamp' + k]):.1f} (bonded joint, expect > 0)")

    print("\nsweep, body frame: left arm +phi, right arm -phi (rigid with their wheels and motors)")
    print(f"{'phi':>5s}  {'arm+wheels vs body/cells':>26s}  {'L vs R':>8s}")
    for phi in (-15, -10.7, -5, 0, 5, 10.7, 15):
        tot_body = 0.0
        groups = {}
        for sy, (arm, wheels, motors) in sides.items():
            parts = list(arm.values()) + list(wheels.values()) + list(motors.values())
            moved = [rotate_about_pivot(p, phi * sy) for p in parts]
            groups[sy] = Compound(moved)
            tot_body += overlap(groups[sy], body_group)
        lr = overlap(groups[1], groups[-1])
        print(f"{phi:5.1f}  {tot_body:26.1f}  {lr:8.1f}")

    out = HERE / "out"
    out.mkdir(exist_ok=True)
    allp = list(diff.values()) + [body_group]
    for sy, (arm, wheels, motors) in sides.items():
        allp += list(arm.values()) + list(wheels.values()) + list(motors.values())
    export_step(Compound(allp, label="al-maha-drive"), str(out / "rover_drive.step"))
