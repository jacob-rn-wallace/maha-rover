import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { addLunarScene } from "./lunar";
import { Terrain } from "./terrain";
import { FJS1 } from "./soil";
import { RockField } from "./rocks";
import { loadTerrainShadow, applyTerrainShadow, computeTerrainShadow } from "./terrainShadow";
import { TerrainView } from "./terrainView";
import { applyRegolithPhotometry } from "./regolith";
import { MastCameraFx } from "./cameraFx";
import { Power } from "./power";
import { RoverPhysics, WHEELS, MOTOR, type Spec, type Controls } from "./physics";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

const canvas = document.getElementById("c") as HTMLCanvasElement;
const hud = document.getElementById("hud")!;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, logarithmicDepthBuffer: true });   // terrain from 5 cm to 74 km
const coarse = matchMedia("(pointer: coarse)").matches || new URLSearchParams(location.search).get("touch") === "1";      // phone or tablet: lighter rendering, touch sticks
renderer.setPixelRatio(Math.min(devicePixelRatio, coarse ? 1.25 : 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
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
    new GLTFLoader().loadAsync("rover.glb"),
    fetch("rover.json").then((r) => r.json() as Promise<Spec>),
  ]);
  gltf.scene.traverse((o) => { if ((o as THREE.Mesh).isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  scene.add(gltf.scene);
  const names = Object.keys(spec.bodies);
  const nodes: Record<string, THREE.Object3D> = Object.fromEntries(names.map((n) => [n, gltf.scene.getObjectByName(n)!]));   // look all up before re-parenting
  const node = (n: string) => nodes[n];
  for (const n of names) scene.attach(nodes[n]);            // body nodes move in world space: the physics drives each one
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
    view.addRing().then((r) => { console.log("ring mesh", r.triangles, "triangles, at", performance.now().toFixed(0), "ms"); for (const k of (q.get("hide") ?? "").split(",").filter(Boolean)) view!.group.children[Number(k)].visible = false; });   // ?hide=0,1,2,3,4: hide a terrain level (0 finest to 3) or 4 the ring, for finding seams
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
  if (still) { hud.innerHTML = `<b>المَهَا al-maha</b><br>model loaded: ${names.length} bodies, ${spec.total_mass_kg.toFixed(2)} kg`; renderer.setAnimationLoop(() => { resize(); controls.update(); renderer.render(scene, camera); }); return; }

  const soil = q.get("soil") === "0" || (flat && q.get("soil") !== "1") ? undefined : FJS1;     // ?soil=0 Coulomb friction instead; ?soil=1 with ?flat=1 or ?test=1
  const phys = await RoverPhysics.create(spec, 0.03, terrain, soil);
  if (q.get("test") === "1") { runTest(phys); return; }
  const input = setupInput();
  // the mast camera: Raspberry Pi HQ (IMX477, 6.287 x 4.712 mm active area, Raspberry Pi documentation) behind a 4 mm lens: 76.6 x 61.4 degrees, 4:3, no distortion
  const cam = spec.camera, mastCam = new THREE.PerspectiveCamera(61.4, 4 / 3, 0.02, 200000);
  const camOff = new THREE.Vector3(...cam.position_m), camBasis = new THREE.Matrix4().makeBasis(new THREE.Vector3(0, 0, 1), new THREE.Vector3(0, 1, 0), new THREE.Vector3(-1, 0, 0));     // camera looks along the head's +x, up is its +y
  if (q.has("pip")) pip.mode = Number(q.get("pip"));      // ?pip=0|1|2: camera view off, small, large at start
  const camFx = new MastCameraFx(renderer, 640, 480, q.has("vignette") ? Number(q.get("vignette")) : 0.6, q.get("noise") === "0" ? 0 : 1, q.has("distort") ? Number(q.get("distort")) : 1, q.get("ae") !== "0");      // ?vignette=0..1, ?noise=0, ?distort=0..., ?ae=0
  mastCam.fov = camFx.renderFov(61.4); mastCam.updateProjectionMatrix();
  const headQ = new THREE.Quaternion();
  const power = new Power();
  const el = THREE.MathUtils.degToRad(lunar.sunElevationDeg), az = THREE.MathUtils.degToRad(lunar.sunAzimuthDeg);
  const sunDir = new THREE.Vector3(Math.cos(el) * Math.cos(az), Math.sin(el), -Math.cos(el) * Math.sin(az));
  const chassisQ = new THREE.Quaternion();
  const chase = new THREE.Vector3(spawn.x, spawn.y + 0.25, spawn.z);
  const euler = new THREE.Euler();
  let last = performance.now(), hudT = 0;
  renderer.setAnimationLoop((now) => {
    const dt = (now - last) / 1000; last = now;
    if (resetRequested) { resetRequested = false; phys.resetUpright(); }
    phys.advance(dt, input.read());
    { const r = phys.bodies.chassis.rotation(); chassisQ.set(r.x, r.y, r.z, r.w); power.step(Math.min(dt, 0.1), phys.motorPackAmps, phys.servoMoving, sunDir, chassisQ); }
    for (const n of names) {
      const b = phys.bodies[n], t = b.translation(), r = b.rotation();
      node(n).position.set(t.x, t.y, t.z);
      node(n).quaternion.set(r.x, r.y, r.z, r.w);
    }
    const c = phys.bodies.chassis, ct = c.translation();
    const delta = new THREE.Vector3(ct.x, ct.y + 0.25, ct.z).sub(chase);
    chase.add(delta); camera.position.add(delta); controls.target.copy(chase);
    lunar.followSun(new THREE.Vector3(ct.x, ct.y, ct.z));
    view?.update(ct.x, ct.z);
    rockField?.update(ct.x, ct.z);
    hudT += dt;
    if (hudT > 0.1) { hudT = 0; hud.innerHTML = coarse && !hudFull ? shortText(phys, c, euler, power) : hudText(phys, c, euler) + powerText(power) + (terrain ? edgeText(ct.x, ct.z, terrain) : ""); }
    resize();
    controls.update();
    const vw = canvas.clientWidth, vh = canvas.clientHeight;
    renderer.setScissorTest(false); renderer.setViewport(0, 0, vw, vh);
    renderer.render(scene, camera);
    if (pip.mode > 0) {
      const hb = node("head"), hp = hb.position;
      headQ.copy(hb.quaternion);
      mastCam.position.copy(camOff).applyQuaternion(headQ).add(hp);
      mastCam.quaternion.copy(headQ).multiply(new THREE.Quaternion().setFromRotationMatrix(camBasis));
      const pw = Math.min(vw * (pip.mode === 2 ? 0.7 : 0.3), (vh * (pip.mode === 2 ? 0.7 : 0.3)) * 4 / 3), ph = pw * 3 / 4, px = vw - pw - 12, py = coarse ? vh - ph - 12 : 12;
      camFx.render(scene, mastCam, px, py, pw, ph);
      pip.label.textContent = `mast camera, HQ + 4 mm lens, 76.6 x 61.4 deg, exposure gain x${camFx.gain.toFixed(2)}`;
      Object.assign(pip.box.style, { display: "block", right: "12px", ...(coarse ? { top: "12px", bottom: "" } : { bottom: "12px" }), width: pw + "px", height: ph + "px" });
    } else pip.box.style.display = "none";
  });
}

/** phones: three lines, tap the panel for the full readout */
let hudFull = false;
if (coarse) { hud.style.fontSize = "11px"; hud.style.maxWidth = "230px"; hud.addEventListener("click", () => { hudFull = !hudFull; }); }
function shortText(phys: RoverPhysics, c: any, euler: THREE.Euler, p: Power) {
  const r = c.rotation(); euler.setFromQuaternion(new THREE.Quaternion(r.x, r.y, r.z, r.w), "YXZ");
  const v = c.linvel(), deg = (x: number) => (x * 180 / Math.PI).toFixed(0);
  return `<b>المَهَا al-maha</b> ${Math.hypot(v.x, v.z).toFixed(2)} m/s<br>pitch ${deg(euler.z)}°, roll ${deg(euler.x)}°, battery ${(p.soc * 100).toFixed(0)}%${phys.tiltCut ? '<br><span style="color:#ffb04a">tilt guard: drive cut</span>' : ""}<br><span style="opacity:.6">tap for more</span>`;
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
function soilLine(phys: RoverPhysics) {
  const on = WHEELS.map((w) => phys.soilState[w]).filter((s) => s && s.load > 0.02);
  if (!on.length) return "";
  const slip = on.reduce((a, s) => a + s.slip, 0) / on.length, sink = on.reduce((a, s) => a + s.sinkage, 0) / on.length, load = on.reduce((a, s) => a + s.load, 0);
  return `, soil slip ${(slip * 100).toFixed(0)}%, sinkage about ${sink.toFixed(0)} mm, load ${load.toFixed(1)} N`;
}

function hudText(phys: RoverPhysics, c: any, euler: THREE.Euler) {
  const r = c.rotation(); euler.setFromQuaternion(new THREE.Quaternion(r.x, r.y, r.z, r.w), "YXZ");
  const v = c.linvel(), fwd = new THREE.Vector3(1, 0, 0).applyQuaternion(new THREE.Quaternion(r.x, r.y, r.z, r.w));
  const speed = v.x * fwd.x + v.y * fwd.y + v.z * fwd.z;
  const deg = (x: number) => (x * 180 / Math.PI).toFixed(0);
  const amps = WHEELS.map((w) => Math.abs(phys.wheelCurrent[w] ?? 0).toFixed(1)).join(" ");
  const wrate = (WHEELS.reduce((a, w) => a + (phys.wheelRate[w] ?? 0), 0) / 4) * 0.1;
  const slip = Math.abs(wrate) > 0.02 ? Math.max(-1, Math.min(1, 1 - speed / wrate)) : 0;
  return `<b>المَهَا al-maha</b> (lunar gravity ${phys.gravity} m/s2)<br>speed ${speed.toFixed(2)} m/s, wheel slip ${(slip * 100).toFixed(0)}%${soilLine(phys)}<br>pitch ${deg(euler.z)}°, roll ${deg(euler.x)}°<br>links L ${deg(phys.linkAngle.L)}° R ${deg(phys.linkAngle.R)}° (differential)<br>mast pan ${deg(phys.panAngle)}°, tilt ${deg(phys.tiltAngle)}°<br>motor current ${amps} A (cap ${MOTOR.iCap})${phys.tiltCut ? ' <span style="color:#ffb04a">tilt guard: drive cut (T to stand upright)</span>' : ''}<br><span style="opacity:.7">W/S drive, A/D steer, Space brake, Q/E pan, R/F tilt, T upright, C camera view; gamepad: left stick drive, right stick mast</span>`;
}

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

function setupInput() {
  const touch = coarse ? touchSticks() : undefined;
  const keys = new Set<string>();
  addEventListener("keydown", (e) => { keys.add(e.code); if (e.code === "Space") e.preventDefault(); if (e.code === "KeyT" && !e.repeat) resetRequested = true; if (e.code === "KeyC" && !e.repeat) pip.mode = (pip.mode + 1) % 3; });
  addEventListener("keyup", (e) => keys.delete(e.code));
  addEventListener("blur", () => keys.clear());
  const k = (...c: string[]) => (c.some((x) => keys.has(x)) ? 1 : 0);
  return {
    read(): Controls {
      let throttle = k("KeyW", "ArrowUp") - k("KeyS", "ArrowDown"), turn = k("KeyD", "ArrowRight") - k("KeyA", "ArrowLeft");
      let pan = k("KeyQ") - k("KeyE"), tilt = k("KeyR") - k("KeyF");
      const gp = navigator.getGamepads?.().find((g) => g);
      if (gp) {
        const dz = (x: number) => (Math.abs(x) < 0.12 ? 0 : x);
        throttle += -dz(gp.axes[1] ?? 0); turn += dz(gp.axes[0] ?? 0);
        pan += -dz(gp.axes[2] ?? 0); tilt += -dz(gp.axes[3] ?? 0);
      }
      if (touch) { throttle += touch.drive[1]; turn += touch.drive[0]; pan += -touch.mast[0]; tilt += touch.mast[1]; }
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
