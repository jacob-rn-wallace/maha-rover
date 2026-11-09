/** How old and how out of date a mast camera still is, after Open MCT's imagery freshness indicators (docs/sim-ui-research.md): the **age** (fresh for a while after capture), the **position** (whether
 *  the rover has moved or turned since) and the **camera** (whether the pan-tilt head still points where it did). Thresholds: Open MCT's age window is 2 to 5 minutes by deployment: 2 minutes here;
 *  the position and camera tolerances (5 cm, 2 degrees of heading, 1 degree of pan or tilt) are look choices. No DOM and no three: tests/freshness-check.ts imports this file. */
export interface CamPose { t: number; x: number; z: number; headingDeg: number; panDeg: number; tiltDeg: number }

export const FRESH_S = 120, MOVE_M = 0.05, TURN_DEG = 2, HEAD_DEG = 1;

/** the smallest signed difference between two angles in degrees */
export const angleDiff = (a: number, b: number) => ((a - b + 540) % 360) - 180;
/** a bearing in degrees clockwise from north, from the world's east (x) and north (-z) components */
export const bearingDeg = (east: number, north: number) => (((Math.atan2(east, north) * 180) / Math.PI) % 360 + 360) % 360;
export const CARDINALS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"];
export const cardinal = (deg: number) => CARDINALS[Math.round((((deg % 360) + 360) % 360) / 45) % 8];

export interface Freshness { ageS: number; fresh: boolean; roverMoved: boolean; cameraMoved: boolean }
/** `then`: the pose when the still was taken; `now`: the pose and time now */
export function freshness(then: CamPose, now: CamPose): Freshness {
  const roverMoved = Math.hypot(now.x - then.x, now.z - then.z) > MOVE_M || Math.abs(angleDiff(now.headingDeg, then.headingDeg)) > TURN_DEG;
  const cameraMoved = Math.abs(now.panDeg - then.panDeg) > HEAD_DEG || Math.abs(now.tiltDeg - then.tiltDeg) > HEAD_DEG;
  const ageS = Math.max(0, (now.t - then.t) / 1000);
  return { ageS, fresh: ageS <= FRESH_S, roverMoved, cameraMoved };
}
export function formatAge(s: number) { return s < 60 ? `${s.toFixed(0)} s` : `${Math.floor(s / 60)} min ${Math.floor(s % 60)} s`; }
