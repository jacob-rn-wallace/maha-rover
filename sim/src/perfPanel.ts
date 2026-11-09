import { downloadJson } from "./perfLog";
import { h, type Layout } from "./layout";

/** the panel over the middle of the page that shows a finished recording or benchmark, with a button to download the log file */
export class PerfPanel {
  private el = h("div", "panel");

  constructor(layout: Layout) {
    this.el.style.cssText = "background:rgba(0,0,0,.85);padding:14px 18px;max-width:440px;font:13px/1.5 system-ui;color:#eee;display:none";
    layout.modal.appendChild(this.el);
  }

  hide() { this.el.style.display = "none"; }

  show(name: string, data: { summary: any }, bufferW: number, bufferH: number) {
    const sm = data.summary, stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
    this.el.innerHTML = `<b>${name} finished</b><br>${sm.frames} frames over ${sm.seconds} s: <b>${sm.meanFps} fps</b> mean, ${sm.onePercentLowFps} fps 1% low<br>frame time median ${sm.frameMs.median} ms, 95th percentile ${sm.frameMs.p95} ms, worst ${sm.frameMs.worst} ms<br>main thread ${sm.meanJsMs} ms/frame, physics step ${sm.physicsStepMs} ms, pixel ratio ${sm.meanPixelRatio}, buffer ${bufferW} x ${bufferH}<br><br>`;
    const b = document.createElement("button"); b.textContent = "Download the log file"; b.style.cssText = "padding:6px 12px;margin-right:8px"; b.onclick = () => downloadJson(`almaha-perf-${stamp}.json`, data);
    const c = document.createElement("button"); c.textContent = "Close"; c.style.cssText = "padding:6px 12px"; c.onclick = () => this.hide();
    this.el.append(b, c); this.el.style.display = "block";
  }
}
