import * as THREE from "three";

/** Regolith look, in the shader.
 *
 *  Photometry: the sun's direct light is weighted like a Lommel-Seeliger surface with a shadow-hiding opposition surge instead of a Lambertian one, as the lunar-regolith renderers do
 *  (Chrono::Sensor's lunar model, arXiv 2410.04371, "modern Hapke with simplifications": single scattering Lommel-Seeliger, shadow hiding B(g) = 1 + B0 / (1 + tan(g/2) / h),
 *  B0 = 1.80238 from its Table I; h = 0.050 from Sato et al. 2014 (maria, 40 S to 40 N: poleward of about 40 degrees the paper calls hS poorly constrained, and this site is at 47.6 N, so it is a mare value assumed to hold); coherent backscatter, multiple scattering and macroscopic roughness are left out).
 *  Lambert: radiance ~ cos(i). Lommel-Seeliger: radiance ~ cos(i) / (cos(i) + cos(e)), brighter towards grazing views and no darkening towards the limb;
 *  the weight on the irradiance is 2 / (cos i + cos e), equal to Lambert's at the vertical. The surge is normalised to 1 at a phase angle of 30 degrees (the full-Moon look: the picture brightens
 *  and loses contrast looking along the sun's direction). Look-development choices on top: the weight is capped at 3 and the albedo is the material's colour.
 *
 *  Ground only, ground texture: no tiled image at all (the earlier tiled texture repeated visibly). Albedo mottling and the centimetre-scale normal roughness are world-space value noise
 *  evaluated per pixel, octaves faded out as their wavelength drops under about two pixel footprints so nothing shimmers; the mesh carries the relief down to 0.5 m (terrain.ts).
 *  Octave strengths are look-development choices, not measurements.
 */
const B0 = 1.80238, H = 0.050;                      // B0: Chrono's; H: the maria's median hS 0.050 +- 0.008 (Sato et al. 2014, Fig. 16e text; Chrono's 0.07145 is the highlands' 0.074)

export function applyRegolithPhotometry(material: THREE.MeshStandardMaterial, opts: { ground?: boolean } = {}) {
  const prev = material.onBeforeCompile, prevKey = material.customProgramCacheKey.bind(material);
  material.onBeforeCompile = (shader, renderer) => {
    prev?.call(material, shader, renderer);
    const phys = THREE.ShaderChunk.lights_physical_pars_fragment.replace("vec3 irradiance = dotNL * directLight.color;",
      `float dotNV_r = saturate( dot( geometryNormal, geometryViewDir ) );
	float lsw = min( 2.0 / ( dotNL + dotNV_r + 1e-3 ), 3.0 );
	float cosg = clamp( dot( directLight.direction, geometryViewDir ), -1.0, 1.0 );
	float tanHalf = sqrt( max( ( 1.0 - cosg ) / ( 1.0 + cosg + 1e-4 ), 0.0 ) );
	float surge = ( 1.0 + ${B0.toFixed(5)} / ( 1.0 + tanHalf / ${H.toFixed(5)} ) ) / 1.2835;
	vec3 irradiance = dotNL * directLight.color * lsw * surge;`);
    shader.fragmentShader = shader.fragmentShader.replace("#include <lights_physical_pars_fragment>", phys);
    if (opts.ground) {
      shader.vertexShader = "varying vec3 vRegPos;\n" + shader.vertexShader.replace("#include <begin_vertex>", "#include <begin_vertex>\n  vRegPos = (modelMatrix * vec4(transformed, 1.0)).xyz;");
      shader.fragmentShader = `varying vec3 vRegPos;
float rgHash( vec2 p ) { p = fract( p * vec2( 123.34, 456.21 ) ); p += dot( p, p + 45.32 ); return fract( p.x * p.y ); }
float rgNoise( vec2 p ) { vec2 i = floor( p ), f = fract( p ); f = f * f * f * ( f * ( f * 6.0 - 15.0 ) + 10.0 );
  return mix( mix( rgHash( i ), rgHash( i + vec2( 1, 0 ) ), f.x ), mix( rgHash( i + vec2( 0, 1 ) ), rgHash( i + vec2( 1, 1 ) ), f.x ), f.y ); }
const mat2 RG_ROT = mat2( 0.8, 0.6, -0.6, 0.8 );
// mean-zero noise sum over wavelengths wl0, wl0/2.1, ...; each octave's weight fades as its wavelength approaches the pixel footprint
float rgFbm( vec2 p, float wl0, int n, float footprint, float decay ) {
  float s = 0.0, w = 1.0, wl = wl0; vec2 q = p;
  for ( int i = 0; i < 6; i++ ) { if ( i >= n ) break;
    float fade = smoothstep( 1.0 * footprint, 3.0 * footprint, wl );
    s += ( rgNoise( q / wl ) - 0.5 ) * w * fade; q = RG_ROT * q * 1.0 + 17.0; wl /= 2.1; w *= decay; }
  return s; }
` + shader.fragmentShader.replace("#include <color_fragment>", `#include <color_fragment>
      float fpt = max( length( fwidth( vRegPos ) ), 1e-4 );
      float mott = rgFbm( vRegPos.xz, 90.0, 6, fpt, 0.8 ) * 1.2 + rgFbm( vRegPos.xz + 311.0, 0.9, 4, fpt, 0.7 ) * 0.3;      // metre-scale patches and finer grain
      diffuseColor.rgb *= clamp( 1.0 + 0.45 * mott, 0.7, 1.35 );`)
        .replace("#include <normal_fragment_maps>", `#include <normal_fragment_maps>
      {
        float e = 0.02;
        vec2 P = vRegPos.xz;
        float h0 = rgFbm( P, 0.5, 5, fpt, 0.476 ), hx = rgFbm( P + vec2( e, 0.0 ), 0.5, 5, fpt, 0.476 ), hz = rgFbm( P + vec2( 0.0, e ), 0.5, 5, fpt, 0.476 );
        vec3 gw = vec3( hx - h0, 0.0, hz - h0 ) / e * 0.045;                       // world-space slope of the centimetre-scale relief
        vec3 gv = ( viewMatrix * vec4( gw, 0.0 ) ).xyz;
        gv -= dot( gv, normal ) * normal;
        normal = normalize( normal - gv );
      }`);
    }
  };
  material.customProgramCacheKey = () => prevKey() + (opts.ground ? "|regolithG" : "|regolith");
  material.needsUpdate = true;
}
