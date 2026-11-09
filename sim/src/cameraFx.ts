import * as THREE from "three";

/** The mast camera's image as the sensor and lens would deliver it, not as the renderer draws it: the scene is rendered at the camera's stream resolution into a linear float target,
 *  then a pass applies the lens's cos^4 natural vignetting, Poisson-Gaussian sensor noise and the display tone curve.
 *  Method and form follow the camera model of Chrono::Sensor (arXiv 2410.04371: cos^4 vignetting, Poisson-Gaussian noise, an HDR response curve).
 *  - Vignetting: the relative illumination at field angle t is cos^4(t), t = atan(r / f), r the distance from the principal point on the sensor and f = 4 mm (the lens, `docs/mast-spec.md`);
 *    at the corner of the 6.287 x 4.712 mm image area t is 44.5 degrees and the factor 0.26. The Pi's image pipeline normally applies lens-shading correction that removes most of it;
 *    ?vignette=0..1 scales the effect (default 0.6: ASSUMPTION, a look choice for a partly corrected image).
 *  - Noise: shot noise with variance equal to the signal over a full-well capacity of FULL_WELL electrons, plus Gaussian read noise of READ_E electrons, per channel, in linear light before the tone curve.
 *    FULL_WELL = 4000 and READ_E = 3 are ASSUMPTIONS (the IMX477's pixels are 1.55 um: small, so a full well of a few thousand electrons and a read noise of a few electrons are typical; neither figure was looked up). ?noise=0 switches it off.
 *  - Lens distortion: radial, barrel, r_ideal = r (1 + K1 r^2 + K2 r^4) with r the distance from the image centre over the half-diagonal (the output pixel at r shows the scene point an ideal pinhole
 *    camera would put at r_ideal). K1 = 0.08 and K2 = 0 give about 7% barrel distortion at the corners (TV distortion): ASSUMPTION, a typical figure for a wide-angle fixed-focus lens, not this lens's
 *    (the 4 mm lens is one retailer's listing with no maker named, `docs/mast-spec.md`). The scene is rendered with a field of view widened by the corner factor so the corners are real picture;
 *    ?distort=0 turns it off, ?distort=k scales K1.
 *  - Auto-exposure: a centre-weighted mean of the scene's linear luminance (a Gaussian of sigma 0.4 of the half-height, the way the Pi's camera stack meters by default, from memory) is held at
 *    AE_TARGET by a gain that moves towards it with time constant AE_TAU, between AE_MIN and AE_MAX. The target 0.18 (mid-grey in linear light), AE_TAU = 0.5 s and the gain limits are ASSUMPTIONS. The metering image is read back
 *    at 32 x 24 every few frames. The gain scales the signal before the noise, so a dark scene is noisier relative to its signal, as on a sensor. ?ae=0 holds the gain at 1.
 *  - Not modelled: defocus, chromatic effects, the sensor's colour response, rolling shutter, compression.
 */
const FULL_WELL = 4000, READ_E = 3;
const SENSOR_W = 6.287, SENSOR_H = 4.712, FOCAL = 4.0;
const K1 = 0.08, K2 = 0;
const SKY_L = 0.003;
const AE_TARGET = 0.18, AE_TAU = 0.5, AE_MIN = 0.05, AE_MAX = 32, METER_W = 32, METER_H = 24, METER_EVERY = 6, SCENE_EVERY = 2;

