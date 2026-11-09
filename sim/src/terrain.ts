import { decode } from "fast-png";

/** Real lunar terrain: the 5 x 5 km Atlas tile (hardware/sim/terrain/atlas_tile.py) smoothed and with deterministic procedural detail below its resolution,
 *  and the low-detail ring beyond it (hardware/sim/terrain/viewshed.py).
 *
 *  World frame: x east, y up, z south (north is -z, so the frame is right-handed), origin at the tile centre at the tile's centre height.
 *  Lunar curvature is in the heights: y = height - centre height - d^2 / 2R, d the distance from the origin (the ring uses the exact sphere).
 *  Look-development choices, not measurements: the smoothing and the procedural roughness (ASSUMPTION, to be set from the soil papers and a rock model).
 */
export const MOON_R = 1737400;
const HALF = 2500, POST = 2;
const SMOOTH_SIGMA_POSTS = 2;                       // removes stereo noise: the product's vertical precision is 2.89 m (atlas_5km.json)
const DETAIL_WAVELENGTHS = [8, 4, 2, 1, 0.5];       // metres: procedural octaves below the smoothed tile's scale
const DETAIL_SLOPE = 0.006;                         // amplitude = DETAIL_SLOPE x wavelength (a third of a degree of slope per octave; 0.02 looked like water ripples): ASSUMPTION
/** Small craters below the Atlas tile's resolution (it resolves about 10 m and up), by the equilibrium law: cumulative density N(>D) = CRATER_SAT x 1.54 D^-2 per m2 (geometric saturation 1.54 D^-2, Gault 1970 as quoted in the crater-counting literature,
 *  recalled not read here: ASSUMPTION; CRATER_SAT = 3% is a look-development choice). Six size tiers of a factor 2, 0.75 m to 48 m; per cell of 4 x the tier's top diameter a hash decides the craters (expected 0.55 per cell for every tier). Profile: a parabolic bowl with a low rim, depth/diameter 0.04 to 0.20
 *  (fresh craters are deeper; degraded ones are shallow). The same function feeds the visuals, the physics and the rocks, so they agree. */
const CRATER_SAT = 0.03;
const CRATER_TIERS: { d1: number; cell: number }[] = [0.75, 1.5, 3, 6, 12, 24].map((d1) => ({ d1, cell: 8 * d1 }));
const BLEND_M = 500;                                // beyond the tile edge the ring takes over, offset so the two meet; the offset fades out over this distance with a cosine (zero slope at both ends: an exponential fade lit up as a band)

interface Ring {
  nAz: number; nR: number; r0: number; growth: number; hMin: number; hMax: number;
  h: Uint16Array; mask: Uint8Array;
}

export class Terrain {
  readonly half = HALF;
  private tile!: Float32Array; private n!: number;
  private ring!: Ring;
  private hc = 0;                                   // raw height of the tile centre, metres
  spawn = { x: 0, z: 0, y: 0 };
  rocks?: { physics(x: number, z: number): { version: number; hulls: Float32Array[] } };      // set by main.ts: the rock population the physics needs near a point
  detailScale = 1;                                  // ?detail=0 switches the procedural roughness off

  static async load(base = "terrain/", opts: { smoothPosts?: number; detail?: number } = {}): Promise<Terrain> {
    const t = new Terrain();
    t.detailScale = opts.detail ?? 1;
    const png = async (f: string) => decode(await (await fetch(base + f)).arrayBuffer());
    const [meta, tile, ring, mask, ringMeta] = await Promise.all([
      fetch(base + "atlas_5km.json").then((r) => r.json()), png("atlas_5km.png"), png("ring.png"), png("ring_mask.png"), fetch(base + "ring.json").then((r) => r.json()),
    ]);
    const t0 = performance.now(); const lap = (l: string) => console.debug("terrain.load", l, (performance.now() - t0).toFixed(0), "ms");
    lap("decoded");
    const n = tile.width;
    const raw = new Float32Array(n * n);
    const k = (meta.height_max_m - meta.height_min_m) / 65535;
    for (let i = 0; i < raw.length; i++) raw[i] = meta.height_min_m + (tile.data as Uint16Array)[i] * k;
    t.n = n;
    t.tile = gaussian(raw, n, opts.smoothPosts ?? SMOOTH_SIGMA_POSTS);
    lap("smoothed");
    t.hc = t.tileAt(0, 0);
    t.ring = { nAz: ringMeta.n_az, nR: ringMeta.n_range, r0: ringMeta.r0_m, growth: ringMeta.growth, hMin: ringMeta.height_min_m, hMax: ringMeta.height_max_m, h: ring.data as Uint16Array, mask: mask.data as Uint8Array };
    t.spawn = t.flattestSpot();
    lap("spawn search");
    return t;
  }

