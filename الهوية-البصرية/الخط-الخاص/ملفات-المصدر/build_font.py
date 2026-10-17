"""Build "Raihat Kufi" — the brand typeface for رائحة أمي.

Based on Kufam (SIL OFL 1.1) at ExtraBold, modified:
  * every Arabic dot redrawn as a Najdi diamond
  * stylistic set ss02: alif becomes a Hail fort door with crenellations
  * brand ornaments in the Private Use Area (U+E000–U+E004)
  * renamed to Raihat Kufi / خط رائحة أمي
"""
import os, sys
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib.tables import otTables as ot

SRC, OUT = sys.argv[1], sys.argv[2]

font = instancer.instantiateVariableFont(TTFont(SRC), {"wght": 800})
glyf, hmtx, gs = font["glyf"], font["hmtx"], font.getGlyphSet()
order = font.getGlyphOrder()


def contours_of(name):
    coords, ends, _ = glyf[name].getCoordinates(glyf)
    out, s = [], 0
    for e in ends:
        out.append([tuple(p) for p in coords[s:e + 1]])
        s = e + 1
    return out


def area(pts):
    return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
               for i in range(len(pts))) / 2


def put(name, polys, advance, lsb=None):
    """polys: list of point lists; outer contours clockwise, holes counter-clockwise."""
    pen = TTGlyphPen(None)
    for poly in polys:
        pen.moveTo(poly[0])
        for p in poly[1:]:
            pen.lineTo(p)
        pen.closePath()
    g = pen.glyph()
    if name not in glyf.glyphs:
        order.append(name)
    glyf[name] = g
    g.recalcBounds(glyf)
    hmtx[name] = (advance, g.xMin if lsb is None else lsb)


def cw(poly):  # make clockwise (outer)
    return poly if area(poly) < 0 else poly[::-1]


def ccw(poly):  # make counter-clockwise (hole)
    return poly if area(poly) > 0 else poly[::-1]


# 1. Najdi diamond dots -------------------------------------------------------
DOT_GLYPHS = [n for n in order if "dot" in n.lower() and n != "dotlessi"
              and not glyf[n].isComposite() and glyf[n].numberOfContours > 0]
changed = 0
for n in DOT_GLYPHS:
    polys = []
    for c in contours_of(n):
        xs, ys = [p[0] for p in c], [p[1] for p in c]
        w, h = max(xs) - min(xs), max(ys) - min(ys)
        if len(c) == 12 and 100 < w < 200 and abs(w - h) < 8:
            cx, cy, r = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, w * 0.62
            polys.append(cw([(cx, cy - r), (cx - r * 0.82, cy), (cx, cy + r), (cx + r * 0.82, cy)]))
            changed += 1
        else:
            polys.append(c)
    adv, lsb = hmtx[n]
    put(n, [[(round(x), round(y)) for x, y in p] for p in polys], adv)
print("diamond dots:", changed, "in", len(DOT_GLYPHS), "glyphs")


# 2. Fort-door alif ------------------------------------------------------------
def door(x0=60, w=300, top=760):
    x1, tooth = x0 + w, w / 3
    body = [(x0, 0), (x0, top - 100)]
    for k in range(3):
        a = x0 + k * tooth
        body += [(a + tooth / 2, top), (a + tooth, top - 100)]
    body += [(x1, 0)]
    body = cw(body)
    m = w * 0.2
    opening = ccw([(x0 + m, 60), (x1 - m, 60), (x1 - m, 420), (x0 + w / 2, 500), (x0 + m, 420)])
    split = cw([(x0 + w / 2 - 9, 60), (x0 + w / 2 + 9, 60), (x0 + w / 2 + 9, 440), (x0 + w / 2 - 9, 440)])
    windows = []
    for k in range(3):
        a = x0 + m + k * (w - 2 * m) / 3
        b = a + (w - 2 * m) / 3
        windows.append(ccw([(a + 8, 600), (b - 8, 600), ((a + b) / 2, 555)]))
    return [body, opening, split] + windows


def hamza(dx, dy, s=0.62):
    pts = []
    for c in contours_of("uni0654"):
        pts.append([(round(x * s + dx), round(y * s + dy)) for x, y in c])
    return pts


def ints(polys):
    return [[(round(x), round(y)) for x, y in p] for p in polys]


connector = contours_of("uniFE8E")[0]  # baseline joining stroke of final alif
hz_dx = 210 - (20 + 237 / 2) * 0.62

put("uni0627.door", ints(door()), 420)
put("uni0623.door", ints(door()) + hamza(hz_dx, 800), 420)
put("uniFE8E.door", ints(door()) + [[(x + 65, y) for x, y in connector]], 460)
put("uniFE84.door", ints(door()) + hamza(hz_dx, 800) + [[(x + 65, y) for x, y in connector]], 460)

