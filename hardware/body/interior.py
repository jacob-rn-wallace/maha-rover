"""al-maha body interior: cavity inside the panels, contents, and fit check.

Replica design. The body of body.py is a solid envelope; this module cuts the cavity
inside the panels (aluminium sheet, 2 mm side, end and floor panels, 3 mm deck) and
places what goes inside, so fit can be checked. The structure that holds the panels
and the differential (T-slot frame, bearing plates) is in hardware/chassis/frame.py.
Everything here is ASSUMPTION except the outer shape (body.py) and the pivot (3i).

  * Rear compartment: battery pack on the floor. Front compartment: controller and
    drivers on the floor, with a keep-out under the mast base for the cable entry.
  * Part sizes follow docs/electronics-spec.md (candidates, not bought); heights and
    masses marked ASSUMPTION are not sourced.

Run:  .venv/bin/python hardware/body/interior.py
Out:  hardware/body/out/interior.step
"""
import math
import sys
from pathlib import Path

from build123d import Box, Compound, Cylinder, Plane, Polygon, Pos, Rot, extrude, export_step

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "suspension"))
sys.path.insert(0, str(HERE.parent / "electronics"))
import body as B    # noqa: E402
import arms as A    # noqa: E402
import boards as E  # noqa: E402

_MODELS = None

WALL_T = 2.0             # side wall and end wall panels (aluminium sheet)   ASSUMPTION
FLOOR_T = 2.0            # floor panel                              ASSUMPTION
TAN = math.tan(math.radians(B.SIDEWALL_DEG))
COS = math.cos(math.radians(B.SIDEWALL_DEG))

# Parts. Those with a "model" are the dimensioned boards of hardware/electronics/boards.py (outline, holes and heights from vendor drawings; see that file for
# what is sourced), placed by the centre of their footprint; the rest are still placeholder boxes (size x, y, z), marked below. mass kg.
PARTS = {
    "battery 2S2P 18650":  dict(size=(68.0, 38.0, 38.0), mass=0.22, at=(-110.0, 0.0)),                                      # size class from 4 cells in 2 x 2; box
    "controller (Pi Zero 2 W)": dict(model="pi_zero_2w", at=(95.0, 33.0), deck=True),                                        # on the deck's underside since 2026-11-08 (was on the floor at 60, 35): near the mast cable entry
    "GNSS receiver (NEO-M9N breakout)": dict(model="gnss_breakout", at=(58.0, -30.0), deck=True),                          # on the deck's underside, a short coax and UART run from the entry and the Pi
    "servo bus adapter (Waveshare, STS3215)": dict(model="bus_servo_adapter", at=(104.0, -3.0), deck=True),                   # on the deck's underside beside the Pi: short USB lead, short servo cable
    "motor driver A (MC33926)": dict(model="mc33926", at=(60.0, -16.0)),
    "motor driver B (MC33926)": dict(model="mc33926", at=(60.0, -44.0)),
    "5 V converter (D24V22F5)":   dict(model="d24v22fx", at=(130.0, 60.0)),
    "BMS board (2S, common port)": dict(size=(48.0, 20.0, 4.0), mass=0.012, at=(-65.0, 45.0)),                              # about 48 x 20 x 4 mm from the 2S 20 A listings; box
    "fuse block (4-way blade)":    dict(model="fuse_block", at=(-70.0, -50.0)),
    "bus bar (power node)":        dict(size=(40.0, 20.0, 15.0), mass=0.03, at=(-52.0, 0.0)),                               # size class ASSUMPTION; box
    "servo regulator (6 V)":       dict(model="d24v22fx", at=(-10.0, -60.0)),
    "master switch (rear panel)":  dict(model="rocker_switch", at=(-190.0, 35.0), z=165.0),                                 # bezel face on the rear panel's outer face; body inside
    "solar charge controller":    dict(size=(50.0, 25.0, 20.0), mass=0.03, at=(112.0, -65.0)),                              # BQ24650-type buck module, 50 x 25 x 17 mm from the listings; box
}
SWITCH_CUTOUT_D = 20.2   # panel cut-out of the round rocker switch                          stated (listing)
PANEL_GAP = 10.0         # clearance between the side panels and the frame behind them. The original's side panels stand proud
                         # of its body on spacers (front view, [S18] Fig. 1; about 10 mm read by eye on a 1.10 mm/px scale, uncertain
                         # by several mm)                                                     derived, by eye
