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
CY = B.CAM_Y                       # camera lateral position, 28 right of the mast axis [S8]; the disk length (below) takes up the difference
AZ = 667.0                         # tilt axis and camera axis height: measured on the original's Fig. 1 front and side views, lens centre about 32 mm below the top plate (z 700 -> 667-668); [S12] states 660, the earlier side-view reading was 664
FX = B.WHEELBASE / 2 + 77.9
Z_EXT = 597.0                      # top of the extrusion: raised from 577 to 597 (2026-11-08); above about z 600 the swept corners of the camera box hit it when the head tilts
box = H._box
LID = 0.0                          # nothing between the camera module and its cradle plate (the module sits against the plate)


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
    plate = box(xp0, xp0 + 4, CY - 20.0, CY + 20.0, AZ - 20.0, AZ + 20.0)                          # 40 square cradle inside the box (the 45 of the earlier concept cannot sit between the cast screw posts), ASSUMPTION
    for sy in (-1, 1):
        for sz in (-1, 1):
            plate = plate - cyl_x(xp0 - 1, xp0 + 5, CY + sy * 12.5, AZ + sz * 12.5, 1.25)           # corner holes (the module's M2.5 on 25 mm)
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


# ---- bracket (owner's simplified redesign, mast_simplified_in_situ.step, 2026-11-08) ---------------------------------
BR_FLANGE_YZ = [(20.0, 545.0), (54.0, 566.25), (54.0, 634.6), (36.0, 690.0), (20.0, 690.0)]    # y, z of each flange: a tapered fin on the +y side of the extrusion
BR_WEB_Y0, BR_WEB_Y1 = 20.0, 22.0     # the web plate lies on the extrusion's +y face; the servo sits against its outer face (+y), its horn through the hole
BR_HOLE_D = 19.2                      # horn pass-through in the web
BR_BOLT_Z = (555.0, 569.0, 583.0)       # Ø6.8 holes (555 and 569 are the owner's; 583 added when the extrusion was raised to 597)  # for M6 into the centre slot of the +y face


def _prism_yz(x0, pts_yz, t=BR_T):
    from build123d import Face, Vector, Wire, extrude
    f = Face(Wire.make_polygon([Vector(x0, y, z) for (y, z) in pts_yz], close=True))
    return extrude(f, amount=t, dir=(1, 0, 0))


def bracket():
    """Sheet bracket from the owner's simplified redesign (outline traced from the original's front view): a 2 mm aluminium web, 40 wide, z 545 to 690, lying on the extrusion's
    +y face with two Ø6.8 holes (z 555, 569) for M6 into the centre slot, and a 2 mm flange along each side edge (x +-18 to +-20 from the mast axis) standing out to y 54: bottom point at the
    extrusion, slant to full depth by z 566, vertical to z 635, slant in to y 36 at the top z 690. The tilt servo sits between the flanges against the web, its horn through a Ø19.2 hole at z 660.
    The web reaches 93 mm above the extrusion top (z 597) to 690 and carries the head; no part straddles the extrusion. Sizes read from the STEP file."""
    t = BR_T
    out = box(TX - 20.0, TX + 20.0, BR_WEB_Y0, BR_WEB_Y1, 545.0, 690.0) - cyl_y(BR_WEB_Y0 - 1, BR_WEB_Y1 + 1, TX, AZ, BR_HOLE_D / 2)
    for zz in BR_BOLT_Z:
        out = out - cyl_y(BR_WEB_Y0 - 1, BR_WEB_Y1 + 1, TX, zz, 3.4)
    for x0 in (TX - 20.0, TX + 18.0):
        out = out + _prism_yz(x0, BR_FLANGE_YZ)
    return out


