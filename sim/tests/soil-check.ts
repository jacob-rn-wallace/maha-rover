/** Headless check of the wheel-soil model (src/soil.ts) in the rover physics: `npm run check:soil` (bundles this file with esbuild, runs it in Node).
 *  Flat or inclined ground, no terrain data needed. Prints numbers; the expectations are in docs/sim-spec.md (soil model).
 */
import { readFileSync } from "node:fs";
import { RoverPhysics, WHEELS, type Controls, type Spec, type GroundSource } from "../src/physics";
import { FJS1 } from "../src/soil";

const spec = JSON.parse(readFileSync(new URL("../public/rover.json", import.meta.url), "utf8")) as Spec;
const idle: Controls = { throttle: 0, turn: 0, pan: 0, tilt: 0, brake: true };
const go = (throttle: number, turn = 0): Controls => ({ ...idle, brake: false, throttle, turn });

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

const which = process.argv[2] ?? "all";
if (which === "all" || which === "flat") { await scenario("flat, Coulomb", 0, false); await scenario("flat, soil", 0, true); }
if (which === "all" || which === "slope") for (const a of [5, 10, 15, 20, 25]) await scenario(`climb ${a}`, a, true);
