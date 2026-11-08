"""al-maha mast base: the pan drive. The whole mast turns on a spindle in a die-cast box on the deck, driven by the pan servo in line with it, as the
original's pan motor sits in the blue block at the mast base (original-dimensions.md 3j, 3m).

Box: Takachi AL080807, IP65 die-cast aluminium, 80 x 75 x 70 mm (W x D x H), 347 g, gasketed, M4 cover screws; drawing AL080807 (2025). The lid (a 15 mm deep
cap) is on the TOP. The original's base block is about 79 mm wide and 73 mm tall, its top near z 425 (measured on Fig. 1); the box is 80 wide and its top is at z 424.

Stack, bottom to top (z above ground; deck top 348, 6 mm aluminium base plate to 354):
  box base 354..409 (floor 3.6) holding the pan servo (STS3215, as head.py) standing on the floor with its long side along y (45.2 mm of the 70.5 mm cavity: it clears by 0.1 mm), shaft vertical on the mast axis
  coupling disc on the servo horn; aluminium spindle tube 30/22 from the disc up through a bearing tower hung under the lid: two 6806-size bearings (30 x 42 x 7) 12.6 mm apart,
  the upper one against the lid's underside; the spindle leaves through a 36 mm hole in the lid to a 60 mm flange 2 mm above it; the T-slot extrusion stands on the flange.
The servo only turns the mast; the bearings carry its weight and the bending load (the 12.6 mm spacing puts about three times the radial load on them than the earlier 30 mm spacing did,
still far below a 6806 bearing's rating; not checked), and the lid carries the bearings, so the load path is mast, bearings, tower, lid, four M4 cover screws, base. Lid
stiffness, the gasket, a seal where the spindle leaves the lid, fixing the box to the base plate (the box has two M4 external mounting holes), the compliant servo coupling, the
320 degree hard stop and the cable loop are not designed. Bearing figures are a standard size; their rating and mass are not checked (ASSUMPTION).

Run:  .venv/bin/python hardware/mast/base.py
"""
import math
import sys
from pathlib import Path

from build123d import Box, Cylinder, Pos, Rot

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import head as H  # noqa: E402

BOX_Y, BOX_X, BOX_BASE, BOX_COVER = 80.0, 75.0, 55.0, 15.0     # W (along y), D (along x), base and cover heights
BOX_H = BOX_BASE + BOX_COVER
WALL_T = 3.6                                     # floor and cover top: (70 - 62.75) / 2 from the drawing's interior height 62.75
CAV_Y, CAV_X = 70.5, 66.8                        # cavity at the mouth, drawing "max dim"
BOX_KG = 0.347                                   # catalogue (347 g)
BRG_D, BRG_OD, BRG_W = 30.0, 42.0, 7.0          # 6806-size
TOWER_OD = 52.0
SP_OD, SP_ID = 30.0, 22.0
AL = 2.70e-6                                     # kg/mm3
BEARING_KG = 0.024                               # ASSUMPTION (per bearing, 6806-2RS class; not looked up)
HARDWARE_KG = 0.03                               # screws, retaining rings, coupling hardware ASSUMPTION
HOUS_XY = BOX_Y                                  # for the plate size in mast.py


def _box(x0, x1, y0, y1, z0, z1):
    return H._box(x0, x1, y0, y1, z0, z1)


