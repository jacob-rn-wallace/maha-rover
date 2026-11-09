# Browser simulation of al-maha on the lunar surface

**Goal (owner, 2026-11-08):** nothing can be bought or physically tested for the foreseeable future, so the current goal is a
high-fidelity simulation of the rover on the lunar surface that anyone can run and drive in a browser from GitHub (in spirit
like PUTvision/LunarSim, which is a Unity and ROS 2 Linux binary; this one is a static web page). Fidelity first, then
optimisation, then phones (owner's order).

## Architecture (decided by the assistant, owner deferred the choice)
| Part | Choice | Why |
|---|---|---|
| Rendering | three.js (WebGL2) | mature, runs on GitHub Pages as a static site, glTF native |
| Physics | Rapier (WASM, `@dimforge/rapier3d-compat`) | deterministic, fast, revolute and prismatic joints, heightfield and trimesh colliders, runs in a worker later |
| Model | glTF binary exported from the build123d CAD | the CAD stays the single source of truth: `hardware/sim/export_sim.py` |
| Build | Vite + TypeScript, built by `.github/workflows/pages.yml` | repo Settings > Pages > Source "GitHub Actions" is the one manual step |
| Fidelity-critical models | written in TypeScript, unit-checked against the docs | wheel-soil contact, the differential, the motor, power, camera |

## What is in the repo now (phase 1)
- `hardware/sim/export_sim.py` splits the assembly (187 parts, 50.9k triangles) into 9 rigid bodies and writes
  `sim/public/rover.glb` (1.7 MB) and `sim/public/rover.json` (joints, masses, centres of mass, inertia, camera).
  Bodies: chassis; link plate L and R (each with its two motors and a differential side gear); four wheels; mast pan; camera head.
  Body masses come from `hardware/mass/replica.py` (total 9.554 kg, as `docs/replica-mass.md`), the inertia from the meshes at uniform density.
- `sim/` is the web app: it loads the model on a placeholder plane and exercises every joint (pan, tilt, differential links, wheels).
- Axes: glTF Y up, metres; rover X forward stays X, rover Y (left) becomes -Z, rover Z (up) becomes Y.

## Fidelity criteria (proposed; the owner has not confirmed them)
1. **Geometry:** the sim rover is the CAD, to the millimetre; wheels have their 14 grousers as real collision geometry.
2. **Mass:** per-body mass and centre of mass from `replica.py`; lunar gravity 1.62 m/s2.
3. **Mechanism:** the passive differential is simulated as the mechanism it is (links coupled, angle L = -angle R), not a rocker; skid steering emerges from four driven wheels.
4. **Drive:** each wheel driven by the Pololu 37D motor model (torque-speed line, 1.6 A current cap, gear ratio 131:1) from `docs/drive-spec.md`; the battery sag and power from `docs/power-spec.md`.
5. **Terrain:** procedural lunar surface (crater size-frequency distribution, rocks, regolith relief), real lunar lighting (sun at a low elevation, black sky, hard shadows, earthshine optional), regolith appearance; wheel-soil interaction through a simple Bekker-type sinkage and slip model, tuned to published lunar regolith values (cited when added).
6. **Mast and camera:** pan and tilt servos with speed and range limits; the HQ camera view (field of view, resolution, no auto-exposure tricks) shown as a picture-in-picture.
7. **Telemetry:** speed, wheel slip, link-plate angle, tilt, power draw, battery state, solar input.
8. **Validation:** static tip angles and the 20 degree slope climb from `replica.py` and `docs/suspension-spec.md` must reproduce in the sim.

## Phases
1. **Sim-ready design (done, this commit):** exporter, JSON, viewer scaffold, Pages workflow.
2. **Rover on flat ground:** Rapier bodies and joints from the JSON, differential constraint, wheel motors, keyboard and gamepad driving, chase camera.
3. **Terrain and lighting:** lunar sun, black sky, procedural terrain with craters and rocks, lunar gravity, soil model.
4. **Mast camera and telemetry:** pan-tilt control, camera PiP, HUD, power model.
5. **Publish:** GitHub Pages, README with controls.
6. **Optimise (later):** meshopt or Draco, instancing, LOD, shadow budget, a worker for physics, touch controls, phone profile.

## Open items and unverified
- The camera field of view (76.6 x 61.4 degrees) uses a sensor size remembered, not sourced: **unverified**.
- Pan range of the pan servo and servo speeds are assumptions.
- The wheel is a single solid mesh; its collision shape is the full mesh (grousers included); the cost of a trimesh wheel in Rapier is untested.
- The differential's internal friction and backlash are not modelled yet.
- Soil parameters (cohesion, friction angle, sinkage moduli) need sources before they are claimed as lunar.
- The camera-link cable is fixed to the chassis in the model; it does not follow the pan yet.
- Physics inertia is mesh-derived at uniform density, so heavy small parts (motors, battery) are only right in the total mass and centre of mass.
