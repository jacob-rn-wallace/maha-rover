import RAPIER from "@dimforge/rapier3d-compat";
import * as THREE from "three";

/** al-maha physics (phase 2): rigid bodies and joints from rover.json, the differential as a stiff torque coupling of the two link plates,
 *  the Pololu 37D motor model on each wheel, PD-driven servos for the mast.  glTF axes (Y up, metres); wheel, link and tilt axes are +Z, pan is +Y.
 *  Sign conventions: forward is +X; a wheel turns forward for a NEGATIVE rotation about +Z (rover +Y is glTF -Z).
 */
export interface BodySpec {
  parent: string | null; origin_m: number[]; mass_kg: number; com_m: number[];
  inertia_principal_kgm2?: number[]; inertia_frame_quat_xyzw?: number[];
  collider_hull_points_m?: number[]; grouser_hulls_m?: number[][];
}
export interface Spec { total_mass_kg: number; wheel: { radius_m: number; width_m: number }; bodies: Record<string, BodySpec>; }

// ---- Pololu 37D #4746 (131.25:1) from docs/drive-spec.md: 76 rpm and 0.2 A no load at 12 V, 5.5 A stall at 12 V, 0.59 N.m at 0.74 A (best efficiency) ----
export const MOTOR = (() => {
  const N = 131.25, R = 12 / 5.5, i0 = 0.2;
  const wFree = (76 * 2 * Math.PI) / 60 * N;                 // motor shaft rad/s at 12 V, no load
  const Ke = (12 - R * i0) / wFree;                          // V.s/rad (equals the torque constant N.m/A in SI)
  const eta = 0.59 / (Ke * (0.74 - i0) * N);                 // gearbox efficiency implied by the datasheet point (about 0.75)
  const rotor = 1.0e-6;                                      // motor armature inertia kg.m2: ASSUMPTION (typical 37 mm brushed motor, not from the datasheet)
  return { N, R, i0, Ke, eta, iCap: 1.6, vBatt: 7.4, rotorReflected: rotor * N * N };       // 1.6 A current cap: docs/differential-spec.md; 7.4 V nominal 2S pack: docs/power-spec.md
})();

// ---- Feetech STS3215 (7.4 V): 19.5 kg.cm stall, 52 rpm no load (docs/electronics-spec.md); the PD gains are tuning choices ----
const PAN_LIMIT = (160 * Math.PI) / 180;      // the design's 320 degree pan stop (docs/mast-spec.md)
const SERVO = { tMax: 1.91, wMax: (52 * 2 * Math.PI) / 60 };

/** Duty slew rate, per second. The rover tips nose-over if it decelerates harder than g * (half wheelbase + centre of mass offset) / centre of mass height
 *  = 1.62 * 0.68 = 1.1 m/s2 on the Moon (CAD centre of mass z 235 mm, x +23 mm); at 0.53 m/s a full brake through the 1.6 A cap (about 5 m/s2) flips it in the first test.
 *  1.5 per second from full duty is about 0.8 m/s2. A design consequence: the motor controller firmware needs a deceleration limit. */
const DUTY_SLEW = 1.5;
const G_GROUND = 1, G_CHASSIS = 2, G_WHEEL = 4;
const groups = (member: number, filter: number) => (member << 16) | filter;
const v3 = (a: number[]) => ({ x: a[0], y: a[1], z: a[2] });

export interface Controls { throttle: number; turn: number; pan: number; tilt: number; brake: boolean; }
export const WHEELS = ["FL", "FR", "RL", "RR"] as const;

export class RoverPhysics {
  world!: RAPIER.World;
  bodies: Record<string, RAPIER.RigidBody> = {};
  readonly dt = 1 / 480;
  panTarget = 0; tiltTarget = 0;
  panAngle = 0; tiltAngle = 0;
  linkAngle = { L: 0, R: 0 };
  wheelCurrent: Record<string, number> = {};
  wheelRate: Record<string, number> = {};
  private duty: Record<string, number> = { FL: 0, FR: 0, RL: 0, RR: 0 };
  private acc = 0;
  private spec!: Spec;
  readonly gravity = 1.62;

