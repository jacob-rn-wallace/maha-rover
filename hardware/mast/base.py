"""al-maha mast base: the pan drive. The whole mast turns on a spindle in a housing on the deck, driven by the pan servo in line with it, as the
original's pan motor sits in the blue block at the mast base (original-dimensions.md 3j; the owner's reading of the CAD figure).

Stack, bottom to top (z above ground; deck top 348, 6 mm aluminium base plate to 354):
  printed housing 76 x 76 (wall 2.5, floor 2) with a bearing tower, 354..438; the base plate is the mounting plate
  pan servo (STS3215, as head.py) standing on the floor, shaft vertical on the mast axis; its output horn is bolted to a coupling disc
  spindle: aluminium tube 30/22 from the disc up through two 6806-size bearings (30 x 42 x 7) 30 mm apart, to a 60 mm top flange at 440..446
  the T-slot extrusion stands on the flange; the camera and servo cables run down its slots into the hollow spindle and out through a hole in the disc.
The servo only turns the mast; the bearings carry its weight and the bending load, so no side load reaches the servo's output bearing. Between the
servo horn and the disc the joint must tolerate a little misalignment (compliant coupling, not designed). Bearing figures (30 x 42 x 7) are a standard
size; their rating and mass are not checked (ASSUMPTION). Hard stop for the 320 degree limit and the cable loop are not designed.

Run:  .venv/bin/python hardware/mast/base.py
"""
import math
import sys
from pathlib import Path

from build123d import Box, Cylinder, Pos

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import head as H  # noqa: E402

WALL, FLOOR = 2.5, 2.0
HOUS_XY = 76.0
BRG_D, BRG_OD, BRG_W = 30.0, 42.0, 7.0          # 6806-size
TOWER_OD = 52.0
SP_OD, SP_ID = 30.0, 22.0
AL = 2.70e-6                                     # kg/mm3
BEARING_KG = 0.024                               # ASSUMPTION (per bearing, 6806-2RS class; not looked up)
HARDWARE_KG = 0.03                               # screws, retaining rings, coupling hardware ASSUMPTION


def _box(x0, x1, y0, y1, z0, z1):
    return H._box(x0, x1, y0, y1, z0, z1)


