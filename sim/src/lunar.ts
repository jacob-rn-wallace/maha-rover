import * as THREE from "three";

/** Lunar lighting and surface: a low sun, a black sky with stars, regolith-coloured ground bounce, a procedural regolith ground.
 *  Values are look-development choices, not measurements: sun elevation is a parameter; albedo 0.12 is the usual mean for the Moon (not sourced here).
 */
export interface LunarOpts { sunElevationDeg: number; sunAzimuthDeg: number; }

export function addLunarScene(scene: THREE.Scene, renderer: THREE.WebGLRenderer, opts: LunarOpts = { sunElevationDeg: 14, sunAzimuthDeg: 40 }) {
  scene.background = new THREE.Color(0x000000);
  const el = THREE.MathUtils.degToRad(opts.sunElevationDeg), az = THREE.MathUtils.degToRad(opts.sunAzimuthDeg);
  const sunDir = new THREE.Vector3(Math.cos(el) * Math.cos(az), Math.sin(el), -Math.cos(el) * Math.sin(az)).normalize();

  // sun: hard, white, no atmosphere
  const sun = new THREE.DirectionalLight(0xfff6ea, 3.0);
  sun.position.copy(sunDir).multiplyScalar(20);
  sun.castShadow = true;
  sun.shadow.mapSize.set(4096, 4096);
  Object.assign(sun.shadow.camera, { left: -2, right: 2, top: 2, bottom: -2, near: 1, far: 60 });
  sun.shadow.bias = -0.0002;
  sun.shadow.normalBias = 0.002;
  scene.add(sun);

  // environment for reflections and fill: black sky, a bright regolith floor lit by the sun, a small sun disc
  const envScene = new THREE.Scene();
  const sky = new THREE.Mesh(new THREE.SphereGeometry(50, 48, 24), new THREE.ShaderMaterial({
    side: THREE.BackSide,
    uniforms: { sunDir: { value: sunDir } },
    vertexShader: "varying vec3 d; void main(){ d = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }",
    fragmentShader: `varying vec3 d; uniform vec3 sunDir;
      void main(){
        float h = d.y;
        vec3 ground = vec3(0.16) * (0.25 + 0.75 * clamp(sunDir.y * 2.5 + 0.2, 0.0, 1.0)) * 3.0;   // sunlit regolith, brighter toward the sun side
        ground *= 0.6 + 0.4 * max(dot(normalize(vec3(d.x, 0.0, d.z)), normalize(vec3(sunDir.x, 0.0, sunDir.z))), 0.0);
        vec3 c = h < 0.0 ? ground : vec3(0.0);
        float s = smoothstep(0.9995, 0.9999, dot(d, sunDir));                                   // sun disc
        c += vec3(60.0) * s;
        gl_FragColor = vec4(c, 1.0);
      }`,
  }));
  envScene.add(sky);
  scene.environment = new THREE.PMREMGenerator(renderer).fromScene(envScene, 0.02).texture;
  scene.environmentIntensity = 1.0;

  // stars (seeded, so the sky is the same every run)
  let seed = 12345;
  const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
  const n = 4000, pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    const u = rnd() * 2 - 1, t = rnd() * Math.PI * 2, r = Math.sqrt(1 - u * u);
    pos.set([r * Math.cos(t) * 900, Math.abs(u) * 900 * 0.98 + 5, r * Math.sin(t) * 900], i * 3);
    const b = 0.25 + Math.pow(rnd(), 4) * 0.75;
    col.set([b, b, b * (0.9 + rnd() * 0.1)], i * 3);
  }
  const stars = new THREE.BufferGeometry();
  stars.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  stars.setAttribute("color", new THREE.BufferAttribute(col, 3));
  const starPts = new THREE.Points(stars, new THREE.PointsMaterial({ size: 1.6, sizeAttenuation: false, vertexColors: true, fog: false, toneMapped: false, depthTest: false, depthWrite: false }));
  starPts.renderOrder = -1000;                                   // drawn first and never depth-tested: the terrain reaches 74 km, beyond the star sphere
  starPts.frustumCulled = false;
  scene.add(starPts);

  // regolith ground: tiling multi-scale noise for albedo and bump (craters and relief come with the terrain in phase 3)
  const tex = regolithTexture(1024);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshStandardMaterial({
    map: tex.map, bumpMap: tex.bump, bumpScale: 0.6, roughness: 1, metalness: 0, color: new THREE.Color(0.34, 0.325, 0.31),
  }));
  // the 2.5 m tile repeats visibly from above: two more samples of the albedo at unrelated scales and angles (about 13 m and 47 m) vary it over distance, mean-preserving
  const gm = ground.material as THREE.MeshStandardMaterial;
  gm.onBeforeCompile = (shader) => {
    shader.uniforms.macroMap = { value: tex.macro };
    shader.fragmentShader = "uniform sampler2D macroMap;\n" + shader.fragmentShader;
    shader.fragmentShader = shader.fragmentShader.replace("#include <map_fragment>", `#include <map_fragment>
      { vec2 q = vMapUv * 400.0;
        float a = texture2D(macroMap, mat2(0.8, -0.6, 0.6, 0.8) * q / 31.0 + 0.31).r, b = texture2D(macroMap, mat2(0.5, 0.866, -0.866, 0.5) * q / 113.0 + 0.77).r;
        diffuseColor.rgb *= clamp(0.35 + 1.3 * (0.55 * a + 0.45 * b), 0.55, 1.45); }`);
  };
  gm.customProgramCacheKey = () => "regolithMacro";
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  for (const t of [tex.map, tex.bump]) { t.repeat.set(160, 160); }
  tex.macro.wrapS = tex.macro.wrapT = THREE.RepeatWrapping;
  scene.add(ground);
  return { sun, ground, sunDir, sunElevationDeg: opts.sunElevationDeg, sunAzimuthDeg: opts.sunAzimuthDeg, groundMaterial: ground.material as THREE.MeshStandardMaterial, followSun(target: THREE.Vector3) { sun.target.position.copy(target); sun.position.copy(sunDir).multiplyScalar(20).add(target); sun.target.updateMatrixWorld(); } };
}

