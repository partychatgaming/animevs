"""Portrait frames for the battle scene, drawn in code (no image files).

A frame replaces the card template around the character circle:

  * metal ring       – material set by tier (iron … prismatic), with a sheen
  * universe accent  – thin inner ring + crest disc in the universe's colour
  * ornaments        – studs from tier 3, side blades from tier 5
  * tier stars       – arc over the top, coloured like the card's star sprites
  * level badge      – lower outer corner, level colours as on the cards

Frames depend only on (radius, tier, level, accent, flip, resolved), so they
are drawn once at 3x and cached.
"""
import colorsys
import math
import threading
from collections import OrderedDict

from PIL import Image, ImageDraw, ImageFilter

import render_cache

SS = 3                       # supersampling factor
PAD = 62                     # room outside the portrait for stars / badge / blades

# (dark, light) per tier; tier 10 is drawn as a prismatic sweep
MATERIALS = {
    1: ((70, 74, 82), (176, 182, 194)),        # iron
    2: ((96, 52, 24), (226, 150, 92)),         # bronze
    3: ((112, 120, 136), (246, 248, 255)),     # silver
    4: ((140, 96, 14), (255, 226, 120)),       # gold
    5: ((18, 52, 140), (120, 180, 255)),       # sapphire
    6: ((6, 92, 62), (110, 238, 176)),         # emerald
    7: ((120, 12, 30), (255, 110, 120)),       # ruby
    8: ((14, 6, 10), (150, 36, 48)),           # obsidian
    9: ((64, 24, 120), (214, 150, 255)),       # amethyst
    10: None,                                  # prismatic
}
NAMES = {1: "Iron", 2: "Bronze", 3: "Silver", 4: "Gold", 5: "Sapphire", 6: "Emerald",
         7: "Ruby", 8: "Obsidian", 9: "Amethyst", 10: "Prismatic"}

# star colours follow the card star sprites: gold 1-3, blue 4-6, red 7-8, purple 9, dark 10
def star_color(tier):
    if tier >= 10:
        return (245, 245, 255), (70, 50, 140)
    if tier >= 9:
        return (176, 92, 255), (60, 10, 100)
    if tier >= 7:
        return (255, 72, 72), (90, 0, 0)
    if tier >= 4:
        return (90, 170, 255), (10, 40, 100)
    return (255, 208, 60), (110, 70, 0)


def level_color(level):
    if level <= 500:
        return (255, 255, 255)
    if level <= 1000:
        return (255, 215, 0)
    if level <= 2000:
        return (255, 165, 0)
    if level <= 3000:
        return (240, 70, 70)
    return (150, 90, 255)


def _lerp(a, b, t):
    return tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


def _ring_color(tier, angle):
    """Colour of the metal at an angle (radians, 0 = right, clockwise)."""
    if tier >= 10:
        h = (angle / (2 * math.pi)) % 1.0
        r, g, b = colorsys.hsv_to_rgb(h, 0.55, 1.0)
        shade = 0.72 + 0.28 * (0.5 + 0.5 * math.cos(2 * angle - 0.9))
        return tuple(int(255 * c * shade) for c in (r, g, b))
    dark, light = MATERIALS.get(tier) or MATERIALS[1]
    # two broad highlights (top-left and bottom-right) give a polished look
    t = 0.5 + 0.5 * math.cos(2 * angle + 1.2)
    t = t ** 1.6
    return _lerp(dark, light, 0.25 + 0.75 * t)


def _star(draw, cx, cy, r, fill, outline, width):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    draw.polygon(pts, fill=fill, outline=outline)
    draw.line(pts + [pts[0]], fill=outline, width=width, joint="curve")


def _diamond(draw, cx, cy, r, fill, outline, width):
    pts = [(cx, cy - r), (cx + r * 0.7, cy), (cx, cy + r), (cx - r * 0.7, cy)]
    draw.polygon(pts, fill=fill)
    draw.line(pts + [pts[0]], fill=outline, width=width)


