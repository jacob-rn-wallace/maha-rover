"""Single source of truth for the al-maha wordmark geometry and the source photo.

Wordmark coordinates are in design units (20-unit lattice, 15 degree lean).
"""
import os
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

# Source photo, resized to the working size all grid/crop constants assume.
PHOTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "source-photos", "art002e009288orig.jpg")
WORK_SIZE = (2576, 1717)

def load_photo(path=PHOTO, size=WORK_SIZE):
    """Load a photo as RGB; resize to `size` (w, h) unless size is None."""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    if size is not None and im.size != tuple(size):
        im = im.resize(tuple(size), Image.LANCZOS)
    return im

def rect(x, y, w, h): return box(x, y, x + w, y + h)
def poly(s): return Polygon([tuple(map(float, p.split(','))) for p in s.split()])

shapes = [
    rect(60, 235, 340, 10), rect(110, 207.68, 40, 10), rect(160, 170.36, 60, 10),
    rect(300, 170.36, 40, 10), rect(305, 133.04, 30, 7), rect(175, 133.04, 30, 7),
    poly("50,245 70,245 100,133.04 80,133.04"),
    poly("390,245 410,245 380,133.04 360,133.04"),
    poly("430,245 450,245 420,133.04 400,133.04"),
    poly("90,245 110,245 120,207.68 100,207.68"),
    poly("150,245 170,245 160,207.68 140,207.68"),
    poly("140,207.68 160,207.68 170,170.36 150,170.36"),
    poly("230,245 250,245 230,170.36 210,170.36"),
    poly("270,245 290,245 310,170.36 290,170.36"),
    poly("350,245 370,245 350,170.36 330,170.36"),
]

merged = unary_union(shapes).buffer(0).simplify(0.001)
geoms = list(merged.geoms) if merged.geom_type == "MultiPolygon" else [merged]

def ring(coords, ox=0.0, oy=0.0):
    pts = list(coords)[:-1]
    return "M" + "L".join(f"{x+ox:.2f} {y+oy:.2f}" for x, y in pts) + "Z"

def path_d(ox=0.0, oy=0.0):
    """SVG path data for the merged outline, optionally translated."""
    d = ""
    for g in geoms:
        d += ring(g.exterior.coords, ox, oy)
        for h in g.interiors:
            d += ring(h.coords, ox, oy)
    return d