/** integer matrices (a b; -b a) turn each octave's lattice by atan(b/a) and still tile: no common grid direction, which showed as a weave */
const ROT: [number, number][] = [[1, 0], [2, 1], [3, 2], [1, 1], [3, 1], [2, 3], [4, 1]];

function regolithTexture(fullSize: number) {
  const make = (contrast: number, seed: number, cells = [16, 32, 64, 128, 256], size = fullSize) => {
    const c = document.createElement("canvas"); c.width = c.height = size;
    const g = c.getContext("2d")!;
    const img = g.createImageData(size, size);
    // tileable value noise from a few octaves of random lattices
    const oct = cells.map((cells, k) => {
      const lat = new Float32Array(cells * cells);
      let s = seed + k * 91;
      for (let i = 0; i < lat.length; i++) lat[i] = ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
      return { cells, lat, w: Math.pow(0.62, k) };
    });
    const sample = (o: { cells: number; lat: Float32Array }, x: number, y: number) => {
      const fx = x * o.cells, fy = y * o.cells, x0 = Math.floor(fx), y0 = Math.floor(fy), tx = fx - x0, ty = fy - y0;
      const sx = tx * tx * (3 - 2 * tx), sy = ty * ty * (3 - 2 * ty);
      const a = o.lat[(y0 % o.cells) * o.cells + (x0 % o.cells)], b = o.lat[(y0 % o.cells) * o.cells + ((x0 + 1) % o.cells)];
      const d = o.lat[((y0 + 1) % o.cells) * o.cells + (x0 % o.cells)], e = o.lat[((y0 + 1) % o.cells) * o.cells + ((x0 + 1) % o.cells)];
      return (a * (1 - sx) + b * sx) * (1 - sy) + (d * (1 - sx) + e * sx) * sy;
    };
    const wsum = oct.reduce((a, o) => a + o.w, 0);
    for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
      let v = 0;
      for (let k = 0; k < oct.length; k++) { const o = oct[k], m = ROT[k % ROT.length], u = (x * m[0] + y * m[1]) / size, w = (-x * m[1] + y * m[0]) / size; v += sample(o, u - Math.floor(u), w - Math.floor(w)) * o.w; }
      v = Math.min(1, Math.max(0, 0.5 + (v / wsum - 0.5) * contrast));
      const i = (y * size + x) * 4;
      img.data[i] = img.data[i + 1] = img.data[i + 2] = Math.round(v * 255); img.data[i + 3] = 255;
    }
    g.putImageData(img, 0, 0);
    const t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.colorSpace = THREE.NoColorSpace;
    t.anisotropy = 8;
    return t;
  };
  const map = make(2.2, 777), bump = make(2.4, 4242), macro = make(2.0, 99, [2, 4, 8, 16], 512);
  map.colorSpace = THREE.SRGBColorSpace;
  return { map, bump, macro };
}
