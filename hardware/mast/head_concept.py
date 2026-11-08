"""al-maha mast head, concept B: the layout seen in the CAD figures ([S5] Fig. 1; original-dimensions.md 3l), as a rough model for the owner to judge.

Differences from head.py: an open frame (two vertical arm plates and a thin top plate) instead of closed shells; the camera is a CASPEX stack
(module, square cradle plate, round collar, slotted baffle ring, black hood with a square window) hung off a round gimbal drive by a bracket, with its
hood standing out in front of the head. Sizes: whole camera 35 x 35 x 73 mm [S12] (module 25.2 mm of that, 3DDS-0734); cradle plate 45 mm square, collar,
ring, hood and bracket sizes are read by eye from the photos and the CAD figure (ASSUMPTION). Run:  .venv/bin/python hardware/mast/head_concept.py
"""
import math
import sys
from pathlib import Path

from build123d import Box, Cylinder, Pos, Rot

HERE = Path(__file__).parent
for sub in ("body", "mast", "assembly", "suspension", "wheel", "drive", "chassis"):
    sys.path.insert(0, str(HERE.parent / sub))
import head as H            # noqa: E402
import mast as MAST         # noqa: E402
import rover as R           # noqa: E402

TX, CY, AZ, FX = MAST.TUBE_X, MAST.CAM_Y, MAST.CAM_AXIS_Z, MAST.CAM_FRONT_X
box = H._box


def cyl_x(x0, x1, y, z, r):
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(r, x1 - x0)


def cyl_y(y0, y1, x, z, r):
    return Pos(x, (y0 + y1) / 2, z) * Rot(90, 0, 0) * Cylinder(r, y1 - y0)


def caspex():
    """Module + plate + collar + baffle ring + hood, lens looking +x, lens front at FX. Returns {group: shape}."""
    x_back = FX - 73.0
    mod = box(x_back, x_back + 25.2, CY - 17.5, CY + 17.5, AZ - 17.5, AZ + 17.5)                  # 35 x 35 x 25.2 over the pins
    xp0 = x_back + 25.2
    plate = box(xp0, xp0 + 4, CY - 22.5, CY + 22.5, AZ - 22.5, AZ + 22.5)                          # 45 square cradle, ASSUMPTION
    for sy in (-1, 1):
        for sz in (-1, 1):
            plate = plate - cyl_x(xp0 - 1, xp0 + 5, CY + sy * 19.5, AZ + sz * 19.5, 1.6)           # corner holes
    collar = cyl_x(xp0 + 4, xp0 + 24, CY, AZ, 16.0)                                                # round collar, ASSUMPTION
    ring0 = xp0 + 24
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
    z0 = MAST.TUBE_Z1
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
    web = web - box(TX - 18.0, TX + 18.0, BR_Y1 - t - 1, BR_Y1 + 1, 645.0, 690.0)             # window over the tilt servo
    fl = [(-20.0, zl), (-20.0, z0), (27.0, z0 + 47.0), (27.0, 689.0), (35.0, 697.0), (BR_Y1, 697.0), (BR_Y1, z0 + BR_Y1 - 20.0), (20.0, z0), (20.0, zl)]
    out = web
    for x0 in (TX - 22.0, TX + 20.0):
        f = _flange(x0, fl)
        for zz in (zl + 10.0, zl + 24.0):
            f = f - cyl_x(x0 - 1, x0 + t + 1, 0.0, zz, 3.4)                               # M6 clearance into the side-slot T-nuts
        out = out + f
    return out


def head():
    """Version 3 (owner's rule, 2026-11-07: keep the silhouette-defining features that cost nothing, otherwise design for our parts).
    Rotating column: T-slot to z 577, a flat adapter plate on it reaching out to +y, an arm of printed shell on the +y side holding the tilt servo (visible
    through a window on the outer face), a sideways disk, the camera enclosure with the CASPEX lens assembly on its front and the flat round hat on top.
    The plate is only 6 mm thick under the camera, so the enclosure's corners swing clear of it; the arm stays out of the enclosure's y range."""
    parts = {}
    parts["bracket"] = bracket()
    tilt = Pos(TX, 47.5, AZ) * Rot(-90, 0, 0) * Rot(0, 0, 90) * H.sts3215()
    parts["servos"] = tilt
    parts["disk"] = cyl_y(2.0, 22.0, TX, AZ, 23.0)                                      # sideways disk, encoder or mounting, ASSUMPTION
    x_face = FX - 22.0
    cube = H.hollow(x_face - 60.0, x_face, CY - 30.0, CY + 30.0, AZ - 30.0, AZ + 30.0)  # roughly cubic enclosure, 60 mm, ASSUMPTION
    cube = cube - cyl_x(x_face - 3.0, x_face + 1.0, CY, AZ, 17.5)
    for sy in (-1, 1):
        for sz in (-1, 1):
            cube = cube + cyl_x(x_face, x_face + 2.0, CY + sy * 25.0, AZ + sz * 25.0, 2.8)
    parts["enclosure"] = cube
    hz = AZ + 30.0
    parts["antenna hat"] = Pos(x_face - 30.0, CY, hz + 3.5) * Cylinder(35.0, 7.0) + \
        (Pos(x_face - 30.0, CY, hz + 8.5) * Cylinder(35.0, 3.0) - Pos(x_face - 30.0, CY, hz + 8.5) * Cylinder(31.5, 3.2))
    c = caspex()
    parts["camera body"], parts["cradle"], parts["collar"], parts["baffle"], parts["hood"] = (c[k] for k in ("camera body", "cradle", "collar", "baffle", "hood"))
    return parts


