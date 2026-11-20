"""Builds the sky assets for the simulation (sim/public/sky/): real stars, the Milky Way, and the Earth as seen from the site.

Usage:  python build_sky.py DC_DATA_DIR THREE_GLOBE_IMG_DIR [OUT_DIR]
  DC_DATA_DIR        the data/ folder of the npm package d3-celestial 0.7.35 (stars.8.json, milkyway.json)
  THREE_GLOBE_IMG_DIR the example/ folder of the npm package three-globe 2.45.6 (img/earth-blue-marble.jpg, clouds/clouds.png)
Needs numpy, astropy, pillow (and the sibling lunar_frame.py). The outputs are committed, so this only runs again to change the epoch or the cuts.

Sources and status
  Stars:     Hipparcos catalogue (ESA 1997) positions (J2000, no proper motion: under 0.1 deg over centuries, so invisible), V magnitude and B-V,
             as packaged by d3-celestial (BSD-3-Clause, Olaf Frohn). Cut at V <= 7.5 (25 723 stars; the eye's limit is about 6.5). stated
  Milky Way: the five brightness contours of d3-celestial (milkyway.json), filled, summed and blurred. A smooth glow, no dust lanes. approximate
  Earth:     NASA Blue Marble with bathymetry (a copy in the three-globe examples; NASA imagery is public domain, the copy's provenance is not
             checked) and a static cloud map from the same package, mixed into one albedo texture. Not the cloud cover of the epoch. approximate
  Orientation: Moon rotation from the IAU model, Earth from astropy's built-in ephemeris; see lunar_frame.py for the check against Meeus.
Epoch: 2030-10-02 14:48 UTC, found by search (50 lunations from 2027-06-01; search kept out of this file): the real Sun at the site is 14.0 deg up in the
  morning (the simulation's sun elevation) at bearing 108 deg, the libration is small (Earth near its mean place) and the Earth turned so that Africa faces
  the Moon. The simulation's sun is set to this real Sun (lunar.ts and the shadow textures), so the sky and the lighting agree. The Earth is lit by it.
"""
import sys, json, struct, warnings
warnings.filterwarnings('ignore')
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
from astropy.time import Time
import erfa
from lunar_frame import sky_at, az_el

EPOCH = '2030-10-02 14:48:00'
MAG_LIMIT = 7.5
R_EARTH_KM = 6378.137

dc, tg = Path(sys.argv[1]), Path(sys.argv[2])
out = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).resolve().parents[3] / 'sim' / 'public' / 'sky'
out.mkdir(parents=True, exist_ok=True)
atlas = json.load(open(Path(__file__).resolve().parents[3] / 'sim' / 'public' / 'terrain' / 'atlas_5km.json'))
lat, lon = atlas['centre_lat'], atlas['centre_lon']

# ---- orientation
t = Time(EPOCH, scale='utc')
s = sky_at(t, lat, lon)
S = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float)             # ENU (east, north, up) -> sim world (x east, y up, z south)
M_sim = S @ s['M']                                                  # ICRF axes -> sim world
earth_dir = S @ s['earth']
earth_r = float(np.arcsin(R_EARTH_KM / s['earth_dist_km']))
c2t = erfa.c2t06a(t.tt.jd1, t.tt.jd2, t.utc.jd1, t.utc.jd2, 0.0, 0.0)   # ICRF -> Earth-fixed (UT1 taken as UTC: under 1 s, 0.004 deg)
to_fixed = c2t @ M_sim.T                                             # sim world -> Earth-fixed
# sub-lunar point on the Earth, from the direction to the Moon (opposite the Earth direction, in ICRF)
moon_icrf = -(M_sim.T @ earth_dir)
moon_fixed = c2t @ moon_icrf
sub_lunar = (float(np.degrees(np.arcsin(moon_fixed[2]))), float(np.degrees(np.arctan2(moon_fixed[1], moon_fixed[0]))))
sun_az, sun_el = az_el(s['sun']); e_az, e_el = az_el(s['earth'])
print('site %.4f N %.4f E; epoch %s' % (lat, lon, EPOCH))
print('sub-Earth point on the Moon: lat %.2f lon %.2f' % s['sub_earth'])
print('Earth from the site: bearing %.1f el %.1f, distance %.0f km, angular diameter %.2f deg' % (e_az, e_el, s['earth_dist_km'], 2 * np.degrees(earth_r)))
print('real Sun: bearing %.1f el %.1f; sub-lunar point on the Earth: lat %.1f lon %.1f (Moon declination limit 28.6)' % (sun_az, sun_el, *sub_lunar))
assert abs(sub_lunar[0]) < 29.5 and abs(s['sub_earth'][0]) < 8 and abs(s['sub_earth'][1]) < 8

# ---- stars
feats = json.load(open(dc / 'stars.8.json'))['features']
rows = []
for f in feats:
    m = f['properties']['mag']
    if m <= MAG_LIMIT:
        ra, de = f['geometry']['coordinates']; rows.append((ra % 360.0, de, m, float(f['properties']['bv'] or 0.6)))
