/** A compass rose for the mast camera view, after Open MCT's imagery compass: north up or camera direction up (a click toggles), the camera's field of view as a wedge, the sun as a dot
 *  (only when it is above the horizon). Bearings are degrees clockwise from north. */
export class Compass {
  readonly el = document.createElement("canvas");
  northUp = true;
  private ctx: CanvasRenderingContext2D;
  private size = 72;

  constructor(private fovDeg: number) {
    const r = 2;      // drawn at twice the CSS size so the lines stay sharp
    this.el.width = this.el.height = this.size * r; this.el.style.cssText = `width:${this.size}px;height:${this.size}px;cursor:pointer;pointer-events:auto`;
    this.el.title = "click: north up or camera direction up";
    this.ctx = this.el.getContext("2d")!; this.ctx.scale(r, r);
    this.el.addEventListener("click", () => { this.northUp = !this.northUp; });
  }

  draw(cameraBearing: number, sunBearing: number, sunElDeg: number) {
    const c = this.ctx, S = this.size, R = S / 2 - 2, cx = S / 2, cy = S / 2;
    const rot = this.northUp ? 0 : cameraBearing, ang = (b: number) => ((b - rot) * Math.PI) / 180;      // screen angle clockwise from up
    const at = (b: number, r: number): [number, number] => [cx + r * Math.sin(ang(b)), cy - r * Math.cos(ang(b))];
    c.clearRect(0, 0, S, S);
    c.fillStyle = "rgba(0,0,0,.5)"; c.beginPath(); c.arc(cx, cy, R, 0, 2 * Math.PI); c.fill();
    c.strokeStyle = "rgba(255,255,255,.6)"; c.lineWidth = 1; c.stroke();
    c.fillStyle = "rgba(255,255,255,.28)"; c.beginPath(); c.moveTo(cx, cy);      // the field of view
    for (let k = 0; k <= 12; k++) { const [x, y] = at(cameraBearing - this.fovDeg / 2 + (this.fovDeg * k) / 12, R); c.lineTo(x, y); }
    c.closePath(); c.fill();
    c.font = "bold 10px system-ui"; c.textAlign = "center"; c.textBaseline = "middle";
    for (const [b, t] of [[0, "N"], [90, "E"], [180, "S"], [270, "W"]] as const) { const [x, y] = at(b, R - 8); c.fillStyle = b === 0 ? "#ff6a5a" : "#eee"; c.fillText(t, x, y); }
    if (sunElDeg > 0) { const [x, y] = at(sunBearing, R - 17); c.fillStyle = "#ffd84a"; c.beginPath(); c.arc(x, y, 3.5, 0, 2 * Math.PI); c.fill(); }
  }
}
