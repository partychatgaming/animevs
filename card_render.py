"""Portrait card image used everywhere a card is shown (/build, /viewcard, drops,
level-ups, encounters...).  Replaces the old landscape template render.

    ┌───────────────── 720 x 1080 ─────────────────┐
    │            ★ ★ ★ ★  (tier stars)             │
    │   ┌──────────────────────────────────────┐   │
    │   │                                      │   │
    │   │        card art (framed panel)       │   │
    │   │                                      │   │
    │  (LV)                                  (UNI) │
    │              Naruto Uzumaki                  │
    │         <class> Fighter · <crest> Naruto     │
    │   [ HP 1.8K ] [ ST 100 ] [ ATK 120 ] [ DEF 95 ]
    │   ┌ moves ───────────────────────────────┐   │
    │   │ 👊 Rasengan                  80  10 ST│   │
    │   │ ...                                   │   │
    └──────────────────────────────────────────────┘

The art is the card's plain art (CARD_ART...) when it has some, otherwise the art
inside the character circle of its premade card, so no template ever shows.
"""
import textwrap
import threading
from collections import OrderedDict

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
from pilmoji import Pilmoji

import battle_panels
import element_art
import battle_scene
import crown_utilities
import custom_logging
import render_cache

W, H = 720, 1080
PANEL_W, PANEL_H = 500, 580
PANEL_X, PANEL_Y = (W - PANEL_W) // 2, 74
WHITE = (255, 255, 255)
MUTED = (196, 202, 220)

STAT_STYLES = (
    ("HP", (46, 204, 113)),
    ("ST", (64, 156, 255)),
    ("ATK", (255, 120, 90)),
    ("DEF", (110, 175, 255)),
)

_cache = OrderedDict()
_lock = threading.Lock()


def _art(url, kind, focus, label):
    """(panel art, blurred full-card background), cached per art."""
    key = (url, kind, str(focus))
    with _lock:
        hit = _cache.get(key)
        if hit is not None:
            _cache.move_to_end(key)
            return hit
    if kind == "raw":
        panel, full = battle_panels.load_panel_art(url, PANEL_W, PANEL_H, focus)
    else:
        panel, full = battle_panels.load_template_panel(url, PANEL_W, PANEL_H, label)
    bg = battle_panels.smart_crop(full, W / H).resize((48, 72), Image.BILINEAR)
    bg = bg.filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BICUBIC)
    bg = ImageEnhance.Brightness(bg).enhance(0.36)
    bg = ImageEnhance.Color(bg).enhance(1.2)
    made = (panel, bg)
    with _lock:
        _cache[key] = made
        while len(_cache) > 48:
            _cache.popitem(last=False)
    return made


def art_source(card):
    """(url, kind, crop). One picture for the card, including focus and resolve."""
    raw = battle_scene.battle_art_for(card)
    if raw:
        return raw, "raw", getattr(card, "battle_art_focus", None)
    return getattr(card, "path", None), "template", None


def _font(name, size):
    return render_cache.get_font(name, size)


def _fit(draw, text, name, size, max_width, min_size=22):
    while size > min_size and draw.textlength(text, font=_font(name, size)) > max_width:
        size -= 2
    return _font(name, size)


def _emoji(value):
    """Text form of an emoji (unicode, or <:name:id> for Discord emoji)."""
    if value is None:
        return ""
    return str(value)


