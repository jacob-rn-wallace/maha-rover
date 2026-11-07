"""al-maha suspension: passive differential, side link plates, and a clearance sweep.

Replica design, an INTERPRETATION of [S25] (passive differential gear in place of a
rocker, four wheels, no springs) guided by the CAD figures (original-dimensions.md
section 3i): one plate per side joining the front and rear hubs, with a pivot boss at
the wheelbase midpoint about 147 mm above the ground line and a short stub into the
body wall at that height. The plate shape, thicknesses and everything inside the body
are ASSUMPTION.

Concept
  * One rigid plate per side carries the front and rear wheel (a walking beam).
  * The plates pivot on a common axis along Y at x = 0, z = 147, and each is joined by a
    shaft through the body wall to a side gear of a bevel differential INSIDE the body.
  * The differential housing (the carrier) is fixed to the body, so the body pitches by
    the AVERAGE of the two plate angles. Body roll is taken by the rigid body.
  * Each motor hangs on its plate through a sleeve joining the plate to the motor's
    clamp ring; the sleeve covers the motor terminals.

Frame as in body.py: X forward, Y left, Z up from the ground, origin under the axle
midpoint. Wheel frame as in wheel.py / motor.py. The body model is a solid envelope,
so the shaft appears to overlap it where it would pass through a hole.

Run:  .venv/bin/python hardware/suspension/arms.py
Out:  hardware/suspension/out/rover_drive.step
"""
import math
import sys
from pathlib import Path

from build123d import (
    Box, Compound, Cylinder, Plane, Polygon, Pos, Rot, extrude, export_step,
)

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "body"))
sys.path.insert(0, str(HERE.parent / "drive"))
sys.path.insert(0, str(HERE.parent / "wheel"))
import body as B   # noqa: E402
import motor as M  # noqa: E402
import wheel as W  # noqa: E402

PIVOT_Z = B.HUB_Z + 45.7  # boss 45.7 above the hub centres        derived [3i]
PLATE_Y0, PLATE_T = 133.0, 8.0   # plate inner face from the centreline, thickness  ASSUMPTION
                                 # (front view: plate about 30 mm inboard of the wheel's inner face)
PLATE_BOTTOM = B.HUB_Z + 5.0     # lower edge about 5 above the hub centre  derived [3i]
PLATE_TOP_MID, PLATE_TOP_END = 178.0, 128.0   # upper outline           ASSUMPTION
PAD_HALF, PAD_BOTTOM = 22.0, B.HUB_Z - 22.0   # tab behind each sleeve  ASSUMPTION
PLATE_END = B.WHEELBASE / 2 + 22.0            # plate ends past the hubs ASSUMPTION
BOSS_D, BOSS_T = 48.0, 12.0      # pivot boss on the outer face: diameter derived [3i], by eye; 12 thick (was 6) so the 12 mm shaft is bonded in 20 mm of plate and boss   ASSUMPTION
SLEEVE_OD, SLEEVE_ID = 44.0, 38.0   # sleeve from plate to clamp ring   ASSUMPTION
SHAFT_R = 6.0            # pivot shaft radius: a 12 mm OD, 8 mm ID steel tube from the link plate to the differential housing wall, so it can carry the
                         # bending of the wheel loads (rail_check.py: the earlier 8 mm tube would see about 680 MPa at 3 g)   ASSUMPTION
