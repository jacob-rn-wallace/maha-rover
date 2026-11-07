"""al-maha: strength check of the pivot shaft, its two supports and the drilled bottom side rail (first-pass hand calculation).

Layout (frame.py, arms.py, differential.py): each pivot shaft is a 12 mm OD, 8 mm ID steel tube bonded into a 12 mm bore through the link plate
and its boss (20 mm engagement, y 133 to 153) and running inwards. It is supported at two places: by two igus-type flanged plain bushings
(12 bore, 14 OD, 9 long) pressed into a 16/14 mm aluminium sleeve bonded in a 16 mm hole drilled through the 20 x 40 bottom side rail, and by a
12 long bushing in the differential housing wall boss. Inside the housing an 8 mm OD, 5 mm ID stub tube, bonded 15 mm into the main tube, carries the
side gear. The wheel loads reach the shaft through the link plate and the motor sleeves, 100 mm outboard of the rail.

What is checked:
  1. loads: vertical wheel load per side and wheel scrub (lateral force at the ground), static and with a dynamic factor,
  2. support reactions, with the loads referred to the correct plane (the wheel's y = 207.7, not the link plate's y = 137),
  3. bending and torsion of the shaft where the moment peaks (at the outer face of the rail), for the earlier 8/5 tube and the 12/8 tube,
  4. the rail as a beam, and tear-out and bearing of the thin face walls around the rail hole,
  5. the housing wall and boss, the bushings' surface pressure, the housing's four lugs and the differential cross rails,
  6. the link plate joint (shaft bonded in plate and boss) and the stub's bonded joint.

Everything is ASSUMPTION unless tagged. Material values are typical, not datasheet: rail A6N01SS-T5 (6005A-T5 equivalent),
yield about 200 MPa; shaft steel E355 precision tube (355), 4130 normalized (435, the lowest of three supplier figures), 4140 quenched and tempered (about 650), 304 stainless (215). The rail's second moment is
the catalogue value (Misumi HFS5-2040, 5.13 x 10^4 mm4 about the stiff axis); the net section at the hole is estimated from a simplified 2 mm
wall model of the profile.

Run:  .venv/bin/python hardware/chassis/rail_check.py
"""
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "body"))
sys.path.insert(0, str(HERE.parent / "suspension"))
import body as B   # noqa: E402
import arms as A   # noqa: E402
import frame as F  # noqa: E402

# ---- materials -------------------------------------------------------------------
RAIL_YIELD = 200.0                 # MPa, 6005A-T5 typical (the catalogue gives no figure)
RAIL_TAU = 0.58 * RAIL_YIELD
SHAFT_MATERIALS = {"E355 tube": 355.0, "4130 norm.": 435.0, "4140 Q&T": 650.0, "304 stainless": 215.0}   # MPa yield; typical. 4130 normalized: 435 is the lowest of three conflicting supplier figures (435, 460, 483)
I_RAIL = 5.13e4                    # mm4, HFS5-2040 about the stiff axis (catalogue)
T_WALL, SLOT = 2.0, 6.0            # modelled profile wall and slot width     ASSUMPTION

# ---- loads ------------------------------------------------------------------------
MASS = 9.9                         # kg, replica estimate rounded up (replica-mass.md: 9.89)
G0 = 9.81
N_DYN = 3.0                        # dynamic factor on the static load: drops, grouser impacts   ASSUMPTION
MU = 0.6                           # wheel-ground friction for skid-steer scrub                  ASSUMPTION
T_CAP = 4.5e3                      # N.mm, shaft torque at the 1.6 A motor cap (differential-spec.md)
T_LIMIT = 7.1e3                    # N.mm, at the gearbox limit
BOND_TAU = 15.0                    # MPa, retaining compound lap shear used here (datasheet values for the 600 series run higher, from memory, unverified)   ASSUMPTION
PLATE_YIELD = 240.0                # MPa, 6061-T6 plate, typical   ASSUMPTION
P_BUSH_ALLOW = 20.0                # MPa, permissible bushing pressure used here, deliberately low (the manufacturer's static figure is higher, not looked up)   ASSUMPTION
M4_PROOF_AREA = 8.78               # mm2, M4 tensile stress area
M4_PROOF = 580.0                   # MPa, class 8.8 proof
Y_WHEEL = B.TRACK / 2              # the wheel load acts here
Z_PIVOT = A.PIVOT_Z                # the lateral scrub acts at the ground, this far below the shaft axis
Y_RAIL_OUT = F.YB                  # outer face of the rail
Y_RAIL_C = F.YB - F.P / 2          # support at the rail: the centre of the two bushings
Y_HOUSING = (A.STEP_Y + A.BOSS_Y1) / 2   # centre of the housing bushing


def tube(D, d):
    """Section modulus and polar moment of a tube."""
    return math.pi * (D ** 4 - d ** 4) / (32 * D), math.pi * (D ** 4 - d ** 4) / 32


