"""Creative arrangements of رائحة أمي using only the official brand font (Raihat Kufi), one colour."""
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

FONT, OUT = sys.argv[1], sys.argv[4]
os.makedirs(OUT, exist_ok=True)
TT = TTFont(FONT)
HB = hb.Font(hb.Face(open(FONT, "rb").read()))
GS, ORDER = TT.getGlyphSet(), TT.getGlyphOrder()
ALIFS = {"uni0627", "uni0623", "uniFE8E", "uniFE84"}


def shape(text):
    b = hb.Buffer()
    b.add_str(text)
    b.guess_segment_properties()
    hb.shape(HB, b, {})
    return [(ORDER[i.codepoint], p) for i, p in zip(b.glyph_infos, b.glyph_positions)]


class Line:
    """A shaped word in font units; `tall` stretches alifs upward (y-scale from the baseline)."""

    def __init__(self, text, tall=1.0, scale=1.0):
        self.items, self.boxes, self.alifs, cx = [], [], [], 0
        for g, p in shape(text):
            sy = tall if g in ALIFS else 1.0
            tf = (scale, 0, 0, scale * sy, (cx + p.x_offset) * scale, p.y_offset * scale)
            bp = BoundsPen(GS)
            GS[g].draw(TransformPen(bp, tf))
            if bp.bounds:
                self.boxes.append(bp.bounds)
                if g in ALIFS:
                    self.alifs.append(bp.bounds)
            self.items.append((g, tf))
            cx += p.x_advance
        self.width = cx * scale
        self.top = max(b[3] for b in self.boxes)
        self.bottom = min(b[1] for b in self.boxes)

    def path(self, s, x_left, y):
        pen = SVGPathPen(GS)
        for g, (a, b, c, d, e, f) in self.items:
            GS[g].draw(TransformPen(pen, (a * s, 0, 0, -d * s, x_left + e * s, y - f * s)))
        return pen.getCommands()


def gap_between(l1, l2, dx1, dx2, pad):
    need = -10 ** 9
    for a in l1.boxes:
        for b in l2.boxes:
            if a[0] + dx1 - pad < b[2] + dx2 and b[0] + dx2 - pad < a[2] + dx1:
                need = max(need, -a[1] + b[3] + pad)
    return need


def compose(l1, l2, align, pad=45):
    """Return offsets (dx1, dx2, gap) in font units; align: centre | right | nest."""
    W = max(l1.width, l2.width)
    if align == "centre":
        dx1, dx2 = (W - l1.width) / 2, (W - l2.width) / 2
    elif align == "right":
        dx1, dx2 = W - l1.width, W - l2.width
    elif align == "diagonal":  # line 2 steps down-left, letters overlap in height
        best = None
        for dx in range(-int(l2.width), int(l1.width * 0.6), 10):
            dx1 = max(0, -dx)
            dx2 = dx1 + dx
            g = max(gap_between(l1, l2, dx1, dx2, 60), l1.top * 0.35)
            span = max(dx1 + l1.width, dx2 + l2.width)
            score = min(560 / span, 470 / (l1.top + g - l2.bottom))
            if best is None or score > best[0]:
                best = (score, dx1, dx2, g, span)
        _, dx1, dx2, gap, W = best
        return dx1, dx2, gap, W
    else:  # nest: line 2 slides left under line 1 so the letters interlock
        dx1, best = W - l1.width, None
        for dx in range(0, int(W - l2.width) + 1, 10):
            g = gap_between(l1, l2, dx1, dx, pad)
            if best is None or g < best[1] - 1:
                best = (dx, g)
        dx2 = best[0]
    gap = max(gap_between(l1, l2, dx1, dx2, pad), l1.top * 0.55)
    return dx1, dx2, gap, W


def block(t1, t2, align="centre", tall=1.0, s2=1.0, kashida=0, caps=False):
    if kashida:
        t2 = t2[:2] + "ـ" * kashida + t2[2:]
    l1, l2 = Line(t1, tall), Line(t2, tall, s2)
    dx1, dx2, gap, W = compose(l1, l2, align)
    H = l1.top + gap - l2.bottom
    if caps:
        H += 140

    def stacked(cx, top, width, height, ink):
        s = min(width / W, height / H)
        x0 = cx - W * s / 2
        y1 = top + (l1.top + (140 if caps else 0)) * s
        y2 = y1 + gap * s
        d1, d2 = l1.path(s, x0 + dx1 * s, y1), l2.path(s, x0 + dx2 * s, y2)
        out = f'<path d="{d1}" fill="{ink}"/><path d="{d2}" fill="{ink}"/>'
        if caps:  # fort crenellation on top of every alif
            for line, dx, y in ((l1, dx1, y1), (l2, dx2, y2)):
                for a in line.alifs:
                    xa, xb = x0 + (dx + a[0]) * s, x0 + (dx + a[2]) * s
                    yt = y - a[3] * s
                    w = xb - xa
                    out += Bd.poly([(xa - w * .25, yt - 4), (xb + w * .25, yt - 4), ((xa + xb) / 2, yt - w * 1.1)], OCHRE)
        return out, top + H * s
    return stacked


def fit_kashida(t1, t2):
    w1 = Line(t1).width
    for n in range(20):
        if Line(t2[:2] + "ـ" * n + t2[2:]).width >= w1 * 0.98:
            return n
    return 0


K = fit_kashida("رائحة", "أمي")
VARIANTS = {
    "1-مربع-ممتد": block("رائحة", "أمي", "centre", kashida=K),
    "2-متدرج": block("رائحة", "أمي", "diagonal"),
    "3-أمي-كبيرة": block("رائحة", "أمي", "centre", s2=1.6),
}


def save(name, s, width=1400):
    open(os.path.join(OUT, name + ".svg"), "w").write(s)
    open(os.path.join(OUT, name + ".png"), "wb").write(bytes(resvg_py.svg_to_bytes(svg_string=s, width=width)))


for key, fn in VARIANTS.items():
    Bd.stacked = fn
    save(f"مربع-{key}", Bd.square(hail=True))
    save(f"باب-{key}", Bd.door(hail=True))
print("lettering ok, kashida", K)
