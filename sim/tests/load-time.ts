/** CPU time of the start-up steps in node (no GPU): Terrain.load (decode, smooth, spawn search) and the ring mesh. npm run check:load */
import * as THREE from "three";
import { readFileSync } from "node:fs";
import { Terrain } from "../src/terrain";
import { TerrainView } from "../src/terrainView";

(globalThis as any).fetch = async (u: string) => { const b = readFileSync("public/" + u); return { arrayBuffer: async () => b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength), json: async () => JSON.parse(b.toString()) }; };
const t = (label: string, t0: number) => console.log(label.padEnd(28), (performance.now() - t0).toFixed(0), "ms");
let t0 = performance.now();
const terrain = await Terrain.load("terrain/");
t("Terrain.load", t0);
t0 = performance.now();
const view = new TerrainView(terrain, new THREE.MeshBasicMaterial());
view.update(terrain.spawn.x, terrain.spawn.z);
t("TerrainView + first update", t0);
t0 = performance.now();
const r = await view.addRing();
t(`ring mesh (${r.triangles} tris)`, t0);
t0 = performance.now();
for (let i = 0; i < 20; i++) view.update(terrain.spawn.x + 20 * i, terrain.spawn.z);
t("20 clipmap updates (400 m)", t0);