def rail_net_ratio(d_hole=F.HOLE_D, step=0.1):
    """Ratio of the net to the gross second moment about the horizontal axis (hole seen as a strip |z| < d/2),
    from a hollow 20 x 40 rectangle with 2 mm walls and 6 mm slots."""
    W, H = F.P, F.RAIL_H
    ny, nz = int(W / step), int(H / step)
    y = (np.arange(ny) + 0.5) * step - W / 2
    z = (np.arange(nz) + 0.5) * step - H / 2
    Y, Z = np.meshgrid(y, z, indexing="ij")
    mat = ~((np.abs(Y) < W / 2 - T_WALL) & (np.abs(Z) < H / 2 - T_WALL))
    for zs in (-10.0, 10.0):                                   # slots on the two tall faces (the 40 mm sides)
        mat &= ~((np.abs(Z - zs) < SLOT / 2) & (np.abs(Y) > W / 2 - T_WALL))
    mat &= ~((np.abs(Y) < SLOT / 2) & (np.abs(Z) > H / 2 - T_WALL))   # slots on the two narrow faces
    gross = float((Z ** 2 * mat).sum())
    net = float((Z ** 2 * (mat & ~(np.abs(Z) < d_hole / 2))).sum())
    return net / gross


def reactions(n):
    """Static equilibrium of the shaft in the vertical plane (up positive): wheel load Fz at the wheel plane, scrub moment Ms,
    outer support Ro at the rail, inner support Rh at the housing."""
    W = MASS * G0
    Fz, Fy = n * W / 2, n * MU * W / 2
    Ms = Fy * Z_PIVOT
    Ro = (Fz * (Y_WHEEL - Y_HOUSING) + Ms) / (Y_RAIL_C - Y_HOUSING)
    Rh = Ro - Fz
    Mmax = Rh * (Y_RAIL_C - Y_HOUSING)            # shaft bending moment at the rail support
    return Fz, Fy, Ms, Ro, Rh, Mmax


