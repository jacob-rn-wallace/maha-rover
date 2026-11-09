import * as THREE from "three";
import { Terrain, MOON_R } from "./terrain";
import { decode } from "fast-png";

/** Visual terrain: nested grid levels around the rover (a geometry clipmap) over the tile, and the viewshed ring beyond it.
 *
 *  Level k has cell size s_k and N_k cells a side; it is a world-aligned lattice, so vertices do not swim as the rover moves, and it is rebuilt when the rover has moved
 *  `snap_k` from the level's centre. Each level has a hole where the next finer level lies (their edges coincide: the finer level's boundary vertices take the coarser
 *  level's linear interpolation, so the surface is watertight). The coarsest level is fixed and covers the tile; every level is clipped to the tile square, and the ring mesh
 *  (hardware/sim/terrain/viewshed.py output: only the terrain that can be seen from the tile) lies beyond it.
 *  Octaves of procedural detail a level cannot resolve (shorter than twice its cell size) are left out of its heights.
 */
const CHUNKS = 10;
interface Level { s: number; n: number; snap: number; fixed?: boolean }
const LEVELS: Level[] = [
  { s: 0.25, n: 256, snap: 4 },          // 64 m, aligned to the next level's 1 m lattice
  { s: 1, n: 256, snap: 16 },            // 256 m
  { s: 4, n: 250, snap: 80 },            // 1000 m
  { s: 10, n: 500, snap: 0, fixed: true }, // the whole 5 km tile
];

class LevelMesh {
  readonly mesh: THREE.Mesh;
  cx = NaN; cz = NaN;                      // lattice centre of the current build
  private holeKey = "";
  private pos: Float32Array; private nor: Float32Array; private idx: Uint32Array;
  private geo = new THREE.BufferGeometry();
  private hts: Float32Array;
  /** the fixed tile level is cut into CHUNKS x CHUNKS meshes over the shared vertex buffers (own index buffers, bounding spheres), so the frustum culling drops the 10 m cells behind the camera */
  readonly object: THREE.Object3D;
  private chunks: THREE.Mesh[] = []; private bounded = false;
  constructor(readonly level: Level, material: THREE.Material, readonly terrain: Terrain, readonly finer: LevelMesh | null, readonly coarser: Level | null) {
    const v = (level.n + 1) ** 2;
    this.pos = new Float32Array(v * 3); this.nor = new Float32Array(v * 3); this.idx = new Uint32Array(level.n * level.n * 6);
    this.hts = new Float32Array((level.n + 3) ** 2);
    this.geo.setAttribute("position", new THREE.BufferAttribute(this.pos, 3).setUsage(THREE.DynamicDrawUsage));
    this.geo.setAttribute("normal", new THREE.BufferAttribute(this.nor, 3).setUsage(THREE.DynamicDrawUsage));
    this.geo.setIndex(new THREE.BufferAttribute(this.idx, 1).setUsage(THREE.DynamicDrawUsage));
    this.mesh = new THREE.Mesh(this.geo, material);
    this.mesh.frustumCulled = false;
    this.mesh.receiveShadow = true;
    if (level.fixed) {
      const g = new THREE.Group(); this.object = g;
      for (let c = 0; c < CHUNKS * CHUNKS; c++) {
        const cg = new THREE.BufferGeometry();
        cg.setAttribute("position", this.geo.attributes.position); cg.setAttribute("normal", this.geo.attributes.normal);
        const m = new THREE.Mesh(cg, material); m.receiveShadow = true; this.chunks.push(m); g.add(m);
      }
    } else this.object = this.mesh;
  }

  private job: { cx: number; cz: number; row: number; h: Float32Array } | null = null;

