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
import detail as DT      # noqa: E402

OUT = ROOT / "sim" / "public"
M = 1e-3
WHEEL_RIM_R = 0.100
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


# ---- visual layer: T-slot profiles in place of the CAD's plain extrusion boxes (the CAD ignores slots; mass is from catalogue kg/m) ----
from build123d import Box, Cylinder, Pos, Rot  # noqa: E402

# (opening, lip thickness, cavity width, cavity depth, bore): 5-series 20 mm profile (6 mm slot) and 8-series 40 mm profile (10 mm slot)   ASSUMPTION (typical catalogue values)
PROFILES = {20.0: (6.2, 1.8, 11.0, 4.5, 4.2), 40.0: (10.2, 3.0, 20.0, 9.0, 8.5)}


def tslot_bar(size, length):
    """A square T-slot bar of side `size` (20 or 40), `length` along Z, centred on the origin."""
    op, lip, cw, cd, bore = PROFILES[size]
    bar = Box(size, size, length)
    for k in range(4):
        cut = Pos(0, size / 2 - lip / 2 + 0.5, 0) * Box(op, lip + 1.0, length + 2) + Pos(0, size / 2 - lip - cd / 2, 0) * Box(cw, cd, length + 2)
        bar = bar - Rot(0, 0, 90 * k) * cut
    t = size * 0.12                                                 # diagonal webs joining the core to the corners
    sq = Box(size, size, length)
    for ang in (45, -45):
        bar = bar + ((Rot(0, 0, ang) * Box(t, size * 1.5, length)) & sq)
    return bar - Cylinder(bore / 2, length + 2)


def refine(group, name, shape):
    """Visual detail for the head and base (hardware/sim/detail.py), then the T-slot swap below."""
    if name == "pan housing":
        return DT.seam(DT.soften(shape, 3.0), 2, 406.0, 1.0, 0.9)                                   # lid seam 15 mm below the top (Takachi cover height)
    if name == "enclosure":
        return DT.seam(DT.soften(shape, 2.5), 0, HB.FX - 73.0 + 47.5 - 10.0, 1.0, 0.9)    # lid seam 10 mm back from the front face   ASSUMPTION
    if name == "cable gland":
        return DT.gland_pg7(HB.GLAND_X, HB.AZ, -60.0)
    return refine_extrusion(group, name, shape)


