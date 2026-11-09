import * as THREE from "three";
import type { Prediction } from "./delay";
import type { Minimap } from "./minimap";

const CYAN = 0x44ffe8, MAXP = 400;

/** The predictive display of a delayed link: a ghost of the rover where it will be when a command issued now arrives, the path it takes to get there from the state the operator sees, and a circle that grows
 *  with the distance covered (a look choice: 15 cm plus a tenth of the path) because the prediction ignores slope, soil and rocks. Drawn in the world and on the map; the operator's overlay, so `without` hides
 *  it while the mast camera draws. */
export class DelayView {
  readonly group = new THREE.Group();
  private ghost = new THREE.Group(); private path: THREE.Line; private ring: THREE.LineLoop; private pos = new Float32Array(3 * MAXP);
  private last: Prediction | null = null;
  private mat = new THREE.LineBasicMaterial({ color: CYAN, toneMapped: false, transparent: true, opacity: 0.9 });

  constructor(scene: THREE.Scene, private ground: (x: number, z: number) => number) {
    const box = new THREE.BoxGeometry(0.5, 0.3, 0.47);      // the rover's envelope: about 0.5 m long, 0.47 m wide, a wedge at most 0.3 m deep above the axles (a box stands for it)
    this.ghost.add(new THREE.LineSegments(new THREE.EdgesGeometry(box), this.mat), new THREE.Mesh(box, new THREE.MeshBasicMaterial({ color: CYAN, transparent: true, opacity: 0.1, toneMapped: false, depthWrite: false })));
    const arrow = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.14, 8), new THREE.MeshBasicMaterial({ color: CYAN, toneMapped: false, transparent: true, opacity: 0.7 })); arrow.rotation.z = -Math.PI / 2; arrow.position.set(0.35, 0, 0); this.ghost.add(arrow);      // along the rover's +x
    const pg = new THREE.BufferGeometry(); pg.setAttribute("position", new THREE.BufferAttribute(this.pos, 3)); pg.setDrawRange(0, 0);
    this.path = new THREE.Line(pg, this.mat); this.path.frustumCulled = false;
    const rg = new THREE.BufferGeometry().setFromPoints(Array.from({ length: 48 }, (_, i) => new THREE.Vector3(Math.cos((i / 48) * 2 * Math.PI), 0, Math.sin((i / 48) * 2 * Math.PI)))); this.ring = new THREE.LineLoop(rg, this.mat);
    this.group.add(this.ghost, this.path, this.ring); this.group.visible = false; scene.add(this.group);
  }

  /** null hides it */
  update(p: Prediction | null) {
    this.last = p; this.group.visible = !!p; if (!p) return;
    const n = Math.min(MAXP, p.path.length), stride = Math.max(1, Math.ceil(p.path.length / MAXP));
    let k = 0; for (let i = 0; i < p.path.length && k < MAXP; i += stride, k++) { const q = p.path[i]; this.pos[3 * k] = q.x; this.pos[3 * k + 1] = this.ground(q.x, q.z) + 0.05; this.pos[3 * k + 2] = q.z; }
    (this.path.geometry.attributes.position as THREE.BufferAttribute).needsUpdate = true; this.path.geometry.setDrawRange(0, Math.min(k, n));
    const e = p.end, y = this.ground(e.x, e.z), r = 0.15 + 0.1 * p.distance;
    this.ghost.position.set(e.x, y + 0.25, e.z); this.ghost.rotation.set(0, -(e.headingDeg - 90) * Math.PI / 180, 0);      // bearing 90 (east) is the world +x: rotation about y is the bearing minus 90, clockwise seen from above
    this.ring.position.set(e.x, y + 0.06, e.z); this.ring.scale.set(r, 1, r);
  }

  /** the map: the predicted path and the ghost's place, with its circle */
  drawOverlay(map: Minimap, g: CanvasRenderingContext2D) {
    const p = this.last; if (!p) return;
    g.save(); g.strokeStyle = "#44ffe8"; g.lineWidth = 2; g.beginPath();
    p.path.forEach((q, i) => { const [X, Y] = map.toCanvas(q.x, q.z); if (i) g.lineTo(X, Y); else g.moveTo(X, Y); }); g.stroke();
    const [X, Y] = map.toCanvas(p.end.x, p.end.z), [X2] = map.toCanvas(p.end.x + 1, p.end.z), px = X2 - X, r = Math.max(5, (0.15 + 0.1 * p.distance) * px);      // pixels per metre
    g.beginPath(); g.arc(X, Y, r, 0, 2 * Math.PI); g.stroke();
    const a = ((p.end.headingDeg - 90) * Math.PI) / 180; g.translate(X, Y); g.rotate(a); g.fillStyle = "#44ffe8"; g.beginPath(); g.moveTo(9, 0); g.lineTo(-5, 5); g.lineTo(-5, -5); g.closePath(); g.fill();
    g.restore();
  }

  without(draw: () => void) { const v = this.group.visible; this.group.visible = false; try { draw(); } finally { this.group.visible = v; } }
}
