"""Tiny vector 3D renderer for the packaging pages: orthographic camera,
lit flat faces, metal/glass sheen, and SVG artwork mapped onto faces
(labels wrap around cylinders strip by strip). World units are millimetres.
"""
import math, re

_ID = [0]


def _uid(p):
    _ID[0] += 1
    return f"{p}{_ID[0]}"


def _hex(c):
    c = c.lstrip("#")
    return [int(c[i:i + 2], 16) for i in (0, 2, 4)]


def shade(color, k, spec=0.0):
    """k < 1 darkens toward a cool shadow, spec > 0 lifts toward white."""
    r, g, b = _hex(color)
    r, g, b = r * k, g * k, b * k
    r, g, b = r + (255 - r) * spec, g + (255 - g) * spec, b + (255 - b) * spec
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(v))) for v in (r, g, b))


def _norm(v):
    l = math.sqrt(sum(a * a for a in v)) or 1
    return tuple(a / l for a in v)


class Scene:
    def __init__(self, az=-32, el=24, scale=3.0, ox=0, oy=0, light=(-0.55, -0.75, 0.95)):
        a, e = math.radians(az), math.radians(el)
        self.ca, self.sa, self.ce, self.se = math.cos(a), math.sin(a), math.cos(e), math.sin(e)
        self.s, self.ox, self.oy = scale, ox, oy
        self.L = _norm(light)
        self.V = _norm(self.unrot((0, -self.ce, self.se)))
        self.H = _norm(tuple(l + v for l, v in zip(self.L, self.V)))
        self.defs, self.objects, self.tex = [], [], {}
        self.right = (self.ca, -self.sa)
        self.far = (self.sa, self.ca)

    def unrot(self, v):  # view-space direction back to world
        X, Y, z = v
        return (X * self.ca + Y * self.sa, -X * self.sa + Y * self.ca, z)

    def rot(self, v):
        x, y, z = v
        return (x * self.ca - y * self.sa, x * self.sa + y * self.ca, z)

    def P(self, p):
        X, Y, z = self.rot(p)
        return (self.ox + X * self.s, self.oy - (z * self.ce + Y * self.se) * self.s)

    def depth(self, p):
        X, Y, z = self.rot(p)
        return Y * self.ce - z * self.se

    def visible(self, n):
        return sum(a * b for a, b in zip(n, self.V)) > 1e-6

    def light(self, n, mat):
        d = max(0.0, sum(a * b for a, b in zip(n, self.L)))
        if mat == "metal":
            sp = max(0.0, sum(a * b for a, b in zip(n, self.H))) ** 18
            return 0.45 + 0.5 * d, 0.85 * sp
        if mat == "glass":
            sp = max(0.0, sum(a * b for a, b in zip(n, self.H))) ** 40
            return 0.6 + 0.4 * d, 0.9 * sp
        return 0.62 + 0.38 * d, 0.0

    # ---- artwork
    def texture(self, svg_str, key=None):
        key = key or id(svg_str)
        if key in self.tex:
            return self.tex[key]
        m = re.match(r'<svg[^>]*viewBox="([^"]+)"[^>]*>', svg_str)
        vx, vy, vw, vh = [float(v) for v in m.group(1).split()]
        inner = svg_str[m.end():svg_str.rfind("</svg>")]
        tid = _uid("tx")
        self.defs.append(f'<g id="{tid}">{inner}</g>')
        self.tex[key] = (tid, vx, vy, vw, vh)
        return self.tex[key]

    def _mapped(self, tex, P00, P10, P01, clip_pts, u0=None, uw=None, v0=None, vh=None):
        tid, vx, vy, vw, vh_ = tex
        u0 = vx if u0 is None else u0
        uw = vw if uw is None else uw
        v0 = vy if v0 is None else v0
        vh = vh_ if vh is None else vh
        a, b = (P10[0] - P00[0]) / uw, (P10[1] - P00[1]) / uw
        c, d = (P01[0] - P00[0]) / vh, (P01[1] - P00[1]) / vh
        e, f = P00[0] - a * u0 - c * v0, P00[1] - b * u0 - d * v0
        cid = _uid("cp")
        pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in clip_pts)
        return (f'<clipPath id="{cid}"><polygon points="{pts}"/></clipPath>'
                f'<g clip-path="url(#{cid})"><use href="#{tid}" xlink:href="#{tid}" '
                f'transform="matrix({a:.5f},{b:.5f},{c:.5f},{d:.5f},{e:.3f},{f:.3f})"/></g>')

    # ---- primitives (each returns svg for one convex part, drawn back-to-front within the object)
    def poly_face(self, pts3, n, color, mat="matte", opacity=1.0, stroke=None):
        if not self.visible(n):
            return ""
        k, sp = self.light(n, mat)
        pts = " ".join("%.2f,%.2f" % self.P(p) for p in pts3)
        st = f' stroke="{stroke}" stroke-width="0.6"' if stroke else f' stroke="{shade(color, k, sp)}" stroke-width="0.4"'
        op = f' fill-opacity="{opacity}"' if opacity < 1 else ""
        return f'<polygon points="{pts}" fill="{shade(color, k, sp)}"{op}{st}/>'

    def overlay(self, pts3, n, mat="matte", strength=0.85):
        """Darken artwork to match the face's lighting."""
        k, sp = self.light(n, mat)
        pts = " ".join("%.2f,%.2f" % self.P(p) for p in pts3)
        out = ""
        if k < 1:
            out += f'<polygon points="{pts}" fill="#0b1a1c" fill-opacity="{(1 - k) * strength:.3f}"/>'
        if sp > 0.02:
            out += f'<polygon points="{pts}" fill="#ffffff" fill-opacity="{sp * 0.6:.3f}"/>'
        return out

    def _grad(self, stops, x0, x1, kind="fill"):
        gid = _uid("gr")
        span = (x1 - x0) or 1
        st = "".join(
            f'<stop offset="{max(0, min(1, (x - x0) / span)):.4f}" stop-color="{c}" stop-opacity="{o:.3f}"/>'
            for x, c, o in stops)
        self.defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x0:.2f}" y1="0" x2="{x1:.2f}" y2="0">{st}</linearGradient>')
        return gid

    def prism(self, cx, cy, z0, r, h, n=72, color="#0D4A52", top=None, mat="matte", rot=0.0,
              side_tex=None, top_tex=None, opacity=1.0, r_top=None):
        """Upright n-sided prism / cylinder (frustum if r_top).
        side_tex=(tex, wrap_mm, z_top, z_bot, centre_deg). n >= 24 renders as a smooth surface."""
        rt = r if r_top is None else r_top
        top = top or color
        out = []
        front = math.degrees(math.atan2(-self.far[1], -self.far[0]))
        smooth = n >= 24
        slope = (r - rt) / h if h else 0

        def pt(rad, a, z):
            return (cx + rad * math.cos(a), cy + rad * math.sin(a), z)

        facets = []
        for i in range(n):
            a0 = math.radians(rot + 360 * i / n)
            a1 = math.radians(rot + 360 * (i + 1) / n)
            am = (a0 + a1) / 2
            nrm = _norm((math.cos(am), math.sin(am), slope))
            facets.append((i, a0, a1, nrm, self.visible(nrm)))
        # rotate the list so the visible run is contiguous
        k0 = next((i for i in range(n) if facets[i][4] and not facets[i - 1][4]), 0)
        run = [f for f in facets[k0:] + facets[:k0] if f[4]]

        if smooth and run:
            bottoms = [self.P(pt(r, f[1], z0)) for f in run] + [self.P(pt(r, run[-1][2], z0))]
            tops = [self.P(pt(rt, f[1], z0 + h)) for f in run] + [self.P(pt(rt, run[-1][2], z0 + h))]
            sil = bottoms + tops[::-1]
            xs = [p[0] for p in sil]
            stops = []
            for f in run:
                k, sp = self.light(f[3], mat)
                xm = self.P(pt(r, (f[1] + f[2]) / 2, z0))[0]
                stops.append((xm, shade(color, k, sp), opacity))
            gid = self._grad(sorted(stops), min(xs), max(xs))
            ptxt = " ".join(f"{x:.2f},{y:.2f}" for x, y in sil)
            out.append(f'<polygon points="{ptxt}" fill="url(#{gid})"/>')
        elif not smooth:
            for (i, a0, a1, nrm, vis) in run:
                q = [pt(r, a0, z0), pt(r, a1, z0), pt(rt, a1, z0 + h), pt(rt, a0, z0 + h)]
                out.append(self.poly_face(q, nrm, color, mat, opacity))

        if side_tex and run:
            tex, wrap, zt, zb, cdeg = side_tex
            cdeg = front if cdeg is None else cdeg

            def arc(a):
                d = (math.degrees(a) - cdeg + 540) % 360 - 180
                return math.radians(d) * r
            tid, vx, vy, vw, vh = tex
            u = lambda sv: vx + (sv + wrap / 2) / wrap * vw
            band_b, band_t, dark, light = [], [], [], []
            for (i, a0, a1, nrm, vis) in run:
                s0, s1 = arc(a0), arc(a1)
                if s1 < s0 or s1 < -wrap / 2 or s0 > wrap / 2:
                    continue
                P00, P10 = self.P(pt(r, a0, zt)), self.P(pt(r, a1, zt))
                P01, P11 = self.P(pt(r, a0, zb)), self.P(pt(r, a1, zb))
                if smooth:  # overlap neighbouring slices slightly so no hairlines show
                    d = (a1 - a0) * 0.35
                    clip = [self.P(pt(r, a0 - d, zt)), self.P(pt(r, a1 + d, zt)), self.P(pt(r, a1 + d, zb)), self.P(pt(r, a0 - d, zb))]
                else:
                    clip = [P00, P10, P11, P01]
                out.append(self._mapped(tex, P00, P10, P01, clip, u0=u(s0), uw=u(s1) - u(s0)))
                lo, hi = max(s0, -wrap / 2), min(s1, wrap / 2)
                if not band_b:
                    band_b.append(self.P(pt(r, a0 + (lo - s0) / r, zb)))
                    band_t.append(self.P(pt(r, a0 + (lo - s0) / r, zt)))
                band_b.append(self.P(pt(r, a0 + (hi - s0) / r, zb)))
                band_t.append(self.P(pt(r, a0 + (hi - s0) / r, zt)))
                k, sp = self.light(nrm, mat if mat != "metal" else "matte")
                xm = (P00[0] + P10[0]) / 2
                dark.append((xm, "#0b1a1c", (1 - k) * 0.7))
                light.append((xm, "#ffffff", sp * 0.5))
            if band_b:
                poly_pts = band_b + band_t[::-1]
                xs = [p[0] for p in poly_pts]
                ptxt = " ".join(f"{x:.2f},{y:.2f}" for x, y in poly_pts)
                if smooth:
                    g1 = self._grad(sorted(dark), min(xs), max(xs))
                    out.append(f'<polygon points="{ptxt}" fill="url(#{g1})"/>')
                    if any(o > 0.02 for _, _, o in light):
                        g2 = self._grad(sorted(light), min(xs), max(xs))
                        out.append(f'<polygon points="{ptxt}" fill="url(#{g2})"/>')
                else:
                    for (i, a0, a1, nrm, vis) in run:
                        s0, s1 = arc(a0), arc(a1)
                        if s1 < s0 or s1 < -wrap / 2 or s0 > wrap / 2:
                            continue
                        bandq = [pt(r, a0, zb), pt(r, a1, zb), pt(r, a1, zt), pt(r, a0, zt)]
                        out.append(self.overlay(bandq, nrm, "matte", 0.55))

        topn = (0, 0, 1)
        ring = [pt(rt, math.radians(rot + 360 * i / n), z0 + h) for i in range(n)]
        out.append(self.poly_face(ring, topn, top, mat, opacity))
        if top_tex:
            tex, rr = top_tex
            c = (cx, cy, z0 + h)
            R, F = self.right, self.far
            P00 = self.P((c[0] - rr * R[0] + rr * F[0], c[1] - rr * R[1] + rr * F[1], c[2]))
            P10 = self.P((c[0] + rr * R[0] + rr * F[0], c[1] + rr * R[1] + rr * F[1], c[2]))
            P01 = self.P((c[0] - rr * R[0] - rr * F[0], c[1] - rr * R[1] - rr * F[1], c[2]))
            clip = [self.P(p) for p in ring]
            out.append(self._mapped(tex, P00, P10, P01, clip))
            out.append(self.overlay(ring, topn, "matte", 0.6))
        return "".join(out)

    def box(self, x0, y0, z0, dx, dy, dz, color, top=None, mat="matte", tex=None):
        """Axis-aligned box. tex: {'top'|'front'|'right'|'left'|'back': svg_texture_tuple}."""
        tex = tex or {}
        x1, y1, z1 = x0 + dx, y0 + dy, z0 + dz
        faces = {
            "front": ([(x0, y0, z1), (x1, y0, z1), (x1, y0, z0), (x0, y0, z0)], (0, -1, 0)),
            "back": ([(x1, y1, z1), (x0, y1, z1), (x0, y1, z0), (x1, y1, z0)], (0, 1, 0)),
            "left": ([(x0, y1, z1), (x0, y0, z1), (x0, y0, z0), (x0, y1, z0)], (-1, 0, 0)),
            "right": ([(x1, y0, z1), (x1, y1, z1), (x1, y1, z0), (x1, y0, z0)], (1, 0, 0)),
            "top": ([(x0, y1, z1), (x1, y1, z1), (x1, y0, z1), (x0, y0, z1)], (0, 0, 1)),
        }
        out = []
        for name in ("back", "left", "right", "front", "top"):
            pts, n = faces[name]
            if not self.visible(n):
                continue
            col = top if (name == "top" and top) else color
            out.append(self.poly_face(pts, n, col, mat))
            if name in tex:
                P = [self.P(p) for p in pts]  # corners: TL, TR, BR, BL as seen from outside
                out.append(self._mapped(tex[name], P[0], P[1], P[3], P))
                out.append(self.overlay(pts, n, "matte", 0.75))
        return "".join(out)

    def shadow(self, cx, cy, rx, ry=None, z=0, op=0.28):
        ry = ry or rx
        gid = _uid("sh")
        self.defs.append(f'<radialGradient id="{gid}"><stop offset="0" stop-color="#2b1d10" stop-opacity="{op}"/>'
                         f'<stop offset="1" stop-color="#2b1d10" stop-opacity="0"/></radialGradient>')
        pts = []
        for i in range(48):
            a = 2 * math.pi * i / 48
            pts.append(self.P((cx + rx * math.cos(a), cy + ry * math.sin(a), z)))
        ptxt = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        return f'<polygon points="{ptxt}" fill="url(#{gid})"/>'

    def add(self, anchor, svg):
        self.objects.append((self.depth(anchor), svg))

    def render(self):
        body = "".join(s for _, s in sorted(self.objects, key=lambda o: -o[0]))
        return f'<defs>{"".join(self.defs)}</defs>{body}'
