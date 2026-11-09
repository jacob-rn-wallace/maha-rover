import type { Controls } from "./physics";
import { touchSticks } from "./touch";

/** what the keys and touch buttons trigger (main.ts owns the things they act on) */
export interface Actions { upright(): void; cycleCamera(): void; cycleMap(): void; toggleLog(): void; toggleHazard(): void }

const autoDrive = (new URLSearchParams(location.search).get("autodrive") ?? "").split(",").map(Number).filter(isFinite) as number[];      // ?autodrive=from,to: full throttle between those seconds after load (for scripted screenshots)
const t0 = performance.now();

/** keyboard, gamepad and touch; `scripted` returns the controls of a scripted run (the benchmark) while one is on, and null otherwise */
export function setupInput(coarse: boolean, on: Actions, scripted: () => Controls | null) {
  const touch = coarse ? touchSticks(on) : undefined;
  const keys = new Set<string>();
  addEventListener("keydown", (e) => { keys.add(e.code); if (e.code === "Space") e.preventDefault(); if (e.repeat) return; if (e.code === "KeyT") on.upright(); if (e.code === "KeyC") on.cycleCamera(); if (e.code === "KeyM") on.cycleMap(); if (e.code === "KeyL") on.toggleLog(); if (e.code === "KeyH") on.toggleHazard(); });
  addEventListener("keyup", (e) => keys.delete(e.code));
  addEventListener("blur", () => keys.clear());
  const k = (...c: string[]) => (c.some((x) => keys.has(x)) ? 1 : 0);
  return {
    read(): Controls {
      const s = scripted(); if (s) return s;
      let throttle = k("KeyW", "ArrowUp") - k("KeyS", "ArrowDown"), turn = k("KeyD", "ArrowRight") - k("KeyA", "ArrowLeft");
      let pan = k("KeyQ") - k("KeyE"), tilt = k("KeyR") - k("KeyF");
      const gp = navigator.getGamepads?.().find((g) => g);
      if (gp) {
        const dz = (x: number) => (Math.abs(x) < 0.12 ? 0 : x);
        throttle += -dz(gp.axes[1] ?? 0); turn += dz(gp.axes[0] ?? 0);
        pan += -dz(gp.axes[2] ?? 0); tilt += -dz(gp.axes[3] ?? 0);
      }
      if (touch) { throttle += touch.drive[1]; turn += touch.drive[0]; pan += -touch.mast[0]; tilt += touch.mast[1]; }
      if (autoDrive.length === 2 && performance.now() - t0 < autoDrive[1] * 1000 && performance.now() - t0 > autoDrive[0] * 1000) throttle += 1;
      const cl = (x: number) => Math.max(-1, Math.min(1, x));
      return { throttle: cl(throttle), turn: cl(turn), pan: cl(pan), tilt: cl(tilt), brake: keys.has("Space") };
    },
  };
}
