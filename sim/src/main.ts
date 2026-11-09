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
import { applyMetalDetail } from "./metal";
import { Cable } from "./cable";
import { Minimap } from "./minimap";
import { PerfLog, downloadJson } from "./perfLog";
import { Power } from "./power";
import { PhysicsProxy, type PhysicsView } from "./physicsProxy";
import { WHEELS, MOTOR } from "./constants";
import type { RoverPhysics, Spec, Controls } from "./physics";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

const canvas = document.getElementById("c") as HTMLCanvasElement;
const hud = document.getElementById("hudtext")!;      // the text under the wordmark logo (index.html)
// ?depth=reverse: a reversed floating-point depth buffer instead of the logarithmic one, if the browser offers EXT_clip_control (the logarithmic buffer writes depth in every fragment shader, which switches off early-z
// rejection and is slow on tile-based GPUs such as Apple's). Experimental in three r170 and not testable here (no GPU): opt in, compare with ?stats=1, report.
const wantReverse = new URLSearchParams(location.search).get("depth") === "reverse" && !!document.createElement("canvas").getContext("webgl2")?.getExtension("EXT_clip_control");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: devicePixelRatio < 1.75, logarithmicDepthBuffer: !wantReverse, reverseDepthBuffer: wantReverse, powerPreference: "high-performance" });      // MSAA only on low-DPR screens: a retina screen is sharp enough without it, and it is the larger share of the fill cost   // terrain from 5 cm to 74 km
const coarse = matchMedia("(pointer: coarse)").matches || new URLSearchParams(location.search).get("touch") === "1";      // phone or tablet: lighter rendering, touch sticks
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

