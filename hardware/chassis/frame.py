"""al-maha chassis: T-slot aluminium frame behind sheet panels, plus bearing plates.

Replica design. A frame of 20 x 20 mm T-slot extrusion (the 5-series, 6 mm slot, as
Misumi HFS5-2020: 0.50 kg/m, 183 mm2) sits just inside the panels of body.py / interior.py.
The panels (2 mm aluminium sheet on the sides, ends and floor, 3 mm on the deck) bolt to
it through the slots. Members are modelled as plain 20 x 20 sections; the slots are
ignored, and mass comes from the catalogue linear mass. All positions and the panel
material are ASSUMPTION.

Frame:
  * bottom frame: two end cross rails and two side rails, on the floor panel; the side
    rails are split at |x| < GAP to let the pivot shafts through
  * top frame: two end cross rails, two side rails, and a cross rail under the mast base
  * four sloped corner posts, 10 degrees from vertical, ends cut at 10 degrees (a
    mitre: not an option on the vendor's cut-to-length service, which lists 45 only)
  * two mid rails along X at z 175, with two cross rails at x = +-28 that carry the
    differential housing on printed cradles (not modelled)
  * two bearing plates (6 mm) in the side walls at x = 0, bridging the split bottom
    rails and carrying the 6800 bearings for the pivot shafts

Frame as in body.py.

Run:  .venv/bin/python hardware/chassis/frame.py
Out:  hardware/chassis/out/frame.step
"""
import math
import sys
from pathlib import Path

from build123d import Box, Compound, Cylinder, Plane, Polygon, Pos, Rot, extrude, export_step

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "body"))
sys.path.insert(0, str(HERE.parent / "suspension"))
import body as B       # noqa: E402
import interior as I   # noqa: E402
import arms as A       # noqa: E402

P = 20.0                 # extrusion section, 20 x 20             stated (catalogue)
KG_PER_M = 0.50          # HFS5-2020 and a second 20 x 20 datasheet   stated (catalogue)
TAN, COS = I.TAN, I.COS
GAP = 35.0               # side rails stop this far from x = 0     ASSUMPTION
EDGE = 0.2               # members sit this far inside the panels, so they never touch
CROSS_X = 28.0           # differential cross rails at x = +-28
MAST_RAIL_X = 140.7      # cross rail under the mast base; the base (x 122 to 200) also spans the front end rail  ASSUMPTION
MID_Z = 175.0            # centre height of the mid rails          ASSUMPTION
PLATE_T = 6.0            # bearing plate thickness                 ASSUMPTION
BEARING_SEAT_R = 9.5     # 6800 outer radius (ISO size from memory)
ALU = 2.70               # g/cm3, standard value for aluminium sheet
PANEL_MASS_NOTE = "aluminium sheet at 2.70 g/cm3"

Z_FLOOR = I.floor_z()                       # floor panel top
Z_DECK = B.DECK_TOP_Z - B.DECK_T            # deck panel underside
X_END = B.SIDE_PLATE_LEN / 2 - I.WALL_T     # inner face of the end panels


def yin(z):
    """Half-width of the cavity at height z (inside the side panels)."""
    return I.inner_half_width(z)


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def side_rail(sy, x0, x1, zc):
    """Rail along X against a sloped wall: its outer top corner clears the wall by EDGE."""
    yc = yin(zc + P / 2) - EDGE - P / 2
    return box(x0, x1, sy * yc - P / 2, sy * yc + P / 2, zc - P / 2, zc + P / 2)


def cross_rail(xc, zc, abut):
    """Rail along Y at x = xc between the two sides, ending on the inner faces of the posts
    (abut = 'post') or of the side rails (abut = 'rail'), measured at the rail's top, where the cavity is narrowest."""
    w = yin(zc + P / 2) - EDGE - (P / COS if abut == "post" else P)
    return box(xc - P / 2, xc + P / 2, -w, w, zc - P / 2, zc + P / 2)


