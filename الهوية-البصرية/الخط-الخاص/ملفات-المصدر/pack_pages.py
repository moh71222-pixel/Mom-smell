# Packaging section of the brand book: 3D renders, technical drawings, dielines.
# Executed inside book.py's namespace (uses page, T, para, nest, rect, poly, LOGO...).
import pack3d as P3
from pack3d import Scene, shade

GOLD = OCHRE
GLASS = "#5a2610"
KRAFT = "#C9A57C"
LINE = "#8B7B6B"
CUT = "#C2362B"
FOLD = "#2A6F78"

# ---------------------------------------------------------------- packaging spec (mm)
SPEC = {
    "jar": dict(body_d=80, body_h=66, lid_d=84, lid_h=24, label_d=60, volume="250 مل"),
    "spray": dict(body_d=70, body_h=175, shoulder_h=22, neck_d=26, neck_h=10, cap_d=30, cap_h=38,
                  label_w=70, label_h=110, label_z=30, volume="500 مل"),
    "tola": dict(flat=26, body_h=48, neck_d=14, neck_h=4, cap_d=18, cap_h=30, print_w=32, print_h=30, volume="12 مل (تولة)"),
    "qtola": dict(flat=16, body_h=30, neck_d=9, neck_h=3, cap_d=12, cap_h=20, print_w=20, print_h=18, volume="3 مل (ربع تولة)"),
    "carton_jar": (88, 88, 96),
    "carton_spray": (74, 74, 250),
    "carton_tola": (30, 30, 86),
    "carton_qtola": (20, 20, 57),
    "gift": dict(l=300, w=150, h=105, lid_h=35, wall=2),
    "mailer": (320, 165, 125),
}


def total_h(k):
    s = SPEC[k]
    if k == "jar":
        return s["body_h"] + s["lid_h"]
    if k == "spray":
        return s["body_h"] + s["shoulder_h"] + s["neck_h"] + s["cap_h"]
    return s["body_h"] + s["neck_h"] + s["cap_h"]


# ---------------------------------------------------------------- artwork for the faces
def tola_print(name, w_mm, h_mm):
    """Gold screen print for the glass (transparent background)."""
    W, H = w_mm * 10, h_mm * 10
    o = [tri_row(10, W - 10, 8, H * 0.07, (GOLD, GOLD), down=True, n=9),
         tri_row(10, W - 10, H - 8 - H * 0.07, H * 0.07, (GOLD, GOLD), n=9)]
    o.append(lettering(W / 2, H * 0.15, W * 0.62, H * 0.40, GOLD))
    o.append(Bd.divider(W / 2, H * 0.63, W * 0.22, GOLD, GOLD))
    o.append(T(name, "kufi", fit(name, "kufi", W * 0.8, H * 0.13), W / 2, H * 0.80, GOLD, "middle"))
    return svgdoc(W, H, "".join(o))


def carton_front(name, cat, size_txt, w_mm, h_mm, accent=TEAL):
    W, H = w_mm * 10, h_mm * 10
    band = max(40, H * 0.07)
    o = [rect(0, 0, W, H, accent), sadu_strip(0, W, 0, band), sadu_strip(0, W, H - band, band)]
    o.append(rect(W * 0.08, band + H * 0.03, W * 0.84, H - 2 * band - H * 0.06, "none", stroke=GOLD, sw=max(3, W * 0.006)))
    lw = min(W * 0.62, (H - 2 * band) * 0.42)
    o.append(nest(LOGO_REV, W / 2 - lw / 2, band + H * 0.07, lw, vb=MARK_VB))
    y = band + H * 0.07 + lw * 740 / 756 + H * 0.08
    o.append(T(name, "kufi", fit(name, "kufi", W * 0.74, min(W * 0.16, H * 0.09)), W / 2, y, CREAM, "middle"))
    o.append(T(cat + " · " + size_txt, "bold", min(W * 0.06, H * 0.035), W / 2, y + min(W * 0.1, H * 0.06), GOLD, "middle"))
    return svgdoc(W, H, "".join(o))


def carton_side(w_mm, h_mm):
    W, H = w_mm * 10, h_mm * 10
    o = [rect(0, 0, W, H, SAND)]
    n = max(3, int(H / (W * 0.45)))
    for k in range(n):
        o.append(diamond(W / 2, H * (k + 0.5) / n, W * 0.16, (RED, GOLD)[k % 2], hole=SAND))
    return svgdoc(W, H, "".join(o))


def carton_top(w_mm, d_mm):
    W, H = w_mm * 10, d_mm * 10
    o = [rect(0, 0, W, H, CREAM)]
    s = min(W, H) * 0.7
    o.append(nest(LOGO, W / 2 - s / 2, H / 2 - s / 2, s, s, vb=MARK_VB))
    return svgdoc(W, H, "".join(o))


def gift_lid_top(l, w):
    W, H = l * 10, w * 10
    b = H * 0.12
    o = [rect(0, 0, W, H, TEAL), sadu_strip(0, W, 0, b), sadu_strip(0, W, H - b, b)]
    o.append(rect(W * 0.03, b * 1.35, W * 0.94, H - 2.7 * b, "none", stroke=GOLD, sw=8))
    lw = H - 3.4 * b
    o.append(nest(LOGO_REV, W / 2 - lw / 2, 1.7 * b, lw, lw, vb=MARK_VB))
    for side in (-1, 1):
        for k in range(4):
            o.append(diamond(W / 2 + side * (lw / 2 + 120 + k * 110), H / 2, 34, (GOLD, RED)[k % 2], hole=TEAL))
    return svgdoc(W, H, "".join(o))


def band_art(l, h, bg=TEAL):
    W, H = l * 10, h * 10
    o = [rect(0, 0, W, H, bg), tri_row(0, W, H * 0.3, H * 0.4, (GOLD, RED), n=max(4, int(W / (H * 0.5))))]
    return svgdoc(W, H, "".join(o))


def mailer_top(l, w):
    W, H = l * 10, w * 10
    o = [rect(0, 0, W, H, KRAFT)]
    o.append(lettering(W / 2, H * 0.2, W * 0.36, H * 0.46, TEAL))
    o.append(T("RAIHAT UMMI", "enb", H * 0.07, W / 2, H * 0.8, TEAL, "middle", track=12))
    return svgdoc(W, H, "".join(o))


