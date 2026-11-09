# Sim interface layout: where everything goes (proposal, 2026-11-09)

Status: **parts A to D built (2026-11-09), see sections 10 and 11; the Plan mode's waypoint planner (step 4) is built, section 12; E (the phone bottom sheet) not yet.** Written after the HUD, hazard overlay and camera view were added one at a time and began to collide. Wireframes: `docs/images/sim-ui-layout.svg` (and `.png`). Background: `docs/sim-ui-research.md` (rover operations tools); this file adds drone ground-station and OSD practice.

## 1. The problem today

A screenshot with everything on (1280 x 800) and one at 844 x 390 with touch on:
- **The left HUD is a wall of text**: 13 lines of telemetry, the key help, and (with `?stats=1`) the GPU string and frame statistics, all in one box under the wordmark. It grows with every feature.
- **Floating elements with no owner**: the hazard legend (bottom left), the camera view and its roll strip (bottom right), the minimap (top right), the touch sticks and three buttons, the perf panel (centre). Each positions itself with `position: fixed`, so each collision is found only by looking.
- **On a phone**: the camera view's compass readout runs over the picture and the minimap; the legend sits across the rover; the roll strip lands on the right stick.
- **Warnings are ad hoc**: the tilt guard, the wall distance and the recording line are separate coloured strings inside the text.
- Everything is visible all the time. Steps 4 to 8 of the plan (waypoints, delay, strips, panels, rehearsal) would each add more.

## 2. What the drone dashboards do (sources: a search; the QGroundControl docs read as summaries only)

