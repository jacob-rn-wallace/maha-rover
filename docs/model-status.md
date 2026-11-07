# What is modelled (2026-11-07)

`hardware/assembly/rover.py` collects every modelled part into one assembly (168 parts, a 6 MB STEP file it writes to `hardware/assembly/out/`, not tracked) and renders
`docs/images/rover-assembly.png`: exterior from front-left and rear-right, a side view, a view with panels and cells hidden to show the frame and interior, a top view and a front
view. Overall extent over the grouser tips: 503 x 495 x 712 mm (the wheel-rim plan is 473 x 495 and the height with the mast up is 700). Shapes are simplified; nothing has been built.

## Modelled, with simplified geometry

| System | What is in the CAD | Where |
|---|---|---|
| Body shell | floor, two end walls and the deck as aluminium panels (2 mm, 3 mm deck); two separate 10 degree side panels (2 mm, with the 12 solar wire holes and the shaft clearance holes) | `body.py`, `interior.py` |
| T-slot frame | 17 plain members, all vertical or horizontal, in a stepped (wide bottom, narrow top) frame (the two bottom side rails 20 x 40, each a single member with the pivot shaft through a drilled hole); 8 pivot standoffs holding the two side panels off the frame; 4 bushings | `frame.py` |
| Solar | 60 plain plates, 31 x 41.6 mm, two per slot on the original's 5 x 3 grid | `body.py`, `solar.py` |
| Wheels | 4: hub tube, 10 ribs in two layers, rim band, 14 grousers | `wheel.py` |
| Drive | 4 motor envelopes (gearbox, can, boss, shaft), 8 bearings, clamp rings, hub extensions, drive flanges, collars | `motor.py` |
| Suspension | 2 link plates with bosses and motor sleeves, 2 hollow stepped pivot shafts (12 / 8 tube, 8 / 5 stub) with their wire holes | `arms.py` |
| Differential | the 48 x 50 x 36 mm housing with its two shaft bosses and bushings, 4 gears as tooth-tip envelopes, cross pin | `differential.py` |
| Mast | 76 mm base plate, 40 x 40 T-slot extrusion, printed neck, C-arm, camera housing, tilt motor housing, CAM-1 tube | `mast.py` |
| Interior (as boxes) | battery, BMS, fuse block, bus bar, servo regulator, rear-panel switch, charger module, Pi, two motor drivers, 5 V converter | `interior.py` |

Checks run in the scripts: every part fits inside the cavity, nothing clashes, the pivot shafts clear the frame, the wire holes clear the frame, and the mass is 9.8 kg with the centre of mass at z 206 mm.

## Not modelled, though designed in the docs

Gear teeth (the gears are tooth-tip envelopes, so the mesh overlaps); the differential's cradles, bushings and fasteners; the real battery cells and holder; every wire and the harness; fasteners, T-nuts and
corner brackets; the clear laminate over the solar pieces and the tabbing on their backs; the mast's servos, camera module and cable entry; the terminal boards (checked in `solar.py`, not in the assembly).

## Not yet designed

The link-plate-to-shaft joint and the pins fixing the gears to the shafts; the mast plate's joint to the extrusion and its bolts; the pivot hardware for the side panels (rod ends, hinges), the seams between the panels, and the stiffness of the side panels; the mast cable connector; cell protection (fuses, bypass diodes); the motor current cap (firmware);
a way to remove the deck lid with its connector; the controller firmware; the second-pass mass reduction.

## What the pictures show that the numbers do not

The proportions look right against the original (a trapezoid body on four large grousered wheels, a tall offset mast at the front, a grid of cells on the sloped side), but the wheels are an open rib-and-rim
approximation, the cells are plain plates, and the head is a set of boxes. The mast looks tall because it is: 700 mm over a 348 mm deck.