def mailer_front(l, h):
    W, H = l * 10, h * 10
    o = [rect(0, 0, W, H, KRAFT), tri_row(0, W, H - 70, 50, (TEAL, TEAL), n=24)]
    o.append(T("هدية من بيت أمي · حائل", "bold", 60, W / 2, H * 0.48, TEAL, "middle"))
    return svgdoc(W, H, "".join(o))


JAR_LABEL = jar_label("المخصوص", "معمول", "100 جرام", TEAL)
OUD_LABEL = jar_label("عود مسقى", "عود", "80 جرام", RED)
SPRAY_LABEL = spray_label("أسيل", "500 مل", OCHRE)
TOLA_PRINT = tola_print("خمرية المسك", SPEC["tola"]["print_w"], SPEC["tola"]["print_h"])
QTOLA_PRINT = tola_print("دهن العود", SPEC["qtola"]["print_w"], SPEC["qtola"]["print_h"])


# ---------------------------------------------------------------- 3D models
def m_jar(sc, cx, cy, label=JAR_LABEL):
    s = SPEC["jar"]
    o = sc.shadow(cx + 6, cy + 10, s["lid_d"] * 0.62, s["lid_d"] * 0.5)
    o += sc.prism(cx, cy, 0, s["body_d"] / 2, s["body_h"], 72, TEAL)
    o += sc.prism(cx, cy, s["body_h"] - 1, s["body_d"] / 2 + 0.6, 3, 72, GOLD, mat="metal")
    o += sc.prism(cx, cy, s["body_h"], s["lid_d"] / 2, s["lid_h"], 72, GOLD, mat="metal",
                  top_tex=(sc.texture(label), s["label_d"] / 2))
    sc.add((cx, cy, 0), o)


def m_spray(sc, cx, cy, label=SPRAY_LABEL):
    s = SPEC["spray"]
    r = s["body_d"] / 2
    z = 0
    o = sc.shadow(cx + 8, cy + 12, r * 1.25, r)
    o += sc.prism(cx, cy, z, r, s["body_h"], 72, TEAL,
                  side_tex=(sc.texture(label), s["label_w"], s["label_z"] + s["label_h"], s["label_z"], None))
    z += s["body_h"]
    o += sc.prism(cx, cy, z, r, s["shoulder_h"], 72, TEAL, r_top=s["neck_d"] / 2)
    z += s["shoulder_h"]
    o += sc.prism(cx, cy, z, s["neck_d"] / 2, s["neck_h"], 48, GOLD, mat="metal")
    z += s["neck_h"]
    o += sc.prism(cx, cy, z, s["cap_d"] / 2, s["cap_h"], 48, RED)
    sc.add((cx, cy, 0), o)


def m_tola(sc, cx, cy, key="tola", art=TOLA_PRINT):
    s = SPEC[key]
    r = s["flat"] / 2 / math.cos(math.pi / 8)
    front = math.degrees(math.atan2(-sc.far[1], -sc.far[0]))
    rot = front - 22.5
    o = sc.shadow(cx + 4, cy + 6, r * 1.3, r * 1.1, op=0.22)
    o += sc.prism(cx, cy, 0, r, s["body_h"], 8, GLASS, top="#8a4a22", mat="glass", rot=rot,
                  side_tex=(sc.texture(art), s["print_w"], s["body_h"] * 0.86, s["body_h"] * 0.86 - s["print_h"], front))
    z = s["body_h"]
    o += sc.prism(cx, cy, z, r * 0.92, s["neck_h"], 8, "#c9b49a", mat="glass", rot=rot, r_top=s["neck_d"] / 2)
    z += s["neck_h"]
    o += sc.prism(cx, cy, z, s["cap_d"] / 2, s["cap_h"], 48, GOLD, mat="metal")
    o += sc.prism(cx, cy, z + s["cap_h"] * 0.82, s["cap_d"] / 2 + 0.5, 1.2, 48, shade(GOLD, 0.8), mat="metal")
    sc.add((cx, cy, 0), o)


def m_carton(sc, x0, y0, dims, name, cat, size_txt, accent=TEAL):
    l, d, h = dims
    tex = {"front": sc.texture(carton_front(name, cat, size_txt, l, h, accent), ("cf", name, dims)),
           "right": sc.texture(carton_side(d, h), ("cs", dims)),
           "left": sc.texture(carton_side(d, h), ("cs", dims)),
           "top": sc.texture(carton_top(l, d), ("ct", dims))}
    o = sc.shadow(x0 + l / 2 + 6, y0 + d / 2 + 8, l * 0.75, d * 0.75)
    o += sc.box(x0, y0, 0, l, d, h, accent, top=CREAM, tex=tex)
    sc.add((x0 + l / 2, y0 + d / 2, 0), o)


def m_gift_closed(sc, x0, y0):
    g = SPEC["gift"]
    l, w, h, lh = g["l"], g["w"], g["h"], g["lid_h"]
    o = sc.shadow(x0 + l / 2 + 10, y0 + w / 2 + 14, l * 0.62, w * 0.75)
    o += sc.box(x0 + 1.5, y0 + 1.5, 0, l - 3, w - 3, h - lh, TEAL_DARK)
    tex = {"top": sc.texture(gift_lid_top(l, w), "giftlid"),
           "front": sc.texture(band_art(l, lh), ("band", l, lh)),
           "right": sc.texture(band_art(w, lh), ("band", w, lh)),
           "left": sc.texture(band_art(w, lh), ("band", w, lh))}
    o += sc.box(x0, y0, h - lh, l, w, lh, TEAL, tex=tex)
    sc.add((x0 + l / 2, y0 + w / 2, 0), o)


def gift_layout():
    """Cavity centres (x along length, y across width) for 2 jars + 2 tolas."""
    g = SPEC["gift"]
    jd, tf = SPEC["jar"]["lid_d"], SPEC["tola"]["flat"]
    gap = (g["l"] - 2 * jd - 2 * tf) / 5
    xs, x = [], gap
    for d in (jd, jd, tf, tf):
        xs.append(x + d / 2)
        x += d + gap
    return xs, gap