PIVOT_HOLE_D = 22.0      # clearance hole in each side panel for the pivot shaft (the panel floats on its pivots)  ASSUMPTION
KEEP_OUT = dict(size=(15.0, 40.0, 30.0), at=(159.2, 0.0))   # under the mast base, in the gap between the mast cross rail
                                                           # and the front end rail (frame.py), for the cable entry  ASSUMPTION


def half_width(z):
    """Outer half-width of the wedge at height z."""
    return B.TOP_WIDTH / 2 + (B.DECK_TOP_Z - B.DECK_T - z) * TAN


def inner_half_width(z):
    """Half-width of the cavity (inside the side panels) at height z."""
    return half_width(z) - WALL_T / COS


def cavity():
    z0 = B.UNDERSIDE_Z + FLOOR_T
    z1 = B.DECK_TOP_Z - B.DECK_T
    pts = [(-inner_half_width(z0), z0), (inner_half_width(z0), z0),
           (inner_half_width(z1), z1), (-inner_half_width(z1), z1)]
    length = B.SIDE_PLATE_LEN - 2 * WALL_T
    return Pos(B.BODY_X0, 0, 0) * extrude(Plane.YZ * Polygon(*pts, align=None), amount=length / 2, both=True)


def floor_z():
    return B.UNDERSIDE_Z + FLOOR_T


def _models():
    global _MODELS
    if _MODELS is None:
        _MODELS = E.models()
    return _MODELS


def part_mass(name):
    d = PARTS[name]
    return _models()[d["model"]]["mass"] if "model" in d else d["mass"]


