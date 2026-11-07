"""al-maha solar panels: AnySolar SM261K10TF modules on the side panels. Checks, wiring and numbers.

Decided 2026-11-07: the primary cell is the AnySolar SM261K10TF module (64 x 45 x 1.2 mm, 10 cells inside, 5.58 V
and 102 mA at the maximum power point, 571 mW, datasheet Rev. May 2021), plain on the original's 5 x 3 grid (row
pitch 46 mm so the 45 mm modules clear). Each module has two solder pads on its back, so the panel is drilled
behind every pad: 2 holes per module, 30 per side, 60 in all. The Futurlec 60 x 30 mm cell is the fallback.

Wiring: three modules in series per column (rows 1 to 3), the five columns in parallel; the + bus runs behind
row 3, the - bus behind row 1, both to a terminal board on the front post.

Run:  .venv/bin/python hardware/solar/solar.py
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "body"))
sys.path.insert(0, str(HERE.parent / "chassis"))
sys.path.insert(0, str(HERE.parent / "suspension"))
import body as B       # noqa: E402
import interior as I   # noqa: E402
import frame as F      # noqa: E402

# ---- SM261K10TF datasheet (typical values, 1 sun, AM1.5, 25 C) ----
VOC, ISC, VMP, IMP, PMP = 6.91, 0.109, 5.58, 0.102, 0.571
DVOC_DT = -0.0174        # V per kelvin per module (10 cells)
N_SERIES = B.N_ROWS      # modules in series per column
WIRE_R = 0.0842          # ohm per metre, 24 AWG copper (standard value)
SLACK = 1.3
V_MAX_BQ25798, V_MAX_BUCK = 24.0, 28.0     # input limits: BQ25798 recommended, cheap buck modules' listed input


def electrical():
    voc, vmp = N_SERIES * VOC, N_SERIES * VMP
    i_side = B.N_COLS * IMP
    print("\nElectrical (datasheet values; arithmetic is mine)")
    print(f"  module: Voc {VOC} V, Isc {ISC * 1000:.0f} mA, Vmpp {VMP} V, Impp {IMP * 1000:.0f} mA, Pmpp {PMP * 1000:.0f} mW; "
          f"{DVOC_DT * 1000:.1f} mV/K Voc")
    print(f"  a column of {N_SERIES} in series: Voc {voc:.2f} V, Vmpp {vmp:.2f} V, {IMP * 1000:.0f} mA, {vmp * IMP:.2f} W")
    print(f"  {B.N_COLS} columns in parallel (one side): {vmp:.2f} V at {i_side:.2f} A = {vmp * i_side:.2f} W; "
          f"Vmpp/Voc = {vmp / voc:.3f} (BQ25798 VOC_PCT 4h = 0.8125)")
    for temp in (25, 10, 0, -10, -20):
        v = voc + N_SERIES * -DVOC_DT * (25 - temp)
        ok = "ok" if v < V_MAX_BQ25798 else "OVER 24 V"
        print(f"  Voc at {temp:3d} C: {v:5.2f} V ({ok} for the BQ25798, {'ok' if v < V_MAX_BUCK else 'OVER'} for a 28 V buck module)")
    print(f"  both sides (30 modules): {2 * B.N_COLS * B.N_ROWS * PMP:.1f} W if both were lit; one side faces the sun at a time")
    return vmp, voc


def geometry():
    print(f"\nModules: {B.CELL_W:.0f} x {B.CELL_H:.0f} mm, stack {B.CELL_T:.1f} mm; columns pitch {B.PITCH_U:.1f} (gap {B.PITCH_U - B.CELL_W:.1f}), "
          f"rows pitch {B.PITCH_V:.0f} (gap {B.PITCH_V - B.CELL_H:.0f})")
    top = B.FIELD_Z + (B.N_ROWS - 1) / 2 * B.PITCH_V * math.cos(math.radians(B.SIDEWALL_DEG)) + B.CELL_H / 2 * math.cos(math.radians(B.SIDEWALL_DEG))
    bot = B.FIELD_Z - (top - B.FIELD_Z)
    print(f"  field z {bot:.1f} to {top:.1f} (the original's: 196 to 314, 3k); top rail behind the panel starts at z {F.Z_DECK - F.P:.0f}")
    print(f"  body width over the modules at the middle of the field {2 * (I.half_width(B.FIELD_Z) + B.CELL_T):.1f}")


def pads_check():
    pads = B.solar_pads(length=I.WALL_T / I.COS + 2.0)
    print(f"\nPad holes: {len(pads)} of {B.PAD_D} mm, one behind each pad (2 per module), pads {B.PAD_DX:.0f} mm either side of the module centre")
    cav = I.cavity()
    members = F.build()
    plates, _ = F.bearing_plates()
    behind = {**members, **{f"plate {i}": p for i, p in enumerate(plates)}, **F.wedge_strips(members), **F.post_shims(members)}
    # a 4.5 mm clearance cylinder, 14 mm deep, behind each hole
    hits = []
    clear = B.solar_holes(length=14.0, d=4.5)
    for k, c in enumerate(clear):
        for n, m in behind.items():
            v = (c & m).volume
            if v > 0.5:
                hits.append((k, n, round(v, 1)))
    print(f"  members, plates, strips or shims within 2.25 mm of a hole's axis, 14 mm deep: {hits or 'none'}")
    # distance of the outermost holes to the front/rear post faces
    xmax = max(abs((p[4].center().X)) for p in pads)
    print(f"  outermost hole at x = +-{xmax:.1f}; the posts' inner faces are at x = +-{F.X_END - F.P:.1f}: gap {F.X_END - F.P - xmax - B.PAD_D / 2:.1f} mm from the hole edge")
    # holes against the module footprint: all inside their module (pad 10 mm from the end)
    print(f"  each hole is {B.CELL_W / 2 - B.PAD_DX:.0f} mm from its module's end; modules cover their own holes")
    cells = [v for k, v in B.build_rover()[0].items() if k.startswith("cell")]
    from build123d import Pos
    clash = 0.0
    n = (0.0, math.cos(math.radians(B.SIDEWALL_DEG)), math.sin(math.radians(B.SIDEWALL_DEG)))
    for h in B.solar_holes(length=B.CELL_T + 1.0, d=B.PAD_D):
        c = h.center()
        sy = 1 if c.Y > 0 else -1
        moved = Pos(0, sy * n[1] * (B.CELL_T / 2 + 0.5), n[2] * (B.CELL_T / 2 + 0.5)) * h
        for cell in cells:
            clash += (moved & cell).volume
    print(f"  holes extended outward through the stack: overlap with the modules {clash:.0f} mm3 (expected: each hole lies inside its own module)")
    return pads


def wiring(pads):
    print("\nWiring per side (30 holes): modules in columns of 3 in series, 5 columns in parallel")
    by = {}
    for sd, i, j, pol, c in pads:
        by[(sd, i, j, pol)] = c.center()
    P = lambda sd, i, j, pol: (by[(sd, i, j, pol)].X, by[(sd, i, j, pol)].Y, by[(sd, i, j, pol)].Z)
    d = lambda a, b: math.dist(a, b)
    for sd in ("L", "R"):
        jump = [SLACK * d(P(sd, i, j, "+"), P(sd, i, j + 1, "-")) for i in range(B.N_COLS) for j in range(B.N_ROWS - 1)]
        busp = SLACK * sum(d(P(sd, i, B.N_ROWS - 1, "+"), P(sd, i + 1, B.N_ROWS - 1, "+")) for i in range(B.N_COLS - 1))
        busm = SLACK * sum(d(P(sd, i, 0, "-"), P(sd, i + 1, 0, "-")) for i in range(B.N_COLS - 1))
        print(f"  side {sd}: 10 series jumpers of {min(jump):.0f} to {max(jump):.0f} mm (module + pad of row j to the - pad of row j+1, same column); "
              f"+ bus {busp:.0f} mm along row 3; - bus {busm:.0f} mm along row 1")
    # terminal boards on the front posts
    from build123d import Plane, Polygon, Pos, extrude
    boards = {}
    BOARD = (20.0, 8.0, 110.0)
    zc = B.FIELD_Z
    z0, z1 = zc - BOARD[2] / 2, zc + BOARD[2] / 2
    for sy in (1, -1):
        xc = F.X_END - F.P / 2 - F.EDGE
        face = lambda z: F.yin(z) - F.EDGE - F.P / F.COS
        t = BOARD[1] / F.COS
        pts = [(sy * face(z0), z0), (sy * face(z1), z1), (sy * (face(z1) - t), z1), (sy * (face(z0) - t), z0)]
        boards["board " + ("L" if sy > 0 else "R")] = Pos(xc, 0, 0) * extrude(Plane.YZ * Polygon(*pts, align=None), amount=BOARD[0] / 2, both=True)
    members = F.build()
    plates, _ = F.bearing_plates()
    allf = list(members.values()) + plates + list(F.wedge_strips(members).values()) + list(F.post_shims(members).values()) + list(I.placed_parts().values())
    bad = [(n, round(sum((b & m).volume for m in allf), 1)) for n, b in boards.items() if sum((b & m).volume for m in allf) > 0.5]
    print(f"  terminal board per side on the front post ({BOARD[0]:.0f} x {BOARD[1]:.0f} x {BOARD[2]:.0f} mm, z {z0:.0f} to {z1:.0f}): clashes {bad or 'none'}")
    ctrl = I.placed_parts()["solar charge controller"].center()
    for sy, nm in ((1, "L"), (-1, "R")):
        b = boards["board " + nm].center()
        print(f"  board {nm} to the charger: {SLACK * math.dist((b.X, b.Y, b.Z), (ctrl.X, ctrl.Y, ctrl.Z)):.0f} mm of lead (two wires)")
    for label, amps in (("array current 0.51 A", 0.51),):
        L = 2 * 0.5
        print(f"  {label} over 1 m of 24 AWG lead pair drops {amps * L * WIRE_R:.2f} V of 16.7 V")
    pad_gap = F.X_END - F.P
    return boards


def cost():
    print("\nCost (DigiKey listing for the TF part, qty-1 US$16.32, US$13.84 at 10, US$10.58 at 500; 12 week lead time; 93 in stock when seen)")
    for n, price, lab in ((15, 16.32, "one panel at qty 1"), (30, 16.32, "both panels at qty 1"), (30, 13.84, "both panels at the 10-unit tier")):
        print(f"  {lab}: {n} x {price:.2f} = US${n * price:.0f}")


if __name__ == "__main__":
    electrical()
    geometry()
    pads = pads_check()
    wiring(pads)
    cost()
