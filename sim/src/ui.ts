import * as THREE from "three";
import { Layout } from "./layout";
import { TopBar, type BarActions } from "./topbar";
import { Alerts, type AlertItem } from "./alerts";
import { TelemetryPanel, type Section, type Row } from "./telemetry";
import { Cluster } from "./cluster";
import { Help } from "./help";
import type { HazardOverlay } from "./hazard";
import { WHEELS, MOTOR } from "./constants";
import { evaluate, LIMITS } from "./limits";
import { bearingDeg } from "./freshness";
import type { PhysicsView } from "./physicsProxy";
import type { Power } from "./power";
import type { Terrain } from "./terrain";

/** what the interface shows each time it is updated (10 Hz) */
export interface UiState {
  phys: PhysicsView; chassis: any; power: Power; terrain?: Terrain;
  recording: { on: boolean; seconds: number; benchOf?: number }; stats?: string;
}

const deg = (x: number) => (x * 180 / Math.PI).toFixed(0);

/** The interface as a whole (docs/sim-ui-layout.md): the layout, the top bar with its status chips, the alerts, the telemetry panel, the instrument cluster and the help.
 *  Each update reads the rover's state once, evaluates the limits table once, and gives every part what it shows. */
export class UI {
  readonly layout: Layout; readonly bar: TopBar; readonly alerts: Alerts; readonly tele: TelemetryPanel; readonly cluster: Cluster; readonly help: Help;
  private euler = new THREE.Euler(); private q = new THREE.Quaternion(); private f = new THREE.Vector3();
  private lastBattery = ""; private lastStats = "";

  constructor(coarse: boolean, private hazard: HazardOverlay, on: BarActions) {
    this.layout = new Layout(coarse);
    this.bar = new TopBar(this.layout, hazard.legend, on);
    this.alerts = new Alerts(this.layout);
    this.tele = new TelemetryPanel(this.layout);
    this.cluster = new Cluster(this.layout);
    this.help = new Help(this.layout);
    hazard.onChange = (isOn) => { setTimeout(() => this.layout.togglePop("legend", isOn), 100); if (isOn) setTimeout(() => this.layout.togglePop("legend", false), 8000); };      // the legend shows for a few seconds when the overlay goes on (opened a moment later: opened in the same turn as the toggle it did not paint in headless Chrome)
    const once = () => { this.alerts.dismissHint(); removeEventListener("keydown", once); removeEventListener("pointerdown", once); };
    addEventListener("keydown", once); addEventListener("pointerdown", once);
  }

