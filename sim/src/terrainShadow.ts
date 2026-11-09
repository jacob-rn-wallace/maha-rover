import * as THREE from "three";
import { decode } from "fast-png";

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
      "#include <begin_vertex>\n  vTsPos = (modelMatrix * vec4(transformed, 1.0)).xyz;");
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
