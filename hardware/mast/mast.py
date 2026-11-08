"""al-maha mast: replica mast, head and camera, fixed upright.

Replica design guided by the original's CAD figures (original-dimensions.md 3j) and
[S12] (CAM-1 35 x 35 x 73 mm on a pan-tilt gimbal). Dimensions tagged derived are from
the figures; everything else is ASSUMPTION.

The mast is FIXED for now: the original stows flat under 120 mm [S19] and springs up on
landing, but the replica's stowing and deploying are deferred (decision 2026-11-07). A
T-slot extrusion (40 x 40, decided 2026-11-07) stands on a base plate bolted to the deck and carries the printed
bent sheet bracket and head (headb.py) on its end. Pan is a servo in the base and tilt a servo in the bracket
(Feetech STS3215, docs/electronics-spec.md). The earlier hinged design, with a hinge pin,
pedestal and fold sweep, is in commit 20aec90.

Frame as in body.py.

Run:  .venv/bin/python hardware/mast/mast.py
Out:  hardware/mast/out/mast.step
"""
import math
import sys
from pathlib import Path

from build123d import Axis, Box, Compound, Cylinder, Pos, Rot, export_step

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "body"))
sys.path.insert(0, str(HERE))
import body as B  # noqa: E402
import head as H  # noqa: E402
import headb as HB  # noqa: E402
import base as BASE  # noqa: E402

# ---- Positions (3j) ---------------------------------------------------------
TUBE_X = B.MAST_X                  # tube centre; 24.2 ahead of the front axle   derived [3j]
TUBE_W = 58.0                      # width of the printed neck, X and Y (the original's tube measures about 60 x 59)  derived [3j]
EXT = 40.0                         # mast extrusion section, 40 x 40 (narrower than the original's 58 mm tube)  ASSUMPTION
EXT_KG_PER_M = 1.86                # Misumi HFS8-4040 catalogue (sources list 1.73 to 1.90 by variant; get it from the vendor)  stated (catalogue)
PLATE_XY, PLATE_T = 76.0, 6.0      # aluminium base plate on the deck, 4 M4 bolts at x +-19 / y +-30 from the tube centre  ASSUMPTION
TOP_Z = B.TOP_Z                    # top of the head                              stated [S1]

# ---- Rotating parts, measured along the mast from the hinge ----------------
BASE_Z0, BASE_Z1 = B.DECK_TOP_Z, B.DECK_TOP_Z + PLATE_T   # base plate on the deck
_BASE_PARTS, _BASE_INFO = BASE.build(TUBE_X, BASE_Z1)      # pan drive housing, servo, spindle and bearings (base.py)
TUBE_Z0, TUBE_Z1 = _BASE_INFO["z_flange_top"], 577.0  # extrusion from the spindle flange to the neck; top at 577 as the original's tube   derived [3j]
CAM_Y = HB.CY                      # the sourced 28 right of the centreline [S8], moved to 23.5 in the owner's redesign (2026-11-08)
CAM_AXIS_Z = 660.0                 # CAM-1 optical axis height                    stated [S12]
CAM_FRONT_X = B.WHEELBASE / 2 + 77.9   # [S8] 77.9 ahead of the front axle: matches the lens front in [3j]
assert (HB.TX, HB.CY, HB.AZ, HB.FX, HB.Z_EXT) == (TUBE_X, CAM_Y, CAM_AXIS_Z, CAM_FRONT_X, TUBE_Z1)

# ---- Replica masses, kg (ASSUMPTION unless from a catalogue) -----------------------------
# bracket: volume x 2.68 g/cm3 (aluminium sheet); printed parts: volume x PETG; the sideways disk is printed with a hollow core (mass ASSUMPTION);
# servos 55 g each (retailers); the camera body stands in for a Camera Module 3 (4 g) and its printed mount (ASSUMPTION 10 g); hardware 0.02
AL_G_CM3 = 2.68
DISK_KG = 0.015
CAMBODY_KG = 0.010
MASSES = {"pan and tilt servos": 2 * H.SERVO_MASS, "hardware": 0.02}
ENCLOSURE_KG = 0.090              # Takachi TD6-6-4, catalogue (90 g)   stated
PRINTED_HEAD = ("antenna hat", "cradle", "collar", "baffle", "hood")