def build(tx, z_plate_top):
    """Parts in the rover frame, mast axis at (tx, 0). Returns (parts, info). info: z of the flange top (the extrusion starts there), masses, bearing z's."""
    z0 = z_plate_top                              # housing bottom
    zf = z0 + FLOOR                               # floor top
    horn_b = zf                                   # servo bottom horn rests on the floor
    sv_c = horn_b + H.SV_HORN_T + H.SV_T / 2      # servo centre (the shaft origin)
    sv_top = sv_c + H.SV_TOTAL / 2 - H.SV_HORN_T + H.SV_HORN_T   # top of the upper horn
    disc_z0, disc_z1 = sv_top, sv_top + 4.0
    b1_z0 = disc_z1 + 2.8; b1_z1 = b1_z0 + BRG_W    # lower bearing
    b2_z1 = b1_z1 + 23.0 + BRG_W; b2_z0 = b2_z1 - BRG_W   # upper bearing, 30 mm centres
    z_top_h = b2_z1 + 1.0                         # housing top
    fl0, fl1 = z_top_h + 2.0, z_top_h + 8.0       # rotating top flange
    h = HOUS_XY / 2
    # housing: walls and floor, tower, ribs, lid
    hous = _box(tx - h, tx + h, -h, h, z0, z_top_h) - _box(tx - h + WALL, tx + h - WALL, -h + WALL, h - WALL, zf, z_top_h - 3.0)
    tower = Pos(tx, 0, (disc_z1 + z_top_h) / 2) * (Cylinder(TOWER_OD / 2, z_top_h - disc_z1) - Cylinder(BRG_OD / 2, z_top_h - disc_z1 + 1.0))
    ribs = _box(tx - h + WALL, tx + h - WALL, -1.25, 1.25, disc_z1, z_top_h - 3.0) + _box(tx - 1.25, tx + 1.25, -h + WALL, h - WALL, disc_z1, z_top_h - 3.0)
    ribs = ribs - Pos(tx, 0, (disc_z1 + z_top_h) / 2) * Cylinder(BRG_OD / 2, z_top_h - disc_z1 + 1.0)
    lid = _box(tx - h, tx + h, -h, h, z_top_h - 3.0, z_top_h) - Pos(tx, 0, z_top_h - 1.5) * Cylinder(BRG_OD / 2, 4.0)
    shelf = Pos(tx, 0, disc_z1 + 1.0) * (Cylinder(TOWER_OD / 2, 2.0) - Cylinder(SP_OD / 2 + 1.5, 3.0))                      # tower floor
    housing = (hous + tower + ribs + lid + shelf) - Pos(tx, 0, (disc_z1 + z_top_h) / 2) * Cylinder(BRG_OD / 2, z_top_h - disc_z1 + 1.0) + tower
    servo = Pos(tx, 0, sv_c) * H.sts3215()
    # coupling disc with a cable hole off the axis; spindle tube; top flange
    disc = Pos(tx, 0, (disc_z0 + disc_z1) / 2) * Cylinder(18.0, 4.0) - Pos(tx + 9.0, 0, (disc_z0 + disc_z1) / 2) * Cylinder(5.0, 6.0)
    sp_z0, sp_z1 = disc_z1, fl1
    spindle = Pos(tx, 0, (sp_z0 + sp_z1) / 2) * (Cylinder(SP_OD / 2, sp_z1 - sp_z0) - Cylinder(SP_ID / 2, sp_z1 - sp_z0 + 1.0))
    flange = Pos(tx, 0, (fl0 + fl1) / 2) * (Cylinder(30.0, fl1 - fl0) - Cylinder(SP_ID / 2, fl1 - fl0 + 1.0))
    brgs = []
    for zb0, zb1 in ((b1_z0, b1_z1), (b2_z0, b2_z1)):
        brgs.append(Pos(tx, 0, (zb0 + zb1) / 2) * (Cylinder(BRG_OD / 2, BRG_W) - Cylinder(BRG_D / 2, BRG_W + 1.0)))
    parts = {"pan housing": housing, "pan servo": servo, "pan coupling disc": disc, "spindle": spindle + flange, "pan bearings": brgs[0] + brgs[1]}
    kg_al = (disc.volume + spindle.volume + flange.volume) * AL
    info = dict(z_flange_top=fl1, z_housing_top=z_top_h, bearing_z=((b1_z0 + b1_z1) / 2, (b2_z0 + b2_z1) / 2), servo_z=(sv_c - H.SV_TOTAL / 2, sv_c + H.SV_TOTAL / 2),
                al_kg=kg_al, bearing_kg=2 * BEARING_KG, hardware_kg=HARDWARE_KG, housing_kg=H.shell_mass(housing))
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
    print(f"  servo x {sb.min.X:.1f}..{sb.max.X:.1f}, y {sb.min.Y:.1f}..{sb.max.Y:.1f}, z {sb.min.Z:.1f}..{sb.max.Z:.1f}; housing inside x {tx - HOUS_XY / 2 + WALL:.1f}..{tx + HOUS_XY / 2 - WALL:.1f}")
    print(f"  stack: servo z {info['servo_z'][0]:.1f}..{info['servo_z'][1]:.1f}; bearings at z {info['bearing_z'][0]:.1f} and {info['bearing_z'][1]:.1f} "
          f"({info['bearing_z'][1] - info['bearing_z'][0]:.0f} mm apart); housing top {info['z_housing_top']:.1f}; flange top {info['z_flange_top']:.1f}")
    print(f"  masses: housing {info['housing_kg']:.3f} kg (PETG), aluminium parts {info['al_kg']:.3f}, bearings {info['bearing_kg']:.3f} (ASSUMPTION), hardware {info['hardware_kg']:.3f}")
    if moment_1g_nm:
        span = (info['bearing_z'][1] - info['bearing_z'][0]) / 1000.0
        for g in (1, 3):
            r = moment_1g_nm * g / span
            print(f"  bearing radial load at {g} g sideways: {r:.0f} N each (30 mm apart); axial {mast_kg * 9.81 * g:.0f} N; a 6806-size bearing's catalogue rating is in the kN range (not checked)")
        print(f"  pan servo: stall 19.5 kg.cm = 1.91 N.m, continuous 6.5 kg.cm = 0.64 N.m (electronics-spec.md); head inertia about the axis is small "
              f"(about {mast_kg * 0.06 ** 2 * 1e3:.1f} g.m2 at a 60 mm radius, an order of magnitude estimate)")


if __name__ == "__main__":
    import mast as M
    p, info = build(M.TUBE_X, M.BASE_Z1)
    checks(p, info, M.TUBE_X)
