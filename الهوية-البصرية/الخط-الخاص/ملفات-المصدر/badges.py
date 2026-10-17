"""Logo badges 2 (square Kufic frame) and 3 (Najdi door), drawn with Raihat Kufi."""
import os, sys
import resvg_py
sys.path.insert(0, os.path.dirname(__file__))
from brand import TEAL, TEAL_DARK, RED, OCHRE, SAND, CREAM, text_path, svg
import wordmark as W  # loads the custom font (argv[1])

OUT = sys.argv[3]
os.makedirs(OUT, exist_ok=True)
U = W.UPEM


def units(text):
    _, total, _ = W.draw(W.shape(text), U, 0, 0, "start")
    return total


def stacked(cx, top, width, height, ink):
    """رائحة over أمي, both centred, fitted inside width x height."""
    u1 = units("رائحة")
    size = min(width * U / u1, height / 2.65)
    y1 = top + size * 1.0
    y2 = y1 + size * 1.42
    b1, _, _ = W.draw(W.shape("رائحة"), size, cx, y1, "middle", default=ink)
    b2, _, _ = W.draw(W.shape("أمي"), size, cx, y2, "middle", default=ink)
    return b1 + b2


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


def diamond(cx, cy, r, col):
    return poly([(cx, cy - r), (cx + r * .78, cy), (cx, cy + r), (cx - r * .78, cy)], col)


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


# ---------- 2. square Kufic frame ----------
def square(bg=SAND, frame=TEAL, ink=TEAL, line=OCHRE, hail=False, tag=RED):
    p = []
    x0, y0, s, sw = 170, 70, 660, 30
    x1, y1 = x0 + s, y0 + s
    p.append(f'<rect x="{x0}" y="{y0}" width="{s}" height="{s}" fill="none" stroke="{frame}" stroke-width="{sw}"/>')
    i0, j0, i1, j1 = x0 + 34, y0 + 34, x1 - 34, y1 - 34
    p.append(f'<rect x="{i0}" y="{j0}" width="{i1-i0}" height="{j1-j0}" fill="none" stroke="{line}" stroke-width="5"/>')
    p.append(tri_row(i0 + 18, i1 - 18, j0 + 18, 34, (OCHRE, RED), down=True, n=11))
    if hail:
        p.append(ridge(i0 + 3, i1 - 3, j1 - 3, 120, RED))
        p.append(stacked((x0 + x1) / 2, j0 + 90, 420, 330, ink))
    else:
        p.append(tri_row(i0 + 18, i1 - 18, j1 - 52, 34, (OCHRE, RED), n=11))
        p.append(stacked((x0 + x1) / 2, j0 + 95, 430, 380, ink))
    for cx in (x0, x1):
        p.append(diamond(cx, (y0 + y1) / 2, 30, OCHRE))
    p.append(english(y1 + 105, ink))
    p.append(tagline(y1 + 165, tag))
    return svg(1000, y1 + 215, "".join(p), bg)


# ---------- 3. Najdi door ----------
def door(bg=SAND, frame=TEAL, ink=TEAL, line=OCHRE, hail=False, tag=RED):
    p = []
    L, R, top, bot, sw = 285, 715, 175, 905, 30
    cx = (L + R) / 2
    if hail:  # Aja and Salma rising behind the gate
        p.append(ridge(40, cx + 60, bot - 120, 300, RED))
        p.append(ridge(cx - 60, 960, bot - 120, 250, RED))
        p.append(f'<rect x="{L-sw/2}" y="{top}" width="{R-L+sw}" height="{bot-top}" fill="{bg}"/>')
    n, w = 5, (R - L + sw) / 5
    for k in range(n):
        a = L - sw / 2 + k * w
        col = (OCHRE if k % 2 == 0 else RED) if hail else frame
        p.append(poly([(a + 6, top - 4), (a + w - 6, top - 4), (a + w / 2, top - 70)], col))
    p.append(f'<rect x="{L}" y="{top+sw/2}" width="{R-L}" height="{bot-top-sw}" fill="none" stroke="{frame}" stroke-width="{sw}"/>')
    i0, j0, i1, j1 = L + 32, top + 47, R - 32, bot - 47
    p.append(f'<rect x="{i0}" y="{j0}" width="{i1-i0}" height="{j1-j0}" fill="none" stroke="{line}" stroke-width="5"/>')
    p.append(tri_row(i0 + 16, i1 - 16, j0 + 16, 32, (OCHRE, RED), down=True, n=7))
    p.append(stacked(cx, j0 + 95, 300, 330, ink))
    for x in (cx - 34, cx + 34):
        p.append(f'<circle cx="{x}" cy="{j1-170}" r="15" fill="none" stroke="{OCHRE}" stroke-width="7"/>')
    p.append(f'<line x1="{cx}" y1="{j1-215}" x2="{cx}" y2="{j1-16}" stroke="{line}" stroke-width="5"/>')
    p.append(tri_row(i0 + 16, i1 - 16, j1 - 66, 50, (RED, OCHRE), n=7))
    p.append(english(bot + 100, ink))
    p.append(tagline(bot + 160, tag))
    return svg(1000, bot + 210, "".join(p), bg)


def save(name, s, width=2000):
    open(os.path.join(OUT, name + ".svg"), "w").write(s)
    open(os.path.join(OUT, name + ".png"), "wb").write(bytes(resvg_py.svg_to_bytes(svg_string=s, width=width)))


save("2-الإطار-المربع", square())
save("2-الإطار-المربع-لمسة-حائل", square(hail=True))
save("2-الإطار-المربع-معكوس", square(TEAL, CREAM, CREAM, hail=True, tag=OCHRE))
save("3-الباب-النجدي", door())
save("3-الباب-النجدي-لمسة-حائل", door(hail=True))
save("3-الباب-النجدي-معكوس", door(TEAL, CREAM, CREAM, hail=True, tag=OCHRE))
print("badges ok")
