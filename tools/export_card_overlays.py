"""Export the element frame overlays as PNG templates (developer tool).

    python tools/export_card_overlays.py

Writes assets/card_overlays/<element>.png (592 x 672, the /cards and /viewcard
card frame) and <element>@2x.png (1184 x 1344), plus contact_sheet.jpg.  The
bot draws these itself at runtime (element_art.py); the PNGs are for artists who
want to repaint them, and for previewing.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("RENDER_OFFLINE", "1")

from PIL import Image, ImageDraw  # noqa: E402

import element_art  # noqa: E402
import render_cache  # noqa: E402

PANEL_W, PANEL_H, PAD = 500, 580, 46


def main():
    out_dir = os.path.join(ROOT, "assets", "card_overlays")
    os.makedirs(out_dir, exist_ok=True)
    keys = list(element_art.STYLES)
    thumbs = []
    for key in keys:
        small = element_art.overlay(key, PANEL_W, PANEL_H, PAD)
        big = element_art.overlay(key, PANEL_W * 2, PANEL_H * 2, PAD * 2, radius=44, border=30)
        name = key.lower()
        small.save(os.path.join(out_dir, f"{name}.png"))
        big.save(os.path.join(out_dir, f"{name}@2x.png"))
        tile = Image.new("RGBA", small.size, (40, 42, 52, 255))
        ImageDraw.Draw(tile).rounded_rectangle((PAD, PAD, PAD + PANEL_W, PAD + PANEL_H), radius=22, fill=(70, 74, 90, 255))
        tile.alpha_composite(small)
        ImageDraw.Draw(tile).text((tile.width // 2, tile.height // 2), element_art.style(key)[0], fill=(240, 240, 250),
                                  font=render_cache.get_font("Roboto-Black.ttf", 48), anchor="mm")
        thumbs.append(tile.convert("RGB").resize((296, 336), Image.LANCZOS))
        print("wrote", name)
    cols = 5
    sheet = Image.new("RGB", (cols * 296, ((len(thumbs) + cols - 1) // cols) * 336), (24, 26, 34))
    for i, t in enumerate(thumbs):
        sheet.paste(t, ((i % cols) * 296, (i // cols) * 336))
    sheet.save(os.path.join(out_dir, "contact_sheet.jpg"), quality=88)
    print("contact sheet:", os.path.join(out_dir, "contact_sheet.jpg"))


if __name__ == "__main__":
    main()
