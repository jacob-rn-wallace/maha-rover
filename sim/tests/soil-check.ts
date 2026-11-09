/** Headless check of the wheel-soil model (src/soil.ts) in the rover physics: `npm run check:soil` (bundles this file with esbuild, runs it in Node).
 *  Flat or inclined ground, no terrain data needed. Prints numbers; the expectations are in docs/sim-spec.md (soil model).
 */
import { readFileSync } from "node:fs";
import { RoverPhysics, WHEELS, type Controls, type Spec, type GroundSource } from "../src/physics";
import { FJS1 } from "../src/soil";
import { RockField } from "../src/rocks";
import * as THREE from "three";

const spec = JSON.parse(readFileSync(new URL("../public/rover.json", import.meta.url), "utf8")) as Spec;
const idle: Controls = { throttle: 0, turn: 0, pan: 0, tilt: 0, brake: true };
const go = (throttle: number, turn = 0): Controls => ({ ...idle, brake: false, throttle, turn });

/** one rock in the path of the left wheels: an icosahedron of the given size and height, as src/rocks.ts makes the collider hulls */
function rockAt(x: number, z: number, d: number, h: number) {
  const t = (1 + Math.sqrt(5)) / 2, v = [[-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0], [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t], [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]];
  const pts = new Float32Array(36), n = Math.hypot(1, t);
  v.forEach((p, i) => { pts[i * 3] = x + (p[0] / n) * d / 2; pts[i * 3 + 1] = h / 2 + (p[1] / n) * h / 2; pts[i * 3 + 2] = z + (p[2] / n) * d / 2; });
  return pts;
}

function ground(slopeDeg: number): GroundSource {
  const k = Math.tan(slopeDeg * Math.PI / 180);
  return { height: (x) => k * Math.max(0, x - 1), half: 2500, spawn: { x: 0, y: 0, z: 0 } };      // flat to x = 1 m, then a ramp: the rover drives up it
}
const acc = { n: 0, load: [0, 0, 0, 0], slip: [0, 0, 0, 0], contact: [0, 0, 0, 0] };
const run = (p: RoverPhysics, sec: number, c: Controls) => {
  acc.n = 0; acc.load.fill(0); acc.slip.fill(0); acc.contact.fill(0);
  for (let i = 0; i < sec / p.dt; i++) {
    (p as any).substep(c);
    WHEELS.forEach((k, j) => { const s = p.soilState[k]; if (!s) return; acc.load[j] += s.load; acc.slip[j] += s.slip; acc.contact[j] += s.load > 0.02 ? 1 : 0; });
    acc.n++;
  }
};
const mean = () => ({ load: acc.load.map((x) => x / acc.n), slip: acc.slip.map((x, j) => x / Math.max(1, acc.contact[j])), contact: acc.contact.map((x) => x / acc.n) });
function state(p: RoverPhysics) {
  const c = p.bodies.chassis, t = c.translation(), v = c.linvel(), r = c.rotation(), w = c.angvel();
  const fwd = { x: 1 - 2 * (r.y * r.y + r.z * r.z), y: 2 * (r.x * r.y + r.w * r.z), z: 2 * (r.x * r.z - r.w * r.y) };
  const m = mean();
  return { x: t.x, y: t.y, z: t.z, speed: v.x * fwd.x + v.y * fwd.y + v.z * fwd.z, yawRate: w.y * 180 / Math.PI, load: m.load, slip: m.slip, contact: m.contact };
}
const f = (a: number[], d = 2) => a.map((x) => x.toFixed(d)).join(" ");