def main():
    W = MASS * G0
    print(f"rover {MASS:.2f} kg = {W:.0f} N; per pivot static {W / 2:.0f} N vertical, scrub {MU * W / 2:.0f} N (mu {MU}); dynamic factor {N_DYN:.0f}")
    print(f"planes: wheel y {Y_WHEEL:.1f}, rail support y {Y_RAIL_C:.1f} (bushings at the faces {F.YB - F.P:.1f} and {F.YB:.1f}), housing bushing y {Y_HOUSING:.1f}")

    print("\n1. support reactions and the shaft's peak bending moment (at the rail support)")
    res = {}
    for n in (1, N_DYN):
        Fz, Fy, Ms, Ro, Rh, Mmax = reactions(n)
        res[n] = (Fz, Fy, Ms, Ro, Rh, Mmax)
        print(f"   x{n:.0f}: wheel load {Fz:.0f} N, scrub {Fy:.0f} N ({Ms / 1e3:.1f} N.m); rail support {Ro:.0f} N, housing support {Rh:.0f} N; shaft moment {Mmax / 1e3:.1f} N.m")
    # the earlier layout: the same loads, the rail alone (two bushings 12 mm apart)
    n = N_DYN
    Fz, Fy, Ms = res[n][:3]
    span_old = F.P - F.BUSH_L
    R_old = (Fz * (Y_WHEEL - Y_RAIL_C) + Ms) / span_old
    print(f"   (the earlier layout, bushings alone 12 mm apart, x{n:.0f}: {R_old:.0f} N on each bushing)")

    print("\n2. the shaft tube at the peak moment (bending plus torsion at the 1.6 A cap), von Mises, yield factor for three steels")
    hdr = "".join(f"{k:>16s}" for k in SHAFT_MATERIALS)
    print(" " * 33 + hdr)
    for D, d, label in ((8.0, 5.0, "8/5 (the earlier shaft)"), (12.0, 8.0, "12/8 (now)")):
        Z, J = tube(D, d)
        for nn in (1, N_DYN):
            M = res[nn][5]
            s = M / Z
            t = T_CAP * (D / 2) / J
            vm = math.sqrt(s * s + 3 * t * t)
            facs = "".join(f"{y / vm:>16.1f}" for y in SHAFT_MATERIALS.values())
            print(f"   {label:16s} x{nn:.0f} {vm:6.0f} MPa{facs}")
    Zs, Js = tube(2 * A.STUB_R, A.STUB_ID)
    for lab, T in (("1.6 A cap", T_CAP), ("gearbox limit", T_LIMIT)):
        tau = T * A.STUB_R / Js
        print(f"   gear stub 8/5 in torsion alone at the {lab}: {tau:.0f} MPa; with the 3 mm cross hole (Kt about 3): {3 * tau:.0f} MPa")
    print("   the bending moment falls to near zero at the housing support, so the cross hole sits inside the housing; no hole in the 12 mm section")

    print("\n3. the rail")
    ratio = rail_net_ratio()
    Zr = I_RAIL / (F.RAIL_H / 2)
    for nn in (1, N_DYN):
        Ro = res[nn][3]
        L = 2 * (F.X_END - F.EDGE)
        M = Ro * L / 4
        s_g = M / Zr
        s_n = s_g / ratio
        print(f"   x{nn:.0f}: beam, simply supported over {L:.0f} mm, load {Ro:.0f} N at midspan: {M / 1e3:.1f} N.m; stress gross {s_g:.0f} MPa, net at the hole {s_n:.0f} MPa "
              f"(yield {RAIL_YIELD:.0f}): factor {RAIL_YIELD / s_n:.1f}")
    print(f"   net section at the 16 mm hole keeps {ratio * 100:.0f} percent of the stiffness (simplified wall model)")
    lig = F.RAIL_H / 2 - F.HOLE_D / 2                       # face wall left above or below the hole
    shear_area = 2 * lig * T_WALL
    bear_area = F.SLEEVE_OD * T_WALL
    for nn in (1, N_DYN):
        R = res[nn][3] / 2                                   # one of the two bushings
        print(f"   x{nn:.0f}: each bushing {R:.0f} N: tear-out of the {lig:.0f} mm ligament of 2 mm wall, shear {R / shear_area:.1f} MPa (allow {RAIL_TAU:.0f}); "
              f"bearing {R / bear_area:.1f} MPa (yield {RAIL_YIELD:.0f})")

    print("\n4. bushings, housing wall and its mount")
    for nn in (1, N_DYN):
        Rh, Ro = res[nn][4], res[nn][3]
        pr = (Ro / 2) / (12.0 * F.BUSH_L)
        ph = Rh / (12.0 * (A.BOSS_Y1 - A.STEP_Y))
        print(f"   x{nn:.0f}: rail bushing {Ro / 2:.0f} N, {pr:.1f} MPa on 12 x {F.BUSH_L:.0f} mm; housing bushing {Rh:.0f} N, {ph:.1f} MPa on 12 x {A.BOSS_Y1 - A.STEP_Y:.0f} mm (allow {P_BUSH_ALLOW:.0f})  -> {'OK' if max(pr, ph) < P_BUSH_ALLOW else 'CHECK'}")
    # housing: four lugs, M4 into T-nuts in the cross rails. Loads: both shafts push the housing down with Rh; the carrier torque is twice the side torque
    for nn, T in ((1, T_CAP), (N_DYN, T_LIMIT)):
        Rh = res[nn][4]
        lever = F.CROSS_X                           # bolts at x = +-28 about the housing's y axis
        F_down = 2 * Rh / 4                          # both shafts, four bolts
        F_tq = 2 * T / (2 * lever) / 2               # carrier torque 2T, couple of two bolt pairs
        Fb = F_down + F_tq
        print(f"   x{nn:.0f} with torque {T / 1e3:.1f} N.m per side: bolt pull {Fb:.0f} N (weight and shaft reaction {F_down:.0f}, torque {F_tq:.0f}); M4 8.8 proof load {M4_PROOF_AREA * M4_PROOF:.0f} N")
    Rh = res[N_DYN][4]
    Lc = 2 * (F.YO - F.P)
    Mc = Rh * Lc / 4
    print(f"   each differential cross rail (20 x 20, span {Lc:.0f} mm, load {Rh:.0f} N at midspan at 3x): {Mc / 1e3:.1f} N.m, {Mc / (7400 / 10):.0f} MPa gross (catalogue I 0.74e4 mm4) against {RAIL_YIELD:.0f}")

    print("\n5. joints at the shaft ends")
    eng = F.P if False else (A.PLATE_T + A.BOSS_T)
    M_p = res[N_DYN][0] * (Y_WHEEL - A.PLATE_Y0) + res[N_DYN][2]
    p_peak = 6 * M_p / (12.0 * eng ** 2) + res[N_DYN][0] / (12.0 * eng)
    print(f"   link plate: shaft bonded in {eng:.0f} mm of plate and boss; moment at the plate face {M_p / 1e3:.1f} N.m (3x); peak contact pressure on the aluminium {p_peak:.0f} MPa (yield {PLATE_YIELD:.0f}): factor {PLATE_YIELD / p_peak:.1f}")
    for lab, T in (("cap", T_CAP), ("gearbox limit", T_LIMIT)):
        cap = BOND_TAU * math.pi * 12.0 * eng * 6.0
        print(f"   link plate bond torque capacity {cap / 1e3:.0f} N.m against {T / 1e3:.1f} N.m at the {lab}: factor {cap / T:.1f}")
    for lab, T in (("cap", T_CAP), ("gearbox limit", T_LIMIT)):
        cap = BOND_TAU * math.pi * 8.0 * A.STUB_INSERT * 4.0
        print(f"   stub bond ({A.STUB_INSERT:.0f} mm into the tube) torque capacity {cap / 1e3:.1f} N.m against {T / 1e3:.1f} N.m at the {lab}: factor {cap / T:.1f}")
    print("   (no cross pins: a cross hole at the plate would see about 3 x the bending stress and a pin through the stub would block the wire bore)")


if __name__ == "__main__":
    main()
