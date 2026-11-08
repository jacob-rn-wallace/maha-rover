"""al-maha replica mass and centre of mass, from the CAD parts.

Adds up the replica as designed so far (frame, panels, link plates and sleeves, shafts, wheels, motors, mast,
electronics, solar pieces) with densities and a few allowances. Where a part is not designed (the differential's gears,
harness, fasteners) the value is an allowance, marked ASSUMPTION. Frame as in body.py.

Run:  .venv/bin/python hardware/mass/replica.py
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
for d in ("body", "chassis", "suspension", "mast", "wheel", "drive"):
    sys.path.insert(0, str(HERE.parent / d))
import body as B        # noqa: E402
import interior as I    # noqa: E402
import frame as F       # noqa: E402
import arms as A        # noqa: E402
import mast as MAST     # noqa: E402
import antenna as ANT   # noqa: E402
import wheel as W       # noqa: E402

AL, STEEL, PETG = 2.70, 7.85, 1.27   # g/cm3: aluminium and steel standard; PETG typical (printed, solid)   ASSUMPTION for PETG
ASA = 1.07                           # g/cm3, typical ASA/ABS filament (not verified)   ASSUMPTION
WHEEL_DENSITY = ASA                  # replica wheels printed in ASA (chosen 2026-11-08 in the mass second pass; PETG 1.27 was the heavy case)
MOTOR = 0.195                        # kg each, vendor upper bound
DIFFERENTIAL = 0.30                  # kg: housing, four steel gears, cross pin, bushings, hardware (differential.py: 0.17 kg of gears and housing)   ASSUMPTION
HARNESS_FASTENERS = 0.40             # kg: wiring, T-nuts, brackets, bolts                                     ASSUMPTION
SOLAR = 60 * 0.0015                  # kg: 60 pieces with adhesive and laminate, 1.5 g each                    ASSUMPTION
TERMINALS = 0.05                     # kg: boards, diodes, fuses                                               ASSUMPTION
RF_CABLES = 0.006                    # kg: two micro-coax runs with u.FL ends, the RP-SMA pigtail, a short USB lead, two short camera ribbons, the Zero 2 W u.FL modification   ASSUMPTION
RJ45_CABLE = 0.030                   # kg: the extension kit's 1 m RJ45 patch cable (about 30 g/m for a Cat5e patch cord; ASSUMPTION, not weighed)
TARGET = 10.0


def kg(volume_mm3, density):
    return volume_mm3 / 1e3 * density / 1000.0


def collect():
    items = []   # (group, name, kg, (x, y, z))
    add = lambda g, n, m, p: items.append((g, n, m, p))
    c = lambda s: (s.center().X, s.center().Y, s.center().Z)

    cav = I.cavity()
    members = F.build()
    for n, s in members.items():
        add("T-slot frame", n, F.member_kg(n, s), c(s))
    sh = I.shell(cav)
    add("panels", "floor, ends, deck", kg(sh.volume, AL), c(sh))
    for i, sp in enumerate(I.side_panels(cav)):
        add("panels", f"side panel {i}", kg(sp.volume, AL), c(sp))
    for i, b in enumerate(F.bushings()):
        add("bushings", f"bushings {i}", 0.01, c(b))      # two flanged bronze or plastic bushings, about 5 g each (ASSUMPTION)
    for n, s in F.standoffs().items():
        add("pivot standoffs", n, F.PIV_KG, c(s))

    for sy in (1, -1):
        arm, wheels, motors = A.side(sy)
        tag = "L" if sy > 0 else "R"
        for n, s in arm.items():
            add("link plates, sleeves, shafts", f"{n} {tag}", kg(s.volume, STEEL if n == "shaft" else AL), c(s))
        for n, s in wheels.items():
            add("wheels", f"{n} {tag}", kg(W.build_wheel().volume, WHEEL_DENSITY), c(s))
        for sx in (1, -1):
            hub = (sx * B.WHEELBASE / 2, sy * B.TRACK / 2, B.HUB_Z)
            add("drive motors", f"motor {'F' if sx > 0 else 'R'}{tag}", MOTOR, hub)
    add("differential", "housing, gears, pin", DIFFERENTIAL, (0.0, 0.0, A.PIVOT_Z))

    m, xc, zc, h, _ = MAST.cg_and_moment()
    add("mast, head and camera", "mast", m, (xc, 0.0, zc))

    placed = I.placed_parts()
    for n, d in I.PARTS.items():
        s = placed[n]
        add("electronics", n, I.part_mass(n), c(s))
    cells = B.cells()
    cx = sum(c(s)[0] for s in cells) / len(cells)
    cy = sum(abs(c(s)[1]) for s in cells) / len(cells)
    for sy in (1, -1):
        add("solar pieces", "pieces " + ("L" if sy > 0 else "R"), SOLAR / 2, (cx, sy * cy, B.FIELD_Z))
    add("terminals, diodes, fuses", "boards etc.", TERMINALS, (0.0, 0.0, 255.0))
    add("harness and fasteners", "allowance", HARNESS_FASTENERS, (0.0, 0.0, 190.0))
    from build123d import Compound
    a = Compound(list(ANT.build().values())).center()
    add("antennas and radios", "2.4 GHz dipole and block", ANT.MASS, (a.X, a.Y, a.Z))
    add("antennas and radios", "RF cables, USB lead, short ribbons", RF_CABLES, (100.0, 0.0, 300.0))
    add("antennas and radios", "RJ45 camera-link cable (1 m)", RJ45_CABLE, (140.0, 0.0, 480.0))     # the GNSS board and servo adapter are electronics parts (interior.py); the GNSS patch is in the mast group
    return items


def tip_angles(com):
    x, y, z = com
    hb, ht = B.WHEELBASE / 2, B.TRACK / 2 + 40.0
    return {
        "nose-down": math.degrees(math.atan((hb + x) / z)),
        "nose-up": math.degrees(math.atan((hb - x) / z)),
        "sideways": math.degrees(math.atan((ht - abs(y)) / z)),
    }


if __name__ == "__main__":
    items = collect()
    groups = {}
    for g, n, m, p in items:
        groups.setdefault(g, [0.0, [0.0, 0.0, 0.0]])
        groups[g][0] += m
        for k in range(3):
            groups[g][1][k] += m * p[k]
    total = sum(v[0] for v in groups.values())
    com = tuple(sum(v[1][k] for v in groups.values()) / total for k in range(3))
    print(f"{'group':34s}{'kg':>7s}{'share':>8s}{'x':>7s}{'z':>7s}")
    for g, (m, mom) in sorted(groups.items(), key=lambda kv: -kv[1][0]):
        print(f"{g:34s}{m:7.2f}{m / total * 100:7.0f}%{mom[0] / m:7.0f}{mom[2] / m:7.0f}")
    print(f"{'TOTAL':34s}{total:7.2f}   target {TARGET:.0f} kg: margin {TARGET - total:+.2f} kg")
    print(f"\ncentre of mass: x {com[0]:.1f}, y {com[1]:.1f}, z {com[2]:.1f} (mm, ground at the rim line)")
    t = tip_angles(com)
    print("static tip angles: " + ", ".join(f"{k} {v:.0f} deg" for k, v in t.items()) + "  (the slope requirement is 20 deg)")
    print(f"  assumptions: wheels {WHEEL_DENSITY} g/cm3 solid ({W.build_wheel().volume / 1e3 * WHEEL_DENSITY / 1000:.2f} kg each), allowances {DIFFERENTIAL + HARNESS_FASTENERS + SOLAR + TERMINALS:.2f} kg")

    # levers: what saves mass (applied 2026-11-08: link plates 4 mm, wheels in ASA, mast base plate 3 mm; the tube column was declined to keep the T-slot expandable)
    g = {k: v[0] for k, v in groups.items()}
    print("\nremaining levers for a further pass (arithmetic on the numbers above; docs/replica-mass.md):")
    shell = sum(m for gg, n, m, p in items if gg == "panels")
    print(f"  panels 2 mm -> 1.5 mm (walls only, deck as is): about {shell * 0.2:.2f} kg (panel stiffness not checked)")
    mid = sum(m for gg, n, m, p in items if gg == "T-slot frame" and n.startswith(("mid side", "differential cross")))
    print(f"  drop the two mid rails and the differential cross rails (not possible if they hold the differential): up to {mid:.2f} kg")
    wheel = g["wheels"]
    print(f"  wheels in nylon (1.01 g/cm3) instead of ASA: {wheel * (1 - 1.01 / 1.07):.2f} kg")
    plates_kg = sum(m for gg, n, m, p in items if gg.startswith("link plates") and n.startswith("plate"))
    print(f"  link plates 4 mm -> 3 mm: {plates_kg * 0.25:.2f} kg (out-of-plane deflection roughly 2.4 times: not recommended)")
    ext = (MAST.TUBE_Z1 - MAST.TUBE_Z0) / 1000.0
    print(f"  mast column to a 60 x 60 x 2 aluminium tube: {ext * (1.86 - 1.25):.2f} kg (declined: the T-slot extrusion is kept for expandability)")
