# What is modelled (2026-11-08)

`hardware/assembly/rover.py` collects every modelled part into one assembly (186 parts, a STEP file it writes to `hardware/assembly/out/`, not tracked) and renders
`docs/images/rover-assembly.png`: exterior from front-left and rear-right, a side view, a view with panels and cells hidden to show the frame and interior, a top view and a front
view, two views of the electronics bay, two sectioned close-ups of the mast head (a front-half section at the mast axis and a plan section at the camera axis height) and two of the
pivot of the left side (a cut at the shaft axis seen from above, and a cut at x = 0 seen from the rear left). Overall extent over the grouser tips: 503 x 495 x 714 mm (the height with the
mast up is 700 plus the hat). Shapes are simplified; nothing has been built. The replica mass from the CAD is **9.58 kg** (goal 10, ceiling 10.5; `replica-mass.md`), centre of mass z 234 mm,
static tip angles 34 / 26 / 47 degrees (nose-down / nose-up / sideways).

## Modelled, with simplified geometry

| System | What is in the CAD | Where |
|---|---|---|
| Body shell | floor, two end panels recessed full height to the wheel axle line (x +-136.5), and the deck (401 long, overhanging the end panels) as aluminium panels (2 mm, 3 mm deck); three 3 mm gussets per end under the deck's overhang (by eye); two separate 10 degree side panels (2 mm, 380 long, with the 12 solar wire holes now at x +-107 and the shaft clearance holes) | `body.py`, `interior.py` |
| T-slot frame | 16 plain members, all vertical or horizontal, in a stepped (wide bottom, narrow top) frame; every rail and post ends at x +-134.3, inside the recessed end panels; no rail under the mast (it bolts to the deck alone); the two bottom side rails 20 x 40, each a single member with the pivot shaft through a drilled hole; 8 pivot standoffs at x +-125 holding the side panels off the frame; 4 bushings | `frame.py` |
| Solar | 60 plain plates, 31 x 41.6 mm, two per slot on the original's 5 x 3 grid | `body.py`, `solar.py` |
| Wheels | 4: hub tube, 10 ribs in two layers, rim band, 14 grousers | `wheel.py` |
| Drive | 4 motor envelopes (gearbox, can, boss, shaft), 8 bearings, clamp rings, hub extensions, drive flanges, collars | `motor.py` |
| Suspension | the owner's link design from `link/link_plate.step` (plate with R35 lobes at the hubs and the pivot, pivot boss, two hub sleeves, the hollow 12 / 8 pivot shaft with its bonded 8 / 5 stub and wire hole), imported by `arms.py` | `arms.py`, `link/` |
| Differential | the 48 x 50 x 36 mm housing with its two shaft bosses, bushings and four mounting lugs, 4 gears as tooth-tip envelopes, cross pin | `differential.py` |
| Mast | 75 x 80 x 3 mm base plate bolted to the deck, a pan base (Takachi AL080807 die-cast box with the lid on top, STS3215 pan servo, two 6806-size bearings, aluminium spindle), 40 x 40 T-slot extrusion on the spindle flange, and a head: 2 mm aluminium sheet bracket (web and two flanges), STS3215 tilt servo, aluminium disk, die-cast camera box (Takachi AL060605), Raspberry Pi HQ camera with a 4 mm CS lens, printed baffle ring and hood, an aluminium hat with a GNSS patch, the camera-link Tx board and HDMI plug inside the camera box with a PG7 gland, and the loose camera-link cord to the deck gland; the tilt sweep clears 90 degrees either way (`mast-spec.md`) | `mast.py`, `base.py`, `headb.py`, `cable_route.py` |
| Antenna | the 158 mm 2.4 GHz dipole on a block on the deck, 290 mm behind the mast (no three-leg stand, owner's decision) | `antenna.py` |
| Interior | dimensioned boards (`boards.py`): Pi Zero 2 W, GNSS breakout, servo bus adapter and CSI extender Rx hung from the deck's underside, two MC33926 driver carriers, 5 V and 6 V converters, fuse block, rear-panel switch with its 20.2 mm hole (on the recessed rear panel); still boxes: battery, BMS, power node, charger module | `interior.py`, `boards.py` |

Checks run in the scripts: every part fits inside the cavity (0 mm3 outside, no clashes), the pivot shafts clear the frame, the wire holes clear the frame, the frame is one connected piece, the pan sweep
(plus or minus 180 degrees) and the tilt sweep clear, the link plates sweep plus or minus 15 degrees clear of the body with 12 mm to the belly, and shaft bending, bonds and cross rails are checked in `rail_check.py`.

## Placeholder or assumed sizes

The battery (a 68 x 38 x 38 mm box in place of the real cells and holder), the BMS, the power node and the charger module are boxes. The GNSS breakout is a placeholder size
(the CSI extender boards are now the measured Arducam B0091, from its vendor STEP, with the Tx board inside the camera box; their mass, standoff fixing and ribbon route are not designed). The gussets' number and size are read by eye. The bearings, the GNSS patch (15 g), GNSS board (8 g) and dipole (15 g) masses are assumptions, and
0.84 kg of the mass is allowances for the unmodelled items below.

## Not modelled, though designed in the docs

Gear teeth (the gears are tooth-tip envelopes, so the mesh overlaps); the differential's lug bolts and shim washers, the bushing flanges, the bonding and fasteners of the sleeves; the real battery cells and holder;
every wire and the harness (only the camera cord is modelled; the servo wires, GNSS coax, 2.4 GHz cable and the motor wires are not); fasteners, T-nuts and corner brackets; the clear laminate over the solar pieces and
the tabbing on their backs; the terminal boards (checked in `solar.py`, not in the assembly).

## Not yet designed

How the gussets are fixed to the end panels and the deck; the link plate to shaft bond in practice and the pins fixing the gears to the shafts; the pivot hardware for the side panels (rod ends, hinges), the seams
between panels, and the stiffness of the side panels (65 mm overhang beyond the standoffs at each end); the mast base's gasket, the seal where the spindle leaves the lid, the compliant servo coupling and the
320 degree pan stop; the tilt hard stop and the lens focus lock; cell protection (fuses, bypass diodes); the connector for parting the deck lid from the mast wiring and a way to remove the lid; the motor current cap
(firmware) and the controller firmware; mast stowing (deferred).

## Unverified

The depth of the recessed end faces (taken from the owner's reading of the CAD models; the dense cloud had it shallower, and the perspective views hint that the lower and upper parts may differ); the gusset size;
the 2.4 GHz antenna position (y +58); whether the B0091 CSI extender works with the HQ camera and a Pi Zero 2 W in practice (the vendor lists both; untested) and which slim HDMI cord carries all its pins; whether the Waveshare servo adapter works at 6 V; the deck's stiffness under the mast
(estimated in `frame-spec.md`, not analysed); the hat size (70 mm against the original's 84).

## Original features left out (decided 2026-11-08)

The original's CAM-M, CAM-2 and CAM-T camera windows on the end faces, the Langmuir probe whips and the flag plate are not modelled and will not be, not even as cosmetic dummies (owner, 2026-11-08):
al-maha is a Rashid-like rover, not a copy of Rashid, so features that exist only to carry the original's instruments stay out of the model and the simulation.

## What the pictures show that the numbers do not

The proportions look right against the original (a trapezoid body on four large grousered wheels, a tall offset mast at the front, a grid of cells on the sloped side, recessed ends under an overhanging deck),
but the wheels are an open rib-and-rim approximation, the cells are plain plates, and the head is a set of boxes. The mast looks tall because it is: 700 mm over a 348 mm deck.
