"""al-maha body interior: hollow shell, differential mount, shaft bearings, layout.

Replica design. The body of body.py is a solid envelope; this module cuts the
cavity and places what goes inside it, so fit can be checked. Everything here is
ASSUMPTION except the outer shape (body.py) and the pivot position (3i).

  * Shell: 3 mm walls and floor, 5 mm deck (body.py), 3 mm end walls.
  * Two 3 mm bulkheads at x = +-24, wall to wall, hold the differential housing
    between them and stiffen the shell.
  * Each pivot shaft runs through a bearing boss in the side wall (a 6800 bearing,
    10 x 19 x 5, on the 10 mm shaft; ISO size from memory) and into the housing.
  * Rear compartment: battery pack on the floor. Front compartment: controller and
    drivers on the floor, with a keep-out volume under the deck for the mast
    hinge and gimbal drive. Part choices are NOT made: the boxes are placeholders
    for the size class.

Run:  .venv/bin/python hardware/body/interior.py
Out:  hardware/body/out/interior.step
"""
import math
import sys
from pathlib import Path

from build123d import Box, Compound, Cylinder, Plane, Polygon, Pos, Rot, extrude, export_step

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "suspension"))
import body as B    # noqa: E402
import arms as A    # noqa: E402

WALL_T = 3.0             # side wall and end wall thickness        ASSUMPTION
FLOOR_T = 3.0            # floor thickness                          ASSUMPTION
BULKHEAD_T, BULKHEAD_X = 3.0, 24.0   # cross walls either side of the differential  ASSUMPTION
BULKHEAD_TOP = A.PIVOT_Z + 30.0      # bulkhead height                ASSUMPTION
BOSS_OD, BOSS_ID = 26.0, 19.0        # bearing boss; seat for a 6800 (OD 19)  ASSUMPTION
BOSS_LEN = 12.0
BEARING = dict(id=10.0, od=19.0, w=5.0)   # 6800, ISO size from memory
TAN = math.tan(math.radians(B.SIDEWALL_DEG))
COS = math.cos(math.radians(B.SIDEWALL_DEG))

# placeholder part sizes (x, y, z), mass kg: size classes, NOT chosen parts
PARTS = {
    "battery 2S2P 18650":  dict(size=(68.0, 38.0, 38.0), mass=0.22, at=(-110.0, 0.0)),
    "controller (Zero-class)": dict(size=(65.0, 30.0, 8.0), mass=0.015, at=(60.0, 35.0)),
    "motor drivers x2":    dict(size=(50.0, 70.0, 15.0), mass=0.05, at=(60.0, -30.0)),
    "5 V converter":       dict(size=(40.0, 20.0, 12.0), mass=0.015, at=(130.0, 60.0)),
}
KEEP_OUT = dict(size=(70.0, 70.0, 60.0),
                at=(B.BODY_X0 + B.SIDE_PLATE_LEN / 2 - WALL_T - 35.0, 0.0))
                # under the deck, as far forward as the cavity allows (a 70 mm box centred on the
                # mast base, x = 171, would pass the front end wall)  ASSUMPTION


def half_width(z):
    """Outer half-width of the wedge at height z."""
    return B.TOP_WIDTH / 2 + (B.DECK_TOP_Z - B.DECK_T - z) * TAN


def cavity():
    z0 = B.UNDERSIDE_Z + FLOOR_T
    z1 = B.DECK_TOP_Z - B.DECK_T
    off = WALL_T / COS
    pts = [(-(half_width(z0) - off), z0), (half_width(z0) - off, z0),
           (half_width(z1) - off, z1), (-(half_width(z1) - off), z1)]
    length = B.SIDE_PLATE_LEN - 2 * WALL_T
    return Pos(B.BODY_X0, 0, 0) * extrude(Plane.YZ * Polygon(*pts, align=None), amount=length / 2, both=True)


def floor_z():
    return B.UNDERSIDE_Z + FLOOR_T


def bulkheads(cav):
    out = []
    for sx in (1, -1):
        slab = Pos(sx * BULKHEAD_X, 0, (floor_z() + BULKHEAD_TOP) / 2) * Box(BULKHEAD_T, 400.0, BULKHEAD_TOP - floor_z())
        out.append(slab & cav)          # trimmed to the cavity so it spans wall to wall
    return out


