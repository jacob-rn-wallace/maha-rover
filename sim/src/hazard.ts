import * as THREE from "three";
import { LIMITS } from "./limits";

/** Hazard overlay (H): the ground tinted by local slope and the rocks by their height, in four classes, as VERVE's hazard map does for VIPER (docs/sim-ui-research.md).
 *  Slope is the angle of the drawn mesh's normal from the vertical (the mesh carries the relief down to 0.25 m cells near the rover), not the centimetre-scale shading noise.
 *  Slope classes: under half the tilt guard's resume angle, up to that angle, up to the cut angle, past it (the guard cuts the drive there): 7.5, 15 and 25 degrees from `LIMITS.tilt`.
 *  Rock step height classes: 5, 10 and 20 cm: the sim's own findings (docs/sim-spec.md, tilt guard): a 0.1 m rock is climbed with the guard's help, a 0.2 m rock lifts the front to 48 degrees.
 *  A rock's height is taken as 0.7 of its instance's vertical scale (buried by 20 to 40% of it, rocks.ts). The tint fades out between `near` and `far` metres from the rover:
 *  beyond that the ground mesh is 1 to 10 m cells and its slope no longer says what the wheels will meet. Tints are alpha blends before tone mapping; the colours and alphas are look choices.
 */
export const SLOPE_CLASSES_DEG = [LIMITS.tilt.yellow / 2, LIMITS.tilt.yellow, LIMITS.tilt.red] as const;
export const STEP_CLASSES_M = [0.05, 0.10, 0.20] as const;
const CLASS_COLOURS = [[0.20, 0.75, 0.30], [0.80, 0.85, 0.20], [1.00, 0.62, 0.15], [1.00, 0.20, 0.15]];      // gentle, moderate, steep (the HUD's yellow), over the limit (the HUD's red)
const CLASS_HEX = ["#33bf4d", "#ccd933", "#ff9e26", "#ff3326"];

const RAMP = `
vec4 hzRamp( float v, vec3 t, vec4 a ) {
  vec3 c = vec3( ${CLASS_COLOURS[0].join(", ")} );
  float al = a.x;
  float k1 = smoothstep( t.x * 0.9, t.x * 1.1, v ), k2 = smoothstep( t.y * 0.9, t.y * 1.1, v ), k3 = smoothstep( t.z * 0.9, t.z * 1.1, v );
  c = mix( c, vec3( ${CLASS_COLOURS[1].join(", ")} ), k1 ); al = mix( al, a.y, k1 );
  c = mix( c, vec3( ${CLASS_COLOURS[2].join(", ")} ), k2 ); al = mix( al, a.z, k2 );
  c = mix( c, vec3( ${CLASS_COLOURS[3].join(", ")} ), k3 ); al = mix( al, a.w, k3 );
  return vec4( c, al );
}`;

export class HazardOverlay {
  on = false;
  readonly near = 25; readonly far = 70;
  private uniforms = {
    hzOn: { value: 0 }, hzCenter: { value: new THREE.Vector2() }, hzNear: { value: this.near }, hzFar: { value: this.far },
    hzSlope: { value: new THREE.Vector3(...SLOPE_CLASSES_DEG) }, hzStep: { value: new THREE.Vector3(...STEP_CLASSES_M) },
  };
  readonly legend = document.createElement("div");      // shown in the top bar's legend popover
  onChange?: (on: boolean) => void;

  constructor(coarse: boolean) {
    const sw = (i: number) => `<span style="display:inline-block;width:10px;height:10px;background:${CLASS_HEX[i]};margin:0 4px 0 8px;vertical-align:-1px"></span>`;
    const [a, b, c] = SLOPE_CLASSES_DEG;
    this.legend.innerHTML = `<b>hazard</b> slope${sw(0)}under ${a}°${sw(1)}to ${b}°${sw(2)}to ${c}°${sw(3)}over ${c}° (tilt guard cuts the drive)<br>rocks by height${sw(1)}${STEP_CLASSES_M[0] * 100}${sw(2)}${STEP_CLASSES_M[1] * 100}${sw(3)}${STEP_CLASSES_M[2] * 100} cm and over; within ${this.near} m of the rover, fading by ${this.far} m`;
    this.legend.style.cssText = `font:${coarse ? 11 : 12}px/1.6 system-ui;white-space:normal`;
  }

  toggle() { this.set(!this.on); }
  set(on: boolean) { this.on = on; this.uniforms.hzOn.value = on ? 1 : 0; this.onChange?.(on); }
  /** runs `draw` with the tint off: the mast camera must not see the operator's overlay */
  without(draw: () => void) { const v = this.uniforms.hzOn.value; this.uniforms.hzOn.value = 0; try { draw(); } finally { this.uniforms.hzOn.value = v; } }
  update(x: number, z: number) { this.uniforms.hzCenter.value.set(x, z); }

  /** patches a material: "ground" tints by slope (the mesh normal), "rock" by the instance's height */
  apply(material: THREE.Material, kind: "ground" | "rock") {
    const prev = material.onBeforeCompile, prevKey = material.customProgramCacheKey.bind(material);
    material.onBeforeCompile = (shader, renderer) => {
      prev?.call(material, shader, renderer);
      Object.assign(shader.uniforms, this.uniforms);
      const world = kind === "rock" ? "(modelMatrix * instanceMatrix * vec4(transformed, 1.0)).xyz" : "(modelMatrix * vec4(transformed, 1.0)).xyz";
      const step = kind === "rock" ? "\n  vHzStep = length(instanceMatrix[1].xyz) * 0.7;" : "";
      shader.vertexShader = `varying vec3 vHzPos;${kind === "rock" ? "\nvarying float vHzStep;" : ""}\n` + shader.vertexShader.replace("#include <begin_vertex>", `#include <begin_vertex>\n  vHzPos = ${world};${step}`);
      const value = kind === "rock" ? "vHzStep" : "degrees( acos( clamp( ( normalize( vNormal ) * mat3( viewMatrix ) ).y, 0.0, 1.0 ) ) )";
      const alphas = kind === "rock" ? "vec4( 0.0, 0.55, 0.7, 0.8 )" : "vec4( 0.10, 0.28, 0.50, 0.60 )";
      const thresholds = kind === "rock" ? "hzStep" : "hzSlope";
      shader.fragmentShader = `varying vec3 vHzPos;${kind === "rock" ? "\nvarying float vHzStep;" : ""}
uniform float hzOn; uniform vec2 hzCenter; uniform float hzNear; uniform float hzFar; uniform vec3 hzSlope; uniform vec3 hzStep;
${RAMP}
` + shader.fragmentShader.replace("#include <opaque_fragment>", `#include <opaque_fragment>
  if ( hzOn > 0.5 ) {
    vec4 hz = hzRamp( ${value}, ${thresholds}, ${alphas} );
    float hzFade = 1.0 - smoothstep( hzNear, hzFar, length( vHzPos.xz - hzCenter ) );
    gl_FragColor.rgb = mix( gl_FragColor.rgb, hz.rgb, hz.a * hzFade );
  }`);
    };
    material.customProgramCacheKey = () => prevKey() + "|hazard" + kind;
    material.needsUpdate = true;
  }
}