  /** smoothed tile height above the centre, metres, by bicubic (Catmull-Rom) interpolation; clamped outside the tile */
  tileAt(x: number, z: number): number {
    const n = this.n, fx = (x + HALF) / POST - 0.5, fz = (z + HALF) / POST - 0.5;
    const x0 = Math.floor(fx), z0 = Math.floor(fz), tx = fx - x0, tz = fz - z0;
    const wx = cr(tx), wz = cr(tz);
    let s = 0;
    for (let j = 0; j < 4; j++) {
      const zi = Math.min(n - 1, Math.max(0, z0 - 1 + j));
      let r = 0;
      for (let i = 0; i < 4; i++) r += this.tile[zi * n + Math.min(n - 1, Math.max(0, x0 - 1 + i))] * wx[i];
      s += r * wz[j];
    }
    return s;
  }

  /** height of the ring at (x, z) in metres above the sphere, bilinear in the polar grid; NaN where the polar grid has no data */
  ringAt(x: number, z: number): number {
    const g = this.ring, d = Math.hypot(x, z);
    const fr = Math.log(Math.max(d, g.r0) / g.r0) / Math.log(g.growth) - 0.5;
    const az = (Math.atan2(x, -z) + 2 * Math.PI) % (2 * Math.PI);
    const fa = az / (2 * Math.PI) * g.nAz - 0.5;
    const r0 = Math.min(g.nR - 2, Math.max(0, Math.floor(fr))), tr = Math.min(1, Math.max(0, fr - r0));
    const a0 = Math.floor(fa), ta = fa - a0;
    const at = (r: number, a: number) => g.hMin + g.h[r * g.nAz + ((a % g.nAz) + g.nAz) % g.nAz] * (g.hMax - g.hMin) / 65535;
    return (at(r0, a0) * (1 - ta) + at(r0, a0 + 1) * ta) * (1 - tr) + (at(r0 + 1, a0) * (1 - ta) + at(r0 + 1, a0 + 1) * ta) * tr;
  }

  /** the ring's world height y at (x, z): exact sphere, heights above the sphere taken from the polar grid */
  private ringWorld(x: number, z: number): number {
    const d = Math.hypot(x, z);
    return (MOON_R + this.ringAt(x, z)) * Math.cos(d / MOON_R) - (MOON_R + this.hc);
  }

  /** world height y of the ground at (x, z); minWavelength drops the procedural octaves a coarse mesh cannot show */
  height(x: number, z: number, minWavelength = 0.5): number {
    if (Math.abs(x) <= HALF && Math.abs(z) <= HALF) return this.tileAt(x, z) - this.hc - (x * x + z * z) / (2 * MOON_R) + this.detail(x, z, minWavelength) + this.craters(x, z, minWavelength);
    const cx = Math.min(HALF, Math.max(-HALF, x)), cz = Math.min(HALF, Math.max(-HALF, z));
    const dist = Math.hypot(x - cx, z - cz), fade = dist >= BLEND_M ? 0 : 0.5 * (1 + Math.cos(Math.PI * dist / BLEND_M));
    const edge = this.tileAt(cx, cz) - this.hc - (cx * cx + cz * cz) / (2 * MOON_R);
    return this.ringWorld(x, z) + (edge - this.ringWorld(cx, cz)) * fade + (this.detail(x, z, minWavelength) + this.craters(x, z, minWavelength)) * fade;
  }

  /** height change of the small craters at (x, z); tiers whose craters the sampling (minWavelength = 2 x the mesh cell) cannot show with 4 cells across are skipped */
  craters(x: number, z: number, minWavelength: number): number {
    if (this.detailScale === 0) return 0;
    let h = 0;
    for (let t = 0; t < CRATER_TIERS.length; t++) {
      const { d1, cell } = CRATER_TIERS[t];
      if (d1 < 2 * minWavelength) continue;
      const cx = Math.floor(x / cell), cz = Math.floor(z / cell), m = 2 * d1;        // a crater reaches at most 2 radii = 2 d1 beyond its centre's cell: neighbours matter only near the cell's edges
      const fx = x - cx * cell, fz = z - cz * cell;
      const i0 = fx < m ? -1 : 0, i1 = fx > cell - m ? 1 : 0, j0 = fz < m ? -1 : 0, j1 = fz > cell - m ? 1 : 0;
      for (let i = i0; i <= i1; i++) for (let j = j0; j <= j1; j++) {
        const list = this.craterCell(t, cx + i, cz + j);
        for (let q = 0; q < list.length; q += 4) {
          const dx = x - list[q], dz = z - list[q + 1], R = list[q + 2], r2 = (dx * dx + dz * dz) / (R * R);
          if (r2 > 4) continue;
          const d = list[q + 3], r = Math.sqrt(r2), rim = 0.22 * d * Math.exp(-((r - 1) * (r - 1)) / 0.045);
          h += r < 1 ? -d * (1 - r2) + rim : rim * (r < 1.6 ? 1 : (2 - r) / 0.4);
        }
      }
    }
    return h * this.detailScale;
  }

