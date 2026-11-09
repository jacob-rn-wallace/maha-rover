# Sim interface hand-off (written 2026-11-09, at the pause after step 5)

Read this first in a new session that works on the **interface** of the browser sim (`sim/src`). `docs/sim-handoff.md` is the older hand-off for the whole sim (data, terrain, physics, deployment); `docs/sim-spec.md` is the specification; this file is the working state of the interface work done on 2026-11-09 and what to do next.
Companion documents, in the order they were written: `docs/sim-ui-research.md` (what real rover and drone interfaces do, the 8-step plan), `docs/sim-ui-layout.md` (the layout, the modes, and a dated "built" section for each part). This file points into them rather than repeating them.

## What exists

All of it is committed and pushed to `main` (last commit `94213c9`, "signal delay"), except what this file's own commit adds. The interface is about 3,400 lines of TypeScript in `sim/src` together with the physics and terrain code.

| Area | Built | Where (`sim/src`) | Detail |
|---|---|---|---|
| Research and plan | rover and drone interface research; 8 steps | docs only | `sim-ui-research.md` sections 1 to 8 |
| Limits | one table of yellow and red limits colours every readout | `limits.ts`, `constants.ts` | layout doc section 10 |
| Hazard overlay (H) | ground tinted by slope, rocks by height, four classes | `hazard.ts` | `sim-ui-research.md` section 11 |
| Mast camera view | compass, camera roll of stills (P, [ ], V), freshness flags, offscreen stills | `cameraView.ts`, `cameraRoll.ts`, `compass.ts`, `freshness.ts`, `cameraFx.ts` (`snapshot`) | `sim-ui-research.md` section 12 |
| Layout shell | regions, top bar with chips, alerts, telemetry dock, instrument cluster, help, popovers | `ui.css`, `layout.ts`, `ui.ts`, `topbar.ts`, `alerts.ts`, `telemetry.ts`, `cluster.ts`, `help.ts` | layout doc section 10 |
| Modes | Drive, Plan, Camera, Data (keys 1 to 4), chase view as an inset | `modes.ts` | layout doc section 11 |
| Waypoint planning (step 4) | waypoints with headings on a zoomable map, totals, solar heading, camera footprint, route chip, world markers | `plan.ts`, `planPanel.ts`, `routeView.ts`, `minimap.ts` | layout doc section 12 |
| Phones | portrait two-row bar and bottom sheet, landscape drawer, pinch and pan on the map | `ui.css`, `modes.ts`, `touch.ts`, `planPanel.ts` | layout doc section 13 |
| Signal delay and cruise (step 5) | delayed commands and view, predictive ghost, cruise at 1.25 km/h | `delay.ts`, `delayView.ts`, `topbar.ts`, `main.ts` | layout doc section 14 |

Commits in order: `c5a4833` research, `018187e` module split, `0d65792` limits, `4495476` and `df19308` hazard overlay, `1c01971` camera view, `8cbbaac` layout plan, `3cb5fd2` layout shell, `4f1907f` modes, `74ad417` planner, `b260475` phones, `94213c9` delay.

## The owner's decisions (do not reopen without asking)
- The goal stays the high-fidelity browser sim (`docs/sim-handoff.md`); hardware purchases remain deferred (`CLAUDE.md`).
- Interface layout, 2026-11-09: **four modes as drawn** (Drive, Plan, Camera, Data); **wordmark shrunk to the top bar's height**; **telemetry closed by default** (the chips and the cluster carry the glance); **the full key list only behind `?`**.
- The owner asked for drone-dashboard-style layout ("drone control dashboard concepts") and "one overall plan for what goes where"; the rule set is in `sim-ui-layout.md` section 3 (centre clear, a thin always-on layer, one home per kind of information, alerts only at yellow or red, UI under 25% of the screen).
- Pushes: the owner has said yes to each push so far; **commit locally and ask before pushing**.
- Facts are labelled: sourced, derived or ASSUMPTION; the interface docs list what was not checked. Keep doing that.

## How the code fits together