def post(sx, sy):
    """Sloped corner post with horizontal (mitred) ends, outer face on the wall."""
    z0, z1 = Z_FLOOR, Z_DECK
    o0, o1 = yin(z0) - EDGE, yin(z1) - EDGE            # outer face y at each end
    d = P / COS                                         # horizontal width of the section
    pts = [(sy * o0, z0), (sy * (o0 - d), z0), (sy * (o1 - d), z1), (sy * o1, z1)]
    xc = sx * (X_END - P / 2 - EDGE)
    return Pos(xc, 0, 0) * extrude(Plane.YZ * Polygon(*pts, align=None), amount=P / 2, both=True)


def build():
    m = {}
    zb = Z_FLOOR + P / 2                                # bottom rails sit on the floor panel
    zt = Z_DECK - P / 2                                 # top rails sit under the deck panel
    for sx in (1, -1):
        m[f"post {'F' if sx > 0 else 'R'}L"] = post(sx, 1)
        m[f"post {'F' if sx > 0 else 'R'}R"] = post(sx, -1)
        xc = sx * (X_END - P / 2 - EDGE)
        m[f"bottom end cross {'F' if sx > 0 else 'R'}"] = cross_rail(xc, zb, "post")
        m[f"top end cross {'F' if sx > 0 else 'R'}"] = cross_rail(xc, zt, "post")
    inner = X_END - P - 2 * EDGE                       # rails run between the end cross rails
    for sy in (1, -1):
        s = "L" if sy > 0 else "R"
        m[f"bottom side {s} front"] = side_rail(sy, GAP, inner, zb)
        m[f"bottom side {s} rear"] = side_rail(sy, -inner, -GAP, zb)
        m[f"top side {s}"] = side_rail(sy, -inner, inner, zt)
        m[f"mid side {s}"] = side_rail(sy, -inner, inner, MID_Z)
    m["top cross under mast"] = cross_rail(MAST_RAIL_X, zt, "rail")
    for sx in (1, -1):
        m[f"differential cross {'F' if sx > 0 else 'R'}"] = cross_rail(sx * CROSS_X, MID_Z, "rail")
    return m


def bearing_plates():
    """6 mm plate against each side wall at x = 0, with a seat for the 6800 bearing."""
    plates, bearings = [], []
    z0, z1 = Z_FLOOR, MID_Z - P / 2 - 1.0               # up to 1 mm under the mid rails
    for sy in (1, -1):
        o0, o1 = yin(z0) - EDGE, yin(z1) - EDGE
        pts = [(sy * o0, z0), (sy * (o0 - PLATE_T / COS), z0), (sy * (o1 - PLATE_T / COS), z1), (sy * o1, z1)]
        plate = extrude(Plane.YZ * Polygon(*pts, align=None), amount=GAP, both=True)
        # bore along Y through the plate for the bearing
        bore = Pos(0, 0, A.PIVOT_Z) * Rot(90, 0, 0) * Cylinder(BEARING_SEAT_R, 400.0)
        plates.append(plate - bore)
        # bearing ring, 5 mm wide, seated at the inner face of the plate
        y_in_face = yin(A.PIVOT_Z) - EDGE - PLATE_T / COS
        b = Cylinder(BEARING_SEAT_R, 5.0) - Cylinder(5.2, 5.0)
        bearings.append(Pos(0, sy * (y_in_face + 2.5 + 0.5), A.PIVOT_Z) * Rot(90, 0, 0) * b)
    return plates, bearings


def member_length(name, shape):
    bb = shape.bounding_box()
    if name.startswith("post"):
        return (B.DECK_TOP_Z - B.DECK_T - Z_FLOOR) / COS     # axis length, mitred ends
    dims = sorted([bb.size.X, bb.size.Y, bb.size.Z], reverse=True)
    return dims[0]


