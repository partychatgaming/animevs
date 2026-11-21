"""The battle screen image: both fighters face to face in one picture.

Replaces the old per-turn card render (which only ever showed the card whose
turn it was, with the opponent's numbers squeezed into the embed's author
line).  One image now carries everything a player scans every turn:

    portrait  name / level / class      VS      class / level / name  portrait
              ATK  DEF                  TURN n                 ATK  DEF
    [ HP bar ......................... ]        [ ......................... HP bar ]
    [ ST bar ........ ]                         [ ........ ST bar ]
    (status chips: guards, focus/resolve, burns, poison...)

Usage
-----
Take snapshots on the event loop (cheap, and the battle cannot change a card
while it is being drawn), then draw in the render pool::

    left = battle_scene.snapshot(player_card, opponent_card)
    right = battle_scene.snapshot(opponent_card, player_card)
    data = await render_cache.render_async(battle_scene.render, left, right, turn_total=7, active="left")

``render`` never raises: if anything goes wrong a plain text scene is drawn.
"""
import random
import threading
from collections import OrderedDict
from io import BytesIO

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps

import battle_frames
import battle_panels
import battle_fx
import element_art
import render_cache
from logger import loggy

WIDTH, HEIGHT = 1200, 600
HALF = WIDTH // 2

# Where the character portrait sits inside the standard 1200x600 card art,
# as fractions of the art size (the art's own frame circle is a little larger).
ART_PORTRAIT_CX = 0.225
ART_PORTRAIT_CY = 0.523
ART_PORTRAIT_R = 0.333

PORTRAIT_R = 128
PORTRAIT_Y = 200
LEFT_PORTRAIT_X = 186
RIGHT_PORTRAIT_X = WIDTH - LEFT_PORTRAIT_X
TEXT_INNER = 352              # text column starts this far from the outer edge
TEXT_WIDTH = 220
BAR_MARGIN = 36
HP_BAR_Y, HP_BAR_H = 392, 44
ST_BAR_Y, ST_BAR_H = 446, 28
CHIPS_Y = 492
JPEG_QUALITY = 86
RESOLVE_RADIUS_BONUS = 12      # a resolved fighter's portrait grows
GIF_SIZE = (900, 450)
PANEL_W, PANEL_H = 236, 296     # raw battle art panels (4:5)
PANEL_RESOLVE_SCALE = 1.06

WHITE = (255, 255, 255)
MUTED = (196, 202, 220)
DIM = (140, 146, 165)
GOLD = (255, 205, 64)
BAR_BACK = (16, 18, 26)
RING = (70, 76, 96)
STAMINA = (64, 156, 255)

CHIP_COLORS = {
    "guard": (52, 120, 220),
    "focus": (214, 64, 120),
    "resolve": (226, 168, 30),
    "summon": (40, 160, 120),
    "debuff": (196, 52, 52),
    "info": (86, 92, 112),
}

FONT_NAME = "YesevaOne-Regular.ttf"
FONT_BOLD = "Roboto-Bold.ttf"
FONT_BLACK = "Roboto-Black.ttf"
FONT_NUM = "RobotoCondensed-Bold.ttf"
FONT_VS = "KomikaTitle.ttf"


# --------------------------------------------------------------------------- universes
UNIVERSE_ACCENTS = {
    "Naruto": (235, 120, 30), "My Hero Academia": (52, 168, 96), "Jujutsu Kaisen": (124, 72, 210),
    "Jujustu Kaisen": (124, 72, 210), "Bleach": (44, 44, 52), "Chainsawman": (200, 40, 60),
    "One Piece": (220, 50, 50), "Dragon Ball Z": (240, 140, 20), "Demon Slayer": (40, 150, 140),
    "Attack On Titan": (120, 90, 60), "Pokemon": (230, 60, 60), "One Punch Man": (240, 200, 40),
}


def universe_accent(universe):
    if universe in UNIVERSE_ACCENTS:
        return UNIVERSE_ACCENTS[universe]
    import colorsys, hashlib
    h = hashlib.md5(str(universe).encode()).digest()[0] / 255
    r, g, b = colorsys.hsv_to_rgb(h, 0.62, 0.86)
    return int(r * 255), int(g * 255), int(b * 255)


def universe_initials(universe):
    words = [w for w in str(universe or "").replace("-", " ").split() if w[:1].isalnum()]
    if not words:
        return ""
    if len(words) == 1:
        return words[0][:3].upper()
    skip = {"of", "the", "a", "an", "as", "in", "to"}
    letters = "".join(w[0] for w in words if w.lower() not in skip) or "".join(w[0] for w in words)
    return letters[:3].upper()


