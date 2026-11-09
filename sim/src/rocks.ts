import * as THREE from "three";
import { mergeVertices } from "three/examples/jsm/utils/BufferGeometryUtils.js";
import type { Terrain } from "./terrain";

/** Rocks: a deterministic population of boulders and stones over the tile, from a published size law scaled to the mapped boulder density of the landing ellipse.
 *
 *  Sources (private library papers; numbers only):
 *   - Joulaud et al., Space Science Reviews 220:65 (2024): 7232 boulders mapped by hand on LROC NAC images in the 8 km ellipse FR-11 in Atlas crater, 144 per km2. Objects under
 *     about 1.5 to 2 m cannot be detected at 0.5 to 1 m/px, so the count is of boulders of about 2 m and more. Boulder fields lie near the centre (south-west, by a large degraded crater),
 *     in the north-east, and at topographic highs; elsewhere the plains are rock-poor. The mapped positions are only in the paper's figures, not in a data file.
 *   - Bandfield et al., JGR Planets 116, E00H02 (2011), from 769 blocks (2 to 11 m and more) counted on LROC images of King Crater's central peak, after Cintala and McBride (1995):
 *     the cumulative areal fraction of rocks of diameter d or more is c = 0.082 d^-1.326 (d in metres). Their LROC counts under 3 m are probably incomplete.
 *  From c the number of rocks of diameter d or more per m2 is N(d) = A d^-3.326, A = 4 K b / (pi (b + 2)) with c = K d^-b, b = 1.326.
 *
 *  ASSUMPTIONS (not in the sources): (1) the exponent of the King Crater peak holds on the Atlas floor, and down to 0.12 m, a factor of 17 below the smallest mapped boulders;
 *  (2) the 144 per km2 is complete at 2 m (K then is 0.00285; if it were complete at 3 m, K would be 0.011); (3) the density varies in space as a smooth random field times a
 *  slope factor, normalised to the mean of the tile: boulder fields exist, but their mapped places are not used; (4) shapes are lumpy ellipsoids buried by 20 to 40% of their height.
 *  Cross-check: K is also the areal fraction of rocks of 1 m and more, 0.285%; the Diviner rock abundance of FR-11 is 0.0029 in the site-selection paper (Flahaut et al. 2024, a fraction if
 *  its column "(%)" is a mislabel as for its slope column) and 0.029% in Joulaud et al.: the first agrees, so the second is probably a slip of a factor ten (unresolved in the papers).
 */
export const ROCK_LAW = {
  b: 1.326,                          // cumulative areal fraction exponent, Bandfield et al. 2011
  n2PerKm2: 144,                     // boulders of 2 m and more per km2, Joulaud et al. 2024 (ASSUMPTION: complete at 2 m)
  completeAtM: 2,
  dMin: 0.12, dMax: 14,              // metres: 0.12 m is the smallest stone that matters to a 0.2 m wheel; 14 m a little above the largest blocks counted on King Crater
};
/** smaller stones are only drawn: partly buried, they stand under 7 cm, and a 0.2 m wheel rolls over them (ASSUMPTION; the wheel's real obstacle limit is a result of the simulation) */
export const PHYSICS_MIN = 0.2;
const E = ROCK_LAW.b + 2;                                                                 // exponent of the cumulative number law
const A = ROCK_LAW.n2PerKm2 * 1e-6 * Math.pow(ROCK_LAW.completeAtM, E);                  // rocks per m2 of diameter 1 m and more
export const ROCK_K = A * Math.PI * E / (4 * ROCK_LAW.b);                                // areal fraction of rocks of 1 m and more
const nBetween = (d0: number, d1: number) => A * (Math.pow(d0, -E) - Math.pow(d1, -E));  // rocks per m2 with diameter in [d0, d1)

export interface Rock { x: number; z: number; y: number; d: number; sx: number; sy: number; sz: number; q: THREE.Quaternion; grey: number; }

interface Tier { name: string; d0: number; d1: number; cell: number; radius: number; snap: number; }
const TIERS: Tier[] = [
  { name: "stones", d0: ROCK_LAW.dMin, d1: 0.5, cell: 4, radius: 50, snap: 16 },
  { name: "rocks", d0: 0.5, d1: 2, cell: 16, radius: 300, snap: 64 },
  { name: "boulders", d0: 2, d1: ROCK_LAW.dMax, cell: 64, radius: 1500, snap: 256 },
];

