"""al-maha mast head, built version (owner's design, 2026-11-08): a bent sheet bracket on the T-slot, a printed camera enclosure on a sideways disk,
a Raspberry Pi HQ camera with a 4 mm CS lens behind a printed baffle ring and hood, a flat antenna hat. Concept history and the reasoning: docs/mast-spec.md,
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


# Camera: Raspberry Pi High Quality Camera (CS mount, IMX477) with a 4 mm CS-mount lens, replacing the 3D Plus CASPEX module and its custom optics (2026-11-08).
# HQ camera: board 38 x 38 mm, four Ø2.5 holes 4 mm from the edges, lens mount (focus ring) Ø36 reaching 10.35 mm in front of the board, board 1.4 mm, connectors about 5.7 mm behind
# [Raspberry Pi HQ camera product brief, Jan 2023, p. 4]. Lens: generic 4 mm 5 MP CS-mount, 1/2", f/1.2, 80 degrees horizontal, 30 x 42 mm (Ø x length, order not stated on the
# listing), 49 g [PiShop SKU 485-1, a retailer listing; no maker named]. The original's 3DCM739 camera is a 4 MP, f/8, 7.8 mm, 82 x 82 degree unit [S12].
HQ_PCB, HQ_T, HQ_RING_D, HQ_RING_L, HQ_REAR = 38.0, 1.4, 36.0, 10.35, 5.71
LENS_D, LENS_L = 30.0, 42.0
LENS_FRONT = FX - 8.0                             # the lens front sits 8 mm behind the hood face, like the original's recessed front element
HQ_KG, LENS_KG = 0.050, 0.049                     # retailer figures; the CS variant of the HQ camera is assumed to weigh the same as the listed M12 one
HOOD_ANGLE = 0.0                                  # the window of the hood is square to the box (the flight photo [S5] Fig. 8 shows it turned a few degrees; the CAD figure does not)


def camera():
    """HQ camera, CS lens, printed slotted baffle ring and hood, looking +x. Returns {group: shape}."""
    x_m1 = LENS_FRONT - LENS_L                    # lens back = mount front face
    x_p1 = x_m1 - HQ_RING_L                       # board front face
    x_p0 = x_p1 - HQ_T
    pcb = box(x_p0, x_p1, CY - HQ_PCB / 2, CY + HQ_PCB / 2, AZ - HQ_PCB / 2, AZ + HQ_PCB / 2)
    for sy in (-1, 1):
        for sz in (-1, 1):
            pcb = pcb - cyl_x(x_p0 - 1, x_p1 + 1, CY + sy * 15.0, AZ + sz * 15.0, 1.25)
    ring = cyl_x(x_p1, x_m1, CY, AZ, HQ_RING_D / 2)
    rear = box(x_p0 - HQ_REAR, x_p0, CY - 11.0, CY + 11.0, AZ - 14.0, AZ - 8.0)       # FPC connector block, ASSUMPTION
    body = pcb + ring + rear
    lens = cyl_x(x_m1, LENS_FRONT, CY, AZ, LENS_D / 2) - cyl_x(LENS_FRONT - 1.0, LENS_FRONT + 1.0, CY, AZ, 9.0)   # barrel with a recessed glass
    r0 = ENC_X1                                   # baffle ring from the box cover to the hood
    r1 = FX - 3.5
    bring = cyl_x(r0, r1, CY, AZ, 18.5) - cyl_x(r0 - 1.0, r1 + 1.0, CY, AZ, 15.6)
    for k in range(36):
        a = math.radians(k * 10)
        bring = bring - Pos(r1 - 4.5, CY + 17.0 * math.cos(a), AZ + 17.0 * math.sin(a)) * Rot(a * 180 / math.pi, 0, 0) * Box(9, 2.2, 3.0)
    hood = cyl_x(FX - 12.0, FX, CY, AZ, 20.5) - cyl_x(FX - 13.0, FX - 3.0, CY, AZ, 18.8)
    hood = hood - Pos(FX - 1.5, CY, AZ) * Rot(HOOD_ANGLE, 0, 0) * Box(6, 24, 24)       # square window
    return {"camera body": body, "lens": lens, "baffle": bring, "hood": hood}


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
    for sx in (-1, 1):                                                                                   # the servo's four front-face holes: 20.5 across, 25.4 along, 7.4 and 32.8 from the shaft (Waveshare drawing)
        for dz in (7.4, 32.8):
            out = out - cyl_y(BR_WEB_Y0 - 1, BR_WEB_Y1 + 1, TX + sx * 10.25, AZ - dz, 1.7)
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
    ys0, ys1 = CY + hy - ENC_WALL - 1.0, CY + hy + 1.0                                                  # the +y side wall carries the disk
    base = base - cyl_y(ys0, ys1, TX, AZ - 8.0, 7.0)                                                    # Ø14 cable hole
    for sx in (-1, 1):
        for sz in (-1, 1):
            base = base - cyl_y(ys0, ys1, TX + sx * 12.7, AZ + sz * 12.7, 1.7)                           # four M3 clearance holes on a Ø36 circle (into threads tapped in the disk's ring)
    for sy in (-1, 1):
        for sz in (-1, 1):
            post = cyl_x(x0 + ENC_WALL - 0.1, xj, CY + sy * 26.0, AZ + sz * 23.0, 5.5)
            base = base + post
            cover = cover + cyl_x(x1, x1 + 1.5, CY + sy * 26.0, AZ + sz * 23.0, 3.4)      # M4 cover screw heads
    return base + cover


DISK_D = 40.0


def disk(y_box):
    """The disk between the camera box and the tilt servo: the structural coupling and the cable spool, a hollow turned aluminium shell (6061 bar, 4 mm side wall, 2 mm end wall) that rotates with the camera.
    Box end open and bolted to the box wall (four M3 tapped straight into the shell's ring, on a Ø36 circle); servo end closed, with a Ø19.2 boss that sits on the servo horn
    (four screws on the horn's Ø14 pattern, one centre screw). The camera ribbon comes through the box wall's Ø14 hole into the shell and leaves through a slot in the rim at the bottom,
    loops round the rim (the rim is the spool: the tilt is +-90 degrees, so the cable length changes by about 31 mm) and is clamped to the bracket's fin edge. An annular recess round the
    boss clears the servo's four screw heads. The servo's own magnetic encoder gives the tilt angle, so the disk carries no sensor. A tilt hard stop is not designed."""
    y_end = BR_WEB_Y0 - 3.0 + 0.0                                                      # shell end wall's outer face; the boss runs on to the horn face
    y_horn = BR_WEB_Y0 - 0.5
    shell = cyl_y(y_box, y_end, TX, AZ, DISK_D / 2) - cyl_y(y_box - 1.0, y_end - 2.0, TX, AZ, 16.0)               # hollow, open at the box end, 2 mm end wall, 4 mm side wall
    boss = cyl_y(y_end - 1.0, y_horn, TX, AZ, 9.6)
    shell = shell + boss
    for sx in (-1, 1):                                                                 # horn screws, Ø14 pattern
        shell = shell - cyl_y(y_end - 4.0, y_horn + 1.0, TX + sx * 7.0, AZ, 1.4) - cyl_y(y_end - 4.0, y_horn + 1.0, TX, AZ + sx * 7.0, 1.4)
    shell = shell - cyl_y(y_end - 4.0, y_horn + 1.0, TX, AZ, 2.0)
    shell = shell - box(TX - 9.0, TX + 9.0, y_box + 3.0, y_box + 9.0, AZ - DISK_D / 2 - 1.0, AZ - 12.0)            # cable slot in the rim, bottom
    return shell


def head(z_ext=Z_EXT):
    """All head parts in the rover frame: bracket, tilt servo, disk, enclosure, hat and the camera stack. Rotating column: T-slot to z 597, the bracket on its end."""
    parts = {}
    parts["bracket"] = bracket()
    tilt = Pos(TX, 38.1, AZ) * Rot(-90, 0, 0) * Rot(0, 0, 90) * H.sts3215()
    parts["tilt servo"] = tilt
    box_y_max = CY + ENC_Y / 2
    parts["disk"] = disk(box_y_max)
    parts["enclosure"] = enclosure()
    xc = ENC_X1 - ENC_X / 2
    hz = AZ + ENC_Z / 2                                                                                     # top of the box (z 696); the flat hat sits on the cover's top face up to z 700
    parts["antenna hat"] = Pos(xc, CY, hz + 2.0) * Cylinder(35.0, 4.0)
    c = camera()
    parts["camera body"], parts["lens"], parts["baffle"], parts["hood"] = (c[k] for k in ("camera body", "lens", "baffle", "hood"))
    return parts


TILTING = ("disk", "enclosure", "antenna hat", "camera body", "lens", "baffle", "hood")
