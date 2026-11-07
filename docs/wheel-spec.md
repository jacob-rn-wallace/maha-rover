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

## 2. Position on the rover

| Item | Value | Status | Source |
|---|---|---|---|
| Wheelbase (axle to axle) | 273 (270 stated, "27 cm") | derived; stated | 3e, [S6] |
| Track (wheel centre to wheel centre) | 415 | derived | 3f, [S8] |
| Width over the wheels | about 497 | derived | 3f |
| Length over the rims | about 474 | derived | 3e |
| Hub plate diameter | about 50 | derived, low confidence (small purple disc in the CAD side views) | 3e, 3f |
| Load per wheel | 2.5 kg on Earth, about 4.05 N on the Moon | derived (10 kg / 4) | [S4], [S7] |

## 3. Not known, and what is open

| Item | What is known | Status |
|---|---|---|
| **Web pattern** | Final CAD side views ([S5] Fig. 15, [S18] Fig. 1): the see-through openings are spaced at **36 degrees** (measured 36 plus or minus 1 in three wheels), so ten equal openings per turn. This agrees with the project owner's observation of the hardware: five spokes on each side of the wheel, the inner and outer sets rotated 36 degrees (360 / 10) from each other. Earlier variants: six open spokes ([S23] finite element model), five aligned spokes in the turntable video's outer layer, and closed faces (test and engineering-model wheels). [S4] says only that the flight wheel is "skeletonized". See section 2 of `original-dimensions.md`. | derived (36 degree spacing); the axial layering of the two sets is the owner's observation, not yet measured from a figure |
| Rim band thickness | none given | (unverified) |
| Rib and web thickness | none given | (unverified) |
| Grouser plate thickness and width | In [S23] the plates stand wider than the rim band; in the CAD front view the whole wheel is 80 to 81 wide | (unverified) |
| Wheel mass, flight | the closed test wheel is 1.18 kg ([S4]), not the flight wheel | (unverified) |
| Hub and axle interface | only the purple hub plate and a motor housing are visible in CAD views | (unverified) |

## 4. Suggested choices for a first CAD model

These are choices, not facts, and each should be changed if a better source appears.

1. **Web:** two sets of five spokes, the inner set rotated 36 degrees from the outer, so ten
   equally spaced spokes side-on. This matches the final CAD side views and the owner's
   observation of the hardware. The six-spoke [S23] geometry stays as an alternative variant.
2. **Thicknesses:** set rim band, ribs and grouser plates to values a replica can make (for example
   1.5 to 2 mm sheet), because the original values are not published. Label them as the replica's,
   not the original's.
3. **Envelope:** hold the rim diameter, width, 14 grousers, 15 mm grouser height and the 100 mm
   centre height exactly; they are the values that carry fidelity.
4. **Material:** the replica need not be magnesium; record the substitute in the BOM.

## 5. How this sheet was checked

The 200 mm and 80 mm figures agree across the traction paper, the regolith sampler paper, the
Khalifa thesis, the CAD side view (rim fit 201 mm) and the CAD front view (width 81 mm). The tip
diameter of about 230 mm is the CAD value; the thesis lists 215, which looks like 200 + 15 and does
not match the CAD.
