/** touch: two virtual sticks (left: drive and steer, right: mast pan and tilt) and two buttons, shown when the primary pointer is coarse (a phone or tablet) or with ?touch=1 */
export function touchSticks(parent: HTMLElement, on: { upright: () => void; toggleCamera: () => void; toggleTelemetry: () => void }) {
  const out = { drive: [0, 0], mast: [0, 0] };
  const R = 50;
  const make = (side: "left" | "right", key: "drive" | "mast") => {
    const base = document.createElement("div"), knob = document.createElement("div");
    base.style.cssText = `position:absolute;${side}:24px;bottom:24px;pointer-events:auto;width:${2 * R}px;height:${2 * R}px;border-radius:50%;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.3);touch-action:none`;
    knob.style.cssText = `position:absolute;left:${R - 22}px;top:${R - 22}px;width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,.45);pointer-events:none`;
    base.appendChild(knob); parent.appendChild(base);
    const set = (e: PointerEvent) => {
      const b = base.getBoundingClientRect();
      let dx = (e.clientX - b.left - R) / R, dy = (e.clientY - b.top - R) / R; const m = Math.hypot(dx, dy); if (m > 1) { dx /= m; dy /= m; }
      out[key] = [dx, -dy]; knob.style.transform = `translate(${dx * (R - 22)}px,${dy * (R - 22)}px)`;
    };
    const end = () => { out[key] = [0, 0]; knob.style.transform = ""; };
    base.addEventListener("pointerdown", (e) => { base.setPointerCapture(e.pointerId); set(e); });
    base.addEventListener("pointermove", (e) => { if (base.hasPointerCapture(e.pointerId)) set(e); });
    base.addEventListener("pointerup", end); base.addEventListener("pointercancel", end);
  };
  make("left", "drive"); make("right", "mast");
  const mk = (label: string, bottom: number, fn: () => void) => {
    const b = document.createElement("button"); b.textContent = label; b.dataset.b = label;
    b.style.cssText = `position:absolute;left:50%;transform:translateX(-50%);bottom:${bottom}px;pointer-events:auto;padding:8px 14px;border-radius:8px;background:rgba(255,255,255,.15);color:#fff;border:1px solid rgba(255,255,255,.3);font:13px system-ui`;
    b.addEventListener("click", fn); parent.appendChild(b);
  };
  mk("stand upright", 24, on.upright);
  mk("camera view", 64, on.toggleCamera);
  mk("panels", 104, on.toggleTelemetry);
  return out;
}
