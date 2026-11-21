"""Tall art panels for raw (template-free) battle art of any shape.

Every card is shown as a framed portrait panel (battles, /build, /viewcard...).
A card can carry plain art (no card template) in its database document:

    CARD_ART          normal art (URL)
    CARD_FOCUS_ART    art while focused (optional, falls back to CARD_ART)
    CARD_RESOLVE_ART  art while resolved (optional, falls back to CARD_ART)
    CARD_ART_CROP     optional crop centre "x,y" (fractions 0-1, e.g. "0.5,0.3")

Cards without CARD_ART use the art inside the character circle of their premade
card (PATH / FPATH / RPATH), so no template is ever shown.

Any image shape works: ``smart_crop`` picks the most detailed window (edges),
leaning toward the top where faces usually are, unless a crop centre is set.
Cloudinary URLs are asked for a pre-cropped, smaller image (content-aware
``g_auto``), which is sharper and faster to download; if Cloudinary refuses the
transformation the original URL is used.
"""
import math
import re
import threading
from collections import OrderedDict

from PIL import Image, ImageDraw, ImageFilter

import battle_frames
import render_cache

SS = 3


def smart_crop(im, aspect, focus=None, upper_bias=0.18):
    """Crop ``im`` to width/height ``aspect`` keeping the most detailed region."""
    im = im.convert("RGB")
    w, h = im.size
    if w / h > aspect:          # too wide: choose x
        cw, ch = int(round(h * aspect)), h
    else:                       # too tall: choose y
        cw, ch = w, int(round(w / aspect))
    if focus is not None:
        fx, fy = focus
        x = min(max(0, int(fx * w - cw / 2)), w - cw)
        y = min(max(0, int(fy * h - ch / 2)), h - ch)
        return im.crop((x, y, x + cw, y + ch))

    scale = 96 / max(w, h)
    sw, sh = max(1, int(w * scale)), max(1, int(h * scale))
    energy = im.resize((sw, sh), Image.BILINEAR).convert("L").filter(ImageFilter.FIND_EDGES)
    px = energy.load()
    cols = [sum(px[x, y] for y in range(sh)) for x in range(sw)]
    rows = [sum(px[x, y] for x in range(sw)) for y in range(sh)]
    if cw < w:
        win = max(1, int(cw * scale))
        best, bx = -1, 0
        for x in range(0, sw - win + 1):
            s = sum(cols[x:x + win])
            if s > best:
                best, bx = s, x
        x = min(int(bx / scale), w - cw)
        return im.crop((x, 0, x + cw, h))
    win = max(1, int(ch * scale))
    best, by = -1, 0
    for y in range(0, sh - win + 1):
        s = sum(rows[y:y + win]) * (1 - upper_bias * y / max(1, sh - win))
        if s > best:
            best, by = s, y
    y = min(int(by / scale), h - ch)
    return im.crop((0, y, w, y + ch))


def parse_focus(value):
    """'0.5,0.3' / [0.5, 0.3] / {'x': .5, 'y': .3} -> (x, y) clamped to 0..1, or None."""
    try:
        if value is None or value == "":
            return None
        if isinstance(value, dict):
            x, y = value.get("x", value.get("X")), value.get("y", value.get("Y"))
        elif isinstance(value, (list, tuple)):
            x, y = value[0], value[1]
        else:
            parts = re.split(r"[,\s]+", str(value).strip())
            x, y = parts[0], parts[1]
        x, y = float(x), float(y)
        if x > 1 or y > 1:          # given as percentages
            x, y = x / 100, y / 100
        return max(0.0, min(1.0, x)), max(0.0, min(1.0, y))
    except Exception:
        return None


def cloudinary_variant(url, width, height):
    """Same Cloudinary image, cropped to width x height around the subject (None if not Cloudinary)."""
    if not url or "res.cloudinary.com" not in url or "/upload/" not in url:
        return None
    head, tail = url.split("/upload/", 1)
    return f"{head}/upload/c_fill,g_auto,w_{int(width)},h_{int(height)}/{tail}"


