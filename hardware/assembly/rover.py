"""al-maha full assembly: every modelled part in one place, a STEP file, and rendered views.

Collects the parts of body.py, interior.py, frame.py, arms.py, differential.py, mast.py, wheel.py and motor.py into one
colour-coded assembly (rover frame: X forward, Y left, Z up, origin on the ground under the axle midpoint). Renders orthographic
views with a small painter's-algorithm shader (no GPU needed) to docs/images/rover-assembly.png, including two sectioned
close-ups of the left pivot (shaft, sleeve and bushings, rail, housing boss, link plate boss).

Run:  .venv/bin/python hardware/assembly/rover.py
Out:  hardware/assembly/out/rover_assembly.step (not tracked: large), docs/images/rover-assembly.png
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
for d in ("body", "chassis", "suspension", "mast", "wheel", "drive"):
    sys.path.insert(0, str(HERE.parent / d))
import body as B           # noqa: E402
import interior as I       # noqa: E402
import frame as F          # noqa: E402
import arms as A           # noqa: E402
import differential as D   # noqa: E402
import mast as MAST        # noqa: E402
import wheel as W          # noqa: E402
import motor as M          # noqa: E402
from build123d import Box, Compound, Pos, Rot, export_step  # noqa: E402

COLORS = {
    "panels": (178, 184, 190), "frame": (96, 102, 112), "frame upper": (96, 102, 112), "bushings": (150, 155, 160), "pivot standoffs": (236, 205, 90),
    "solar pieces": (22, 32, 62), "wheels": (74, 78, 86), "motors": (196, 122, 62), "link plates": (118, 130, 150),
    "differential": (205, 180, 80), "differential housing": (160, 170, 182), "mast": (214, 217, 222), "camera": (30, 30, 34),
    "battery": (70, 140, 80), "electronics": (50, 100, 180), "BMS": (30, 110, 90), "fuses": (200, 64, 52), "bus bar": (190, 150, 50),
    "switch": (60, 60, 64), "bearings": (225, 225, 230), "wheel hardware": (110, 112, 120),
    "pivot shaft": (40, 150, 165), "pivot boss": (150, 110, 190),
    "controller": (30, 140, 90), "motor drivers": (30, 70, 160), "converters": (140, 70, 170), "charger": (210, 120, 50),
}
LEGEND_NAMES = {
    "frame": "20 x 40 rail and cross rails", "bearings": "sleeve and bushings", "pivot shaft": "shaft and stub", "link plates": "link plate",
    "pivot boss": "link plate boss", "differential housing": "differential housing, bosses, lugs", "differential": "gears and pin",
    "panels": "side panel", "controller": "Raspberry Pi Zero 2 W", "motor drivers": "motor drivers (MC33926 carriers)", "converters": "5 V and 6 V converters (D24V22Fx)",
    "charger": "solar charge module (box)", "battery": "battery pack (box)", "BMS": "BMS (box)", "fuses": "4-way fuse block", "bus bar": "power node (box)", "switch": "master switch",
}


def collect():
    """[(group, name, shape)] for everything modelled."""
    items = []
    add = lambda g, n, s: items.append((g, n, s))
    cav = I.cavity()
    add("panels", "shell", I.shell(cav))
    for i, sp in enumerate(I.side_panels(cav)):
        add("panels", f"side panel {i}", sp)
    members = F.build()
    for n, s in members.items():
        add("frame upper" if n.startswith(("top", "mid", "post", "differential cross")) else "frame", n, s)
    bearings = F.bushings()
    for i, p in enumerate(bearings):
        add("bearings", f"bearing {i}", p)
    for n, s in F.standoffs().items():
        add("pivot standoffs", n, s)
    for i, c in enumerate(B.cells()):
        add("solar pieces", f"piece {i}", c)

    fixed_m, rot_m, _ = M.build_parts()
    for sy in (1, -1):
        arm, wheels, motors = A.side(sy)
        tag = "L" if sy > 0 else "R"
        for n, s in arm.items():
            add("link plates", f"{n} {tag}", s)
        for n, s in wheels.items():
            add("wheels", f"{n} {tag}", s)
        for n, s in motors.items():
            add("motors", f"{n} {tag}", s)
        for sx in (1, -1):
            place = Pos(sx * B.WHEELBASE / 2, sy * B.TRACK / 2, B.HUB_Z) * Rot(-sy * 90, 0, 0)
            for n, s in rot_m.items():
                add("wheel hardware", f"{n} {'F' if sx > 0 else 'R'}{tag}", place * s)
    parts = D.build()
    for n, s in parts.items():
        add("differential housing" if n == "housing" else "differential", n, Pos(0, 0, A.PIVOT_Z) * s)
    for n, s in MAST.parts().items():
        add("camera" if n == "camera" else "mast", n, s)
    placed = I.placed_parts()
    for n, s in placed.items():
        if n.startswith("keep-out"):
            continue
        g = ("battery" if "battery" in n else "BMS" if "BMS" in n else "fuses" if "fuse" in n else "bus bar" if "bus bar" in n
             else "switch" if "switch" in n else "charger" if "charge" in n else "controller" if "controller" in n else "motor drivers" if "driver" in n
             else "converters" if ("converter" in n or "regulator" in n) else "electronics")
        add(g, n, s)
    return items


def mesh(shape, tol=0.4, ang=0.4):
    v, t = shape.tessellate(tol, ang)
    return np.array([(p.X, p.Y, p.Z) for p in v], dtype=float), np.array(t, dtype=int)


def render(meshes, azim, elev, size, hide=(), label=None, zoom=1.0, center=None, legend=(), legend_left=False, shift=0, legend_cols=1):
    """Orthographic z-buffer render, flat shaded, two-sided. azim: camera angle about Z from +X toward +Y, elev above the horizon."""
    a, e = math.radians(azim), math.radians(elev)
    d = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])      # toward the camera
    right = np.array([-math.sin(a), math.cos(a), 0.0])
    up = np.cross(d, right)
    light = np.array([0.35, 0.55, 0.75])
    light = light / np.linalg.norm(light)               # in camera axes (right, up, toward camera)
    W_, H_ = size
    ss = 2
    sel = [(g, v, t, col) for g, v, t, col in meshes if g not in hide]
    allv = np.vstack([v for g, v, t, col in sel])
    if center is None:
        center = (allv.min(axis=0) + allv.max(axis=0)) / 2
    proj = lambda v: np.stack([(v - center) @ right, (v - center) @ up, (v - center) @ d], axis=1)
    p = proj(allv)
    scale = min(W_ * 0.92 / (p[:, 0].max() - p[:, 0].min()), H_ * 0.92 / (p[:, 1].max() - p[:, 1].min())) * zoom * ss
    w, h = W_ * ss, H_ * ss
    zbuf = np.full((h, w), -1e18)
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:] = (248, 248, 245)
    for g, v, t, col in sel:
        pv = proj(v)
        px = np.stack([pv[:, 0] * scale + w / 2, h / 2 - shift * ss - pv[:, 1] * scale, pv[:, 2]], axis=1)
        tri = px[t]
        nrm = np.cross(pv[t][:, 1] - pv[t][:, 0], pv[t][:, 2] - pv[t][:, 0])
        nl = np.linalg.norm(nrm, axis=1)
        nl[nl == 0] = 1
        nrm = nrm / nl[:, None]
        shade = 0.30 + 0.70 * np.abs(nrm @ light)
        for k in range(len(t)):
            (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = tri[k]
            xmin, xmax = int(max(math.floor(min(x0, x1, x2)), 0)), int(min(math.ceil(max(x0, x1, x2)), w - 1))
            ymin, ymax = int(max(math.floor(min(y0, y1, y2)), 0)), int(min(math.ceil(max(y0, y1, y2)), h - 1))
            if xmax < xmin or ymax < ymin:
                continue
            den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
            if abs(den) < 1e-9:
                continue
            xs = np.arange(xmin, xmax + 1) + 0.5
            ys = np.arange(ymin, ymax + 1) + 0.5
            X, Y = np.meshgrid(xs, ys)
            l0 = ((y1 - y2) * (X - x2) + (x2 - x1) * (Y - y2)) / den
            l1 = ((y2 - y0) * (X - x2) + (x0 - x2) * (Y - y2)) / den
            l2 = 1 - l0 - l1
            inside = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
            if not inside.any():
                continue
            Z = l0 * z0 + l1 * z1 + l2 * z2
            zb = zbuf[ymin:ymax + 1, xmin:xmax + 1]
            upd = inside & (Z > zb)
            if upd.any():
                zb[upd] = Z[upd]
                img[ymin:ymax + 1, xmin:xmax + 1][upd] = tuple(int(c * shade[k]) for c in col)
    im = Image.fromarray(img).resize((W_, H_), Image.LANCZOS)
    if label:
        t = ImageDraw.Draw(im)
        f = ImageFont.load_default()
        for p_ in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc"):
            try:
                f = ImageFont.truetype(p_, 17)
                break
            except OSError:
                continue
        t.text((10, 8), label, fill=(30, 30, 30), font=f)
        f2 = ImageFont.truetype(f.path, 14) if hasattr(f, "path") else f
        per = math.ceil(len(legend) / legend_cols)
        for k, (name, col) in enumerate(legend):
            colk, rowk = divmod(k, per)
            y0 = H_ - 22 - 20 * (per - 1 - rowk)
            x0 = (12 if legend_left else W_ - 270 * legend_cols) + colk * 270
            t.rectangle((x0, y0, x0 + 16, y0 + 13), fill=tuple(col), outline=(60, 60, 60))
            t.text((x0 + 24, y0 - 1), name, fill=(30, 30, 30), font=f2)
    return im


def pivot_detail(items, region, skip=()):
    """Left-side pivot parts clipped to a box (x0, x1, y0, y1, z0, z1): the shaft, bosses, sleeve and bushings, rail, differential and
    cross rails. Each part is cut by the box, so the cut faces are closed solids. Returns [(group, shape)]."""
    x0, x1, y0, y1, z0, z1 = region
    box = Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)
    keep = lambda g, n: (
        (g == "frame" and (n.startswith("bottom side L") or n.startswith("differential cross") or n.startswith("mid side L") or n.startswith("bottom end cross")))
        or (g == "bearings" and n == "bearing 0")
        or (g in ("differential", "differential housing"))
        or (g == "link plates" and n.endswith(" L") and n.split()[0] in ("plate", "boss", "shaft"))
        or (g == "panels" and n == "side panel 0"))
    out = []
    for g, n, sh in items:
        if not keep(g, n) or n in skip:
            continue
        try:
            c = sh & box
            if c.volume < 1e-3:
                continue
        except Exception:
            continue
        gg = "pivot shaft" if (g == "link plates" and n.startswith("shaft")) else "pivot boss" if (g == "link plates" and n.startswith("boss")) else g
        out.append((gg, c))
    return out


def main():
    items = collect()
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    comp = Compound([s for g, n, s in items], label="al-maha")
    export_step(comp, str(out / "rover_assembly.step"))
    bb = comp.bounding_box()
    print(f"assembly: {len(items)} parts; bounding box x {bb.min.X:.0f}..{bb.max.X:.0f}, y {bb.min.Y:.0f}..{bb.max.Y:.0f}, z {bb.min.Z:.0f}..{bb.max.Z:.0f}")
    meshes = []
    ntri = 0
    for g, n, s in items:
        v, t = mesh(s)
        meshes.append((g, v, t, COLORS[g]))
        ntri += len(t)
    print(f"triangles: {ntri}")
    size = (760, 560)
    views = [
        ("Exterior, front left", 35, 22, (), 0.86),
        ("Exterior, rear right", 215, 22, (), 0.86),
        ("Side (right), exterior", -90, 0, (), 0.95),
        ("Frame and interior: panels and cells hidden", 35, 25, ("panels", "solar pieces", "pivot standoffs"), 0.86),
        ("Top, panels and mast hidden", 90, 89.5, ("panels", "solar pieces", "pivot standoffs", "mast", "camera"), 0.9),
        ("Front", 0, 0, (), 1.0),
    ]
    imgs = []
    for lab, az, el, hide, zm in views:
        # side views: the camera azimuth about Z measured from +X: for the side view we look along -Y from +Y: azim 90
        imgs.append(render(meshes, az, el, size, hide=hide, label=lab, zoom=zm))
    # ---- pivot detail panels (left side), sectioned ----
    def detail(region, az, el, label, zoom=1.0, skip=(), legend_left=False):
        parts = pivot_detail(items, region, skip)
        ms = []
        for g, sh in parts:
            v, t = mesh(sh)
            ms.append((g, v, t, COLORS[g]))
        seen = []
        for g, v, t, col in ms:
            if g not in [x[0] for x in seen]:
                seen.append((g, col))
        leg = [(LEGEND_NAMES.get(g, g), col) for g, col in seen]
        return render(ms, az, el, size, label=label, zoom=zoom, legend=leg, legend_left=legend_left)
    zc = A.PIVOT_Z
    imgs.append(detail((-72, 72, 0, 165, 100, zc), 0, 90, "Pivot detail, left: section at the shaft axis (z 145.7), from above", 0.98, legend_left=True))
    imgs.append(detail((0, 72, 0, 122, 100, 200), 150, 30, "Pivot detail, left: section at x = 0 from the rear left (panel and link plate removed)", 0.9,
                       skip=("side panel 0", "plate L", "boss L", "mid side L")))
    def bay(az, el, label, zoom, shift=0):
        hide = ("panels", "solar pieces", "pivot standoffs", "mast", "camera", "wheels", "motors", "link plates", "wheel hardware", "frame upper", "bearings", "differential")
        present = []
        for g, v, t, col in meshes:
            if g not in hide and g not in [x[0] for x in present]:
                present.append((g, col))
        keep = ("controller", "motor drivers", "converters", "charger", "battery", "BMS", "fuses", "bus bar", "switch", "frame", "differential housing")
        leg = [(LEGEND_NAMES.get(g, g), col) for g, col in present if g in keep]
        return render(meshes, az, el, size, hide=hide, label=label, zoom=zoom, legend=leg, legend_left=False, shift=shift, legend_cols=2)
    imgs.append(bay(90, 89.5, "Electronics bay from above (upper frame, panels, mast and wheels hidden)", 0.92, shift=40))
    imgs.append(bay(40, 52, "Electronics bay from the front left, raised view", 0.85, shift=40))
    cols, rows = 2, 5
    gap = 12
    sheet = Image.new("RGB", (cols * size[0] + (cols + 1) * gap, rows * size[1] + (rows + 1) * gap + 34), (255, 255, 255))
    t = ImageDraw.Draw(sheet)
    t.text((gap, 8), "al-maha: every modelled part (colours by group; simplified shapes; nothing built)", fill=(30, 30, 30), font=ImageFont.load_default())
    for k, im in enumerate(imgs):
        r, c = divmod(k, cols)
        sheet.paste(im, (gap + c * (size[0] + gap), 34 + gap + r * (size[1] + gap)))
    dst = HERE.parent.parent / "docs" / "images"
    dst.mkdir(parents=True, exist_ok=True)
    sheet.save(dst / "rover-assembly.png")
    print("wrote", dst / "rover-assembly.png", sheet.size)


if __name__ == "__main__":
    main()
