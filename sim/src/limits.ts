/** Limits on the readouts: one table of yellow and red thresholds, evaluated for the HUD (and later the telemetry strips and the minimap), in the manner of Open MCT's telemetry limits.
 *  A level is OK (0), yellow (1) or red (2). The tilt thresholds are the tilt guard's own (constants.ts); the current thresholds are fractions of the 1.6 A cap; the battery and wall thresholds are
 *  look choices, not sourced (the wall one reuses the 100 m the HUD already warned at). No DOM and no three: the node check (tests/limits-check.ts) imports this file. */
import { MOTOR, TILT_CUT_DEG, TILT_BACK_DEG } from "./constants";

export const LIMITS = {
  battery: { label: "battery", unit: "%", below: true, yellow: 30, red: 15 },                                  // state of charge
  current: { label: "motor current", unit: "A", below: false, yellow: 0.75 * MOTOR.iCap, red: 0.95 * MOTOR.iCap },    // the largest of the four wheels (the cap clamps at 1.6 A)
  tilt: { label: "tilt", unit: "deg", below: false, yellow: TILT_BACK_DEG, red: TILT_CUT_DEG },                // the larger of |pitch| and |roll|
  wall: { label: "sandbox edge", unit: "m", below: true, yellow: 100, red: 20 },                                // distance to the hard wall ahead (the walls stand 20 m inside the tile edge)
} as const;
export type LimitId = keyof typeof LIMITS;
export type Level = 0 | 1 | 2;
export const LEVEL_COLOR = ["", "#ffb04a", "#ff6a5a"] as const;

export function level(id: LimitId, value: number): Level {
  const l = LIMITS[id];
  if (!isFinite(value)) return 0;
  const past = (t: number) => (l.below ? value < t : value >= t);
  return past(l.red) ? 2 : past(l.yellow) ? 1 : 0;
}

/** wraps html in the level's colour (unchanged at OK) */
export function paint(html: string, lv: Level) { return lv ? `<span style="color:${LEVEL_COLOR[lv]}">${html}</span>` : html; }

/** the readings the limits apply to; wall is undefined without the terrain */
export interface Readings { battery: number; current: number; tilt: number; wall?: number }
export function evaluate(r: Readings): Record<LimitId, Level> {
  return { battery: level("battery", r.battery), current: level("current", r.current), tilt: level("tilt", r.tilt), wall: r.wall === undefined ? 0 : level("wall", r.wall) };
}
