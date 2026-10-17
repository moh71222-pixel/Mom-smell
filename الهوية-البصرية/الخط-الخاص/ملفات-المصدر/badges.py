"""Logo badges 2 (square Kufic frame) and 3 (Najdi door), drawn with Raihat Kufi."""
import os, sys
import resvg_py
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
sys.path.insert(0, os.path.dirname(__file__))
from brand import TEAL, TEAL_DARK, RED, OCHRE, SAND, CREAM, text_path, svg
import wordmark as W  # loads the custom font (argv[1])

OUT = sys.argv[3]
os.makedirs(OUT, exist_ok=True)
U = W.UPEM


# ---------- text fitting ----------
def boxes(text):
    """Per-glyph ink boxes in font units, relative to (left edge, baseline), y up."""
    glyphs = W.shape(text)
    total = sum(p.x_advance for _, p in glyphs)
    out, cx = [], 0
    for g, p in glyphs:
        bp = BoundsPen(W.GS)
        W.GS[g].draw(TransformPen(bp, (1, 0, 0, 1, cx + p.x_offset, p.y_offset)))
        if bp.bounds:
            out.append(bp.bounds)
        cx += p.x_advance
    return out, total


B1, T1 = boxes("رائحة")
B2, T2 = boxes("أمي")


def min_gap(pad, dx):
    """Smallest baseline distance so line 2 (shifted dx units) never touches line 1."""
    off1, off2 = -T1 / 2, -T2 / 2 + dx
    need = 0
    for a in B1:
        for b in B2:
            if a[0] + off1 - pad < b[2] + off2 and b[0] + off2 - pad < a[2] + off1:
                need = max(need, -a[1] + b[3] + pad)
    return need


TOP1 = max(b[3] for b in B1)
BOT2 = min(b[1] for b in B2)


def layout(dx):
    gap = min_gap(40, dx)
    left = min(-T1 / 2, -T2 / 2 + dx)
    right = max(T1 / 2, T2 / 2 + dx)
    return gap, right - left, (left + right) / 2


def fit_score(dx, box_w=520, box_h=420):
    gap, span, _ = layout(dx)
    return min(box_w / span, box_h / (TOP1 + gap - BOT2))


DX = 0
GAP, WIDTH, CENTRE = layout(DX)
HEIGHT = TOP1 + GAP - BOT2


def stacked(cx, top, width, height, ink):
    """رائحة over أمي (nudged so the letters interlock), as large as fits; returns svg and bottom y."""
    s = min(width / WIDTH, height / HEIGHT)
    size = s * U
    x = cx - CENTRE * s
    y1 = top + TOP1 * s
    y2 = y1 + GAP * s
    b1, _, _ = W.draw(W.shape("رائحة"), size, x, y1, "middle", default=ink)
    b2, _, _ = W.draw(W.shape("أمي"), size, x + DX * s, y2, "middle", default=ink)
    return b1 + b2, top + HEIGHT * s


# ---------- shapes ----------
def poly(pts, col):
    return '<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" fill="{col}"/>'


def tri_row(x0, x1, y, h, cols, down=False, n=None):
    n = n or max(3, round((x1 - x0) / (h * 1.2)))
    w = (x1 - x0) / n
    out = []
    for k in range(n):
        a = x0 + k * w
        pts = [(a, y), (a + w, y), (a + w / 2, y + h)] if down else [(a, y + h), (a + w, y + h), (a + w / 2, y)]
        out.append(poly(pts, cols[k % len(cols)]))
    return "".join(out)


def diamond(cx, cy, r, col, hole=None):
    d = poly([(cx, cy - r), (cx + r * .78, cy), (cx, cy + r), (cx - r * .78, cy)], col)
    if hole:
        d += poly([(cx, cy - r * .45), (cx + r * .35, cy), (cx, cy + r * .45), (cx - r * .35, cy)], hole)
    return d


def divider(cx, y, half, col, accent):
    return (f'<line x1="{cx-half}" y1="{y}" x2="{cx-22}" y2="{y}" stroke="{col}" stroke-width="5"/>'
            f'<line x1="{cx+22}" y1="{y}" x2="{cx+half}" y2="{y}" stroke="{col}" stroke-width="5"/>'
            + diamond(cx, y, 16, accent))


def corner(x, y, sx, sy, col, acc):
    """Najdi corner motif: stepped L with a small diamond."""
    pts = [(0, 0), (60, 0), (60, 14), (14, 14), (14, 60), (0, 60)]
    out = poly([(x + px * sx, y + py * sy) for px, py in pts], col)
    return out + diamond(x + 34 * sx, y + 34 * sy, 12, acc)


def english(y, col, size=56, w=1000):
    d, _ = text_path("RAIHAT UMMI", "Jost.ttf", size, w / 2, y, "middle", wght=600, tracking=220)
    return f'<path d="{d}" fill="{col}"/>'


def tagline(y, col, w=1000):
    d, _ = text_path("من أرض حاتم · حائل", "Almarai-Regular.ttf", 32, w / 2, y, "middle")
    return f'<path d="{d}" fill="{col}"/>'


def ridge(x0, x1, base, h, col):
    w = x1 - x0
    pts = [(x0, base), (x0 + w * .10, base - h * .45), (x0 + w * .18, base - h * .35), (x0 + w * .30, base - h),
           (x0 + w * .42, base - h * .55), (x0 + w * .50, base - h * .62), (x0 + w * .63, base - h * .92),
           (x0 + w * .78, base - h * .40), (x0 + w * .88, base - h * .52), (x1, base)]
    return poly(pts, col)


