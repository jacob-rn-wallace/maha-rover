/** Checks the camera-still freshness logic (src/freshness.ts): `npm run check:freshness`. Exits non-zero on a failure. */
import { freshness, angleDiff, bearingDeg, cardinal, formatAge, type CamPose } from "../src/freshness";

let bad = 0;
const eq = (name: string, got: unknown, want: unknown) => { const ok = got === want; if (!ok) bad++; console.log(ok ? "ok  " : "FAIL", name, ok ? "" : `got ${got}, want ${want}`); };
const p = (o: Partial<CamPose> = {}): CamPose => ({ t: 0, x: 0, z: 0, headingDeg: 0, panDeg: 0, tiltDeg: 0, ...o });

eq("same pose, just taken: fresh, nothing moved", JSON.stringify(freshness(p(), p())), JSON.stringify({ ageS: 0, fresh: true, roverMoved: false, cameraMoved: false }));
eq("119 s old is fresh", freshness(p(), p({ t: 119000 })).fresh, true);
eq("121 s old is stale", freshness(p(), p({ t: 121000 })).fresh, false);
eq("4 cm is not a move", freshness(p(), p({ x: 0.04 })).roverMoved, false);
eq("6 cm is a move", freshness(p(), p({ z: 0.06 })).roverMoved, true);
eq("3 degrees of heading is a move", freshness(p(), p({ headingDeg: 3 })).roverMoved, true);
eq("heading across north: 359 to 1 is 2 degrees, not a move", freshness(p({ headingDeg: 359 }), p({ headingDeg: 1 })).roverMoved, false);
eq("pan 2 degrees moves the camera", freshness(p(), p({ panDeg: 2 })).cameraMoved, true);
eq("tilt 0.5 degrees does not", freshness(p(), p({ tiltDeg: 0.5 })).cameraMoved, false);
eq("angleDiff wraps", angleDiff(350, 10), -20);
eq("bearing east is 90", Math.round(bearingDeg(1, 0)), 90);
eq("bearing north is 0", Math.round(bearingDeg(0, 1)), 0);
eq("bearing south-west is 225", Math.round(bearingDeg(-1, -1)), 225);
eq("cardinal 350 is N", cardinal(350), "N");
eq("cardinal 100 is E", cardinal(100), "E");
eq("age text under a minute", formatAge(12.4), "12 s");
eq("age text over a minute", formatAge(192), "3 min 12 s");
process.exit(bad ? 1 : 0);
