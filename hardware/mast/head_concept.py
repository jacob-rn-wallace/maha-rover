"""al-maha mast head, concept B: the layout seen in the CAD figures ([S5] Fig. 1; original-dimensions.md 3l), as a rough model for the owner to judge.

Differences from head.py: an open frame (two vertical arm plates and a thin top plate) instead of closed shells; the camera is a CASPEX stack
(module, square cradle plate, round collar, slotted baffle ring, black hood with a square window) hung off a round gimbal drive by a bracket, with its
hood standing out in front of the head. Sizes: whole camera 35 x 35 x 73 mm [S12] (module 25.2 mm of that, 3DDS-0734); cradle plate 45 mm square, collar,
ring, hood and bracket sizes are read by eye from the photos and the CAD figure (ASSUMPTION). Run:  .venv/bin/python hardware/mast/head_concept.py
"""
import math
import sys
from pathlib import Path

from build123d import Box, Cylinder, Pos, Rot

HERE = Path(__file__).parent
for sub in ("body", "mast", "assembly", "suspension", "wheel", "drive", "chassis"):
    sys.path.insert(0, str(HERE.parent / sub))
import head as H            # noqa: E402
import mast as MAST         # noqa: E402
import rover as R           # noqa: E402
from headb import *         # noqa: E402,F401
import headb                # noqa: E402

def tilt_check(parts):
    """Sweep the tilting unit (disk, enclosure, hat, camera) about the tilt axis against the fixed parts: adapter plate, arm, tilt servo, extrusion."""
    from build123d import Axis, Compound
    ax = Axis((TX, 0, AZ), (0, 1, 0))
    unit = Compound([parts[n] for n in TILTING])
    fixed = {"bracket": parts["bracket"], "tilt servo": parts["tilt servo"], "extrusion": Pos(TX, 0, (446.0 + MAST.TUBE_Z1) / 2) * Box(40, 40, MAST.TUBE_Z1 - 446.0)}
    print("tilt sweep, the whole camera head about the tilt axis, overlap with fixed parts (mm3 > 1 counts as contact):")
    for sgn, nm in ((1, "positive (nose down?)"), (-1, "negative")):
        first = None
        who = None
        for deg in range(0, 91, 5):
            u = unit.rotate(ax, sgn * deg)
            hit = {k: (lambda r: 0.0 if r is None else r.volume)(u & f) for k, f in fixed.items()}
            tot = sum(hit.values())
            if tot > 1.0 and first is None:
                first, who = deg, {k: round(v) for k, v in hit.items() if v > 1.0}
        print(f"  {nm}: first contact at {first if first is not None else 'none up to 90'} degrees {who or ''}")
    ub = unit.bounding_box()
    print(f"  unit z {ub.min.Z:.0f}..{ub.max.Z:.0f}; lowest corner at 75 degrees about z {AZ - math.hypot(37.7, 30.0) :.0f}; top of the extrusion z {MAST.TUBE_Z1:.0f}")
    kg = parts["antenna hat"].volume / 1e6 * 1.27
    al = parts["bracket"].volume / 1e6 * 2.68
    print(f"  bracket (2 mm aluminium) {al:.3f} kg; printed hat {kg:.3f} kg; bracket valid {parts['bracket'].is_valid}")


COL = {"bracket": (170, 176, 184), "tilt servo": (60, 100, 190), "disk": (190, 100, 90), "enclosure": (236, 236, 232), "antenna hat": (200, 204, 208), "GNSS patch": (200, 170, 70), "HDMI plug": (190, 196, 204), "cable gland": (90, 90, 96), "CSI extender Tx": (60, 140, 110), "camera-link cable": (225, 140, 50), "camera body": (40, 120, 80),
       "lens": (70, 74, 82), "baffle": (150, 154, 160), "hood": (28, 28, 32)}
NAMES = {"bracket": "sheet bracket: web and two fins (2 mm Al)", "tilt servo": "STS3215 tilt servo", "disk": "disk: horn coupler and cable spool", "enclosure": "camera box (die-cast)", "antenna hat": "aluminium hat (ground plane)", "GNSS patch": "GNSS L1 patch", "HDMI plug": "HDMI plug (slim boot) on the Tx board", "cable gland": "PG7 cable gland", "CSI extender Tx": "CSI extender Tx board", "camera-link cable": "camera-link cable (a loose loop, as the original's harness)",
         "camera body": "Pi HQ camera", "lens": "4 mm CS lens", "baffle": "slotted baffle ring", "hood": "black hood, square window"}


def disk_section():
    """Section at the mast axis (the front half removed), looking from the front: bracket web with its horn hole and servo screw holes, the servo, the disk (horn boss, cavity,
    rim slot), the camera box wall with the cable and screw holes. docs/images/disk-section.png"""
    from build123d import Box, Pos
    parts = head()
    keep = Pos(TX, 0, AZ - 100.0) * Box(400.0, 400.0, 200.0)          # z <= the tilt axis height (plan section)
    ms = []
    for g in ("bracket", "tilt servo", "disk", "enclosure", "camera body", "lens", "baffle", "hood"):
        sh = parts[g] & keep
        v, t = R.mesh(sh, 0.25, 0.3)
        ms.append((g, v, t, COL[g]))
    size = (1100, 760)
    im = R.render(ms, -90, 89, size, label="Plan section at the tilt axis (z 667), from above, +y at the top and the front (+x) to the right: camera box, disk (cavity and horn boss), bracket web and servo", zoom=1.4, legend=[(NAMES[g], COL[g]) for g in ("bracket", "tilt servo", "disk", "enclosure", "camera body", "lens")], legend_left=True)
    out = HERE.parent.parent / "docs" / "images" / "disk-section.png"
    im.save(out)
    print("saved", out)


def main():
    disk_section()
    parts = head()
    ms = []
    for g, sh in parts.items():
        v, t = R.mesh(sh, 0.25, 0.3)
        ms.append((g, v, t, COL[g]))
    tilt_check(parts)
    leg = [(NAMES[g], COL[g]) for g in parts]
    size = (760, 620)
    views = [("Front left (hood towards the viewer)", 35, 14, 1.0), ("Straight on, from the front", 0, 0, 1.0),
             ("Side, from the right", -90, 0, 1.0), ("From the rear left", 215, 20, 1.0)]
    imgs = [R.render(ms, az, el, size, label=lab, zoom=z, legend=leg if i == 0 else (), legend_left=True) for i, (lab, az, el, z) in enumerate(views)]
    from PIL import Image
    sheet = Image.new("RGB", (2 * size[0] + 36, 2 * size[1] + 36), (255, 255, 255))
    for k, im in enumerate(imgs):
        r, c = divmod(k, 2)
        sheet.paste(im, (12 + c * (size[0] + 12), 12 + r * (size[1] + 12)))
    out = HERE.parent.parent / "docs" / "images" / "head-concept.png"
    sheet.save(out)
    bb = Compound_bb(parts)
    print("saved", out, sheet.size, bb)


def Compound_bb(parts):
    from build123d import Compound
    b = Compound(list(parts.values())).bounding_box()
    return f"x {b.min.X:.0f}..{b.max.X:.0f} y {b.min.Y:.0f}..{b.max.Y:.0f} z {b.min.Z:.0f}..{b.max.Z:.0f}"


if __name__ == "__main__":
    main()
