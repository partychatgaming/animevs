"""Focus and Resolve effects for the battle scene.

The two powered-up states are meant to read differently at a glance:

FOCUS  - cool and controlled.  The fighter's half turns deep blue, manga
         "concentration lines" converge on the portrait, twin cyan rings and
         sparks circle the frame.
RESOLVE - hot and explosive.  The half burns red, golden light rays burst from
         behind the fighter, a layered flame aura flares around a larger
         portrait, lightning crackles off the frame and embers drift upward.

Both looks are coloured by the fighter's type (the element of its Ultimate):
a Fire card focuses in embers and resolves in a blaze, an Ice card in frost and
snowflakes, Electric in violet and lightning, and so on (element_art.py).

Each effect is clipped to its fighter's half of the scene.  Effect layers are
drawn once and cached; per-turn variation (lightning, sparks) is seeded by the
turn number so the scene shifts a little every turn.  ``t`` (0..1) animates the
transformation for the GIF played on the turn a card powers up.
"""
import math
import random
import threading
from collections import OrderedDict

from PIL import Image, ImageChops, ImageDraw, ImageFilter

import element_art

LAYER = 760                 # effect layers are LAYER x LAYER, centred on the portrait
HALF_LAYER = LAYER // 2

VARIANTS = 4                # per-turn variations of sparks / lightning (cached)
FOCUS_TINT = (16, 52, 120)
FOCUS_CYAN = (120, 225, 255)
RESOLVE_TINT = (110, 14, 8)

_cache = OrderedDict()
_lock = threading.Lock()


def _cached(key, make):
    with _lock:
        hit = _cache.get(key)
        if hit is not None:
            _cache.move_to_end(key)
            return hit
    value = make()
    with _lock:
        _cache[key] = value
        while len(_cache) > 96:
            _cache.popitem(last=False)
    return value


STYLES = 8                  # distinct ray/burst shapes; cards share them so the cache stays warm


def _seed(text):
    return (sum(ord(ch) * (i + 1) for i, ch in enumerate(str(text))) & 0xFFFFFFFF) % STYLES


def _falloff(inner, outer):
    """L mask: 255 inside ``inner`` radius, fading to 0 at ``outer``."""
    def make():
        m = Image.new("L", (LAYER, LAYER), 0)
        d = ImageDraw.Draw(m)
        steps = 40
        for i in range(steps, -1, -1):
            r = inner + (outer - inner) * i / steps
            d.ellipse((HALF_LAYER - r, HALF_LAYER - r, HALF_LAYER + r, HALF_LAYER + r), fill=int(255 * (1 - i / steps)))
        return m
    return _cached(("falloff", inner, outer), make)


def _with_alpha(layer, mask):
    r, g, b, a = layer.split()
    return Image.merge("RGBA", (r, g, b, ImageChops.multiply(a, mask)))


# --------------------------------------------------------------------------- focus
def _pal(element):
    name, emoji, dark, mid, light, glow, motif = element_art.style(element)
    return dark, mid, light, glow, motif


def _lift(color, amount):
    return tuple(min(255, int(c + (255 - c) * amount)) for c in color)


