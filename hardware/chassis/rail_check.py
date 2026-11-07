"""al-maha: strength check of the bottom side rail with the pivot hole drilled through it (first-pass hand calculation).

The bottom side rail is a 20 x 20 T-slot extrusion, 375.6 mm long, with a 12 mm hole drilled along Y through its middle at x = 0 for
the pivot shaft (frame.py). A flanged plain bushing sits at each end of the hole. This script estimates:

  1. the rail as a beam (vertical load at midspan), gross section and net section at the hole,
  2. the loads the shaft puts on the two bushings (a couple from the cantilevered link plate and from wheel scrub),
  3. the tear-out and bearing stress in the thin face walls around the hole.

Everything is ASSUMPTION unless tagged: the profile is modelled as a hollow square with 2 mm walls and a 6 mm slot opening
on each face (this gives a second moment of area of 0.58 x 10^4 mm4, about 20 percent under the catalogue's 0.74 x 10^4 for the Misumi
HFS5-2020, so the model is on the conservative side; the real profile's core is not modelled), the aluminium is 6063-T5 (typical yield 145 MPa, ultimate 186 MPa; typical values, not a
datasheet), and the loads are rough.

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

# ---- material and profile -----------------------------------------------------
YIELD, ULT = 145.0, 186.0          # MPa, 6063-T5 typical
TAU_ALLOW = 0.58 * YIELD           # MPa, shear yield (von Mises)
P = 20.0                           # section
T_WALL = 2.0                       # wall thickness of the modelled profile      ASSUMPTION
SLOT = 6.0                         # slot opening on each face
I_CATALOGUE = 0.74e4               # mm4, HFS5-2020 (frame-spec.md)

# ---- loads ----------------------------------------------------------------------
MASS = 9.54                        # kg, replica estimate (replica-mass.md)
G0 = 9.81
N_DYN = 3.0                        # dynamic factor on the static load: drops, grouser impacts   ASSUMPTION
MU = 0.6                           # wheel-ground friction for skid steering scrub                ASSUMPTION
Y_LINK = 133.0 + 4.0               # y of the link plate's mid-thickness (inner face 133, 8 mm thick)
Y_BUSH_OUT = F.YB - F.BUSH_L / 2   # centre of the outer bushing
Y_BUSH_IN = F.YB - F.P + F.BUSH_L / 2
Y_HOUSING = 25.0                   # the differential housing wall: a second shaft support if its bore carries a bushing   ASSUMPTION
LEVER_SCRUB = A.PIVOT_Z            # the wheel's lateral force acts at the ground, this far below the pivot axis


def section_inertia(net_hole=False, d_hole=F.HOLE_D, step=0.1):
    """Second moment of area about the horizontal axis (vertical bending), and area, of the modelled profile.
    net_hole: remove the strip |z| < d_hole / 2 (the drilled hole seen in the section at x = 0)."""
    n = int(P / step)
    c = (np.arange(n) + 0.5) * step - P / 2
    Y, Z = np.meshgrid(c, c, indexing="ij")
    inner = (np.abs(Y) < P / 2 - T_WALL) & (np.abs(Z) < P / 2 - T_WALL)
    mat = ~inner
    # slot openings on all four faces
    mat &= ~((np.abs(Y) < SLOT / 2) & (np.abs(Z) > P / 2 - T_WALL))
    mat &= ~((np.abs(Z) < SLOT / 2) & (np.abs(Y) > P / 2 - T_WALL))
    if net_hole:
        mat &= ~(np.abs(Z) < d_hole / 2)
    dA = step * step
    return float((Z ** 2 * mat).sum() * dA), float(mat.sum() * dA)


def main():
    W = MASS * G0
    Fz_static = W / 2                          # vertical load on one pivot on level ground
    Fz = N_DYN * Fz_static
    Fy_static = MU * W / 2                     # lateral scrub force on one side (two wheels)
    Fy = N_DYN * Fy_static
    L = 2 * (F.X_END - F.EDGE)                 # rail length
    print(f"rover {MASS:.2f} kg = {W:.0f} N; per pivot static {Fz_static:.0f} N vertical; design case x{N_DYN:.0f}: {Fz:.0f} N vertical, {Fy:.0f} N lateral (scrub, mu {MU})")

    Ig, Ag = section_inertia()
    In, An = section_inertia(net_hole=True)
    print(f"\nprofile model: 2 mm walls, 6 mm slots: I = {Ig:.0f} mm4 (catalogue about {I_CATALOGUE:.0f}), area {Ag:.0f} mm2 (catalogue 183: the core is not modelled)")
    print(f"net section at the hole (|z| < {F.HOLE_D / 2:.0f} removed): I = {In:.0f} mm4 ({In / Ig * 100:.0f} percent), area {An:.0f} mm2")

    # 1. beam
    M = Fz * L / 4
    s_g = M * (P / 2) / Ig
    s_n = M * (P / 2) / In
    print(f"\n1. beam, simply supported over {L:.0f} mm, midspan load {Fz:.0f} N: M = {M:.0f} N.mm")
    print(f"   bending stress, gross {s_g:.0f} MPa, net at the hole {s_n:.0f} MPa (yield {YIELD:.0f}): factor {YIELD / s_n:.1f}")

    # 2. bushing reactions
    M_link = Fz * (Y_LINK - Y_BUSH_OUT)
    M_scrub = Fy * LEVER_SCRUB
    M_tot = M_link + M_scrub
    print(f"\n2. moment on the shaft about the rail's own axis: link plate cantilever {M_link:.0f} + wheel scrub {M_scrub:.0f} = {M_tot:.0f} N.mm")
    cases = {
        "bushings only (span %.0f mm)" % (Y_BUSH_OUT - Y_BUSH_IN): Y_BUSH_OUT - Y_BUSH_IN,
        "outer bushing and the housing wall (span %.0f mm)" % (Y_BUSH_OUT - Y_HOUSING): Y_BUSH_OUT - Y_HOUSING,
    }
    # 3. tear-out in the face wall: the load pushes the bushing against the wall above (or below) the hole
    lig_h = P / 2 - F.HOLE_D / 2                       # wall left above/below the hole on the face: 4 mm
    shear_area = 2 * lig_h * T_WALL                    # two shear planes, one each side of the ligament
    bear_area = F.BUSH_OD * T_WALL
    for name, span in cases.items():
        for label, scale in (("static (x1)", 1.0 / N_DYN), (f"design (x{N_DYN:.0f})", 1.0)):
            R = M_tot * scale / span + 0.5 * Fz * scale
            tau = R / shear_area
            sb = R / bear_area
            print(f"   {name}, {label}: reaction {R:.0f} N; tear-out shear {tau:.0f} MPa (allow {TAU_ALLOW:.0f}); bearing {sb:.0f} MPa (yield {YIELD:.0f})"
                  f"  -> {'OK' if tau < TAU_ALLOW and sb < YIELD else 'FAILS'}")
    print(f"\n   face-wall ligament above/below the hole: {lig_h:.0f} mm x {T_WALL:.0f} mm wall, two shear planes: {shear_area:.0f} mm2; bearing area {bear_area:.0f} mm2")
    print("   a flange or sleeve that clamps the face wall, or a thicker plate on the rail, spreads this load; not designed")


if __name__ == "__main__":
    main()
