import { h, type Layout } from "./layout";
import type { Minimap } from "./minimap";
import { Route, metrics, bestSolarHeading, solarWatts, footprint, forward, bearingTo, turn, PACK_WH, SPEED, TURN_RATE, DRIVE_W, type Pose } from "./plan";
import { bearingDeg, formatAge, cardinal } from "./freshness";

const BLUE = "#4aa3ff";
const hdg = (d: number) => String(Math.round(d) % 360).padStart(3, "0") + "°";
const turnText = (t: number) => (Math.abs(t) < 1 ? "no turn" : `${t > 0 ? "R" : "L"} ${Math.abs(t).toFixed(0)}°`);

/** The Plan panel (the left dock in Plan mode) and the map's part in planning: a click on the map places a waypoint, a drag sets its heading (without a drag, the heading is the direction of travel),
 *  a click on a waypoint selects it. The panel lists the waypoints with the turns, the totals (distance, time, energy: estimates, see plan.ts) and the solar heading. `drawOverlay` paints the route on the map.
 *  The rover is driven along the route with the usual controls; the route chip in the top bar and the markers in the world guide it. */
export class PlanPanel {
  readonly box = h("div", "panel plan");
  private pan: { x: number; y: number; pid: number } | null = null;
  private last = ""; private drag: { x: number; z: number; sx: number; sy: number; headingDeg: number; moved: boolean; pid: number } | null = null; private pose: Pose = { x: 0, z: 0, headingDeg: 0 };

  constructor(layout: Layout, readonly route: Route, private map: Minimap, private sun: { bearingDeg: number; elevationDeg: number }, private active: () => boolean) {
    layout.left.append(this.box); this.box.style.display = "none";
    map.overlay = (g) => this.drawOverlay(g); map.onCentre = () => this.centre();
    const c = map.canvas;
    c.addEventListener("pointerdown", (e) => { if (!this.active()) return; const w = map.toWorld(e.clientX, e.clientY); if (!w) return; c.setPointerCapture(e.pointerId); if (e.button === 2 || e.shiftKey) { this.pan = { x: e.clientX, y: e.clientY, pid: e.pointerId }; return; } this.drag = { x: w.x, z: w.z, sx: e.clientX, sy: e.clientY, headingDeg: NaN, moved: false, pid: e.pointerId }; });
    c.addEventListener("pointermove", (e) => { const p = this.pan; if (p && e.pointerId === p.pid) { const m = (2 * map.vhalf) / c.getBoundingClientRect().width; map.pan(-(e.clientX - p.x) * m, -(e.clientY - p.y) * m); p.x = e.clientX; p.y = e.clientY; return; } const d = this.drag; if (!d || e.pointerId !== d.pid) return; const dx = e.clientX - d.sx, dy = e.clientY - d.sy; if (Math.hypot(dx, dy) > 8) { d.moved = true; d.headingDeg = bearingDeg(dx, -dy); } });
    c.addEventListener("pointerup", (e) => { if (this.pan && e.pointerId === this.pan.pid) { this.pan = null; return; } const d = this.drag; if (!d || e.pointerId !== d.pid) return; this.drag = null; this.release(d); });
    c.addEventListener("pointercancel", () => { this.drag = null; this.pan = null; });
    this.box.addEventListener("click", (e) => {
      const t = e.target as HTMLElement, row = t.closest<HTMLElement>("[data-i]"), i = row ? Number(row.dataset.i) : -1;
      if (t.closest("[data-act=del]")) route.remove(i); else if (t.closest("[data-act=sun]")) this.solar(i); else if (t.closest("[data-act=undo]")) route.undo(); else if (t.closest("[data-act=clear]")) route.clear(); else if (i >= 0) route.select(i);
      this.update(this.pose, true);
    });
  }

  /** the pointer was released on the map: a drag on a waypoint's marker selects it; otherwise a new waypoint is placed */
  private release(d: NonNullable<PlanPanel["drag"]>) {
    const scale = this.map.canvas.getBoundingClientRect().width / (2 * this.map.vhalf), hit = d.moved ? -1 : this.route.near(d.x, d.z, 10 / scale);      // within 10 screen pixels
    if (hit >= 0) { this.route.select(hit); return; }
    const from = this.route.wps.length ? this.route.wps[this.route.wps.length - 1] : this.pose;
    this.route.add({ x: d.x, z: d.z, headingDeg: d.moved ? d.headingDeg : bearingTo(from.x, from.z, d.x, d.z) });
  }

  /** the selected waypoint's heading becomes the one with the most solar power, of the two equivalent ones the one nearer its travel direction */
  private solar(i: number) {
    const w = this.route.wps[i]; if (!w) return;
    const prev = i ? this.route.wps[i - 1] : this.pose, travel = bearingTo(prev.x, prev.z, w.x, w.z);
    this.route.setHeading(i, bestSolarHeading(this.sun.bearingDeg, this.sun.elevationDeg, travel).headingDeg);
  }

  /** the map window: 800 m across, centred on the rover (on entering Plan mode and with the centre button) */
  centre() { this.map.setView(this.pose.x, this.pose.z, 400); }