def m_gift_open(sc, x0, y0):
    g = SPEC["gift"]
    l, w, h = g["l"], g["w"], g["h"]
    xs, _ = gift_layout()
    o = sc.shadow(x0 + l / 2 + 10, y0 + w / 2 + 14, l * 0.62, w * 0.75)
    o += sc.box(x0, y0, 0, l, w, h, TEAL, top="#E9DCC5",
                tex={"front": sc.texture(band_art(l, h, TEAL_DARK), ("band2", l, h))})
    insert_z = h
    # cavity rims
    for i, cx in enumerate(xs):
        cy = y0 + w / 2
        if i < 2:
            rr = SPEC["jar"]["lid_d"] / 2 + 1
            pts = " ".join("%.2f,%.2f" % sc.P((x0 + cx + rr * math.cos(a / 30 * math.pi), cy + rr * math.sin(a / 30 * math.pi), insert_z)) for a in range(60))
        else:
            rr = SPEC["tola"]["flat"] / 2 + 1.5
            pts = " ".join("%.2f,%.2f" % sc.P(p) for p in [(x0 + cx - rr, cy - rr, insert_z), (x0 + cx + rr, cy - rr, insert_z),
                                                           (x0 + cx + rr, cy + rr, insert_z), (x0 + cx - rr, cy + rr, insert_z)])
        o += f'<polygon points="{pts}" fill="#3a2a1c"/>'
    # products seated in the insert (drawn after the box so they read as sitting inside)
    sub = Scene.__new__(Scene)
    sub.__dict__.update(sc.__dict__)
    sub.objects = []
    jars = [JAR_LABEL, OUD_LABEL]
    for i, cx in enumerate(xs):
        cy = y0 + w / 2
        if i < 2:
            sj = SPEC["jar"]
            zb = insert_z - sj["body_h"] * 0.55
            part = sub.prism(x0 + cx, cy, zb, sj["body_d"] / 2, sj["body_h"], 72, TEAL)
            part += sub.prism(x0 + cx, cy, zb + sj["body_h"], sj["lid_d"] / 2, sj["lid_h"], 72, GOLD, mat="metal",
                              top_tex=(sc.texture(jars[i]), sj["label_d"] / 2))
        else:
            st = SPEC["tola"]
            r = st["flat"] / 2 / math.cos(math.pi / 8)
            zb = insert_z - st["body_h"] * 0.6
            front = math.degrees(math.atan2(-sc.far[1], -sc.far[0]))
            part = sub.prism(x0 + cx, cy, zb, r, st["body_h"], 8, GLASS, top="#8a4a22", mat="glass", rot=front - 22.5)
            part += sub.prism(x0 + cx, cy, zb + st["body_h"], st["cap_d"] / 2, st["cap_h"], 48, GOLD, mat="metal")
        o += part
    sc.add((x0 + l / 2, y0 + w / 2, 0), o)


def m_mailer(sc, x0, y0):
    l, w, h = SPEC["mailer"]
    tex = {"top": sc.texture(mailer_top(l, w), "mtop"), "front": sc.texture(mailer_front(l, h), "mfront")}
    o = sc.shadow(x0 + l / 2 + 10, y0 + w / 2 + 14, l * 0.62, w * 0.75)
    o += sc.box(x0, y0, 0, l, w, h, KRAFT, tex=tex)
    # closure seal sticker on the front lip
    seal = sc.texture(seal_sticker(), "seal")
    a, b = sc.P((x0 + l / 2 - 22, y0, h + 0.1)), sc.P((x0 + l / 2 + 22, y0, h + 0.1))
    c = sc.P((x0 + l / 2 - 22, y0, h - 44))
    d_ = sc.P((x0 + l / 2 + 22, y0, h - 44))
    o += sc._mapped(seal, a, b, c, [a, b, d_, c])
    sc.add((x0 + l / 2, y0 + w / 2, 0), o)


def scene_svg(sc):
    return sc.render()