# 3. Brand ornaments (Private Use Area) ---------------------------------------
tri = []
for k in range(3):
    a = 40 + k * 200
    tri.append(cw([(a, 0), (a + 100, 180), (a + 200, 0)]) if k % 2 == 0 else
               cw([(a, 180), (a + 200, 180), (a + 100, 0)]))
put("raihat.triangles", ints(tri), 680)
put("raihat.diamond", ints([cw([(300, 0), (80, 300), (300, 600), (520, 300)]),
                             ccw([(300, 140), (185, 300), (300, 460), (415, 300)])]), 600)
mountains = cw([(20, 0), (160, 330), (230, 250), (330, 560), (450, 300), (520, 380), (640, 120), (700, 0)])
put("raihat.ajasalma", ints([mountains]), 720)
put("raihat.door", ints(door(60, 360, 900)), 480)
put("raihat.smoke", ints([cw([(140, 0), (190, 0), (240, 180), (180, 360), (250, 560), (200, 560),
                              (130, 360), (190, 180)])]), 380)
PUA = {0xE000: "raihat.door", 0xE001: "raihat.ajasalma", 0xE002: "raihat.triangles",
       0xE003: "raihat.diamond", 0xE004: "raihat.smoke"}
for table in font["cmap"].tables:
    if table.isUnicode():
        table.cmap.update(PUA)
font.setGlyphOrder(order)

# 4. ss02 stylistic set: door alif ---------------------------------------------
gsub = font["GSUB"].table
lk = ot.Lookup()
lk.LookupType, lk.LookupFlag = 1, 0
st = ot.SingleSubst()
st.mapping = {"uni0627": "uni0627.door", "uni0623": "uni0623.door",
              "uniFE8E": "uniFE8E.door", "uniFE84": "uniFE84.door"}
lk.SubTable, lk.SubTableCount = [st], 1
gsub.LookupList.Lookup.append(lk)
gsub.LookupList.LookupCount = len(gsub.LookupList.Lookup)
fr = ot.FeatureRecord()
fr.FeatureTag = "ss02"
fr.Feature = ot.Feature()
fr.Feature.FeatureParams = None
fr.Feature.LookupListIndex = [len(gsub.LookupList.Lookup) - 1]
fr.Feature.LookupCount = 1
gsub.FeatureList.FeatureRecord.append(fr)
gsub.FeatureList.FeatureCount = len(gsub.FeatureList.FeatureRecord)
fi = len(gsub.FeatureList.FeatureRecord) - 1
for sr in gsub.ScriptList.ScriptRecord:
    for ls in [sr.Script.DefaultLangSys] + [r.LangSys for r in sr.Script.LangSysRecord]:
        if ls is not None:
            ls.FeatureIndex.append(fi)
            ls.FeatureCount = len(ls.FeatureIndex)

# 5. Names -----------------------------------------------------------------------
name = font["name"]
orig_copy = str(name.getName(0, 3, 1, 0x409))
for rec in list(name.names):
    if rec.nameID in (1, 2, 3, 4, 6, 16, 17, 21, 22, 25) or rec.nameID >= 256:
        name.removeNames(nameID=rec.nameID)
fam, sty = "Raihat Kufi", "Regular"
name.setName(orig_copy + ". Modifications Copyright 2026 Raihat Ummi.", 0, 3, 1, 0x409)
for nid, val in {1: fam, 2: sty, 3: "RaihatKufi-Regular;2026", 4: f"{fam} {sty}",
                 5: "Version 1.000", 6: "RaihatKufi-Regular"}.items():
    name.setName(val, nid, 3, 1, 0x409)
    name.setName(val, nid, 1, 0, 0)
name.setName("خط رائحة أمي", 1, 3, 1, 0x401)
name.setName("خط رائحة أمي", 4, 3, 1, 0x401)
name.setName("Raihat Ummi — based on Kufam by Original Type (SIL OFL 1.1)", 8, 3, 1, 0x409)
font["OS/2"].usWeightClass = 400
font["OS/2"].fsSelection = (font["OS/2"].fsSelection & ~0b1100001) | 0b1000000
font["head"].macStyle = 0
font["post"].italicAngle = 0
# merge overlapping contours so joins render solid in every app
from fontTools.ttLib.removeOverlaps import removeOverlaps
removeOverlaps(font)
for t in ("STAT", "MVAR", "HVAR", "avar", "fvar", "gvar"):
    if t in font:
        del font[t]
font.save(OUT)
try:
    f2 = TTFont(OUT)
    f2.flavor = "woff2"
    f2.save(os.path.splitext(OUT)[0] + ".woff2")
except Exception as e:  # brotli missing
    print("woff2 skipped:", e)
print("saved", OUT)
