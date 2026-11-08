"""al-maha mast head: the neck, C-arm, camera housing and camera tube as hollow printed shells holding real servos and a camera module.

Replaces the solid boxes of the first mast model. Everything printed is a 2 mm wall shell (ASSUMPTION: material PETG, solid walls); the outer sizes follow
the CAD figures (original-dimensions.md 3j) as before. Inside:
  * pan servo   Feetech STS3215-class, shaft vertical on the mast axis, in the neck
  * tilt servo  the same, shaft along Y at the camera axis height, in the C-arm
  * camera      Raspberry Pi Camera Module 3 (standard lens) in the CAM-1 tube (35 x 35 x 73 mm [S12])

The servo is modelled from the Waveshare ST3215 drawing (2D drawing rev 2022-06-08) and its STEP model, which has the same 45.2 x 24.7 x 35 mm outline as the
Feetech STS3215 in the retailers' listings and the Feetech datasheet (the equivalence is assumed; the Feetech datasheet read has no drawing):
  body 45.22 x 24.72 x 32 mm; the output shaft is 10.11 mm from one end of the long side; a 19.2 mm horn disc at each end of the shaft, 37.25 mm over both.
  The mounting ears and horn hole patterns are not modelled (the horn holes are a 14 mm pattern on the drawing).
The camera module is modelled from the Camera Module 3 product brief p. 4: PCB 25 x 23.862 x 1.12 mm, four 2.2 mm holes, lens block 10.8 mm square, 11.3 mm total
with the standard lens; the lens centre is 12.5 mm from one side and 14.4 mm from the bottom edge. The FPC connector block is ASSUMPTION.

Run:  .venv/bin/python hardware/mast/head.py
"""
import math
import sys
from pathlib import Path

from build123d import Box, Compound, Cylinder, Pos, Rot

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "body"))
import body as B  # noqa: E402

WALL = 2.0               # printed shell wall                                  ASSUMPTION
PETG = 1.27              # g/cm3
SERVO_MASS = 0.055       # kg, retailers' figure (docs/electronics-spec.md)
MODULE_MASS = 0.004      # kg, ASSUMPTION (not found)


def _box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def hollow(x0, x1, y0, y1, z0, z1, wall=WALL):
    return _box(x0, x1, y0, y1, z0, z1) - _box(x0 + wall, x1 - wall, y0 + wall, y1 - wall, z0 + wall, z1 - wall)


# ---- servo ----------------------------------------------------------------------------------
SV_L, SV_W, SV_T = 45.22, 24.72, 32.0          # body: long side, width, thickness along the shaft   [Waveshare drawing]
SV_END = 10.11                                 # shaft to the near end of the long side               [drawing]
SV_HORN_D, SV_HORN_T = 19.2, 2.6               # horn disc at each end, 37.25 over both               [drawing]
SV_TOTAL = SV_T + 2 * SV_HORN_T                # 37.2


def sts3215():
    """Servo in its own frame: output shaft = the z axis through the origin; the body runs along +x from -10.11 to +35.11, y +-12.36, z +-16."""
    body = _box(-SV_END, SV_L - SV_END, -SV_W / 2, SV_W / 2, -SV_T / 2, SV_T / 2)
    horn_a = Pos(0, 0, SV_T / 2 + SV_HORN_T / 2) * Cylinder(SV_HORN_D / 2, SV_HORN_T)
    horn_b = Pos(0, 0, -SV_T / 2 - SV_HORN_T / 2) * Cylinder(SV_HORN_D / 2, SV_HORN_T)
    return body + horn_a + horn_b


# ---- camera module ----------------------------------------------------------------------------
def camera_module(x_front, cy, cz):
    """Camera Module 3 (standard lens) in the world frame with the lens looking +x: the lens front at x_front, the lens centre on (cy, cz).
    The PCB lies in the y-z plane."""
    PCB_W, PCB_H, PCB_T = 25.0, 23.862, 1.12
    LENS_X, LENS_Y = 12.5, 14.4                  # lens centre from one side edge and from the bottom edge   [brief]
    total = 11.3                                 # standard lens                                              [brief]
    x_pcb_back = x_front - total
    def yz(u, v):                                # board (u along y, v along z) to world offsets from the lens centre
        return cy + (u - LENS_X), cz + (v - LENS_Y)
    y0, z0 = yz(0, 0)
    solid = _box(x_pcb_back, x_pcb_back + PCB_T, y0, y0 + PCB_W, z0, z0 + PCB_H)
    ly, lz = yz(LENS_X, LENS_Y)
    solid = solid + _box(x_pcb_back + PCB_T, x_pcb_back + PCB_T + 2.75, ly - 5.4, ly + 5.4, lz - 5.4, lz + 5.4)        # 10.8 square block
    solid = solid + Pos(x_pcb_back + PCB_T + 2.75 + (total - PCB_T - 2.75) / 2, ly, lz) * Rot(0, 90, 0) * Cylinder(2.875, total - PCB_T - 2.75)   # barrel, 5.75 mm
    ucon, vcon = yz(12.5, 4.0)                   # FPC connector on the back, ASSUMPTION
    solid = solid + _box(x_pcb_back - 5.71, x_pcb_back, ucon - 4.45, ucon + 4.45, vcon - 2.0, vcon + 2.0)
    for (u, v) in ((2.0, 2.0), (23.0, 2.0), (2.0, 16.5), (23.0, 16.5)):                                                  # 2.2 mm holes
        hy, hz = yz(u, v)
        solid = solid - Pos(x_pcb_back + PCB_T / 2, hy, hz) * Rot(0, 90, 0) * Cylinder(1.1, PCB_T + 2.0)
    return solid


