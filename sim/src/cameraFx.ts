import * as THREE from "three";

/** The mast camera's image as the sensor and lens would deliver it, not as the renderer draws it: the scene is rendered at the camera's stream resolution into a linear float target,
 *  then a pass applies the lens's cos^4 natural vignetting, Poisson-Gaussian sensor noise and the display tone curve.
 *  Method and form follow the camera model of Chrono::Sensor (arXiv 2410.04371: cos^4 vignetting, Poisson-Gaussian noise, an HDR response curve).
 *  - Vignetting: the relative illumination at field angle t is cos^4(t), t = atan(r / f), r the distance from the principal point on the sensor and f = 4 mm (the lens, `docs/mast-spec.md`);
 *    at the corner of the 6.287 x 4.712 mm image area t is 44.5 degrees and the factor 0.26. The Pi's image pipeline normally applies lens-shading correction that removes most of it;
 *    ?vignette=0..1 scales the effect (default 0.6: ASSUMPTION, a look choice for a partly corrected image).
 *  - Noise: shot noise with variance equal to the signal over a full-well capacity of FULL_WELL electrons, plus Gaussian read noise of READ_E electrons, per channel, in linear light before the tone curve.
 *    FULL_WELL = 4000 and READ_E = 3 are ASSUMPTIONS (the IMX477's pixels are 1.55 um: small, so a full well of a few thousand electrons and a read noise of a few electrons are typical; neither figure was looked up). ?noise=0 switches it off.
 *  - Not modelled: lens distortion, defocus, chromatic effects, the sensor's colour response, rolling shutter, auto-exposure and compression.
 */
const FULL_WELL = 4000, READ_E = 3;
const SENSOR_W = 6.287, SENSOR_H = 4.712, FOCAL = 4.0;

export class MastCameraFx {
  readonly target: THREE.WebGLRenderTarget;
  private quad: THREE.Mesh; private cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1); private scene = new THREE.Scene();
  private mat: THREE.ShaderMaterial;
  private frame = 0;

  constructor(private renderer: THREE.WebGLRenderer, width = 640, height = 480, vignette = 0.6, noise = 1) {
    this.target = new THREE.WebGLRenderTarget(width, height, { type: THREE.HalfFloatType, samples: 4, colorSpace: THREE.LinearSRGBColorSpace });
    this.mat = new THREE.ShaderMaterial({
      uniforms: { tex: { value: this.target.texture }, seed: { value: 0 }, vig: { value: vignette }, noiseOn: { value: noise }, sensorHalf: { value: new THREE.Vector2(SENSOR_W / 2, SENSOR_H / 2) } },
      vertexShader: "varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }",
      fragmentShader: `uniform sampler2D tex; uniform float seed, vig, noiseOn; uniform vec2 sensorHalf; varying vec2 vUv;
        float h1(vec2 p){ vec3 q = fract(vec3(p, seed) * vec3(0.1031, 0.1030, 0.0973)); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
        vec3 gauss(vec2 p){ vec3 u1 = vec3(h1(p), h1(p + 7.1), h1(p + 13.7)), u2 = vec3(h1(p + 3.3), h1(p + 11.9), h1(p + 19.3)); return sqrt(-2.0 * log(max(u1, 1e-4))) * cos(6.2831853 * u2); }
        void main(){
          vec3 c = max(texture2D(tex, vUv).rgb, 0.0);
          vec2 r = (vUv - 0.5) * 2.0 * sensorHalf;                         // mm from the principal point on the sensor
          float cos2 = ${(FOCAL * FOCAL).toFixed(1)} / (${(FOCAL * FOCAL).toFixed(1)} + dot(r, r));
          c *= mix(1.0, cos2 * cos2, vig);                            // cos^4 of the field angle
          vec2 px = gl_FragCoord.xy;
          c += noiseOn * gauss(px) * sqrt(c / ${FULL_WELL.toFixed(1)} + pow(${READ_E.toFixed(1)} / ${FULL_WELL.toFixed(1)}, 2.0));
          gl_FragColor = vec4(max(c, 0.0), 1.0);
          #include <tonemapping_fragment>
          #include <colorspace_fragment>
        }`,
      toneMapped: true, depthTest: false, depthWrite: false,
    });
    this.quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.mat);
    this.scene.add(this.quad);
  }

  /** render `scene` through `camera` into the sensor target, then draw the processed image into the screen rectangle (CSS pixels, origin bottom left) */
  render(scene: THREE.Scene, camera: THREE.Camera, x: number, y: number, w: number, h: number) {
    const r = this.renderer;
    r.setScissorTest(false);
    r.setRenderTarget(this.target); r.clear(); r.render(scene, camera); r.setRenderTarget(null);
    this.mat.uniforms.seed.value = (this.frame++ % 997) * 0.37;
    r.setViewport(x, y, w, h); r.setScissor(x, y, w, h); r.setScissorTest(true);
    r.clear(); r.render(this.scene, this.cam);
    r.setScissorTest(false);
  }
}