def parts():
    base = Pos(TUBE_X, 0, (BASE_Z0 + BASE_Z1) / 2) * Box(PLATE_XY, PLATE_XY, PLATE_T)
    tube = Pos(TUBE_X, 0, (TUBE_Z0 + TUBE_Z1) / 2) * Box(EXT, EXT, TUBE_Z1 - TUBE_Z0)   # slots ignored, as in frame.py
    hp = HB.head()
    return {"base": base, "tube": tube, **hp, **_BASE_PARTS}


def cg_and_moment():
    rot = parts()
    pts = []   # (mass, x, z)
    c = lambda n: rot[n].center()
    pts.append((PLATE_XY * PLATE_XY * PLATE_T / 1e3 * 2.70 / 1000.0, c("base").X, c("base").Z))                 # aluminium plate
    pts.append(((TUBE_Z1 - TUBE_Z0) / 1000.0 * EXT_KG_PER_M, c("tube").X, c("tube").Z))                          # extrusion
    pts.append((rot["bracket"].volume / 1e6 * AL_G_CM3, c("bracket").X, c("bracket").Z))
    for n in PRINTED_HEAD:
        pts.append((H.shell_mass(rot[n]), c(n).X, c(n).Z))
    pts.append((ENCLOSURE_KG, c("enclosure").X, c("enclosure").Z))
    pts.append((DISK_KG, c("disk").X, c("disk").Z))
    pts.append((CAMBODY_KG, c("camera body").X, c("camera body").Z))
    for n in ("pan servo", "tilt servo"):
        pts.append((H.SERVO_MASS, c(n).X, c(n).Z))
    pts.append((MASSES["hardware"] + _BASE_INFO["hardware_kg"], TUBE_X, B.DECK_TOP_Z + 30.0))
    pts.append((_BASE_INFO["housing_kg"], c("pan housing").X, c("pan housing").Z))
    pts.append((_BASE_INFO["al_kg"], c("spindle").X, c("spindle").Z))
    pts.append((_BASE_INFO["bearing_kg"], c("pan bearings").X, c("pan bearings").Z))
    m = sum(p[0] for p in pts)
    zc = sum(p[0] * p[2] for p in pts) / m
    xc = sum(p[0] * p[1] for p in pts) / m
    h = zc - B.DECK_TOP_Z                  # height of the centre of mass above the deck
    return m, xc, zc, h, m * 9.81 * h / 1000.0   # N.m about the base (h in mm), Earth gravity, sideways acceleration of 1 g


def _vol(a, b):
    r = a & b
    return 0.0 if r is None else r.volume


def head_checks(p):
    """Head checks: tilt servo between the bracket flanges, pan sweep of the whole turning mast, tilt sweep of the camera unit."""
    ax_p = Axis((TUBE_X, 0, 0), (0, 0, 1))
    ax_t = Axis((TUBE_X, 0, CAM_AXIS_Z), (0, 1, 0))
    br = p["bracket"].bounding_box()
    tv = p["tilt servo"].bounding_box()
    print("\nhead: tilt servo between the bracket flanges (inner width 40) and under its top, clear of the sheet (mm3, want 0)")
    print(f"  tilt servo vs bracket: {_vol(p['tilt servo'], p['bracket']):.1f}; servo x {tv.min.X:.1f}..{tv.max.X:.1f} y {tv.min.Y:.1f}..{tv.max.Y:.1f} z {tv.min.Z:.1f}..{tv.max.Z:.1f}; "
          f"bracket x {br.min.X:.1f}..{br.max.X:.1f} y {br.min.Y:.1f}..{br.max.Y:.1f} z {br.min.Z:.1f}..{br.max.Z:.1f}")
    print(f"  bracket vs extrusion: {_vol(p['bracket'], p['tube']):.1f}; disk vs bracket {_vol(p['disk'], p['bracket']):.1f}; enclosure vs bracket {_vol(p['enclosure'], p['bracket']):.1f}")
    print("  camera stack vs die-cast enclosure (mm3, want 0): " + ", ".join(f"{n} {_vol(p[n], p['enclosure']):.1f}" for n in ("camera body", "cradle", "collar", "baffle", "hood")))
    eb = p["enclosure"].bounding_box()
    print(f"  enclosure x {eb.min.X:.1f}..{eb.max.X:.1f} y {eb.min.Y:.1f}..{eb.max.Y:.1f} z {eb.min.Z:.1f}..{eb.max.Z:.1f}; the disk (40 mm, x {TUBE_X - 20:.0f}..{TUBE_X + 20:.0f}) reaches {TUBE_X + 20 - eb.max.X:.1f} mm past the box front")
    turning = ("bracket", "tube", "spindle", "tilt servo") + HB.TILTING
    static = [p["base"], p["pan housing"], p["pan servo"], p["pan bearings"], p["pan coupling disc"]]
    moving = Compound([p[n] for n in turning])
    worst = 0.0
    for deg in range(-180, 181, 30):
        m_ = moving.rotate(ax_p, deg)
        worst = max(worst, sum(_vol(m_, s_) for s_ in static))
    print(f"\npan sweep, -180 to +180 degrees in 30 degree steps: overlap of the whole turning mast with the base plate, pan housing, servo and bearings: worst {worst:.1f} mm3")
    unit = Compound([p[n] for n in HB.TILTING])
    fixed = [p["bracket"], p["tilt servo"], p["tube"]]
    print("tilt sweep, the camera unit (disk, enclosure, hat, camera) about the tilt axis (x %.1f, z %.0f), overlap with the bracket, tilt servo and extrusion:" % (TUBE_X, CAM_AXIS_Z))
    for sgn, nm in ((1, "positive"), (-1, "negative")):
        first = None
        for deg in range(0, 91, 5):
            u_ = unit.rotate(ax_t, sgn * deg)
            if sum(_vol(u_, f_) for f_ in fixed) > 1.0 and first is None:
                first = deg
        print(f"  {nm} tilt: first contact at {first if first is not None else 'none up to 90'} degrees (the original tilts plus or minus 75 degrees [S19])")


