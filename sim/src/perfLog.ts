/** Performance log: one sample per frame, written out as a JSON file the owner can hand over.
 *  Recording starts with the L key or with ?bench=1 (the scripted benchmark, main.ts) and a Download button appears when it stops.
 *  The file holds: the machine (browser, GPU name, screen and window, pixel ratio, build), the settings, a per-second summary and the frames
 *  (columns named in `frameColumns`), plus the physics worker's step time and snapshot rate. Frame times are the gaps between animation frames (what the player sees),
 *  `jsMs` the main thread's own work up to the main render call, `drawCalls` and `triangles` those of the main view. Nothing leaves the machine unless the file is sent. */
export interface FrameSample { t: number; dt: number; jsMs: number; ratio: number; drawCalls: number; triangles: number; x: number; z: number; stepMs: number; snapHz: number; }

const COLUMNS = ["t_s", "frame_ms", "js_ms", "pixel_ratio", "draw_calls", "triangles", "x_m", "z_m", "physics_step_ms", "snapshot_hz"] as const;

export class PerfLog {
  private frames: number[][] = [];
  private t0 = 0;
  recording = false;
  private meta: Record<string, unknown> = {};
  constructor(private info: () => Record<string, unknown>) {}

  start(label: string, settings: Record<string, unknown> = {}) {
    this.frames = []; this.t0 = performance.now(); this.recording = true;
    this.meta = { label, startedAt: new Date().toISOString(), settings, ...this.info() };
  }

  frame(s: FrameSample) {
    if (!this.recording) return;
    this.frames.push([+((performance.now() - this.t0) / 1000).toFixed(3), +(Math.max(0, s.dt) * 1000).toFixed(2), +s.jsMs.toFixed(2), +s.ratio.toFixed(3), s.drawCalls, s.triangles, +s.x.toFixed(2), +s.z.toFixed(2), +s.stepMs.toFixed(3), s.snapHz]);
  }

  get seconds() { return this.recording ? (performance.now() - this.t0) / 1000 : 0; }

  /** stop and return the summary; frames before `skipSeconds` (shader compile, first uploads) are kept in the file but left out of the statistics */
  stop(skipSeconds = 0) {
    this.recording = false;
    const f = this.frames.filter((r) => r[0] >= skipSeconds);
    const ms = f.map((r) => r[1]).sort((a, b) => a - b);
    const pct = (p: number) => ms.length ? ms[Math.min(ms.length - 1, Math.floor(p * ms.length))] : NaN;
    const mean = (i: number) => f.length ? f.reduce((a, r) => a + r[i], 0) / f.length : NaN;
    const secs = new Map<number, { n: number; ms: number; worst: number; js: number }>();
    for (const r of this.frames) { const k = Math.floor(r[0]); const e = secs.get(k) ?? { n: 0, ms: 0, worst: 0, js: 0 }; e.n++; e.ms += r[1]; e.worst = Math.max(e.worst, r[1]); e.js += r[2]; secs.set(k, e); }
    const med = pct(0.5), meanMs = mean(1), std = Math.sqrt(f.reduce((a, r) => a + (r[1] - meanMs) ** 2, 0) / Math.max(1, f.length));
    const span = f.length ? f[f.length - 1][0] - f[0][0] : 0;
    const summary = {
      skippedSeconds: skipSeconds, frames: f.length, seconds: +span.toFixed(1), meanFps: +(f.length / Math.max(span, 1e-6)).toFixed(1),
      frameMs: { mean: +mean(1).toFixed(2), median: pct(0.5), p95: pct(0.95), p99: pct(0.99), worst: ms[ms.length - 1] },
      frameMsStd: +std.toFixed(2), stutterFramesPct: +(100 * f.filter((r) => r[1] > 1.5 * med).length / Math.max(1, f.length)).toFixed(1),      // stutter: frames over 1.5 x the median
      onePercentLowFps: +(1000 / pct(0.99)).toFixed(1), meanJsMs: +mean(2).toFixed(2), meanPixelRatio: +mean(3).toFixed(3), meanDrawCalls: +mean(4).toFixed(0), meanTriangles: +mean(5).toFixed(0),
      physicsStepMs: +mean(8).toFixed(3), snapshotHz: +mean(9).toFixed(0),
    };
    const perSecond = [...secs.entries()].sort((a, b) => a[0] - b[0]).map(([k, e]) => ({ second: k, fps: +(e.n / (e.ms / 1000)).toFixed(1), worstFrameMs: +e.worst.toFixed(1), meanJsMs: +(e.js / e.n).toFixed(1) }));
    return { meta: this.meta, summary, perSecond, frameColumns: COLUMNS, frames: this.frames };
  }
}

export function downloadJson(name: string, data: unknown) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([JSON.stringify(data)], { type: "application/json" }));
  a.download = name; document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 10000);
}