addEventListener("error", (e) => { hud.textContent = "error: " + e.message; });
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
  // terrain: the real lunar tile and ring (default); ?flat=1 keeps the flat plane, which the scripted ?test=1 check assumes (add ?terrain=1 to run it on the terrain)
  const flat = q.get("flat") === "1" || (q.get("test") === "1" && q.get("terrain") !== "1");
  let terrain: Terrain | undefined, view: TerrainView | undefined, rockField: RockField | undefined;
  const spawn = new THREE.Vector3();
  if (!flat) {
    hud.textContent = "loading terrain...";
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
      hud.textContent = "computing terrain shadows for the sun...";
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
  if (still) { hud.innerHTML = `model loaded: ${names.length} bodies, ${spec.total_mass_kg.toFixed(2)} kg`; renderer.setAnimationLoop(() => { resize(); controls.update(); renderer.render(scene, camera); }); return; }

  const soil = q.get("soil") === "0" || (flat && q.get("soil") !== "1") ? undefined : FJS1;     // ?soil=0 Coulomb friction instead; ?soil=1 with ?flat=1 or ?test=1
  // the physics runs in a worker (its own copy of the terrain) unless ?worker=0, in the scripted test, or without the terrain
  const useWorker = q.get("worker") !== "0" && q.get("test") !== "1" && typeof Worker !== "undefined";
  let phys: PhysicsView;
  if (useWorker) {
    hud.textContent = "starting physics...";
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
  const input = setupInput();
  // the mast camera: Raspberry Pi HQ (IMX477, 6.287 x 4.712 mm active area, Raspberry Pi documentation) behind a 4 mm lens: 76.6 x 61.4 degrees, 4:3, no distortion
  const cam = spec.camera, mastCam = new THREE.PerspectiveCamera(61.4, 4 / 3, 0.02, 200000);
  const camOff = new THREE.Vector3(...cam.position_m), camBasis = new THREE.Matrix4().makeBasis(new THREE.Vector3(0, 0, 1), new THREE.Vector3(0, 1, 0), new THREE.Vector3(-1, 0, 0));     // camera looks along the head's +x, up is its +y
  if (q.has("pip")) pip.mode = Number(q.get("pip"));      // ?pip=0|1|2: camera view off, small, large at start
  const camFx = new MastCameraFx(renderer, 640, 480, q.has("vignette") ? Number(q.get("vignette")) : 0.6, q.get("noise") === "0" ? 0 : 1, q.has("distort") ? Number(q.get("distort")) : 1, q.get("ae") !== "0");      // ?vignette=0..1, ?noise=0, ?distort=0..., ?ae=0
  (window as any).__fx = camFx;
  mastCam.fov = camFx.renderFov(61.4); mastCam.updateProjectionMatrix();
  const headQ = new THREE.Quaternion();
  const power = new Power();
  const el = THREE.MathUtils.degToRad(lunar.sunElevationDeg), az = THREE.MathUtils.degToRad(lunar.sunAzimuthDeg);
  const sunDir = new THREE.Vector3(Math.cos(el) * Math.cos(az), Math.sin(el), -Math.cos(el) * Math.sin(az));
  const chassisQ = new THREE.Quaternion();
  const minimap = terrain && q.get("map") !== "0" ? new Minimap(terrain, lunar.sunElevationDeg, lunar.sunAzimuthDeg, coarse) : undefined;      // M cycles it; ?map=0 leaves it out
  if (minimap && q.has("mapmode")) { minimap.mode = Number(q.get("mapmode")); minimap.layout(); }
  const mapOffset = () => (minimap && minimap.mode ? (minimap.mode === 2 ? 240 : 110) + 24 : 12);      // on phones the camera view sits under the map
  const fwd = new THREE.Vector3();
  mapToggle = () => minimap?.cycle();
  const chase = new THREE.Vector3(spawn.x, spawn.y + 0.25, spawn.z);
  const euler = new THREE.Euler();
  const gl = renderer.getContext(), dbg = gl.getExtension("WEBGL_debug_renderer_info"), gpuName = dbg ? String(gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL)) : "unknown GPU";
  // performance log: L records, L again stops and offers the file; ?bench=1 runs the scripted benchmark and offers the file at the end
  const perf = new PerfLog(() => ({
    build: __BUILD__, url: location.href, userAgent: navigator.userAgent, gpu: gpuName, devicePixelRatio, screen: `${screen.width}x${screen.height}`, window: `${innerWidth}x${innerHeight}`,
    canvas: `${canvas.width}x${canvas.height}`, maxPixelsM: maxPixels / 1e6, cores: navigator.hardwareConcurrency, deviceMemoryGB: (navigator as any).deviceMemory ?? null, physicsInWorker: useWorker, refreshHz: +(1000 / refreshMsRef.v).toFixed(1), fpsCap: q.has("fps") ? Number(q.get("fps")) : 60,
  }));
  const result = document.createElement("div");
  result.style.cssText = "position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);z-index:10;background:rgba(0,0,0,.85);border:1px solid #888;border-radius:8px;padding:14px 18px;max-width:440px;font:13px/1.5 system-ui;color:#eee;display:none";
  document.body.appendChild(result);
  const finish = (stopSkip: number, name: string) => {
    const data = perf.stop(stopSkip); (data.summary as any).snapshotUnderrunPct = +(100 * ((phys as any).underruns ?? 0) / Math.max(1, (phys as any).frames ?? 1)).toFixed(1); (data.meta as any).refreshHzAtEnd = +(1000 / refreshMsRef.v).toFixed(1); (data.meta as any).canvasAtEnd = `${canvas.width}x${canvas.height}`; (window as any).__perfData = data; const sm = data.summary, stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
    result.innerHTML = `<b>${name} finished</b><br>${sm.frames} frames over ${sm.seconds} s: <b>${sm.meanFps} fps</b> mean, ${sm.onePercentLowFps} fps 1% low<br>frame time median ${sm.frameMs.median} ms, 95th percentile ${sm.frameMs.p95} ms, worst ${sm.frameMs.worst} ms<br>main thread ${sm.meanJsMs} ms/frame, physics step ${sm.physicsStepMs} ms, pixel ratio ${sm.meanPixelRatio}, buffer ${canvas.width} x ${canvas.height}<br><br>`;
    const b = document.createElement("button"); b.textContent = "Download the log file"; b.style.cssText = "padding:6px 12px;margin-right:8px"; b.onclick = () => downloadJson(`almaha-perf-${stamp}.json`, data);
    const c = document.createElement("button"); c.textContent = "Close"; c.style.cssText = "padding:6px 12px"; c.onclick = () => { result.style.display = "none"; };
    result.append(b, c); result.style.display = "block";
    return data;
  };
  logToggle = () => { if (perf.recording) { finish(0, "Recording"); } else { result.style.display = "none"; perf.start("manual", { search: location.search }); } };
  let benchStart = 0;
  if (bench) { benchStart = performance.now(); benchT = 0; perf.start("benchmark", { search: location.search, seconds: BENCH_SECONDS, warmupSeconds: BENCH_WARMUP, adaptive: q.get("adapt") === "1" }); }
  let last = performance.now(), hudT = 0, mapT = 1, fpsEma = 60, frameEma = 1 / 60, resNote = 0, drawCalls = 0, drawTris = 0;
  let jsMs = 0;
  const showStats = q.get("stats") === "1" || bench;      // ?stats=1: frame rate and draw load of the main view on the HUD
  // Frame pacing: on a display faster than the cap (a 120 Hz MacBook screen) only every Nth animation frame is drawn, N = round(cap interval / refresh interval), so the frames come at an even 60 Hz.
  // Drawing every frame at 120 Hz, with the camera view's extra scene pass on every third, gave frame times alternating 8 and 17 ms: judder although the mean was 90 fps (the owner's log, 2026-11-09).
  // ?fps=N sets the cap (default 60, 0 = draw every frame).
  const fpsCap = q.has("fps") ? Number(q.get("fps")) : 60;
  let rafLast = 0, skip = 0;
  refreshMsRef.v = 1000 / 60;
  renderer.setAnimationLoop((now) => {
    if (rafLast) { const d = now - rafLast; if (d > 2 && d < 60) refreshMsRef.v += (d - refreshMsRef.v) * 0.05; }
    rafLast = now;
    if (fpsCap > 0) { const step = Math.max(1, Math.round(1000 / fpsCap / refreshMsRef.v)); if (++skip < step) return; skip = 0; }
    const jsStart = performance.now();
    const dt = (now - last) / 1000; last = now;
    if (resetRequested) { resetRequested = false; phys.resetUpright(); }
    phys.advance(dt, input.read());
    { const r = phys.bodies.chassis.rotation(); chassisQ.set(r.x, r.y, r.z, r.w); power.step(Math.min(dt, 0.1), phys.motorPackAmps, phys.servoMoving, sunDir, chassisQ); }
    for (const n of names) {
      const b = phys.bodies[n], t = b.translation(), r = b.rotation();
      node(n).position.set(t.x, t.y, t.z);
      node(n).quaternion.set(r.x, r.y, r.z, r.w);
    }
    cable?.update(dt);
    const c = phys.bodies.chassis, ct = c.translation();
    const delta = new THREE.Vector3(ct.x, ct.y + 0.25, ct.z).sub(chase);
    chase.add(delta); camera.position.add(delta); controls.target.copy(chase);
    lunar.followSun(new THREE.Vector3(ct.x, ct.y, ct.z));
    mapT += dt;
    if (minimap && mapT > 0.1) { mapT = 0; fwd.set(1, 0, 0).applyQuaternion(chassisQ); minimap.update(ct.x, ct.z, fwd.x, fwd.z); }
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
    if (hudT > 0.1) { hudT = 0; hud.innerHTML = (coarse && !hudFull ? shortText(phys, c, euler, power) : hudText(phys, c, euler) + powerText(power) + (terrain ? edgeText(ct.x, ct.z, terrain) : "")) + (perf.recording ? `<br><span style="color:#ff6a5a">● recording ${perf.seconds.toFixed(0)} s${benchT !== null ? ` of ${BENCH_SECONDS} (benchmark: keep the window in front)` : " (L to stop)"}</span>` : "") + (showStats ? `<br>${gpuName}<br>main thread ${jsMs.toFixed(1)} ms/frame, ${fpsEma.toFixed(0)} fps, pixel ratio ${ratio.toFixed(2)} (${canvas.width} x ${canvas.height}), ${drawCalls} draw calls, ${(drawTris / 1e6).toFixed(2)} M triangles` : ""); }
    resize();
    controls.update();
    const vw = canvas.clientWidth, vh = canvas.clientHeight;
    renderer.setScissorTest(false); renderer.setViewport(0, 0, vw, vh);
    renderer.render(scene, camera);
    drawCalls = renderer.info.render.calls; drawTris = renderer.info.render.triangles;
    if (benchT !== null) { benchT = (performance.now() - benchStart) / 1000; if (benchT > BENCH_SECONDS) { benchT = null; finish(BENCH_WARMUP, "Benchmark"); } }
    perf.frame({ t: 0, dt, jsMs: performance.now() - jsStart, ratio, drawCalls, triangles: drawTris, x: ct.x, z: ct.z, stepMs: phys.stepMs ?? 0, snapHz: phys.snapHz ?? 0 });
    jsMs += (performance.now() - jsStart - jsMs) * 0.1;      // main-thread time of this frame up to the main render call (the GPU works after it)
    if (pip.mode > 0) {
      const hb = node("head"), hp = hb.position;
      headQ.copy(hb.quaternion);
      mastCam.position.copy(camOff).applyQuaternion(headQ).add(hp);
      mastCam.quaternion.copy(headQ).multiply(new THREE.Quaternion().setFromRotationMatrix(camBasis));
      const pw = Math.min(vw * (pip.mode === 2 ? 0.7 : 0.3), (vh * (pip.mode === 2 ? 0.7 : 0.3)) * 4 / 3), ph = pw * 3 / 4, px = vw - pw - 12, py = coarse ? vh - ph - mapOffset() : 12;
      camFx.render(scene, mastCam, px, py, pw, ph);
      pip.label.textContent = `mast camera, HQ + 4 mm lens, 76.6 x 61.4 deg, exposure gain x${camFx.gain.toFixed(2)}`;
      Object.assign(pip.box.style, { display: "block", right: "12px", ...(coarse ? { top: mapOffset() + "px", bottom: "" } : { bottom: "12px" }), width: pw + "px", height: ph + "px" });
    } else pip.box.style.display = "none";
  });
}

