"""al-maha mast head, built version (owner's design, 2026-11-08): a bent sheet bracket on the T-slot, a printed camera enclosure on a sideways disk,
the CASPEX-look lens assembly in front of a Camera Module 3 stand-in, a flat antenna hat. Concept history and the reasoning: docs/mast-spec.md,
hardware/mast/head_concept.py (render of this head). Frame as in body.py.

Sizes: whole camera 35 x 35 x 73 mm [S12], module 25.2 of it (3DDS-0734); cradle plate 45 mm, collar, ring, hood, enclosure 60 mm, disk, hat sizes are
read by eye from the photos and CAD figures (ASSUMPTION); the bracket outline follows the original's arm in [S18] Fig. 1 (45 degree S-bend, arm at y +27 to
+69). Sheet 2 mm aluminium, thickness ASSUMPTION; flanges bolt into the extrusion's side slots (M6 into T-nuts), not yet checked against the profile.
"""
import math
import sys
from pathlib import Path

from build123d import Box, Cylinder, Pos, Rot

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "body"))
sys.path.insert(0, str(HERE))
import body as B  # noqa: E402
import head as H  # noqa: E402

TX = B.MAST_X
CY = B.CAM_Y
AZ = 660.0
FX = B.WHEELBASE / 2 + 77.9
Z_EXT = 577.0                      # top of the extrusion
box = H._box
LID = 2.0                          # lid thickness of the die-cast enclosure (Takachi TD6-6-4, drawing)


def cyl_x(x0, x1, y, z, r):
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(r, x1 - x0)


def cyl_y(y0, y1, x, z, r):
    return Pos(x, (y0 + y1) / 2, z) * Rot(90, 0, 0) * Cylinder(r, y1 - y0)


def caspex():
    """Module + plate + collar + baffle ring + hood, lens looking +x, lens front at FX. Returns {group: shape}."""
    x_back = FX - 73.0
    mod = box(x_back, x_back + 25.2, CY - 17.5, CY + 17.5, AZ - 17.5, AZ + 17.5)                  # 35 x 35 x 25.2 over the pins
    xp0 = x_back + 25.2
    xp0 += LID                                                                                      # the 2 mm enclosure lid lies between the module and the plate
    plate = box(xp0, xp0 + 4, CY - 22.5, CY + 22.5, AZ - 22.5, AZ + 22.5)                          # 45 square cradle, ASSUMPTION
    for sy in (-1, 1):
        for sz in (-1, 1):
            plate = plate - cyl_x(xp0 - 1, xp0 + 5, CY + sy * 19.5, AZ + sz * 19.5, 1.6)           # corner holes
    xp0 -= 0.0
    collar = cyl_x(xp0 + 4, xp0 + 22, CY, AZ, 16.0)                                                # round collar, ASSUMPTION
    ring0 = xp0 + 22
    ring = cyl_x(ring0, FX - 2, CY, AZ, 18.5)                                                      # slotted baffle ring
    for k in range(36):
        a = math.radians(k * 10)
        ring = ring - Pos(FX - 6, CY + 16.5 * math.cos(a), AZ + 16.5 * math.sin(a)) * Rot(a * 180 / math.pi, 0, 0) * Box(9, 2.2, 3.0)
    ring = ring - cyl_x(ring0 + 3, FX, CY, AZ, 14.0)
    barrel = cyl_x(ring0 - 1, FX - 5, CY, AZ, 8.0) + cyl_x(FX - 12, FX - 5.5, CY, AZ, 11.0)         # lens barrel and glass, recessed
    hood = cyl_x(FX - 12, FX, CY, AZ, 20.5) - (Pos(FX - 6, CY, AZ) * Rot(8, 0, 0) * Box(20, 24, 24))   # black cap with a square window
    return {"camera body": mod, "cradle": plate, "collar": collar, "baffle": ring + barrel, "hood": hood}


BR_T = 2.0               # sheet thickness, aluminium 5052, ASSUMPTION
BR_Y0, BR_Y1 = 20.0, 69.0   # extrusion face, outer face of the vertical web


def _flange(x0, pts):
    from build123d import Face, Vector, Wire, extrude
    f = Face(Wire.make_polygon([Vector(x0, y, z) for (y, z) in pts], close=True))
    return extrude(f, amount=BR_T, dir=(1, 0, 0))


