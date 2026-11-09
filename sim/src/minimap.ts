import type { Terrain } from "./terrain";

/** A map of the 5 x 5 km sandbox: the elevation tile as hill shading (the sim's own sun) tinted by height, the rover as an arrow with its path behind it, north up.
 *  Built once from the smoothed tile (SIZE x SIZE samples, 20 m each); the rover and path are redrawn at 10 Hz. M cycles small, large, off.
 *  The tile is the only thing mapped: the ring beyond it is not shown. Height tint is relative to the tile's own range. */
const SIZE = 256, BIG = 768, TRAIL_STEP = 3, TRAIL_MAX = 800;      // BIG: the resolution of the base map when the map is the main view (Plan mode)

export class Minimap {
  readonly box = document.createElement("div");
  readonly canvas = document.createElement("canvas");
  private base = document.createElement("canvas");
  private label = document.createElement("div");
  private trail: [number, number][] = [];
  mode = 1;                       // 0 off, 1 small, 2 large
  shown = true;                   // false in the modes that have no map
  overlay?: (g: CanvasRenderingContext2D) => void;      // drawn over the trail, under the rover (the route); `toCanvas` maps world to canvas
  private primaryX = NaN;          // the centre of the main-view square, when it is not the window's
  private primary = false;        // the main view (Plan): a big square in the middle
  private primaryPx = 400;
  private res = SIZE;             // samples a side of the base map
  private sunEl: number; private sunAz: number;
  readonly half: number;
  // the view: a window of the tile (centre and half width, metres); the whole tile unless zoomed (Plan mode). The base map is painted for a window and repainted, at most every 150 ms, when the view moves.
  private vcx = 0; private vcz = 0; vhalf: number;
  private baseWin = { cx: 0, cz: 0, half: 0 }; private lastPaint = 0; lastPaintMs = 0;
  onCentre?: () => void;

  constructor(private terrain: Terrain, sunElevationDeg: number, sunAzimuthDeg: number, private coarse: boolean, parent: HTMLElement) {
    this.half = terrain.half; this.vhalf = terrain.half; this.sunEl = sunElevationDeg; this.sunAz = sunAzimuthDeg;
    this.base.width = this.base.height = SIZE;
    this.paintBase(sunElevationDeg, sunAzimuthDeg);
    this.canvas.width = this.canvas.height = SIZE;
    this.box.className = "panel tile map-tile";
    this.canvas.style.cssText = "display:block";
    this.label.style.cssText = "position:absolute;left:4px;bottom:2px;font:10px system-ui;color:#ddd;text-shadow:0 0 3px #000";
    const ctl = document.createElement("div"); ctl.className = "map-ctl";
    for (const [t, tip, fn] of [["+", "zoom in", () => this.zoom(0.6)], ["–", "zoom out", () => this.zoom(1 / 0.6)], ["◎", "centre on the rover", () => this.onCentre?.()]] as [string, string, () => void][]) { const b = document.createElement("button"); b.textContent = t; b.title = tip; b.addEventListener("click", fn); ctl.append(b); }
    this.canvas.addEventListener("wheel", (e) => { if (!this.primary) return; e.preventDefault(); const w = this.toWorld(e.clientX, e.clientY); if (w) this.zoom(e.deltaY > 0 ? 1.25 : 0.8, w.x, w.z); }, { passive: false });
    this.canvas.addEventListener("contextmenu", (e) => { if (this.primary) e.preventDefault(); });
    this.box.append(this.canvas, this.label, ctl);
    parent.appendChild(this.box);
    this.layout(); addEventListener("resize", () => this.layout());
  }

