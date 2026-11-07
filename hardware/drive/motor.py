"""al-maha drive motor: placement and clearance check inside the wheel hub.

Placeholder for a 37 mm planetary DC gearmotor WITHOUT encoder. The dimensions
are typical-class values from memory, not a datasheet: check them against the
part chosen, then update them here.

Wheel frame as in wheel.py: axle along Z, centred on the origin, wheel spans
z = +-40, hub tube z = +-20. The motor body is fixed to the suspension arm
(inboard end, -Z); the wheel is driven from the output shaft (outboard, +Z).

Run:  .venv/bin/python hardware/drive/motor.py
"""
import sys
from pathlib import Path

from build123d import Cylinder, Pos

sys.path.insert(0, str(Path(__file__).parent.parent / "wheel"))
import wheel as W  # noqa: E402

MOTOR_D = 37.0           # body diameter                          ASSUMPTION (37D class)
MOTOR_LEN = 65.0         # body length, gearbox + motor, no
                         # encoder                                ASSUMPTION
SHAFT_D, SHAFT_LEN = 6.0, 15.0   # output shaft                   ASSUMPTION
SHAFT_END_Z = W.WIDTH / 2 - 3.0  # shaft tip, 3 mm inside the wheel's outer face
MOTOR_MASS = 0.20        # kg, each                               ASSUMPTION


def build_motor():
    z_out = SHAFT_END_Z - SHAFT_LEN              # gearbox face (outboard end of the body)
    body = Pos(0, 0, z_out - MOTOR_LEN / 2) * Cylinder(MOTOR_D / 2, MOTOR_LEN)
    shaft = Pos(0, 0, z_out + SHAFT_LEN / 2) * Cylinder(SHAFT_D / 2, SHAFT_LEN)
    return body + shaft, z_out


if __name__ == "__main__":
    motor, z_out = build_motor()
    wheel = W.build_wheel()
    bore_r = W.HUB_D / 2 - W.HUB_WALL
    inner_end = z_out - MOTOR_LEN
    overlap = (motor & wheel).volume
    print(f"motor body z   : {inner_end:.1f} .. {z_out:.1f}   (wheel inner face z = {-W.WIDTH / 2:.0f})")
    print(f"protrudes inboard of the wheel by {max(0.0, -W.WIDTH / 2 - inner_end):.1f} mm")
    print(f"hub bore radius: {bore_r:.1f}   motor radius {MOTOR_D / 2:.1f}   radial gap {bore_r - MOTOR_D / 2:.1f} mm")
    print(f"overlap with the wheel solid: {overlap:.1f} mm3 (want 0)")
    print(f"free bore for a bearing between hub and motor body: wall {(bore_r - MOTOR_D / 2):.1f} mm "
          f"(even thin-section bearings need about 6 mm of radial space)")
