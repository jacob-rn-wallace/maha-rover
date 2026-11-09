import { h } from "./layout";
import type { UI } from "./ui";
import type { CameraView } from "./cameraView";
import type { Minimap } from "./minimap";

export type Mode = "drive" | "plan" | "camera" | "data";
export const MODES: { id: Mode; label: string; key: number }[] = [{ id: "drive", label: "Drive", key: 1 }, { id: "plan", label: "Plan", key: 2 }, { id: "camera", label: "Camera", key: 3 }, { id: "data", label: "Data", key: 4 }];

/** The modes of docs/sim-ui-layout.md: layout presets that decide which view is the main one and which panels are open (the top bar, the alerts and the cluster stay in every mode).
 *  - Drive: the chase view; the map and the camera as small tiles. Camera: the mast camera as the main view (the 4:3 picture, with its flags, compass and roll), the chase view as an inset. Plan: the map as the
 *  main view, the chase view as an inset (the waypoint planner comes with step 4). Data: the chase view with the telemetry dock open and the map small (the strips come with step 6).
 *  The inset is a DOM box over the canvas; the chase view is drawn into its rectangle. Clicking it returns to Drive. */
export class Modes {
  mode: Mode = "drive";
  onEnter?: (m: Mode) => void;      // called after a mode is set
  private inset = h("div"); private lastMapKey = "";

  /** `planBox`: the Plan panel, shown in the left dock in Plan mode in place of the telemetry */
  constructor(private ui: UI, private cam: CameraView, private map: Minimap | undefined, private coarse: boolean, private planBox?: HTMLElement) {
    const box = ui.layout.inset; box.classList.add("panel"); box.title = "chase view: click to return to Drive";
    const label = h("span", "inset-label", "chase view"); box.append(label); this.inset = box; box.addEventListener("click", () => this.set("drive"));
    this.set("drive");
  }

  set(m: Mode) {
    this.mode = m;
    const { ui, cam, map } = this;
    const planBox = this.planBox; ui.layout.root.dataset.mode = m; ui.bar.setMode(m);
    cam.primary = m === "camera"; cam.shown = m === "drive" || m === "camera";
    if (map) { map.shown = m !== "camera"; if (m !== "plan") map.setPrimary(false); }
    ui.tele.toggle(m === "data" || m === "plan");
    ui.tele.box.style.display = m === "plan" && planBox ? "none" : ""; if (planBox) planBox.style.display = m === "plan" ? "" : "none";
    this.inset.style.display = this.hasInset ? "block" : "none";
    this.onEnter?.(m);
  }
  get hasInset() { return this.mode === "camera" || this.mode === "plan"; }
  /** C: the camera as the main view, and back */
  toggleCamera() { this.set(this.mode === "camera" ? "drive" : "camera"); }

  /** sizes the inset and the main-view tiles for a window of vw x vh CSS pixels; call once a frame, before the views are drawn */
  layout(vw: number, vh: number) {
    const w = Math.round(this.coarse ? 120 : Math.max(160, Math.min(240, vw * 0.17)));
    this.inset.style.width = w + "px"; this.inset.style.height = Math.round(w * 0.625) + "px";
    this.cam.reserveX = w + 24;
    if (this.mode === "plan" && this.map) {      // the square map in the room between the dock and the inset
      const bar = this.coarse ? 32 : 36, x0 = this.planBox ? 316 : 12, x1 = vw - w - 24, px = Math.round(Math.max(120, Math.min(x1 - x0, vh - bar - 16))), cx = Math.round((x0 + x1) / 2), key = px + "," + cx;
      if (key !== this.lastMapKey) { this.lastMapKey = key; this.map.setPrimary(true, px, cx); }
    }
  }

  /** the rectangle the chase view is drawn into (CSS pixels, origin bottom left), or null for the whole window */
  chaseRect(vh: number) {
    if (!this.hasInset) return null;
    const r = this.inset.getBoundingClientRect();
    return { x: r.left, y: vh - r.bottom, w: r.width, h: r.height };
  }
}
