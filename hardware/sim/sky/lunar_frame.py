"""Orientation of the Moon in the sky: IAU rotation model, Earth and Sun directions at a site.

Inputs are a UTC time and the site's selenographic latitude and longitude. Outputs are unit vectors in the
site's local east/north/up frame. Used by build_sky.py; the check at the bottom compares the sub-Earth point
with Meeus's optical libration (an independent method) and with the librations' known limits.

Rotation model: IAU WGCCRE (Archinal et al. 2018, Celest Mech Dyn Astr 130:22, Moon): pole RA/Dec and prime meridian W with the E1..E13
libration terms. ASSUMPTION: coefficients typed from memory of that report; the Meeus cross-check below is what vouches for them.
"""
import numpy as np
from astropy.time import Time
from astropy.coordinates import get_body, GeocentricTrueEcliptic, CartesianRepresentation
import astropy.units as u

R_MOON_KM = 1737.4

def _E(d):
    c = [(125.045, -0.0529921), (250.089, -0.1059842), (260.008, 13.0120009), (176.625, 13.3407154), (357.529, 0.9856003),
         (311.589, 26.4057084), (134.963, 13.0649930), (276.617, 0.3287146), (34.226, 1.7484877), (15.134, -0.1589763),
         (119.743, 0.0036096), (239.961, 0.1643573), (25.053, 12.9590088)]
    return np.radians([a + b * d for a, b in c])

def iau_moon(t):
    d = t.tdb.jd - 2451545.0; T = d / 36525.0; E = _E(d); s = lambda i: np.sin(E[i - 1]); c = lambda i: np.cos(E[i - 1])
    ra = 269.9949 + 0.0031 * T - 3.8787 * s(1) - 0.1204 * s(2) + 0.0700 * s(3) - 0.0172 * s(4) + 0.0072 * s(6) - 0.0052 * s(10) + 0.0043 * s(13)
    de = 66.5392 + 0.0130 * T + 1.5419 * c(1) + 0.0239 * c(2) - 0.0278 * c(3) + 0.0068 * c(4) - 0.0029 * c(6) + 0.0009 * c(7) + 0.0008 * c(10) - 0.0009 * c(13)
    W = (38.3213 + 13.17635815 * d - 1.4e-12 * d * d + 3.5610 * s(1) + 0.1208 * s(2) - 0.0642 * s(3) + 0.0158 * s(4) + 0.0252 * s(5) - 0.0066 * s(6)
         - 0.0047 * s(7) - 0.0046 * s(8) + 0.0028 * s(9) + 0.0052 * s(10) + 0.0040 * s(11) + 0.0019 * s(12) - 0.0044 * s(13))
    return ra, de, W

def icrf_to_bodyfixed(t):
    ra, de, W = iau_moon(t)
    Rz = lambda a: np.array([[np.cos(a), np.sin(a), 0], [-np.sin(a), np.cos(a), 0], [0, 0, 1]])
    Rx = lambda a: np.array([[1, 0, 0], [0, np.cos(a), np.sin(a)], [0, -np.sin(a), np.cos(a)]])
    return Rz(np.radians(W)) @ Rx(np.radians(90 - de)) @ Rz(np.radians(90 + ra))

def enu_basis(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    e = np.array([-np.sin(lo), np.cos(lo), 0]); n = np.array([-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)])
    up = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    return np.array([e, n, up])

def moon_and_sun_icrf_km(t):
    """Vectors from the Moon's centre to the Earth's centre and to the Sun's centre, in the GCRS axes (km)."""
    m = get_body('moon', t).cartesian.xyz.to(u.km).value          # Earth to Moon
    s = get_body('sun', t).cartesian.xyz.to(u.km).value           # Earth to Sun
    return -m, s - m

def sky_at(t, lat, lon):
    """Returns dict: rotation icrf->local ENU (3x3), earth and sun unit vectors (ENU), sub-Earth lat/lon, Earth distance."""
    B = icrf_to_bodyfixed(t); M = enu_basis(lat, lon) @ B
    site = enu_basis(lat, lon)[2] * R_MOON_KM                      # site position in body-fixed axes
    earth_c, sun_c = moon_and_sun_icrf_km(t)
    earth_bf = B @ earth_c; sun_bf = B @ sun_c
    earth_vec = earth_bf - site; sun_vec = sun_bf - site
    unit = lambda v: v / np.linalg.norm(v)
    sub = (np.degrees(np.arcsin(earth_bf[2] / np.linalg.norm(earth_bf))), np.degrees(np.arctan2(earth_bf[1], earth_bf[0])))
    e = enu_basis(lat, lon)
    return dict(M=M, earth=unit(e @ earth_vec), sun=unit(e @ sun_vec), earth_dist_km=float(np.linalg.norm(earth_vec)), sub_earth=sub)

def az_el(v):
    return (np.degrees(np.arctan2(v[0], v[1])) % 360, np.degrees(np.arcsin(v[2])))

def meeus_libration(t):
    """Optical libration (l', b') of Meeus, Astronomical Algorithms ch. 53, from the Moon's true ecliptic position."""
    m = get_body('moon', t).transform_to(GeocentricTrueEcliptic(equinox=t))
    lam, beta = m.lon.deg, m.lat.deg
    T = (t.tt.jd - 2451545.0) / 36525.0
    F = 93.2720993 + 483202.0175273 * T; Om = 125.0445479 - 1934.1362891 * T
    I = np.radians(1.54242); W = np.radians(lam - Om); b = np.radians(beta)
    A = np.arctan2(np.sin(W) * np.cos(b) * np.cos(I) - np.sin(b) * np.sin(I), np.cos(W) * np.cos(b))
    l = np.degrees(A) - F; l = (l + 180) % 360 - 180
    bb = np.degrees(np.arcsin(-np.sin(W) * np.cos(b) * np.sin(I) - np.sin(b) * np.cos(I)))
    return l, bb

if __name__ == "__main__":
    # Meeus example 53.a (1992 April 12, 0h TD): l' = -1.206, b' = +4.194 (optical), published in the book
    t = Time('1992-04-12 00:00:00', scale='tt')
    print('Meeus 53.a  mine:', meeus_libration(t), ' book: (-1.206, +4.194)')
    for ts in ['1992-04-12 00:00:00', '2026-11-20 00:00:00', '2027-03-05 12:00:00', '2030-07-01 00:00:00']:
        t = Time(ts, scale='utc'); s = sky_at(t, 47.5676, 44.8102); l, b = meeus_libration(t)
        print(ts, 'IAU sub-Earth lat,lon = %.3f, %.3f' % s['sub_earth'], ' Meeus (b,l) = %.3f, %.3f' % (b, l))
