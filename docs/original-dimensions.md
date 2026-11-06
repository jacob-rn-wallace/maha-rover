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
| Track (FL to FR wheel centres) | 415.4 | derived (235.7 + 179.7 from camera offsets) | [S8] |
| Width check | 415.4 + 80 = 495.4 vs stated 505 | derived, 10 mm gap unexplained | [S1], [S8] |
| Body shape | Wedge. Sloped side faces carry the solar panels. Mast at the front | derived (figures only) | [S1], [S7], [S11] |
| Body main dimensions | "about 20 x 20 x 40 cm" | stated, rounded. Now plausible: see 3a and 3b | [S6] |
| Sidewall angle | about 9 degrees from vertical in the rear view (see 3a). Not stated anywhere | derived from a figure, low confidence | [S3] Fig. 2 |

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

Note that this video gives a wheel diameter near 205 mm, close to 200 mm, whereas the CAD
rear view gives 228 mm. The two disagree, and the open question in 3a stands.
| Ground clearance | not found | (unverified) | n/a |
| Frame material | Magnesium alloy, covered in ITO-coated MLI | stated | [S10] |
| Obstacle / slope / speed | 100 mm obstacle, 20 degrees, 10 cm/s | stated | [S1], [S3] |

The [S6] body figure of 20 x 20 x 40 cm is probably a rough description of something other than the
main structure. It cannot be the full body width, since the wheels' centres are 415 apart.
Do not use it until it is explained.

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
2. Body height, body width, sidewall angle and ground clearance. Rough values now in
   section 3a (derived from a figure). Still need a dimensioned source. Body length
   is about 370 to 410 mm from a video (section 3b, low confidence).
3. Panel size and the position of each panel on its sloped face.
4. Suspension and drivetrain layout.
5. Wheel width conflict (80 vs 168). The figure scaling in section 3a favours 80.
   Wheel diameter (200 rim vs about 228 over grousers) is a new open question.
6. What 470 and 505 are measured over.
7. Battery capacity, motor specifications.

Candidate sources: the Els et al. 2025 rover science programme paper (cited by [S6] and
[S12] as "this collection", in preparation or recent; not in the local papers folder as of
2026-11-06), any MBRSC dimensioned drawing, and photographs of the EM with a known
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

Not used for Rashid dimensions: Walker J, et al. *ispace Modular Rover Design.* IAC-19 (2019).
It describes ispace's Hakuto and modular rovers, not Rashid.

This file is licensed CC BY 4.0 (see `LICENSE-DOCUMENTATION.txt`). Figures and text from the papers
are the property of their authors and publishers; only numerical facts are recorded here.
