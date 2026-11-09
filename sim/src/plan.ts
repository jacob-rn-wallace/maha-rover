/** Route planning (docs/sim-ui-layout.md, Plan mode; docs/sim-ui-research.md, step 4): waypoints with headings, the path and its cost, the heading that best faces the solar panels to the sun, the mast camera's
 *  footprint on the ground, and the guidance to the next waypoint. Pure (no DOM, no three): tests/plan-check.ts imports this file.
 *  World axes: x east, z south, so a bearing (degrees clockwise from north) points along (sin b, -cos b) in (x, z). */
import { angleDiff, bearingDeg } from "./freshness";
import { SOLAR_W_PER_SIDE, CHARGER_EFF, TILT, PACK } from "./power";

export interface Waypoint { x: number; z: number; headingDeg: number }
export interface Pose { x: number; z: number; headingDeg: number }

/** Estimates. SPEED: the sim's full-throttle speed on flat rigid ground (0.527 m/s, `?test=1`). TURN_RATE: the sim turns in place at about 100 deg/s at full command on flat rigid ground (`?test=1`); 60 deg/s
 *  is an assumed operating rate (soil losses are not measured). DRIVE_W: about 2 A at 7 V, the flat-driving draw in docs/sim-spec.md (an assumption), used for turning too. Slope, soil and rocks are not in the estimate. */
export const SPEED = 0.5, TURN_RATE = 60, DRIVE_W = 14, ARRIVE_M = 1.5;
export const PACK_WH = PACK.capacityAh * PACK.vNominal;

export const forward = (bearing: number): [number, number] => [Math.sin((bearing * Math.PI) / 180), -Math.cos((bearing * Math.PI) / 180)];
/** bearing from (x0, z0) to (x1, z1) */
export const bearingTo = (x0: number, z0: number, x1: number, z1: number) => bearingDeg(x1 - x0, -(z1 - z0));
/** a signed turn in degrees (positive is clockwise, a right turn) from one heading to another */
export const turn = (from: number, to: number) => angleDiff(to, from);

export interface Leg { distance: number; travelBearing: number; turnToTravel: number; turnToHeading: number }
export interface Metrics { legs: Leg[]; distanceM: number; turnDeg: number; seconds: number; wh: number; batteryPct: number }

/** the legs from a start pose through the waypoints: turn to face the waypoint, drive, turn to its heading */
export function metrics(start: Pose, wps: Waypoint[]): Metrics {
  const legs: Leg[] = []; let p: Pose = start, distance = 0, turned = 0;
  for (const w of wps) {
    const d = Math.hypot(w.x - p.x, w.z - p.z), tb = d > 0.05 ? bearingTo(p.x, p.z, w.x, w.z) : p.headingDeg;
    const t1 = turn(p.headingDeg, tb), t2 = turn(tb, w.headingDeg);
    legs.push({ distance: d, travelBearing: tb, turnToTravel: t1, turnToHeading: t2 }); distance += d; turned += Math.abs(t1) + Math.abs(t2); p = w;
  }
  const seconds = distance / SPEED + turned / TURN_RATE, wh = (DRIVE_W * seconds) / 3600;
  return { legs, distanceM: distance, turnDeg: turned, seconds, wh, batteryPct: (wh / PACK_WH) * 100 };
}

/** the solar power a flat rover delivers at a heading: each side panel's normal (10 degrees above the horizon, on the body's right and left) against the sun (bearing and elevation, degrees) */
export function solarWatts(headingDeg: number, sunBearing: number, sunElDeg: number) {
  const el = (sunElDeg * Math.PI) / 180, s = [Math.cos(el) * Math.sin((sunBearing * Math.PI) / 180), Math.sin(el), -Math.cos(el) * Math.cos((sunBearing * Math.PI) / 180)];
  let w = 0;
  for (const side of [90, -90]) { const [nx, nz] = forward(headingDeg + side), n = [nx * Math.cos(TILT), Math.sin(TILT), nz * Math.cos(TILT)]; w += SOLAR_W_PER_SIDE * Math.max(0, n[0] * s[0] + n[1] * s[1] + n[2] * s[2]); }
  return w * CHARGER_EFF;
}
/** the heading with the most solar power; the two sides are equivalent, so the one nearer `near` (the travel direction) is returned */
export function bestSolarHeading(sunBearing: number, sunElDeg: number, near = 0) {
  let best = 0, bw = -1;
  for (let h = 0; h < 360; h += 1) { const w = solarWatts(h, sunBearing, sunElDeg) - Math.abs(angleDiff(h, near)) * 1e-6; if (w > bw) { bw = w; best = h; } }
  return { headingDeg: best, watts: solarWatts(best, sunBearing, sunElDeg) };
}

