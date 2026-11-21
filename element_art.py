"""Element styles: one look per element, used by the card frame overlay and by the
Focus / Resolve effects.

A card's "type" is the element of its Ultimate (move 3).  Each style has

  * a palette: dark, mid, light (metal/ink colours) and glow (light colour);
  * a motif: the glyph drawn in the frame's corners and as particles
    (flames for Fire, snowflakes for Ice, leaves for Nature...).

``overlay(element, w, h, pad)`` draws the decorative layer that sits over a
w x h art panel framed by battle_panels.panel_frame (same padding), so it lines
up with the stars, level badge and crest without covering them.
"""
import math
import random
import threading
from collections import OrderedDict

from PIL import Image, ImageChops, ImageDraw, ImageFilter

# name, emoji, dark, mid, light, glow, motif
STYLES = {
    "PHYSICAL": ("Physical", "👊", (90, 44, 16), (214, 120, 52), (255, 196, 140), (255, 150, 70), "shard"),
    "SWORD":    ("Sword", "⚔️", (44, 52, 66), (150, 168, 190), (236, 244, 255), (170, 210, 255), "blade"),
    "RANGED":   ("Ranged", "🏹", (40, 60, 26), (120, 160, 70), (220, 236, 170), (170, 230, 110), "arrow"),
    "GUN":      ("Gun", "🔫", (40, 40, 44), (176, 140, 70), (240, 214, 150), (255, 200, 110), "bullet"),
    "RECKLESS": ("Reckless", "♻️", (60, 10, 10), (220, 50, 40), (255, 210, 60), (255, 80, 40), "zigzag"),
    "FIRE":     ("Fire", "🔥", (110, 20, 6), (240, 96, 20), (255, 214, 90), (255, 120, 30), "flame"),
    "WATER":    ("Water", "💧", (8, 50, 110), (40, 140, 230), (180, 230, 255), (80, 180, 255), "drop"),
    "EARTH":    ("Earth", "⛰️", (70, 46, 24), (160, 112, 62), (230, 200, 150), (220, 170, 90), "rock"),
    "ELECTRIC": ("Electric", "🌩️", (60, 30, 110), (250, 210, 40), (255, 250, 190), (255, 230, 80), "bolt"),
    "WIND":     ("Wind", "🌪️", (30, 90, 80), (120, 220, 190), (230, 255, 245), (160, 255, 220), "swirl"),
    "NATURE":   ("Nature", "🌿", (20, 70, 24), (70, 170, 60), (190, 240, 140), (120, 230, 90), "leaf"),
    "ICE":      ("Ice", "❄️", (30, 70, 120), (140, 210, 250), (240, 252, 255), (180, 236, 255), "snow"),
    "BLEED":    ("Bleed", "🅱️", (70, 0, 10), (190, 20, 40), (255, 120, 120), (255, 40, 60), "drip"),
    "ENERGY":   ("Energy", "🧿", (20, 30, 90), (60, 200, 255), (250, 150, 255), (120, 220, 255), "orb"),
    "PSYCHIC":  ("Psychic", "🔮", (60, 20, 90), (190, 90, 230), (255, 190, 250), (220, 120, 255), "eye"),
    "SLEEP":    ("Sleep", "💤", (24, 26, 70), (130, 130, 220), (220, 220, 255), (170, 170, 255), "moon"),
    "DEATH":    ("Death", "☠️", (16, 16, 18), (110, 110, 116), (232, 228, 214), (190, 255, 210), "thorn"),
    "LIFE":     ("Life", "❤️‍🔥", (110, 20, 60), (240, 90, 140), (255, 220, 160), (255, 140, 170), "heart"),
    "LIGHT":    ("Light", "🌕", (150, 110, 30), (250, 220, 120), (255, 255, 240), (255, 240, 170), "sun"),
    "DARK":     ("Dark", "🌑", (14, 8, 24), (80, 40, 120), (190, 140, 240), (140, 70, 220), "smoke"),
    "POISON":   ("Poison", "🧪", (40, 16, 60), (120, 210, 50), (220, 255, 160), (150, 255, 60), "bubble"),
    "ROT":      ("Rot", "🩻", (40, 40, 24), (130, 130, 80), (210, 210, 170), (180, 200, 120), "spore"),
    "TIME":     ("Time", "⌛", (70, 50, 20), (196, 160, 90), (250, 236, 190), (240, 210, 130), "gear"),
    "GRAVITY":  ("Gravity", "🪐", (20, 16, 60), (90, 80, 200), (200, 190, 255), (130, 110, 255), "orbit"),
    "DRACONIC": ("Draconic", "🐲", (10, 60, 46), (40, 170, 120), (250, 214, 110), (90, 230, 170), "scale"),
}
ALIASES = {"RECOIL": "RECKLESS", "SPIRIT": "ENERGY", "SPIRIT ENERGY": "ENERGY"}
DEFAULT = ("Unbound", "✨", (110, 74, 20), (196, 140, 40), (255, 214, 120), (255, 214, 120), "star")


