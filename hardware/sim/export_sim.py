"""Export the al-maha assembly for the browser simulation (sim/): a glTF binary of rigid bodies and a JSON of the joints, masses and camera.

The assembly of hardware/assembly/rover.py is split into the bodies that move relative to each other:
  chassis            frame, panels, cells, electronics, differential housing, mast base and pan housing (everything fixed to the body)
  link L, link R     link plate, boss, shaft, sleeves, the four drive motors' fixed parts, a side gear; revolute about the pivot axis (rover Y)
  wheel FL..RR       wheel and its rotating motor hardware; revolute about the hub axis (rover Y), driven
  mast pan           spindle, tube, sheet bracket, tilt servo; revolute about the vertical mast axis, driven
  camera head        disk, camera box, camera, hat; revolute about the tilt axis (rover Y), driven
The differential couples the two link plates (angle L = -angle R); that is a constraint in the simulation, listed in the JSON.

Frames: the glTF uses Y up, metres: glTF (x, y, z) = (rover X, rover Z, -rover Y) / 1000 (rover: X forward, Y left, Z up, mm, ground at the rim line).
Every body's mesh is stored relative to its joint origin, so a node's rotation is the joint rotation.  The JSON is in glTF axes and metres too.

Run:  .venv/bin/python hardware/sim/export_sim.py
Out:  sim/public/rover.glb, sim/public/rover.json
"""
import json
import math
import struct
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
for d in ("assembly", "mass", "body", "chassis", "suspension", "mast", "wheel", "drive"):
    sys.path.insert(0, str(ROOT / "hardware" / d))
import rover as R        # noqa: E402  (hardware/assembly/rover.py)
import replica as REP    # noqa: E402
import body as B         # noqa: E402
import arms as A         # noqa: E402
import mast as MAST      # noqa: E402
import headb as HB       # noqa: E402

OUT = ROOT / "sim" / "public"
M = 1e-3
CREASE = math.cos(math.radians(35))     # smooth-shading threshold between faces

# ---- joint geometry, rover frame (mm) ----------------------------------------------------------------------------
HX, HY, HZ = B.WHEELBASE / 2, B.TRACK / 2, B.HUB_Z
PIVOT = (0.0, 0.0, A.PIVOT_Z)
PAN = (MAST.TUBE_X, 0.0, 0.0)
TILT = (MAST.TUBE_X, 0.0, MAST.CAM_AXIS_Z)
WHEELS = {f"{'F' if sx > 0 else 'R'}{'L' if sy > 0 else 'R'}": (sx * HX, sy * HY, HZ) for sx in (1, -1) for sy in (1, -1)}

BODIES = {"chassis": (0.0, 0.0, 0.0), "linkL": PIVOT, "linkR": PIVOT, "pan": PAN, "head": TILT, **{f"wheel{k}": v for k, v in WHEELS.items()}}
PARENT = {"chassis": None, "linkL": "chassis", "linkR": "chassis", "pan": "chassis", "head": "pan",
          **{f"wheel{k}": "link" + k[1] for k in WHEELS}}


def body_of(group, name):
    """Which rigid body a part of rover.collect() belongs to."""
    if group == "wheels":
        return "wheel" + name[5] + name[-1]                       # 'wheelF L' -> wheelFL
    if group == "wheel hardware":
        return "wheel" + name[-2:]                                # 'shaft FL' -> wheelFL
    if group in ("motors", "link plates"):
        return "link" + name[-1]
    if group == "differential" and name.startswith("side gear"):
        return "linkL" if "+Y" in name else "linkR"
    if group in ("mast", "camera", "camera module", "GNSS patch", "servos", "pan base", "cable"):
        if name in HB.TILTING:
            return "head"
        if name in ("tube", "bracket", "spindle", "tilt servo"):
            return "pan"
    return "chassis"


def to_gl(p):
    """rover mm -> glTF metres"""
    p = np.asarray(p, dtype=float)
    return np.stack([p[..., 0], p[..., 2], -p[..., 1]], axis=-1) * M


def mesh_of(shape, tol=0.4, ang=0.4):
    v, t = shape.tessellate(tol, ang)
    return np.array([(p.X, p.Y, p.Z) for p in v], dtype=float), np.array(t, dtype=int)