def build(tx, z_plate_top):
    """Parts in the rover frame, mast axis at (tx, 0). Returns (parts, info). info: z of the flange top (the extrusion starts there), masses, bearing z's."""
    z0 = z_plate_top                              # box bottom
    zj = z0 + BOX_BASE                            # joint between base and cover
    zt = z0 + BOX_H                               # top of the lid
    zf = z0 + WALL_T                              # floor top
    zin = zt - WALL_T                             # inner face of the lid
    sv_c = zf + H.SV_HORN_T + H.SV_T / 2          # servo centre (the shaft origin), lower horn on the floor
    sv_top = sv_c + H.SV_TOTAL / 2
    disc_z0, disc_z1 = sv_top, sv_top + 4.0
    b2_z1 = zin; b2_z0 = b2_z1 - BRG_W            # upper bearing against the lid
    b1_z0 = disc_z1 + 2.0; b1_z1 = b1_z0 + BRG_W  # lower bearing
    fl0, fl1 = zt + 2.0, zt + 8.0                 # rotating top flange
    hy, hx = BOX_Y / 2, BOX_X / 2
    # base: walls and floor, four cast screw posts; cover: cap with a hole for the spindle; bearing tower hung under the lid
    base = _box(tx - hx, tx + hx, -hy, hy, z0, zj) - _box(tx - CAV_X / 2, tx + CAV_X / 2, -CAV_Y / 2, CAV_Y / 2, zf, zj + 1.0)
    cover = _box(tx - hx, tx + hx, -hy, hy, zj, zt) - _box(tx - CAV_X / 2, tx + CAV_X / 2, -CAV_Y / 2, CAV_Y / 2, zj - 1.0, zin)
    cover = cover - Pos(tx, 0, zt - WALL_T / 2) * Cylinder(18.0, WALL_T + 2.0)                                # 36 mm spindle hole
    for sx in (-1, 1):
        for sy in (-1, 1):
            base = base + Pos(tx + sx * 31.5, sy * 34.0, (zf + zj) / 2 - 0.05) * Cylinder(5.5, zj - zf + 0.1)    # M4 cover screw posts on 63 x 68
    t0 = b1_z0 - 1.0
    tower = Pos(tx, 0, (t0 + zin) / 2) * (Cylinder(TOWER_OD / 2, zin - t0) - Cylinder(BRG_OD / 2, zin - t0 + 1.0))
    shelf = Pos(tx, 0, t0 + 0.5) * (Cylinder(TOWER_OD / 2, 1.0) - Cylinder(SP_OD / 2 + 3.0, 2.0))
    housing = base + cover + tower + shelf
    servo = Pos(tx, 0, sv_c) * Rot(0, 0, 90) * H.sts3215()                       # long side along +y
    # coupling disc with a cable hole off the axis; spindle tube; top flange
    disc = Pos(tx, 0, (disc_z0 + disc_z1) / 2) * Cylinder(18.0, 4.0) - Pos(tx + 9.0, 0, (disc_z0 + disc_z1) / 2) * Cylinder(5.0, 6.0)
    sp_z0, sp_z1 = disc_z1, fl1
    spindle = Pos(tx, 0, (sp_z0 + sp_z1) / 2) * (Cylinder(SP_OD / 2, sp_z1 - sp_z0) - Cylinder(SP_ID / 2, sp_z1 - sp_z0 + 1.0))
    flange = Pos(tx, 0, (fl0 + fl1) / 2) * (Cylinder(30.0, fl1 - fl0) - Cylinder(SP_ID / 2, fl1 - fl0 + 1.0))
    brgs = []
    for zb0, zb1 in ((b1_z0, b1_z1), (b2_z0, b2_z1)):
        brgs.append(Pos(tx, 0, (zb0 + zb1) / 2) * (Cylinder(BRG_OD / 2, BRG_W) - Cylinder(BRG_D / 2, BRG_W + 1.0)))
    parts = {"pan housing": housing, "pan servo": servo, "pan coupling disc": disc, "spindle": spindle + flange, "pan bearings": brgs[0] + brgs[1]}
    kg_al = (disc.volume + spindle.volume + flange.volume + tower.volume + shelf.volume) * AL
    info = dict(z_flange_top=fl1, z_housing_top=zt, bearing_z=((b1_z0 + b1_z1) / 2, (b2_z0 + b2_z1) / 2), servo_z=(sv_c - H.SV_TOTAL / 2, sv_c + H.SV_TOTAL / 2),
                al_kg=kg_al, bearing_kg=2 * BEARING_KG, hardware_kg=HARDWARE_KG, housing_kg=BOX_KG)
    return parts, info


def checks(parts, info, tx, moment_1g_nm=None, mast_kg=None):
    v = lambda a, b: (lambda r: 0.0 if r is None else r.volume)(parts[a] & parts[b])
    print("pan base: overlaps (mm3, want 0 except the press fits):")
    for a, b in (("pan servo", "pan housing"), ("pan servo", "spindle"), ("pan servo", "pan coupling disc"), ("pan coupling disc", "pan housing"),
                 ("spindle", "pan housing"), ("pan bearings", "pan housing"), ("spindle", "pan coupling disc")):
        print(f"  {a:18s} vs {b:18s}: {v(a, b):9.1f}")
    print(f"  bearings on the spindle (30 mm bore, in the 42 mm seat): the volume shared with the spindle/housing above is the seat contact "
          f"({v('pan bearings', 'spindle'):.0f}, {v('pan bearings', 'pan housing'):.0f} mm3, a zero-gap fit)")
    sb = parts["pan servo"].bounding_box()
    print(f"  servo x {sb.min.X:.1f}..{sb.max.X:.1f}, y {sb.min.Y:.1f}..{sb.max.Y:.1f}, z {sb.min.Z:.1f}..{sb.max.Z:.1f}; box cavity x {tx - CAV_X / 2:.1f}..{tx + CAV_X / 2:.1f}, y {-CAV_Y / 2:.1f}..{CAV_Y / 2:.1f}")
    print(f"  stack: servo z {info['servo_z'][0]:.1f}..{info['servo_z'][1]:.1f}; bearings at z {info['bearing_z'][0]:.1f} and {info['bearing_z'][1]:.1f} "
          f"({info['bearing_z'][1] - info['bearing_z'][0]:.0f} mm apart); box top {info['z_housing_top']:.1f}; flange top {info['z_flange_top']:.1f}")
    print(f"  masses: die-cast box {info['housing_kg']:.3f} kg (catalogue), aluminium parts {info['al_kg']:.3f}, bearings {info['bearing_kg']:.3f} (ASSUMPTION), hardware {info['hardware_kg']:.3f}")
    if moment_1g_nm:
        span = (info['bearing_z'][1] - info['bearing_z'][0]) / 1000.0
        for g in (1, 3):
            r = moment_1g_nm * g / span
            print(f"  bearing radial load at {g} g sideways: {r:.0f} N each ({span*1000:.1f} mm apart); axial {mast_kg * 9.81 * g:.0f} N; a 6806-size bearing's catalogue rating is in the kN range (not checked)")
        print(f"  pan servo: stall 19.5 kg.cm = 1.91 N.m, continuous 6.5 kg.cm = 0.64 N.m (electronics-spec.md); head inertia about the axis is small "
              f"(about {mast_kg * 0.06 ** 2 * 1e3:.1f} g.m2 at a 60 mm radius, an order of magnitude estimate)")


if __name__ == "__main__":
    import mast as M
    p, info = build(M.TUBE_X, M.BASE_Z1)
    checks(p, info, M.TUBE_X)