def focus_lines(radius, seed, element=None):
    def make():
        rng = random.Random(seed)
        im = Image.new("RGBA", (LAYER, LAYER), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        c = HALF_LAYER
        for _ in range(110):
            a = rng.uniform(0, 2 * math.pi)
            r_in = radius + rng.uniform(34, 110)
            r_out = HALF_LAYER + 20
            w = rng.uniform(0.006, 0.022)
            alpha = rng.randint(70, 170)
            pts = [(c + r_in * math.cos(a), c + r_in * math.sin(a)),
                   (c + r_out * math.cos(a - w), c + r_out * math.sin(a - w)),
                   (c + r_out * math.cos(a + w), c + r_out * math.sin(a + w))]
            d.polygon(pts, fill=line_color + (alpha,))
        return _with_alpha(im, _falloff(radius + 120, HALF_LAYER))
    line_color = _lift(_pal(element)[2], 0.55)
    return _cached(("focus_lines", radius, seed, line_color), make)


def focus_aura(radius, turn_seed, element=None):
    dark, mid, light, glow, motif = _pal(element)
    def make():
        rng = random.Random(turn_seed)
        im = Image.new("RGBA", (LAYER, LAYER), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        c = HALF_LAYER
        for r, w, alpha in ((radius + 36, 14, 200), (radius + 62, 8, 160)):
            d.ellipse((c - r, c - r, c + r, c + r), outline=glow + (alpha,), width=w)
        haze = im.filter(ImageFilter.GaussianBlur(10))
        haze = Image.alpha_composite(haze, haze)
        im = Image.alpha_composite(haze, im)
        d = ImageDraw.Draw(im)
        for r, alpha in ((radius + 36, 255), (radius + 62, 200)):
            d.ellipse((c - r, c - r, c + r, c + r), outline=_lift(light, 0.6) + (alpha,), width=3)
        # the type's motif circling the rings (snowflakes, embers, leaves...)
        for _ in range(16):
            a = rng.uniform(0, 2 * math.pi)
            r = radius + rng.uniform(26, 96)
            x, y = c + r * math.cos(a), c + r * math.sin(a)
            element_art.glyph(d, motif, x, y, rng.uniform(7, 13), rng.uniform(0, 6.28), (dark, mid, light, glow), alpha=rng.randint(190, 255))
        return im
    return _cached(("focus_aura", radius, turn_seed, element_art.style(element)[0]), make)


# --------------------------------------------------------------------------- resolve
def resolve_rays(radius, seed, element=None):
    dark, mid, light, glow, motif = _pal(element)
    def make():
        rng = random.Random(seed)
        im = Image.new("RGBA", (LAYER, LAYER), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        c = HALF_LAYER
        n = 16
        offset = rng.uniform(0, 2 * math.pi / n)
        for i in range(n):
            a0 = offset + 2 * math.pi * i / n
            a1 = a0 + math.pi / n * rng.uniform(0.55, 0.9)
            r = HALF_LAYER + 30
            color = light + (150,) if i % 2 == 0 else glow + (120,)
            d.polygon([(c, c), (c + r * math.cos(a0), c + r * math.sin(a0)), (c + r * math.cos(a1), c + r * math.sin(a1))], fill=color)
        im = im.filter(ImageFilter.GaussianBlur(2))
        return _with_alpha(im, _falloff(radius + 40, HALF_LAYER))
    return _cached(("resolve_rays", radius, seed, element_art.style(element)[0]), make)


def resolve_burst(radius, seed, element=None):
    dark, mid, light, glow, motif = _pal(element)
    def make():
        rng = random.Random(seed)
        im = Image.new("RGBA", (LAYER, LAYER), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        c = HALF_LAYER
        spikes = 30
        lengths = [rng.uniform(0.35, 1.0) for _ in range(spikes)]
        for scale, color in ((1.0, _lift(dark, 0.25) + (235,)), (0.84, mid + (240,)), (0.70, light + (245,))):
            pts = []
            for i in range(spikes * 2):
                a = 2 * math.pi * i / (spikes * 2) - math.pi / 2
                if i % 2 == 0:
                    r = radius + 26 + 64 * lengths[i // 2] * scale
                else:
                    r = radius + 18
                pts.append((c + r * math.cos(a), c + r * math.sin(a)))
            d.polygon(pts, fill=color)
        haze = im.filter(ImageFilter.GaussianBlur(14))
        return Image.alpha_composite(haze, im.filter(ImageFilter.GaussianBlur(1.5)))
    return _cached(("resolve_burst", radius, seed, element_art.style(element)[0]), make)


def resolve_sparks(radius, turn_seed, element=None):
    """Lightning and the type's particles: re-rolled every turn so the aura keeps moving."""
    dark, mid, light, glow, motif = _pal(element)
    def make():
        rng = random.Random(turn_seed)
        im = Image.new("RGBA", (LAYER, LAYER), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        c = HALF_LAYER
        # the type's particles drift up: bias them above the portrait
        for _ in range(30):
            a = rng.uniform(-math.pi, 0) if rng.random() < 0.75 else rng.uniform(0, math.pi)
            r = rng.uniform(radius + 70, HALF_LAYER - 20)
            x, y = c + r * math.cos(a), c + r * math.sin(a)
            element_art.glyph(d, motif, x, y, rng.uniform(5, 11), rng.uniform(0, 6.28), (dark, mid, light, glow), alpha=rng.randint(170, 255))
        bolts = Image.new("RGBA", (LAYER, LAYER), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bolts)
        for _ in range(6):
            a = rng.uniform(0, 2 * math.pi)
            r = radius + 16
            pts = [(c + r * math.cos(a), c + r * math.sin(a))]
            for _ in range(6):
                r += rng.uniform(14, 26)
                a += rng.uniform(-0.22, 0.22)
                pts.append((c + r * math.cos(a), c + r * math.sin(a)))
            bd.line(pts, fill=light + (255,), width=13, joint="curve")
        haze = bolts.filter(ImageFilter.GaussianBlur(7))
        im = Image.alpha_composite(im, haze)
        im = Image.alpha_composite(im, _thin(bolts))
        return im
    return _cached(("resolve_sparks", radius, turn_seed, element_art.style(element)[0]), make)


def _thin(bolts):
    """White core for the lightning: the bolt mask shrunk with a min filter."""
    a = bolts.getchannel("A").filter(ImageFilter.MinFilter(7))
    white = Image.new("RGBA", bolts.size, (255, 255, 250, 0))
    white.putalpha(a)
    return white


# --------------------------------------------------------------------------- compositing
def _transform(layer, scale=1.0, angle=0.0, alpha=1.0):
    out = layer
    if angle:
        out = out.rotate(angle, resample=Image.BILINEAR)
    if abs(scale - 1.0) > 0.01:
        size = max(2, int(LAYER * scale))
        resized = out.resize((size, size), Image.BILINEAR)
        out = Image.new("RGBA", (LAYER, LAYER), (0, 0, 0, 0))
        if size >= LAYER:
            off = (size - LAYER) // 2
            out = resized.crop((off, off, off + LAYER, off + LAYER))
        else:
            off = (LAYER - size) // 2
            out.paste(resized, (off, off))
    if alpha < 0.999:
        a = out.getchannel("A").point(lambda v: int(v * max(0.0, alpha)))
        out = out.copy()
        out.putalpha(a)
    return out


def _ease_out_back(t):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def apply(canvas, side_mask, center, radius, state, name="", turn=0, t=1.0, frame=0, element=None):
    """Draw the effect for ``state`` ("focus" / "resolve") onto ``canvas`` (RGB, in place).

    ``side_mask`` (L, canvas size) clips the effect to the fighter's half.
    ``t`` < 1 draws an intermediate frame of the power-up animation.
    """
    if state not in ("focus", "resolve"):
        return
    t = max(0.0, min(1.0, t))
    if t >= 1.0:
        # the finished effect is identical turn to turn (up to VARIANTS), so keep it
        key = (state, radius, center, canvas.size, id(side_mask), _seed(name), turn % VARIANTS, element_art.style(element)[0])
        with _lock:
            hit = _finished.get(key)
            if hit is not None:
                _finished.move_to_end(key)
        if hit is None:
            hit = _render_effect(canvas.size, side_mask, center, radius, state, name, turn, 1.0, frame, element)
            with _lock:
                _finished[key] = hit
                while len(_finished) > FINISHED_CACHE:
                    _finished.popitem(last=False)
    else:
        hit = _render_effect(canvas.size, side_mask, center, radius, state, name, turn, t, frame, element)
    rgb, alpha, box = hit
    canvas.paste(rgb, box[:2], alpha)


FINISHED_CACHE = 16            # ~1.6 MB each (one fighter's half, RGBA)
_finished = OrderedDict()


def _render_effect(size, side_mask, center, radius, state, name, turn, t, frame, element=None):
    """The effect for one half as (RGBA layer cropped to that half, box)."""
    w, h = size
    cx, cy = center
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pos = (cx - HALF_LAYER, cy - HALF_LAYER)
    seed = _seed(name)
    dark, mid, light, glow, motif = _pal(element)
    focus_tint = tuple(int(c * 0.55) for c in _lift(dark, 0.15))
    resolve_tint = _lift(dark, 0.1)

    if state == "focus":
        tint_alpha = int(120 * t)
        overlay.paste(focus_tint + (tint_alpha,), (0, 0, w, h))
        lines = _transform(focus_lines(radius, seed, element), scale=1.0 + 0.9 * (1 - t) ** 2, alpha=min(1.0, t * 1.4))
        overlay.alpha_composite(lines, pos)
        aura = focus_aura(radius, seed + turn % VARIANTS, element)
        overlay.alpha_composite(_transform(aura, alpha=t), pos)
        if t < 1:
            # a shockwave ring travelling outwards as the fighter locks in
            ring = Image.new("RGBA", (LAYER, LAYER), (0, 0, 0, 0))
            rr = radius + 30 + 260 * t
            ImageDraw.Draw(ring).ellipse((HALF_LAYER - rr, HALF_LAYER - rr, HALF_LAYER + rr, HALF_LAYER + rr),
                                         outline=_lift(glow, 0.5) + (int(230 * (1 - t)),), width=8)
            overlay.alpha_composite(ring.filter(ImageFilter.GaussianBlur(2)), pos)
    else:
        overlay.paste(resolve_tint + (int(150 * t),), (0, 0, w, h))
        rays = _transform(resolve_rays(radius, seed, element), scale=0.7 + 0.3 * t, angle=-35 * (1 - t), alpha=min(1.0, t * 1.6))
        overlay.alpha_composite(rays, pos)
        burst_scale = 0.45 + 0.55 * _ease_out_back(t) if t < 1 else 1.0
        overlay.alpha_composite(_transform(resolve_burst(radius, seed, element), scale=burst_scale, alpha=min(1.0, 0.3 + t)), pos)
        if t > 0.35:
            overlay.alpha_composite(resolve_sparks(radius, seed + (turn + frame) % VARIANTS, element), pos)
        if t < 0.6:
            # white flash as the power releases
            flash = int(235 * max(0.0, 1 - abs(t - 0.22) / 0.38))
            if flash > 0:
                overlay.alpha_composite(Image.new("RGBA", (w, h), _lift(light, 0.6) + (flash,)))

    a = ImageChops.multiply(overlay.getchannel("A"), side_mask)
    overlay.putalpha(a)
    box = side_mask.getbbox() or (0, 0, w, h)
    layer = overlay.crop(box)
    return layer.convert("RGB"), layer.getchannel("A"), box


def state_of(snap):
    if not snap or snap.get("health", 0) <= 0:
        return "normal"
    if snap.get("resolved"):
        return "resolve"
    if snap.get("focused"):
        return "focus"
    return "normal"