Frame loop (`main.ts`, `renderer.setAnimationLoop`), in order: read the controls (`input.ts`) and apply the cruise control; log them (`ControlLog`); advance the physics with the controls from one delay ago; record the real poses (`History`); pick the **shown** state (the real one, or the one from one delay ago when the delay is on) and put the model, the chase camera, the map and the route guidance on it; update the ghost; draw the chase view (full window, or into the inset's rectangle in Camera and Plan modes); draw the mast camera into the rectangle of its tile's picture box (hiding the operator overlays: hazard tint, route, ghost). Every 0.1 s: route guidance and the route chip, then `ui.update(...)`.

- **Regions** (`layout.ts`, `ui.css`): `#ui` is one overlay over the canvas with named regions (`top`, `left` dock, `right` column, `inset`, `cluster`, `alerts`, `sticks`, `modal`); parts mount into a region and stack, they never position themselves. Popovers hang under the top bar. `#ui` is `pointer-events: none`, panels `auto`.
- **`ui.ts`** reads the rover once per update, evaluates `limits.ts` once, and feeds the chips, the alerts, the cluster and the telemetry rows. The scripted checks read the telemetry from `#hud` (the dock, slid off the screen when closed, so it stays readable).
- **Modes** (`modes.ts`): a mode sets which tiles are shown or primary, the dock, and the inset; `layout()` runs every frame and sizes the inset and the main-view tiles (and the portrait class). The map and the camera each have `primary` and `shown` flags.
- **The picture is drawn into the canvas under a DOM box**: the camera view reads `getBoundingClientRect()` of its tile's picture box each frame; nothing in the DOM may cover that box (the camera tile's background is transparent for that reason, and there is no backdrop blur on panels).
- **Pure logic with node checks** (no DOM, no three): `limits.ts`, `freshness.ts`, `plan.ts`, `delay.ts`. Keep new logic in this style so it can be checked without a GPU.
- **Delay** (`delay.ts`, `main.ts`): `ControlLog` (commands by time), `History` (poses by time, quaternions interpolated), `predict()` (the drive model stepped through the commands of the next round trip). The model's figures are the sim's own (0.527 m/s, 100 degrees a second, duty slew 1.5 a second); slope, soil and rocks are not in it.

## How to run and check

