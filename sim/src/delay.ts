/** Signal delay (docs/sim-ui-research.md, step 5): the commands reach the rover one way-delay late, and what the operator sees (video, telemetry) is that old, so a command is seen to take effect
 *  a whole round trip later. This file holds the pure parts: a log of the commands issued, a history of the rover's poses to show the operator the delayed state, and a predictor of where the rover will be
 *  when a command issued now arrives (the predictive display of the NASA lunar-vehicle studies). No DOM and no three: tests/delay-check.ts imports it. */
import type { Controls } from "./physics";

/** The predictor's model of the drive, from the sim's own figures (`?test=1`, docs/sim-spec.md): full throttle gives 0.527 m/s on flat rigid ground, a full turn command turns the rover in place at about 100 degrees a
 *  second, the motor duty changes at 1.5 a second at most (physics.ts, DUTY_SLEW). Slope, soil and rocks are not modelled: the ghost is an estimate, and its circle says so. */
export const V_FULL = 0.527, W_FULL = 100, SLEW = 1.5;
/** 1.25 km/h, the middle of the 1 to 1.5 km/h cruise speed that operators settled on in NASA's 4 to 8 s delay studies (docs/sim-ui-research.md): the throttle that gives it (0.347 m/s) */
export const CRUISE_THROTTLE = (1.25 / 3.6) / V_FULL;
/** the Earth to Moon one-way light time, about 1.28 s: the default delay */
export const MOON_ONE_WAY_S = 1.3;

const IDLE: Controls = { throttle: 0, turn: 0, pan: 0, tilt: 0, brake: false };

/** the commands issued, with the time each was issued; `at(t)` is the command in force at t (the latest issued at or before t; none before the first) */
export class ControlLog {
  private t: number[] = []; private c: Controls[] = [];
  push(t: number, c: Controls) { this.t.push(t); this.c.push(c); const keep = t - 12; let n = 0; while (n < this.t.length - 2 && this.t[n + 1] < keep) n++; if (n) { this.t.splice(0, n); this.c.splice(0, n); } }
  at(t: number): Controls { let lo = 0, hi = this.t.length - 1, r = -1; while (lo <= hi) { const m = (lo + hi) >> 1; if (this.t[m] <= t) { r = m; lo = m + 1; } else hi = m - 1; } return r < 0 ? IDLE : this.c[r]; }
}

/** a history of numbers over time (the rover's poses), sampled by linear interpolation; `quats` lists the offsets of four-number quaternion groups, which are interpolated and renormalised */
export class History {
  private t: number[] = []; private v: Float64Array[] = [];
  constructor(readonly width: number, private quats: number[], private keepS = 12) {}
  push(t: number, values: ArrayLike<number>) {
    this.t.push(t); this.v.push(Float64Array.from(values));
    let n = 0; while (n < this.t.length - 2 && this.t[n + 1] < t - this.keepS) n++; if (n) { this.t.splice(0, n); this.v.splice(0, n); }
  }
  get length() { return this.t.length; }
  /** writes the state at time t into `out` (the oldest or newest when t is outside the history); false when the history is empty */
  sample(t: number, out: Float64Array) {
    const n = this.t.length; if (!n) return false;
    if (t <= this.t[0]) { out.set(this.v[0]); return true; }
    if (t >= this.t[n - 1]) { out.set(this.v[n - 1]); return true; }
    let lo = 0, hi = n - 1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (this.t[m] <= t) lo = m; else hi = m; }
    const a = this.v[lo], b = this.v[hi], k = (t - this.t[lo]) / (this.t[hi] - this.t[lo] || 1);
    for (let i = 0; i < this.width; i++) out[i] = a[i] + (b[i] - a[i]) * k;
    for (const o of this.quats) {      // the shorter way round, then renormalised
      const dot = a[o] * b[o] + a[o + 1] * b[o + 1] + a[o + 2] * b[o + 2] + a[o + 3] * b[o + 3], s = dot < 0 ? -1 : 1;
      let l = 0; for (let i = 0; i < 4; i++) { out[o + i] = a[o + i] + (s * b[o + i] - a[o + i]) * k; l += out[o + i] ** 2; }
      l = Math.sqrt(l) || 1; for (let i = 0; i < 4; i++) out[o + i] /= l;
    }
    return true;
  }
}

export interface PredPoint { x: number; z: number; headingDeg: number }
export interface Prediction { path: PredPoint[]; end: PredPoint; distance: number }

/** Where the rover will be when the command issued at `now` arrives, from the state the operator sees (the pose at now - delay, with its speed): the model of the drive is stepped through the
 *  commands in force at the rover over the next round trip, which are the ones issued from now - 2 delay to now (the command in force at the rover at time s was issued at s - delay). */
export function predict(start: PredPoint, startSpeed: number, log: ControlLog, now: number, delay: number, step = 0.05): Prediction {
  let { x, z, headingDeg: h } = start, duty = Math.max(-1, Math.min(1, startSpeed / V_FULL)), turnDuty = 0, distance = 0;
  const path: PredPoint[] = [{ x, z, headingDeg: h }];
  for (let s = now - delay; s < now + delay - 1e-9; s += step) {
    const c = log.at(s - delay), tgt = c.brake ? 0 : c.throttle, tgtTurn = c.brake ? 0 : c.turn, dd = SLEW * step;
    duty += Math.max(-dd, Math.min(dd, tgt - duty)); turnDuty += Math.max(-dd, Math.min(dd, tgtTurn - turnDuty));
    const v = duty * V_FULL; h = (((h + turnDuty * W_FULL * step) % 360) + 360) % 360;
    const dx = Math.sin((h * Math.PI) / 180) * v * step, dz = -Math.cos((h * Math.PI) / 180) * v * step;
    x += dx; z += dz; distance += Math.hypot(dx, dz); path.push({ x, z, headingDeg: h });
  }
  return { path, end: path[path.length - 1], distance };
}
