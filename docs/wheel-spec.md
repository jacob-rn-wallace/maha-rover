# Wheel specification (working draft for CAD)

This sheet collects what is known about the original Rashid-1 wheel, so the replica wheel can be
modelled from sourced numbers. It is built from
[`original-dimensions.md`](original-dimensions.md); source tags ([S4], [S8], 3e and so on) refer to
that file, which holds the full citations and the reasoning. Millimetres throughout.

Status words: **stated** (a source gives it), **derived** (measured from a figure, typically plus or
minus 2 to 3%), **(unverified)** (no source, or sources disagree).

## 1. Fixed envelope (all sources agree)

| Item | Value | Status | Source |
|---|---|---|---|
| Rim diameter | 200 (radius 100) | stated | [S4], [S7], [S8], [S23] |
| Wheel width, overall | 80 | stated; derived 81 from the CAD front view | [S4], [S8], [S23], 3f |
| Grousers | 14, radial, straight, evenly spaced | stated | [S4], [S8], [S23] |
| Grouser height above the rim | 15 | stated | [S4], [S23] |
| Diameter over grouser tips | about 230 | derived (200 + 2 x 15; CAD front and side views agree) | 3e, 3f |
| Grouser pitch | 25.71 degrees; 44.9 along the rim | derived (360 / 14; pi x 200 / 14) | [S5], [S8] |
| Sample slot between grousers | about 44 x 80 | stated | [S8] |
| Material | Magnesium alloy AZ91E | stated | [S10] |
| Wheel centre height above the rim's ground contact | 100 | derived (rim radius) | 3e |
| Ribs | 10, equally spaced at 36 degrees (two sets of 5 on two axial layers per the project owner), constant width about 14.5, flared at the rim root | derived | [S23] Fig. 88a, [S5], [S18] |
| Hub tube diameter | about 50 (50 from the thesis drawing and the CAD; about 54 read from a photograph of the hardware, which reads high through perspective) | derived (three sources) | [S23], 3e, 3f, [S24] |
| Rim band thickness | about 3 (plus or minus 1) | derived, coarse (drawn edge lines) | [S23] Fig. 88a |
| Grouser plate thickness | about 0.8 (0.5 to 1.0) | derived (flight photographs with a built-in scale, and a second method) | [S8] Fig. 3, [S23] |
| Slot width between grousers | about 43 (stated 44) | derived, stated | [S8] |
| Grouser tip radius | 116 (tip diameter 232) | derived; [S23] Table 3 lists 215, which its own drawing contradicts | [S23], 3e, 3f |
| Grouser phase | a grouser plate lies on the 0 degree rib axis; the other 13 at 25.71 degree steps | derived | [S23] Fig. 88a |

## 2. Position on the rover

| Item | Value | Status | Source |
|---|---|---|---|
| Wheelbase (axle to axle) | 273 (270 stated, "27 cm") | derived; stated | 3e, [S6] |
| Track (wheel centre to wheel centre) | 415 | derived | 3f, [S8] |
| Width over the wheels | about 497 | derived | 3f |
| Length over the rims | about 474 | derived | 3e |
| Load per wheel | 2.5 kg on Earth, about 4.05 N on the Moon | derived (10 kg / 4) | [S4], [S7] |

## 3. Not known, and what is open

| Item | What is known | Status |
|---|---|---|
| Axial layering of the two rib sets | The owner reports five ribs on each side with the inner set rotated 36 degrees; the side views cannot show depth. The turntable video's earlier wheel has its two sets roughly in phase | stated by the owner, not yet measured from a figure |
| Rib thickness | about 3 (2 to 4), very low confidence (one edge strip in one oblique thesis figure); not visible side-on, where only the 14.5 mm width shows | (unverified), rough estimate only |
| Grouser plate width | In [S23] the plates stand wider than the rim band; in the CAD front view the whole wheel is 80 to 81 wide | (unverified) |
| Wheel mass, flight | the closed test wheel is 1.18 kg ([S4]), not the flight wheel. The photographed wheels are machined, so a machined-magnesium mass estimate would be possible, but none is published | (unverified) |
| Hub tube length, bore and axle interface | outer diameter about 50 is known. A hardware photograph shows a cup-shaped hub with a floor and four small screw holes, a flange with six bolt holes, and, nearby, black cylindrical housings with six-hole bolt circles and silver flanged adapters that may be the matching drive parts (not confirmed). Length, bore and exact bolt-circle sizes are not known | (unverified) |

## 4. Suggested choices for a first CAD model

These are choices, not facts, and each should be changed if a better source appears.

1. **Web:** two sets of five constant-width ribs (14.5 mm wide), the inner set rotated 36 degrees
   from the outer, flared at the rim root, on a 50 mm hub tube. This is the wheel in [S23] Fig. 88a and the
   final CAD views.
2. **Thicknesses:** rim band about 3 mm and grouser plates about 0.8 mm (thin sheet) are derived from
   figures; the ribs are about 3 mm at best. A replica may need thicker plates than 0.8 mm for its own
   material, so treat the original values as a target and record any change in the BOM.
3. **Envelope:** hold the rim diameter, width, 14 grousers, 15 mm grouser height and the 100 mm
   centre height exactly; they are the values that carry fidelity.
4. **Material:** the replica need not be magnesium; record the substitute in the BOM.

## 5. How this sheet was checked

The 200 mm and 80 mm figures agree across the traction paper, the regolith sampler paper, the
Khalifa thesis, the CAD side view (rim fit 201 mm) and the CAD front view (width 81 mm). The tip
diameter of about 230 mm is the CAD value, and the thesis's own side-on drawing gives 232; its Table 3
lists 215, which looks like 200 + 15 and contradicts both. The 50 mm hub tube comes out the same from
the thesis drawing and from the CAD side views. The ten-rib, 36 degree pattern comes out the same from
the thesis drawing and from the CAD side views.