- `cd sim && npm install && npm run dev` (port 5173; the owner often has their own dev server on it, which serves the current files: use it rather than starting a second one, which fails on the port with `--strictPort`). `npm run build` is `tsc --noEmit && vite build`.
- Node checks (no GPU, no browser): `npm run check:limits` (16 cases), `check:freshness` (17), `check:plan` (28), `check:delay` (19), and the older `check:soil`, `check:rocks`, `check:load`. All pass at `94213c9`.
- **Headless screenshots**: `node tests/cdp-shot.mjs out.png "query" [seconds] [width height]` prints the telemetry text and console errors; `tests/cdp-eval.mjs` (new) does the same after running a script in the page (`EVAL='...' EVALWAIT=1500`; the script can put a result in `document.title`, printed as `TITLE ...`). Use about 30 s for the load; `touch=1` with 844 x 390 (landscape) or 390 x 844 (portrait) for phones. Synthetic key events (`window.dispatchEvent(new KeyboardEvent('keydown', {code:'KeyH'}))`) and pointer events (`new PointerEvent(...)`, with `setPointerCapture` stubbed) work for scripted checks; the page exposes `__phys`, `__fx`, `__camview`, `__ui`, `__route`, `__map`, `__shown` and `rover`.
- **The headless browser runs the sim at about one frame a second** (software GL), so a driving test must be timed in wall-clock seconds, not frames; a small window and `res=0.4` help only a little.
- URL parameters (the interface's; the others are in `sim-spec.md`): `mode=drive|plan|camera|data`, `pip=0|1|2` (0 folds the camera tile, 2 starts in Camera mode), `mapmode=0|1|2`, `map=0`, `hazard=1`, `delay=<seconds one way>`, `stats=1` (opens the settings popover with frame statistics), `touch=1`, `fps=N`, `res=`, `maxpx=`, `autodrive=from,to`, `bench=1`, `flat=1`, `worker=0`, `still=1&cam=...`.
- Keys (also behind `?`): W S A D or arrows drive, Space brake, Q E pan, R F tilt, T upright, 1 to 4 modes, C camera mode, P still, [ ] roll, V live, M map size, H hazard, I telemetry, L performance log, Backspace undo waypoint (Plan), Z delay, X cruise, `?` help, Esc close.

## Things that bit (add to `sim-handoff.md`'s list)
- **`pkill -f` / `pgrep -f` with a pattern that appears in your own command line kills the shell** (it happened twice in this work; exit code 144). Find a PID by port with `ss -ltnp | grep :5173`, or use `[v]ite`.
- **A popover opened in the same turn as the toggle that triggers it did not paint in headless Chrome** (the DOM said open and topmost); the hazard legend now opens 100 ms later. Cause not found; a real browser may not need it.
- A synchronous `readPixels` or `readRenderTargetPixels` fails with INVALID_OPERATION if a pixel pack buffer is bound; the auto-exposure metering's asynchronous read leaves one bound (`MastCameraFx.snapshot` unbinds it). Reading the screen back with `readPixels` returned empty images; the stills are drawn offscreen instead.
- Inline `style.display` or `position` beats the stylesheet: elements the stylesheet must control (tile `position`, the roll strip's `display`) must not be given those inline.
- `canvas { width: 100%; height: 100% }` applied to every canvas, including the new small ones; it is now `canvas#c`.
- The tool output of `pdftotext`, `WebFetch` and long scripts is large: write results to the scratchpad and read the part you need.

## Not checked anywhere (the honest list)
No real GPU was ever used for any of the interface (headless software GL only). No real phone or touch screen. No real mouse wheel or right-drag. The predictor's accuracy against the real rover's path; the energy estimates; the thresholds (battery 30% and 15%, wall 100 m and 20 m, the hazard classes' 7.5 degrees and 5 cm) are look choices. The drone and NASA sources were read as search summaries except the VERVE paper, the VERVE slides, the Open MCT guide and the RSVP paper (read in full). Details per feature are in the "not checked" lines of each section of `sim-ui-layout.md`.

## Next steps (in the order of the plan, `sim-ui-research.md` section 8)
1. **Step 6: telemetry strips with a shared time window** (Data mode's bottom region, which is empty now). Scrolling plots of battery, motor current and tilt with the limit lines from `limits.ts`, under one pause-and-scrub window with a history of recent windows (Open MCT's time conductor); stacked plots with a common time axis. Needs a 10 Hz ring buffer of telemetry (`History` in `delay.ts` can hold it). **Load the `dataviz` skill before writing chart code.** Mind the layout rules: a new bottom region that stacks above the alerts and the sticks, and the 25% budget.
2. **Step 7: panel layout** (open, close, move the camera tile, the map and the strips; saved in `localStorage` inside try/catch; a readout converts to a plot). Do after 6 so there is something to arrange.
3. **Step 8: rehearse mode** (stretch): run the planned route through a fast preview and report errors (slope past 25 degrees from `Terrain.height`, the wall, battery below a floor) before executing, as RSVP's simulation did. Options: step the `predict()` model along the route with terrain checks, or run the real physics in the worker at accelerated time.
4. Smaller items found on the way: the hazard overlay on the minimap and in the Plan map; the hazard classes following the limits if they change at run time; thumbnails of the camera roll on phones; the chase camera's framing in portrait; the touch buttons for Z and X and the delay popover on a portrait phone; drag-to-dismiss for the bottom sheet; `?pip=0` uses a hack (`(cameraView as any).fold.click()`); orbit-dragging on the canvas while the chase view is only an inset; telemetry rows other than the pose-derived ones are live under delay; the plan's energy cost on slopes; the route is not saved between sessions.
5. Before any of this is called done: **try it on a real GPU, a real phone and a real mouse**, and write down what the headless runs could not show.

## How to start a session on this
Read `CLAUDE.md`, this file, then `docs/sim-ui-layout.md` sections 3 and 10 to 14. Run `git log --oneline | head`, `npm run check:limits` and the other three checks, and a headless screenshot of the default view to see that the tools work. Ask the owner before pushing.