/** phones: three lines, tap the panel for the full readout */
let hudFull = false;
if (coarse) { hud.style.fontSize = "11px"; hud.style.maxWidth = "230px"; hud.addEventListener("click", () => { hudFull = !hudFull; }); }
function shortText(phys: PhysicsView, c: any, euler: THREE.Euler, p: Power) {
  const r = c.rotation(); euler.setFromQuaternion(new THREE.Quaternion(r.x, r.y, r.z, r.w), "YXZ");
  const v = c.linvel(), deg = (x: number) => (x * 180 / Math.PI).toFixed(0);
  return `${Math.hypot(v.x, v.z).toFixed(2)} m/s<br>pitch ${deg(euler.z)}°, roll ${deg(euler.x)}°, battery ${(p.soc * 100).toFixed(0)}%${phys.tiltCut ? '<br><span style="color:#ffb04a">tilt guard: drive cut</span>' : ""}<br><span style="opacity:.6">tap for more</span>`;
}

function powerText(p: Power) {
  const t = p.minutesLeft;
  return `<br>battery ${(p.soc * 100).toFixed(1)}% (${p.volts.toFixed(2)} V), load ${p.wattsLoad.toFixed(1)} W (${p.loadAmps.toFixed(1)} A), solar ${p.solarW.toFixed(1)} W${isFinite(t) ? `, ${t > 120 ? (t / 60).toFixed(1) + " h" : t.toFixed(0) + " min"} left at this draw` : ", charging"}`;
}

