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


def octagon(x, y, z0, z1, across, wall=2.0):
    def solid(a):
        return Pos(x, y, (z0 + z1) / 2) * (Box(a, a, z1 - z0) + Rot(0, 0, 45) * Box(a, a, z1 - z0))
    return solid(across) - Pos(0, 0, 0) * solid(across - 2 * wall) if False else solid(across) - Pos(0, 0, wall) * solid(across - 2 * wall)


def head():
    """Layout from the owner's reading of the CAD figure and the flight photo: hollow octagonal mast, a lateral overhang to +y, the tilt servo in a pocket
    on the outer (+y) face at the top of the overhang, a sideways disk (encoder or mount) between the overhang and the camera enclosure, a roughly
    cube-shaped enclosure with the lens assembly on its front, and a flat round antenna hat on top that tilts with the camera."""
    from build123d import Plane, Polygon, extrude
    parts = {}
    z0, z1 = MAST.TUBE_Z1, 620.0
    parts["mast"] = octagon(TX, 0.0, z0, z1, MAST.TUBE_W)
    pts = [(-29.0, z1), (70.0, z1), (70.0, 697.0), (20.0, 697.0), (20.0, 650.0), (-29.0, 650.0)]      # overhang profile in (y, z); solid placeholder
    over = Pos(TX - 27.0, 0, 0) * extrude(Plane.YZ * Polygon(*pts, align=None), amount=54.0)
    over = over - box(TX - 24.0, TX + 24.0, 27.0, 71.0, 623.0, 674.0)                                # pocket for the tilt servo, open to +y
    parts["overhang"] = over
    tilt = Pos(TX, 47.5, AZ) * Rot(-90, 0, 0) * Rot(0, 0, 90) * H.sts3215()
    pan = Pos(TX, 0, z0 + H.WALL + H.SV_TOTAL / 2) * Rot(0, 0, 90) * H.sts3215()
    parts["servos"] = tilt + pan
    parts["disk"] = cyl_y(2.0, 20.0, TX, AZ, 23.0)                                                   # sideways disk, encoder or mounting, ASSUMPTION
    x_face = FX - 22.0
    cube = H.hollow(x_face - 60.0, x_face, CY - 30.0, CY + 30.0, AZ - 30.0, AZ + 30.0)               # roughly cubic enclosure, 60 mm, ASSUMPTION
    cube = cube - cyl_x(x_face - 3.0, x_face + 1.0, CY, AZ, 17.5)
    for sy in (-1, 1):
        for sz in (-1, 1):
            cube = cube + cyl_x(x_face, x_face + 2.0, CY + sy * 25.0, AZ + sz * 25.0, 2.8)           # corner screw heads
    parts["enclosure"] = cube
    parts["antenna hat"] = Pos(x_face - 30.0, CY, AZ + 30.0 + 3.5) * Cylinder(35.0, 7.0) + \
        (Pos(x_face - 30.0, CY, AZ + 30.0 + 8.5) * Cylinder(35.0, 3.0) - Pos(x_face - 30.0, CY, AZ + 30.0 + 8.5) * Cylinder(31.5, 3.2))
    c = caspex()
    parts["camera body"], parts["cradle"], parts["collar"], parts["baffle"], parts["hood"] = (c[k] for k in ("camera body", "cradle", "collar", "baffle", "hood"))
    return parts


COL = {"mast": (214, 217, 222), "overhang": (200, 160, 170), "servos": (60, 100, 190), "disk": (190, 100, 90), "enclosure": (236, 236, 232), "antenna hat": (200, 204, 208), "camera body": (214, 175, 60),
       "cradle": (240, 240, 236), "collar": (232, 232, 228), "baffle": (150, 154, 160), "hood": (28, 28, 32)}
NAMES = {"mast": "octagonal hollow mast", "overhang": "overhang (solid placeholder, MLI pink)", "servos": "STS3215 pan and tilt servos", "disk": "sideways disk (encoder or mount)", "enclosure": "camera enclosure", "antenna hat": "planar antenna hat",
         "camera body": "3DCM739 module", "cradle": "cradle plate (45 mm)", "collar": "collar", "baffle": "slotted baffle ring and lens", "hood": "black hood, square window"}


def main():
    parts = head()
    ms = []
    for g, sh in parts.items():
        v, t = R.mesh(sh, 0.25, 0.3)
        ms.append((g, v, t, COL[g]))
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