async function scenario(name: string, slopeDeg: number, soil: boolean) {
  const p = await RoverPhysics.create(spec, 0.03, ground(slopeDeg), soil ? FJS1 : undefined);
  const t0 = performance.now();
  run(p, 5, idle);
  const s0 = state(p);
  console.log(`\n== ${name} (slope ${slopeDeg} deg, ${soil ? "soil model" : "Coulomb 0.9"})`);
  console.log(`settled: wheel loads (FL FR RL RR, mean over the last 5 s) ${f(s0.load)} N, in contact ${f(s0.contact, 2)} of the time, sum ${s0.load.reduce((a, b) => a + b, 0).toFixed(2)} N (weight ${(spec.total_mass_kg * p.gravity).toFixed(2)} N, wheels and links carry most of it)`);
  const x0 = s0.x, tr: string[] = [];
  for (let k = 1; k <= 12; k++) { run(p, 1, go(1)); const s = state(p); if (k % 3 === 0 || k < 3) tr.push(`${k}s v ${s.speed.toFixed(3)} mean slip ${f(s.slip)}, in contact ${f(s.contact, 2)}, load ${f(s.load)} N`); }
  console.log("full throttle:\n  " + tr.join("\n  "));
  const s1 = state(p);
  const pitch = (() => { const r = p.bodies.chassis.rotation(); return Math.asin(Math.max(-1, Math.min(1, 2 * (r.x * r.y + r.w * r.z)))) * 180 / Math.PI; })();
  console.log(`after 12 s: ${(s1.x - x0).toFixed(2)} m along x, pitch ${pitch.toFixed(1)} deg, height ${s1.y.toFixed(2)} m`);
  run(p, 4, { ...idle, brake: false, throttle: 0 }); const s2 = state(p);
  console.log(`coasting 4 s (duty 0): speed ${s2.speed.toFixed(3)} m/s`);
  run(p, 3, idle); const s3 = state(p);
  console.log(`braked 3 s: speed ${s3.speed.toFixed(3)} m/s`);
  run(p, 2, go(0, 1)); run(p, 2, go(0, 1)); const s4 = state(p);
  console.log(`turn in place 4 s: yaw rate ${s4.yawRate.toFixed(0)} deg/s, mean slip ${f(s4.slip)}, in contact ${f(s4.contact, 2)}`);
  console.log(`wall time ${((performance.now() - t0) / 1000).toFixed(1)} s for ${(5 + 12 + 4 + 3 + 4)} s simulated`);
}

async function rockScenario(name: string, d: number, h: number) {
  const g = { height: () => 0, half: 2500, spawn: { x: 0, y: 0, z: 0 }, rocks: { physics: () => ({ version: 1, hulls: [rockAt(1.2, -0.21, d, h), rockAt(1.2, 0.21, d, h)] }) } };    // a rock in front of each side's wheels
  const p = await RoverPhysics.create(spec, 0.03, g, FJS1);
  run(p, 3, idle);
  console.log(`\n== ${name}: a rock ${d} m wide and ${h} m high in front of both wheel tracks (1.2 m ahead)`);
  let maxPitch = 0, maxRoll = 0;
  const ang = () => { const r = p.bodies.chassis.rotation(); return { pitch: Math.asin(Math.max(-1, Math.min(1, 2 * (r.x * r.y + r.w * r.z)))) * 180 / Math.PI, roll: Math.asin(Math.max(-1, Math.min(1, 2 * (r.w * r.x - r.y * r.z)))) * 180 / Math.PI }; };
  for (let k = 1; k <= 12; k++) { if (process.env.TRACE && k >= 3 && k <= 4) for (let q = 0; q < 3; q++) { run(p, 0.25, go(1)); console.log(`   ${(k - 1 + 0.25 * (q + 1)).toFixed(2)}s cut ${p.tiltCut} pitch ${ang().pitch.toFixed(0)} amps ${WHEELS.map((w) => p.wheelCurrent[w].toFixed(2)).join(' ')}`); } run(p, k >= 3 && k <= 4 && process.env.TRACE ? 0.25 : 1, go(1)); const a = ang(); maxPitch = Math.max(maxPitch, Math.abs(a.pitch)); maxRoll = Math.max(maxRoll, Math.abs(a.roll)); if (process.env.TRACE) console.log(`  t${k}s stalled ${p.stalled} pitch ${a.pitch.toFixed(0)} roll ${a.roll.toFixed(0)}`); const s = state(p); if (k % 3 === 0) console.log(`${k}s x ${s.x.toFixed(2)} m, speed ${s.speed.toFixed(3)} m/s, height ${s.y.toFixed(3)} m`); }
  console.log(`largest pitch ${maxPitch.toFixed(1)} deg, roll ${maxRoll.toFixed(1)} deg`);
}

