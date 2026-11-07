"""al-maha differential: loads, gear sizing, and a CAD envelope for the bevel gear train.

Decided 2026-11-07: the passive differential is a bevel gear differential (as [S25] says: "a passive differential gear"),
with the body as its carrier: two side gears, one on each pivot shaft, and two spider gears on a cross pin, all 1:1 mitre
gears. This script works out what the gears must carry, picks stock-size gears, and checks the envelope. The gears are
modelled as tooth-tip envelopes (cones and hubs), not involute teeth, so the mesh zone overlaps by design.

Loads. The ground thrust of the four wheels acts at the ground line, 145.7 mm below the pivot axis, so every newton of
thrust puts 0.1457 N.m of pitching moment into the arms, and the differential carries that moment into the body. Each side
gear carries the same torque T (a differential splits torque equally), and the carrier takes 2 T.

Run:  .venv/bin/python hardware/suspension/differential.py
"""
import math
import sys
from pathlib import Path

from build123d import Box, Compound, Cone, Cylinder, Pos, Rot

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "body"))
sys.path.insert(0, str(HERE.parent / "chassis"))
sys.path.insert(0, str(HERE.parent / "drive"))
sys.path.insert(0, str(HERE.parent / "wheel"))
import body as B       # noqa: E402
import arms as A       # noqa: E402

G = 9.81
WHEEL_R = 0.100          # m, rim radius (the ground line is the rim line)
PIVOT_H = A.PIVOT_Z / 1000.0     # m, pivot axis above the ground line
MASS = 9.24              # kg, replica estimate (docs/replica-mass.md)
SLOPE_DEG = 20.0
MOTOR_CAP_A = 1.6        # A per motor: the firmware cap this design assumes (about 1.5 N.m)
SIGMA_ALLOW = 200.0      # MPa bending, steel mitre gears: ASSUMPTION (depends on hardening; none verified)
SHAFT_OD, SHAFT_ID = 2 * A.SHAFT_R, A.SHAFT_ID


def motor_torque_nm(i_amp):
    """Gearmotor output torque at current i, from the datasheet's 0.2 A no-load and 0.74 A at 60 kg.mm (linear), N.m."""
    kgmm = (i_amp - 0.2) / ((0.74 - 0.2) / 60.0)
    return kgmm * 0.00981


def side_torque(tau_wheel):
    """Torque in each side gear when all four wheels deliver tau_wheel (N.m): thrust x pivot height, two wheels an arm."""
    f = tau_wheel / WHEEL_R
    return 2 * f * PIVOT_H


def lewis_y(z, cone_deg=45.0):
    zv = z / math.cos(math.radians(cone_deg))
    return math.pi * (0.154 - 0.912 / zv)


def stress(t_nm, m, z, b, spiders=2):
    rp = m * z / 2
    rm = rp - 0.5 * b * math.sin(math.radians(45))      # mean pitch radius along the face
    ft = t_nm * 1000.0 / rm                              # N on the side gear
    per_mesh = ft / spiders
    return rp, rm, ft, per_mesh / (b * m * lewis_y(z))


CASES = {
    "slope (all four wheels at the 20 degree torque)": MASS * G * math.sin(math.radians(SLOPE_DEG)) / 4 * WHEEL_R,
    f"firmware cap ({MOTOR_CAP_A} A a motor)": motor_torque_nm(MOTOR_CAP_A),
    "gearbox instantaneous limit (2.45 N.m, 2.45 A)": 2.45,
}

OPTIONS = [(1.0, 20, 7.0), (1.25, 16, 8.0), (1.5, 16, 8.0), (1.5, 18, 9.0), (2.0, 16, 10.0)]
CHOSEN = (1.5, 16, 8.0)     # module, teeth, face width: stock mitre gear with an 8 mm bore (RS PRO listing)