  static async create(spec: Spec, spawnHeight = 0.03): Promise<RoverPhysics> {
    await RAPIER.init();
    const p = new RoverPhysics();
    p.spec = spec;
    p.world = new RAPIER.World({ x: 0, y: -p.gravity, z: 0 });
    p.world.integrationParameters.dt = p.dt;
    p.world.integrationParameters.numSolverIterations = 8;

    const ground = p.world.createRigidBody(RAPIER.RigidBodyDesc.fixed());
    p.world.createCollider(RAPIER.ColliderDesc.cuboid(500, 0.5, 500).setTranslation(0, -0.5, 0).setFriction(0.8).setRestitution(0)
      .setCollisionGroups(groups(G_GROUND, G_CHASSIS | G_WHEEL)), ground);

    const half = Math.SQRT1_2;
    for (const [name, b] of Object.entries(spec.bodies)) {
      const inertia = [...(b.inertia_principal_kgm2 ?? [1e-4, 1e-4, 1e-4])];
      if (name.startsWith("wheel")) inertia[2] += MOTOR.rotorReflected;     // the wheel's spin axis is its largest principal axis (index 2): add the motor rotor seen through the gearbox
      const desc = RAPIER.RigidBodyDesc.dynamic()
        .setTranslation(b.origin_m[0], b.origin_m[1] + spawnHeight, b.origin_m[2])
        .setCanSleep(false)
        .setAdditionalMassProperties(b.mass_kg, v3(b.com_m), v3(inertia),
          b.inertia_frame_quat_xyzw ? { x: b.inertia_frame_quat_xyzw[0], y: b.inertia_frame_quat_xyzw[1], z: b.inertia_frame_quat_xyzw[2], w: b.inertia_frame_quat_xyzw[3] } : { x: 0, y: 0, z: 0, w: 1 });
      const body = p.world.createRigidBody(desc);
      p.bodies[name] = body;
      if (b.collider_hull_points_m) {                                  // all colliders have zero density: mass comes from the CAD mass properties above
        const hull = RAPIER.ColliderDesc.convexHull(new Float32Array(b.collider_hull_points_m));
        if (hull) p.world.createCollider(hull.setDensity(0).setFriction(0.5).setRestitution(0).setCollisionGroups(groups(G_CHASSIS, G_GROUND)), body);
      }
      if (b.grouser_hulls_m) {
        p.world.createCollider(RAPIER.ColliderDesc.cylinder(spec.wheel.width_m / 2, spec.wheel.radius_m).setRotation({ x: half, y: 0, z: 0, w: half })
          .setDensity(0).setFriction(0.9).setRestitution(0).setCollisionGroups(groups(G_WHEEL, G_GROUND)), body);
        for (const h of b.grouser_hulls_m) {
          const c = RAPIER.ColliderDesc.convexHull(new Float32Array(h));
          if (c) p.world.createCollider(c.setDensity(0).setFriction(0.9).setRestitution(0).setCollisionGroups(groups(G_WHEEL, G_GROUND)), body);
        }
      }
    }
    // joints: each child's origin is its joint point; every body starts unrotated, so the same axis serves both local frames
    const rev = (parent: string, child: string, axis: number[]) => {
      const a = spec.bodies[child].origin_m.map((x, i) => x - spec.bodies[parent].origin_m[i]);
      p.world.createImpulseJoint(RAPIER.JointData.revolute(v3(a), { x: 0, y: 0, z: 0 }, v3(axis)), p.bodies[parent], p.bodies[child], true);
    };
    rev("chassis", "linkL", [0, 0, 1]);
    rev("chassis", "linkR", [0, 0, 1]);
    for (const w of WHEELS) rev("link" + w[1], "wheel" + w, [0, 0, 1]);
    rev("chassis", "pan", [0, 1, 0]);
    rev("pan", "head", [0, 0, 1]);
    return p;
  }