  /** hill shading with the sim's sun, tinted dark to light by height (a tile-relative ramp) */
  private paintBase(el: number, az: number) {
    const SIZE = this.res, t0 = performance.now();
    const w = this.baseWin = { cx: this.vcx, cz: this.vcz, half: this.vhalf }; this.lastPaint = t0;
    const g = this.base.getContext("2d")!, img = g.createImageData(SIZE, SIZE), step = 2 * w.half / SIZE;
    const hs = new Float32Array(SIZE * SIZE);
    let lo = Infinity, hi = -Infinity;
    for (let j = 0; j < SIZE; j++) for (let i = 0; i < SIZE; i++) {
      const h = this.terrain.tileAt(w.cx - w.half + (i + 0.5) * step, w.cz - w.half + (j + 0.5) * step);
      hs[j * SIZE + i] = h; lo = Math.min(lo, h); hi = Math.max(hi, h);
    }
    const e = el * Math.PI / 180, a = az * Math.PI / 180;
    const sx = Math.cos(e) * Math.cos(a), sy = Math.sin(e), sz = -Math.cos(e) * Math.sin(a);        // towards the sun, world x east, y up, z south
    for (let j = 0; j < SIZE; j++) for (let i = 0; i < SIZE; i++) {
      const at = (x: number, y: number) => hs[Math.min(SIZE - 1, Math.max(0, y)) * SIZE + Math.min(SIZE - 1, Math.max(0, x))];
      const dx = (at(i + 1, j) - at(i - 1, j)) / (2 * step), dz = (at(i, j + 1) - at(i, j - 1)) / (2 * step);
      const l = Math.hypot(dx, 1, dz), shade = Math.max(0, (-dx * sx + sy - dz * sz) / l);       // normal (-dx, 1, -dz)
      const t = (hs[j * SIZE + i] - lo) / (hi - lo || 1), k = (j * SIZE + i) * 4;
      const v = Math.min(1, Math.max(0.12, 0.55 + 1.1 * (shade / Math.max(sy, 0.1) - 1)));         // flat ground (shade = sin(elevation)) maps to 0.55, slopes towards the sun brighter, away darker
      img.data[k] = 255 * v * (0.55 + 0.45 * t); img.data[k + 1] = 255 * v * (0.52 + 0.4 * t); img.data[k + 2] = 255 * v * (0.5 + 0.3 * t); img.data[k + 3] = 255;
    }
    g.putImageData(img, 0, 0);
    this.lastPaintMs = performance.now() - t0;
  }

  /** the tile's size: 200 px small, large up to 420 but at most 38% of the window's height (the camera tile stacks under it); 96 and 240 on phones; as the main view, a square of `primaryPx` */
  layout() {
    const size = this.primary ? this.primaryPx : this.mode === 2 ? (this.coarse ? Math.min(240, innerHeight * 0.45) : Math.min(420, innerHeight * 0.38)) : this.coarse ? 96 : 200;
    this.box.style.display = this.mode === 0 || !this.shown ? "none" : "block";
    this.box.classList.toggle("primary", this.primary); this.box.style.left = this.primary && isFinite(this.primaryX) ? Math.round(this.primaryX) + "px" : "";
    this.canvas.style.width = this.canvas.style.height = Math.round(size) + "px";
  }

  /** the main view (Plan mode): a bigger base map (painted once, on first use) in a square of `px` */
  setPrimary(on: boolean, px = this.primaryPx, centreX = NaN) {
    this.primaryPx = px; this.primaryX = centreX;
    if (on && this.res !== BIG) { this.res = BIG; this.base.width = this.base.height = BIG; this.canvas.width = this.canvas.height = BIG; this.paintBase(this.sunEl, this.sunAz); }
    this.primary = on; if (!on) this.setView(0, 0, this.half); this.layout();
  }

  /** the window shown: centre (x, z) and half width in metres, kept inside the tile and at least 40 m */
  setView(cx: number, cz: number, half: number) {
    this.vhalf = Math.max(40, Math.min(this.half, half)); this.vcx = Math.max(-this.half + this.vhalf, Math.min(this.half - this.vhalf, cx)); this.vcz = Math.max(-this.half + this.vhalf, Math.min(this.half - this.vhalf, cz));
  }
  pan(dx: number, dz: number) { this.setView(this.vcx + dx, this.vcz + dz, this.vhalf); }
  /** zooms by `factor` (above 1 shows more) keeping the world point (wx, wz) where it is on the screen */
  zoom(factor: number, wx = this.vcx, wz = this.vcz) { const h = Math.max(40, Math.min(this.half, this.vhalf * factor)), r = h / this.vhalf; this.setView(wx - (wx - this.vcx) * r, wz - (wz - this.vcz) * r, h); }
  /** world to canvas pixels */
  toCanvas(x: number, z: number): [number, number] { const k = this.res / (2 * this.vhalf); return [(x - (this.vcx - this.vhalf)) * k, (z - (this.vcz - this.vhalf)) * k]; }

