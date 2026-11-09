import * as THREE from "three";

/** The camera-link cable as a rope (the exporter drops its mesh; rover.json `cable` has its centre line): Verlet points with stretch constraints and "shape memory" ones (every second and third neighbour keeps its rest distance),
 *  so it hangs in its designed loop and swings as the head pans and tilts or the rover moves. The two ends are pinned: one to the head (it tilts), one to the chassis' deck gland.
 *  Gravity is the Moon's. No collision with the body or the ground (the loop hangs clear of both in the CAD). Drawn as a round tube, rebuilt each frame. */
export interface CableSpec { radius_m: number; colour_srgb: number[]; points_m: number[][]; head_end_m: number[]; chassis_end_m: number[] }

const SIDES = 8, STEP = 1 / 120, ITER = 8, DAMP = 0.985, SKIP_K = 0.6;

export class Cable {
  readonly mesh: THREE.Mesh;
  private n: number; private p: THREE.Vector3[]; private q: THREE.Vector3[];
  private d1: number[]; private d2: number[]; private d3: number[];
  private ready = false; private acc = 0;
  private pos: Float32Array; private nor: Float32Array; private geo = new THREE.BufferGeometry();
  private tmp = new THREE.Vector3(); private headEnd: THREE.Vector3; private chassisEnd: THREE.Vector3;
  constructor(private spec: CableSpec, private chassis: THREE.Object3D, private head: THREE.Object3D, private gravity = 1.62) {
    const pts = spec.points_m.map((a) => new THREE.Vector3(a[0], a[1], a[2]));
    this.n = pts.length; this.p = pts.map((v) => v.clone()); this.q = pts.map((v) => v.clone());
    this.d1 = pts.slice(1).map((v, i) => v.distanceTo(pts[i]));
    this.d2 = pts.slice(2).map((v, i) => v.distanceTo(pts[i]));
    this.d3 = pts.slice(3).map((v, i) => v.distanceTo(pts[i]));
    this.headEnd = new THREE.Vector3(...(spec.head_end_m as [number, number, number])); this.chassisEnd = new THREE.Vector3(...(spec.chassis_end_m as [number, number, number]));
    this.pos = new Float32Array(this.n * SIDES * 3); this.nor = new Float32Array(this.n * SIDES * 3);
    const idx: number[] = [];
    for (let i = 0; i < this.n - 1; i++) for (let s = 0; s < SIDES; s++) {
      const a = i * SIDES + s, b = i * SIDES + (s + 1) % SIDES, c = a + SIDES, d = b + SIDES;
      idx.push(a, c, b, b, c, d);
    }
    this.geo.setAttribute("position", new THREE.BufferAttribute(this.pos, 3).setUsage(THREE.DynamicDrawUsage));
    this.geo.setAttribute("normal", new THREE.BufferAttribute(this.nor, 3).setUsage(THREE.DynamicDrawUsage));
    this.geo.setIndex(idx);
    const lin = (c: number) => Math.pow(c / 255, 2.2);
    const mat = new THREE.MeshStandardMaterial({ color: new THREE.Color(lin(spec.colour_srgb[0]), lin(spec.colour_srgb[1]), lin(spec.colour_srgb[2])), roughness: 0.55, metalness: 0 });
    this.mesh = new THREE.Mesh(this.geo, mat);
    this.mesh.frustumCulled = false; this.mesh.castShadow = true; this.mesh.receiveShadow = true;
  }

  private pin() {
    this.p[0].copy(this.headEnd).applyMatrix4(this.head.matrixWorld);
    this.p[this.n - 1].copy(this.chassisEnd).applyMatrix4(this.chassis.matrixWorld);
  }
  private pull(a: THREE.Vector3, b: THREE.Vector3, rest: number, k: number) {
    const t = this.tmp.subVectors(b, a), l = t.length(); if (l < 1e-9) return;
    t.multiplyScalar(k * 0.5 * (l - rest) / l); a.add(t); b.sub(t);
  }

  update(dt: number) {
    this.chassis.updateMatrixWorld(true); this.head.updateMatrixWorld(true);
    if (!this.ready) {                                   // first call: lay the designed loop on the chassis where it now is
      for (let i = 0; i < this.n; i++) { const a = this.spec.points_m[i]; this.p[i].set(a[0], a[1], a[2]).applyMatrix4(this.chassis.matrixWorld); this.q[i].copy(this.p[i]); }
      this.ready = true;
    }
    this.acc = Math.min(this.acc + dt, 0.05);
    const g = this.gravity * STEP * STEP;
    while (this.acc >= STEP) {
      this.acc -= STEP;
      for (let i = 1; i < this.n - 1; i++) {
        const p = this.p[i], q = this.q[i], x = p.x, y = p.y, z = p.z;
        p.x += (p.x - q.x) * DAMP; p.y += (p.y - q.y) * DAMP - g; p.z += (p.z - q.z) * DAMP; q.set(x, y, z);
      }
      this.pin();
      for (let it = 0; it < ITER; it++) {
        for (let i = 0; i < this.n - 1; i++) this.pull(this.p[i], this.p[i + 1], this.d1[i], 1);
        for (let i = 0; i < this.n - 2; i++) this.pull(this.p[i], this.p[i + 2], this.d2[i], SKIP_K);
        for (let i = 0; i < this.n - 3; i++) this.pull(this.p[i], this.p[i + 3], this.d3[i], SKIP_K);
        this.pin();
      }
    }
    this.rebuild();
  }

  /** the round tube along the points: rings of SIDES vertices in a frame carried along the line (no twist) */
  private rebuild() {
    const r = this.spec.radius_m, t = new THREE.Vector3(), nrm = new THREE.Vector3(), bi = new THREE.Vector3(), prevT = new THREE.Vector3();
    for (let i = 0; i < this.n; i++) {
      const a = this.p[Math.max(0, i - 1)], b = this.p[Math.min(this.n - 1, i + 1)];
      t.subVectors(b, a).normalize();
      if (i === 0) { nrm.set(0, 1, 0); if (Math.abs(t.y) > 0.9) nrm.set(1, 0, 0); nrm.addScaledVector(t, -nrm.dot(t)).normalize(); }
      else { const ax = this.tmp.crossVectors(prevT, t); const s = ax.length(); if (s > 1e-6) nrm.applyAxisAngle(ax.normalize(), Math.asin(Math.min(1, s))); nrm.addScaledVector(t, -nrm.dot(t)).normalize(); }
      prevT.copy(t); bi.crossVectors(t, nrm);
      for (let s = 0; s < SIDES; s++) {
        const ang = (s / SIDES) * Math.PI * 2, c = Math.cos(ang), sn = Math.sin(ang), k = (i * SIDES + s) * 3;
        const nx = nrm.x * c + bi.x * sn, ny = nrm.y * c + bi.y * sn, nz = nrm.z * c + bi.z * sn;
        this.nor[k] = nx; this.nor[k + 1] = ny; this.nor[k + 2] = nz;
        this.pos[k] = this.p[i].x + nx * r; this.pos[k + 1] = this.p[i].y + ny * r; this.pos[k + 2] = this.p[i].z + nz * r;
      }
    }
    (this.geo.attributes.position as THREE.BufferAttribute).needsUpdate = true; (this.geo.attributes.normal as THREE.BufferAttribute).needsUpdate = true;
  }
}