  /** rebuild the heights if the rover left the snap cell; returns true if they changed. The height sampling is spread over frames (rows of the lattice until `deadline`, a performance.now() time):
   *  the old mesh stays until the new one is complete, then the swap is cheap. The first build (no mesh yet) runs to the end. */
  follow(x: number, z: number, deadline: number): boolean {
    const { s, n, snap, fixed } = this.level;
    if (!this.job) {
      const cx = fixed ? 0 : Math.round(x / snap) * snap, cz = fixed ? 0 : Math.round(z / snap) * snap;
      if (cx === this.cx && cz === this.cz) { if (this.finer && this.holeKey !== `${this.finer.cx},${this.finer.cz}`) this.indices(); return false; }
      this.job = { cx, cz, row: 0, h: new Float32Array((n + 3) ** 2) };
      if (!Number.isFinite(this.cx)) deadline = Infinity;
    }
    const J = this.job, m = n + 3, minWl = 2 * s, half = n / 2;
    while (J.row < m && performance.now() < deadline) {
      const j = J.row++;
      for (let i = 0; i < m; i++) J.h[j * m + i] = this.terrain.height(J.cx + (i - 1 - half) * s, J.cz + (j - 1 - half) * s, minWl);
    }
    if (J.row < m) return false;
    this.job = null;
    const h = J.h, cx = J.cx, cz = J.cz;
    this.cx = cx; this.cz = cz;
    const stride = n + 1;
    for (let j = 0; j <= n; j++) for (let i = 0; i <= n; i++) {
      const k = j * stride + i, x = cx + (i - half) * s, z = cz + (j - half) * s;
      let y = h[(j + 1) * m + i + 1];
      if (this.coarser && (i === 0 || i === n || j === 0 || j === n)) y = this.stitch(i, j, x, z);
      this.pos[k * 3] = x; this.pos[k * 3 + 1] = y; this.pos[k * 3 + 2] = z;
      const dx = (h[(j + 1) * m + i + 2] - h[(j + 1) * m + i]) / (2 * s), dz = (h[(j + 2) * m + i + 1] - h[j * m + i + 1]) / (2 * s);
      const l = Math.hypot(dx, 1, dz);
      this.nor[k * 3] = -dx / l; this.nor[k * 3 + 1] = 1 / l; this.nor[k * 3 + 2] = -dz / l;
    }
    (this.geo.attributes.position as THREE.BufferAttribute).needsUpdate = true;
    (this.geo.attributes.normal as THREE.BufferAttribute).needsUpdate = true;
    if (fixed && !this.bounded) this.bound();
    this.indices();
    return true;
  }

  /** bounding spheres of the chunks (the fixed level's heights never change) */
  private bound() {
    this.bounded = true;
    const { n } = this.level, per = n / CHUNKS, stride = n + 1, box = new THREE.Box3(), v = new THREE.Vector3();
    this.chunks.forEach((m, c) => {
      const i0 = (c % CHUNKS) * per, j0 = Math.floor(c / CHUNKS) * per;
      box.makeEmpty();
      for (let j = j0; j <= j0 + per; j++) for (let i = i0; i <= i0 + per; i++) { const k = (j * stride + i) * 3; box.expandByPoint(v.set(this.pos[k], this.pos[k + 1], this.pos[k + 2])); }
      m.geometry.boundingSphere = box.getBoundingSphere(new THREE.Sphere());
      m.frustumCulled = true;
    });
  }

  /** a boundary vertex lies on the coarser level's lattice line: take the linear interpolation of the two coarser vertices beside it */
  private stitch(i: number, j: number, x: number, z: number): number {
    const S = this.coarser!.s;
    const onX = i === 0 || i === this.level.n;                         // an edge of constant x: interpolate along z
    const t = onX ? z : x, a = Math.floor(t / S + 1e-9) * S, w = (t - a) / S;
    const f = (u: number) => onX ? this.terrain.height(x, u, 2 * S) : this.terrain.height(u, z, 2 * S);
    return f(a) * (1 - w) + f(a + S) * w;
  }