def smooth(v, t):
    """Weld vertices by position, then average face normals within the crease angle: returns (verts, normals, indices)."""
    key = np.round(v / 1e-3).astype(np.int64)
    _, inv = np.unique(key, axis=0, return_inverse=True)
    inv = inv.ravel()
    tri = inv[t]                                                       # welded indices per triangle
    p0, p1, p2 = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    fn = np.cross(p1 - p0, p2 - p0)
    area = np.linalg.norm(fn, axis=1)
    ok = area > 1e-12
    tri, fn, t = tri[ok], fn[ok] / area[ok, None], t[ok]
    faces_at = {}
    for fi, tr in enumerate(tri):
        for c in tr:
            faces_at.setdefault(int(c), []).append(fi)
    out_v, out_n, out_i, cache = [], [], [], {}
    for fi, tr in enumerate(tri):
        for k in range(3):
            c = int(tr[k])
            n = np.zeros(3)
            for fj in faces_at[c]:
                if fn[fj] @ fn[fi] > CREASE:
                    n += fn[fj]
            n /= np.linalg.norm(n) or 1.0
            kk = (c, tuple(np.round(n, 2)))
            if kk not in cache:
                cache[kk] = len(out_v)
                out_v.append(v[t[fi, k]])
                out_n.append(n)
            out_i.append(cache[kk])
    return np.array(out_v), np.array(out_n), np.array(out_i, dtype=np.uint32)


# (base colour, metallic, roughness): the groups of rover.py; bare aluminium, dark cells, black plastic and so on
def material(group):
    r, g, b = R.COLORS.get(group, (150, 150, 150))
    metal = {"panels": 0.85, "frame": 0.8, "frame upper": 0.8, "mast": 0.8, "pan base": 0.7, "link plates": 0.7, "differential": 0.9,
             "differential housing": 0.7, "pivot shaft": 0.9, "bearings": 0.9, "servos": 0.2, "motors": 0.6, "solar pieces": 0.4}.get(group, 0.15)
    rough = {"solar pieces": 0.25, "wheels": 0.65, "camera": 0.5}.get(group, 0.45)
    return ((r / 255) ** 2.2, (g / 255) ** 2.2, (b / 255) ** 2.2, 1.0), metal, rough


def mass_props(v, t, mass):
    """Centre of mass and inertia tensor (about the COM, kg m2) of a closed mesh, uniform density, scaled to `mass`.  v in metres."""
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    vol6 = np.einsum("ij,ij->i", a, np.cross(b, c))
    vol = vol6.sum() / 6.0
    if abs(vol) < 1e-15:
        return None
    com = ((a + b + c) * (vol6 / 24.0)[:, None]).sum(0) / vol
    f = lambda x: (x[:, :, None] * x[:, None, :])
    # integral of x x^T over a tetrahedron (0, a, b, c): vol/20 * (sum_i p_i p_i^T + (sum p)(sum p)^T)
    s = a + b + c
    tet = (vol6 / 6.0 / 20.0)[:, None, None] * (f(a) + f(b) + f(c) + f(s))
    C = tet.sum(0) * np.sign(vol)
    C = C - abs(vol) * np.outer(com, com)
    I = np.trace(C) * np.eye(3) - C
    return com, I * (mass / abs(vol))


