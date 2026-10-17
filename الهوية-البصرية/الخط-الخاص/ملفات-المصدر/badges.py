"""Logo badges 2 (square Kufic frame) and 3 (arched door frame), drawn with Raihat Kufi."""
import os, sys
import resvg_py
sys.path.insert(0, os.path.dirname(__file__))
from brand import TEAL, TEAL_DARK, RED, OCHRE, SAND, CREAM, text_path, svg
import wordmark as W  # loads the custom font (argv[1])

OUT = sys.argv[3]
os.makedirs(OUT, exist_ok=True)
S = W.UPEM


def word(text, x, y, height_px, anchor, colors=None, ink=TEAL, swap=None):
    """Draw a word scaled so its glyph box (baseline to cap) is ~height_px."""
    glyphs = W.shape(text)
    size = height_px / 0.78
    body, total, x0 = W.draw(glyphs, size, x, y, anchor, colors=colors, default=ink, swap=swap)
    return body, total, x0, size


def tri(x, y, w, h, col, down=False):
    if down:
        return f'<polygon points="{x},{y} {x+w},{y} {x+w/2},{y+h}" fill="{col}"/>'
    return f'<polygon points="{x},{y+h} {x+w},{y+h} {x+w/2},{y}" fill="{col}"/>'


def diamond(cx, cy, r, col):
    return f'<polygon points="{cx},{cy-r} {cx+r*.8},{cy} {cx},{cy+r} {cx-r*.8},{cy}" fill="{col}"/>'


def english(y, col, size=58, w=1000):
    d, _ = text_path("RAIHAT UMMI", "Jost.ttf", size, w / 2, y, "middle", wght=600, tracking=200)
    return f'<path d="{d}" fill="{col}"/>'


def tagline(y, col, w=1000):
    d, _ = text_path("من أرض حاتم · حائل", "Almarai-Regular.ttf", 34, w / 2, y, "middle")
    return f'<path d="{d}" fill="{col}"/>'


DOOR = {"uni0623": "uni0623.door"}


def units(text, swap=None):
    _, total, _ = W.draw(W.shape(text), S, 0, 0, "start", swap=swap)
    return total  # width in font units at size == UPEM


def stacked(cx, top, width, height, ink, door_col):
    """رائحة on top, أمي below, right-aligned, fitted inside width x height."""
    u1, u2 = units("رائحة"), units("أمي", DOOR)
    size = min(width * S / max(u1, u2), height / 2.55)
    right = cx + max(u1, u2) * size / S / 2
    y1 = top + size * 0.95
    y2 = y1 + size * 1.3
    b1, _, _ = W.draw(W.shape("رائحة"), size, right, y1, "end", default=ink)
    b2, _, _ = W.draw(W.shape("أمي"), size, right, y2, "end", default=ink,
                      colors={"uni0623.door": door_col}, swap=DOOR)
    return b1 + b2


