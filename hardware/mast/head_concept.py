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


def head():
    parts = {}
    z_neck0, z_neck1 = MAST.TUBE_Z1, MAST.NECK_Z1
    w = MAST.TUBE_W
    neck = H.hollow(TX - w / 2, TX + w / 2, -w / 2, MAST.ARM_Y1, z_neck0, z_neck1)
    neck = neck - Pos(TX, 0, z_neck1) * Cylinder(H.SV_HORN_D / 2 + 1.0, 5.0)
    parts["neck"] = neck
    ax = MAST.ARM_X
    top_z = MAST.TOP_Z
    arm_in = box(TX - ax / 2, TX + ax / 2, 25.0, 28.5, z_neck1, top_z - 3)
    arm_out = box(TX - ax / 2, TX + ax / 2, 66.6, 70.0, z_neck1, top_z - 3)
    for z in (640.0, 670.0):                                                                       # lightening slots in the outer plate
        arm_out = arm_out - box(TX - 10, TX + 10, 60, 75, z - 8, z + 8) if False else arm_out
    arm_in = arm_in - cyl_y(24, 29, TX, AZ, 11.0)
    top = box(TX - 30.0, TX + 30.0, -60.0, 70.0, top_z - 3, top_z)                                 # thin top plate
    parts["arm"] = arm_in + arm_out + top
    # tilt servo in the arm (as head.py), round drive boss, bracket to the camera plate
    tilt = Pos(TX, 47.5, AZ) * Rot(-90, 0, 0) * Rot(0, 0, 90) * H.sts3215()
    pan = Pos(TX, 0, z_neck0 + H.WALL + H.SV_TOTAL / 2) * Rot(0, 0, 90) * H.sts3215()
    parts["servos"] = tilt + pan
    boss = cyl_y(8.0, 25.0, TX, AZ, 17.0)                                                          # round drive housing (red in the CAD figure)
    yoke = box(TX - 22, TX + 22, 2.0, 8.0, AZ - 25, AZ + 25)
    wing = box(TX - 20, FX - 73 + 25.2 + 4, CY + 22.5 - 0.0, 2.0, AZ - 25, AZ + 25)                # from the yoke across to the cradle plate
    parts["bracket"] = boss + yoke + wing
    parts.update(caspex())
    return parts


COL = {"neck": (214, 217, 222), "arm": (214, 217, 222), "servos": (60, 100, 190), "bracket": (190, 100, 90), "camera body": (214, 175, 60),
       "cradle": (240, 240, 236), "collar": (232, 232, 228), "baffle": (150, 154, 160), "hood": (28, 28, 32)}
NAMES = {"neck": "printed neck", "arm": "arm plates and top plate", "servos": "STS3215 pan and tilt servos", "bracket": "gimbal drive and camera bracket",
         "camera body": "3DCM739 module", "cradle": "cradle plate (45 mm, assumed)", "collar": "collar", "baffle": "slotted baffle ring and lens", "hood": "black hood, square window"}


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