  /** triangles of the cells inside the tile square and outside the finer level's extent */
  indices() {
    const { s, n } = this.level, half = n / 2, stride = n + 1, H = this.terrain.half;
    const f = this.finer && Number.isFinite(this.finer.cx) ? this.finer : null;
    const fh = f ? (f.level.n * f.level.s) / 2 : 0;
    this.holeKey = f ? `${f.cx},${f.cz}` : "";
    let c = 0;
    if (this.level.fixed) {                                            // per chunk: its cells, in the shared index array
      const per = n / CHUNKS;
      this.chunks.forEach((m, ch) => {
        const i0 = (ch % CHUNKS) * per, j0 = Math.floor(ch / CHUNKS) * per, start = c;
        for (let j = j0; j < j0 + per; j++) for (let i = i0; i < i0 + per; i++) {
          const mx = this.cx + (i - half) * s + s / 2, mz = this.cz + (j - half) * s + s / 2;
          if (Math.abs(mx) > H || Math.abs(mz) > H) continue;
          if (f && Math.abs(mx - f.cx) < fh && Math.abs(mz - f.cz) < fh) continue;
          const a = j * stride + i, b = a + 1, d = a + stride, e = d + 1;
          this.idx[c++] = a; this.idx[c++] = d; this.idx[c++] = b; this.idx[c++] = b; this.idx[c++] = d; this.idx[c++] = e;
        }
        m.geometry.setIndex(new THREE.BufferAttribute(this.idx.slice(start, c), 1)); m.visible = c > start;
      });
      return;
    }
    for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
      const x0 = this.cx + (i - half) * s, z0 = this.cz + (j - half) * s;
      const mx = x0 + s / 2, mz = z0 + s / 2;
      if (Math.abs(mx) > H || Math.abs(mz) > H) continue;
      if (f && Math.abs(mx - f.cx) < fh && Math.abs(mz - f.cz) < fh) continue;
      const a = j * stride + i, b = a + 1, d = a + stride, e = d + 1;
      this.idx[c++] = a; this.idx[c++] = d; this.idx[c++] = b; this.idx[c++] = b; this.idx[c++] = d; this.idx[c++] = e;
    }
    this.geo.setDrawRange(0, c);
    (this.geo.index as THREE.BufferAttribute).needsUpdate = true;
  }
}

export class TerrainView {
  readonly group = new THREE.Group();
  private levels: LevelMesh[] = [];
  constructor(private terrain: Terrain, private material: THREE.Material) {
    let finer: LevelMesh | null = null;
    const built: LevelMesh[] = [];
    // finest first, each knowing the next coarser level for stitching
    for (let k = 0; k < LEVELS.length; k++) {
      const lm: LevelMesh = new LevelMesh(LEVELS[k], material, terrain, finer, LEVELS[k + 1] ?? null);
      built.push(lm); finer = lm;
    }
    this.levels = built;
    for (const l of built) this.group.add(l.object);
  }

  update(x: number, z: number) {
    const deadline = performance.now() + 4;                          // at most about 4 ms a frame on rebuilding heights (the first build ignores it)
    for (const l of this.levels) l.follow(x, z, deadline);                      // a level's hole follows the finer level inside it: indices() is rebuilt when either moved
  }

