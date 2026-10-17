"""Raihat Ummi brand book (vector PDF) + print-ready labels and stickers."""
import os, re, sys, io, math
SCR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BRAND_FONT = os.path.join(SCR, "out", "RaihatKufi-Regular.ttf")
sys.argv = [sys.argv[0], BRAND_FONT, "/tmp/_bk_wm", "/tmp/_bk_badges", "/tmp/_bk_letter"]
sys.path.insert(0, os.path.dirname(__file__))
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import cairosvg, resvg_py
from pypdf import PdfWriter, PdfReader
import lettering as Lt
import badges as Bd
from brand import TEAL, TEAL_DARK, RED, OCHRE, SAND, CREAM

Bd.stacked = Lt.block("رائحة", "أمي", "diagonal")
STACK = Bd.stacked
OUT = os.environ["BOOK_OUT"]
FD = os.path.join(SCR, "fonts")
INK = "#2B2522"
MUTED = "#6E6259"

# ------------------------------------------------------------------ text
class Face:
    def __init__(self, path):
        self.tt = TTFont(path)
        self.hb = hb.Font(hb.Face(open(path, "rb").read()))
        self.gs, self.order, self.upem = self.tt.getGlyphSet(), self.tt.getGlyphOrder(), self.tt["head"].unitsPerEm

FACES = {k: Face(v) for k, v in {
    "kufi": BRAND_FONT,
    "reg": os.path.join(FD, "Almarai-Regular.ttf"),
    "bold": os.path.join(FD, "Almarai-Bold.ttf"),
    "xbold": os.path.join(FD, "Almarai-ExtraBold.ttf"),
    "en": os.path.join(FD, "_Jost_400.ttf"),
    "enm": os.path.join(FD, "_Jost_500.ttf"),
    "enb": os.path.join(FD, "_Jost_600.ttf"),
}.items()}
AR = re.compile(r"[؀-ۿﭐ-﻿]")
LTR = re.compile(r"[A-Za-z0-9#@][A-Za-z0-9#@.,:%/+\-'&_ ]*[A-Za-z0-9%)]|[A-Za-z0-9#@%]")


def _shape(face, text, rtl):
    b = hb.Buffer()
    b.add_str(text)
    b.guess_segment_properties()
    b.direction = "rtl" if rtl else "ltr"
    hb.shape(face.hb, b, {"kern": True})
    return [(face.order[i.codepoint], p) for i, p in zip(b.glyph_infos, b.glyph_positions)]


def _runs(text):
    if not AR.search(text):
        return [(text, False)]
    out, pos = [], 0
    for m in LTR.finditer(text):
        if m.start() > pos:
            out.append((text[pos:m.start()], True))
        out.append((m.group(), False))
        pos = m.end()
    if pos < len(text):
        out.append((text[pos:], True))
    return out


def measure(text, font, size, track=0):
    f = FACES[font]
    s = size / f.upem
    w = 0
    for seg, rtl in _runs(text):
        gl = _shape(f, seg, rtl)
        w += sum(p.x_advance for _, p in gl) * s + track * max(0, len(gl) - 1)
    return w


def T(text, font, size, x, y, fill=INK, anchor="end", track=0):
    """Draw one line; RTL base if it contains Arabic. anchor end = x is the right edge."""
    f = FACES[font]
    s = size / f.upem
    rtl_base = bool(AR.search(text))
    segs = []
    for seg, rtl in _runs(text):
        gl = _shape(f, seg, rtl)
        segs.append((gl, sum(p.x_advance for _, p in gl) * s + track * max(0, len(gl) - 1)))
    total = sum(w for _, w in segs)
    left = {"end": x - total, "middle": x - total / 2, "start": x}[anchor]
    order = list(reversed(segs)) if rtl_base else segs
    out, cx = [], left
    for gl, w in order:
        gx = cx
        for g, p in gl:
            pen = SVGPathPen(f.gs)
            f.gs[g].draw(TransformPen(pen, (s, 0, 0, -s, gx + p.x_offset * s, y - p.y_offset * s)))
            d = pen.getCommands()
            if d:
                out.append(f'<path d="{d}" fill="{fill}"/>')
            gx += p.x_advance * s + track
        cx += w
    return "".join(out)


def para(text, font, size, x, y, width, fill=INK, lh=1.75, anchor="end"):
    """Wrapped paragraph; returns (svg, y_after)."""
    out, line = [], ""
    for word in text.split():
        cand = (line + " " + word).strip()
        if line and measure(cand, font, size) > width:
            out.append(line)
            line = word
        else:
            line = cand
    if line:
        out.append(line)
    svg = "".join(T(l, font, size, x, y + i * size * lh, fill, anchor) for i, l in enumerate(out))
    return svg, y + len(out) * size * lh


# ------------------------------------------------------------------ shapes
poly, diamond, tri_row, ridge = Bd.poly, Bd.diamond, Bd.tri_row, Bd.ridge


def rect(x, y, w, h, fill, rx=0, stroke=None, sw=0):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{st}/>'


def nest(svg_str, x, y, w, h=None, vb=None):
    m = re.match(r'<svg[^>]*viewBox="([^"]+)"[^>]*>', svg_str)
    vb = vb or m.group(1)
    vw, vh = [float(v) for v in vb.split()[2:]]
    h = h or w * vh / vw
    inner = svg_str[m.end():svg_str.rfind("</svg>")]
    return (f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vb}" '
            f'preserveAspectRatio="xMidYMid meet" overflow="hidden">{inner}</svg>')


MARK_VB = "122 40 756 740"
LOGO = Bd.square(bg=None)
LOGO_REV = Bd.square(bg=None, frame=CREAM, ink=CREAM, tag=OCHRE)
LOGO_HAIL = Bd.square(bg=None, hail=True)
LOGO_DOOR = Bd.door(bg=None)


def lettering(cx, top, w, h, ink):
    return STACK(cx, top, w, h, ink)[0]


def sadu_strip(x0, x1, y, h, cols=(OCHRE, RED), bg=None):
    out = [rect(x0, y, x1 - x0, h, bg)] if bg else []
    out.append(tri_row(x0, x1, y, h * .5, cols, down=True, n=max(3, round((x1 - x0) / (h * .9)))))
    out.append(tri_row(x0, x1, y + h * .5, h * .5, cols[::-1], n=max(3, round((x1 - x0) / (h * .9)))))
    return "".join(out)


def svgdoc(w, h, body, bg=None):
    r = rect(0, 0, w, h, bg) if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{r}{body}</svg>'


# ------------------------------------------------------------------ products
CATS = [
    ("معمول", "BUKHOOR", TEAL, "بخور يدوي معجون بالزيوت العطرية، يُصنع على دفعات صغيرة", [
        ("الملكي", "80 جرام", "130"), ("المخصوص", "100 جرام", "250"), ("العرايسي", "80 جرام", "120")]),
    ("عود", "OUD", RED, "قطع عود مختارة للمجالس والمناسبات", [
        ("عود مسقى", "80 جرام", "95"), ("عود طبيعي", "80 جرام", "250")]),
    ("مرشات", "ROOM SPRAY", OCHRE, "معطرات مفارش ومجالس بريحة البيت", [
        ("أسيل", "500 مل", "80"), ("شهد", "500 مل", "80"), ("سديم", "500 مل", "80")]),
    ("أدهان", "PERFUME OIL", TEAL_DARK, "زيوت عطرية مركّزة للجسم والملابس", [
        ("فتشة العروس", "تولة", "70"), ("خمرية الزعفران", "تولة", "60"),
        ("خمرية المسك", "تولة", "60"), ("دهن العود الطبيعي", "ربع تولة", "120")]),
]