def main():
    items = R.collect()
    per = {k: {} for k in BODIES}            # body -> material group -> [mesh pieces (in joint-origin frame, glTF metres)]
    raw = {k: [] for k in BODIES}            # body -> triangles for the inertia
    for g, n, s in items:
        b = body_of(g, n)
        v, t = mesh_of(s)
        if len(t) == 0:
            continue
        v = to_gl(v - np.array(BODIES[b]))
        per[b].setdefault(g, []).append((v, t))
        raw[b].append((v, t))

    # --- masses (replica.py, the same list as docs/replica-mass.md), placed in the bodies by the same rules ---
    mass = {k: 0.0 for k in BODIES}
    mom = {k: np.zeros(3) for k in BODIES}
    allitems = REP.collect()
    m_all, xc, zc, _, _ = MAST.cg_and_moment()
    head_pts = []
    rot = MAST.parts()
    cen = lambda n: rot[n].center()
    for n, m_ in (("enclosure", MAST.ENCLOSURE_KG), ("antenna hat", rot["antenna hat"].volume / 1e6 * MAST.AL_G_CM3), ("GNSS patch", HB.GNSS_PATCH_KG),
                  ("disk", rot["disk"].volume / 1e6 * MAST.AL_G_CM3), ("camera body", MAST.CAMBODY_KG), ("lens", HB.LENS_KG),
                  ("CSI extender Tx", HB.TX_BOARD_KG), ("cable gland", 0.005)):
        head_pts.append((m_, cen(n)))
    for n in MAST.PRINTED_HEAD:
        head_pts.append((MAST.H.shell_mass(rot[n]), cen(n)))
    mh = sum(p[0] for p in head_pts)
    ch = sum(p[0] * np.array([p[1].X, p[1].Y, p[1].Z]) for p in head_pts) / mh
    cm = np.array([xc, 0.0, zc])
    # the turning pan body: extrusion, sheet bracket, tilt servo, spindle; the rest of the mast mass (base plate, pan servo, housing, bearings, hardware) is fixed to the chassis
    pan_pts = [((MAST.TUBE_Z1 - MAST.TUBE_Z0) / 1000.0 * MAST.EXT_KG_PER_M, cen("tube")), (rot["bracket"].volume / 1e6 * MAST.AL_G_CM3, cen("bracket")),
               (MAST.H.SERVO_MASS, cen("tilt servo")), (MAST._BASE_INFO["al_kg"], cen("spindle"))]
    vec = lambda c: np.array([c.X, c.Y, c.Z])
    pan_m = sum(p[0] for p in pan_pts)
    pan_c = sum(p[0] * vec(p[1]) for p in pan_pts) / pan_m
    base_m = m_all - mh - pan_m
    base_c = (m_all * cm - mh * ch - pan_m * pan_c) / base_m
    for g, n, m_, p in allitems:
        if g == "mast, head and camera":
            for b, mm, pp in (("head", mh, ch), ("pan", pan_m, pan_c), ("chassis", base_m, base_c)):
                mass[b] += mm
                mom[b] += mm * np.asarray(pp)
            continue
        if g == "wheels":
            b = "wheel" + n[5] + n[-1]
        elif g == "drive motors":
            b = "link" + n[-1]
        elif g == "link plates, sleeves, shafts":
            b = "link" + n[-1]
        else:
            b = "chassis"
        mass[b] += m_
        mom[b] += m_ * np.asarray(p)
    total = sum(mass.values())

    # --- glTF binary ---
    bin_ = bytearray()
    views, accs, meshes, mats, nodes = [], [], [], [], []
    mat_idx = {}

    def add_buf(arr, target):
        while len(bin_) % 4:
            bin_.append(0)
        views.append({"buffer": 0, "byteOffset": len(bin_), "byteLength": arr.nbytes, "target": target})
        bin_.extend(arr.tobytes())
        return len(views) - 1

    def add_acc(arr, target, ctype, typ, minmax=False):
        vi = add_buf(arr, target)
        a = {"bufferView": vi, "componentType": ctype, "count": len(arr), "type": typ}
        if minmax:
            a["min"], a["max"] = arr.min(0).tolist(), arr.max(0).tolist()
        accs.append(a)
        return len(accs) - 1

    stats = {}
    for b in BODIES:
        prims = []
        ntri = 0
        for g, pieces in per[b].items():
            v = np.concatenate([p[0] for p in pieces])
            off = np.cumsum([0] + [len(p[0]) for p in pieces[:-1]])
            t = np.concatenate([p[1] + o for p, o in zip(pieces, off)])
            vv, nn, ii = smooth(v, t)
            if g not in mat_idx:
                col, me, ro = material(g)
                mats.append({"name": g, "pbrMetallicRoughness": {"baseColorFactor": list(col), "metallicFactor": me, "roughnessFactor": ro}})
                mat_idx[g] = len(mats) - 1
            prims.append({"attributes": {"POSITION": add_acc(vv.astype("<f4"), 34962, 5126, "VEC3", True), "NORMAL": add_acc(nn.astype("<f4"), 34962, 5126, "VEC3")},
                          "indices": add_acc(ii.astype("<u4"), 34963, 5125, "SCALAR"), "material": mat_idx[g]})
            ntri += len(ii) // 3
        meshes.append({"name": b, "primitives": prims})
        stats[b] = ntri
    order = list(BODIES)
    for b in order:
        o = to_gl(np.array(BODIES[b]))
        par = PARENT[b]
        if par:
            o = o - to_gl(np.array(BODIES[par]))
        nodes.append({"name": b, "mesh": order.index(b), "translation": [float(x) for x in o]})
    for i, b in enumerate(order):
        if PARENT[b]:
            nodes[order.index(PARENT[b])].setdefault("children", []).append(i)
    gltf = {"asset": {"version": "2.0", "generator": "al-maha hardware/sim/export_sim.py"}, "scene": 0,
            "scenes": [{"nodes": [0]}], "nodes": nodes, "meshes": meshes, "materials": mats, "accessors": accs,
            "bufferViews": views, "buffers": [{"byteLength": len(bin_)}]}
    js = json.dumps(gltf, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    while len(bin_) % 4:
        bin_.append(0)
    glb = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bin_)) + struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(bin_), 0x004E4942) + bytes(bin_)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "rover.glb").write_bytes(glb)

    # --- JSON: joints, masses, camera ---
    bodies = {}
    for b in order:
        com_rover = mom[b] / mass[b] if mass[b] else np.array(BODIES[b])
        com = to_gl(com_rover - np.array(BODIES[b])).tolist()
        entry = {"parent": PARENT[b], "origin_m": to_gl(np.array(BODIES[b])).tolist(), "mass_kg": round(mass[b], 5), "com_m": [round(x, 5) for x in com], "triangles": stats[b]}
        verts = [p for pc in raw[b] for p in [pc]]
        if verts:
            v = np.concatenate([p[0] for p in verts])
            off = np.cumsum([0] + [len(p[0]) for p in verts[:-1]])
            t = np.concatenate([p[1] + o for p, o in zip(verts, off)])
            mp = mass_props(v, t, mass[b])
            if mp:
                w = np.linalg.eigvalsh(mp[1])
                entry["mesh_com_m"] = [round(x, 5) for x in mp[0].tolist()]
                entry["inertia_principal_kgm2"] = [float(f"{x:.4g}") for x in w]
        bodies[b] = entry
    hx, hy, hz = HX * M, HY * M, HZ * M
    cam_x = HB.FX * M
    spec = {
        "units": "metres, kilograms, seconds; axes are glTF (Y up, -Z is rover left, +X forward)",
        "source": "hardware/sim/export_sim.py from hardware/assembly/rover.py and hardware/mass/replica.py; docs/sim-spec.md",
        "total_mass_kg": round(total, 4),
        "wheel": {"radius_m": 0.100, "width_m": 0.080, "grousers": 14, "grouser_height_m": 0.015},
        "wheelbase_m": B.WHEELBASE * M, "track_m": B.TRACK * M,
        "bodies": bodies,
        "joints": [
            {"name": f"wheel{k}", "type": "revolute", "body": f"wheel{k}", "parent": "link" + k[1], "axis": [0, 0, -1], "actuated": True,
             "note": "axis is rover +Y (glTF (0,0,-1)); the rover rolls forward for a positive rotation about it with the right-hand rule"} for k in WHEELS
        ],
        "differential": {"links": ["linkL", "linkR"], "pivot_axis_gltf": [0, 0, -1], "pivot_height_m": A.PIVOT_Z * M, "coupling": "angle_L = -angle_R (bevel gear differential, mitre gears 1:1)", "friction": "none modelled yet"},
        "mast": {"pan": {"origin_m": to_gl(np.array(PAN)).tolist(), "axis": [0, 1, 0], "limit_deg": [-180, 180], "servo": "STS3215", "note": "pan range: ASSUMPTION"},
                 "tilt": {"origin_m": to_gl(np.array(TILT)).tolist(), "axis": [0, 0, -1], "limit_deg": [-90, 90], "note": "swept clear to 90 either way in the CAD; the original tilts +-75 [S19]"}},
        "camera": {"mount": "head", "position_m": to_gl(np.array([cam_x, 0.0, MAST.CAM_AXIS_Z]) - np.array(TILT)).tolist(), "direction": [1, 0, 0],
                   "sensor": "Raspberry Pi HQ (IMX477) with a 4 mm CS lens", "fov_deg_horizontal_approx": 76.6, "fov_deg_vertical_approx": 61.4,
                   "note": "FOV from a 6.287 x 4.712 mm active area (remembered, UNVERIFIED) and 4 mm focal length, no distortion"},
        "motor": {"model": "Pololu 37D 131:1 (candidate #4746)", "current_cap_A": 1.6, "note": "speed and torque curves: docs/drive-spec.md"},
        "ground_reference": "y = 0 is the rim line (grouser tips reach 12.2 mm below it)",
    }
    (OUT / "rover.json").write_text(json.dumps(spec, indent=1))
    print(f"glb {len(glb) / 1e6:.1f} MB, {sum(stats.values())} triangles, total {total:.3f} kg (replica.py 9.55)")
    for b in order:
        print(f"  {b:10s} {mass[b]:6.3f} kg  {stats[b]:7d} tri")


if __name__ == "__main__":
    main()