  /** the ring beyond the tile: a polar mesh with only the cells (and a one-cell margin) that some observer on the tile can see */
  async addRing(base = "terrain/") {
    const [meta, hpng, mpng] = await Promise.all([
      fetch(base + "ring.json").then((r) => r.json()),
      fetch(base + "ring.png").then((r) => r.arrayBuffer()).then((b) => decode(b)),
      fetch(base + "ring_mask.png").then((r) => r.arrayBuffer()).then((b) => decode(b)),
    ]);
    const nA: number = meta.n_az, nR: number = meta.n_range, edges: number[] = meta.range_edges_m, mask = mpng.data as Uint8Array;
    const H = this.terrain.half, BAND = 150;                       // the ring is also drawn within BAND metres of the tile whether or not an observer sees it: no gap at the edge
    const cx = new Float32Array(nR * nA), cz = new Float32Array(nR * nA);
    for (let r = 0; r < nR; r++) {
      const d = Math.sqrt(edges[r] * edges[r + 1]);
      for (let a = 0; a < nA; a++) { const az = (a + 0.5) * 2 * Math.PI / nA; cx[r * nA + a] = d * Math.sin(az); cz[r * nA + a] = -d * Math.cos(az); }
    }
    const near = (k: number) => Math.max(Math.abs(cx[k]), Math.abs(cz[k])) <= H + BAND;
    const used = new Uint8Array(nR * nA);
    const vis = (r: number, a: number) => r >= 0 && r < nR && (mask[r * nA + (a + nA) % nA] > 0 || near(r * nA + (a + nA) % nA));
    for (let r = 0; r < nR; r++) for (let a = 0; a < nA; a++) {
      let on = false;
      for (let dr = -1; dr <= 1 && !on; dr++) for (let da = -1; da <= 1 && !on; da++) on = vis(r + dr, a + da);
      used[r * nA + a] = on ? 1 : 0;
    }
    const pos = new Float32Array(nR * nA * 3), nor = new Float32Array(nR * nA * 3);
    const inside = new Uint8Array(nR * nA);
    for (let r = 0; r < nR; r++) for (let a = 0; a < nA; a++) {
      const k = r * nA + a;
      if (!used[k]) continue;
      const x = cx[k], z = cz[k], din = H - Math.max(Math.abs(x), Math.abs(z));          // metres inside the tile edge (negative outside)
      inside[k] = din >= 0 ? 1 : 0;
      // where the ring lies under the tile's own mesh it is sunk, by up to 2 m at 10 m inside the edge: the tile mesh is a linear interpolation (10 m cells) and sags below the surface on convex ground
      pos[k * 3] = x; pos[k * 3 + 1] = this.terrain.height(x, z, 1e9) - Math.min(2, Math.max(0, din) * 0.2); pos[k * 3 + 2] = z;
    }
    // normals from the neighbours in the polar grid
    const P = (r: number, a: number, o: number) => pos[(Math.min(nR - 1, Math.max(0, r)) * nA + ((a + nA) % nA)) * 3 + o];
    for (let r = 0; r < nR; r++) for (let a = 0; a < nA; a++) {
      const k = r * nA + a;
      if (!used[k]) continue;
      const ux = P(r + 1, a, 0) - P(r - 1, a, 0), uy = P(r + 1, a, 1) - P(r - 1, a, 1), uz = P(r + 1, a, 2) - P(r - 1, a, 2);   // outward
      const vx = P(r, a + 1, 0) - P(r, a - 1, 0), vy = P(r, a + 1, 1) - P(r, a - 1, 1), vz = P(r, a + 1, 2) - P(r, a - 1, 2);   // clockwise from north
      let nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;                                                // u x v: points up for this orientation
      const l = Math.hypot(nx, ny, nz) || 1;
      if (ny < 0) { nx = -nx; ny = -ny; nz = -nz; }
      nor[k * 3] = nx / l; nor[k * 3 + 1] = ny / l; nor[k * 3 + 2] = nz / l;
    }
    // the ring is cut into SECTORS azimuth sectors x BANDS range bands, one mesh each over shared vertex buffers, so the frustum culling drops what is behind the camera (792,000 triangles in all)
    const SECTORS = 16, BANDS = 6, posAttr = new THREE.BufferAttribute(pos, 3), norAttr = new THREE.BufferAttribute(nor, 3);
    const chunks: number[][] = Array.from({ length: SECTORS * BANDS }, () => []);
    let triangles = 0;
    for (let r = 0; r < nR - 1; r++) for (let a = 0; a < nA; a++) {
      const a1 = (a + 1) % nA, A = r * nA + a, B = r * nA + a1, C = (r + 1) * nA + a, D = (r + 1) * nA + a1;
      if (!(used[A] && used[B] && used[C] && used[D])) continue;
      if (inside[A] && inside[B] && inside[C] && inside[D]) continue;
      chunks[Math.floor(r * BANDS / nR) * SECTORS + Math.floor(a * SECTORS / nA)].push(A, B, C, B, D, C);
      triangles += 2;
    }
    const box = new THREE.Box3(), v = new THREE.Vector3();
    for (const idx of chunks) {
      if (!idx.length) continue;
      const g = new THREE.BufferGeometry();
      g.setAttribute("position", posAttr); g.setAttribute("normal", norAttr);
      g.setIndex(new THREE.BufferAttribute(new Uint32Array(idx), 1));
      box.makeEmpty();
      for (const i of idx) box.expandByPoint(v.set(pos[i * 3], pos[i * 3 + 1], pos[i * 3 + 2]));
      g.boundingSphere = box.getBoundingSphere(new THREE.Sphere());
      g.boundingSphere.radius += 50;
      const mesh = new THREE.Mesh(g, this.material);
      this.group.add(mesh);
    }
    return { triangles, radius: MOON_R };
  }
}
