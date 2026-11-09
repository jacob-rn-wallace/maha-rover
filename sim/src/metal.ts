import * as THREE from "three";

/** Metal surface detail without texture coordinates (the exported model has none): a brushed or machined grain computed in the shader from the part's own coordinates.
 *  Streaks run along the face's long in-plane axis (the one most nearly horizontal in the part's frame; x for faces that face up or down), noise is stretched 40:1 across them.
 *  It modulates the roughness (+-0.12) and the albedo (+-3%) and nudges the normal across the grain by a few degrees, so highlights break up the way sheet and extrusion do.
 *  Look-development choices, not measurements: the real finishes are ASSUMPTIONS in hardware/sim/export_sim.py MATERIALS.
 *  Applied to materials with metalness >= 0.3 (the aluminium, steel and anodised parts); plastics, glass and cells are left alone.
 */
export function applyMetalDetail(material: THREE.Material) {
  const m = material as THREE.MeshStandardMaterial;
  if (!m.isMeshStandardMaterial || m.metalness < 0.3 || m.userData.metalDetail) return;
  m.userData.metalDetail = true;
  const prev = m.onBeforeCompile, prevKey = m.customProgramCacheKey.bind(m);
  m.onBeforeCompile = (shader, renderer) => {
    prev?.call(m, shader, renderer);
    shader.vertexShader = "varying vec3 vMdPos; varying vec3 vMdN;\n" + shader.vertexShader.replace("#include <begin_vertex>", "#include <begin_vertex>\n  vMdPos = position; vMdN = normal;");
    shader.fragmentShader = `varying vec3 vMdPos; varying vec3 vMdN;
float mdHash( vec2 p ) { p = fract( p * vec2( 123.34, 456.21 ) ); p += dot( p, p + 45.32 ); return fract( p.x * p.y ); }
float mdNoise( vec2 p ) { vec2 i = floor( p ), f = fract( p ); f = f * f * ( 3.0 - 2.0 * f );
  return mix( mix( mdHash( i ), mdHash( i + vec2( 1, 0 ) ), f.x ), mix( mdHash( i + vec2( 0, 1 ) ), mdHash( i + vec2( 1, 1 ) ), f.x ), f.y ); }
float mdGrain( vec3 p, vec3 n, out float across ) {
  vec3 a = cross( n, vec3( 0.0, 1.0, 0.0 ) ); a = dot( a, a ) < 1e-3 ? vec3( 1.0, 0.0, 0.0 ) : normalize( a );
  vec3 b = normalize( cross( n, a ) );
  float u = dot( p, a ) * 1000.0 / 40.0, v = dot( p, b ) * 1000.0;          // part coordinates are metres: v in mm, 1 grain per mm across, 40 mm along
  across = v;
  return 0.6 * mdNoise( vec2( u, v ) ) + 0.4 * mdNoise( vec2( u * 3.1 + 5.0, v * 2.3 + 9.0 ) );
}
` + shader.fragmentShader
      .replace("#include <color_fragment>", "#include <color_fragment>\n  float mdAcross; float mdG = mdGrain( vMdPos, normalize( vMdN ), mdAcross ) - 0.5;\n  diffuseColor.rgb *= 1.0 + 0.06 * mdG;")
      .replace("#include <roughnessmap_fragment>", "#include <roughnessmap_fragment>\n  roughnessFactor = clamp( roughnessFactor + 0.24 * mdG, 0.05, 1.0 );")
      .replace("#include <normal_fragment_maps>", "#include <normal_fragment_maps>\n  { vec3 mdT = normalize( cross( normal, vec3( 0.0, 1.0, 0.0 ) + 1e-3 ) ); normal = normalize( normal + mdT * mdG * 0.08 ); }");
  };
  m.customProgramCacheKey = () => prevKey() + "|metalDetail";
  m.needsUpdate = true;
}
