// Real-time headless screenshot through the DevTools protocol (the --virtual-time-budget flag does not wait for workers):
//   node tests/cdp-shot.mjs out.png "query" [seconds] [width height] [keys]
// keys: e.g. "w:3" holds W for 3 s before the shot. Prints the HUD text and console errors.
import { spawn } from "node:child_process";
import { writeFileSync, rmSync } from "node:fs";
const [out, query = "", secs = "20", w = "1280", h = "800", keys = ""] = process.argv.slice(2);
const PROFILE_DIR = "/tmp/cdp-profile-" + process.pid;      // removed at exit: each profile grows to about 100 MB
const chrome = spawn("google-chrome", ["--headless=new", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--no-sandbox", `--window-size=${w},${h}`, "--remote-debugging-port=9333", "--user-data-dir=" + PROFILE_DIR, "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let list;
for (let i = 0; i < 50; i++) { try { list = await (await fetch("http://127.0.0.1:9333/json")).json(); if (list.length) break; } catch {} await sleep(200); }
const ws = new WebSocket(list.find((t) => t.type === "page").webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0; const pending = new Map(); const logs = [];
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pending.has(d.id)) { pending.get(d.id)(d.result); pending.delete(d.id); } else if (d.method === "Runtime.consoleAPICalled" && ["error", "warning"].includes(d.params.type)) logs.push(d.params.args.map((a) => a.value ?? a.description).join(" ")); else if (d.method === "Runtime.exceptionThrown") logs.push("EXC " + d.params.exceptionDetails.text + " " + (d.params.exceptionDetails.exception?.description ?? "")); };
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await send("Runtime.enable"); await send("Page.enable");
await send("Emulation.setDeviceMetricsOverride", { width: +w, height: +h, deviceScaleFactor: 1, mobile: false });
await send("Page.navigate", { url: "http://127.0.0.1:5173/?" + query });
await sleep(+secs * 1000);
const PROFILE = process.env.PROFILE;
if (PROFILE) { await send("Profiler.enable"); await send("Profiler.start"); await sleep(+PROFILE * 1000); const prof = (await send("Profiler.stop")).profile; const self = new Map(); const dt = prof.timeDeltas; const byId = new Map(prof.nodes.map((n) => [n.id, n])); prof.samples.forEach((id, i) => { const n = byId.get(id), key = n.callFrame.functionName + " " + n.callFrame.url.split("/").pop() + ":" + n.callFrame.lineNumber; self.set(key, (self.get(key) ?? 0) + dt[i]); }); const tot = [...self.values()].reduce((a, b) => a + b, 0); console.log("PROFILE (self time, % of " + (tot / 1e6).toFixed(1) + " s):"); [...self.entries()].sort((a, b) => b[1] - a[1]).slice(0, 14).forEach(([k, v]) => console.log((100 * v / tot).toFixed(1).padStart(5) + "% " + k)); }
if (keys) { const [k, t] = keys.split(":"); const code = { w: "KeyW", s: "KeyS", d: "KeyD", a: "KeyA" }[k];
  const fire = (type) => send("Runtime.evaluate", { expression: `window.dispatchEvent(new KeyboardEvent('${type}', { code: '${code}', key: '${k}' }))` });
  await fire("keydown"); await sleep(+t * 500); { const m = await send("Runtime.evaluate", { expression: "document.getElementById('hud').innerText.split('\\n').filter(l => /speed|position/.test(l)).join(' | ')", returnByValue: true }); console.log("mid-hold:", m.result.value); } await sleep(+t * 500); await fire("keyup"); await sleep(500); }
const dbg = await send("Runtime.evaluate", { expression: "(() => { const p = window.__phys; if (!p) return 'no phys'; const t = p.bodies.chassis.translation(); return JSON.stringify({ x: +t.x.toFixed(2), y: +t.y.toFixed(2), z: +t.z.toFixed(2), cur: p.wheelCurrent, cut: p.tiltCut }); })()", returnByValue: true }); console.log("phys:", dbg.result.value);
const fx = await send("Runtime.evaluate", { expression: "window.__fx ? JSON.stringify({ gain: window.__fx.gain, metered: window.__fx.metered, stats: window.__fx.stats }) : 'no fx'", returnByValue: true }); console.log("fx:", fx.result.value);
const fr = await send("Runtime.evaluate", { expression: "window.__frames", returnByValue: true }); console.log("frames:", fr.result.value);
if (process.env.DUMPPERF) { const d = await send("Runtime.evaluate", { expression: "JSON.stringify(window.__perfData ?? null)", returnByValue: true }); writeFileSync(process.env.DUMPPERF, d.result.value); }
const hud = await send("Runtime.evaluate", { expression: "document.getElementById('hud').innerText", returnByValue: true });
const shot = await send("Page.captureScreenshot", { format: "png" });
writeFileSync(out, Buffer.from(shot.data, "base64"));
console.log(hud.result.value); if (logs.length) console.log("LOGS:", logs.slice(0, 8).join("\n"));
ws.close(); chrome.kill();
await sleep(500);
rmSync(PROFILE_DIR, { recursive: true, force: true });
process.exit(0);
