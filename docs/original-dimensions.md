# Original Rashid-1 rover: sourced dimensions

Source of truth for the replica's dimensions. Where this file and the
"provisional design" in `CLAUDE.md` disagree, this file wins.

Units are millimetres unless stated. Last reviewed: 2026-11-06.

## How to read this file

Every value carries a source tag `[S#]` (see [Sources](#sources)) and a status:

| Status | Meaning |
|---|---|
| **stated** | Printed in a source, by authors affiliated with MBRSC or the instrument teams |
| **derived** | Not printed. Computed from stated values, or read from a figure. Check before relying on it |
| **(unverified)** | Single weak source, a conflict is open, or only a press figure |

"Rashid-1" is the rover that flew on ispace's Hakuto-R Mission 1 (launched 2022-12-11). It
was lost when the lander crashed on 2023-04-25 [S5]. The engineering model (EM) survived at MBRSC.
All figures below describe the flight design unless noted.

## 1. Overall envelope

| Quantity | Value | Status | Source |
|---|---|---|---|
| Mass | 10 kg (design) | stated | [S1], [S2], [S3] |
| Height, mast deployed | 700 | stated | [S1] |
| Length | 470 | stated | [S1] |
| Width | 505 | stated | [S1] |
| Height, mast stowed | not found | (unverified) | n/a |
| Mass, alternative figure | "about 11 kg" | (unverified), conflicts with 10 kg | [S6] |

[S1] does not say what L and W are measured over. Length is probably **over the
wheels**: it equals wheelbase 270 [S6] + wheel diameter 200 [S4] = 470 exactly **(derived)**.
Width is not as clean, see the track check in section 3.

Press figures of "about 50 x 50 cm" and 70 cm height agree with [S1] to within rounding.
Use [S1].

## 2. Wheels (4)

| Quantity | Value | Status | Source |
|---|---|---|---|
| Diameter | 200 (radius 100) | stated | [S4], [S7], [S8] |
| Width | 80 | stated for the test wheel [S4]; consistent with the 8 cm grouser slot in [S8]. **A conflicting 168 is printed in [S9]** | [S4], [S8] |
| Grousers | 14, radial | stated | [S4], [S8] |
| Grouser length, flight wheel | 15 | stated | [S4] |
| Grouser length, test wheel | 20 (not the flight value) | stated | [S4] |
| Grouser pitch | about 44 to 45 | derived (pi x 200 / 14 = 44.9), matches the "4 cm" separation in [S5] and the 4.4 cm slot in [S8] | [S5], [S8] |
| Sample slot between grousers | about 44 x 80 | stated | [S8] |
| Construction | Skeletonized (spoked); flight wheel is not the closed-sided test wheel | stated | [S4] |
| Material | Magnesium alloy AZ91E (wheels and body frame) | stated | [S10] |
| Wheel mass, flight | not found | (unverified) | n/a |
| Wheel mass, closed test wheel | 1.18 kg (not the flight value) | stated | [S4] |
| Load per wheel, Earth / Moon | 24.5 N / 4.05 N | derived (10 kg x g / 4, 10 kg x 1.62 / 4) | [S4], [S7] |

Open conflict: [S9] says the flight model's wheel width is 168. The 80 figure is supported by
two other papers and by the 8 cm slot geometry [S8]. A 168 wheel would also be inconsistent
with the 505 overall width. Treat 80 as working value, but this needs confirming from a
photo or the overview paper.

## 3. Layout and chassis

| Quantity | Value | Status | Source |
|---|---|---|---|
| Wheelbase | 270 ("27 cm") | stated, rounded | [S6] |
| Wheelbase (final CAD, side view) | 273 | derived, agrees with 270 (see 3e) | [S5] Fig. 15 |
| Track (FL to FR wheel centres) | 415.4 | derived (235.7 + 179.7 from camera offsets) | [S8] |
| Width check | 415.4 + 80 = 495.4 vs stated 505. Final CAD front view: about 497 (see 3f) | derived. The CAD agrees with 495.4 and is 1.6% under 505, so the gap is within scale uncertainty | [S1], [S8], [S18] |
| Body shape | Wedge. Sloped side faces carry the solar panels. Mast at the front | derived (figures only) | [S1], [S7], [S11] |
| Body main dimensions | "about 20 x 20 x 40 cm" | stated, rounded. Now plausible: see 3a and 3b | [S6] |
| Sidewall angle | about 10 degrees from vertical (front view, 3f); 9 from the rear view (3a) and the flight photo (3e). Not stated anywhere | derived from figures, three views agree | [S18] Fig. 1, [S3] Fig. 2, [S10] Fig. 1 |
| Ground clearance | not stated. About 120 from the rear-view figure (see 3a) | derived from a figure, low confidence | [S3] Fig. 2 |
| Frame material | Magnesium alloy, covered in ITO-coated MLI | stated | [S10] |
| Obstacle / slope / speed | 100 mm obstacle, 20 degrees, 10 cm/s | stated | [S1], [S3] |

### 3a. Measurements from the rear-view CAD figure

[S3] Fig. 2 (left panel) and [S11] Fig. 1(a) show a rear view of the CAD model that looks close
to orthographic (left-right symmetric, no visible convergence). I measured pixel extents in
the [S3] figure (about 1500 px wide at 400 dpi, blurry) and scaled them with the stated
80 mm wheel width, which is 55 px. That gives 1.455 mm per pixel. Edges are good to about
2 px, so values are good to about 3 mm plus any perspective error. Treat everything here
as **derived**, not stated.

Cross-check against stated values, which were not used to set the scale:

| Quantity | Measured | Stated | Agreement |
|---|---|---|---|
| Track (wheel centre to centre) | 419 mm (288 px) | 415.4 [S8] | 1% |
| Overall width over wheels | 499 mm (343 px) | 495 to 505 [S1], [S8] | within 1% |
| Overall height, ground to mast top | 706 mm (485 px) | 700 [S1] | 1% |

The agreement supports the 80 mm wheel width. A 168 mm width would imply 3.05 mm per pixel
and a 1.5 m wide rover.

New values read from the same figure:

| Quantity | Value (mm) | Status |
|---|---|---|
| Body width at the underside | about 230 | derived |
| Body width at the top deck | about 157 | derived |
| Body height, underside to top deck | about 233 | derived |
| Ground clearance under the body | about 120 | derived |
| Side taper | about 9 degrees from vertical (25 px inset over 160 px) | derived |
| Wheel diameter over the grouser tips | about 228 | derived, see below |

**Open tension.** The measured wheel diameter over the grousers is about 228 mm, close to
200 mm rim plus 2 x 15 mm grousers = 230 mm. So the stated 200 mm may be the rim diameter.
But the 470 mm length equals the 270 mm wheelbase plus 200 mm, which fits a 200 mm overall
wheel. With 230 mm overall wheels the length would be about 500 mm. Not resolved. Section 6
and the wheel table above still show 200 mm as the stated figure.

Not measured: the side view in the same figure is a perspective view, so no lengths were
taken from it. The grid overlay and crop are kept out of the repo (third-party figure).

### 3b. Measurements from the 360 degree turntable video [S17]

[S17] is a 12 s, 2880 x 1620 render of the rover with the camera orbiting it. It is a
2021 marketing model: the camera head is a plain box and the panel cells are triangular, so
it is not the flight CAD in [S3]. Use it for proportions only. I took one near side-on frame
(t = 5.0 s), scaled it with the stated 700 mm overall height (757 px, so 0.925 mm per
pixel), and measured it at low contrast with a perspective camera. Error is about 10%.

| Quantity | Value (mm) | Status |
|---|---|---|
| Body length (front to back), top deck | about 370 | derived, low confidence |
| Wheel diameter | about 205 | derived, low confidence |
| Wheelbase (centre to centre) | about 250 | derived, low confidence |
| Length over the wheels | about 445 | derived, low confidence |

Scaling with the 228 mm wheel from 3a instead gives a body length of about 410 mm. Taking
the range, **body length is about 370 to 410 mm**.

**Reconciling [S6].** Langmuir paper [S6] says the body is "about 20 x 20 x 40 cm". I had
marked this as irreconcilable with the 415 mm track. That was wrong. The track is
wheel centre to wheel centre, and the hubs sit outboard of the body. From 3a the body is
about 230 mm wide at the underside and 157 mm at the deck (mean about 195), about 233 mm
tall, and from 3b about 370 to 410 mm long. That matches 20 x 20 x 40 cm at the rounding
[S6] uses. The wheels' inner faces are at 415.4 - 80 = 335 mm across, which leaves about
50 mm each side between the body and the wheel for the hub. The same gap is visible in the
rear view.

### 3c. Structure from motion on the video [S17]

COLMAP 4.2.1 (CPU) on 96 frames (8 per second), cropped to 1000 x 1000 around the rover,
registered all 96 images (0.39 px mean reprojection error, about 50,000 sparse points).
The camera path is a near-perfect circle (radius 3.80 model units, height scatter 0.0008).
So the video is a clean orbit of a static scene, and the sparse cloud holds the rover: four
wheel clusters, a deck outline at the top of the body, and the mast and camera head.

Scale is not recoverable from the video. Setting the mast-top height (0.94 units) to the
stated 700 mm gives about 745 mm per unit. At that scale the sparse cloud gives:

| Quantity | SfM value (mm) | Compare | Status |
|---|---|---|---|
| Deck length | about 380 | 370 to 410 from 3b | derived, about 8% |
| Deck width | about 168 | 157 from 3a | derived, about 8% |
| Deck height above ground | about 335 | 353 from 3a (120 + 233) | derived, about 8% |

These agree with 3a and 3b, so they corroborate the proportions but add no new precision.
**Do not use the wheel-level footprint from this run.** At wheel height the cloud includes
terrain points around the wheels and the extents come out about 15% too large. The cloud
is sparse on the dark rover and the wheels are only partly resolved. The point cloud and the
frames stay in the scratchpad and are not in the repo.

**Second pass.** I kept the solved camera poses and re-triangulated from tight rover
crops (900 px at 1.5x, contrast boosted, up to 16,000 features per frame). That gave about
67,000 points at 0.47 px error, but the wheels are still not resolved: the wheel-level
slice stays a mix of wheel and terrain points. The deck result did stabilise. Across
height bands and trim levels the deck comes out 0.50 to 0.52 units long and 0.20 to 0.22
wide, which at 745 mm per unit is about 380 mm long and 159 mm wide. The 159 mm width
matches the 157 mm from 3a. So the deck figures above stand, and further SfM on this
video is unlikely to pay off. (That turned out wrong for the dense stage: see 3d.)

Note that this video gives a wheel diameter near 205 mm, close to 200 mm, whereas the CAD
rear view gives 228 mm. The two disagree, and the open question in 3a stands.

The [S6] body figure of 20 x 20 x 40 cm is probably a rough description of something other than the
main structure. It cannot be the full body width, since the wheels' centres are 415 apart.
Do not use it until it is explained.

### 3d. Dense stereo on the video [S17]

The same 96 frames and the solved camera poses went through COLMAP dense stereo (patch
match with geometric consistency, then fusion) on a Colab T4. The result is 1.28 million
coloured points, and unlike the sparse cloud it resolves the whole rover: body ribs, the
mast, the camera head and all four grousered wheels. I fitted the terrain around the rover
as a plane (0.007 units scatter, 9 degree tilt), levelled the cloud, found the rover's yaw by
minimum bounding box, and took the scale from the stated 700 mm mast-top height, as in 3c
(745 mm per unit). All values are derived. The video is a render, so these are
measurements of a CAD model, not of hardware. The point cloud stays out of the repo.

| Quantity | Dense value (mm) | Compare | Status |
|---|---|---|---|
| Wheel diameter | 195 to 200 (four circle fits, 2 to 3 mm scatter) | 200 stated; 205 from 3b; 228 from 3a | derived, **agrees with the stated 200** |
| Wheel width | about 80 (tread band, left side; right side 60 to 70, noisier) | 80 stated; 168 from the other figure | derived, **favours 80** |
| Wheelbase | 247 to 251 | 250 from 3b; 270 stated "27 cm" | derived, **about 20 mm under the stated value** |
| Length over wheels | about 450 (rim to rim) | 470 stated | derived, about 4% under |
| Width over wheels | about 520 to 527 | 505 stated | derived, about 3 to 4% over |
| Deck length (upper body) | about 397 | 380 from 3c; 370 to 410 from 3b | derived |
| Deck width (top face) | about 170 | 159 from 3c; 157 from 3a | derived |
| Deck top height above ground | about 345 | 335 from 3c; 353 from 3a | derived |
| Body half-width at 250 mm height | about 115 | n/a | derived |
| Sidewall angle (250 to 345 mm height) | about 19 degrees from vertical | **9 degrees from 3a** | derived, conflict |

Notes on confidence.
- **Scale.** Ground under the wheels sits about 15 to 20 mm above my fitted plane, so the
  mast-top height above wheel contact is about 685 mm at 745 mm per unit. Setting that to 700
  mm would raise every value by about 2%. Treat all values here as plus or minus 3%.
- **Wheels agree with the stated 200 mm and 80 mm.** This is the first measurement that
  does, and it is independent of the rear-view figure, which still gives 228 mm. I now
  think the 228 figure was measured over grouser tips or had a scaling error. The open
  question in 3a is narrowed, not closed.
- **Width over wheels is 3 to 4% over the stated 505, while the wheelbase is 7% under the
  stated 270.** (Resolved in 3e: the video is a different revision from the final model.) Both disagree in different directions, so a scale error does not explain
  them. Either the video's model is a different revision from the one the figures describe,
  or what 470 and 505 are measured over differs from my edges (open item 6 in section 7).
  The first is supported by a visual difference the project owner noticed: the video's solar
  layout has one column of cells at the end set sideways, whereas other images of the rover
  show every cell horizontal. That suggests an earlier or later design iteration, so treat
  the video as a possibly different revision for all of 3b, 3c and 3d. Checked in the video
  frames: the long panel face is a 4 x 4 grid of landscape cells plus one extra tall, narrow
  column at the end, visible in frame f001 and in other turntable views. It is not yet
  compared against other renders: the press render (Gulf News) is too low-resolution to show
  whether that column exists there.
- **Sidewall angle conflicts with 3a.** The dense slices give a half-width of about 115 mm at
  250 mm height narrowing to about 85 mm at 345 mm, which is about 19 degrees from
  vertical. The rear-view figure gave 9. The lower flank is hidden behind the wheels, so I
  could only measure the upper part. Do not use either value for design yet.

### 3e. Final-configuration CAD figures [S5], [S12]

The same CAD model appears in four papers: [S8] Fig. 1, [S7] Fig. 1, [S12] Fig. 1 (front-left
and rear-right views) and [S5] Fig. 1. [S5] Fig. 15 is the useful one: a true side-on
orthographic view with the ground line drawn. I measured it at its native 818 x 706 px
resolution. Scale is the stated 700 mm height, taken from the ground line to the top of the
CAM-1 head (644 px, so 1.087 mm per px). All values are derived.

| Quantity | Value (mm) | Compare | Status |
|---|---|---|---|
| Wheel diameter (rim) | 201 (radius 92.6 px from hub; 93 px from hub to ground) | 200 stated | derived, **matches** |
| Wheel diameter over grouser tips | about 230 | 228 from 3a | derived, **explains 3a** |
| Wheelbase (hub to hub) | 273 | 270 stated "27 cm" | derived, **matches** |
| Length over wheels (rim to rim) | 474 | 470 stated | derived, **matches** |
| Hub height above ground | 101 | n/a | derived |
| Body length (side plates) | about 380 | 380 from 3c; 397 from 3d | derived |
| Deck top height above ground | 343 | 345 from 3d; 353 from 3a | derived |
| Mast centre ahead of front axle | about 35 | n/a | derived, low confidence |
| Solar face grid | 5 columns x 3 rows, all landscape cells | video: 4 x 4 plus a sideways column | derived |
| Solar face, projected in the side view | about 357 x 120 (cell pitch about 71 x 40) | n/a | derived, low confidence |

Three values (wheel diameter, wheelbase, length over wheels) match the stated figures with
the scale set from height alone, so the scale is good to about 1 to 2% and this model is the
one the stated figures describe. The 228 mm wheel diameter from 3a is the diameter over
grouser tips, not a conflict: the rim is 200 and the tips reach about 230. The panel
cell pitch is projected onto the side view, so the cell height is a minimum (the face is
sloped). The panel count is also much larger than the provisional design's 4 per side of
170 x 112 mm cells.

**The video [S17] is a different revision.** Against this model the video has a 250 mm
wheelbase (not 273), a 4 x 4 panel grid plus one sideways column (not 5 x 3), no vertical
probe mast or antenna on the deck, and a flat grousered band with five spokes on each wheel.
The wheel interior also differs between [S5] Fig. 15 (about twelve petal-shaped webs) and
[S12] Fig. 1 (open spokes), but the rim diameter and grouser tips agree. **Use 3e, not 3b to
3d, for the final configuration.** The video values stay recorded as an earlier or promotional
variant. Width over wheels and sidewall angle are not measurable from a side view; section 3f
measures both from an orthographic front view (about 497 mm and about 10 degrees).
[S12] Fig. 1 is not a safe source for them: the hubs in its front-left view differ
in apparent size by about 14% (near 34.6 px, far 30.4 px major axis), so it is a perspective
view. The rear-right view could not be tested (its two hubs are at nearly equal depth).
A trial of fitting wheel-rim ellipses to both views gave a wheelbase constrained only to
about plus or minus 12% and a track to about plus or minus 8%, so that method was dropped.

**Flight-model photo [S10] Fig. 1 (right).** A real photograph of the flight model from the
rear with the mast stowed (camera head folded over the top of the body). The body outline is
a trapezoid, as in the CAD rear view. Reading the left and right silhouette edges by eye
between the top plate and the lower edge of the MLI gives about 8.5 and 10 degrees from
vertical, so **about 9 degrees (plus or minus 2)**. That agrees with the 9 degrees from 3a
(rear-view CAD) and not with the 19 degrees from the video, so the video's steeper sides
are another sign of a different revision. Treat the 9 degrees as the final value, pending a
dimensioned source. The photo is a perspective view with the wheel bottoms cropped, so it
gives no scale and no stowed height. As a ratio, the body's top width is about 0.32 and its
lower width about 0.44 of the width over the wheels, which at 505 mm gives about 160 and
about 220 mm (circular, since it uses the stated 505).

### 3f. Front and side orthographic views of the final CAD [S18]

[S18] Fig. 1 (credited to [S16]) is a front view and a side view of the same CAD model as
3e, drawn orthographically with NX axes: petal-web wheels, 5 x 3 panel grid, mast deployed.
It is the first orthographic front view found. I measured the front view at its native
1136 x 714 px resolution. Three independent scale cues agree within 1.3%: the stated 700
mm mast height from wheel contact (1.109 mm per px), the 230 mm wheel height over grouser
tips from 3e (1.095), and the 415.4 mm track from [S8] (1.102). I used **1.10 mm per px**.
All values are derived.

| Quantity | Value (mm) | Compare | Status |
|---|---|---|---|
| Width over wheels (outer faces) | 497 (495 to 500) | 495.4 derived from [S8]; 505 stated | derived, **matches [S8]**; 1.6% under the stated 505 |
| Wheel width | 81 (74 px) | 80 stated; 168 printed in [S9] | derived, **matches 80; 168 excluded** (it would be 153 px) |
| Track (wheel centre to centre) | 415 (413 to 418) | 415.4 from [S8] | derived, matches (scale partly set from this value) |
| Wheel height over grouser tips | 232 | 230 from 3e | derived |
| Sidewall angle | 10 (plus or minus 1) from vertical; left 10.3, right 9.7 | 9 from 3a; about 9.4 from the [S10] photo | derived, **resolves the conflict: about 10** |
| Body top width, just below the deck lip | about 164 | 157 to 170 from 3a and 3d | derived |
| Body width, 205 mm above ground | about 205 | n/a | derived |
| Underside of body above ground | about 124 | 120 from 3a | derived |
| Deck top above ground | about 348 | 343 from 3e | derived |
| Mast and camera head above the deck | about 347 | 358 labelled in [S11] Fig. 6 | derived |

The sloped panel faces appear edge-on as thin dark lines about 10 degrees from vertical,
parallel to the body side plates, so the panel slope and the body wall slope are the same.
**Width over wheels is about 497 mm, not the 520 mm of the video**, so the stated 505 mm is
consistent with the final model to within 1.6%. The stated 470 x 505 mm is therefore the
plan size over the wheel rims (474 and about 497 to 500 in the CAD); the 10 mm gap in
section 3 is now within the scale uncertainty.

Other figures reviewed for this section (all 293 raster images in the 14 Rashid papers; vector-only
drawings are not covered):
- **[S11] Fig. 6** is a simplified antenna model with labelled dimensions: a rover top panel
  401 mm long and a mast with camera box 358 mm tall. The side view in 3e gives a top plate
  of about 403 mm (side plates about 380 mm), so 401 matches the top plate. The text states
  the mast is 290 mm from the dipole antenna (stated, [S11]).
- **[S4] Fig. 1** photographs the experimental wheel next to the CAD. Its "200 mm" line
  spans the disc and excludes the grousers, which stand proud of it. This supports 200 mm
  as the rim diameter, with grouser tips beyond it.
- Everything else was either another perspective view of the same CAD (Fig. 1 of [S5], [S7], [S8], [S6], [S10] and [S12]; the layout figure
  in [S9]), a sandbox or gymnasium photograph of the engineering model, or science
  data. None gives a further dimension.

### 3g. Solar cell size [S18], [S5]

The final-configuration CAD has 15 cells on each sloped side face, in 5 columns x 3 rows,
all landscape. I measured them in two orthographic side views ([S5] Fig. 15 and [S18]
Fig. 1), with the scale set as in 3e and 3f. All values are derived.

| Quantity | [S5] Fig. 15 | [S18] Fig. 1 | Used |
|---|---|---|---|
| Cell width (dark rectangle) | 65.8 mm | 68.0 mm | about 67 (plus or minus 1.5) |
| Cell height, projected | 37.5 mm | 38.4 mm | about 38 (about 38.6 true at a 10 degree slope) |
| Pitch along the row | 72.3 mm | 70.9 mm | about 71.6 |
| Row pitch, projected | 40.8 mm | 39.9 mm | about 40.4 (about 41 true) |
| Corner clip | not resolved | about 6.5 mm legs at 45 degrees, both bottom corners; top corners square | about 6.5 |

The outline (square top corners, both bottom corners clipped) is the outline of a half of a
wafer-sized cell, as on CubeSat half-cut cells. The size and clip match the standard
26.5 to 26.6 cm2 triple-junction cell: CESI CTJ30 lists 6.9 x 3.9 cm and 26.5 cm2, and the
Spectrolab UTJ datasheet lists a 26.6 cm2 size sold "2 per wafer". Gross area 6.9 x 3.9 =
26.9 cm2, so two equal 45 degree clips remove about 0.41 cm2, a leg of about 6.4 mm each
(my arithmetic from the catalogue areas; neither datasheet gives corner dimensions).
Measured clip legs agree. A 4 x 8 cm cell with two clips would need legs of about 14 mm,
which does not fit. The measured cell is within 1.5% of 69 x 39 mm, which also supports
the 1.10 mm per px scale in 3f.

**Test of the panel grid as a camera fiducial.** On the two perspective CAD views in [S12]
Fig. 1, the 15 cell centres were located automatically and fitted with the cell positions
known from 3f and 3g (camera pose and focal length free). In the front-left view the fit
is very tight (0.11 px residual, focal length 1,398 px, camera about 2.3 m away), and
rim ellipses placed from that pose and the true geometry (wheelbase 273, track 415) land
on the two near-side wheel outlines to about 2 px (about 3 mm). A joint fit of grid and
rims then recovered a wheelbase of 271 to 276 mm (true 273) but a track 3.6 to 6% low
(389 to 400 mm; the track depends on the panel-to-wheel offset taken from the front
view). It is not robust: the far-side arc is ambiguous (10 px off), the result moves a lot
if the traced edge is taken as 108 mm instead of 100 mm radius, and in the rear-right
view the panel is seen so obliquely that the focal length runs to its upper bound and the
fit is unusable. Conclusion: the grid fixes camera pose well when the panel face is seen
at a moderate angle, so it is worth trying on photographs of the flight rover that show a
panel, but expect wheelbase to about 2% and track to about 5 to 8%, and do not use it
where the panel is seen near edge-on.

The cell supplier is not named in any paper. The cover glass is 200 um cerium-doped
borosilicate from Qioptiq ([S10]). CESI's 26.5 cm2 and Spectrolab's 26.6 cm2 differ by 0.4%,
so the outline cannot separate them, and a cell of 7 x 4 cm (AZUR 3G30C-Advanced size
list) is within 1.5% as well. Treat the exact catalogue part as (unverified); the size
class is the finding. The CAD outline may be simplified.

## 4. Mast and cameras

Heights are above ground, measured with wheels on a hard surface.

| Quantity | Value | Status | Source |
|---|---|---|---|
| Mast length | about 300 | stated, rounded | [S6] |
| CAM-1 optical axis height | 660 (630 with grousers buried in regolith) | stated | [S12] |
| CAM-1 offset from front wheel axis | 77.9 forward, 550.8 up | stated | [S8] |
| CAM-1 height from [S8] offsets | 550.8 + 100 (wheel radius) = 650.8 | derived, consistent with 660 | [S8] |
| CAM-1 lateral position | 28 right of centreline | derived from [S8] offsets | [S8] |
| Mast rotation | 320 degrees (azimuth -170 to +150) | stated | [S12] |
| CAM-1 / CAM-2 field of view | 80 degrees | stated | [S12] |
| CAM-1 / CAM-2 body | 35 x 35 x 73 mm optical tube, 210 g each | stated | [S12] |
| CAM-2 | Fixed, rear, axis at about 250 high | stated | [S12] |
| CAM-M (microscope) | Front, aperture about 210 high, field of view about 176 ahead of aperture, 140 ahead of front wheels, tilted down (about 40 degrees in the paper figure, read from figure) | stated / derived | [S13] |
| CAM-T (thermal imager) | Rear | stated | [S2], [S12] |
| Langmuir probes | 4 identical, 80 long, mounted between about 150 and 650 height | stated | [S14], [S15] |

## 5. Power, mobility, thermal

| Quantity | Value | Status | Source |
|---|---|---|---|
| Solar panels | 2, one on each sloped side | stated | [S3] |
| Peak power generation | 15 W | stated | [S3] |
| Panel cell layout | roughly two staggered rows per side | derived (figure only) | [S1] |
| Panel size, cell size, cell count | not found | (unverified) | n/a |
| Drive | 4 in-wheel electric motors | stated | [S3] |
| Drive (alternative wording) | "four wheeled with differential gear" | stated, **unresolved** against the line above | [S1] |
| Steering | Not found. Operators "steer" by joystick, but the mechanism is not described | (unverified) | [S3] |
| Battery | Small, capacity not found | (unverified) | [S3] |
| Survival temperature range, design | -40 to +85 C for electronics | stated | [S16] |
| Operating latitude | 37.5 to 52.5 N | stated | [S16] |

The "differential gear" in [S1] and "four in-wheel electric motors" in [S3] may both be true
(for example, a differential suspension linkage plus hub motors). This file does not resolve
it. The thermal paper lists the mobility subsystem as "Wheels, Linkage, Gearbox" [S16].

## 6. Reconciliation with the provisional design in CLAUDE.md

The provisional design was inspired by Rashid, not copied from it. It does not bind the replica.

| Provisional item | Original | Action |
|---|---|---|
| 6U CubeSat envelope 100 x 200 x 340.5 | 470 x 505 x 700 | Drop the envelope |
| 15 degree sidewalls | Wedge sides exist, angle not found | Keep as a placeholder only until measured |
| 170 x 112 mm PET panels, 4 per side | 2 panels, cell layout approximate | Replace once panel size is found |
| Wheels 200 x 80 mm, hub + TPU tire, chevron grousers | 200 x 80, 14 radial grousers of 15 mm, skeletonized, Mg alloy | Diameter and width agree. Grouser shape and construction need to change |
| In-wheel planetary motors | 4 in-wheel motors [S3] | Plausibly consistent |
| 4-wheel rocker, Nomad-style Double Ackermann | Differential gear / linkage, steering not described | Unverified. Do not carry Ackermann over |
| 40120 / 4040 extrusion frame | Mg alloy frame with MLI | Ground-testbed hardware only |
| No mast | Rotating mast, about 300 long, CAM-1 on a pan and tilt gimbal | Add |

## 7. What is still missing

1. Stowed envelope (mast down), which is also the envelope inside the lander bay.
2. Body height, body width, sidewall angle and ground clearance. Derived from CAD
   figures in 3a, 3e and 3f, which agree (sidewall about 10 degrees, underside about
   124 mm up, deck top about 348 mm, body top width about 164 mm). Still need a dimensioned
   source.
3. Panel size and the position of each panel on its sloped face. Cell size and grid are now
   derived in 3g (15 cells per side, about 69 x 39 mm each, pitch about 71.6 x 41 mm); the
   absolute position of the field on the face and the cell part number remain open.
4. Suspension and drivetrain layout.
5. Wheel width is settled at about 80: 3a, 3d and the front view in 3f all give it, and
   168 is excluded.
   Wheel diameter: 3d and 3e give 200, matching the stated 200. The 228 from 3a is the
   diameter over grouser tips (3e). The video (3b to 3d) is a different revision; use 3e.
   Sidewall angle for the final model is about 10 degrees (3a, [S10] photo and 3f; the
   video's 19 is a different revision). Width over wheels is about 497 (3f). Still open:
   the panel grid detail.
6. What 470 and 505 are measured over: the CAD (3e, 3f) says plan size over the wheel rims,
   474 and about 497 to 500, so now probably answered; a stated source would confirm it.
7. Battery capacity, motor specifications.

Candidate sources: the Els et al. 2025 rover science programme paper (cited by [S6] and
[S12] as "this collection". Checked 2026-11-06: not on the Springer collection page (the
project owner looked), not in Crossref or OpenAlex, and the latest collection paper ([S8],
30 Oct 2025) still cites it without a DOI. Probably unpublished, or published under a
different title; the citing papers disagree on year, volume and title wording), any MBRSC dimensioned drawing, and photographs of the EM with a known
scale object (the EM sits in the MBRSC Moon Yard, [S13] Fig. 10).

## Sources

All checked from the PDFs in `~/Documents/scientific papers` unless a URL is given.
Journal for all Springer papers is *Space Science Reviews*.

- **[S1]** Almaeeni S, Els S, Almarzooqi H. *The Rashid rover: to guide the way for the next
  generation lunar missions and solar system exploration.* EGU General Assembly 2021,
  EGU21-14732. MBRSC. https://presentations.copernicus.org/EGU21/EGU21-12950_presentation.pdf
  (spec table on slide 1; slide 2 is EGU21-12950, Els et al.).
- **[S2]** Els S, Almaeeni S, Almarzooqi H. *The science system on-board the Emirates Lunar
  Mission's Rashid rover.* EGU General Assembly 2021, EGU21-12950. Same file as [S1].
- **[S3]** Alzaabi M, Burtz L-J, Amilineni S, et al. *Operational Concepts and Rehearsal
  Results of the First Emirates Lunar Rover: Rashid-1.* Space Sci Rev 220:84 (2024).
  doi:10.1007/s11214-024-01118-6
- **[S4]** Hurrell J, Takehana K, Tanaka T, Uno K, Busoud AK, Yoshida K. *Traction
  Performance Evaluation for a Rashid-1 Rover Wheel.* Space Sci Rev 221:37 (2025).
  doi:10.1007/s11214-025-01164-8
- **[S5]** Théret N, Cucchetti E, Robert E, Virmontois C, et al. *Enhanced Image Processing for
  the CASPEX Cameras Onboard the Rashid-1 Rover.* Space Sci Rev 220(5):60 (2024).
  doi:10.1007/s11214-024-01091-0 (HAL hal-04672725)
- **[S6]** Clausen LBN, Bekkeng T-A, Els S, et al. *The Langmuir Probe Instrument on Board the
  Rashid-1 Rover of the Emirates Lunar Mission.* Space Sci Rev 221:34 (2025).
  doi:10.1007/s11214-025-01159-5
- **[S7]** Els SG, Ageorges N, Bogosavljevic M, et al. *The Microscope Camera CAM-M on-Board the
  Rashid-1 Lunar Rover.* Space Sci Rev 220:81 (2024). doi:10.1007/s11214-024-01117-7
  (same paper as [S13]; [S7] is used for the wheel and mass statements).
- **[S8]** Stober KJ, Dorrington S, Rupasinghe D, et al. *The Passive Regolith Sampler: From
  Concept to Delivery to the Lunar Surface.* Space Sci Rev 221:99 (2025).
  doi:10.1007/s11214-025-01217-y. Camera offsets in Table 3 are from MBRSC rover documentation
  as stated by the authors.
- **[S9]** Bickel VT, Kolvenbach H, Schwarb E, Els SG, AlShehhi AM. *PLATE: a Passive,
  Light-Weight Wheel Abrasion and Terramechanics Experiment.* Space Sci Rev 221:71 (2025).
  doi:10.1007/s11214-025-01198-y
- **[S10]** Manenti L, Kaloš S, Sarnoff I, et al. *Absolute Photoelectric Yield Measurements of
  the Rashid Lunar Rover Materials at the BABE Synchrotron Facility.* Space Sci Rev 220:83
  (2024). doi:10.1007/s11214-024-01116-8
- **[S11]** Gadhafi R, Serria E, AlMaeeni S, Mukhtar H, Abd-Alhameed R, Mansoor W.
  *Investigating the Impact of Lunar Rover Structure and Lunar Surface Characteristics on
  Antenna Performance.* Sensors 24:5361 (2024). doi:10.3390/s24165361
  (figures only; no dimensions used).
- **[S12]** Ioannou Z, Amilineni S, Els SG, et al. *Onboard and Ground Processing of the
  Wide-Field Cameras of the Rashid-1 Rover of the Emirates Lunar Mission.* Space Sci Rev 221:8
  (2025). doi:10.1007/s11214-024-01127-5
- **[S13]** Els et al. 2024, as [S7].
- **[S14]** As [S6] (probe length).
- **[S15]** Gadhafi et al. 2024, as [S11] (probe height range, about 15 to 65 cm).
- **[S16]** Almehisni R, Garg P, Wali M. *Thermal Management System Design and Analysis of
  Rashid Rover - Emirates Lunar Mission.* IAC-21-C2.7, 72nd International Astronautical
  Congress, Dubai, 2021. MBRSC.

- **[S17]** "Inside the Dubai lab building the UAE lunar Rashid rover" (page title "Building
  Rashid"), *The National*, thenational.shorthandstories.com. Article text gives only the
  10 kg mass limit. Its header video, a 360 degree turntable render
  (`09-07-2021_t_d23fe02bec2c4765ae27f64a5d75389c_name_the__VKJ6.mp4`), is used for
  proportions only. Third-party, kept in an untracked local folder, not redistributed.

- **[S18]** Yakubu M, Zweiri Y, Abuassi L, et al. *A Novel Mobility Concept for Terrestrial
  Wheel-Legged Lunar Rover.* IEEE Access 13 (2025). doi:10.1109/ACCESS.2025.3529262. Used for
  Fig. 1 only (orthographic front and side views of the Rashid CAD, credited to [S16];
  the authors thank MBRSC for technical support).

Otherwise not used for Rashid dimensions: the rest of [S18] (Yakubu M, et al., *A Novel Mobility
Concept for Terrestrial Wheel-Legged Lunar Rover*, apart from Fig. 1). Its Rashid model (Fig. 29) is a
simplified simulation body, and its Table 3 gives Rashid a 0.10 m obstacle limit at a ratio of 2 to the
wheel radius, which implies a 50 mm radius and contradicts the stated 200 mm diameter. It
confirms only the 10 kg mass (including payload).

Not used for Rashid dimensions: Walker J, et al. *ispace Modular Rover Design.* IAC-19 (2019).
It describes ispace's Hakuto and modular rovers, not Rashid.

This file is licensed CC BY 4.0 (see `LICENSE-DOCUMENTATION.txt`). Figures and text from the papers
are the property of their authors and publishers; only numerical facts are recorded here.