- **QGroundControl, Fly View** ([UI overview](https://docs.qgroundcontrol.com/master/en/qgc-user-guide/getting_started/ui_overview.html), [Fly View](https://docs.qgroundcontrol.com/master/en/qgc-user-guide/fly_view/fly_view.html)): one main view with the other swapped to a small window ("video switcher": a click puts the video or the map in the foreground); a toolbar that always shows key status (sensors, battery, mode, armed) and changes with the view; a **multi-page instrument panel** (telemetry, camera, health) that docks bottom centre or right; separate **views** for flying and planning (Fly, Plan).
- **DJI Fly** ([guide](https://www.pix-pro.com/dji-fly-guide-part1), several guides disagree on details): video fills the screen; a **status bar** top left (mode; tapping opens the checklist and warnings) and **four status icons** top right (battery, remote, obstacle sensing, GPS); a **small map bottom left** that swaps with the video; altitude and distance along the bottom; the settings live in menus.
- **Mission Planner** ([Flight Data screen](https://ardupilot.org/planner/docs/mission-planner-flight-data.html)): HUD upper left, **tabbed control and status area** lower left, map on the right that is also the control surface ("fly to here"). Its own users call it cluttered (a forum thread, an opinion).
- **FPV on-screen display** ([a Betaflight layout guide](https://kiwiquads.co.nz/understanding-the-betaflight-osd-and-how-to-customise-it/), vendor and forum sources): **keep the centre clear**; secondary data in the corners (link top left, timer top right, battery along the bottom); stay inset from the edge; warnings only when needed.
- **Human factors for control stations** ([NASA guideline work](https://ntrs.nasa.gov/api/citations/20190001770/downloads/20190001770.pdf), summaries only): consistency and clear icons; **minimise switching** to preserve situation awareness; **customisable** displays; guidelines are not mandatory and conflict in places.
- **Rover operations** (`sim-ui-research.md`): VERVE and Open MCT both use **saved layouts of panels** around one primary 3D view; both keep telemetry limits and image freshness as small, always-visible flags.

## 3. Principles for al-maha

1. **The world view is primary and its centre stays clear**: nothing in the middle 50% x 50% of the screen (the FPV rule); the rover and the terrain ahead are the content.
2. **A thin always-on layer, everything else on demand**: a top bar of status chips (battery, tilt, wall, delay, hazard) and one small instrument cluster; detail opens when asked and closes again.
3. **One home per kind of information** (section 4); no element positions itself.
4. **Panels live in regions that stack**, so two panels can never overlap (section 6).
5. **Alerts are a layer of their own**, driven by the limits table (`limits.ts`): shown only at yellow or red, always in the same place, replacing the ad hoc strings.
6. **Modes are layout presets** (Drive, Camera, Plan, Data), as QGC's Fly and Plan views and VERVE's layouts: a mode decides which panels are open and which view is primary; it never hides the top bar or alerts.
7. **Swap, don't stack**: the mast camera and the map can each take the main area, with the chase view as the inset (QGC and DJI's swap).
8. **Budget**: the UI covers at most 25% of the screen in any mode; 12 px margins; type 11 to 13 px.

## 4. Where each thing goes

| Element | Home | Visible | Notes |
|---|---|---|---|
| Wordmark | top bar, left, at bar height (about 24 px) | always | the owner's text-to-wordmark change of 2026-11-09 stays; its large size and the readouts under it go |
| Mode tabs (Drive, Plan, Camera, Data) | top bar, left of centre | always | keys 1 to 4 |
| Status chips: battery, tilt, wall, delay, hazard, recording | top bar, centre | always; coloured by `limits.ts` | a chip opens its detail (the hazard chip opens the legend; the battery chip the power lines) |
| Help (keys) and settings, performance log | top bar, right: `?` and gear | on demand | the key line leaves the HUD; stats and the log panel go under the gear |
| Speed, heading, pitch and roll (attitude ball) | instrument cluster, bottom left | Drive, Camera | replaces the first lines of the text; the DJI and FPV bottom-corner position |
| Full telemetry (drive, soil, links, mast, current, power, position) | left dock panel "Telemetry" | Data (open); other modes (closed, slim handle) | grouped, level-coloured; the panel the text wall becomes |
| Alerts (tilt guard, wall, battery, recording) | bottom centre, above the hint line | only at yellow or red | stack up to two; the tilt guard's "T to stand upright" lives here |
| Key hints | bottom centre, under the alerts | until the first input, then gone | one line |
| Minimap | right column, top | Drive, Data (small); Plan (primary) | |
| Mast camera tile | right column, below the map | Drive (small); Camera (primary) | the compass, the readout and the flags move into the tile's own header and footer, not over the picture |
| Camera roll (snap, thumbnails, live) | the camera tile's footer | with the tile | no longer a separate floating strip |
| Hazard legend | popover from the hazard chip | when the overlay is on | not on the main view |
| Hazard tint, waypoints, path, camera footprint | in the 3D world | by toggle | no chrome |
| Plan panel (waypoints, distance, energy, solar heading, rehearse) | left dock | Plan | step 4 and 8 |
| Delay controls and the predicted ghost | the delay chip and a popover; the ghost in the world | Drive, Camera | step 5 |
| Telemetry strips and time conductor | bottom region | Data | step 6 |
| Touch sticks | bottom corners | touch screens | their own layer; nothing else may sit in the bottom corners on a phone |
| Performance panel | centre modal | after a recording | as now |

## 5. The four modes (wireframes 1 to 4)

| Mode | Main area | Left dock | Right column | Bottom |
|---|---|---|---|---|
| **Drive** | chase view | closed | map (small), camera tile (small) | instrument cluster, alerts |
| **Camera** | mast camera, large | closed | chase view inset | roll and flags, alerts |
| **Plan** | map, large (hazard classes on) | plan panel | chase view inset | alerts |
| **Data** | chase view (upper 60%) | telemetry panel | map (small) | strips and time conductor |

Phone (wireframes 5 and 6): the top bar becomes chips plus a mode menu; one tile at a time (tap to expand it over the main view); telemetry, the legend and settings in a bottom sheet; the two sticks and "stand upright" are the only things in the bottom band.

## 6. How to build it (so that overlap cannot happen)

- **`ui.css`**: tokens for the panel look (background, radius, type sizes, spacing, the level colours from `limits.ts`), replacing the many inline `cssText` strings.
- **`layout.ts`**: one overlay `<div id="ui">` with a CSS grid of named regions: `topbar`, `left`, `right`, `bottom`, `cluster` (bottom left), `alerts` (bottom centre), `sticks` (bottom corners, touch). `pointer-events: none` on the grid, `auto` on panels. A `Panel` base class (title, collapse, which modes show it, which region) that `Hud`, `Minimap`, `CameraView`, the legend, and later the plan panel and the strips extend. Regions stack their panels, so adding one pushes the others instead of covering them.
- **`alerts.ts`**: reads `evaluate()` from `limits.ts` and the tilt guard and recording flags; one place that decides what is shown.
- **Mode switching** in `layout.ts`: a table of mode to open panels and primary view; a saved choice in `localStorage` (try/catch).
- The 3D canvas, the camera render and the minimap canvas keep their code; only their placement and wrapper change.

## 7. Order of work (each step leaves the sim working; checks by headless screenshots at 1280 x 800 and 844 x 390)

A. **Layout shell**: `ui.css`, `layout.ts`, `Panel`; move the existing elements into regions with no change of content: minimap and camera tile in the right column, the legend into a popover, the stats and the key help into the gear and `?` panels. Screenshot comparison before and after.
B. **Top bar**: wordmark, status chips from `limits.ts`, `alerts.ts` replacing the ad hoc strings.
C. **Telemetry panel and instrument cluster**: the text wall becomes the grouped left dock panel plus the bottom-left cluster (speed, heading, attitude).
D. **Modes and swap** (Drive, Camera first; Plan and Data as their features arrive).
E. **Phone layout**: bottom sheet, one tile at a time.
Then plan steps 4 to 8 mount their UI in the regions above.

## 8. Decisions (owner, 2026-11-09)

1. **Modes**: four, as drawn (Drive, Plan, Camera, Data).
2. **Wordmark**: shrunk to the top bar's height (built: 24 px, 20 on phones).
3. **Telemetry**: the full panel is closed by default (built: the status chips and the instrument cluster carry the glanceable part; **I** or the handle opens it).
4. **Key list**: only behind `?` (built: `?` button or key; a one-line hint shows until the first input).

## 9. What this does not cover

No user testing; the proportions are from one 1280 x 800 and one 844 x 390 screenshot. The drone sources are documentation and guides read as search summaries, not the full texts. The 25% budget and the 50% x 50% clear centre are design rules of thumb, not measured limits.

## 10. Built so far (2026-11-09: parts A, B and C)

Files (`sim/src`): `ui.css` (tokens and regions), `layout.ts` (the regions, popovers), `topbar.ts` (wordmark, chips, help and settings), `alerts.ts` (alerts, status banner, hint), `telemetry.ts` (the left dock), `cluster.ts` (attitude ball, speed, heading), `help.ts` (the key list), `ui.ts` (the facade that evaluates `limits.ts` once and feeds each part). `hud.ts` is gone. The minimap, the camera view, the hazard legend, the touch sticks and the performance panel were moved into regions.

What changed on screen:
- **Top bar**: wordmark; chips for battery, tilt, wall distance (with terrain), hazard (a pair: toggle, and an arrow that opens the legend popover), and a red recording chip; `?` and a gear. The battery chip opens a power popover; the gear opens settings, with the GPU string and frame statistics (open with `?stats=1`) and the record button.
- **Alerts** (bottom centre): only at yellow or red: tilt guard cut, tilt near or over the limit, wall, battery, motor current at the cap, benchmark running. Loading and error text use the same place.
- **Instrument cluster** (bottom left): attitude ball, speed, heading, pitch and roll (level-coloured).
- **Telemetry** (left dock, closed): grouped rows (drive, attitude, mast, power, world) in the old order of information; key I.
- **Right column**: the minimap on top, the mast camera tile below. The camera tile now holds its own header, freshness flags, picture, footer (compass and readout) and roll; the picture is drawn into the canvas under the tile's picture box, so the tile's place in the layout is the only place the view is (no more `mapOffset`). Large camera is the room under the map, at most 46% of the width; large map at most 38% of the height.
- **Hazard legend**: a popover from the hazard chip, shown for 8 seconds when the overlay goes on.
- **Phones**: the right stick shrank to 100 px, the camera tile loses its footer, roll and flags (below 140 px wide), the minimap is 96 px, nothing overlaps the sticks.
- Panels have no backdrop blur (it would be re-blurred every frame over the animating canvas).

Checked in headless screenshots (1280 x 800 and 844 x 390): the default Drive layout, telemetry open, hazard on with the legend, the help list, a past still with flags, the battery and settings popovers, a forced 74-degree tilt (red chip, alert, red cluster), the phone layout with and without the dock. `tsc`, `vite build`, `check:limits` (16) and `check:freshness` (17) pass.

Not checked or known:
- **A rendering quirk in headless Chrome**: the legend popover did not paint when it was opened in the same turn as the hazard toggle (the DOM said open and the element was topmost); opened 100 ms later it paints. The cause is not understood; the delay is a workaround. A real browser may not need it.
- A real GPU or touch device; the cost of the DOM over the canvas; the large-map plus large-camera combination on small windows; the wordmark's contrast on a bright sky.
- On a phone the open telemetry dock sits under the left stick's area.
- The bench and recording chips were not triggered in a screenshot.
- The phone bottom sheet (E) is not built.

## 11. Modes (part D, built 2026-11-09)

`sim/src/modes.ts`; tabs in the top bar, keys **1 to 4**, `?mode=drive|plan|camera|data` at the start.

| Mode | Main view | Panels |
|---|---|---|
| Drive | chase view | map and camera as small tiles; telemetry closed |
| Camera | the mast camera, as a centred 4:3 tile with its header, flags, picture, compass, readout and roll | chase view as an inset; map hidden; telemetry closed |
| Plan | the map, a centred square, zoomable (the waypoint planner, section 12) | the Plan panel in the left dock; chase view as an inset; camera hidden |
| Data | chase view | telemetry dock open; map small; camera hidden. **No strips yet** (step 6) |

- A mode is a preset: switching sets the telemetry dock, the tiles and the inset; it does not remember a manual toggle.
- **C** toggles Camera mode and back (it used to cycle small, large, off); **M** still cycles the map small, large, off, in Drive and Data. The camera tile in Drive has a fold button (–) in its header; `?pip=0` starts it folded and `?pip=2` starts in Camera mode.
- The **inset** is a transparent box in the top-right corner (under the bar, where the map is in Drive) and the chase view is drawn into its rectangle with a scissor; clicking it returns to Drive. It sits at the top right, not the bottom as in the wireframe, so it never meets the touch sticks or the alerts.
- The main-view tile is sized to the largest fit under the bar with the inset's width kept free on both sides, so the inset never overlaps it.
- Checked in headless screenshots (1280 x 800, 844 x 390): all four modes, the keys 1 to 4 and C, the inset click, the fold button, Camera mode on a phone. `tsc`, `vite build` and the node checks pass.
- Not checked: a real GPU; the cost of the chase view as an inset plus the camera view; the camera's picture when the window is very narrow; orbit dragging on the canvas while the chase view is only an inset (it still moves the chase camera); the 768-sample map's first-use pause (it is a one-off paint of 590,000 height samples).
- On phones the two touch buttons ("camera view", "stand upright") sit over the bottom of the Camera mode picture.

## 12. Waypoint planning (step 4, built 2026-11-09)

Files (`sim/src`): `plan.ts` (the pure logic: route, metrics, solar heading, footprint, guidance; `npm run check:plan`, 28 cases), `planPanel.ts` (the dock panel and the map interaction), `routeView.ts` (the markers in the world), plus a zoomable view in `minimap.ts`.

- **Placing**: in Plan mode a click on the map places a waypoint; a drag sets its heading (without a drag it is the direction of travel); a click on a marker selects it. The panel lists each waypoint with its distance from the previous point, its heading and the turn it makes there (L or R), with a ☀ button (face the panels to the sun) and a remove button; Backspace or "undo" removes the last; "clear" empties the route.
- **Map view**: on entering Plan it shows 800 m across, centred on the rover (1 m a pixel at the default window size); the wheel zooms about the cursor, shift-drag or right-drag pans, the buttons in the corner zoom and centre; the base map is repainted for the window (23 ms in the test) at most every 150 ms; the scale bar picks 10 m to 2 km. Leaving Plan resets the small map to the whole tile.
- **On the map**: the path (dashed blue, distinct from the amber trail) from the rover through the waypoints, numbered markers with heading arrows, an arc with an arrowhead for the turn at each waypoint, and the selected waypoint's **camera footprint** (a quadrilateral for the camera 0.667 m up, level, out to 15 m: near edge 1.1 m).
- **In the world**: a pole, a heading cone and a flag at each waypoint, the path on the ground and the selected footprint's outline (all drawn on the terrain, hidden from the mast camera's own view, as the hazard overlay is).
- **Totals** (estimates, labelled in the panel): distance, turn degrees, time, energy in Wh and as a percentage of the pack's 44.4 Wh, and the solar power at the last waypoint's heading against the best possible. Assumptions: 0.5 m/s (the sim's full throttle gives 0.527), turns at 60 degrees a second (the sim turns at about 100 degrees a second at full command on flat rigid ground, `?test=1`; soil losses are not measured), 14 W while moving or turning (about 2 A, `sim-spec.md`). Slope, soil and rocks are not counted.
- **Solar heading**: the side panels face the body's left and right, 10 degrees above the horizon, so the best heading puts one side to the sun (two equivalent headings; the one nearer the direction of travel is used). For the fixed sun (bearing 50 degrees, 14 degrees up) that is about 320 degrees or 140 degrees.
- **Following the route**: the rover is driven with the usual controls. A **route chip** in the top bar (click: Plan mode) shows the next waypoint, the distance and the turn to face it (for example "wp 1/3 · 18 m · left 40°"); a waypoint counts as reached within 1.5 m. There is no autopilot.
- Checked in headless screenshots and scripted pointer events: three waypoints placed (one with a drag), the solar heading button, the chip, the markers and footprint in the chase view, the zoomed map. `tsc`, `vite build`, `check:limits` (16), `check:freshness` (17), `check:plan` (28).
- Not checked: a real mouse (wheel, shift and right-drag pans, the drag preview), touch placing on a phone, a waypoint list longer than the panel, waypoints near the tile edge, the footprint on slopes (it is flat-ground geometry), the route while the rover moves, a real GPU.
- Not built from the plan: rehearse mode (step 8); energy cost on slopes; the path avoiding the hazard classes; a time-ordered view of the route.
