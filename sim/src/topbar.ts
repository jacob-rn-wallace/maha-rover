import { h, type Layout } from "./layout";
import type { Level } from "./limits";
import type { Mode } from "./modes";
import { MODES } from "./modes";

export interface BarActions { toggleHazard(): void; toggleHelp(): void; toggleLog(): void; setMode(m: Mode): void }
export type ChipId = "battery" | "tilt" | "wall" | "hazard" | "rec" | "route";
type Lv = Level | "off" | "on" | "route";

/** The top bar: the wordmark at the bar's height, status chips coloured by the limits table (a chip's popover holds its detail), and the help and settings buttons.
 *  The mode tabs (Drive, Plan, Camera, Data) sit beside the wordmark. */
export class TopBar {
  private chips: Record<ChipId, HTMLElement>; private tabs = new Map<Mode, HTMLElement>();
  readonly batteryDetail = h("div"); readonly settings = h("div"); readonly stats = h("pre"); private rec = h("button", "act", "record a performance log (L)");

  constructor(private layout: Layout, legend: HTMLElement, on: BarActions) {
    const bar = layout.top;
    const logo = h("img", "logo"); logo.src = "almaha-wordmark-white.svg"; logo.alt = "المَهَا al-maha";
    const chip = (id: ChipId, text: string) => { const c = h("button", "chip", text); c.dataset.level = "off"; c.title = id; return c; };
    const battery = chip("battery", "battery"), tilt = chip("tilt", "tilt"), wall = chip("wall", "wall"), recChip = chip("rec", "rec"), route = chip("route", "route");
    wall.classList.add("hidden"); recChip.classList.add("hidden"); route.classList.add("hidden"); route.title = "the route: click for the Plan mode"; route.addEventListener("click", () => on.setMode("plan"));
    const hz = h("span", "chip pair"); hz.dataset.level = "off";
    const hzMain = h("button", "", "hazard"), hzMore = h("button", "", "▾"); hzMain.title = "hazard overlay (H)"; hzMore.title = "hazard legend";
    hz.append(hzMain, hzMore);
    this.chips = { battery, tilt, wall, hazard: hz, rec: recChip, route };
    const help = h("button", "iconbtn", "?"), gear = h("button", "iconbtn", "⚙"); help.title = "keys (?)"; gear.title = "settings and performance";
    const tabs = h("div", "tabs");
    for (const m of MODES) { const t = h("button", "tab", m.label); t.title = `${m.label} (${m.key})`; t.addEventListener("click", () => on.setMode(m.id)); this.tabs.set(m.id, t); tabs.append(t); }
    const sp = () => h("span", "spacer");
    bar.append(logo, tabs, sp(), route, battery, tilt, wall, hz, recChip, sp(), help, gear);

    this.batteryDetail.innerHTML = "";
    layout.popover("battery", battery, this.batteryDetail);
    layout.popover("legend", hz, legend);
    this.settings.append(h("h4", "", "settings and performance"), this.stats, this.rec);
    layout.popover("settings", gear, this.settings);
    battery.addEventListener("click", () => layout.togglePop("battery"));
    hzMain.addEventListener("click", () => on.toggleHazard());
    hzMore.addEventListener("click", () => layout.togglePop("legend"));
    help.addEventListener("click", () => on.toggleHelp());
    gear.addEventListener("click", () => layout.togglePop("settings"));
    this.rec.addEventListener("click", () => on.toggleLog());
    recChip.addEventListener("click", () => on.toggleLog());
  }

  set(id: ChipId, text: string | null, level: Lv) {
    const c = this.chips[id];
    if (text === null) { c.classList.add("hidden"); return; }
    c.classList.remove("hidden"); c.dataset.level = String(level);
    if (id === "hazard") return;      // a pair of buttons: its label is fixed
    if (c.textContent !== text) c.textContent = text;
  }
  setMode(m: Mode) { for (const [id, t] of this.tabs) t.classList.toggle("active", id === m); }
  setRecording(on: boolean) { this.rec.textContent = on ? "stop and show the log (L)" : "record a performance log (L)"; }
}
