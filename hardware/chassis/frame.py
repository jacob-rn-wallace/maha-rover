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
  * four sloped corner posts, 10 degrees from vertical, square-cut ends
  * two mid rails along X at z 175, with two cross rails at x = +-28 that carry the
    differential housing on printed cradles (not modelled)
  * two bearing plates (6 mm) in the side walls at x = 0, bridging the split bottom
    rails and carrying the 6800 bearings for the pivot shafts

Joints and fixing (decided 2026-11-07, see docs/frame-spec.md): every extrusion is cut square
(no mitres). Rails stay axis-aligned and join each other with standard 20-series corner
brackets. The posts lean 10 degrees with square-cut ends and are joined by bracket plus a
printed 10 degree wedge shim where an end cross rail meets them. The sloped side panels sit
on printed tapered strips (0 to 3.5 mm) on the side rails and flush on the posts. Panels bolt
to the frame with M4 screws into T-nuts. The deck is the lid: it carries the mast.

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
BEARING_SEAT_R = 8.0     # 688 outer radius (8 x 16 x 5, ISO size from memory)
FIX_PITCH = 100.0        # panel screw pitch                      ASSUMPTION
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
    """Sloped corner post, outer face on the wall. Modelled with horizontal ends (a simplification:
    the real post is cut square and stops up to 3.5 mm short of the floor and deck planes)."""
    z0, z1 = Z_FLOOR, Z_DECK
    o0, o1 = yin(z0) - EDGE, yin(z1) - EDGE            # outer face y at each end
    d = P / COS                                         # horizontal width of the section
    pts = [(sy * o0, z0), (sy * (o0 - d), z0), (sy * (o1 - d), z1), (sy * o1, z1)]
    xc = sx * (X_END - P / 2 - EDGE)
    return Pos(xc, 0, 0) * extrude(Plane.YZ * Polygon(*pts, align=None), amount=P / 2, both=True)


def wedge_strips(members):
    """Printed tapered strips between each axis-aligned side rail and its sloped panel."""
    strips = {}
    for n, r in members.items():
        if not (n.startswith("bottom side") or n.startswith("mid side") or n.startswith("top side")):
            continue
        bb = r.bounding_box()
        sy = 1 if bb.max.Y > 0 else -1
        z0, z1 = bb.min.Z, bb.max.Z
        y_o = (bb.max.Y if sy > 0 else -bb.min.Y)            # rail outer face, vertical
        y_panel_bottom = yin(z0) - EDGE                        # sloped panel surface at the rail's bottom edge
        pts = [(sy * y_o, z1), (sy * y_o, z0), (sy * y_panel_bottom, z0)]
        x0, x1 = bb.min.X, bb.max.X
        strip = Pos((x0 + x1) / 2, 0, 0) * extrude(Plane.YZ * Polygon(*pts, align=None), amount=(x1 - x0) / 2, both=True)
        strips["strip " + n] = strip
    return strips


def post_shims(members):
    """Printed 10 degree wedges where an end cross rail meets a sloped post."""
    shims = {}
    for n, r in members.items():
        if "end cross" not in n:
            continue
        bb = r.bounding_box()
        z0, z1 = bb.min.Z, bb.max.Z
        for sy in (1, -1):
            w = bb.max.Y if sy > 0 else -bb.min.Y
            t = P * TAN
            pts = [(sy * w, z1), (sy * w, z0), (sy * (w + t), z0)]
            shims[f"shim {n} {'L' if sy > 0 else 'R'}"] = Pos((bb.min.X + bb.max.X) / 2, 0, 0) * extrude(Plane.YZ * Polygon(*pts, align=None), amount=P / 2, both=True)
    return shims


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
        b = Cylinder(BEARING_SEAT_R, 5.0) - Cylinder(4.2, 5.0)
        bearings.append(Pos(0, sy * (y_in_face + 2.5 + 0.5), A.PIVOT_Z) * Rot(90, 0, 0) * b)
    return plates, bearings