SHAFT_ID = 8.0           # the drive motors' wires run through it, and leave axially at the link plate end   ASSUMPTION
STUB_R, STUB_ID = 4.0, 5.0   # inside the housing the tube is turned down to 8 mm OD, 5 mm ID to suit the 8 mm bore of the stock 1.5 module mitre gears   ASSUMPTION
STEP_Y = 22.0            # the shoulder: the housing wall's inner face. The 12 mm section runs out from here
BOSS_Y0, BOSS_Y1, BOSS_R = 25.0, 34.0, 11.0   # boss on the outside of each housing wall: with the 3 mm wall it carries a 12 mm long bushing (the shaft's second support)   ASSUMPTION
STUB_INSERT = 15.0       # the 8 / 5 stub is a separate tube bonded 15 mm into the 12 / 8 tube (an 8 mm bore cannot be turned down to an 8 mm OD)   ASSUMPTION
LUG_X0, LUG_X1, LUG_Y, LUG_W, LUG_T = 24.0, 34.0, 14.0, 14.0, 2.0   # four lugs on the housing top, bolted to the differential cross rails (x = +-28)   ASSUMPTION
CROSS_D = 3.0            # radial wire holes in the tube: one inside the body, one in the gap outside the wall
CROSS_Y_IN = 20.0          # one radial wire hole in the 8 mm stub, inside the housing between the gear hub (ends y 18) and the wall (y 22). There is no hole
                         # out in the bending zone: the wires leave axially at the link plate   ASSUMPTION
DIFF_X, DIFF_Y, DIFF_Z = 48.0, 50.0, 36.0   # differential housing, inside the body: x across the spider gears' pin, y along the shafts, z height.
                                # 36 mm tall keeps it clear of the 2 mm floor panel (bottom z 127.7 against the floor top 126) and
                                # of the cross rails (top z 163.7 against 165): see differential.py   ASSUMPTION
OVERLAP = 0.5


def ring(y0, y1, r_out, r_in):
    """Tube along Y between y0 and y1 (either order)."""
    h = abs(y1 - y0)
    return Pos(0, (y0 + y1) / 2, 0) * Rot(90, 0, 0) * (Cylinder(r_out, h) - Cylinder(r_in, h))


def plate_outline():
    e, hx = PLATE_END, B.WHEELBASE / 2
    pb, pad = PLATE_BOTTOM, PAD_BOTTOM
    x_in = hx - PAD_HALF
    return [(-e, pad), (-x_in, pad), (-x_in, pb), (x_in, pb), (x_in, pad), (e, pad),
            (e, PLATE_TOP_END), (70.0, PLATE_TOP_MID), (-70.0, PLATE_TOP_MID), (-e, PLATE_TOP_END)]