def load_panel_art(url, width, height, focus=None):
    """Panel-shaped RGB art (width x height) and the full picture for the backdrop.

    Never raises: a placeholder is returned if the art cannot be downloaded.
    """
    import render_cache
    focus = parse_focus(focus)
    if focus is None:
        variant = cloudinary_variant(url, width, height)
        if variant:
            data = render_cache.fetch_image_bytes(variant)
            if data is not None:
                try:
                    from io import BytesIO
                    im = Image.open(BytesIO(data)).convert("RGB")
                    full = render_cache.load_image(url).convert("RGB") if render_cache.fetch_image_bytes(url) else im
                    if im.size != (width, height):
                        im = smart_crop(im, width / height).resize((width, height), Image.LANCZOS)
                    return im, full
                except Exception:
                    pass
    full = render_cache.load_image(url, fallback_label="").convert("RGB")
    panel = smart_crop(full, width / height, focus).resize((width, height), Image.LANCZOS)
    return panel, full


# Where the character circle sits inside a premade (templated) 1200x600 card,
# as fractions of the image size.  Only used for cards without plain art.
TEMPLATE_CX, TEMPLATE_CY, TEMPLATE_R = 0.225, 0.523, 0.320
TEMPLATE_LIFT = 0.12          # how far above the circle centre the crop is centred (fraction of r)


def load_template_panel(url, width, height, label=""):
    """Panel art cut from a premade card: the largest width:height rectangle
    that fits inside the card's character circle, so no template shows.

    Returns (panel, picture for the blurred backdrop).  Never raises.
    """
    import render_cache
    full = render_cache.load_image(url, fallback_label=label).convert("RGB")
    w, h = full.size
    aspect = width / height
    if w >= 1.7 * h:                       # the usual 2:1 card template
        cx, cy, r = TEMPLATE_CX * w, TEMPLATE_CY * h, TEMPLATE_R * h
        # largest rectangle inside the circle whose centre sits a little above the
        # circle's (faces tend to be in the upper half): (a²+1)/4·h² + s·h + s² - r² = 0
        s = TEMPLATE_LIFT * r
        qa, qb, qc = (aspect * aspect + 1) / 4, s, s * s - r * r
        rh = (-qb + math.sqrt(qb * qb - 4 * qa * qc)) / (2 * qa)
        rw = aspect * rh
        top = cy - s - rh / 2
        box = (int(cx - rw / 2), int(top), int(cx + rw / 2), int(top + rh))
        art = full.crop(box)
        backdrop = full.crop((int(cx - r), int(cy - r), int(cx + r), int(cy + r)))
    else:                                  # not a template: treat it as plain art
        art = smart_crop(full, aspect)
        backdrop = full
    panel = art.resize((width, height), Image.LANCZOS)
    if art.size[0] < width:
        # the art inside the circle is small: sharpen a little after enlarging it
        panel = panel.filter(ImageFilter.UnsharpMask(radius=1.6, percent=70, threshold=2))
    return panel, backdrop


