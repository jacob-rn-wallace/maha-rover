import { h, type Layout } from "./layout";
import type { Level } from "./limits";

export interface AlertItem { text: string; level: Level }

/** Bottom centre: alerts (only when a limit is yellow or red, or the tilt guard has cut the drive), a status banner (loading, errors) and the one-line key hint, which goes after the first input. */
export class Alerts {
  private list = h("div"); private banner = h("div", "alert"); private hint = h("div", "hint", "W/S drive · A/D steer · Q/E pan · R/F tilt · Space brake · ? for all keys");
  private shown = "";

  constructor(layout: Layout) {
    this.list.style.cssText = "display:flex;flex-direction:column;align-items:center;gap:6px";
    this.banner.style.display = "none"; this.banner.dataset.level = "0";
    layout.alerts.append(this.list, this.banner, this.hint);
  }

  /** loading and error text; null clears it */
  status(text: string | null, level: Level = 0) {
    this.banner.style.display = text ? "" : "none"; if (text) { this.banner.textContent = text; this.banner.dataset.level = String(level); }
  }
  set(items: AlertItem[]) {
    const key = items.map((i) => i.level + i.text).join("|"); if (key === this.shown) return; this.shown = key;
    this.list.replaceChildren(...items.map((i) => { const a = h("div", "alert", i.text); a.dataset.level = String(i.level); return a; }));
  }
  /** the hint fades out once the user has done something */
  dismissHint() { this.hint.classList.add("gone"); }
}