def draw_frame(radius, tier=1, level=1, accent=(120, 140, 200), flip=False, resolved=False, crest_text=""):
    """RGBA frame image; the portrait circle (``radius``) is transparent, centred."""
    try:
        tier = max(1, min(10, int(tier)))
    except (TypeError, ValueError):
        tier = 1
    R = radius * SS
    pad = PAD * SS
    size = 2 * (R + pad)
    c = size // 2
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    black = (0, 0, 0, 255)
    ring_in, ring_out = R + 3 * SS, R + 17 * SS

    # resolved: energy halo behind everything
    if resolved:
        halo = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        hd = ImageDraw.Draw(halo)
        hr = ring_out + 22 * SS
        hd.ellipse((c - hr, c - hr, c + hr, c + hr), fill=(255, 210, 80, 170))
        halo = halo.filter(ImageFilter.GaussianBlur(14 * SS))
        im.alpha_composite(halo)
        d = ImageDraw.Draw(im)

    # side blades (tier 5+), drawn under the ring
    if tier >= 5:
        for side in (-1, 1):
            base = _ring_color(tier, 0 if side > 0 else math.pi)
            tip = c + side * (ring_out + 34 * SS)
            pts = [(c + side * (ring_out - 6 * SS), c - 30 * SS), (tip, c), (c + side * (ring_out - 6 * SS), c + 30 * SS)]
            d.polygon(pts, fill=base + (255,))
            d.line(pts + [pts[0]], fill=black, width=3 * SS)
            inner = [(c + side * (ring_out - 2 * SS), c - 14 * SS), (tip - side * 14 * SS, c), (c + side * (ring_out - 2 * SS), c + 14 * SS)]
            d.polygon(inner, fill=_lerp(base, (255, 255, 255), 0.35) + (255,))

    # metal ring: thin wedges, each with the sheen colour for its angle
    d.ellipse((c - ring_out - 3 * SS, c - ring_out - 3 * SS, c + ring_out + 3 * SS, c + ring_out + 3 * SS), fill=black)
    steps = 240
    for i in range(steps):
        a0 = 360 * i / steps
        col = _ring_color(tier, math.radians(a0 + 180 / steps))
        d.pieslice((c - ring_out, c - ring_out, c + ring_out, c + ring_out), a0, a0 + 360 / steps + 0.6, fill=col + (255,))
    # bevel lines
    d.ellipse((c - ring_out, c - ring_out, c + ring_out, c + ring_out), outline=(255, 255, 255, 70), width=2 * SS)
    mid = (ring_in + ring_out) // 2
    d.ellipse((c - mid, c - mid, c + mid, c + mid), outline=(0, 0, 0, 60), width=SS)
    # universe accent ring just inside the metal
    d.ellipse((c - ring_in, c - ring_in, c + ring_in, c + ring_in), fill=black)
    acc_r = ring_in - SS
    d.ellipse((c - acc_r, c - acc_r, c + acc_r, c + acc_r), fill=tuple(accent) + (255,))
    # punch the portrait hole
    hole = R
    d.ellipse((c - hole - 2 * SS, c - hole - 2 * SS, c + hole + 2 * SS, c + hole + 2 * SS), fill=black)
    d.ellipse((c - hole, c - hole, c + hole, c + hole), fill=(0, 0, 0, 0))

    # studs (tier 3+) at the diagonals
    if tier >= 3:
        for deg in (225, 315):
            a = math.radians(deg)
            x, y = c + mid * math.cos(a), c + mid * math.sin(a)
            col = _lerp(_ring_color(tier, a), (255, 255, 255), 0.45)
            _diamond(d, x, y, 13 * SS, col + (255,), black, 2 * SS)

    # tier stars on an arc over the top
    fill, outline = star_color(tier)
    star_r = (15 if tier <= 5 else 12.5 if tier <= 8 else 11) * SS
    arc_r = ring_out + 20 * SS
    spread = math.radians(min(100, 18 * (tier - 1) + 1)) if tier > 1 else 0
    for i in range(tier):
        a = -math.pi / 2 + (-spread / 2 + spread * i / (tier - 1) if tier > 1 else 0)
        x, y = c + arc_r * math.cos(a), c + arc_r * math.sin(a)
        _star(d, x, y, star_r + 3 * SS, black, black, 2 * SS)
        _star(d, x, y, star_r, fill + (255,), outline + (255,), 2 * SS)

    # level badge on the lower outer diagonal (stars own the top)
    a = math.radians(135 if not flip else 45)
    bx, by = c + (ring_out + 4 * SS) * math.cos(a), c + (ring_out + 4 * SS) * math.sin(a)
    br = 36 * SS
    d.ellipse((bx - br - 4 * SS, by - br - 4 * SS, bx + br + 4 * SS, by + br + 4 * SS), fill=black)
    d.ellipse((bx - br, by - br, bx + br, by + br), fill=_ring_color(tier, a) + (255,))
    d.ellipse((bx - br + 6 * SS, by - br + 6 * SS, bx + br - 6 * SS, by + br - 6 * SS), fill=(22, 24, 34, 255))
    d.text((bx, by - 13 * SS), "LV", font=render_cache.get_font("Roboto-Black.ttf", 13 * SS), fill=(200, 205, 220, 255), anchor="mm")
    lvl = str(int(level))
    lsize = 30 if len(lvl) <= 2 else 24 if len(lvl) == 3 else 19
    d.text((bx, by + 8 * SS), lvl, font=render_cache.get_font("RobotoCondensed-Bold.ttf", lsize * SS),
           fill=level_color(int(level)) + (255,), anchor="mm", stroke_width=2 * SS, stroke_fill=black)

    # universe crest disc on the lower inner diagonal
    a = math.radians(45 if not flip else 135)
    cx2, cy2 = c + (ring_out + 2 * SS) * math.cos(a), c + (ring_out + 2 * SS) * math.sin(a)
    cr = 25 * SS
    d.ellipse((cx2 - cr - 3 * SS, cy2 - cr - 3 * SS, cx2 + cr + 3 * SS, cy2 + cr + 3 * SS), fill=black)
    d.ellipse((cx2 - cr, cy2 - cr, cx2 + cr, cy2 + cr), fill=tuple(accent) + (255,))
    d.ellipse((cx2 - cr, cy2 - cr, cx2 + cr, cy2 + cr), outline=(255, 255, 255, 110), width=2 * SS)
    if crest_text:
        d.text((cx2, cy2), crest_text[:3], font=render_cache.get_font("Roboto-Black.ttf", 18 * SS), fill=(255, 255, 255, 255),
               anchor="mm", stroke_width=SS, stroke_fill=black)

    return im.resize((size // SS, size // SS), Image.LANCZOS)


_CACHE = OrderedDict()
_LOCK = threading.Lock()


def get_frame(radius, tier, level, accent, flip=False, resolved=False, crest_text=""):
    key = (radius, tier, level, tuple(accent), flip, resolved, crest_text)
    with _LOCK:
        hit = _CACHE.get(key)
        if hit is not None:
            _CACHE.move_to_end(key)
            return hit
    frame = draw_frame(radius, tier, level, accent, flip, resolved, crest_text)
    with _LOCK:
        _CACHE[key] = frame
        while len(_CACHE) > 96:
            _CACHE.popitem(last=False)
    return frame