def refine_extrusion(group, name, shape):
    """Swap a plain extrusion box of the frame or mast for a slotted profile, keeping holes cut in the box."""
    if not (group in ("frame", "frame upper") or (group == "mast" and name == "tube")):
        return shape
    bb = shape.bounding_box()
    d = np.array([bb.size.X, bb.size.Y, bb.size.Z])
    ax = int(np.argmax(d))
    sec = sorted(float(x) for i, x in enumerate(d) if i != ax)
    ok = lambda a, b: abs(a - b) < 0.6
    if not ((ok(sec[0], 20) and ok(sec[1], 20)) or (ok(sec[0], 20) and ok(sec[1], 40)) or (ok(sec[0], 40) and ok(sec[1], 40))):
        return shape
    L = float(d[ax])
    c = ((bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2, (bb.min.Z + bb.max.Z) / 2)
    if ok(sec[0], 20) and ok(sec[1], 40):
        bar = Pos(-10, 0, 0) * tslot_bar(20.0, L) + Pos(10, 0, 0) * tslot_bar(20.0, L)      # local X is the 40 mm direction
    else:
        bar = tslot_bar(20.0 if ok(sec[1], 20) else 40.0, L)
    rotations = {0: Rot(0, 90, 0), 1: Rot(-90, 0, 0), 2: Rot(0, 0, 0)}
    base = rotations[ax]
    box_vol = bb.size.X * bb.size.Y * bb.size.Z
    best = None
    for roll in (0, 90):
        cand = Pos(*c) * base * Rot(0, 0, roll) * bar
        cb = cand.bounding_box()
        err = abs(cb.size.X - bb.size.X) + abs(cb.size.Y - bb.size.Y) + abs(cb.size.Z - bb.size.Z)
        if best is None or err < best[0]:
            best = (err, cand)
    err, cand = best
    if err > 1.0:
        return shape
    if abs(shape.volume - box_vol) > 1.0:                                  # holes or cuts in the CAD member: keep them
        cand = cand - (Pos(*c) * Box(bb.size.X, bb.size.Y, bb.size.Z) - shape)
    return cand


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
        if name in ("tube", "bracket", "spindle", "tilt servo", "mast cap", "mast cap screw"):
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


# Real-world materials, by part, for the visual layer (sRGB colour, metallic, roughness).  Interior parts keep the group colours of rover.py.   ASSUMPTION (finishes are not sourced)
MATERIALS = {
    "cast aluminium": ((158, 162, 166), 0.9, 0.55),        # die-cast Takachi boxes, the mast base and camera box
    "sheet aluminium": ((190, 194, 198), 0.9, 0.38),       # deck, panels, bracket, disk, hat
    "anodised T-slot": ((176, 180, 186), 0.85, 0.32),      # extrusions
    "black plastic": ((22, 22, 24), 0.05, 0.65),           # printed hood and baffle, servo cases, antenna
    "lens glass": ((8, 10, 14), 0.1, 0.08),
    "cord": ((20, 20, 22), 0.0, 0.55),                     # the HDMI cord jacket (black assumed)
    "solar cell": ((12, 18, 38), 0.35, 0.14),              # back-contact silicon behind glass: dark, glossy
    "wheel print": ((70, 72, 76), 0.05, 0.6),              # ASA print, mid-grey
    "steel": ((120, 124, 130), 0.95, 0.4),
    "black anodised": ((26, 26, 28), 0.7, 0.4),            # lens barrel
    "ceramic patch": ((128, 112, 84), 0.0, 0.5),           # GNSS patch antenna
}


def material_key(group, name):
    if group == "solar pieces":
        return "solar cell"
    if group == "wheels":
        return "wheel print"
    if group in ("frame", "frame upper") or name == "tube":
        return "anodised T-slot"
    if name in ("pan housing", "enclosure", "base", "pan coupling disc"):
        return "cast aluminium"
    if name == "mast cap screw":
        return "steel"
    if name in ("bracket", "disk", "antenna hat", "mast cap") or group == "panels":
        return "sheet aluminium"
    if name == "GNSS patch":
        return "ceramic patch"
    if name in ("hood", "baffle", "cable gland", "HDMI plug") or "servo" in name or group == "wifi antenna":
        return "black plastic"
    if name == "lens":
        return "black anodised"
    if name == "camera-link cable":
        return "cord"
    if group in ("pivot shaft", "bearings", "wheel hardware", "differential") or name == "spindle":
        return "steel"
    return group


def plain_finish(key):
    """a material key with the default finish (metal 0.15, rough 0.45): mergeable by vertex colour"""
    return key not in MATERIALS and key not in ("link plates", "differential housing", "motors")


def material(key):
    if key in MATERIALS:
        (r, g, b), metal, rough = MATERIALS[key]
    else:
        r, g, b = R.COLORS.get(key, (150, 150, 150))
        metal, rough = {"link plates": 0.7, "differential housing": 0.7, "motors": 0.6}.get(key, 0.15), 0.45
    lin = lambda c: (c / 255) ** 2.2
    return (lin(r), lin(g), lin(b), 1.0), metal, rough


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
    wheel_mesh = {}                          # wheel body -> its rim-and-grouser vertices (glTF metres, hub-centred), for the collision hulls
    for g, n, s in items:
        b = body_of(g, n)
        pieces = [(material_key(g, n), refine(g, n, s))]
        if n == "lens":                                                   # visual detail: grooved barrel, glass, retaining ring
            barrel, glass, ring = DT.lens_detail(s)
            pieces = [("black anodised", barrel), ("lens glass", glass), ("steel", ring)]
        if n == "bracket":
            pieces += [("steel", bolt) for bolt in DT.bracket_bolts(s)]
        if n == "pan housing":                                            # four lid screws on the cover, inset 7 mm from the corners
            bb = s.bounding_box()
            pieces += [("steel", DT.cap_screw(x, y, bb.max.Z, "+z")) for x in (bb.min.X + 7, bb.max.X - 7) for y in (bb.min.Y + 7, bb.max.Y - 7)]
        for key, sh in pieces:
            v, t = mesh_of(sh)
            if len(t) == 0:
                continue
            bb_ = "pan" if (n == "bracket" and key == "steel") else b
            v = to_gl(v - np.array(BODIES[bb_]))
            if g == "wheels":
                wheel_mesh[b] = v
            per[bb_].setdefault(key, []).append((v, t))
            raw[bb_].append((v, t))

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
    pan_pts = [((MAST.EXT_TOP - MAST.TUBE_Z0) / 1000.0 * MAST.EXT_KG_PER_M, cen("tube")), (rot["mast cap"].volume / 1e6 * MAST.AL_G_CM3, cen("mast cap")), (MAST.CAP_SCREW_KG, cen("mast cap screw")), (rot["bracket"].volume / 1e6 * MAST.AL_G_CM3, cen("bracket")),
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
        classes = {}                                 # draw-call merge: parts with the default finish (one colour each) share one material with per-vertex colours
        for g, pieces in per[b].items():
            classes.setdefault("interior" if plain_finish(g) else g, []).append((g, pieces))
        for cls, groups in classes.items():
            vs, ns, iis, cols, base = [], [], [], [], 0
            for g, pieces in groups:
                v = np.concatenate([p[0] for p in pieces])
                off = np.cumsum([0] + [len(p[0]) for p in pieces[:-1]])
                t = np.concatenate([p[1] + o for p, o in zip(pieces, off)])
                vv, nn, ii = smooth(v, t)
                vs.append(vv); ns.append(nn); iis.append(ii + base); base += len(vv)
                cols.append(np.tile(np.array(material(g)[0][:3]), (len(vv), 1)))
            vv, nn, ii = np.concatenate(vs), np.concatenate(ns), np.concatenate(iis)
            if cls not in mat_idx:
                if cls == "interior":
                    mats.append({"name": cls, "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.15, "roughnessFactor": 0.45}})
                else:
                    col, me, ro = material(cls)
                    mats.append({"name": cls, "pbrMetallicRoughness": {"baseColorFactor": list(col), "metallicFactor": me, "roughnessFactor": ro}})
                mat_idx[cls] = len(mats) - 1
            attrs = {"POSITION": add_acc(vv.astype("<f4"), 34962, 5126, "VEC3", True), "NORMAL": add_acc(nn.astype("<f4"), 34962, 5126, "VEC3")}
            if cls == "interior":
                attrs["COLOR_0"] = add_acc(np.concatenate(cols).astype("<f4"), 34962, 5126, "VEC3")
            prims.append({"attributes": attrs, "indices": add_acc(ii.astype("<u4"), 34963, 5125, "SCALAR"), "material": mat_idx[cls]})
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
                mcom, I = mp
                d = np.array(com) - mcom                                   # the mass-weighted centre of mass is not the mesh's: parallel axis
                I = I + mass[b] * (d @ d * np.eye(3) - np.outer(d, d))
                w, V = np.linalg.eigh(I)
                if np.linalg.det(V) < 0:
                    V[:, 2] = -V[:, 2]
                qw = math.sqrt(max(0.0, 1 + V[0, 0] + V[1, 1] + V[2, 2])) / 2
                q = [(V[2, 1] - V[1, 2]) / (4 * qw), (V[0, 2] - V[2, 0]) / (4 * qw), (V[1, 0] - V[0, 1]) / (4 * qw), qw] if qw > 1e-6 else [1, 0, 0, 0]
                entry["mesh_com_m"] = [round(x, 5) for x in mcom.tolist()]
                entry["inertia_principal_kgm2"] = [float(f"{x:.4g}") for x in w]
                entry["inertia_frame_quat_xyzw"] = [round(float(x), 6) for x in q]
        if b == "chassis" and raw[b]:                                  # collision hull of the whole fixed structure, on a 6 mm grid
            pts = np.unique(np.round(np.concatenate([p[0] for p in raw[b]]) / 0.006), axis=0) * 0.006
            entry["collider_hull_points_m"] = [round(float(x), 4) for x in pts.ravel()]
        if b in wheel_mesh:                                            # one convex hull per grouser (clustered by angle about the hub axis, glTF Z), plates thickened to 3 mm
            v = wheel_mesh[b]
            r = np.hypot(v[:, 0], v[:, 1])
            gv = v[r > (WHEEL_RIM_R + 0.0005)]
            ang = np.arctan2(gv[:, 1], gv[:, 0])
            order_ = np.argsort(ang)
            ang, gv = ang[order_], gv[order_]
            cuts = np.where(np.diff(ang) > math.radians(5))[0] + 1
            groups = np.split(np.arange(len(ang)), cuts)
            if len(groups) > 1 and (ang[0] + 2 * math.pi - ang[-1]) < math.radians(5):    # first and last clusters are one across the +-pi seam
                groups[0] = np.concatenate([groups[-1], groups[0]])
                groups = groups[:-1]
            hulls = []
            for gi in groups:
                P = gv[gi]
                phi = float(np.arctan2(P[:, 1].mean(), P[:, 0].mean()))
                tdir = np.array([-math.sin(phi), math.cos(phi), 0.0])
                P2 = np.concatenate([P + 0.0015 * tdir, P - 0.0015 * tdir])
                hulls.append([round(float(x), 4) for x in P2.ravel()])
            entry["grouser_hulls_m"] = hulls
        bodies[b] = entry
    hx, hy, hz = HX * M, HY * M, HZ * M
    cam_x = HB.FX
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
                   "note": "FOV from a 6.287 x 4.712 mm active area (Raspberry Pi camera documentation, checked 2026-11-09) and 4 mm focal length, no distortion"},
        "motor": {"model": "Pololu 37D 131:1 (candidate #4746)", "current_cap_A": 1.6, "note": "speed and torque curves: docs/drive-spec.md"},
        "ground_reference": "y = 0 is the rim line (grouser tips reach 12.2 mm below it)",
    }
    (OUT / "rover.json").write_text(json.dumps(spec, indent=1))
    print(f"glb {len(glb) / 1e6:.1f} MB, {sum(stats.values())} triangles, total {total:.3f} kg (replica.py 9.58)")
    for b in order:
        print(f"  {b:10s} {mass[b]:6.3f} kg  {stats[b]:7d} tri")


if __name__ == "__main__":
    main()
