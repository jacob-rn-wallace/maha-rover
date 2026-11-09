import { freshness, formatAge, type CamPose } from "./freshness";

/** What was known when a still was taken, for the compass and the readout beside it */
export interface Shot { image: HTMLCanvasElement; pose: CamPose; cameraBearing: number; pitchDeg: number; rollDeg: number }

const MAX = 6;
const GREEN = "#6fdc7a", AMBER = "#ffb04a", GREY = "#aaa";

/** A short camera roll of stills (P takes one; [ and ] step back and forward; V or the live button returns to the live view), with Open MCT's three freshness flags for the selected still.
 *  Viewing a past still pauses the live view (CameraView draws the still instead); `selected` is -1 for live. The roll strip is a DOM row of thumbnails and two buttons. */
export class CameraRoll {
  readonly strip = document.createElement("div");
  readonly flags = document.createElement("div");
  shots: Shot[] = [];
  selected = -1;
  private thumbs = document.createElement("span");
  private liveBtn = document.createElement("button");

  constructor() {
    this.strip.className = "tile-roll"; this.strip.style.display = "none";
    const snap = this.button("snap<span class=\"k\"> (P)</span>"); snap.addEventListener("click", () => this.onSnap?.());
    this.liveBtn = this.button("live<span class=\"k\"> (V)</span>"); this.liveBtn.addEventListener("click", () => this.live());
    this.thumbs.style.cssText = "display:flex;gap:4px;flex-wrap:wrap";
    this.strip.append(this.thumbs, this.liveBtn, snap);
    this.flags.className = "flags";
  }
  /** set by CameraView: take a still at the next draw */
  onSnap?: () => void;

  private button(text: string) {
    const b = document.createElement("button"); b.innerHTML = text;
    b.style.cssText = "padding:3px 8px;border-radius:5px;background:rgba(0,0,0,.6);color:#fff;border:1px solid rgba(255,255,255,.4);font:11px system-ui;cursor:pointer";
    return b;
  }

  get past() { return this.selected >= 0; }
  get current(): Shot | undefined { return this.past ? this.shots[this.selected] : undefined; }
  live() { this.selected = -1; this.render(); }
  /** older (-1) or newer (+1): from live, older goes to the newest still; past the newest, newer goes back to live */
  step(dir: -1 | 1) {
    if (!this.shots.length) return;
    if (this.selected < 0) { if (dir < 0) this.selected = this.shots.length - 1; }
    else { this.selected += dir; if (this.selected >= this.shots.length) this.selected = -1; else if (this.selected < 0) this.selected = 0; }
    this.render();
  }
  add(shot: Shot) {
    this.shots.push(shot); if (this.shots.length > MAX) { this.shots.shift(); if (this.selected > 0) this.selected--; }
    this.render();
  }

  private render() {
    this.thumbs.replaceChildren(...this.shots.map((s, i) => {
      const c = document.createElement("canvas"); c.width = 48; c.height = 36; c.getContext("2d")!.drawImage(s.image, 0, 0, 48, 36);
      c.style.cssText = `border:2px solid ${i === this.selected ? AMBER : "rgba(255,255,255,.4)"};cursor:pointer;display:block`;
      c.addEventListener("click", () => { this.selected = i; this.render(); });
      return c;
    }));
    this.liveBtn.style.borderColor = this.past ? "rgba(255,255,255,.4)" : GREEN;
  }

  /** updates the flag chips for the selected still (or "live") against the pose now */
  updateFlags(now: CamPose) {
    const chip = (text: string, colour: string) => `<span style="padding:1px 6px;border-radius:9px;background:rgba(0,0,0,.6);border:1px solid ${colour};color:${colour}">${text}</span>`;
    const s = this.current;
    if (!s) { this.flags.innerHTML = chip("live", GREEN); return; }
    const f = freshness(s.pose, now);
    this.flags.innerHTML = chip(`past image, ${formatAge(f.ageS)} old`, f.fresh ? GREEN : GREY) + chip(f.roverMoved ? "rover has moved" : "rover has not moved", f.roverMoved ? AMBER : GREEN) + chip(f.cameraMoved ? "camera has moved" : "camera unchanged", f.cameraMoved ? AMBER : GREEN);
  }

  /** shown by the stylesheet (flex, or none on phones); hidden here only while the tile is off */
  show(visible: boolean) { this.strip.style.display = visible ? "" : "none"; }
}