def style(element):
    key = str(element or "").upper().strip()
    key = ALIASES.get(key, key)
    return STYLES.get(key, DEFAULT)


def element_of(card):
    """The card's type: the element of its Ultimate."""
    return str(getattr(card, "move3_element", "") or "").upper() or None


# --------------------------------------------------------------------------- glyphs
def _rot(points, cx, cy, angle):
    c, s = math.cos(angle), math.sin(angle)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in points]


def glyph(d, motif, x, y, size, angle, pal, alpha=255):
    """Draw one motif glyph centred at (x, y)."""
    dark, mid, light, glow = pal
    A = lambda col: tuple(col) + (alpha,)
    s = size
    if motif == "flame":
        pts = [(0, -s), (s * 0.45, -s * 0.2), (s * 0.5, s * 0.35), (0, s * 0.7), (-s * 0.5, s * 0.35), (-s * 0.35, -s * 0.15), (-s * 0.05, s * 0.05)]
        d.polygon(_rot(pts, x, y, angle), fill=A(mid), outline=A(dark))
        inner = [(0, -s * 0.35), (s * 0.22, s * 0.15), (0, s * 0.5), (-s * 0.22, s * 0.15)]
        d.polygon(_rot(inner, x, y, angle), fill=A(light))
    elif motif in ("drop", "drip"):
        pts = [(0, -s)] + [(math.cos(t) * s * 0.55, s * 0.25 + math.sin(t) * s * 0.55) for t in [i * math.pi / 10 for i in range(-1, 12)]]
        d.polygon(_rot(pts, x, y, angle), fill=A(mid), outline=A(dark))
        d.ellipse((x - s * 0.18, y + s * 0.05, x + s * 0.02, y + s * 0.3), fill=A(light))
    elif motif == "leaf":
        pts = [(0, -s)] + [(math.sin(t) * s * 0.45, -math.cos(t) * s) for t in [i * math.pi / 8 for i in range(1, 8)]] + [(0, s)] + \
              [(-math.sin(t) * s * 0.45, math.cos(t) * s) for t in [i * math.pi / 8 for i in range(1, 8)]]
        d.polygon(_rot(pts, x, y, angle), fill=A(mid), outline=A(dark))
        d.line(_rot([(0, -s * 0.85), (0, s * 0.85)], x, y, angle), fill=A(light), width=max(1, int(s / 8)))
    elif motif in ("shard", "rock"):
        pts = [(0, -s), (s * 0.5, -s * 0.2), (s * 0.3, s * 0.8), (-s * 0.35, s * 0.6), (-s * 0.55, -s * 0.1)] if motif == "rock" else \
              [(0, -s), (s * 0.3, 0), (0, s * 0.5), (-s * 0.3, 0)]
        d.polygon(_rot(pts, x, y, angle), fill=A(mid), outline=A(dark))
        d.polygon(_rot([(0, -s * 0.8), (s * 0.18, -s * 0.1), (0, s * 0.1)], x, y, angle), fill=A(light))
    elif motif == "bolt":
        pts = [(s * 0.15, -s), (-s * 0.45, s * 0.1), (-s * 0.02, s * 0.1), (-s * 0.2, s), (s * 0.45, -s * 0.15), (s * 0.02, -s * 0.15)]
        d.polygon(_rot(pts, x, y, angle), fill=A(mid), outline=A(dark))
    elif motif == "snow":
        for k in range(6):
            a = angle + k * math.pi / 3
            ex, ey = x + math.cos(a) * s, y + math.sin(a) * s
            d.line([(x, y), (ex, ey)], fill=A(light), width=max(1, int(s / 6)))
            for f in (0.55,):
                bx, by = x + math.cos(a) * s * f, y + math.sin(a) * s * f
                for side in (-1, 1):
                    b = a + side * 0.7
                    d.line([(bx, by), (bx + math.cos(b) * s * 0.3, by + math.sin(b) * s * 0.3)], fill=A(light), width=max(1, int(s / 8)))
        d.ellipse((x - s * 0.15, y - s * 0.15, x + s * 0.15, y + s * 0.15), fill=A(mid))
    elif motif == "swirl":
        pts = [(x + math.cos(angle + t) * s * (t / 12), y + math.sin(angle + t) * s * (t / 12)) for t in [i * 0.25 for i in range(49)]]
        d.line(pts, fill=A(mid), width=max(2, int(s / 5)), joint="curve")
        d.line(pts[10:], fill=A(light), width=max(1, int(s / 12)), joint="curve")
    elif motif in ("orb", "bubble", "spore"):
        r = s * (0.6 if motif == "orb" else 0.5)
        d.ellipse((x - r, y - r, x + r, y + r), fill=A(mid if motif != "bubble" else glow), outline=A(dark), width=max(1, int(s / 10)))
        d.ellipse((x - r * 0.5, y - r * 0.6, x - r * 0.1, y - r * 0.2), fill=A(light))
        if motif == "orb":
            d.ellipse((x - r * 1.5, y - r * 1.5, x + r * 1.5, y + r * 1.5), outline=A(light), width=max(1, int(s / 12)))
        if motif == "spore":
            for k in range(5):
                a = angle + k * 1.256
                d.ellipse((x + math.cos(a) * r * 1.4 - r * 0.2, y + math.sin(a) * r * 1.4 - r * 0.2,
                           x + math.cos(a) * r * 1.4 + r * 0.2, y + math.sin(a) * r * 1.4 + r * 0.2), fill=A(mid))
    elif motif == "eye":
        pts = [(-s, 0), (0, -s * 0.5), (s, 0), (0, s * 0.5)]
        d.polygon(_rot(pts, x, y, angle), fill=A(light), outline=A(dark))
        d.ellipse((x - s * 0.3, y - s * 0.3, x + s * 0.3, y + s * 0.3), fill=A(mid))
        d.ellipse((x - s * 0.12, y - s * 0.12, x + s * 0.12, y + s * 0.12), fill=A(dark))
    elif motif == "moon":
        d.ellipse((x - s * 0.7, y - s * 0.7, x + s * 0.7, y + s * 0.7), fill=A(light))
        ox, oy = x + math.cos(angle) * s * 0.35, y + math.sin(angle) * s * 0.35 - s * 0.2
        d.ellipse((ox - s * 0.6, oy - s * 0.6, ox + s * 0.6, oy + s * 0.6), fill=(0, 0, 0, 0))
    elif motif == "thorn":
        pts = [(0, -s), (s * 0.22, s * 0.6), (0, s * 0.4), (-s * 0.22, s * 0.6)]
        d.polygon(_rot(pts, x, y, angle), fill=A(mid), outline=A(dark))
        d.line(_rot([(0, -s * 0.8), (0, s * 0.3)], x, y, angle), fill=A(light), width=max(1, int(s / 10)))
    elif motif == "heart":
        pts = [(0, s * 0.7)] + [(s * 0.3 + math.cos(t) * s * 0.32, -s * 0.15 + math.sin(t) * s * 0.32) for t in [math.pi * (i / 8) for i in range(-8, 2)]] + \
              [(-s * 0.3 + math.cos(t) * s * 0.32, -s * 0.15 + math.sin(t) * s * 0.32) for t in [math.pi * (i / 8) for i in range(-9, 1)][::-1]]
        d.polygon(_rot(pts, x, y, angle), fill=A(mid), outline=A(dark))
        d.ellipse((x - s * 0.42, y - s * 0.35, x - s * 0.22, y - s * 0.15), fill=A(light))
    elif motif == "sun":
        for k in range(8):
            a = angle + k * math.pi / 4
            d.polygon([(x + math.cos(a) * s, y + math.sin(a) * s), (x + math.cos(a + 0.25) * s * 0.45, y + math.sin(a + 0.25) * s * 0.45),
                       (x + math.cos(a - 0.25) * s * 0.45, y + math.sin(a - 0.25) * s * 0.45)], fill=A(mid))
        d.ellipse((x - s * 0.42, y - s * 0.42, x + s * 0.42, y + s * 0.42), fill=A(light), outline=A(mid))
    elif motif == "smoke":
        for k, (dx, dy, r) in enumerate(((0, 0, 0.55), (0.4, -0.3, 0.42), (-0.35, -0.35, 0.38), (0.1, -0.7, 0.3))):
            px, py = _rot([(dx * s, dy * s)], x, y, angle)[0]
            d.ellipse((px - r * s, py - r * s, px + r * s, py + r * s), fill=A(mid if k % 2 else dark), outline=A(light) if k == 3 else None)
    elif motif == "gear":
        teeth = 8
        pts = []
        for k in range(teeth * 2):
            a = angle + k * math.pi / teeth
            r = s if k % 2 == 0 else s * 0.75
            pts += [(x + math.cos(a - 0.15) * r, y + math.sin(a - 0.15) * r), (x + math.cos(a + 0.15) * r, y + math.sin(a + 0.15) * r)]
        d.polygon(pts, fill=A(mid), outline=A(dark))
        d.ellipse((x - s * 0.3, y - s * 0.3, x + s * 0.3, y + s * 0.3), fill=A(light), outline=A(dark))
    elif motif == "orbit":
        d.ellipse((x - s * 0.4, y - s * 0.4, x + s * 0.4, y + s * 0.4), fill=A(mid), outline=A(dark))
        ring = [(x + math.cos(t) * s, y + math.sin(t) * s * 0.35) for t in [i * math.pi / 16 for i in range(33)]]
        d.line(_rot([(px - x, py - y) for px, py in ring], x, y, angle - 0.4), fill=A(light), width=max(1, int(s / 8)))
    elif motif == "scale":
        pts = [(x + math.cos(t) * s * 0.6, y - s * 0.2 + math.sin(t) * s * 0.8) for t in [math.pi * (i / 10) for i in range(0, 11)]] + [(x, y - s)]
        d.polygon(pts, fill=A(mid), outline=A(light))
        d.line([(x - s * 0.3, y + s * 0.1), (x, y + s * 0.45), (x + s * 0.3, y + s * 0.1)], fill=A(light), width=max(1, int(s / 10)))
    elif motif == "blade":
        pts = [(0, -s), (s * 0.14, s * 0.45), (0, s * 0.55), (-s * 0.14, s * 0.45)]
        d.polygon(_rot(pts, x, y, angle), fill=A(light), outline=A(dark))
        d.line(_rot([(-s * 0.35, s * 0.5), (s * 0.35, s * 0.5)], x, y, angle), fill=A(mid), width=max(2, int(s / 7)))
    elif motif == "arrow":
        d.line(_rot([(0, s), (0, -s * 0.4)], x, y, angle), fill=A(mid), width=max(2, int(s / 8)))
        d.polygon(_rot([(0, -s), (s * 0.3, -s * 0.35), (-s * 0.3, -s * 0.35)], x, y, angle), fill=A(light), outline=A(dark))
        d.polygon(_rot([(0, s * 0.6), (s * 0.25, s), (-s * 0.25, s)], x, y, angle), fill=A(mid))
    elif motif == "bullet":
        pts = [(0, -s)] + [(math.cos(t) * s * 0.3, -s * 0.55 + math.sin(t) * s * 0.4) for t in [math.pi * (1 + i / 8) for i in range(9)]][::-1]
        body = [(-s * 0.3, -s * 0.5), (s * 0.3, -s * 0.5), (s * 0.3, s * 0.8), (-s * 0.3, s * 0.8)]
        d.polygon(_rot(body, x, y, angle), fill=A(mid), outline=A(dark))
        d.polygon(_rot([(0, -s), (s * 0.3, -s * 0.5), (-s * 0.3, -s * 0.5)], x, y, angle), fill=A(light), outline=A(dark))
    elif motif == "zigzag":
        pts = [(-s, -s * 0.2), (-s * 0.35, -s * 0.6), (-s * 0.1, -s * 0.1), (s * 0.35, -s * 0.5), (s, s * 0.2), (s * 0.35, s * 0.6), (s * 0.1, s * 0.1), (-s * 0.35, s * 0.5)]
        d.polygon(_rot(pts, x, y, angle), fill=A(mid), outline=A(light))
    else:   # star
        pts = []
        for k in range(8):
            r = s if k % 2 == 0 else s * 0.28
            a = angle + k * math.pi / 4 - math.pi / 2
            pts.append((x + math.cos(a) * r, y + math.sin(a) * r))
        d.polygon(pts, fill=A(light))


