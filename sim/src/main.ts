import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";
import { addLunarScene } from "./lunar";
import { Terrain } from "./terrain";
import { FJS1 } from "./soil";
import { RockField } from "./rocks";
import { loadTerrainShadow, applyTerrainShadow, computeTerrainShadow } from "./terrainShadow";
import { TerrainView } from "./terrainView";
import { applyRegolithPhotometry } from "./regolith";
import { MastCameraFx } from "./cameraFx";
import { WHEELS } from "./constants";
import { UI } from "./ui";
import { Modes, MODES, type Mode } from "./modes";
import { Route, type Pose } from "./plan";
import { PlanPanel } from "./planPanel";
import { RouteView } from "./routeView";
import { ControlLog, History, predict, CRUISE_THROTTLE, MOON_ONE_WAY_S } from "./delay";
import { DelayView } from "./delayView";
import { bearingDeg } from "./freshness";
import { HazardOverlay } from "./hazard";
import { CameraView } from "./cameraView";
import { PerfPanel } from "./perfPanel";
import { setupInput } from "./input";
import { applyMetalDetail } from "./metal";
import { Cable } from "./cable";
import { Minimap } from "./minimap";
import { PerfLog } from "./perfLog";
import { Power } from "./power";
import { PhysicsProxy, type PhysicsView } from "./physicsProxy";
import type { RoverPhysics, Spec, Controls } from "./physics";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

const canvas = document.getElementById("c") as HTMLCanvasElement;
// ?depth=reverse: a reversed floating-point depth buffer instead of the logarithmic one, if the browser offers EXT_clip_control (the logarithmic buffer writes depth in every fragment shader, which switches off early-z
// rejection and is slow on tile-based GPUs such as Apple's). Experimental in three r170 and not testable here (no GPU): opt in, compare with ?stats=1, report.
const wantReverse = new URLSearchParams(location.search).get("depth") === "reverse" && !!document.createElement("canvas").getContext("webgl2")?.getExtension("EXT_clip_control");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: devicePixelRatio < 1.75, logarithmicDepthBuffer: !wantReverse, reverseDepthBuffer: wantReverse, powerPreference: "high-performance" });      // MSAA only on low-DPR screens: a retina screen is sharp enough without it, and it is the larger share of the fill cost   // terrain from 5 cm to 74 km
const coarse = matchMedia("(pointer: coarse)").matches || new URLSearchParams(location.search).get("touch") === "1";      // phone or tablet: lighter rendering, touch sticks
const hazard = new HazardOverlay(coarse);      // H toggles it; ?hazard=1 starts it on
const handlers = { toggleLog: () => {}, setMode: (_m: Mode) => {}, setDelay: (_s: number) => {}, toggleCruise: () => {} };      // set once the performance log and the modes exist
const ui: UI = new UI(coarse, hazard, { toggleHazard: () => hazard.toggle(), toggleHelp: () => ui.help.toggle(), toggleLog: () => handlers.toggleLog(), setMode: (m) => handlers.setMode(m), setDelay: (s) => handlers.setDelay(s), toggleCruise: () => handlers.toggleCruise() });
(window as any).__ui = ui;      // for scripted checks
// The drawing buffer is capped in total pixels (default 1 million, about 1280 x 780; ?maxpx=megapixels, e.g. 2.1 for a 1080p frame), whatever the window or monitor: on a 4K screen the canvas is drawn at that size and scaled up by the browser
// (a 4K frame is four times the shading of a 1080p one). The cap follows the window and the screen it is on (devicePixelRatio changes when the window moves between monitors).
const maxPixels = (Number(new URLSearchParams(location.search).get("maxpx")) || 1) * 1e6;
const ratioCap = () => Math.min(devicePixelRatio, coarse ? 1.25 : 1.5, Math.sqrt(maxPixels / Math.max(1, canvas.clientWidth * canvas.clientHeight)));
let maxRatio = ratioCap();
let ratio = maxRatio;                                     // adaptive: lowered while frames take longer than FRAME_BUDGET, raised again when there is room (?res=1 fixes it at 1, ?res=auto is the default)
renderer.setPixelRatio(ratio);
const fixedRes = new URLSearchParams(location.search).get("res");
if (fixedRes && fixedRes !== "auto") { ratio = Number(fixedRes); renderer.setPixelRatio(ratio); }
const FRAME_BUDGET = 1 / 55;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.85;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 200000);
camera.position.set(0.9, 0.6, 0.9);
const controls = new OrbitControls(camera, canvas);
controls.target.set(0.1, 0.3, 0);