if __name__ == "__main__":
    cav = I.cavity()
    shell = I.shell(cav)
    members = build()
    plates, bearings = bearing_plates()
    diff = A.differential()["diff_housing"]
    contents = {**I.placed_parts(), "differential housing": diff}

    print(f"profile {P:.0f} x {P:.0f}, {KG_PER_M} kg/m; panels {I.WALL_T:.0f} mm (side, end, floor), {B.DECK_T:.0f} mm deck")
    print("\nmember list (name, length mm)")
    total = 0.0
    for n, s in members.items():
        L = member_length(n, s)
        total += L
        print(f"  {n:26s} {L:6.1f}")
    print(f"  total {total / 1000:.2f} m  ->  {total / 1000 * KG_PER_M:.2f} kg")

    print("\ncontainment in the cavity (mm3 outside, want 0)")
    bad = [(n, s.volume - (s & cav).volume) for n, s in members.items() if s.volume - (s & cav).volume > 0.5]
    print("  members:", "all inside" if not bad else bad)
    badp = [s.volume - (s & cav).volume for s in plates]
    print("  bearing plates outside:", [round(v, 1) for v in badp])

    print("\nmember vs member overlaps (mm3, want 0 except where members meet end to end)")
    names = list(members)
    hits = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            v = (members[a] & members[b]).volume
            if v > 0.5:
                hits.append((a, b, round(v, 1)))
    print("  ", "none" if not hits else "")
    for h in hits:
        print("   ", h)

    print("\nframe vs contents (mm3, want 0)")
    allm = Compound(list(members.values()) + plates)
    for n, c in contents.items():
        v = (allm & c).volume
        print(f"  {n:42s}: {v:8.1f}")

    print("\nshafts and bearings")
    for sy in (1, -1):
        arm, _, _ = A.side(sy)
        sh = arm["shaft"]
        print(f"  shaft {'L' if sy > 0 else 'R'} vs members {sum((sh & s).volume for s in members.values()):.1f}; "
              f"vs plate {(sh & plates[0 if sy > 0 else 1]).volume:.1f}; vs bearing {(sh & bearings[0 if sy > 0 else 1]).volume:.1f}")

    print("\nmounting")
    mast_rail = members["top cross under mast"].bounding_box()
    front = members["top end cross F"].bounding_box()
    print(f"  mast base block x {B.MAST_X - 39:.0f}..{B.MAST_X + 39:.0f}; it lies over the mast cross rail (x {mast_rail.min.X:.0f}..{mast_rail.max.X:.0f}) "
          f"and the front end rail (x {front.min.X:.0f}..{front.max.X:.0f}); cable gap between them {front.min.X - mast_rail.max.X:.0f} mm")
    print(f"  top side rails at y +-{yin(Z_DECK - P / 2) - EDGE - P / 2:.0f}: the mast base (y +-45) lies between them, "
          f"so the base needs the cross rail, and its cable hole can sit beside it")

    # masses
    plate_vol = sum(s.volume for s in plates)
    sh_mass = shell.volume / 1e3 * ALU / 1000.0
    print(f"\npanels (the shell of interior.py, {PANEL_MASS_NOTE}): {sh_mass:.2f} kg")
    print(f"frame {total / 1000 * KG_PER_M:.2f} kg; bearing plates {plate_vol / 1e3 * ALU / 1000:.2f} kg; "
          f"chassis total {sh_mass + total / 1000 * KG_PER_M + plate_vol / 1e3 * ALU / 1000:.2f} kg "
          f"(original structure: 2 kg excluding mobility [S26])")
    free = cav.volume - sum(s.volume for s in members.values()) - plate_vol
    print(f"cavity {cav.volume / 1e6:.2f} L, frame and plates occupy {(cav.volume - free) / 1e6:.2f} L")

    out = HERE / "out"
    out.mkdir(exist_ok=True)
    export_step(Compound(list(members.values()) + plates + bearings + [shell], label="al-maha-chassis"), str(out / "frame.step"))
