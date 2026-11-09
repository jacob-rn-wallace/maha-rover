/** Statistics of the rock generator (src/rocks.ts) on a flat stand-in terrain: `npm run check:rocks`.
 *  Expected: 144 rocks of 2 m and more per km2 on average (Joulaud et al. 2024), the cumulative areal fraction c(d) = K d^-1.326 (Bandfield et al. 2011) with K = 0.00285.
 */
import * as THREE from "three";
import { RockField, ROCK_K, ROCK_LAW } from "../src/rocks";

const terrain: any = { half: 2500, height: () => 0, detail: () => 0, spawn: { x: 0, z: 0, y: 0 } };
const field = new RockField(terrain, new THREE.MeshBasicMaterial(), terrain.spawn);
const tiers = (field as any).tiers.map((t: any) => t.tier);
// each tier is counted over a square suited to its size: 0.4 km for the stones, 1.6 km for the rocks, the whole tile (4.8 km) for the boulders
const halves = [200, 800, 2400];
const perTier: { tier: any; area: number; rocks: any[] }[] = tiers.map((tier: any, k: number) => {
  const L = halves[k], n0 = Math.floor(-L / tier.cell), n1 = Math.floor(L / tier.cell), rocks: any[] = [];
  for (let j = n0; j <= n1; j++) for (let i = n0; i <= n1; i++) for (const r of field.rocksIn(tier, i, j)) if (Math.abs(r.x) <= L && Math.abs(r.z) <= L) rocks.push(r);
  return { tier, area: (2 * L) ** 2, rocks };                      // m2
});
console.log("rocks: " + perTier.map((t) => `${t.tier.name} ${t.rocks.length} in ${(t.area / 1e6).toFixed(2)} km2`).join(", "));
const count = (d: number) => perTier.reduce((a, t) => a + t.rocks.filter((r) => r.d >= d).length / t.area * 1e6, 0);                               // per km2
const cover = (d: number) => perTier.reduce((a, t) => a + t.rocks.filter((r) => r.d >= d).reduce((b, r) => b + Math.PI * r.d * r.d / 4, 0) / t.area, 0);
for (const d of [0.12, 0.25, 0.5, 1, 2, 3, 5, 10]) {
  const model = ROCK_K * Math.pow(d, -ROCK_LAW.b);
  console.log(`d >= ${String(d).padEnd(4)} m: ${count(d).toFixed(0).padStart(8)} per km2, areal fraction ${(cover(d) * 100).toFixed(3)}% (law: ${(model * 100).toFixed(3)}%)`);
}
console.log(`mapped density target: ${ROCK_LAW.n2PerKm2} per km2 of 2 m and more; K = ${ROCK_K.toFixed(5)}`);
const t0 = performance.now(); field.update(0, 0); console.log(`first update (3 tiers round the origin): ${(performance.now() - t0).toFixed(0)} ms, instances ${(field as any).tiers.map((t: any) => t.mesh.count).join(" ")}`);
const t1 = performance.now(); field.update(20, 0); console.log(`update after 20 m: ${(performance.now() - t1).toFixed(0)} ms`);
const t2 = performance.now(); const ph = field.physics(0, 0); console.log(`physics set at the origin: ${ph.hulls.length} hulls, ${(performance.now() - t2).toFixed(0)} ms`);
