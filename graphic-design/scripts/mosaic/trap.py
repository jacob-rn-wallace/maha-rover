import numpy as np

def group_geometry(b, h, r, g):
    """Polygon of trapezoid group g in strip r (3 triangles merged)."""
    y0, y1 = r * h, (r + 1) * h
    s = (r % 2) * b / 2.0
    j0 = 2 if r % 2 == 0 else 1
    js = j0 + 3 * g
    if js % 2 == 0:                      # up, down, up  -> wide at bottom
        k = js // 2; xk = s + k * b
        return [(xk, y0), (xk + b, y0), (xk + 1.5 * b, y1), (xk - 0.5 * b, y1)]
    k = (js - 1) // 2; xk = s + k * b     # down, up, down -> wide at top
    return [(xk, y0), (xk + 2 * b, y0), (xk + 1.5 * b, y1), (xk + 0.5 * b, y1)]

def labels(W, H, b, h):
    ys, xs = np.mgrid[0:H, 0:W]
    ys = ys + 0.5; xs = xs + 0.5
    r = np.floor(ys / h).astype(np.int64)
    u = (ys - r * h) / h
    s = (r % 2) * b / 2.0
    xp = xs - s
    t = xp / b
    k0 = np.floor(t).astype(np.int64)
    f = t - k0
    kn = np.where(f < 0.5, k0, k0 + 1)
    d = np.abs(xp - kn * b)
    is_up = d <= (b / 2.0) * u
    k = np.where(is_up, kn, k0)
    j = 2 * k + np.where(is_up, 0, 1)
    j0 = np.where(r % 2 == 0, 2, 1)
    g = (j - j0) // 3
    tri = (r, is_up.astype(np.int64), k)
    return r, g, tri
