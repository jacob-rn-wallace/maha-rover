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


if __name__ == "__main__":
    # ---- stack and layout ----
    print(f"cell stack on the panel: {B.CELL_T:.1f} mm (dummy plates use the same); cell outline {B.CELL_W:.0f} x {B.CELL_H:.0f} mm, "
          f"clip {B.CLIP:.1f} mm; {CELLS_PER_ROW} x {ROWS} per side, row pitch {B.PITCH_U:.1f} x {B.PITCH_V:.1f}")
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
    print(f"  end cell spans x {end_cell_x - B.CELL_W / 2:.1f}..{end_cell_x + B.CELL_W / 2:.1f}; hole at x {end_cell_x + B.HOLE_OFFSET:.1f} (under the cell: "
          f"{'yes' if end_cell_x + B.HOLE_OFFSET < end_cell_x + B.CELL_W / 2 else 'no'})")
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
            v = (j - (ROWS - 1) / 2) * B.PITCH_V
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

    # ---- sun angle ----
    print("\nsun on a near-vertical panel: the normal is 10 degrees above horizontal, so output = normal-incidence power x cos(sun elevation - 10 deg) x cos(azimuth off the panel normal)")
    for e in (10, 30, 50, 70):
        print(f"  elevation {e:2d} deg, facing the sun: {math.cos(math.radians(e - 10)):.2f}")