  cycle() { this.mode = (this.mode + 1) % 3; this.layout(); }

  /** the world position (x east, z south) under a point of the window, or null outside the map */
  toWorld(clientX: number, clientY: number) {
    const r = this.canvas.getBoundingClientRect(), u = (clientX - r.left) / r.width, v = (clientY - r.top) / r.height;
    return u < 0 || u > 1 || v < 0 || v > 1 ? null : { x: this.vcx + (u * 2 - 1) * this.vhalf, z: this.vcz + (v * 2 - 1) * this.vhalf };
  }

  /** x, z: rover position (world); fx, fz: its forward direction on the ground */
  update(x: number, z: number, fx: number, fz: number) {
    if (this.mode === 0) return;
    const last = this.trail[this.trail.length - 1];
    if (!last || Math.hypot(x - last[0], z - last[1]) > TRAIL_STEP) { this.trail.push([x, z]); if (this.trail.length > TRAIL_MAX) this.trail.shift(); }
    if (!this.shown) return;      // the trail is kept, the drawing is not
    const w = this.baseWin, moved = w.cx !== this.vcx || w.cz !== this.vcz || w.half !== this.vhalf;
    if (moved && performance.now() - this.lastPaint > 150) this.paintBase(this.sunEl, this.sunAz);
    const g = this.canvas.getContext("2d")!, S = this.res, k = S / (2 * this.vhalf);
    const [px, py] = this.toCanvas(x, z), [bx, by] = this.toCanvas(this.baseWin.cx - this.baseWin.half, this.baseWin.cz - this.baseWin.half);
    g.fillStyle = "#000"; g.fillRect(0, 0, S, S);
    g.drawImage(this.base, bx, by, 2 * this.baseWin.half * k, 2 * this.baseWin.half * k);      // the base map, placed by the window it was painted for (a stale one shows in the frames before a repaint)
    g.strokeStyle = "rgba(255,200,80,.9)"; g.lineWidth = 1.5; g.beginPath();
    this.trail.forEach(([tx, tz], i) => { const [X, Y] = this.toCanvas(tx, tz); if (i) g.lineTo(X, Y); else g.moveTo(X, Y); });
    g.lineTo(px, py); g.stroke();
    this.overlay?.(g);
    // heading arrow, drawn at a fixed size whatever the scale
    const ang = Math.atan2(fz, fx);
    g.save(); g.translate(px, py); g.rotate(ang);
    g.fillStyle = "#ff4a3a"; g.strokeStyle = "#fff"; g.lineWidth = 1.2;
    g.beginPath(); g.moveTo(8, 0); g.lineTo(-5, 5); g.lineTo(-2, 0); g.lineTo(-5, -5); g.closePath(); g.fill(); g.stroke();
    g.restore();
    g.fillStyle = "#fff"; g.font = "bold 13px system-ui"; g.fillText("N", S / 2 - 4, 13);       // north is up
    const target = (0.15 * S) / k, len = [10, 20, 50, 100, 200, 500, 1000, 2000].reduce((a, b) => (Math.abs(b - target) < Math.abs(a - target) ? b : a)), bar = len * k;      // a scale bar of about 15% of the map
    g.fillStyle = "#fff"; g.fillRect(S - bar - 8, S - 10, bar, 2); g.font = "10px system-ui"; g.fillText(len >= 1000 ? `${len / 1000} km` : `${len} m`, S - bar - 8, S - 14);
    this.label.textContent = `${x.toFixed(0)} E, ${(-z).toFixed(0)} N`;
  }
}