def fit(text, font, max_w, max_size):
    w = measure(text, font, 100)
    return min(max_size, 100 * max_w / w)


# ------------------------------------------------------------------ labels (print units: 10 px = 1 mm)
def jar_label(name, cat, size_txt, accent):
    """Round sticker, 60 mm."""
    W = 600
    c = W / 2
    o = [f'<circle cx="{c}" cy="{c}" r="300" fill="{accent}"/>',
         f'<circle cx="{c}" cy="{c}" r="262" fill="{CREAM}"/>',
         f'<circle cx="{c}" cy="{c}" r="248" fill="none" stroke="{OCHRE}" stroke-width="3"/>']
    n = 40
    for k in range(n):  # ring of tiny triangles on the coloured band
        a = 2 * math.pi * k / n
        tip = (c + 284 * math.cos(a), c + 284 * math.sin(a))
        b1 = (c + 266 * math.cos(a - .05), c + 266 * math.sin(a - .05))
        b2 = (c + 266 * math.cos(a + .05), c + 266 * math.sin(a + .05))
        o.append(poly([b1, b2, tip], OCHRE if k % 2 == 0 else CREAM))
    o.append(lettering(c, 92, 170, 95, TEAL))
    o.append(Bd.divider(c, 215, 70, OCHRE, RED))
    sz = fit(name, "kufi", 360, 96)
    o.append(T(name, "kufi", sz, c, 330, accent if accent != OCHRE else TEAL, "middle"))
    o.append(T(cat, "bold", 30, c, 385, OCHRE, "middle"))
    o.append(T(size_txt, "xbold", 30, c, 440, TEAL, "middle"))
    o.append(T("صُنع يدوياً في حائل", "reg", 20, c, 488, MUTED, "middle"))
    o.append(T("رقم التشغيلة ........", "reg", 18, c, 520, MUTED, "middle"))
    return svgdoc(W, W, "".join(o))


def spray_label(name, size_txt, accent):
    """Rectangular wrap label, 70 x 110 mm."""
    W, H = 700, 1100
    o = [rect(0, 0, W, H, CREAM), rect(14, 14, W - 28, H - 28, "none", stroke=TEAL, sw=18),
         rect(40, 40, W - 80, H - 80, "none", stroke=OCHRE, sw=3)]
    o.append(tri_row(70, W - 70, 56, 26, (OCHRE, RED), down=True, n=13))
    o.append(nest(LOGO, 225, 105, 250, vb=MARK_VB))
    sz = fit(name, "kufi", 480, 170)
    o.append(T(name, "kufi", sz, W / 2, 560, TEAL, "middle"))
    o.append(Bd.divider(W / 2, 615, 140, OCHRE, RED))
    o.append(T("معطر مفارش ومجالس", "bold", 36, W / 2, 685, accent if accent != OCHRE else RED, "middle"))
    o.append(T(size_txt, "xbold", 44, W / 2, 750, TEAL, "middle"))
    o.append(T("رشّه على المفارش والستائر من مسافة ٢٠ سم", "reg", 22, W / 2, 815, MUTED, "middle"))
    o.append(T("رقم التشغيلة ........   تاريخ الإنتاج ........", "reg", 20, W / 2, 860, MUTED, "middle"))
    o.append(ridge(44, W - 44, H - 44, 110, RED))
    o.append(T("من أرض حاتم · حائل", "bold", 24, W / 2, H - 70, CREAM, "middle"))
    return svgdoc(W, H, "".join(o))


def oil_label(name, size_txt):
    """Small bottle label, 50 x 30 mm."""
    W, H = 500, 300
    o = [rect(0, 0, W, H, CREAM), rect(W - 90, 0, 90, H, TEAL_DARK)]
    for k in range(5):
        o.append(diamond(W - 45, 40 + k * 55, 14, OCHRE if k % 2 == 0 else RED))
    o.append(rect(10, 10, W - 110, H - 20, "none", stroke=OCHRE, sw=3))
    o.append(T("رائحة أمي", "kufi", 30, W - 125, 62, TEAL, "end"))
    sz = fit(name, "kufi", 340, 64)
    o.append(T(name, "kufi", sz, W - 125, 158, TEAL_DARK, "end"))
    o.append(T("دهن عطري · " + size_txt, "bold", 24, W - 125, 210, RED, "end"))
    o.append(T("صُنع يدوياً في حائل · رقم التشغيلة ......", "reg", 15, W - 125, 255, MUTED, "end"))
    return svgdoc(W, H, "".join(o))


def seal_sticker():
    W = 500
    c = W / 2
    o = [f'<circle cx="{c}" cy="{c}" r="250" fill="{TEAL}"/>',
         f'<circle cx="{c}" cy="{c}" r="228" fill="none" stroke="{OCHRE}" stroke-width="4"/>']
    n = 36
    for k in range(n):
        a = 2 * math.pi * k / n
        tip = (c + 200 * math.cos(a), c + 200 * math.sin(a))
        b1 = (c + 222 * math.cos(a - .06), c + 222 * math.sin(a - .06))
        b2 = (c + 222 * math.cos(a + .06), c + 222 * math.sin(a + .06))
        o.append(poly([b1, b2, tip], OCHRE if k % 2 == 0 else RED))
    o.append(lettering(c, 120, 250, 190, CREAM))
    o.append(Bd.divider(c, 345, 80, OCHRE, RED))
    o.append(T("حائل", "bold", 30, c, 395, OCHRE, "middle"))
    return svgdoc(W, W, "".join(o))


def thanks_sticker():
    W, H = 800, 400
    o = [rect(0, 0, W, H, SAND, rx=40), rect(16, 16, W - 32, H - 32, "none", rx=28, stroke=TEAL, sw=10)]
    o.append(nest(LOGO, W - 300, 55, 250, vb=MARK_VB))
    o.append(T("شكراً لأنك", "kufi", 62, W - 330, 150, TEAL, "end"))
    o.append(T("من أهل البيت", "kufi", 62, W - 330, 240, RED, "end"))
    o.append(tri_row(60, W - 330, 285, 26, (OCHRE, RED), n=12))
    o.append(T("@raihatummi", "enm", 28, W - 330, 355, TEAL, "end"))
    return svgdoc(W, H, "".join(o))


def handmade_sticker():
    W = 400
    c = W / 2
    o = [f'<circle cx="{c}" cy="{c}" r="200" fill="{OCHRE}"/>',
         f'<circle cx="{c}" cy="{c}" r="182" fill="none" stroke="{CREAM}" stroke-width="4"/>']
    o.append(Bd.mabkhara(c, 175, 110, TEAL, RED, CREAM))
    o.append(T("صُنع يدوياً", "kufi", 50, c, 245, TEAL, "middle"))
    o.append(T("في حائل", "kufi", 50, c, 305, CREAM, "middle"))
    return svgdoc(W, W, "".join(o))