def side(sy):
    """Everything that rides on one plate, for side sy = +1 (left) or -1 (right):
    plate parts, and the two wheels with their fixed motor parts."""
    hx = B.WHEELBASE / 2
    hub_y = sy * B.TRACK / 2
    y_in, y_out = PLATE_Y0, PLATE_Y0 + PLATE_T
    # plate: sketch in the XZ plane, extruded along Y
    sk = Plane.XZ * Polygon(*plate_outline(), align=None)       # Plane.XZ normal is -Y
    # Plane.XZ extrudes toward -Y from y = 0, so shift: sy=+1 occupies y_in..y_out, sy=-1 -y_out..-y_in
    plate = Pos(0, (y_out if sy > 0 else -y_in), 0) * extrude(sk, amount=PLATE_T)
    boss = Pos(0, sy * (y_out + BOSS_T / 2 - OVERLAP / 2), PIVOT_Z) * Rot(90, 0, 0) * Cylinder(BOSS_D / 2, BOSS_T + OVERLAP)
    shaft_y0 = 1.0   # the two shafts stop 2 mm apart inside the housing, at the side gears
    y_end = y_out + BOSS_T                               # the tube ends flush with the boss tip; the motor wires leave there
    stub_y1 = STEP_Y + STUB_INSERT
    stub = Pos(0, sy * (shaft_y0 + stub_y1) / 2, PIVOT_Z) * Rot(90, 0, 0) * (Cylinder(STUB_R, stub_y1 - shaft_y0) - Cylinder(STUB_ID / 2, stub_y1 - shaft_y0 + 2.0))
    longpart = Pos(0, sy * (STEP_Y + y_end) / 2, PIVOT_Z) * Rot(90, 0, 0) * (Cylinder(SHAFT_R, y_end - STEP_Y) - Cylinder(SHAFT_ID / 2, y_end - STEP_Y + 2.0))
    shaft = stub + longpart
    sleeves = {}
    fixed_m, rot_m, z = M.build_parts()
    clamp_face = abs(hub_y) - (-z["cl"][0])        # y of the clamp ring's inner face (z['cl'][0] is negative)
    bore = Pos(0, sy * (y_in + y_end) / 2, PIVOT_Z) * Rot(90, 0, 0) * Cylinder(SHAFT_R, y_end - y_in + 2.0)   # the shaft is bonded in a 12 mm bore through plate and boss
    plate, boss = plate - bore, boss - bore
    for sx in (1, -1):
        y0, y1 = sy * y_out, sy * (clamp_face + OVERLAP)
        sleeves["F" if sx > 0 else "R"] = Pos(sx * hx, 0, B.HUB_Z) * ring(y0 - sy * OVERLAP, y1, SLEEVE_OD / 2, SLEEVE_ID / 2)
    shaft = shaft - Pos(0, sy * CROSS_Y_IN, PIVOT_Z) * Cylinder(CROSS_D / 2, 2 * STUB_R + 2.0)
    arm = {"plate": plate, "boss": boss, "shaft": shaft,
           "sleeveF": sleeves["F"], "sleeveR": sleeves["R"]}

    wheel = W.build_wheel()
    place = lambda sx: Pos(sx * hx, hub_y, B.HUB_Z) * Rot(-sy * 90, 0, 0)
    wheels = {f"wheel{'F' if sx > 0 else 'R'}": place(sx) * wheel for sx in (1, -1)}
    motors = {f"motor_{k}{'F' if sx > 0 else 'R'}": place(sx) * v
              for sx in (1, -1) for k, v in fixed_m.items()}
    return arm, wheels, motors


def differential():
    out = {"diff_housing": Pos(0, 0, PIVOT_Z) * Box(DIFF_X, DIFF_Y, DIFF_Z)}
    for sy in (1, -1):
        out["diff_boss " + ("L" if sy > 0 else "R")] = Pos(0, sy * (BOSS_Y0 + BOSS_Y1) / 2, PIVOT_Z) * Rot(90, 0, 0) * Cylinder(BOSS_R, BOSS_Y1 - BOSS_Y0)
    for sx in (1, -1):
        for sy in (1, -1):
            out[f"diff_lug {'F' if sx > 0 else 'R'}{'L' if sy > 0 else 'R'}"] = Pos(sx * (LUG_X0 + LUG_X1) / 2, sy * LUG_Y, PIVOT_Z + DIFF_Z / 2 - LUG_T / 2) * Box(LUG_X1 - LUG_X0, LUG_W, LUG_T)
    return out


def rotate_about_pivot(shape, deg):
    return Pos(0, 0, PIVOT_Z) * Rot(0, deg, 0) * Pos(0, 0, -PIVOT_Z) * shape


def overlap(a, b):
    return (a & b).volume


