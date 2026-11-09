# Simulation hand-off (written 2026-11-08, laptop to the home server)

Read this first in a new session. `docs/sim-spec.md` is the specification and status; this file is the working state: what was decided, where the data is, how to run things, what to do next, and what went wrong before.
Also see the memory files (`simulation-goal`, `no-instrument-dummies`, `purchases-deferred`) in the Claude project memory.
**The interface** (top bar, modes, planner, delay, phone layouts) has its own hand-off since 2026-11-09: `docs/sim-ui-handoff.md`. Parts of the state below are older than that (for example the HUD it describes is gone).

## Goal and decisions (owner)
- **Goal (2026-11-08):** nothing can be bought or tested physically for the foreseeable future, so the current goal is a high-fidelity browser simulation of al-maha on the lunar surface that runs from GitHub (like PUTvision/LunarSim in spirit). Fidelity first, then optimisation, then phones.
- **Engine (assistant's choice, the owner deferred):** three.js + Rapier (WASM), Vite + TypeScript, GitHub Pages. CAD stays the source of truth (`hardware/sim/export_sim.py`).
- **No Rashid-only features** (instrument windows, Langmuir whips, flag plate): al-maha is Rashid-like, not Rashid.
- **Terrain layering (owner's idea):** a 5 x 5 km high-detail sandbox of real terrain; physics only on a patch (about 30 m) around the rover; beyond the sandbox only what is visible from it, as a low-detail ring from the whole-Moon map.
  The owner expects nobody to reach the edge (0.53 m/s gives about 80 minutes from the centre), but the edge still needs a soft boundary. Real data first, procedural detail on top.
- **Site criteria must be supported by the Rashid papers**, not invented (the owner's push, 2026-11-08). They are: Flahaut et al. 2024 (site selection) and Joulaud et al. 2024 (boulders, regolith), in `maha-rover-private/papers/`.
- **Purchases remain deferred.** Mast end plate: 40 x 40 x 6 aluminium plate with one countersunk M10 screw (owner's choice).

## State of the work (all committed and pushed to `main`)
- Phase 1 done: `hardware/sim/export_sim.py` writes `sim/public/rover.glb` and `rover.json` (9 rigid bodies, joints, masses, inertia frames, wheel grouser hulls, chassis hull). Visual layer: `hardware/sim/detail.py` (head and base detail) and T-slot profiles and materials in the exporter.
- Phase 2 done: `sim/src/physics.ts` (Rapier, differential coupling, 37D motor model with current cap, servo PD, duty slew limit), `sim/src/main.ts` (controls, HUD, `?test=1` scripted check, `?still=1&cam=...` for screenshots), `sim/src/lunar.ts` (lunar light, stars, flat procedural regolith ground). Findings are in `docs/sim-spec.md` (braking above about 1.1 m/s2 tips the rover; top speed 0.53 m/s).
- Terrain started (viewshed ring added 2026-11-09, see next steps): `hardware/sim/terrain/atlas_tile.py` (cuts the 5 x 5 km tile; `build-local` reads the full file), `hardware/sim/terrain/site_select.py` (scores windows by the paper's criteria), tile in `sim/public/terrain/atlas_5km.png` + `.json`
  (16 bit, 2 m posts, centre 47.5676 N, 44.8102 E, heights -3210 to -2877 m). **The tile is not yet used by the sim** (the sim still drives on the flat plane).
- Mass: replica 9.58 kg; CAD checks in `hardware/mast/mast.py` etc. as before.

## Data (NOT in git; copied by hand)
Put in `~/lunar-data/` on the server (and `~/Downloads` on the laptop). All files public domain per their archives' terms (LROC: https://lroc.im-ldi.com/about/terms, credit NASA/GSFC/Arizona State University; the LOLA archive's own terms were not read).
| file | bytes | sha256 |
|---|---|---|
| `NAC_DTM_ATLAS_E468N0446.IMG` (LROC Atlas crater DTM, 2 m posts, float32, 29426 x 10607, header 42428 bytes, three strips with a large empty north-west part) | 1248528756 | `ce1352aab6d8c2e7ec54fa372ea53244a528751e4a88788670934102082c0fef` |
| `ldem_128.img` (LOLA whole Moon, int16 LSB, 46080 x 23040, 237 m/px, height = DN x 0.5 m above the 1737.4 km sphere, column 0 = longitude 0 east positive) | 2123366400 | `0e4fea9b863e3255f58de15ccbd2bb8b1e248cb09217fd55d23ed37489f764b4` |
| `ldem_128.lbl` | 5133 | `85b1901def6901ee8a50415384f17a71e773af2d979beb7245fd6ac4d5e1671b` |
| `ldem_128.xml` | 11952 | `1bed6e7c269a3a811251f9f16417f31f76f5b7570b39af3b14f873771397b5f2` |
Private files not in any git history (copied into the clone of `maha-rover-private` on the server): `3d-files/UC-392(B0091).STEP`, `datasheets/B0091_CSI_to_HDMI.pdf`, `datasheets/lindy-hdmi-cable-slim-1m-datablad-1.pdf`.
Do not fetch these from the archives again: **the LROC archive's CDN rate-limited a burst of 2500 range requests (HTTP 429, retry-after 3600 s)**. Read the local files.

## How to run
- Python: `python3 -m venv .venv && .venv/bin/pip install -r requirements-lock.txt` (pinned from the laptop's Python 3.12; the pins resolve on 3.14).
- Terrain: `.venv/bin/python hardware/sim/terrain/site_select.py ~/lunar-data/NAC_DTM_ATLAS_E468N0446.IMG <cache dir>`; `.venv/bin/python hardware/sim/terrain/atlas_tile.py build-local ~/lunar-data/NAC_DTM_ATLAS_E468N0446.IMG sim/public/terrain`.
- Model export: `.venv/bin/python hardware/sim/export_sim.py` (about 30 s), then compress it: `cd sim && npx @gltf-transform/cli meshopt public/rover.glb public/rover.glb --level high` (2.1 MB to 0.38 MB; the page needs the meshopt decoder, already wired in `main.ts`). CAD checks: `.venv/bin/python hardware/mast/mast.py`, `hardware/mass/replica.py`, etc.
- Web app: `cd sim && npm install && npm run dev` (needs Node; see below). Scripted physics check: open `?test=1` and read `<pre id="test">`; screenshots with headless Chrome (`--headless=new --use-angle=swiftshader --enable-unsafe-swiftshader --virtual-time-budget=15000 --screenshot=out.png "http://127.0.0.1:5173/?still=1&cam=..."`; the laptop's binary is `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`).
- **Server notes:** Python 3.14.4 only; Node 22.22.1 and npm 9.2.0 (apt) and Google Chrome 157 (Google's .deb, `google-chrome`) were installed on 2026-11-09 with the owner's go-ahead; headless screenshots need `--no-sandbox` here; `npm install` rewrites `sim/package-lock.json` (drops `libc` fields): `git checkout` it; `claude` is at `~/.local/bin/claude`. Git over SSH works (gh logged in as the owner).

## Deployment
GitHub Pages (source: GitHub Actions, `sim-pages` workflow) was enabled by the owner on 2026-11-09 and serves https://jacob-rn-wallace.github.io/maha-rover/ . Before that every deploy failed with a 404 at `deploy-pages` (Pages was not enabled). The owner's report: the 1 to 2 fps seen on a MacBook Air M2 was with the local build; the deployed site "works perfectly" (no figures yet: `?stats=1` shows frame rate, pixel ratio, GPU name and main-thread time).

## Next steps, in order
1. **Viewshed: done 2026-11-09** (`hardware/sim/terrain/viewshed.py prep|run`, results and limits in `docs/sim-spec.md` under Terrain data; ring files in `sim/public/terrain/`). Not yet used by the sim: the ring mesh is built from `ring.png` and `ring_mask.png` as part of step 2. The prep cache is in `~/lunar-data/viewshed-cache/` (not in git; `prep` takes 15 s, `run` 3 min).
2. **Tile and ring in the sim: first version done 2026-11-09** (see `docs/sim-spec.md`, 'In the sim'). Done 2026-11-09: the tile-edge line (it was a step in the elevation model where the Atlas ends, and the ring poking through the tile mesh) and shadows beyond 2 m (precomputed for the fixed sun, `shadow.py`). Left: the stripe near the tile's east edge (check it is not the Atlas strip seam), a sun that can change (the shadow textures are for 14/40 degrees), soft boundary, craters, the texture ripples, load time (the tile is smoothed in the browser, about 1 s; the ring mesh takes a few seconds).
3. **Soil model: done 2026-11-09** (`docs/sim-spec.md`, 'Soil model'; `npm run check:soil`). Open: sinkage is not simulated (the HUD shows the paper's value for the slip), the Advance Simulation paper's MBRSC regolith parameters (friction angle 23 degrees) are recorded but unused: a `?soil=` switch for a softer soil would need a rewrite of the curve from them; FJS-1 is a simulant at 25% relative density.
4. **Rocks: done 2026-11-09** (`docs/sim-spec.md`, 'Rocks'; `npm run check:rocks`). The size law is Bandfield et al. 2011's (c = 0.082 d^-1.326) scaled to Joulaud's 144 per km2; the Diviner units question is unresolved in the papers (the agreement with Flahaut's 0.0029 as a fraction is recorded). Open: the stone population below 2 m is an extrapolation (too many small stones is likely), the density field is invented (the mapped boulder fields exist only as figures), motor stall protection (the rover tips on a wheel-high rock), rock shadows beyond 4 m.
5. **Mast camera view and telemetry: done 2026-11-09** (`docs/sim-spec.md`, 'Mast camera and telemetry'): PiP on C, FOV checked against the Raspberry Pi documentation, `power.ts` battery and solar model with assumed curve and resistance. Camera vignetting, noise, lens distortion and auto-exposure added later the same day (`cameraFx.ts`; the distortion and exposure numbers are assumptions). Open: no defocus, rolling shutter or compression, solar ignores shadows, no telemetry log or plot.
6. **Polish and optimise (in progress; done 2026-11-09: regolith texture weave, `?sun=el,az`, tilt guard, load-time check, touch sticks, minimap (M), slower mast (35 deg/s), brushed metal, physics worker, shadow-map size, see `docs/sim-spec.md` 'Polish round'):** metal textures (the export has no UVs), craters and dust, meshopt, instancing, shadows budget, physics in a worker, touch controls, phones.

## Things that bit before
- Rapier: no joint motor torque limit in 0.14, so actuators are explicit torques; `addTorque` persists until `resetTorques`; a wheel through a 131:1 gearbox needs the rotor's reflected inertia or the explicit torque loop chatters.
- glTF nodes: look all body nodes up before re-parenting them to the scene root, or the children vanish from the lookup.
- Rapier heightfield colliders: `nrows`/`ncols` are cells (the heights array has (n+1)^2 entries), rows run along z, columns along x, column-major; without `HeightFieldFlags.FIX_INTERNAL_EDGES` the rover's wheels catch on triangle edges and it wheelies on flat ground.
- Rapier contact impulses (`contactImpulse`) over-report by (n + 1) / n for n solver iterations (1.125 for 8): checked by summing wheel loads against the weight at rest. Rigid grousers on a rigid floor make the wheels hop and starve the soil model of load: with the soil model on, the grouser hulls do not collide with the ground.
- `pkill -f` or `pgrep -f` with a pattern that also appears in your own command line kills the shell (use `[v]ite`).
- Wheel grousers look like needles seen edge-on: not an artifact.
- Regenerating `sim/public/rover.glb` on another machine gives slightly different bytes: only the chassis mesh differs (118 of 29,476 triangles on the server, probably fillet tessellation), the masses, centres of mass and inertia agree to 0.01% and the collision hulls are identical. Commit a regenerated model only if the CAD changed.
- Site data: the Atlas DTM's valid area is irregular; a fully covered window must be checked, not assumed (the first tile was all missing values).
- `site_select.py` slopes come from stereo-matched 2 m posts averaged to 8 m: comparable to the paper's 7.4 m/px Kaguya slopes, not identical.

## Server verification (2026-11-08)
Clones at `~/maha-rover` (same commit as the laptop's `main`) and `~/maha-rover-private`; the private untracked files match the laptop's by checksum; venv built from `requirements-lock.txt` on Python 3.14; `hardware/mass/replica.py` reproduces the laptop's result (centre of mass x 23.2, z 234.6 mm, tip angles 34/26/47 degrees) and `export_sim.py` runs (total 9.579 kg).