def panel_frame(w, h, tier=1, level=1, accent=(120, 140, 200), flip=False, crest_text="", radius=22):
    """RGBA frame for a w x h panel (inner area transparent), with stars, level badge and crest."""
    tier = max(1, min(10, int(tier or 1)))
    pad = 46
    W, H = (w + 2 * pad) * SS, (h + 2 * pad) * SS
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = pad * SS, pad * SS, (pad + w) * SS, (pad + h) * SS
    black = (0, 0, 0, 255)
    border = 15 * SS
    r = radius * SS
    # metal border: draw thin vertical strips with the sheen colour for their angle round the centre
    outer = (x0 - border, y0 - border, x1 + border, y1 + border)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle(outer, radius=r + border, fill=255)
    md.rounded_rectangle((x0, y0, x1, y1), radius=r, fill=0)
    metal = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mdraw = ImageDraw.Draw(metal)
    cx, cy = W / 2, H / 2
    steps = 240
    big = max(W, H)
    for i in range(steps):
        a0 = 360 * i / steps
        col = battle_frames._ring_color(tier, math.radians(a0 + 180 / steps))
        mdraw.pieslice((cx - big, cy - big, cx + big, cy + big), a0, a0 + 360 / steps + 0.6, fill=col + (255,))
    d.rounded_rectangle((outer[0] - 3 * SS, outer[1] - 3 * SS, outer[2] + 3 * SS, outer[3] + 3 * SS), radius=r + border + 3 * SS, fill=black)
    im.paste(metal, (0, 0), mask)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(outer, radius=r + border, outline=(255, 255, 255, 70), width=2 * SS)
    # universe accent line + punch the art window
    d.rounded_rectangle((x0 - 4 * SS, y0 - 4 * SS, x1 + 4 * SS, y1 + 4 * SS), radius=r + 4 * SS, fill=black)
    d.rounded_rectangle((x0 - 2 * SS, y0 - 2 * SS, x1 + 2 * SS, y1 + 2 * SS), radius=r + 2 * SS, fill=tuple(accent) + (255,))
    d.rounded_rectangle((x0, y0, x1, y1), radius=r, fill=(0, 0, 0, 0))
    # corner studs from tier 3
    if tier >= 3:
        for (sx, sy) in ((x0, y0), (x1, y0)):
            col = battle_frames._lerp(battle_frames._ring_color(tier, 0.8), (255, 255, 255), 0.45)
            battle_frames._diamond(d, sx, sy, 14 * SS, col + (255,), black, 2 * SS)
    # stars along the top edge
    fill, outline = battle_frames.star_color(tier)
    star_r = (14 if tier <= 6 else 11.5) * SS
    gap = star_r * 2.25
    sx0 = (x0 + x1) / 2 - gap * (tier - 1) / 2
    for i in range(tier):
        sx = sx0 + gap * i
        battle_frames._star(d, sx, y0 - border / 2, star_r + 3 * SS, black, black, 2 * SS)
        battle_frames._star(d, sx, y0 - border / 2, star_r, fill + (255,), outline + (255,), 2 * SS)
    # level badge bottom outer corner, crest bottom inner corner
    bx = x0 if not flip else x1
    by = y1
    br = 34 * SS
    d.ellipse((bx - br - 4 * SS, by - br - 4 * SS, bx + br + 4 * SS, by + br + 4 * SS), fill=black)
    d.ellipse((bx - br, by - br, bx + br, by + br), fill=battle_frames._ring_color(tier, 2.3) + (255,))
    d.ellipse((bx - br + 6 * SS, by - br + 6 * SS, bx + br - 6 * SS, by + br - 6 * SS), fill=(22, 24, 34, 255))
    d.text((bx, by - 12 * SS), "LV", font=render_cache.get_font("Roboto-Black.ttf", 12 * SS), fill=(200, 205, 220, 255), anchor="mm")
    lvl = str(int(level))
    lsize = 28 if len(lvl) <= 2 else 22 if len(lvl) == 3 else 18
    d.text((bx, by + 8 * SS), lvl, font=render_cache.get_font("RobotoCondensed-Bold.ttf", lsize * SS),
           fill=battle_frames.level_color(int(level)) + (255,), anchor="mm", stroke_width=2 * SS, stroke_fill=black)
    cx2 = x1 if not flip else x0
    cr = 24 * SS
    d.ellipse((cx2 - cr - 3 * SS, by - cr - 3 * SS, cx2 + cr + 3 * SS, by + cr + 3 * SS), fill=black)
    d.ellipse((cx2 - cr, by - cr, cx2 + cr, by + cr), fill=tuple(accent) + (255,))
    if crest_text:
        d.text((cx2, by), crest_text[:3], font=render_cache.get_font("Roboto-Black.ttf", 17 * SS), fill=(255, 255, 255, 255),
               anchor="mm", stroke_width=SS, stroke_fill=black)
    return im.resize((W // SS, H // SS), Image.LANCZOS), pad


_FRAMES = OrderedDict()
_LOCK = threading.Lock()


def get_panel_frame(w, h, tier, level, accent, flip=False, crest_text=""):
    key = (w, h, tier, level, tuple(accent), flip, crest_text)
    with _LOCK:
        hit = _FRAMES.get(key)
        if hit is not None:
            _FRAMES.move_to_end(key)
            return hit
    frame = panel_frame(w, h, tier, level, accent, flip, crest_text)
    with _LOCK:
        _FRAMES[key] = frame
        while len(_FRAMES) > 64:
            _FRAMES.popitem(last=False)
    return frame
