import * as THREE from "three";

/** The sky: real stars, the Milky Way and the Earth, at infinity.
 *
 *  Every layer is drawn with the camera's translation removed (the vertex shader multiplies by the rotation part of the view matrix only), so
 *  the sky turns with the camera and never moves with it: no parallax however far the camera is from the rover, like a skybox. The layers
 *  are drawn first, never depth-tested, and the terrain is drawn over them.
 *
 *  Data is made by `hardware/sim/sky/build_sky.py` (sources, epoch and checks are in its header and in `docs/sim-spec.md`, 'Sky'):
 *  Hipparcos stars to V 7.5 with their B-V colours, a Milky Way glow image, an Earth albedo image, and the matrices placing them in the
 *  world frame (x east, y up, z south) for the site and the epoch 2030-10-02 14:48 UTC, when the real Sun is where the simulation's default sun is (14 degrees up, bearing 108).
 *  The Earth is lit by the simulation's sun, so its phase agrees with the shadows on the ground and with the stars.
 */
interface SkyMeta {
  epoch_utc: string; n_stars: number;
  icrf_to_world: number[];
  earth: { dir_world: number[]; angular_radius_rad: number; world_to_fixed: number[]; bearing_deg: number; elevation_deg: number; sub_lunar_earth_latlon: number[] };
}

// the vertex shaders' common part: unit-sphere direction -> clip space, translation removed, on the far plane
const CLIP = `vec4 skyClip(vec3 d) { vec4 p = projectionMatrix * vec4(mat3(viewMatrix) * d, 1.0); p.z = p.w * 0.99999; return p; }`;

/** Black-body colour for a B-V index (Ballesteros 2012 for the temperature, a piecewise fit for the colour), desaturated: a camera's white balance and the eye
 *  both wash most of it out, but red and blue-white stars are still told apart. */
function starColour(bv: number): [number, number, number] {
  const T = 4600 * (1 / (0.92 * bv + 1.7) + 1 / (0.92 * bv + 0.62)), t = T / 100;
  let r = t <= 66 ? 255 : 329.7 * Math.pow(t - 60, -0.1332), g = t <= 66 ? 99.47 * Math.log(t) - 161.1 : 288.1 * Math.pow(t - 60, -0.0755), b = t >= 66 ? 255 : t <= 19 ? 0 : 138.5 * Math.log(t - 10) - 305.0;
  const c = [r, g, b].map((v) => Math.min(1, Math.max(0, v / 255)));
  const m = Math.max(...c);
  return c.map((v) => 0.45 + 0.55 * (v / m)) as [number, number, number];      // 45% white
}

