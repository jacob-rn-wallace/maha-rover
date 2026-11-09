import "./ui.css";

/** a DOM element with a class and optional html */
export function h<K extends keyof HTMLElementTagNameMap>(tag: K, cls = "", html = ""): HTMLElementTagNameMap[K] {
  const e = document.createElement(tag); if (cls) e.className = cls; if (html) e.innerHTML = html; return e;
}

/** The overlay over the canvas and the regions in it (docs/sim-ui-layout.md, section 6). Panels are mounted into a region and stack there: nothing positions itself, so panels cannot overlap.
 *  top: the bar. left: the telemetry dock (slides in over a handle). right: a column of tiles (map, camera). cluster: bottom left. alerts: bottom centre. sticks: the touch controls. modal: the centre. */
export class Layout {
  readonly root = h("div"); readonly top = h("div"); readonly left = h("div"); readonly handle = h("button", "iconbtn", "›");
  readonly right = h("div"); readonly cluster = h("div"); readonly alerts = h("div"); readonly sticks = h("div"); readonly modal = h("div");
  private pops = new Map<string, { pop: HTMLElement; anchor: HTMLElement }>();

  constructor(readonly coarse: boolean) {
    this.root.id = "ui"; if (coarse) this.root.classList.add("coarse");
    this.top.id = "ui-top"; this.left.id = "ui-left"; this.handle.id = "ui-handle"; this.right.id = "ui-right"; this.cluster.id = "ui-cluster"; this.alerts.id = "ui-alerts"; this.sticks.id = "ui-sticks"; this.modal.id = "ui-modal";
    this.handle.title = "telemetry (I)";
    this.root.append(this.top, this.left, this.handle, this.right, this.cluster, this.alerts, this.sticks, this.modal);
    document.body.appendChild(this.root);
    addEventListener("pointerdown", (e) => { if (!(e.target as Element).closest?.(".pop, .chip, .iconbtn")) this.closePops(); });
    addEventListener("keydown", (e) => { if (e.code === "Escape") this.closePops(); });
  }

  /** a popover under the top bar, aligned to its anchor; one is open at a time per id, any click elsewhere or Escape closes them */
  popover(id: string, anchor: HTMLElement, content: HTMLElement) {
    const pop = h("div", "panel pop"); pop.append(content); this.root.appendChild(pop); this.pops.set(id, { pop, anchor });
    return pop;
  }
  togglePop(id: string, on?: boolean) {
    const p = this.pops.get(id); if (!p) return;
    const open = on ?? !p.pop.classList.contains("open");
    if (open) { this.closePops(id); const r = p.anchor.getBoundingClientRect(); p.pop.style.left = Math.max(8, Math.min(r.left, innerWidth - 8 - Math.max(220, p.pop.offsetWidth))) + "px"; }
    p.pop.classList.toggle("open", open);
  }
  closePops(except?: string) { for (const [id, p] of this.pops) if (id !== except) p.pop.classList.remove("open"); }
  isPopOpen(id: string) { return !!this.pops.get(id)?.pop.classList.contains("open"); }
}
