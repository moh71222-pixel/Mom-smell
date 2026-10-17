"""Three free-hand brand compositions for رائحة أمي, all vector, all with the brand font."""
import math, os, sys
import resvg_py
sys.path.insert(0, os.path.dirname(__file__))
from brand import TEAL, TEAL_DARK, RED, OCHRE, SAND, CREAM, text_path, svg
import badges as Bd
import wordmark as W  # brand-font stacking helpers (argv: font, wm-dir, badges-dir)

OUT = sys.argv[4]
os.makedirs(OUT, exist_ok=True)
poly, diamond, tri_row, ridge = Bd.poly, Bd.diamond, Bd.tri_row, Bd.ridge


def curved(text, cx, cy, r, start_deg, col, size=40, spacing=1.0, bottom=False):
    """Set Latin capitals along a circle (top arc reads clockwise, bottom arc counter-clockwise)."""
    widths = []
    for ch in text:
        if ch == " ":
            widths.append(size * 0.35)
            continue
        _, w = text_path(ch, "Jost.ttf", size, 0, 0, "middle", wght=600)
        widths.append(w + size * 0.18 * spacing)
    total = sum(widths)
    arc = total / r * 180 / math.pi
    a = start_deg - arc / 2 if not bottom else start_deg + arc / 2
    out = []
    for ch, w in zip(text, widths):
        step = w / r * 180 / math.pi
        mid = a + (step / 2 if not bottom else -step / 2)
        if ch != " ":
            d, _ = text_path(ch, "Jost.ttf", size, 0, size * 0.36 if not bottom else size * 0.36, "middle", wght=600)
            if not bottom:
                tf = f"translate({cx},{cy}) rotate({mid}) translate(0,{-r})"
            else:
                tf = f"translate({cx},{cy}) rotate({mid - 180}) translate(0,{r})"
            out.append(f'<path transform="{tf}" d="{d}" fill="{col}"/>')
        a += step if not bottom else -step
    return "".join(out)


def star(cx, cy, r, col):
    pts = []
    for k in range(8):
        ang = math.pi / 4 * k - math.pi / 2
        rr = r if k % 2 == 0 else r * 0.38
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    return poly(pts, col)


def sadu_band(x0, y0, x1, y1, h, cols):
    """Woven Sadu border: stepped diamonds between saw-tooth edges, around a rectangle."""
    bg, dia, tooth, dot = cols
    out = [f'<path d="M{x0},{y0} H{x1} V{y1} H{x0} Z M{x0+h},{y0+h} V{y1-h} H{x1-h} V{y0+h} Z" '
           f'fill="{bg}" fill-rule="evenodd"/>']

    def run(ax, ay, bx, by, nx, ny):
        length = math.hypot(bx - ax, by - ay)
        n = max(4, round(length / (h * 1.25)))
        ux, uy = (bx - ax) / length, (by - ay) / length
        seg = length / n
        for k in range(n):
            c = (ax + ux * seg * (k + .5) + nx * h / 2, ay + uy * seg * (k + .5) + ny * h / 2)
            # stepped diamond
            r = h * 0.32
            out.append(diamond(c[0], c[1], r, dia if k % 2 == 0 else dot, hole=bg))
            # saw teeth on both edges
            for side in (0, 1):
                bxp = ax + ux * seg * k + nx * (h if side else 0)
                byp = ay + uy * seg * k + ny * (h if side else 0)
                inward = (nx, ny) if side == 0 else (-nx, -ny)
                p1 = (bxp, byp)
                p2 = (bxp + ux * seg, byp + uy * seg)
                p3 = (bxp + ux * seg / 2 + inward[0] * h * 0.18, byp + uy * seg / 2 + inward[1] * h * 0.18)
                out.append(poly([p1, p2, p3], tooth))
    run(x0 + h, y0, x1 - h, y0, 0, 1)
    run(x0 + h, y1 - h, x1 - h, y1 - h, 0, 1)
    run(x0, y0 + h, x0, y1 - h, 1, 0)
    run(x1 - h, y0 + h, x1 - h, y1 - h, 1, 0)
    for cx, cy in ((x0 + h / 2, y0 + h / 2), (x1 - h / 2, y0 + h / 2), (x0 + h / 2, y1 - h / 2), (x1 - h / 2, y1 - h / 2)):
        out.append(star(cx, cy, h * 0.38, tooth))
    return "".join(out)