def batch_sticker():
    W, H = 600, 220
    o = [rect(0, 0, W, H, CREAM, rx=20), rect(0, 0, 110, H, RED, rx=20), rect(60, 0, 50, H, RED)]
    o.append(Bd.diamond(55, H / 2, 34, OCHRE, hole=RED))
    o.append(T("رقم التشغيلة", "bold", 30, W - 30, 70, TEAL, "end"))
    o.append(f'<line x1="140" y1="80" x2="{W-230}" y2="80" stroke="{MUTED}" stroke-width="2" stroke-dasharray="6 6"/>')
    o.append(T("تاريخ الإنتاج", "bold", 30, W - 30, 150, TEAL, "end"))
    o.append(f'<line x1="140" y1="160" x2="{W-230}" y2="160" stroke="{MUTED}" stroke-width="2" stroke-dasharray="6 6"/>')
    return svgdoc(W, H, "".join(o))


def gift_sticker():
    W, H = 600, 300
    o = [rect(0, 0, W, H, TEAL, rx=150), rect(14, 14, W - 28, H - 28, "none", rx=136, stroke=OCHRE, sw=4)]
    o.append(T("هدية من القلب", "kufi", 70, W / 2, 150, CREAM, "middle"))
    o.append(tri_row(160, W - 160, 185, 22, (OCHRE, RED), n=9))
    o.append(T("رائحة أمي", "bold", 28, W / 2, 255, OCHRE, "middle"))
    return svgdoc(W, H, "".join(o))


LABELS = {}
for cat, en, acc, desc, items in CATS:
    for name, size_txt, price in items:
        if cat in ("معمول", "عود"):
            LABELS[name] = ("jar", jar_label(name, cat, size_txt, acc), 60, 60)
        elif cat == "مرشات":
            LABELS[name] = ("spray", spray_label(name, size_txt, acc), 70, 110)
        else:
            LABELS[name] = ("oil", oil_label(name, size_txt), 50, 30)
STICKERS = {
    "ختم-الإغلاق": (seal_sticker(), 50, 50),
    "شكراً": (thanks_sticker(), 80, 40),
    "صنع-يدوياً": (handmade_sticker(), 40, 40),
    "رقم-التشغيلة": (batch_sticker(), 60, 22),
    "هدية": (gift_sticker(), 60, 30),
}

# ------------------------------------------------------------------ packaging & stationery
def gift_box_lid():
    W, H = 1400, 1000
    o = [rect(0, 0, W, H, TEAL), sadu_strip(0, W, 0, 70), sadu_strip(0, W, H - 70, 70)]
    o.append(rect(60, 110, W - 120, H - 220, "none", stroke=OCHRE, sw=4))
    o.append(nest(LOGO_REV, W / 2 - 330, 140, 660))
    return svgdoc(W, H, "".join(o))


def card_front():
    W, H = 1480, 1050
    o = [rect(0, 0, W, H, SAND), nest(LOGO, W / 2 - 360, 60, 720)]
    return svgdoc(W, H, "".join(o))


def card_back():
    W, H = 1480, 1050
    o = [rect(0, 0, W, H, CREAM), rect(40, 40, W - 80, H - 80, "none", stroke=TEAL, sw=14),
         tri_row(110, W - 110, 80, 34, (OCHRE, RED), down=True, n=24)]
    o.append(T("أهلاً فيك في بيت أمي", "kufi", 92, W / 2, 300, TEAL, "middle"))
    msg = ("كل علبة من «رائحة أمي» انخلطت باليد في حائل، على دفعات صغيرة، "
           "بنفس الخلطات اللي ورثناها من البيت. نتمنى ريحتها تفتح لك باب ذكرى حلوة.")
    s, y = para(msg, "reg", 40, W / 2, 420, 1050, INK, 1.8, "middle")
    o.append(s)
    o.append(Bd.divider(W / 2, y + 40, 160, OCHRE, RED))
    o.append(T("@raihatummi  ·  raihatummi.com", "enm", 36, W / 2, y + 130, TEAL, "middle"))
    o.append(ridge(54, W - 54, H - 54, 120, RED))
    return svgdoc(W, H, "".join(o))


def biz_front():
    W, H = 900, 500
    o = [rect(0, 0, W, H, TEAL), sadu_strip(0, W, H - 40, 40)]
    o.append(lettering(W / 2, 60, 360, 270, CREAM))
    o.append(T("RAIHAT UMMI", "enb", 34, W / 2, 400, OCHRE, "middle", track=8))
    return svgdoc(W, H, "".join(o))


def biz_back():
    W, H = 900, 500
    o = [rect(0, 0, W, H, CREAM), rect(0, 0, 40, H, RED), tri_row(0, 40, 0, 0, (OCHRE,), n=1)]
    for k in range(7):
        o.append(diamond(20, 45 + k * 68, 11, OCHRE))
    o.append(nest(LOGO, 70, 70, 260, vb=MARK_VB))
    o.append(T("الاسم الكامل", "xbold", 44, W - 50, 120, TEAL, "end"))
    o.append(T("المؤسس", "reg", 28, W - 50, 168, OCHRE, "end"))
    for i, line in enumerate(["05X XXX XXXX", "@raihatummi", "raihatummi.com", "حائل · المملكة العربية السعودية"]):
        o.append(T(line, "reg" if AR.search(line) else "en", 26, W - 50, 260 + i * 52, INK, "end"))
    return svgdoc(W, H, "".join(o))


# ------------------------------------------------------------------ social
def icon_glyph(kind, c, col):
    if kind == "mab":
        return Bd.mabkhara(c, c + 45, 100, col, RED, col)
    if kind == "oud":
        return poly([(c - 50, c + 25), (c - 20, c - 40), (c + 10, c - 30), (c + 45, c - 55),
                     (c + 55, c - 10), (c + 25, c + 45), (c - 10, c + 30)], col)
    if kind == "spray":
        return (rect(c - 32, c - 20, 64, 80, col, rx=10) + rect(c - 12, c - 48, 24, 28, col)
                + rect(c - 45, c - 50, 33, 12, col))
    if kind == "oil":
        return (f'<path d="M{c},{c-60} C{c+40},{c-5} {c+45},{c+20} {c+45},{c+30} '
                f'A45,45 0 0 1 {c-45},{c+30} C{c-45},{c+20} {c-40},{c-5} {c},{c-60} Z" fill="{col}"/>')
    if kind == "gift":
        return (rect(c - 50, c - 15, 100, 70, col) + rect(c - 58, c - 35, 116, 22, col)
                + rect(c - 6, c - 35, 12, 90, RED) + diamond(c, c - 48, 16, RED))
    return ""


def highlight(kind, label):
    W = 400
    c = 200
    o = [f'<circle cx="{c}" cy="{c - 20}" r="150" fill="{TEAL}"/>',
         f'<circle cx="{c}" cy="{c - 20}" r="136" fill="none" stroke="{OCHRE}" stroke-width="4"/>']
    o.append(f'<g transform="translate(0,-20)">{icon_glyph(kind, c, CREAM)}</g>')
    o.append(T(label, "bold", 34, c, 385, TEAL, "middle"))
    return o