  update(s: UiState) {
    const { phys, chassis: c, power: p, terrain } = s;
    const t = c.translation(), r = c.rotation(), v = c.linvel();
    this.q.set(r.x, r.y, r.z, r.w); this.euler.setFromQuaternion(this.q, "YXZ");
    const fwd = this.f.set(1, 0, 0).applyQuaternion(this.q), speed = v.x * fwd.x + v.y * fwd.y + v.z * fwd.z, heading = bearingDeg(fwd.x, -fwd.z);
    const pitch = (this.euler.z * 180) / Math.PI, roll = (this.euler.x * 180) / Math.PI;
    const cur = WHEELS.map((w) => Math.abs(phys.wheelCurrent[w] ?? 0)), edge = terrain ? terrain.half - 20 - Math.max(Math.abs(t.x), Math.abs(t.z)) : undefined;      // the walls stand 20 m inside the tile edge (physics.ts)
    const tilt = Math.max(Math.abs(pitch), Math.abs(roll)), lv = evaluate({ battery: p.soc * 100, current: Math.max(...cur), tilt, wall: edge });

    // status chips
    this.bar.set("battery", `batt ${(p.soc * 100).toFixed(0)}%`, lv.battery);
    this.bar.set("tilt", `tilt ${tilt.toFixed(0)}°`, lv.tilt);
    this.bar.set("wall", edge === undefined ? null : `edge ${Math.max(0, edge).toFixed(0)} m`, lv.wall);
    this.bar.set("hazard", "", this.hazard.on ? "on" : "off");
    this.bar.set("rec", s.recording.on ? `● rec ${s.recording.seconds.toFixed(0)} s${s.recording.benchOf ? ` of ${s.recording.benchOf}` : ""}` : null, 2);
    this.bar.setRecording(s.recording.on);

    // alerts: only yellow or red
    const alerts: AlertItem[] = [];
    if (phys.tiltCut) alerts.push({ text: "tilt guard: drive cut. T stands the rover upright", level: 2 });
    else if (lv.tilt) alerts.push({ text: `tilt ${tilt.toFixed(0)}°: ${lv.tilt === 2 ? "over" : "near"} the tilt-guard limit`, level: lv.tilt });
    if (edge !== undefined && lv.wall) alerts.push({ text: `sandbox edge ${Math.max(0, edge).toFixed(0)} m ahead`, level: lv.wall });
    if (lv.battery) alerts.push({ text: `battery ${(p.soc * 100).toFixed(0)}%`, level: lv.battery });
    if (lv.current === 2) alerts.push({ text: `motor current at the ${MOTOR.iCap} A cap`, level: 2 });
    if (s.recording.on && s.recording.benchOf) alerts.push({ text: "benchmark running: keep the window in front", level: 1 });
    this.alerts.set(alerts);

    // cluster and the telemetry panel
    this.cluster.update(speed, heading, pitch, roll, lv.tilt);
    const wrate = (WHEELS.reduce((a, w) => a + (phys.wheelRate[w] ?? 0), 0) / 4) * 0.1, slip = Math.abs(wrate) > 0.02 ? Math.max(-1, Math.min(1, 1 - speed / wrate)) : 0;
    const drive: Row[] = [{ label: "speed", value: `${speed.toFixed(2)} m/s` }, { label: "wheel slip", value: `${(slip * 100).toFixed(0)}%` }];
    const on = WHEELS.map((w) => phys.soilState[w]).filter((x) => x && x.load > 0.02);
    if (on.length) {      // with the soil model: the mean tip-referred slip of the wheels in contact and the sinkage the model predicts for it (the ground itself stays rigid)
      drive.push({ label: "soil slip", value: `${((on.reduce((a, x) => a + x.slip, 0) / on.length) * 100).toFixed(0)}%` }, { label: "sinkage", value: `about ${(on.reduce((a, x) => a + x.sinkage, 0) / on.length).toFixed(0)} mm` }, { label: "wheel load", value: `${on.reduce((a, x) => a + x.load, 0).toFixed(1)} N` });
    }
    drive.push({ label: `motor A (cap ${MOTOR.iCap})`, value: cur.map((a) => a.toFixed(1)).join(" "), level: lv.current });
    const t2 = p.minutesLeft;
    const sections: Section[] = [
      { title: "drive", rows: drive },
      { title: "attitude", rows: [{ label: "pitch", value: `${deg(this.euler.z)}°`, level: lv.tilt }, { label: "roll", value: `${deg(this.euler.x)}°`, level: lv.tilt }, { label: "links L, R (differential)", value: `${deg(phys.linkAngle.L)}°, ${deg(phys.linkAngle.R)}°` }, { label: "heading", value: `${heading.toFixed(0)}°` }] },
      { title: "mast", rows: [{ label: "pan", value: `${deg(phys.panAngle)}°` }, { label: "tilt", value: `${deg(phys.tiltAngle)}°` }] },
      { title: "power", rows: [{ label: "battery", value: `${(p.soc * 100).toFixed(1)}% (${p.volts.toFixed(2)} V)`, level: lv.battery }, { label: "load", value: `${p.wattsLoad.toFixed(1)} W (${p.loadAmps.toFixed(1)} A)` }, { label: "solar", value: `${p.solarW.toFixed(1)} W` }, { label: "left at this draw", value: isFinite(t2) ? (t2 > 120 ? (t2 / 60).toFixed(1) + " h" : t2.toFixed(0) + " min") : "charging" }] },
      { title: "world", rows: [{ label: "gravity", value: `${phys.gravity} m/s2` }, ...(terrain ? [{ label: "position", value: `${t.x.toFixed(0)} m E, ${(-t.z).toFixed(0)} m N of the tile centre` }] : [])] },
    ];
    this.tele.update(sections);

    // battery chip detail, settings stats
    const bat = `<h4>power</h4>voltage ${p.volts.toFixed(2)} V<br>load ${p.wattsLoad.toFixed(1)} W (${p.loadAmps.toFixed(1)} A)<br>solar ${p.solarW.toFixed(1)} W<br>${isFinite(t2) ? (t2 > 120 ? (t2 / 60).toFixed(1) + " h" : t2.toFixed(0) + " min") + " left at this draw" : "charging"}<br><span class="dim">limits: yellow under ${LIMITS.battery.yellow}%, red under ${LIMITS.battery.red}%</span>`;
    if (bat !== this.lastBattery) { this.lastBattery = bat; this.bar.batteryDetail.innerHTML = bat; }
    if (s.stats !== undefined && s.stats !== this.lastStats) { this.lastStats = s.stats; this.bar.stats.textContent = s.stats; }
  }
}
