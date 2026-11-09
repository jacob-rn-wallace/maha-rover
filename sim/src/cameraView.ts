import * as THREE from "three";
import type { MastCameraFx } from "./cameraFx";

/** the mast camera's picture-in-picture: C cycles small, large, off (frame and label are a DOM box over the canvas) */
export class CameraView {
  mode = 1;
  private box = document.createElement("div");
  private label = document.createElement("span");
  // the mast camera: Raspberry Pi HQ (IMX477, 6.287 x 4.712 mm active area, Raspberry Pi documentation) behind a 4 mm lens: 76.6 x 61.4 degrees, 4:3, no distortion
  private cam = new THREE.PerspectiveCamera(61.4, 4 / 3, 0.02, 200000);
  private offset: THREE.Vector3;
  private basis = new THREE.Matrix4().makeBasis(new THREE.Vector3(0, 0, 1), new THREE.Vector3(0, 1, 0), new THREE.Vector3(-1, 0, 0));     // camera looks along the head's +x, up is its +y
  private headQ = new THREE.Quaternion();

  constructor(private fx: MastCameraFx, positionM: [number, number, number], private coarse: boolean) {
    this.offset = new THREE.Vector3(...positionM);
    this.box.style.cssText = "display:none;position:fixed;border:1px solid #888;box-sizing:border-box;pointer-events:none";
    this.label.style.cssText = "position:absolute;left:4px;top:2px;font-size:11px;opacity:.8";
    this.box.appendChild(this.label); document.body.appendChild(this.box);
    this.cam.fov = fx.renderFov(61.4); this.cam.updateProjectionMatrix();
  }

  cycle() { this.mode = (this.mode + 1) % 3; }

  /** draws the view into the corner of a vw x vh canvas; `mapOffset` is the height the minimap takes on phones, where the view sits under it */
  render(scene: THREE.Scene, head: THREE.Object3D, vw: number, vh: number, mapOffset: number) {
    if (this.mode === 0) { this.box.style.display = "none"; return; }
    const { cam, fx, coarse } = this;
    this.headQ.copy(head.quaternion);
    cam.position.copy(this.offset).applyQuaternion(this.headQ).add(head.position);
    cam.quaternion.copy(this.headQ).multiply(new THREE.Quaternion().setFromRotationMatrix(this.basis));
    const big = this.mode === 2, pw = Math.min(vw * (big ? 0.7 : 0.3), (vh * (big ? 0.7 : 0.3)) * 4 / 3), ph = pw * 3 / 4, px = vw - pw - 12, py = coarse ? vh - ph - mapOffset : 12;
    fx.render(scene, cam, px, py, pw, ph);
    this.label.textContent = `mast camera, HQ + 4 mm lens, 76.6 x 61.4 deg, exposure gain x${fx.gain.toFixed(2)}`;
    Object.assign(this.box.style, { display: "block", right: "12px", ...(coarse ? { top: mapOffset + "px", bottom: "" } : { bottom: "12px" }), width: pw + "px", height: ph + "px" });
  }
}
