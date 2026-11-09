import { h, type Layout } from "./layout";

const KEYS: [string, string][] = [
  ["W / S, up / down", "drive forward and back"], ["A / D, left / right", "steer (skid steering)"], ["Space", "brake"],
  ["Q / E", "mast pan"], ["R / F", "mast tilt"], ["T", "stand the rover upright where it is"],
  ["1 2 3 4", "modes: Drive, Plan, Camera, Data"], ["C", "the mast camera as the main view, and back"], ["P", "take a still of the camera view"], ["[ / ]", "step back and forward through the stills"], ["V", "back to the live camera view"],
  ["M", "minimap: small, large, off (Drive and Data)"], ["H", "hazard overlay"], ["I", "telemetry panel"], ["L", "record a performance log (L again to stop)"], ["Backspace", "undo the last waypoint (Plan mode)"], ["? / Esc", "this list / close"],
];

/** the full key list, behind the ? button and key (a box in the modal region) */
export class Help {
  private box = h("div", "panel");
  constructor(layout: Layout) {
    this.box.style.cssText = "padding:10px 14px;min-width:300px;display:none";
    this.box.innerHTML = `<h4 style="margin:0 0 6px;font-size:12px;color:#fff">keys</h4>` + KEYS.map(([k, d]) => `<div style="display:flex;gap:14px;justify-content:space-between"><b style="color:#fff">${k}</b><span class="dim">${d}</span></div>`).join("") + `<div class="dim" style="margin-top:6px">gamepad: left stick drive, right stick mast</div>`;
    layout.modal.append(this.box);
  }
  toggle() { this.box.style.display = this.box.style.display === "none" ? "block" : "none"; }
  close() { this.box.style.display = "none"; }
}
