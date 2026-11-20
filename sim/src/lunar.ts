import * as THREE from "three";
import { applyRegolithPhotometry } from "./regolith";

/** Lunar lighting and surface: a low sun, a black sky (the stars are in sky.ts), regolith-coloured ground bounce, a procedural regolith ground.
 *  Values are look-development choices, not measurements: sun elevation is a parameter; albedo 0.12 is the usual mean for the Moon (not sourced here).
 */
export interface LunarOpts { sunElevationDeg: number; sunAzimuthDeg: number; }

export function addLunarScene(scene: THREE.Scene, renderer: THREE.WebGLRenderer, opts: LunarOpts = { sunElevationDeg: 14, sunAzimuthDeg: -18 }) {
  scene.background = new THREE.Color(0x000000);
  const el = THREE.MathUtils.degToRad(opts.sunElevationDeg), az = THREE.MathUtils.degToRad(opts.sunAzimuthDeg);
  const sunDir = new THREE.Vector3(Math.cos(el) * Math.cos(az), Math.sin(el), -Math.cos(el) * Math.sin(az)).normalize();

  // sun: hard, white, no atmosphere
  const sun = new THREE.DirectionalLight(0xfff6ea, 3.0);
  sun.position.copy(sunDir).multiplyScalar(20);
  sun.castShadow = true;
  const q = new URLSearchParams(location.search), coarse = matchMedia("(pointer: coarse)").matches || q.get("touch") === "1";
  const smap = q.has("shadow") ? Number(q.get("shadow")) : 2048;      // 4 m across: 2048 is 2 mm per texel and 16 MB of depth (4096 was 1 mm and 64 MB); ?shadow=N overrides
  sun.shadow.mapSize.set(smap, smap);
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

  // the stars, Milky Way and Earth are in sky.ts

  // regolith ground: no texture image; the albedo mottling and the fine relief are world-space noise in the shader (regolith.ts)
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshStandardMaterial({ roughness: 1, metalness: 0, color: new THREE.Color(0.20, 0.19, 0.18) }));
  applyRegolithPhotometry(ground.material as THREE.MeshStandardMaterial, { ground: true });
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);
  return { sun, ground, sunDir, sunElevationDeg: opts.sunElevationDeg, sunAzimuthDeg: opts.sunAzimuthDeg, groundMaterial: ground.material as THREE.MeshStandardMaterial, followSun(target: THREE.Vector3) { sun.target.position.copy(target); sun.position.copy(sunDir).multiplyScalar(20).add(target); sun.target.updateMatrixWorld(); } };
}
