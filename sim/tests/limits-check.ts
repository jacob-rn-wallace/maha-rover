/** Checks the limit table (src/limits.ts): `npm run check:limits`. Exits non-zero on a failure. */
import { level, evaluate, LIMITS } from "../src/limits";
import { MOTOR, TILT_CUT_DEG, TILT_BACK_DEG } from "../src/constants";

let bad = 0;
const eq = (name: string, got: unknown, want: unknown) => { const ok = got === want; if (!ok) bad++; console.log(ok ? "ok  " : "FAIL", name, ok ? "" : `got ${got}, want ${want}`); };

eq("battery 100% ok", level("battery", 100), 0);
eq("battery 30% ok (below is strict)", level("battery", 30), 0);
eq("battery 29% yellow", level("battery", 29), 1);
eq("battery 14% red", level("battery", 14), 2);
eq("tilt just under the guard's resume angle", level("tilt", TILT_BACK_DEG - 0.1), 0);
eq("tilt at the resume angle yellow", level("tilt", TILT_BACK_DEG), 1);
eq("tilt at the cut angle red", level("tilt", TILT_CUT_DEG), 2);
eq("current at 50% of the cap ok", level("current", 0.5 * MOTOR.iCap), 0);
eq("current at 80% yellow", level("current", 0.8 * MOTOR.iCap), 1);
eq("current at the cap red", level("current", MOTOR.iCap), 2);
eq("wall 150 m ok", level("wall", 150), 0);
eq("wall 99 m yellow", level("wall", 99), 1);
eq("wall 10 m red", level("wall", 10), 2);
eq("NaN is ok", level("tilt", NaN), 0);
eq("no terrain: wall level 0", evaluate({ battery: 100, current: 0, tilt: 0 }).wall, 0);
eq("thresholds ordered (yellow before red)", (Object.values(LIMITS) as any[]).every((l) => (l.below ? l.yellow > l.red : l.yellow < l.red)), true);
process.exit(bad ? 1 : 0);