# --------------------------------------------------------------------------- snapshots
def _num(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def short_number(value):
    """1234 -> '1,234', 23456 -> '23.5K', 1234567 -> '1.23M' (fits small spaces)."""
    n = round(_num(value))
    sign = "-" if n < 0 else ""
    n = abs(n)
    if n < 10_000:
        return f"{sign}{n:,}"
    if n < 1_000_000:
        return f"{sign}{n / 1000:.1f}".rstrip("0").rstrip(".") + "K"
    return f"{sign}{n / 1_000_000:.2f}".rstrip("0").rstrip(".") + "M"


def art_for(card):
    """The one picture this card uses, including while focused or resolved."""
    return getattr(card, "path", None)


def battle_art_for(card):
    """Raw (template-free) art for this card, or None. Focus and resolve use the same picture."""
    return getattr(card, "battle_art", None) or None


def status_chips(card, opponent):
    """(text, kind) pairs for what is currently affecting ``card``.

    Damage-over-time effects are stored on the card that applied them, so the
    afflictions shown for ``card`` are read from ``opponent``.
    """
    chips = []
    g = lambda obj, name, default=0: getattr(obj, name, default) if obj is not None else default

    if g(card, "used_resolve", False):
        chips.append(("RESOLVED", "resolve"))
    elif g(card, "used_focus", False):
        chips.append(("FOCUSED", "focus"))
    if g(card, "used_block", False) or g(card, "used_defend", False):
        chips.append(("GUARDING", "guard"))
    if g(card, "barrier_active", False) and _num(g(card, "_barrier_value")) > 0:
        chips.append((f"BARRIER x{round(_num(g(card, '_barrier_value')))}", "guard"))
    if g(card, "shield_active", False) and _num(g(card, "_shield_value")) > 0:
        chips.append((f"SHIELD {short_number(g(card, '_shield_value'))}", "guard"))
    if g(card, "parry_active", False) and _num(g(card, "_parry_value")) > 0:
        chips.append((f"PARRY x{round(_num(g(card, '_parry_value')))}", "guard"))
    if g(card, "siphon_active", False) and _num(g(card, "_siphon_value")) > 0:
        chips.append((f"SIPHON {short_number(g(card, '_siphon_value'))}", "guard"))

    if opponent is not None:
        if _num(g(opponent, "burn_dmg")) > 15:
            chips.append((f"BURN {short_number(g(opponent, 'burn_dmg'))}", "debuff"))
        if _num(g(opponent, "poison_dmg")) > 0:
            chips.append((f"POISON {short_number(g(opponent, 'poison_dmg'))}", "debuff"))
        if _num(g(opponent, "rot_dmg")) > 0:
            chips.append((f"ROT {short_number(g(opponent, 'rot_dmg'))}", "debuff"))
        if g(opponent, "freeze_enh", False):
            chips.append(("FROZEN", "debuff"))
        if g(opponent, "bleed_hit", False):
            chips.append(("BLEEDING", "debuff"))
        if g(opponent, "gravity_hit", False):
            chips.append(("NO BLOCK", "debuff"))
    return chips


def snapshot(card, opponent=None):
    """Everything the scene needs from a card, copied so drawing is thread-safe."""
    if card is None:
        return None
    try:
        level = int(_num(getattr(card, "card_lvl", 0)))
    except Exception:
        level = 0
    class_name = str(getattr(card, "class_message", "") or getattr(card, "card_class", "") or "").strip()
    name = str(getattr(card, "rname", "") if getattr(card, "used_resolve", False) and getattr(card, "rname", "") else getattr(card, "name", "") or "")
    try:
        chips = status_chips(card, opponent)
    except Exception as ex:
        loggy.warning(f"battle scene: status chips failed: {type(ex).__name__}: {ex}")
        chips = []
    return {
        "name": name.strip() or "Unknown",
        "level": level,
        "class_name": class_name,
        "art": art_for(card),
        "health": max(0.0, _num(getattr(card, "health", 0))),
        "max_health": max(1.0, _num(getattr(card, "max_health", 1), 1)),
        "stamina": max(0.0, _num(getattr(card, "stamina", 0))),
        "max_stamina": max(1.0, _num(getattr(card, "max_stamina", 100), 100)),
        "attack": _num(getattr(card, "attack", 0)),
        "defense": _num(getattr(card, "defense", 0)),
        "chips": chips,
        "tier": int(_num(getattr(card, "tier", 1), 1)) or 1,
        "universe": str(getattr(card, "universe", "") or ""),
        "resolved": bool(getattr(card, "used_resolve", False)),
        "focused": bool(getattr(card, "used_focus", False)),
        "element": element_art.element_of(card),
        "battle_art": battle_art_for(card),
        "art_focus": getattr(card, "battle_art_focus", None),
    }


# --------------------------------------------------------------------------- art cache
class _ArtCache:
    """Portrait circles and blurred backdrops, keyed by art URL.

    Decoding a 1200x600 card and blurring it costs more than drawing the whole
    rest of the scene, and the same three or four arts are drawn every turn.
    """

    def __init__(self, max_items=64):
        self._items = OrderedDict()
        self._max = max_items
        self._lock = threading.Lock()

    def get(self, url, label, maker=None):
        key = (url, label, maker is not None)
        with self._lock:
            hit = self._items.get(key)
            if hit is not None:
                self._items.move_to_end(key)
                return hit
        made = (maker or _make_art)(url, label)
        with self._lock:
            self._items[key] = made
            while len(self._items) > self._max:
                self._items.popitem(last=False)
        return made

    def clear(self):
        with self._lock:
            self._items.clear()


def _backdrop_from(full):
    bw = HALF + 80
    small = battle_panels.smart_crop(full, bw / HEIGHT).resize((64, max(1, 64 * HEIGHT // bw)), Image.BILINEAR)
    backdrop = small.filter(ImageFilter.GaussianBlur(3)).resize((bw, HEIGHT), Image.BICUBIC)
    backdrop = ImageEnhance.Brightness(backdrop).enhance(0.42)
    return ImageEnhance.Color(backdrop).enhance(1.25)


def _make_panel(url, focus, kind, label):
    """(panel art at resolve size, blurred backdrop): plain art, or the art cut from a premade card."""
    w, h = int(PANEL_W * PANEL_RESOLVE_SCALE), int(PANEL_H * PANEL_RESOLVE_SCALE)
    if kind == "raw":
        panel, full = battle_panels.load_panel_art(url, w, h, focus)
    else:
        panel, full = battle_panels.load_template_panel(url, w, h, label)
    return panel, _backdrop_from(full)


def side_art(snap):
    """(panel art, backdrop, True) for a snapshot.  Every card is a portrait panel."""
    if snap.get("battle_art"):
        url, kind, focus = snap["battle_art"], "raw", snap.get("art_focus")
    else:
        url, kind, focus = snap.get("art"), "template", None
    panel, backdrop = ART_CACHE.get(url, f"{kind}|{focus}|{snap['name']}",
                                    maker=lambda u, _label: _make_panel(u, focus, kind, snap["name"]))
    return panel, backdrop, True


def _make_art(url, label):
    im = render_cache.load_image(url, fallback_label=label) if url else render_cache.placeholder_image(label=label)
    im = im.convert("RGB")
    w, h = im.size
    cx, cy, r = ART_PORTRAIT_CX * w, ART_PORTRAIT_CY * h, ART_PORTRAIT_R * h
    if w < 2 * h * 0.9:
        # Not the usual 2:1 card art: use the centre of the picture.
        cx, cy, r = w / 2, h / 2, min(w, h) * 0.48
    box = tuple(int(round(v)) for v in (cx - r, cy - r, cx + r, cy + r))
    face = im.crop(box)
    portrait = face.resize((PORTRAIT_R * 2, PORTRAIT_R * 2), Image.LANCZOS)

    # Backdrop: the same art, heavily blurred and darkened (blur at low res: fast).
    small = face.resize((60, 60), Image.BILINEAR).filter(ImageFilter.GaussianBlur(4))
    backdrop = small.resize((HALF + 80, HEIGHT), Image.BICUBIC)
    backdrop = ImageEnhance.Brightness(backdrop).enhance(0.42)
    backdrop = ImageEnhance.Color(backdrop).enhance(1.25)
    return portrait, backdrop


ART_CACHE = _ArtCache()


def _circle_mask(size, scale=4):
    big = Image.new("L", (size * scale, size * scale), 0)
    ImageDraw.Draw(big).ellipse((0, 0, size * scale - 1, size * scale - 1), fill=255)
    return big.resize((size, size), Image.LANCZOS)


_MASKS = {}


def circle_mask(size):
    mask = _MASKS.get(size)
    if mask is None:
        mask = _MASKS[size] = _circle_mask(size)
    return mask


# --------------------------------------------------------------------------- drawing helpers
def font(name, size):
    return render_cache.get_font(name, size)


def text_width(draw, text, fnt):
    if not text:
        return 0
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def fit_font(draw, text, name, size, max_width, min_size=18):
    while size > min_size and text_width(draw, text, font(name, size)) > max_width:
        size -= 2
    return font(name, size)


def _wrap(draw, words, fnt, max_width):
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if text_width(draw, trial, fnt) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _ellipsize(draw, text, fnt, max_width):
    if text_width(draw, text, fnt) <= max_width:
        return text
    while text and text_width(draw, text + "…", fnt) > max_width:
        text = text[:-1]
    return text.rstrip() + "…"


def wrap_name(draw, text, name, size, max_width, max_lines=2, min_size=26):
    """Break a long name over two lines, shrinking the font only if it must."""
    words = text.split() or [text]
    for s in range(size, min_size - 1, -2):
        fnt = font(name, s)
        lines = _wrap(draw, words, fnt, max_width)
        if len(lines) <= max_lines and all(text_width(draw, l, fnt) <= max_width for l in lines):
            return lines, fnt
    fnt = font(name, min_size)
    lines = _wrap(draw, words, fnt, max_width)
    head = [_ellipsize(draw, l, fnt, max_width) for l in lines[:max_lines - 1]]
    tail = _ellipsize(draw, " ".join(lines[max_lines - 1:]), fnt, max_width)
    return head + [tail], fnt


def hex_to_rgb(value, default=(46, 204, 113)):
    try:
        value = int(value)
        return (value >> 16) & 255, (value >> 8) & 255, value & 255
    except Exception:
        return default


def health_rgb(health, max_health):
    ratio = health / max_health if max_health else 0
    if ratio >= 0.80:
        return (46, 204, 113)
    if ratio > 0.50:
        return (241, 196, 15)
    if ratio > 0.25:
        return (230, 126, 34)
    return (231, 76, 60)


def draw_text(draw, xy, text, fnt, fill=WHITE, anchor="la", stroke=2):
    draw.text(xy, text, fill=fill, font=fnt, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))


def draw_bar(draw, box, ratio, color, label_left, label_right, fnt, flip=False):
    x0, y0, x1, y1 = box
    radius = (y1 - y0) // 2
    draw.rounded_rectangle(box, radius=radius, fill=BAR_BACK, outline=(0, 0, 0), width=2)
    ratio = max(0.0, min(1.0, ratio))
    if ratio > 0:
        inner = (x0 + 3, y0 + 3, x1 - 3, y1 - 3)
        fill_w = max(int((inner[2] - inner[0]) * ratio), (y1 - y0) - 6)
        if flip:
            fill_box = (inner[2] - fill_w, inner[1], inner[2], inner[3])
        else:
            fill_box = (inner[0], inner[1], inner[0] + fill_w, inner[3])
        draw.rounded_rectangle(fill_box, radius=radius - 3, fill=color)
        # a lighter strip on top gives the bar a bit of depth
        hl = tuple(min(255, c + 45) for c in color)
        top = (fill_box[0] + radius // 2, fill_box[1] + 2, max(fill_box[0] + radius // 2, fill_box[2] - radius // 2), fill_box[1] + max(3, (y1 - y0) // 6))
        draw.rectangle(top, fill=hl)
    cy = (y0 + y1) // 2
    left, right = (label_right, label_left) if flip else (label_left, label_right)
    if left:
        draw_text(draw, (x0 + 16, cy), left, fnt, anchor="lm", stroke=2)
    if right:
        draw_text(draw, (x1 - 16, cy), right, fnt, anchor="rm", stroke=2)


def draw_chips(draw, chips, x_edge, y, max_width, flip=False, max_rows=2):
    """Status pills, packed from the outer edge inward; extra chips become '+n'."""
    if not chips:
        return
    fnt = font(FONT_BLACK, 21)
    h, gap, pad = 34, 8, 13
    rows, row, row_w = [], [], 0
    for text, kind in chips:
        w = text_width(draw, text, fnt) + pad * 2
        if row and row_w + gap + w > max_width:
            rows.append(row)
            row, row_w = [], 0
        row.append((text, kind, w))
        row_w += (gap if row_w else 0) + w
    if row:
        rows.append(row)
    if len(rows) > max_rows:
        hidden = sum(len(r) for r in rows[max_rows - 1:])
        last = rows[max_rows - 1]
        keep = []
        used = 0
        more_w = text_width(draw, f"+{hidden}", fnt) + pad * 2
        for item in last:
            if used + item[2] + gap + more_w > max_width:
                break
            keep.append(item)
            used += item[2] + gap
        hidden = sum(len(r) for r in rows[max_rows - 1:]) - len(keep)
        rows = rows[:max_rows - 1] + [keep + [(f"+{hidden}", "info", more_w)]]
    for r_index, row in enumerate(rows):
        cy = y + r_index * (h + gap)
        x = x_edge
        for text, kind, w in row:
            box = (x - w, cy, x, cy + h) if flip else (x, cy, x + w, cy + h)
            draw.rounded_rectangle(box, radius=h // 2, fill=CHIP_COLORS.get(kind, CHIP_COLORS["info"]), outline=(0, 0, 0), width=2)
            draw.text(((box[0] + box[2]) // 2, cy + h // 2), text, fill=WHITE, font=fnt, anchor="mm")
            x = x - w - gap if flip else x + w + gap


# --------------------------------------------------------------------------- the scene
_GLOWS = {}


def glow_mask(radius):
    """Soft disc behind the acting fighter (cached per size)."""
    glow = _GLOWS.get(radius)
    if glow is None:
        spread = max(14, radius // 2)
        g = radius * 2 + 4 * spread
        glow = Image.new("L", (g, g), 0)
        ImageDraw.Draw(glow).ellipse((spread, spread, g - spread, g - spread), fill=230)
        glow = _GLOWS[radius] = glow.filter(ImageFilter.GaussianBlur(max(5, spread // 2)))
    return glow


_PANEL_GLOWS = {}


def panel_glow(w, h):
    glow = _PANEL_GLOWS.get((w, h))
    if glow is None:
        glow = Image.new("L", (w + 120, h + 120), 0)
        ImageDraw.Draw(glow).rounded_rectangle((40, 40, w + 80, h + 80), radius=40, fill=230)
        glow = _PANEL_GLOWS[(w, h)] = glow.filter(ImageFilter.GaussianBlur(16))
    return glow


_PANEL_MASKS = {}


def panel_mask(w, h):
    mask = _PANEL_MASKS.get((w, h))
    if mask is None:
        big = Image.new("L", (w * 3, h * 3), 0)
        ImageDraw.Draw(big).rounded_rectangle((0, 0, w * 3 - 1, h * 3 - 1), radius=66, fill=255)
        mask = _PANEL_MASKS[(w, h)] = big.resize((w, h), Image.LANCZOS)
    return mask


def _type_color(snap, which="glow"):
    name, emoji, dark, mid, light, glow, motif = element_art.style(snap.get("element"))
    return {"glow": glow, "light": light, "mid": mid}[which]


def _active_color(snap):
    state = battle_fx.state_of(snap)
    return _type_color(snap, "glow") if state == "focus" else _type_color(snap, "light") if state == "resolve" else GOLD


def _paste_panel(canvas, draw, snap, center, panel, active, flip, glow=True):
    """Raw battle art in a tall framed panel."""
    cx, cy = center
    scale = PANEL_RESOLVE_SCALE if battle_fx.state_of(snap) == "resolve" else 1.0
    w, h = int(PANEL_W * scale), int(PANEL_H * scale)
    art = panel if panel.size == (w, h) else panel.resize((w, h), Image.LANCZOS)
    dead = snap["health"] <= 0
    if dead:
        art = ImageEnhance.Brightness(ImageOps.grayscale(art).convert("RGB")).enhance(0.55)
    elif not active:
        art = ImageEnhance.Brightness(art).enhance(0.8)
    x0, y0 = cx - w // 2, cy - h // 2
    if active and glow and not dead:
        halo = panel_glow(w, h)
        canvas.paste(_active_color(snap), (x0 - 60, y0 - 60, x0 - 60 + halo.width, y0 - 60 + halo.height), halo)
    canvas.paste(art, (x0, y0), panel_mask(w, h))
    frame, pad = battle_panels.get_panel_frame(w, h, snap.get("tier", 1), snap.get("level", 0), universe_accent(snap.get("universe")),
                                               flip=flip, crest_text=universe_initials(snap.get("universe")))
    canvas.paste(frame, (x0 - pad, y0 - pad), frame)
    deco = element_art.overlay(snap.get("element"), w, h, pad)      # the card's type: element of its Ultimate
    canvas.paste(deco, (x0 - pad, y0 - pad), deco)
    if dead:
        draw_text(draw, (cx, cy), "KO", font(FONT_VS, 84), fill=(235, 70, 70), anchor="mm", stroke=5)


def _paste_portrait(canvas, draw, snap, center, radius, active, flip=False, framed=True, glow=True):
    portrait, _, is_panel = side_art(snap)
    if is_panel and framed:
        return _paste_panel(canvas, draw, snap, center, portrait, active, flip, glow)
    if is_panel:
        # small round badge (co-op partner): the top of the panel art, where the face is
        portrait = portrait.crop((0, 0, portrait.width, portrait.width))
    size = radius * 2
    if portrait.size != (size, size):
        portrait = portrait.resize((size, size), Image.LANCZOS)
    dead = snap["health"] <= 0
    if dead:
        portrait = ImageOps.grayscale(portrait).convert("RGB")
        portrait = ImageEnhance.Brightness(portrait).enhance(0.55)
    elif not active:
        portrait = ImageEnhance.Brightness(portrait).enhance(0.78)
    cx, cy = center
    if active and glow and not dead:
        # soft gold glow behind the active fighter
        halo = glow_mask(radius)
        g = halo.size[0]
        canvas.paste(_active_color(snap), (cx - g // 2, cy - g // 2, cx - g // 2 + g, cy - g // 2 + g), halo)
    canvas.paste(portrait, (cx - radius, cy - radius), circle_mask(size))
    if framed:
        frame = battle_frames.get_frame(radius, snap.get("tier", 1), snap.get("level", 0), universe_accent(snap.get("universe")),
                                        flip=flip, resolved=snap.get("resolved", False) and not dead,
                                        crest_text=universe_initials(snap.get("universe")))
        canvas.paste(frame, (cx - frame.width // 2, cy - frame.height // 2), frame)
    else:
        ring = 6
        draw.ellipse((cx - radius - ring, cy - radius - ring, cx + radius + ring, cy + radius + ring),
                     outline=GOLD if active and not dead else RING, width=ring)
    if dead:
        draw_text(draw, (cx, cy), "KO", font(FONT_VS, 84), fill=(235, 70, 70), anchor="mm", stroke=5)


def _draw_side(canvas, draw, snap, side, active, ally=None, ally_active=False, shake=(0, 0), glow=True):
    flip = side == "right"
    edge = WIDTH if flip else 0
    sign = -1 if flip else 1
    px = RIGHT_PORTRAIT_X if flip else LEFT_PORTRAIT_X
    hp_rgb = health_rgb(snap["health"], snap["max_health"])

    state = battle_fx.state_of(snap)
    radius = PORTRAIT_R + (RESOLVE_RADIUS_BONUS if state == "resolve" else 0)
    _paste_portrait(canvas, draw, snap, (px + shake[0], PORTRAIT_Y + shake[1]), radius, active, flip=flip, glow=glow)

    # name / level / class column
    tx = edge + sign * TEXT_INNER
    anchor_l = "ra" if flip else "la"
    lines, name_font = wrap_name(draw, snap["name"], FONT_NAME, 40, TEXT_WIDTH)
    y = 82 if len(lines) == 1 else 62
    for line in lines:
        draw_text(draw, (tx, y), line, name_font, anchor=anchor_l, stroke=3)
        y += int(name_font.size * 1.12)
    meta = snap["class_name"].upper() if snap["class_name"] else f"LV {snap['level']}"
    meta_color = MUTED
    if state == "resolve":
        meta, meta_color = f"RESOLVED  ·  {meta}", _type_color(snap, "light")
    elif state == "focus":
        meta, meta_color = f"FOCUSED  ·  {meta}", _type_color(snap, "glow")
    draw_text(draw, (tx, y + 6), meta, fit_font(draw, meta, FONT_BLACK if state != "normal" else FONT_BOLD, 24, TEXT_WIDTH),
              fill=meta_color, anchor=anchor_l, stroke=2)

    # attack / defense
    label_font = font(FONT_BLACK, 20)
    value_font = font(FONT_NUM, 44)
    stat_y = 236
    cols = [("ATK", snap["attack"], (255, 120, 90)), ("DEF", snap["defense"], (110, 175, 255))]
    if flip:
        cols = cols[::-1]
    for index, (label, value, color) in enumerate(cols):
        cx = tx + sign * index * 128
        draw_text(draw, (cx, stat_y), label, label_font, fill=color, anchor=anchor_l, stroke=2)
        draw_text(draw, (cx, stat_y + 24), short_number(value), value_font, anchor=anchor_l, stroke=3)

    # health and stamina
    bar_x0 = BAR_MARGIN if not flip else HALF + 28
    bar_x1 = HALF - 28 if not flip else WIDTH - BAR_MARGIN
    hp_text = f"{short_number(snap['health'])} / {short_number(snap['max_health'])}"
    draw_bar(draw, (bar_x0, HP_BAR_Y, bar_x1, HP_BAR_Y + HP_BAR_H), snap["health"] / snap["max_health"], hp_rgb,
             "HP", hp_text, font(FONT_NUM, 30), flip=flip)
    st_x1 = bar_x0 + int((bar_x1 - bar_x0) * 0.72) if not flip else bar_x1
    st_x0 = bar_x0 if not flip else bar_x1 - int((bar_x1 - bar_x0) * 0.72)
    st_text = f"{round(snap['stamina'])}"
    draw_bar(draw, (st_x0, ST_BAR_Y, st_x1, ST_BAR_Y + ST_BAR_H), snap["stamina"] / snap["max_stamina"], STAMINA,
             "ST", st_text, font(FONT_NUM, 22), flip=flip)

    if ally is not None:
        # partner: compact badge beside the stamina bar
        r = 21
        ax = (st_x1 + 14 + r) if not flip else (st_x0 - 14 - r)
        ay = ST_BAR_Y + ST_BAR_H // 2
        _paste_portrait(canvas, draw, ally, (ax, ay), r, ally_active, flip=flip, framed=False, glow=glow)
        label = short_number(ally["health"])
        hp_font = font(FONT_NUM, 24)
        tx2 = ax + sign * (r + 10)
        draw_text(draw, (tx2, ay), label, hp_font, fill=health_rgb(ally["health"], ally["max_health"]),
                  anchor="lm" if not flip else "rm", stroke=2)

    chip_edge = bar_x1 if flip else bar_x0
    draw_chips(draw, snap["chips"], chip_edge, CHIPS_Y, bar_x1 - bar_x0, flip=flip)


def _backdrop(left, right):
    canvas = Image.new("RGB", (WIDTH, HEIGHT), (14, 16, 24))
    _, lb, _ = side_art(left)
    _, rb, _ = side_art(right)
    canvas.paste(lb, (0, 0))
    seam = Image.new("L", (WIDTH, HEIGHT), 0)
    ImageDraw.Draw(seam).polygon([(HALF + 60, 0), (WIDTH, 0), (WIDTH, HEIGHT), (HALF - 60, HEIGHT)], fill=255)
    right_layer = Image.new("RGB", (WIDTH, HEIGHT))
    right_layer.paste(rb, (HALF - 80, 0))
    canvas.paste(right_layer, (0, 0), seam)
    return canvas


_BASE_CACHE = OrderedDict()
_BASE_LOCK = threading.Lock()


def _base_layer(left, right):
    """Backdrop + seam + vignette for a pair of arts (cached: identical every turn)."""
    key = (left.get("battle_art") or left["art"], left["name"], str(left.get("art_focus")),
           right.get("battle_art") or right["art"], right["name"], str(right.get("art_focus")), "panels")
    with _BASE_LOCK:
        hit = _BASE_CACHE.get(key)
        if hit is not None:
            _BASE_CACHE.move_to_end(key)
            return hit.copy()
    canvas = _backdrop(left, right)
    shade = Image.new("L", (WIDTH, HEIGHT), 0)
    sd = ImageDraw.Draw(shade)
    for i in range(HEIGHT - 240, HEIGHT):            # darker floor under the bars
        sd.line([(0, i), (WIDTH, i)], fill=int(170 * (i - (HEIGHT - 240)) / 240))
    canvas.paste((8, 9, 14), (0, 0), shade)
    d = ImageDraw.Draw(canvas)
    d.line([(HALF + 60, 0), (HALF - 60, HEIGHT)], fill=(0, 0, 0), width=12)
    d.line([(HALF + 60, 0), (HALF - 60, HEIGHT)], fill=(235, 238, 255), width=4)
    with _BASE_LOCK:
        _BASE_CACHE[key] = canvas
        while len(_BASE_CACHE) > 32:
            _BASE_CACHE.popitem(last=False)
    return canvas.copy()


def _center(draw, turn_total, label=None):
    draw_text(draw, (HALF, PORTRAIT_Y + 10), "VS", font(FONT_VS, 86), fill=WHITE, anchor="mm", stroke=6)
    label = label or f"TURN {max(0, int(_num(turn_total)))}"
    fnt = font(FONT_BLACK, 24)
    w = text_width(draw, label, fnt) + 36
    box = (HALF - w // 2, 18, HALF + w // 2, 56)
    draw.rounded_rectangle(box, radius=19, fill=(20, 22, 32), outline=GOLD, width=3)
    draw.text((HALF, 37), label, fill=GOLD, font=fnt, anchor="mm")


_SIDE_MASKS = {}


def side_mask(side):
    """L mask of one fighter's half (split along the diagonal seam)."""
    mask = _SIDE_MASKS.get(side)
    if mask is None:
        right = Image.new("L", (WIDTH, HEIGHT), 0)
        ImageDraw.Draw(right).polygon([(HALF + 60, 0), (WIDTH, 0), (WIDTH, HEIGHT), (HALF - 60, HEIGHT)], fill=255)
        mask = right if side == "right" else ImageOps.invert(right)
        _SIDE_MASKS[side] = mask
    return mask


def _compose(left, right, turn_total, active, left_ally, right_ally, fx_t=None, frame=0, shake=None, label=None, spotlight=True):
    fx_t = fx_t or {}
    shake = shake or {}
    canvas = _base_layer(left, right)
    for side, snap, px in (("left", left, LEFT_PORTRAIT_X), ("right", right, RIGHT_PORTRAIT_X)):
        state = battle_fx.state_of(snap)
        if state != "normal":
            radius = PORTRAIT_R + (RESOLVE_RADIUS_BONUS if state == "resolve" else 0)
            battle_fx.apply(canvas, side_mask(side), (px, PORTRAIT_Y), radius, state, name=snap["name"],
                            turn=int(_num(turn_total)), t=fx_t.get(side, 1.0), frame=frame, element=snap.get("element"))
    draw = ImageDraw.Draw(canvas)
    # the seam is drawn again so the effects stay on their own side
    draw.line([(HALF + 60, 0), (HALF - 60, HEIGHT)], fill=(0, 0, 0), width=12)
    draw.line([(HALF + 60, 0), (HALF - 60, HEIGHT)], fill=(235, 238, 255), width=4)
    if spotlight:
        _draw_side(canvas, draw, left, "left", active == "left", left_ally, active == "left_ally", shake.get("left", (0, 0)))
        _draw_side(canvas, draw, right, "right", active == "right", right_ally, active == "right_ally", shake.get("right", (0, 0)))
    else:
        # nobody is acting yet (match start): everyone at full brightness, no glow
        _draw_side(canvas, draw, left, "left", True, left_ally, True, glow=False)
        _draw_side(canvas, draw, right, "right", True, right_ally, True, glow=False)
    _center(draw, turn_total, label)
    return canvas


def render(left, right, turn_total=0, active="left", left_ally=None, right_ally=None, fmt="JPEG"):
    """Draw the scene and return a rewound BytesIO (JPEG by default).

    ``active`` is "left", "right", "left_ally", "right_ally" or None.
    """
    try:
        with render_cache.RENDER_LOCK:
            canvas = _compose(left, right, turn_total, active, left_ally, right_ally)
        return encode(canvas, fmt)
    except Exception as ex:
        loggy.warning(f"battle scene render failed: {type(ex).__name__}: {ex}")
        return fallback(left, right, turn_total, fmt)


def render_matchup(left, right, label="MATCH", left_ally=None, right_ally=None):
    """The match start scene: both fighters at full brightness, ``label`` in the centre pill."""
    try:
        with render_cache.RENDER_LOCK:
            canvas = _compose(left, right, 0, None, left_ally, right_ally, label=label, spotlight=False)
        return encode(canvas)
    except Exception as ex:
        loggy.warning(f"matchup render failed: {type(ex).__name__}: {ex}")
        return fallback(left, right, 0)


def render_power_up(left, right, sides, turn_total=0, active="left", left_ally=None, right_ally=None):
    """Animated GIF of a fighter entering Focus or Resolve (``sides``: e.g. {"left": "resolve"}).

    Plays once and holds on the final frame (the long last frame also keeps
    clients that loop GIFs from replaying it constantly).  Returns (BytesIO,
    extension): ("gif") normally, or a still ("jpg") if anything fails.
    """
    try:
        resolve = "resolve" in sides.values()
        count = 14 if resolve else 10
        frames, durations = [], []
        rng = random.Random(battle_fx._seed(str(sides)) + int(_num(turn_total)))
        for i in range(count):
            t = (i + 1) / count
            shake = {}
            for side, state in sides.items():
                if state == "resolve" and t < 0.7:
                    amp = 9 * (1 - t / 0.7)
                    shake[side] = (int(rng.uniform(-amp, amp)), int(rng.uniform(-amp, amp)))
            with render_cache.RENDER_LOCK:
                canvas = _compose(left, right, turn_total, active, left_ally, right_ally,
                                  fx_t={side: t for side in sides}, frame=i, shake=shake)
            frame = canvas.resize(GIF_SIZE, Image.BILINEAR).quantize(colors=255, method=Image.Quantize.FASTOCTREE)
            frames.append(frame)
            durations.append(70 if resolve else 80)
        durations[-1] = 60000
        out = BytesIO()
        frames[0].save(out, "GIF", save_all=True, append_images=frames[1:], duration=durations, optimize=False, disposal=1)
        out.seek(0)
        return out, "gif"
    except Exception as ex:
        loggy.warning(f"power-up animation failed: {type(ex).__name__}: {ex}")
        return render(left, right, turn_total, active, left_ally, right_ally), "jpg"


def encode(canvas, fmt="JPEG"):
    out = BytesIO()
    if fmt.upper() in ("JPG", "JPEG"):
        # 4:4:4 keeps coloured text and thin outlines sharp
        canvas.save(out, "JPEG", quality=JPEG_QUALITY, subsampling=0, optimize=False)
    else:
        canvas.save(out, "PNG", compress_level=3)
    out.seek(0)
    return out


def fallback(left, right, turn_total=0, fmt="JPEG"):
    """Text-only scene used if the normal render fails (never raises)."""
    canvas = Image.new("RGB", (WIDTH, HEIGHT), (24, 26, 36))
    try:
        with render_cache.RENDER_LOCK:
            draw = ImageDraw.Draw(canvas)
            fnt = font(FONT_BOLD, 34)
            for x, snap in ((60, left), (HALF + 60, right)):
                if not snap:
                    continue
                lines = [snap.get("name", ""),
                         f"HP {short_number(snap.get('health'))} / {short_number(snap.get('max_health'))}",
                         f"ST {round(_num(snap.get('stamina')))}",
                         f"ATK {short_number(snap.get('attack'))}   DEF {short_number(snap.get('defense'))}"]
                for i, line in enumerate(lines):
                    draw.text((x, 150 + i * 70), str(line)[:28], fill=WHITE, font=fnt)
            draw.text((HALF, 60), f"TURN {turn_total}", fill=GOLD, font=fnt, anchor="mm")
    except Exception:
        pass
    return encode(canvas, fmt)


def render_art_preview(card):
    """The one battle picture for this card (for the /battleart admin command)."""
    try:
        base = snapshot(card)
        url = getattr(card, "battle_art", None)
        cell_w, height = 330, 470
        canvas = Image.new("RGB", (cell_w, height), (24, 26, 34))
        with render_cache.RENDER_LOCK:
            draw = ImageDraw.Draw(canvas)
            snap = dict(base, battle_art=url, resolved=False, focused=False, health=max(1.0, base["health"]))
            if url:
                panel, _, _ = side_art(snap)
                _paste_panel(canvas, draw, snap, (cell_w // 2, 215), panel, True, False)
            else:
                draw_text(draw, (cell_w // 2, 215), "no art", font(FONT_BOLD, 28), fill=DIM, anchor="mm")
            draw_text(draw, (cell_w // 2, height - 40), "Card", font(FONT_BLACK, 28), anchor="mm")
        return encode(canvas)
    except Exception as ex:
        loggy.warning(f"battle art preview failed: {type(ex).__name__}: {ex}")
        return encode(Image.new("RGB", (330, 470), (24, 26, 34)))
