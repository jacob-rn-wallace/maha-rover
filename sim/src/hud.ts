import * as THREE from "three";
import type { PhysicsView } from "./physicsProxy";
import type { Power } from "./power";
import type { Terrain } from "./terrain";
import { WHEELS, MOTOR } from "./constants";

/** phones: three lines, tap the panel for the full readout */
function shortText(phys: PhysicsView, c: any, euler: THREE.Euler, p: Power) {
  const r = c.rotation(); euler.setFromQuaternion(new THREE.Quaternion(r.x, r.y, r.z, r.w), "YXZ");
  const v = c.linvel(), deg = (x: number) => (x * 180 / Math.PI).toFixed(0);
  return `${Math.hypot(v.x, v.z).toFixed(2)} m/s<br>pitch ${deg(euler.z)}°, roll ${deg(euler.x)}°, battery ${(p.soc * 100).toFixed(0)}%${phys.tiltCut ? '<br><span style="color:#ffb04a">tilt guard: drive cut</span>' : ""}<br><span style="opacity:.6">tap for more</span>`;
}

function powerText(p: Power) {
  const t = p.minutesLeft;
  return `<br>battery ${(p.soc * 100).toFixed(1)}% (${p.volts.toFixed(2)} V), load ${p.wattsLoad.toFixed(1)} W (${p.loadAmps.toFixed(1)} A), solar ${p.solarW.toFixed(1)} W${isFinite(t) ? `, ${t > 120 ? (t / 60).toFixed(1) + " h" : t.toFixed(0) + " min"} left at this draw` : ", charging"}`;
}

function edgeText(x: number, z: number, t: Terrain) {
  const edge = t.half - 20 - Math.max(Math.abs(x), Math.abs(z));      // the walls stand 20 m inside the tile edge (physics.ts)
  const warn = edge < 100 ? `<br><span style="color:#ffb04a">sandbox edge ${Math.max(0, edge).toFixed(0)} m ahead</span>` : "";
  return `<br>position ${x.toFixed(0)} m E, ${(-z).toFixed(0)} m N of the tile centre${warn}`;
}

/** with the soil model: the mean tip-referred slip of the wheels in contact and the sinkage the model predicts for it (the ground itself stays rigid) */
function soilLine(phys: PhysicsView) {
  const on = WHEELS.map((w) => phys.soilState[w]).filter((s) => s && s.load > 0.02);
  if (!on.length) return "";
  const slip = on.reduce((a, s) => a + s.slip, 0) / on.length, sink = on.reduce((a, s) => a + s.sinkage, 0) / on.length, load = on.reduce((a, s) => a + s.load, 0);
  return `, soil slip ${(slip * 100).toFixed(0)}%, sinkage about ${sink.toFixed(0)} mm, load ${load.toFixed(1)} N`;
}

function hudText(phys: PhysicsView, c: any, euler: THREE.Euler) {
  const r = c.rotation(); euler.setFromQuaternion(new THREE.Quaternion(r.x, r.y, r.z, r.w), "YXZ");
  const v = c.linvel(), fwd = new THREE.Vector3(1, 0, 0).applyQuaternion(new THREE.Quaternion(r.x, r.y, r.z, r.w));
  const speed = v.x * fwd.x + v.y * fwd.y + v.z * fwd.z;
  const deg = (x: number) => (x * 180 / Math.PI).toFixed(0);
  const amps = WHEELS.map((w) => Math.abs(phys.wheelCurrent[w] ?? 0).toFixed(1)).join(" ");
  const wrate = (WHEELS.reduce((a, w) => a + (phys.wheelRate[w] ?? 0), 0) / 4) * 0.1;
  const slip = Math.abs(wrate) > 0.02 ? Math.max(-1, Math.min(1, 1 - speed / wrate)) : 0;
  return `lunar gravity ${phys.gravity} m/s2<br>speed ${speed.toFixed(2)} m/s, wheel slip ${(slip * 100).toFixed(0)}%${soilLine(phys)}<br>pitch ${deg(euler.z)}°, roll ${deg(euler.x)}°<br>links L ${deg(phys.linkAngle.L)}° R ${deg(phys.linkAngle.R)}° (differential)<br>mast pan ${deg(phys.panAngle)}°, tilt ${deg(phys.tiltAngle)}°<br>motor current ${amps} A (cap ${MOTOR.iCap})${phys.tiltCut ? ' <span style="color:#ffb04a">tilt guard: drive cut (T to stand upright)</span>' : ''}<br><span style="opacity:.7">W/S drive, A/D steer, Space brake, Q/E pan, R/F tilt, T upright, C camera view, M map, L performance log; gamepad: left stick drive, right stick mast</span>`;
}

/** the text readout under the wordmark (the element is in index.html); on phones a short form that a tap expands */
export class Hud {
  private full = false;
  private euler = new THREE.Euler();

  constructor(readonly el: HTMLElement, private coarse: boolean) {
    if (coarse) { el.style.fontSize = "11px"; el.style.maxWidth = "230px"; el.addEventListener("click", () => { this.full = !this.full; }); }
  }

  /** `extra` is html appended after the readout (the recording line, the stats line) */
  update(phys: PhysicsView, chassis: any, power: Power, terrain: Terrain | undefined, extra = "") {
    const ct = chassis.translation();
    this.el.innerHTML = (this.coarse && !this.full ? shortText(phys, chassis, this.euler, power) : hudText(phys, chassis, this.euler) + powerText(power) + (terrain ? edgeText(ct.x, ct.z, terrain) : "")) + extra;
  }
}
