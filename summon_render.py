"""Portrait summon image. Same layout as a card, dressed as a companion.

    ┌───────────────── 720 x 1080 ─────────────────┐
    │                 S U M M O N                  │
    │              ╭──────────────╮                │
    │              │  PET medallion│               │
    │              ╰──────────────╯                │
    │                 Kurama                       │
    │            Companion · Naruto                │
    │      [ LV 12 ]   [ BOND 3 ]   [ AP 240 ]     │
    │   ┌ ability ─────────────────────────────┐   │
    │   │ 🔥 Roar                         240   │   │
    │   │ what the summon just did             │   │
    └──────────────────────────────────────────────┘

The portrait is a round medallion: the pet inside an old summon template,
or a plain picture cropped to a circle. The landscape template never shows.
"""
import math
import textwrap
import threading
from collections import OrderedDict

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
from pilmoji import Pilmoji

import battle_panels
import battle_scene
import card_render
import crown_utilities
import render_cache

W, H = card_render.W, card_render.H
PANEL_W = card_render.PANEL_W
PANEL_H = 500
PANEL_X, PANEL_Y = card_render.PANEL_X, card_render.PANEL_Y
# Inner edge of the character circle on a 1200x600 summon template.
# Inset from the gold ring so the old LVL badge stays outside the medallion.
SUMMON_CX, SUMMON_CY, SUMMON_R = 0.262, 0.535, 0.372

GOLD = (232, 184, 74)
CREAM = (255, 244, 214)
INK = (18, 12, 8)
WHITE = (255, 255, 255)
MUTED = (214, 196, 160)

_cache = OrderedDict()
_lock = threading.Lock()


def _font(name, size):
    return card_render._font(name, size)


def _fit(draw, text, name, size, max_width, min_size=18):
    return card_render._fit(draw, text, name, size, max_width, min_size)


def _portrait(full):
    """Round pet picture. Old summon templates are cut on their own circle."""
    w, h = full.size
    if w >= 1.7 * h:
        cx, cy, r = SUMMON_CX * w, SUMMON_CY * h, SUMMON_R * h
        box = (max(0, int(cx - r)), max(0, int(cy - r)), min(w, int(cx + r)), min(h, int(cy + r)))
        art = full.crop(box)
        backdrop = full.crop(box)
    else:
        art = battle_panels.smart_crop(full, 1)
        backdrop = full
    art = art.resize((PANEL_W, PANEL_H), Image.LANCZOS)
    mask = Image.new("L", (PANEL_W, PANEL_H), 0)
    ImageDraw.Draw(mask).ellipse((1, 1, PANEL_W - 2, PANEL_H - 2), fill=255)
    panel = art.convert("RGBA")
    panel.putalpha(mask)
    return panel, backdrop


def _art(url, label):
    key = (url, label)
    with _lock:
        hit = _cache.get(key)
        if hit is not None:
            _cache.move_to_end(key)
            return hit
    full = render_cache.load_image(url, fallback_label=label).convert("RGB")
    panel, backdrop = _portrait(full)
    bg = battle_panels.smart_crop(backdrop, W / H).resize((48, 72), Image.BILINEAR)
    bg = bg.filter(ImageFilter.GaussianBlur(3)).resize((W, H), Image.BICUBIC)
    bg = ImageEnhance.Brightness(bg).enhance(0.32)
    bg = ImageEnhance.Color(bg).enhance(1.35)
    wash = Image.new("RGB", (W, H), (120, 72, 18))
    bg = Image.blend(bg, wash, 0.22)
    made = (panel, bg)
    with _lock:
        _cache[key] = made
        while len(_cache) > 48:
            _cache.popitem(last=False)
    return made


def _paw(draw, cx, cy, scale=1.0, fill=GOLD):
    toe = 6 * scale
    for dx, dy in ((-10, -11), (0, -15), (10, -11)):
        x, y = cx + dx * scale, cy + dy * scale
        draw.ellipse((x - toe, y - toe, x + toe, y + toe), fill=fill)
    pad_x, pad_y = 11 * scale, 8 * scale
    draw.ellipse((cx - pad_x, cy - pad_y * 0.2, cx + pad_x, cy + pad_y * 1.5), fill=fill)