# Camera box: Takachi AL060605, IP65 die-cast aluminium, 64 x 58 x 46 mm (W x D x H), 162 g, gasketed, M4 cover screws; drawing AL060605 (2025). The cover (9 mm deep cap) is at the front,
# like the cover screws seen on the original's camera box; the 46 mm depth is along the camera axis.
ENC_Y, ENC_Z, ENC_X = 64.0, 58.0, 46.0
ENC_WALL = 3.7                                  # wall, floor and cover top: (64 - 56.6) / 2 and (58 - 50.6) / 2 from the drawing's maximum cavity 56.6 x 50.6
ENC_COVER = 9.0                                 # depth of the cover cap
ENC_X1 = FX - 73.0 - ENC_WALL + ENC_X + 0.0     # front face: the inner back wall touches the module's back (module x_back = FX - 73)
ENC_KG = 0.162                                  # catalogue (162 g)


def enclosure():
    """Takachi AL060605 die-cast box (drawing AL060605, 2025): outer 64 (y) x 58 (z) x 46 (x), walls 3.7, cavity 56.6 x 50.6 at the mouth, cover cap 9 deep at the front with a 35 mm
    lens hole, four M4 cover screws on 52 x 46 (y x z) at the corners. The cast screw posts (modelled as round 11 mm posts) leave 31.7 and 32.8 between them on the drawing; the
    module (35) and the 40 mm cradle plate clear them in this model, which is not certain (the real posts may be larger). Draft, gasket, corner radii, earth screws not modelled."""
    x1 = ENC_X1
    x0 = x1 - ENC_X
    xj = x1 - ENC_COVER                         # joint between base and cover
    hy, hz = ENC_Y / 2, ENC_Z / 2
    base = box(x0, xj, CY - hy, CY + hy, AZ - hz, AZ + hz) - box(x0 + ENC_WALL, xj + 1.0, CY - 28.3, CY + 28.3, AZ - 25.3, AZ + 25.3)
    cover = box(xj, x1, CY - hy, CY + hy, AZ - hz, AZ + hz) - box(xj - 1.0, x1 - ENC_WALL, CY - 28.3, CY + 28.3, AZ - 25.3, AZ + 25.3)
    cover = cover - cyl_x(x1 - ENC_WALL - 1.0, x1 + 1.0, CY, AZ, 17.5)
    for sy in (-1, 1):
        for sz in (-1, 1):
            post = cyl_x(x0 + ENC_WALL - 0.1, xj, CY + sy * 26.0, AZ + sz * 23.0, 5.5)
            base = base + post
            cover = cover + cyl_x(x1, x1 + 1.5, CY + sy * 26.0, AZ + sz * 23.0, 3.4)      # M4 cover screw heads
    return base + cover


def head(z_ext=Z_EXT):
    """All head parts in the rover frame: bracket, tilt servo, disk, enclosure, hat and the camera stack. Rotating column: T-slot to z 597, the bracket on its end."""
    parts = {}
    parts["bracket"] = bracket()
    tilt = Pos(TX, 38.1, AZ) * Rot(-90, 0, 0) * Rot(0, 0, 90) * H.sts3215()
    parts["tilt servo"] = tilt
    box_y_max = CY + ENC_Y / 2
    parts["disk"] = cyl_y(box_y_max, BR_WEB_Y0 - 0.5, TX, AZ, 20.0)                                       # sideways disk, ASSUMPTION; its thickness takes up the gap from the box to the web
    parts["enclosure"] = enclosure()
    xc = ENC_X1 - ENC_X / 2
    hz = AZ + ENC_Z / 2                                                                                     # top of the box (z 696); the flat hat sits on the cover's top face up to z 700
    parts["antenna hat"] = Pos(xc, CY, hz + 2.0) * Cylinder(35.0, 4.0)
    c = caspex()
    parts["camera body"], parts["cradle"], parts["collar"], parts["baffle"], parts["hood"] = (c[k] for k in ("camera body", "cradle", "collar", "baffle", "hood"))
    return parts


TILTING = ("disk", "enclosure", "antenna hat", "camera body", "cradle", "collar", "baffle", "hood")
