"""al-maha mass budget and centre-of-mass check.

Little about the original's mass split is published, so this is built
to show what is sourced, what is assumed, and how much of the 10 kg is still
unallocated. The unallocated remainder is placed at three bounding heights
inside the body to give a CoM range, not a CoM.

Frame as in body.py: X forward, Y left, Z up from the ground (rim line).
Masses in kg, lengths in mm.

Run:  .venv/bin/python hardware/mass/budget.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "body"))
import body as B  # noqa: E402

TOTAL = 10.0            # design mass, incl. payload              stated [S1][S2][S3]
SLOPE_LIMIT = 20.0      # degrees                                 stated [S1][S3]

# (name, kg, status/source, (x, y, z) mm for deployed, stowed override or None)
BODY_CENTROID_Z = B.body()[0].center().Z
items = [
    ("wheels x4", 4 * 0.398, "ASSUMPTION: 398 g from wheel.py at AZ91E density; closed test wheel 1.18 kg [S4] is not the flight wheel", None),
    ("mast + gimbal", 1.237, "stated [S19]: 1.237 kg EM, < 1.4 kg flight; assumed to exclude CAM-1", None),
    ("CAM-1", 0.210, "stated [S12]", None),
    ("structure", 2.0, "stated [S26]: 2 kg for the mechanical structure, excluding the mobility subsystem; placed at the body envelope centroid (ASSUMPTION)", None),
    ("CAM-2", 0.210, "stated [S12]; position: rear, axis 250 high (stated), x assumed at body rear", None),
]


def positions(stowed):
    """Item centres of mass. Wheels at the hubs; mast at the tube midpoint."""
    wheels = [(sx * B.WHEELBASE / 2, sy * B.TRACK / 2, B.HUB_Z) for sx in (1, -1) for sy in (1, -1)]
    if stowed:
        mast = (B.MAST_X - 176.0, 0.0, B.DECK_TOP_Z + B.HEAD_W / 2)
        cam1 = (B.MAST_X - 302.0, B.CAM_Y, B.DECK_TOP_Z + B.HEAD_W / 2 + 43.0)
    else:
        mast = (B.MAST_X, 0.0, (B.DECK_TOP_Z + B.TOP_Z) / 2)
        cam1 = (B.CAM_X, B.CAM_Y, B.CAM_AXIS_Z)
    cam2 = (B.BODY_X0 - B.SIDE_PLATE_LEN / 2, 0.0, 250.0)
    struct = (B.BODY_X0, 0.0, BODY_CENTROID_Z)
    return {"structure": [struct], "wheels x4": wheels, "mast + gimbal": [mast], "CAM-1": [cam1], "CAM-2": [cam2]}


def com(stowed, remainder_z):
    pos = positions(stowed)
    m_tot = x = y = z = 0.0
    for name, kg, _, _ in items:
        pts = pos[name]
        for (px, py, pz) in pts:
            w = kg / len(pts)
            m_tot += w; x += w * px; y += w * py; z += w * pz
    rem = TOTAL - sum(i[1] for i in items)
    # remainder in the body, centred in plan, at the given height
    m_tot += rem; x += rem * B.BODY_X0; y += 0.0; z += rem * remainder_z
    return m_tot, (x / m_tot, y / m_tot, z / m_tot), rem


def tip_angles(c):
    """Static tip-over angles about the wheel contact lines, degrees."""
    x, y, z = c
    half_b = B.WHEELBASE / 2 + 0.0          # contact at the hub line, rim at ground
    half_t = B.TRACK / 2 + 40.0             # outer wheel face
    return {
        "nose-down (descending)": math.degrees(math.atan((half_b + x) / z)),
        "nose-up (climbing)": math.degrees(math.atan((half_b - x) / z)),
        "sideways": math.degrees(math.atan((half_t - abs(y)) / z)),
    }


if __name__ == "__main__":
    body_c = B.body()[0].center()
    print(f"body envelope centroid z = {body_c.Z:.0f} mm (solid wedge, deck included)\n")
    print("| Item | kg | Status |\n|---|---|---|")
    for n, kg, s, _ in items:
        print(f"| {n} | {kg:.3f} | {s} |")
    rem = TOTAL - sum(i[1] for i in items)
    print(f"| Unallocated: battery, electronics, drive motors and differential, harness, panels and MLI if not in the 2 kg, other instruments | {rem:.2f} | (unverified): the rest of the stated 10 kg [S1] |")
    print(f"| **Total** | **{TOTAL:.2f}** | stated [S1] |\n")

    cases = {"low (z=150)": 150.0, f"body centroid (z={body_c.Z:.0f})": body_c.Z, "high (z=300)": 300.0}
    print(f"| Configuration | Remainder height | CoM x | CoM z | nose-down | nose-up | sideways |\n|---|---|---|---|---|---|---|")
    for stowed in (False, True):
        for label, rz in cases.items():
            _, c, _ = com(stowed, rz)
            t = tip_angles(c)
            print(f"| {'stowed' if stowed else 'deployed'} | {label} | {c[0]:.0f} | {c[2]:.0f} | "
                  f"{t['nose-down (descending)']:.0f} | {t['nose-up (climbing)']:.0f} | {t['sideways']:.0f} |")
    print(f"\nSlope requirement: {SLOPE_LIMIT:.0f} degrees [S1][S3]. Tip angles are static, on a rigid chassis, wheels at the hub line.")
