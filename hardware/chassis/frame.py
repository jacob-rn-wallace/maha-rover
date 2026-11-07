"""al-maha chassis: T-slot aluminium frame behind sheet panels.

Replica design. A frame of 20 x 20 mm T-slot extrusion (the 5-series, 6 mm slot, as
Misumi HFS5-2020: 0.50 kg/m, 183 mm2) with the two bottom side rails in 20 x 40 (HFS5-2040:
0.88 kg/m, 324 mm2), sits inside the side panels of body.py / interior.py. Members are modelled
as plain sections; the slots are ignored, and mass comes from the catalogue linear mass.
All positions and the panel material are ASSUMPTION.

Frame (owner's sketch, 2026-11-07: every extrusion is vertical or horizontal; only the panels lean):
  * a STEPPED frame: a wide bottom frame (two side rails running the full length, joined by
    two end cross rails) and a narrow top frame (end cross rails, side rails and a mast cross
    rail under the deck), joined by four vertical posts that stand on the bottom end cross rails
  * each bottom side rail is a single 20 x 40 member (20 wide, 40 tall, z 126 to 166) with a 16 mm
    hole drilled through it for the pivot shaft (a 12 mm tube), a flanged plain bushing at each
    end of the hole; the shaft's second support is a bushing in the differential housing wall
    (hardware/suspension/differential.py). The tall rail leaves 12 mm of wall above and below the hole.
  * two mid rails along X at z 175 between the posts, with two cross rails at x = +-28
    that carry the differential housing on printed cradles (not modelled)
  * the side panels (the solar panels, 2 mm) are separate sloped plates held PANEL_GAP off
    the frame on four pivot standoffs each, near the corners (two on a bottom rail, two on
    a top rail), as the original's panels stand proud of its body; the pivots take up the
    10 degrees between the horizontal studs and the sloped plate

Joints: every extrusion is cut square; rail-to-rail and post joints are 90 degree butt joints
with standard 20-series corner brackets. The floor, end panels and deck bolt to the frame with
M4 screws into T-nuts. The deck is the lid: it carries the mast.

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
RAIL_H = 40.0            # the bottom side rails are 20 wide x 40 tall (HFS5-2040), standing on the floor, so the 16 mm pivot hole leaves 12 mm of wall above and below
KG_PER_M_2040 = 0.88     # HFS5-2040 catalogue                              stated (catalogue)
F_SLEEVE_L = 20.0
HOLE_D = 16.0            # hole drilled through each bottom side rail for the pivot shaft and its bushings   ASSUMPTION
SLEEVE_OD, SLEEVE_ID = 16.0, 14.0   # aluminium sleeve, 20 long, bonded in the rail hole; it holds the bushings (a 2 mm extrusion wall cannot hold a press fit)   ASSUMPTION
BUSH_ID, BUSH_OD, BUSH_L = 12.0, 14.0, 9.0   # one igus GFM-1214-09 type flanged plain bushing (12 bore, 14 OD, 9 long, H7 press fit) in each end of the sleeve (replaces the 688 bearing)  stated (retailer listing)
EDGE = 0.2               # clearance to the end panels and the floor
G = I.PANEL_GAP          # frame outer faces sit this far inside the side panels (at the top outer corner of the rails)
PIV_X = 150.0            # pivot standoffs at x = +-150, near the corners   ASSUMPTION
PIV_D = 8.0              # standoff stud diameter                          ASSUMPTION
PIV_KG = 0.015           # one standoff with its rod end and fasteners     ASSUMPTION
CROSS_X = 28.0           # differential cross rails at x = +-28
MAST_RAIL_X = 140.7      # cross rail under the mast base; the base (x 122 to 200) also spans the front end rail  ASSUMPTION
MID_Z = 175.0            # centre height of the mid rails          ASSUMPTION
PETG = 1.27              # g/cm3
FIX_PITCH = 100.0        # panel screw pitch                      ASSUMPTION
ALU = 2.70               # g/cm3, standard value for aluminium sheet
PANEL_MASS_NOTE = "aluminium sheet at 2.70 g/cm3"

Z_FLOOR = I.floor_z()                       # floor panel top
Z_DECK = B.DECK_TOP_Z - B.DECK_T            # deck panel underside
X_END = B.SIDE_PLATE_LEN / 2 - I.WALL_T     # inner face of the end panels


def yin(z):
    """Half-width of the cavity at height z (inside the side panels)."""
    return I.inner_half_width(z)


YO = yin(Z_DECK) - G       # outer face of the top frame, posts and mid rails
YB = yin(Z_FLOOR + RAIL_H) - G   # outer face of the bottom frame


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def side_rail(sy, x0, x1, zc, yo=None, h=None):
    """Rail along X, outer face vertical at y = +-yo (default YO), h tall (default P)."""
    yc = (YO if yo is None else yo) - P / 2
    h = P if h is None else h
    return box(x0, x1, sy * yc - P / 2, sy * yc + P / 2, zc - h / 2, zc + h / 2)


def cross_rail(xc, zc, yo=None):
    """Rail along Y at x = xc, ending on the inner faces of the side rails below or above it."""
    w = (YO if yo is None else yo) - P
    return box(xc - P / 2, xc + P / 2, -w, w, zc - P / 2, zc + P / 2)


def post(sx, sy):
    """Vertical post standing on the bottom end cross rail, up to the deck underside."""
    xc = sx * (X_END - P / 2 - EDGE)
    y0, y1 = (YO - P, YO) if sy > 0 else (-YO, -(YO - P))
    return box(xc - P / 2, xc + P / 2, y0, y1, Z_FLOOR + P, Z_DECK)


def standoffs():
    """Eight pivot standoffs: four per side panel, near the corners, two on a bottom side rail and two on a top side rail.
    Each is a horizontal stud from the rail's outer face to the panel (its end is cut by the panel's slope here); the rod end
    or ball joint that takes up the 10 degrees is not modelled."""
    cav = I.cavity()
    out = {}
    for sy in (1, -1):
        for sx in (1, -1):
            for lvl, zc, yo in (("bottom", Z_FLOOR + RAIL_H / 2, YB), ("top", Z_DECK - P / 2, YO)):
                stud = Pos(sx * PIV_X, sy * (yo + (yin(zc) - yo + 6) / 2), zc) * Box(PIV_D, yin(zc) - yo + 6, PIV_D)
                out[f"pivot {lvl} {'F' if sx > 0 else 'R'}{'L' if sy > 0 else 'R'}"] = stud & cav
    return out


def build():
    m = {}
    zb = Z_FLOOR + P / 2                                # bottom end cross rails sit on the floor panel
    zr = Z_FLOOR + RAIL_H / 2                           # the tall bottom side rails too
    zt = Z_DECK - P / 2                                 # top rails sit under the deck panel
    for sx in (1, -1):
        f = 'F' if sx > 0 else 'R'
        m[f"post {f}L"] = post(sx, 1)
        m[f"post {f}R"] = post(sx, -1)
        xc = sx * (X_END - P / 2 - EDGE)
        m[f"bottom end cross {f}"] = cross_rail(xc, zb, YB)
        m[f"top end cross {f}"] = cross_rail(xc, zt)
    inner = X_END - P - 2 * EDGE                       # rails run between the end cross rails
    for sy in (1, -1):
        s = "L" if sy > 0 else "R"
        rail = side_rail(sy, -(X_END - EDGE), X_END - EDGE, zr, YB, RAIL_H)
        m[f"bottom side {s}"] = rail - Pos(0, 0, A.PIVOT_Z) * Rot(90, 0, 0) * Cylinder(HOLE_D / 2, 400.0)   # the pivot shaft goes through
        m[f"top side {s}"] = side_rail(sy, -inner, inner, zt)
        m[f"mid side {s}"] = side_rail(sy, -inner, inner, MID_Z)
    m["top cross under mast"] = cross_rail(MAST_RAIL_X, zt)
    for sx in (1, -1):
        m[f"differential cross {'F' if sx > 0 else 'R'}"] = cross_rail(sx * CROSS_X, MID_Z)
    return m


def bushings():
    """Per side: an aluminium sleeve (16 OD, 14 ID, 20 long) bonded in the hole through the bottom side rail, with a flanged plain
    bushing (12 ID, 14 OD, 9 long) pressed into each end. The flanges are not modelled."""
    out = []
    ring = Cylinder(BUSH_OD / 2, BUSH_L) - Cylinder(BUSH_ID / 2, BUSH_L)
    sleeve = Cylinder(SLEEVE_OD / 2, F_SLEEVE_L) - Cylinder(SLEEVE_ID / 2, F_SLEEVE_L)
    for sy in (1, -1):
        parts = [Pos(0, sy * (YB - P / 2), A.PIVOT_Z) * Rot(90, 0, 0) * sleeve]
        for face in (YB - P, YB):                      # inner and outer rail faces
            yc = face + BUSH_L / 2 if face == YB - P else face - BUSH_L / 2
            parts.append(Pos(0, sy * yc, A.PIVOT_Z) * Rot(90, 0, 0) * ring)
        out.append(Compound(parts))
    return out


def member_kg(name, shape):
    """Catalogue mass of a member: 0.88 kg/m for the 20 x 40 bottom side rails, 0.50 kg/m for the rest."""
    return member_length(name, shape) / 1000.0 * (KG_PER_M_2040 if name.startswith("bottom side") else KG_PER_M)


def member_length(name, shape):
    bb = shape.bounding_box()
    if name.startswith("post"):
        return Z_DECK - Z_FLOOR - P
    dims = sorted([bb.size.X, bb.size.Y, bb.size.Z], reverse=True)
    return dims[0]


if __name__ == "__main__":
    cav = I.cavity()
    shell = I.shell(cav)
    members = build()
    bush = bushings()
    plates = []
    dh = A.differential()
    contents = {**I.placed_parts(), **{("differential " + k.replace("diff_", "")): v for k, v in dh.items()}}

    print(f"profile {P:.0f} x {P:.0f}, {KG_PER_M} kg/m; panels {I.WALL_T:.0f} mm (side, end, floor), {B.DECK_T:.0f} mm deck")
    print("\nmember list (name, length mm)")
    total = 0.0
    frame_kg = 0.0
    for n, s in members.items():
        L = member_length(n, s)
        total += L
        frame_kg += member_kg(n, s)
        print(f"  {n:26s} {L:6.1f}")
    print(f"  total {total / 1000:.2f} m  ->  {frame_kg:.2f} kg ({KG_PER_M_2040} kg/m for the 20 x 40 bottom side rails, {KG_PER_M} for the rest)")

    print("\ncontainment in the cavity (mm3 outside, want 0)")
    bad = [(n, s.volume - (s & cav).volume) for n, s in members.items() if s.volume - (s & cav).volume > 0.5]
    print("  members:", "all inside" if not bad else bad)
    badb = [round(sum(b.volume for b in bs) - (bs & cav).volume, 1) for bs in bush]
    print("  bushings outside:", badb)

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
    allm = Compound(list(members.values()))
    for n, c in contents.items():
        v = (allm & c).volume
        print(f"  {n:42s}: {v:8.1f}")

    print("\nshafts and bushings")
    for sy in (1, -1):
        arm, _, _ = A.side(sy)
        sh = arm["shaft"]
        print(f"  shaft {'L' if sy > 0 else 'R'} vs members {sum((sh & s).volume for s in members.values()):.1f}; "
              f"vs bushings {(sh & bush[0 if sy > 0 else 1]).volume:.1f}")
        rail = members[f"bottom side {'L' if sy > 0 else 'R'}"]
        print(f"  rail hole {HOLE_D:.0f} mm: bushings vs rail {(bush[0 if sy > 0 else 1] & rail).volume:.1f} mm3; sleeve OD {SLEEVE_OD:.0f} in a {HOLE_D:.0f} mm hole")

    print("\nmounting")
    mast_rail = members["top cross under mast"].bounding_box()
    front = members["top end cross F"].bounding_box()
    print(f"  mast base plate x {B.MAST_X - 38:.0f}..{B.MAST_X + 38:.0f}; it lies over the mast cross rail (x {mast_rail.min.X:.0f}..{mast_rail.max.X:.0f}) "
          f"and the front end rail (x {front.min.X:.0f}..{front.max.X:.0f}); cable gap between them {front.min.X - mast_rail.max.X:.0f} mm")
    print(f"  top side rails at y +-{YO - P / 2:.0f}: the mast plate (y +-38) lies between their outer faces, "
          f"so the plate bolts to the cross rail and front end rail, and its cable hole can sit in the gap between them")

    # ---- connectivity: every member must touch another along a face (joint), and the frame must be one piece ----
    names_ = list(members)
    def grown(sh):
        bb = sh.bounding_box()
        return box(bb.min.X - 0.5, bb.max.X + 0.5, bb.min.Y - 0.5, bb.max.Y + 0.5, bb.min.Z - 0.5, bb.max.Z + 0.5)
    gr = {n: grown(s_) for n, s_ in members.items()}
    adj = {n: set() for n in names_}
    for i, a_ in enumerate(names_):
        for b_ in names_[i + 1:]:
            if (gr[a_] & members[b_]).volume > 0.5 and (gr[b_] & members[a_]).volume > 0.5:
                adj[a_].add(b_); adj[b_].add(a_)
    seen, stack = set(), [names_[0]]
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n); stack.extend(adj[n] - seen)
    print(f"\nconnectivity (members within 0.5 mm of each other): {len(seen)} of {len(names_)} in one piece; loose: {[n for n in names_ if n not in seen] or 'none'}")
    for n in names_:
        if len(adj[n]) < 2:
            print(f"  only {len(adj[n])} neighbour(s): {n} -> {sorted(adj[n])}")
    for n in ("bottom side L", "bottom end cross F", "post FL"):
        print(f"  {n}: {sorted(adj[n])}")

    # ---- pivot standoffs ----
    st = standoffs()
    print(f"\npivot standoffs: {len(st)} ({len(st) // 2} per side panel), at x = +-{PIV_X:.0f}; panel held {G:.0f} mm off the frame at the top outer corner of the rails")
    for n, v in list(st.items())[:2]:
        bb = v.bounding_box()
        print(f"  {n}: length {bb.size.Y:.1f} mm, z {bb.min.Z:.1f} to {bb.max.Z:.1f}")
    clash = [(n, m_, round((v & mem).volume, 1)) for n, v in st.items() for m_, mem in members.items() if (v & mem).volume > 0.5]
    print(f"  clashes with members: {clash or 'none'}")
    sides = I.side_panels()
    allm_ = Compound(list(members.values()) + [x for bs in bush for x in bs])
    print(f"  frame and bushings vs the side panels (mm3, want 0): {sum((allm_ & sp).volume for sp in sides):.1f}")

    # ---- joint inventory (explicit, from the topology above) ----
    n_end_cross = sum("end cross" in n for n in members)
    joints = {
        "bottom end cross rail to bottom side rail (bracket)": 4,
        "bottom end cross rail to post (post stands on it, bracket)": 4,
        "top end cross rail to post (bracket)": 4,
        "top side rail to post (bracket)": 4,
        "mid side rail to post (bracket)": 4,
        "differential cross rail to mid side rail (bracket)": 4,
        "mast cross rail to top side rail (bracket)": 2,
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
    side_b = 8                                         # the pivot standoffs: one M4 into a T-nut each (the side panels have no other fixing)
    total_b = floor_b + deck_b + end_b + side_b
    print(f"\npanel fixing (M4 button head into T-nuts, pitch about {FIX_PITCH:.0f} mm, at least 2 per member)")
    print(f"  floor {floor_b}, deck (the lid) {deck_b}, end panels {end_b}, side panels {side_b} (the 8 pivot standoffs): total {total_b} screws and {total_b} T-nuts")
    print("  mast base: 4 M4 bolts through the base plate and deck into the mast cross rail (x 141) and front end rail (x 178), y +-30")

    # masses
    sh_mass = (shell.volume + sum(sp.volume for sp in sides)) / 1e3 * ALU / 1000.0
    print(f"\npanels (floor, ends, deck and the two side panels of interior.py, {PANEL_MASS_NOTE}): {sh_mass:.2f} kg")
    print(f"frame {frame_kg:.2f} kg; chassis total {sh_mass + frame_kg:.2f} kg (original structure: 2 kg excluding mobility [S26])")
    free = cav.volume - sum(s.volume for s in members.values())
    print(f"cavity {cav.volume / 1e6:.2f} L, frame occupies {(cav.volume - free) / 1e6:.2f} L")

    out = HERE / "out"
    out.mkdir(exist_ok=True)
    export_step(Compound(list(members.values()) + [x for bs in bush for x in bs] + list(st.values()) + [shell] + sides, label="al-maha-chassis"), str(out / "frame.step"))
