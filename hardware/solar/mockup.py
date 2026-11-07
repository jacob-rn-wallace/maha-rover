"""al-maha solar cell mockups: the side of the rover with each candidate cell on the panel.

Side elevation from outside (orthographic along Y), from the same numbers as body.py: wall
190 mm either side of the middle, z 124 to 345, deck to 348, cell field centred at body.FIELD_Z on the
original's grid (pitch 71.6 x 41), wheels as outlines (rim 200, grouser tips 230) in front.
Cells are projected onto the vertical plane (the wall leans 10 degrees, so heights shrink by cos 10).
Colours are illustrative: no cell colour was found for any candidate, and an AnySolar module's
internal cell stripes are drawn evenly along its long side as an assumption.

Run:  .venv/bin/python hardware/solar/mockup.py
Out:  docs/images/solar-cell-mockups.png
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "body"))
import body as B  # noqa: E402

COS = math.cos(math.radians(B.SIDEWALL_DEG))
S = 1.1                   # pixels per mm in a tile
SS = 2                    # supersampling
X0, X1, Z0, Z1 = -265.0, 265.0, -8.0, 362.0
TILE_W, TILE_H = int((X1 - X0) * S), int((Z1 - Z0) * S)
LABEL_H = 74

# name, cell w, cell h (on the face, mm), row pitch, inner cell grid (columns, rows) drawn inside the module or (0, 0), clipped corners, note
VARIANTS = [
    ("Tiled back-contact pieces, 2 per slot (decided)", 62.5, 41.6, 42.5, (2, 1), 0.0, "two 31 x 41.6 mm pieces per slot, 0.5 mm gap; no front contacts; 30 a side"),
    ("Original (reference)", 69.0, 39.0, 41.0, (0, 0), 6.5, "69 x 39 mm, clipped bottom corners [3g]"),
    ("AnySolar SM261K10TF (US$415-490)", 64.0, 45.0, 46.0, (5, 2), 0.0, "64 x 45 x 1.2 mm, 10 cells in a 5 x 2 grid [datasheet]; row pitch 46"),
    ("Futurlec SZGD6030 (about US$45)", 60.0, 30.0, 41.0, (0, 0), 0.0, "60 x 30 x 2.8 mm, one cell each, plain"),
    ("Tiled back-contact pieces, 1 per slot", 62.5, 41.6, 42.5, (0, 0), 0.0, "62.5 x 41.6 mm: a 1/3-cut strip halved; no front contacts"),
    ("AnySolar SM141K10", 70.0, 23.0, 41.0, (10, 1), 0.0, "70 x 23 mm, 10 cells in series per module (inner layout assumed)"),
    ("AnySolar SM261K05", 67.0, 25.0, 41.0, (5, 1), 0.0, "67 x 25 mm, 5 cells in series per module (inner layout assumed)"),
]

BG = (250, 250, 247)
GROUND = (120, 120, 120)
WALL = (186, 191, 196)
WALL_EDGE = (110, 116, 122)
DECK = (150, 156, 162)
CELL = (24, 33, 58)
CELL_LINE = (70, 84, 118)
WHEEL = (60, 64, 70)
TEXT = (30, 30, 30)


def font(size):
    for p in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def px(x, z):
    return ((x - X0) * S * SS, (Z1 - z) * S * SS)


def draw_tile(name, w, h, pitch, grid, clip, note):
    im = Image.new("RGB", (TILE_W * SS, TILE_H * SS), BG)
    d = ImageDraw.Draw(im)
    # ground
    d.line([px(X0, 0), px(X1, 0)], fill=GROUND, width=2 * SS)
    # body side (wall), deck
    z_wall0, z_wall1 = B.UNDERSIDE_Z, B.DECK_TOP_Z - B.DECK_T
    half = B.SIDE_PLATE_LEN / 2
    d.rectangle([px(-half, z_wall1), px(half, z_wall0)], fill=WALL, outline=WALL_EDGE, width=SS)
    dh = B.DECK_LEN / 2
    d.rectangle([px(-dh, B.DECK_TOP_Z), px(dh, z_wall1)], fill=DECK, outline=WALL_EDGE, width=SS)
    # cells
    for j in range(B.N_ROWS):
        v = (j - (B.N_ROWS - 1) / 2) * pitch
        zc = B.FIELD_Z + v * COS
        for i in range(B.N_COLS):
            xc = (i - (B.N_COLS - 1) / 2) * B.PITCH_U
            hz = h * COS
            x0, x1, za, zb = xc - w / 2, xc + w / 2, zc - hz / 2, zc + hz / 2
            if clip > 0:
                c = clip
                pts = [px(x0 + c, za), px(x1 - c, za), px(x1, za + c * COS), px(x1, zb), px(x0, zb), px(x0, za + c * COS)]
                d.polygon(pts, fill=CELL)
            else:
                d.rectangle([px(x0, zb), px(x1, za)], fill=CELL)
            gc, gr = grid
            for k in range(1, gc):
                xs = x0 + w * k / gc
                d.line([px(xs, zb), px(xs, za)], fill=CELL_LINE, width=SS)
            for k in range(1, gr):
                zs = za + (zb - za) * k / gr
                d.line([px(x0, zs), px(x1, zs)], fill=CELL_LINE, width=SS)
    # wheels in front: rim, grouser tips, hub, spokes
    for wx in (B.WHEELBASE / 2, -B.WHEELBASE / 2):
        cx, cz = wx, B.HUB_Z
        for r, dash in ((100.0, False), (115.0, True)):
            if dash:
                for a in range(0, 360, 6):
                    a0, a1 = math.radians(a), math.radians(a + 3)
                    d.line([px(cx + r * math.cos(a0), cz + r * math.sin(a0)), px(cx + r * math.cos(a1), cz + r * math.sin(a1))], fill=WHEEL, width=SS)
            else:
                d.ellipse([px(cx - r, cz + r), px(cx + r, cz - r)], outline=WHEEL, width=2 * SS)
        for k in range(10):
            a = math.radians(k * 36 + 18)
            d.line([px(cx + 26 * math.cos(a), cz + 26 * math.sin(a)), px(cx + 97 * math.cos(a), cz + 97 * math.sin(a))], fill=WHEEL, width=SS)
        d.ellipse([px(cx - 26, cz + 26), px(cx + 26, cz - 26)], fill=(100, 104, 112), outline=WHEEL, width=SS)
    im = im.resize((TILE_W, TILE_H), Image.LANCZOS)
    tile = Image.new("RGB", (TILE_W, TILE_H + LABEL_H), BG)
    tile.paste(im, (0, LABEL_H))
    t = ImageDraw.Draw(tile)
    t.text((10, 8), name, fill=TEXT, font=font(22))
    t.text((10, 38), note, fill=(80, 80, 80), font=font(15))
    # field extent and fill
    n = B.N_COLS * B.N_ROWS * (2 if grid == (2, 1) and w > 60 else 1)
    area = B.N_COLS * B.N_ROWS * w * h / 100.0
    t.text((10, 56), f"{area:.0f} cm2 of cell area per side", fill=(80, 80, 80), font=font(13))
    return tile


def main():
    tiles = [draw_tile(*v) for v in VARIANTS]
    cols = 2
    rows = math.ceil(len(tiles) / cols)
    gap = 14
    W = cols * TILE_W + (cols + 1) * gap
    H = rows * (TILE_H + LABEL_H) + (rows + 1) * gap + 40
    sheet = Image.new("RGB", (W, H), (255, 255, 255))
    t = ImageDraw.Draw(sheet)
    t.text((gap, 10), "al-maha side panel: cell options (side elevation from outside; wheels drawn as outlines; colours illustrative)", fill=TEXT, font=font(18))
    for k, tile in enumerate(tiles):
        r, c = divmod(k, cols)
        sheet.paste(tile, (gap + c * (TILE_W + gap), 40 + gap + r * (TILE_H + LABEL_H + gap)))
    # key tile in the last free slot
    if len(tiles) % cols:
        r, c = divmod(len(tiles), cols)
        x, y = gap + c * (TILE_W + gap), 40 + gap + r * (TILE_H + LABEL_H + gap)
        t.text((x + 10, y + 10), "Notes", fill=TEXT, font=font(22))
        lines = [
            "Columns on the original's pitch (71.6 mm); rows 41 mm, 42.5 for the tiled",
            "pieces, 46 for the SM261K10. Tiled pieces: gap 0.5 mm, drawn as one slot.",
            "The wall leans 10 degrees; heights are drawn foreshortened by cos 10.",
            "AnySolar parts are modules of several cells. The SM261K10's 5 x 2 inner",
            "grid is from its datasheet drawing; the others' inner layout and all",
            "colours are assumptions. On the SM261K10 the two solder pads are on",
            "the back, so the panel is drilled behind each (60 holes).",
            "The field is at the original's height (z 196 to 314, 3k): the wheel",
            "rim tops just reach the lowest row's bottom edge and the grouser",
            "tips overlap it. The original's field and body sit about 14 mm",
            "behind the wheelbase midpoint; the model centres them.",
            "Futurlec corner shape is unknown (plain rectangles drawn).",
        ]
        for i, s in enumerate(lines):
            t.text((x + 10, y + 46 + i * 24), s, fill=(60, 60, 60), font=font(15))
    out = HERE.parent.parent / "docs" / "images"
    out.mkdir(parents=True, exist_ok=True)
    sheet.save(out / "solar-cell-mockups.png")
    print("wrote", out / "solar-cell-mockups.png", sheet.size)


if __name__ == "__main__":
    main()