/** The mast camera's footprint on flat ground: the quadrilateral (near left, near right, far right, far left; world x, z) the picture covers for a camera `heightM` up, looking along `bearing`
 *  pitched `pitchDownDeg` below the horizon, out to at most `rangeM` (VERVE's hazard maps reach 1 to 15 m). Field of view 76.6 x 61.4 degrees (docs/mast-spec.md). */
export function footprint(x: number, z: number, bearing: number, heightM = 0.667, pitchDownDeg = 0, rangeM = 15, hfovDeg = 76.6, vfovDeg = 61.4): [number, number][] {
  const r = (d: number) => (d * Math.PI) / 180, phi = r(pitchDownDeg), bottom = phi + r(vfovDeg / 2), top = phi - r(vfovDeg / 2), a = Math.tan(r(hfovDeg / 2));
  const near = Math.min(rangeM, heightM / Math.tan(bottom)), far = top > 0.02 ? Math.min(rangeM, heightM / Math.tan(top)) : rangeM;
  const half = (d: number) => (d * Math.cos(phi) + heightM * Math.sin(phi)) * a;      // the picture's half width at ground distance d: the distance along the axis times tan(half the horizontal field)
  const [fx, fz] = forward(bearing), [rx, rz] = forward(bearing + 90), pt = (d: number, s: number): [number, number] => [x + fx * d + rx * s, z + fz * d + rz * s];
  return [pt(near, -half(near)), pt(near, half(near)), pt(far, half(far)), pt(far, -half(far))];
}

/** The route: waypoints, a selection and the next waypoint to drive to. */
export class Route {
  wps: Waypoint[] = []; selected = -1; next = 0;
  version = 0;      // counts changes, so the views know when to redraw

  add(w: Waypoint) { this.wps.push(w); this.selected = this.wps.length - 1; this.version++; return this.selected; }
  select(i: number) { if (i !== this.selected) { this.selected = i; this.version++; } }
  setHeading(i: number, headingDeg: number) { if (this.wps[i]) { this.wps[i].headingDeg = ((headingDeg % 360) + 360) % 360; this.version++; } }
  remove(i: number) { if (i < 0 || i >= this.wps.length) return; this.version++; this.wps.splice(i, 1); this.selected = Math.min(this.selected, this.wps.length - 1); if (this.next > i) this.next--; this.next = Math.min(this.next, this.wps.length); }
  undo() { this.remove(this.wps.length - 1); }
  clear() { this.wps = []; this.selected = -1; this.next = 0; this.version++; }
  /** the index of the waypoint within `m` metres of (x, z), or -1 */
  near(x: number, z: number, m: number) { let b = -1, bd = m; this.wps.forEach((w, i) => { const d = Math.hypot(w.x - x, w.z - z); if (d < bd) { bd = d; b = i; } }); return b; }

  /** advances past the waypoints the rover has reached; returns the guidance to the next one, or null when there is none */
  guide(p: Pose) {
    while (this.next < this.wps.length && Math.hypot(this.wps[this.next].x - p.x, this.wps[this.next].z - p.z) < ARRIVE_M) this.next++;
    if (this.next >= this.wps.length) return null;
    const w = this.wps[this.next], b = bearingTo(p.x, p.z, w.x, w.z);
    return { index: this.next, count: this.wps.length, distance: Math.hypot(w.x - p.x, w.z - p.z), bearing: b, turn: turn(p.headingDeg, b) };
  }
}