rows = np.array(rows); n = len(rows)
sir = rows[np.argmin(rows[:, 2])]
print('stars: %d; brightest m=%.2f at RA %.2f Dec %.2f (Sirius: RA 101.29 Dec -16.72)' % (n, sir[2], sir[0], sir[1]))
assert abs(sir[0] - 101.29) < 0.2 and abs(sir[1] + 16.72) < 0.2
ra16 = np.round(rows[:, 0] / 360 * 65536).astype(np.uint32) % 65536
de16 = np.round(rows[:, 1] / 90 * 32767).astype(np.int16)
mg8 = np.clip(np.round((rows[:, 2] + 2) * 25), 0, 255).astype(np.uint8)
bv8 = np.clip(np.round((rows[:, 3] + 0.6) * 100), 0, 255).astype(np.uint8)
with open(out / 'stars.bin', 'wb') as fh:
    fh.write(ra16.astype('<u2').tobytes()); fh.write(de16.astype('<i2').tobytes()); fh.write(mg8.tobytes()); fh.write(bv8.tobytes())

# ---- Milky Way
W, H = 2048, 1024
acc = np.zeros((H, W), np.float32)
for f in json.load(open(dc / 'milkyway.json'))['features']:
    img = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(img)
    g = f['geometry']; polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
    for poly in polys:
        for k, ring in enumerate(poly):
            pts = [((x % 360.0) / 360 * W, (90 - y) / 180 * H) for x, y in ring]
            dr.polygon(pts, fill=255 if k == 0 else 0)
    acc += np.asarray(img, np.float32) / 255
acc /= 5
mw = Image.fromarray((np.clip(acc, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14)).resize((1024, 512), Image.LANCZOS)
mw.save(out / 'milkyway.png', optimize=True)
gc = np.asarray(mw, float)[int((90 + 29.0) / 180 * 512), int(266.4 / 360 * 1024)]
print('Milky Way level at the galactic centre (RA 266.4, Dec -29): %.0f of 255; at the north galactic pole (RA 192.9 Dec 27.1): %.0f' % (gc, np.asarray(mw, float)[int((90 - 27.1) / 180 * 512), int(192.9 / 360 * 1024)]))

# ---- Earth albedo (surface and clouds in one)
surf = Image.open(tg / 'img' / 'earth-blue-marble.jpg').convert('RGB').resize((1024, 512), Image.LANCZOS)
cl = Image.open(tg / 'clouds' / 'clouds.png').convert('RGBA').split()[3].resize((1024, 512), Image.LANCZOS)      # cloud density is the alpha channel (white colour)
sa = np.asarray(surf, np.float32) / 255; ca = np.clip(np.asarray(cl, np.float32) / 255 * 1.5, 0, 1)[..., None]      # x1.5: the map covers 15% of the sky, the Earth's mean cloud cover is about two thirds (look-development)
lin = np.where(sa <= 0.04045, sa / 12.92, ((sa + 0.055) / 1.055) ** 2.4)
mix = lin * (1 - 0.9 * ca) + 0.9 * ca * 0.8                                  # opaque cloud: albedo 0.72 (linear), a typical thick-cloud value (ASSUMPTION)
srgb = np.where(mix <= 0.0031308, mix * 12.92, 1.055 * mix ** (1 / 2.4) - 0.055)
Image.fromarray((np.clip(srgb, 0, 1) * 255).astype(np.uint8)).save(out / 'earth.jpg', quality=88)

json.dump({
    'epoch_utc': EPOCH, 'site': {'lat': lat, 'lon': lon}, 'n_stars': int(n), 'mag_limit': MAG_LIMIT,
    'icrf_to_world': [round(float(x), 7) for x in M_sim.ravel()],
    'earth': {'dir_world': [round(float(x), 6) for x in earth_dir], 'angular_radius_rad': round(earth_r, 6), 'world_to_fixed': [round(float(x), 7) for x in to_fixed.ravel()],
              'bearing_deg': round(e_az, 2), 'elevation_deg': round(e_el, 2), 'distance_km': round(s['earth_dist_km']), 'sub_earth_moon_latlon': [round(x, 2) for x in s['sub_earth']], 'sub_lunar_earth_latlon': [round(x, 2) for x in sub_lunar]},
    'real_sun_at_epoch': {'bearing_deg': round(sun_az, 1), 'elevation_deg': round(sun_el, 1)},
    'frame': 'world: x east, y up, z south (north is -z); matrices are row-major, applied to column vectors',
    'credits': 'Hipparcos (ESA 1997) via d3-celestial (BSD-3-Clause, O. Frohn); NASA Blue Marble imagery via the three-globe example images (MIT package; NASA imagery public domain)',
}, open(out / 'sky.json', 'w'), indent=1)
print('wrote', out)
