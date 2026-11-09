import * as THREE from "three";
import { Route, footprint, forward, type Pose } from "./plan";

const BLUE = 0x4aa3ff;

/** The route in the world: a pole and a heading arrow at each waypoint, the path from the rover through them on the ground, and the selected waypoint's camera footprint (VERVE's waypoints and RSVP's
 *  footprint, docs/sim-ui-research.md). Rebuilt when the route changes and (the path's first point) when the rover has moved half a metre. It is the operator's overlay, so `without` hides it while the mast camera draws. */
export class RouteView {
  readonly group = new THREE.Group();
  private version = -1; private px = NaN; private pz = NaN;
  private mats = { blue: new THREE.MeshBasicMaterial({ color: BLUE, toneMapped: false }), white: new THREE.MeshBasicMaterial({ color: 0xffffff, toneMapped: false }), line: new THREE.LineBasicMaterial({ color: BLUE, toneMapped: false }), foot: new THREE.LineBasicMaterial({ color: 0x9fd0ff, toneMapped: false }) };

  constructor(scene: THREE.Scene, private route: Route, private ground: (x: number, z: number) => number) { scene.add(this.group); }

  /** sample a ground polyline every metre or so, a few centimetres up */
  private sampled(pts: [number, number][], close = false) {
    const out: THREE.Vector3[] = [], n = pts.length;
    for (let i = 0; i < (close ? n : n - 1); i++) {
      const [x0, z0] = pts[i], [x1, z1] = pts[(i + 1) % n], steps = Math.max(1, Math.ceil(Math.hypot(x1 - x0, z1 - z0) / 1));
      for (let s = 0; s < steps; s++) { const t = s / steps, x = x0 + (x1 - x0) * t, z = z0 + (z1 - z0) * t; out.push(new THREE.Vector3(x, this.ground(x, z) + 0.06, z)); }
    }
    if (!close && n) out.push(new THREE.Vector3(pts[n - 1][0], this.ground(pts[n - 1][0], pts[n - 1][1]) + 0.06, pts[n - 1][1]));
    return out;
  }

  update(pose: Pose) {
    const r = this.route;
    if (r.version === this.version && Math.hypot(pose.x - this.px, pose.z - this.pz) < 0.5) return;
    this.version = r.version; this.px = pose.x; this.pz = pose.z;
    for (const c of [...this.group.children]) { this.group.remove(c); (c as THREE.Mesh).geometry?.dispose(); }
    if (!r.wps.length) return;
    r.wps.forEach((w, i) => {
      const sel = i === r.selected, mat = sel ? this.mats.white : this.mats.blue, y = this.ground(w.x, w.z);
      const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 1.4, 6), mat); pole.position.set(w.x, y + 0.7, w.z); this.group.add(pole);
      const cone = new THREE.Mesh(new THREE.ConeGeometry(0.14, 0.5, 8), mat), [fx, fz] = forward(w.headingDeg);      // lies flat, its tip along the heading
      cone.position.set(w.x + fx * 0.35, y + 0.14, w.z + fz * 0.35); cone.rotation.set(0, 0, 0); cone.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), new THREE.Vector3(fx, 0, fz)); this.group.add(cone);
      const flag = new THREE.Mesh(new THREE.PlaneGeometry(0.3, 0.2), mat); flag.position.set(w.x + 0.15, y + 1.3, w.z); flag.material = mat; this.group.add(flag);
    });
    const path = this.sampled([[pose.x, pose.z], ...r.wps.map((w) => [w.x, w.z] as [number, number])]);
    if (path.length > 1) this.group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(path), this.mats.line));
    const sel = r.wps[r.selected];
    if (sel) this.group.add(new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(this.sampled(footprint(sel.x, sel.z, sel.headingDeg), true)), this.mats.foot));
  }

  /** runs `draw` with the route hidden */
  without(draw: () => void) { const v = this.group.visible; this.group.visible = false; try { draw(); } finally { this.group.visible = v; } }
}