def _spaced(draw, text, y, font, fill, tracking=6):
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = (W - total) / 2
    for ch, width in zip(text, widths):
        draw.text((x, y), ch, fill=fill, font=font)
        x += width + tracking


def render(url, name, message="", lvl=0, bond=0, universe="", ability="", ability_type="", power=None):
    """Draw a summon as a portrait PNG (rewound BytesIO). Never raises."""
    try:
        name = str(name or "Summon")
        panel, bg = _art(url, name)
        canvas = bg.copy()
        with render_cache.RENDER_LOCK:
            draw = ImageDraw.Draw(canvas)
            _spaced(draw, "SUMMON", 28, _font("Roboto-Black.ttf", 18), GOLD, tracking=8)

            glow = Image.new("L", (PANEL_W + 160, PANEL_H + 160), 0)
            ImageDraw.Draw(glow).ellipse((36, 36, PANEL_W + 124, PANEL_H + 124), fill=160)
            glow = glow.filter(ImageFilter.GaussianBlur(26))
            tint = Image.new("RGB", glow.size, GOLD)
            canvas.paste(tint, (PANEL_X - 80, PANEL_Y - 80), glow)

            canvas.paste(panel.convert("RGB"), (PANEL_X, PANEL_Y), panel)
            frame = (PANEL_X - 8, PANEL_Y - 8, PANEL_X + PANEL_W + 8, PANEL_Y + PANEL_H + 8)
            draw.ellipse(frame, outline=GOLD, width=8)
            draw.ellipse(
                (frame[0] + 12, frame[1] + 12, frame[2] - 12, frame[3] - 12),
                outline=(90, 62, 18), width=2,
            )
            ccx, ccy = PANEL_X + PANEL_W / 2, PANEL_Y + PANEL_H / 2
            paw_r = PANEL_W / 2 + 28
            for deg in (225, 315, 135, 45):
                ang = math.radians(deg)
                _paw(draw, ccx + math.cos(ang) * paw_r, ccy + math.sin(ang) * paw_r, 0.62)

            tag_x, tag_y = W // 2, PANEL_Y - 6
            draw.line((tag_x, PANEL_Y - 28, tag_x, tag_y), fill=GOLD, width=3)
            draw.rounded_rectangle((tag_x - 38, tag_y, tag_x + 38, tag_y + 58), radius=12, fill=INK, outline=GOLD, width=3)
            draw.ellipse((tag_x - 5, tag_y + 8, tag_x + 5, tag_y + 18), outline=GOLD, width=2)
            draw.text((tag_x, tag_y + 38), "PET", fill=GOLD, font=_font("Roboto-Black.ttf", 16), anchor="mm")

            y = PANEL_Y + PANEL_H + 36
            name_font = _fit(draw, name, "YesevaOne-Regular.ttf", 52, W - 80, 28)
            battle_scene.draw_text(draw, (W // 2, y + 20), name, name_font, anchor="mm", stroke=3)
            crest = ""
            try:
                crest = crown_utilities.crest_dict.get(universe, "") or ""
            except Exception:
                crest = ""
            sub = f"🐾 Companion    {crest} {universe}".strip()
            sub_font = _fit(draw, sub, "Roboto-Bold.ttf", 26, W - 80, 16)
            with Pilmoji(canvas, source=render_cache.EMOJI_SOURCE, cache=False) as pilmoji:
                sw = pilmoji.getsize(sub, font=sub_font)[0]
                pilmoji.text((int(W / 2 - sw / 2), y + 62), sub, MUTED, font=sub_font, stroke_width=2, stroke_fill=(0, 0, 0))

            y = PANEL_Y + PANEL_H + 132
            pills = [("LV", _number(lvl), GOLD), ("BOND", _number(bond), (255, 138, 176))]
            if power not in (None, ""):
                pills.append(("AP", battle_scene.short_number(power), (166, 255, 60)))
            pill_w, gap = (200 if len(pills) == 2 else 152), 14
            x = (W - (len(pills) * pill_w + (len(pills) - 1) * gap)) // 2
            for label, value, color in pills:
                draw.rounded_rectangle((x, y, x + pill_w, y + 66), radius=16, fill=(22, 16, 10), outline=color, width=3)
                draw.text((x + pill_w // 2, y + 18), label, fill=color, font=_font("Roboto-Black.ttf", 16), anchor="mm")
                vf = _fit(draw, str(value), "RobotoCondensed-Bold.ttf", 30, pill_w - 16, 16)
                battle_scene.draw_text(draw, (x + pill_w // 2, y + 45), str(value), vf, anchor="mm", stroke=2)
                x += pill_w + gap

            box = (34, y + 82, W - 34, H - 22)
            overlay = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]), (16, 12, 8, 210))
            mask = Image.new("L", overlay.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, overlay.width - 1, overlay.height - 1), radius=18, fill=210)
            canvas.paste(overlay.convert("RGB"), box[:2], mask)
            draw.rounded_rectangle(box, radius=18, outline=GOLD, width=2)
            _paw(draw, box[0] + 28, box[1] + 28, 0.55, GOLD)
            draw.text((box[0] + 52, box[1] + 16), "ABILITY", fill=GOLD, font=_font("Roboto-Black.ttf", 14))

            emoji = ""
            try:
                emoji = crown_utilities.set_emoji(ability_type) if ability_type else ""
            except Exception:
                emoji = ""
            with Pilmoji(canvas, source=render_cache.EMOJI_SOURCE, cache=False) as pilmoji:
                text_top = box[1] + 48
                if ability:
                    row = f"{emoji} {ability}".strip()
                    row_font = _fit(draw, row, "Roboto-Bold.ttf", 28, box[2] - box[0] - 160, 18)
                    pilmoji.text((box[0] + 22, text_top), row, WHITE, font=row_font, stroke_width=2, stroke_fill=(0, 0, 0))
                    if power not in (None, ""):
                        shown = battle_scene.short_number(power)
                        battle_scene.draw_text(draw, (box[2] - 22, text_top + 16), shown, _font("RobotoCondensed-Bold.ttf", 30),
                                               fill=CREAM, anchor="rm", stroke=2)
                    if ability_type:
                        draw.text((box[0] + 22, text_top + 36), str(ability_type).title(), fill=GOLD, font=_font("Roboto-Bold.ttf", 16))
                    text_top += 64
                body = textwrap.fill(str(message or "").strip() or "A companion fighting beside you.", width=36)
                line_font = _font("Roboto-Bold.ttf", 22)
                line_y = text_top
                for line in body.splitlines():
                    if line_y > box[3] - 36:
                        break
                    pilmoji.text((box[0] + 22, line_y), line, WHITE, font=line_font, stroke_width=2, stroke_fill=(0, 0, 0))
                    line_y += 28
        return render_cache.encode_png(canvas)
    except Exception:
        return _fallback(name)


def _number(value):
    try:
        return str(int(float(value)))
    except (TypeError, ValueError):
        return "0"


def _fallback(name):
    try:
        im = Image.new("RGB", (W, H), (28, 20, 12))
        with render_cache.RENDER_LOCK:
            d = ImageDraw.Draw(im)
            _paw(d, W // 2, 420, 3, GOLD)
            d.text((W // 2, 560), "SUMMON", fill=GOLD, font=_font("Roboto-Black.ttf", 28), anchor="mm")
            d.text((W // 2, 620), str(name)[:28], fill=WHITE, font=_font("Roboto-Bold.ttf", 36), anchor="mm")
        return render_cache.encode_png(im)
    except Exception:
        return render_cache.encode_png(Image.new("RGB", (W, H), (28, 20, 12)))


def parts_from_doc(doc):
    """Name, art, ability and numbers stored on a summon record."""
    name = doc.get("PET") or doc.get("NAME") or "Summon"
    universe = doc.get("UNIVERSE") or ""
    url = doc.get("PATH") or ""
    lvl = doc.get("LVL") or 0
    bond = doc.get("BOND") or 0
    ability, ability_type, power = "", "", None
    abilities = doc.get("ABILITIES") or []
    if abilities and isinstance(abilities[0], dict):
        ability_type = str(abilities[0].get("TYPE") or "")
        for key, value in abilities[0].items():
            if key != "TYPE":
                ability, power = str(key), value
                break
    try:
        message = crown_utilities.element_mapping.get(str(ability_type).upper(), "") if ability_type else ""
    except Exception:
        message = ""
    if not message and ability:
        message = f"{ability}: {power}"
    return {
        "url": url, "name": name, "message": message, "lvl": lvl, "bond": bond,
        "universe": universe, "ability": ability, "ability_type": ability_type, "power": power,
    }
