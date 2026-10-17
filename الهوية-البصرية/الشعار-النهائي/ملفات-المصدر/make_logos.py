import os, sys
import resvg_py
sys.path.insert(0, os.path.dirname(__file__))
from brand import *

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)


def save(name, s, png_w=None):
    with open(os.path.join(OUT, name + ".svg"), "w") as f:
        f.write(s)
    png = resvg_py.svg_to_bytes(svg_string=s, width=png_w) if png_w else resvg_py.svg_to_bytes(svg_string=s)
    with open(os.path.join(OUT, name + ".png"), "wb") as f:
        f.write(bytes(png))


# 1. primary vertical logo
def primary(door, light, accent, gold, ar, en, tag, bg=None):
    b = [emblem(500, 600, 1.0, door, light, accent, gold)]
    p, _ = wordmark_ar(500, 800, 130, ar); b.append(p)
    p, _ = wordmark_en(500, 960, 54, en); b.append(p)
    p, _ = small("من أرض حاتم · حائل", "Almarai-Regular.ttf", 500, 1035, 34, tag); b.append(p)
    return svg(1000, 1100, "".join(b), bg)

save("شعار-رئيسي", primary(TEAL, OCHRE, RED, OCHRE, TEAL, TEAL, OCHRE), 2000)
save("شعار-رئيسي-خلفية-رملية", primary(TEAL, OCHRE, RED, OCHRE, TEAL, TEAL, RED, SAND), 2000)
save("شعار-رئيسي-معكوس", primary(CREAM, OCHRE, RED, OCHRE, CREAM, CREAM, OCHRE, TEAL), 2000)
save("شعار-رئيسي-لون-واحد", primary(TEAL, TEAL, TEAL, CREAM, TEAL, TEAL, TEAL), 2000)

# 2. horizontal lockup (emblem on the right, Arabic reads right-to-left)
def horizontal(bg=None, door=TEAL, txt=TEAL, tag=OCHRE):
    b = [emblem(1500, 470, 0.72, door, OCHRE, RED, OCHRE)]
    p, w = wordmark_ar(1230, 270, 130, txt, anchor="end"); b.append(p)
    p, _ = wordmark_en(1230, 390, 50, txt, anchor="end", tracking=200); b.append(p)
    p, _ = small("من أرض حاتم · حائل", "Almarai-Regular.ttf", 1230, 455, 32, tag, anchor="end"); b.append(p)
    body = "".join(b)
    rect = f'<rect x="560" width="1200" height="520" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="560 0 1200 520" width="1200" height="520">'
            f"{rect}{body}</svg>")

save("شعار-أفقي", horizontal(), 2400)
save("شعار-أفقي-معكوس", horizontal(TEAL, CREAM, CREAM), 2400)

# 3. icon / avatar
def icon(bg, door, light):
    b = [f'<rect width="1000" height="1000" rx="0" fill="{bg}"/>',
         emblem(500, 760, 1.25, door, light, RED, OCHRE)]
    return svg(1000, 1000, "".join(b))

save("أيقونة-الحساب", icon(TEAL, CREAM, OCHRE), 1080)
save("أيقونة-الحساب-رملية", icon(SAND, TEAL, OCHRE), 1080)

# 4. emblem only, transparent
save("الرمز", svg(1000, 600, emblem(500, 590, 1.0)), 1600)
print("done")
