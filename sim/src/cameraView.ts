import * as THREE from "three";
import type { MastCameraFx } from "./cameraFx";
import { Compass } from "./compass";
import { CameraRoll } from "./cameraRoll";
import { bearingDeg, cardinal, type CamPose } from "./freshness";
import { h } from "./layout";

/** the rover's state each frame, for the compass, the readout and the freshness flags */
export interface RoverPose { x: number; z: number; quat: THREE.Quaternion; pan: number; tilt: number }

const HFOV_DEG = 76.6;      // horizontal field of view of the HQ camera behind its 4 mm lens (the vertical is 61.4)

/** the mast camera's tile in the right column: C cycles small, large, off. The tile holds a header, the freshness flags, the picture, a footer with the compass rose and a readout (the camera's bearing, the head angles,
 *  the body's attitude, the sun) and the camera roll of stills (docs/sim-ui-research.md, Open MCT's imagery view). The picture is drawn into the canvas under the tile's picture box, so the tile's place in the layout
 *  is the only place the view is. A past still pauses the live view and gives the tile an orange border. */
export class CameraView {
  shown = true;           // false in the modes that have no camera tile
  primary = false;        // the main view (Camera mode): a big tile in the middle
  collapsed = false;      // the tile shrunk to its header (the button in it)
  reserveX = 0;           // as the main view, the width kept free on each side (for the chase inset)
  readonly roll = new CameraRoll();
  private tile = h("div", "panel tile cam-tile");
  private label = h("span");
  private readout = h("div");
  private pic = h("div", "tile-pic");
  private still = h("canvas", "still");
  private stillKey = "";
  private compass = new Compass(HFOV_DEG);
  private snapPending = false; private fold!: HTMLElement;
  // the mast camera: Raspberry Pi HQ (IMX477, 6.287 x 4.712 mm active area, Raspberry Pi documentation) behind a 4 mm lens: 76.6 x 61.4 degrees, 4:3, no distortion
  private cam = new THREE.PerspectiveCamera(61.4, 4 / 3, 0.02, 200000);
  private offset: THREE.Vector3;
  private basis = new THREE.Matrix4().makeBasis(new THREE.Vector3(0, 0, 1), new THREE.Vector3(0, 1, 0), new THREE.Vector3(-1, 0, 0));     // camera looks along the head's +x, up is its +y
  private headQ = new THREE.Quaternion();
  private euler = new THREE.Euler();
  private v = new THREE.Vector3();

  /** `sun`: compass bearing (clockwise from north) and elevation of the fixed sun, degrees; `parent`: the layout's right column */
  constructor(private fx: MastCameraFx, positionM: [number, number, number], private coarse: boolean, private sun: { bearingDeg: number; elevationDeg: number }, parent: HTMLElement) {
    this.offset = new THREE.Vector3(...positionM);
    const head = h("div", "panel-head"); this.label.style.cssText = "overflow:hidden;text-overflow:ellipsis;white-space:nowrap";
    const fold = h("button", "tbtn", "–"); fold.title = "fold the tile away"; fold.addEventListener("click", () => { this.collapsed = !this.collapsed; fold.textContent = this.collapsed ? "+" : "–"; });
    head.append(this.label, fold); this.fold = fold;
    this.pic.append(this.still);
    this.readout.style.cssText = "color:#eee";
    const foot = h("div", "tile-foot"); foot.append(this.compass.el, this.readout);
    this.tile.append(head, this.roll.flags, this.pic, foot, this.roll.strip); parent.appendChild(this.tile);
    this.cam.fov = fx.renderFov(61.4); this.cam.updateProjectionMatrix();
    this.roll.onSnap = () => this.snap();
  }

  /** takes a still of the live view at the next draw (nothing while a past still is shown or the view is off) */
  snap() { if (this.shown && !this.collapsed && !this.roll.past) this.snapPending = true; }

  /** the tile's width: a fifth of the window (110 to 140 px on phones, 220 to 320 otherwise), or as the main view the largest 4:3 picture that fits under the bar with the chase inset's room kept free on both sides */
  private size(vw: number, vh: number) {
    let w: number;
    if (this.primary) { const free = vh - this.tile.getBoundingClientRect().top - 12 - (this.tile.offsetHeight - this.pic.offsetHeight); w = Math.max(this.coarse ? 160 : 240, Math.min(vw - 2 * this.reserveX, (free * 4) / 3)); }
    else w = this.coarse ? Math.max(110, Math.min(140, vw * 0.16)) : Math.max(220, Math.min(320, vw * 0.2));
    this.tile.style.width = Math.round(w) + "px";
  }

  /** draws the view into the canvas under the tile's picture box (vw x vh: the canvas in CSS pixels) */
  render(scene: THREE.Scene, head: THREE.Object3D, vw: number, vh: number, rover: RoverPose) {
    if (!this.shown) { this.tile.style.display = "none"; return; }
    this.tile.style.display = "";
    this.tile.classList.toggle("primary", this.primary); this.tile.classList.toggle("collapsed", this.collapsed && !this.primary);
    this.fold.style.display = this.primary ? "none" : "";
    if (this.collapsed && !this.primary) { this.tile.style.width = ""; return; }
    const { cam, fx, roll } = this;
    this.headQ.copy(head.quaternion);
    cam.position.copy(this.offset).applyQuaternion(this.headQ).add(head.position);
    cam.quaternion.copy(this.headQ).multiply(new THREE.Quaternion().setFromRotationMatrix(this.basis));
    this.size(vw, vh);
    const rect = this.pic.getBoundingClientRect(), px = rect.left, py = vh - rect.bottom, pw = rect.width, ph = rect.height;

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
    const text = `<b>mast camera</b> <span class="dim">HQ 4 mm, ${HFOV_DEG} x 61.4°${shot ? "" : `, gain x${fx.gain.toFixed(2)}`}</span>`;
    if (this.label.innerHTML !== text) this.label.innerHTML = text;
    this.tile.classList.toggle("past", !!shot);
    roll.show(true);
  }
}
