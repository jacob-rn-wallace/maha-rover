import * as THREE from "three";
import type { PhysicsView } from "./physicsProxy";
import type { Power } from "./power";
import type { Terrain } from "./terrain";
import { WHEELS, MOTOR } from "./constants";
import { evaluate, paint, LEVEL_COLOR, type Level, type LimitId } from "./limits";

type Levels = Record<LimitId, Level>;
const deg = (x: number) => (x * 180 / Math.PI).toFixed(0);

/** phones: three lines, tap the panel for the full readout */
function shortText(phys: PhysicsView, c: any, euler: THREE.Euler, p: Power, lv: Levels, wall: number | undefined) {
  const v = c.linvel();
  return `${Math.hypot(v.x, v.z).toFixed(2)} m/s<br>${paint(`pitch ${deg(euler.z)}°, roll ${deg(euler.x)}°`, lv.tilt)}, ${paint(`battery ${(p.soc * 100).toFixed(0)}%`, lv.battery)}${wall !== undefined && lv.wall ? `<br>${wallWarning(wall, lv.wall)}` : ""}${phys.tiltCut ? '<br><span style="color:#ffb04a">tilt guard: drive cut</span>' : ""}<br><span style="opacity:.6">tap for more</span>`;
}

function powerText(p: Power, lv: Levels) {
  const t = p.minutesLeft;
  return `<br>${paint(`battery ${(p.soc * 100).toFixed(1)}% (${p.volts.toFixed(2)} V)`, lv.battery)}, load ${p.wattsLoad.toFixed(1)} W (${p.loadAmps.toFixed(1)} A), solar ${p.solarW.toFixed(1)} W${isFinite(t) ? `, ${t > 120 ? (t / 60).toFixed(1) + " h" : t.toFixed(0) + " min"} left at this draw` : ", charging"}`;
}

function wallWarning(edge: number, lv: Level) {
  return `<span style="color:${LEVEL_COLOR[lv] || LEVEL_COLOR[1]}">sandbox edge ${Math.max(0, edge).toFixed(0)} m ahead</span>`;
}
function edgeText(x: number, z: number, edge: number, lv: Level) {
  return `<br>position ${x.toFixed(0)} m E, ${(-z).toFixed(0)} m N of the tile centre${lv ? "<br>" + wallWarning(edge, lv) : ""}`;
}

/** with the soil model: the mean tip-referred slip of the wheels in contact and the sinkage the model predicts for it (the ground itself stays rigid) */
function soilLine(phys: PhysicsView) {
  const on = WHEELS.map((w) => phys.soilState[w]).filter((s) => s && s.load > 0.02);
  if (!on.length) return "";
  const slip = on.reduce((a, s) => a + s.slip, 0) / on.length, sink = on.reduce((a, s) => a + s.sinkage, 0) / on.length, load = on.reduce((a, s) => a + s.load, 0);
  return `, soil slip ${(slip * 100).toFixed(0)}%, sinkage about ${sink.toFixed(0)} mm, load ${load.toFixed(1)} N`;
}

function hudText(phys: PhysicsView, c: any, euler: THREE.Euler, lv: Levels, amps: string) {
  const r = c.rotation();
  const v = c.linvel(), fwd = new THREE.Vector3(1, 0, 0).applyQuaternion(new THREE.Quaternion(r.x, r.y, r.z, r.w));
  const speed = v.x * fwd.x + v.y * fwd.y + v.z * fwd.z;
  const wrate = (WHEELS.reduce((a, w) => a + (phys.wheelRate[w] ?? 0), 0) / 4) * 0.1;
  const slip = Math.abs(wrate) > 0.02 ? Math.max(-1, Math.min(1, 1 - speed / wrate)) : 0;
  return `lunar gravity ${phys.gravity} m/s2<br>speed ${speed.toFixed(2)} m/s, wheel slip ${(slip * 100).toFixed(0)}%${soilLine(phys)}<br>${paint(`pitch ${deg(euler.z)}°, roll ${deg(euler.x)}°`, lv.tilt)}<br>links L ${deg(phys.linkAngle.L)}° R ${deg(phys.linkAngle.R)}° (differential)<br>mast pan ${deg(phys.panAngle)}°, tilt ${deg(phys.tiltAngle)}°<br>${paint(`motor current ${amps} A (cap ${MOTOR.iCap})`, lv.current)}${phys.tiltCut ? ' <span style="color:#ffb04a">tilt guard: drive cut (T to stand upright)</span>' : ''}<br><span style="opacity:.7">W/S drive, A/D steer, Space brake, Q/E pan, R/F tilt, T upright, C camera view (P still, [ ] roll, V live), M map, H hazard overlay, L performance log; gamepad: left stick drive, right stick mast</span>`;
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
    const ct = chassis.translation(), r = chassis.rotation();
    this.euler.setFromQuaternion(new THREE.Quaternion(r.x, r.y, r.z, r.w), "YXZ");
    const cur = WHEELS.map((w) => Math.abs(phys.wheelCurrent[w] ?? 0)), edge = terrain ? terrain.half - 20 - Math.max(Math.abs(ct.x), Math.abs(ct.z)) : undefined;      // the walls stand 20 m inside the tile edge (physics.ts)
    const lv = evaluate({ battery: power.soc * 100, current: Math.max(...cur), tilt: Math.max(Math.abs(this.euler.z), Math.abs(this.euler.x)) * 180 / Math.PI, wall: edge });
    const amps = cur.map((a) => a.toFixed(1)).join(" ");
    this.el.innerHTML = (this.coarse && !this.full ? shortText(phys, chassis, this.euler, power, lv, edge) : hudText(phys, chassis, this.euler, lv, amps) + powerText(power, lv) + (terrain ? edgeText(ct.x, ct.z, edge!, lv.wall) : "")) + extra;
  }
}
