"""al-maha 2.4 GHz antenna: a vertical dipole on the top face of the body, 290 mm behind the mast, after the original's sleeve dipole.

Source: Gadhafi et al., Sensors, "Investigating the Impact of Lunar Rover Structure and Lunar Surface Characteristics on Antenna Performance" [S11, S15]. Rashid's primary
communication (rover to lander) uses a sleeve dipole, 2.23 dBi; the paper models it at 2.42 GHz, 55.7 mm long (inner conductor and sleeve), covered by a 0.2 mm ABS tube to
a 159.5 mm "commercial height", and puts the rover's mast 290 mm from it. The owner reports a vertical dipole on the body's top face in many photographs of the original.
[S28] (Serria et al., IEEE CAMA 2023) adds: 2.42 GHz, 55.7 mm core, 159.5 mm with the ABS cover, 2.23 dBi, and a Fig. 2 render with the antenna as a tall vertical rod on a stand on the top deck.
Position: x = mast x - 290 = -129.3 mm; y about +58 mm is my reading of the front view of [S18] Fig. 1, where a gold dome with a thin near-vertical rod rises at the right of the
deck (`docs/original-dimensions.md` 3m); unverified. (The thin tilted rod at the rear end of the deck in that figure is probably a Langmuir probe, not this antenna.)

The replica uses it for 2.4 GHz with an off-the-shelf dipole of the paper's length: the AIR802 ANRD2403-RSP (3 dBi, 13.5 x 158 mm, black, RP-SMA plug; listing) is modelled, on a 6 mm aluminium
block; the 5 dBi ANRD2405-RPSMA (157.4 mm) is the alternative. Shorter ones: Taoglas GW.20.A151W (89.5 mm, white), Adafruit 944 swivel (100 mm, 9.92 g), LSR (105 mm, black); listings. Frame as in body.py.
Run:  .venv/bin/python hardware/body/antenna.py
"""
import sys
from pathlib import Path

from build123d import Box, Cylinder, Pos

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import body as B  # noqa: E402

MAST_TO_ANTENNA = 290.0            # mm, stated [paper], mast to dipole
ANT_X = B.MAST_X - MAST_TO_ANTENNA # -129.3
ANT_Y = 58.0                       # my reading of the front view: unverified
ANT_L, ANT_D = 158.0, 13.5         # AIR802 ANRD2403-RSP, 3 dBi, 13.5 x 158 mm, black, RP-SMA plug (retailer listing); the paper's antenna is 159.5 mm
MASS = 0.015 + 0.004               # kg: antenna 15 g (ASSUMPTION: a 158 mm rubber duck, mass not found; the shorter Adafruit 100 mm one lists 9.92 g), mounting block ASSUMPTION


def build():
    z0 = B.DECK_TOP_Z
    block = Pos(ANT_X, ANT_Y, z0 + 3.0) * Box(20.0, 20.0, 6.0)                                   # 6 mm aluminium mounting block, ASSUMPTION
    ant = Pos(ANT_X, ANT_Y, z0 + 6.0 + ANT_L / 2) * Cylinder(ANT_D / 2, ANT_L)
    return {"antenna block": block, "antenna": ant}


if __name__ == "__main__":
    from build123d import Compound
    p = build()
    bb = Compound(list(p.values())).bounding_box()
    print(f"antenna x {bb.min.X:.1f}..{bb.max.X:.1f}, y {bb.min.Y:.1f}..{bb.max.Y:.1f}, z {bb.min.Z:.1f}..{bb.max.Z:.1f}; "
          f"mast at x {B.MAST_X:.1f}, so {B.MAST_X - ANT_X:.0f} mm behind it; deck x +-{B.DECK_LEN / 2:.1f}, half-width {B.TOP_WIDTH / 2:.0f}")
