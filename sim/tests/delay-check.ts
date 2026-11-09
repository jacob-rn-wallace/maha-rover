/** Checks the signal-delay logic (src/delay.ts): `npm run check:delay`. Exits non-zero on a failure. */
import { ControlLog, History, predict, V_FULL, W_FULL, SLEW, CRUISE_THROTTLE } from "../src/delay";

let bad = 0;
const near = (name: string, got: number, want: number, tol = 1e-6) => { const ok = Math.abs(got - want) <= tol; if (!ok) bad++; console.log(ok ? "ok  " : "FAIL", name, ok ? "" : `got ${got}, want ${want}`); };
const eq = (name: string, got: unknown, want: unknown) => { const ok = got === want; if (!ok) bad++; console.log(ok ? "ok  " : "FAIL", name, ok ? "" : `got ${got}, want ${want}`); };
const c = (throttle: number, turn = 0, brake = false) => ({ throttle, turn, pan: 0, tilt: 0, brake });

const log = new ControlLog(); log.push(1, c(0.5)); log.push(2, c(1)); log.push(4, c(0, 1));
eq("before the first command: none", log.at(0.5).throttle, 0);
eq("the command in force at t is the latest issued before it", log.at(3).throttle, 1);
eq("exactly at the time of issue", log.at(2).throttle, 1);
eq("a later one replaces it", log.at(5).turn, 1);

const h = new History(9, [3]);      // x, y, z, then a quaternion at 3..6, then two numbers
const q = (deg: number) => [Math.cos((deg * Math.PI) / 360), 0, Math.sin((deg * Math.PI) / 360), 0];      // a turn about y
h.push(0, [0, 0, 0, ...q(0), 5, 0]); h.push(2, [10, 4, -2, ...q(90), 9, 0]);
const out = new Float64Array(9);
h.sample(1, out); near("position at the midpoint", out[0], 5); near("height", out[1], 2); near("an extra number", out[7], 7);
near("the quaternion at the midpoint is 45 degrees about y", 2 * Math.atan2(out[5], out[3]) * 180 / Math.PI, 45, 1e-6); near("it stays a unit quaternion", Math.hypot(out[3], out[4], out[5], out[6]), 1, 1e-9);
h.sample(-5, out); near("before the history: the oldest", out[0], 0); h.sample(9, out); near("after it: the newest", out[0], 10);
h.push(3, [11, 4, -2, ...q(-270), 9, 0]); h.sample(2.5, out);
near("the shorter way round between 90 and -270 (the same turn)", Math.hypot(out[3], out[4], out[5], out[6]), 1, 1e-9);

// the predictor: no commands, the rover stays; full throttle for ever, heading north; a full turn for ever
const none = new ControlLog();
near("no commands: the ghost stays", predict({ x: 3, z: 4, headingDeg: 90 }, 0, none, 10, 1.3).end.x, 3);
const go = new ControlLog(); go.push(0, c(1));
const p = predict({ x: 0, z: 0, headingDeg: 0 }, 0, go, 10, 1);      // 2 s of the model: ramp 1/1.5 s, then full speed
near("distance in 2 s from rest at full throttle", p.distance, V_FULL * (2 - 1 / SLEW / 2), 0.02);
near("heading north: z decreases, x stays", p.end.x, 0, 1e-9); near("z", -p.end.z, p.distance, 1e-9);
const turn = new ControlLog(); turn.push(0, c(0, 1));
near("a full right turn for 2 s", predict({ x: 0, z: 0, headingDeg: 0 }, 0, turn, 10, 1).end.headingDeg, W_FULL * (2 - 1 / SLEW / 2), 3);
const early = new ControlLog(); early.push(0, c(1)); early.push(10.5, c(0, 0, true));      // a brake issued 0.5 s ago, delay 1: the rover brakes from the last 0.5 s of the window on
const pb = predict({ x: 0, z: 0, headingDeg: 0 }, V_FULL, early, 10, 1);
eq("a brake issued now is already part of the prediction (in force at the rover from now + 0 s on)", pb.distance < V_FULL * 2, true);
near("cruise throttle gives 1.25 km/h", CRUISE_THROTTLE * V_FULL * 3.6, 1.25, 1e-9);
process.exit(bad ? 1 : 0);