  private rel(parent: string, child: string, axis: THREE.Vector3) {
    const bp = this.bodies[parent], bc = this.bodies[child];
    const qp = new THREE.Quaternion(bp.rotation().x, bp.rotation().y, bp.rotation().z, bp.rotation().w);
    const qc = new THREE.Quaternion(bc.rotation().x, bc.rotation().y, bc.rotation().z, bc.rotation().w);
    const q = qp.clone().invert().multiply(qc);
    const s = axis.x * q.x + axis.y * q.y + axis.z * q.z;            // twist about the axis
    const angle = 2 * Math.atan2(s, q.w);
    const axW = axis.clone().applyQuaternion(qp);
    const wp = bp.angvel(), wc = bc.angvel();
    const rate = (wc.x - wp.x) * axW.x + (wc.y - wp.y) * axW.y + (wc.z - wp.z) * axW.z;
    return { angle: ((angle + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI, rate, axW };
  }

  private torquePair(parent: string, child: string, axW: THREE.Vector3, tau: number) {
    this.bodies[child].addTorque({ x: axW.x * tau, y: axW.y * tau, z: axW.z * tau }, true);
    this.bodies[parent].addTorque({ x: -axW.x * tau, y: -axW.y * tau, z: -axW.z * tau }, true);
  }

  private substep(c: Controls) {
    for (const b of Object.values(this.bodies)) b.resetTorques(false);
    const Z = new THREE.Vector3(0, 0, 1), Y = new THREE.Vector3(0, 1, 0);

    // differential: the two link plates are coupled so that angle L + angle R = 0 (bevel gear differential, 1:1), as a stiff spring and damper
    const L = this.rel("chassis", "linkL", Z), R = this.rel("chassis", "linkR", Z);
    this.linkAngle = { L: L.angle, R: R.angle };
    const tauC = -(600 * (L.angle + R.angle) + 6 * (L.rate + R.rate));
    this.torquePair("chassis", "linkL", L.axW, tauC);
    this.torquePair("chassis", "linkR", R.axW, tauC);

    // wheels: skid steering from throttle and turn; the 37D model with the current cap; a forward turn is negative about +Z
    const m = MOTOR;
    for (const w of WHEELS) {
      const side = w[1] === "L" ? 1 : -1;
      const target = c.brake ? 0 : Math.max(-1, Math.min(1, c.throttle + side * c.turn));
      const du = Math.max(-DUTY_SLEW * this.dt, Math.min(DUTY_SLEW * this.dt, target - this.duty[w]));      // firmware-style slew limit: unlimited braking tips the rover (see below)
      const u = (this.duty[w] += du);
      const r = this.rel("link" + w[1], "wheel" + w, Z);
      const wm = -r.rate * m.N;                                       // motor shaft speed, forward positive
      let i = (u * m.vBatt - m.Ke * wm) / m.R;
      i = Math.max(-m.iCap, Math.min(m.iCap, i));
      this.wheelCurrent[w] = i;
      this.wheelRate[w] = -r.rate;
      const tm = m.Ke * (i - Math.sign(wm || i) * m.i0 * (Math.abs(i) > 1e-6 ? 1 : 0));
      const tOut = m.N * tm * (tm * wm >= 0 ? m.eta : 1 / m.eta);
      this.torquePair("link" + w[1], "wheel" + w, r.axW, -tOut);
    }

    // servos: a PD loop on the target angle, torque limited to the stall torque, target moved at the no-load speed
    const dtc = this.dt;
    this.panTarget = Math.max(-PAN_LIMIT, Math.min(PAN_LIMIT, this.panTarget + c.pan * SERVO.wMax * dtc));
    this.tiltTarget = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, this.tiltTarget + c.tilt * SERVO.wMax * dtc));
    const P = this.rel("chassis", "pan", Y), T = this.rel("pan", "head", Z);
    this.panAngle = P.angle; this.tiltAngle = T.angle;
    const clampT = (x: number) => Math.max(-SERVO.tMax, Math.min(SERVO.tMax, x));
    this.torquePair("chassis", "pan", P.axW, clampT(8 * (this.panTarget - P.angle) - 0.15 * P.rate));
    this.torquePair("pan", "head", T.axW, clampT(6 * (this.tiltTarget - T.angle) - 0.1 * T.rate));
    this.world.step();
  }

  /** advance by wall-clock seconds (clamped), in fixed substeps */
  advance(seconds: number, c: Controls) {
    this.acc += Math.min(seconds, 0.05);
    while (this.acc >= this.dt) { this.substep(c); this.acc -= this.dt; }
  }
}
