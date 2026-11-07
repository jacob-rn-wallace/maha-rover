"""al-maha chassis: T-slot aluminium frame behind sheet panels, plus bearing plates.

Replica design. A frame of 20 x 20 mm T-slot extrusion (the 5-series, 6 mm slot, as
Misumi HFS5-2020: 0.50 kg/m, 183 mm2) sits just inside the panels of body.py / interior.py.
The panels (2 mm aluminium sheet on the sides, ends and floor, 3 mm on the deck) bolt to
it through the slots. Members are modelled as plain 20 x 20 sections; the slots are
ignored, and mass comes from the catalogue linear mass. All positions and the panel
material are ASSUMPTION.

Frame (decided 2026-11-07: every extrusion is vertical or horizontal; only the panels lean):
  * a plain rectangular box of members, as wide as the cavity is at the deck (the narrowest
    point), so every member's outer face is vertical at y = +-YO
  * bottom frame: two end cross rails and two side rails, on the floor panel; the side
    rails are split at |x| < GAP to let the pivot shafts through
  * top frame: two end cross rails, two side rails, and a cross rail under the mast base
  * four vertical corner posts
  * two mid rails along X at z 175, with two cross rails at x = +-28 that carry the
    differential housing on printed cradles (not modelled)
  * the sloped side panels stand off the frame on printed ribs (two per side, at x = +-100)
  * two bearing plates (6 mm, in the XZ plane against the bottom rails) at x = 0, each with
    a standoff tube out to the side panel; a 688 bearing at each end of the tube carries the
    pivot shaft

Joints and fixing (see docs/frame-spec.md): every extrusion is cut square and every
rail-to-rail and rail-to-post joint is a plain 90 degree butt joint with a standard 20-series
corner bracket. No wedge shims. The 10 degree slope appears only in the panels, the ribs and
the standoff tube ends. Panels bolt to the frame with M4 screws into T-nuts, to the ribs with
heat-set inserts. The deck is the lid: it carries the mast.

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
PLATE_X = 25.0           # the plate reaches this far past GAP over the rail ends   ASSUMPTION
PLATE_Z1 = 166.0         # top of the bearing plate                ASSUMPTION
TUBE_OD = 22.0           # standoff tube, bearing bore 16 mm inside   ASSUMPTION
RIB_T = 6.0              # printed rib thickness                    ASSUMPTION
RIB_X = 100.0            # ribs at x = +-100                        ASSUMPTION
PETG = 1.27              # g/cm3
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


YO = yin(Z_DECK) - EDGE     # outer face of every member: the cavity is narrowest at the deck


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def side_rail(sy, x0, x1, zc):
    """Rail along X, outer face vertical at y = +-YO."""
    yc = YO - P / 2
    return box(x0, x1, sy * yc - P / 2, sy * yc + P / 2, zc - P / 2, zc + P / 2)


def cross_rail(xc, zc, abut=None):
    """Rail along Y at x = xc between the two sides, ending on the inner faces of the posts or side rails."""
    w = YO - P
    return box(xc - P / 2, xc + P / 2, -w, w, zc - P / 2, zc + P / 2)


def post(sx, sy):
    """Vertical corner post, floor panel to deck underside."""
    xc = sx * (X_END - P / 2 - EDGE)
    return box(xc - P / 2, xc + P / 2, sy * (YO - P) if sy > 0 else -YO, YO if sy > 0 else -(YO - P), Z_FLOOR, Z_DECK)


def ribs():
    """Printed ribs that stand the sloped side panels off the vertical frame: a trapezoid in the YZ plane, flat edge
    against the outer faces of the rails (bolted to their outer slots), sloped edge under the panel."""
    out = {}
    z0, z1 = Z_FLOOR, Z_DECK - P
    for sy in (1, -1):
        for sx in (1, -1):
            pts = [(sy * YO, z0), (sy * (yin(z0) - EDGE), z0), (sy * (yin(z1) - EDGE), z1), (sy * YO, z1)]
            out[f"rib {'F' if sx > 0 else 'R'}{'L' if sy > 0 else 'R'}"] = Pos(sx * RIB_X, 0, 0) * extrude(
                Plane.YZ * Polygon(*pts, align=None), amount=RIB_T / 2, both=True)
    return out


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
    """Per side: a 6 mm plate in the XZ plane against the outer faces of the split bottom rails, and a standoff tube from
    the plate out to the side panel (end cut by the panel). 688 bearings sit in the plate bore and in the tube's outer end."""
    cav = I.cavity()
    plates, bearings = [], []
    z0 = Z_FLOOR
    for sy in (1, -1):
        y0 = YO
        plate = box(-(GAP + PLATE_X), GAP + PLATE_X, min(sy * y0, sy * (y0 + PLATE_T)), max(sy * y0, sy * (y0 + PLATE_T)), z0, PLATE_Z1)
        y_wall = yin(A.PIVOT_Z) - EDGE
        tube = box(-TUBE_OD / 2, TUBE_OD / 2, min(sy * (y0 + PLATE_T), sy * (y_wall + 12)), max(sy * (y0 + PLATE_T), sy * (y_wall + 12)),
                   A.PIVOT_Z - TUBE_OD / 2, A.PIVOT_Z + TUBE_OD / 2)
        tube = tube & cav                                  # the panel cuts the end at 10 degrees
        bore = Pos(0, 0, A.PIVOT_Z) * Rot(90, 0, 0) * Cylinder(BEARING_SEAT_R, 400.0)
        plates.append((plate + tube) - bore)
        ring = Cylinder(BEARING_SEAT_R, 5.0) - Cylinder(4.2, 5.0)
        b_in = Pos(0, sy * (y0 + PLATE_T / 2), A.PIVOT_Z) * Rot(90, 0, 0) * ring
        b_out = Pos(0, sy * (y_wall - 2.0 - 2.5 - 0.5), A.PIVOT_Z) * Rot(90, 0, 0) * ring
        bearings.append(Compound([b_in, b_out]))
    return plates, bearings


