# Sim interface layout: where everything goes (proposal, 2026-11-09)

Status: **a plan, not built.** Written after the HUD, hazard overlay and camera view were added one at a time and began to collide. Wireframes: `docs/images/sim-ui-layout.svg` (and `.png`). Background: `docs/sim-ui-research.md` (rover operations tools); this file adds drone ground-station and OSD practice.

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

## 8. Decisions for the owner

1. **Modes**: four presets (Drive, Plan, Camera, Data) as drawn, or fewer (for example Drive with the camera swap, and Plan)? Plan and Data only matter once steps 4 and 6 exist.
2. **Wordmark**: shrunk to the top bar's height, or kept large in a corner with the bar starting beside it?
3. **Telemetry**: the full panel closed by default in Drive (as drawn: the cluster and chips carry the glanceable part), or open as now?
4. **Real-time hints**: the one-line key hints fade after the first input; is that acceptable, or should the full key list stay one click away only (the `?`)?

## 9. What this does not cover

No user testing; the proportions are from one 1280 x 800 and one 844 x 390 screenshot. The drone sources are documentation and guides read as search summaries, not the full texts. The 25% budget and the 50% x 50% clear centre are design rules of thumb, not measured limits.