  private centred = false;
  update(pose: Pose, force = false) {
    this.pose = pose; if (!this.centred) { this.centred = true; if (this.active()) this.centre(); }
    const r = this.route, m = metrics(pose, r.wps);
    const rows = r.wps.map((w, i) => {
      const l = m.legs[i];
      return `<div class="wp${i === r.selected ? " sel" : ""}${i < r.next ? " done" : ""}" data-i="${i}"><b>${i + 1}</b><span class="n">${l.distance.toFixed(0)} m</span><span class="n">${hdg(w.headingDeg)}</span><span class="dim n" title="the turn at the waypoint, from the direction of travel to its heading">${turnText(l.turnToHeading)}</span><span class="grow"></span><button data-act="sun" title="face the panels to the sun">☀</button><button data-act="del" title="remove">✕</button></div>`;
    }).join("");
    const last = r.wps[r.wps.length - 1], best = last ? bestSolarHeading(this.sun.bearingDeg, this.sun.elevationDeg, last.headingDeg).watts : 0;
    const summary = r.wps.length
      ? `<h4>route</h4><div class="row"><span>path</span><span>${m.distanceM.toFixed(0)} m, ${m.turnDeg.toFixed(0)}° of turns</span></div><div class="row"><span>time</span><span>${formatAge(m.seconds)}</span></div><div class="row"><span>energy</span><span>${m.wh.toFixed(2)} Wh (${m.batteryPct.toFixed(1)}% of the pack)</span></div><div class="row"><span>solar at the end</span><span>${solarWatts(last.headingDeg, this.sun.bearingDeg, this.sun.elevationDeg).toFixed(1)} of ${best.toFixed(1)} W</span></div><div class="dim note">estimates: ${SPEED} m/s, ${TURN_RATE}°/s turns, ${DRIVE_W} W while moving; slope, soil and rocks not counted. Sun ${hdg(this.sun.bearingDeg)} ${cardinal(this.sun.bearingDeg)}, ${this.sun.elevationDeg.toFixed(0)}° up.</div><div class="btns"><button data-act="undo">undo (Backspace)</button><button data-act="clear">clear</button></div>`
      : "";
    const html = `<h4>plan</h4><div class="dim hint">${this.map.shown ? "Click the map to place a waypoint; drag to set its heading. Wheel zooms, shift-drag or right-drag pans. ☀ turns the selected waypoint to face the panels to the sun." : ""}</div>${rows}${summary}`;
    if (force || html !== this.last) { this.last = html; this.box.innerHTML = html; }
  }

  /** the route on the map: the path from the rover through the waypoints, each waypoint's number and heading, the turn it makes, and the selected waypoint's camera footprint */
  drawOverlay(g: CanvasRenderingContext2D) {
    const r = this.route, P = (x: number, z: number) => this.map.toCanvas(x, z);
    const d = this.drag, wps = d && !d.moved ? r.wps : r.wps;
    if (!wps.length && !(d && d.moved)) return;
    g.save();
    const pts = [this.pose, ...wps].map((p) => P(p.x, p.z));
    g.strokeStyle = BLUE; g.lineWidth = 2; g.setLineDash([7, 4]); g.beginPath(); pts.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.stroke(); g.setLineDash([]);
    const sel = r.wps[r.selected];
    if (sel) {      // the camera footprint at the selected waypoint (flat ground, camera level, out to 15 m)
      g.fillStyle = "rgba(74,163,255,.18)"; g.strokeStyle = "rgba(74,163,255,.7)"; g.lineWidth = 1; g.beginPath();
      footprint(sel.x, sel.z, sel.headingDeg).forEach(([x, z], i) => { const [X, Y] = P(x, z); if (i) g.lineTo(X, Y); else g.moveTo(X, Y); }); g.closePath(); g.fill(); g.stroke();
    }
    let prev: Pose = this.pose;
    wps.forEach((w, i) => {
      const [X, Y] = P(w.x, w.z), tb = bearingTo(prev.x, prev.z, w.x, w.z), t = turn(tb, w.headingDeg), [fx, fz] = forward(w.headingDeg), isSel = i === r.selected;
      if (Math.abs(t) > 2) {      // the turn to the waypoint's heading: an arc from the travel direction, with an arrowhead
        const a0 = ((tb - 90) * Math.PI) / 180, a1 = ((tb + t - 90) * Math.PI) / 180;
        g.strokeStyle = "#fff"; g.lineWidth = 1.5; g.beginPath(); g.arc(X, Y, 15, a0, a1, t < 0); g.stroke();
        const ex = X + 15 * Math.cos(a1), ey = Y + 15 * Math.sin(a1), tang = a1 + (t > 0 ? Math.PI / 2 : -Math.PI / 2);
        g.fillStyle = "#fff"; g.beginPath(); g.moveTo(ex + 5 * Math.cos(tang), ey + 5 * Math.sin(tang)); g.lineTo(ex + 3 * Math.cos(tang + 2.2), ey + 3 * Math.sin(tang + 2.2)); g.lineTo(ex + 3 * Math.cos(tang - 2.2), ey + 3 * Math.sin(tang - 2.2)); g.closePath(); g.fill();
      }
      g.strokeStyle = isSel ? "#fff" : BLUE; g.lineWidth = 2.5; g.beginPath(); g.moveTo(X, Y); g.lineTo(X + fx * 26, Y + fz * 26); g.stroke();      // the heading
      g.fillStyle = isSel ? "#fff" : BLUE; g.beginPath(); g.arc(X, Y, 7, 0, 2 * Math.PI); g.fill();
      g.fillStyle = isSel ? "#003" : "#fff"; g.font = "bold 10px system-ui"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText(String(i + 1), X, Y + 0.5);
      prev = w;
    });
    if (d && d.moved) {      // the heading being dragged
      const [X, Y] = P(d.x, d.z), [fx, fz] = forward(d.headingDeg);
      g.strokeStyle = "#fff"; g.lineWidth = 2.5; g.beginPath(); g.moveTo(X, Y); g.lineTo(X + fx * 30, Y + fz * 30); g.stroke(); g.fillStyle = "#fff"; g.beginPath(); g.arc(X, Y, 6, 0, 2 * Math.PI); g.fill();
    }
    g.restore();
  }
}
