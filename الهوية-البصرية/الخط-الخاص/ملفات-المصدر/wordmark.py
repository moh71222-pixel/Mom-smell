"""Brand wordmark + font specimen using Raihat Kufi (the custom brand font)."""
import os, sys
import uharfbuzz as hb
import resvg_py
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
sys.path.insert(0, os.path.dirname(__file__))
from brand import TEAL, TEAL_DARK, RED, OCHRE, SAND, CREAM, text_path, svg

FONT, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
TT = TTFont(FONT)
HB = hb.Font(hb.Face(open(FONT, "rb").read()))
GS, ORDER, UPEM = TT.getGlyphSet(), TT.getGlyphOrder(), TT["head"].unitsPerEm


def shape(text, features=None):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(HB, buf, features or {})
    return [(ORDER[i.codepoint], p) for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


def draw(glyphs, size, x, y, anchor="middle", colors=None, default=TEAL, swap=None):
    """Draw shaped glyphs; colors maps glyph name -> fill. swap maps glyph -> replacement."""
    swap = swap or {}
    s = size / UPEM
    items = []
    for g, p in glyphs:
        g2 = swap.get(g, g)
        adv = TT["hmtx"][g2][0] if g2 != g else p.x_advance
        items.append((g2, p, adv))
    total = sum(a for _, _, a in items) * s
    x0 = {"middle": x - total / 2, "end": x - total, "start": x}[anchor]
    out, cx = [], 0
    for g, p, adv in items:
        pen = SVGPathPen(GS)
        GS[g].draw(TransformPen(pen, (s, 0, 0, -s, x0 + (cx + p.x_offset) * s, y - p.y_offset * s)))
        d = pen.getCommands()
        if d:
            out.append(f'<path d="{d}" fill="{(colors or {}).get(g, default)}"/>')
        cx += adv
    return "".join(out), total, x0


def tri_row(x0, x1, y, h, cols=(OCHRE, RED)):
    n = max(3, round((x1 - x0) / (h * 1.15)))
    w = (x1 - x0) / n
    return "".join(f'<polygon points="{x0+k*w:.1f},{y+h:.1f} {x0+(k+1)*w:.1f},{y+h:.1f} {x0+k*w+w/2:.1f},{y:.1f}" '
                   f'fill="{cols[k % 2]}"/>' for k in range(n))


def smoke(cx, base, h, col, sw):
    return (f'<path d="M{cx},{base} C{cx-h*.35},{base-h*.3} {cx+h*.35},{base-h*.55} {cx},{base-h*.75} '
            f'S{cx-h*.15},{base-h*.95} {cx+h*.12},{base-h}" fill="none" stroke="{col}" '
            f'stroke-width="{sw}" stroke-linecap="round"/>')


def wordmark(bg=None, ink=TEAL, en=TEAL, tag=None, w=1500, h=820):
    body, total, x0 = draw(shape("رائحة أمي"), 300, w / 2, 430, default=ink)
    parts = [body, tri_row(x0, x0 + total, 545, 34)]
    d, _ = text_path("RAIHAT UMMI", "Jost.ttf", 66, w / 2, 670, "middle", wght=600, tracking=200)
    parts.append(f'<path d="{d}" fill="{en}"/>')
    if tag:
        d, _ = text_path("من أرض حاتم · حائل", "Almarai-Regular.ttf", 38, w / 2, 745, "middle")
        parts.append(f'<path d="{d}" fill="{tag}"/>')
    return svg(w, h, "".join(parts), bg)


def save(name, s, width):
    open(os.path.join(OUT, name + ".svg"), "w").write(s)
    open(os.path.join(OUT, name + ".png"), "wb").write(bytes(resvg_py.svg_to_bytes(svg_string=s, width=width)))


save("الكتابة-الرئيسية", wordmark(tag=RED), 2800)
save("الكتابة-الرئيسية-رملية", wordmark(SAND, tag=RED), 2800)
save("الكتابة-الرئيسية-معكوسة", wordmark(TEAL, ink=CREAM, en=CREAM, tag=OCHRE), 2800)
save("الكتابة-الرئيسية-داكنة", wordmark(TEAL_DARK, ink=SAND, en=SAND), 2800)

# specimen ----------------------------------------------------------------------
W, rows = 1800, []
y = 150
d, _ = text_path("خط رائحة أمي", "Almarai-Bold.ttf", 40, W - 90, 90, "end")
rows.append(f'<path d="{d}" fill="{RED}"/>')
d, _ = text_path("RAIHAT KUFI", "Jost.ttf", 34, 90, 90, "start", wght=600, tracking=150)
rows.append(f'<path d="{d}" fill="{RED}"/>')
for text, size, feats in [("رائحة أمي", 190, None), ("بخور · عود · دهن · مرش", 120, None),
                          ("معمول ملكي مخصوص عرايسي", 95, None), ("حائل أجا سلمى", 130, {"ss02": True}),
                          ("أبجد هوز حطي كلمن سعفص قرشت ثخذ ضظغ", 70, None),
                          ("٠١٢٣٤٥٦٧٨٩  0123456789", 70, None)]:
    y += size * 1.05
    body, _, _ = draw(shape(text, feats), size, W - 90, y, "end")
    rows.append(body)
    y += 40
ornaments, _, _ = draw(shape("    "), 150, W - 90, y + 180, "end",
                       default=OCHRE)
rows.append(ornaments)
labels = [("ألف الباب (ss02)", y - 30), ("زخارف خاصة", y + 230)]
for t, yy in labels:
    d, _ = text_path(t, "Almarai-Regular.ttf", 28, 90, yy, "start")
    rows.append(f'<path d="{d}" fill="{RED}"/>')
save("عينة-الخط", svg(W, y + 300, "".join(rows), CREAM), 1800)
print("ok")
