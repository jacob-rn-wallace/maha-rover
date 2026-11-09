import * as THREE from "three";
import { decode } from "fast-png";
import type { Terrain } from "./terrain";

/** Shadows cast by terrain onto terrain and rover: two precomputed lit-fraction textures (hardware/sim/terrain/shadow.py) for the fixed sun, multiplied into the sun's light in the shader.
 *  The renderer's own shadow map still covers the 4 m round the rover (the rover's shadow). The textures hold the sun they were computed for: if lunar.ts uses another sun,
 *  they are not applied (run shadow.py with the new angles).
 */
export interface TerrainShadow { tile: THREE.DataTexture; coarse: THREE.DataTexture; tileHalf: number; coarseHalf: number; sunElevationDeg: number; sunAzimuthDeg: number; }

export async function loadTerrainShadow(base = "terrain/"): Promise<TerrainShadow> {
  const meta = await fetch(base + "shadow.json").then((r) => r.json());
  const tex = async (f: string) => {
    const p = decode(await (await fetch(base + f)).arrayBuffer());
    const t = new THREE.DataTexture(p.data as Uint8Array, p.width, p.height, THREE.RedFormat, THREE.UnsignedByteType);
    t.minFilter = t.magFilter = THREE.LinearFilter;
    t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
    t.generateMipmaps = false; t.flipY = false; t.needsUpdate = true;
    return t;
  };
  const [tile, coarse] = await Promise.all([tex("shadow_tile.png"), tex("shadow_coarse.png")]);
  return { tile, coarse, tileHalf: meta.tile.half_m, coarseHalf: meta.coarse.half_m, sunElevationDeg: meta.sun_elevation_deg, sunAzimuthDeg: meta.sun_azimuth_deg };
}

/** multiply the sun's light by the terrain's lit fraction at the fragment's world position (world x, z: texture row 0 is north = -z) */
const patched = new WeakSet<THREE.Material>();
export function applyTerrainShadow(material: THREE.Material, ts: TerrainShadow) {
  if (patched.has(material)) return;
  patched.add(material);
  const prev = material.onBeforeCompile, prevKey = material.customProgramCacheKey.bind(material);
  material.onBeforeCompile = (shader, renderer) => {
    prev?.call(material, shader, renderer);
    shader.uniforms.tsTile = { value: ts.tile };
    shader.uniforms.tsCoarse = { value: ts.coarse };
    shader.uniforms.tsTileHalf = { value: ts.tileHalf };
    shader.uniforms.tsCoarseHalf = { value: ts.coarseHalf };
    shader.vertexShader = "varying vec3 vTsPos;\n" + shader.vertexShader.replace("#include <begin_vertex>",
      "#include <begin_vertex>\n  #ifdef USE_INSTANCING\n  vTsPos = (modelMatrix * instanceMatrix * vec4(transformed, 1.0)).xyz;\n  #else\n  vTsPos = (modelMatrix * vec4(transformed, 1.0)).xyz;\n  #endif");
    const chunk = THREE.ShaderChunk.lights_fragment_begin.replace("getDirectionalLightInfo( directionalLight, directLight );",
      "getDirectionalLightInfo( directionalLight, directLight );\n\t\tdirectLight.color *= terrainShadow( vTsPos );");
    shader.fragmentShader = `varying vec3 vTsPos;
uniform sampler2D tsTile; uniform sampler2D tsCoarse; uniform float tsTileHalf; uniform float tsCoarseHalf;
float terrainShadow( vec3 p ) {
  vec2 q = p.xz;
  if ( abs( q.x ) < tsTileHalf && abs( q.y ) < tsTileHalf ) return texture2D( tsTile, ( q + tsTileHalf ) / ( 2.0 * tsTileHalf ) ).r;
  if ( abs( q.x ) < tsCoarseHalf && abs( q.y ) < tsCoarseHalf ) return texture2D( tsCoarse, ( q + tsCoarseHalf ) / ( 2.0 * tsCoarseHalf ) ).r;
  return 1.0;
}
` + shader.fragmentShader.replace("#include <lights_fragment_begin>", chunk);
  };
  material.customProgramCacheKey = () => prevKey() + "|terrainShadow";
  material.needsUpdate = true;
}

/** Shadows for a sun other than the precomputed one (?sun=elevation,azimuth), computed in the browser by the same horizon sweep as shadow.py, from the terrain the sim itself draws
 *  (Terrain.height without the procedural detail, lunar curvature included, so far shadows come out slightly shorter than shadow.py's). Coarser than the precomputed files (8 m grid
 *  for the tile, 150 m for the 200 km map, blockers up to 20 km towards the sun beyond each map): takes a few seconds. */
export function computeTerrainShadow(terrain: Terrain, elDeg: number, azDeg: number): TerrainShadow {
  const SOFT = 2, T = Math.tan(elDeg * Math.PI / 180), az = azDeg * Math.PI / 180;
  const sx = Math.cos(az), sz = -Math.sin(az);                 // towards the sun on the ground, (east, south)
  const ex = -sx, ez = -sz, vx = -ez, vz = ex;                // e_u away from the sun, e_v perpendicular
  const map = (half: number, outStep: number, g: number, lead: number): THREE.DataTexture => {
    const diag = half * Math.SQRT2, nu = Math.ceil((2 * diag + lead) / g), nv = Math.ceil(2 * diag / g), u0 = -(diag + lead), v0 = -diag;
    const lit = new Float32Array(nu * nv), run = new Float32Array(nv).fill(-1e9);
    for (let i = 0; i < nu; i++) {
      const u = u0 + i * g;
      for (let j = 0; j < nv; j++) {
        const v = v0 + j * g, S = terrain.height(u * ex + v * vx, u * ez + v * vz, 1e9) + T * u;
        lit[i * nv + j] = Math.min(1, Math.max(0, 1 + (S - run[j]) / SOFT));
        if (S > run[j]) run[j] = S;
      }
    }
    const n = Math.round(2 * half / outStep), out = new Uint8Array(n * n);
    for (let r = 0; r < n; r++) for (let c = 0; c < n; c++) {
      const x = -half + outStep * (c + 0.5), z = -half + outStep * (r + 0.5);       // row 0 = north = -z
      const fu = ((x * ex + z * ez) - u0) / g, fv = ((x * vx + z * vz) - v0) / g;
      const i = Math.min(nu - 2, Math.max(0, Math.floor(fu))), j = Math.min(nv - 2, Math.max(0, Math.floor(fv))), a = Math.min(1, Math.max(0, fu - i)), b = Math.min(1, Math.max(0, fv - j));
      const l = (lit[i * nv + j] * (1 - b) + lit[i * nv + j + 1] * b) * (1 - a) + (lit[(i + 1) * nv + j] * (1 - b) + lit[(i + 1) * nv + j + 1] * b) * a;
      out[r * n + c] = Math.round(l * 255);
    }
    const t = new THREE.DataTexture(out, n, n, THREE.RedFormat, THREE.UnsignedByteType);
    t.minFilter = t.magFilter = THREE.LinearFilter; t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping; t.generateMipmaps = false; t.flipY = false; t.needsUpdate = true;
    return t;
  };
  return { tile: map(2500, 4, 8, 20000), coarse: map(100000, 100, 150, 20000), tileHalf: 2500, coarseHalf: 100000, sunElevationDeg: elDeg, sunAzimuthDeg: azDeg };
}
