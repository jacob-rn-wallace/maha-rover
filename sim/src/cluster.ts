import { h, type Layout } from "./layout";
import { cardinal } from "./freshness";
import type { Level } from "./limits";

/** The instrument cluster, bottom left: an attitude ball (pitch and roll), the speed and the heading. On phones the ball is hidden and the numbers remain. */
export class Cluster {
  private ball = h("canvas"); private text = h("div"); private ctx: CanvasRenderingContext2D; private S = 64;

  constructor(layout: Layout) {
    const box = h("div", "panel cluster");
    this.ball.width = this.ball.height = this.S * 2; this.ball.style.cssText = `width:${this.S}px;height:${this.S}px`;
    this.ctx = this.ball.getContext("2d")!; this.ctx.scale(2, 2);
    box.append(this.ball, this.text); layout.cluster.append(box);
  }

  /** speed in m/s, heading degrees clockwise from north, pitch (nose up positive) and roll (right bank positive) in degrees, the tilt level */
  update(speed: number, heading: number, pitch: number, roll: number, tilt: Level) {
    const c = this.ctx, S = this.S, R = S / 2 - 2;
    c.save(); c.clearRect(0, 0, S, S);
    c.beginPath(); c.arc(S / 2, S / 2, R, 0, 2 * Math.PI); c.clip();
    c.translate(S / 2, S / 2); c.rotate((-roll * Math.PI) / 180);      // a right bank turns the horizon counterclockwise
    const dy = Math.max(-R, Math.min(R, (pitch / 30) * R));            // a nose-up pitch moves the horizon down; 30 degrees is the edge of the ball
    c.fillStyle = "#3b6fa8"; c.fillRect(-S, -S + dy, 2 * S, S);
    c.fillStyle = "#7a5a3a"; c.fillRect(-S, dy, 2 * S, S);
    c.strokeStyle = "#fff"; c.lineWidth = 1; c.beginPath(); c.moveTo(-S, dy); c.lineTo(S, dy); c.stroke();
    c.restore();
    c.strokeStyle = "#fff"; c.lineWidth = 2; c.beginPath(); c.moveTo(S / 2 - 16, S / 2); c.lineTo(S / 2 - 5, S / 2); c.moveTo(S / 2 + 5, S / 2); c.lineTo(S / 2 + 16, S / 2); c.stroke();      // the fixed rover symbol
    c.strokeStyle = "rgba(255,255,255,.6)"; c.lineWidth = 1; c.beginPath(); c.arc(S / 2, S / 2, R, 0, 2 * Math.PI); c.stroke();
    const html = `<div class="speed">${speed.toFixed(2)} <small>m/s</small></div><div>heading ${heading.toFixed(0)}° ${cardinal(heading)}</div><div data-level="${tilt}">pitch ${pitch.toFixed(0)}° roll ${roll.toFixed(0)}°</div>`;
    if (html !== this.last) { this.last = html; this.text.innerHTML = html; }
  }
  private last = "";
}