/** the mast camera's picture-in-picture: C cycles small, large, off (frame and label are a DOM box over the canvas) */
const pip = (() => {
  const box = document.createElement("div");
  box.style.cssText = "display:none;position:fixed;border:1px solid #888;box-sizing:border-box;pointer-events:none";
  const label = document.createElement("span");
  label.style.cssText = "position:absolute;left:4px;top:2px;font-size:11px;opacity:.8";
  box.appendChild(label); document.body.appendChild(box);
  return { box, label, mode: 1 };
})();

function edgeText(x: number, z: number, t: Terrain) {
  const edge = t.half - 20 - Math.max(Math.abs(x), Math.abs(z));      // the walls stand 20 m inside the tile edge (physics.ts)
  const warn = edge < 100 ? `<br><span style="color:#ffb04a">sandbox edge ${Math.max(0, edge).toFixed(0)} m ahead</span>` : "";
  return `<br>position ${x.toFixed(0)} m E, ${(-z).toFixed(0)} m N of the tile centre${warn}`;
}

/** with the soil model: the mean tip-referred slip of the wheels in contact and the sinkage the model predicts for it (the ground itself stays rigid) */
function soilLine(phys: PhysicsView) {
  const on = WHEELS.map((w) => phys.soilState[w]).filter((s) => s && s.load > 0.02);
  if (!on.length) return "";
  const slip = on.reduce((a, s) => a + s.slip, 0) / on.length, sink = on.reduce((a, s) => a + s.sinkage, 0) / on.length, load = on.reduce((a, s) => a + s.load, 0);
  return `, soil slip ${(slip * 100).toFixed(0)}%, sinkage about ${sink.toFixed(0)} mm, load ${load.toFixed(1)} N`;
}

