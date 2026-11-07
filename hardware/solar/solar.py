"""al-maha solar panels: tiled back-contact pieces, two per slot, 30 per side in series. Checks, wiring, numbers.

Decided 2026-11-07: each of the 5 x 3 slots on a side panel holds two pieces of a SunPower-type back-contact cell
(a 125 x 41.6 mm third-cut strip cut in four: 31 x 41.6 mm each), 0.5 mm apart, laid on the original's column pitch and
a 42.5 mm row pitch. 30 pieces per side are wired in one series string (about 18.8 V at maximum power), so a cheap
buck 2S MPPT module (BQ24650 or CN3722 type) can charge the pack. Row ends come inside through 5 mm holes
under the end pieces; the serpentine, terminal boards and checks are below.

Cell figures are the retailer's (LinkSolar, full 125 mm cell: 0.625 V, 6.05 A, 3.78 W at standard conditions) scaled by
piece area; Voc and the temperature coefficient are assumptions (typical silicon), marked below.

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

CELL_VMP, CELL_IMP, CELL_P = 0.625, 6.05, 3.78     # full 125 mm cell, retailer's figures
CELL_AREA = 153.0        # cm2, 125 x 125 mm with the clipped corners (derived)
CELL_VOC = 0.70          # V per cell: ASSUMPTION (typical back-contact silicon)
DVOC = -0.0020           # V per kelvin per cell: ASSUMPTION (typical silicon)
PIECES = B.N_COLS * B.N_ROWS * B.PIECES_PER_SLOT   # per side
WIRE_R = 0.0842          # ohm per metre, 24 AWG copper
SLACK = 1.3
BUCK_LIMIT = 28.0        # input limit of the BQ24650 and CN3722 modules (listings recommend under 24 V)


def piece():
    area = B.PIECE_W * B.PIECE_H / 100.0
    return area, CELL_IMP * area / CELL_AREA


def electrical():
    area, imp = piece()
    vmp, voc = PIECES * CELL_VMP, PIECES * CELL_VOC
    print(f"Piece {B.PIECE_W:.0f} x {B.PIECE_H:.1f} mm = {area:.1f} cm2: {CELL_VMP} V, {imp:.2f} A, {CELL_VMP * imp:.2f} W at one sun (full-cell figures scaled by area)")
    print(f"One side, {PIECES} pieces in series ({B.N_ROWS} rows of {PIECES // B.N_ROWS}): Vmp {vmp:.2f} V, Imp {imp:.2f} A, {vmp * imp:.1f} W; "
          f"each row {vmp / B.N_ROWS:.2f} V")
    print(f"  Voc (assumed {CELL_VOC} V per cell) {voc:.1f} V at 25 C")
    for temp in (25, 10, 0, -10, -20):
        v = voc - PIECES * DVOC * (25 - temp)
        print(f"    Voc at {temp:3d} C: {v:5.2f} V ({'under' if v < 24 else 'OVER'} the 24 V the listings recommend, {'under' if v < BUCK_LIMIT else 'OVER'} the 28 V limit)")
    hot = vmp + PIECES * DVOC * 25
    print(f"  Vmp 25 K hotter: {hot:.2f} V; a fixed set point of about 17.5 V sits between the cold and hot Vmp")
    print(f"  both sides: {2 * vmp * imp:.1f} W if both were lit (one side faces the sun at a time)")
    print(f"  pieces in all: {2 * PIECES} = {2 * PIECES / 4:.0f} third-cut strips with no breakage (4 pieces each), {2 * 2 * PIECES / 4:.0f} with a 100 percent margin")
    return vmp, imp


def geometry():
    c = math.cos(math.radians(B.SIDEWALL_DEG))
    top = B.FIELD_Z + ((B.N_ROWS - 1) / 2 * B.PITCH_V + B.PIECE_H / 2) * c
    bot = B.FIELD_Z - (top - B.FIELD_Z)
    print(f"\nLayout: slots {B.SLOT_W:.1f} mm wide on a {B.PITCH_U} mm pitch (gap {B.PITCH_U - B.SLOT_W:.1f}), two pieces {B.PIECE_W:.0f} mm with a {B.PIECE_GAP} mm gap; "
          f"rows {B.PITCH_V} pitch, pieces {B.PIECE_H} tall (gap {B.PITCH_V - B.PIECE_H:.1f}); stack {B.CELL_T} mm; 30 pieces a side")
    print(f"  field z {bot:.1f} to {top:.1f} (the original's cells: 196 to 314, 3k); top rail behind the panel from z {F.Z_DECK - F.P:.0f}")
    print(f"  field x +-{(B.N_COLS - 1) / 2 * B.PITCH_U + B.SLOT_W / 2:.1f}; the posts begin at x = +-{F.X_END - F.P:.0f}")


def holes_check():
    holes = B.solar_holes(length=I.WALL_T / I.COS + 2.0)
    print(f"\nWire holes: {len(holes)} of {B.HOLE_D:.0f} mm at x = +-{B.HOLE_X}, one at each end of each row, under the end pieces "
          f"(end piece spans x {(B.N_COLS - 1) / 2 * B.PITCH_U + B.PIECE_GAP / 2:.1f} to {(B.N_COLS - 1) / 2 * B.PITCH_U + B.PIECE_GAP / 2 + B.PIECE_W:.1f})")
    members = F.build()
    behind = {**members, **F.standoffs()}
    hits = []
    for k, cyl in enumerate(B.solar_holes(length=14.0, d=B.HOLE_D + 2.0)):
        for n, m in behind.items():
            v = (cyl & m).volume
            if v > 0.5:
                hits.append((k, n, round(v, 1)))
    print(f"  members or standoffs within 1 mm of a hole's edge, 14 mm deep: {hits or 'none'}")
    print(f"  nearest post face at x = +-{F.X_END - F.P:.0f}: {F.X_END - F.P - B.HOLE_X - B.HOLE_D / 2:.1f} mm from the hole edge")
    return holes


def hole_table():
    ids = []
    for sy in ("L", "R"):
        for j in (1, 2, 3):
            for e in ("F", "R"):
                ids.append(f"{sy}{j}{e}")
    hs = B.solar_holes(length=I.WALL_T / I.COS)
    # solar_holes order: sy (1,-1), j, sx (1,-1) = F then R
    return {n: (h.center().X, h.center().Y, h.center().Z) for n, h in zip(ids, hs)}


def wiring():
    H = hole_table()
    ctrl = I.placed_parts()["solar charge controller"].center()
    C = (ctrl.X, ctrl.Y, ctrl.Z)
    d = math.dist
    print("\nSerpentine per side (row 1 is the bottom row; 10 pieces per row, tabbed on the rear before bonding)")
    print("  row 1 rear (-) -> row 1 front  =jumper A=  row 2 front -> row 2 rear  =jumper B=  row 3 rear -> row 3 front (+)")
    for sy in ("L", "R"):
        ja = SLACK * d(H[f"{sy}1F"], H[f"{sy}2F"])
        jb = SLACK * d(H[f"{sy}2R"], H[f"{sy}3R"])
        print(f"  side {sy}: jumpers {ja:.0f} and {jb:.0f} mm; lead (-) from {sy}1R {SLACK * d(H[f'{sy}1R'], C):.0f} mm; lead (+) from {sy}3F {SLACK * d(H[f'{sy}3F'], C):.0f} mm")
    amps = piece()[1]
    L = 2 * 0.55
    print(f"  string current {amps:.2f} A over {L:.2f} m of 24 AWG lead pair drops {amps * L * WIRE_R:.2f} V of {PIECES * CELL_VMP:.1f} V")
    return H


def boards(H):
    from build123d import Box, Pos
    BOARD = (20.0, 8.0, 100.0)
    zc = B.FIELD_Z
    z0, z1 = zc - BOARD[2] / 2, zc + BOARD[2] / 2
    out = {}
    for sx in (1, -1):
        for sy in (1, -1):
            xc = sx * (F.X_END - F.P / 2 - F.EDGE)
            face = F.YO - F.P                                  # the post's inner face, vertical
            out[f"board {'F' if sx > 0 else 'R'}{'L' if sy > 0 else 'R'}"] = Pos(xc, sy * (face - BOARD[1] / 2), (z0 + z1) / 2) * Box(BOARD[0], BOARD[1], z1 - z0)
    members = F.build()
    allf = list(members.values()) + list(F.standoffs().values()) + list(I.placed_parts().values())
    bad = [(n, round(sum((b & m).volume for m in allf), 1)) for n, b in out.items() if sum((b & m).volume for m in allf) > 0.5]
    print(f"\nTerminal boards ({BOARD[0]:.0f} x {BOARD[1]:.0f} x {BOARD[2]:.0f} mm, one per post, z {z0:.0f} to {z1:.0f}, on the post's cavity-facing face): clashes {bad or 'none'}")
    for n, b in out.items():
        c = b.center()
        near = min(math.dist((c.X, c.Y, c.Z), H[k]) for k in H if k[0] == ("L" if c.Y > 0 else "R") and k[2] == ("F" if c.X > 0 else "R"))
        print(f"  {n}: nearest hole {near:.0f} mm from the board centre")
    return out


def cost():
    print("\nCost (prices seen, not quoted orders)")
    print("  cells: two LinkSolar lots of 20 third-cut strips at US$16.96 = US$34 (40 strips), if that price is real; else 10 full cells at US$43.60 = US$44 (30 strips)")
    print("  charger: BQ24650 module about US$11 to 17 (ended eBay listings), LaskaKit CN3722 module EUR 10.19; plus 2 Schottky diodes and wire")
    print("  total about US$45 to 61 for both panels")


if __name__ == "__main__":
    electrical()
    geometry()
    holes_check()
    H = wiring()
    boards(H)
    cost()