def render(card, mode="non-battle", encounter=False):
    """Draw ``card`` as a portrait PNG (rewound BytesIO).  Never raises."""
    try:
        url, kind, focus = art_source(card)
        name = card.rname if getattr(card, "used_resolve", False) and getattr(card, "rname", "") else card.name
        panel, bg = _art(url, kind, focus, name)
        canvas = bg.copy()
        dead = getattr(card, "health", 1) <= 0
        art = panel
        if dead:
            art = ImageEnhance.Brightness(ImageOps.grayscale(panel).convert("RGB")).enhance(0.55)

        with render_cache.RENDER_LOCK:
            draw = ImageDraw.Draw(canvas)
            tier = int(getattr(card, "tier", 1) or 1)
            level = int(getattr(card, "card_lvl", 0) or 0)
            universe = getattr(card, "universe", "")
            accent = battle_scene.universe_accent(universe)

            # soft accent glow behind the panel
            glow = Image.new("L", (PANEL_W + 160, PANEL_H + 160), 0)
            ImageDraw.Draw(glow).rounded_rectangle((50, 50, PANEL_W + 110, PANEL_H + 110), radius=50, fill=150)
            glow = glow.filter(ImageFilter.GaussianBlur(26))
            type_glow = element_art.style(element_art.element_of(card))[5]
            canvas.paste(type_glow, (PANEL_X - 80, PANEL_Y - 80, PANEL_X - 80 + glow.width, PANEL_Y - 80 + glow.height), glow)

            canvas.paste(art, (PANEL_X, PANEL_Y), battle_scene.panel_mask(PANEL_W, PANEL_H))
            frame, pad = battle_panels.get_panel_frame(PANEL_W, PANEL_H, tier, level, accent,
                                                        crest_text=battle_scene.universe_initials(universe))
            canvas.paste(frame, (PANEL_X - pad, PANEL_Y - pad), frame)
            deco = element_art.overlay(element_art.element_of(card), PANEL_W, PANEL_H, pad)   # type = Ultimate's element
            canvas.paste(deco, (PANEL_X - pad, PANEL_Y - pad), deco)
            if dead:
                battle_scene.draw_text(draw, (W // 2, PANEL_Y + PANEL_H // 2), "KO", _font("KomikaTitle.ttf", 120),
                                       fill=(235, 70, 70), anchor="mm", stroke=6)

            # name and class / universe
            y = PANEL_Y + PANEL_H + 34
            name_font = _fit(draw, name, "YesevaOne-Regular.ttf", 54, W - 70, 30)
            battle_scene.draw_text(draw, (W // 2, y + 22), name, name_font, anchor="mm", stroke=3)
            class_emoji = _emoji(crown_utilities.class_emojis.get(getattr(card, "card_class", ""), ""))
            crest = _emoji(getattr(card, "universe_crest", ""))
            sub = f"{class_emoji} {getattr(card, 'class_message', '') or str(getattr(card, 'card_class', '')).title()}   {crest} {universe}"
            sub_font = _fit(draw, sub, "Roboto-Bold.ttf", 28, W - 80, 18)
            with Pilmoji(canvas, source=render_cache.EMOJI_SOURCE, cache=False) as pilmoji:
                sw = pilmoji.getsize(sub, font=sub_font)[0]
                pilmoji.text((int(W / 2 - sw / 2), y + 68), sub, MUTED, font=sub_font, stroke_width=2, stroke_fill=(0, 0, 0))

            # stat pills
            y = PANEL_Y + PANEL_H + 140
            values = (
                f"{battle_scene.short_number(card.health)}" if round(card.health) >= round(card.max_health)
                else f"{battle_scene.short_number(card.health)}/{battle_scene.short_number(card.max_health)}",
                f"{round(card.stamina)}",
                battle_scene.short_number(card.attack),
                battle_scene.short_number(card.defense),
            )
            pill_w, gap = 152, 12
            x = (W - (4 * pill_w + 3 * gap)) // 2
            for (label, color), value in zip(STAT_STYLES, values):
                draw.rounded_rectangle((x, y, x + pill_w, y + 66), radius=16, fill=(16, 18, 26), outline=color, width=3)
                draw.text((x + pill_w // 2, y + 18), label, fill=color, font=_font("Roboto-Black.ttf", 18), anchor="mm")
                vf = _fit(draw, value, "RobotoCondensed-Bold.ttf", 32, pill_w - 16, 18)
                battle_scene.draw_text(draw, (x + pill_w // 2, y + 45), value, vf, anchor="mm", stroke=2)
                x += pill_w + gap

            # moves (or the encounter line in Adventure)
            box = (34, y + 82, W - 34, H - 22)
            overlay = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]), (10, 12, 18, 200))
            mask = Image.new("L", overlay.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, overlay.width - 1, overlay.height - 1), radius=18, fill=200)
            canvas.paste(overlay.convert("RGB"), box[:2], mask)
            draw.rounded_rectangle(box, radius=18, outline=(70, 76, 96), width=2)
            with Pilmoji(canvas, source=render_cache.EMOJI_SOURCE, cache=False) as pilmoji:
                if mode == "RPG" and encounter:
                    text = textwrap.fill(str(getattr(card, "ai_encounter_message", "") or f"{card.name} appears!"), 44)
                    pilmoji.text((box[0] + 22, box[1] + 18), text, WHITE, font=_font("Roboto-Bold.ttf", 26),
                                 stroke_width=2, stroke_fill=(0, 0, 0))
                else:
                    suffix = crown_utilities.enhancer_suffix_mapping.get(card.move4enh, "")
                    rows = [
                        (f"{card.move1_emoji} {card.move1}", f"{card.move1ap}", "10"),
                        (f"{card.move2_emoji} {card.move2}", f"{card.move2ap}", "30"),
                        (f"{card.move3_emoji} {card.move3}", f"{card.move3ap}", "80"),
                        (f"🦠 {card.move4}", f"{str(card.move4enh).title()} {card.move4ap}{suffix}", "20"),
                    ]
                    row_h = (box[3] - box[1] - 20) / 4
                    move_font = _font("Roboto-Bold.ttf", 27)
                    for i, (left, value, cost) in enumerate(rows):
                        ry = int(box[1] + 12 + i * row_h + row_h / 2)
                        value_font = _font("RobotoCondensed-Bold.ttf", 30)
                        cost_text = f"{cost} ST"
                        cost_font = _font("Roboto-Bold.ttf", 18)
                        cost_w = draw.textlength(cost_text, font=cost_font)
                        value_w = draw.textlength(value, font=value_font)
                        right = box[2] - 20
                        draw.text((right, ry), cost_text, fill=(140, 146, 165), font=cost_font, anchor="rm")
                        battle_scene.draw_text(draw, (right - cost_w - 14, ry), value, value_font, fill=(255, 214, 90), anchor="rm", stroke=2)
                        max_left = right - cost_w - 14 - value_w - 18 - (box[0] + 20)
                        label = left
                        while label and pilmoji.getsize(label, font=move_font)[0] > max_left:
                            label = label[:-2] + "…" if len(label) > 2 else ""
                        pilmoji.text((box[0] + 20, ry - 17), label, WHITE, font=move_font, stroke_width=2, stroke_fill=(0, 0, 0))
        return render_cache.encode_png(canvas)
    except Exception as ex:
        custom_logging.debug(ex)
        return fallback(card)


def fallback(card):
    try:
        im = Image.new("RGB", (W, H), (28, 30, 38))
        with render_cache.RENDER_LOCK:
            d = ImageDraw.Draw(im)
            f = _font("Roboto-Bold.ttf", 40)
            lines = [str(getattr(card, "name", "Card")),
                     f"HP {battle_scene.short_number(getattr(card, 'health', 0))}  ST {round(getattr(card, 'stamina', 0))}",
                     f"ATK {battle_scene.short_number(getattr(card, 'attack', 0))}  DEF {battle_scene.short_number(getattr(card, 'defense', 0))}"]
            for i, line in enumerate(lines):
                d.text((W // 2, 420 + i * 80), line[:30], fill=WHITE, font=f, anchor="mm")
        return render_cache.encode_png(im)
    except Exception:
        out = render_cache.encode_png(Image.new("RGB", (W, H), (28, 30, 38)))
        return out