const sunParam = new URLSearchParams(location.search).get("sun")?.split(",").map(Number);      // ?sun=elevation,azimuth (degrees; azimuth counterclockwise from east, 90 = north): another sun, its terrain shadows computed at load
const lunar = addLunarScene(scene, renderer, sunParam && sunParam.length === 2 && sunParam.every(isFinite) ? { sunElevationDeg: sunParam[0], sunAzimuthDeg: sunParam[1] } : undefined);
const ground = lunar.ground;

addEventListener("error", (e) => { ui.alerts.status("error: " + e.message, 2); });
async function main() {
  const [gltf, spec] = await Promise.all([
    new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).loadAsync("rover.glb"),
    fetch("rover.json").then((r) => r.json() as Promise<Spec>),
  ]);
  gltf.scene.traverse((o) => { if ((o as THREE.Mesh).isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  gltf.scene.traverse((o) => { const m = (o as THREE.Mesh).material; if (m) for (const x of Array.isArray(m) ? m : [m]) applyMetalDetail(x); });
  scene.add(gltf.scene);
  const names = Object.keys(spec.bodies);
  const nodes: Record<string, THREE.Object3D> = Object.fromEntries(names.map((n) => [n, gltf.scene.getObjectByName(n)!]));   // look all up before re-parenting
  // each body gets a pivot at its physics origin that the physics drives; the glTF node hangs under it with whatever local transform the file gave it (the original file's nodes sat at the body
  // origin, but a meshopt-compressed file puts a position offset and a scale on the node to undo the vertex quantisation, which setting the node's position from the physics would have overwritten)
  gltf.scene.updateMatrixWorld(true);
  const pivots: Record<string, THREE.Group> = {};
  for (const n of names) { const p = new THREE.Group(); p.position.set(...(spec.bodies[n].origin_m as [number, number, number])); scene.add(p); p.updateMatrixWorld(true); pivots[n] = p; }
  for (const n of names) pivots[n].attach(nodes[n]);
  const node = (n: string) => pivots[n];
  const cable = spec.cable ? new Cable(spec.cable, pivots) : null;
  if (cable) scene.add(cable.mesh);
  (window as any).rover = { node, spec };

  const q = new URLSearchParams(location.search);
  hazard.apply(lunar.groundMaterial, "ground");
  if (q.get("hazard") === "1") hazard.set(true);
  // terrain: the real lunar tile and ring (default); ?flat=1 keeps the flat plane, which the scripted ?test=1 check assumes (add ?terrain=1 to run it on the terrain)
  const flat = q.get("flat") === "1" || (q.get("test") === "1" && q.get("terrain") !== "1");
  let terrain: Terrain | undefined, view: TerrainView | undefined, rockField: RockField | undefined;
  const spawn = new THREE.Vector3();
  if (!flat) {
    ui.alerts.status("loading terrain...");
    const tl = performance.now();
    terrain = await Terrain.load("terrain/", { smoothPosts: q.has("smooth") ? Number(q.get("smooth")) : undefined, detail: q.has("detail") ? Number(q.get("detail")) : undefined });   // ?smooth=posts, ?detail=scale: tuning
    console.log("load: terrain", (performance.now() - tl).toFixed(0), "ms");
    spawn.set(terrain.spawn.x, terrain.spawn.y, terrain.spawn.z);
    scene.remove(ground);
    view = new TerrainView(terrain, lunar.groundMaterial);
    scene.add(view.group);
    view.update(spawn.x, spawn.z);
    let ts = await loadTerrainShadow();
    if (ts.sunElevationDeg !== lunar.sunElevationDeg || ts.sunAzimuthDeg !== lunar.sunAzimuthDeg) {
      ui.alerts.status("computing terrain shadows for the sun...");
      await new Promise((r) => setTimeout(r));
      const t0 = performance.now();
      ts = computeTerrainShadow(terrain, lunar.sunElevationDeg, lunar.sunAzimuthDeg);
      console.log("terrain shadows computed in", ((performance.now() - t0) / 1000).toFixed(1), "s");
    }
    if (ts.sunElevationDeg === lunar.sunElevationDeg && ts.sunAzimuthDeg === lunar.sunAzimuthDeg) {
      applyTerrainShadow(lunar.groundMaterial, ts);
      if (cable) applyTerrainShadow(cable.mesh.material as THREE.Material, ts);
      for (const n of names) nodes[n].traverse((o) => { const m = (o as THREE.Mesh).material; if (m) for (const x of Array.isArray(m) ? m : [m]) applyTerrainShadow(x, ts); });
    } else console.warn("terrain shadow textures are for another sun: not applied (run hardware/sim/terrain/shadow.py)");
    let rocks: RockField | undefined;
    if (q.get("rocks") !== "0") {
      const rockMat = new THREE.MeshStandardMaterial({ color: new THREE.Color(0.24, 0.23, 0.22), roughness: 1, metalness: 0 });
      applyRegolithPhotometry(rockMat);
      hazard.apply(rockMat, "rock");
      if (ts.sunElevationDeg === lunar.sunElevationDeg && ts.sunAzimuthDeg === lunar.sunAzimuthDeg) applyTerrainShadow(rockMat, ts);
      rocks = new RockField(terrain, rockMat, terrain.spawn);
      terrain.rocks = rocks;
      scene.add(rocks.group);
      rocks.update(terrain.spawn.x, terrain.spawn.z);
    }
    rockField = rocks;
    view.addRing().then((r) => { console.log("ring mesh", r.triangles, "triangles, at", performance.now().toFixed(0), "ms"); for (const k of (q.get("hide") ?? "").split(",").filter(Boolean)) view!.group.children.forEach((c, n) => { if (n === Number(k) || (Number(k) === 4 && n >= 4)) c.visible = false; }); });   // ?hide=0,1,2,3,4: hide a terrain level (0 finest to 3) or 4 the ring, for finding seams
    for (const n of names) node(n).position.add(spawn);       // the rover model starts at the spawn point
    camera.position.add(spawn); controls.target.add(spawn);
  }
  if (q.get("cam")) {                      // ?cam=x,y,z,tx,ty,tz&still=1: fixed view for screenshots (metres, glTF axes, relative to the spawn point on the terrain); still=1 also pauses the physics
    const v = q.get("cam")!.split(",").map(Number);
    camera.position.set(v[0] + spawn.x, v[1] + spawn.y, v[2] + spawn.z);
    controls.target.set(v[3] + spawn.x, v[4] + spawn.y, v[5] + spawn.z);
  }
  const still = q.get("still") === "1";
  lunar.followSun(spawn);
  if (still) { ui.alerts.status(`model loaded: ${names.length} bodies, ${spec.total_mass_kg.toFixed(2)} kg`); renderer.setAnimationLoop(() => { resize(); controls.update(); renderer.render(scene, camera); }); return; }

  const soil = q.get("soil") === "0" || (flat && q.get("soil") !== "1") ? undefined : FJS1;     // ?soil=0 Coulomb friction instead; ?soil=1 with ?flat=1 or ?test=1
  // the physics runs in a worker (its own copy of the terrain) unless ?worker=0, in the scripted test, or without the terrain
  const useWorker = q.get("worker") !== "0" && q.get("test") !== "1" && typeof Worker !== "undefined";
  let phys: PhysicsView;
  if (useWorker) {
    ui.alerts.status("starting physics...");
    phys = await PhysicsProxy.create(spec, { spawnHeight: 0.03, terrainBase: terrain ? new URL("terrain/", location.href).href : undefined,
      terrainOpts: { smoothPosts: q.has("smooth") ? Number(q.get("smooth")) : undefined, detail: q.has("detail") ? Number(q.get("detail")) : undefined }, rocks: !!terrain && q.get("rocks") !== "0", soil: !!soil, mastRateDeg: q.has("mastrate") ? Number(q.get("mastrate")) : undefined });
  } else {
    const { RoverPhysics: RP } = await import("./physics");      // loaded only here: it carries Rapier and its WASM
    const direct = await RP.create(spec, 0.03, terrain, soil);
    if (q.get("test") === "1") { runTest(direct); return; }
    if (q.has("mastrate")) direct.mastRate = Number(q.get("mastrate")) * Math.PI / 180;
    phys = direct;
  }
  (window as any).__phys = phys;      // for scripted checks (tests/cdp-shot.mjs)
  const camFx = new MastCameraFx(renderer, 640, 480, q.has("vignette") ? Number(q.get("vignette")) : 0.6, q.get("noise") === "0" ? 0 : 1, q.has("distort") ? Number(q.get("distort")) : 1, q.get("ae") !== "0");      // ?vignette=0..1, ?noise=0, ?distort=0..., ?ae=0
  (window as any).__fx = camFx;
  const power = new Power();
  const el = THREE.MathUtils.degToRad(lunar.sunElevationDeg), az = THREE.MathUtils.degToRad(lunar.sunAzimuthDeg);
  const sunDir = new THREE.Vector3(Math.cos(el) * Math.cos(az), Math.sin(el), -Math.cos(el) * Math.sin(az));
  const chassisQ = new THREE.Quaternion();
  const roverPose = { x: 0, z: 0, quat: new THREE.Quaternion(), pan: 0, tilt: 0 };
  const minimap = terrain && q.get("map") !== "0" ? new Minimap(terrain, lunar.sunElevationDeg, lunar.sunAzimuthDeg, coarse, ui.layout.right) : undefined;      // M cycles it; ?map=0 leaves it out
  if (minimap && q.has("mapmode")) { minimap.mode = Number(q.get("mapmode")); minimap.layout(); }
  const cameraView = new CameraView(camFx, spec.camera.position_m as [number, number, number], coarse, { bearingDeg: (90 - lunar.sunAzimuthDeg + 360) % 360, elevationDeg: lunar.sunElevationDeg }, ui.layout.right);      // the sun's azimuth is counterclockwise from east: bearing = 90 - azimuth
  (window as any).__camview = cameraView;      // for scripted checks
  // the route: waypoints placed on the map in Plan mode (drag to set the heading), shown on the map and in the world, followed with the usual controls
  const sun = { bearingDeg: (90 - lunar.sunAzimuthDeg + 360) % 360, elevationDeg: lunar.sunElevationDeg };
  const route = new Route();
  const routeView = new RouteView(scene, route, (x, z) => (terrain ? terrain.height(x, z) : 0));
  let modes: Modes;
  const plan = minimap ? new PlanPanel(ui.layout, route, minimap, sun, () => modes.mode === "plan") : undefined;
  modes = new Modes(ui, cameraView, minimap, coarse, plan?.box);
  handlers.setMode = (m) => modes.set(m);
  modes.onEnter = (m) => { if (m === "plan") plan?.centre(); };
  (window as any).__route = route;      // for scripted checks
  (window as any).__map = minimap;
  if (q.has("pip")) { const v = Number(q.get("pip")); if (v === 2) modes.set("camera"); else if (v === 0) (cameraView as any).fold.click(); }      // ?pip=0|1|2: camera tile folded away, small, as the main view at the start
  if (MODES.some((m) => m.id === q.get("mode"))) modes.set(q.get("mode") as Mode);      // ?mode=drive|plan|camera|data
  const fwd = new THREE.Vector3();
  const chase = new THREE.Vector3(spawn.x, spawn.y + 0.25, spawn.z);
  const gl = renderer.getContext(), dbg = gl.getExtension("WEBGL_debug_renderer_info"), gpuName = dbg ? String(gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL)) : "unknown GPU";
  // performance log: L records, L again stops and offers the file; ?bench=1 runs the scripted benchmark and offers the file at the end
  const perf = new PerfLog(() => ({
    build: __BUILD__, url: location.href, userAgent: navigator.userAgent, gpu: gpuName, devicePixelRatio, screen: `${screen.width}x${screen.height}`, window: `${innerWidth}x${innerHeight}`,
    canvas: `${canvas.width}x${canvas.height}`, maxPixelsM: maxPixels / 1e6, cores: navigator.hardwareConcurrency, deviceMemoryGB: (navigator as any).deviceMemory ?? null, physicsInWorker: useWorker, refreshHz: +(1000 / refreshMsRef.v).toFixed(1), fpsCap: q.has("fps") ? Number(q.get("fps")) : 60,
  }));
  const panel = new PerfPanel(ui.layout);
  const finish = (stopSkip: number, name: string) => {
    const data = perf.stop(stopSkip); (data.summary as any).snapshotUnderrunPct = +(100 * ((phys as any).underruns ?? 0) / Math.max(1, (phys as any).frames ?? 1)).toFixed(1); (data.meta as any).refreshHzAtEnd = +(1000 / refreshMsRef.v).toFixed(1); (data.meta as any).canvasAtEnd = `${canvas.width}x${canvas.height}`; (window as any).__perfData = data;
    panel.show(name, data, canvas.width, canvas.height);
    return data;
  };
  const toggleLog = () => { if (perf.recording) { finish(0, "Recording"); } else { panel.hide(); perf.start("manual", { search: location.search }); } };
  handlers.toggleLog = toggleLog;
  // signal delay: the commands reach the rover delayS late and the operator sees the rover's state delayS old (the pose history below); a ghost shows where it will be when a command issued now arrives
  let delayS = 0, cruise = false;
  const ctlLog = new ControlLog(), nB = names.length, W = 7 * nB + 5, hist = new History(W, names.map((_, i) => 7 * i + 3)), hvals = new Float64Array(W), hbuf = new Float64Array(W), ci = names.indexOf("chassis");
  const sc = { t: { x: 0, y: 0, z: 0 }, r: { x: 0, y: 0, z: 0, w: 1 }, v: { x: 0, y: 0, z: 0 }, translation() { return this.t; }, rotation() { return this.r; }, linvel() { return this.v; } };      // the chassis as the operator sees it
  const shownQ = new THREE.Quaternion(); let shownPan = 0, shownTilt = 0;
  const delayView = new DelayView(scene, (x, z) => (terrain ? terrain.height(x, z) : 0));
  minimap?.overlays.push((g) => delayView.drawOverlay(minimap, g));
  handlers.setDelay = (v) => { delayS = Math.max(0, Math.min(5, v)); ui.bar.setDelay(delayS); cameraView.roll.delayS = delayS; };
  handlers.toggleCruise = () => { cruise = !cruise; ui.bar.setCruise(cruise); };
  ui.bar.setDelay(0); if (q.has("delay")) handlers.setDelay(Number(q.get("delay")));
  const input = setupInput(coarse, ui.layout.sticks, { upright: () => { if (delayS > 0) setTimeout(() => { resetRequested = true; }, delayS * 1000); else resetRequested = true; }, toggleDelay: () => handlers.setDelay(delayS > 0 ? 0 : MOON_ONE_WAY_S), toggleCruise: () => handlers.toggleCruise(), toggleCamera: () => modes.toggleCamera(), setMode: (i) => modes.set(MODES[i - 1].id), cycleMap: () => minimap?.cycle(), toggleLog, toggleHazard: () => hazard.toggle(), toggleTelemetry: () => ui.tele.toggle(), toggleHelp: () => ui.help.toggle(), undoWaypoint: () => { if (modes.mode === "plan") route.undo(); }, closeAll: () => { ui.help.close(); }, snap: () => cameraView.snap(), stepRoll: (d) => cameraView.roll.step(d), live: () => cameraView.roll.live() }, () => (benchT !== null ? benchControls(benchT) : null));
  let benchStart = 0;
  if (bench) { benchStart = performance.now(); benchT = 0; perf.start("benchmark", { search: location.search, seconds: BENCH_SECONDS, warmupSeconds: BENCH_WARMUP, adaptive: q.get("adapt") === "1" }); }
  let last = performance.now(), hudT = 0, mapT = 1, fpsEma = 60, frameEma = 1 / 60, resNote = 0, drawCalls = 0, drawTris = 0;
  let jsMs = 0;
  const showStats = q.get("stats") === "1" || bench;      // ?stats=1: frame rate and draw load of the main view, in the settings popover (opened at the start)
  if (showStats) ui.layout.togglePop("settings", true);
  // Frame pacing: on a display faster than the cap (a 120 Hz MacBook screen) only every Nth animation frame is drawn, N = round(cap interval / refresh interval), so the frames come at an even 60 Hz.
  // Drawing every frame at 120 Hz, with the camera view's extra scene pass on every third, gave frame times alternating 8 and 17 ms: judder although the mean was 90 fps (the owner's log, 2026-11-09).
  // ?fps=N sets the cap (default 60, 0 = draw every frame).
  const fpsCap = q.has("fps") ? Number(q.get("fps")) : 60;
  let rafLast = 0, skip = 0;
  refreshMsRef.v = 1000 / 60;
  ui.alerts.status(null);
  renderer.setAnimationLoop((now) => {
    if (rafLast) { const d = now - rafLast; if (d > 2 && d < 60) refreshMsRef.v += (d - refreshMsRef.v) * 0.05; }
    rafLast = now;
    if (fpsCap > 0) { const step = Math.max(1, Math.round(1000 / fpsCap / refreshMsRef.v)); if (++skip < step) return; skip = 0; }
    const jsStart = performance.now();
    const dt = (now - last) / 1000; last = now;
    const tNow = performance.now() / 1000;
    let user = input.read();
    if (cruise && (user.throttle < 0 || user.brake)) { cruise = false; ui.bar.setCruise(false); }      // S or the brake cancels the cruise control
    if (cruise && user.throttle === 0) user = { ...user, throttle: CRUISE_THROTTLE };
    ctlLog.push(tNow, user);
    if (resetRequested) { resetRequested = false; phys.resetUpright(); }
    phys.advance(dt, delayS > 0 ? ctlLog.at(tNow - delayS) : user);
    { const r = phys.bodies.chassis.rotation(); chassisQ.set(r.x, r.y, r.z, r.w); power.step(Math.min(dt, 0.1), phys.motorPackAmps, phys.servoMoving, sunDir, chassisQ); }
    for (let i = 0; i < nB; i++) { const b = phys.bodies[names[i]], t = b.translation(), r = b.rotation(); hvals.set([t.x, t.y, t.z, r.x, r.y, r.z, r.w], 7 * i); }
    { const v = phys.bodies.chassis.linvel(); hvals.set([v.x, v.y, v.z, phys.panAngle, phys.tiltAngle], 7 * nB); }
    hist.push(tNow, hvals);
    const src = delayS > 0 && hist.sample(tNow - delayS, hbuf) ? hbuf : hvals;      // what the operator sees: the state delayS ago
    for (let i = 0; i < nB; i++) { node(names[i]).position.set(src[7 * i], src[7 * i + 1], src[7 * i + 2]); node(names[i]).quaternion.set(src[7 * i + 3], src[7 * i + 4], src[7 * i + 5], src[7 * i + 6]); }
    sc.t.x = src[7 * ci]; sc.t.y = src[7 * ci + 1]; sc.t.z = src[7 * ci + 2]; sc.r.x = src[7 * ci + 3]; sc.r.y = src[7 * ci + 4]; sc.r.z = src[7 * ci + 5]; sc.r.w = src[7 * ci + 6]; sc.v.x = src[7 * nB]; sc.v.y = src[7 * nB + 1]; sc.v.z = src[7 * nB + 2];
    shownPan = src[7 * nB + 3]; shownTilt = src[7 * nB + 4];
    (window as any).__shown = { real: hvals[7 * ci], shown: src[7 * ci], delay: delayS };      // for scripted checks
    cable?.update(dt);
    const c = delayS > 0 ? sc : phys.bodies.chassis, ct = c.translation();
    { const r = c.rotation(); shownQ.set(r.x, r.y, r.z, r.w); }
    if (delayS > 0) { fwd.set(1, 0, 0).applyQuaternion(shownQ); const v = c.linvel(); const p = predict({ x: ct.x, z: ct.z, headingDeg: bearingDeg(fwd.x, -fwd.z) }, v.x * fwd.x + v.y * fwd.y + v.z * fwd.z, ctlLog, tNow, delayS); delayView.update(p.distance > 0.04 ? p : null); }      // the ghost is shown only while the rover is predicted to move else delayView.update(null);
    const delta = new THREE.Vector3(ct.x, ct.y + 0.25, ct.z).sub(chase);
    chase.add(delta); camera.position.add(delta); controls.target.copy(chase);
    lunar.followSun(new THREE.Vector3(ct.x, ct.y, ct.z));
    mapT += dt;
    if (minimap && mapT > 0.1) { mapT = 0; fwd.set(1, 0, 0).applyQuaternion(shownQ); minimap.update(ct.x, ct.z, fwd.x, fwd.z); }
    hazard.update(ct.x, ct.z);
    view?.update(ct.x, ct.z);
    rockField?.update(ct.x, ct.z);
    hudT += dt;
    (window as any).__frames = ((window as any).__frames ?? 0) + 1;
    fpsEma += (1 / Math.max(dt, 1e-3) - fpsEma) * 0.05;
    if ((!fixedRes || fixedRes === "auto") && !(bench && q.get("adapt") !== "1")) {
      maxRatio = ratioCap(); if (ratio > maxRatio) { ratio = maxRatio; renderer.setPixelRatio(ratio); }
      // adaptive resolution: a slow frame (a smoothed 1 / fps below 50) steps the pixel ratio down, a long run of fast frames steps it back up
      frameEma += (dt - frameEma) * 0.1; resNote++;
      if (resNote > 20) {
        if (frameEma > FRAME_BUDGET * 1.15 && ratio > 0.5) { ratio = Math.max(0.5, ratio * 0.85); renderer.setPixelRatio(ratio); resNote = 0; }
        else if (frameEma < FRAME_BUDGET * 0.75 && ratio < maxRatio && resNote > 120) { ratio = Math.min(maxRatio, ratio * 1.1); renderer.setPixelRatio(ratio); resNote = 0; }
      }
    }
    if (hudT > 0.1) {      // the route: guidance to the next waypoint (the top-bar chip), the world markers and the panel
      fwd.set(1, 0, 0).applyQuaternion(shownQ); const pose: Pose = { x: ct.x, z: ct.z, headingDeg: bearingDeg(fwd.x, -fwd.z) }, g = route.guide(pose);
      ui.bar.set("route", g ? `wp ${g.index + 1}/${g.count} · ${g.distance.toFixed(0)} m · ${Math.abs(g.turn) < 3 ? "ahead" : (g.turn > 0 ? "right " : "left ") + Math.abs(g.turn).toFixed(0) + "°"}` : null, "route");
      routeView.update(pose); plan?.update(pose);
    }
    if (hudT > 0.1) { hudT = 0; ui.update({ phys, chassis: c, power, terrain, recording: { on: perf.recording, seconds: perf.seconds, benchOf: benchT !== null ? BENCH_SECONDS : undefined }, stats: showStats ? `${gpuName}\nmain thread ${jsMs.toFixed(1)} ms/frame, ${fpsEma.toFixed(0)} fps, pixel ratio ${ratio.toFixed(2)} (${canvas.width} x ${canvas.height}), ${drawCalls} draw calls, ${(drawTris / 1e6).toFixed(2)} M triangles` : `${gpuName}\nopen with ?stats=1 for frame statistics` }); }
    resize();
    controls.update();
    const vw = canvas.clientWidth, vh = canvas.clientHeight;
    modes.layout(vw, vh);
    const cr = modes.chaseRect(vh);
    renderer.setScissorTest(false);
    if (!cr) { renderer.setViewport(0, 0, vw, vh); renderer.render(scene, camera); }
    else {      // the chase view as an inset (Camera and Plan modes): the rest of the window is cleared
      renderer.clear(); renderer.setViewport(cr.x, cr.y, cr.w, cr.h); renderer.setScissor(cr.x, cr.y, cr.w, cr.h); renderer.setScissorTest(true);
      const aspect = camera.aspect; camera.aspect = cr.w / cr.h; camera.updateProjectionMatrix();
      renderer.render(scene, camera);
      camera.aspect = aspect; camera.updateProjectionMatrix(); renderer.setScissorTest(false);
    }
    drawCalls = renderer.info.render.calls; drawTris = renderer.info.render.triangles;
    if (benchT !== null) { benchT = (performance.now() - benchStart) / 1000; if (benchT > BENCH_SECONDS) { benchT = null; finish(BENCH_WARMUP, "Benchmark"); } }
    perf.frame({ t: 0, dt, jsMs: performance.now() - jsStart, ratio, drawCalls, triangles: drawTris, x: ct.x, z: ct.z, stepMs: phys.stepMs ?? 0, snapHz: phys.snapHz ?? 0 });
    jsMs += (performance.now() - jsStart - jsMs) * 0.1;      // main-thread time of this frame up to the main render call (the GPU works after it)
    roverPose.x = ct.x; roverPose.z = ct.z; roverPose.quat.copy(shownQ); roverPose.pan = shownPan; roverPose.tilt = shownTilt;
    hazard.without(() => routeView.without(() => delayView.without(() => cameraView.render(scene, node("head"), vw, vh, roverPose))));
  });
}

let resetRequested = false;                 // T: stand the rover upright where it is
const refreshMsRef = { v: 1000 / 60 };      // smoothed interval between animation frames (the display's refresh)
const bench = new URLSearchParams(location.search).get("bench") === "1";      // ?bench=1: the scripted benchmark run (see runBench)
const BENCH_SECONDS = Number(new URLSearchParams(location.search).get("benchsecs")) || 60, BENCH_WARMUP = 3;
let benchT: number | null = null;                    // seconds into the benchmark while it runs: the input is then the script below, not the keyboard
/** the benchmark's fixed route (the same whatever the machine; the physics runs in real time): 3 s settling, 17 s straight, 4 s turning, 16 s straight, 15 s of mast sweeps while creeping, 5 s stopped */
function benchControls(t: number): Controls {
  let throttle = 0, turn = 0, pan = 0, tilt = 0, brake = false;
  if (t < 3) brake = true;
  else if (t < 20) throttle = 1;
  else if (t < 24) turn = 0.6;
  else if (t < 40) throttle = 1;
  else if (t < 55) { throttle = 0.3; const ph = Math.floor((t - 40) / 2.5) % 2 ? -1 : 1; pan = ph; tilt = -ph * 0.6; }
  else brake = true;
  return { throttle, turn, pan, tilt, brake };
}
function resize() {
  const w = canvas.clientWidth, h = canvas.clientHeight;
  if (canvas.width !== Math.floor(w * renderer.getPixelRatio()) || canvas.height !== Math.floor(h * renderer.getPixelRatio())) {
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
}
main().catch((e) => { ui.alerts.status("load failed: " + e, 2); console.error(e); });

/** ?test=1: scripted run without rendering; the numbers go into <pre id="test"> (read with chrome --dump-dom) */
function runTest(phys: RoverPhysics) {
  const out: string[] = [];
  const st = () => { const c = phys.bodies.chassis, t = c.translation(), r = c.rotation(), v = c.linvel(), e = new THREE.Euler().setFromQuaternion(new THREE.Quaternion(r.x, r.y, r.z, r.w), "YXZ");
    return { x: +t.x.toFixed(3), y: +t.y.toFixed(3), z: +t.z.toFixed(3), speed: +Math.hypot(v.x, v.z).toFixed(3), yawDeg: +(e.y * 180 / Math.PI).toFixed(1), pitchDeg: +(e.z * 180 / Math.PI).toFixed(2), rollDeg: +(e.x * 180 / Math.PI).toFixed(2),
      linkL: +(phys.linkAngle.L * 180 / Math.PI).toFixed(2), linkR: +(phys.linkAngle.R * 180 / Math.PI).toFixed(2), amps: WHEELS.map((w) => +(phys.wheelCurrent[w] ?? 0).toFixed(2)), pan: +(phys.panAngle * 180 / Math.PI).toFixed(1), tilt: +(phys.tiltAngle * 180 / Math.PI).toFixed(1) }; };
  const run = (sec: number, c: Controls) => { for (let i = 0; i < sec / phys.dt; i++) (phys as any).substep(c); };
  const idle: Controls = { throttle: 0, turn: 0, pan: 0, tilt: 0, brake: true };
  const t0 = performance.now();
  run(5, idle); out.push("settled 5 s: " + JSON.stringify(st()));
  run(6, { ...idle, brake: false, throttle: 1 }); out.push("forward full 6 s: " + JSON.stringify(st()));
  { const tr: string[] = []; for (let k = 0; k < 16; k++) { run(0.25, idle); const c = phys.bodies.chassis, v = c.linvel(), w = c.angvel(); tr.push(`v(${v.x.toFixed(3)},${v.y.toFixed(3)},${v.z.toFixed(3)}) w(${w.x.toFixed(2)},${w.y.toFixed(2)},${w.z.toFixed(2)}) y${c.translation().y.toFixed(4)}`); } out.push("long brake trace: " + tr.join(" | ")); }
  out.push("braked 3 s: " + JSON.stringify(st()));
  run(2, { ...idle, brake: false, turn: 1 });
  const wy = phys.bodies.chassis.angvel().y;
  run(2, { ...idle, brake: false, turn: 1 }); out.push("turn in place 4 s (full turn command): steady yaw rate " + (wy * 180 / Math.PI).toFixed(0) + " deg/s (negative = clockwise, a right turn): " + JSON.stringify(st()));
  run(2, idle);
  run(3, { ...idle, brake: false, pan: 1, tilt: 1 }); out.push("mast pan+tilt 3 s: " + JSON.stringify(st()));
  out.push("wall time " + ((performance.now() - t0) / 1000).toFixed(1) + " s (headless virtual clock: not meaningful) for " + (5 + 6 + 2 + 3 + 4 + 2 + 3) + " s simulated");
  const pre = document.createElement("pre"); pre.id = "test"; pre.textContent = out.join("\n"); document.body.appendChild(pre);
}
