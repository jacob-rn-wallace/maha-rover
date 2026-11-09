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

## 7. Gaps

- No source found on MBRSC's or Rashid's own ground interface; nothing here is Rashid-specific.
- Open MCT's time conductor, limits and conditional styling were not read, only listed.
- JPL RSVP's actual screens were not seen (the JPL page lists components without UI description); a search for its display features found no HUD-style slope overlay **(unverified)**.
- Chinese rover UI details are thin; the Yutu-2 papers cover imaging and mapping, not the console.
- Worth reading next: the [VERVE presentation](https://ntrs.nasa.gov/api/citations/20250005241/downloads/VERVE%20SpaceOps%202025%20Presentation.pdf) (screenshots), the [Open MCT User Guide](https://nasa.github.io/openmct/docs/static/files/Open_MCT_Users_Guide.pdf), and JPL's [Rapid Traverse paper](https://robotics.jpl.nasa.gov/media/documents/2023-rapid-traverse.pdf) for how drivers use autonomy products.