def bracket():
    """Bent sheet bracket (owner's sketch, 2026-11-08), outline matched to the original's arm ([S18] Fig. 1 front view: vertical mast, a 45 degree
    S-bend towards +y over about z 577 to 625, then a vertical arm at y +27 to +69; the band is parallel-sided). One blank, two folds: a web on the +y
    face of the extrusion that kinks out to +y and rises vertical, and two side flanges that straddle the extrusion (inner width 40) and are bolted
    through into the side slots, then follow the band up to z 697. The tilt servo sits between the flanges, seen through a window in the web."""
    from build123d import Face, Vector, Wire, extrude
    z0 = Z_EXT
    t = BR_T
    zl = z0 - 32.0                                              # bottom of the bracket, z 545
    xw0, xw1 = TX - 22.0, TX + 22.0
    ya, yb = 20.0 + t / 2, BR_Y1 - t / 2                          # sheet centre lines of the tab and the vertical web
    za, zb = z0 + t / 2, z0 + t / 2 + (yb - ya)                   # 45 degree diagonal between them
    L = math.hypot(yb - ya, zb - za)
    tab = box(xw0, xw1, 20.0, 20.0 + t, zl, za)
    diag = Pos(TX, (ya + yb) / 2, (za + zb) / 2) * Rot(-45, 0, 0) * Box(44.0, t, L + t)
    vert = box(xw0, xw1, BR_Y1 - t, BR_Y1, zb, 697.0)
    web = tab + diag + vert
    web = web - box(TX - 18.0, TX + 18.0, BR_Y1 - t - 1, BR_Y1 + 1, 632.0, 674.0)             # window over the tilt servo
    fl = [(-20.0, zl), (-20.0, z0), (27.0, z0 + 47.0), (27.0, 689.0), (35.0, 697.0), (BR_Y1, 697.0), (BR_Y1, z0 + BR_Y1 - 20.0), (20.0, z0), (20.0, zl)]
    out = web
    for x0 in (TX - 22.0, TX + 20.0):
        f = _flange(x0, fl)
        for zz in (zl + 10.0, zl + 24.0):
            f = f - cyl_x(x0 - 1, x0 + t + 1, 0.0, zz, 3.4)                               # M6 clearance into the side-slot T-nuts
        out = out + f
    return out


ENC_D = 35.0                                    # depth of the box (Takachi TD6-6-4: 60 x 60 x 35, ADC12, 90 g)
ENC_X1 = FX - 73.0 + 25.2 + LID                 # front face: the module (25.2) sits inside against the 2 mm lid, the cradle plate on the outside


def enclosure():
    """Takachi TD6-6-4 die-cast aluminium box (catalogue drawing TD6-6-4B/N, 2019): 60 x 60 x 35, walls 2, cover lip 4, internal maximum 50.3 x 36.3 x 31
    (36.3 is the clear span between the corner screw bosses, which are modelled as 7 x 7 mm blocks), four M3.5 countersunk cover screws at +-25. Draft
    and corner radii are not modelled. The cover is at the front, with a 35 mm hole for the lens barrel; the cavity opens to the front, the base is behind."""
    x1 = ENC_X1
    x0 = x1 - ENC_D
    base = box(x0, x1 - LID, CY - 30.0, CY + 30.0, AZ - 30.0, AZ + 30.0) - box(x0 + 2.0, x1 - LID + 1, CY - 28.0, CY + 28.0, AZ - 28.0, AZ + 28.0)
    for sy in (-1, 1):
        for sz in (-1, 1):
            ya, yb = sorted((CY + sy * 18.15, CY + sy * 28.5))                # corner screw boss: 7 x 7 mm block against the walls
            za, zb = sorted((AZ + sz * 18.15, AZ + sz * 28.5))
            base = base + box(x0 + 1.9, x1 - LID, ya, yb, za, zb)
    lid = box(x1 - LID, x1, CY - 30.0, CY + 30.0, AZ - 30.0, AZ + 30.0) - cyl_x(x1 - LID - 1, x1 + 1, CY, AZ, 17.5)
    return base + lid


def head(z_ext=Z_EXT):
    """All head parts in the rover frame: bracket, tilt servo, disk, enclosure, hat and the camera stack. Rotating column: T-slot to z 577, the bracket on its end."""
    parts = {}
    parts["bracket"] = bracket()
    tilt = Pos(TX, 47.5, AZ) * Rot(-90, 0, 0) * Rot(0, 0, 90) * H.sts3215()
    parts["tilt servo"] = tilt
    parts["disk"] = cyl_y(2.0, 22.0, TX, AZ, 20.0)                                      # sideways disk, encoder or mounting, ASSUMPTION; 40 mm so that it stays near the box
    parts["enclosure"] = enclosure()
    xc = ENC_X1 - ENC_D / 2
    hz = AZ + 30.0
    parts["antenna hat"] = Pos(xc, CY, hz + 3.5) * Cylinder(35.0, 7.0) + \
        (Pos(xc, CY, hz + 8.5) * Cylinder(35.0, 3.0) - Pos(xc, CY, hz + 8.5) * Cylinder(31.5, 3.2))
    c = caspex()
    parts["camera body"], parts["cradle"], parts["collar"], parts["baffle"], parts["hood"] = (c[k] for k in ("camera body", "cradle", "collar", "baffle", "hood"))
    return parts


TILTING = ("disk", "enclosure", "antenna hat", "camera body", "cradle", "collar", "baffle", "hood")
