"""al-maha solar provisions: real cells in place of the dummy ones, wire holes, wiring options.

The 30 cells of body.py are plates today. This script checks what must be true for real cells
to go on later and prints the expected electrical options. Cell data are quoted in
docs/solar-spec.md with their sources and caveats; derived numbers are marked.

  * Stack on the panel: CELL_T (body.py) leaves room for insulating film, adhesive, the cell
    and a 200 um cover glass [S10].
  * Wire holes: 5 mm holes through each side panel beside both ends of every cell row, so all
    string ends come inside the cavity and series/parallel is chosen on a terminal block.
  * Clearance: nothing in the frame, wedge strips, bearing plates or shaft path stands behind
    the holes; harness length to the charge controller.

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

# ---- cell data as read (docs/solar-spec.md) --------------------------------
TJ_AREA = 26.5           # cm2, CESI CTJ30 class (3g)                       derived
TJ_VM, TJ_JM = 2.3, 17.1  # V, mA/cm2 at the maximum power point, CESI CTJ30 v2025.1 table as extracted from text
TJ_PMAX = 39.8           # mW/cm2, BOL, 29.1 % (same table); test conditions not read
SI_V, SI_I, SI_AREA = 0.582, 5.93, 153.0   # C60-class 125 x 125 mm cell: a database entry (rounded), area derived
CELLS_PER_ROW, ROWS, SIDES = B.N_COLS, B.N_ROWS, 2
AM0 = 1367.0             # W/m2, solar constant (standard value)


def tj():
    i_cell = TJ_JM * TJ_AREA / 1000.0
    p_cell = TJ_PMAX * TJ_AREA / 1000.0
    v_str = CELLS_PER_ROW * TJ_VM
    return i_cell, p_cell, v_str


def si():
    j = SI_I / SI_AREA                        # A/cm2 at one sun, the whole cell
    i_piece = j * TJ_AREA
    return i_piece, i_piece * SI_V, SIDES


def pieces_per_cell(a, b, side=125.0, margin=2.0, kerf=0.5):
    """Most a x b pieces that fit in a side x side cell by one guillotine split, with rotation, an edge
    margin and a saw kerf. A simple packing, not an optimised one."""
    W = side - 2 * margin
    best = 0
    step = 0.5
    x = 0.0
    while x <= W:
        n1 = math.floor((x + kerf) / (a + kerf)) * math.floor((W + kerf) / (b + kerf))
        n2 = math.floor((W - x + kerf) / (b + kerf)) * math.floor((W + kerf) / (a + kerf))
        best = max(best, n1 + n2)
        x += step
    # and the pure rotated case
    best = max(best, math.floor((W + kerf) / (b + kerf)) * math.floor((W + kerf) / (a + kerf)))
    return best


def silicon_options():
    rows = []
    j = SI_I / SI_AREA                       # A/cm2, whole C60-class cell at one sun
    for name, a, b in (("full outline", 69.0, 39.0), ("inset 2 mm (65 x 35)", 65.0, 35.0), ("inset 5 mm (59 x 29)", 59.0, 29.0)):
        area = (a * b - (2 * B.CLIP * B.CLIP / 2 if a == 69.0 else 0.0)) / 100.0   # cm2, the full outline loses its two clipped corners
        n = pieces_per_cell(a, b)
        i = j * area
        cells = math.ceil(CELLS_PER_ROW * ROWS / n)
        rows.append((name, a, b, area, n, i, SI_V * i, cells))
    return rows


# ---- wiring plan --------------------------------------------------------------
WIRE_R = 0.0842          # ohm per metre, 24 AWG copper (standard table value)
SLACK = 1.3              # routing slack on straight-line wire lengths


def hole_table():
    """Hole id -> (x, y, z) of each of the 12 holes, on the inner face of the panel.
    Id: side L/R, row 1..3 (bottom to top), end F (front, +x) or R (rear, -x)."""
    holes = B.solar_holes(length=I.WALL_T / I.COS)       # starts at the outer face, runs inward by the panel thickness
    names = []
    for sy in ("L", "R"):
        for j in (1, 2, 3):
            for e in ("R", "F"):
                names.append(f"{sy}{j}{e}")
    # solar_holes order: for sy in (1,-1): for j: for sx in (1,-1) -> F then R
    order = []
    for sy in ("L", "R"):
        for j in (1, 2, 3):
            for e in ("F", "R"):
                order.append(f"{sy}{j}{e}")
    out = {}
    for n, h in zip(order, holes):
        bb = h.bounding_box()
        c = h.center()
        out[n] = (c.X, c.Y, c.Z)
    return out


def wiring_report():
    H = hole_table()
    ctrl = I.placed_parts()["solar charge controller"].center()
    C = (ctrl.X, ctrl.Y, ctrl.Z)
    d = lambda a, b: math.dist(a, b)
    print("\nwire holes (x, y, z on the inner face of the panel)")
    for n, p in H.items():
        print(f"  {n}  ({p[0]:7.1f}, {p[1]:7.1f}, {p[2]:6.1f})")
    print("\nserpentine for one side (15 cells in series; row 1 is the bottom row)")
    print("  row 1 rear (-)  ->  row 1 front  =jumper=  row 2 front  ->  row 2 rear  =jumper=  row 3 rear  ->  row 3 front (+)")
    for sy in ("L", "R"):
        j1 = SLACK * d(H[f"{sy}1F"], H[f"{sy}2F"])
        j2 = SLACK * d(H[f"{sy}2R"], H[f"{sy}3R"])
        lm = SLACK * d(H[f"{sy}1R"], C)
        lp = SLACK * d(H[f"{sy}3F"], C)
        print(f"  side {sy}: jumpers {j1:.0f} and {j2:.0f} mm; lead (-) from {sy}1R {lm:.0f} mm; lead (+) from {sy}3F {lp:.0f} mm")
    # voltage drop at the option currents
    for label, amps in (("Futurlec, 15 in series, listed 0.28 A", 0.28), ("Futurlec, if 0.64 A at one sun", 0.64), ("silicon cut to 69 x 39, 15 in series", 1.03), ("triple junction, three rows in parallel", 3 * 0.453), ("tiled 52 x 19, listed, 30 in series", 0.40)):
        L = 2 * 0.55                                    # a typical lead pair, metres (+ and -)
        print(f"  {label}: {amps:.2f} A over {L:.2f} m of 24 AWG drops {amps * L * WIRE_R:.2f} V")
    return H


BOARD = (20.0, 8.0, 60.0)    # terminal board on each post's cavity-facing face: x (the post width), y, z    ASSUMPTION
BOARD_Z = 235.0              # centre height; the hole rows are at about 194, 234 and 275


def terminal_boards():
    """One terminal board per post (four per side pair would be two per side: front and rear), lying flat on the post's
    cavity-facing face, which leans 10 degrees like the post."""
    from build123d import Plane, Polygon, Pos, extrude
    out = {}
    z0, z1 = BOARD_Z - BOARD[2] / 2, BOARD_Z + BOARD[2] / 2
    for sx in (1, -1):
        for sy in (1, -1):
            xc = sx * (F.X_END - F.P / 2 - F.EDGE)
            face = lambda z: F.yin(z) - F.EDGE - F.P / F.COS
            t = BOARD[1] / F.COS
            pts = [(sy * face(z0), z0), (sy * face(z1), z1), (sy * (face(z1) - t), z1), (sy * (face(z0) - t), z0)]
            out[f"board {'F' if sx > 0 else 'R'}{'L' if sy > 0 else 'R'}"] = Pos(xc, 0, 0) * extrude(Plane.YZ * Polygon(*pts, align=None), amount=BOARD[0] / 2, both=True)
    return out


if __name__ == "__main__":
    # ---- stack and layout ----
    print(f"cell stack on the panel: {B.CELL_T:.1f} mm; plain cell {B.CELL_W:.0f} x {B.CELL_H:.0f} mm (Futurlec SZGD6030), "
          f"{CELLS_PER_ROW} x {ROWS} per side on the original's grid, pitch {B.PITCH_U:.1f} x {B.PITCH_V:.1f}; gaps {B.PITCH_U - B.CELL_W:.1f} x {B.PITCH_V - B.CELL_H:.1f} mm")
    width_over_cells = 2 * (I.half_width(B.FIELD_Z) + B.CELL_T)
    print(f"body width over the cells at the middle of the field {width_over_cells:.1f}")

    # ---- holes ----
    holes = B.solar_holes(length=I.WALL_T / I.COS + 2.0)
    print(f"\nwire holes: {len(holes)} of {B.HOLE_D:.0f} mm, {B.HOLE_OFFSET:.0f} mm outboard of the end cells' centres (x = +-{(B.N_COLS - 1) / 2 * B.PITCH_U + B.HOLE_OFFSET:.1f})")
    sh = I.shell(I.cavity())
    # each hole should remove panel material only
    print(f"  panel shell volume with holes {sh.volume / 1e3:.1f} cm3")
    # holes sit under the end cell: check the hole is within the end cell's x span
    end_cell_x = (B.N_COLS - 1) / 2 * B.PITCH_U
    print(f"  end cell spans x {end_cell_x - B.CELL_W / 2:.1f}..{end_cell_x + B.CELL_W / 2:.1f}; each hole at x {end_cell_x + B.HOLE_OFFSET:.1f}, {B.HOLE_V:.1f} mm up the slope from its row's centre, "
          f"in the gap above the row ({(B.PITCH_V - B.CELL_H):.0f} mm gap, hole {B.HOLE_D:.0f} mm; the cell edge is {B.CELL_H / 2:.0f} mm from the row centre)")
    cells_ = [v for k, v in B.build_rover()[0].items() if k.startswith("cell")]
    h_out = B.solar_holes(length=B.CELL_T + 2.0, d=B.HOLE_D)       # starts at the outer face, runs inward; the cells stand outside, so move the test out
    from build123d import Pos
    clash = 0.0
    for h in B.solar_holes(length=B.CELL_T + 1.0, d=B.HOLE_D):
        # extend the hole outward through the cell stack: shift by the stack thickness along the wall normal
        n = (0.0, math.cos(math.radians(B.SIDEWALL_DEG)), math.sin(math.radians(B.SIDEWALL_DEG)))
        c = h.center()
        sy = 1 if c.Y > 0 else -1
        moved = Pos(0, sy * n[1] * (B.CELL_T / 2 + 0.5), n[2] * (B.CELL_T / 2 + 0.5)) * h
        for cell in cells_:
            clash += (moved & cell).volume
    print(f"  holes extended outward through the cell stack against the 30 cells: overlap {clash:.1f} mm3 (want 0)")
    # clearance behind the holes: a 12 mm clearance cylinder 14 mm deep must not meet the frame
    clear = B.solar_holes(length=14.0, d=12.0)
    members = F.build()
    plates, _ = F.bearing_plates()
    strips = F.wedge_strips(members)
    shims = F.post_shims(members)
    behind = {**members, **{f"plate {i}": p for i, p in enumerate(plates)}, **strips, **shims}
    hits = []
    for k, c in enumerate(clear):
        for n, m in behind.items():
            v = (c & m).volume
            if v > 0.5:
                hits.append((k, n, round(v, 1)))
    print(f"  members, plates, strips or shims within 6 mm of a hole's axis, 14 mm deep: {hits or 'none'}")
    mids = F.MID_Z
    # nearest frame member to each hole centre (z gap)
    rows_z = []
    for sy in (1,):
        for j in range(ROWS):
            v = (j - (ROWS - 1) / 2) * B.PITCH_V + B.HOLE_V
            rows_z.append(B.FIELD_Z + v * math.cos(math.radians(B.SIDEWALL_DEG)))
    print(f"  hole rows at z {', '.join(f'{z:.0f}' for z in rows_z)}; the mid rail occupies z {mids - F.P / 2:.0f} to {mids + F.P / 2:.0f} "
          f"(and its wedge strip), the top rail z {F.Z_DECK - F.P:.0f} to {F.Z_DECK:.0f}; posts at x +-{F.X_END - F.P:.0f} to +-{F.X_END:.0f}")

    # ---- harness ----
    ctrl = I.placed_parts()["solar charge controller"].center()
    far = 0.0
    for h in holes:
        c = h.center()
        d = math.dist((c.X, c.Y, c.Z), (ctrl.X, ctrl.Y, ctrl.Z))
        far = max(far, d)
    print(f"\ncharge controller at ({ctrl.X:.0f}, {ctrl.Y:.0f}, {ctrl.Z:.0f}); longest straight line from a hole {far:.0f} mm; "
          f"allow about {far * 1.3:.0f} mm of wire per lead with routing slack (12 leads' worth of runs, 6 per side)")

    # ---- electrical options ----
    i_cell, p_cell, v_str = tj()
    print("\nOption A, triple-junction cells (CTJ30 class), as the original")
    print(f"  per cell: Vm {TJ_VM} V, Im {i_cell * 1000:.0f} mA, Pmax {p_cell:.2f} W at AM0 BOL (derived from the datasheet table: {TJ_JM} mA/cm2, {TJ_PMAX} mW/cm2 x {TJ_AREA} cm2)")
    print(f"  one row of {CELLS_PER_ROW} in series: {v_str:.1f} V, {i_cell:.2f} A, {v_str * i_cell:.1f} W")
    print(f"  three rows in parallel (one side): {v_str:.1f} V, {ROWS * i_cell:.2f} A, {ROWS * v_str * i_cell:.1f} W; both sides {SIDES * ROWS * v_str * i_cell:.1f} W "
          f"(one side faces the sun at a time; the original's stated peak is 15 W [S3])")
    print(f"  string voltage {v_str:.1f} V is above the 2S pack's 8.4 V: a buck MPPT charger")
    i_p, p_p, _ = si()
    v_si = CELLS_PER_ROW * ROWS * SI_V
    print("\nOption B, silicon cells cut to the 69 x 39 outline (C60-class, 22.5 percent)")
    print(f"  per piece at one sun, perpendicular: {SI_V} V, {i_p:.2f} A, {SI_V * i_p:.2f} W (database entry, rounded; cutting losses ignored)")
    print(f"  all 15 cells of one side in one series string: {v_si:.1f} V, {i_p:.2f} A, {v_si * i_p:.1f} W; "
          f"that is close to the pack's 8.4 V, so a buck-boost MPPT charger is needed")
    print(f"  or three rows of 5 in parallel: {CELLS_PER_ROW * SI_V:.1f} V, {ROWS * i_p:.2f} A (too low for a 2S charge: a boost converter)")

    # ---- decided option: Futurlec SZGD6030, plain ----
    n = CELLS_PER_ROW * ROWS
    print(f"\nDecided cell (2026-11-07): Futurlec SZGD6030, 60 x 30 x 2.8 mm mono, 0.48 V, 280 mA listed (test light not stated), 17 percent")
    print(f"  {n} per side in series: {n * 0.48:.1f} V, 0.28 A listed = {n * 0.48 * 0.28:.1f} W per side; 60 x 30 mm = 18 cm2, so at one sun and 17 percent about "
          f"{0.17 * 0.1 * 18 / 0.48:.2f} A and {n * 0.17 * 0.1 * 18:.1f} W per side if the listed current were a one-sun figure (arithmetic, unconfirmed)")
    print(f"  both sides {2 * n} cells: US$1.50 each = {2 * n * 1.5:.0f}, US$1.35 from 25 = {2 * n * 1.35:.0f}")

    # ---- silicon fill options ----
    print("\nsilicon fill options for the 69 x 39 mm cell positions (one side = 15 positions, 15 pieces in series)")
    print(f"  {'option':24s}{'piece mm':>10s}{'cm2':>7s}{'per cell':>9s}{'A':>7s}{'W/piece':>9s}{'side V':>8s}{'side W':>8s}{'cells/side':>11s}")
    for name, a, b, area, n, i, p, cells in silicon_options():
        print(f"  {name:24s}{a:5.0f} x {b:2.0f}{area:7.1f}{n:9d}{i:7.2f}{p:9.2f}{15 * SI_V:8.1f}{15 * p:8.1f}{cells:11d}")
    j = SI_I / SI_AREA
    print(f"  (per-cm2 current {j * 1000:.1f} mA at one sun from the C60-class entry; cut losses ignored; the pieces' voltage is taken as 0.582 V)")
    # tiled small cells (52 x 19 mm, listed 0.5 V and 400 mA; one reviewer measured 0.65 V and 140 mA)
    fit_x, fit_y = math.floor(69.0 / 52.0), math.floor(39.0 / 19.0)
    per_pos = fit_x * fit_y
    pieces = per_pos * CELLS_PER_ROW * ROWS
    print(f"\n  tiled 52 x 19 mm cells: {per_pos} per position ({fit_x} across, {fit_y} down, covering {per_pos * 52 * 19 / (69 * 39) * 100:.0f} percent of the 69 x 39 outline), "
          f"{pieces} per side, {2 * pieces} for both sides (a pack of 100 covers them)")
    print(f"    listed 0.5 V and 0.40 A: all {pieces} in series {pieces * 0.5:.0f} V, 0.40 A, {pieces * 0.5 * 0.4:.1f} W per side; "
          f"as measured by one reviewer (0.65 V, 0.14 A): {pieces * 0.65:.0f} V, {pieces * 0.65 * 0.14:.1f} W per side")
    print(f"    or {per_pos} pieces in parallel per position and 15 positions in series: 7.5 V, {per_pos * 0.4:.2f} A listed ({15 * 0.5 * per_pos * 0.4:.1f} W)")

    H = wiring_report()
    boards = terminal_boards()
    members_ = F.build()
    plates_, _ = F.bearing_plates()
    cav = I.cavity()
    allf = list(members_.values()) + plates_ + list(F.wedge_strips(members_).values()) + list(F.post_shims(members_).values()) + list(I.placed_parts().values())
    bad = [(n, round(sum((b & m).volume for m in allf), 1)) for n, b in boards.items() if sum((b & m).volume for m in allf) > 0.5]
    out_c = [n for n, b in boards.items() if b.volume - (b & cav).volume > 0.5]
    print(f"\nterminal boards ({BOARD[0]:.0f} x {BOARD[1]:.0f} x {BOARD[2]:.0f} mm, one per post, on its cavity-facing face at z {BOARD_Z:.0f}): "
          f"clashes {bad or 'none'}; outside the cavity {out_c or 'none'}")
    for n, b in boards.items():
        c = b.center()
        near = min(math.dist((c.X, c.Y, c.Z), H[k]) for k in H if k[0] == ('L' if c.Y > 0 else 'R') and k[2] == ('F' if c.X > 0 else 'R'))
        print(f"  {n}: nearest hole {near:.0f} mm from the board centre")

    # ---- sun angle ----
    print("\nsun on a near-vertical panel: the normal is 10 degrees above horizontal, so output = normal-incidence power x cos(sun elevation - 10 deg) x cos(azimuth off the panel normal)")
    for e in (10, 30, 50, 70):
        print(f"  elevation {e:2d} deg, facing the sun: {math.cos(math.radians(e - 10)):.2f}")