function hash2(ix: number, iz: number, k: number): number {
  let h = Math.imul(ix, 0x27d4eb2d) ^ Math.imul(iz, 0x165667b1) ^ Math.imul(k + 7, 0x9e3779b1);
  h = Math.imul(h ^ (h >>> 15), 0x85ebca6b); h = Math.imul(h ^ (h >>> 13), 0xc2b2ae35);
  return (h ^ (h >>> 16)) >>> 0;
}
function rng(seed: number) { let s = seed >>> 0; return () => { s = (s + 0x6d2b79f5) >>> 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
function poisson(l: number, r: () => number) {
  if (l > 40) { const g = Math.sqrt(-2 * Math.log(r() + 1e-12)) * Math.cos(2 * Math.PI * r()); return Math.max(0, Math.round(l + Math.sqrt(l) * g)); }
  let k = 0, p = Math.exp(-l), s = p; const u = r();
  while (u > s && k < 200) { k++; p *= l / k; s += p; }
  return k;
}

export class RockField {
  private density: (x: number, z: number) => number;           // relative to the tile mean
  readonly group = new THREE.Group();
  private tiers: { tier: Tier; mesh: THREE.InstancedMesh; cx: number; cz: number; max: number }[] = [];
  private phys = { cx: NaN, cz: NaN, version: 0, hulls: [] as Float32Array[] };

  constructor(private terrain: Terrain, material: THREE.Material, private spawn: { x: number; z: number }) {
    // relative density: a smooth random field (log-normal, fields a few hundred metres across) times a slope factor, normalised to a mean of 1 over the tile
    const field = (x: number, z: number) => {
      let g = 0, amp = 1, f = 1 / 300, tot = 0;
      for (let o = 0; o < 3; o++) { g += amp * (noise(x * f, z * f, o) - 0.5); tot += amp; amp *= 0.5; f *= 2.3; }
      return Math.exp(5.0 * (g / tot));
    };
    const slope = (x: number, z: number) => {
      const h = 6, dx = (terrain.height(x + h, z, 1e9) - terrain.height(x - h, z, 1e9)) / (2 * h), dz = (terrain.height(x, z + h, 1e9) - terrain.height(x, z - h, 1e9)) / (2 * h);
      return Math.hypot(dx, dz);
    };
    const raw = (x: number, z: number) => field(x, z) * (1 + Math.min(4, Math.pow(slope(x, z) / 0.14, 2)));     // 0.14 = 8 degrees
    let sum = 0, n = 0;
    for (let x = -2400; x <= 2400; x += 100) for (let z = -2400; z <= 2400; z += 100) { sum += raw(x, z); n++; }
    const mean = sum / n;
    this.density = (x, z) => raw(x, z) / mean;

    const geo = lumpyRock();
    for (const tier of TIERS) {
      const max = Math.ceil(Math.PI * tier.radius * tier.radius * nBetween(tier.d0, tier.d1) * 6) + 64;       // room for fields several times the mean
      const mesh = new THREE.InstancedMesh(geo, material, max);
      mesh.count = 0; mesh.frustumCulled = false; mesh.castShadow = tier.d0 < 0.5;      // only the stones cast into the rover's 4 m shadow map (instanced meshes are drawn whole into it every frame) mesh.receiveShadow = true;
      this.group.add(mesh);
      this.tiers.push({ tier, mesh, cx: NaN, cz: NaN, max });
    }
  }

  /** the rocks of one tier in one cell: the same every time (seeded by the cell) */
  rocksIn(tier: Tier, ix: number, iz: number): Rock[] {
    const { cell } = tier, x0 = ix * cell, z0 = iz * cell;
    if (Math.abs(x0 + cell / 2) > this.terrain.half + 40 || Math.abs(z0 + cell / 2) > this.terrain.half + 40) return [];
    const r = rng(hash2(ix, iz, tier.d0 * 1000));
    const w = this.density(x0 + cell / 2, z0 + cell / 2);
    const k = poisson(nBetween(tier.d0, tier.d1) * cell * cell * w, r);
    const out: Rock[] = [];
    const a = Math.pow(tier.d0, -E), b = Math.pow(tier.d1, -E);
    for (let i = 0; i < k; i++) {
      const x = x0 + r() * cell, z = z0 + r() * cell;
      if (Math.hypot(x - this.spawn.x, z - this.spawn.z) < 3 + tier.d1) continue;                    // keep the spawn point clear
      const d = Math.pow(a - r() * (a - b), -1 / E);
      const e1 = 0.35 + 0.35 * r(), e2 = 0.6 + 0.4 * r();                                           // axis ratios: a flattened lumpy ellipsoid (vertical axis 0.35 to 0.7 of the width)
      const q = new THREE.Quaternion().setFromEuler(new THREE.Euler(r() * 6.283, r() * 6.283, r() * 6.283));
      const bury = 0.2 + 0.2 * r();                                                                 // fraction of the rock's height below the ground
      const sx = d, sy = d * e1, sz = d * e2;
      const y = this.terrain.height(x, z, 0.5) + sy * (0.5 - bury);
      out.push({ x, z, y, d, sx, sy, sz, q, grey: 0.75 + 0.5 * r() });
    }
    return out;
  }

  /** rebuild the visible rocks when the rover has moved to another snap cell of a tier */
  update(x: number, z: number) {
    const m = new THREE.Matrix4(), s = new THREE.Vector3(), p = new THREE.Vector3(), c = new THREE.Color();
    for (const t of this.tiers) {
      const { tier } = t, cx = Math.round(x / tier.snap) * tier.snap, cz = Math.round(z / tier.snap) * tier.snap;
      if (cx === t.cx && cz === t.cz) continue;
      t.cx = cx; t.cz = cz;
      const i0 = Math.floor((cx - tier.radius) / tier.cell), i1 = Math.floor((cx + tier.radius) / tier.cell), j0 = Math.floor((cz - tier.radius) / tier.cell), j1 = Math.floor((cz + tier.radius) / tier.cell);
      let n = 0;
      for (let j = j0; j <= j1 && n < t.max; j++) for (let i = i0; i <= i1 && n < t.max; i++) {
        for (const rk of this.rocksIn(tier, i, j)) {
          if (Math.hypot(rk.x - cx, rk.z - cz) > tier.radius || n >= t.max) continue;
          m.compose(p.set(rk.x, rk.y, rk.z), rk.q, s.set(rk.sx, rk.sy, rk.sz));
          t.mesh.setMatrixAt(n, m);
          t.mesh.setColorAt(n, c.setScalar(rk.grey));
          n++;
        }
      }
      t.mesh.count = n;
      t.mesh.instanceMatrix.needsUpdate = true;
      if (t.mesh.instanceColor) t.mesh.instanceColor.needsUpdate = true;
    }
  }

  /** hulls (world-space points, flat xyz) of the rocks the physics needs round (x, z): stones of PHYSICS_MIN and more within 8 m, rocks within 30 m, boulders within 60 m; `version` changes when the set does */
  physics(x: number, z: number) {
    const ph = this.phys, cx = Math.round(x / 4) * 4, cz = Math.round(z / 4) * 4;
    if (cx === ph.cx && cz === ph.cz) return ph;
    ph.cx = cx; ph.cz = cz; ph.version++; ph.hulls = [];
    const reach = [8, 30, 60];
    TIERS.forEach((tier, k) => {
      const R = reach[k], i0 = Math.floor((cx - R) / tier.cell), i1 = Math.floor((cx + R) / tier.cell), j0 = Math.floor((cz - R) / tier.cell), j1 = Math.floor((cz + R) / tier.cell);
      for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) for (const rk of this.rocksIn(tier, i, j)) {
        if (Math.hypot(rk.x - cx, rk.z - cz) > R || rk.d < PHYSICS_MIN) continue;
        ph.hulls.push(rockHull(rk));
      }
    });
    return ph;
  }
}

/** world-space points of a rock's collider: an icosahedron, scaled and turned like the visible rock */
const ICO = (() => { const t = (1 + Math.sqrt(5)) / 2, v = [[-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0], [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t], [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]]; return v.map((p) => new THREE.Vector3(...p).normalize().multiplyScalar(0.5)); })();
function rockHull(r: Rock): Float32Array {
  const out = new Float32Array(ICO.length * 3), v = new THREE.Vector3();
  ICO.forEach((p, i) => { v.set(p.x * r.sx, p.y * r.sy, p.z * r.sz).applyQuaternion(r.q); out[i * 3] = v.x + r.x; out[i * 3 + 1] = v.y + r.y; out[i * 3 + 2] = v.z + r.z; });
  return out;
}

/** an icosphere of diameter 1 with its vertices pushed in and out by a fixed lumpy pattern */
function lumpyRock() {
  const g0 = new THREE.IcosahedronGeometry(0.5, 2);
  g0.deleteAttribute("normal"); g0.deleteAttribute("uv");
  const g = mergeVertices(g0);                                       // shared vertices: smooth normals
  const p = g.attributes.position as THREE.BufferAttribute, v = new THREE.Vector3();
  for (let i = 0; i < p.count; i++) {
    v.fromBufferAttribute(p, i);
    const n = noise(v.x * 3.1 + 5, v.y * 3.1, 1) * 0.5 + noise(v.z * 6.3, v.x * 6.3 + 9, 2) * 0.25 + noise(v.y * 12 + 3, v.z * 12, 3) * 0.12;
    v.multiplyScalar(0.82 + 0.5 * n);
    p.setXYZ(i, v.x, v.y, v.z);
  }
  g.computeVertexNormals();
  return g;
}

function noise(x: number, z: number, k: number): number {
  const x0 = Math.floor(x), z0 = Math.floor(z), tx = x - x0, tz = z - z0;
  const sx = tx * tx * (3 - 2 * tx), sz = tz * tz * (3 - 2 * tz);
  const h = (a: number, b: number) => hash2(a, b, k) / 4294967296;
  return (h(x0, z0) * (1 - sx) + h(x0 + 1, z0) * sx) * (1 - sz) + (h(x0, z0 + 1) * (1 - sx) + h(x0 + 1, z0 + 1) * sx) * sz;
}