  private craterCache = new Map<number, Float32Array>();
  private craterCell(t: number, ix: number, iz: number): Float32Array {
    const key = (t * 200003 + ix) * 200003 + iz;
    let l = this.craterCache.get(key);
    if (l) return l;
    const { d1, cell } = CRATER_TIERS[t], k = 40 + t;
    const lam = CRATER_SAT * 1.54 * (1 / (d1 * d1) - 1 / (4 * d1 * d1)) * cell * cell, e = Math.exp(-lam), u = hash(ix, iz, k);
    const n = u < e ? 0 : u < e * (1 + lam) ? 1 : u < e * (1 + lam + lam * lam / 2) ? 2 : 3;
    l = new Float32Array(n * 4);
    for (let c = 0; c < n; c++) {
      const kk = k + 10 * (c + 1), D = d1 * Math.pow(2, hash(ix, iz, kk + 200)), eps = 0.04 + 0.16 * hash(ix, iz, kk + 300) ** 2;
      l[c * 4] = (ix + hash(ix, iz, kk)) * cell; l[c * 4 + 1] = (iz + hash(ix, iz, kk + 100)) * cell; l[c * 4 + 2] = D / 2; l[c * 4 + 3] = eps * D;
    }
    if (this.craterCache.size > 60000) this.craterCache.clear();
    this.craterCache.set(key, l);
    return l;
  }

  /** procedural roughness, deterministic in position */
  detail(x: number, z: number, minWavelength = 0.5): number {
    let s = 0;
    if (this.detailScale === 0) return 0;
    for (let k = 0; k < DETAIL_WAVELENGTHS.length; k++) {
      const wl = DETAIL_WAVELENGTHS[k];
      if (wl < minWavelength) break;
      const c = Math.cos(0.7 + 1.3 * k), sn = Math.sin(0.7 + 1.3 * k);        // each octave's lattice turned by its own angle, so no grid direction shows
      s += (valueNoise((x * c - z * sn) / wl + 17.3 * k, (x * sn + z * c) / wl - 5.1 * k, k) * 2 - 1) * DETAIL_SLOPE * wl;
    }
    return s * this.detailScale;
  }

  /** the flattest spot within 400 m of the centre: smallest worst slope to eight neighbours 6 m away (the rover is 0.5 m across) */
  private flattestSpot() {
    let best = { x: 0, z: 0, y: 0 }, bs = Infinity;
    for (let x = -400; x <= 400; x += 10) for (let z = -400; z <= 400; z += 10) {
      const h0 = this.height(x, z);
      let m = 0;
      for (let k = 0; k < 8; k++) m = Math.max(m, Math.abs(this.height(x + 6 * Math.cos(k * Math.PI / 4), z + 6 * Math.sin(k * Math.PI / 4)) - h0) / 6);
      if (m < bs) { bs = m; best = { x, z, y: h0 }; }
    }
    return best;
  }
}

function cr(t: number): [number, number, number, number] {
  const t2 = t * t, t3 = t2 * t;
  return [-0.5 * t3 + t2 - 0.5 * t, 1.5 * t3 - 2.5 * t2 + 1, -1.5 * t3 + 2 * t2 + 0.5 * t, 0.5 * t3 - 0.5 * t2];
}

function hash(ix: number, iz: number, k: number): number {
  let h = Math.imul(ix, 374761393) ^ Math.imul(iz, 668265263) ^ Math.imul(k + 1, 2147483647);
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}

function valueNoise(x: number, z: number, k: number): number {
  const x0 = Math.floor(x), z0 = Math.floor(z), tx = x - x0, tz = z - z0;
  const sx = tx * tx * tx * (tx * (tx * 6 - 15) + 10), sz = tz * tz * tz * (tz * (tz * 6 - 15) + 10);
  const a = hash(x0, z0, k), b = hash(x0 + 1, z0, k), c = hash(x0, z0 + 1, k), d = hash(x0 + 1, z0 + 1, k);
  return (a * (1 - sx) + b * sx) * (1 - sz) + (c * (1 - sx) + d * sx) * sz;
}

function gaussian(src: Float32Array, n: number, sigma: number): Float32Array {
  const r = Math.ceil(sigma * 3), k = new Float32Array(2 * r + 1);
  let sum = 0;
  for (let i = -r; i <= r; i++) sum += (k[i + r] = Math.exp(-(i * i) / (2 * sigma * sigma)));
  for (let i = 0; i < k.length; i++) k[i] /= sum;
  const tmp = new Float32Array(n * n), out = new Float32Array(n * n), kl = k.length;
  // rows then columns; the interior (no clamping) is the hot loop, the r posts at each edge clamp
  for (let y = 0; y < n; y++) {
    const row = y * n;
    for (let x = 0; x < n; x++) {
      let s = 0;
      if (x >= r && x < n - r) { const b = row + x - r; for (let i = 0; i < kl; i++) s += src[b + i] * k[i]; }
      else for (let i = -r; i <= r; i++) s += src[row + Math.min(n - 1, Math.max(0, x + i))] * k[i + r];
      tmp[row + x] = s;
    }
  }
  for (let y = 0; y < n; y++) {                       // columns, accumulated a whole row at a time (sequential memory)
    const o = y * n;
    for (let i = -r; i <= r; i++) {
      const w = k[i + r], src2 = Math.min(n - 1, Math.max(0, y + i)) * n;
      for (let x = 0; x < n; x++) out[o + x] += tmp[src2 + x] * w;
    }
  }
  return out;
}