def post_template():
    W = 1080
    o = [rect(0, 0, W, W, SAND), rect(40, 40, W - 80, W - 80, "none", stroke=TEAL, sw=22),
         rect(76, 76, W - 152, W - 152, "none", stroke=OCHRE, sw=4),
         tri_row(130, W - 130, 96, 30, (OCHRE, RED), down=True, n=19)]
    o.append(rect(150, 170, W - 300, 560, "#D8C3A1"))
    o.append(T("صورة المنتج", "bold", 40, W / 2, 470, MUTED, "middle"))
    o.append(T("المخصوص", "kufi", 96, W - 150, 860, TEAL, "end"))
    o.append(T("معمول · 100 جرام", "bold", 36, W - 150, 920, RED, "end"))
    o.append(nest(LOGO, 150, 770, 190, vb=MARK_VB))
    return svgdoc(W, W, "".join(o))


def story_template():
    W, H = 1080, 1920
    o = [rect(0, 0, W, H, TEAL), sadu_strip(0, W, 0, 80), sadu_strip(0, W, H - 80, 80)]
    o.append(lettering(W / 2, 200, 560, 380, CREAM))
    o.append(rect(120, 680, W - 240, 760, "#0F5660"))
    o.append(T("صورة / فيديو", "bold", 44, W / 2, 1080, OCHRE, "middle"))
    o.append(T("ريحة البيت اللي تعرفه", "kufi", 74, W / 2, 1580, CREAM, "middle"))
    o.append(T("اطلب الحين · @raihatummi", "bold", 40, W / 2, 1680, OCHRE, "middle"))
    return svgdoc(W, H, "".join(o))


def avatar():
    W = 1000
    o = [f'<clipPath id="av"><circle cx="500" cy="500" r="500"/></clipPath>',
         f'<g clip-path="url(#av)">{rect(0, 0, W, W, SAND)}{nest(LOGO, 110, 115, 780, vb=MARK_VB)}</g>']
    return svgdoc(W, W, "".join(o))


# ------------------------------------------------------------------ pages
PW, PH = 1600, 1000
PAGES = []


def page(title, subtitle, body, num, bg=CREAM, dark=False):
    head = TEAL if not dark else CREAM
    o = [rect(0, 0, PW, PH, bg), tri_row(0, PW, 0, 18, (OCHRE, RED), down=True, n=64)]
    if title:
        o.append(T(title, "kufi", 54, PW - 90, 120, head, "end"))
        if subtitle:
            o.append(T(subtitle, "reg", 22, PW - 90, 165, MUTED if not dark else SAND, "end"))
        o.append(diamond(PW - 72, 103, 10, RED))
    o.append(body)
    o.append(T(f"{num:02d}", "enm", 20, 80, PH - 40, MUTED if not dark else SAND, "start"))
    o.append(T("رائحة أمي · دليل الهوية البصرية", "reg", 18, PW - 80, PH - 40, MUTED if not dark else SAND, "end"))
    PAGES.append(svgdoc(PW, PH, "".join(o)))


def card(x, y, w, h, title, text, accent=TEAL, fill="#EFE4D2"):
    o = [rect(x, y, w, h, fill, rx=14), rect(x + w - 10, y, 10, h, accent)]
    o.append(T(title, "xbold", 28, x + w - 34, y + 52, accent, "end"))
    s, _ = para(text, "reg", 21, x + w - 34, y + 98, w - 68, INK, 1.7)
    o.append(s)
    return "".join(o)


def label_box(x, y, w, label, sub=None):
    o = T(label, "bold", 22, x + w / 2, y, TEAL, "middle")
    if sub:
        o += T(sub, "reg", 17, x + w / 2, y + 30, MUTED, "middle")
    return o


n = 1
# 1 cover
cov = [rect(0, 0, PW, PH, TEAL), sadu_strip(0, PW, PH - 60, 60)]
cov.append(nest(LOGO_REV, 90, 150, 500))
cov.append(T("دليل الهوية البصرية", "kufi", 78, PW - 120, 420, CREAM, "end"))
cov.append(T("BRAND IDENTITY GUIDELINES", "enb", 30, PW - 120, 480, OCHRE, "end", track=6))
cov.append(f'<line x1="{PW-520}" y1="530" x2="{PW-120}" y2="530" stroke="{OCHRE}" stroke-width="3"/>')
cov.append(T("الشعار · الألوان · الخطوط · العناصر · المنتجات · الملصقات · التغليف", "reg", 24, PW - 120, 590, SAND, "end"))
cov.append(T("الإصدار الأول · 2026", "bold", 24, PW - 120, 640, OCHRE, "end"))
PAGES.append(svgdoc(PW, PH, "".join(cov)))
n += 1

# 2 contents
toc = ["قصة البراند", "قصة الشعار", "نسخ الشعار", "الأيقونة والشعار الأفقي", "قواعد استخدام الشعار",
       "الألوان", "الخطوط", "العناصر والنقوش", "صوت البراند", "المنتجات", "ملصقات المعمول والعود",
       "ملصقات المرشات", "ملصقات الأدهان", "الستكرات", "التغليف", "السوشال ميديا", "القرطاسية",
       "مواصفات الطباعة"]
b = []
for i, t in enumerate(toc):
    col, row = i // 9, i % 9
    x = PW - 120 - col * 640
    y = 270 + row * 70
    b.append(T(f"{i + 3:02d}", "enb", 26, x, y, OCHRE, "end"))
    b.append(T(t, "bold", 30, x - 70, y, TEAL, "end"))
    b.append(f'<line x1="{x-560}" y1="{y+22}" x2="{x}" y2="{y+22}" stroke="#D9CBB3" stroke-width="1.5"/>')
b.append(nest(LOGO, 90, 300, 300, vb=MARK_VB))
page("المحتويات", None, "".join(b), n); n += 1

# 3 brand story
b = []
story = [
    "«رائحة أمي» مو مجرد اسم؛ هي الريحة اللي تستقبلك أول ما ينفتح باب البيت: بخور يوم الجمعة، ودهن العود على ثوب العيد، ومعمول يطلع دخانه من المبخرة قبل وصول الضيوف.",
    "من حائل، أرض حاتم الطائي ورمز الكرم عند العرب، نصنع بخورنا ودهوننا يدوياً على دفعات صغيرة، بنفس الخلطات اللي تعلمناها في البيت، وكل منتج يحمل رقم تشغيلته.",
    "وعدنا بسيط: كل علبة تفتحها، تفتح معها باب بيت أمي.",
]
y = 250
for k, ptxt in enumerate(story):
    s, y = para(ptxt, "reg" if k < 2 else "kufi", 27 if k < 2 else 40, PW - 90, y, 820, INK if k < 2 else RED, 1.85)
    b.append(s)
    y += 30
b.append(T("النص مقترح، ويُعدّل حسب قصتكم الحقيقية.", "reg", 18, PW - 90, y + 10, MUTED, "end"))
cards = [("الرسالة", "نقدم طيباً سعودياً أصيلاً مصنوعاً باليد، يحمل دفء البيت وكرم حائل.", TEAL),
         ("الرؤية", "أن تكون «رائحة أمي» الاسم الأول لبخور البيت وهدايا الطيب في المملكة.", RED),
         ("القيم", "الكرم · الأصالة · الصنعة اليدوية · الثقة والشفافية", OCHRE)]
