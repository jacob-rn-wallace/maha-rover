import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

const canvas = document.getElementById("c") as HTMLCanvasElement;
const hud = document.getElementById("hud")!;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x000000);
const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 2000);
camera.position.set(0.9, 0.6, 0.9);
const controls = new OrbitControls(camera, canvas);
controls.target.set(0.1, 0.3, 0);

// Placeholder lighting and ground (phase 3 replaces them with the lunar sun, earthshine and terrain)
const sun = new THREE.DirectionalLight(0xffffff, 6);
sun.position.set(2, 1.2, 1);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -1, right: 1, top: 1, bottom: -1, near: 0.1, far: 10 });
scene.add(sun, new THREE.HemisphereLight(0x8890a0, 0x202020, 0.4));
const ground = new THREE.Mesh(new THREE.PlaneGeometry(20, 20), new THREE.MeshStandardMaterial({ color: 0x777777, roughness: 1 }));
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);

interface Spec { total_mass_kg: number; bodies: Record<string, { mass_kg: number }>; }

async function main() {
  const [gltf, spec] = await Promise.all([
    new GLTFLoader().loadAsync("rover.glb"),
    fetch("rover.json").then((r) => r.json() as Promise<Spec>),
  ]);
  gltf.scene.traverse((o) => { if ((o as THREE.Mesh).isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  scene.add(gltf.scene);
  const node = (n: string) => gltf.scene.getObjectByName(n)!;
  hud.innerHTML = `<b>المَهَا al-maha</b><br>model loaded: ${Object.keys(spec.bodies).length} bodies, ${spec.total_mass_kg.toFixed(2)} kg`;
  // joint test, to check the export's axes: the pan, the tilt, the link plates (differential) and the wheels move
  (window as any).rover = { node, spec };
  const t0 = performance.now();
  renderer.setAnimationLoop(() => {
    const t = (performance.now() - t0) / 1000;
    node("pan").rotation.y = Math.sin(t * 0.6) * 1.2;
    node("head").rotation.z = Math.sin(t * 0.9) * 0.6;
    node("linkL").rotation.z = Math.sin(t * 0.5) * 0.15;
    node("linkR").rotation.z = -Math.sin(t * 0.5) * 0.15;
    for (const w of ["FL", "FR", "RL", "RR"]) node("wheel" + w).rotation.z = -t * 2;
    resize();
    controls.update();
    renderer.render(scene, camera);
  });
}
function resize() {
  const w = canvas.clientWidth, h = canvas.clientHeight;
  if (canvas.width !== Math.floor(w * renderer.getPixelRatio()) || canvas.height !== Math.floor(h * renderer.getPixelRatio())) {
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
}
main().catch((e) => { hud.textContent = "load failed: " + e; console.error(e); });