def bosses():
    """Bearing bosses in the side walls at the pivot, plus the bearings."""
    out, bearings = [], []
    y_out = half_width(A.PIVOT_Z)       # flush at the axis; the top edge stands about 2.3 mm proud
    for sy in (1, -1):
        y0, y1 = y_out - BOSS_LEN, y_out
        ring = (Cylinder(BOSS_OD / 2, BOSS_LEN) - Cylinder(BOSS_ID / 2, BOSS_LEN))
        out.append(Pos(0, sy * (y0 + y1) / 2, A.PIVOT_Z) * Rot(90, 0, 0) * ring)
        b = Cylinder(BEARING["od"] / 2, BEARING["w"]) - Cylinder(BEARING["id"] / 2 + 0.2, BEARING["w"])
        bearings.append(Pos(0, sy * (y1 - BEARING["w"] / 2 - 2.0), A.PIVOT_Z) * Rot(90, 0, 0) * b)
    return out, bearings


def placed_parts():
    out = {}
    for n, d in PARTS.items():
        sx, sy, sz = d["size"]
        x, y = d["at"]
        out[n] = Pos(x, y, floor_z() + sz / 2) * Box(sx, sy, sz)
    kx, ky, kz = KEEP_OUT["size"]
    out["keep-out: mast hinge and gimbal drive"] = Pos(KEEP_OUT["at"][0], KEEP_OUT["at"][1],
                                                       B.DECK_TOP_Z - B.DECK_T - kz / 2) * Box(kx, ky, kz)
    return out


def shell(cav):
    outer, _ = B.body()
    return outer - cav


if __name__ == "__main__":
    cav = cavity()
    sh = shell(cav)
    bh = bulkheads(cav)
    bs, brg = bosses()
    diff = A.differential()["diff_housing"]
    parts = placed_parts()

    ib = cav.bounding_box()
    print(f"cavity x {ib.min.X:.0f}..{ib.max.X:.0f}, y +-{ib.max.Y:.0f}, z {ib.min.Z:.0f}..{ib.max.Z:.0f}; "
          f"volume {cav.volume / 1e6:.2f} L")
    print(f"shell volume {sh.volume / 1e3:.0f} cm3")

    print("\nfit (mm3 outside the cavity, want 0)")
    contents = {"differential housing": diff, **parts}
    for n, p in contents.items():
        out = p.volume - (p & cav).volume
        print(f"  {n:42s}: {out:8.1f}")

    print("\nclashes between contents and fixed structure (mm3, want 0)")
    fixed = {"bulkhead +x": bh[0], "bulkhead -x": bh[1]}
    names = list(contents)
    for i, n in enumerate(names):
        for m, f in fixed.items():
            v = (contents[n] & f).volume
            if v > 0.01:
                print(f"  {n} vs {m}: {v:.1f}")
        for n2 in names[i + 1:]:
            v = (contents[n] & contents[n2]).volume
            if v > 0.01:
                print(f"  {n} vs {n2}: {v:.1f}")
    print("  (anything not listed is 0)")

    print("\nshafts and bosses")
    arm_shafts = []
    for sy in (1, -1):
        arm, _, _ = A.side(sy)
        arm_shafts.append(arm["shaft"])
    for i, sh_ in enumerate(arm_shafts):
        v = sum((sh_ & x).volume for x in bs) + sum((sh_ & x).volume for x in brg)
        print(f"  shaft {i} vs bosses and bearings: {v:.1f} (want 0: shaft turns freely inside the bearing)")
        print(f"  shaft {i} vs bulkheads          : {sum((sh_ & x).volume for x in bh):.1f}")
        print(f"  shaft {i} vs differential housing: {(sh_ & diff).volume:.1f} (enters the housing, expect > 0)")
    print(f"  boss ends {half_width(A.PIVOT_Z):.1f} from the centreline at the axis; the wall's outer surface is "
          f"{half_width(A.PIVOT_Z + BOSS_OD / 2):.1f} at the top of the boss: stands "
          f"{half_width(A.PIVOT_Z) - half_width(A.PIVOT_Z + BOSS_OD / 2):.1f} mm proud there")
    print(f"  boss top z = {A.PIVOT_Z + BOSS_OD / 2:.1f}; cell field starts z = {B.FIELD_Z - B.N_ROWS * B.PITCH_V / 2:.0f}")

    mass = sum(d["mass"] for d in PARTS.values())
    x = sum(d["mass"] * d["at"][0] for d in PARTS.values()) / mass
    z = sum(d["mass"] * (floor_z() + d["size"][2] / 2) for d in PARTS.values()) / mass
    print(f"\nplaceholder electronics: {mass:.3f} kg, centre x {x:.0f}, z {z:.0f}")

    out = HERE / "out"
    out.mkdir(exist_ok=True)
    allp = [sh, *bh, *bs, *brg, diff, *parts.values()]
    export_step(Compound(allp, label="al-maha-interior"), str(out / "interior.step"))