for i, (t, txt, a) in enumerate(cards):
    b.append(card(80, 230 + i * 220, 560, 190, t, txt, a))
page("قصة البراند", "من نحن، ولماذا نوجد", "".join(b), n); n += 1

# 4 logo story
b = []
lx, ly, lw = 80, 200, 640
b.append(rect(lx - 20, ly - 20, lw + 40, lw * 990 / 1000 + 40, SAND, rx=16))
b.append(nest(LOGO, lx, ly, lw))
sc = lw / 1000
pts = [(160, 300, "الإطار المزدوج", "جدار البيت الطيني وإطار بابه؛ البيت اللي يجمعنا."),
       (500, 120, "شريط المثلثات", "نقوش الأبواب النجدية الملوّنة وشُرَف قصور حائل."),
       (215, 128, "الزوايا المدرّجة", "زوايا البناء الطيني النجدي."),
       (218, 420, "مسامير الباب", "صفوف المعينات مثل مسامير الأبواب القديمة ونقش السدو."),
       (560, 330, "الكتابة المتدرّجة", "«رائحة» ثم «أمي» تنزل كدرجة عتبة البيت، بخطّنا الخاص ونقاطه المعيّنة."),
       (500, 650, "المبخرة والدخان", "قلب منتجنا وأول ما يُقدَّم للضيف."),
       (840, 410, "المعينان الجانبيان", "مقابض الباب؛ دعوة للدخول."),
       (320, 930, "من أرض حاتم · حائل", "أصلنا، والكرم اللي نحمله."),]
for i, (px, py, t, txt) in enumerate(pts):
    cx, cy = lx + px * sc, ly + py * sc
    b.append(f'<circle cx="{cx}" cy="{cy}" r="17" fill="{RED}" stroke="{CREAM}" stroke-width="3"/>')
    b.append(T(str(i + 1), "enb", 18, cx, cy + 6, CREAM, "middle"))
    yy = 230 + i * 86
    b.append(f'<circle cx="{PW-110}" cy="{yy-9}" r="17" fill="{RED}"/>')
    b.append(T(str(i + 1), "enb", 18, PW - 110, yy - 3, CREAM, "middle"))
    b.append(T(t, "xbold", 26, PW - 145, yy, TEAL, "end"))
    b.append(T(txt, "reg", 20, PW - 145, yy + 34, INK, "end"))
page("قصة الشعار", "كل عنصر في الشعار له معنى", "".join(b), n); n += 1

# 5 logo versions
b = []
vers = [(LOGO, SAND, "الشعار الأساسي", "الاستخدام الافتراضي في كل مكان"),
        (LOGO_HAIL, SAND, "نسخة لمسة حائل", "الحملات والمناسبات وهوية المدينة"),
        (LOGO_REV, TEAL, "النسخة المعكوسة", "على الخلفيات الغامقة والتغليف"),
        (LOGO_DOOR, SAND, "الشعار الثانوي: الباب", "الواجهات واللوحات والأماكن الطولية")]
for i, (lg, bgc, t, sub) in enumerate(vers):
    x = PW - 90 - (i + 1) * 350 - i * 10 + 10
    b.append(rect(x, 220, 350, 520, bgc, rx=14))
    b.append(nest(lg, x + 15, 235, 320, 490))
    b.append(label_box(x, 790, 350, t, sub))
page("نسخ الشعار", "أربع نسخ معتمدة؛ لا تُستخدم غيرها", "".join(b), n); n += 1

# 6 icon & horizontal
b = []
b.append(rect(PW - 450, 210, 360, 360, SAND, rx=14))
b.append(nest(LOGO, PW - 430, 230, 320, 320, vb=MARK_VB))
b.append(rect(PW - 850, 210, 360, 360, TEAL, rx=14))
b.append(nest(LOGO_REV, PW - 830, 230, 320, 320, vb=MARK_VB))
b.append(f'<clipPath id="avc"><circle cx="{PW-1070}" cy="390" r="180"/></clipPath>')
b.append(f'<g clip-path="url(#avc)">{rect(PW-1250, 210, 360, 360, SAND)}{nest(LOGO, PW-1225, 235, 310, 310, vb=MARK_VB)}</g>')
b.append(label_box(PW - 450, 610, 360, "الأيقونة", "الختم والملصقات الصغيرة"))
b.append(label_box(PW - 850, 610, 360, "الأيقونة المعكوسة", "على البترولي"))
b.append(label_box(PW - 1250, 610, 360, "صورة الحساب", "إنستقرام · تيك توك · سناب"))
hx, hy = PW - 90 - 760, 700
b.append(rect(hx, hy, 760, 210, "#EFE4D2", rx=14))
b.append(nest(LOGO, hx + 560, hy + 20, 170, 170, vb=MARK_VB))
b.append(T("رائحة أمي", "kufi", 70, hx + 535, hy + 105, TEAL, "end"))
b.append(T("RAIHAT UMMI", "enb", 22, hx + 535, hy + 145, TEAL, "end", track=5))
b.append(T("من أرض حاتم · حائل", "reg", 19, hx + 535, hy + 178, RED, "end"))
b.append(T("الشعار الأفقي", "bold", 24, hx - 40, hy + 70, TEAL, "end"))
s_, _ = para("لترويسة الموقع والفواتير والإيميل. الأيقونة هي الإطار بدون النص الإنجليزي والعبارة، "
             "وتُستخدم حين تقل المساحة، ولا يُحذف منها أي عنصر.", "reg", 20, hx - 40, hy + 115, 560)
b.append(s_)
page("الأيقونة والشعار الأفقي", "للمساحات الصغيرة والعرضية", "".join(b), n); n += 1

# 7 usage rules
b = []
bx, by, bw = PW - 560, 230, 460
b.append(rect(bx, by, bw, bw, SAND, rx=14))
m = 60
b.append(rect(bx + m, by + m, bw - 2 * m, bw - 2 * m, "none", stroke=RED, sw=2))
b.append(f'<rect x="{bx+m}" y="{by+m}" width="{bw-2*m}" height="{bw-2*m}" fill="none" stroke="{RED}" stroke-dasharray="8 8" stroke-width="2"/>')
b.append(nest(LOGO, bx + m + 20, by + m + 20, bw - 2 * m - 40, bw - 2 * m - 40, vb=MARK_VB))
b.append(T("المساحة الآمنة = عرض المعين الجانبي من كل جهة", "bold", 22, bx + bw, by + bw + 50, TEAL, "end"))
b.append(T("الحد الأدنى: 25 مم في الطباعة · 120 بكسل في الشاشة", "reg", 21, bx + bw, by + bw + 90, INK, "end"))
wrongs = [("لا تمطّه أو تضغطه", 'transform="translate({x},{y}) scale(1.45,0.75)"', SAND),
          ("لا تُدِره", 'transform="translate({x},{y}) rotate(-12,100,100)"', SAND),
          ("لا تغيّر ألوانه", 'transform="translate({x},{y})" style="filter:hue-rotate(140deg)"', SAND),
          ("لا تضعه على خلفية مزدحمة", 'transform="translate({x},{y})"', None)]
