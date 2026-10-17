"""Same frames (logos 2 and 3), different lettering treatments of رائحة أمي."""
import os, sys
import resvg_py
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
sys.path.insert(0, os.path.dirname(__file__))
from brand import TEAL, RED, OCHRE, SAND, CREAM, svg
import badges as Bd

FONTS = os.path.join(os.path.dirname(__file__), "..", "fonts")
BRAND = sys.argv[1]
OUT = sys.argv[4]
os.makedirs(OUT, exist_ok=True)


class Face:
    def __init__(self, path):
        self.tt = TTFont(path)
        self.hb = hb.Font(hb.Face(open(path, "rb").read()))
        self.gs, self.order, self.upem = self.tt.getGlyphSet(), self.tt.getGlyphOrder(), self.tt["head"].unitsPerEm

    def shape(self, text):
        b = hb.Buffer()
        b.add_str(text)
        b.guess_segment_properties()
        hb.shape(self.hb, b, {})
        return [(self.order[i.codepoint], p) for i, p in zip(b.glyph_infos, b.glyph_positions)]

    def boxes(self, text):
        out, cx, gl = [], 0, self.shape(text)
        for g, p in gl:
            bp = BoundsPen(self.gs)
            self.gs[g].draw(TransformPen(bp, (1, 0, 0, 1, cx + p.x_offset, p.y_offset)))
            if bp.bounds:
                out.append(bp.bounds)
            cx += p.x_advance
        return out, cx

    def path(self, text, s, x_left, y):
        pen, cx = SVGPathPen(self.gs), 0
        for g, p in self.shape(text):
            self.gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x_left + (cx + p.x_offset) * s, y - p.y_offset * s)))
            cx += p.x_advance
        return pen.getCommands()


KUFI = Face(BRAND)
RUQAA = Face(os.path.join(FONTS, "ArefRuqaa-Bold.ttf"))
AMIRI = Face(os.path.join(FONTS, "Amiri-Bold.ttf"))


def two_lines(face, t1, t2, cx, top, width, height, c1, c2, scale2=1.0, pad=50):
    """Stack t1 over t2 (t2 optionally scaled), centred, fitted, never touching."""
    b1, w1 = face.boxes(t1)
    b2, w2 = face.boxes(t2)
    b2 = [(a * scale2, b * scale2, c * scale2, d * scale2) for a, b, c, d in b2]
    w2 *= scale2
    gap = 0
    for a in b1:
        for b in b2:
            if a[0] - w1 / 2 - pad < b[2] - w2 / 2 and b[0] - w2 / 2 - pad < a[2] - w1 / 2:
                gap = max(gap, -a[1] + b[3] + pad)
    top1 = max(b[3] for b in b1)
    bot2 = min(b[1] for b in b2)
    H, Wd = top1 + gap - bot2, max(w1, w2)
    s = min(width / Wd, height / H)
    y1 = top + top1 * s
    y2 = y1 + gap * s
    p1 = face.path(t1, s, cx - w1 * s / 2, y1)
    p2 = face.path(t2, s * scale2, cx - w2 * s / 2, y2)
    return f'<path d="{p1}" fill="{c1}"/><path d="{p2}" fill="{c2}"/>', top + H * s


def justified(face, t1, t2):
    """Add kashida to the shorter word until both lines are the same width."""
    _, w1 = face.boxes(t1)
    for n in range(0, 20):
        cand = t2[0:2] + "ـ" * n + t2[2:]
        if face.boxes(cand)[1] >= w1 * 0.97:
            return cand
    return t2


VARIANTS = {
    "1-كوفي-ممتد": lambda cx, top, w, h, ink: two_lines(KUFI, "رائحة", justified(KUFI, "رائحة", "أمي"),
                                                          cx, top, w, h, ink, ink),
    "2-أمي-بارزة": lambda cx, top, w, h, ink: two_lines(KUFI, "رائحة", "أمي", cx, top, w, h, RED, ink, 1.55),
    "3-لونين": lambda cx, top, w, h, ink: two_lines(KUFI, "رائحة", justified(KUFI, "رائحة", "أمي"),
                                                     cx, top, w, h, ink, RED),
    "4-رقعة": lambda cx, top, w, h, ink: two_lines(RUQAA, "رائحة", "أمي", cx, top, w, h, ink, ink, 1.15),
    "5-نسخ": lambda cx, top, w, h, ink: two_lines(AMIRI, "رائحة", "أمي", cx, top, w, h, ink, RED, 1.2),
}


def save(name, s, width=1400):
    open(os.path.join(OUT, name + ".svg"), "w").write(s)
    open(os.path.join(OUT, name + ".png"), "wb").write(bytes(resvg_py.svg_to_bytes(svg_string=s, width=width)))


for key, fn in VARIANTS.items():
    Bd.stacked = fn
    save(f"مربع-{key}", Bd.square(hail=True))
    save(f"باب-{key}", Bd.door(hail=True))
print("typo ok")