def build():
    m, z, b = CHOSEN
    rp = m * z / 2
    y1 = rp - b * math.sin(math.radians(45))
    tip = 1.0
    parts = {}
    # side gear on +Y (and mirror): teeth cone y1..rp, hub rp..rp+6
    def side(sy):
        cone = Cone(y1 + tip, rp + tip, rp - y1)
        cone = Pos(0, sy * (y1 + rp) / 2, 0) * Rot(-sy * 90, 0, 0) * cone
        hub = Pos(0, sy * (rp + 3), 0) * Rot(90, 0, 0) * Cylinder(9.0, 6.0)
        gear = cone + hub
        bore = Pos(0, sy * 12, 0) * Rot(90, 0, 0) * Cylinder(4.0, 40.0)
        return gear - bore
    def spider(sx):
        cone = Cone(y1 + tip, rp + tip, rp - y1)
        cone = Pos(sx * (y1 + rp) / 2, 0, 0) * Rot(0, sx * 90, 0) * cone
        hub = Pos(sx * (rp + 2.5), 0, 0) * Rot(0, 90, 0) * Cylinder(7.0, 5.0)
        gear = cone + hub
        bore = Pos(sx * 12, 0, 0) * Rot(0, 90, 0) * Cylinder(3.0, 30.0)
        return gear - bore
    parts["side gear +Y"], parts["side gear -Y"] = side(1), side(-1)
    parts["spider +X"], parts["spider -X"] = spider(1), spider(-1)
    parts["cross pin"] = Rot(0, 90, 0) * Cylinder(3.0, 2 * (A.DIFF_X / 2 - 1.0))
    # housing: box shell with bores for the shafts
    outer = Box(A.DIFF_X, A.DIFF_Y, A.DIFF_Z)
    inner = Box(A.DIFF_X - 6.0, A.DIFF_Y - 6.0, A.DIFF_Z - 6.0)
    shaft_bore = Rot(90, 0, 0) * Cylinder(4.2, A.DIFF_Y + 4.0)
    housing = outer - inner - shaft_bore
    parts["housing"] = housing
    return parts


if __name__ == "__main__":
    print("Loads (arithmetic): pivot axis %.1f mm above the ground line, wheel radius %.0f mm" % (A.PIVOT_Z, WHEEL_R * 1000))
    print(f"  {'case':50s}{'wheel torque':>13s}{'side-gear torque':>18s}")
    for name, tw in CASES.items():
        print(f"  {name:50s}{tw:10.2f} N.m{side_torque(tw):13.2f} N.m")
    print(f"  carrier (body) torque is twice the side torque; the cap is a design requirement (the driver board has no current limit; use its current sense)")

    print(f"\nGear options (mitre, 45 degree cones, two spiders, Lewis bending, allowable {SIGMA_ALLOW:.0f} MPa assumed)")
    print(f"  {'m':>4s}{'Z':>4s}{'b':>5s}{'pitch dia':>10s}  " + "".join(f"{c.split(' (')[0][:14]:>16s}" for c in CASES))
    for m, z, b in OPTIONS:
        row = f"  {m:4.2f}{z:4d}{b:5.1f}{m * z:9.1f} mm "
        for tw in CASES.values():
            row += f"{stress(side_torque(tw), m, z, b)[3]:13.0f} MPa"
        print(row + ("   <- chosen" if (m, z, b) == CHOSEN else ""))

    # shaft
    j = math.pi / 32.0 * (SHAFT_OD ** 4 - SHAFT_ID ** 4)
    for name, tw in list(CASES.items())[1:]:
        t = side_torque(tw) * 1000.0
        tau = t * (SHAFT_OD / 2) / j
        print(f"\nShaft {SHAFT_OD:.0f} mm tube, {SHAFT_ID:.0f} mm bore: shear {tau:.0f} MPa at {side_torque(tw):.1f} N.m; with a stress-concentration factor of 3 at the cross holes {3 * tau:.0f} MPa" if name.startswith("firmware") else
              f"  at the gearbox limit: {tau:.0f} MPa, with the factor {3 * tau:.0f} MPa (too high for plain steel: hence the cap)")

    parts = build()
    print("\nEnvelope (simplified gears; the mesh zone overlaps by design)")
    h = parts["housing"]
    inner_clear = {}
    for n, p in parts.items():
        if n in ("housing",):
            continue
        out = p.volume - (p & Box(A.DIFF_X - 6.0, A.DIFF_Y - 6.0, A.DIFF_Z - 6.0)).volume
        inner_clear[n] = out
    print("  gear parts outside the housing's inner cavity (mm3, want 0 except the cross pin ends and the hubs' bores):",
          {k: round(v, 1) for k, v in inner_clear.items()})
    print(f"  housing {A.DIFF_X:.0f} x {A.DIFF_Y:.0f} x {A.DIFF_Z:.0f} mm; z {A.PIVOT_Z - A.DIFF_Z / 2:.1f} to {A.PIVOT_Z + A.DIFF_Z / 2:.1f} (floor top {B.UNDERSIDE_Z + 2:.0f}, cross rails from z 165)")
    steel = sum(p.volume for n, p in parts.items() if n != "housing") / 1e3 * 7.85 / 1000.0
    alu = h.volume / 1e3 * 2.70 / 1000.0
    print(f"  steel gears and pin about {steel:.2f} kg (hubs counted), aluminium housing {alu:.2f} kg: {steel + alu:.2f} kg; the mass script allows 0.45 kg with bushings")
    g = parts["side gear +Y"].bounding_box()
    print(f"  gear tip radius {13.0:.1f} mm against the housing's inner half-height {A.DIFF_Z / 2 - 3:.0f} mm: clearance {A.DIFF_Z / 2 - 3 - 13.0:.1f} mm")
