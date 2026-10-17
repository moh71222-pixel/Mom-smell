"""Vector brand assets for رائحة أمي / RAIHAT UMMI, built from real fonts (no AI)."""
import os
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")

TEAL = "#0D4A52"
TEAL_DARK = "#08343A"
RED = "#A8473A"
OCHRE = "#C99A3C"
SAND = "#E4D2B5"
CREAM = "#F4ECDD"

_cache = {}


def font(name, wght=None):
    key = (name, wght)
    if key in _cache:
        return _cache[key]
    path = os.path.join(FONT_DIR, name)
    tt = TTFont(path)
    if wght is not None and "fvar" in tt:
        tt = instancer.instantiateVariableFont(tt, {"wght": wght})
        tmp = os.path.join(FONT_DIR, f"_{os.path.splitext(name)[0]}_{wght}.ttf")
        tt.save(tmp)
        path = tmp
        tt = TTFont(path)
    with open(path, "rb") as f:
        data = f.read()
    hbfont = hb.Font(hb.Face(data))
    _cache[key] = (tt, hbfont)
    return _cache[key]


def text_path(text, fontname, size, x, y, anchor="middle", wght=None, tracking=0, rtl=None):
    """Return (svg path d, width) for text shaped with HarfBuzz. tracking in em/1000."""
    tt, hbf = font(fontname, wght)
    upem = tt["head"].unitsPerEm
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    if rtl is not None:
        buf.direction = "rtl" if rtl else "ltr"
    hb.shape(hbf, buf, {"kern": True, "liga": True})
    infos, poss = buf.glyph_infos, buf.glyph_positions
    track = tracking * upem / 1000
    total = sum(p.x_advance for p in poss) + track * (len(poss) - 1)
    s = size / upem
    if anchor == "middle":
        x0 = x - total * s / 2
    elif anchor == "end":
        x0 = x - total * s
    else:
        x0 = x
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    pen = SVGPathPen(gs)
    cx = 0
    for i, (info, pos) in enumerate(zip(infos, poss)):
        g = order[info.codepoint]
        tx = x0 + (cx + pos.x_offset) * s
        ty = y - pos.y_offset * s
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, tx, ty)))
        cx += pos.x_advance + (track if i < len(poss) - 1 else 0)
    return pen.getCommands(), total * s


def emblem(cx=500, base=560, scale=1.0, door=TEAL, light=OCHRE, accent=RED, gold=OCHRE, smoke=True):
    """Najdi double door, slightly open; panel tops are the peaks of Aja and Salma."""
    def P(x, y):
        return f"{cx + (x - 500) * scale:.2f},{base + (y - 560) * scale:.2f}"

    def poly(pts, fill):
        return f'<polygon points="{" ".join(P(*p) for p in pts)}" fill="{fill}"/>'

    out = []
    # light spilling through the open gap (widens toward the ground)
    out.append(poly([(492, 240), (508, 240), (540, 560), (460, 560)], light))
    # left panel: Aja — two jagged peaks
    left = [(330, 560), (330, 300), (372, 205), (398, 238), (432, 150), (466, 222), (489, 240), (477, 560)]
    # right panel: Salma — one broad peak with a shoulder
    right = [(523, 560), (511, 236), (538, 196), (556, 214), (590, 140), (630, 222), (670, 290), (670, 560)]
    out.append(poly(left, door))
    out.append(poly(right, door))
    # painted Najdi triangles: top and bottom bands on each panel
    for x0, x1 in ((345, 475), (525, 655)):
        n = 4
        w = (x1 - x0) / n
        for band_y, flip in ((318, False), (506, True)):
            for k in range(n):
                a = x0 + k * w
                col = gold if k % 2 == 0 else accent
                if not flip:
                    out.append(poly([(a, band_y), (a + w, band_y), (a + w / 2, band_y + 26)], col))
                else:
                    out.append(poly([(a, band_y + 26), (a + w, band_y + 26), (a + w / 2, band_y)], col))
        # diamond in the middle of the panel
        mx = (x0 + x1) / 2
        out.append(poly([(mx, 372), (mx + 34, 412), (mx, 452), (mx - 34, 412)], accent))
        out.append(poly([(mx, 392), (mx + 17, 412), (mx, 432), (mx - 17, 412)], gold))
    # door rings
    r = 9 * scale
    for x in (448, 552):
        out.append(f'<circle cx="{P(x, 470).split(",")[0]}" cy="{P(x, 470).split(",")[1]}" r="{r:.2f}" '
                   f'fill="none" stroke="{gold}" stroke-width="{4.5 * scale:.2f}"/>')
    # threshold
    out.append(poly([(312, 560), (688, 560), (688, 574), (312, 574)], door))
    if smoke:
        d = (f"M{P(500, 246)} C{P(470, 205)} {P(530, 170)} {P(502, 128)} "
             f"S{P(476, 70)} {P(508, 34)}")
        out.append(f'<path d="{d}" fill="none" stroke="{light}" stroke-width="{11 * scale:.2f}" '
                   f'stroke-linecap="round"/>')
    return "\n".join(out)


def svg(w, h, body, bg=None):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f"{rect}{body}</svg>")


def wordmark_ar(x, y, size, fill, anchor="middle"):
    d, w = text_path("رائحة أمي", "Alexandria.ttf", size, x, y, anchor, wght=800)
    return f'<path d="{d}" fill="{fill}"/>', w


def wordmark_en(x, y, size, fill, anchor="middle", tracking=180):
    d, w = text_path("RAIHAT UMMI", "Jost.ttf", size, x, y, anchor, wght=600, tracking=tracking)
    return f'<path d="{d}" fill="{fill}"/>', w


def small(text, fontname, x, y, size, fill, anchor="middle", wght=None, tracking=0):
    d, w = text_path(text, fontname, size, x, y, anchor, wght=wght, tracking=tracking)
    return f'<path d="{d}" fill="{fill}"/>', w
