/** touch: two virtual sticks (left: drive and steer, right: mast pan and tilt) and two buttons, shown when the primary pointer is coarse (a phone or tablet) or with ?touch=1 */
export function touchSticks(on: { upright: () => void; cycleCamera: () => void; toggleHazard: () => void }) {
  const out = { drive: [0, 0], mast: [0, 0] };
  const R = 60;
  const make = (side: "left" | "right", key: "drive" | "mast") => {
    const base = document.createElement("div"), knob = document.createElement("div");
    base.style.cssText = `position:fixed;${side}:24px;bottom:24px;width:${2 * R}px;height:${2 * R}px;border-radius:50%;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.3);touch-action:none`;
    knob.style.cssText = `position:absolute;left:${R - 22}px;top:${R - 22}px;width:44px;height:44px;border-radius:50%;background:rgba(255,255,255,.45);pointer-events:none`;
    base.appendChild(knob); document.body.appendChild(base);
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
    const b = document.createElement("button"); b.textContent = label;
    b.style.cssText = `position:fixed;left:50%;transform:translateX(-50%);bottom:${bottom}px;padding:8px 14px;border-radius:8px;background:rgba(255,255,255,.15);color:#fff;border:1px solid rgba(255,255,255,.3);font:13px system-ui`;
    b.addEventListener("click", fn); document.body.appendChild(b);
  };
  mk("stand upright", 24, on.upright);
  mk("camera view", 64, on.cycleCamera);
  mk("hazard", 104, on.toggleHazard);
  return out;
}
