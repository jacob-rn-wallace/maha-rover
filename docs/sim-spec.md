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
  Body masses come from `hardware/mass/replica.py` (total 9.58 kg, as `docs/replica-mass.md`), the inertia from the meshes at uniform density.
- `sim/` is the web app: it loads the model on a placeholder plane and exercises every joint (pan, tilt, differential links, wheels).
- Axes: glTF Y up, metres; rover X forward stays X, rover Y (left) becomes -Z, rover Z (up) becomes Y.

## Visual layer (not in the CAD checks or the mass budget)
`hardware/sim/export_sim.py` and `hardware/sim/detail.py` add detail to the exported model only, so the CAD, its fit checks and the 9.58 kg estimate stay as they are:
- T-slot profiles (20 x 20, 20 x 40, 40 x 40: slots, diagonal webs, bore) in place of the plain extrusion boxes, with drilled holes kept; typical catalogue slot sizes, ASSUMPTION.
- Real-world materials by part (cast and sheet aluminium, anodised T-slot, black plastic, black cord, glossy dark cells, ASA wheels); the finishes are ASSUMPTIONS.
- Head and base: rounded vertical edges and a lid seam on the pan base box (seam 15 mm below the top, Takachi cover height) with four lid screws; a lid seam 10 mm behind the front face of the camera box (ASSUMPTION, not from the drawing); a PG7 hex gland with a domed cap nut; the lens with a grooved focus ring, front glass and retaining ring; two M5 bolts through the bracket web (positions ASSUMPTION).
- No Rashid-only features are added (owner, 2026-11-08).

## Lunar look (`sim/src/lunar.ts`, first version)
A low sun (14 degrees elevation, a parameter), hard shadows from a 4096 shadow map, a black sky with 4000 seeded stars, a reflection environment of black sky over sunlit regolith (so metals reflect the ground and not a room), and a flat
ground with procedural multi-scale regolith albedo and bump. Look-development values, not measurements: the albedo (about 0.12 to 0.2 effective) and the sun and exposure settings are choices. No craters, rocks or relief yet (phase 3's terrain), no earthshine, no dust.

## Phase 2: driving physics (done 2026-11-08, `sim/src/physics.ts`)
Rapier at 480 Hz fixed steps, lunar gravity 1.62 m/s2, flat ground. Nine rigid bodies from `rover.json`, with the CAD's mass, centre of mass and inertia tensor (mesh-derived, uniform density).
- **Differential:** the two link plates are separate revolute joints on the chassis, coupled by a stiff spring and damper so that angle L + angle R = 0 (k = 600 N.m/rad, c = 6 N.m.s/rad, tuned for critical damping of the sum mode; not gears, so friction and backlash are not modelled).
- **Drive:** each wheel has the Pololu 37D #4746 model from `docs/drive-spec.md`: R = 12 V / 5.5 A = 2.18 ohm, back-EMF constant 0.0111 V.s/rad from 76 rpm and 0.2 A no load, gearbox efficiency 0.75 (the value the datasheet's 0.59 N.m at 0.74 A implies), 7.4 V pack, current cap 1.6 A, shorted-terminal braking at zero duty. The motor rotor's inertia seen through the 131:1 gearbox (0.017 kg.m2, from an ASSUMED 1e-6 kg.m2 rotor) is added to each wheel.
- **Wheels:** collision shapes from the CAD mesh: a rim cylinder and 14 convex grouser hulls (plates thickened from 0.8 to 3 mm to stop tunnelling). Wheels collide with the ground only. Ground friction 0.8 and wheel 0.9 are placeholders until the soil model (phase 3).
- **Mast:** pan (limit +-160 degrees, the design's 320 degree stop) and tilt (+-90) servos as PD loops, torque capped at the STS3215's 1.91 N.m stall, target slewed at its 52 rpm no-load speed; gains are tuning choices. The mast and head have no collision shapes yet.
- **Chassis collision:** the convex hull of the fixed structure on a 6 mm grid.

Scripted check (`?test=1`, 7.4 V, flat ground, grouser tip radius 115 mm):
| test | result |
|---|---|
| parked 5 s | still: 0.001 m/s, motor currents under 0.03 A |
| full throttle 6 s | steady 0.53 m/s |
| brake from speed | stops in about 1 s, no tipping |
| full turn command | spins in place at 102 deg/s (clockwise for a right turn), about 35% wheel slip |
| mast pan and tilt | reach +160 and +90 degrees |

**What the first runs showed about the design:**
- **Speed:** 0.53 m/s at full duty, above `drive-spec.md`'s 0.49 m/s no-load figure, because that used the 100 mm rim radius and the wheel rolls on its 115 mm grouser tips on hard ground (derived: 47 rpm x 0.115 m x 2 pi = 0.566 m/s before slip). On soft soil the effective radius will be smaller.
- **Braking tips the rover:** it tips nose-over if it decelerates harder than about 0.68 x g = 1.1 m/s2 on the Moon (CAD centre of mass z 235 mm, x +23 mm, half wheelbase 136.5 mm; the threshold scales with g). With zero duty the 37D shorts its terminals and a full brake through the 1.6 A cap is about 5 m/s2; the first test flipped to pitch -100 degrees. The sim limits duty change to 1.5 per second (about 0.8 m/s2). The real motor controller firmware needs the same deceleration limit; this is a finding for the electronics, not only the sim.
- **Wheel spin and friction:** with the placeholder friction the rover can spin in place; the real soil may not allow it.

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
1. **Sim-ready design (done):** exporter, JSON, viewer scaffold, Pages workflow.
2. **Rover on flat ground (done, see above):** Rapier bodies and joints from the JSON, differential constraint, wheel motors, keyboard and gamepad driving, chase camera.
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
