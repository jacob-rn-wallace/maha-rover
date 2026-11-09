import { h, type Layout } from "./layout";
import type { Level } from "./limits";
import type { Mode } from "./modes";
import { MODES } from "./modes";

export interface BarActions { toggleHazard(): void; toggleHelp(): void; toggleLog(): void; setMode(m: Mode): void; setDelay(oneWayS: number): void; toggleCruise(): void }
export type ChipId = "battery" | "tilt" | "wall" | "hazard" | "rec" | "route" | "delay" | "cruise";
type Lv = Level | "off" | "on" | "route";

/** The top bar: the wordmark at the bar's height, status chips coloured by the limits table (a chip's popover holds its detail), and the help and settings buttons.
 *  The mode tabs (Drive, Plan, Camera, Data) sit beside the wordmark. */
export class TopBar {
  private chips: Record<ChipId, HTMLElement>; private tabs = new Map<Mode, HTMLElement>();
  private delayChip!: HTMLElement; private delayUi!: { range: HTMLInputElement; dv: Element };
  readonly batteryDetail = h("div"); readonly settings = h("div"); readonly stats = h("pre"); private rec = h("button", "act", "record a performance log (L)");

  constructor(private layout: Layout, legend: HTMLElement, on: BarActions) {
    const bar = layout.top;
    const logo = h("img", "logo"); logo.src = "almaha-wordmark-white.svg"; logo.alt = "المَهَا al-maha";
    const chip = (id: ChipId, text: string) => { const c = h("button", "chip", text); c.dataset.level = "off"; c.title = id; return c; };
    const battery = chip("battery", "battery"), tilt = chip("tilt", "tilt"), wall = chip("wall", "wall"), recChip = chip("rec", "rec"), route = chip("route", "route"), delay = chip("delay", "delay off"), cruise = chip("cruise", "cruise");
    cruise.classList.add("hidden"); cruise.addEventListener("click", () => on.toggleCruise()); this.delayChip = delay;
    wall.classList.add("hidden"); recChip.classList.add("hidden"); route.classList.add("hidden"); route.title = "the route: click for the Plan mode"; route.addEventListener("click", () => on.setMode("plan"));
    const hz = h("span", "chip pair"); hz.dataset.level = "off";
    const hzMain = h("button", "", "hazard"), hzMore = h("button", "", "▾"); hzMain.title = "hazard overlay (H)"; hzMore.title = "hazard legend";
    hz.append(hzMain, hzMore);
    this.chips = { battery, tilt, wall, hazard: hz, rec: recChip, route, delay, cruise };
    const help = h("button", "iconbtn", "?"), gear = h("button", "iconbtn", "⚙"); help.title = "keys (?)"; gear.title = "settings and performance";
    const tabs = h("div", "tabs");
    for (const m of MODES) { const t = h("button", "tab", m.label); t.title = `${m.label} (${m.key})`; t.addEventListener("click", () => on.setMode(m.id)); this.tabs.set(m.id, t); tabs.append(t); }
    const sp = () => h("span", "spacer");
    const chipRow = h("div", "chips"); chipRow.append(route, battery, tilt, wall, hz, delay, cruise, recChip);
    bar.append(logo, tabs, sp(), chipRow, sp(), help, gear);

    this.batteryDetail.innerHTML = "";
    layout.popover("battery", battery, this.batteryDetail);
    layout.popover("legend", hz, legend);
    this.settings.append(h("h4", "", "settings and performance"), this.stats, this.rec);
    layout.popover("settings", gear, this.settings);
    const dp = h("div"); dp.innerHTML = `<h4>signal delay</h4><div>one way: <b class="dv">off</b></div><input type="range" min="0" max="5" step="0.1" value="0" style="width:100%"><div class="presets" style="display:flex;gap:6px;margin-top:6px"></div><div class="dim" style="margin-top:6px;font-size:11px">Commands reach the rover this late and what you see (the video, the rover's pose, the map) is this old, so a command shows its effect after twice this. The cyan ghost and path show where the rover should be when a command issued now arrives (a flat-ground estimate).</div><h4 style="margin-top:8px">cruise control</h4><button class="act cr">cruise at 1.25 km/h (X)</button>`;
    const range = dp.querySelector("input")!, dv = dp.querySelector(".dv")!, presets = dp.querySelector(".presets")!;
    for (const [label, v] of [["off", 0], ["0.5 s", 0.5], ["1.3 s Moon", 1.3], ["3 s", 3]] as [string, number][]) { const b = h("button", "act", label); b.style.marginTop = "0"; b.addEventListener("click", () => on.setDelay(v)); presets.append(b); }
    range.addEventListener("input", () => on.setDelay(Number(range.value))); dp.querySelector(".cr")!.addEventListener("click", () => on.toggleCruise());
    this.delayUi = { range, dv };
    layout.popover("delay", delay, dp); delay.addEventListener("click", () => layout.togglePop("delay"));
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
  /** the one-way delay in seconds (0 = off) */
  setDelay(s: number) { this.delayChip.textContent = s > 0 ? `delay ${s.toFixed(1)} s` : "delay off"; this.delayChip.dataset.level = s > 0 ? "on" : "off"; this.delayUi.dv.textContent = s > 0 ? `${s.toFixed(1)} s (round trip ${(2 * s).toFixed(1)} s)` : "off"; if (document.activeElement !== this.delayUi.range) this.delayUi.range.value = String(s); }
  setCruise(on: boolean) { this.chips.cruise.classList.toggle("hidden", !on); this.chips.cruise.dataset.level = on ? "on" : "off"; this.chips.cruise.textContent = "cruise 1.25 km/h"; }
  setRecording(on: boolean) { this.rec.textContent = on ? "stop and show the log (L)" : "record a performance log (L)"; }
}