def save(name, s, width=2000):
    open(os.path.join(OUT, name + ".svg"), "w").write(s)
    open(os.path.join(OUT, name + ".png"), "wb").write(bytes(resvg_py.svg_to_bytes(svg_string=s, width=width)))


# ---------- A. Hail seal ----------
def seal(bg=SAND, ink=TEAL, ring=TEAL, light=CREAM, accent=OCHRE, page=CREAM):
    cx, cy, R = 500, 500, 440
    p = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{ring}"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{R-14}" fill="none" stroke="{OCHRE}" stroke-width="4"/>']
    # outer text band
    p.append(curved("RAIHAT UMMI", cx, cy, R - 62, 0, light, 50, 1.4))
    p.append(curved("HAIL · SAUDI ARABIA", cx, cy, R - 62, 180, accent, 34, 1.2, bottom=True))
    p.append(star(cx - (R - 62), cy, 16, accent))
    p.append(star(cx + (R - 62), cy, 16, accent))
    # inner disc
    r2 = R - 118
    p.append(f'<circle cx="{cx}" cy="{cy}" r="{r2}" fill="{bg}"/>')
    # ring of tiny triangles inside the disc edge
    n = 48
    for k in range(n):
        a = 2 * math.pi * k / n
        tip = (cx + (r2 - 26) * math.cos(a), cy + (r2 - 26) * math.sin(a))
        b1 = (cx + r2 * math.cos(a - 0.055), cy + r2 * math.sin(a - 0.055))
        b2 = (cx + r2 * math.cos(a + 0.055), cy + r2 * math.sin(a + 0.055))
        p.append(poly([b1, b2, tip], OCHRE if k % 2 == 0 else RED))
    # Aja & Salma clipped to the disc
    p.append(f'<clipPath id="disc"><circle cx="{cx}" cy="{cy}" r="{r2-30}"/></clipPath>')
    p.append(f'<g clip-path="url(#disc)">{ridge(cx - r2, cx + r2, cy + r2, 150, RED)}'
             f'<rect x="{cx-r2}" y="{cy+r2-60}" width="{2*r2}" height="60" fill="{RED}"/></g>')
    body, bottom = Bd.stacked(cx, cy - 205, 330, 300, ink)
    p.append(body)
    p.append(star(cx, cy - 238, 14, OCHRE))
    return svg(1000, 1000, "".join(p), page)


