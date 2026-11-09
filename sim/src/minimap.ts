import type { Terrain } from "./terrain";

/** A map of the 5 x 5 km sandbox: the elevation tile as hill shading (the sim's own sun) tinted by height, the rover as an arrow with its path behind it, north up.
 *  Built once from the smoothed tile (SIZE x SIZE samples, 20 m each); the rover and path are redrawn at 10 Hz. M cycles small, large, off.
 *  The tile is the only thing mapped: the ring beyond it is not shown. Height tint is relative to the tile's own range. */
const SIZE = 256, TRAIL_STEP = 3, TRAIL_MAX = 800;

export class Minimap {
  readonly box = document.createElement("div");
  private canvas = document.createElement("canvas");
  private base = document.createElement("canvas");
  private label = document.createElement("div");
  private trail: [number, number][] = [];
  mode = 1;                       // 0 off, 1 small, 2 large
  private half: number;

  constructor(private terrain: Terrain, sunElevationDeg: number, sunAzimuthDeg: number, private coarse: boolean, parent: HTMLElement) {
    this.half = terrain.half;
    this.base.width = this.base.height = SIZE;
    this.paintBase(sunElevationDeg, sunAzimuthDeg);
    this.canvas.width = this.canvas.height = SIZE;
    this.box.className = "panel tile map-tile"; this.box.style.cssText = "position:relative;background:#000";
    this.canvas.style.cssText = "display:block";
    this.label.style.cssText = "position:absolute;left:4px;bottom:2px;font:10px system-ui;color:#ddd;text-shadow:0 0 3px #000";
    this.box.append(this.canvas, this.label);
    parent.appendChild(this.box);
    this.layout(); addEventListener("resize", () => this.layout());
  }

  /** hill shading with the sim's sun, tinted dark to light by height (a tile-relative ramp) */
  private paintBase(el: number, az: number) {
    const g = this.base.getContext("2d")!, img = g.createImageData(SIZE, SIZE), step = 2 * this.half / SIZE;
    const hs = new Float32Array(SIZE * SIZE);
    let lo = Infinity, hi = -Infinity;
    for (let j = 0; j < SIZE; j++) for (let i = 0; i < SIZE; i++) {
      const h = this.terrain.tileAt(-this.half + (i + 0.5) * step, -this.half + (j + 0.5) * step);
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
  }

  /** the tile's size: 200 px small, large up to 420 but at most 38% of the window's height (the camera tile stacks under it); 110 and 240 on phones */
  layout() {
    const size = this.mode === 2 ? (this.coarse ? Math.min(240, innerHeight * 0.45) : Math.min(420, innerHeight * 0.38)) : this.coarse ? 96 : 200;
    this.box.style.display = this.mode === 0 ? "none" : "block";
    this.canvas.style.width = this.canvas.style.height = Math.round(size) + "px";
  }

  cycle() { this.mode = (this.mode + 1) % 3; this.layout(); }

  /** x, z: rover position (world); fx, fz: its forward direction on the ground */
  update(x: number, z: number, fx: number, fz: number) {
    if (this.mode === 0) return;
    const last = this.trail[this.trail.length - 1];
    if (!last || Math.hypot(x - last[0], z - last[1]) > TRAIL_STEP) { this.trail.push([x, z]); if (this.trail.length > TRAIL_MAX) this.trail.shift(); }
    const g = this.canvas.getContext("2d")!, S = SIZE, k = S / (2 * this.half);
    const px = (x + this.half) * k, py = (z + this.half) * k;
    g.drawImage(this.base, 0, 0);
    g.strokeStyle = "rgba(255,200,80,.9)"; g.lineWidth = 1.5; g.beginPath();
    this.trail.forEach(([tx, tz], i) => { const X = (tx + this.half) * k, Y = (tz + this.half) * k; if (i) g.lineTo(X, Y); else g.moveTo(X, Y); });
    g.lineTo(px, py); g.stroke();
    // heading arrow, drawn at a fixed size whatever the scale
    const ang = Math.atan2(fz, fx);
    g.save(); g.translate(px, py); g.rotate(ang);
    g.fillStyle = "#ff4a3a"; g.strokeStyle = "#fff"; g.lineWidth = 1.2;
    g.beginPath(); g.moveTo(8, 0); g.lineTo(-5, 5); g.lineTo(-2, 0); g.lineTo(-5, -5); g.closePath(); g.fill(); g.stroke();
    g.restore();
    g.fillStyle = "#fff"; g.font = "bold 13px system-ui"; g.fillText("N", S / 2 - 4, 13);       // north is up
    const km = 1000 * k;                                                                          // a 1 km scale bar
    g.fillStyle = "#fff"; g.fillRect(S - km - 8, S - 10, km, 2); g.font = "10px system-ui"; g.fillText("1 km", S - km - 8, S - 14);
    this.label.textContent = `${x.toFixed(0)} E, ${(-z).toFixed(0)} N`;
  }
}