function hudText(phys: PhysicsView, c: any, euler: THREE.Euler) {
  const r = c.rotation(); euler.setFromQuaternion(new THREE.Quaternion(r.x, r.y, r.z, r.w), "YXZ");
  const v = c.linvel(), fwd = new THREE.Vector3(1, 0, 0).applyQuaternion(new THREE.Quaternion(r.x, r.y, r.z, r.w));
  const speed = v.x * fwd.x + v.y * fwd.y + v.z * fwd.z;
  const deg = (x: number) => (x * 180 / Math.PI).toFixed(0);
  const amps = WHEELS.map((w) => Math.abs(phys.wheelCurrent[w] ?? 0).toFixed(1)).join(" ");
  const wrate = (WHEELS.reduce((a, w) => a + (phys.wheelRate[w] ?? 0), 0) / 4) * 0.1;
  const slip = Math.abs(wrate) > 0.02 ? Math.max(-1, Math.min(1, 1 - speed / wrate)) : 0;
  return `lunar gravity ${phys.gravity} m/s2<br>speed ${speed.toFixed(2)} m/s, wheel slip ${(slip * 100).toFixed(0)}%${soilLine(phys)}<br>pitch ${deg(euler.z)}°, roll ${deg(euler.x)}°<br>links L ${deg(phys.linkAngle.L)}° R ${deg(phys.linkAngle.R)}° (differential)<br>mast pan ${deg(phys.panAngle)}°, tilt ${deg(phys.tiltAngle)}°<br>motor current ${amps} A (cap ${MOTOR.iCap})${phys.tiltCut ? ' <span style="color:#ffb04a">tilt guard: drive cut (T to stand upright)</span>' : ''}<br><span style="opacity:.7">W/S drive, A/D steer, Space brake, Q/E pan, R/F tilt, T upright, C camera view, M map, L performance log; gamepad: left stick drive, right stick mast</span>`;
}

