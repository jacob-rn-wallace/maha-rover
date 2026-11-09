import * as THREE from "three";
import type { MastCameraFx } from "./cameraFx";
import { Compass } from "./compass";
import { CameraRoll } from "./cameraRoll";
import { bearingDeg, cardinal, type CamPose } from "./freshness";

/** the rover's state each frame, for the compass, the readout and the freshness flags */
export interface RoverPose { x: number; z: number; quat: THREE.Quaternion; pan: number; tilt: number }

const HFOV_DEG = 76.6;      // horizontal field of view of the HQ camera behind its 4 mm lens (the vertical is 61.4)

/** the mast camera's picture-in-picture: C cycles small, large, off (frame and label are a DOM box over the canvas). It carries a compass rose and a readout of the camera's bearing, the head angles,
 *  the body's attitude and the sun, and a camera roll of stills with freshness flags (docs/sim-ui-research.md, Open MCT's imagery view). A past still pauses the live view and has an orange border. */
export class CameraView {
  mode = 1;
  readonly roll = new CameraRoll();
  private box = document.createElement("div");
  private label = document.createElement("span");
  private readout = document.createElement("div");
  private still = document.createElement("canvas");
  private stillKey = "";
  private compass = new Compass(HFOV_DEG);
  private snapPending = false;
  // the mast camera: Raspberry Pi HQ (IMX477, 6.287 x 4.712 mm active area, Raspberry Pi documentation) behind a 4 mm lens: 76.6 x 61.4 degrees, 4:3, no distortion
  private cam = new THREE.PerspectiveCamera(61.4, 4 / 3, 0.02, 200000);
  private offset: THREE.Vector3;
  private basis = new THREE.Matrix4().makeBasis(new THREE.Vector3(0, 0, 1), new THREE.Vector3(0, 1, 0), new THREE.Vector3(-1, 0, 0));     // camera looks along the head's +x, up is its +y
  private headQ = new THREE.Quaternion();
  private euler = new THREE.Euler();
  private v = new THREE.Vector3();

  /** `sun`: compass bearing (clockwise from north) and elevation of the fixed sun, degrees */
  constructor(private fx: MastCameraFx, positionM: [number, number, number], private coarse: boolean, private sun: { bearingDeg: number; elevationDeg: number }) {
    this.offset = new THREE.Vector3(...positionM);
    this.box.style.cssText = "display:none;position:fixed;border:1px solid #888;box-sizing:border-box;pointer-events:none;overflow:hidden";
    this.label.style.cssText = "position:absolute;left:4px;top:2px;font-size:11px;opacity:.8;z-index:1";
    this.still.style.cssText = "position:absolute;left:0;top:0;width:100%;height:100%;display:none";
    this.readout.style.cssText = "position:absolute;left:78px;bottom:4px;font:10px/1.4 system-ui;color:#eee;text-shadow:0 0 3px #000;z-index:1";
    this.compass.el.style.cssText += ";position:absolute;left:4px;bottom:4px;z-index:1";
    this.box.append(this.still, this.label, this.roll.flags, this.compass.el, this.readout); document.body.appendChild(this.box);
    this.cam.fov = fx.renderFov(61.4); this.cam.updateProjectionMatrix();
    this.roll.onSnap = () => this.snap();
  }

  cycle() { this.mode = (this.mode + 1) % 3; }
  /** takes a still of the live view at the next draw (nothing while a past still is shown or the view is off) */
  snap() { if (this.mode > 0 && !this.roll.past) this.snapPending = true; }

  /** draws the view into the corner of a vw x vh canvas; `mapOffset` is the height the minimap takes on phones, where the view sits under it */
  render(scene: THREE.Scene, head: THREE.Object3D, vw: number, vh: number, mapOffset: number, rover: RoverPose) {
    if (this.mode === 0) { this.box.style.display = "none"; this.roll.show(false); return; }
    const { cam, fx, coarse, roll } = this;
    this.headQ.copy(head.quaternion);
    cam.position.copy(this.offset).applyQuaternion(this.headQ).add(head.position);
    cam.quaternion.copy(this.headQ).multiply(new THREE.Quaternion().setFromRotationMatrix(this.basis));
    const big = this.mode === 2, pw = Math.min(vw * (big ? 0.7 : 0.3), (vh * (big ? 0.7 : 0.3)) * 4 / 3), ph = pw * 3 / 4, px = vw - pw - 12, py = coarse ? vh - ph - mapOffset : 12;

    const f = this.v.set(1, 0, 0).applyQuaternion(rover.quat), heading = bearingDeg(f.x, -f.z);
    this.euler.setFromQuaternion(rover.quat, "YXZ");
    const pitch = THREE.MathUtils.radToDeg(this.euler.z), rollDeg = THREE.MathUtils.radToDeg(this.euler.x), deg = THREE.MathUtils.radToDeg;
    const look = this.v.set(0, 0, -1).applyQuaternion(cam.quaternion), camBearing = bearingDeg(look.x, -look.z);
    const now: CamPose = { t: performance.now(), x: rover.x, z: rover.z, headingDeg: heading, panDeg: deg(rover.pan), tiltDeg: deg(rover.tilt) };

    const shot = roll.current;
    if (shot) {      // a past still: the live view is paused
      const key = `${roll.selected}|${Math.round(pw)}x${Math.round(ph)}|${roll.shots.length}`;
      if (key !== this.stillKey) { this.stillKey = key; this.still.width = Math.round(pw); this.still.height = Math.round(ph); this.still.getContext("2d")!.drawImage(shot.image, 0, 0, this.still.width, this.still.height); }
      this.still.style.display = "block";
    } else {
      this.still.style.display = "none";
      fx.render(scene, cam, px, py, pw, ph);
      if (this.snapPending) { this.snapPending = false; roll.add({ image: fx.snapshot(), pose: now, cameraBearing: camBearing, pitchDeg: pitch, rollDeg }); }
    }

    const b = shot ? shot.cameraBearing : camBearing, pan = shot ? shot.pose.panDeg : now.panDeg, tilt = shot ? shot.pose.tiltDeg : now.tiltDeg, p = shot ? shot.pitchDeg : pitch, r = shot ? shot.rollDeg : rollDeg;
    this.compass.draw(b, this.sun.bearingDeg, this.sun.elevationDeg);
    this.readout.innerHTML = `camera ${b.toFixed(0)}° ${cardinal(b)}, pan ${pan.toFixed(0)}°, tilt ${tilt.toFixed(0)}°<br>body pitch ${p.toFixed(0)}°, roll ${r.toFixed(0)}°<br>sun ${this.sun.bearingDeg.toFixed(0)}° ${cardinal(this.sun.bearingDeg)}, ${this.sun.elevationDeg.toFixed(0)}° up`;
    roll.updateFlags(now);
    this.label.textContent = `mast camera, HQ + 4 mm lens, ${HFOV_DEG} x 61.4 deg${shot ? "" : `, exposure gain x${fx.gain.toFixed(2)}`}`;
    Object.assign(this.box.style, { display: "block", borderColor: shot ? "#ffb04a" : "#888", borderWidth: shot ? "2px" : "1px", right: "12px", ...(coarse ? { top: mapOffset + "px", bottom: "" } : { bottom: "12px" }), width: pw + "px", height: ph + "px" });
    roll.show(true);
    Object.assign(roll.strip.style, { right: "12px", ...(coarse ? { top: mapOffset + ph + 6 + "px", bottom: "" } : { bottom: ph + 18 + "px" }) });
  }
}
