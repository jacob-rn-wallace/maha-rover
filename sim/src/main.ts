import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { addLunarScene } from "./lunar";
import { RoverPhysics, WHEELS, MOTOR, type Spec, type Controls } from "./physics";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

const canvas = document.getElementById("c") as HTMLCanvasElement;
const hud = document.getElementById("hud")!;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.85;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 2000);
camera.position.set(0.9, 0.6, 0.9);
const controls = new OrbitControls(camera, canvas);
controls.target.set(0.1, 0.3, 0);

const lunar = addLunarScene(scene, renderer);
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
  if (q.get("cam")) {                      // ?cam=x,y,z,tx,ty,tz&still=1: fixed view for screenshots (metres, glTF axes); still=1 also pauses the physics
    const v = q.get("cam")!.split(",").map(Number);
    camera.position.set(v[0], v[1], v[2]);
    controls.target.set(v[3], v[4], v[5]);
  }
  const still = q.get("still") === "1";
  lunar.followSun(new THREE.Vector3(0, 0, 0));
  if (still) { hud.innerHTML = `<b>المَهَا al-maha</b><br>model loaded: ${names.length} bodies, ${spec.total_mass_kg.toFixed(2)} kg`; renderer.setAnimationLoop(() => { resize(); controls.update(); renderer.render(scene, camera); }); return; }

  const phys = await RoverPhysics.create(spec);
  if (q.get("test") === "1") { runTest(phys); return; }
  const input = setupInput();
  const chase = new THREE.Vector3(0, 0.25, 0);
  const euler = new THREE.Euler();
  let last = performance.now(), hudT = 0;
  renderer.setAnimationLoop((now) => {
    const dt = (now - last) / 1000; last = now;
    phys.advance(dt, input.read());
    for (const n of names) {
      const b = phys.bodies[n], t = b.translation(), r = b.rotation();
      node(n).position.set(t.x, t.y, t.z);
      node(n).quaternion.set(r.x, r.y, r.z, r.w);
    }
    const c = phys.bodies.chassis, ct = c.translation();
    const delta = new THREE.Vector3(ct.x, ct.y + 0.25, ct.z).sub(chase);
    chase.add(delta); camera.position.add(delta); controls.target.copy(chase);
    lunar.followSun(new THREE.Vector3(ct.x, 0, ct.z));
    ground.position.set(0, 0, 0);
    hudT += dt;
    if (hudT > 0.1) { hudT = 0; hud.innerHTML = hudText(phys, c, euler); }
    resize();
    controls.update();
    renderer.render(scene, camera);
  });
}

function hudText(phys: RoverPhysics, c: any, euler: THREE.Euler) {
  const r = c.rotation(); euler.setFromQuaternion(new THREE.Quaternion(r.x, r.y, r.z, r.w), "YXZ");
  const v = c.linvel(), fwd = new THREE.Vector3(1, 0, 0).applyQuaternion(new THREE.Quaternion(r.x, r.y, r.z, r.w));
  const speed = v.x * fwd.x + v.y * fwd.y + v.z * fwd.z;
  const deg = (x: number) => (x * 180 / Math.PI).toFixed(0);
  const amps = WHEELS.map((w) => Math.abs(phys.wheelCurrent[w] ?? 0).toFixed(1)).join(" ");
  const wrate = (WHEELS.reduce((a, w) => a + (phys.wheelRate[w] ?? 0), 0) / 4) * 0.1;
  const slip = Math.abs(wrate) > 0.02 ? Math.max(-1, Math.min(1, 1 - speed / wrate)) : 0;
  return `<b>المَهَا al-maha</b> (lunar gravity ${phys.gravity} m/s2)<br>speed ${speed.toFixed(2)} m/s, wheel slip ${(slip * 100).toFixed(0)}%<br>pitch ${deg(euler.z)}°, roll ${deg(euler.x)}°<br>links L ${deg(phys.linkAngle.L)}° R ${deg(phys.linkAngle.R)}° (differential)<br>mast pan ${deg(phys.panAngle)}°, tilt ${deg(phys.tiltAngle)}°<br>motor current ${amps} A (cap ${MOTOR.iCap})<br><span style="opacity:.7">W/S drive, A/D steer, Space brake, Q/E pan, R/F tilt; gamepad: left stick drive, right stick mast</span>`;
}

function setupInput() {
  const keys = new Set<string>();
  addEventListener("keydown", (e) => { keys.add(e.code); if (e.code === "Space") e.preventDefault(); });
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