const which = process.argv[2] ?? "all";
if (which === "field") {                                          // drive through the generated rock field on flat ground, from several starting points and headings
  for (const [sx, sz] of [[0, 0], [300, -200], [-500, 700], [900, 400]]) {
    const base: any = { half: 2500, height: () => 0, detail: () => 0, spawn: { x: sx, y: 0, z: sz } };
    const field = new RockField(base, new THREE.MeshBasicMaterial(), base.spawn);
    base.rocks = field;
    const p = await RoverPhysics.create(spec, 0.03, base, FJS1);
    run(p, 3, idle);
    let maxP = 0, maxR = 0, flipped = false; const x0 = state(p).x, z0 = state(p).z;
    for (let k = 0; k < 120; k++) {                                // 120 s at full throttle, through advance() so that the rocks follow the rover
      for (let i = 0; i < 60; i++) p.advance(1 / 60, go(1));
      const r = p.bodies.chassis.rotation(), pitch = Math.asin(Math.max(-1, Math.min(1, 2 * (r.x * r.y + r.w * r.z)))) * 180 / Math.PI, roll = Math.asin(Math.max(-1, Math.min(1, 2 * (r.w * r.x - r.y * r.z)))) * 180 / Math.PI;
      maxP = Math.max(maxP, Math.abs(pitch)); maxR = Math.max(maxR, Math.abs(roll)); if (Math.abs(pitch) > 60 || Math.abs(roll) > 60) { flipped = true; break; }
    }
    if (flipped) {                                                  // T: stand it upright again and see that it drives
      p.resetUpright(); for (let i = 0; i < 180; i++) p.advance(1 / 60, idle);
      const r = p.bodies.chassis.rotation(), pitch = Math.asin(Math.max(-1, Math.min(1, 2 * (r.x * r.y + r.w * r.z)))) * 180 / Math.PI, roll = Math.asin(Math.max(-1, Math.min(1, 2 * (r.w * r.x - r.y * r.z)))) * 180 / Math.PI;
      const xa = p.bodies.chassis.translation().x; for (let i = 0; i < 180; i++) p.advance(1 / 60, go(-1));
      console.log(`  after reset: pitch ${pitch.toFixed(1)} deg, roll ${roll.toFixed(1)} deg, reversed ${Math.abs(p.bodies.chassis.translation().x - xa).toFixed(2)} m in 3 s`);
    }
    const t = p.bodies.chassis.translation();
    console.log(`start (${sx}, ${sz}): ${flipped ? "FLIPPED" : "drove"} ${Math.hypot(t.x - x0, t.z - z0).toFixed(1)} m in up to 120 s, largest pitch ${maxP.toFixed(0)} deg, roll ${maxR.toFixed(0)} deg, hulls ${(base.rocks.physics(t.x, t.z).hulls.length)}`);
  }
  process.exit(0);
}
if (which === "rocks") { await rockScenario("small rock", 0.12, 0.06); await rockScenario("rock", 0.2, 0.1); await rockScenario("big rock", 0.4, 0.2); process.exit(0); }
if (which === "all" || which === "flat") { await scenario("flat, Coulomb", 0, false); await scenario("flat, soil", 0, true); }
if (which === "all" || which === "slope") for (const a of [5, 10, 15, 20, 25]) await scenario(`climb ${a}`, a, true);