if __name__ == "__main__":
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    body_parts, _ = B.build_rover()
    deck = body_parts["body"]
    cells = Compound([v for k, v in body_parts.items() if k.startswith("cell")])
    hull = Compound([deck, cells])

    p = parts()
    allp = Compound(list(p.values()))
    bb = allp.bounding_box()
    print(f"mast x {bb.min.X:.0f}..{bb.max.X:.0f}, y {bb.min.Y:.0f}..{bb.max.Y:.0f}, z {bb.min.Z:.0f}..{bb.max.Z:.0f}")
    print(f"top z {bb.max.Z:.0f} (stated 700); camera axis z {CAM_AXIS_Z:.0f}; lens front x {CAM_FRONT_X:.1f} "
          f"({B.WHEELBASE / 2:.1f} + 77.9); body front end x {B.BODY_X0 + B.SIDE_PLATE_LEN / 2:.0f}")
    print(f"base plate x {TUBE_X - PLATE_XY / 2:.0f}..{TUBE_X + PLATE_XY / 2:.0f}, y +-{PLATE_XY / 2:.0f}; extrusion {EXT:.0f} x {EXT:.0f}, z {TUBE_Z0:.0f}..{TUBE_Z1:.0f}; deck half-width {B.TOP_WIDTH / 2:.0f}, "
          f"deck x +-{B.DECK_LEN / 2:.0f}")
    print(f"overlap with body+cells (mm3, want 0): {(allp & hull).volume:.1f}")
    # the base plate must sit on the deck
    deck_top = Pos(B.BODY_X0, 0, B.DECK_TOP_Z + 0.5) * Box(B.DECK_LEN, B.TOP_WIDTH, 1.0)   # 1 mm slab just above the deck
    print(f"base plate footprint on the deck plate (mm2): {(p['base'] & deck_top).volume / 1.0:.0f} of {PLATE_XY * PLATE_XY:.0f}")

    m, xc, zc, h, tq = cg_and_moment()
    print(f"\nreplica mast (ASSUMPTION masses): {m:.2f} kg, centre of mass {h:.0f} mm above the deck")
    print(f"moment at the base for a sideways acceleration of 1 g: {tq:.2f} N.m "
          f"(rover tilted 45 degrees: the same; a 20 degree slope gives {tq * math.sin(math.radians(20)):.2f} N.m)")

    print(f"extrusion {(TUBE_Z1 - TUBE_Z0):.0f} mm x {EXT_KG_PER_M} kg/m = {(TUBE_Z1 - TUBE_Z0) / 1000 * EXT_KG_PER_M:.2f} kg; its slots carry the camera and servo cables")
    print()
    BASE.checks(p, _BASE_INFO, TUBE_X, moment_1g_nm=tq, mast_kg=m)
    head_checks(p)

    export_step(Compound(list(p.values()), label="mast"), str(out / "mast.step"))