for i, (t, tf, bgc) in enumerate(wrongs):
    col, row = i % 2, i // 2
    x, y = 120 + col * 420, 230 + row * 330
    b.append(rect(x - 20, y - 20, 240, 240, bgc or "#9C6B3D", rx=12))
    if bgc is None:
        for k in range(6):
            b.append(poly([(x - 20 + k * 40, y + 220), (x + 20 + k * 40, y - 20), (x + 60 + k * 40, y + 220)], [RED, OCHRE, TEAL][k % 3]))
    mark = nest(LOGO, 0, 0, 200, 200, vb=MARK_VB)
    if "hue" in tf:
        mark = mark.replace(TEAL, "#7A3E9D").replace(RED, "#2E7D32").replace(OCHRE, "#E91E63")
    b.append(f'<g {tf.format(x=x, y=y)}>{mark}</g>')
    b.append(f'<line x1="{x-20}" y1="{y-20}" x2="{x+220}" y2="{y+220}" stroke="{RED}" stroke-width="8"/>')
    b.append(T(t, "bold", 22, x + 100, y + 260, RED, "middle"))
page("قواعد استخدام الشعار", "المساحة الآمنة، والحجم الأدنى، والأخطاء الممنوعة", "".join(b), n); n += 1

# 8 colours
def cmyk(hexc):
    r, g, bb = [int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    k = 1 - max(r, g, bb)
    if k >= 1:
        return 0, 0, 0, 100
    return tuple(round(100 * v) for v in ((1 - r - k) / (1 - k), (1 - g - k) / (1 - k), (1 - bb - k) / (1 - k), k))


b = []
cols = [(TEAL, "بترولي حائل", "اللون الرئيسي: الشعار والعناوين", CREAM),
        (TEAL_DARK, "بترولي الليل", "الخلفيات الغامقة والأدهان", CREAM),
        (RED, "أحمر أجا", "جبال حائل: لمسات ونقوش وفئة العود", CREAM),
        (OCHRE, "مغرة", "الدخان والخطوط والنقوش", TEAL),
        (SAND, "طين", "الخلفية الأساسية", TEAL),
        (CREAM, "كريمي", "الملصقات والمساحات البيضاء", TEAL)]
for i, (hx_, name, use, tc) in enumerate(cols):
    x = PW - 90 - (i + 1) * 230 - i * 8 + 8
    b.append(rect(x, 210, 230, 330, hx_, rx=14, stroke="#D9CBB3" if hx_ == CREAM else None, sw=2))
    b.append(T(name, "xbold", 26, x + 200, 270, tc, "end"))
    c_, m_, y_, k_ = cmyk(hx_)
    r_, g_, b_ = [int(hx_[j:j + 2], 16) for j in (1, 3, 5)]
    for j, line in enumerate([hx_, f"RGB {r_} {g_} {b_}", f"CMYK {c_} {m_} {y_} {k_}"]):
        b.append(T(line, "enm", 19, x + 30, 440 + j * 30, tc, "start"))
    s, _ = para(use, "reg", 18, x + 215, 580, 200, INK, 1.6)
    b.append(s)
b.append(T("نسبة الاستخدام", "xbold", 26, PW - 90, 760, TEAL, "end"))
xr = PW - 90
for hx_, pct in ((SAND, 40), (TEAL, 30), (CREAM, 12), (OCHRE, 10), (RED, 8)):
    w = 1420 * pct / 100
    b.append(rect(xr - w, 790, w, 60, hx_, stroke="#D9CBB3", sw=1))
    b.append(T(f"{pct}%", "enb", 20, xr - w / 2, 828, TEAL if hx_ in (SAND, CREAM, OCHRE) else CREAM, "middle"))
    xr -= w
b.append(T("قيم CMYK تقريبية؛ تُعتمد بعد بروفة الطباعة مع المطبعة.", "reg", 18, PW - 90, 900, MUTED, "end"))
page("الألوان", "ألوان مأخوذة من باب البيت النجدي وجبال حائل", "".join(b), n); n += 1

# 9 typography
b = []
b.append(rect(PW - 760, 210, 670, 640, "#EFE4D2", rx=14))
b.append(T("خط رائحة أمي", "kufi", 90, PW - 120, 330, TEAL, "end"))
b.append(T("Raihat Kufi · الخط الخاص بالبراند", "enm", 22, PW - 120, 380, RED, "end"))
b.append(T("أبجد هوز حطي كلمن سعفص", "kufi", 50, PW - 120, 480, TEAL, "end"))
b.append(T("قرشت ثخذ ضظغ ٠١٢٣٤٥٦٧٨٩", "kufi", 50, PW - 120, 560, TEAL, "end"))
s, _ = para("للشعار والعناوين وأسماء المنتجات فقط. نقاطه على شكل معين نجدي، "
            "ويحتوي زخارف خاصة: الباب، والجبلين، والمثلثات، والمعين، والدخان.", "reg", 20, PW - 120, 640, 600)
b.append(s)
b.append(rect(80, 210, 670, 300, "#EFE4D2", rx=14))
b.append(T("المراعي Almarai", "xbold", 52, 720, 300, TEAL, "end"))
s, _ = para("للنصوص والوصف والملصقات والموقع. واضح ومريح في القراءة بكل الأحجام: Regular للنص، وBold للتأكيد، وExtraBold للعناوين الصغيرة.",
            "reg", 21, 720, 360, 600)
b.append(s)
b.append(rect(80, 550, 670, 300, "#EFE4D2", rx=14))
b.append(T("Jost", "enb", 60, 110, 640, TEAL, "start"))
b.append(T("RAIHAT UMMI · Aa Bb Cc 0123", "enm", 26, 110, 690, RED, "start", track=2))
s, _ = para("للنصوص الإنجليزية، والاسم اللاتيني بأحرف كبيرة وتباعد واسع.", "reg", 21, 720, 760, 600)
b.append(s)
b.append(T("جميع الخطوط مجانية ومرخّصة للاستخدام التجاري (SIL OFL).", "reg", 18, PW - 90, 910, MUTED, "end"))
page("الخطوط", "ثلاثة خطوط فقط", "".join(b), n); n += 1

# 10 elements
b = []
items = []
def el(x, y, w, h, art, t):
    return rect(x, y, w, h, "#EFE4D2", rx=14) + art + T(t, "bold", 22, x + w / 2, y + h + 38, TEAL, "middle")
X = [PW - 90 - 340 * (i + 1) - 20 * i for i in range(4)]
b.append(el(X[0], 210, 340, 240, tri_row(X[0] + 30, X[0] + 310, 300, 60, (OCHRE, RED), n=7), "شريط المثلثات النجدي"))
art = "".join(diamond(X[1] + 60 + k * 55, 330, 18, (OCHRE, RED)[k % 2]) for k in range(5))
b.append(el(X[1], 210, 340, 240, art, "المعينات (مسامير الباب)"))
b.append(el(X[2], 210, 340, 240, ridge(X[2] + 20, X[2] + 320, 430, 160, RED), "جبلا أجا وسلمى"))
b.append(el(X[3], 210, 340, 240, Bd.mabkhara(X[3] + 170, 420, 180, TEAL, RED, OCHRE), "المبخرة والدخان"))
pat = []
tile = 90
for r in range(3):
    for c in range(16):
        x, y = 80 + c * tile, 560 + r * tile
        if x + tile > PW - 80:
            continue
        bgc = (TEAL, SAND)[(r + c) % 2]
        pat.append(rect(x, y, tile, tile, bgc))
        pat.append(diamond(x + tile / 2, y + tile / 2, 26, (OCHRE, RED)[(r + c) % 2], hole=bgc))
        pat.append(poly([(x, y), (x + 18, y), (x, y + 18)], OCHRE))
b.append("".join(pat))
b.append(T("نقشة البراند: للأغلفة الداخلية وشرائط التغليف وخلفيات السوشال", "bold", 22, PW - 90, 880, TEAL, "end"))
page("العناصر والنقوش", "مفردات بصرية تُستخدم مع الشعار وبدونه", "".join(b), n); n += 1

# 11 voice
b = []
b.append(card(PW - 560, 210, 470, 300, "نتكلم كأهل البيت",
              "لهجة سعودية بيضاء، دافية وقريبة. جمل قصيرة، وكلمات من البيت: «حيّاك»، «ريحة»، «تبخيرة الجمعة».", TEAL))
b.append(card(PW - 1060, 210, 470, 300, "كرم بدون مبالغة",
              "نعطي التفاصيل بصدق: من وين المادة، ورقم التشغيلة، وطريقة الاستخدام. بدون وعود ما نقدر نثبتها.", RED))
b.append(card(90, 210, 470, 300, "فخر بحائل",
              "نذكر حائل وحاتم الطائي وأجا وسلمى بفخر، كجزء من الحكاية وليس كشعار تسويقي فقط.", OCHRE))
b.append(T("عبارات البراند", "xbold", 30, PW - 90, 600, TEAL, "end"))
tags = ["من أرض حاتم · حائل", "ريحة البيت اللي تعرفه", "باب أمي مفتوح", "حيّاك في بيتنا"]
x = PW - 90
for t in tags:
    w = measure(t, "kufi", 32) + 56
    b.append(rect(x - w, 630, w, 70, SAND, rx=35))
    b.append(T(t, "kufi", 32, x - w / 2, 677, TEAL, "middle"))
    x -= w + 20
b.append(T("الهاشتاقات والحسابات", "xbold", 30, PW - 90, 790, TEAL, "end"))
b.append(T("@raihatummi   ·   #رائحة_أمي   ·   #raihatummi   ·   #بخور_حائل", "bold", 26, PW - 90, 850, RED, "end"))
page("صوت البراند", "كيف نتكلم مع الناس", "".join(b), n); n += 1

# 12 products
b = []
for i, (cat, en, acc, desc, items) in enumerate(CATS):
    x = PW - 90 - (i + 1) * 340 - i * 20
    b.append(rect(x, 210, 340, 690, "#EFE4D2", rx=14))
    b.append(rect(x, 210, 340, 110, acc, rx=14))
    b.append(rect(x, 290, 340, 30, acc))
    b.append(T(cat, "kufi", 46, x + 310, 268, CREAM, "end"))
    b.append(T(en, "enb", 14, x + 310, 305, CREAM if acc != OCHRE else TEAL, "end", track=3))
    s, yy = para(desc, "reg", 19, x + 310, 360, 280, INK, 1.6)
    b.append(s)
    yy += 20
    for name, size_txt, price in items:
        b.append(f'<line x1="{x+30}" y1="{yy}" x2="{x+310}" y2="{yy}" stroke="#D9CBB3" stroke-width="1.5"/>')
        b.append(T(name, "kufi", fit(name, "kufi", 280, 34), x + 310, yy + 55, TEAL, "end"))
        b.append(T(size_txt, "reg", 19, x + 310, yy + 94, MUTED, "end"))
        b.append(T(price + " ر.س", "xbold", 22, x + 30, yy + 94, acc if acc != OCHRE else RED, "start"))
        yy += 120
page("المنتجات", "أربع فئات، ولكل فئة لون يميزها", "".join(b), n); n += 1

# 13-15 labels
def label_page(title, sub, names, lw, per_row):
    b = []
    total = len(names)
    gap = 40
    xr = PW - 90
    for i, nm in enumerate(names):
        kind, s_, mw, mh = LABELS[nm]
        r, c = i // per_row, i % per_row
        h = lw * mh / mw
        x = xr - (c + 1) * lw - c * gap
        y = 220 + r * (h + 90)
        b.append(nest(s_, x, y, lw, h))
        b.append(T(f"{nm} · {mw}×{mh} مم", "bold", 20, x + lw / 2, y + h + 38, TEAL, "middle"))
    page(title, sub, "".join(b), len(PAGES) + 1)


label_page("ملصقات المعمول والعود", "ملصق دائري 60 مم لأغطية العلب، ولون الحلقة يميز الفئة",
           ["الملكي", "المخصوص", "العرايسي", "عود مسقى", "عود طبيعي"], 270, 3)
label_page("ملصقات المرشات", "ملصق مستطيل 70×110 مم يلف القارورة", ["أسيل", "شهد", "سديم"], 330, 3)
label_page("ملصقات الأدهان", "ملصق صغير 50×30 مم لقارورة التولة", ["فتشة العروس", "خمرية الزعفران", "خمرية المسك", "دهن العود الطبيعي"], 470, 2)

# 16 stickers
b = []
lay = [("ختم-الإغلاق", PW - 400, 220, 300, "ختم إغلاق البوكس · 50 مم"),
       ("شكراً", PW - 940, 240, 480, "شكراً · 80×40 مم"),
       ("صنع-يدوياً", 140, 230, 260, "صُنع يدوياً · 40 مم"),
       ("رقم-التشغيلة", PW - 560, 640, 460, "رقم التشغيلة · 60×22 مم"),
       ("هدية", 300, 600, 440, "هدية · 60×30 مم")]
for key, x, y, w, t in lay:
    s_, mw, mh = STICKERS[key]
    h = w * mh / mw
    b.append(nest(s_, x, y, w, h))
    b.append(T(t, "bold", 20, x + w / 2, y + h + 38, TEAL, "middle"))
page("الستكرات", "ملصقات الإغلاق والشكر والهدايا", "".join(b), len(PAGES) + 1)

# 17 packaging
b = []
b.append(nest(gift_box_lid(), PW - 690, 210, 600))
b.append(T("غطاء بوكس الهدايا", "bold", 22, PW - 390, 690, TEAL, "middle"))
b.append(nest(card_front(), 470, 210, 420))
b.append(T("كرت الشكر · الوجه A6", "bold", 20, 680, 540, TEAL, "middle"))
b.append(nest(card_back(), 470, 580, 420))
b.append(T("كرت الشكر · الظهر", "bold", 20, 680, 910, TEAL, "middle"))
s, _ = para("البوكس بلون البترولي مع شريط نقشة البراند، والشعار المعكوس في المنتصف. "
            "يُغلق بختم الإغلاق، ويوضع داخله كرت الشكر.", "reg", 21, 420, 260, 330)
b.append(s)
page("التغليف", "بوكس الهدايا وكرت الشكر", "".join(b), len(PAGES) + 1)

# 18 social
b = []
b.append(nest(avatar(), PW - 330, 220, 240))
b.append(T("صورة الحساب", "bold", 20, PW - 210, 500, TEAL, "middle"))
b.append(nest(post_template(), PW - 830, 220, 440))
b.append(T("قالب منشور 1080×1080", "bold", 20, PW - 610, 700, TEAL, "middle"))
b.append(nest(story_template(), PW - 1130, 220, 260))
b.append(T("قالب ستوري", "bold", 20, PW - 1000, 720, TEAL, "middle"))
hl = [("mab", "معمول"), ("oud", "عود"), ("spray", "مرشات"), ("oil", "أدهان"), ("gift", "هدايا")]
for i, (k, t) in enumerate(hl):
    x = PW - 330 - i * 0
    hs = svgdoc(400, 400, "".join(highlight(k, t)))
    b.append(nest(hs, 90 + i * 0, 0, 0)) if False else None
    b.append(nest(hs, 90 + (i % 2) * 190, 220 + (i // 2) * 200, 170))
b.append(T("أيقونات الهايلايت", "bold", 20, 270, 860, TEAL, "middle"))
page("السوشال ميديا", "قوالب جاهزة لإنستقرام وتيك توك وسناب", "".join(b), len(PAGES) + 1)

# 19 stationery
b = []
b.append(nest(biz_front(), PW - 720, 230, 630))
b.append(T("كرت العمل · الوجه 90×50 مم", "bold", 20, PW - 405, 620, TEAL, "middle"))
b.append(nest(biz_back(), 90, 230, 630))
b.append(T("كرت العمل · الظهر", "bold", 20, 405, 620, TEAL, "middle"))
s, _ = para("البيانات في الكرت أمثلة؛ تُستبدل بالاسم والجوال والحسابات الفعلية بعد حجزها.", "reg", 21, PW - 90, 720, 1400)
b.append(s)
page("القرطاسية", "كرت العمل", "".join(b), len(PAGES) + 1)

# 20 print specs
b = []
rows = [("الملصق", "المقاس", "الخامة المقترحة", "التشطيب"),
        ("علب المعمول والعود", "دائري 60 مم", "ورق ملصق مطفي (Matte)", "مقاوم للزيت"),
        ("قارورة المرش", "70×110 مم", "فينيل أبيض مقاوم للماء", "لامينيت مطفي"),
        ("قارورة الدهن", "50×30 مم", "ورق ملصق مطفي", "مقاوم للزيت"),
        ("ختم الإغلاق", "دائري 50 مم", "فينيل", "مطفي"),
        ("ستكر شكراً وهدية", "80×40 / 60×30 مم", "ورق مطفي", "اختياري: طباعة ذهبية"),
        ("كرت الشكر", "A6 · 148×105 مم", "كرتون 350 جم", "مطفي"),
        ("كرت العمل", "90×50 مم", "كرتون 400 جم", "طباعة ذهبية للنقوش اختيارياً")]
colsx = [PW - 90, PW - 500, PW - 820, PW - 1220]
for r, row in enumerate(rows):
    y = 240 + r * 70
    if r == 0:
        b.append(rect(90, y - 45, PW - 180, 65, TEAL, rx=10))
    elif r % 2 == 0:
        b.append(rect(90, y - 45, PW - 180, 65, "#EFE4D2"))
    for cx_, cell in zip(colsx, row):
        b.append(T(cell, "bold" if r == 0 else "reg", 22, cx_ - 20, y, CREAM if r == 0 else INK, "end"))
notes = ["كل الملفات مرفقة SVG (فكتور) وPNG بدقة طباعة 300 نقطة في البوصة.",
         "اطلب بروفة مطبوعة قبل الكمية، وطابق الألوان على البروفة.",
         "اترك 3 مم زيادة (Bleed) حول الملصقات المقصوصة."]
for i, t in enumerate(notes):
    b.append(diamond(PW - 100, 828 + i * 42, 8, RED))
    b.append(T(t, "reg", 21, PW - 125, 835 + i * 42, INK, "end"))
page("مواصفات الطباعة", "للمطبعة والمصمم", "".join(b), len(PAGES) + 1)

# back cover
bc = [rect(0, 0, PW, PH, SAND), nest(LOGO, PW / 2 - 300, 120, 600)]
bc.append(T("@raihatummi  ·  raihatummi.com", "enm", 28, PW / 2, 900, TEAL, "middle"))
PAGES.append(svgdoc(PW, PH, "".join(bc)))

# ------------------------------------------------------------------ export
os.makedirs(OUT, exist_ok=True)
writer = PdfWriter()
for i, p in enumerate(PAGES):
    pdf = cairosvg.svg2pdf(bytestring=p.encode("utf-8"))
    for pg in PdfReader(io.BytesIO(pdf)).pages:
        writer.add_page(pg)
with open(os.path.join(OUT, "دليل-الهوية-البصرية-رائحة-أمي.pdf"), "wb") as f:
    writer.write(f)
prev = os.path.join(OUT, "_preview")
os.makedirs(prev, exist_ok=True)
for i, p in enumerate(PAGES):
    open(os.path.join(prev, f"{i+1:02d}.png"), "wb").write(bytes(resvg_py.svg_to_bytes(svg_string=p, width=1200)))

pr = os.path.join(OUT, "ملفات-الطباعة")
for sub in ("ملصقات-المنتجات", "ستكرات", "تغليف-وقرطاسية", "سوشال-ميديا"):
    os.makedirs(os.path.join(pr, sub), exist_ok=True)


def save(folder, name, s, mm_w):
    open(os.path.join(pr, folder, name + ".svg"), "w").write(s)
    px = int(mm_w / 25.4 * 300) if mm_w else None
    data = resvg_py.svg_to_bytes(svg_string=s, width=px) if px else resvg_py.svg_to_bytes(svg_string=s)
    open(os.path.join(pr, folder, name + ".png"), "wb").write(bytes(data))


for nm, (kind, s_, mw, mh) in LABELS.items():
    save("ملصقات-المنتجات", nm, s_, mw)
for nm, (s_, mw, mh) in STICKERS.items():
    save("ستكرات", nm, s_, mw)
save("تغليف-وقرطاسية", "غطاء-بوكس-الهدايا", gift_box_lid(), 200)
save("تغليف-وقرطاسية", "كرت-الشكر-وجه", card_front(), 148)
save("تغليف-وقرطاسية", "كرت-الشكر-ظهر", card_back(), 148)
save("تغليف-وقرطاسية", "كرت-العمل-وجه", biz_front(), 90)
save("تغليف-وقرطاسية", "كرت-العمل-ظهر", biz_back(), 90)
save("سوشال-ميديا", "صورة-الحساب", avatar(), None)
save("سوشال-ميديا", "قالب-منشور", post_template(), None)
save("سوشال-ميديا", "قالب-ستوري", story_template(), None)
for k, t in hl:
    save("سوشال-ميديا", "هايلايت-" + t, svgdoc(400, 400, "".join(highlight(k, t))), None)
print("book ok", len(PAGES), "pages")
