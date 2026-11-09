# al-maha lunar simulation (browser)

A static web app: three.js for rendering, Rapier (WASM) for physics, the rover model exported from the CAD. Spec and status: [`../docs/sim-spec.md`](../docs/sim-spec.md).

```
cd sim
npm install
npm run dev        # http://localhost:5173
npm run build      # static site in sim/dist (GitHub Pages: .github/workflows/pages.yml)
```

The model and its physical data are generated, not hand-written: `../.venv/bin/python ../hardware/sim/export_sim.py` writes `public/rover.glb` and `public/rover.json` from the CAD.

## Controls
| | keyboard | gamepad |
|---|---|---|
| drive | W / S, arrow up / down | left stick up / down |
| steer (skid) | A / D, arrow left / right | left stick left / right |
| brake | Space | |
| mast pan | Q / E | right stick left / right |
| mast tilt | R / F | right stick up / down |

## URL options
- `?still=1&cam=x,y,z,tx,ty,tz` pauses the physics and sets a fixed camera (metres, glTF axes: Y up): for screenshots.
- `?test=1` runs a scripted check without rendering (settle, drive, brake, spin, mast) and writes the numbers into `<pre id="test">`; read it with `chrome --headless --dump-dom`.
