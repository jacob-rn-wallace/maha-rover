# Simulation hand-off (written 2026-11-08, laptop to the home server)

Read this first in a new session. `docs/sim-spec.md` is the specification and status; this file is the working state: what was decided, where the data is, how to run things, what to do next, and what went wrong before.
Also see the memory files (`simulation-goal`, `no-instrument-dummies`, `purchases-deferred`) in the Claude project memory.

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
- Terrain started: `hardware/sim/terrain/atlas_tile.py` (cuts the 5 x 5 km tile; `build-local` reads the full file), `hardware/sim/terrain/site_select.py` (scores windows by the paper's criteria), tile in `sim/public/terrain/atlas_5km.png` + `.json`
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
- Model export: `.venv/bin/python hardware/sim/export_sim.py` (about 30 s). CAD checks: `.venv/bin/python hardware/mast/mast.py`, `hardware/mass/replica.py`, etc.
- Web app: `cd sim && npm install && npm run dev` (needs Node; see below). Scripted physics check: open `?test=1` and read `<pre id="test">`; screenshots with headless Chrome (`--use-angle=swiftshader --enable-unsafe-swiftshader --virtual-time-budget=...`, macOS path in `docs`-less notes: `/Applications/Google Chrome.app/...`).
- **Server notes:** Python 3.14.4 only; Node was not installed (not set up on 2026-11-08: needs the owner's go-ahead); no Chrome found; `claude` is at `~/.local/bin/claude`. Git over SSH works (gh logged in as the owner).

## Next steps, in order
1. **Viewshed (the owner's plan):** from points on the sandbox's edge (and a few inside), at camera height 0.7 m and with lunar curvature (R 1737.4 km), find which terrain beyond the tile is visible; use the Atlas 2 m data where it has coverage (it extends well past 5 km in the strips), the LDEM_128 map for the rest; keep only the visible part as the ring.
2. **Use the tile in the sim:** heightfield collider and visual mesh (patch of about 30 m around the rover, rebuilt as it moves), smoothing of the stereo stripes (note a thin vertical stripe near the tile's east edge), procedural fine detail seeded by position (deterministic), curvature, edge boundary.
3. **Soil model:** read `Advance_Simulation_Method_for_Wheel-Terrain_Interactions_of_Space_Rovers_A_Case_Study_on_the_UAE_Rashid_Rover.pdf` and `Traction_Performance_Evaluation_for_a_Rashid-1_Rover_Wheel.pdf` (private papers) for Bekker-type parameters; cite them; replace the placeholder friction (ground 0.8, wheel 0.9).
4. **Rocks:** Atlas ellipse FR-11: 144 boulders per km2 mapped (Joulaud 2024); the size distribution and smallest mapped size were not found in the pages read (find them, or a published lunar rock size-frequency law, and cite). The two papers disagree on Diviner rock abundance units (0.029% vs 0.0029): check.
5. **Mast camera view and telemetry (phase 4);** camera FOV figure (76.6 x 61.4 degrees) is from a remembered sensor size: unverified.
6. **Polish and optimise (later):** metal textures (the export has no UVs), craters and dust, meshopt, instancing, shadows budget, physics in a worker, touch controls, phones.

## Things that bit before
- Rapier: no joint motor torque limit in 0.14, so actuators are explicit torques; `addTorque` persists until `resetTorques`; a wheel through a 131:1 gearbox needs the rotor's reflected inertia or the explicit torque loop chatters.
- glTF nodes: look all body nodes up before re-parenting them to the scene root, or the children vanish from the lookup.
- Wheel grousers look like needles seen edge-on: not an artifact.
- Site data: the Atlas DTM's valid area is irregular; a fully covered window must be checked, not assumed (the first tile was all missing values).
- `site_select.py` slopes come from stereo-matched 2 m posts averaged to 8 m: comparable to the paper's 7.4 m/px Kaguya slopes, not identical.
