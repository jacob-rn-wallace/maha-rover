// Print the headline figures of a performance log written by the sim (L key or ?bench=1):  node tests/bench-summary.mjs bench/almaha-perf-....json [more files]
import { readFileSync } from "node:fs";
for (const f of process.argv.slice(2)) {
  const d = JSON.parse(readFileSync(f, "utf8")), m = d.meta, s = d.summary;
  console.log(`\n== ${f}\n${m.label} ${m.startedAt}, build ${m.build}\n${m.gpu}\nscreen ${m.screen}, window ${m.window}, buffer ${m.canvasAtEnd ?? m.canvas}, dpr ${m.devicePixelRatio}, max ${m.maxPixelsM} Mpx, ${m.cores} cores, worker ${m.physicsInWorker}\n${m.settings?.search ?? ""}`);
  console.log(`${s.frames} frames, ${s.seconds} s (first ${s.skippedSeconds} s skipped): ${s.meanFps} fps mean, 1% low ${s.onePercentLowFps} fps`);
  console.log(`frame ms: mean ${s.frameMs.mean}, median ${s.frameMs.median}, p95 ${s.frameMs.p95}, p99 ${s.frameMs.p99}, worst ${s.frameMs.worst}`);
  console.log(`frame time spread: std ${s.frameMsStd} ms, stutter frames (over 1.5 x median) ${s.stutterFramesPct}%, snapshot underruns ${s.snapshotUnderrunPct ?? "n/a"}%, display ${m.refreshHzAtEnd ?? m.refreshHz ?? "?"} Hz, cap ${m.fpsCap ?? "n/a"}`);
  console.log(`main thread ${s.meanJsMs} ms, physics step ${s.physicsStepMs} ms at ${s.snapshotHz} Hz, pixel ratio ${s.meanPixelRatio}, ${s.meanDrawCalls} draw calls, ${s.meanTriangles} triangles`);
  console.log("per second (fps / worst frame ms):", d.perSecond.map((p) => `${p.second}s ${p.fps}/${p.worstFrameMs}`).join("  "));
}