# --------------------------------------------------------------------------- overlay
_cache = OrderedDict()
_lock = threading.Lock()


def overlay(element, w, h, pad, radius=22, border=15):
    """RGBA decoration for a w x h panel framed with ``pad`` (same canvas as panel_frame). Cached."""
    key = (str(element).upper(), w, h, pad, radius, border)
    with _lock:
        hit = _cache.get(key)
        if hit is not None:
            _cache.move_to_end(key)
            return hit
    img = _draw_overlay(element, w, h, pad, radius, border)
    with _lock:
        _cache[key] = img
        while len(_cache) > 80:
            _cache.popitem(last=False)
    return img


def _draw_overlay(element, w, h, pad, radius, border):
    name, emoji, dark, mid, light, glow, motif = style(element)
    pal = (dark, mid, light, glow)
    S = 2
    k = w / 500.0                     # designed for the 500 px wide card panel
    W, H = (w + 2 * pad) * S, (h + 2 * pad) * S
    X0, Y0, X1, Y1 = pad * S, pad * S, (pad + w) * S, (pad + h) * S
    R, B = radius * S, border * S
    u = S * k                          # one design pixel

    def lay():
        return Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def window(inset=0):
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).rounded_rectangle((X0 + inset, Y0 + inset, X1 - inset, Y1 - inset), radius=max(1, R - inset), fill=255)
        return m

    out = lay()
    # depth: tinted vignette + bright rim inside the art window
    vig = Image.new("L", (W, H), 0)
    dv = ImageDraw.Draw(vig)
    dv.rounded_rectangle((X0, Y0, X1, Y1), radius=R, fill=150)
    dv.rounded_rectangle((X0 + 34 * u, Y0 + 34 * u, X1 - 34 * u, Y1 - 34 * u), radius=R, fill=0)
    vig = ImageChops.multiply(vig.filter(ImageFilter.GaussianBlur(26 * u)), window())
    tint = Image.new("RGBA", (W, H), tuple(int(c * 0.35) for c in dark) + (0,))
    tint.putalpha(vig)
    out.alpha_composite(tint)
    edge = Image.new("L", (W, H), 0)
    de = ImageDraw.Draw(edge)
    de.rounded_rectangle((X0, Y0, X1, Y1), radius=R, fill=120)
    de.rounded_rectangle((X0 + 16 * u, Y0 + 16 * u, X1 - 16 * u, Y1 - 16 * u), radius=R, fill=0)
    edge = ImageChops.multiply(edge.filter(ImageFilter.GaussianBlur(12 * u)), window())
    eg = Image.new("RGBA", (W, H), glow + (0,))
    eg.putalpha(edge)
    out.alpha_composite(eg)
    rim = lay()
    ImageDraw.Draw(rim).rounded_rectangle((X0 + 3 * u, Y0 + 3 * u, X1 - 3 * u, Y1 - 3 * u), radius=max(1, R - 3 * u),
                                          outline=light + (110,), width=max(1, int(2 * u)))
    out.alpha_composite(rim)
    # holographic sheen, tinted with the element's glow
    sheen = Image.new("L", (W, H), 0)
    ds = ImageDraw.Draw(sheen)
    for offset, width, alpha in ((-0.18, 70, 44), (0.10, 26, 32)):
        cx = W * (0.5 + offset)
        ds.polygon([(cx - width * u - H * 0.35, H), (cx + width * u - H * 0.35, H), (cx + width * u + H * 0.35, 0), (cx - width * u + H * 0.35, 0)], fill=alpha)
    sheen = ImageChops.multiply(sheen.filter(ImageFilter.GaussianBlur(14 * u)), window(int(2 * u)))
    holo = Image.new("RGBA", (W, H), tuple(min(255, (c + 255 * 2) // 3) for c in glow) + (0,))
    holo.putalpha(sheen)
    out.alpha_composite(holo)
    # glow hugging the frame
    gl = Image.new("L", (W, H), 0)
    ImageDraw.Draw(gl).rounded_rectangle((X0 - B - 4 * u, Y0 - B - 4 * u, X1 + B + 4 * u, Y1 + B + 4 * u), radius=R + B, outline=235, width=max(3, int(12 * u)))
    gl = ImageChops.subtract(gl.filter(ImageFilter.GaussianBlur(13 * u)), window(-B))
    g = Image.new("RGBA", (W, H), glow + (0,))
    g.putalpha(gl)
    out.alpha_composite(g)

    orn = lay()
    od = ImageDraw.Draw(orn)
    # top corners: a jewel and a short run of motif glyphs along each edge
    for side in (-1, 1):
        cx = X0 - B // 2 if side < 0 else X1 + B // 2
        cy = Y0 - B // 2
        sgn = 1 if side < 0 else -1
        for i, (dx, dy, sz) in enumerate(((44, -8, 24), (86, -6, 19), (122, -4, 14), (-8, 48, 24), (-6, 92, 19), (-4, 130, 14))):
            ang = (math.pi / 2 if dy > dx else 0) + (0.3 * sgn if i % 2 else 0)
            glyph(od, motif, cx + sgn * dx * u, cy + dy * u, sz * u, ang if sgn > 0 else -ang, pal)
        for rr, col in ((24, dark), (20, mid), (14, glow)):
            od.regular_polygon((cx, cy, rr * u), 4, rotation=45, fill=col + (255,))
        glyph(od, motif, cx, cy, 13 * u, 0, (dark, light, (255, 255, 255), glow))
    # side gems
    for cx in (X0 - B // 2, X1 + B // 2):
        cy = (Y0 + Y1) // 2
        for rr, col in ((17, dark), (14, mid), (9, glow), (4, light)):
            od.ellipse((cx - rr * u, cy - rr * u * 1.6, cx + rr * u, cy + rr * u * 1.6), fill=col + (255,))
        for dy in (-1, 1):
            glyph(od, motif, cx, cy + dy * 50 * u, 16 * u, 0 if dy < 0 else math.pi, pal)
            glyph(od, motif, cx, cy + dy * 88 * u, 11 * u, 0 if dy < 0 else math.pi, pal)
    # bottom plate between badge and crest
    cx, cy = W // 2, Y1 + B // 2
    wing = 118 * u
    for shrink, col in ((0, dark), (10, mid)):
        s2 = shrink * u
        od.polygon([(cx - wing + s2, cy), (cx - 26 * u, cy - (14 * u - s2 * 0.4)), (cx, cy - (22 * u - s2 * 0.5)), (cx + 26 * u, cy - (14 * u - s2 * 0.4)),
                    (cx + wing - s2, cy), (cx + 26 * u, cy + (14 * u - s2 * 0.4)), (cx, cy + (22 * u - s2 * 0.5)), (cx - 26 * u, cy + (14 * u - s2 * 0.4))], fill=col + (255,))
    od.polygon([(cx - 58 * u, cy), (cx, cy - 11 * u), (cx + 58 * u, cy), (cx, cy + 11 * u)], fill=light + (255,))
    for rr, col in ((26, dark), (22, glow)):
        od.ellipse((cx - rr * u, cy - rr * u, cx + rr * u, cy + rr * u), fill=col + (255,))
    glyph(od, motif, cx, cy, 17 * u, 0, (dark, light, (255, 255, 255), glow))

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow.putalpha(orn.getchannel("A").filter(ImageFilter.GaussianBlur(4 * u)).point(lambda v: int(v * 0.7)))
    shine = Image.new("RGBA", (W, H), glow + (0,))
    shine.putalpha(orn.getchannel("A").filter(ImageFilter.GaussianBlur(9 * u)).point(lambda v: int(v * 0.55)))
    out.alpha_composite(shine)
    out.alpha_composite(shadow, (0, int(2 * u)))
    out.alpha_composite(orn)

    # motif particles floating in the margin
    rng = random.Random(sum(ord(ch) for ch in name))
    sp = lay()
    spd = ImageDraw.Draw(sp)
    spots = [(X0 - 30 * u, Y0 + 170 * u), (X1 + 28 * u, Y0 + 230 * u), (X0 + 118 * u, Y0 - 30 * u), (X1 - 108 * u, Y0 - 32 * u),
             (X0 - 26 * u, Y1 - 150 * u), (X1 + 30 * u, Y1 - 120 * u), (W // 2 - 170 * u, Y1 + 30 * u), (W // 2 + 170 * u, Y1 + 30 * u)]
    for x, y in spots:
        glyph(spd, motif, x, y, rng.uniform(10, 15) * u, rng.uniform(-0.6, 0.6), pal, alpha=240)
    out.alpha_composite(sp.filter(ImageFilter.GaussianBlur(4 * u)))
    out.alpha_composite(sp)

    return out.resize((W // S, H // S), Image.LANCZOS)


def particles(size, count, element, seed, alpha=220, area=None):
    """A transparent layer of motif particles (for Focus / Resolve effects)."""
    name, emoji, dark, mid, light, glow, motif = style(element)
    rng = random.Random(seed)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = area or (0, 0, size[0], size[1])
    for _ in range(count):
        glyph(d, motif, rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(5, 11), rng.uniform(0, 6.28), (dark, mid, light, glow), alpha=alpha)
    return img