# ---------- B. mother's door at night ----------
def night(bg=CREAM):
    p = []
    L, R, top, bot = 190, 810, 70, 820
    cx = (L + R) / 2
    rr = (R - L) / 2
    panel = f"M{L},{bot} V{top+rr} A{rr},{rr} 0 0 1 {R},{top+rr} V{bot} Z"
    p.append(f'<clipPath id="panel"><path d="{panel}"/></clipPath>')
    g = [f'<rect x="{L}" y="{top}" width="{R-L}" height="{bot-top}" fill="{TEAL_DARK}"/>']
    # crescent and stars over Hail
    g.append(f'<circle cx="{cx+150}" cy="{top+150}" r="44" fill="{OCHRE}"/>'
             f'<circle cx="{cx+168}" cy="{top+138}" r="40" fill="{TEAL_DARK}"/>')
    for x, y, r in ((cx - 170, top + 140, 12), (cx - 60, top + 95, 8), (cx + 40, top + 200, 7),
                    (cx - 230, top + 250, 7), (cx + 230, top + 270, 9), (cx - 110, top + 215, 6)):
        g.append(star(x, y, r, CREAM))
    g.append(ridge(L - 40, cx + 70, bot - 210, 250, RED))
    g.append(ridge(cx - 70, R + 40, bot - 210, 200, "#8E3B31"))
    g.append(f'<rect x="{L}" y="{bot-215}" width="{R-L}" height="215" fill="{SAND}"/>')
    # the door: mud wall, open leaves, warm light spilling out
    dx0, dx1, dy0 = cx - 95, cx + 95, bot - 430
    g.append(f'<rect x="{dx0-40}" y="{dy0-40}" width="{dx1-dx0+80}" height="{bot-215-dy0+40}" fill="#D9C29E"/>')
    for k in range(5):
        a = dx0 - 40 + k * (dx1 - dx0 + 80) / 5
        w = (dx1 - dx0 + 80) / 5
        g.append(poly([(a + 4, dy0 - 40), (a + w - 4, dy0 - 40), (a + w / 2, dy0 - 82)], "#D9C29E"))
    g.append(f'<rect x="{dx0}" y="{dy0}" width="{dx1-dx0}" height="{bot-215-dy0}" fill="{OCHRE}"/>')
    g.append(poly([(dx0, bot - 215), (dx1, bot - 215), (dx1 + 70, bot), (dx0 - 70, bot)], "#E2C58A"))
    g.append(poly([(dx0, dy0), (dx0 + 60, dy0 + 22), (dx0 + 60, bot - 230), (dx0, bot - 215)], TEAL))
    g.append(poly([(dx1, dy0), (dx1 - 60, dy0 + 22), (dx1 - 60, bot - 230), (dx1, bot - 215)], TEAL))
    for y in range(int(dy0) + 40, int(bot) - 240, 46):
        g.append(f'<circle cx="{dx0+30}" cy="{y+12}" r="4" fill="{OCHRE}"/><circle cx="{dx1-30}" cy="{y+12}" r="4" fill="{OCHRE}"/>')
    g.append(Bd.smoke(cx, dy0 - 10, 120, CREAM, 6))
    p.append(f'<g clip-path="url(#panel)">{"".join(g)}</g>')
    p.append(f'<path d="{panel}" fill="none" stroke="{TEAL}" stroke-width="16"/>')
    b, total, x0 = W.draw(W.shape("رائحة أمي"), 150, cx, bot + 185, "middle", default=TEAL)
    p.append(b)
    p.append(tri_row(x0, x0 + total, bot + 230, 24, (OCHRE, RED)))
    p.append(Bd.english(bot + 320, TEAL, 46))
    p.append(Bd.tagline(bot + 375, RED))
    return svg(1000, bot + 420, "".join(p), bg)


# ---------- C. Sadu square ----------
def sadu(bg=CREAM, ink=TEAL):
    x0, y0, x1, y1, h = 90, 90, 910, 910, 78
    p = [sadu_band(x0, y0, x1, y1, h, (RED, CREAM, TEAL_DARK, OCHRE))]
    p.append(f'<rect x="{x0+h}" y="{y0+h}" width="{x1-x0-2*h}" height="{y1-y0-2*h}" fill="{SAND}"/>')
    p.append(f'<rect x="{x0+h+18}" y="{y0+h+18}" width="{x1-x0-2*h-36}" height="{y1-y0-2*h-36}" '
             f'fill="none" stroke="{OCHRE}" stroke-width="4"/>')
    body, bottom = Bd.stacked(500, y0 + h + 70, 520, 470, ink)
    p.append(body)
    p.append(Bd.divider(500, y1 - h - 80, 150, OCHRE, RED))
    p.append(Bd.english(y1 + 95, TEAL, 50))
    p.append(Bd.tagline(y1 + 150, RED))
    return svg(1000, y1 + 190, "".join(p), bg)


save("أ-ختم-حائل", seal())
save("أ-ختم-حائل-معكوس", seal(bg=TEAL_DARK, ink=CREAM, ring=OCHRE, light=TEAL_DARK, accent=TEAL_DARK, page=TEAL_DARK))
save("أ-ختم-حائل-شفاف", seal(page=None))
save("ب-باب-أمي-ليلاً", night())
save("ج-إطار-السدو", sadu())
print("creative ok")