def placed_parts():
    out = {}
    for n, d in PARTS.items():
        if "model" in d:
            sol = _models()[d["model"]]["solid"]
            if d["model"] == "rocker_switch":
                # model axis +z, bezel face at z = 0 with the bezel to +z and the body to -z. Turn it so +z -> -x: the bezel is then outside
                # the rear panel (x smaller) and the body inside; the bezel's back face (model z = 0) sits on the panel's outer face, x = at.
                out[n] = Pos(d["at"][0], d["at"][1], d["z"]) * (Rot(0, -90, 0) * sol)
                continue
            if d.get("deck"):                          # hung from the deck's underside: flipped so the standoffs point up to the deck and the components hang down
                sol = Rot(180, 0, 0) * sol
                bb = sol.bounding_box()
                cx, cy = (bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2
                out[n] = Pos(d["at"][0] - cx, d["at"][1] - cy, B.DECK_TOP_Z - B.DECK_T - bb.max.Z) * sol
                continue
            bb = sol.bounding_box()
            cx, cy = (bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2
            out[n] = Pos(d["at"][0] - cx, d["at"][1] - cy, floor_z() - bb.min.Z) * sol
        else:
            sx, sy, sz = d["size"]
            x, y = d["at"]
            out[n] = Pos(x, y, d.get("z", floor_z() + sz / 2)) * Box(sx, sy, sz)
    kx, ky, kz = KEEP_OUT["size"]
    out["keep-out: mast cable entry"] = Pos(KEEP_OUT["at"][0], KEEP_OUT["at"][1],
                                            B.DECK_TOP_Z - B.DECK_T - kz / 2) * Box(kx, ky, kz)
    return out


def side_panels(cav=None):
    """The two 2 mm side panels (the solar panels), one per side, 10 degrees from vertical, with the 12 wire holes and a
    clearance hole for each pivot shaft. They are separate plates, held off the frame on pivot standoffs (frame.py)."""
    outer, _ = B.body()
    z0, z1 = floor_z(), B.DECK_TOP_Z - B.DECK_T
    pts = [(-inner_half_width(z0), z0), (inner_half_width(z0), z0), (inner_half_width(z1), z1), (-inner_half_width(z1), z1)]
    cav_long = Pos(B.BODY_X0, 0, 0) * extrude(Plane.YZ * Polygon(*pts, align=None), amount=(B.SIDE_PLATE_LEN + 20) / 2, both=True)
    slab = Pos(B.BODY_X0, 0, (z0 + z1) / 2) * Box(B.SIDE_PLATE_LEN + 20, 2 * B.TOP_WIDTH, z1 - z0)
    both = (outer & slab) - cav_long
    out = []
    for sy in (1, -1):
        half = Pos(0, sy * 150.0, (z0 + z1) / 2) * Box(B.SIDE_PLATE_LEN + 20, 300.0, z1 - z0)
        pl = both & half
        for h in B.solar_holes(length=WALL_T / COS + 2.0):
            pl = pl - h
        pl = pl - Pos(0, 0, A.PIVOT_Z) * Rot(90, 0, 0) * Cylinder(PIVOT_HOLE_D / 2, 400.0)
        out.append(pl)
    return out


def shell(cav):
    """Floor, end walls and deck. The side panels are separate (side_panels). The rear panel has the 20.2 mm hole for the master switch."""
    outer, _ = B.body()
    z0, z1 = floor_z(), B.DECK_TOP_Z - B.DECK_T
    pts = [(-inner_half_width(z0), z0), (inner_half_width(z0), z0), (inner_half_width(z1), z1), (-inner_half_width(z1), z1)]
    cav_long = Pos(B.BODY_X0, 0, 0) * extrude(Plane.YZ * Polygon(*pts, align=None), amount=(B.SIDE_PLATE_LEN + 20) / 2, both=True)
    slab = Pos(B.BODY_X0, 0, (z0 + z1) / 2) * Box(B.SIDE_PLATE_LEN + 20, 2 * B.TOP_WIDTH, z1 - z0)
    walls = (outer & slab) - cav_long
    sh = (outer - cav) - walls
    d = PARTS["master switch (rear panel)"]
    cut = Pos(d["at"][0] + 3.0, d["at"][1], d["z"]) * Rot(0, 90, 0) * Cylinder(SWITCH_CUTOUT_D / 2, 12.0)
    return sh - cut


if __name__ == "__main__":
    cav = cavity()
    sh = shell(cav)
    sides = side_panels(cav)
    diff = A.differential()["diff_housing"]
    parts = placed_parts()

    ib = cav.bounding_box()
    print(f"cavity x {ib.min.X:.0f}..{ib.max.X:.0f}, y +-{ib.max.Y:.0f}, z {ib.min.Z:.0f}..{ib.max.Z:.0f}; "
          f"volume {cav.volume / 1e6:.2f} L")
    print(f"panels: floor, ends and deck {sh.volume / 1e3:.0f} cm3; two side panels {sum(p.volume for p in sides) / 1e3:.0f} cm3 "
          f"(2 mm, {PANEL_GAP:.0f} mm off the frame on pivot standoffs)")

    print("\nfit (mm3 outside the cavity, want 0)")
    contents = {"differential housing": diff, **parts}
    for n, p in contents.items():
        out_v = p.volume - (p & cav).volume
        print(f"  {n:42s}: {out_v:8.1f}" + ("   (by design: the switch's bezel and the 2 mm it passes through in the rear panel)" if n.startswith("master switch") else ""))

    print("\nclashes between contents (mm3, want 0)")
    names = list(contents)
    for i, n in enumerate(names):
        for n2 in names[i + 1:]:
            v = (contents[n] & contents[n2]).volume
            if v > 0.01:
                print(f"  {n} vs {n2}: {v:.1f}")
    print("  (anything not listed is 0)")

    mass = sum(part_mass(n) for n in PARTS)
    cen = {n: parts[n].bounding_box() for n in PARTS}
    x = sum(part_mass(n) * (cen[n].min.X + cen[n].max.X) / 2 for n in PARTS) / mass
    z = sum(part_mass(n) * (cen[n].min.Z + cen[n].max.Z) / 2 for n in PARTS) / mass
    print(f"\nelectronics: {mass:.3f} kg, centre x {x:.0f}, z {z:.0f}")

    out = HERE / "out"
    out.mkdir(exist_ok=True)
    export_step(Compound([sh, *sides, diff, *parts.values()], label="al-maha-interior"), str(out / "interior.step"))
