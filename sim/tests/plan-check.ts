/** Checks the route planning logic (src/plan.ts): `npm run check:plan`. Exits non-zero on a failure. */
import { metrics, solarWatts, bestSolarHeading, footprint, Route, bearingTo, turn, SPEED, TURN_RATE, DRIVE_W } from "../src/plan";

let bad = 0;
const near = (name: string, got: number, want: number, tol = 1e-6) => { const ok = Math.abs(got - want) <= tol; if (!ok) bad++; console.log(ok ? "ok  " : "FAIL", name, ok ? "" : `got ${got}, want ${want}`); };
const eq = (name: string, got: unknown, want: unknown) => { const ok = got === want; if (!ok) bad++; console.log(ok ? "ok  " : "FAIL", name, ok ? "" : `got ${got}, want ${want}`); };

near("bearing due north is 0 (z decreases)", bearingTo(0, 0, 0, -10), 0);
near("bearing due east is 90", bearingTo(0, 0, 10, 0), 90);
near("bearing south-west is 225", bearingTo(0, 0, -1, 1), 225);
eq("turn from 350 to 10 is +20 (right)", turn(350, 10), 20);
eq("turn from 10 to 350 is -20 (left)", turn(10, 350), -20);

// 10 m north of a rover that faces north and ends facing east: no turn to travel, a 90 degree turn at the end
const m = metrics({ x: 0, z: 0, headingDeg: 0 }, [{ x: 0, z: -10, headingDeg: 90 }]);
near("distance 10 m", m.distanceM, 10); near("turn 90 deg", m.turnDeg, 90);
near("time = distance / speed + turn / rate", m.seconds, 10 / SPEED + 90 / TURN_RATE);
near("energy = power x time", m.wh, (DRIVE_W * (10 / SPEED + 90 / TURN_RATE)) / 3600);
const m2 = metrics({ x: 0, z: 0, headingDeg: 0 }, [{ x: 10, z: 0, headingDeg: 90 }]);
near("facing north, waypoint east: a 90 degree right turn first", m2.legs[0].turnToTravel, 90);
near("two legs add up", metrics({ x: 0, z: 0, headingDeg: 0 }, [{ x: 0, z: -3, headingDeg: 0 }, { x: 4, z: -3, headingDeg: 0 }]).distanceM, 7);

// solar: sun due east at 14 degrees; a rover facing north has its right panel facing east, the best heading is north or south
const best = bestSolarHeading(90, 14, 0);
near("best heading with the sun in the east and a northward path is north", best.headingDeg % 360, 0, 1);
const bestS = bestSolarHeading(90, 14, 180);
near("with a southward path, south", bestS.headingDeg, 180, 1);
eq("facing the sun end-on gives less than broadside", solarWatts(90, 90, 14) < solarWatts(0, 90, 14), true);
near("both choices give the same power", solarWatts(0, 90, 14), solarWatts(180, 90, 14), 1e-9);

// footprint: camera 0.667 m up, level, looking north from the origin
const f = footprint(0, 0, 0);
near("near edge at h / tan(30.7 deg)", -f[0][1], 0.667 / Math.tan((30.7 * Math.PI) / 180), 1e-6);
near("far edge at the 15 m cap (the top ray is above the horizon)", -f[3][1], 15);
near("left of the picture is west", f[0][0] < 0 ? 1 : 0, 1); near("near edge narrower than far", Math.abs(f[1][0] - f[0][0]) < Math.abs(f[2][0] - f[3][0]) ? 1 : 0, 1);
const fd = footprint(0, 0, 0, 0.667, 45);
near("pitched 45 degrees down the far edge is closer than the cap", -fd[3][1] < 15 ? 1 : 0, 1);

// route: add, guide, arrive, remove
const r = new Route(); r.add({ x: 0, z: -10, headingDeg: 0 }); r.add({ x: 5, z: -10, headingDeg: 90 });
let g = r.guide({ x: 0, z: 0, headingDeg: 0 })!;
eq("guide to waypoint 0 first", g.index, 0); near("distance 10", g.distance, 10); near("dead ahead", g.turn, 0);
g = r.guide({ x: 0, z: -9, headingDeg: 0 })!; eq("within 1.5 m: waypoint 0 reached, next is 1", g.index, 1);
eq("past the last waypoint there is no guidance", r.guide({ x: 5, z: -10, headingDeg: 90 }), null);
r.clear(); r.add({ x: 1, z: 1, headingDeg: 0 }); r.add({ x: 2, z: 2, headingDeg: 0 });
eq("near finds a waypoint", r.near(2.2, 2.1, 1), 1); eq("near returns -1 when none", r.near(50, 50, 1), -1);
r.remove(0); eq("remove keeps the rest", r.wps.length, 1);
process.exit(bad ? 1 : 0);
