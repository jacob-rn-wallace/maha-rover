import { h, type Layout } from "./layout";
import type { Level } from "./limits";

export interface Row { label: string; value: string; level?: Level }
export interface Section { title: string; rows: Row[] }

/** The telemetry panel: the left dock, closed by default (the status chips and the instrument cluster carry what is needed at a glance); I or the handle opens it. Grouped rows, coloured by the limits table.
 *  Closed, it is slid off the screen but stays in the page, so scripted checks can still read it. */
export class TelemetryPanel {
  readonly box = h("div", "panel tele");
  private last = "";

  constructor(private layout: Layout) {
    this.box.id = "hud";      // tests/cdp-shot.mjs reads the readout from here
    layout.left.append(this.box);
    layout.handle.addEventListener("click", () => this.toggle());
  }

  get open() { return this.layout.left.classList.contains("open"); }
  toggle(on?: boolean) {
    const open = on ?? !this.open; this.layout.left.classList.toggle("open", open); this.layout.handle.textContent = open ? "‹" : "›";
    this.layout.left.style.pointerEvents = open ? "auto" : "none";
  }

  update(sections: Section[]) {
    const html = sections.map((s) => `<h4>${s.title}</h4>` + s.rows.map((r) => `<div class="row"><span>${r.label}</span><span${r.level ? ` data-level="${r.level}"` : ""}>${r.value}</span></div>`).join("")).join("");
    if (html !== this.last) { this.last = html; this.box.innerHTML = html; }
  }
}
