/** Power model: the 2S2P pack of docs/power-spec.md, the loads on it and the solar input, integrated in time.
 *  Sourced: 4 x Samsung INR18650-30Q (3000 mAh each: retailer figures in power-spec.md), Pi, camera and 5 V converter 0.8 A at 7.4 V (power-spec.md, itself an assumption), solar module 9.6 W at one sun per side (solar-spec.md).
 *  ASSUMPTIONS, not sourced: the open-circuit curve (linear 8.4 V full to 6.4 V empty: a 30Q's real curve is flatter in the middle and steeper at the ends), pack resistance 0.05 ohm (two cells in parallel
 *  at about 25 mohm each in series, plus wiring and the BMS), servo draw 0.3 A moving and 0.04 A holding, charger efficiency 0.9, panel normals 10 degrees above the horizontal side directions (the panels lean at 80 degrees).
 *  Solar input ignores shadows and the lunar day's real sun: it uses the sim's fixed sun and the chassis attitude.
 */
import * as THREE from "three";

export const PACK = { capacityAh: 6.0, vFull: 8.4, vEmpty: 6.4, rInt: 0.05, vNominal: 7.4 };
const PI_AMPS = 0.8, SERVO_MOVING_AMPS = 0.3, SERVO_HOLD_AMPS = 0.04;
const SOLAR_W_PER_SIDE = 9.6, CHARGER_EFF = 0.9;
const TILT = Math.PI / 18;

export class Power {
  chargeAh = PACK.capacityAh;
  volts = PACK.vFull;
  loadAmps = 0;            // drawn from the pack by drive, computer and servos
  solarW = 0;              // delivered by the charger to the pack node
  netAmps = 0;             // positive = discharging
  private n = [new THREE.Vector3(0, Math.sin(TILT), 1), new THREE.Vector3(0, Math.sin(TILT), -1)];

  get soc() { return Math.max(0, this.chargeAh / PACK.capacityAh); }
  get wattsLoad() { return this.loadAmps * this.volts; }
  get minutesLeft() { return this.netAmps > 0.01 ? (this.chargeAh / this.netAmps) * 60 : Infinity; }

  /** sunDir: unit vector towards the sun (world); q: chassis orientation; motorAmps: pack current of the drive */
  step(dt: number, motorAmps: number, servoMoving: boolean, sunDir: THREE.Vector3, q: THREE.Quaternion) {
    let sw = 0;
    for (const n of this.n) sw += SOLAR_W_PER_SIDE * Math.max(0, n.clone().applyQuaternion(q).dot(sunDir));
    this.solarW = sw * CHARGER_EFF;
    this.loadAmps = motorAmps + PI_AMPS + (servoMoving ? SERVO_MOVING_AMPS : SERVO_HOLD_AMPS);
    const ocv = PACK.vEmpty + (PACK.vFull - PACK.vEmpty) * this.soc;
    const solarAmps = this.solarW / Math.max(ocv, 1);
    this.netAmps = this.loadAmps - solarAmps;
    this.volts = Math.max(0, ocv - this.loadAmps * PACK.rInt);
    this.chargeAh = Math.min(PACK.capacityAh, Math.max(0, this.chargeAh - this.netAmps * dt / 3600));
  }
}