export async function addSky(scene: THREE.Scene, sunDir: THREE.Vector3, base = "sky/") {
  const [meta, buf] = await Promise.all([
    fetch(base + "sky.json").then((r) => r.json() as Promise<SkyMeta>),
    fetch(base + "stars.bin").then((r) => r.arrayBuffer()),
  ]);
  const loader = new THREE.TextureLoader();
  const tex = (f: string, srgb: boolean) => new Promise<THREE.Texture>((res, rej) => loader.load(base + f, (t) => {
    t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace; t.generateMipmaps = false; t.minFilter = THREE.LinearFilter; t.magFilter = THREE.LinearFilter; res(t);
  }, undefined, rej));
  const [mwTex, earthTex] = await Promise.all([tex("milkyway.png", false), tex("earth.jpg", true)]);

  const R = meta.icrf_to_world;       // row-major, ICRF -> world
  const group = new THREE.Group(); group.name = "sky";

  // ---- Milky Way: a sphere looked up in the image by direction (RA, Dec)
  const toIcrf = new THREE.Matrix3().set(R[0], R[3], R[6], R[1], R[4], R[7], R[2], R[5], R[8]);      // the transpose: world -> ICRF
  const mwMat = new THREE.ShaderMaterial({
    uniforms: { map: { value: mwTex }, toIcrf: { value: toIcrf } },
    vertexShader: `varying vec3 d; ${CLIP} void main(){ d = position; gl_Position = skyClip(position); }`,
    fragmentShader: `varying vec3 d; uniform sampler2D map; uniform mat3 toIcrf;
      void main(){
        vec3 v = normalize(toIcrf * normalize(d));
        float ra = atan(v.y, v.x); ra += ra < 0.0 ? 6.28318530718 : 0.0;
        float g = texture2D(map, vec2(ra / 6.28318530718, 0.5 + asin(clamp(v.z, -1.0, 1.0)) / 3.14159265359)).r;
        gl_FragColor = vec4(vec3(0.95, 0.9, 0.82) * g * 0.16, 1.0);
        #include <colorspace_fragment>
      }`,
    depthTest: false, depthWrite: false, toneMapped: false, fog: false, side: THREE.BackSide,
  });
  const mw = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 24), mwMat);
  mw.renderOrder = -1003; mw.frustumCulled = false; group.add(mw);

  // ---- stars
  const n = meta.n_stars, dv = new DataView(buf);
  const pos = new Float32Array(n * 3), col = new Float32Array(n * 3), size = new Float32Array(n), lum = new Float32Array(n);
  const oRa = 0, oDec = 2 * n, oMag = 4 * n, oBv = 5 * n;
  for (let i = 0; i < n; i++) {
    const ra = (dv.getUint16(oRa + 2 * i, true) / 65536) * 2 * Math.PI, de = (dv.getInt16(oDec + 2 * i, true) / 32767) * (Math.PI / 2);
    const mag = dv.getUint8(oMag + i) / 25 - 2, bv = dv.getUint8(oBv + i) / 100 - 0.6;
    const x = Math.cos(de) * Math.cos(ra), y = Math.cos(de) * Math.sin(ra), z = Math.sin(de);        // ICRF
    pos.set([R[0] * x + R[1] * y + R[2] * z, R[3] * x + R[4] * y + R[5] * z, R[6] * x + R[7] * y + R[8] * z], i * 3);
    const [r, g, b] = starColour(bv); col.set([r, g, b], i * 3);
    lum[i] = Math.min(1, Math.max(0.14, 0.2 + (6.5 - mag) * 0.16));                                 // display brightness: look-development, not photometry
    size[i] = 1.3 + Math.min(2.2, Math.max(0, (4.5 - mag) * 0.35));                                 // px: brighter stars bloom larger
  }
  const sg = new THREE.BufferGeometry();
  sg.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  sg.setAttribute("color", new THREE.BufferAttribute(col, 3));
  sg.setAttribute("size", new THREE.BufferAttribute(size, 1));
  sg.setAttribute("lum", new THREE.BufferAttribute(lum, 1));
  const starMat = new THREE.ShaderMaterial({
    uniforms: { pr: { value: 1 } },
    vertexShader: `attribute float size; attribute float lum; varying vec3 c; uniform float pr; ${CLIP}
      void main(){ c = color * lum; gl_PointSize = size * pr; gl_Position = skyClip(position); }`,
    fragmentShader: `varying vec3 c;
      void main(){
        float r = length(gl_PointCoord - 0.5) * 2.0;
        float a = 1.0 - smoothstep(0.35, 1.0, r);
        gl_FragColor = vec4(c * a, 1.0);
        #include <colorspace_fragment>
      }`,
    vertexColors: true, blending: THREE.AdditiveBlending, transparent: false, depthTest: false, depthWrite: false, toneMapped: false, fog: false,
  });
  starMat.onBeforeRender = (r) => { starMat.uniforms.pr.value = r.getRenderTarget() ? 1 : r.getPixelRatio(); };      // sizes are in pixels of the image being drawn
  const stars = new THREE.Points(sg, starMat);
  stars.renderOrder = -1002; stars.frustumCulled = false; group.add(stars);

  // ---- Earth: a sphere whose silhouette subtends the true angular radius, textured by the Earth-fixed direction of each point, lit by the sun
  const e = meta.earth, ed = new THREE.Vector3(...e.dir_world), th = e.angular_radius_rad;
  const centre = ed.clone().multiplyScalar(Math.cos(th)), rad = Math.sin(th);
  const eg = new THREE.SphereGeometry(rad, 64, 40); eg.translate(centre.x, centre.y, centre.z);
  const F = e.world_to_fixed;
  const toFixed = new THREE.Matrix3().set(F[0], F[1], F[2], F[3], F[4], F[5], F[6], F[7], F[8]);
  const SUN_RADIANCE = 3.0 / Math.PI;           // the terrain's: sun light intensity 3.0 on a Lambertian surface (lunar.ts)
  const earthMat = new THREE.ShaderMaterial({
    uniforms: { map: { value: earthTex }, toFixed: { value: toFixed }, sun: { value: sunDir.clone().normalize() }, centre: { value: centre }, rad: { value: rad } },
    vertexShader: `varying vec3 n; varying vec3 dirW; uniform vec3 centre; uniform float rad; ${CLIP}
      void main(){ n = (position - centre) / rad; dirW = normalize(position); gl_Position = skyClip(position); }`,
    fragmentShader: `varying vec3 n; varying vec3 dirW; uniform sampler2D map; uniform mat3 toFixed; uniform vec3 sun;
      void main(){
        vec3 nn = normalize(n), f = toFixed * nn;
        vec2 uv = vec2(atan(f.y, f.x) / 6.28318530718 + 0.5, asin(clamp(f.z, -1.0, 1.0)) / 3.14159265359 + 0.5);
        vec3 alb = texture2D(map, uv).rgb;
        float ndl = dot(nn, sun), lit = smoothstep(-0.02, 0.12, ndl);                       // soft terminator (the atmosphere scatters past it)
        vec3 c = alb * ${SUN_RADIANCE.toFixed(5)} * max(ndl, 0.0) * 1.0;
        float rim = pow(1.0 - max(dot(nn, -dirW), 0.0), 3.0);                               // atmosphere at the limb, on the lit side
        c += vec3(0.16, 0.34, 0.9) * rim * 0.55 * lit * ${SUN_RADIANCE.toFixed(5)};
        gl_FragColor = vec4(c, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
    depthTest: false, depthWrite: false, fog: false,
  });
  const earth = new THREE.Mesh(eg, earthMat);
  earth.name = "earth"; earth.renderOrder = -1001; earth.frustumCulled = false; group.add(earth);

  scene.add(group);
  return { group, earth, meta, setSun(d: THREE.Vector3) { earthMat.uniforms.sun.value.copy(d).normalize(); } };
}