def build(tube_x, neck_z0, neck_z1, top_z, tube_w, arm_x, arm_y0, arm_y1, head_x, head_y, cam_y, cam_axis_z, cam_front_x, cam_tube):
    """All head parts in the rover frame. Parts: neck, arm, head (printed shells); camera_tube (printed shell); pan_servo, tilt_servo, camera_module.
    Returns (parts, axes) where axes holds the pan axis (x, y) and the tilt axis (x, z)."""
    neck_y0, neck_y1 = -tube_w / 2, arm_y1
    neck = hollow(tube_x - tube_w / 2, tube_x + tube_w / 2, neck_y0, neck_y1, neck_z0, neck_z1)
    neck = neck - Pos(tube_x, 0, neck_z1) * Cylinder(SV_HORN_D / 2 + 1.0, 2 * WALL + 1.0)                 # hole in the top for the horn
    arm_z1 = top_z - 10.0
    arm = hollow(tube_x - arm_x / 2, tube_x + arm_x / 2, arm_y0, arm_y1, neck_z1, arm_z1)
    hx0, hx1 = tube_x - head_x / 2, tube_x + head_x / 2
    head = hollow(hx0, hx1, cam_y - head_y / 2, cam_y + head_y / 2, neck_z1, top_z)
    ct_l, ct_w, ct_h = cam_tube
    ct_x1 = cam_front_x
    ct_x0 = ct_x1 - ct_l
    head = head - _box(hx1 - WALL - 1.0, hx1 + 1.0, cam_y - ct_w / 2 - 0.5, cam_y + ct_w / 2 + 0.5, cam_axis_z - ct_h / 2 - 0.5, cam_axis_z + ct_h / 2 + 0.5)   # front window for the tube
    tube = hollow(ct_x0, ct_x1, cam_y - ct_w / 2, cam_y + ct_w / 2, cam_axis_z - ct_h / 2, cam_axis_z + ct_h / 2)
    tube = tube - Pos(ct_x1 - WALL / 2, cam_y, cam_axis_z) * Rot(0, 90, 0) * Cylinder(6.0, WALL + 1.0)  # lens aperture, 12 mm
    # pan servo: shaft vertical on the mast axis, the long side towards +y; bottom horn on the neck floor
    pan_zc = neck_z0 + WALL + SV_TOTAL / 2
    pan = Pos(tube_x, 0, pan_zc) * Rot(0, 0, 90) * sts3215()
    # tilt servo: shaft along y at the camera axis height; body below the shaft (long side down), centred in the arm in y
    tilt_yc = (arm_y0 + arm_y1) / 2
    tilt = Pos(tube_x, tilt_yc, cam_axis_z) * Rot(-90, 0, 0) * Rot(0, 0, 90) * sts3215()
    cam = camera_module(ct_x1 - WALL, cam_y, cam_axis_z)
    parts = {"neck": neck, "arm": arm, "head": head, "camera": tube, "pan servo": pan, "tilt servo": tilt, "camera module": cam}
    return parts, {"pan": (tube_x, 0.0), "tilt": (tube_x, cam_axis_z)}


def shell_mass(shape):
    return shape.volume / 1e3 * PETG / 1000.0


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    import mast as M
    parts = M.parts()
    for n in ("neck", "arm", "head", "camera", "pan servo", "tilt servo", "camera module"):
        bb = parts[n].bounding_box()
        print(f"{n:14s} x {bb.min.X:7.1f}..{bb.max.X:7.1f}  y {bb.min.Y:7.1f}..{bb.max.Y:7.1f}  z {bb.min.Z:7.1f}..{bb.max.Z:7.1f}   valid {parts[n].is_valid}")
    M.head_checks(parts)
