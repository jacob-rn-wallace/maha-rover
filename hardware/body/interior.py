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

from build123d import Box, Compound, Plane, Polygon, Pos, extrude, export_step

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "suspension"))
import body as B    # noqa: E402
import arms as A    # noqa: E402

WALL_T = 2.0             # side wall and end wall panels (aluminium sheet)   ASSUMPTION
FLOOR_T = 2.0            # floor panel                              ASSUMPTION
TAN = math.tan(math.radians(B.SIDEWALL_DEG))
COS = math.cos(math.radians(B.SIDEWALL_DEG))

# placeholder part sizes (x, y, z), mass kg
PARTS = {
    "battery 2S2P 18650":  dict(size=(68.0, 38.0, 38.0), mass=0.22, at=(-110.0, 0.0)),
    "controller (Pi Zero 2 W)": dict(size=(65.0, 30.0, 8.0), mass=0.015, at=(60.0, 35.0)),    # 65 x 30 stated; height and mass ASSUMPTION
    "motor drivers x2 (MC33926)": dict(size=(46.0, 56.0, 12.0), mass=0.014, at=(60.0, -30.0)),  # 28 x 46 each, side by side; height ASSUMPTION; 7 g each
    "5 V converter (D24V22F5)":   dict(size=(18.0, 18.0, 8.0), mass=0.0023, at=(130.0, 60.0)),   # 17.8 x 17.8 x 7.9, 2.3 g
    "solar charge controller":    dict(size=(50.0, 30.0, 12.0), mass=0.03, at=(110.0, -85.0)),    # size class and mass ASSUMPTION; part not chosen
}
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


def placed_parts():
    out = {}
    for n, d in PARTS.items():
        sx, sy, sz = d["size"]
        x, y = d["at"]
        out[n] = Pos(x, y, floor_z() + sz / 2) * Box(sx, sy, sz)
    kx, ky, kz = KEEP_OUT["size"]
    out["keep-out: mast cable entry"] = Pos(KEEP_OUT["at"][0], KEEP_OUT["at"][1],
                                            B.DECK_TOP_Z - B.DECK_T - kz / 2) * Box(kx, ky, kz)
    return out


def shell(cav):
    outer, _ = B.body()
    shell_ = outer - cav
    for h in B.solar_holes(length=WALL_T / COS + 2.0):
        shell_ = shell_ - h
    return shell_


if __name__ == "__main__":
    cav = cavity()
    sh = shell(cav)
    diff = A.differential()["diff_housing"]
    parts = placed_parts()

    ib = cav.bounding_box()
    print(f"cavity x {ib.min.X:.0f}..{ib.max.X:.0f}, y +-{ib.max.Y:.0f}, z {ib.min.Z:.0f}..{ib.max.Z:.0f}; "
          f"volume {cav.volume / 1e6:.2f} L")
    print(f"panels (shell) volume {sh.volume / 1e3:.0f} cm3")

    print("\nfit (mm3 outside the cavity, want 0)")
    contents = {"differential housing": diff, **parts}
    for n, p in contents.items():
        print(f"  {n:42s}: {p.volume - (p & cav).volume:8.1f}")

    print("\nclashes between contents (mm3, want 0)")
    names = list(contents)
    for i, n in enumerate(names):
        for n2 in names[i + 1:]:
            v = (contents[n] & contents[n2]).volume
            if v > 0.01:
                print(f"  {n} vs {n2}: {v:.1f}")
    print("  (anything not listed is 0)")

    mass = sum(d["mass"] for d in PARTS.values())
    x = sum(d["mass"] * d["at"][0] for d in PARTS.values()) / mass
    z = sum(d["mass"] * (floor_z() + d["size"][2] / 2) for d in PARTS.values()) / mass
    print(f"\nelectronics: {mass:.3f} kg, centre x {x:.0f}, z {z:.0f}")

    out = HERE / "out"
    out.mkdir(exist_ok=True)
    export_step(Compound([sh, diff, *parts.values()], label="al-maha-interior"), str(out / "interior.step"))