def member_length(name, shape):
    bb = shape.bounding_box()
    if name.startswith("post"):
        return (B.DECK_TOP_Z - B.DECK_T - Z_FLOOR) / COS     # length along the axis at the outer edge
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

    # ---- printed wedges ----
    strips = wedge_strips(members)
    shims = post_shims(members)
    print(f"\nprinted parts: {len(strips)} tapered strips (0 to {P * TAN:.1f} mm), {len(shims)} post shims (0 to {P * TAN:.1f} mm)")
    sv = sum(v.volume for v in strips.values()) + sum(v.volume for v in shims.values())
    out_s = [n for n, v in {**strips, **shims}.items() if v.volume - (v & cav).volume > 0.5]
    print(f"  total volume {sv / 1e3:.1f} cm3; outside the cavity: {out_s or 'none'}")
    clash = []
    for n, v in {**strips, **shims}.items():
        for m, mem in members.items():
            o = (v & mem).volume
            if o > 0.5:
                clash.append((n, m, round(o, 1)))
    print(f"  clashes with members: {clash or 'none'}")
    # gap left between each strip's outer face and the panel, and between each rail and the strip
    for n in list(strips)[:2]:
        bb = strips[n].bounding_box()
        print(f"  {n}: thickness at the thick edge {abs(max(bb.max.Y, -bb.min.Y) - min(abs(bb.max.Y), abs(bb.min.Y))):.2f} mm")

    # ---- joint inventory (explicit, from the topology above) ----
    n_end_cross = sum("end cross" in n for n in members)
    joints = {
        "end cross rail to post (bracket + wedge shim)": n_end_cross * 2,
        "side rail to end cross rail (bracket)": 4 + 4,                 # bottom (outer ends) and top side rails
        "mid side rail to post (bracket)": 4,
        "differential cross rail to mid side rail (bracket)": 4,
        "mast cross rail to top side rail (bracket)": 2,
        "bottom side rail to bearing plate (bracket)": 4,
    }
    nj = sum(joints.values())
    print("\njoints (one standard corner bracket each, 2 T-nuts and 2 M4 bolts)")
    for k, v in joints.items():
        print(f"  {k:55s} {v:3d}")
    print(f"  total {nj} brackets, {2 * nj} T-nuts, {2 * nj} bolts")

    # ---- panel fixing: M4 into T-nuts, pitch FIX_PITCH, at least 2 per member ----
    L = {n: member_length(n, s) for n, s in members.items()}
    def nbolts(names):
        return sum(max(2, math.ceil(L[n] / FIX_PITCH)) for n in names)
    pick = lambda *keys: [n for n in members if any(k in n for k in keys)]
    floor_b = nbolts(pick("bottom side", "bottom end cross"))
    deck_b = nbolts(pick("top side", "top end cross", "top cross under mast"))
    end_b = (nbolts([n for n in members if n.endswith("cross F") and n.startswith(("bottom end", "top end"))] + pick("post FL", "post FR")) +
             nbolts([n for n in members if n.endswith("cross R") and n.startswith(("bottom end", "top end"))] + pick("post RL", "post RR")))
    side_b = 0
    for s_ in ("L", "R"):
        side_b += nbolts([n for n in members if (n.startswith(("bottom side " + s_, "mid side " + s_, "top side " + s_)))] + pick("post FL" if s_ == "L" else "post FR", "post RL" if s_ == "L" else "post RR"))
    total_b = floor_b + deck_b + end_b + side_b
    print(f"\npanel fixing (M4 button head into T-nuts, pitch about {FIX_PITCH:.0f} mm, at least 2 per member)")
    print(f"  floor {floor_b}, deck (the lid) {deck_b}, end panels {end_b}, side panels {side_b}: total {total_b} screws and {total_b} T-nuts")
    print("  mast base: 4 M4 bolts through the base block and deck into the mast cross rail (x 141) and front end rail (x 178), y +-30")

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
    export_step(Compound(list(members.values()) + plates + bearings + list(strips.values()) + list(shims.values()) + [shell], label="al-maha-chassis"), str(out / "frame.step"))
