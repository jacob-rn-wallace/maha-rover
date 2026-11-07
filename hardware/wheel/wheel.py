"""al-maha wheel: parametric CAD (build123d), first model.

Replica of the Rashid-1 wheel. Millimetres. Axle along Z, wheel centred on the
origin, a grouser plate on the +X axis (the 0 degree rib axis).

Every value names its status from docs/wheel-spec.md: stated / derived /
(unverified). Values marked ASSUMPTION are modelling choices with no source;
change them when a source appears and record the change in the BOM.

Run:  .venv/bin/python hardware/wheel/wheel.py
Out:  hardware/wheel/out/wheel.step, wheel.stl
"""
import math
from pathlib import Path

from build123d import (
    Align, Axis, Cylinder, Location, Plane, Polygon, Pos, Rot, export_step,
    export_stl, extrude, Box, Sketch,
)

# ---- Envelope (stated, all sources agree) --------------------------------
RIM_R = 100.0            # rim radius (200 mm diameter)             stated
WIDTH = 80.0             # overall width                            stated
N_GROUSERS = 14          # radial, straight, evenly spaced          stated
GROUSER_H = 15.0         # height above the rim                     stated
# Diameter over tips is derived 230-232; 200 + 2 x 15 = 230 is used.

# ---- Derived from figures (plus or minus 2-3 %) --------------------------
N_RIBS = 10              # ten ribs at 36 degrees                   derived
RIB_W = 14.5             # constant tangential width                derived
HUB_D = 50.0             # hub tube outer diameter                  derived
RIM_T = 3.0              # rim band thickness, +-1                  derived, coarse
GROUSER_T = 0.8          # plate thickness, 0.5-1.0                 derived

# ---- (unverified) / ASSUMPTION -------------------------------------------
RIB_T = 3.0              # rib plate thickness along the axle       (unverified)
WEB_H = 6.0              # T web height off the plate face; 0 gives
                         # a flat plate. Web seen on one face only
                         # in [S23] Fig. 68a/91/92                  ASSUMPTION
WEB_T = 2.0              # T web thickness                          ASSUMPTION
RIB_LAYER_Z = 10.0       # two rib sets at z = +-RIB_LAYER_Z        ASSUMPTION
HUB_LEN = 40.0           # hub tube length                          ASSUMPTION
HUB_WALL = 3.0           # hub tube wall; bore not known            ASSUMPTION
RIM_BAND_W = 80.0        # band width; thesis hints plates stand
                         # wider than the band                      ASSUMPTION
FLARE_LEN = 10.0         # rib root flare length along the rib      ASSUMPTION
FLARE_HALF_W = 12.0      # half-width of the rib at the rim         ASSUMPTION

OVERLAP = 0.5            # unions overlap this much so solids fuse


def rib(angle_deg: float, z: float):
    """One T-section rib: flat plate (constant width, flared at the rim root)
    with a web on the face pointing away from the wheel mid-plane (sign of z).
    The two layers are mirror images about z = 0 (assumed)."""
    r0 = HUB_D / 2 - OVERLAP
    r1 = RIM_R - RIM_T + OVERLAP
    rf = r1 - FLARE_LEN
    hw = RIB_W / 2
    pts = [(r0, -hw), (rf, -hw), (r1, -FLARE_HALF_W),
           (r1, FLARE_HALF_W), (rf, hw), (r0, hw)]
    plate = extrude(Polygon(*pts, align=None), amount=RIB_T / 2, both=True)
    if WEB_H > 0:
        # web: runs from the hub to the start of the flare, centred on the rib
        side = 1 if z > 0 else -1
        web_len = rf - r0
        web = Pos(r0 + web_len / 2, 0, side * (RIB_T / 2 + WEB_H / 2 - OVERLAP / 2)) * Box(
            web_len, WEB_T, WEB_H + OVERLAP)
        plate = plate + web
    return Rot(0, 0, angle_deg) * Pos(0, 0, z) * plate


def build_wheel():
    # Rim band: tube, outer radius RIM_R
    band = Cylinder(RIM_R, RIM_BAND_W) - Cylinder(RIM_R - RIM_T, RIM_BAND_W)

    # Hub tube
    hub = Cylinder(HUB_D / 2, HUB_LEN) - Cylinder(HUB_D / 2 - HUB_WALL, HUB_LEN)

    wheel = band + hub

    # Ribs: two sets of five on two axial layers, inner set rotated 36 deg
    step = 360.0 / N_RIBS
    for i in range(N_RIBS):
        z = RIB_LAYER_Z if i % 2 == 0 else -RIB_LAYER_Z
        wheel = wheel + rib(i * step, z)

    # Grousers: thin radial plates, full width, one on +X
    g_in = RIM_R - RIM_T / 2          # embedded in the band
    g_out = RIM_R + GROUSER_H
    gp = Pos((g_in + g_out) / 2, 0, 0) * Box(
        g_out - g_in, GROUSER_T, WIDTH)
    for i in range(N_GROUSERS):
        wheel = wheel + Rot(0, 0, i * 360.0 / N_GROUSERS) * gp

    return wheel


if __name__ == "__main__":
    wheel = build_wheel()
    out = Path(__file__).parent / "out"
    out.mkdir(exist_ok=True)
    export_step(wheel, str(out / "wheel.step"))
    export_stl(wheel, str(out / "wheel.stl"))

    bb = wheel.bounding_box()
    print(f"valid solid : {wheel.is_valid}")
    print(f"solids      : {len(wheel.solids())}")
    print(f"bbox X      : {bb.size.X:.2f}  (tips; target 230)")
    print(f"bbox Y      : {bb.size.Y:.2f}")
    print(f"bbox Z      : {bb.size.Z:.2f}  (width; target 80)")
    print(f"volume      : {wheel.volume / 1000:.1f} cm3")
    print(f"mass @AZ91E : {wheel.volume / 1000 * 1.81:.0f} g  (density 1.81 g/cm3; assumption-laden)")