if __name__ == "__main__":
    body_parts, _ = B.build_rover()
    body_only = body_parts["body"]
    cells = Compound([v for k, v in body_parts.items() if k.startswith("cell")])
    body_group = Compound([body_only, cells])
    diff = differential()

    sides = {sy: side(sy) for sy in (1, -1)}
    half_w_pivot = B.TOP_WIDTH / 2 + (B.DECK_TOP_Z - B.DECK_T - PIVOT_Z) * math.tan(math.radians(B.SIDEWALL_DEG))
    print(f"pivot axis z = {PIVOT_Z:.1f} (hub {B.HUB_Z:.0f} + 45.7, [3i]); belly z = {B.UNDERSIDE_Z:.0f}; "
          f"cell field starts z = {B.FIELD_Z - (B.N_ROWS * B.PITCH_V) / 2:.0f}")
    print(f"body half-width at the pivot {half_w_pivot:.1f}; plate inner face y {PLATE_Y0:.0f} "
          f"(gap {PLATE_Y0 - half_w_pivot:.0f}); wheel inner face y {B.TRACK / 2 + W.WIDTH / 2 - W.WIDTH:.1f}")
    inside = overlap(diff["diff_housing"], body_only) / diff["diff_housing"].volume
    print(f"differential housing inside the body envelope: {inside * 100:.0f} % of its volume "
          f"(z {PIVOT_Z - DIFF_Z / 2:.0f}..{PIVOT_Z + DIFF_Z / 2:.0f}; belly {B.UNDERSIDE_Z:.0f})")

    h = 100.0
    th = math.degrees(math.asin(h / B.WHEELBASE))
    print(f"100 mm step under one front wheel: plate {th:.1f} deg from level, body pitch {th / 2:.1f} deg, "
          f"plate {th / 2:.1f} deg in the body frame; front hub moves "
          f"{B.WHEELBASE / 2 * math.sin(math.radians(th / 2)):.0f} mm in the body frame")

    print("\nstatic overlaps at nominal (mm3, want 0; the shaft passes through the body wall by design)")
    for sy, (arm, wheels, motors) in sides.items():
        tag = "L" if sy > 0 else "R"
        arm_all = Compound([v for k, v in arm.items()])
        for n, p in {**wheels, **motors}.items():
            v = overlap(arm_all, p)
            if v > 0.01:
                print(f"  {tag} arm vs {n:24s}: {v:8.1f}")
        for n, p in arm.items():
            v = overlap(p, body_group)
            if v > 0.01:
                print(f"  {tag} {n:8s} vs body+cells        : {v:8.1f}{'  (shaft through the wall)' if n == 'shaft' else '  <-- unexpected'}")
    print("  (anything not listed is 0)")
    for sy, (arm, wheels, motors) in sides.items():
        for k in ("F", "R"):
            sl = arm["sleeve" + k]
            print(f"  {'L' if sy > 0 else 'R'} sleeve_{k} vs clamp ring: {overlap(sl, motors['motor_clamp' + k]):.1f} (bonded joint, expect > 0)")

    print("\nsweep, body frame: left plate +phi, right plate -phi, each with its wheels and motors")
    print(f"{'phi':>5s}  {'plate parts vs body+cells':>26s}  {'wheels,motors vs body':>22s}  {'L vs R':>7s}  {'min gap plate-body':>18s}")
    for phi in (-15, -10.7, -5, 0, 5, 10.7, 15):
        t_plate = t_wm = 0.0
        groups = {}
        gap = float("inf")
        for sy, (arm, wheels, motors) in sides.items():
            plate_parts = [arm["plate"], arm["boss"], arm["sleeveF"], arm["sleeveR"]]
            wm = list(wheels.values()) + list(motors.values())
            mp = Compound([rotate_about_pivot(p, phi * sy) for p in plate_parts])
            mw = Compound([rotate_about_pivot(p, phi * sy) for p in wm])
            t_plate += overlap(mp, body_group)
            t_wm += overlap(mw, body_group)
            groups[sy] = Compound([mp, mw])
            try:
                gap = min(gap, mp.distance_to(body_group))
            except Exception:
                gap = float("nan")
        print(f"{phi:5.1f}  {t_plate:26.1f}  {t_wm:22.1f}  {overlap(groups[1], groups[-1]):7.1f}  {gap:18.1f}")

    out = HERE / "out"
    out.mkdir(exist_ok=True)
    allp = list(diff.values()) + [body_group]
    for sy, (arm, wheels, motors) in sides.items():
        allp += list(arm.values()) + list(wheels.values()) + list(motors.values())
    export_step(Compound(allp, label="al-maha-drive"), str(out / "rover_drive.step"))