def member_length(name, shape):
    bb = shape.bounding_box()
    if name.startswith("post"):
        return Z_DECK - Z_FLOOR
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
    print(f"  mast base plate x {B.MAST_X - 38:.0f}..{B.MAST_X + 38:.0f}; it lies over the mast cross rail (x {mast_rail.min.X:.0f}..{mast_rail.max.X:.0f}) "
          f"and the front end rail (x {front.min.X:.0f}..{front.max.X:.0f}); cable gap between them {front.min.X - mast_rail.max.X:.0f} mm")
    print(f"  top side rails at y +-{YO - P / 2:.0f}: the mast plate (y +-38) lies between their outer faces, "
          f"so the plate bolts to the cross rail and front end rail, and its cable hole can sit in the gap between them")

    # ---- printed ribs ----
    rb = ribs()
    print(f"\nprinted parts: {len(rb)} ribs ({RIB_T:.0f} mm thick), total {sum(v.volume for v in rb.values()) / 1e3:.1f} cm3, "
          f"{sum(v.volume for v in rb.values()) / 1e3 * PETG / 1000:.2f} kg in PETG")
    out_s = [n for n, v in rb.items() if v.volume - (v & cav).volume > 0.5]
    print(f"  outside the cavity: {out_s or 'none'}")
    clash = []
    for n, v in rb.items():
        for m, mem in {**members, **{f"plate{i}": p_ for i, p_ in enumerate(plates)}}.items():
            o = (v & mem).volume
            if o > 0.5:
                clash.append((n, m, round(o, 1)))
    print(f"  clashes with members and plates: {clash or 'none'}")
    print(f"  member outer faces at y = +-{YO:.1f}; gap to the panel at the floor {yin(Z_FLOOR) - EDGE - YO:.1f} mm, at the top rail's lower edge {yin(Z_DECK - P) - EDGE - YO:.1f} mm")

    # ---- joint inventory (explicit, from the topology above) ----
    n_end_cross = sum("end cross" in n for n in members)
    joints = {
        "end cross rail to post (bracket)": n_end_cross * 2,
        "side rail to end cross rail (bracket)": 4 + 4,                 # bottom (outer ends) and top side rails
        "mid side rail to post (bracket)": 4,
        "differential cross rail to mid side rail (bracket)": 4,
        "mast cross rail to top side rail (bracket)": 2,
        "bottom side rail to bearing plate (plate bolted over the rail end, 2 bolts)": 4,
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
    inserts = len(rb) * 4 + 2 * 4                      # side panels: 4 heat-set M3 inserts per rib, 4 on each standoff tube end (ASSUMPTION)
    total_b = floor_b + deck_b + end_b
    print(f"\npanel fixing (M4 button head into T-nuts, pitch about {FIX_PITCH:.0f} mm, at least 2 per member)")
    print(f"  floor {floor_b}, deck (the lid) {deck_b}, end panels {end_b}: total {total_b} screws and {total_b} T-nuts")
    print(f"  side panels (they stand off the frame, so no T-nuts): {inserts} M3 screws into heat-set inserts in the ribs and standoff tubes; edge angles not designed")
    print("  mast base: 4 M4 bolts through the base plate and deck into the mast cross rail (x 141) and front end rail (x 178), y +-30")

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
    export_step(Compound(list(members.values()) + plates + bearings + list(rb.values()) + [shell], label="al-maha-chassis"), str(out / "frame.step"))