TILTING = ("disk", "enclosure", "antenna hat", "camera body", "cradle", "collar", "baffle", "hood")


def tilt_check(parts):
    """Sweep the tilting unit (disk, enclosure, hat, camera) about the tilt axis against the fixed parts: adapter plate, arm, tilt servo, extrusion."""
    from build123d import Axis, Compound
    ax = Axis((TX, 0, AZ), (0, 1, 0))
    unit = Compound([parts[n] for n in TILTING])
    fixed = {"bracket": parts["bracket"], "tilt servo": parts["servos"], "extrusion": Pos(TX, 0, (446.0 + MAST.TUBE_Z1) / 2) * Box(40, 40, MAST.TUBE_Z1 - 446.0)}
    print("tilt sweep, the whole camera head about the tilt axis, overlap with fixed parts (mm3 > 1 counts as contact):")
    for sgn, nm in ((1, "positive (nose down?)"), (-1, "negative")):
        first = None
        who = None
        for deg in range(0, 91, 5):
            u = unit.rotate(ax, sgn * deg)
            hit = {k: (lambda r: 0.0 if r is None else r.volume)(u & f) for k, f in fixed.items()}
            tot = sum(hit.values())
            if tot > 1.0 and first is None:
                first, who = deg, {k: round(v) for k, v in hit.items() if v > 1.0}
        print(f"  {nm}: first contact at {first if first is not None else 'none up to 90'} degrees {who or ''}")
    ub = unit.bounding_box()
    print(f"  unit z {ub.min.Z:.0f}..{ub.max.Z:.0f}; lowest corner at 75 degrees about z {AZ - math.hypot(37.7, 30.0) :.0f}; top of the extrusion z {MAST.TUBE_Z1:.0f}")
    kg = (parts["enclosure"].volume + parts["antenna hat"].volume) / 1e6 * 1.27
    al = parts["bracket"].volume / 1e6 * 2.68
    print(f"  bracket (2 mm aluminium) {al:.3f} kg; printed enclosure and hat {kg:.3f} kg; bracket valid {parts['bracket'].is_valid}")


COL = {"bracket": (170, 176, 184), "servos": (60, 100, 190), "disk": (190, 100, 90), "enclosure": (236, 236, 232), "antenna hat": (200, 204, 208), "camera body": (214, 175, 60),
       "cradle": (240, 240, 236), "collar": (232, 232, 228), "baffle": (150, 154, 160), "hood": (28, 28, 32)}
NAMES = {"bracket": "bent sheet bracket (2 mm Al)", "servos": "STS3215 tilt servo", "disk": "sideways disk (encoder or mount)", "enclosure": "camera enclosure", "antenna hat": "planar antenna hat",
         "camera body": "3DCM739 module", "cradle": "cradle plate (45 mm)", "collar": "collar", "baffle": "slotted baffle ring and lens", "hood": "black hood, square window"}


def main():
    parts = head()
    ms = []
    for g, sh in parts.items():
        v, t = R.mesh(sh, 0.25, 0.3)
        ms.append((g, v, t, COL[g]))
    tilt_check(parts)
    leg = [(NAMES[g], COL[g]) for g in parts]
    size = (760, 620)
    views = [("Front left (hood towards the viewer)", 35, 14, 1.0), ("Straight on, from the front", 0, 0, 1.0),
             ("Side, from the right", -90, 0, 1.0), ("From the rear left", 215, 20, 1.0)]
    imgs = [R.render(ms, az, el, size, label=lab, zoom=z, legend=leg if i == 0 else (), legend_left=True) for i, (lab, az, el, z) in enumerate(views)]
    from PIL import Image
    sheet = Image.new("RGB", (2 * size[0] + 36, 2 * size[1] + 36), (255, 255, 255))
    for k, im in enumerate(imgs):
        r, c = divmod(k, 2)
        sheet.paste(im, (12 + c * (size[0] + 12), 12 + r * (size[1] + 12)))
    out = HERE.parent.parent / "docs" / "images" / "head-concept.png"
    sheet.save(out)
    bb = Compound_bb(parts)
    print("saved", out, sheet.size, bb)


def Compound_bb(parts):
    from build123d import Compound
    b = Compound(list(parts.values())).bounding_box()
    return f"x {b.min.X:.0f}..{b.max.X:.0f} y {b.min.Y:.0f}..{b.max.Y:.0f} z {b.min.Z:.0f}..{b.max.Z:.0f}"


if __name__ == "__main__":
    main()