export class MastCameraFx {
  readonly target: THREE.WebGLRenderTarget;
  private quad: THREE.Mesh; private cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1); private scene = new THREE.Scene();
  private mat: THREE.ShaderMaterial; private snapMat: THREE.ShaderMaterial; private snapTarget: THREE.WebGLRenderTarget;
  private frame = 0;
  readonly k1: number; private sMax: number;
  private ae: boolean; gain = 1;
  private meterTarget = new THREE.WebGLRenderTarget(METER_W, METER_H, { type: THREE.UnsignedByteType, colorSpace: THREE.LinearSRGBColorSpace });      // 8 bit: the read-back is asynchronous (no GPU stall); the luminance is stored as sqrt(L / 4)
  private meterMat: THREE.ShaderMaterial; private meterBuf = new Uint8Array(METER_W * METER_H * 4); private metering = false;
  private lastT = performance.now();
  /** metered scene luminance, for display */
  metered = 0;
  stats = { started: 0, done: 0, failed: '' };

  constructor(readonly renderer: THREE.WebGLRenderer, width = 640, height = 480, vignette = 0.6, noise = 1, distort = 1, ae = true) {
    this.k1 = K1 * distort; this.sMax = Math.max(1, 1 + this.k1 + K2); this.ae = ae;
    this.target = new THREE.WebGLRenderTarget(width, height, { type: THREE.HalfFloatType, samples: 0, colorSpace: THREE.LinearSRGBColorSpace });
    this.mat = new THREE.ShaderMaterial({
      uniforms: { tex: { value: this.target.texture }, seed: { value: 0 }, vig: { value: vignette }, noiseOn: { value: noise }, k1: { value: this.k1 }, k2: { value: K2 }, sMax: { value: this.sMax }, gain: { value: 1 }, sensorHalf: { value: new THREE.Vector2(SENSOR_W / 2, SENSOR_H / 2) } },
      vertexShader: "varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }",
      fragmentShader: `uniform sampler2D tex; uniform float seed, vig, noiseOn, k1, k2, sMax, gain; uniform vec2 sensorHalf; varying vec2 vUv;
        float h1(vec2 p){ vec3 q = fract(vec3(p, seed) * vec3(0.1031, 0.1030, 0.0973)); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
        vec3 gauss(vec2 p){ vec3 u1 = vec3(h1(p), h1(p + 7.1), h1(p + 13.7)), u2 = vec3(h1(p + 3.3), h1(p + 11.9), h1(p + 19.3)); return sqrt(-2.0 * log(max(u1, 1e-4))) * cos(6.2831853 * u2); }
        void main(){
          float hd = length(sensorHalf);
          vec2 n = (vUv - 0.5) * 2.0 * sensorHalf / hd;               // sensor position over the half-diagonal
          float r2 = dot(n, n), sc = 1.0 + k1 * r2 + k2 * r2 * r2;
          vec2 uvIdeal = 0.5 + n * sc * hd / (2.0 * sensorHalf);       // where the ideal pinhole image shows this scene point
          vec2 uvTex = 0.5 + (uvIdeal - 0.5) / sMax;                   // the target was rendered sMax times wider
          vec3 c = max(texture2D(tex, uvTex).rgb, 0.0) * gain;
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
    // a still is the same pass drawn into an 8-bit offscreen target: three applies no tone mapping or colour space conversion when drawing into a target, so this variant has the ACES filmic curve
    // (the renderer's exposure) and the sRGB encoding written out in the shader
    const aces = `vec3 snapRRT( vec3 v ) { vec3 a = v * ( v + 0.0245786 ) - 0.000090537; vec3 b = v * ( 0.983729 * v + 0.4329510 ) + 0.238081; return a / b; }
        vec3 snapTone( vec3 c ) {
          const mat3 I = mat3( vec3( 0.59719, 0.07600, 0.02840 ), vec3( 0.35458, 0.90834, 0.13383 ), vec3( 0.04823, 0.01566, 0.83777 ) );
          const mat3 O = mat3( vec3( 1.60475, -0.10208, -0.00327 ), vec3( -0.53108, 1.10813, -0.07276 ), vec3( -0.07367, -0.00605, 1.07602 ) );
          c *= ${this.renderer.toneMappingExposure.toFixed(3)} / 0.6; c = O * snapRRT( I * c ); c = clamp( c, 0.0, 1.0 );
          return mix( c * 12.92, 1.055 * pow( c, vec3( 1.0 / 2.4 ) ) - 0.055, step( 0.0031308, c ) ); }
        `;
    this.snapMat = new THREE.ShaderMaterial({
      uniforms: this.mat.uniforms, vertexShader: this.mat.vertexShader, depthTest: false, depthWrite: false, toneMapped: false,
      fragmentShader: aces + this.mat.fragmentShader.replace(/#include <tonemapping_fragment>\s*#include <colorspace_fragment>/, "gl_FragColor.rgb = snapTone( gl_FragColor.rgb );"),
    });
    this.snapTarget = new THREE.WebGLRenderTarget(width, height, { type: THREE.UnsignedByteType, samples: 0, colorSpace: THREE.LinearSRGBColorSpace });
    this.meterMat = new THREE.ShaderMaterial({
      uniforms: { tex: { value: this.target.texture } },
      vertexShader: "varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }",
      fragmentShader: `uniform sampler2D tex; varying vec2 vUv;
        void main(){ vec3 s = vec3(0.0); for (int i = 0; i < 5; i++) for (int j = 0; j < 5; j++) s += texture2D(tex, vUv + (vec2(float(i), float(j)) - 2.0) / vec2(${METER_W * 5}.0, ${METER_H * 5}.0)).rgb; gl_FragColor = vec4(sqrt(clamp(s / 25.0 / 4.0, 0.0, 1.0)), 1.0); }`,
      toneMapped: false, depthTest: false, depthWrite: false,
    });
    this.quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.mat);
    this.scene.add(this.quad);
  }

  /** field of view (vertical, degrees) to render with so that the distortion pass has picture out to the corners */
  renderFov(fovDeg: number) { return 2 * Math.atan(Math.tan(fovDeg * Math.PI / 360) * this.sMax) * 180 / Math.PI; }

  private meter() {
    if (this.metering) return;
    const r = this.renderer;
    this.quad.material = this.meterMat; r.setRenderTarget(this.meterTarget); r.setScissorTest(false); r.setViewport(0, 0, METER_W, METER_H); r.render(this.scene, this.cam); r.setRenderTarget(null);
    this.quad.material = this.mat;
    this.metering = true; this.stats.started++;
    r.readRenderTargetPixelsAsync(this.meterTarget, 0, 0, METER_W, METER_H, this.meterBuf).then(() => { this.metering = false; this.stats.done++; this.adapt(); }, (e) => { this.metering = false; this.stats.failed = String(e); });
  }

  private adapt() {
    let sum = 0, wsum = 0;
    for (let j = 0; j < METER_H; j++) for (let i = 0; i < METER_W; i++) {
      const x = (i + 0.5) / METER_W - 0.5, y = ((j + 0.5) / METER_H - 0.5) * METER_H / METER_W, w = Math.exp(-(x * x + y * y) / (2 * (0.4 * 0.5 * METER_H / METER_W) ** 2));
      const k = (j * METER_W + i) * 4, d = (c: number) => { const v = this.meterBuf[c] / 255; return v * v * 4; };
      const L = 0.2126 * d(k) + 0.7152 * d(k + 1) + 0.0722 * d(k + 2);
      if (L < SKY_L) continue;                                 // black sky carries no information to meter on (a highlight- and shadow-aware metering, like the Pi's histogram weighting; ASSUMPTION)
      sum += w * L; wsum += w;
    }
    this.metered = wsum > 0 ? sum / wsum : AE_TARGET;
    const now = performance.now(), dt = Math.min((now - this.lastT) / 1000, 0.5); this.lastT = now;
    const want = Math.min(AE_MAX, Math.max(AE_MIN, AE_TARGET / Math.max(this.metered, 1e-4)));
    this.gain *= Math.exp(Math.log(want / this.gain) * (1 - Math.exp(-dt / AE_TAU)));
  }

  /** the current image (the last scene pass through the vignette, noise, distortion and tone curve) as a canvas at the stream's resolution: a still for the camera roll */
  snapshot(): HTMLCanvasElement {
    const r = this.renderer, w = this.snapTarget.width, h = this.snapTarget.height;
    this.quad.material = this.snapMat; r.setRenderTarget(this.snapTarget); r.setScissorTest(false); r.setViewport(0, 0, w, h); r.clear(); r.render(this.scene, this.cam); r.setRenderTarget(null);
    this.quad.material = this.mat;
    (r.getContext() as WebGL2RenderingContext).bindBuffer(WebGL2RenderingContext.PIXEL_PACK_BUFFER, null);      // the metering's asynchronous read leaves a pack buffer bound, which makes a synchronous read fail (INVALID_OPERATION)
    const buf = new Uint8Array(w * h * 4); r.readRenderTargetPixels(this.snapTarget, 0, 0, w, h, buf);
    const img = new ImageData(w, h);
    for (let y = 0; y < h; y++) img.data.set(buf.subarray((h - 1 - y) * w * 4, (h - y) * w * 4), y * w * 4);      // rows come bottom-up
    const c = document.createElement("canvas"); c.width = w; c.height = h; c.getContext("2d")!.putImageData(img, 0, 0);
    return c;
  }

  /** render `scene` through `camera` into the sensor target, then draw the processed image into the screen rectangle (CSS pixels, origin bottom left) */
  render(scene: THREE.Scene, camera: THREE.Camera, x: number, y: number, w: number, h: number) {
    const r = this.renderer;
    r.setScissorTest(false);
    if (this.frame % SCENE_EVERY === 0) {                      // the scene is rendered into the sensor image at 1 / SCENE_EVERY of the frame rate (the stream's rate; a second full pass of the scene is the costly part); the noise pass runs every frame
      r.setRenderTarget(this.target); r.clear(); r.render(scene, camera); r.setRenderTarget(null);
      if (this.ae && this.frame % (METER_EVERY * SCENE_EVERY) === 0) this.meter();
    }
    this.mat.uniforms.gain.value = this.ae ? this.gain : 1;
    this.mat.uniforms.seed.value = (this.frame++ % 997) * 0.37;
    r.setViewport(x, y, w, h); r.setScissor(x, y, w, h); r.setScissorTest(true);
    r.clear(); r.render(this.scene, this.cam);
    r.setScissorTest(false);
  }
}