# ---------- 2. square Kufic frame ----------
def square(bg=SAND, frame=TEAL, ink=TEAL, hail=False, tag=None):
    p = []
    x0, y0, s = 180, 90, 640
    p.append(f'<rect x="{x0}" y="{y0}" width="{s}" height="{s}" fill="none" stroke="{frame}" stroke-width="34"/>')
    i0, i1 = x0 + 40, x0 + s - 40
    # corner triangles
    t = 62
    p += [f'<polygon points="{i0},{y0+40} {i0+t},{y0+40} {i0},{y0+40+t}" fill="{RED}"/>',
          f'<polygon points="{i1},{y0+40} {i1-t},{y0+40} {i1},{y0+40+t}" fill="{RED}"/>']
    if not hail:
        p += [f'<polygon points="{i0},{y0+s-40} {i0+t},{y0+s-40} {i0},{y0+s-40-t}" fill="{RED}"/>',
              f'<polygon points="{i1},{y0+s-40} {i1-t},{y0+s-40} {i1},{y0+s-40-t}" fill="{RED}"/>']
    # top row of three triangles
    for k, c in enumerate((OCHRE, RED, OCHRE)):
        p.append(tri(x0 + s / 2 - 105 + k * 70, y0 + 45, 70, 58, c))
    p.append(stacked(x0 + s / 2, y0 + 140, 440, 360 if hail else 430, ink, OCHRE))
    if hail:  # Aja & Salma ridge along the bottom inside the frame
        ridge = [(i0, y0 + s - 40), (i0, y0 + s - 75), (i0 + 90, y0 + s - 105), (i0 + 150, y0 + s - 88),
                 (i0 + 240, y0 + s - 135), (i0 + 330, y0 + s - 92), (i0 + 400, y0 + s - 115),
                 (i1, y0 + s - 70), (i1, y0 + s - 40)]
        p.insert(1, '<polygon points="' + " ".join(f"{a},{b}" for a, b in ridge) + f'" fill="{RED}"/>')
    p.append(english(y0 + s + 120, ink))
    if tag:
        p.append(tagline(y0 + s + 185, tag))
    return svg(1000, y0 + s + (225 if tag else 170), "".join(p), bg)


# ---------- 3. arched door frame ----------
def arch(bg=SAND, frame=TEAL, ink=TEAL, hail=False, tag=None):
    p = []
    L, R, top, bot = 290, 710, 120, 900
    cx = (L + R) / 2

    def arch_path(l, r, t, b):
        w = r - l
        return (f"M{l},{b} L{l},{t+190} C{l},{t+150} {l+w*.12},{t+140} {l+w*.18},{t+120} "
                f"C{l+w*.26},{t+70} {cx-30},{t+40} {cx},{t} C{cx+30},{t+40} {r-w*.26},{t+70} {r-w*.18},{t+120} "
                f"C{r-w*.12},{t+140} {r},{t+150} {r},{t+190} L{r},{b} Z")
    p.append(f'<path d="{arch_path(L, R, top, bot)}" fill="none" stroke="{frame}" stroke-width="34" stroke-linejoin="round"/>')
    p.append(f'<path d="{arch_path(L+40, R-40, top+50, bot-40)}" fill="none" stroke="{OCHRE}" stroke-width="12" stroke-linejoin="round"/>')
    if hail:  # fort crenellations on top of the arch
        for k in range(-2, 3):
            p.append(tri(cx + k * 64 - 30, top - 92 + abs(k) * 22, 60, 58, OCHRE if k % 2 == 0 else RED))
    p.append(stacked(cx, top + 215, 310, 520, ink, OCHRE))
    # threshold triangles
    n, x_a, x_b, y = 7, L + 52, R - 52, bot - 128
    w = (x_b - x_a) / n
    cols = [RED, OCHRE, RED, frame, RED, OCHRE, RED]
    for k in range(n):
        p.append(tri(x_a + k * w, y, w, 70, cols[k], down=(k == 3)))
        p.append(english(bot + 105, ink))
    if tag:
        p.append(tagline(bot + 170, tag))
    return svg(1000, bot + (210 if tag else 150), "".join(p), bg)


def save(name, s, width=2000):
    open(os.path.join(OUT, name + ".svg"), "w").write(s)
    open(os.path.join(OUT, name + ".png"), "wb").write(bytes(resvg_py.svg_to_bytes(svg_string=s, width=width)))


save("2-الإطار-المربع", square(tag=RED))
save("2-الإطار-المربع-لمسة-حائل", square(hail=True, tag=RED))
save("2-الإطار-المربع-معكوس", square(TEAL, CREAM, CREAM, hail=True, tag=OCHRE))
save("3-إطار-الباب", arch(tag=RED))
save("3-إطار-الباب-لمسة-حائل", arch(hail=True, tag=RED))
save("3-إطار-الباب-معكوس", arch(TEAL, CREAM, CREAM, hail=True, tag=OCHRE))
print("badges ok")
