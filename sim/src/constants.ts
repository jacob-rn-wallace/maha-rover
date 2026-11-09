/** Constants the page needs without loading the physics engine (physics.ts pulls in Rapier and its WASM). */
export const WHEELS = ["FL", "FR", "RL", "RR"] as const;

// ---- Pololu 37D #4746 (131.25:1) from docs/drive-spec.md: 76 rpm and 0.2 A no load at 12 V, 5.5 A stall at 12 V, 0.59 N.m at 0.74 A (best efficiency) ----
export const MOTOR = (() => {
  const N = 131.25, R = 12 / 5.5, i0 = 0.2;
  const wFree = (76 * 2 * Math.PI) / 60 * N;                 // motor shaft rad/s at 12 V, no load
  const Ke = (12 - R * i0) / wFree;                          // V.s/rad (equals the torque constant N.m/A in SI)
  const eta = 0.59 / (Ke * (0.74 - i0) * N);                 // gearbox efficiency implied by the datasheet point (about 0.75)
  const rotor = 1.0e-6;                                      // motor armature inertia kg.m2: ASSUMPTION (typical 37 mm brushed motor, not from the datasheet)
  return { N, R, i0, Ke, eta, iCap: 1.6, vBatt: 7.4, rotorReflected: rotor * N * N };       // 1.6 A current cap: docs/differential-spec.md; 7.4 V nominal 2S pack: docs/power-spec.md
})();

/** Tilt guard thresholds in degrees (physics.ts cuts the drive past CUT until the tilt is back under BACK; the HUD's tilt limit uses the same two numbers) */
export const TILT_CUT_DEG = 25, TILT_BACK_DEG = 15;
