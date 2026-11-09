# Rover control and monitoring UIs: research for the al-maha sim (2026-11-09)

Purpose: what real planetary-rover operations software shows and how it is organised, to inform the sim's HUD, camera view, minimap and controls (`sim/src`, `docs/sim-spec.md`). Facts come from web search summaries and one full paper read (VERVE); nothing here is from the Rashid team (no source found on how MBRSC drives it). Items marked **(unverified)** were only seen in a search summary. No images or text were copied.

## 1. Sources by system

| System | What it is | UI facts worth borrowing | Source |
|---|---|---|---|
| **VERVE** (NASA Ames; VIPER driving, Astrobee) | Desktop 3D ops tool; VIPER is a lunar rover driven with about 3 s latency | See section 2 (read in full) | [SpaceOps 2025 paper](https://ntrs.nasa.gov/citations/20250003387) |
| **RSVP / MSLICE / MobSketch / ArmSketch / SSim** (JPL; Curiosity, Perseverance) | Sequencing and visualisation suite; drives are sketched graphically, then turned into hundreds of commands | Routes colour-coded by drive type (directed vs AutoNav); a flight-software-in-the-loop simulator to rehearse before uplink | [JPL RSVP page](https://robotics.jpl.nasa.gov/what-we-do/flight-projects/mars-2020-rover/rsvp-mars-2020), [m2020 syseng slides](https://ai.jpl.nasa.gov/public/documents/presentations/m2020-5-syseng.pdf) |
| **COCPIT** (NASA Ames, Perseverance) | Web app for collaborative activity planning | Shared plans edited by many users, translated to sequences | [SJSU record](https://scholarworks.sjsu.edu/faculty_rsca/3724) |
| **Open MCT / VISTA** (NASA Ames, JPL) | Open-source web telemetry dashboard framework, used for Mars 2020 | Object tree; drag-and-drop composition into plots, tables, imagery and user-sized layouts; live and historical data side by side; responsive for mobile; plugin telemetry adapters. A time conductor, limits and conditional styling exist in its user guide but were not read **(unverified)** | [About Open MCT](https://nasa.github.io/openmct/about-open-mct), [User Guide](https://nasa.github.io/openmct/docs/static/files/Open_MCT_Users_Guide.pdf) |
| **PRoViP / PRo3D** (JOANNEUM, VRVis; ExoMars ROCC in Turin) | Ground 3D reconstruction and geology visualisation from PanCam | Waypoints double as instrument-view planning: the instrument footprint and its simulated view are shown on the surface | [ASTRA 2022 paper](https://robotics.estec.esa.int/ASTRA/Astra2022/30_ASTRA_2022-Paar-Ortner-et-al_V1.1-30-77-Ortner-Thomas.pdf) |
| **3DROV** (ESA) | Rover simulation for early design testing, Mars and Moon | A sim, not an ops UI; the nearest peer of this project | [ESA article](https://www.esa.int/Enabling_Support/Space_Engineering_Technology/New_planetary_simulation_software_puts_ESA_rover_designs_to_the_test) |
| **Yutu-2 / Chang'e-4 teleoperation** (Beijing Aerospace Control Center) | Hybrid ground teleoperation and onboard hazard avoidance via the Queqiao relay | Stereo imaging before every move; terrain mapping and localisation minutes after downlink; Chang'e-3 used an immersive stereo scene on a curved screen **(unverified: no UI detail found)** | [ISPRS 2020](https://isprs-annals.copernicus.org/articles/V-3-2020/595/2020/isprs-annals-V-3-2020-595-2020.pdf) |
| **Student rover challenges** (URC, ERC) | React or Qt base-station GUIs over a ROS bridge or a TCP link | Camera feeds, a minimap for awareness, joystick driving, point cloud plus camera fusion | [BYU 2025](https://repository.arizona.edu/handle/10150/679589), [ICARSC 2024](https://robotik.informatik.uni-wuerzburg.de/telematics/download/icarsc2024.pdf) |

## 2. VERVE in detail (the closest analogue: a lunar rover driven live)

From the SpaceOps 2025 paper (read in full):
- **Layout:** a central 3D view with the rover model in its terrain, plus individually openable and closable views (image viewers, telemetry, command status); the user can save a layout. Several image viewers can be open, each on its own camera, showing the camera's settings; a history stepper with an **orange border on older images** and **freshness markers** on the newest.
- **Hazard map as the main driving layer:** a wedge of terrain 1 to 15 m ahead of the cameras, scored on a 10 cm grid from slope, step height and the rover's own limits, drawn as a colour overlay on the 3D terrain. Other layers (slope, gradient direction, elevation isolines, step height) can be switched in, and the colour gradient is adjustable. Opacity of overlapping products (point cloud, hazard map, image) is adjustable.
- **Photo quads:** each camera image is placed in 3D in front of the camera that took it; "zoom" flies the virtual camera to that viewpoint so image and map line up.
- **Waypoint driving:** the driver places a waypoint (position and heading) in the 3D view, up to 8 m away; one drive step is about 5 minutes, pipelined (aim the camera and queue the next image while the rover is still moving).
- **Waypoint aids:** an arrow showing the turn direction (so a turn of more than 180 degrees does not surprise the driver); a one-click heading that maximises solar power; a "CamPoint" that places a virtual camera target on the terrain to aim the gimbal.
- **Roles:** Driver and Co-Driver have command authority; Nav and Real-Time Science watch the same views. Proposed commands and map markup sync across consoles.
- **Display choice:** 2D screen with a 3D view, not a head-mounted display, because of fatigue, nausea and load.
- **Pose correction:** a manual pose adjustment when the estimate drifts from the map.

## 3. Time delay and predictive displays

- NASA's lunar terrain vehicle teleoperation studies at 0, 4, 6 and 8 s delay ([NTRS 20240011392](https://ntrs.nasa.gov/citations/20240011392)): operators drove slower and braked more under any delay; three distinct strategies at 4 s; at 6 to 8 s they leaned on cruise control (low-speed cruise of about 1 to 1.5 kph preferred); a **predictive circle** on the navigation display was used; over 95% of navigation involved panning the mast camera through 180 degrees to check for boulders and craters; workload rose significantly with delay. Vehicle fenders and rails in view were used to judge the path.
- A study of three interfaces at 3 s (avatar-aided, predictive, hybrid): both aids confused operators and the authors call for showing prediction uncertainty. **(unverified, abstract only)**
- MDA predictive display with 3 s artificial delay and a velocity-projection display (Efremov et al.): older and smaller studies, same idea. **(unverified)**

Relevance: al-maha's sim is real-time. The Earth to Moon delay is the single largest difference between an operator UI and a game HUD, so an optional **delay mode** would be the most faithful addition: a command and video delay of about 2.6 s round trip, with a ghost or predicted pose drawn on the delayed view.

## 4. Patterns that recur across all of these

1. **A 3D world view of the rover is primary**; camera images are secondary, placed in context (VERVE, PRo3D, Chang'e).
2. **Hazard and slope are painted on the terrain**, not shown as numbers.
3. **Freshness is explicit**: old images are marked, ages are shown (VERVE; Open MCT's live versus historical).
4. **Plan, then command**: waypoints and routes drawn on the map with colour for mode; command status shown as proposed, executing, done.
5. **Layouts are user-arranged panels**, many views, saved (VERVE, Open MCT).
6. **Telemetry is plotted over time and in tables with limits**, not only current values (Open MCT).
7. **Drive increments are short** where delay is short (8 m steps; 1 to 1.5 kph cruise).
8. **Power orientation is a first-class driving constraint** (VERVE's solar heading).
9. **Simulate before you send** (SSim, RSIM with VERVE): the rehearsal tool is the same UI as the live one.

## 5. What al-maha's sim already has (from `docs/sim-spec.md`)

HUD with speed, slip, pitch and roll, link angles, mast pan and tilt, motor currents, battery, solar and position; a mast camera view as a picture-in-picture (with vignetting and noise); a minimap with trail; tilt-guard and wall warnings; touch sticks; a perf recorder. It is a first-person driving HUD, closer to a game than to VERVE.

## 6. Candidate additions, ranked by value for effort (suggestions, not decisions)

1. **Slope and hazard overlay** on the terrain ahead (a tint by local slope against the rover's tip limits, from the heightfield the sim already has; also rock step height from the rock generator). Matches VERVE's primary driving layer and the existing tilt guard.
2. **Image freshness and age** on the mast view (age stamp, frozen-frame border when a delay mode is on).
3. **Waypoint mode**: click on the terrain to place a waypoint with heading and a turn-direction arrow; the rover drives it with the existing controls. Pairs with a "drive step" readout.
4. **Delay mode** (off, 1.3 s one way, or custom) with a predicted-pose ghost and predictive path circle, as in the NASA LTV studies.
5. **Telemetry strips**: scrolling plots of battery state, motor current, pitch and roll with limit lines (Open MCT style), toggled by key; plus a sun-heading indicator and a "best heading for solar" shortcut (VERVE).
6. **Panel layout**: let the user open, close, and drag the camera view, minimap and plots (saved in localStorage).
7. **Plan preview**: draw the planned path on the minimap in a colour distinct from the trail, with distance and estimated energy use (the power model exists in `sim/src/power.ts`).
8. **Mast pointing aids**: a pan and tilt compass on the camera view, and a click-to-aim on the terrain (VERVE's CamPoint).

Not worth copying: multi-user collaboration (COCPIT, VERVE markup sync), stereo or head-mounted displays (fatigue; VERVE avoided it), ground-side photogrammetry (PRoViP).

## 7. Further reading done (2026-11-09): three documents from the private repo

Read in full: the [VERVE SpaceOps 2025 presentation](https://ntrs.nasa.gov/api/citations/20250005241/downloads/VERVE%20SpaceOps%202025%20Presentation.pdf) (`reference-material/`; mostly screenshots, little text), the Open MCT User's Guide v1.0, 2021 (`reference-material/`), and Maxwell et al., "The Design and Architecture of the Rover Sequencing and Visualization Program (RSVP)" (`papers/`; the Mars Exploration Rover version, 2003-04, not the Mars 2020 one). Citations only here; the files stay in the private repo.

**VERVE slides.** The primary view is a third-person 3D view with a HUD over it. The hazard gradient has four classes and *switches to a slope display at the operational limit*, so the colour means "past what the rover can take". Image viewers carry a labelled grid overlay. Pose is drawn twice: the onboard filter (blue line) and the ground-corrected path (green, with orientation arrows). Foxglove and RViz are named as the common 3D robot interfaces; immersive telepresence is called unsuitable for high-tempo operations.

**Open MCT guide.**
- *Imagery freshness*: three separate flags per image: **age** (blinks for a new image, green for 2 to 5 minutes), **position** (the rover has not moved or turned since), **camera** (the pan-tilt unit still points the same way).
- A **compass rose** on the image: north up or camera up (click toggles), the camera angle relative to the body, the body attitude, and the sun angle against the cardinal directions.
- Past images: a thumbnail roll; an **orange border** on a past image; live refresh pauses until the play button is pressed; brightness and contrast sliders, with reset.
- **Limits**: yellow and red, carried in the telemetry, shown only while violated, in tables, plots (violating points drawn distinctly) and layouts.
- **Condition sets**: ordered rules, first match wins, a default at the bottom; they restyle widgets (fill, border, text colour, image, visibility) and can output named states (LOW, NORMAL, HIGH). Test data can force values to check a rule.
- **Time conductor**: one shared window for every view, fixed or "now minus an offset" (a right-hand offset above zero leaves room for predictions), draggable, with a history of the last 10 windows, shareable in the URL. Time systems include ERT, SCET, SCLK and sol.
- **Layouts**: a readout is placed as an alphanumeric (label, value, or both) and converts to a plot or table in one step; selecting several converts them into one stacked plot. Overlay plots share a y axis, stacked plots each have their own with a common time axis. Time strips show plans as swimlanes. Notebooks keep time-stamped shift logs.

**RSVP (MER).**
- The design rule: mix 3D visualisation and text. Motion and imaging commands suit the 3D view; housekeeping commands (heaters, communication windows) suit text. Both stay synchronised on one underlying sequence, through a message hub, and the user uses whichever fits.
- The 3D tool (HyperDrive) shows a **trapezoidal footprint** on the terrain for an imaging command and a marker at a drive destination; the user flies around to judge whether a rock is traversable. Areas without terrain data are drawn as a plain beige zone.
- It simulates the move with the rover's own navigation code and **reports errors** (for example an arm target out of reach); it shows the **predicted view from any camera**; and it renders the **movie of the planned day**, shown at every daily uplink meeting so the team shares one picture.
- A sequence-flow timeline shows when commands run against the communication windows; it was added late, after an operational readiness test, which the message-hub design made cheap.
- The command editor builds its dialogs from a data file (ranges, units, tooltips, out-of-range arguments flagged).

## 8. Plan for the sim (2026-11-09)

The existing HUD is a text block over a first-person view. The cheapest, most self-contained items come first, and each step leaves the sim working.

0. **Split the UI out of `main.ts`** (done 2026-11-09, section 9): `hud.ts`, `cameraView.ts`, `perfPanel.ts`, `touch.ts`, `input.ts`. Each later step is then a small change in one file.
1. **Limits table and status colours** (done 2026-11-09, section 10). One rule table (a `limits.ts`: name, value function, yellow and red thresholds, in the style of Open MCT's condition sets) for battery state, motor current, pitch and roll, tilt-guard state and wall distance. The HUD colours each readout from it; the same table later drives the telemetry strips and the minimap. The current HUD shows numbers only, and the tilt guard and wall warnings are ad hoc strings.
2. **Hazard and slope overlay on the terrain.** A tint of the ground by local slope against the rover's tilt limits (25 degrees cut, 15 resume), four classes, switching to the slope colour at the limit as VERVE does; a second layer for rock step height from the generator; toggled by a key, drawn on the main view and optionally on the minimap. Slope comes from the heightfield the sim already samples.
3. **Mast camera view: freshness and compass.** Age, position-changed and camera-moved flags (Open MCT's three), a compass rose with north-up or camera-up, the camera angle against the body, the body attitude and the sun angle, an orange border and paused refresh when viewing a past frame (a short frame history). Cheap, and useful before any delay mode exists.
4. **Waypoint planning.** Click the terrain to place a waypoint and heading; a turn-direction arrow; a **footprint** of the mast camera on the ground at the waypoint (RSVP); a path preview on the minimap in a colour distinct from the trail, with distance and energy cost from `power.ts`; a "best heading for solar" shortcut from the fixed sun (VERVE). The rover drives it with the existing controls first (assisted driving), autonomy later if wanted.
5. **Delay mode.** Command and video delayed by an adjustable one-way time (default 1.3 s for the Moon), with a ghost at the predicted pose and a predicted-path circle (NASA lunar vehicle studies); an optional cruise control for the 1 to 1.5 kph range operators chose. Needs steps 3 and 4.
6. **Telemetry strips with a shared time window.** Scrolling plots of battery, motor current and tilt with limit lines from step 1, under one pause and scrub window, with the last windows remembered.
7. **Panel layout.** Open, close and move the camera view, minimap and strips, saved in `localStorage`; a readout converts to a plot (Open MCT).
8. **Rehearse mode (stretch).** Plan a drive, run it in a fast preview with errors reported (steep slope, wall, battery below a floor) before executing, as RSVP's simulation and movie did.

Not copied: collaboration and map markup sync, stereo or head-mounted views, ground photogrammetry, and a text command editor (the sim has no command dictionary; a key-bound console is the most it would need).

## 9. UI module split (done 2026-11-09)

`sim/src/main.ts` held the HUD text, the camera view's box and drawing, the touch sticks, the keyboard and gamepad input and the benchmark's result panel as module-level functions with shared mutable variables (`pip`, `logToggle`, `mapToggle`, `hudFull`). They now live in their own files; the behaviour is meant to be unchanged.

| File | Holds |
|---|---|
| `hud.ts` | `Hud` (the readout under the wordmark; the phone short form and tap-to-expand) with the text builders for the readout, the power line, the wall warning and the soil line |
| `cameraView.ts` | `CameraView`: the mast camera, its picture-in-picture box and label, the C cycle (small, large, off) |
| `touch.ts` | the two touch sticks and the two buttons |
| `input.ts` | `setupInput`: keyboard, gamepad and touch into `Controls`, with an `Actions` interface (upright, camera, map, log) instead of shared variables, and a hook for the scripted benchmark controls |
| `perfPanel.ts` | `PerfPanel`: the result panel and the log download button |

`main.ts` keeps the scene set-up, the frame loop, the benchmark route and the `?test=1` script (283 lines, from 405). Checked: `tsc --noEmit` and `vite build` pass; headless screenshots through `tests/cdp-shot.mjs` (flat ground, `pip=1`, and `pip=2&touch=1`) show the HUD text, camera view and touch sticks drawn as expected. Not checked: a real GPU or touch device, the recording line and the benchmark panel (not triggered), the minimap offset on phones with terrain loaded, and a before-and-after pixel comparison (the old build was not screenshotted).

## 10. Limits table (done 2026-11-09)

`sim/src/limits.ts` holds one table of yellow and red thresholds; `evaluate()` gives each readout a level (OK, yellow, red) and the HUD colours the readout from it (`hud.ts`). The tilt thresholds moved to `constants.ts` (`TILT_CUT_DEG` 25, `TILT_BACK_DEG` 15) so the tilt guard in `physics.ts` and the HUD share them.

| Readout | Yellow | Red | Basis |
|---|---|---|---|
| battery state of charge | below 30% | below 15% | look choice, not sourced |
| motor current (largest wheel) | 1.2 A (75% of the cap) | 1.52 A (95%) | fractions of the 1.6 A cap (`differential-spec.md`) |
| tilt (larger of pitch and roll) | 15 degrees | 25 degrees | the tilt guard's resume and cut angles (an assumed firmware rule) |
| distance to the sandbox wall ahead | under 100 m | under 20 m | the 100 m the HUD already warned at; red is a look choice |

Changes you can see: pitch and roll, motor current and battery turn yellow or red; the wall warning is yellow, then red; the phone short form gains the wall warning (it had none). `npm run check:limits` checks the thresholds (16 cases, all pass). Checked in a headless screenshot with the chassis forced to a 23 degree roll (the pitch and roll line turned yellow). Not checked: red in the page, the battery and current colours in the page, the phone form.

## 11. Gaps

- No source found on MBRSC's or Rashid's own ground interface; nothing here is Rashid-specific.
- The Chinese rover console details are thin: the Yutu-2 papers cover imaging and mapping, not the interface.
- The VERVE slides are mostly images; the Open MCT guide is a 2021 version 1.0; the RSVP paper is the 2003 MER design. The Mars 2020 RSVP screens and JPL's Rapid Traverse paper are still unread.
- The two delay-interface studies in section 3 were read as abstracts only.