def smoke(cx, base, h, col, sw=7):
    return (f'<path d="M{cx},{base} c-{h*.22},-{h*.2} {h*.22},-{h*.38} 0,-{h*.58} '
            f's-{h*.2},-{h*.3} {h*.06},-{h*.42}" fill="none" stroke="{col}" stroke-width="{sw}" '
            f'stroke-linecap="round"/>')


# ---------- 2. square Kufic frame ----------
def square(bg=SAND, frame=TEAL, ink=TEAL, line=OCHRE, hail=False, tag=RED):
    p = []
    x0, y0, s, sw = 160, 70, 680, 30
    x1, y1 = x0 + s, y0 + s
    cx = (x0 + x1) / 2
    p.append(f'<rect x="{x0}" y="{y0}" width="{s}" height="{s}" fill="none" stroke="{frame}" stroke-width="{sw}"/>')
    i0, j0, i1, j1 = x0 + 32, y0 + 32, x1 - 32, y1 - 32
    p.append(f'<rect x="{i0}" y="{j0}" width="{i1-i0}" height="{j1-j0}" fill="none" stroke="{line}" stroke-width="5"/>')
    p.append(tri_row(i0 + 70, i1 - 70, j0 + 14, 24, (OCHRE, RED), down=True, n=11))
    p += [corner(i0 + 12, j0 + 12, 1, 1, frame, RED), corner(i1 - 12, j0 + 12, -1, 1, frame, RED),
          corner(i0 + 12, j1 - 12, 1, -1, frame, RED), corner(i1 - 12, j1 - 12, -1, -1, frame, RED)]
    if hail:
        p.append(ridge(i0 + 3, i1 - 3, j1 - 3, 80, RED))
        body, _ = stacked(cx, j0 + 50, 540, 425, ink)
    else:
        p.append(tri_row(i0 + 70, i1 - 70, j1 - 38, 24, (OCHRE, RED), n=11))
        body, _ = stacked(cx, j0 + 52, 550, 500, ink)
    p.append(body)
    for x in (x0, x1):
        p.append(diamond(x, (y0 + y1) / 2, 32, OCHRE, hole=frame))
    p.append(english(y1 + 105, ink))
    p.append(divider(500, y1 + 140, 150, line, RED))
    p.append(tagline(y1 + 195, tag))
    return svg(1000, y1 + 240, "".join(p), bg)


# ---------- 3. Najdi door ----------
def door(bg=SAND, frame=TEAL, ink=TEAL, line=OCHRE, hail=False, tag=RED):
    p = []
    L, R, top, bot, sw = 215, 785, 230, 990, 30
    cx = (L + R) / 2
    if hail:  # Aja and Salma rising behind the gate
        p.append(ridge(10, cx + 60, bot - 120, 330, RED))
        p.append(ridge(cx - 60, 990, bot - 120, 270, RED))
        p.append(f'<rect x="{L-sw/2}" y="{top}" width="{R-L+sw}" height="{bot-top}" fill="{bg}"/>')
    n, w = 5, (R - L + sw) / 5
    for k in range(n):
        a = L - sw / 2 + k * w
        col = (OCHRE if k % 2 == 0 else RED) if hail else frame
        p.append(poly([(a + 6, top - 4), (a + w - 6, top - 4), (a + w / 2, top - 72)], col))
    p.append(smoke(cx, top - 82, 95, OCHRE))
    p.append(f'<rect x="{L}" y="{top+sw/2}" width="{R-L}" height="{bot-top-sw}" fill="none" stroke="{frame}" stroke-width="{sw}"/>')
    i0, j0, i1, j1 = L + 32, top + 47, R - 32, bot - 47
    p.append(f'<rect x="{i0}" y="{j0}" width="{i1-i0}" height="{j1-j0}" fill="none" stroke="{line}" stroke-width="5"/>')
    p.append(tri_row(i0 + 16, i1 - 16, j0 + 16, 32, (OCHRE, RED), down=True, n=9))
    for x in (i0 + 22, i1 - 22):
        for k in range(9):
            p.append(f'<circle cx="{x}" cy="{j0 + 80 + k * 56}" r="6" fill="{line}"/>')
    body, bottom = stacked(cx, j0 + 66, 400, 435, ink)
    p.append(body)
    ky = bottom + 55
    p.append(f'<line x1="{cx}" y1="{bottom+30}" x2="{cx}" y2="{j1-16}" stroke="{line}" stroke-width="5"/>')
    for x in (cx - 36, cx + 36):
        p.append(f'<circle cx="{x}" cy="{ky}" r="17" fill="none" stroke="{OCHRE}" stroke-width="7"/>')
        p.append(f'<circle cx="{x}" cy="{ky-23}" r="5" fill="{OCHRE}"/>')
    p.append(tri_row(i0 + 16, i1 - 16, j1 - 66, 50, (RED, OCHRE), n=9))
    p.append(english(bot + 100, ink))
    p.append(divider(500, bot + 135, 150, line, RED))
    p.append(tagline(bot + 190, tag))
    return svg(1000, bot + 235, "".join(p), bg)


def save(name, s, width=2000):
    open(os.path.join(OUT, name + ".svg"), "w").write(s)
    open(os.path.join(OUT, name + ".png"), "wb").write(bytes(resvg_py.svg_to_bytes(svg_string=s, width=width)))


save("2-الإطار-المربع", square())
save("2-الإطار-المربع-لمسة-حائل", square(hail=True))
save("2-الإطار-المربع-معكوس", square(TEAL, CREAM, CREAM, hail=True, tag=OCHRE))
save("3-الباب-النجدي", door())
save("3-الباب-النجدي-لمسة-حائل", door(hail=True))
save("3-الباب-النجدي-معكوس", door(TEAL, CREAM, CREAM, hail=True, tag=OCHRE))
print("badges ok", DX, round(GAP), round(WIDTH), round(HEIGHT))