# ---------------------------------------------------------------- 2D technical drawing helpers
def dim_h(x1, x2, y, label, ext_from=None, col=INK):
    o = [f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{col}" stroke-width="1.6"/>']
    for x in (x1, x2):
        o.append(f'<line x1="{x-6}" y1="{y+6}" x2="{x+6}" y2="{y-6}" stroke="{col}" stroke-width="2"/>')
        if ext_from is not None:
            o.append(f'<line x1="{x}" y1="{ext_from}" x2="{x}" y2="{y + (8 if y > ext_from else -8)}" stroke="{LINE}" stroke-width="1" stroke-dasharray="4 3"/>')
    o.append(rect((x1 + x2) / 2 - measure(label, "enm", 20) / 2 - 8, y - 30, measure(label, "enm", 20) + 16, 24, CREAM))
    o.append(T(label, "enm", 20, (x1 + x2) / 2, y - 11, col, "middle"))
    return "".join(o)


def dim_v(x, y1, y2, label, ext_from=None, col=INK):
    o = [f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{col}" stroke-width="1.6"/>']
    for y in (y1, y2):
        o.append(f'<line x1="{x-6}" y1="{y+6}" x2="{x+6}" y2="{y-6}" stroke="{col}" stroke-width="2"/>')
        if ext_from is not None:
            o.append(f'<line x1="{ext_from}" y1="{y}" x2="{x + (8 if x > ext_from else -8)}" y2="{y}" stroke="{LINE}" stroke-width="1" stroke-dasharray="4 3"/>')
    cy = (y1 + y2) / 2
    w = measure(label, "enm", 20)
    o.append(f'<g transform="rotate(-90 {x} {cy})">{rect(x - w / 2 - 8, cy - 30, w + 16, 24, CREAM)}{T(label, "enm", 20, x, cy - 11, col, "middle")}</g>')
    return "".join(o)


def spec_list(x_right, y, rows, width=520):
    o = []
    for k, v in rows:
        o.append(T(k, "bold", 21, x_right, y, TEAL, "end"))
        o.append(T(v, "reg", 21, x_right - 200, y, INK, "end"))
        o.append(f'<line x1="{x_right - width}" y1="{y + 14}" x2="{x_right}" y2="{y + 14}" stroke="#D9CBB3" stroke-width="1.2"/>')
        y += 46
    return "".join(o), y


def framed_scene(sc_body, x, y, w, h, bg="#EFE4D2"):
    return rect(x, y, w, h, bg, rx=16) + sc_body


# ---------------------------------------------------------------- pages
import re as _re


def fit_render(build, x, y, w, h, az=-30, el=22, pad=0.9):
    """Render a scene scaled and centred to fit the box (projection is linear in scale/offset)."""
    probe = Scene(az=az, el=el, scale=1, ox=0, oy=0)
    build(probe)
    body = probe.render().split("</defs>", 1)[1]  # artwork coordinates live in defs; measure only the scene
    body = _re.sub(r'<clipPath.*?</clipPath>', '', body)
    pts = [tuple(map(float, q.split(","))) for m in _re.findall(r'points="([^"]+)"', body) for q in m.split()]
    xs, ys = [p_[0] for p_ in pts], [p_[1] for p_ in pts]
    k = min(w / (max(xs) - min(xs)), h / (max(ys) - min(ys))) * pad
    sc = Scene(az=az, el=el, scale=k, ox=x + w / 2 - k * (min(xs) + max(xs)) / 2, oy=y + h / 2 - k * (min(ys) + max(ys)) / 2)
    build(sc)
    return sc.render()


def spec_list2(x_right, y, rows, width=390):
    o = []
    for k_, v in rows:
        o.append(T(k_, "bold", 21, x_right, y, TEAL, "end"))
        sv, y2 = para(v, "reg", 19, x_right, y + 32, width, INK, 1.5)
        o.append(sv)
        y = y2 + 6
        o.append(f'<line x1="{x_right - width}" y1="{y - 12}" x2="{x_right}" y2="{y - 12}" stroke="#D9CBB3" stroke-width="1.2"/>')
        y += 22
    return "".join(o), y


pack_start = len(PAGES) + 1

# A. hero lineup
def hero(sc):
    m_mailer(sc, -470, 200)
    m_gift_closed(sc, -430, -10)
    m_carton(sc, 250, 210, SPEC["carton_spray"], "أسيل", "مرش", "500 مل", TEAL)
    m_carton(sc, 350, 120, SPEC["carton_jar"], "المخصوص", "معمول", "100 جرام", TEAL)
    m_spray(sc, 110, 10)
    m_jar(sc, -10, -110)
    m_jar(sc, 220, -40, OUD_LABEL)
    m_tola(sc, 90, -170)
    m_tola(sc, 140, -190, "qtola", QTOLA_PRINT)
b = [rect(70, 200, PW - 140, 690, "#EFE4D2", rx=18), fit_render(hero, 90, 215, PW - 180, 620)]
b.append(T("كل قطعة مرسومة بمقاسها الحقيقي ونسبها الصحيحة", "reg", 20, PW - 110, 870, MUTED, "end"))
page("التغليف ثلاثي الأبعاد", "منظومة التغليف كاملة: العلب والقوارير والكراتين وبوكس الهدايا وكرتون الشحن", "".join(b), len(PAGES) + 1)


def product_page(title, sub, build, drawing, specs, note=None):
    b = [rect(70, 200, 560, 700, "#EFE4D2", rx=18), fit_render(build, 90, 230, 520, 640)]
    b.append(drawing)
    s_, y = spec_list2(PW - 90, 245, specs)
    b.append(s_)
    if note:
        sn, _ = para(note, "reg", 17, PW - 90, max(y + 10, 820), 390, MUTED, 1.5)
        b.append(sn)
    page(title, sub, "".join(b), len(PAGES) + 1)


# B. jar
s = SPEC["jar"]
k = 2.0
x0, base = 780, 600
bw, lw_ = s["body_d"] * k, s["lid_d"] * k
th = total_h("jar")
dr = [rect(x0 - bw / 2, base - s["body_h"] * k, bw, s["body_h"] * k, TEAL, rx=6),
      rect(x0 - lw_ / 2, base - th * k, lw_, s["lid_h"] * k, GOLD, rx=4)]
dr.append(dim_h(x0 - lw_ / 2, x0 + lw_ / 2, base - th * k - 26, f"Ø {s['lid_d']}"))
dr.append(dim_h(x0 - bw / 2, x0 + bw / 2, base + 34, f"Ø {s['body_d']}"))
dr.append(dim_v(x0 + lw_ / 2 + 38, base - th * k, base, f"{th}", ext_from=x0 + lw_ / 2))
dr.append(dim_v(x0 - lw_ / 2 - 38, base - th * k, base - s["body_h"] * k, f"{s['lid_h']}", ext_from=x0 - lw_ / 2))
dr.append(dim_v(x0 - lw_ / 2 - 38, base - s["body_h"] * k, base, f"{s['body_h']}", ext_from=x0 - bw / 2))
dr.append(T("منظر أمامي", "bold", 20, x0, base + 82, MUTED, "middle"))
tx, ty = 1010, 400
dr.append(f'<circle cx="{tx}" cy="{ty}" r="{lw_/2}" fill="{GOLD}"/>')
dr.append(nest(JAR_LABEL, tx - s["label_d"] * k / 2, ty - s["label_d"] * k / 2, s["label_d"] * k, s["label_d"] * k))
dr.append(dim_h(tx - s["label_d"] * k / 2, tx + s["label_d"] * k / 2, ty + lw_ / 2 + 34, f"Ø {s['label_d']}"))
dr.append(T("منظر علوي · الملصق", "bold", 20, tx, ty + lw_ / 2 + 82, MUTED, "middle"))
product_page("علبة المعمول والعود", "جسم بترولي مطفي وغطاء ذهبي، والملصق الدائري على الغطاء · المقاسات بالمليمتر",
             lambda sc: (m_jar(sc, -50, 0), m_jar(sc, 55, 75, OUD_LABEL)), "".join(dr),
             [("السعة", s["volume"] + "، تكفي 80 إلى 100 جرام"), ("الجسم", f"Ø{s['body_d']} × {s['body_h']} مم، بترولي مطفي"),
              ("الغطاء", f"Ø{s['lid_d']} × {s['lid_h']} مم، ذهبي لامع"), ("الارتفاع الكلي", f"{th} مم"),
              ("الملصق", f"دائري Ø{s['label_d']} مم على الغطاء"), ("الخامة", "زجاج أو PET مقوّى، وغطاء ألمنيوم")])

# C. spray
s = SPEC["spray"]
k = 1.4
x0, base = 860, 680
r = s["body_d"] / 2 * k
th = total_h("spray")
zs = base - s["body_h"] * k
dr = [rect(x0 - r, zs, 2 * r, s["body_h"] * k, TEAL, rx=8),
      poly([(x0 - r, zs), (x0 + r, zs), (x0 + s["neck_d"] / 2 * k, zs - s["shoulder_h"] * k), (x0 - s["neck_d"] / 2 * k, zs - s["shoulder_h"] * k)], TEAL)]
zn = zs - s["shoulder_h"] * k
dr.append(rect(x0 - s["neck_d"] / 2 * k, zn - s["neck_h"] * k, s["neck_d"] * k, s["neck_h"] * k, GOLD))
zc = zn - s["neck_h"] * k
dr.append(rect(x0 - s["cap_d"] / 2 * k, zc - s["cap_h"] * k, s["cap_d"] * k, s["cap_h"] * k, RED, rx=3))
lab_top = base - (s["label_z"] + s["label_h"]) * k
dr.append(nest(SPRAY_LABEL, x0 - s["label_w"] / 2 * k * 0.92, lab_top, s["label_w"] * k * 0.92, s["label_h"] * k))
dr.append(dim_v(x0 + r + 48, base - th * k, base, f"{th}", ext_from=x0 + r))
dr.append(dim_v(x0 - r - 42, lab_top, base - s["label_z"] * k, f"{s['label_h']}", ext_from=x0 - r))
dr.append(dim_v(x0 - r - 42, base - s["label_z"] * k, base, f"{s['label_z']}", ext_from=x0 - r))
dr.append(dim_h(x0 - r, x0 + r, base + 34, f"Ø {s['body_d']}"))
dr.append(dim_h(x0 - s["cap_d"] / 2 * k, x0 + s["cap_d"] / 2 * k, base - th * k - 22, f"Ø {s['cap_d']}"))
dr.append(T("منظر أمامي", "bold", 20, x0, base + 82, MUTED, "middle"))
product_page("قارورة المرش", "500 مل · جسم بترولي وغطاء أحمر، والملصق المستطيل يلف القارورة",
             lambda sc: m_spray(sc, 0, 0), "".join(dr),
             [("السعة", s["volume"]), ("الجسم", f"Ø{s['body_d']} × {s['body_h']} مم"),
              ("الكتف والرقبة", f"{s['shoulder_h']} + {s['neck_h']} مم، ورقبة Ø{s['neck_d']}"),
              ("الغطاء", f"Ø{s['cap_d']} × {s['cap_h']} مم، أحمر مطفي"), ("الارتفاع الكلي", f"{th} مم"),
              ("الملصق", f"{s['label_w']}×{s['label_h']} مم، يبدأ على ارتفاع {s['label_z']} مم")],
             "يمكن استبدال الغطاء ببخّاخ ضغط بنفس قطر الرقبة.")

# D. tola
t, q = SPEC["tola"], SPEC["qtola"]
dr = []
k = 4.0
for key, x0 in (("tola", 770), ("qtola", 1000)):
    s = SPEC[key]
    base = 700
    fw = s["flat"] * k
    dr.append(rect(x0 - fw / 2, base - s["body_h"] * k, fw, s["body_h"] * k, GLASS, rx=4))
    dr.append(rect(x0 - fw * 0.21, base - s["body_h"] * k, fw * 0.42, s["body_h"] * k, shade(GLASS, 1.3)))
    zt = base - s["body_h"] * k
    dr.append(poly([(x0 - fw / 2 * 0.92, zt), (x0 + fw / 2 * 0.92, zt), (x0 + s["neck_d"] / 2 * k, zt - s["neck_h"] * k), (x0 - s["neck_d"] / 2 * k, zt - s["neck_h"] * k)], "#c9b49a"))
    zc = zt - s["neck_h"] * k
    dr.append(rect(x0 - s["cap_d"] / 2 * k, zc - s["cap_h"] * k, s["cap_d"] * k, s["cap_h"] * k, GOLD, rx=3))
    art = TOLA_PRINT if key == "tola" else QTOLA_PRINT
    pw, ph = min(s["print_w"], s["flat"]) * k, s["print_h"] * k
    dr.append(nest(art, x0 - pw / 2, base - s["body_h"] * 0.86 * k, pw, ph))
    th = total_h(key)
    dr.append(dim_v(x0 + fw / 2 + 38, base - th * k, base, f"{th}", ext_from=x0 + fw / 2))
    dr.append(dim_h(x0 - fw / 2, x0 + fw / 2, base + 34, f"{s['flat']}"))
    dr.append(dim_h(x0 - s["cap_d"] / 2 * k, x0 + s["cap_d"] / 2 * k, base - th * k - 22, f"Ø {s['cap_d']}"))
    dr.append(T("تولة" if key == "tola" else "ربع تولة", "bold", 20, x0, base + 82, MUTED, "middle"))
product_page("تولة الدهن", "زجاج مثمّن شفاف وغطاء ذهبي طويل، وطباعة ذهبية بالشعار ومثلثات الباب النجدي",
             lambda sc: (m_tola(sc, -18, 0), m_tola(sc, 24, 36, "qtola", QTOLA_PRINT)), "".join(dr),
             [("التولة", f"{t['volume']}، قاعدة {t['flat']}×{t['flat']} مم، ارتفاع {total_h('tola')} مم"),
              ("ربع التولة", f"{q['volume']}، قاعدة {q['flat']}×{q['flat']} مم، ارتفاع {total_h('qtola')} مم"),
              ("الغطاء", f"ألمنيوم ذهبي Ø{t['cap_d']}×{t['cap_h']} و Ø{q['cap_d']}×{q['cap_h']} مم"),
              ("الطباعة", f"ذهبية على 3 أوجه: {t['print_w']}×{t['print_h']} و {q['print_w']}×{q['print_h']} مم"),
              ("الخامة", "زجاج كريستالي مثمّن مع عصا تطبيق داخلية")],
             "الطباعة الذهبية بالشاشة الحريرية على الزجاج، وتغني عن الملصق الورقي.")

# E. cartons
def cartons(sc):
    m_carton(sc, -380, 0, SPEC["carton_spray"], "أسيل", "مرش", "500 مل", TEAL)
    m_carton(sc, -200, 20, SPEC["carton_jar"], "المخصوص", "معمول", "100 جرام", TEAL)
    m_carton(sc, -40, 40, SPEC["carton_jar"], "عود مسقى", "عود", "80 جرام", RED)
    m_carton(sc, 110, 60, SPEC["carton_tola"], "خمرية المسك", "دهن", "تولة", TEAL_DARK)
    m_carton(sc, 190, 70, SPEC["carton_qtola"], "دهن العود", "دهن", "ربع تولة", TEAL_DARK)
b = [rect(70, 200, PW - 140, 470, "#EFE4D2", rx=18), fit_render(cartons, 90, 215, PW - 180, 440)]
rows = [("الكرتونة", "الطول × العرض × الارتفاع (داخلي)", "يناسب"),
        ("كرتونة العلبة", "%d × %d × %d مم" % SPEC["carton_jar"], "علب المعمول والعود"),
        ("كرتونة المرش", "%d × %d × %d مم" % SPEC["carton_spray"], "قارورة 500 مل"),
        ("كرتونة التولة", "%d × %d × %d مم" % SPEC["carton_tola"], "تولة 12 مل"),
        ("كرتونة ربع التولة", "%d × %d × %d مم" % SPEC["carton_qtola"], "ربع تولة 3 مل")]
for r_, row in enumerate(rows):
    y = 735 + r_ * 42
    if r_ == 0:
        b.append(rect(90, y - 30, PW - 180, 42, TEAL, rx=8))
    for cx_, cell in zip([PW - 100, PW - 560, PW - 1100], row):
        b.append(T(cell, "bold" if r_ == 0 else "reg", 20, cx_, y, CREAM if r_ == 0 else INK, "end"))
page("كراتين المنتجات", "كرتون 350 جم مطبوع بالبترولي والنقشة، والجوانب رملي بمعينات الباب", "".join(b), len(PAGES) + 1)

# F. gift box
g = SPEC["gift"]
b = [rect(70, 200, 700, 430, "#EFE4D2", rx=18), rect(830, 200, 700, 430, "#EFE4D2", rx=18)]
b.append(fit_render(lambda sc: m_gift_closed(sc, 0, 0), 90, 215, 660, 360, el=24))
b.append(fit_render(lambda sc: m_gift_open(sc, 0, 0), 850, 215, 660, 360, el=34))
b.append(T("مغلق", "bold", 20, 420, 610, MUTED, "middle"))
b.append(T("مفتوح · الحشوة الداخلية", "bold", 20, 1180, 610, MUTED, "middle"))
k = 1.35
ix, iy = PW - 120 - g["l"] * k, 690
b.append(rect(ix, iy, g["l"] * k, g["w"] * k, "#E9DCC5", stroke=TEAL, sw=3))
xs_, gap = gift_layout()
for i, cx in enumerate(xs_):
    if i < 2:
        b.append(f'<circle cx="{ix + cx * k}" cy="{iy + g["w"] * k / 2}" r="{SPEC["jar"]["lid_d"] / 2 * k}" fill="#3a2a1c"/>')
    else:
        f_ = SPEC["tola"]["flat"] * k
        b.append(rect(ix + cx * k - f_ / 2, iy + g["w"] * k / 2 - f_ / 2, f_, f_, "#3a2a1c"))
b.append(dim_h(ix, ix + g["l"] * k, iy + g["w"] * k + 32, f"{g['l']}"))
b.append(dim_v(ix - 32, iy, iy + g["w"] * k, f"{g['w']}"))
b.append(dim_h(ix + (xs_[0] - SPEC['jar']['lid_d'] / 2) * k, ix + (xs_[0] + SPEC['jar']['lid_d'] / 2) * k, iy - 12, f"Ø {SPEC['jar']['lid_d']+2}"))
s_, _ = spec_list(ix - 90, 715, [("المقاس الخارجي", f"{g['l']} × {g['w']} × {g['h']} مم"),
                                 ("الغطاء", f"ارتفاع {g['lid_h']} مم، يغطي الجوانب"),
                                 ("الحشوة", "علبتين + تولتين"),
                                 ("الخامة", f"كرتون مقوّى {g['wall']} مم مغلّف بورق")], 470)
b.append(s_)
page("بوكس الهدايا", "صندوق مقوّى بغطاء منفصل، بالبترولي ونقشة البراند، وحشوة تثبّت المنتجات", "".join(b), len(PAGES) + 1)

# G. mailer
l, w_, h_ = SPEC["mailer"]
b = [rect(70, 200, 800, 700, "#EFE4D2", rx=18), fit_render(lambda sc: m_mailer(sc, 0, 0), 90, 230, 760, 640, el=24)]
s_, y = spec_list(PW - 100, 300, [("المقاس الداخلي", f"{l} × {w_} × {h_} مم"),
                                  ("يناسب", "بوكس الهدايا مع حشوة حماية"),
                                  ("الخامة", "كرتون مضلّع E-flute كرافت"),
                                  ("الطباعة الخارجية", "الشعار بالبترولي على الغطاء"),
                                  ("الطباعة الداخلية", "نقشة البراند على كامل الداخل"),
                                  ("الإغلاق", "ختم الإغلاق الدائري 50 مم")], 560)
b.append(s_)
b.append(T("ترتيب التغليف عند الشحن", "xbold", 24, PW - 100, y + 40, RED, "end"))
for i, step in enumerate(["المنتج في كرتونته", "داخل بوكس الهدايا مع كرت الشكر", "داخل كرتون الشحن ويُغلق بالختم"]):
    b.append(diamond(PW - 110, y + 82 + i * 42, 8, OCHRE))
    b.append(T(step, "reg", 21, PW - 132, y + 89 + i * 42, INK, "end"))
page("كرتون الشحن", "كرافت من الخارج، ونقشة البراند تفاجئ العميل من الداخل", "".join(b), len(PAGES) + 1)


# H. dielines
def tuck_dieline(L, W, H, k, x0, y0):
    """Reverse tuck-end carton net (cut = solid red, fold = dashed teal). x0,y0 = top-left of panel strip."""
    glue, tuck = 14, 15
    dust = W * 0.5
    o = []
    xs = [x0, x0 + glue * k, x0 + (glue + L) * k, x0 + (glue + L + W) * k, x0 + (glue + 2 * L + W) * k, x0 + (glue + 2 * L + 2 * W) * k]
    yt, yb = y0, y0 + H * k
    cut = lambda pts: f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{CUT}" stroke-width="2"/>'
    fold = lambda a, b_, c, d: f'<line x1="{a}" y1="{b_}" x2="{c}" y2="{d}" stroke="{FOLD}" stroke-width="1.6" stroke-dasharray="7 5"/>'
    # body panels
    o.append(rect(xs[1], yt, xs[5] - xs[1], yb - yt, "#F3EADB"))
    for xa in xs[2:5]:
        o.append(fold(xa, yt, xa, yb))
    o.append(fold(xs[1], yt, xs[1], yb))
    # glue flap
    o.append(cut([(xs[1], yt), (xs[0], yt + 10 * k), (xs[0], yb - 10 * k), (xs[1], yb)]))
    # top: closure on back panel (xs[3]..xs[4]) with tuck; dust flaps on sides
    o.append(fold(xs[3], yt, xs[4], yt))
    o.append(cut([(xs[3], yt), (xs[3], yt - W * k), (xs[3] + 3 * k, yt - (W + tuck) * k), (xs[4] - 3 * k, yt - (W + tuck) * k), (xs[4], yt - W * k), (xs[4], yt)]))
    o.append(fold(xs[3], yt - W * k, xs[4], yt - W * k))
    for xa, xb in ((xs[2], xs[3]), (xs[4], xs[5])):
        o.append(fold(xa, yt, xb, yt))
        o.append(cut([(xa, yt), (xa + 2 * k, yt - dust * k), (xb - 6 * k, yt - dust * k), (xb, yt - 4 * k), (xb, yt)]))
    o.append(cut([(xs[1], yt), (xs[2], yt)]))
    # bottom: closure on front panel (xs[1]..xs[2])
    o.append(fold(xs[1], yb, xs[2], yb))
    o.append(cut([(xs[1], yb), (xs[1], yb + W * k), (xs[1] + 3 * k, yb + (W + tuck) * k), (xs[2] - 3 * k, yb + (W + tuck) * k), (xs[2], yb + W * k), (xs[2], yb)]))
    o.append(fold(xs[1], yb + W * k, xs[2], yb + W * k))
    for xa, xb in ((xs[2], xs[3]), (xs[4], xs[5])):
        o.append(fold(xa, yb, xb, yb))
        o.append(cut([(xa, yb), (xa + 2 * k, yb + dust * k), (xb - 6 * k, yb + dust * k), (xb, yb + 4 * k), (xb, yb)]))
    o.append(cut([(xs[3], yb), (xs[4], yb)]))
    o.append(cut([(xs[5], yt), (xs[5], yb)]))
    # panel artwork hints
    o.append(nest(LOGO, xs[1] + L * k * 0.2, yt + H * k * 0.25, L * k * 0.6, vb=MARK_VB))
    # dimensions
    o.append(dim_h(xs[1], xs[2], yb + (W + tuck) * k + 40, f"{L}"))
    o.append(dim_h(xs[2], xs[3], yb + (W + tuck) * k + 40, f"{W}"))
    o.append(dim_v(xs[5] + 40, yt, yb, f"{H}"))
    o.append(dim_v(xs[0] - 34, yt - (W + tuck) * k, yt, f"{W + tuck}"))
    return "".join(o)


b = []
L_, W_, H_ = SPEC["carton_jar"]
b.append(tuck_dieline(L_, W_, H_, 2.05, 150, 430))
b.append(T("كرتونة علبة المعمول والعود · %d×%d×%d مم" % SPEC["carton_jar"], "xbold", 24, PW - 100, 230, TEAL, "end"))
leg = [(CUT, "خط قص", False), (FOLD, "خط طي", True)]
for i, (c, t_, dash) in enumerate(leg):
    y = 280 + i * 40
    da = ' stroke-dasharray="7 5"' if dash else ""
    b.append(f'<line x1="{PW-220}" y1="{y-7}" x2="{PW-160}" y2="{y-7}" stroke="{c}" stroke-width="2.4"{da}/>')
    b.append(T(t_, "reg", 20, PW - 240, y, INK, "end"))
s_, _ = spec_list(PW - 100, 420, [("نوع العلبة", "قفل عكسي · Reverse Tuck End"),
                                  ("لسان اللصق", "14 مم"), ("لسان القفل", "15 مم"),
                                  ("الخامة", "كرتون 350 جم مطفي")], 430)
b.append(s_)
b.append(T("القالب نفسه يُعاد لكل الكراتين بتغيير المقاسات حسب الجدول.", "reg", 18, PW - 100, 905, MUTED, "end"))
page("قوالب القص · الكرتونة", "الشكل المفرود للطباعة والقص، بالمقاس الحقيقي", "".join(b), len(PAGES) + 1)


def tray_net(L, W, H, k, cx, cy, label):
    o = []
    x0, y0 = cx - L * k / 2, cy - W * k / 2
    o.append(rect(x0, y0, L * k, W * k, "#F3EADB", stroke=FOLD, sw=1.6))
    for (x, y, w, h) in [(x0, y0 - H * k, L * k, H * k), (x0, y0 + W * k, L * k, H * k),
                         (x0 - H * k, y0, H * k, W * k), (x0 + L * k, y0, H * k, W * k)]:
        o.append(rect(x, y, w, h, "#F3EADB", stroke=CUT, sw=2))
    # corner glue tabs
    t = 12 * k
    for (ax, ay, sx, sy) in [(x0, y0, -1, -1), (x0 + L * k, y0, 1, -1), (x0, y0 + W * k, -1, 1), (x0 + L * k, y0 + W * k, 1, 1)]:
        o.append(poly([(ax, ay), (ax + sx * t, ay), (ax + sx * t, ay + sy * H * k * 0.85), (ax, ay + sy * H * k)], "#E3D5BE"))
    o.append(rect(x0, y0, L * k, W * k, "none", stroke=FOLD, sw=1.6))
    o.append(T(label, "xbold", 22, cx, cy + 8, TEAL, "middle"))
    o.append(dim_h(x0, x0 + L * k, y0 + W * k + H * k + 36, f"{L}"))
    o.append(dim_v(x0 + L * k + H * k + 36, y0, y0 + W * k, f"{W}"))
    o.append(dim_v(x0 - H * k - 36, y0 - H * k, y0, f"{H}"))
    return "".join(o)


b = []
g = SPEC["gift"]
b.append(tray_net(g["l"], g["w"], g["h"] - 5, 1.1, 470, 560, "القاعدة"))
b.append(tray_net(g["l"] + 4, g["w"] + 4, g["lid_h"], 1.1, 1180, 560, "الغطاء"))
b.append(T("بوكس الهدايا · الصندوق المقوّى", "xbold", 24, PW - 100, 230, TEAL, "end"))
b.append(T("القاعدة %d×%d×%d مم · الغطاء %d×%d×%d مم (أوسع 2 مم من كل جهة)" % (g["l"], g["w"], g["h"] - 5, g["l"] + 4, g["w"] + 4, g["lid_h"]),
           "reg", 20, PW - 100, 270, INK, "end"))
b.append(T("الكرتون المقوّى يُقص ثم يُغلّف بورق مطبوع؛ يُضاف 15 مم للف الورق حول الحواف.", "reg", 18, PW - 100, 905, MUTED, "end"))
page("قوالب القص · بوكس الهدايا", "الشكل المفرود للقاعدة والغطاء", "".join(b), len(PAGES) + 1)

# I. master table
b = []
rows = [("القطعة", "المقاس (مم)", "الارتفاع الكلي", "السعة / الاستخدام"),
        ("علبة المعمول والعود", "Ø%d جسم · Ø%d غطاء" % (SPEC["jar"]["body_d"], SPEC["jar"]["lid_d"]), "%d" % total_h("jar"), "250 مل · 80 إلى 100 جرام"),
        ("قارورة المرش", "Ø%d" % SPEC["spray"]["body_d"], "%d" % total_h("spray"), "500 مل"),
        ("تولة", "%d×%d (مثمّن)" % (SPEC["tola"]["flat"], SPEC["tola"]["flat"]), "%d" % total_h("tola"), "12 مل"),
        ("ربع تولة", "%d×%d (مثمّن)" % (SPEC["qtola"]["flat"], SPEC["qtola"]["flat"]), "%d" % total_h("qtola"), "3 مل"),
        ("كرتونة العلبة", "%d×%d" % SPEC["carton_jar"][:2], "%d" % SPEC["carton_jar"][2], "علبة واحدة"),
        ("كرتونة المرش", "%d×%d" % SPEC["carton_spray"][:2], "%d" % SPEC["carton_spray"][2], "قارورة واحدة"),
        ("كرتونة التولة", "%d×%d" % SPEC["carton_tola"][:2], "%d" % SPEC["carton_tola"][2], "تولة واحدة"),
        ("كرتونة ربع التولة", "%d×%d" % SPEC["carton_qtola"][:2], "%d" % SPEC["carton_qtola"][2], "ربع تولة"),
        ("بوكس الهدايا", "%d×%d" % (SPEC["gift"]["l"], SPEC["gift"]["w"]), "%d" % SPEC["gift"]["h"], "علبتين + تولتين"),
        ("كرتون الشحن", "%d×%d" % SPEC["mailer"][:2], "%d" % SPEC["mailer"][2], "بوكس الهدايا")]
colsx = [PW - 100, PW - 520, PW - 900, PW - 1160]
for r_, row in enumerate(rows):
    y = 240 + r_ * 56
    if r_ == 0:
        b.append(rect(90, y - 36, PW - 180, 52, TEAL, rx=10))
    elif r_ % 2 == 0:
        b.append(rect(90, y - 36, PW - 180, 52, "#EFE4D2"))
    for cx_, cell in zip(colsx, row):
        f_ = "enm" if (not AR.search(cell)) else ("bold" if r_ == 0 else "reg")
        b.append(T(cell, f_, 21, cx_ - 20, y, CREAM if r_ == 0 else INK, "end"))
notes = ["المقاسات مقترحة على مقاسات المصانع الشائعة؛ اطلب عينة من المورد وطابقها قبل طباعة الكراتين.",
         "مقاسات الكراتين داخلية، وتشمل 2 إلى 4 مم فراغ حول المنتج.",
         "ملفات الملصقات والطباعة الذهبية والقوالب مرفقة فكتور بالمقاس الحقيقي."]
for i, t_ in enumerate(notes):
    b.append(diamond(PW - 110, 850 + i * 34 - 7, 7, RED))
    b.append(T(t_, "reg", 19, PW - 130, 850 + i * 34, INK, "end"))
page("جدول المقاسات", "كل مقاسات التغليف في مكان واحد للمورد والمطبعة", "".join(b), len(PAGES) + 1)

pack_end = len(PAGES)

# true-scale print files for the packaging (1 mm = 10 units)
PACK_FILES = {
    "طباعة-التولة-ذهبي": (TOLA_PRINT, SPEC["tola"]["print_w"]),
    "طباعة-ربع-التولة-ذهبي": (QTOLA_PRINT, SPEC["qtola"]["print_w"]),
    "غطاء-بوكس-الهدايا-300x150": (gift_lid_top(SPEC["gift"]["l"], SPEC["gift"]["w"]), SPEC["gift"]["l"]),
    "وجه-كرتونة-العلبة": (carton_front("المخصوص", "معمول", "100 جرام", SPEC["carton_jar"][0], SPEC["carton_jar"][2]), SPEC["carton_jar"][0]),
    "غطاء-كرتون-الشحن": (mailer_top(SPEC["mailer"][0], SPEC["mailer"][1]), SPEC["mailer"][0]),
}


def dieline_file(L, W, H):
    glue, tuck = 14, 15
    Wt = (glue + 2 * L + 2 * W + 20)
    Ht = (H + 2 * (W + tuck) + 20)
    body = tuck_dieline(L, W, H, 10, 100, (W + tuck + 10) * 10)
    doc = svgdoc(Wt * 10, Ht * 10, body)  # 10 units = 1 mm; declare the true size for print software
    return doc.replace(f'width="{Wt * 10}" height="{Ht * 10}"', f'width="{Wt}mm" height="{Ht}mm"', 1)
