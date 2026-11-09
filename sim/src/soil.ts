/** Wheel-soil force model: what the soil does to one wheel, as a function of its normal load and its slip, replacing Coulomb friction at the wheels.
 *
 *  Source of every number: Hurrell et al., "Traction Performance Evaluation for a Rashid-1 Rover Wheel", Space Science Reviews 221:37 (2025), doi 10.1007/s11214-025-01164-8
 *  (papers/S4 in the private library): single-wheel experiments and DEM simulations of the Rashid-1 wheel (rim radius 100 mm, width 80 mm, 14 grousers of 20 mm, 1.18 kg)
 *  in FJS-1 lunar simulant at about 25% relative density (bulk density 1740 kg/m3, angle of repose 38 degrees, cohesion 2.4 kPa), at the rover's load of 24.5 N per wheel on Earth,
 *  and the DEM at 4.1 N in lunar gravity. The paper's Table 4 (lunar columns, FJS-1 DEM) is the target; its Fig. 5 shows the experiment 10 to 15% below the DEM at 30 to 50% slip.
 *  Its finding that the traction coefficient (net drawbar pull / load) is the same on Earth and on the Moon, while forces scale with gravity, is why the model is per unit load.
 *
 *  Table 4 (lunar, FJS-1), slip s = (w R_rim - v) / (w R_rim) at 0, 10, 20, 30, 40, 50 %:
 *    net pull / load      0.28 0.34 0.38 0.42 0.45 0.49
 *    wheel torque, N.m    0.22 0.26 0.29 0.31 0.32 0.35   (at a load of 4.07 N and R 0.1 m: gross thrust / load 0.54 0.64 0.71 0.76 0.79 0.86)
 *    total sinkage, mm    5.1  7.8  11.2 15.6 20.5 26.5
 *  Gross thrust is the torque over R, the resistance is gross thrust minus net pull (0.26 0.30 0.33 0.34 0.34 0.37 of the load).
 *
 *  Derived here (not in the paper): the paper's slip is referred to the rim, but the grousers (tip radius 1.2 R on the test wheel) set the kinematic radius, so the thrust
 *  at "0% slip" is not zero. Referring slip to the tip radius, s_e = 1 - (1 - s) / 1.2, the thrust is zero at s_e = 0 and the six points fit a Janosi-Hanamoto shear curve
 *  T = T_MAX (1 - exp(-s_e / K_SLIP)) with T_MAX = 0.86 and K_SLIP = 0.18 (least squares; tan 38 degrees = 0.78, and the cohesion adds to it). The resistance
 *  fits 0.237 + 0.229 s_e. The net pull T - resistance is within 0.04 of the load at all six points. The flight wheel's grousers are 15 mm, not 20 (tip radius 1.15 R): the same curve is used with the sim wheel's own tip radius.
 *  The sinkage is not simulated (the ground is rigid): its effect on the motion is in the resistance. It is returned for display.
 */
export interface Soil {
  name: string;
  thrustMax: number;       // limit of gross thrust / load at large slip
  kSlip: number;           // slip over which the thrust builds up (shear displacement over contact length)
  resist0: number;         // motion resistance / load at zero slip
  resistSlope: number;     // and its growth with slip
  vMin: number;            // m/s: slip is referred to at least this speed, so a wheel at rest has no slip
  sinkage: [number, number][];   // (slip s_e, total sinkage mm) for display
}

export const FJS1: Soil = {
  name: "FJS-1 simulant, Hurrell et al. 2025 Table 4 (lunar gravity DEM)",
  thrustMax: 0.86, kSlip: 0.18, resist0: 0.237, resistSlope: 0.229, vMin: 0.02,
  sinkage: [[0.167, 5.1], [0.25, 7.8], [0.333, 11.2], [0.417, 15.6], [0.5, 20.5], [0.583, 26.5]],
};

export interface SoilForce {
  thrust: number;     // N along the wheel's rolling direction (positive forward), acts at the contact point
  side: number;       // N along the axle, acts at the contact point
  resist: number;     // N opposing the hub's motion (a magnitude, acts against the hub velocity)
  slip: number;       // tip-referred longitudinal slip s_e, -1 to 1
  sinkage: number;    // mm
}

/** n: normal load (N); u: rim speed of the grouser tips w * R_tip (forward positive); vx: hub speed along the rolling direction; vy: hub speed along the axle */
export function soilForce(soil: Soil, n: number, u: number, vx: number, vy: number): SoilForce {
  const ref = Math.max(Math.abs(u), Math.abs(vx), soil.vMin);
  const sx = Math.max(-1, Math.min(1, (u - vx) / ref));
  const sy = vy / ref;
  const m = Math.hypot(sx, sy);
  const f = n * soil.thrustMax * (1 - Math.exp(-m / soil.kSlip));              // the force magnitude, along the slip direction (combined slip)
  const thrust = m > 1e-9 ? f * sx / m : 0, side = m > 1e-9 ? -f * sy / m : 0;
  const s = Math.max(0, sx);
  const resist = n * (soil.resist0 + soil.resistSlope * s) * Math.tanh(Math.abs(vx) / 0.01);
  let sink = 0;
  const t = soil.sinkage;
  if (s <= t[0][0]) sink = t[0][1] * s / t[0][0];
  else if (s >= t[t.length - 1][0]) sink = t[t.length - 1][1];
  else for (let i = 1; i < t.length; i++) if (s <= t[i][0]) { const w = (s - t[i - 1][0]) / (t[i][0] - t[i - 1][0]); sink = t[i - 1][1] + w * (t[i][1] - t[i - 1][1]); break; }
  return { thrust, side, resist, slip: sx, sinkage: sink };
}