let logToggle: (() => void) | undefined;      // L: start or stop the performance log
let mapToggle: (() => void) | undefined;      // set once the minimap exists (M key)
let resetRequested = false;                 // T: stand the rover upright where it is
/** touch: two virtual sticks (left: drive and steer, right: mast pan and tilt) and a T button, shown when the primary pointer is coarse (a phone or tablet) or with ?touch=1 */
function touchSticks() {
  const out = { drive: [0, 0], mast: [0, 0] };
  const R = 60;
  const make = (side: "left" | "right", key: "drive" | "mast") => {
    const base = document.createElement("div"), knob = document.createElement("div");
    base.style.cssText = `position:fixed;${side}:24px;bottom:24px;width:${2 * R}px;height:${2 * R}px;border-radius:50%;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.3);touch-action:none`;
    knob.style.cssText = `position:absolute;left:${R - 22}px;top:${R - 22}px;width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,.45);pointer-events:none`;
    base.appendChild(knob); document.body.appendChild(base);
    const set = (e: PointerEvent) => {
      const b = base.getBoundingClientRect();
      let dx = (e.clientX - b.left - R) / R, dy = (e.clientY - b.top - R) / R; const m = Math.hypot(dx, dy); if (m > 1) { dx /= m; dy /= m; }
      out[key] = [dx, -dy]; knob.style.transform = `translate(${dx * (R - 22)}px,${dy * (R - 22)}px)`;
    };
    const end = () => { out[key] = [0, 0]; knob.style.transform = ""; };
    base.addEventListener("pointerdown", (e) => { base.setPointerCapture(e.pointerId); set(e); });
    base.addEventListener("pointermove", (e) => { if (base.hasPointerCapture(e.pointerId)) set(e); });
    base.addEventListener("pointerup", end); base.addEventListener("pointercancel", end);
  };
  make("left", "drive"); make("right", "mast");
  const mk = (label: string, bottom: number, on: () => void) => {
    const b = document.createElement("button"); b.textContent = label;
    b.style.cssText = `position:fixed;left:50%;transform:translateX(-50%);bottom:${bottom}px;padding:8px 14px;border-radius:8px;background:rgba(255,255,255,.15);color:#fff;border:1px solid rgba(255,255,255,.3);font:13px system-ui`;
    b.addEventListener("click", on); document.body.appendChild(b);
  };
  mk("stand upright", 24, () => { resetRequested = true; });
  mk("camera view", 64, () => { pip.mode = (pip.mode + 1) % 3; });
  return out;
}

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
const autoDrive = (new URLSearchParams(location.search).get("autodrive") ?? "").split(",").map(Number).filter(isFinite) as number[];      // ?autodrive=from,to: full throttle between those seconds after load (for scripted screenshots)
const t0 = performance.now();
function setupInput() {
  const touch = coarse ? touchSticks() : undefined;
  const keys = new Set<string>();
  addEventListener("keydown", (e) => { keys.add(e.code); if (e.code === "Space") e.preventDefault(); if (e.code === "KeyT" && !e.repeat) resetRequested = true; if (e.code === "KeyC" && !e.repeat) pip.mode = (pip.mode + 1) % 3; if (e.code === "KeyM" && !e.repeat) mapToggle?.(); if (e.code === "KeyL" && !e.repeat) logToggle?.(); });
  addEventListener("keyup", (e) => keys.delete(e.code));
  addEventListener("blur", () => keys.clear());
  const k = (...c: string[]) => (c.some((x) => keys.has(x)) ? 1 : 0);
  return {
    read(): Controls {
      if (benchT !== null) return benchControls(benchT);
      let throttle = k("KeyW", "ArrowUp") - k("KeyS", "ArrowDown"), turn = k("KeyD", "ArrowRight") - k("KeyA", "ArrowLeft");
      let pan = k("KeyQ") - k("KeyE"), tilt = k("KeyR") - k("KeyF");
      const gp = navigator.getGamepads?.().find((g) => g);
      if (gp) {
        const dz = (x: number) => (Math.abs(x) < 0.12 ? 0 : x);
        throttle += -dz(gp.axes[1] ?? 0); turn += dz(gp.axes[0] ?? 0);
        pan += -dz(gp.axes[2] ?? 0); tilt += -dz(gp.axes[3] ?? 0);
      }
      if (touch) { throttle += touch.drive[1]; turn += touch.drive[0]; pan += -touch.mast[0]; tilt += touch.mast[1]; }
      if (autoDrive.length === 2 && performance.now() - t0 < autoDrive[1] * 1000 && performance.now() - t0 > autoDrive[0] * 1000) throttle += 1;
      const cl = (x: number) => Math.max(-1, Math.min(1, x));
      return { throttle: cl(throttle), turn: cl(turn), pan: cl(pan), tilt: cl(tilt), brake: keys.has("Space") };
    },
  };
}
function resize() {
  const w = canvas.clientWidth, h = canvas.clientHeight;
  if (canvas.width !== Math.floor(w * renderer.getPixelRatio()) || canvas.height !== Math.floor(h * renderer.getPixelRatio())) {
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
}
main().catch((e) => { hud.textContent = "load failed: " + e; console.error(e); });

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
